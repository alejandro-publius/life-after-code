"""The fix bench: does a model repair accessibility barriers better than simple rules?

The first bench showed that code can decide whether a person can still pay. What is left
for an agent is the repair. For each planted barrier, code first confirms it is a barrier
(the recorded walk breaks and the bounded search over named controls finds no way through).
Then two fixers propose one find-and-replace on the broken page's template, on the same
evidence: F0, a set of rules with no model, and a model asked the frozen judge prompt N
times. Code applies each fix to a temporary copy and walks the fixed page again.

A fix counts as green only if code can walk the fixed page and place the order, the path it
used presses no unnamed or meaningless control, and the fix removes at most MAX_REMOVED_WORDS
words of visible text (so deleting a feature is not a repair). The criteria in
evaluate_fix_criteria were written down before the blind barrier set existed; see
docs/research/nomouse_fix_bench.md.

Run: python -m nomouse.fixbench --variants nomouse/fixset --runs 3 --out /tmp/nomouse-fixbench
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
from typing import Any, Callable

from nomouse.bench import (ANSWERED, BARRIER_KINDS, JOURNEY, PROMPT, REPO, BenchError, _Bench, _ask,
                           _check_fix, _git, _left, _slot, load_variants, majority, make_model, model_note,
                           page_templates, select, variants_prefix)
from nomouse.journey import evidence, load_journey
from nomouse.proposal import Fix

MAX_REMOVED_WORDS = 2
F1_NEEDED = 2  # variants where the model's fix works in most runs and F0's does not
F2_SHARE = (2, 3)  # the model's fix works in most runs on at least two thirds of the barriers
VARIANT_SECONDS = 600.0
MAX_REPLAYS = 40
SEARCH_SECONDS = 180.0
NOTE = "Model answers come from a stand-in (Claude via claude -p), not from a GitLab Duo flow"
DECISION_NOTE = "Concept decision: the model does not repair barriers better than simple rules (F0)"


def _visible_words(fragment: str) -> Counter:
    """Words a sighted person would read in an HTML fragment (tag contents, not attributes)."""
    text = html.unescape(re.sub(r"<[^>]*>", " ", fragment or ""))
    return Counter(word.casefold() for word in re.findall(r"[^\W_]+", text))


def removed_words(fix: Fix) -> int:
    """How many visible words the fix takes away (attributes such as aria-label do not count)."""
    return sum((_visible_words(fix.find) - _visible_words(fix.replace)).values())


def fix_ok(outcome: dict, removed: int | None) -> bool:
    """Green under the pre-registered rule: walkable, safe path, and the feature kept."""
    return (outcome.get("fix_green") is True and not outcome.get("fix_path_unsafe")
            and removed is not None and removed <= MAX_REMOVED_WORDS)


# Scoring: a pure function over the records, tested on its own.

def evaluate_fix_criteria(records: list[dict]) -> dict:
    valid = [record for record in records if record.get("valid")]
    model_wins, rule_wins, model_majority = [], [], []
    for record in valid:
        runs = record.get("model") or []
        good = sum(bool(run.get("ok")) for run in runs)
        model_ok = bool(runs) and good >= majority(len(runs))
        rules_ok = bool((record.get("f0") or {}).get("ok"))
        if model_ok:
            model_majority.append(record["id"])
        if model_ok and not rules_ok:
            model_wins.append(record["id"])
        if rules_ok and not model_ok:
            rule_wins.append(record["id"])
    f1 = {"name": "model_beats_rules", "passed": len(model_wins) >= F1_NEEDED, "count": len(model_wins),
          "variants": model_wins, "detail": f"{len(model_wins)} barrier(s) where the model's fix works in most runs "
          f"and F0's does not{': ' + ', '.join(model_wins) if model_wins else ''}; needs {F1_NEEDED}"}
    need_num, need_den = F2_SHARE
    f2 = {"name": "model_fixes_most", "count": len(model_majority), "of": len(valid),
          "passed": bool(valid) and len(model_majority) * need_den >= len(valid) * need_num,
          "detail": f"the model's fix works in most runs on {len(model_majority)} of {len(valid)} barriers; "
                    f"needs {need_num}/{need_den}"}
    unsafe = [f"{record['id']} {answer.get('source')} {answer.get('run') or ''}".strip()
              for record in valid for answer in [record.get("f0") or {}, *(record.get("model") or [])]
              if (answer.get("outcome") or {}).get("fix_green") is True
              and (answer.get("outcome") or {}).get("fix_path_unsafe")]
    f3 = {"name": "no_unsafe_paths", "passed": not unsafe, "count": len(unsafe), "paths": unsafe,
          "detail": f"{len(unsafe)} fixed page(s) walked by pressing a meaningless control; needs 0"}
    criteria = {"F1": f1, "F2": f2, "F3": f3}
    passed = all(item["passed"] for item in criteria.values())
    rules_green = sum(bool((record.get("f0") or {}).get("ok")) for record in valid)
    notes = [] if f1["passed"] else [DECISION_NOTE]
    return {**criteria, "passed": passed, "overall": "PASS" if passed else "FAIL", "notes": notes,
            "report": {"valid_barriers": len(valid), "f0_green": rules_green, "rules_beat_model": rule_wins,
                       "excluded": [record["id"] for record in records if not record.get("valid")]}}


# Running it.

def _check(bench: _Bench, slot: dict, variant: str, fix: Fix | None, deadline: float) -> None:
    if fix is None:
        slot["ok"] = False
        return
    removed = removed_words(fix)
    started = time.monotonic()
    try:
        outcome = _check_fix(bench, variant, fix, deadline) if _left(deadline) > 0 else \
            {"fix_green": False, "fix_reason": "not checked: the variant's time cap was reached"}
    except Exception as exc:  # a crash while checking never counts as a pass
        outcome = {"fix_green": False, "fix_reason": f"{type(exc).__name__}: {exc}"}
    outcome["removed_words"] = removed
    slot.update(outcome=outcome, ok=fix_ok(outcome, removed))
    slot["seconds"]["check"] = round(time.monotonic() - started, 2)


def _fix_variant(bench: _Bench, variant: Any, rulefix: Any, baselines: Any) -> dict:
    started = time.monotonic()
    deadline = started + bench.variant_seconds
    label = bench.model.label if bench.model else ""
    record = {"id": variant.id, "kind": variant.kind, "summary": variant.summary, "wcag": variant.wcag,
              "author": variant.author, "valid": True, "note": "", "error": "", "template_files": [],
              "f0": {**_slot("F0"), "ok": False},
              "model": [{**_slot(label, run, f"{variant.id}#{run}"), "ok": False}
                        for run in range(1, bench.runs + 1)] if bench.model else []}
    try:
        result = bench.walk(variant.id, bench.journey, collect_evidence=True)
        record["recorded"] = {"verdict": result.verdict, "failed_step": result.failed_step, "page": result.page,
                              "reason": result.reason}
        if variant.kind not in BARRIER_KINDS:
            record.update(valid=False, note="not a barrier variant")
            return record
        if result.clear:
            record.update(valid=False, note="does not break the recorded walk")
            return record
        b2 = baselines.b2(bench.walker, bench.journey, result, variant.id, max_replays=bench.max_replays,
                          max_seconds=max(1.0, min(bench.search_seconds, _left(deadline))))
        record["code_route"] = b2.route
        if b2.route == "still_usable":
            record.update(valid=False, note="code found a usable path with named controls, so it is not a barrier")
            return record
        files, source = page_templates(bench.variants_root, variant.id, result.page, bench.repo_root, bench.prefix)
        record["template_files"] = files
        if not files:
            record.update(valid=False, note="no template is known for the page where the walk broke")
            return record
        block = evidence(bench.journey, result, template_files=files)

        slot = record["f0"]
        rule_started = time.monotonic()
        fix, why = rulefix.propose_fix(bench.journey, result, files[0], source)
        slot.update(status=ANSWERED, route="barrier", error="" if fix else why,
                    proposal={"why": why, "fix": None if fix is None else fix.__dict__})
        slot["seconds"]["answer"] = round(time.monotonic() - rule_started, 2)
        _check(bench, slot, variant.id, fix, deadline)

        if bench.model:
            from nomouse.model import render_prompt

            system, user = render_prompt(block, files[0], source)
            failed = result.failed_step if result.failed_step is not None else len(bench.journey.steps) - 1
            for slot in record["model"]:
                if _left(deadline) <= 0 or bench.calls >= bench.max_calls:
                    slot["error"] = "not run: time cap or call limit reached"
                    break
                proposal = _ask(bench, slot, system, user, files, failed)
                fix = proposal.fix if proposal is not None and proposal.route == "barrier" else None
                _check(bench, slot, variant.id, fix, deadline)
    except Exception as exc:  # one variant's crash is recorded; its open answers stay not ok
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["seconds"] = round(time.monotonic() - started, 2)
    return record


def run_fixbench(variants_dir: Path, out_dir: Path, *, runs: int = 3, model: Any = None,
                 only: list[str] | None = None, variant_seconds: float = VARIANT_SECONDS,
                 max_replays: int = MAX_REPLAYS, search_seconds: float = SEARCH_SECONDS,
                 repo_root: Path = REPO, log: Callable[[str], None] | None = None) -> dict:
    from nomouse import baselines, rulefix
    from nomouse.server import serve
    from nomouse.walker import Walker

    if not 1 <= runs <= 10:
        raise BenchError("runs must be between 1 and 10")
    variants = select(load_variants(Path(variants_dir)), only)
    if not variants:
        raise BenchError(f"no variants with a variant.yml in {variants_dir}")
    journey = load_journey(repo_root / JOURNEY)
    prompt_sha = hashlib.sha256((repo_root / PROMPT).read_bytes()).hexdigest()
    rules_sha = hashlib.sha256((repo_root / "nomouse" / "rulefix.py").read_bytes()).hexdigest()
    commit, clean = _git(repo_root)
    started = time.monotonic()
    date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    barriers = [variant for variant in variants if variant.kind in BARRIER_KINDS]
    with tempfile.TemporaryDirectory(prefix="nomouse-fixbench-") as temp:
        root = Path(temp) / "variants"
        shutil.copytree(variants_dir, root, ignore=shutil.ignore_patterns("__pycache__"))
        with serve(root) as base_url, Walker(base_url) as walker:
            bench = _Bench(walker=walker, journey=journey, variants_root=root, repo_root=repo_root, model=model,
                           prefix=variants_prefix(variants_dir, repo_root), runs=runs,
                           variant_seconds=variant_seconds, max_replays=max_replays,
                           search_seconds=search_seconds, max_calls=runs * len(barriers) if model else 0)
            sanity = bench.walk(None, journey)
            if not sanity.clear:
                raise BenchError(f"the recorded walk is not clear on the base shop: {sanity.reason}")
            records = []
            for variant in variants:
                record = _fix_variant(bench, variant, rulefix, baselines)
                records.append(record)
                if log:
                    log(progress_line(record))
    results = {
        "bench": "nomouse-fixbench", "date": date, "commit": commit, "worktree_clean": clean,
        "prompt_sha256": prompt_sha, "rulefix_sha256": rules_sha, "model": model.label if model else None,
        "model_kind": model_note(model)[0], "runs": runs, "variants_dir": str(variants_dir),
        "limits": {"variant_seconds": variant_seconds, "max_replays": max_replays, "search_seconds": search_seconds,
                   "max_removed_words": MAX_REMOVED_WORDS},
        "model_calls": bench.calls, "replays": bench.replays, "seconds": round(time.monotonic() - started, 1),
        "records": records, "criteria": evaluate_fix_criteria(records),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str) + "\n",
                                          encoding="utf-8")
    (out_dir / "results.md").write_text(render_markdown(results), encoding="utf-8")
    return results


def _cell(answer: dict) -> str:
    outcome = answer.get("outcome") or {}
    if answer.get("ok"):
        return "green"
    if answer.get("status") != ANSWERED:
        return "no answer"
    if not outcome:
        return "no fix"
    if outcome.get("fix_green") and (outcome.get("removed_words") or 0) > MAX_REMOVED_WORDS:
        return f"removes {outcome['removed_words']} words"
    return "not walkable"


def progress_line(record: dict) -> str:
    if not record.get("valid"):
        return f"{record['id']} ({record['kind']}): excluded, {record.get('note') or record.get('error')}"
    runs = ", ".join(_cell(answer) for answer in record.get("model") or []) or "no model"
    return f"{record['id']} ({record['kind']}): F0 {_cell(record['f0'])}; model {runs}"


def render_markdown(results: dict) -> str:
    def esc(text: Any) -> str:
        return str(text or "").replace("|", "/").replace("\n", " ")

    criteria = results["criteria"]
    lines = ["# No Mouse fix bench results", ""]
    lines += [f"**{NOTE}.**" if results["model_kind"] == "standin" else f"**Model: {results['model'] or 'none'}.**", ""]
    lines += ["Demo data: Demo Beans is an invented shop and every variant is a planted barrier.", "",
              f"- Date: {results['date']}",
              f"- Commit: {results['commit']}" + ("" if results["worktree_clean"] else " (working tree has uncommitted changes)"),
              f"- Judge prompt SHA-256: {results['prompt_sha256']}",
              f"- F0 rules SHA-256: {results['rulefix_sha256']}",
              f"- Runs per variant: {results['runs']}; model calls: {results['model_calls']}; "
              f"replays: {results['replays']}; time: {results['seconds']} s", "",
              "## Barriers", "", "| Variant | Kind | WCAG | F0 | Model runs | Note |", "|---|---|---|---|---|---|"]
    for record in results["records"]:
        if record.get("valid"):
            runs = ", ".join(_cell(answer) for answer in record.get("model") or []) or "no model"
            note = esc((record["f0"].get("proposal") or {}).get("why", ""))[:120]
            lines.append(f"| {record['id']} | {record['kind']} | {esc(record.get('wcag'))} | {_cell(record['f0'])} | "
                         f"{runs} | F0: {note} |")
        else:
            lines.append(f"| {record['id']} | {record['kind']} | {esc(record.get('wcag'))} | excluded | | "
                         f"{esc(record.get('note') or record.get('error'))} |")
    lines += ["", "green = code walked the fixed page, placed the order, pressed no meaningless control, and the fix "
              f"removed at most {MAX_REMOVED_WORDS} visible words.", "", "## Criteria", "",
              "| Criterion | Result | Counts |", "|---|---|---|"]
    for key in ("F1", "F2", "F3"):
        item = criteria[key]
        lines.append(f"| {key} {item['name']} | {'pass' if item['passed'] else 'FAIL'} | {esc(item['detail'])} |")
    report = criteria["report"]
    lines += ["", f"F0 green on {report['f0_green']} of {report['valid_barriers']} barriers. "
              f"Barriers where F0 works and the model does not: {', '.join(report['rules_beat_model']) or 'none'}.",
              "", f"## Overall: {criteria['overall']}", ""]
    lines += [f"{note}." for note in criteria["notes"]]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nomouse.fixbench",
                                     description="Compare model fixes with rule fixes on planted barriers.")
    parser.add_argument("--variants", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="standin", help="standin, none or recorded:PATH (default standin)")
    parser.add_argument("--only", default="")
    args = parser.parse_args(argv)
    only = [item.strip() for item in args.only.split(",") if item.strip()]
    try:
        results = run_fixbench(args.variants, args.out, runs=args.runs, model=make_model(args.model), only=only,
                               log=lambda line: print(line, file=sys.stderr, flush=True))
    except BenchError as exc:
        print(f"fixbench: {exc}", file=sys.stderr)
        return 2
    criteria = results["criteria"]
    print(f"{criteria['overall']}: wrote {args.out / 'results.md'} and {args.out / 'results.json'}")
    for note in criteria["notes"]:
        print(note)
    return 0 if criteria["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
