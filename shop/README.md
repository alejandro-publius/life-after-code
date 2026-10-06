# Juniper Market (demo shop)

**DEMO DATA.** Juniper Market is the shop the on-call engineer protects in the Night Orders demo. Its customers, orders, traffic, catalog and both faults are simulated. Nothing is charged or shipped. The shop page carries the banner "DEMO SHOP: simulated customers and planted faults", and API answers say they are demo orders, demo traffic or planted demo faults. Demo data lives in files named for it: `demo_catalog.py` (products, regions, stock cache) and `demo_traffic.py` (simulated customers and carts).

What it does:

- Two checkout paths behind the GitLab feature flag `new_checkout`. The old path rounds every price half up to the cent. The new path (MR !31 in the demo story, "New checkout: price rounding per region") rounds with `round_price()` to each region's step.
- Stock from a small cache when the flag `stock_from_cache` is on.
- Two planted demo faults, `rounding_bug` and `inventory_slow`, switched on purpose during a demo night.
- Per-minute signals at `/metrics.json`, read by the relay (`SHOP_METRICS_URL`).
- A demo traffic loop of about 60 checkouts a minute, at most 30 minutes long.

It behaves like `DemoShop` in [relay/nightorders/demo_night.py](../relay/nightorders/demo_night.py), the shop model the demo night replay uses. `tests/test_shop_traffic.py` checks that: it runs simulated nights against this app and feeds `/metrics.json` into the relay's own alert code, which fires the same alerts as the replay.

## Run it locally

```bash
cd shop
FLAGS_OVERRIDE=new_checkout=on DEMO_KEY=local-demo-key uv run --project .. uvicorn main:app --port 8080
```

Open http://localhost:8080/. Then, in another terminal:

```bash
# One checkout. 16.46 USD of jam is 12.345 GBP after the region step.
curl -s -X POST localhost:8080/checkout -H 'content-type: application/json' \
  -d '{"user": "pilot-01", "region": "uk", "items": [{"sku": "juniper-jam", "price": 16.46, "qty": 1}]}'

# Switch on a planted demo fault, then send 25 minutes of demo traffic.
curl -s -X POST localhost:8080/demo/faults -H 'X-Demo-Key: local-demo-key' \
  -H 'content-type: application/json' -d '{"rounding_bug": true}'
curl -s -X POST 'localhost:8080/demo/traffic?minutes=25' -H 'X-Demo-Key: local-demo-key'

# What the relay reads.
curl -s localhost:8080/metrics.json
```

## Deploy

This folder follows the contract in [deploy/README.md](../deploy/README.md): `main.py` exposes the FastAPI object `app`, `requirements.txt` is fully hash-locked for `pip install --require-hashes`, and `GET /healthz` answers `{"ok": true, "commit": <CI_COMMIT_SHORT_SHA or "local">}`. To ship it, `ARG APP_DIR=deploy/hello` in `deploy/Dockerfile` becomes `ARG APP_DIR=shop` (Codex owns `deploy/`).

`requirements.txt` is generated from `requirements.in`, which pins the versions in `uv.lock`. From the repository root:

```bash
uv pip compile shop/requirements.in --python-version 3.12 --generate-hashes --output-file shop/requirements.txt
```

On 2026-10-06 `pip install --no-cache-dir --require-hashes -r shop/requirements.txt` succeeded on Python 3.12, and the app started from a copy of this folder with `python -m uvicorn main:app`, the image's start command.

**Demo traffic on Cloud Run.** The deploy uses `--cpu-throttling` ([deploy/ci_deploy.sh](../deploy/ci_deploy.sh)): CPU is given only while a request is being handled. The traffic loop runs in the background between requests, so on such a service it would run slowly and unevenly (unverified on a live service). The shop service needs CPU always allocated (`--no-cpu-throttling`) for demo nights, or the traffic must come from outside.

## Endpoints

| Method and path | What it does | Needs DEMO_KEY |
| --- | --- | --- |
| `GET /` | The shop page: banner, flag states and where they come from, planted faults, demo traffic, the last 10 minutes of signals as a table, the catalog. Refreshes every 15 seconds. | no |
| `GET /products` | The demo catalog, US dollar list prices. | no |
| `POST /checkout` | Body: `{"user": "...", "region": "us" \| "uk" \| "eu" \| "ca", "items": [{"sku": "...", "price": 8.0, "qty": 1}]}`. Answers 200 with a demo order, or 500 (the price could not be rounded), 504 (stock lookup timed out), 502 (payment failed), 422 (bad request). | no |
| `GET /metrics.json` | The last 60 complete minutes of signals, for the relay. | no |
| `POST /demo/faults` | Body like `{"rounding_bug": true}`. Changes only the faults named; an unknown name changes nothing and answers 400. | yes |
| `POST /demo/traffic?minutes=N` | Starts (or restarts) N minutes of demo traffic, N from 1 to 30. `minutes=0` stops it. | yes |
| `GET /healthz` | `{"ok": true, "commit": "<CI_COMMIT_SHORT_SHA or local>"}` | no |

Send the key in the `X-Demo-Key` header. A wrong or missing key answers 401. If `DEMO_KEY` is not set, the demo controls are off and answer 403.

## Environment variables

| Name | Meaning | When unset |
| --- | --- | --- |
| `UNLEASH_URL` | GitLab's feature flag API URL, from **Deploy > Feature flags > Configure**. It looks like `https://gitlab.com/api/v4/feature_flags/unleash/<project id>`. | No flag service: every flag is off unless `FLAGS_OVERRIDE` sets it. |
| `UNLEASH_INSTANCE_ID` | The instance ID from the same dialog. Anyone with it can read the project's flags, so keep it in Secret Manager or a masked CI/CD variable, never in the repository. | Same as above. |
| `APP_ENV` | The GitLab environment whose flag strategies apply, sent as the Unleash app name: `production` for the `shop` service, `staging` for `shop-staging`. Shown on the page. | `production` |
| `DEMO_KEY` | Shared key for `POST /demo/faults` and `POST /demo/traffic`. Keep it in Secret Manager. | Demo controls answer 403. |
| `FLAGS_OVERRIDE` | Local override for tests and offline demos, like `new_checkout=on,stock_from_cache=off`. An overridden flag ignores GitLab, and `on` means on for every user. The page labels it "FLAGS_OVERRIDE (local override)". | Flags come from GitLab. |
| `FAULTS` | Planted demo faults to switch on at start, for scripted runs: `rounding_bug,inventory_slow`, or `name=on` / `name=off`. | All faults off. |
| `CI_COMMIT_SHORT_SHA` | Set by the deploy. Shown by `/healthz` and the page. | `local` |

`PORT` is read by the image's start command, not by the app. Bad entries in `FLAGS_OVERRIDE` or `FAULTS` are ignored and logged as warnings at start.

## Feature flags from GitLab

GitLab serves feature flags through an Unleash-compatible API ([feature flags doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/feature_flags.md)). The shop has its own small client in `flags.py` (httpx only, no Unleash SDK):

- It sends `GET {UNLEASH_URL}/client/features` with the headers `UNLEASH-INSTANCEID` and `UNLEASH-APPNAME` (the environment). GitLab reads exactly these headers ([lib/api/unleash.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/unleash.rb)); without an app name it returns no flags ([feature_flags_client.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/operations/feature_flags_client.rb)).
- The answer is `{"version": 1, "features": [{"name", "enabled", "strategies": [{"name", "parameters"}]}]}`. GitLab lists only flags with a strategy for this environment, so a missing flag is off ([unleash_spec.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/spec/requests/api/unleash_spec.rb)).
- Strategies: `default` (all users), `userWithId` (user IDs and user lists, `{"userIds": "a,b"}`), `gradualRolloutUserId` and `flexibleRollout` ([strategy.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/operations/feature_flags/strategy.rb), [unleash_feature.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/entities/unleash_feature.rb)). Percentages use Unleash's hash, checked in the tests against the [Unleash client specification](https://github.com/Unleash/client-specification). `flexibleRollout` by session ID counts as off (the shop has no sessions), and so does any strategy it does not know.
- Flags are cached for 15 seconds. A customer never waits for GitLab: a request that finds the cache old starts a refresh in the background. When GitLab cannot be reached (or answers 401 or garbage), the last known values stay. At start every flag is off until the first good answer.
- GitLab rate-limits this API per source IP as unauthenticated traffic; at one request every 15 seconds that allows about 125 clients behind one IP (feature flags doc, "Maximum supported clients").

Set up for the demo:

1. **Deploy > Feature flags > New feature flag** `new_checkout`. Strategy **User IDs** with `pilot-01,pilot-02,pilot-03,pilot-04,pilot-05,pilot-06,pilot-07,pilot-08,pilot-09,pilot-10`, environment `production` (and `staging` for rehearsals). The demo traffic sends every second checkout from these users, so half the checkouts take the new path, like the replay (`new_path_share: 0.5`). Keep the old path in use: the evidence of "errors only on the new path" or "errors on both paths" comes from comparing the two. With **All users**, every checkout takes the new path.
2. `stock_from_cache` with strategy **All users** for `production`, status off until someone turns it on.
3. **Configure**: copy the API URL and instance ID into `UNLEASH_URL` and `UNLEASH_INSTANCE_ID`, and set `APP_ENV=production`.

## Planted demo faults

| Fault | What happens | Signals here (demo night replay) |
| --- | --- | --- |
| `rounding_bug` | On the new path, `round_price()` refuses a price with more than two decimals after the region step and raises `ValueError: price 12.345 cannot be rounded`. The old path rounds it. | New path 6.7% to 10% errors a minute, about 7.8% on average (7.9%). Old path near 0 (0.3%). |
| `inventory_slow` | Stock lookups take 0.7 to 0.9 seconds and every fifth one times out after 1 second (HTTP 504), on both paths. With `stock_from_cache` on, stock comes from the cache and checkout works. | Both paths 20% errors (20.3%, 20.4%), HTTP 5xx 12% (12.2%), p95 about 1.2 seconds (1,320 ms), under the 1,500 ms latency alert. |

The fault switch is logged ("planted demo fault rounding_bug switched on"), the page lists the faults under "Planted demo faults", and a failed checkout caused by a fault answers with `"fault": "rounding_bug (planted demo fault)"`.

## Demo traffic

`POST /demo/traffic?minutes=N` sends, for N minutes (30 at most):

- about 60 checkouts a minute, one a second, plus 2 product views for every 3 checkouts;
- every second checkout from a pilot customer (`pilot-01` to `pilot-10`), the rest from `shopper-001` to `shopper-050`;
- carts from the demo catalog to the US, UK, EU and Canada. One cart in 13 on each path is a jar of juniper jam shipped to the UK: 16.46 USD becomes 12.345 GBP after the region step. The loop asks the flag client which path a customer will get, only to spread these carts evenly over both paths, so the error rates are steady from minute to minute.

The requests go through the app itself (httpx `ASGITransport`) with the header `X-Demo-Traffic`, so their log lines say `"traffic": "demo traffic"`. The demo payment stub charges nothing and fails one payment in 500, a tiny baseline like the replay's 0.2%.

## How the relay reads /metrics.json

```json
{
  "label": "DEMO SHOP: simulated customers and planted faults",
  "environment": "production",
  "minutes": [
    {"at": "2026-10-21T10:07:00Z", "checkout_error_rate.old": 0.0, "checkout_error_rate.new": 0.0667,
     "checkout_error_rate.all": 0.0333, "http_5xx_ratio": 0.02, "p95_latency_ms": 412.3, "payment_error_rate": 0.0}
  ]
}
```

- One entry per complete minute (UTC), oldest first, at most the last 60. The current minute appears once it has ended. A request counts in the minute it finishes, so a reported minute never changes.
- Every key except `at` is a metric key from `ops/targets.yml` and `ops/alerts.yml`. The relay's `parse_metrics` in [relay/nightorders/sources.py](../relay/nightorders/sources.py) turns each one into a series.
- Rates are errors / max(requests, 1), so a minute without traffic reads 0.0.
- `checkout_error_rate.<path>`: checkouts on that path that failed (500, 502 or 504) over checkouts on that path. `all` is both paths together. Requests rejected with 422 are not checkouts.
- `http_5xx_ratio`: 5xx answers over all requests, except `/healthz` and `/metrics.json`, which machines poll.
- `p95_latency_ms`: nearest-rank 95th percentile of checkout time in that minute, 0.0 without checkouts.
- `payment_error_rate`: failed payments over payment attempts.
- The counters live in memory. Cloud Run may scale the shop to zero between demo nights; after a restart, minutes before the start are left out rather than reported as zeros. Missing data never counts as a breach in the relay.

## Logs

One JSON object per line on stdout, which Cloud Run sends to Cloud Logging as structured entries. The field names (`severity`, `time`, `logging.googleapis.com/sourceLocation` with `file`, `line`, `function`) follow Google's own [logging library](https://github.com/googleapis/google-cloud-python/blob/main/packages/google-cloud-logging/google/cloud/logging_v2/handlers/structured_log.py). A failed checkout writes one line like this (shortened):

```json
{"severity": "ERROR",
 "message": "ValueError: price 12.345 cannot be rounded (shop/checkout.py:63 in round_price, new checkout path)",
 "logging.googleapis.com/sourceLocation": {"file": "shop/checkout.py", "line": 63, "function": "round_price"},
 "stack_trace": "Traceback (most recent call last): ...", "path": "new", "user": "pilot-03", "region": "uk",
 "http_status": 500, "traffic": "demo traffic", "fault": "rounding_bug", "label": "planted demo fault"}
```

The message reads like a real error and points at the real file in this repository. The planted demo fault label sits in its own fields (`fault`, `label`).

## Tests

```bash
uv run pytest -q tests/test_shop_*.py
```

All offline. GitLab is an `httpx.MockTransport`, time is simulated, and service latency is skipped. `relay/main.py` also exists and `relay` comes first on the test path, so the tests load `shop/main.py` by its file path as `shop_main`.

## Not verified

- No real GitLab project was called: there is no GitLab token or project in this workspace. The client follows GitLab's source and request specs and Unleash's client specification (unverified against gitlab.com).
- The background traffic loop on a Cloud Run service with `--cpu-throttling` (unverified, see Deploy).
- Whether Cloud Run passes a header named with an underscore, such as `DEMO_KEY` (the shop accepts it as well as `X-Demo-Key`; unverified). Use `X-Demo-Key`.
