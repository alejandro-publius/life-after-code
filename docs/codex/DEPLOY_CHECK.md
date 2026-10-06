# Deployment check and handoff

Checked on 2026-10-06. Work is confined to `deploy/` and `docs/codex/` on `codex/deploy-skeleton`. Main was not merged or changed. No original Second Look resource was touched. No credential was committed or used to call Google Cloud.

## What is ready

- FastAPI `/healthz` returns `{"ok": true, "commit": "local"}` or the supplied commit.
- A digest-pinned Python 3.12 container runs as UID/GID 10001 and listens on `$PORT`. All placeholder dependencies are pinned with hashes.
- A manual default-branch GitLab job uses `id_tokens` and WIF, submits a remote Cloud Build, deploys by image digest, publishes a dynamic environment URL and saves a public deployment receipt.
- Human bootstrap creates the public service and restricts WIF to the exact GitLab project path, numeric project and namespace IDs, and protected default branch. Separate deploy, build and runtime accounts keep their permissions distinct.
- Setup and teardown keep an ownership journal and refuse conflicting resources. A USD 5 monthly budget sends alerts. It does not cap spending.
- [Rules audit](RULES_CHECK.md) records quotations and source conflicts. [Deployment guide](../../deploy/README.md) contains account links, exact steps, costs, shutdown and official technical references.

## Checks run

| Command or check | Result |
| --- | --- |
| `shellcheck -x deploy/*.sh` | Passed, ShellCheck 0.11.0 |
| `bash -n deploy/setup_gcp.sh deploy/teardown_gcp.sh deploy/ci_deploy.sh deploy/lib.sh` | Passed |
| `python3 -m py_compile deploy/bootstrap_state.py deploy/hello/main.py deploy/tests/demo_gcloud.py deploy/tests/test_bootstrap.py` | Passed |
| `python3 -m unittest discover -s deploy/tests -v` | Nine tests passed, 32.7 seconds, in the bootstrap agent's final run. Root's earlier eight-test run also passed. No live API was used. |
| PyYAML `safe_load` of `deploy/gitlab-ci-deploy.yml` and `deploy/cloudbuild.yaml` | Passed. Assertions checked the GitLab token audience, manual protected default-branch rule, E2_STANDARD_2 machine and BuildKit setting. This does not replace an authenticated GitLab pipeline run. |
| CI helper with debug tracing or missing required input | Both refused before authentication |
| Long-dash and whitespace checks on owned text files | Passed |

The lifecycle tests use the clearly labelled `demo_gcloud.py` command harness. They exercise setup twice without duplicate resources, recovery from the private state backup, rejection of a wrong teardown confirmation, preservation of originally enabled APIs, teardown twice, restoration of owned soft-deleted WIF, rejection of permission errors, and preservation of an unrelated service account. They check our command flow, not Google's real IAM behavior.

The managed workspace has a TLS inspection proxy. The Docker test supplied its public CA bundle as an optional BuildKit secret. It was not copied into the image. Docker was directed explicitly to the managed daemon:

```bash
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock build --platform=linux/amd64 \
  --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt \
  --build-arg CI_COMMIT_SHORT_SHA=deploytest \
  -f deploy/Dockerfile -t life-after-code-deploy:test .
```

Build passed. The resulting image digest was `sha256:ce895b8c2194685655868575a37f977b68b9339157a0e641832a193ed8ebcf38`.

Two real containers were run from that image:

- Host `127.0.0.1:18087`, container port 8080: `curl --fail --silent http://127.0.0.1:18087/healthz` returned `{"ok":true,"commit":"deploytest"}`.
- Host `127.0.0.1:18099`, with `PORT=8099` and empty `CI_COMMIT_SHORT_SHA`: the same route returned `{"ok":true,"commit":"local"}`. This verified a nondefault port and the fallback.
- `docker exec lac-deploy-health id` returned `uid=10001(app) gid=10001(app) groups=10001(app)`.
- The container had no `/run/secrets/proxy_ca`, `/app/.git` or `/app/docs`. Both test containers were stopped and removed.

## What remains account-dependent

No Google credentials or configured GitLab project were available. We did not run live setup, issue a GitLab ID token, perform token exchange, submit a Cloud Build, deploy to Cloud Run, send a budget email or delete live resources. Real IAM, organization policy, billing access and GitLab environment URL behavior remain unverified. The CI SDK and Cloud Build Docker builder use Google's current published tags, so their future changes require a real pipeline smoke test.

Alex must supply the provisioned GitLab project's IDs and protected default branch, create a separate billing-linked Google project, run setup in Cloud Shell, paste the printed protected CI variables, and manually run the deployment after Claude integrates the include. The [guide](../../deploy/README.md#alexs-steps) gives exact clicks and commands.

## Claude integration notes

1. Add `deploy` to the root pipeline's existing stages and include `deploy/gitlab-ci-deploy.yml`. Keep preceding tests and security gates. No root file was created here.
2. Change only `ARG APP_DIR=deploy/hello` in `deploy/Dockerfile` once your app folder has `main.py` exposing `app`, hash-locked `requirements.txt`, and the same `/healthz` commit contract. Other layouts need adaptation before that one-line swap.
3. The pipeline currently deploys one `staging` service. A failed post-deploy health check fails the job but leaves the candidate serving. There is no automatic rollback or separate production environment in this skeleton.
4. Duo Agent Platform is mandatory under the verified rules. Claude API alone is insufficient. Register for the organizer's Contributor provisioning early. The deadline is October 27 at 13:00 UTC; use a public YouTube video strictly under three minutes.
5. Copy the source conflicts from `RULES_CHECK.md` into your owned `docs/DECISIONS.md`. Set up the required public MIT GitLab repository, visible CI history and Contributor/DCO workflow. These Codex commits have no forged Alex sign-off; Alex should review the required legal certification through the GitLab contribution process.

The [Google bonus](https://gitlab-transcend.devpost.com/rules) needs actual deployment code in the public GitLab repository and a public live Google Cloud URL. This skeleton alone does not establish bonus eligibility.
