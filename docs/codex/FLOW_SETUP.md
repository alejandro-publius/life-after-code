# Verified Duo flow setup

On 27 Oct 2026, `scripts/setup_flows.py` checked the live GitLab project `88050495`, created and enabled the missing dusk and dawn flows, and preserved the existing watch flow. Read-back matched the released definitions to the checked-in YAML and returned each actual service account. A repeated apply reported zero changes.

| Workflow | Consumer ID | Service account | Trigger requested at creation |
|---|---|---|---|
| Dusk | `13304391` | `ai-night-orders-dusk-gitlab-ai-hackathon` | Assign |
| Watch | `13303670` | `ai-night-orders-watch-gitlab-ai-hackathon` | Existing configuration preserved |
| Dawn | `13304393` | `ai-night-orders-dawn-gitlab-ai-hackathon` | Mention |

[Machine-readable read-back](flow-setup-evidence.json) includes released version IDs and local definition hashes. The `execution: not_run` fields mean the installer did not start a flow; they do not erase the watch session recorded in the earlier handoff. Dusk and dawn execution remains unverified. No order was signed and no production action was performed by this setup.

The regression tests exercise read-only mode, repeated apply, recovery after partial setup, catalog pagination, ownership checks, definition mismatches, disabled triggers, ambiguous accounts, failed read-back and credential redaction. The installer does not silently update an existing flow or guess a service-account username.

Reproduce from the repository root with `GITLAB_TOKEN` set in the process environment:

```sh
uv run --locked python scripts/setup_flows.py --project 88050495 --out /tmp/night-orders-flows.json
uv run --locked pytest -q tests/test_setup_flows.py tests/test_day_one.py
```

GitLab sources: [custom flows](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), [GraphQL reference](https://docs.gitlab.com/api/graphql/reference/). The live API's schema and the successful requests were checked during this run. [Setup and manual fallback](../FLOWS_SETUP.md).
