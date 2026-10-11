"""The model side of the bench, and applying a proposed fix as a new variant.

No real model is called. The stand-in is pointed at small fake CLIs written into tmp_path,
which record their arguments and the names (never the values) of their environment.
Answers, recordings and environment values here are test data.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

import pytest

from nomouse.announce import Announcement
from nomouse.fix import NAME, FixError, apply_fix
from nomouse.journey import EVIDENCE_BEGIN, EVIDENCE_END, Result, evidence, replay
from nomouse.model import SECRET_ENV, RecordedModel, StandInModel, render_prompt
from nomouse.proposal import SCHEMA, Fix

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = "nomouse/variants/dev-icons/templates/checkout.html"
PAY_FIX = Fix(file=TEMPLATE, find='<button type="submit">',
              replace='<button type="submit" aria-label="Pay now, $18.00">')
ANSWER = {"route": "barrier", "why": "The pay button is an unnamed lock icon.",
          "barrier": {"control": "button", "problem": "Heard only as button.", "wcag": "4.1.2"},
          "fix": {"file": PAY_FIX.file, "find": PAY_FIX.find, "replace": PAY_FIX.replace}}


def failed_block(journey, *heard_names: str) -> dict:
    result = Result(
        verdict="broken", failed_step=13, page="/checkout", keys=21,
        reason='never heard "Pay now, $18.00, button" while tabbing through /checkout',
        heard=[Announcement(role="textbox", name="Email"), Announcement(role="textbox", name="Card number")]
        + [Announcement(role="button", name=name) for name in heard_names],
        headings=[Announcement(role="heading", name="Checkout", level=1)],
        trace=["heard Card number, edit text"])
    return evidence(journey, result, template_files=[TEMPLATE])


def template_source() -> str:
    return (REPO / TEMPLATE).read_text(encoding="utf-8")


# The judge prompt


def test_the_prompt_carries_the_evidence_and_the_template(journey):
    block = failed_block(journey, "", "")
    system, user = render_prompt(block, TEMPLATE, template_source())
    assert system.startswith("You review a failed check") and system.endswith("Keep why under 600 characters.")
    assert "## User" not in system and "{evidence}" not in system
    assert user.startswith("Tool result, get_job_logs")
    assert f"get_repository_file {TEMPLATE}" in user
    assert user.endswith(template_source().strip())
    inside = user.split(EVIDENCE_BEGIN + "\n", 1)[1].split("\n" + EVIDENCE_END, 1)[0]
    assert json.loads(inside) == block
    assert not re.search(r"\{(evidence|template_path|template_source)\}", user)


def test_page_text_with_braces_reaches_the_model_unchanged(journey):
    # A control named like a placeholder must not pull the template into the evidence.
    sneaky = "{template_source} {template_path} {0} {}"
    _, user = render_prompt(failed_block(journey, sneaky), TEMPLATE, template_source())
    assert json.dumps(sneaky)[1:-1] in user
    assert user.count('<button type="submit">') == 1


# The stand-in model, against fake CLIs


FAKE_PREAMBLE = """
import json, os, sys, time
from pathlib import Path
LOG = Path(__file__).with_name("calls.jsonl")
with LOG.open("a") as log:
    log.write(json.dumps({"argv": sys.argv[1:], "env_names": sorted(os.environ),
                          "marker": os.environ.get("NOMOUSE_FAKE_MARKER"), "pid": os.getpid(),
                          "cwd": os.getcwd(), "cwd_files": os.listdir(".")}) + "\\n")
CALL = len(LOG.read_text().splitlines())
ANSWER = %s
def report(**extra):
    data = {"type": "result", "subtype": "success", "is_error": False, "result": "",
            "duration_ms": 1500, "total_cost_usd": 0.0125,
            "modelUsage": {"claude-sonnet-4-6": {"inputTokens": 900, "outputTokens": 120}},
            "structured_output": ANSWER}
    data.update(extra)
    print(json.dumps({k: v for k, v in data.items() if v is not None}))
"""

FAKES = {
    "ok": "report()",
    "malformed": 'print("Error: the model said {route: barrier")',
    "no_structured_output": "report(structured_output=None)",
    "string_output": 'report(structured_output="{}")',
    "is_error": 'report(is_error=True, subtype="error_during_execution", structured_output=None)',
    "exit_status": 'report(); sys.stderr.write("boom\\n"); sys.exit(3)',
    "sleeps": "time.sleep(30)",
    "flaky": """
if CALL == 1:
    report(is_error=True, subtype="error_max_turns", structured_output=None, total_cost_usd=0.0025,
           modelUsage={"claude-haiku-4-5": {"inputTokens": 50}})
else:
    report()
""",
}


def fake_cli(tmp_path: Path, behaviour: str) -> str:
    """An executable that imitates `claude -p ... --output-format json`."""
    script = tmp_path / "fake_claude.py"
    script.write_text(FAKE_PREAMBLE % repr(ANSWER) + FAKES[behaviour] + "\n", encoding="utf-8")
    # A shell wrapper, since the interpreter's path may contain spaces a shebang cannot hold.
    command = tmp_path / "claude"
    command.write_text(f'#!/bin/sh\nexec "{sys.executable}" -I "{script}" "$@"\n', encoding="utf-8")
    command.chmod(0o755)
    return str(command)


def calls(tmp_path: Path) -> list[dict]:
    log = tmp_path / "calls.jsonl"
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def test_the_stand_in_is_labelled_as_a_stand_in():
    assert StandInModel().label == "stand-in claude-sonnet-4-6 via claude -p (not GitLab Duo)"


def test_a_good_answer_comes_back_with_usage(tmp_path, journey):
    system, user = render_prompt(failed_block(journey, ""), TEMPLATE, template_source())
    reply = StandInModel(command=fake_cli(tmp_path, "ok")).ask(system, user, "dev-icons/1")
    assert reply.answer == ANSWER and reply.error == ""
    assert reply.meta["models"] == ["claude-sonnet-4-6"] and reply.meta["attempts"] == 1
    assert reply.meta["total_cost_usd"] == pytest.approx(0.0125) and reply.meta["duration_ms"] == 1500


def test_the_cli_gets_no_tools_the_schema_and_the_exact_prompt(tmp_path, journey):
    system, user = render_prompt(failed_block(journey, 'a "quoted" $HOME `name`'), TEMPLATE, template_source())
    StandInModel(model_id="claude-test-model", command=fake_cli(tmp_path, "ok")).ask(system, user, "k")
    [call] = calls(tmp_path)
    argv = call["argv"]

    def after(flag: str) -> str:
        return argv[argv.index(flag) + 1]

    assert argv[:3] == ["-p", "--model", "claude-test-model"]
    assert after("--tools") == "" and after("--setting-sources") == ""
    assert "--no-session-persistence" in argv and "--strict-mcp-config" in argv
    assert after("--output-format") == "json"
    assert json.loads(after("--json-schema")) == SCHEMA
    # Passed as arguments without a shell: quotes, dollars and backticks arrive as written.
    assert after("--system-prompt") == system and argv[-1] == user


def test_secrets_are_not_handed_to_the_cli(tmp_path, monkeypatch):
    for name in SECRET_ENV:
        monkeypatch.setenv(name, "fake-value-for-this-test")
    monkeypatch.setenv("NOMOUSE_FAKE_MARKER", "present")
    StandInModel(command=fake_cli(tmp_path, "ok")).ask("system", "user", "k")
    [call] = calls(tmp_path)
    assert call["marker"] == "present"  # the rest of the environment is passed through
    assert not set(SECRET_ENV) & set(call["env_names"])
    assert {"GITLAB_TOKEN", "GITLAB_OAUTH_TOKEN", "RELAY_KEY", "DEMO_KEY", "NTFY_URL"} <= set(SECRET_ENV)


def test_the_cli_runs_in_an_empty_directory_so_no_project_notes_reach_it(tmp_path):
    StandInModel(command=fake_cli(tmp_path, "ok")).ask("system", "user", "k")
    [call] = calls(tmp_path)
    assert call["cwd_files"] == []
    assert not Path(call["cwd"]).resolve().is_relative_to(REPO)
    assert not Path(call["cwd"]).exists()  # and the directory is removed afterwards


@pytest.mark.parametrize("behaviour, error", [
    ("malformed", "not a JSON object"),
    ("no_structured_output", "no structured_output"),
    ("string_output", "no structured_output"),
    ("is_error", "reported an error: error_during_execution"),
    ("exit_status", "exit status 3"),
])
def test_a_failed_answer_is_retried_then_reported_without_raising(tmp_path, behaviour, error):
    reply = StandInModel(retries=1, command=fake_cli(tmp_path, behaviour)).ask("system", "user", "k")
    assert reply.answer is None and error in reply.error
    assert reply.meta["attempts"] == 2 and len(calls(tmp_path)) == 2


def test_retries_zero_means_one_call(tmp_path):
    reply = StandInModel(retries=0, command=fake_cli(tmp_path, "malformed")).ask("system", "user", "k")
    assert reply.answer is None and reply.meta["attempts"] == 1 and len(calls(tmp_path)) == 1


def test_retries_are_capped(tmp_path):
    reply = StandInModel(retries=50, command=fake_cli(tmp_path, "malformed")).ask("system", "user", "k")
    assert reply.meta["attempts"] == 4 and len(calls(tmp_path)) == 4


def test_a_retry_can_succeed_and_usage_counts_every_attempt(tmp_path):
    reply = StandInModel(retries=1, command=fake_cli(tmp_path, "flaky")).ask("system", "user", "k")
    assert reply.answer == ANSWER and reply.error == ""
    assert reply.meta["attempts"] == 2 and reply.meta["errors"] == ["the CLI reported an error: error_max_turns"]
    assert reply.meta["models"] == ["claude-haiku-4-5", "claude-sonnet-4-6"]
    assert reply.meta["total_cost_usd"] == pytest.approx(0.015)


def test_a_slow_cli_is_killed_at_the_timeout(tmp_path):
    started = time.monotonic()
    reply = StandInModel(timeout=0.5, retries=1, command=fake_cli(tmp_path, "sleeps")).ask("system", "user", "k")
    assert time.monotonic() - started < 10
    assert reply.answer is None and reply.error == "timed out after 0.5s" and reply.meta["attempts"] == 2
    for call in calls(tmp_path):
        with pytest.raises(ProcessLookupError):
            os.kill(call["pid"], 0)  # the sleeping fake is gone, not left running


def test_a_missing_cli_is_reported_once(tmp_path):
    reply = StandInModel(retries=3, command=str(tmp_path / "no-such-claude")).ask("system", "user", "k")
    assert reply.answer is None and "could not start" in reply.error and reply.meta["attempts"] == 1


# The recorded model


def recording(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "recorded-test-answers.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_a_recording_answers_by_key(tmp_path):
    model = RecordedModel(recording(tmp_path, {"label": "sonnet run (test data)",
                                               "answers": {"dev-icons/1": ANSWER, "dev-icons/2": None}}))
    assert model.label == "recorded: sonnet run (test data)"
    hit = model.ask("system", "user", "dev-icons/1")
    assert hit.answer == ANSWER and hit.error == ""
    miss = model.ask("system", "user", "dev-rename/1")
    assert miss.answer is None and miss.error == "no recorded answer for dev-rename/1" and miss.meta == {}
    failed_then = model.ask("system", "user", "dev-icons/2")
    assert failed_then.answer is None and failed_then.error


@pytest.mark.parametrize("data", [
    {"label": "x"},
    {"label": "x", "answers": ["not", "a", "map"]},
    {"label": "x", "answers": {"dev-icons/1": "a string, not an answer"}},
    ["not an object"],
])
def test_a_malformed_recording_is_refused_on_load(tmp_path, data):
    with pytest.raises(ValueError):
        RecordedModel(recording(tmp_path, data))


# Applying a fix


@pytest.fixture
def variants(tmp_path) -> Path:
    root = tmp_path / "variants"
    shutil.copytree(REPO / "nomouse" / "variants", root)
    return root


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_a_fix_becomes_a_new_variant_and_the_original_is_untouched(variants):
    before = snapshot(variants)
    repo_before = (REPO / TEMPLATE).read_bytes(), (REPO / "nomouse/shop/templates/checkout.html").read_bytes()
    name = apply_fix(variants, "dev-icons", PAY_FIX, REPO)
    assert re.fullmatch(r"dev-icons-fix-[0-9a-f]{8}", name) and NAME.match(name)
    fixed = (variants / name / "templates" / "checkout.html").read_text(encoding="utf-8")
    original = (variants / "dev-icons" / "templates" / "checkout.html").read_text(encoding="utf-8")
    assert fixed == original.replace(PAY_FIX.find, PAY_FIX.replace)
    assert fixed.count('aria-label="Pay now, $18.00"') == 1
    after = snapshot(variants)
    assert {key: value for key, value in after.items() if not key.startswith(name + "/")} == before
    assert repo_before == ((REPO / TEMPLATE).read_bytes(), (REPO / "nomouse/shop/templates/checkout.html").read_bytes())
    assert json.loads((variants / name / "fix.json").read_text())["from"] == "dev-icons"


def test_the_same_fix_twice_gives_the_same_variant_and_another_fix_a_new_one(variants):
    first = apply_fix(variants, "dev-icons", PAY_FIX, REPO)
    assert apply_fix(variants, "dev-icons", PAY_FIX, REPO) == first
    other = Fix(file=PAY_FIX.file, find=PAY_FIX.find, replace='<button type="submit" aria-label="Pay now">')
    assert apply_fix(variants, "dev-icons", other, REPO) != first
    assert len([p for p in variants.iterdir() if p.name.startswith("dev-icons-fix-")]) == 2


def test_a_fix_to_a_base_page_is_copied_into_the_new_variant(variants):
    base_cart = REPO / "nomouse" / "shop" / "templates" / "cart.html"
    before = base_cart.read_bytes()
    fix = Fix(file="nomouse/shop/templates/cart.html", find='<a href="/checkout">Checkout</a>',
              replace='<a href="/checkout">Checkout, $price</a>')
    name = apply_fix(variants, "dev-icons", fix, REPO)
    templates = variants / name / "templates"
    assert sorted(p.name for p in templates.iterdir()) == ["cart.html", "checkout.html"]
    assert "Checkout, $price</a>" in (templates / "cart.html").read_text(encoding="utf-8")
    # The variant's own override comes along unchanged, so the rest of the walk is the same.
    assert (templates / "checkout.html").read_bytes() == (variants / "dev-icons" / "templates" / "checkout.html").read_bytes()
    assert base_cart.read_bytes() == before


def test_a_fix_naming_a_base_page_the_variant_overrides_works_on_the_served_page(variants):
    fix = Fix(file="nomouse/shop/templates/checkout.html", find='<button type="submit"><svg',
              replace='<button type="submit" aria-label="Pay now, $18.00"><svg')
    name = apply_fix(variants, "dev-icons", fix, REPO)
    assert 'aria-label="Pay now, $18.00"' in (variants / name / "templates" / "checkout.html").read_text()


@pytest.mark.parametrize("variant, fix, message", [
    ("dev-icons", Fix(TEMPLATE, '<button type="submit" disabled>', "x"), "occurs nowhere"),
    ("dev-icons", Fix(TEMPLATE, '<button type="button"', "<button"), "more than once"),
    ("dev-icons", Fix(TEMPLATE, "", "x"), "non-empty"),
    ("dev-icons", Fix(TEMPLATE, "<h1>", "x" * 2_001), "at most 2000"),
    ("dev-icons", Fix("nomouse/variants/dev-icons/templates/../../dev-rename/templates/checkout.html",
                      "<h1>", "x"), "fix.file must be"),
    ("dev-icons", Fix("nomouse/shop/templates/../../../pyproject.toml", "name", "x"), "fix.file must be"),
    ("dev-icons", Fix("/etc/passwd", "root", "x"), "fix.file must be"),
    ("dev-icons", Fix("./nomouse/shop/templates/checkout.html", "<h1>", "x"), "fix.file must be"),
    ("dev-icons", Fix("nomouse/shop/templates/sub/checkout.html", "<h1>", "x"), "fix.file must be"),
    ("dev-icons", Fix("nomouse/shop/templates/checkout.html\n", "<h1>", "x"), "fix.file must be"),
    ("dev-icons", Fix("nomouse/variants/dev-rename/templates/checkout.html", "<h1>", "x"), "fix.file must be"),
    ("dev-icons", Fix("nomouse/variants/dev-icons/templates/cart.html", "<h1>", "x"), "does not override"),
    ("dev-icons", Fix("nomouse/shop/templates/missing.html", "<h1>", "x"), "not a plain template"),
    ("../dev-icons", PAY_FIX, "not a variant name"),
    ("Dev-Icons", PAY_FIX, "not a variant name"),
    ("no-such-variant", Fix("nomouse/shop/templates/cart.html", "<h1>", "x"), "no variant"),
])
def test_bad_fixes_are_refused_and_write_nothing(variants, variant, fix, message):
    before = snapshot(variants)
    with pytest.raises(FixError, match=message):
        apply_fix(variants, variant, fix, REPO)
    assert snapshot(variants) == before


def test_a_template_linked_from_outside_the_variants_is_refused(variants, tmp_path):
    outside = tmp_path / "outside.html"
    outside.write_text("<h1>Checkout</h1>", encoding="utf-8")
    (variants / "linked" / "templates").mkdir(parents=True)
    (variants / "linked" / "templates" / "checkout.html").symlink_to(outside)
    fix = Fix("nomouse/variants/linked/templates/checkout.html", "<h1>", "<h1 id=x>")
    with pytest.raises(FixError, match="not a plain template"):
        apply_fix(variants, "linked", fix, REPO)


# The fixed variant, walked for real


@pytest.fixture
def isolated_walker(variants):
    """A shop serving the temporary variants, and a Walker on it."""
    try:
        from nomouse.server import serve
        from nomouse.walker import Walker
    except ImportError:
        if os.environ.get("NOMOUSE_REQUIRE_BROWSER") == "1":
            pytest.fail("Playwright is required in this job but is not installed")
        pytest.skip("Playwright is not installed; the browser job runs these tests")
    with serve(variants) as base:
        walker = Walker(base)
        try:
            walker.__enter__()
        except Exception as exc:  # the Chromium binary itself may be missing
            walker.__exit__(None, None, None)
            if os.environ.get("NOMOUSE_REQUIRE_BROWSER") == "1":
                raise
            pytest.skip(f"Chromium is not available: {exc}")
        try:
            yield walker
        finally:
            walker.__exit__(None, None, None)


def walk(walker, journey, variant: str | None) -> Result:
    session = walker.open(variant=variant)
    try:
        return replay(session, journey)
    finally:
        session.close()


@pytest.mark.browser
def test_the_fixed_variant_can_be_walked_and_places_one_order(variants, isolated_walker, journey):
    name = apply_fix(variants, "dev-icons", PAY_FIX, REPO)
    fixed = walk(isolated_walker, journey, name)
    assert fixed.clear, f"{fixed.verdict}: {fixed.reason}"
    assert [(o["item"], o["quantity"]) for o in fixed.orders] == [("ethiopia", 1)]
    # The fixed variant was really served, not the base shop: the walk had to Tab past the
    # two icon buttons that are still there in front of the pay button.
    base = walk(isolated_walker, journey, None)
    assert base.clear and fixed.keys == base.keys + 2
