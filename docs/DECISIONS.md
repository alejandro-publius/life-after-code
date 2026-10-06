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
