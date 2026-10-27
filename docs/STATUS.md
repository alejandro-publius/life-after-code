# Status

Updated **27 Oct 2026** during the Codex submission handoff.

**Night Orders is on GitLab with a passing pipeline and a real Duo watch-flow run.** The browser demo remains a labelled replay. The relay and shop have not been deployed to Google Cloud, and no real overnight flag change or morning countersign has run.

## Current evidence

| Item | State and source |
|---|---|
| Source | [GitHub main](https://github.com/alejandro-publius/life-after-code/tree/main). Codex is pushing submission fixes here. |
| GitLab project | [Showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase), project `88050495`. Its public API confirms public visibility and the MIT licence. |
| Pipeline | [2993982870](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2993982870) passed on `main`, confirmed through the public API. It reports 94% coverage. This is historical evidence, not a claim that later GitHub commits have run on GitLab. |
| Release | [v0.1.8](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.8) exists, confirmed through the public API. |
| Standing watch | [Issue #2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/2), titled "Tonight's watch", confirmed through the public API. |
| Duo | Claude's [27 Oct handoff](HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable) records enabled watch and probe flows and [finished watch session 10120703](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703). The watch declined the demo incident because no orders were signed and posted one suggestion. Codex could not independently read the incident notes without GitLab authentication. |
| Pages | [Published demo URL](https://showcase-700ee4.gitlab.io), recorded by the release job. Public playback remains unverified here: the environment proxy returned HTTP 403 on CONNECT to this host. Local demo health, assets and all four replay outcomes pass. |
| Local checks | The submission fixes pass **622 application tests with 94% coverage** and repository-wide lint. The earlier onboarding run also passed 47 deployment tests with one gcloud-dependent skip, flow/order/state validation, the static build and all four HTTP demo choices. Deployment code is unchanged. See [submission checks](codex/SUBMISSION_CHECK.md). |

## Submission fixes

The day-one script used `/api/v4/graphql`, which GitLab returns as HTTP 404. Requests now go to `/api/graphql`, preserving authentication, the 20-second timeout and any self-managed URL prefix. Catalog discovery, probe creation/enabling and workflow-status queries share this correction. The existing `serviceAccount` and `parentItemConsumer` fields are present in GitLab's published schema, so they remain in the query. See [GraphQL reference](https://docs.gitlab.com/api/graphql/reference/) and [the check record](codex/SUBMISSION_CHECK.md).

The live-gates generator now accepts explicit evidence links for day-one gates when the original result JSON is unavailable. It does not pretend those links are a fresh script run, and a supplied link cannot replace a failed measured check. [LIVE_GATES.md](LIVE_GATES.md) distinguishes these linked historical observations from pending work.

## What still needs to happen

- GitHub and GitLab are separate repositories. The handoff describes manual merges, not an automatic mirror. GitLab retains its starter merge commit. Never force-push it. GitLab push access is unavailable in this Codex environment; `GITLAB_TOKEN` must be provided securely in environment settings before syncing new commits.
- Open the Pages demo in a browser and play sign, approve and morning. Its local build passes; the public URL has not been verified here.
- Alex must complete the [Devpost submission](https://devpost.com/submit-to/31503-life-after-code/manage/submissions/1220111/edit) using [DEVPOST.md](DEVPOST.md). The recorded deadline is **27 Oct, 13:00 UTC (6:00 AM Pacific)**, from [the rules check](codex/RULES_CHECK.md).
- No video has been made. The handoff records Alex's decision to omit it; the [rules check](codex/RULES_CHECK.md) lists a public YouTube video under 3:00 as required. The submission is not claimed complete.
- No Google Cloud deployment, live overnight action or morning countersign has been demonstrated. No Cloud bonus is claimed. Dusk and dawn have not run live. Demo impact counts are from an invented night.

## Earlier work

The previous 11 Oct status described the offline build before GitLab access arrived. Its statement that nothing had run on GitLab is superseded by the evidence above. Research, design decisions, the reviewed deployment code and the offline test history remain in [DECISIONS.md](DECISIONS.md), [PLAN.md](PLAN.md), [the handoff](HANDOFF.md), and Git history. Earlier reported network blocks do not establish current access; the Pages restriction above was checked in this session.
