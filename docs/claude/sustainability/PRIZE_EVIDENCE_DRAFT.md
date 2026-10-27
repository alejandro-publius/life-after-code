# Draft for the Most Environmentally Impactful opt-in (honest version)

Drafted by Claude Code on 27 Oct 2026, after the submission deadline, for Alex and Codex to decide on. The prize text asks entrants to explain "exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices" and to "quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks" ([rules check](../../codex/RULES_CHECK.md)). This draft claims only what was measured or counted, says what was not, and gives no carbon number, because none was measured. The measurements are post-submission and are labelled so.

## What Night Orders does by design, and what the benchmark counted

**The model is asked at most three times a night, and never decides.** The on-call engineer signs up to three reversible actions before bed; code evaluates the alert rules every minute and carries out a signed order only when its numbers hold; the model is started once per incident to judge whether the evidence fits, within a per-night budget (`model_runs_per_night: 3` in `ops/oncall.yml`). In the standard demo night the benchmark counted 546 minute ticks, 2743 alert-condition evaluations and 2 model sessions. A design that asked a model every minute would make 546 calls for the same night. (Counted, not weighed: the model sessions' energy is unavailable.)

**The decision loop is cheap and bounded.** One completed night costs about 33 ms of CPU on one core (12 runs, 95% CI 32.6 to 34.2 ms) with about 0.65 MiB of peak Python allocations, measured on an Apple M1 laptop. Every loop has a hard limit on steps and time; the replay itself is bounded to 960 steps and 10 seconds; the Flows API polling and the countersign restore retries are bounded in code. ([RESULTS.md](RESULTS.md), measured.)

**The browser demo costs the server nothing per visitor.** The four demo replays are computed once per build and published as static files on GitLab Pages; the relay caches the same four replays in memory (`lru_cache(maxsize=4)`) when it serves them itself. Visitors download files; no server computes a night for them. (Design, read from the code; per-visitor transfer not measured.)

**One concrete code change, measured.** A one-method change to `Metrics.window` (the per-minute alert evaluation) saves about 2.2 ms of CPU per night, 7% of the loop, with identical outcomes across 24 runs and non-overlapping 95% intervals. It is proposed to the maintainers as a patch; it is small in absolute terms, and it is a resource saving, not a measured emission reduction. ([proposed-signals-window.patch](proposed-signals-window.patch).)

## The pipeline, read from the public API

Each push to main runs 18 jobs across GitLab's nine stages. On 27 Oct 2026 the three newest successful main pipelines took 148 to 155 s of wall time and 743 to 765 job-seconds each (about 12.5 job-minutes per push), read anonymously from `GET /projects/88050495/pipelines/:id/jobs`. The longest jobs in pipeline 2994456180 were the deployment unit tests (149 s), the CLI audit (82 s), the application unit tests (78 s), the browser walk (71 s), the image build (55 s) and container scanning (53 s). Three validation jobs (flows, orders, state) each spent about 19 s, nearly all of it starting a container and syncing dependencies for a sub-second check.

What could be done, proposed and not done: run the three validations as one job (about 38 job-seconds per push, 5% of the pipeline, by the durations above); not re-run the browser walk when a push touches only docs; keep `interruptible` so a newer push cancels an older pipeline (already the case for checks). These are suggestions to the pipeline's owner; none has been applied or measured.

## What this entry does not claim

- No SCI score. The SCI needs energy (E), a location-based grid intensity (I) and allocated embodied emissions (M) for the functional unit. Only the decision code's CPU time was measured; E, I and M are unavailable, as [SCI.md](SCI.md) lists term by term. The specification permits modelled inputs when stated; none are modelled here because no defensible source was obtained.
- No token or energy figures for the model. The demo night's replies are recorded notes, so the benchmark has character counts (1051 sent in goals, 777 received) and no provider measurements.
- No measured production footprint. The relay has not been deployed; a night's container runtime and its GitLab polling (5 polls in the demo night) are counted by structure, not timed.
- No "percent greener". Fewer CPU milliseconds and fewer model calls are resource facts; turning them into carbon needs the missing inputs.

## If this is submitted

Opt in only if the form accepts a resource-level account with the SCI terms named as unavailable. Attach [RESULTS.md](RESULTS.md), [SCI.md](SCI.md) and the raw records, and state the measurement date (after the deadline). A padded version with an invented factor would be worse than none.
