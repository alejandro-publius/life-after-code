# Decisions

Each entry: date, decision, reason.

## 2026-10-06: push to both main and the session branch

The handoff says "commit and push to main after every part". The cloud session is set up to develop on `claude/life-after-code-hackathon-5wm0gs`. Work is committed on that branch and pushed to both `claude/life-after-code-hackathon-5wm0gs` and `main`, so the handoff instruction is met and nothing is lost if the session ends.

## 2026-10-06: dashes in quoted text

Alex asked for no em dashes anywhere. Where a source quoted word for word contains an em dash or en dash, it is replaced with a spaced hyphen " - ". Everything else in the quote is kept exactly.

## 2026-10-06: rule conflicts (from docs/codex/RULES_CHECK.md and docs/RULES.md)

The Official Rules say they win over any other hackathon material. Codex read them directly. Each conflict and the choice made:

| Conflict | Sources | Choice |
|---|---|---|
| Deadline time | Rules and dates page: Oct 27, 13:00 UTC. GitLab's guide and code: 14:00 UTC. | 13:00 UTC (6:00 AM Pacific). Our own target is Oct 26, 9:00 PM Pacific. |
| Judging end | Rules: Nov 14, 17:00 UTC. GitLab's guide: Nov 11. | Nov 14. Keep everything live and frozen until winners are announced (about Nov 16). |
| Submission opening | Rules: Oct 5, 10:00 UTC. Dates page: Oct 5, 17:00 UTC. | Rules. Make the first commit of new work after Oct 5, 10:00 UTC (the repo began Oct 6, so this is met). |
| Judging start | Rules: Oct 28, 10:00 UTC. Dates page: 09:00 UTC. | Rules. No effect on us. |
| Public or private repo | Submission requirements: "must be public". A generic testing paragraph mentions private repos. | Public GitLab repo with visible CI history. |
| Third-party licences | Rules allow OSI-approved third-party licences. The FAQ says everything must be MIT. | Our own work is MIT. Third-party packages keep their own OSI licences and notices, per the more specific rule. |
| YouTube visibility | Rules: "publicly visible". FAQ: Public or Unlisted. | Public, under 3:00 (aim for 2:40). |
| Edits after deadline | Rules freeze the submission. FAQ also freezes the repo, video and linked material until winners. | Freeze everything from Oct 27 to about Nov 16. Any further work goes in a fork. |
| Webinar time | Resources page gives two clock readings for Oct 9. Home page: Oct 9, 10 AM ET. | Check the calendar invite after registering. Not needed for the build. |
| Autonomy prize vs special prize | Earlier notes left open whether one project can win several prizes. | Rules: one path prize plus one special prize at most. Plan for one autonomy prize and one special prize (Most Stages Covered or Most Creative). |

## 2026-10-06: Codex deploy branch merged

Codex's `codex/deploy-skeleton` branch (keyless Cloud Run deploy, setup and teardown scripts, placeholder app) was reviewed and merged. Its 9 mocked tests pass here. One follow-up was sent back to Codex: `gcloud run deploy` in gcloud 530 has `--min` but no `--max` flag, so `--max=1` may fail; `--max-instances=1` alone is enough. A second follow-up: the job reads its Google Cloud values from CI/CD settings, which need the Maintainer role; since none of them are secrets, they should also be settable in the CI file.

## 2026-10-06: CLI audit runs in the pinned CI image

`deploy/tests/test_cli_flags.py` checks every gcloud flag the deploy scripts use against the real help text. Run on this machine's gcloud 530 it fails two subtests (`alpha projects update`, `beta services identity create`) only because the alpha and beta components are not installed here. Run inside the pinned CI image (`gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:be4876b4...`, Google Cloud SDK 587.0.0 with alpha and beta 2026.09.25) it passes: 2 tests, OK. The audit stays as written and becomes a CI job in that image, so it runs on every pipeline.

## 2026-10-06: build Night Orders

Chosen from 57 scored concepts and five briefs ([IDEAS.md](IDEAS.md)). It ranks first on the five official criteria (mean 8.53, level with No Mouse and ahead on Technological Implementation, the first tie-break) and first on our total (88.6 of 110). No Mouse is the backup; Front Row is the first alternate. The prize plan is Path A Best Hands-off Agent plus Most Stages Covered.

## 2026-10-06: where the orders schema lives

The brief put the schema at `ops/schema/night-orders.schema.json`. It lives at `relay/nightorders/night-orders.schema.json` instead, inside the Python package, so the relay container (built from `relay/` alone) can load it.

## 2026-10-06: recorded mode for the dusk drafter

This cloud session has no Anthropic API key and no GitLab token. The dusk drafter (`agent/dusk.py`) calls Claude through the Anthropic API when a key is present, and otherwise uses a recorded answer from `demo/night-2026-10-20/dusk_recorded.json`. The orders file it writes then says "DEMO DATA" in its header, and the merge request text says the draft came from a recorded answer. Code validates both kinds of draft the same way. In GitLab the same job is the dusk Duo flow.

## 2026-10-06: the relay raises alerts itself in the first build

The relay reads the shop's per-minute counters each tick and applies the rules in `ops/alerts.yml`. A Cloud Monitoring alert policy with Pub/Sub is left for later: it adds moving parts, and its price from May 2026 is known only from a search excerpt (unverified). The cut order in [PLAN.md](PLAN.md) already allowed this.

## 2026-10-06: how the relay's tick is protected

The relay's status page must be public, and Cloud Run's invoker setting covers a whole service. So `/tick` checks a shared key (`X-Relay-Key`) kept in Secret Manager, which the Cloud Scheduler job sends. CI jobs that ask the relay to rehearse or apply state will use GitLab ID tokens that the relay verifies, so CI never holds the GitLab token.

## 2026-10-06: pages go to ntfy

GitLab escalation policies need the Maintainer role, so the night page is a push notification through an ntfy topic with a random name, plus a note on the incident. The thumbs-up that approves a suggested action is read from that note, and code checks who reacted and when.

## 2026-10-06: Alex's steps stay on the phone until Oct 23

Alex is busy until Oct 23. Every step before then is a phone step of 15 minutes or less. Once the workspace exists, Alex adds a GitLab token to the Claude Code environment as `GITLAB_TOKEN` (never in the chat or the repo), and Claude Code runs the API parts of the day-one test and pushes the code to GitLab.

## 2026-10-06: the relay applies the morning countersign

The dawn flow writes the kept changes to `ops/state.yml` in the countersign merge request. When the on-call person signs it (merge, or approval where merging is not allowed) after the watch end, the relay undoes every other night change, once, and notes what it did on the watch issue. A state file cannot make a new change, a countersign by anyone else changes nothing, and a traffic change that is not kept is listed for a person to undo, because code does not know which revision should serve next. Code for this: `relay/nightorders/countersign.py` and `relay/nightorders/morning.py`. Superseded on 2026-10-11: a change with a snapshot, traffic included, is restored by code to that snapshot (see the exact restore entry below).

## 2026-10-06: two apps named main.py

The relay and the shop are each deployed from their own folder with a `main.py`, as the deploy contract asks. Their tests load each `main.py` from its file under its own module name, so one test run can cover both.

## 2026-10-06: what "on" means for a flag

`flag_set` to `"on"` turns a flag on for every user in that environment. Turning a flag off removes its strategies for that environment only. So turning a flag back on does not restore an earlier partial rollout (for example the demo's pilot customers); a person does that in GitLab. This keeps the night action simple and its undo predictable.

## 2026-10-06: every thumbs-up is checked

The relay's builder found that taking only the first thumbs-up on a page note let a teammate's reaction block the on-call person's own approval. Now code checks every thumbs-up, oldest first: a refused one is noted once and the suggestion keeps waiting, and a suggestion nobody approves within 60 minutes of the page is dropped with nothing changed.

## 2026-10-11: exact restore at the countersign

A code audit found three gaps: the ledger did not say whether an action changed anything, so an order that set a flag already off was still "undone" (turned on) in the morning; the morning undo was a plain inversion, so turning a flag back on gave it to every user instead of the earlier rollout (the demo's `new_checkout` was on only for pilot users before the night), and a traffic change could not be undone at all; and the docs promised more than the code did.

Now every port action returns a `Change`: whether anything changed, a JSON-safe snapshot of the target from before the action, and plain words. The ledger keeps `changed` and `before` on acted and approved events, and an action that changed nothing says so and leaves no loose end. At the countersign, code calls `restore` with the snapshot: a flag gets back exactly the strategies it had for that environment (re-created with a scope for that environment only, and read back to check), a service gets back its earlier traffic allocation. The night action still means on for every user, as the 2026-10-06 entry says, but the morning restore puts back the earlier strategies instead of turning the flag off or on for everyone, so that entry's last sentences no longer hold. Records written before this change have no snapshot: a flag is then turned the other way, as before, and a traffic change is listed for a person. Code for this: `relay/nightorders/model.py` (`Change`), `gitlab_ports.py` (`flag_snapshot`, `flag_restore_changes`, `restore`), `dawn.py` (`LooseEnd`), `countersign.py` and `morning.py`.

## 2026-10-11: Night Orders stays; the live gate decides, not another review

On 6 Oct a separate session reopened the concept choice on branch `claude/concept-review` and recommended No Mouse, pending a Codex review that never happened. Its two solid points are kept: the hackathon role's ability to create and enable a custom flow is the one gate every candidate shares, and the Night Orders code had real gaps (a relay that answered healthy while every tick failed, two overlapping ticks, a morning undo that was a plain inversion). The gaps are fixed on main today (readiness and paging on settings problems, one tick at a time across instances, change snapshots and an exact restore at the countersign). The concept is not switched: sixteen days remain, the code and demo exist, and the live gate is the same for every candidate. The day-one test ([scripts/day_one.py](../scripts/day_one.py)) runs within 48 hours of the token arriving; if the Flows API cannot start a flow for this role, the fallback order in [PLAN.md](PLAN.md) applies (pipeline route, then Standing Orders), and No Mouse stays the backup concept. The branch is kept for its research and not merged.

## 2026-10-11: the dusk flow reads a day sheet written by code

GitLab's docs list the APIs a flow's token reaches, and deployments and feature flags are not among them ([research note](research/sponsors/gitlab_duo.md), the `ai_workflows` scope; which exact APIs a custom flow's tools can call is (unverified) until the day-one test). So code collects today's merged merge requests, deployments and flag states and posts them as one note on the watch issue ([relay/nightorders/daysheet.py](../relay/nightorders/daysheet.py)); the dusk scout reads that note first and then only the diffs that matter. The same data as JSON feeds the local drafter, so both paths see the same day.

## 2026-10-11: Standing Orders is built now, as a setting, not after the live gate

[PLAN.md](PLAN.md) names Standing Orders (no model at night; code alone carries out the signed orders) as the last fallback if the Flows API will not start a flow for this account. It is built today rather than after decision D1, because it is small (one setting, `WATCH_MODE=standing` on the relay; one branch in the watch) and because it removes the one outcome of the live gate that would have cost a build day late in the plan. The relay's default stays `flow`. Under standing orders the same code checks the signature, the expiry, the numbers and the first use; what is lost is the model's check of the reason, and the note on the incident and the status page both say so, so nobody mistakes the fallback for the design. `FLOW_CONSUMER_ID` and `FLOW_SERVICE_ACCOUNT` may be empty in that mode.

Replaying the demo night under standing orders showed a gap in the re-check that was there in both modes: after an order ran, the re-check looked only at the order's own signal. Turning the new checkout off empties that path, so its error rate reads zero while the old path is still failing, and the night would have been logged as "handled" with nobody woken. The re-check now also looks at the incident's other alerts, and pages when one still fires. In the model night this changes nothing (the model declined that order); in the standing night it wakes Priya at 02:00, which is the honest outcome.
