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
