# Adopt Night Orders on your own project

For a team that wants its on-call person to sign a few exact actions before bed, on its own GitLab project. Every step below uses files in this repository. Status: the whole loop runs offline here; no live night has run yet ([STATUS.md](STATUS.md)), so treat this as the intended setup, and run the day-one test before trusting it with a real night.

## What you need

| Need | Why | Where it is checked |
|---|---|---|
| A GitLab project with the Duo Agent Platform, feature flags and incidents | The flows draft and judge; flags and incidents hold the record | `scripts/day_one.py` (whoami, catalog, flow steps) |
| A service whose risky changes sit behind a GitLab feature flag, or on Cloud Run with earlier revisions | Those are the only two actions an order may take: set a flag in one environment, or move all traffic to a named earlier revision | [orders.py](../relay/nightorders/orders.py) refuses anything else |
| Per-minute numbers as JSON, in the shape the relay reads | Code decides what is true from these numbers, never from model text | [shop/metrics.py](../shop/metrics.py) writes the shape; [sources.py](../relay/nightorders/sources.py) reads it |
| An ntfy topic, or a phone that can receive one | Pages and the quiet morning push | the relay's `NTFY_URL` |
| A place to run the relay once a minute | Cloud Run plus Cloud Scheduler here, with keyless auth | [deploy/README.md](../deploy/README.md) |

The numbers: `{"minutes": [{"at": "2026-10-21T10:12:00+00:00", "checkout_error_rate.new": 0.079, "checkouts.new": 30, ...}]}`, one object per complete minute. Each rate needs the count behind it (`checkouts.new` for `checkout_error_rate.new`), because an order never acts on thin traffic.

## Steps

1. **Say what an order may touch.** Edit [ops/targets.yml](../ops/targets.yml): your flags and their environments, your Cloud Run services, your signals, and `min_per_minute` for each signal. List only what you would reverse yourself at 03:00 without thinking. Signals in `always_wake` can never be covered by an order; payment errors are added by code whatever this file says.
2. **Say who is on call.** Edit [ops/oncall.yml](../ops/oncall.yml): the GitLab username (only this person's merge or approval signs), time zone, when orders end, when the day sheet is posted. Put the same username in [.gitlab/CODEOWNERS](../.gitlab/CODEOWNERS).
3. **Say when to look.** Edit [ops/alerts.yml](../ops/alerts.yml): the alert rules the relay applies to your numbers.
4. **Bring the flows.** Create and enable the four flows in [flows/](../flows/) (dusk, watch, dawn, and the probe the day-one test starts) as [FLOWS_SETUP.md](FLOWS_SETUP.md) describes. Copy [.gitlab/duo/mr-review-instructions.yaml](../.gitlab/duo/mr-review-instructions.yaml) too, so Duo Code Review reads each night's orders with these rules. `uv run python flows/validate.py` checks them against GitLab's schema and tool list first. Copy [skills/night-orders/SKILL.md](../skills/night-orders/SKILL.md) too: the flows follow it.
5. **Open the watch issue** from [.gitlab/issue_templates/Night watch.md](../.gitlab/issue_templates/Night%20watch.md). It stays open; each evening the on-call person assigns it to the dusk flow.
6. **Deploy the relay** with [deploy/README.md](../deploy/README.md), or run it anywhere that can call it once a minute with the `X-Relay-Key` header. Its settings are listed at the top of [relay/main.py](../relay/main.py); none is ever printed.
7. **Run the day-one test**: `GITLAB_TOKEN=... python scripts/day_one.py --project <id> --yes`. It checks the token, the flags, the flow catalog, an API-started flow, and whether the on-call person's role signs by merge or by approval. If the Flows API will not start a flow on your account, set `WATCH_MODE=standing`: no model at night, code alone carries out signed orders and says so.
8. **Run one test night** with [TEST_NIGHT.md](TEST_NIGHT.md) before a real one.

## What stays with your team

- **The menu.** Two actions, on purpose. Adding a third means writing its apply, snapshot, restore and holds code, and its refusals; [REFUSALS.md](REFUSALS.md) is the bar.
- **The floor.** Payment errors always wake. Raise the floor in `always_wake`; code will not let it go lower.
- **The morning.** Nothing changed overnight is forgotten: a night never countersigned is carried into the next, and a kept change can name the merge request whose deployment ends it (`until_deployed`).

## Limits today

- One on-call person per project. A rotation means changing `ops/oncall.yml` at handover, which is itself a merge.
- One metrics endpoint, one shape. A Prometheus or Cloud Monitoring adapter would be a new `sources.py` reader (not built).
- The live path is unproven until the day-one test passes on your account ([STATUS.md](STATUS.md)).
