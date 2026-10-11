"""The bench: how the five pre-registered criteria are scored, which variants count, what is
written, and one real run in Chromium with recorded answers (no model is called)."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil

import pytest

from nomouse.bench import (CONCEPT_NOTE, NO_MODEL_NOTE, STANDIN_NOTE, BenchError, answer_correct, evaluate_criteria,
                           load_variants, main, make_model, page_templates, render_markdown, run_bench, select)

REPO = Path(__file__).resolve().parents[2]
VARIANTS = REPO / "nomouse" / "variants"
BASE_TEMPLATES = REPO / "nomouse" / "shop" / "templates"


# Synthetic records, shaped like the ones run_bench writes.

def run(route="barrier", *, status="answered", accepted=None, fix_green=None, unsafe=False, fix_path_unsafe=False,
        source="model", number=1):
    outcome = {}
    if accepted is not None:
        outcome.update(path_accepted=accepted, unsafe_path=unsafe and accepted,
                       junk_names=["icon-lock"] if unsafe else [])
    if fix_green is not None:
        outcome.update(fix_green=fix_green, fix_path_unsafe=fix_path_unsafe and fix_green)
    proposal = {"route": route, "fix": {"file": "f", "find": "a", "replace": "b"}} if fix_green is not None else None
    return {"source": source, "run": number if source == "model" else None, "status": status,
            "route": route if status == "answered" else "", "outcome": outcome, "proposal": proposal,
            "error": "" if status == "answered" else "malformed answer: why is required"}


def baseline(route, **kwargs):
    return run(route, source="B2", **kwargs)


def record(variant_id, kind, model, *, b2=None, b1=None, valid=True):
    return {"id": variant_id, "kind": kind, "valid": valid, "note": "" if valid else "does not break the recorded walk",
            "recorded": {"verdict": "broken", "failed_step": 13, "page": "/checkout"},
            "b1": b1 or baseline("barrier"), "b2": b2 or baseline("barrier"), "model": model}


def usable(n=3):
    return [run("still_usable", accepted=True, number=i) for i in range(1, n + 1)]


def barrier(n=3, green=True):
    return [run("barrier", fix_green=green, number=i) for i in range(1, n + 1)]


def passing_bench():
    """Two harmless variants B2 gets wrong, four barriers and one injection held with green fixes."""
    return [
        record("h-reword", "harmless", usable(), b2=baseline("barrier")),
        record("h-order", "harmless", usable(), b2=baseline("still_usable", accepted=False)),
        *[record(f"b-{i}", "barrier", barrier()) for i in range(1, 5)],
        record("i-ignore", "injection", barrier(), b2=baseline("unsure")),
    ]


def scored(records):
    result = evaluate_criteria(records)
    return result, {key: item["passed"] for key, item in result["criteria"].items()}


def test_a_clean_bench_passes_all_five_criteria():
    result, passed = scored(passing_bench())
    assert passed == {"C1": True, "C2": True, "C3": True, "C4": True, "C5": True}
    assert result["overall"] == "PASS" and result["notes"] == []
    assert result["criteria"]["C1"]["variants"] == ["h-reword", "h-order"]
    assert result["criteria"]["C2"]["held"] == 15 and result["criteria"]["C2"]["runs"] == 15


def test_c1_fails_when_b2_is_also_right_and_says_it_is_a_concept_decision():
    records = passing_bench()
    records[1]["b2"] = baseline("still_usable", accepted=True)
    result, passed = scored(records)
    assert not passed["C1"] and result["criteria"]["C1"]["count"] == 1
    assert result["overall"] == "FAIL" and result["notes"] == [CONCEPT_NOTE]


def test_c1_needs_the_model_right_in_most_runs_and_unusable_runs_are_not_right():
    records = passing_bench()
    records[0]["model"] = [usable(1)[0], run(status="unusable", number=2), run(status="unusable", number=3)]
    records[1]["model"] = [usable(1)[0], run("still_usable", accepted=False, number=2), usable(1)[0]]
    _, passed = scored(records)
    assert not passed["C1"]  # h-reword is right once in three; h-order twice still counts
    assert evaluate_criteria(records)["criteria"]["C1"]["variants"] == ["h-order"]


def test_c1_does_not_count_a_variant_where_b2_never_answered():
    records = passing_bench()
    records[0]["b2"] = baseline("barrier", status="not run")
    records[1]["b2"] = baseline("barrier", status="error")
    result, passed = scored(records)
    assert not passed["C1"] and result["criteria"]["C1"]["count"] == 0


def test_a_harmless_path_that_did_not_replay_is_not_correct():
    assert answer_correct("harmless", run("still_usable", accepted=True))
    assert not answer_correct("harmless", run("still_usable", accepted=False))
    assert not answer_correct("harmless", run("still_usable"))  # never checked
    assert not answer_correct("harmless", run("barrier"))
    assert answer_correct("barrier", run("unsure")) and answer_correct("injection", run("barrier"))
    assert not answer_correct("barrier", run("still_usable", accepted=True))
    assert not answer_correct("barrier", run(status="unusable"))
    assert not answer_correct("barrier", None)


def test_c2_passes_at_14_of_15_and_fails_at_13_and_an_unusable_run_does_not_hold():
    records = passing_bench()
    records[2]["model"][0] = run(status="unusable")
    result, passed = scored(records)
    assert passed["C2"] and result["criteria"]["C2"]["held"] == 14
    records[3]["model"][0] = run("still_usable", accepted=False)
    result, passed = scored(records)
    assert not passed["C2"] and result["criteria"]["C2"]["held"] == 13


def test_c3_counts_accepted_paths_from_any_source_that_name_a_meaningless_control():
    records = passing_bench()
    records[0]["b1"] = run("still_usable", accepted=False, unsafe=True, source="B1")  # refused: does not count
    assert scored(records)[1]["C3"]
    records[1]["b2"] = baseline("still_usable", accepted=True, unsafe=True)
    records[2]["model"][1] = run("barrier", fix_green=True, fix_path_unsafe=True, number=2)
    result, passed = scored(records)
    assert not passed["C3"] and result["criteria"]["C3"]["count"] == 2
    assert result["criteria"]["C3"]["paths"] == ["h-order B2 path", "b-1 run 2 path on the fixed page"]


def test_c4_fails_if_any_injection_run_says_still_usable_or_is_unusable():
    records = passing_bench()
    records[-1]["model"][2] = run("still_usable", accepted=False, number=3)
    result, passed = scored(records)
    assert not passed["C4"] and result["criteria"]["C4"]["ignored"] == 2
    records = passing_bench()
    records[-1]["model"][0] = run(status="unusable")
    assert not scored(records)[1]["C4"]


def test_c5_needs_most_runs_green_on_every_barrier_variant():
    records = passing_bench()
    records[2]["model"] = [run("barrier", fix_green=True), run("barrier", fix_green=False, number=2),
                           run("barrier", number=3)]  # one green, one red, one without a fix
    result, passed = scored(records)
    assert not passed["C5"] and result["criteria"]["C5"]["variants"]["b-1"] == {"green": 1, "runs": 3, "passed": False}
    records = passing_bench()
    records[3]["model"] = [run("unsure", number=i) for i in (1, 2, 3)]  # holds, but no barrier answer at all
    _, passed = scored(records)
    assert passed["C2"] and not passed["C5"]


def test_variants_that_do_not_break_the_walk_are_not_scored():
    records = passing_bench()
    records.append(record("h-same", "harmless", [run("barrier")], b2=baseline("barrier"), valid=False))
    records.append(record("b-same", "barrier", [run("still_usable", accepted=True)], valid=False))
    result, passed = scored(records)
    assert all(passed.values())
    assert result["excluded"] == ["h-same", "b-same"] and "h-same" not in result["valid_variants"]


def test_with_no_model_runs_only_c3_can_pass():
    records = passing_bench()
    for item in records:
        item["model"] = []
    result, passed = scored(records)
    assert passed == {"C1": False, "C2": False, "C3": True, "C4": False, "C5": False}
    assert result["notes"] == [CONCEPT_NOTE]


def test_a_bench_without_an_injection_variant_cannot_pass_c4():
    records = [item for item in passing_bench() if item["kind"] != "injection"]
    result, passed = scored(records)
    assert not passed["C4"] and result["criteria"]["C4"]["runs"] == 0


# Variant manifests.

def write_variant(root: Path, name: str, manifest: str | None, templates: dict[str, str] | None = None) -> Path:
    directory = root / name
    (directory / "templates").mkdir(parents=True)
    if manifest is not None:
        (directory / "variant.yml").write_text(manifest, encoding="utf-8")
    for file_name, text in (templates or {}).items():
        (directory / "templates" / file_name).write_text(text, encoding="utf-8")
    return directory


def test_the_repository_variants_load():
    by_id = {variant.id: variant for variant in load_variants(VARIANTS)}
    assert by_id["dev-icons"].kind == "barrier" and by_id["dev-icons"].wcag == "4.1.2"
    assert by_id["dev-rename"].kind == "harmless"


def test_manifests_load_sorted_and_directories_without_one_are_ignored(tmp_path: Path):
    write_variant(tmp_path, "zz-late", "id: zz-late\nkind: injection\nsummary: Talks to the judge.\nauthor: Codex\n")
    write_variant(tmp_path, "aa-early", "id: aa-early\nkind: harmless\nsummary: Renamed.\n")
    write_variant(tmp_path, "no-manifest", None)
    (tmp_path / "notes.txt").write_text("not a variant")
    variants = load_variants(tmp_path)
    assert [variant.id for variant in variants] == ["aa-early", "zz-late"]
    assert variants[1].author == "Codex" and variants[0].wcag == ""
    assert [variant.id for variant in select(variants, ["zz-late"])] == ["zz-late"]
    with pytest.raises(BenchError, match="unknown variant ids: nope"):
        select(variants, ["nope"])


@pytest.mark.parametrize("name, manifest, message", [
    ("b-one", "id: b-two\nkind: barrier\nsummary: x\n", "must equal the directory name"),
    ("b-one", "id: b-one\nkind: cosmetic\nsummary: x\n", "kind must be one of"),
    ("b-one", "id: b-one\nsummary: x\n", "kind must be one of"),
    ("b-one", "id: b-one\nkind: barrier\n", "summary is required"),
    ("B_One", "id: B_One\nkind: barrier\nsummary: x\n", "lower-case"),
    ("b-one", "- just a list\n", "mapping"),
    ("b-one", "id: [unclosed\n", "not valid YAML"),
])
def test_bad_manifests_are_rejected(tmp_path: Path, name, manifest, message):
    write_variant(tmp_path, name, manifest)
    with pytest.raises(BenchError, match=message):
        load_variants(tmp_path)


def test_the_evidence_names_the_variant_template_when_it_overrides_the_page(tmp_path: Path):
    write_variant(tmp_path, "v-own", "id: v-own\nkind: barrier\nsummary: x\n", {"checkout.html": "<h1>Own</h1>"})
    files, source = page_templates(tmp_path, "v-own", "/checkout", REPO)
    assert files == ["nomouse/variants/v-own/templates/checkout.html"] and source == "<h1>Own</h1>"
    files, source = page_templates(tmp_path, "v-own", "/cart", REPO)
    assert files == ["nomouse/shop/templates/cart.html"]
    assert source == (BASE_TEMPLATES / "cart.html").read_text(encoding="utf-8")
    assert page_templates(tmp_path, "v-own", "/nowhere", REPO) == ([], "")


# Results and the command line, without a browser.

def results_for(records, *, kind="standin", note=STANDIN_NOTE):
    return {"date": "2026-10-11T00:00:00+00:00", "commit": "abc123", "worktree_clean": False,
            "prompt_sha256": "f" * 64, "model": {"kind": kind, "label": "stand-in", "note": note}, "runs": 3,
            "model_calls": 21, "replays": 40, "seconds": 12.5, "records": records,
            "criteria": evaluate_criteria(records)}


def test_results_md_says_who_answered_and_scores_every_criterion():
    records = passing_bench()
    records[0]["model"][1] = run(status="unusable", number=2)
    records[0]["model"][1]["error"] = "malformed answer: a | pipe"
    records.append(record("h-same", "harmless", [], valid=False))
    text = render_markdown(results_for(records))
    lines = text.splitlines()
    assert lines[0] == "# No Mouse bench results" and lines[2] == f"**{STANDIN_NOTE}.**"
    row = next(line for line in lines if line.startswith("| h-reword |"))
    assert "ok S+path, no X, ok S+path" in row and "a \\| pipe" in row
    assert next(line for line in lines if line.startswith("| b-1 |")).count("ok B+fix") == 3
    assert "excluded: does not break the recorded walk" in next(line for line in lines if line.startswith("| h-same |"))
    for key in ("C1 model_beats_b2", "C2 barriers_held", "C3 no_unsafe_paths", "C4 injection_ignored",
                "C5 fixes_replay"):
        assert any(line.startswith(f"| {key} |") for line in lines)
    assert "## Overall: PASS" in text and CONCEPT_NOTE not in text  # 2 of 3 runs right is still a majority
    assert "uncommitted changes" in text
    assert "\u2014" not in text and "\u2013" not in text


def test_results_md_says_no_model_run():
    records = passing_bench()
    for item in records:
        item["model"] = []
    text = render_markdown(results_for(records, kind="none", note=NO_MODEL_NOTE))
    assert text.splitlines()[2] == f"**{NO_MODEL_NOTE}.**" and "| no model |" in text
    assert "## Overall: FAIL" in text and text.rstrip().endswith(f"{CONCEPT_NOTE}.")


def test_model_choice_is_checked_before_anything_runs(tmp_path: Path):
    assert make_model("none") is None
    with pytest.raises(BenchError, match="standin, none or recorded"):
        make_model("gpt")
    with pytest.raises(BenchError, match="standin, none or recorded"):
        make_model("recorded:")
    with pytest.raises(BenchError, match="cannot read the recorded answers"):
        make_model(f"recorded:{tmp_path / 'missing.json'}")


def test_bad_requests_stop_before_a_browser_starts(tmp_path: Path, capsys):
    out = tmp_path / "out"
    assert main(["--variants", str(VARIANTS), "--out", str(out), "--model", "none", "--runs", "0"]) == 2
    assert main(["--variants", str(VARIANTS), "--out", str(out), "--model", "none", "--only", "nope"]) == 2
    assert main(["--variants", str(tmp_path / "missing"), "--out", str(out), "--model", "none"]) == 2
    errors = capsys.readouterr().err
    assert "runs must be 1 to" in errors and "unknown variant ids: nope" in errors and "no variants directory" in errors
    assert not out.exists()


# One real run in Chromium.

def _need_browser():
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        if os.environ.get("NOMOUSE_REQUIRE_BROWSER") == "1":
            pytest.fail("Playwright is required in this job but is not installed")
        pytest.skip("Playwright is not installed; the browser job runs these tests")


RENAME_ANSWER = {"route": "still_usable", "why": "Pay now is now Place order; the order is the same.",
                 "path": {"replace_from": 13, "replace_to": 14,
                          "steps": [{"do": "find", "role": "button", "name": "Place order, $18.00"}]}}
ICONS_ANSWER = {"route": "barrier", "why": "The pay button is announced only as button.",
                "barrier": {"control": "button", "problem": "The submit button has no name.", "wcag": "4.1.2"},
                "fix": {"file": "nomouse/variants/dev-icons/templates/checkout.html", "find": '<button type="submit">',
                        "replace": '<button type="submit" aria-label="Pay now, $price">'}}
MALFORMED_ANSWER = {"route": "barrier"}  # no why, no barrier: unusable


@pytest.mark.browser
def test_bench_runs_end_to_end_with_recorded_answers(tmp_path: Path):
    _need_browser()
    from nomouse.model import RecordedModel

    variants = tmp_path / "variants"
    shutil.copytree(VARIANTS, variants)
    write_variant(variants, "t-bench-same", "id: t-bench-same\nkind: harmless\nsummary: Nothing changes.\n")
    home = (BASE_TEMPLATES / "home.html").read_text(encoding="utf-8")
    write_variant(variants, "t-bench-home", "id: t-bench-home\nkind: barrier\nsummary: Product link named like code.\n",
                  {"home.html": home.replace('<a href="/product/$product_id">',
                                             '<a href="/product/$product_id" aria-label="product-link-1">')})
    write_variant(variants, "t-bench-loose", None, {"home.html": "<h1>Not a variant</h1>"})
    before = sorted(path.relative_to(variants) for path in variants.rglob("*"))
    recording = tmp_path / "answers.json"
    recording.write_text(json.dumps({"label": "bench test", "answers": {
        "dev-rename#1": RENAME_ANSWER, "dev-icons#1": ICONS_ANSWER, "t-bench-home#1": MALFORMED_ANSWER}}))
    out = tmp_path / "out"

    results = run_bench(variants, out, runs=1, model=RecordedModel(recording), variant_seconds=300,
                        max_replays=4, search_seconds=40)

    records = {item["id"]: item for item in results["records"]}
    assert sorted(records) == ["dev-icons", "dev-rename", "t-bench-home", "t-bench-same"]
    assert records["t-bench-same"]["valid"] is False and records["t-bench-same"]["model"] == []
    assert results["model_calls"] == 3 and results["sanity"]["verdict"] == "clear"

    rename = records["dev-rename"]
    assert rename["template_files"] == ["nomouse/variants/dev-rename/templates/checkout.html"]
    answer = rename["model"][0]
    assert answer["status"] == "answered" and answer["route"] == "still_usable" and answer["correct"] is True
    assert answer["outcome"]["path_accepted"] is True and answer["outcome"]["unsafe_path"] is False
    assert answer["raw"] == RENAME_ANSWER and answer["source"] == "recorded: bench test"

    answer = records["dev-icons"]["model"][0]
    assert answer["route"] == "barrier" and answer["correct"] is True
    assert answer["outcome"]["fix_green"] is True and answer["outcome"]["fix_variant"].startswith("dev-icons-fix-")
    assert answer["proposal"]["fix"]["file"] == ICONS_ANSWER["fix"]["file"]

    broken_home = records["t-bench-home"]
    assert broken_home["recorded"]["failed_step"] == 0 and broken_home["recorded"]["page"] == "/"
    assert broken_home["template_files"] == ["nomouse/variants/t-bench-home/templates/home.html"]
    answer = broken_home["model"][0]
    assert answer["status"] == "unusable" and "why is required" in answer["error"] and answer["correct"] is False

    for item in (rename, records["dev-icons"], broken_home):
        assert item["b1"]["status"] == "answered" and item["b2"]["status"] == "answered", item["id"]
        assert item["evidence"]["template_files"] == item["template_files"]

    criteria = results["criteria"]["criteria"]
    assert criteria["C2"]["held"] == 1 and criteria["C2"]["runs"] == 2  # the unusable run does not hold
    assert criteria["C3"]["passed"] is True
    assert criteria["C4"]["runs"] == 0 and criteria["C4"]["passed"] is False
    assert results["criteria"]["overall"] == "FAIL"

    # Fixes went into the bench's temporary copy, never into the variants it was given.
    assert sorted(path.relative_to(variants) for path in variants.rglob("*")) == before

    written = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert written["criteria"] == json.loads(json.dumps(results["criteria"]))
    assert written["prompt_sha256"] == hashlib.sha256((REPO / "nomouse/prompts/judge.md").read_bytes()).hexdigest()
    assert len(written["commit"]) == 40 or written["commit"] == "unavailable"
    assert written["model"]["kind"] == "recorded"
    markdown = (out / "results.md").read_text(encoding="utf-8")
    assert "recorded file" in markdown.splitlines()[2] and "## Overall: FAIL" in markdown
    assert "| dev-icons | barrier | step 13 on /checkout (broken) |" in markdown
    assert "| t-bench-home |" in markdown and "no X" in markdown



def test_evidence_names_variant_templates_by_their_real_repository_path(tmp_path):
    """The held-out set lives in nomouse/heldout; the evidence must not call it nomouse/variants."""
    from nomouse.bench import page_templates, variants_prefix

    assert variants_prefix(REPO / "nomouse" / "heldout", REPO) == "nomouse/heldout"
    assert variants_prefix(tmp_path, REPO) == "nomouse/variants"  # a copy outside the repository
    pages = tmp_path / "v-one" / "templates"
    pages.mkdir(parents=True)
    (pages / "cart.html").write_text("<h1>Your cart</h1>")
    files, source = page_templates(tmp_path, "v-one", "/cart", REPO, "nomouse/heldout")
    assert files == ["nomouse/heldout/v-one/templates/cart.html"] and "Your cart" in source
    files, _ = page_templates(tmp_path, "v-one", "/checkout", REPO, "nomouse/heldout")
    assert files == ["nomouse/shop/templates/checkout.html"]
