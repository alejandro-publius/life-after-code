# Status

Last updated: **Sun 11 Oct 2026, about 17:00 UTC**.

## Current state

| Item | State |
|---|---|
| Concept | Night Orders. A review on branch `claude/concept-review` (6 Oct) proposed No Mouse; not adopted ([DECISIONS.md](DECISIONS.md), 11 Oct). The live gate below decides, and No Mouse stays the backup. |
| Works offline | The decision core, dusk drafter, relay, demo shop, browser demo at `/demo`, day sheet, morning countersign with exact restore, kept changes that end when their fix ships, three Duo flows plus the probe flow, the day-one script, the test-night runner and the Standing Orders fallback. `uv run pytest -q`: **493 passed**, 93% line coverage. `flows/validate.py`: 4 flows ok. |
| Deploy code | Codex's three-service deploy (shop, shop-staging, relay; scoped identities, five secrets, Scheduler, state bucket, uptime check) reviewed with three lenses and a refuter per finding, then merged on 11 Oct. 48 deploy tests pass locally except the two alpha/beta help checks, which pass in the pinned SDK image (4 tests OK, Google Cloud SDK 587.0.0). Twelve minor follow-ups went to Codex in the session report. |
| CI | GitHub Actions ([checks.yml](../.github/workflows/checks.yml)) is green on main for every push today. The GitLab pipeline ([.gitlab-ci.yml](../.gitlab-ci.yml)) has not run yet: there is no GitLab project with our code in it. |
| Live | **Nothing has run on GitLab.com or Google Cloud.** Alex reports the workspace registration was approved on about 10 Oct; the workspace link and a token are not in this environment yet ([MORNING.md](MORNING.md)). |
| Next | The live gate: [scripts/day_one.py](../scripts/day_one.py) within 48 hours of the token (decision D1 in [PLAN.md](PLAN.md)). Then the flows in GitLab, the Cloud Run deploy, and the first test night on 17 or 18 Oct ([TEST_NIGHT.md](TEST_NIGHT.md)). |

## What landed on 11 Oct

- `scripts/day_one.py` and `flows/probe.yml`: the live gate, nine rerunnable steps with 20 offline tests, built on [research/gitlab_day_one_api.md](research/gitlab_day_one_api.md).
- `scripts/test_night.py` and [TEST_NIGHT.md](TEST_NIGHT.md): a real-time bad night against the live shop, started at a local time so the on-call person really sleeps.
- The day sheet (`relay/nightorders/daysheet.py`): at 21:00 the relay posts today's merges, deployments and flag states on the watch issue; the dusk flow reads it first.
- Relay: `GET /readyz`, settings problems count as failed ticks and page, one tick at a time across instances (a lease in Cloud Storage), the day sheet outside the watch's failure path.
- The rehearsal (`relay/nightorders/rehearsal.py`): every new orders merge request is tried on staging (apply, check the staging shop, restore) and the result is posted on it before anyone signs; traffic orders are checked for an existing revision.
- Night actions record what they changed; the countersign restores each target to its snapshot (a flag's strategies for that environment, user lists included; a service's traffic list). A no-op action leaves no loose end.
- The hardening change was reviewed with three lenses; 19 findings, 12 verified by a second reviewer, the rest judged by hand. All real ones are fixed ([commit c78f70f](../relay/nightorders/)).
- Standing Orders, the last fallback of decision D1, built as a relay setting (`WATCH_MODE=standing`): no model at night, code alone carries out the signed orders and says so on the incident and the status page. The demo night replays under it with `--standing`. Found and fixed on the way: the re-check now looks at the incident's other alerts, not only the order's own signal ([DECISIONS.md](DECISIONS.md)).
- The morning cannot be lost (`relay/nightorders/morning.py`): a night never countersigned is carried into the next, one quiet push says what the night did, and code opens the countersign merge request when no flow does.
- A kept change is a lease (`relay/nightorders/kept.py`): `until_deployed: 39` in `ops/state.yml` ends the keep once that merge request is in the last successful production deployment; code restores the snapshot in daytime and notes it on the watch issue. The day sheet and the status page list what is kept.
- The pipeline (`.gitlab-ci.yml`): merge request pipelines, locked dependencies, pinned tools and images, coverage, lint, the browser walk, SAST, IaC scanning, secret detection, a dependency audit with an SBOM, and a scheduled night report (`scripts/night_report.py`). `tests/test_pipeline_config.py` keeps it that way. Incident notes add GitLab timeline events.
- The refusal gallery ([REFUSALS.md](REFUSALS.md), `relay/nightorders/refusals.py`): 23 attempts against the real decision code, 0 production changes, and a control row that acts. A test keeps the page equal to the code's output. Writing it found that a fourth drafted order made the orders check print the whole file back; the message now says "at most 3 allowed, found 4".
- [ADOPT.md](ADOPT.md): what another team needs and the eight steps to run Night Orders on its own project, with today's limits.
- `scripts/video_pace.py`: both shot tables in [VIDEO.md](VIDEO.md) fit their slots and 3:00 (a test runs it); it found a cold-open scene with 23 words in 5 seconds, now rebalanced. It also writes captions.
- Devpost gallery: five 3:2 images in `docs/images/gallery/`, made by `scripts/gallery.py` from components the browser captured from the running demo; the README screenshots are refreshed and show the kept change's lease.
- The case for impact, with sources marked (unverified) until Alex opens them: [research/oncall_case.md](research/oncall_case.md).
- The flows: the dusk flow never waits on a person (its question goes in the merge request), the commit writers see their tool results and pass the branch on, and a test checks every prompt placeholder is wired.

## Verified locally on 11 Oct

| Check | Result |
|---|---|
| `uv run pytest -q` | 493 passed, 1 upstream Starlette deprecation warning; 93% line coverage |
| `uvx --from ruff==0.14.0 ruff check relay shop agent scripts tests flows` | all checks passed |
| pip-audit of the locked runtime dependencies, hashes required | no known vulnerabilities |
| `uv run python flows/validate.py` | dawn, dusk, probe, watch: ok |
| `python3 -m unittest discover -s deploy/tests` | 48 tests, 46 pass; the two alpha/beta help checks need the pinned image |
| The same audit in the pinned SDK image (Docker) | 4 tests OK, 60 command paths and 61 flags |
| Demo night replay and the orders and state checks | pass (run by GitHub CI on every push) |
| Long-dash scan of every changed file | none |

## Not yet true

- No GitLab pipeline history, no flow session, no incident, no flag change, no Cloud Run service, no page on a phone.
- The dusk drafter has only run on its recorded answer (no Anthropic key here), and no Duo flow has run.
- No measured benefit: the counts in the demo are from an invented night.

## Progress

| Part | File | State |
|---|---|---|
| Rules | [RULES.md](RULES.md) | Research retained; [RULES_CHECK.md](codex/RULES_CHECK.md) controls where the early notes differ. |
| 1. Past winners | [PAST_WINNERS.md](PAST_WINNERS.md) | 102 winners across 15 events. |
| 2. Patterns | [PATTERNS.md](PATTERNS.md) | Counts, anti-patterns and ten project rules. |
| 3. Current field | [FIELD.md](FIELD.md) | Dated field research. |
| 4. Sponsors | [SPONSORS.md](SPONSORS.md) | Sponsor research. |
| 5. Ideas | [IDEAS.md](IDEAS.md) | 74 concepts, 57 scored, five briefs; Night Orders chosen; the 6 Oct review on its own branch. |
| 6. Build and plan | [PLAN.md](PLAN.md), code and pipeline files | Everything above the live line. |
| Public materials | [README](../README.md), [GUIDE](GUIDE.md), [DEVPOST](DEVPOST.md), [VIDEO](VIDEO.md), [MORNING](MORNING.md), [TEST_NIGHT](TEST_NIGHT.md), [FLOWS_SETUP](FLOWS_SETUP.md) | Current as of 11 Oct; links to a public GitLab project, a live URL and the video are pending. |

## Historical research access limits

The initial research session reported these network refusals (HTTP 403 on CONNECT or "EGRESS_BLOCKED" from WebFetch). This table records the limits of that earlier research, not the current environment's access policy. The official October Devpost pages were read successfully later, as documented in [RULES_CHECK.md](codex/RULES_CHECK.md) and [source-status.json](codex/source-status.json).

| Host | What we lost | Workaround used |
|---|---|---|
| devpost.com and every *.devpost.com page (gitlab-transcend, gitlab, run, googlecloudmultiagents and others) | The live rules, updates, discussions, gallery, participants and every winner page | Search engine excerpts (tagged as such), GitLab's own guide source on gitlab.com, project repos |
| about.gitlab.com (blog, stages page, events) | GitLab's winner announcements and the DevSecOps stages page | Search excerpts; GitLab's www repo data files on gitlab.com |
| docs.gitlab.com | GitLab documentation site | The same docs read from source: gitlab.com/gitlab-org/gitlab/-/raw/master/doc/... |
| contributors.gitlab.com | GitLab's hackathon pages and registration API | The page source on gitlab.com (contributors-gitlab-com repo) |
| forum.gitlab.com | GitLab forum | none |
| web.archive.org | Archived copies of blocked pages | none |
| youtube.com | Demo videos of past winners (length, content) | Video titles and descriptions from search excerpts only |
| x.com, linkedin.com, medium.com, dev.to, discord | Social posts by entrants and winners | Search excerpts |
| developers.googleblog.com, discuss.google.dev | Some Google announcements | cloud.google.com blog where possible |
| html.duckduckgo.com, www.bing.com | Fallback search | none |
| github.com and api.github.com through curl | Raw API access | WebFetch on github.com pages works |

The initial session exhausted its reported 200-search budget by about 01:40 UTC on 6 Oct, which was still 5 Oct Pacific Time. Later research in that session relied on fetching known pages directly. Items that needed more searching remain marked "(unverified)" in the research docs.

Third-party mirrors of blocked pages appeared in search results. They were not used, because that would route around the block.

## Environment notes

- The browser demo runs with recorded, clearly labelled fixtures and requires no model key or external token.
- GitLab and Google Cloud configuration has not been supplied for the live integration. No GitLab push or cloud deployment is reported here.
- The GitHub repository is public. Its source and research are readable before the deadline; it does not replace the required public GitLab submission repository.
