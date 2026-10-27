# Software Carbon Intensity (SCI) for one Night Orders night: what is measured, what is not

Written by Claude Code on 27 Oct 2026 against the [SCI specification, version 1.1.0](https://sci.greensoftware.foundation/) (Green Software Foundation, read 27 Oct 2026). Post-submission work: none of this existed before the 27 Oct 2026 13:00 UTC deadline.

## The formula, as the specification states it

SCI = (O + M) per R, with O = E x I and M = TE x TS x RS (also written TE x (TiR/EL) x (RR/ToR)).

- E: energy consumed by the software system, in kWh.
- I: location-based grid carbon intensity, in gCO2e/kWh. Market-based instruments (credits, RECs, PPAs) are excluded; only eliminating emissions lowers the score.
- M: the share of the hardware's embodied emissions allocated to the software, by time-share and resource-share.
- R: the functional unit, the same for every term.

The specification allows a calculation from a benchmark in a controlled environment, with modelled inputs where measured ones are missing, as long as the modelled inputs are stated. It does not allow a score without E, I and M.

## R, the functional unit

One standard completed test night: the labelled demo night (`demo/night-2026-10-20`), signed, fallback approved, replayed minute by minute through the same Watch class the relay runs (546 ticks from 22:00 to 07:05), then the morning countersign and the lease end. The inputs are fixed files in the repository; the outcome fingerprint in [results.json](results.json) is identical across every run, which is the precondition the benchmark enforces before it compares anything.

## The software boundary, and which parts this benchmark reaches

| Part of the system per night | In the benchmark | Status |
|---|---|---|
| The decision code: alert rules, triage, orders, apply, re-check, countersign, lease (the replay) | Yes | Measured CPU time, wall time, memory, counts ([RESULTS.md](RESULTS.md)) |
| The model: 2 watch flow sessions per night (budget 3), plus a dusk and a dawn session on a production night | Counted only | The replay serves recorded replies. No provider energy, token or runtime figures exist for them here |
| The relay process itself: one container ticking once a minute for a night, and its GitLab polling | Counted only (5 polls in this night) | Not deployed; no runtime measured |
| GitLab: issues, notes, merge requests, flow sessions | No | Outside the measurement |
| The build pipeline: every push runs 18 jobs on GitLab.com runners | Read from the public API, see RESULTS.md and the prize draft | Durations only; no runner energy data |
| The browser demo: static Pages files, computed once per build, no server compute per visitor | No | Zero per-visitor compute by design; not measured |

## The terms, one by one

| Term | Value for one night | Kind |
|---|---|---|
| CPU time of the decision code, baseline | mean 33.4 ms (12 runs, 95% CI 32.6 to 34.2) | Measured, on the benchmark machine, cold process |
| CPU time of the decision code, with the proposed window change | mean 31.1 ms (12 runs, 95% CI 30.5 to 31.7) | Measured, same machine, same outcomes |
| E, energy of the decision code | Not available | No energy meter. On this Mac `powermetrics` needs root ("must be invoked as the superuser"); the run was on battery at 3%. Apple publishes no per-core power figure for the M1, so no sourced watt figure is multiplied in. |
| E, energy of the model calls | Not available | Recorded replies; the provider publishes no per-call energy |
| E, energy of the relay process and GitLab | Not available | Not deployed; GitLab's own footprint is outside the boundary this benchmark can reach |
| I, grid carbon intensity | Not available | No sourced location-based factor for this machine's grid at the run's hour was obtained. The specification asks for the highest available granularity, annual values otherwise. A future run should take it from the grid operator or a public hourly dataset for the run's region and hour. |
| M, embodied emissions allocated | Not available | The device's life-cycle total (TE) was not taken from a product environmental report, and no time-share or resource-share for 33 ms of one core on an 8-core laptop is claimed without it |

**SCI score: not computed.** Every term except the decision code's CPU time is unavailable, so a number here would be invented. The specification is clear that offsets cannot lower a score; it is equally clear that a score needs E, I and M.

## What the measurement does say

- The decision code's share of a night is small: about a thirtieth of a second of one CPU core per 9-hour night, in a process whose peak resident set is about 32 MiB. The proposed change to `Metrics.window` removes about 2 ms of that (7% of the mean, intervals not overlapping at 12 runs): a resource saving, not a measured carbon reduction, and small in absolute terms.
- What the night's energy mostly is, by structure if not by measurement: the two model sessions (plus dusk and dawn on a production night), the always-on relay container, and the pipeline's 18 jobs per push. The design keeps the first bounded (at most 3 watch calls a night, code decides everything else) and the browser demo at zero server compute per visitor. Those are design choices, and this benchmark can count them, not weigh them in grams.
- "Fewer tokens" and "shorter runs" are not in this report because neither was measured: the replies are recorded, and the runs are the same length by construction (546 ticks).

## What would make a calculation possible

1. E for the decision code: run the benchmark on a machine with a readable energy counter (RAPL on Linux, or `powermetrics` as root on macOS) and record joules around the night, or on a cloud instance with a published per-vCPU power model, stated as a model.
2. E for the model: the provider's per-request energy, or a stated model with its source; token counts from a live session (the recorded replies have none).
3. I: a location-based factor for the run's region and hour from a named public dataset, with its date.
4. M: the device's or instance's life-cycle emissions from a product environmental report or the cloud provider's data, allocated by the night's time-share (33 ms of a multi-year life) and resource-share (one core of eight).

With those, SCI per night is (E_code + E_model + E_relay) x I + M, per night. The benchmark's records give the measured CPU seconds and counts the rest of the formula needs.
