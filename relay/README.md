# The relay

A small FastAPI service on Cloud Run, and the only part of Night Orders that changes production. Code in
[nightorders/](nightorders/) decides; the relay connects it to GitLab, Cloud Run and the on-call phone.

## What one tick does (once a minute, from Cloud Scheduler)

1. Reads tonight's inputs from GitLab: `ops/oncall.yml`, `ops/targets.yml`, `ops/alerts.yml`, the signed
   `ops/night-orders.yml`, and who signed it (the merge, or an approval). Reads the shop's per-minute signals.
2. Restores its memory from Cloud Storage (Cloud Run scales to zero between ticks).
3. Runs one pass of the watch (`nightorders/watch.py`):
   - a new alert opens a GitLab incident with an evidence pack written by code;
   - if a signed order's numbers match, the watch flow is started through the Flows API and asked to name an
     order or decline;
   - code checks the flow's note against the signed file and carries out the order's action, taken from the
     file, never from the note; ten minutes later it re-checks;
   - everything else pages the on-call person (ntfy push plus a note on the incident), with one suggested
     action they can approve with a thumbs-up on that note.
4. In the morning: posts the watch log on the watch issue, starts the dawn flow, and once the on-call
   person signs the countersign (`ops/state.yml`), reverses every night flag change they did not keep and lists traffic changes for a person to undo.
5. Saves its memory. If GitLab, the shop or the store fails three ticks in a row, it pages.

## Routes

| Route | Who calls it | What it does |
|---|---|---|
| `GET /healthz` | deploy job | `{"ok": true, "commit": ...}` |
| `POST /tick` | Cloud Scheduler, with the `X-Relay-Key` header | one tick, as above |
| `GET /` | anyone | read-only status page: tonight's orders, the last watch log (labelled demo) |

## Settings

Environment variables only. Secrets come from Secret Manager; the rest are public identifiers.

| Name | Secret | Meaning |
|---|---|---|
| `GITLAB_URL` | no | `https://gitlab.com` |
| `GITLAB_PROJECT_ID` | no | the project that holds `ops/` and the incidents |
| `GITLAB_TOKEN` | yes | GitLab token with the `api` scope |
| `FLOW_CONSUMER_ID` | no | AI Catalog consumer ID of the watch flow |
| `FLOW_SERVICE_ACCOUNT` | no | the watch flow's GitLab username; only its notes count as answers |
| `DAWN_FLOW_CONSUMER_ID` | no | AI Catalog consumer ID of the dawn flow (optional) |
| `WATCH_ISSUE_IID` | no | the standing "Tonight's watch" issue (optional; without it no log is posted) |
| `SHOP_METRICS_URL` | no | the shop's `/metrics.json` |
| `NTFY_URL` | yes | ntfy topic URL for pages; the random topic name is the only protection |
| `RELAY_KEY` | yes | the key Cloud Scheduler sends in `X-Relay-Key` |
| `GCP_PROJECT_ID`, `GCP_REGION` | no | where the Cloud Run services live (for `traffic_to_revision`) |
| `STATE_BUCKET`, `STATE_OBJECT` | no | where the relay keeps its memory (a local file when the bucket is empty) |

## Run the tests

From the repository root: `uv run pytest -q`. Every test runs offline against fake servers.
