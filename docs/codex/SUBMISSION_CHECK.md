# Submission handoff checks, 27 Oct 2026

Codex is continuing Night Orders from Claude's [handoff](../HANDOFF.md). Alex authorized taking over the code and pushing to GitHub main. No redesign or new project is underway.

## First code fix, pushed to GitHub

Commit `0c972ee` corrects the day-one script's GraphQL endpoint. Read-only requests to GitLab showed `/api/v4/graphql` returning HTTP 404 and `/api/graphql` returning HTTP 200. The configured-items query also returned HTTP 200 from the correct endpoint. Without authentication it returned an empty list, which does not establish that the project has no configured flows.

The [published GraphQL schema](https://gitlab.com/api/graphql) includes `AiCatalogItemConsumer.serviceAccount`, `parentItemConsumer`, and the existing create/enable mutation inputs. The failure was the endpoint, not evidence that these fields should be removed. The [GraphQL documentation](https://docs.gitlab.com/api/graphql/) describes the endpoint.

Validation: `uv run --locked pytest -q tests/test_day_one.py` passed all 25 tests. They cover catalog discovery, probe creation and enabling, workflow-status reads, authentication and timeout preservation, and a self-managed GitLab URL prefix. Ruff passed. Authenticated mutations have not been rerun here because GitLab credentials are missing.

## Final local validation

`uv run --locked pytest -q --cov=relay --cov=shop --cov=agent --cov-report=term` passed **622 tests**, with **94% coverage** and one upstream Starlette deprecation warning. This includes the five new regression cases and the handoff document's link check. The seven live-gate tests pass, including recovery of evidence without a day-one JSON file, preservation of failed checks and refusal of credential-bearing links. Repository-wide Ruff checks passed. No deployment code or pipeline configuration changed.

## Evidence provenance

| Observation | Evidence |
|---|---|
| Public project and detected MIT licence | Read-only `GET https://gitlab.com/api/v4/projects/88050495?license=true`, HTTP 200 |
| Standing watch issue | Read-only `GET https://gitlab.com/api/v4/projects/88050495/issues/2`, HTTP 200, title "Tonight's watch" |
| Passing default-branch pipeline | Read-only `GET https://gitlab.com/api/v4/projects/88050495/pipelines/2993982870`, status `success`, 94% coverage |
| Published release | Read-only `GET https://gitlab.com/api/v4/projects/88050495/releases?per_page=1`, tag `v0.1.8` |
| Watch/probe enabled and a finished watch session | Claude's [handoff](../HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable). Historical evidence; this session's unauthenticated incident-notes request returned HTTP 401. |
| Public Pages playback | Unverified: CONNECT to `showcase-700ee4.gitlab.io` returned HTTP 403 from this environment's proxy. |
| GitHub write access | Commit `0c972ee` pushed successfully to `origin/main`; `git ls-remote` confirmed its full SHA. |
| GitLab write access | Read-only fetch works. A push dry run requests credentials, and `GITLAB_TOKEN` is unset. No GitLab push from this session is claimed. |

The original day-one result JSON was not retained. Do not manufacture it. The live-gates command accepts explicit confirmation links, preserving the source rather than describing a reconstructed JSON file as a new run. It does not fetch or verify supplied links. Current token/role checks, flags, signature, public Pages playback, deployment, real-night actions, morning and video remain pending.

## Rebuild the live evidence page

From the repository root, after reviewing the evidence above:

```sh
uv run --locked python scripts/live_gates.py \
  --done publish=https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase \
  --done issue=https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/2 \
  --done catalog=https://github.com/alejandro-publius/life-after-code/blob/c369846/docs/HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable \
  --done flow=https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703 \
  --done pipeline=https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2993982870 \
  --done release=https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.8 \
  --out docs/LIVE_GATES.md
```

This records six historically confirmed gates. It is not proof that new GitHub commits have reached GitLab or that a complete live night ran.
