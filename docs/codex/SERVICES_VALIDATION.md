# Night Orders deployment handoff

Recorded 2026-10-06 at 04:51 UTC. Branch: `codex/deploy-services`, based on application commit `5fac2ebf9d3b178cf5d54b85340cb286f861ba1d`. Only `deploy/` and `docs/codex/` changed. Main, apps, flows and the root pipeline were not edited.

## What is ready

- Three blocking manual jobs: `deploy_shop`, `deploy_shop_staging`, `deploy_relay`. They use the existing root include, protected default branch and pinned SDK image.
- Shared Dockerfile and Cloud Build choose the app folder explicitly. Each deployed image is identified by its build digest, and each served commit is checked through `/healthz`.
- Separate shop, staging and relay runtime accounts. Relay has service-scoped traffic roles, actAs on the two shop identities, bucket-scoped state access, four secret grants and project Logging Viewer. CI has no secret-reading grant.
- Five Secret Manager secrets. Two hidden human inputs, two generated keys and a generated ntfy topic. Values are absent from tracked config, receipts, ownership metadata and CI arguments.
- Private state and source buckets, budget alert, initially paused minute Scheduler job, one relay uptime check and email policy, and teardown of owned resources.
- Public setup output replaces `deploy/gcp.env`. The README clones `main` after Claude merges this branch.

## Checks completed

| Command or check | Result |
| --- | --- |
| `uv run pytest -q` | 218 passed in 7.49s; one upstream FastAPI/Starlette deprecation warning |
| `uv run python -m unittest discover -s deploy/tests -v` | 48 discovered, 47 passed, one local gcloud-help skip; 121.106s |
| `python3 deploy/tests/test_cli_flags.py` in the exact pinned SDK Docker image | Four passed; all 60 command paths and 61 distinct flags checked, 31.665s, network disabled |
| `shellcheck -x deploy/*.sh` | Passed, ShellCheck 0.11.0 |
| `bash -n` on every deploy shell file | Passed |
| `python3 -m compileall -q deploy` | Passed |
| YAML parsing and three manual job environment contracts | Passed in the deployment orchestration suite |
| Docker builds for `APP_DIR=shop` and `APP_DIR=relay` | Passed with hash-locked dependencies |
| Three offline container HTTP checks | Production shop, staging shop and relay `/healthz` matched the served commit; shop environment and demo labels correct |
| Paths, whitespace and long-dash check | Passed; changed paths confined to the agreed ownership |

The local gcloud-help skip is covered by the separate real pinned-image audit. Full commands and image hashes are in [CLI_FLAGS.md](../../deploy/CLI_FLAGS.md) and [SERVICES_CONTAINER_CHECK.md](SERVICES_CONTAINER_CHECK.md). Cloud setup tests use explicitly labelled demo responses. The container tests use labelled fixture values and no external API access.

## Day-one checks still needed

No Google or GitLab workspace credentials were available. No resource was created in a live cloud account. Verify the actual OIDC exchange, build permissions, per-service deploy roles, runtime secret injection, relay state generation handling, traffic migration, Scheduler delivery, email delivery and GitLab environment URL updates.

Create and enable the Duo flows, populate their public IDs and account username, redeploy relay and test an authenticated tick before resuming Scheduler. The initial Scheduler pause is deliberate: blank flow config returns health 200 but tick 500. That configuration failure currently occurs before the relay's consecutive-failure counter, so the process uptime check does not catch it. Claude should add an application readiness signal or handle that configuration failure through the existing relay failure path. App changes belong to Claude.

Test Scheduler's forced run while paused. Its API documents immediate dispatch but does not explicitly guarantee paused-job behavior. The README restricts CLI output to the public job name and requires verification of the resulting relay evidence. Keep the job paused on any setup or readiness failure.

Both shops require 512Mi for always allocated CPU. Min instances 0 does not guarantee zero charges, particularly when the relay polls production every minute. The [README cost estimate](../../deploy/README.md#costs-and-free-allowances) and [IAM source review](SERVICES_IAM.md) explain the cost and instance-memory limits. Budget alerts do not cap spending. Run Developer is broader than traffic-only permissions; signed-order enforcement remains the app's action boundary.

## Review and merge

Claude can review and merge the branch after these offline checks. No default-branch merge or deployment was performed by Codex. Follow [deploy/README.md](../../deploy/README.md) for Alex's account setup, hidden secret entry, public config, manual jobs and cleanup. Preserve the ownership journal and back up any desired night state before teardown.
