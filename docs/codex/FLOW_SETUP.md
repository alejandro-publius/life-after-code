# Verified Duo flow setup

On 27 Oct 2026, `scripts/setup_flows.py` checked the live GitLab project `88050495`, created and enabled the missing dusk and dawn flows, and preserved the existing watch flow. Read-back matched the released definitions to the checked-in YAML and returned each actual service account. A repeated apply reported zero changes.

| Workflow | Consumer ID | Service account | Trigger requested at creation |
|---|---|---|---|
| Dusk | `13304391` | `ai-night-orders-dusk-gitlab-ai-hackathon` | Assign |
| Watch | `13303670` | `ai-night-orders-watch-gitlab-ai-hackathon` | Existing configuration preserved |
| Dawn | `13304393` | `ai-night-orders-dawn-gitlab-ai-hackathon` | Mention |

[Machine-readable read-back](flow-setup-evidence.json) includes released version IDs and local definition hashes. The `execution: not_run` fields describe the installer, which never starts a flow. Execution was checked separately below. No order was signed and no production action was performed by this setup.

## Live dusk execution

After installation, [Dusk session 10124688](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10124688) finished with execution status `Completed` and no checkpoint errors. Its scout read the skill, watch issue, allowed targets, merge requests, deployments and recent commits. With no merged changes or deployments to justify a reversible action, it proposed zero orders. The critic accepted that draft, the commit writer changed only `ops/night-orders.yml`, and the final component opened [merge request !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/merge_requests/1).

The generated file passed the repository's actual orders parser against `ops/targets.yml` and `ops/oncall.yml`. API read-back confirmed one changed file, no approvals and no merge. The flow opened the MR without the requested draft flag; Codex marked it Draft afterward, without editing its orders. The [execution evidence](dusk-run-evidence.json) records this adjustment, the exact source commit, file hash and validation result. This demonstrates a real scout, critic, commit and MR sequence, not a production remediation. Dawn execution and a deployed relay remain unverified.

[Pipeline 2994232284](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2994232284) passed all 18 jobs for installer sync commit `e551271`, including 639 application tests and 94% coverage. [Release v0.1.15](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/releases/v0.1.15) contains that code.

The regression tests exercise read-only mode, repeated apply, recovery after partial setup, catalog pagination, ownership checks, definition mismatches, disabled triggers, ambiguous accounts, failed read-back and credential redaction. The installer does not silently update an existing flow or guess a service-account username.

Reproduce from the repository root with `GITLAB_TOKEN` set in the process environment:

```sh
uv run --locked python scripts/setup_flows.py --project 88050495 --out /tmp/night-orders-flows.json
uv run --locked pytest -q tests/test_setup_flows.py tests/test_day_one.py
```

GitLab sources: [custom flows](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), [GraphQL reference](https://docs.gitlab.com/api/graphql/reference/). The live API's schema and the successful requests were checked during this run. [Setup and manual fallback](../FLOWS_SETUP.md).
