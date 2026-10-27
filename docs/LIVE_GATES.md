# Live gates

What has really run on GitLab and Google Cloud. Written by [scripts/live_gates.py](../scripts/live_gates.py) at 2026-10-27 11:20 UTC. **6 of 15 passed.** A gate without evidence stays pending; the offline checks are in [STATUS.md](STATUS.md).

| Gate | State | Evidence |
|---|---|---|
| The token works and the role on the project is known | pending |  |
| The GitLab project is public and its MIT licence is detected | passed | [https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase) |
| The standing watch issue exists | passed | [https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/2) |
| The feature flags an order may touch exist, per environment | pending |  |
| The flows are enabled in the project | passed | [https://github.com/alejandro-publius/life-after-code/blob/c369846/docs/HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable](https://github.com/alejandro-publius/life-after-code/blob/c369846/docs/HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable) |
| A flow started through the Flows API ran and posted its note (decision D1) | passed | [https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703) |
| The on-call person can sign by merge or by approval | pending |  |
| The relay answers in public (/healthz) | pending |  |
| A real night: a signed order ran and the re-check passed | pending |  |
| A real countersign was applied by code | pending |  |
| A GitLab pipeline on the default branch passed | passed | [https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2993982870](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2993982870) |
| The browser demo is public on GitLab Pages | pending |  |
| A tagged GitLab Release links the demo, the images and the pipeline | passed | [https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.8](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.8) |
| The relay and the shop were deployed to Cloud Run by the pipeline | pending |  |
| The video is public on YouTube, under 3:00 | pending |  |
