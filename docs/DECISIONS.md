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

The dawn flow writes the kept changes to `ops/state.yml` in the countersign merge request. When the on-call person signs it (merge, or approval where merging is not allowed) after the watch end, the relay undoes every other night change, once, and notes what it did on the watch issue. A state file cannot make a new change, a countersign by anyone else changes nothing, and a traffic change that is not kept is listed for a person to undo, because code does not know which revision should serve next. Code for this: `relay/nightorders/countersign.py` and `relay/nightorders/morning.py`.

## 2026-10-06: two apps named main.py

The relay and the shop are each deployed from their own folder with a `main.py`, as the deploy contract asks. Their tests load each `main.py` from its file under its own module name, so one test run can cover both.

## 2026-10-06: what "on" means for a flag

`flag_set` to `"on"` turns a flag on for every user in that environment. Turning a flag off removes its strategies for that environment only. So turning a flag back on does not restore an earlier partial rollout (for example the demo's pilot customers); a person does that in GitLab. This keeps the night action simple and its undo predictable.

## 2026-10-06: every thumbs-up is checked

The relay's builder found that taking only the first thumbs-up on a page note let a teammate's reaction block the on-call person's own approval. Now code checks every thumbs-up, oldest first: a refused one is noted once and the suggestion keeps waiting, and a suggestion nobody approves within 60 minutes of the page is dropped with nothing changed.

## 2026-10-06 (later): feature branches and Codex review replace pushing to main

Supersedes "push to both main and the session branch" above. Work now goes on a `claude/<task>` or `codex/<task>` branch with a draft pull request. Codex reviews the pushed commits and answers READY, CHANGES REQUIRED or NOT VERIFIED for one exact SHA; only a READY SHA is merged. Nothing is pushed straight to main and nothing is force-pushed. The rules are in [AGENTS.md](../AGENTS.md#branches-and-review).

## 2026-10-06 (later): primary sources read again; differences from earlier notes

Read between 07:35 and 07:50 UTC; details and links in [refresh_2026-10-06.md](research/refresh_2026-10-06.md). The rules have not changed. Differences that matter:

| Topic | Earlier note | Primary source today | Choice |
|---|---|---|---|
| What counts as Duo use | [RULES_CHECK.md](codex/RULES_CHECK.md) states that a standalone Claude API integration does not satisfy the requirement | The [rules](https://gitlab-transcend.devpost.com/rules) give examples only (agents, flows, MCP clients) and a "reasonably uses" gate; nothing is excluded by name | Treat that sentence as our inference. Still put a real Duo flow at the core, because Stage One is pass or fail. |
| External agents | Not covered | No hackathon source mentions them; [GitLab's docs](https://docs.gitlab.com/user/duo_agent_platform/agents/external/) list the managed Claude Code and Codex agents as a Duo Agent Platform feature (Premium or Ultimate, flag for verified customers, Maintainer to enable) | Do not depend on them. |
| Licence | MIT for our work, OSI for third parties | The [rules](https://gitlab-transcend.devpost.com/rules) also put our agent YAML under MIT and require GitLab's DCO v1.1 | Add the DCO to the submission checklist. |
| Autonomy level | Unknown how it is assigned | The unpublished [gallery](https://gitlab-transcend.devpost.com/project-gallery) filters by "Path and Autonomy level", which suggests the entrant selects it (inference) | Pick the level that matches the demonstrated control points. |
| Participants | 621 (unverified) | 725 on the [home page](https://gitlab-transcend.devpost.com/) | Participants are not submissions; no track is assumed empty. |
| Updates and discussions | Blocked | Both pages read: nothing posted | Recheck before submission. |
| Field and winner reasons | Search excerpts | Organizer posts read directly ([June](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/), [February](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/)) | Use organizer statements, not inferred reasons. |

## 2026-10-06 (later): Duo capabilities the existing flows assume but the docs do not support

From the [refresh](research/refresh_2026-10-06.md#2-gitlab-duo-agent-platform), checked against docs.gitlab.com today:

- Flow tokens carry only the `ai_workflows` and `mcp` scopes. GitLab's source shows the Feature flags, Deployments and Environments APIs do not accept them, so `flows/dusk.yml` and `flows/dawn.yml` most likely cannot read flags or deployments as written. Code has to place that evidence where a flow can read it (an issue, a note or a file).
- Triggers fire only on a person's action, have no schedule form, and need Maintainer to create. The Flows API is generally available for starting a flow from code, but a start with a Developer account in the hackathon group is untested.
- A HumanInputComponent is a documented approval step. Its outputs are the conversation and `context:<name>.approval`; `context:ask_oncall.response` in `flows/dusk.yml` is not one of them.
- Signing by merging needs Maintainer on a protected default branch, and by default the author of a flow-created merge request cannot approve it.
- These affect any concept, and are inputs to the [concept review](IDEAS.md#0-reopened-selection-6-oct-2026). No flow was changed in this batch.

## 2026-10-06 (later): what the code audit found in Night Orders

Every one of the ten concerns listed in the 6 Oct handoff was checked against the code on main at `484c411`: eight are confirmed and two partly. The most visible: `/healthz` answers ok while `/tick` fails on blank flow settings; two overlapping ticks can open two incidents and send two pages; the morning reversal covers flag changes only (traffic is listed for a person, and a no-op night action is still reversed); turning a flag back on gives every user the flag, not the earlier rollout. The README, DEVPOST and relay README claimed that code undoes every change that is not kept; that wording was corrected in this batch to match the code. No code was changed.

## 2026-10-06 (later): concept selection reopened; recommendation pending Codex review

Supersedes "build Night Orders" above, which rested on AI persona scores and on platform assumptions that the [refresh](research/refresh_2026-10-06.md) no longer supports. Four candidates were rewritten to documented capabilities and attacked by AI critics ([panel appendix](research/ideas/concept_panel_2026-10-06.md)). The lead recommends **No Mouse** (revised), with **Forget Me** as the closest alternative, Path A Best Supervised Agent and Most Creative ([IDEAS.md, section 0](IDEAS.md#0-reopened-selection-6-oct-2026)). The choice is not final until Codex reviews it and a local feasibility experiment shows the model beating a strong no-model baseline. The Night Orders code stays on main, unchanged, until a replacement is selected and the transition is reviewed.
