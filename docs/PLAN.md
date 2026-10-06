# Plan

Night Orders, from today to the deadline. Written Tue 6 Oct 2026. Times are Pacific unless marked UTC.

Goal: build done Sat 24 Oct; video and Devpost submission done Mon 26 Oct, 9:00 PM. The hard deadline is Tue 27 Oct, 13:00 UTC (6:00 AM Pacific) ([RULES_CHECK.md](codex/RULES_CHECK.md), [DECISIONS.md](DECISIONS.md)).

## Fixed dates

| Date | What | Source |
|---|---|---|
| Mon 5 Oct, 10:00 UTC | Submissions open | [RULES_CHECK.md](codex/RULES_CHECK.md) |
| Fri 9 Oct, 10 AM ET | Hackathon webinar (optional; check the time in the calendar invite) | [DECISIONS.md](DECISIONS.md) |
| Sat 24 Oct | Our target: build done | handoff |
| Mon 26 Oct, 9:00 PM | Our target: submitted | [DECISIONS.md](DECISIONS.md) |
| Tue 27 Oct, 13:00 UTC | Deadline | [RULES_CHECK.md](codex/RULES_CHECK.md) |
| Wed 28 Oct to Sat 14 Nov | Judging. Keep the repo, video and live services up and unchanged. | [DECISIONS.md](DECISIONS.md) |
| About Mon 16 Nov | Winners announced | [RULES.md](RULES.md) |
| Fri 20 Nov | The GitLab token we create expires | our choice |

## Who does what

- **Alex**: accounts, a few taps, the signature on test nights, filming. About four hours in all. Until Fri 23 Oct, only phone steps of 15 minutes or less.
- **Claude Code**: the app, the agents, the flows, the root CI file, the docs. Reviews and merges Codex branches.
- **Codex**: `deploy/` and `docs/codex/`, on `codex/*` branches.

## Done on Tue 6 Oct

- Research, 57 scored concepts, five briefs, the choice ([IDEAS.md](IDEAS.md)).
- The decision code and one test per refusal reason; the dusk drafter (the agent's first job); a labelled demo night replayed through the real code; the relay service; the demo shop; three Duo flows checked against GitLab's flow schema; the CI pipeline, with the gcloud flag audit in the pinned SDK image.

## Week 1: Tue 6 to Sun 11 Oct, accounts and the day-one test

| When | Who | What | Done when |
|---|---|---|---|
| Tue 6 or Wed 7 | Alex, phone, 15 min | Join on Devpost. Register the Devpost username at contributors.gitlab.com/transcend-hackathon. Start the Google Cloud free trial. | Registration shows "pending" |
| Wed 7 | Codex | Deploy three services (`shop`, `shop-staging`, `relay`), the relay's runtime identity, the secrets, the Cloud Scheduler tick, the state bucket. The CLI audit still passes in the pinned image. | Branch pushed with tests |
| Wed 7 to Fri 9 | Claude Code | Review and merge Codex's branch. The rehearsal job (apply, smoke test, undo on staging), the `apply_state` job, the relay's status page, and an eval for the watch prompt over labelled demo nights (one number for the README). | CI green |
| Workspace approved (about one business day) | Alex, phone, 10 min | GitLab identity verification. Create a personal access token (scopes `api` and `write_repository`, expires 20 Nov). Add it to this Claude Code environment as `GITLAB_TOKEN` (environment settings, not the chat). | Claude Code can read the project |
| Same day | Claude Code | Push this repo to the GitLab project. Run the day-one test through the API with the token ([brief, section 10](research/ideas/brief_C01_night_orders.md#10-load-bearing-risk-fallback-and-day-one-test)): the probe flow, its trigger, the Flows API start, the merge rights, a flag change, an incident. | Results in [STATUS.md](STATUS.md) |
| By Sun 11 | Alex, phone, 30 min | Cloud Shell: run the setup script, then press Play on the deploy job. | `/healthz` answers on Cloud Run |

**Decision D1, two days after the workspace exists.** Does a flow start through the Flows API from Cloud Run, with the token, with nobody logged in, and post its note within five minutes?

- Yes: build as designed.
- It fails for a fixable reason (identity verification, role): fix it, or ask in the hackathon Discord that day.
- It still fails: try the pipeline route the next day. If that fails too, build Standing Orders (code alone acts at night; the model drafts at dusk and writes the log at dawn).

Also settled by the day-one test: whether Alex can merge to the default branch. If not, the signature is an approval (code reads who approved and when).

## Week 2: Mon 12 to Sun 18 Oct, the live loop

| When | Who | What |
|---|---|---|
| Mon 12 to Wed 14 | Claude Code | Real GitLab feature flags read by the shop (through the API with the token: `new_checkout` with a User IDs strategy for the demo pilot customers `pilot-01` to `pilot-10`, `stock_from_cache` off); the relay changes them with the token. Real incidents and notes, with the shop's recent error log lines from Cloud Logging in the evidence pack. The watch flow started at night (or the D1 fallback). |
| Wed 14 to Fri 16 | Claude Code | The dusk flow on a real watch issue, drafting from merge requests really merged that day. The dawn flow, the countersign merge request and `apply_state`. |
| Sat 17 or Sun 18 | Alex, phone, 20 min | First full test night (compressed clock, about 25 minutes): merge or approve the orders, then one thumbs-up when paged. |

**Decision D2, Sun 18 Oct.** Did the first test night run end to end? If not, cut in this order: the dusk question; Cloud Monitoring (the relay raises alerts from the shop's counters); the dawn flow (code writes the log, the countersign stays a merge request).

## Week 3: Mon 19 to Sat 24 Oct, second night, polish, freeze

| When | Who | What |
|---|---|---|
| Tue 20 or Wed 21 | Alex, phone, 20 min | Second full test night. |
| Wed 21 to Thu 22 | Claude Code | Fix what the two nights found (at most two review rounds per change). The live status page with a passcode-protected "run a demo night" button, five runs a day. Final README and diagram. The video script and shot list. |
| Fri 23 | Alex, laptop | Walk through the whole loop once. Rehearse the shots. |
| Sat 24 | everyone | Build done. Tag the release. |

**Decision D3, Wed 21 Oct.** If the second night is not clean, film the night with Standing Orders and say so in the video.

Never cut: the dusk draft, the signature, the two-key night check, the dark phone, the wake page.

## Sat 24 to Mon 26 Oct: video and submission

| When | What |
|---|---|
| Sat 24, evening | Film a real demo night (about 25 minutes, compressed clock), plus the dusk and dawn screens. |
| Sun 25 | Edit to about 2:40 (the limit is under 3:00). Captions: "Demo app, planted fault, time compressed." Upload to YouTube as Public. |
| Mon 26, by 9:00 PM | Devpost form. The GitLab repo is public, MIT is shown in its About section, the CI history is visible, the live link works. Submit. |
| Tue 27, 6:00 AM | Deadline. From here, freeze the repo, the video and the live services until winners are announced. Any further work goes in a fork. |

## Risks

| Risk | Early sign | Response |
|---|---|---|
| The Flows API will not start a flow from the relay | 403 or 404 in the day-one test | D1: the pipeline route, then Standing Orders |
| Alex cannot merge to the default branch | No merge button on the test merge request | The signature becomes an approval; ask the organizers in Discord |
| Alex is busy until Fri 23 Oct | Phone steps slip | Keep every step before Oct 23 to the phone. With the token in the environment, Claude Code runs the API steps. |
| The workspace approval is slow | Still "pending" after two business days | Ask in Discord. Keep building offline: everything except the live night runs without accounts. |
| Google Cloud costs | Budget alert email | Free tier and trial credit; a USD 5 budget alert; Scheduler at one job; the teardown script after judging |
| Cloud Monitoring alert policies are billed | Billing line item | The relay raises alerts from the shop's counters instead |
| Not enough time | D2 or D3 missed | The cut order above |
| Someone copies the idea (the repo is public) | A similar entry appears | Keep building. The signed nightly fence and the 07:00 expiry are the idea, and our CI history shows when we built them. |
