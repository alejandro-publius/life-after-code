# Sustainability benchmark of Night Orders (Claude lane)

Post-submission work by Claude Code, 27 Oct 2026. Nothing here existed before the 27 Oct 2026 13:00 UTC deadline, and none of it is presented as evidence that did.

## In one paragraph

A reproducible resource benchmark of one completed Night Orders night, run through the repository's real replay and decision code (`relay/nightorders/demo_night.py` and the Watch it drives), repeated in fresh processes, with a fingerprint of every outcome that must be identical before two variants are compared. It measures CPU time, wall time, peak memory and the counts a night produces (ticks, samples, condition evaluations, model calls, polls, port calls). It compares the code as it is with one proposed change, saved as a patch for Codex. It does not measure energy or carbon: [SCI.md](SCI.md) says exactly which inputs are missing.

## Run it

From the repository root:

```sh
uv run --locked python scripts/claude_sustainability_benchmark.py --runs 12 --out docs/claude/sustainability
uv run --locked python scripts/claude_sustainability_benchmark.py --counts
uv run --locked python -m pytest -q tests/test_claude_sustainability_benchmark.py
```

The first command takes about 15 seconds for 12 runs per variant on a laptop. It writes one raw record per run under `raw/`, `results.json` (summary, machine, labels, counts) and `RESULTS.md` (the generated report). Its exit code is 1 when outcomes differ between runs or variants, and then no comparison is written.

## Functional unit

One standard completed test night: `demo/night-2026-10-20`, signed, fallback approved, replayed minute by minute through the same Watch class the relay runs (546 ticks, 22:00 to 07:05 local), then the morning countersign and the lease end. That is what `python -m nightorders.demo_night` prints. The inputs are fixed files in the repository: the shop, its two planted faults and the agent's two replies are labelled demo data; the decisions are the real code's. The outcome fingerprint (SHA-256 of every log line, ledger event, action, the watch log, the morning and the lease end) is in `results.json`.

## Source commits

- Measured code: GitHub main at `bfa7b6d` (the relay package as of that commit; the benchmark's runtime patch is the only difference between variants).
- Benchmark script, tests, records and these documents: branch `claude/sustainability-benchmark`; the exact head commit is in the handoff report Alex receives, and [HANDOFF.md](HANDOFF.md) says how to integrate it.

## Files

| File | What it is |
|---|---|
| [RESULTS.md](RESULTS.md) | Generated report of the committed 12-run set |
| [results.json](results.json) | The same, machine-readable, with the machine, labels, counts and fingerprints |
| `raw/` | One JSON record per run: 12 baseline, 12 optimized, interleaved |
| [SCI.md](SCI.md) | The SCI formula per the specification, the functional unit, the boundary, measured terms, and the inputs that are unavailable |
| [proposed-signals-window.patch](proposed-signals-window.patch) | The proposed change to `relay/nightorders/signals.py`, for Codex |
| [PRIZE_EVIDENCE_DRAFT.md](PRIZE_EVIDENCE_DRAFT.md) | An honest draft for the Most Environmentally Impactful opt-in |
| [HANDOFF.md](HANDOFF.md) | Integration handoff for Codex |

## Results in brief

From the committed 12-run set (Apple M1 laptop, on battery, macOS 15.1.1, Python 3.13):

- One night costs about 33 ms of CPU on one core and peaks at about 0.65 MiB of Python allocations, in a process whose resident set peaks near 32 MiB. Imports before the night cost about 50 ms.
- A night makes 546 ticks, stores 6006 metric samples, evaluates 2743 alert conditions, starts 2 model sessions (budget 3), polls 3 times for the agent's answer and 2 times for a thumbs-up, opens 2 incidents, applies 2 actions and restores 2.
- The proposed `Metrics.window` change saves about 2.2 ms of CPU per night (7% of the mean) with identical outcomes; the 95% intervals of the two variants do not overlap at 12 runs. It is a small resource saving, not a measured carbon reduction.

## The pipeline, read from the public API

The benchmark does not touch CI, but the prize wording names pipeline optimization, so the numbers were read anonymously from GitLab on 27 Oct 2026: each push to main runs 18 jobs; the three newest successful main pipelines (2994456180, 2994433358, 2994340880) took 148 to 155 s of wall time and 743 to 765 job-seconds each, about 12.5 job-minutes per push. The three validation jobs (flows, orders, state) take about 19 s each for a sub-second check; running them as one job is the one pipeline suggestion in [PRIZE_EVIDENCE_DRAFT.md](PRIZE_EVIDENCE_DRAFT.md). Suggested, not applied, not measured.

## Limitations

- One machine, one night, 12 runs per variant, on battery power at 3% (CPU frequency under battery may differ from mains).
- No energy counter was readable (`powermetrics` needs root), so no joules, and no SCI score: see SCI.md.
- The replay makes no HTTP calls and serves recorded replies; production polling, retries and model runtime are counted by structure, not timed.
- The decision code is a small part of a night's footprint; the model sessions, the relay container and the pipeline are the larger parts, and this benchmark counts them without weighing them.
