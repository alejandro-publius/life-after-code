# Google Cloud CLI flag check

Recorded: 2026-10-06T04:46:25Z. Final three-service result: four tests passed. All 60 distinct command help calls succeeded and all 61 distinct used flags matched the actual SDK 587 help. Test run: 31.665 seconds, exit code 0. The earlier single-service check passed on 2026-10-06T02:20:37Z: 50 command paths, 57 distinct flags.

The CI image is pinned to the actual image inspected during this check:

```text
gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:be4876b4311056bf3ce236a14a7dea1288e70b7cfea2454ea15e4165c819921f
Google Cloud SDK 587.0.0
alpha 2026.09.25
beta 2026.09.25
```

The pulled platform was `linux/amd64`. The floating `:slim` tag resolved to this digest on the check date. The image includes the alpha and beta command components. Sources: [official CLI container documentation](https://cloud.google.com/sdk/docs/downloads-docker) and the local image's `gcloud version` output.

## Changes found by actual command help

1. Google's [official SDK 530.0.0 archive](https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-530.0.0-linux-x86_64.tar.gz) was downloaded and inspected locally. Its `gcloud run deploy --help` supports `--min`, `--max-instances`, `--no-invoker-iam-check`, and `--no-cpu-boost`. It does not support `--max`. Both setup and CI now omit `--max=1` and keep `--max-instances=1`, as requested. SDK 587 supports `--max`, but the scripts still omit it.
2. SDK 587's stable `gcloud projects update --help` does not support `--update-labels` or `--remove-labels`. Its `gcloud alpha projects update --help` supports both. SDK 530 was checked after installing its official alpha component and supports both alpha flags too. Setup and teardown now use the alpha command for their project ownership label. Sources: local help and [alpha projects update](https://cloud.google.com/sdk/gcloud/reference/alpha/projects/update).
3. `--max-instances=1` limits instances for a revision. It does not impose one shared service cap across overlapping revisions. Sources: local `gcloud run deploy --help` and [Cloud Run maximum instances](https://cloud.google.com/run/docs/configuring/max-instances).

`530.0.0-slim` returned `manifest unknown` from the current image registry. No SDK 530 Docker image was used. The archive check is separate from the SDK 587 job-image check.

## Reproduce the actual image check

Run from the repository root with a working Docker daemon:

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock run --rm --network=none \
  -e PYTHONDONTWRITEBYTECODE=1 \
  --mount type=bind,src="$PWD",dst=/repo,readonly \
  --workdir=/repo \
  gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:be4876b4311056bf3ce236a14a7dea1288e70b7cfea2454ea15e4165c819921f \
  python3 deploy/tests/test_cli_flags.py
```

The test scans `ci_deploy.sh`, `setup_gcp.sh`, `teardown_gcp.sh`, `lib.sh`, `bootstrap_secrets.sh`, and `bootstrap_ops.sh`. It also parses `monitoring.py` with Python's AST to find `gcloud` subprocess argument lists and joined flag values. Literal flags assigned to the constrained `cpu_flag` variable and `settings` array are included, including assignments in case branches. Alex's manual `scheduler jobs pause` and `scheduler jobs resume` commands are included with `--project`, `--location`, and `--quiet`. The day-one `scheduler jobs run` command is also included with those flags and `--format='value(name)'`, so its printed result is limited to the resource name.

Each distinct command runs with `--help`. Every used flag must appear in actual help, including `--[no-]` boolean variants. Unknown command paths or flag-carrying shell variables fail the test. Regression checks cover hidden array flags, Python arguments and rejection of unknown commands. Docker's network is disabled and no credentials are mounted. This checks command availability and flag names. It does not prove parameter values, IAM permissions, authentication, API operations, REST request schemas, or a live deployment. Scheduler and Monitoring setup use their REST APIs; those request bodies require their separate tests.

## Command and flag inventory

Each row is checked with `gcloud <command> --help`. SDK reference links help locate the same command online; local command help is the evidence for this audit.

| Command | Used flags |
| --- | --- |
| [`alpha projects update`](https://cloud.google.com/sdk/gcloud/reference/alpha/projects/update) | `--quiet`, `--remove-labels`, `--update-labels` |
| [`artifacts repositories add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/artifacts/repositories/add-iam-policy-binding) | `--condition`, `--location`, `--member`, `--project`, `--quiet`, `--role` |
| [`artifacts repositories create`](https://cloud.google.com/sdk/gcloud/reference/artifacts/repositories/create) | `--description`, `--labels`, `--location`, `--project`, `--quiet`, `--repository-format` |
| [`artifacts repositories delete`](https://cloud.google.com/sdk/gcloud/reference/artifacts/repositories/delete) | `--location`, `--project`, `--quiet` |
| [`artifacts repositories describe`](https://cloud.google.com/sdk/gcloud/reference/artifacts/repositories/describe) | `--format`, `--location`, `--project` |
| [`auth login`](https://cloud.google.com/sdk/gcloud/reference/auth/login) | `--cred-file`, `--quiet` |
| [`auth print-access-token`](https://cloud.google.com/sdk/gcloud/reference/auth/print-access-token) | `--quiet` |
| [`beta services identity create`](https://cloud.google.com/sdk/gcloud/reference/beta/services/identity/create) | `--project`, `--quiet`, `--service` |
| [`billing budgets create`](https://cloud.google.com/sdk/gcloud/reference/billing/budgets/create) | `--billing-account`, `--budget-amount`, `--calendar-period`, `--display-name`, `--filter-projects`, `--format`, `--threshold-rule` |
| [`billing budgets delete`](https://cloud.google.com/sdk/gcloud/reference/billing/budgets/delete) | `--quiet` |
| [`billing budgets list`](https://cloud.google.com/sdk/gcloud/reference/billing/budgets/list) | `--billing-account`, `--format` |
| [`billing budgets update`](https://cloud.google.com/sdk/gcloud/reference/billing/budgets/update) | `--add-threshold-rule`, `--budget-amount`, `--calendar-period`, `--clear-threshold-rules`, `--filter-projects`, `--quiet` |
| [`billing projects describe`](https://cloud.google.com/sdk/gcloud/reference/billing/projects/describe) | `--format` |
| [`builds cancel`](https://cloud.google.com/sdk/gcloud/reference/builds/cancel) | `--project`, `--quiet`, `--region` |
| [`builds describe`](https://cloud.google.com/sdk/gcloud/reference/builds/describe) | `--format`, `--project`, `--region` |
| [`builds list`](https://cloud.google.com/sdk/gcloud/reference/builds/list) | `--format`, `--project`, `--region` |
| [`builds submit`](https://cloud.google.com/sdk/gcloud/reference/builds/submit) | `--config`, `--format`, `--gcs-source-staging-dir`, `--ignore-file`, `--project`, `--quiet`, `--region`, `--service-account`, `--substitutions`, `--suppress-logs` |
| [`config set`](https://cloud.google.com/sdk/gcloud/reference/config/set) | `--quiet` |
| [`iam service-accounts add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/add-iam-policy-binding) | `--condition`, `--member`, `--project`, `--quiet`, `--role` |
| [`iam service-accounts create`](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/create) | `--description`, `--display-name`, `--project`, `--quiet` |
| [`iam service-accounts delete`](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/delete) | `--project`, `--quiet` |
| [`iam service-accounts describe`](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/describe) | `--format`, `--project` |
| [`iam workload-identity-pools create`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/create) | `--description`, `--display-name`, `--location`, `--project`, `--quiet` |
| [`iam workload-identity-pools create-cred-config`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/create-cred-config) | `--credential-source-file`, `--output-file`, `--service-account` |
| [`iam workload-identity-pools delete`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/delete) | `--location`, `--project`, `--quiet` |
| [`iam workload-identity-pools describe`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/describe) | `--format`, `--location`, `--project` |
| [`iam workload-identity-pools providers create-oidc`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/create-oidc) | `--allowed-audiences`, `--attribute-condition`, `--attribute-mapping`, `--description`, `--display-name`, `--issuer-uri`, `--location`, `--project`, `--quiet`, `--workload-identity-pool` |
| [`iam workload-identity-pools providers delete`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/delete) | `--location`, `--project`, `--quiet`, `--workload-identity-pool` |
| [`iam workload-identity-pools providers describe`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/describe) | `--format`, `--location`, `--project`, `--workload-identity-pool` |
| [`iam workload-identity-pools providers undelete`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/undelete) | `--location`, `--project`, `--quiet`, `--workload-identity-pool` |
| [`iam workload-identity-pools providers update-oidc`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/update-oidc) | `--allowed-audiences`, `--attribute-condition`, `--attribute-mapping`, `--issuer-uri`, `--location`, `--project`, `--quiet`, `--workload-identity-pool` |
| [`iam workload-identity-pools undelete`](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/undelete) | `--location`, `--project`, `--quiet` |
| [`projects add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/projects/add-iam-policy-binding) | `--condition`, `--member`, `--quiet`, `--role` |
| [`projects describe`](https://cloud.google.com/sdk/gcloud/reference/projects/describe) | `--format` |
| [`projects get-iam-policy`](https://cloud.google.com/sdk/gcloud/reference/projects/get-iam-policy) | `--format` |
| [`projects remove-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/projects/remove-iam-policy-binding) | `--condition`, `--member`, `--quiet`, `--role` |
| [`run deploy`](https://cloud.google.com/sdk/gcloud/reference/run/deploy) | `--concurrency`, `--cpu`, `--cpu-throttling`, `--env-vars-file`, `--image`, `--ingress`, `--labels`, `--max-instances`, `--memory`, `--min`, `--min-instances`, `--no-cpu-boost`, `--no-cpu-throttling`, `--no-invoker-iam-check`, `--port`, `--project`, `--quiet`, `--region`, `--service-account`, `--set-secrets`, `--timeout` |
| [`run services add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/run/services/add-iam-policy-binding) | `--condition`, `--member`, `--project`, `--quiet`, `--region`, `--role` |
| [`run services delete`](https://cloud.google.com/sdk/gcloud/reference/run/services/delete) | `--project`, `--quiet`, `--region` |
| [`run services describe`](https://cloud.google.com/sdk/gcloud/reference/run/services/describe) | `--format`, `--project`, `--region` |
| [`run services update-traffic`](https://cloud.google.com/sdk/gcloud/reference/run/services/update-traffic) | `--project`, `--quiet`, `--region`, `--to-latest` |
| [`scheduler jobs pause`](https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/pause) | `--location`, `--project`, `--quiet` |
| [`scheduler jobs resume`](https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/resume) | `--location`, `--project`, `--quiet` |
| [`scheduler jobs run`](https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/run) | `--format`, `--location`, `--project`, `--quiet` |
| [`secrets add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/secrets/add-iam-policy-binding) | `--condition`, `--member`, `--project`, `--quiet`, `--role` |
| [`secrets create`](https://cloud.google.com/sdk/gcloud/reference/secrets/create) | `--labels`, `--project`, `--quiet`, `--replication-policy` |
| [`secrets delete`](https://cloud.google.com/sdk/gcloud/reference/secrets/delete) | `--project`, `--quiet` |
| [`secrets describe`](https://cloud.google.com/sdk/gcloud/reference/secrets/describe) | `--format`, `--project` |
| [`secrets versions add`](https://cloud.google.com/sdk/gcloud/reference/secrets/versions/add) | `--data-file`, `--project`, `--quiet` |
| [`secrets versions list`](https://cloud.google.com/sdk/gcloud/reference/secrets/versions/list) | `--format`, `--project` |
| [`services disable`](https://cloud.google.com/sdk/gcloud/reference/services/disable) | `--project`, `--quiet` |
| [`services enable`](https://cloud.google.com/sdk/gcloud/reference/services/enable) | `--project`, `--quiet` |
| [`services list`](https://cloud.google.com/sdk/gcloud/reference/services/list) | `--enabled`, `--format`, `--project` |
| [`storage buckets add-iam-policy-binding`](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/add-iam-policy-binding) | `--member`, `--project`, `--quiet`, `--role` |
| [`storage buckets create`](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/create) | `--location`, `--project`, `--public-access-prevention`, `--quiet`, `--soft-delete-duration`, `--uniform-bucket-level-access` |
| [`storage buckets describe`](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/describe) | `--format`, `--project` |
| [`storage buckets update`](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/update) | `--lifecycle-file`, `--project`, `--public-access-prevention`, `--quiet`, `--soft-delete-duration`, `--uniform-bucket-level-access`, `--update-labels` |
| [`storage cp`](https://cloud.google.com/sdk/gcloud/reference/storage/cp) | `--project`, `--quiet` |
| [`storage objects describe`](https://cloud.google.com/sdk/gcloud/reference/storage/objects/describe) | `--format`, `--project` |
| [`storage rm`](https://cloud.google.com/sdk/gcloud/reference/storage/rm) | `--project`, `--quiet`, `--recursive` |
