# Night Orders service permissions and costs

Checked against official Google documentation on 2026-10-06 at 04:37 UTC. This is a source review, not a live Google Cloud permission test.

## Relay traffic changes

The relay reads a Cloud Run v2 service, keeps its current configuration and etag, and sends a PATCH with `updateMask=traffic` and 100 percent traffic assigned to a named revision. See `relay/nightorders/gitlab_ports.py`, `_send_traffic`. The [PATCH reference](https://docs.cloud.google.com/run/docs/reference/rest/v2/projects.locations.services/patch) documents the field mask and asynchronous operation response. The [IAM permission reference](https://docs.cloud.google.com/run/docs/reference/iam/permissions) identifies `run.services.get` for reads and `run.services.update` for updates.

Google's [rollback and traffic migration guide](https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration) explicitly lists these roles for services deployed from container images:

- `roles/run.developer` on the Cloud Run service.
- `roles/iam.serviceAccountUser` on the service identity.
- `roles/artifactregistry.reader` on the image repository, if applicable.

The [service identity guide](https://docs.cloud.google.com/run/docs/configuring/services/service-identity) explains that Service Account User supplies `iam.serviceAccounts.actAs`. The documented traffic workflow therefore supports granting relay this role on only the shop and shop-staging runtime accounts. Do not grant it on relay's own account, the CI deploy account or the build account.

The public documentation does not explicitly state whether a v2 PATCH restricted to `traffic`, with the template unchanged, skips the actAs check. An exemption for this exact request remains unverified. The setup follows the documented traffic-management requirement; it does not claim that this role is proven necessary for every traffic-only API request. No live identity is available to test omission.

No relay Artifact Registry role is added for the existing-revision traffic request, which reads no image and creates no revision. The guide's broader image-repository prerequisite should be checked if that exact live request fails. Do not grant extra repository access automatically.

Run Developer is scoped to the two shop services. It contains configuration permissions beyond changing traffic. The signed-order checks in the relay provide the narrower action boundary. This is not a Google IAM role that authorizes only traffic changes.

## State and evidence

Relay reads the state object's metadata and a specific generation, then writes with `ifGenerationMatch`. See `relay/nightorders/state.py`, `GcsStore`. [Objects GET](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/get) requires `storage.objects.get`; [Objects INSERT](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/insert) requires `storage.objects.create`, plus `storage.objects.delete` to replace an existing object. [Storage Object User](https://docs.cloud.google.com/iam/docs/roles-permissions/storage) includes those permissions. Grant it on the state bucket only. It does not grant bucket IAM administration.

[Generation preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions) prevent stale writers from overwriting a changed object. A non-matching generation returns HTTP 412. `ifGenerationMatch=0` allows initial creation only when no live object with that name exists. The relay handles 412 as a state conflict. These conditions require no additional IAM role.

Grant relay `roles/logging.viewer` on the dedicated Google project for normal application logs. [Logging access control](https://docs.cloud.google.com/logging/docs/access-control) says this permits reads from the standard log buckets, excluding private Data Access logs. It is project-wide access; filtering a query to a shop service does not narrow the IAM grant. A future narrower boundary would require a log view and a matching application query.

## Secrets and deployments

[Cloud Run secret configuration](https://docs.cloud.google.com/run/docs/configuring/services/secrets) places `roles/secretmanager.secretAccessor` on the runtime service identity. Grant it on each named secret, not the project:

| Runtime account | Secret access |
| --- | --- |
| Shop | unleash-instance-id, demo-key |
| Shop-staging | unleash-instance-id, demo-key |
| Relay | gitlab-token, relay-key, ntfy-url, demo-key |

The keyless CI deploy identity can act as the three runtime accounts and the build account. It configures secret references, not secret contents. Do not grant CI Secret Accessor. Human setup creates the secret versions. Google's secrets guide lists Cloud Run Admin for general secret configuration; the existing service-scoped Run Developer role has `run.services.update` for configuration updates and cannot change service IAM. Deployment with these exact narrow roles remains a live test item.

## Always allocated CPU changes the cost model

The [billing settings guide](https://docs.cloud.google.com/run/docs/configuring/billing-settings) says instance-based billing requires at least 512 MiB. The shop services use `--no-cpu-throttling`, so each needs 512Mi rather than the placeholder's 256Mi. Relay remains request-billed and may use 256Mi.

The [Cloud Run pricing table](https://cloud.google.com/run/pricing) lists, for us-central1 instance billing, 240,000 vCPU-seconds and 450,000 GiB-seconds free each month. Allowances are shared by the billing account. Beyond them, CPU is USD 0.000018 per vCPU-second and memory is USD 0.000002 per GiB-second. One shop at one vCPU and 512 MiB costs USD 0.0684 for one running hour before the free allowance. Two shops running continuously for 30 days cost about USD 93.28 after a fully unused monthly instance allowance. This calculation excludes relay, builds, storage, secrets, scheduling, monitoring and network transfer.

Minimum instances stays zero. Always allocated CPU does not guarantee that a background loop survives: autoscaling can terminate idle instances, and request activity determines scaling from and to zero. The relay's periodic shop metrics request creates request activity on production. Staging can stop when idle. Verify the full demo loop on the real service before recording the video.

[Maximum instance documentation](https://docs.cloud.google.com/run/docs/configuring/max-instances) says limits may be exceeded briefly. `--max-instances=1` applies per revision, so a revision transition can overlap two running revisions. Moving traffic to one revision does not make in-memory metrics durable or preserve them through an instance restart or rollback. Treat fresh or discontinuous windows as incomplete evidence, subject to the application's existing decision rules.

Budget alerts are notifications, not spending caps. The costs above are estimates, not a promise that this deployment stays free. See [Google's budget guide](https://cloud.google.com/billing/docs/how-to/budgets).
