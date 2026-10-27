# Status

Updated **27 Oct 2026** during the Codex submission handoff.

**Night Orders is on GitLab with persistent incident memory and a browser explorer of real Duo work.** Dusk created a validated orders merge request; watch posted a parsed refusal. Their recorded steps and artifacts are visible in the explorer. The guided shop night remains a labelled replay. The relay and shop have not been deployed to Google Cloud, and no real overnight flag change or morning countersign has run.

## Current evidence

| Item | State and source |
|---|---|
| Source | [GitHub main](https://github.com/alejandro-publius/life-after-code/tree/main) at `6311445` was synced to [GitLab main](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/tree/main) through merge `45fb150`, preserving GitLab's starter history without a force push. It includes the permission explorer, flow installer, persistent incident memory and real-execution explorer. |
| GitLab project | [Showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase), project `88050495`. Its public API confirms public visibility and the MIT licence. |
| Pipeline | [2994433358](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2994433358) passed all 18 jobs for `45fb150` on `main`, confirmed through the public API. It reports 663 application tests and 94% coverage. This covers the execution explorer and incident memory; later commits require their own pipeline result. |
| Release | [v0.1.18](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.18) contains the execution explorer sync, confirmed through the public API. |
| Standing watch | [Issue #2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/2), titled "Tonight's watch", confirmed through the public API. |
| Duo | Codex independently read the saved GitLab checkpoints and linked artifacts for [watch session 10120703](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703) and dusk session 10124688. Watch's posted refusal passes the relay's real request parser. The [execution explorer](https://showcase-700ee4.gitlab.io/activity.html) displays both runs, 24 captured steps and their original artifact links. [Capture provenance](EXECUTION_EXPLORER.md). |
| Incident memory | Observed incident history persists across nightly resets and informs the next dusk briefing. The browser exposes decision chains and a downloadable shift handoff. Approval and measured recovery remain separate outcomes. [Implementation and winner research](INCIDENT_MEMORY.md). |
| Flow installation | The new [setup command](FLOWS_SETUP.md) installed dusk and dawn and verified all three application flows against their released GitLab definitions and actual service accounts. A repeated apply made zero changes. [Read-back evidence](codex/FLOW_SETUP.md). Installation does not establish execution. |
| Dusk execution | [Session 10124688](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10124688) completed its scout, critic, commit and MR sequence. [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/merge_requests/1) contains only a valid zero-order `ops/night-orders.yml`: no merged change or deployment justified an action. It remains a draft, unapproved and unmerged. [Execution evidence and review adjustment](codex/FLOW_SETUP.md#live-dusk-execution). |
| Pages | The Pages build and deployment passed in pipeline `2994433358`. [Published demo URL](https://showcase-700ee4.gitlab.io). Public playback remains unverified here: the environment proxy returned HTTP 403 on CONNECT to this host. Local phone and laptop browser checks, the static build and all four HTTP replay outcomes pass. |
| Checks | GitLab CI reports **663 application tests with 94% coverage**, all 18 jobs passed. Local static phone and laptop walkthroughs cover the permission explorer, incident histories and execution explorer. The running preview also passed the actual-session, artifact-link and readable-control checks on both viewports. The generated live dusk file passed the actual orders parser. [Installer and execution checks](codex/FLOW_SETUP.md). |

## Submission fixes

The day-one script used `/api/v4/graphql`, which GitLab returns as HTTP 404. Requests now go to `/api/graphql`, preserving authentication, the 20-second timeout and any self-managed URL prefix. Catalog discovery, probe creation/enabling and workflow-status queries share this correction. The existing `serviceAccount` and `parentItemConsumer` fields are present in GitLab's published schema, so they remain in the query. See [GraphQL reference](https://docs.gitlab.com/api/graphql/reference/) and [the check record](codex/SUBMISSION_CHECK.md).

The live-gates generator now accepts explicit evidence links for day-one gates when the original result JSON is unavailable. It does not pretend those links are a fresh script run, and a supplied link cannot replace a failed measured check. [LIVE_GATES.md](LIVE_GATES.md) distinguishes these linked historical observations from pending work.

## What still needs to happen

- Continue syncing new GitHub commits through normal merges that preserve GitLab's history. The repositories are separate, with no automatic mirror configured. The `6311445` execution explorer sync is complete and its pipeline passed; never force-push GitLab `main`.
- Claude's independent task is the live Dawn demonstration, with flow fixes and evidence in its assigned paths. [Self-contained parallel handoff](CLAUDE_PARALLEL_HANDOFF.md). Codex remains the GitLab main writer.
- Open the Pages demo in a browser and play sign, approve and morning. Its local build passes; the public URL has not been verified here.
- Alex must complete the [Devpost submission](https://devpost.com/submit-to/31503-life-after-code/manage/submissions/1220111/edit) using [DEVPOST.md](DEVPOST.md). The recorded deadline is **27 Oct, 13:00 UTC (6:00 AM Pacific)**, from [the rules check](codex/RULES_CHECK.md).
- Alex will handle the video before submission. Upload a public English YouTube video under 3:00 and add its link to the form, as required by the [rules check](codex/RULES_CHECK.md). A finished upload has not been verified, so the submission is not claimed complete.
- No Google Cloud deployment, live overnight action or morning countersign has been demonstrated. No Cloud bonus is claimed. Dawn has not run live. Demo impact counts are from an invented night.

## Earlier work

The previous 11 Oct status described the offline build before GitLab access arrived. Its statement that nothing had run on GitLab is superseded by the evidence above. Research, design decisions, the reviewed deployment code and the offline test history remain in [DECISIONS.md](DECISIONS.md), [PLAN.md](PLAN.md), [the handoff](HANDOFF.md), and Git history. Earlier reported network blocks do not establish current access; the Pages restriction above was checked in this session.
