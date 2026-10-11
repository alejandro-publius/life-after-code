# Night Orders container checks

Checked on 2026-10-06 at 04:38 UTC against application commit `5fac2ebf9d3b178cf5d54b85340cb286f861ba1d`. These are local Docker results, not a live Google Cloud deployment.

Source files: [Dockerfile](../../deploy/Dockerfile), [shop app](../../shop/main.py), [shop deployment contract](../../shop/README.md), [relay app](../../relay/main.py), [relay schema](../../relay/nightorders/night-orders.schema.json).

Both app folders build with the existing generic Dockerfile. Their full dependency sets install successfully with `pip install --require-hashes`. The relay imports its bundled `nightorders` package, and the packaged JSON schema exists and parses. No app changes were needed.

The build commands used the managed local Docker daemon and a temporary certificate mount for the workspace proxy. The certificate did not remain in either running container.

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock build --platform=linux/amd64 \
  --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt \
  --build-arg APP_DIR=shop --build-arg CI_COMMIT_SHORT_SHA=5fac2eb \
  -f deploy/Dockerfile -t life-after-code-services-shop:test .

env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS \
  -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock build --platform=linux/amd64 \
  --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt \
  --build-arg APP_DIR=relay --build-arg CI_COMMIT_SHORT_SHA=5fac2eb \
  -f deploy/Dockerfile -t life-after-code-services-relay:test .
```

| Image | Local image SHA-256 |
| --- | --- |
| Shop | `5c90dfab45da948af9ff15854402e8eb065fd284937d361e39b768af0ba2634c` |
| Relay | `c4f5164707bbe174a83afc3c1b2c02d154e1ed2df94598a915d771976f5a4fed` |

Each container ran with `--network=none --memory=256m --cpus=1`, no host port mapping, and the image's normal start command. A Python HTTP probe executed inside each container used localhost directly. The relay used clearly labelled fixture credentials, no real credentials, and blank flow settings. All containers were removed after the checks.

| Container | Runtime settings | Result | Observed startup memory |
| --- | --- | --- | --- |
| Shop | `PORT=8091`, `APP_ENV=production` | Health 200; metrics environment `production`; demo label present | 34.73 MiB |
| Shop staging | `PORT=8092`, `APP_ENV=staging` | Health 200; metrics environment `staging`; demo label present | 34.33 MiB |
| Relay | `PORT=8093`, blank flow consumer and service account | Health 200; missing key refused; correct fixture key refused an unconfigured tick | 41.43 MiB |

Every `/healthz` response was exactly `{"ok": true, "commit": "5fac2eb"}`. Every process had UID `10001`, and `/run/secrets/proxy_ca` was absent. Both shop metrics responses contained `"label": "DEMO SHOP: simulated customers and planted faults"` and an empty `minutes` array, as expected before any demo traffic.

The relay answered an unauthenticated `POST /tick` with status 401. With its fixture relay key, it answered status 500 and `{"ok": false, "error": "relay settings: FLOW_CONSUMER_ID is not set; FLOW_SERVICE_ACCOUNT is not set"}`. No key value appeared in the response. Health indicates that the process is alive; it does not prove that a night watch is configured.

The memory values are startup observations only. They do not establish peak memory, Cloud Run resource requirements, always allocated CPU behavior, single-instance persistence, GitLab access, Secret Manager access, bucket access, Scheduler delivery, uptime alerts, or traffic changes. Those still need a live deployment. No external API was called by the running containers.
