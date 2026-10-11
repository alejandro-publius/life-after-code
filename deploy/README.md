# Night Orders on Google Cloud

GitLab CI builds and deploys three Cloud Run services. Each deployment needs a human to click Play on the protected default branch. Google authentication uses a short-lived GitLab OIDC token and Workload Identity Federation, with no stored Google key.

| Cloud Run service | App folder | GitLab environment | Runtime settings |
| --- | --- | --- | --- |
| `shop` | `shop` | `production` | `APP_ENV=production`, 1 CPU, 512Mi, always allocated CPU, 30s timeout |
| `shop-staging` | `shop` | `staging` | `APP_ENV=staging`, 1 CPU, 512Mi, always allocated CPU, 30s timeout |
| `relay` | `relay` | `relay` | 1 CPU, 256Mi, request billing, 60s timeout |

All have minimum instances 0 and revision maximum instances 1. The shops need always allocated CPU for their background demo loop. This requires at least 512 MiB and can incur charges while an instance is idle. It is not a promise of free hosting. See [billing settings](https://docs.cloud.google.com/run/docs/configuring/billing-settings) and the cost section below.

The shops contain clearly labelled simulated customers and planted faults. Each has separate memory and a separate runtime account. Relay stores its night state in a private bucket and receives only the permissions listed below. This deployment creates one relay uptime alert and no shop Monitoring alert policy, following [the application decision](../docs/DECISIONS.md).

## Alex's setup steps

Use these steps after Claude merges `codex/deploy-services`. Do not paste a secret into chat, a tracked file or a CI/CD variable. Secret values are entered directly into Cloud Shell's hidden prompts.

1. Join on [Devpost](https://gitlab-transcend.devpost.com/), then complete [GitLab Contributor registration](https://contributors.gitlab.com/transcend-hackathon). Follow the welcome issue in the project GitLab provisions. The [rules](https://gitlab-transcend.devpost.com/rules) require Duo Agent Platform; account onboarding is separate from this Google setup.
2. In that GitLab project, copy the numeric **Project ID** under **Settings > General** and the full `namespace/project` path from its URL. Open `https://gitlab.com/api/v4/projects/PROJECT_ID`, replacing `PROJECT_ID`, and record `namespace.id` and `default_branch`. For a private project use the authenticated UI or API. See [Projects API](https://docs.gitlab.com/api/projects/#get-a-single-project).
3. Check **Settings > Repository > Branch rules**. The default branch must be protected and Alex must be allowed to run its manual deployments. A Developer cannot change branch protection or project CI/CD variables. Ask the organizer or Maintainer to configure branch permissions if needed. This deployment's public committed config avoids requiring CI/CD variables. See [protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/) and [variables](https://docs.gitlab.com/ci/variables/).
4. Open [personal access tokens](https://gitlab.com/-/user_settings/personal_access_tokens), choose **Add new token**, name it `night-orders-relay`, choose a short expiry covering the event, and select the `api` scope. It acts with your GitLab permissions. Keep its value locally for the hidden setup prompt. If a Maintainer can provide a project access token instead, prefer that project boundary. See [personal tokens](https://docs.gitlab.com/user/profile/personal_access_tokens/) and [project tokens](https://docs.gitlab.com/user/project/settings/project_access_tokens/). A Developer may be unable to create a project token.
5. In the project, open **Deploy > Feature flags > Configure**. Copy the **Instance ID** for the other hidden setup prompt. This is a secret that allows retrieving flags, despite its name. The printed API URL should be `https://gitlab.com/api/v4/feature_flags/unleash/PROJECT_ID`. Configure the flags and flows using [Claude's shop guide](../shop/README.md) and [relay guide](../relay/README.md). See [GitLab flag credentials](https://docs.gitlab.com/operations/feature_flags/#get-access-credentials).
6. Open [Google Cloud Free Program](https://cloud.google.com/free). If eligible, start the free trial and complete account and payment verification. An unupgraded trial is not charged, but resources stop when its credit or 90 days expire. A paid account can incur overages. See [trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features).
7. Open [Create a project](https://console.cloud.google.com/projectcreate). Create a separate project for Night Orders, copy its **Project ID**, then link its billing account under [Billing: My Projects](https://console.cloud.google.com/billing/projects). Do not use a shared project. Alex needs project Owner access and permission to create billing-account budgets, such as Billing Account Administrator or Billing Account Costs Manager. Project ownership alone does not grant the latter. See [budget permissions](https://cloud.google.com/billing/docs/how-to/budgets).
8. Open [Cloud Shell](https://shell.cloud.google.com/), authorize it, replace the four `REPLACE_` values below, and paste. Use the actual default branch if it differs from `main`. Setup asks for the GitLab token, Unleash Instance ID and alert email without echoing them. On a rerun it preserves existing secret versions and does not ask for their values again.

```bash
git clone --branch main https://github.com/alejandro-publius/life-after-code.git life-after-code-deploy
cd life-after-code-deploy
export GCP_PROJECT_ID='REPLACE_GOOGLE_PROJECT_ID'
export GITLAB_PROJECT_ID='REPLACE_NUMERIC_GITLAB_PROJECT_ID'
export GITLAB_PROJECT_PATH='REPLACE_NAMESPACE/PROJECT'
export GITLAB_NAMESPACE_ID='REPLACE_NUMERIC_NAMESPACE_ID'
export GITLAB_DEFAULT_BRANCH='main'
export GCP_REGION='us-central1'
export GCP_DEDICATED_PROJECT='true'
bash deploy/setup_gcp.sh
```

Cloud Shell needs gcloud's alpha and beta commands for project labels and service identity creation. The pinned CI image includes both; [CLI_FLAGS.md](CLI_FLAGS.md) records actual help checks.

Setup creates five accounts, three public seed services, five Secret Manager secrets, Artifact Registry, private source and state buckets, restricted WIF, Scheduler and relay Monitoring resources. The initial services use Google's hello image, so they are not yet Night Orders. It also creates a project-filtered USD 5 monthly budget alert at 50%, 90% and 100%. Confirm billing recipients under [Budgets & alerts](https://console.cloud.google.com/billing) and the relay email channel under [Monitoring > Alerting](https://console.cloud.google.com/monitoring/alerting).

9. Preserve the gitignored `deploy/.life-after-code-bootstrap.json`. It contains ownership and resource IDs, not secret values or the alert email. A private copy lives in `gs://SOURCE_BUCKET/bootstrap/state.json`. Setup restores that copy if needed, and refuses conflicting or unknown resources. Use the same project, region, GitLab namespace and default branch on reruns. Do not edit the journal to bypass ownership checks.
10. In GitLab's **Code > Repository**, open `deploy/gcp.env`, select **Edit > Edit single file**, and paste the entire final public `NAME=value` block from setup. Commit it or propose an MR as branch permissions require. Leave the four flow and watch fields blank until the day-one flow test. CI variables with the same names override the file, including explicitly empty values. See [Web Editor](https://docs.gitlab.com/user/project/repository/web_editor/).
11. The root pipeline already includes `deploy/gitlab-ci-deploy.yml` and has a `deploy` stage. Keep application checks ahead of deployment. Run the protected default-branch pipeline under **Build > Pipelines**. Click Play for `deploy_shop_staging`, then `deploy_shop`, then `deploy_relay`, confirming success after each. These are separate blocking manual jobs; each updates only its named service. Open **Operate > Environments** and the `staging`, `production` and `relay` URLs. Every job checks the exact `/healthz` commit and saves `deploy/result.json` with its service, URL, commit, image digest and build ID. See [environments](https://docs.gitlab.com/ci/environments/).
12. Complete Claude's day-one flow test. Put the actual `FLOW_CONSUMER_ID`, `FLOW_SERVICE_ACCOUNT`, `DAWN_FLOW_CONSUMER_ID` and `WATCH_ISSUE_IID` in `deploy/gcp.env`, then redeploy relay. The username must identify the watch flow's service account, not Alex. A blank flow config passes `/healthz` but fails `/tick`; a health check alone cannot certify readiness.
13. Scheduler is initially paused. In Cloud Shell, request one immediate dispatch with the command below. Output is restricted to the public job name so it does not expose the shared-key header. A successful command does not prove that relay accepted or completed the tick. Check relay's public status page, the watch issue and the resulting state with Claude before resuming. Running a paused job is a live verification item; if Google rejects it, leave it paused and have Claude verify an authenticated `/tick` privately.

```bash
export CLOUDSDK_CORE_LOG_HTTP=false
gcloud scheduler jobs run relay-tick --project="$GCP_PROJECT_ID" \
  --location="$GCP_REGION" --quiet --format='value(name)'
```

After the tick works with real flow settings and the signed-order controls are checked:

```bash
gcloud scheduler jobs resume relay-tick --project="$GCP_PROJECT_ID" \
  --location="$GCP_REGION" --quiet
```

See [force a Scheduler run](https://cloud.google.com/scheduler/docs/reference/rest/v1/projects.locations.jobs/run) and [CLI output projections](https://cloud.google.com/sdk/gcloud/reference/topic/formats).

## Public config and private values

`deploy/gcp.env` is a strict data file. The parser accepts known keys with plain identifier characters, rejects duplicates and secret keys, and never evaluates shell code. Setup prints the complete public file contents. Its key groups are:

| Group | Public keys |
| --- | --- |
| Google identity | `GCP_PROJECT_ID`, `GCP_PROJECT_NUMBER`, `GCP_REGION`, `GCP_WIF_POOL`, `GCP_WIF_PROVIDER` |
| Build and deploy | `GCP_SERVICE_ACCOUNT`, `GCP_BUILD_SERVICE_ACCOUNT`, `GCP_ARTIFACT_REPOSITORY`, `GCP_SOURCE_BUCKET` |
| Services | `GCP_SHOP_SERVICE`, `GCP_STAGING_SERVICE`, `GCP_RELAY_SERVICE`, and their three `GCP_*_SERVICE_ACCOUNT` emails |
| URLs | `SHOP_URL`, `SHOP_STAGING_URL`, `RELAY_URL`, `SHOP_METRICS_URL`, `UNLEASH_URL` |
| GitLab | `GITLAB_URL=https://gitlab.com`, `GITLAB_PROJECT_ID`, `GITLAB_PROJECT_PATH` |
| Relay state | `STATE_BUCKET=PROJECT-night-orders-state`, `STATE_OBJECT=night-orders/state.json` |
| Day-one flows | `FLOW_CONSUMER_ID`, `FLOW_SERVICE_ACCOUNT`, `DAWN_FLOW_CONSUMER_ID`, `WATCH_ISSUE_IID` |

Each deployment writes only its relevant public settings into a temporary env file. Shops receive `APP_ENV=production` or `staging`, `UNLEASH_URL` and the served commit. Relay receives its GitLab, flow, metrics and state settings. Secrets are separate `--set-secrets` references:

| Secret Manager secret | Created how | Runtime recipients |
| --- | --- | --- |
| `gitlab-token` | Alex's hidden prompt | Relay: `GITLAB_TOKEN` |
| `unleash-instance-id` | Alex's hidden prompt | Both shops: `UNLEASH_INSTANCE_ID` |
| `relay-key` | Cryptographically random, once | Relay: `RELAY_KEY`; Scheduler header |
| `demo-key` | Cryptographically random, once | All three: `DEMO_KEY` |
| `ntfy-url` | `https://ntfy.sh/` plus a random topic, once | Relay: `NTFY_URL` |

Secret versions are never printed by setup and are injected into Cloud Run by Secret Manager. The alert email stays in Google's notification channel, not the repo or ownership journal. For Alex's phone subscription, open [Secret Manager](https://console.cloud.google.com/security/secret-manager), select `ntfy-url`, and privately view the enabled version. Use that topic in the ntfy app; do not include it in a public screenshot or demo. The topic's secrecy is its access boundary in the current relay design.

Scheduler sends `POST RELAY_URL/tick` every minute in UTC, with `X-Relay-Key`, zero retries and a 60s deadline. Setup reads the key privately and copies its value into the Scheduler request. Scheduler does not dynamically resolve a Secret Manager reference, so rerun setup after an explicit key rotation. Treat the job's stored header as a secret: do not dump full Scheduler job JSON into logs. Reruns preserve an existing job's paused or active state. See [Scheduler jobs API](https://cloud.google.com/scheduler/docs/reference/rest/v1/projects.locations.jobs).

The uptime check hits relay `/healthz` every minute from three US checker locations. Its email policy reports a sustained failure for two minutes. Confirm email delivery on the live project. It checks process reachability, not GitLab access, flow readiness or signed-order validity. A separate shop policy is intentionally absent.

## Permissions

| Identity | Access |
| --- | --- |
| GitLab federated principal | Impersonates only the deploy account after exact project path, project ID, namespace ID, protected default branch and branch-type checks |
| CI deploy account | Cloud Build Editor and Service Usage Consumer on this dedicated project; Run Developer on the three existing services; Artifact Registry Reader on this repo; Object User and bucket metadata Reader on the source bucket; actAs on build and the three runtime accounts |
| Build account | Artifact Registry Writer on this repo, Object Viewer on the source bucket, project Logging Writer |
| Shop and staging accounts | Secret Accessor on `unleash-instance-id` and `demo-key` only |
| Relay account | Run Developer on shop and shop-staging only; actAs on those two runtime accounts only; Object User on the state bucket only; Secret Accessor on its four secrets only; project Logging Viewer |

CI receives no Secret Accessor role. It cannot change service IAM or budgets. Relay receives no role on its own Cloud Run service, CI account or build account. Run Developer includes permissions beyond changing traffic; the app's signed orders narrow the permitted actions. Logging Viewer is project-wide, which is why this must be a dedicated project.

Google's [traffic migration guide](https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration) lists Service Account User, which supplies `iam.serviceAccounts.actAs`. We grant that role only on the two shop runtime identities. Whether the exact traffic-only v2 PATCH can work without it remains unverified; this follows the documented requirement. No relay Artifact Registry permission is added for moving traffic to existing revisions. If that live operation fails, inspect the denied permission before changing a role. See [SERVICES_IAM.md](../docs/codex/SERVICES_IAM.md), [runtime secret permissions](https://docs.cloud.google.com/run/docs/configuring/services/secrets), [Logging access](https://docs.cloud.google.com/logging/docs/access-control) and [state preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions).

## Build and deployment details

`deploy/Dockerfile` defaults to `ARG APP_DIR=shop`. Cloud Build explicitly chooses `APP_DIR=shop` or `APP_DIR=relay` for each job; no Dockerfile swap is needed. Both folders contain their own hash-locked requirements and packaged app files. The Python base and SDK image are digest pinned. The app uses one worker, UID/GID 10001, `$PORT`, and `/healthz` returning `{"ok": true, "commit": "SHORT_SHA"}`. Cloud Build runs Docker remotely, so the GitLab runner needs no Docker daemon or privileged mode.

Deployments use the immutable build digest. They deliberately move traffic entirely to the latest revision after a human clicks Play; those deploy jobs do not enforce Night Orders' signed traffic policy. Keep them unused during a signed night watch. The relay uses the policy for its own traffic actions. A failed post-deploy health check fails the job, but does not roll back automatically.

The selected WIF route is available on GitLab.com Free: [GitLab's cloud-services guide](https://docs.gitlab.com/ci/cloud_services/google_cloud/), [ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/) and [Google's deployment-pipeline guide](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines). GitLab's [Google IAM integration](https://docs.gitlab.com/integration/google_cloud_iam/) and [Cloud Run component tutorial](https://docs.gitlab.com/tutorials/create_and_deploy_web_service_with_google_cloud_run_component/) use a namespace-specific `auth.gcp.gitlab.com` issuer. This task requires `gitlab.com` OIDC, so it keeps the plain WIF flow. Its issuer is exactly `https://gitlab.com`, matching the [live discovery document](https://gitlab.com/.well-known/openid-configuration), despite the trailing slash shown in GitLab's tutorial. The job and provider allowed audience are both `https://gitlab.com`.

If WIF fails, compare project path, IDs, default branch and protection to the setup inputs. A namespace or default branch change needs an explicit trust update, not a broader condition. Organization policies may prohibit public Cloud Run services or WIF. On a first IAM propagation failure, inspect the error and retry once after propagation. Do not grant Owner to CI.

## Costs and free allowances

Checked 2026-10-06. Allowances are usually shared across a billing account. See [Free Program](https://cloud.google.com/free) and [detailed limits](https://docs.cloud.google.com/free/docs/free-cloud-features).

| Product | Applicable monthly allowance |
| --- | --- |
| Shop instance billing | 240,000 vCPU-seconds and 450,000 GiB-seconds, valued at us-central1 rates. [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Relay request billing | 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests. [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Cloud Build | 2,500 promotional `e2-standard-2` build minutes; this skeleton selects that machine type. [Build pricing](https://cloud.google.com/build/pricing) |
| Artifact Registry | First 0.5 GiB-month storage free; repeated images accumulate storage. [Registry pricing](https://cloud.google.com/artifact-registry/pricing) |
| Two Storage buckets | Shared 5 GB-months regional storage, 5,000 Class A and 50,000 Class B operations in eligible US regions including us-central1. [Storage pricing](https://cloud.google.com/storage/pricing) |
| Secret Manager | Six active versions and 10,000 accesses per billing account. We create five single-version secrets. Disabled versions still count; rotations can exceed the allowance. [Secret pricing](https://cloud.google.com/secret-manager/pricing) |
| Scheduler | Three jobs per billing account. Paused jobs still count. This setup creates one. [Scheduler pricing](https://cloud.google.com/scheduler/pricing) |
| Monitoring | First 1 million regional uptime executions per project. Three minute-by-minute US checks use 133,920 in 31 days. Uptime metric alert policies are exempt from listed policy charges. [Observability pricing](https://cloud.google.com/products/observability/pricing) |
| Logs | First 50 GiB ingestion per project; extra volume and extended retention can be billed. [Observability pricing](https://cloud.google.com/products/observability/pricing) |

At us-central1 prices, one running 1 CPU, 512 MiB shop costs about USD 0.0684 per hour before the instance allowance. Two continuously running for 30 days cost about USD 93.28 after a completely unused instance allowance, excluding all other products. Min instances 0 does not prevent the relay's minute-by-minute production metrics requests from keeping a shop active. Staging can stop when idle. Source archives expire after one day; the bootstrap journal and actual night state remain until teardown. These estimates use [Cloud Run pricing](https://cloud.google.com/run/pricing).

The Free Program marketing page's 120 Cloud Build minutes per day differs from the product page's 2,500 minutes monthly. Use the [product-specific pricing](https://cloud.google.com/build/pricing). Uptime alert policy billing is currently listed as starting no sooner than September 1, 2027, with uptime metrics exempt; recheck [the policy terms](https://cloud.google.com/products/observability/pricing) before submission.

`--max-instances=1` is a per-revision bound, so two revisions can overlap; limits can also be exceeded briefly. Shop metrics are in memory and reset on restart or traffic movement. Always allocated CPU does not make that memory durable or prevent an idle instance from stopping. See [maximum instances](https://docs.cloud.google.com/run/docs/configuring/max-instances) and [CPU allocation](https://docs.cloud.google.com/run/docs/configuring/billing-settings).

## No surprise charges

Budget alerts **do not cap spending**. The USD 5 alert only sends notifications, and usage reporting can lag. See [Google's budget warning](https://cloud.google.com/billing/docs/how-to/budgets). Always allocated shop CPU, public requests, builds, storage, network transfer and model calls can cost money. Google free allowances do not cover GitLab Duo or external model API charges.

Between live demonstrations, pause the scheduled watch after ending its signed orders:

```bash
gcloud scheduler jobs pause relay-tick --project="$GCP_PROJECT_ID" \
  --location="$GCP_REGION" --quiet
```

This stops future scheduled ticks. It does not stop outstanding work, direct requests, uptime checks or storage charges. Do not leave a signed night watch dependent on a paused relay. Inspect [Billing reports](https://console.cloud.google.com/billing) and remove unused images under [Artifact Registry](https://console.cloud.google.com/artifacts).

To remove the owned deployment, keep the same Cloud Shell checkout and original project inputs. Back up any night state you intend to keep, since teardown deletes it:

```bash
bash deploy/teardown_gcp.sh --confirm-project "$GCP_PROJECT_ID"
```

Teardown removes Scheduler, uptime check, email policy and channel, cancels builds under the owned builder, deletes three services, five secrets, images/repository, both buckets, budget, WIF resources and five accounts. It removes its project role bindings and disables only APIs it first enabled. Bucket soft delete is disabled for these disposable owned buckets. Ownership or permission failure stops teardown; do not treat that as complete cleanup. Google-managed service agents and historical build or log records can remain, and WIF resources use recoverable deletion. See [service agents](https://docs.cloud.google.com/iam/docs/service-agents) and [pool deletion](https://docs.cloud.google.com/iam/docs/manage-workload-identity-pools-providers#delete-pool).

For a complete stop on this dedicated project, open [Billing: My Projects](https://console.cloud.google.com/billing/projects), find its exact project ID, open the three-dot Actions menu, choose **Disable billing**, and confirm. Services stop, data can be lost, and already accrued charges can arrive later. External API charges and other projects are unaffected. See [disable billing](https://docs.cloud.google.com/billing/docs/how-to/modify-project). Alternatively, back up needed data and shut down the dedicated project under [IAM & Admin > Settings](https://console.cloud.google.com/iam-admin/settings). Never shut down a shared project.

## Verification and limits

The service builds and localhost HTTP checks passed in Docker. Setup and teardown tests use explicitly labelled demo Google responses; they do not authenticate to Google. The CLI audit uses the exact pinned SDK image, with no network or credentials. Commands are listed in [CLI_FLAGS.md](CLI_FLAGS.md), and container results in [SERVICES_CONTAINER_CHECK.md](../docs/codex/SERVICES_CONTAINER_CHECK.md).

```bash
python3 -m unittest discover -s deploy/tests -v
shellcheck -x deploy/*.sh
```

Live WIF exchange, narrow IAM roles, Secret Manager injection, Cloud Build, traffic movement, state persistence, scheduled ticks, alert email and GitLab environment URL updates are unverified. Alex's Google and GitLab projects are needed. The day-one test must exercise these before a real signed watch or video recording. The tests do not prove that the system is live.
