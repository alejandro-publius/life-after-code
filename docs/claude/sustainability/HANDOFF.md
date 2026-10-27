# Integration handoff for Codex: sustainability benchmark

From Claude Code, 27 Oct 2026. Branch `claude/sustainability-benchmark` on GitHub, started from main at `bfa7b6d`. Claude does not merge to main; the exact head commit to take is in the report Alex pastes to you.

## What is on the branch, and what is not

Added, all new files:

- `scripts/claude_sustainability_benchmark.py`
- `tests/test_claude_sustainability_benchmark.py`
- `docs/claude/sustainability/` (README.md, RESULTS.md, results.json, raw/, SCI.md, PRIZE_EVIDENCE_DRAFT.md, HANDOFF.md, proposed-signals-window.patch)

Not changed: anything under `relay/`, `shop/`, `flows/`, the browser, `.gitlab-ci.yml`, `.github/`, `pyproject.toml`, `uv.lock`. No dependency was added; the benchmark uses the standard library and the project's own packages.

## The proposed change

`proposed-signals-window.patch` changes one method, `Metrics.window` in `relay/nightorders/signals.py`: it reads the series once and looks each whole minute up directly, instead of calling `get()` (which calls `minute()`, a `datetime.replace`) once per minute of the window. Same values, same order, same missing-data behaviour.

Evidence:

- Identical outcomes: the benchmark's fingerprint of every log line, ledger event, action, watch log, morning and lease end is the same for the baseline and for the change, in all 24 runs (`results.json`, `fingerprints`).
- Tests: with the patch applied to the main tree at `bfa7b6d`, `uv run --locked python -m pytest -q` passed 754 tests (the benchmark's own tests excluded from that run); ruff clean. The patch was then reverted; the branch does not change `signals.py`.
- Saving: about 2.2 ms of CPU per night, 7% of the night's 33 ms, 95% intervals not overlapping at 12 runs per variant (`RESULTS.md`). This is a resource saving in the decision loop; it is not a measured carbon reduction, and it is small in absolute terms. The relay evaluates the same windows every minute of a production night, so the saving applies there too, unmeasured.

To apply, from the repository root:

```sh
git apply docs/claude/sustainability/proposed-signals-window.patch
uv run --locked python -m pytest -q
uv run --locked python scripts/claude_sustainability_benchmark.py --runs 12 --out docs/claude/sustainability
```

After the patch is in, the benchmark's "optimized" variant applies the same code at runtime, so the comparison will show no difference: that is correct. Keep the script as a regression benchmark (`--variant baseline`) or leave both variants; `test_the_committed_results_match_this_source_tree` only checks that the committed fingerprint still matches the tree and that the committed set has at least 10 runs, so rerun the benchmark and commit its records whenever the demo night or the decision code changes.

## What Claude asks Codex to decide

1. Whether to apply the patch. It is small and safe by the evidence above, but `signals.py` is yours.
2. Whether to link `docs/claude/sustainability/README.md` from STATUS.md or the README. Claude did not touch shared docs.
3. Whether to opt in to the Most Environmentally Impactful prize with `PRIZE_EVIDENCE_DRAFT.md`. The draft claims no carbon figure, because none was measured; if that is not enough for the form, it is better left unsent than padded.
4. Nothing was added to the pipeline. If a benchmark job is wanted, it is one command of about 15 seconds; Claude suggests a manual job, not one on every push, since the point is fewer runs, not more.

## Limits to carry forward

The benchmark runs on a laptop, on battery, with no energy counter; the night is simulated with recorded replies; no model runtime, relay container or pipeline energy was measured. Any sentence that turns these numbers into grams of CO2e needs the inputs SCI.md lists as unavailable.
