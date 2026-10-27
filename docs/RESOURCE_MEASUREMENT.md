# Local replay resource measurement

Measure a fixed functional unit: **one serialized, completed and outcome-verified demo-night response**, with
signed orders, the fallback approved and the morning checkout change kept. A warm response serves that
previously computed night; it does not execute another independent night or a live agent.

Run from the repository root with the locked dependencies:

```sh
uv run --locked python scripts/benchmark_resources.py --out /tmp/night-orders-resources.json
```

The default is three sequential cold/warm pairs, with a 60-second overall budget. `--repetitions` accepts
1 through 8 and `--max-seconds` accepts 1 through 120. Each worker subprocess has at most 30 seconds and is
terminated if it exceeds its remaining budget. A failed, incomplete, different or timed-out workload returns
a failing exit status and no successful summary. Relevant source changes during measurement also fail it.

Each pair runs in a fresh Python process. The cold sample clears the relay's existing replay LRU and the
fixed comparison and permission-check caches, then calls the actual `demo_replay` function and the same
`JSONResponse` serializer used by `/demo/replay`. The warm sample immediately repeats those selectors.
The application code and fixtures are unchanged. Operating-system page caches are not cleared, so "cold"
means cold application memoization, not a cold machine, filesystem or container start.

The cold response includes the fixed three-way comparisons and permission checks normally bundled with the
demo. Their computation is part of serving this functional unit; the timing is not described as the cost of
only one decision loop. Imports, subprocess startup, result validation, HTTP transport, browser rendering,
network transfer and compression are outside the timed interval.

The JSON report records:

- Every sample in execution order, with process CPU nanoseconds and monotonic elapsed nanoseconds.
- The exact serialized response size and SHA-256, plus observed replay-cache hits and misses.
- Current resident memory before/after where available, and process-lifetime peak RSS. Linux `ru_maxrss`
  is KiB and is multiplied by 1024; macOS reports bytes. Native units are retained; unknown units are not
  silently converted. Current RSS comes from Linux `/proc/self/statm` resident pages times page size.
- The source commit and a content digest over the measurement script, relay code, dependency declarations,
  lockfile and relevant fixtures. The file list and uncommitted-content indicator identify what was measured.
- Python, platform and relevant installed package versions, CPU visibility and affinity when supported.
- Exact equality across all cold/warm response bytes and completed outcomes. A night must include its
  signature, expiry, refusal, approval, action, observed recovery and expected morning keep/restore result.

Peak RSS includes imports and earlier work in the same process. A warm sample inherits the cold sample's
high-water mark; subtracting those peaks does not measure per-request allocation or cache memory. Fixed
cold-then-warm ordering, host load and filesystem caching can affect this small local sample. Raw samples
are retained rather than reporting only a favorable average. No production service, credential, GitLab
write, model request, phone notification or real shop is involved.

**Energy and carbon are not measured.** CPU time, wall time, response bytes and RSS are resource observations,
not electricity or emissions measurements. The report leaves energy, carbon and Software Carbon Intensity
unset. A later SCI calculation would need measured energy, grid intensity, embodied-emissions allocation,
the same functional unit and provenance for each input; no default coefficients or claimed carbon saving
are supplied. This benchmark does not establish a production efficiency or live model-token saving.

## Recorded local run

The default three-pair run completed in 4.658 seconds on Python 3.12.14, Linux x86_64. Its source commit was
`bfa7b6d8fbd03e884ff0db6b22db46a41d1f623c`, plus the uncommitted measurement script. The relevant content
digest was `2e8a6921863660258b6e01c11071688cc6a205add3e903c3f2c4604dc13f34ef`, unchanged across the run.
The [complete JSON](codex/resource-measurement.json) preserves the file list, package versions and every raw
sample. It was originally written to `/workspace/life-after-code-setup/resource-measurement.json` and copied
unchanged into this record. It is a local measurement artifact, not a GitLab CI artifact or deployment result.

| Observation per completed demo-night response | Cold, median of 3 | Warm, median of 3 |
| --- | --- | --- |
| Timed wall duration | 364.691 ms | 2.196 ms |
| Process CPU duration | 364.686 ms | 2.193 ms |
| Serialized response size | 208,925 bytes | 208,925 bytes |
| Replay-cache result per sample | 1 miss, 0 hits | 0 misses, 1 hit |

All six responses had exactly the same bytes, SHA-256
`d1138d187eab5ddb638950825961cf4a16332bc86e70daafe2b28840be2a604d`, and verified outcomes: one page,
one automatic incident handled, one approved action, expired authority and the expected morning keep/restore.
After-sample current RSS ranged from 50,507,776 to 51,695,616 bytes; process-lifetime peak RSS ranged from
50,307,072 to 51,425,280 bytes. These independently sampled Linux counters are approximate and cover
different boundaries. They are not a measurement of cache allocation. No energy or carbon result follows
from these timings.

Regression checks focus on incomplete outcomes, unequal responses, unsupported cache claims, invalid bounds,
worker timeout and changing source content:

```sh
uv run --locked pytest -q tests/test_resource_benchmark.py
```
