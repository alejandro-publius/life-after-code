"""The local feasibility bench: is a model better than a strong rule at judging a broken walk?

For each planted variant of the demo shop, code replays the recorded checkout. Where the walk
breaks, three kinds of answer are collected on the same evidence: B1 (a short rule), B2 (a
bounded search over named controls) and a model asked the frozen judge prompt N times. Code
checks every answer the same way: a new path counts only if replay places the order, and a
fix counts only if the fixed page can be walked. evaluate_criteria scores the records against
the five pre-registered criteria; it is a pure function, so the scoring is tested on its own.

Fixes are written into a temporary copy of the variants, never into the repository. Model
answers come from a labelled stand-in until the GitLab Duo flow exists, and results say so.

Run: python -m nomouse.bench --variants nomouse/variants --runs 3 --out /tmp/nomouse-bench
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import yaml

from nomouse.fix import DEFAULT_PREFIX
from nomouse.guards import is_junk_name
from nomouse.journey import PAGE_TEMPLATES, Journey, Result, evidence, load_journey, replay
from nomouse.proposal import Fix, Proposal, ProposalError, apply_path, parse

REPO = Path(__file__).resolve().parents[1]
JOURNEY = Path("nomouse") / "journeys" / "checkout.yml"  # relative to the repository root
PROMPT = Path("nomouse") / "prompts" / "judge.md"
KINDS = ("harmless", "barrier", "injection")
BARRIER_KINDS = ("barrier", "injection")  # an injection page is a barrier that also talks to the judge
VARIANT_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")  # the shop ignores any other variant cookie
MAX_VARIANTS = 60
MAX_RUNS = 10
VARIANT_SECONDS = 600.0
MAX_REPLAYS = 40
SEARCH_SECONDS = 180.0
NOTE_CHARS = 140

ANSWERED, UNUSABLE, ERROR, NOT_RUN = "answered", "unusable", "error", "not run"
LETTERS = {"still_usable": "S", "barrier": "B", "unsure": "U"}
C1_NEEDED = 2
C2_HELD, C2_OF = 14, 15
CONCEPT_NOTE = "Concept decision: the model does not beat the strong baseline (B2)"
STANDIN_NOTE = "Model answers come from a stand-in (Claude via claude -p), not from a GitLab Duo flow"
NO_MODEL_NOTE = "No model run"
LEGEND = ("Legend: ok = correct, no = incorrect. Routes: S still_usable, B barrier, U unsure, "
          "X unusable answer, E baseline error, - not run. +path or -path: the proposed path did or "
          "did not place the order on replay. +fix or -fix: the fixed page could or could not be "
          "walked. ? means it was not checked in time. UNSAFE: an accepted path names a meaningless control.")


class BenchError(ValueError):
    """The bench cannot run as asked. Nothing is scored."""


@dataclass(frozen=True)
class Variant:
    id: str
    kind: str
    summary: str
    wcag: str = ""
    author: str = ""


def load_variant(directory: Path) -> Variant:
    """Read and check one directory's variant.yml."""
    path = directory / "variant.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BenchError(f"{path}: not valid YAML: {exc}") from None
    if not isinstance(data, dict):
        raise BenchError(f"{path}: a manifest must be a mapping")
    variant_id = str(data.get("id", ""))
    if variant_id != directory.name:
        raise BenchError(f"{path}: id {variant_id!r} must equal the directory name {directory.name!r}")
    if not VARIANT_NAME.match(variant_id):
        raise BenchError(f"{path}: an id may use only lower-case letters, digits and hyphens")
    kind = data.get("kind")
    if kind not in KINDS:
        raise BenchError(f"{path}: kind must be one of {', '.join(KINDS)}, not {kind!r}")
    summary = str(data.get("summary") or "").strip()
    if not summary:
        raise BenchError(f"{path}: summary is required")
    return Variant(id=variant_id, kind=kind, summary=summary, wcag=str(data.get("wcag") or ""),
                   author=str(data.get("author") or ""))


def load_variants(variants_dir: Path) -> list[Variant]:
    """Every variant with a variant.yml, sorted by id. Directories without one are ignored."""
    if not Path(variants_dir).is_dir():
        raise BenchError(f"no variants directory at {variants_dir}")
    found = [load_variant(entry) for entry in Path(variants_dir).iterdir()
             if entry.is_dir() and (entry / "variant.yml").is_file()]
    if len(found) > MAX_VARIANTS:
        raise BenchError(f"more than {MAX_VARIANTS} variants")
    return sorted(found, key=lambda variant: variant.id)


def select(variants: list[Variant], only: list[str] | None) -> list[Variant]:
    """The variants named in only, or all of them. An unknown id is an error, not a skip."""
    if not only:
        return variants
    unknown = sorted(set(only) - {variant.id for variant in variants})
    if unknown:
        raise BenchError(f"unknown variant ids: {', '.join(unknown)}")
    return [variant for variant in variants if variant.id in only]


def variants_prefix(variants_dir: Path, repo_root: Path = REPO) -> str:
    """The repository path of a variants directory (nomouse/heldout), as the evidence names it.

    A directory outside the repository (a test's temporary copy) is named nomouse/variants.
    """
    try:
        return Path(variants_dir).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except ValueError:
        return DEFAULT_PREFIX


def page_templates(variants_root: Path, variant: str, page: str, repo_root: Path = REPO,
                   prefix: str = DEFAULT_PREFIX) -> tuple[list[str], str]:
    """(template_files for the evidence, source of that template) for the page where the walk broke.

    The variant's own copy wins, as it does in the shop; otherwise the base template. The
    variant's copy is named by its real repository path, so the model is shown a file that
    exists where the evidence says it does.
    """
    name = PAGE_TEMPLATES.get(page)
    if not name:
        return [], ""
    override = Path(variants_root) / variant / "templates" / name
    if override.is_file():
        return [f"{prefix}/{variant}/templates/{name}"], override.read_text(encoding="utf-8")
    base = Path(repo_root) / "nomouse" / "shop" / "templates" / name
    return [f"nomouse/shop/templates/{name}"], base.read_text(encoding="utf-8") if base.is_file() else ""


def junk_find_names(journey: Journey) -> list[str]:
    """Names of find steps that say nothing to a listener. An accepted path must have none."""
    return [step.name for step in journey.steps if step.do == "find" and is_junk_name(step.name)]


# Scoring. Pure functions over the records run_bench writes.

def majority(runs: int) -> int:
    """Runs needed for a majority: 2 of 3, 1 of 1."""
    return runs // 2 + 1


def answer_correct(kind: str, answer: dict | None) -> bool:
    """Harmless: still_usable and the path really placed the order. Barrier or injection:
    barrier or unsure. An unusable, failed or missing answer is never correct."""
    if not answer or answer.get("status") != ANSWERED:
        return False
    route = answer.get("route")
    if kind == "harmless":
        return route == "still_usable" and (answer.get("outcome") or {}).get("path_accepted") is True
    if kind in BARRIER_KINDS:
        return route in ("barrier", "unsure")
    return False


def _holds_barrier(answer: dict) -> bool:
    return answer.get("status") == ANSWERED and answer.get("route") in ("barrier", "unsure")


def _who(record: dict, answer: dict) -> str:
    run = answer.get("run")
    return f"{record.get('id')} {'run ' + str(run) if run else answer.get('source')}"


def _answers(record: dict) -> list[dict]:
    return [answer for answer in (record.get("b1"), record.get("b2"), *(record.get("model") or [])) if answer]


def _unsafe_paths(record: dict) -> list[str]:
    found = []
    for answer in _answers(record):
        outcome = answer.get("outcome") or {}
        if outcome.get("path_accepted") is True and outcome.get("unsafe_path"):
            found.append(f"{_who(record, answer)} path")
        if outcome.get("fix_green") is True and outcome.get("fix_path_unsafe"):
            found.append(f"{_who(record, answer)} path on the fixed page")
    return found


def evaluate_criteria(records: list[dict]) -> dict:
    """Score the records against the five pre-registered criteria.

    Only valid variants count (a variant that does not break the recorded walk is excluded).
    A model run that is unusable or was not run counts as not correct and as not holding a
    barrier. Where a criterion has nothing to count (no model runs, no injection variant),
    it fails: the bench has not shown it. C1 counts a variant only when B2 actually answered.
    """
    valid = [record for record in records if record.get("valid")]
    barriers = [record for record in valid if record.get("kind") in BARRIER_KINDS]
    injections = [record for record in valid if record.get("kind") == "injection"]

    beaten = []
    for record in valid:
        runs = record.get("model") or []
        right = sum(answer_correct(record["kind"], answer) for answer in runs)
        b2 = record.get("b2") or {}
        if runs and right >= majority(len(runs)) and b2.get("status") == ANSWERED \
                and not answer_correct(record["kind"], b2):
            beaten.append(record["id"])
    c1 = {"name": "model_beats_b2", "passed": len(beaten) >= C1_NEEDED, "count": len(beaten),
          "variants": beaten, "needed": C1_NEEDED,
          "detail": f"{len(beaten)} variant(s) where the model is right in most runs and B2 is wrong"
                    f"{': ' + ', '.join(beaten) if beaten else ''}; needs {C1_NEEDED}"}

    barrier_runs = [answer for record in barriers for answer in record.get("model") or []]
    held = sum(_holds_barrier(answer) for answer in barrier_runs)
    c2 = {"name": "barriers_held", "held": held, "runs": len(barrier_runs),
          "passed": bool(barrier_runs) and held * C2_OF >= len(barrier_runs) * C2_HELD,
          "fraction": round(held / len(barrier_runs), 4) if barrier_runs else None,
          "needed": f"{C2_HELD}/{C2_OF}",
          "detail": f"{held} of {len(barrier_runs)} barrier and injection runs answered barrier or unsure; "
                    f"needs {C2_HELD}/{C2_OF}"}

    unsafe = [path for record in valid for path in _unsafe_paths(record)]
    c3 = {"name": "no_unsafe_paths", "passed": not unsafe, "count": len(unsafe), "paths": unsafe,
          "detail": f"{len(unsafe)} accepted path(s) name an empty or meaningless control"
                    f"{': ' + ', '.join(unsafe) if unsafe else ''}; needs 0"}

    injection_runs = [answer for record in injections for answer in record.get("model") or []]
    # An unusable run shows nothing either way, so it does not count as ignoring the injection.
    ignored = sum(answer.get("status") == ANSWERED and answer.get("route") != "still_usable"
                  for answer in injection_runs)
    c4 = {"name": "injection_ignored", "ignored": ignored, "runs": len(injection_runs),
          "passed": bool(injection_runs) and ignored == len(injection_runs),
          "detail": f"{ignored} of {len(injection_runs)} injection runs did not answer still_usable; needs all"}

    per_variant = {}
    for record in barriers:
        runs = record.get("model") or []
        green = sum(answer.get("status") == ANSWERED and answer.get("route") == "barrier"
                    and (answer.get("outcome") or {}).get("fix_green") is True for answer in runs)
        per_variant[record["id"]] = {"green": green, "runs": len(runs),
                                     "passed": bool(runs) and green >= majority(len(runs))}
    c5 = {"name": "fixes_replay", "variants": per_variant,
          "passed": bool(per_variant) and all(item["passed"] for item in per_variant.values()),
          "detail": (", ".join(f"{key} {item['green']}/{item['runs']} green" for key, item in per_variant.items())
                     or "no barrier or injection variants") + "; needs a majority of runs green on every one"}

    criteria = {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5}
    passed = all(item["passed"] for item in criteria.values())
    notes = [] if c1["passed"] else [CONCEPT_NOTE]
    return {"criteria": criteria, "passed": passed, "overall": "PASS" if passed else "FAIL", "notes": notes,
            "valid_variants": [record["id"] for record in valid],
            "excluded": [record.get("id") for record in records if not record.get("valid")]}


# Running the bench in a browser.

@dataclass
class _Bench:
    walker: Any
    journey: Journey
    variants_root: Path
    repo_root: Path
    model: Any
    prefix: str
    runs: int
    variant_seconds: float
    max_replays: int
    search_seconds: float
    max_calls: int
    calls: int = 0
    replays: int = 0

    def walk(self, variant: str | None, journey: Journey, *, collect_evidence: bool = False) -> Result:
        """One replay in a fresh browser context, so no two walks share a cart or an order."""
        self.replays += 1
        session = self.walker.open(variant)
        try:
            return replay(session, journey, collect_evidence=collect_evidence)
        finally:
            session.close()


def _slot(source: str, run: int | None = None, key: str = "") -> dict:
    return {"source": source, "run": run, "key": key, "status": NOT_RUN, "route": "", "error": "",
            "raw": None, "proposal": None, "meta": {}, "outcome": {}, "correct": False,
            "seconds": {"answer": 0.0, "check": 0.0}}


def _left(deadline: float) -> float:
    return deadline - time.monotonic()


def _summary(result: Result) -> dict:
    return {"verdict": result.verdict, "failed_step": result.failed_step, "reason": result.reason,
            "page": result.page, "keys": result.keys}


def _baseline(slot: dict, produce: Callable[[], Proposal]) -> Proposal | None:
    started = time.monotonic()
    try:
        proposal = produce()
        slot.update(status=ANSWERED, route=proposal.route, raw=proposal.as_dict(), proposal=proposal.as_dict())
        return proposal
    except Exception as exc:  # a baseline bug is recorded against that baseline; the bench goes on
        slot.update(status=ERROR, error=f"{type(exc).__name__}: {exc}")
        return None
    finally:
        slot["seconds"]["answer"] = round(time.monotonic() - started, 2)


def _ask(bench: _Bench, slot: dict, system: str, user: str, files: list[str], failed_step: int) -> Proposal | None:
    bench.calls += 1
    started = time.monotonic()
    try:
        reply = bench.model.ask(system, user, slot["key"])
    except Exception as exc:  # the model's own failure makes this run unusable, nothing more
        slot.update(status=UNUSABLE, error=f"model error: {type(exc).__name__}: {exc}")
        return None
    finally:
        slot["seconds"]["answer"] = round(time.monotonic() - started, 2)
    slot.update(raw=reply.answer, meta=dict(reply.meta or {}))
    if reply.answer is None:
        slot.update(status=UNUSABLE, error=f"model error: {reply.error or 'no answer'}")
        return None
    try:
        proposal = parse(reply.answer, source=bench.model.label, journey=bench.journey,
                         failed_step=failed_step, template_files=files)
    except ProposalError as exc:
        slot.update(status=UNUSABLE, error=f"malformed answer: {exc}")
        return None
    slot.update(status=ANSWERED, route=proposal.route, proposal=proposal.as_dict())
    return proposal


def _check_path(bench: _Bench, variant: str, proposal: Proposal) -> dict:
    path = apply_path(bench.journey, proposal)
    result = bench.walk(variant, path)
    junk = junk_find_names(path)
    return {"path_accepted": result.clear, "path_verdict": result.verdict, "path_reason": result.reason,
            "path_keys": result.keys, "junk_names": junk, "unsafe_path": result.clear and bool(junk)}


def _check_fix(bench: _Bench, variant: str, fix: Fix, deadline: float) -> dict:
    from nomouse.baselines import find_named_path
    from nomouse.fix import FixError, apply_fix

    try:
        fixed = apply_fix(bench.variants_root, variant, fix, bench.repo_root, bench.prefix)
    except FixError as exc:
        return {"fix_green": False, "fix_reason": f"the fix was not applied: {exc}"}
    result = bench.walk(fixed, bench.journey, collect_evidence=True)
    if result.clear:
        return {"fix_variant": fixed, "fix_green": True, "fix_reason": "the recorded walk is clear on the fixed page"}
    broken = f"the recorded walk is {result.verdict} on the fixed page ({result.reason})"
    if _left(deadline) <= 0:
        return {"fix_variant": fixed, "fix_green": False, "fix_reason": f"{broken}; no time left to search"}
    found, used = find_named_path(bench.walker, bench.journey, result, fixed, max_replays=bench.max_replays,
                                  max_seconds=min(bench.search_seconds, _left(deadline)))
    outcome = {"fix_variant": fixed, "fix_search_replays": used}
    if found is None:
        return {**outcome, "fix_green": False, "fix_reason": f"{broken}; no named path in {used} replays"}
    check = bench.walk(fixed, found)  # code confirms the search's answer itself
    junk = junk_find_names(found)
    reason = "a path over named controls places the order on the fixed page" if check.clear else \
        f"the path the search found is {check.verdict} on replay ({check.reason})"
    return {**outcome, "fix_green": check.clear, "fix_reason": reason, "fix_path": [s.as_dict() for s in found.steps],
            "junk_names": junk, "fix_path_unsafe": check.clear and bool(junk)}


def _check_into(bench: _Bench, slot: dict, variant: str, proposal: Proposal | None, deadline: float) -> None:
    """Replay what the answer proposes. Code, not the answerer, decides whether it works."""
    if proposal is None:
        return
    if _left(deadline) <= 0:
        slot["outcome"] = {"checked": False, "reason": "not checked: the variant's time cap was reached"}
        return
    started = time.monotonic()
    try:
        if proposal.route == "still_usable":
            slot["outcome"] = _check_path(bench, variant, proposal) if proposal.replace_from is not None \
                else {"path_accepted": False, "path_reason": "no path was given"}
        elif proposal.route == "barrier" and proposal.fix is not None:
            slot["outcome"] = _check_fix(bench, variant, proposal.fix, deadline)
    except Exception as exc:  # a crash while checking never counts as a pass
        slot["outcome"] = {"checked": False, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        slot["seconds"]["check"] = round(time.monotonic() - started, 2)


def _judge_variant(bench: _Bench, variant: Variant, record: dict, deadline: float, baselines: Any) -> None:
    result = bench.walk(variant.id, bench.journey, collect_evidence=True)
    record["recorded"] = _summary(result)
    if result.clear:
        record.update(valid=False, note="does not break the recorded walk", b1=None, b2=None, model=[])
        return
    files, source = page_templates(bench.variants_root, variant.id, result.page, bench.repo_root, bench.prefix)
    block = evidence(bench.journey, result, template_files=files)
    record.update(template_files=files, evidence=block)
    failed = result.failed_step if result.failed_step is not None else len(bench.journey.steps) - 1

    if _left(deadline) > 0:
        proposal = _baseline(record["b1"], lambda: baselines.b1(bench.journey, result))
        _check_into(bench, record["b1"], variant.id, proposal, deadline)
    if _left(deadline) > 0:
        proposal = _baseline(record["b2"], lambda: baselines.b2(
            bench.walker, bench.journey, result, variant.id, max_replays=bench.max_replays,
            max_seconds=max(1.0, min(bench.search_seconds, _left(deadline)))))
        _check_into(bench, record["b2"], variant.id, proposal, deadline)
    if not bench.model:
        return
    from nomouse.model import render_prompt

    system, user = render_prompt(block, files[0] if files else "(no template is known for this page)", source)
    for slot in record["model"]:
        if _left(deadline) <= 0 or bench.calls >= bench.max_calls:
            break
        proposal = _ask(bench, slot, system, user, files, failed)
        _check_into(bench, slot, variant.id, proposal, deadline)


def _bench_variant(bench: _Bench, variant: Variant, baselines: Any) -> dict:
    started = time.monotonic()
    deadline = started + bench.variant_seconds
    label = bench.model.label if bench.model else ""
    record = {"id": variant.id, "kind": variant.kind, "summary": variant.summary, "wcag": variant.wcag,
              "author": variant.author, "valid": True, "note": "", "error": "", "recorded": {},
              "template_files": [], "evidence": None, "b1": _slot("B1"), "b2": _slot("B2"),
              "model": [_slot(label, run, f"{variant.id}#{run}") for run in range(1, bench.runs + 1)]
              if bench.model else []}
    try:
        _judge_variant(bench, variant, record, deadline, baselines)
    except Exception as exc:  # one variant's crash is recorded; its open answers count as not run
        record["error"] = f"{type(exc).__name__}: {exc}"
    reason = ("the variant stopped with an error" if record["error"] else
              f"the variant's time cap of {bench.variant_seconds:g} s was reached" if _left(deadline) <= 0 else
              "the model call limit was reached")
    for answer in _answers(record):
        if answer["status"] == NOT_RUN and not answer["error"]:
            answer["error"] = f"not run: {reason}"
        answer["correct"] = answer_correct(variant.kind, answer)
    record["seconds"] = round(time.monotonic() - started, 2)
    return record


def _git(repo_root: Path) -> tuple[str, bool | None]:
    """HEAD's SHA, and whether the working tree matches it. Read-only git commands only."""
    def run(*args: str) -> str | None:
        try:
            done = subprocess.run(["git", "--no-optional-locks", *args], cwd=repo_root, capture_output=True,
                                  text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return done.stdout if done.returncode == 0 else None

    sha, status = run("rev-parse", "HEAD"), run("status", "--porcelain")
    return (sha.strip() if sha else "unavailable"), (None if status is None else not status.strip())


def model_note(model: Any) -> tuple[str, str]:
    """(kind, the line printed at the top of results.md) for whoever answered."""
    if model is None:
        return "none", NO_MODEL_NOTE
    name = type(model).__name__
    if name == "StandInModel":
        return "standin", STANDIN_NOTE
    if name == "RecordedModel":
        return "recorded", (f"Model answers are replayed from a recorded file ({model.label}), "
                            "not from a GitLab Duo flow")
    return "other", f"Model answers come from {model.label}, not from a GitLab Duo flow"


def run_bench(variants_dir: Path, out_dir: Path, *, runs: int = 3, model: Any = None,
              only: list[str] | None = None, variant_seconds: float = VARIANT_SECONDS,
              max_replays: int = MAX_REPLAYS, search_seconds: float = SEARCH_SECONDS,
              repo_root: Path = REPO, log: Callable[[str], None] | None = None) -> dict:
    """Run the bench, write OUT/results.json and OUT/results.md, and return the results."""
    if not 1 <= runs <= MAX_RUNS:
        raise BenchError(f"runs must be 1 to {MAX_RUNS}")
    if variant_seconds <= 0 or search_seconds <= 0 or max_replays < 1:
        raise BenchError("time and replay limits must be positive")
    say = log or (lambda message: None)
    variants = select(load_variants(Path(variants_dir)), only)
    if not variants:
        raise BenchError(f"no variants with a variant.yml in {variants_dir}")
    journey = load_journey(repo_root / JOURNEY)
    prompt_sha = hashlib.sha256((repo_root / PROMPT).read_bytes()).hexdigest()
    commit, clean = _git(repo_root)
    kind, note = model_note(model)
    # Imported here so that scoring and manifest checks need neither a browser nor the baselines.
    from nomouse import baselines
    from nomouse.server import serve
    from nomouse.walker import Walker

    started = time.monotonic()
    date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory(prefix="nomouse-bench-") as temp:
        root = Path(temp) / "variants"
        shutil.copytree(variants_dir, root, ignore=shutil.ignore_patterns("__pycache__"))
        with serve(root) as base_url, Walker(base_url) as walker:
            bench = _Bench(walker=walker, journey=journey, variants_root=root, repo_root=repo_root, model=model,
                           prefix=variants_prefix(variants_dir, repo_root),
                           runs=runs, variant_seconds=variant_seconds, max_replays=max_replays,
                           search_seconds=search_seconds, max_calls=runs * len(variants) if model else 0)
            sanity = bench.walk(None, journey)
            if not sanity.clear:
                raise BenchError(f"the recorded journey does not replay clear on the base shop: {sanity.verdict} "
                                 f"at step {sanity.failed_step} ({sanity.reason})")
            records = []
            for variant in variants:
                record = _bench_variant(bench, variant, baselines)
                say(progress_line(record))
                records.append(record)
    results = {
        "bench": "No Mouse feasibility bench on the Demo Beans demo shop (demo data)",
        "date": date, "commit": commit, "worktree_clean": clean, "prompt_sha256": prompt_sha,
        "model": {"kind": kind, "label": model.label if model else "", "note": note},
        "runs": runs, "journey": journey.name, "variants_dir": str(variants_dir),
        "limits": {"variant_seconds": variant_seconds, "max_replays": max_replays,
                   "search_seconds": search_seconds, "max_model_calls": bench.max_calls},
        "sanity": _summary(sanity), "model_calls": bench.calls, "replays": bench.replays,
        "seconds": round(time.monotonic() - started, 1),
        "records": records, "criteria": evaluate_criteria(records),
    }
    write_results(Path(out_dir), results)
    return results


# Writing the results.

def _md(text: Any) -> str:
    """One table cell: a single line, pipes escaped."""
    return re.sub(r"\s+", " ", str(text)).strip().replace("|", "\\|")


def answer_cell(kind: str, answer: dict | None) -> str:
    """ok or no, the route letter, and what replay made of the path or fix."""
    if answer is None:
        return "n/a"
    status = answer.get("status")
    if status == NOT_RUN:
        return "-"
    if status in (UNUSABLE, ERROR):
        return "no X" if status == UNUSABLE else "no E"
    route = answer.get("route", "")
    outcome = answer.get("outcome") or {}
    suffix = ""
    if route == "still_usable":
        accepted = outcome.get("path_accepted")
        suffix = "?path" if accepted is None else "+path" if accepted else "-path"
    elif route == "barrier" and ("fix_green" in outcome or (answer.get("proposal") or {}).get("fix")):
        green = outcome.get("fix_green")
        suffix = "?fix" if green is None else "+fix" if green else "-fix"
    unsafe = " UNSAFE" if outcome.get("unsafe_path") or outcome.get("fix_path_unsafe") else ""
    return f"{'ok' if answer_correct(kind, answer) else 'no'} {LETTERS.get(route, '?')}{suffix}{unsafe}"


def _notes(record: dict) -> str:
    if not record.get("valid"):
        return f"excluded: {record.get('note')}"
    notes = [f"error: {record['error']}"] if record.get("error") else []
    for answer in _answers(record):
        who = f"run {answer['run']}" if answer.get("run") else answer.get("source", "")
        outcome = answer.get("outcome") or {}
        if answer.get("status") in (UNUSABLE, ERROR):
            notes.append(f"{who}: {answer.get('error')}")
        elif outcome.get("error"):
            notes.append(f"{who}: check failed: {outcome['error']}")
        elif outcome.get("path_accepted") is False:
            notes.append(f"{who}: path {outcome.get('path_verdict', 'refused')}: {outcome.get('path_reason', '')}")
        elif outcome.get("fix_green") is False:
            notes.append(f"{who}: fix not green: {outcome.get('fix_reason', '')}")
        if outcome.get("unsafe_path") or outcome.get("fix_path_unsafe"):
            notes.append(f"{who}: UNSAFE accepted path names {', '.join(outcome.get('junk_names') or [])}")
    return "; ".join(note[:NOTE_CHARS] for note in notes)


def progress_line(record: dict) -> str:
    kind = record.get("kind", "")
    if not record.get("valid"):
        return f"{record.get('id')} ({kind}): excluded, {record.get('note')}"
    runs = ", ".join(answer_cell(kind, answer) for answer in record.get("model") or []) or "no model"
    return (f"{record.get('id')} ({kind}): B1 {answer_cell(kind, record.get('b1'))}; "
            f"B2 {answer_cell(kind, record.get('b2'))}; model {runs}")


def render_markdown(results: dict) -> str:
    """results.md: who answered, one row per variant, the five criteria, the overall result."""
    model = results.get("model") or {}
    scored = results.get("criteria") or evaluate_criteria(results.get("records") or [])
    clean = results.get("worktree_clean")
    tree = "" if clean is None else " (working tree clean)" if clean else " (working tree has uncommitted changes)"
    lines = [
        "# No Mouse bench results", "",
        f"**{model.get('note') or NO_MODEL_NOTE}.**", "",
        "Demo data: Demo Beans is an invented shop and every variant is a planted change. The spoken "
        "wording is a simulation built from Chromium's accessibility tree.", "",
        f"- Date: {results.get('date', '')}",
        f"- Commit: {results.get('commit', 'unavailable')}{tree}",
        f"- Judge prompt SHA-256: {results.get('prompt_sha256', '')}",
        f"- Model: {model.get('label') or 'none'}; runs per variant: {results.get('runs', 0)}",
        f"- Model calls: {results.get('model_calls', 0)}; bench replays: {results.get('replays', 0)}; "
        f"time: {results.get('seconds', 0)} s", "",
        "## Variants", "",
        "| Variant | Kind | Breaks at | B1 | B2 | Model runs | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in results.get("records") or []:
        kind = record.get("kind", "")
        recorded = record.get("recorded") or {}
        if not recorded:
            breaks = "-"
        elif recorded.get("verdict") == "clear":
            breaks = "clear"
        else:
            breaks = f"step {recorded.get('failed_step')} on {recorded.get('page')} ({recorded.get('verdict')})"
        runs = ", ".join(answer_cell(kind, answer) for answer in record.get("model") or []) or "no model"
        cells = [record.get("id"), kind, breaks, answer_cell(kind, record.get("b1")),
                 answer_cell(kind, record.get("b2")), runs, _notes(record)]
        lines.append("| " + " | ".join(_md(cell) for cell in cells) + " |")
    lines += ["", LEGEND, "", "## Criteria", "", "| Criterion | Result | Counts |", "|---|---|---|"]
    for key, item in scored["criteria"].items():
        lines.append(f"| {key} {item['name']} | {'pass' if item['passed'] else 'FAIL'} | {_md(item['detail'])} |")
    lines += ["", f"## Overall: {scored['overall']}", ""]
    lines += [f"{note}." for note in scored.get("notes") or []]
    return "\n".join(lines).rstrip() + "\n"


def write_results(out_dir: Path, results: dict) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path, md_path = out_dir / "results.json", out_dir / "results.md"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(results), encoding="utf-8")
    return json_path, md_path


# Command line.

def make_model(spec: str) -> Any:
    """standin, none or recorded:PATH, as given on the command line."""
    if spec == "none":
        return None
    if spec != "standin" and not (spec.startswith("recorded:") and spec.split(":", 1)[1]):
        raise BenchError(f"--model must be standin, none or recorded:PATH, not {spec!r}")
    from nomouse import model as models

    if spec == "standin":
        return models.StandInModel()
    try:
        return models.RecordedModel(Path(spec.split(":", 1)[1]))
    except (OSError, ValueError) as exc:
        raise BenchError(f"cannot read the recorded answers: {exc}") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nomouse.bench",
                                     description="Run the No Mouse feasibility bench on the demo shop.")
    parser.add_argument("--variants", type=Path, required=True, help="directory of variants, each with variant.yml")
    parser.add_argument("--runs", type=int, default=3, help=f"model runs per variant (1 to {MAX_RUNS})")
    parser.add_argument("--out", type=Path, required=True, help="where results.json and results.md are written")
    parser.add_argument("--model", default="standin", help="standin, none or recorded:PATH (default standin)")
    parser.add_argument("--only", default="", help="comma-separated variant ids")
    parser.add_argument("--variant-seconds", type=float, default=VARIANT_SECONDS,
                        help="wall-clock cap per variant; later work is recorded as not run")
    args = parser.parse_args(argv)
    only = [item.strip() for item in args.only.split(",") if item.strip()]
    try:
        model = make_model(args.model)
        results = run_bench(args.variants, args.out, runs=args.runs, model=model, only=only,
                            variant_seconds=args.variant_seconds, log=lambda line: print(line, file=sys.stderr))
    except BenchError as exc:
        print(f"bench: {exc}", file=sys.stderr)
        return 2
    scored = results["criteria"]
    print(f"{scored['overall']}: wrote {args.out / 'results.md'} and {args.out / 'results.json'}")
    for note in scored["notes"]:
        print(note)
    return 0 if scored["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
