# Deploy the FastAPI app to Google Cloud

This folder is a concept-independent placeholder. A human starts one manual GitLab job on the protected default branch. That job exchanges a short-lived GitLab ID token for a Google identity, builds with Cloud Build, deploys the image by digest to Cloud Run, and checks the served commit. No Google service account key is created or stored.

The default GitLab environment is `staging`. This is one public service, not separate staging and production services. Claude owns the real app, its safety gates and the root pipeline. Local checks are recorded in [DEPLOY_CHECK.md](../docs/codex/DEPLOY_CHECK.md). A successful local build is not evidence of a live Google deployment.

## Why this authentication route

[GitLab's native Google IAM integration](https://docs.gitlab.com/integration/google_cloud_iam/) is available on GitLab.com Free. It uses `identity: google_cloud` and a namespace-specific issuer under `https://auth.gcp.gitlab.com/oidc/`. The [Cloud Run component tutorial](https://docs.gitlab.com/tutorials/create_and_deploy_web_service_with_google_cloud_run_component/) follows that route and uses a privileged Docker runner.

The requested skeleton explicitly requires `id_tokens` issued by `gitlab.com`. We therefore use GitLab's other documented [Google Workload Identity Federation flow](https://docs.gitlab.com/ci/cloud_services/google_cloud/) with [ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/) and Google's [deployment-pipeline guide](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines). Cloud Build runs Docker remotely, so the GitLab runner needs no Docker daemon or privileged mode.

The issuer is exactly `https://gitlab.com`, matching GitLab's live [OIDC discovery document](https://gitlab.com/.well-known/openid-configuration) and Google's example. GitLab's cloud-services tutorial shows a trailing slash; the live issuer takes precedence. Both the job audience and the provider's allowed audience are `https://gitlab.com`. This custom allowed audience is intentional, not a service account key.

## Alex's steps

1. Open [Devpost](https://gitlab-transcend.devpost.com/) and click **Join Hackathon**. Open [GitLab Contributor registration](https://contributors.gitlab.com/transcend-hackathon), complete registration, and follow the welcome onboarding issue in the provisioned GitLab project. The [rules](https://gitlab-transcend.devpost.com/rules) require Duo Agent Platform and describe approval taking about 24 business hours. Use that project's actual namespace, not a guessed personal path.
2. Open that project's **Settings > General**. Copy its numeric project ID. Copy its full `namespace/project` path from its URL. With the project visible, open `https://gitlab.com/api/v4/projects/PROJECT_ID` in the browser, replacing `PROJECT_ID`, and record `namespace.id` and `default_branch`. This endpoint is documented in the [Projects API](https://docs.gitlab.com/api/projects/#get-a-single-project). For a private project, get these details through the authenticated GitLab UI or an authenticated API request without pasting a token into this repository.
3. In the project, open **Settings > Repository > Branch rules**. Add or edit the default branch rule and protect it. Permit Alex to merge and run its manual deployment. The WIF provider also rejects unprotected branches, other branches, other project paths, other numeric project IDs, and other namespace IDs. See [protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/).
4. Open [Google Cloud Free Program](https://cloud.google.com/free). If eligible, start the free trial and complete Google's account and payment verification. An unupgraded trial is not billed, but its resources stop when the credit or 90 days run out. A paid account bills usage beyond credits and allowances. See [trial terms and limits](https://docs.cloud.google.com/free/docs/free-cloud-features). Do not upgrade just to run this setup unless you accept paid overages.
5. Open [Create a project](https://console.cloud.google.com/projectcreate). Create a new, separate project for this entry. Copy the **Project ID**, not its display name. Open [Billing: My Projects](https://console.cloud.google.com/billing/projects), find that exact project, and link it to your billing account. Do not use a project containing another app or production data. Alex needs project Owner access and Billing Account Administrator or Billing Account Costs Manager access on the billing account to create the budget. Project ownership alone is insufficient for billing-account budgets. See [budget permissions](https://cloud.google.com/billing/docs/how-to/budgets).
6. Open [Cloud Shell](https://shell.cloud.google.com/), authorize it for your own Google account, and paste the following. Replace the four `REPLACE_` values with the IDs from steps 2 and 5. Set the default branch to its actual name if it differs from `main`.

```bash
git clone --branch codex/deploy-skeleton https://github.com/alejandro-publius/life-after-code.git life-after-code-deploy
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

The setup enables the required APIs, creates three service accounts, an Artifact Registry repository, a private source bucket and a restricted WIF provider. It creates a public Cloud Run service using Google's hello image, then grants CI permission to update only that existing service. It creates a project-filtered USD 5 monthly alert at 50%, 90% and 100%. Setup prints identifiers, not credentials. Verify **Billing > Budgets & alerts** and confirm billing notification emails reach Alex. The initial Google hello image is only bootstrap, not our FastAPI app.

7. Keep `deploy/.life-after-code-bootstrap.json`. It records resource ownership, enabled APIs and the budget ID. It is gitignored and backed up privately in `gs://SOURCE_BUCKET/bootstrap/state.json`. Rerunning setup with the same inputs updates existing owned resources. A resource with conflicting ownership stops setup. If an interrupted creation leaves an unmarked resource, inspect it before removing that resource and rerunning; setup never adopts it silently. Do not edit the ownership file to bypass these checks.
8. In GitLab, open **Settings > CI/CD > Variables > Add variable**. Add each exact `NAME=value` pair printed by setup as a **Variable**, with **Protect variable** enabled, expansion disabled, and the environment scope set to `staging` or `*`. These are nonsecret identifiers and may remain visible. There is no `GOOGLE_APPLICATION_CREDENTIALS` secret and no stored OIDC token. The job receives its token at runtime. See [CI/CD variables](https://docs.gitlab.com/ci/variables/).
9. Claude reviews this branch and adds the include below to the root pipeline, with `deploy` in its existing stages. Keep app tests and security gates ahead of deployment. Claude also ensures the submitted GitLab repository is public and MIT licensed. Do not create or replace the root pipeline from this folder.

```yaml
include:
  - local: deploy/gitlab-ci-deploy.yml
# Add deploy to the root pipeline's existing stages list.
```

10. In the GitLab project, open **Build > Pipelines**, run the default-branch pipeline, and wait for preceding checks to pass. Click the manual **Play** button on `deploy_cloud_run`. The job builds once, deploys the immutable image and checks `/healthz`. Open **Operate > Environments > staging**, then its URL. The job also saves `deploy/result.json` containing the URL, full commit, image digest and Cloud Build ID. See [environments](https://docs.gitlab.com/ci/environments/) and [dynamic environment URLs](https://docs.gitlab.com/ci/variables/dotenv_variables/). Live URL assignment is still to be verified with Alex's account.

If the job is absent, check that the branch is the protected default branch. If WIF rejects the token, check the project path, project ID, namespace ID and default branch against the setup inputs. If Google IAM propagation causes the first attempt to fail, wait briefly and manually retry once after checking the error. Do not broaden the condition or grant Owner to CI.

## CI/CD variables

Setup prints all required names. The example values below are labels, not real account data.

| Name | Meaning |
| --- | --- |
| `GCP_PROJECT_ID` | Dedicated Google project ID |
| `GCP_PROJECT_NUMBER` | Numeric Google project number |
| `GCP_REGION` | Defaults to `us-central1` |
| `GCP_WIF_POOL` | `lac-GITLAB_ID-pool` |
| `GCP_WIF_PROVIDER` | `gitlab` |
| `GCP_SERVICE_ACCOUNT` | CI deploy identity email |
| `GCP_BUILD_SERVICE_ACCOUNT` | Cloud Build identity email |
| `GCP_RUNTIME_SERVICE_ACCOUNT` | Cloud Run runtime identity email |
| `GCP_ARTIFACT_REPOSITORY` | Owned Docker repository name |
| `GCP_SOURCE_BUCKET` | Owned private source bucket name |
| `GCP_RUN_SERVICE` | Existing owned Cloud Run service name |
| `GITLAB_PROJECT_ID` | Exact numeric GitLab project ID |
| `GITLAB_PROJECT_PATH` | Exact full GitLab project path |

The job supplies `GCP_ENVIRONMENT=staging` itself. Changing its label does not create another Cloud Run service. Set up a separate service and trust configuration before treating another environment as separate production.

## Change the placeholder to Claude's app

Change exactly this line in `deploy/Dockerfile`:

```dockerfile
ARG APP_DIR=deploy/hello
```

Set it to the real app folder. That folder must contain `main.py` exposing a FastAPI object named `app`, and a fully hash-locked `requirements.txt` accepted by `pip install --require-hashes`. It must implement the same public `/healthz` contract, using the `CI_COMMIT_SHORT_SHA` environment variable. This is the one-line swap contract, not a claim that arbitrary package layouts need no adaptation. The Docker build context is the repository root. Python is pinned to a Linux AMD64 3.12 image digest; dependencies are hash locked. The base-image pin needs deliberate updates when security fixes ship.

The app listens on `$PORT`, runs as UID/GID 10001, and uses one worker. Cloud Run's filesystem is temporary. Persistent data, database backups, application secrets, canary promotion and rollback policy belong to the real app design and are not included in this placeholder. The included health check has a 20 second timeout. A health failure fails the job after deployment; it does not automatically roll back.

## Permissions

| Identity | Access |
| --- | --- |
| GitLab federated principal | Impersonates only the deploy service account, after the exact project and protected-branch condition passes |
| Deploy service account | Cloud Build Editor and Service Usage Consumer on this project; Run Developer on the one existing service; Artifact Registry Reader on the one repository; Object User and bucket metadata Reader on the source bucket; `actAs` on only build and runtime accounts |
| Build service account | Artifact Registry Writer on the repository; Object Viewer on the source bucket; Logging Writer on the project |
| Runtime service account | No project roles for this placeholder |

Google service agents retain their product-managed roles. CI does not create services, change Cloud Run IAM or administer billing. The human bootstrap creates public access using `--no-invoker-iam-check`. Organization policies may prohibit public services or WIF creation; that is a setup blocker rather than a reason to weaken them. See [Cloud Run access control](https://cloud.google.com/run/docs/securing/managing-access), [deployment permissions](https://cloud.google.com/run/docs/deploying), [Cloud Build permissions](https://cloud.google.com/build/docs/iam-roles-permissions), and [custom build accounts](https://cloud.google.com/build/docs/securing-builds/configure-user-specified-service-accounts).

## Costs and free allowances

Checked on 2026-10-06. Google requires an active billing account. Allowances do not guarantee a zero bill and are generally shared across a billing account's projects. Compare the [Free Program overview](https://cloud.google.com/free) with the [detailed limits](https://docs.cloud.google.com/free/docs/free-cloud-features) and product pricing before enabling paid billing.

| Used service | Relevant allowance or charge |
| --- | --- |
| Cloud Run, request-based billing | Monthly 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests. Free allowance uses `us-central1` prices. 1 GB outbound from North America monthly. See [Cloud Run pricing](https://cloud.google.com/run/pricing). |
| Cloud Build default pool | 2,500 promotional free build minutes monthly for `e2-standard-2`; USD 0.006 per minute beyond this in `us-central1`. We select `E2_STANDARD_2` explicitly. See [Cloud Build pricing](https://cloud.google.com/build/pricing). |
| Artifact Registry | First 0.5 GiB-month storage free per billing account; extra storage is billed. Same-region transfers to Cloud Run are free. Repeated image builds accumulate storage. See [Artifact Registry pricing](https://cloud.google.com/artifact-registry/pricing). |
| Cloud Storage source bucket | Monthly 5 GB-months regional storage, 5,000 Class A operations and 50,000 Class B operations in eligible US regions. Default `us-central1` qualifies. Source archives expire after one day; the tiny ownership backup remains. See [detailed free limits](https://docs.cloud.google.com/free/docs/free-cloud-features) and [Storage pricing](https://cloud.google.com/storage/pricing). |
| Build and service logs | First 50 GiB of log ingestion per project monthly; default retention has no extra retention charge. See [detailed free limits](https://docs.cloud.google.com/free/docs/free-cloud-features). |

Source conflict: the Free Program marketing page advertises 120 Cloud Build minutes per day; the product pricing page and detailed free limits state 2,500 `e2-standard-2` minutes per month. This skeleton follows the product-specific terms. Recheck before submission.

Cloud Run uses request billing, min instances 0, service max instances 1, revision max instances 1, 1 CPU, 256 MiB, concurrency 20 and a 30 second request timeout. CPU is throttled outside requests and startup CPU boost is disabled. Build time is bounded at 10 minutes and the manual CI job at 20 minutes. These reduce costs but do not cap them. Cloud Run may temporarily exceed an instance limit during some operations; see [maximum instances](https://cloud.google.com/run/docs/configuring/max-instances).

## No surprise charges

Budget alerts **do not cap spending**. The USD 5 alert is a notification, not an automatic shutoff. Usage reporting and emails can lag. Requests, builds, image storage and network traffic can cost money even with one Cloud Run instance. See [Google's budget warning](https://cloud.google.com/billing/docs/how-to/budgets).

Keep the service small, deploy manually, inspect [Billing reports](https://console.cloud.google.com/billing), and delete unused images through [Artifact Registry](https://console.cloud.google.com/artifacts). The script does not enable paid container scanning. It does not create a database, GPU, load balancer, VPC connector or minimum warm instance. Anthropic or other external API charges are separate from Google Cloud and are outside this folder.

To remove everything this setup owns, use the same Cloud Shell checkout and original project inputs:

```bash
bash deploy/teardown_gcp.sh --confirm-project "$GCP_PROJECT_ID"
```

Teardown requires saved ownership metadata and an exact project confirmation. It cancels active builds using the owned build identity, deletes the owned service, images/repository, source bucket, budget, WIF resources and three accounts, removes its project role bindings, and disables only APIs it first enabled. It keeps the parent project and billing link. Bucket soft delete is disabled for these disposable source archives so deletion does not intentionally retain billable copies. If a permission or ownership check fails, teardown stops and reports it. Never treat a stopped teardown as a complete cleanup.

Google-managed service agents and historical build or log records can remain in the parent project. WIF deletion uses Google's recoverable deletion rather than immediate permanent removal. Setup can restore its own soft-deleted pool and provider. For complete project removal, use the dedicated project's shutdown control. See [service agents](https://cloud.google.com/iam/docs/service-agents) and [delete a workload identity pool](https://cloud.google.com/iam/docs/manage-workload-identity-pools-providers#delete-pool).

For a complete stop on this dedicated project, open [Billing: My Projects](https://console.cloud.google.com/billing/projects), find the exact project, open its three-dot Actions menu, choose **Disable billing**, and confirm. This stops Google Cloud services and new billing for that project, but data can be lost and outstanding usage charges still arrive. It does not stop unrelated projects or external model API charges. See [disable billing](https://docs.cloud.google.com/billing/docs/how-to/modify-project). Alternatively, shut down the dedicated project under [IAM & Admin > Settings](https://console.cloud.google.com/iam-admin/settings) after checking the selected project and backing up any real data. Never delete a shared project.

## Official references used

In addition to the linked sources above:

- [Generate a short-lived external-account credential configuration](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/create-cred-config).
- [Submit a build, choose its service account and source bucket](https://cloud.google.com/sdk/gcloud/reference/builds/submit).
- [Deploy and set Cloud Run resource limits](https://cloud.google.com/sdk/gcloud/reference/run/deploy).
- [Create a project-filtered budget and thresholds](https://cloud.google.com/sdk/gcloud/reference/billing/budgets/create).
- [Create a private bucket and disable source soft delete](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/create).
- [Create Google-managed service identities](https://cloud.google.com/sdk/gcloud/reference/beta/services/identity/create).
- [GitLab dotenv report artifacts](https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsdotenv).

No live account setup, OIDC exchange, remote build, budget email, GitLab environment URL or cloud teardown has been tested yet. Alex's account and GitLab project are needed for those checks.

The ownership and cleanup tests use clearly labelled demo cloud responses and never contact Google:

```bash
python3 -m unittest discover -s deploy/tests -v
shellcheck -x deploy/*.sh
```
