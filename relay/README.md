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
     action they can approve with a thumbs-up on that note;
   - the re-check also looks at the incident's other alerts: if the order's own signal is back but another
     alert of the same incident still fires, the action did not help enough, and she is paged.
   With `WATCH_MODE=standing` (Standing Orders, the fallback for an account whose Flows API will not start a
   flow) no flow is started: code carries out the first signed order whose numbers hold, as soon as they
   hold, and the note on the incident says that no model checked the reason. Everything else still wakes her.
4. At dusk: posts the day sheet on the watch issue (today's merges, deployments, flags) for the dusk flow, and
   rehearses every new orders merge request: each flag order is applied on staging, the staging shop is
   checked, the flag is restored, and the result is posted on the merge request before anyone signs.
5. In the morning: posts the watch log on the watch issue, starts the dawn flow, and once the on-call
   person signs the countersign (`ops/state.yml`), restores every night change they did not keep to how it
   was before the night, from the snapshot each change recorded (a flag's earlier strategies for that
   environment, a service's earlier traffic allocation). A change that found its target already in place
   is recorded as such and needs no restore.
6. Saves its memory. If GitLab, the shop or the store fails three ticks in a row, it pages.

Only one tick runs at a time, across Cloud Run instances: a tick first takes a short lease in the state store
(a second object next to the state, taken over after 90 seconds if a tick crashed holding it), and a tick
that finds one held answers 409 and leaves everything else alone.

## Routes

| Route | Who calls it | What it does |
|---|---|---|
| `GET /healthz` | deploy job | `{"ok": true, "commit": ...}` |
| `GET /readyz` | deploy job, probes | `{"ready": true, "store": "ok"}`, or 503 with the missing setting names and the store's problem in a few words (never a token or a URL) |
| `POST /tick` | Cloud Scheduler, with the `X-Relay-Key` header | one tick, as above |
| `GET /` | anyone | read-only status page: tonight's orders, whether the night runs on standing orders, the last watch log (labelled demo) |

## Settings

Environment variables only. Secrets come from Secret Manager; the rest are public identifiers.

| Name | Secret | Meaning |
|---|---|---|
| `GITLAB_URL` | no | `https://gitlab.com` |
| `GITLAB_PROJECT_ID` | no | the project that holds `ops/` and the incidents |
| `GITLAB_TOKEN` | yes | GitLab token with the `api` scope |
| `FLOW_CONSUMER_ID` | no | AI Catalog consumer ID of the watch flow (may be empty under standing orders) |
| `FLOW_SERVICE_ACCOUNT` | no | the watch flow's GitLab username; only its notes count as answers (may be empty under standing orders) |
| `WATCH_MODE` | no | `flow` (default): the watch flow checks the reason at night. `standing`: Standing Orders, no model at night, code alone carries out the signed orders and says so |
| `DAWN_FLOW_CONSUMER_ID` | no | AI Catalog consumer ID of the dawn flow (optional) |
| `WATCH_ISSUE_IID` | no | the standing "Tonight's watch" issue (optional; without it no log is posted) |
| `SHOP_METRICS_URL` | no | the shop's `/metrics.json` |
| `SHOP_STAGING_URL` | no | the staging shop's base URL, for the rehearsal (optional) |
| `NTFY_URL` | yes | ntfy topic URL for pages; the random topic name is the only protection |
| `RELAY_KEY` | yes | the key Cloud Scheduler sends in `X-Relay-Key` |
| `GCP_PROJECT_ID`, `GCP_REGION` | no | where the Cloud Run services live (for `traffic_to_revision`) |
| `STATE_BUCKET`, `STATE_OBJECT` | no | where the relay keeps its memory (a local file when the bucket is empty) |

## Run the tests

From the repository root: `uv run pytest -q`. Every test runs offline against fake servers.

To replay the demo night without its recorded agent replies, as Standing Orders would run it:
`cd relay && uv run --project .. python -m nightorders.demo_night ../demo/night-2026-10-20 --standing`.
Code turns the new checkout off at 01:50 on the numbers alone; ten minutes later the re-check sees the old
path still failing and wakes Priya. The same night with the model declines that order and asks her about the
fallback instead. That difference is why the model's key exists.
