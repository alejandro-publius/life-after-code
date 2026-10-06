"""Night Orders relay: a small FastAPI service on Cloud Run, and the only part that changes production.

Routes:
  GET  /healthz  The deploy contract: {"ok": true, "commit": CI_COMMIT_SHORT_SHA or "local"}.
  POST /tick     Cloud Scheduler calls it once a minute with the X-Relay-Key header. It reads tonight's inputs
                 from GitLab and the shop, restores the Watch from the saved state, runs one tick of
                 nightorders.watch.Watch, saves the state and returns a short JSON summary. The relay does only
                 what the core decides; it adds no decision of its own.
  GET  /         A public, read-only status page: tonight's signed orders or "Nothing signed", whether they
                 are active or expired, and the last watch log written by nightorders.dawn.render_watch_log.

When the relay itself fails (GitLab, the shop, the state store, a production change), the tick returns 500
and is tried again a minute later. After 3 failed ticks in a row the relay pages the on-call person, then
again every 60 minutes while it keeps failing, and sends a quiet push when it works again. A relay error
always wakes her; a single network hiccup does not.

Settings come only from environment variables. The relay never prints, logs or returns their values.

  GITLAB_URL            GitLab base URL, for example https://gitlab.com
  GITLAB_PROJECT_ID     numeric ID (or full path) of the project that holds ops/ and the incidents
  GITLAB_TOKEN          GitLab access token with the api scope (from Secret Manager). Sent only to GITLAB_URL,
                        only in the PRIVATE-TOKEN header.
  FLOW_CONSUMER_ID      numeric AI Catalog item consumer ID of the night watch flow, enabled for the project
                        (Flows API: ai_catalog_item_consumer_id)
  FLOW_SERVICE_ACCOUNT  GitLab username of the watch flow's service account. Only its notes count as answers.
  SHOP_METRICS_URL      the shop's /metrics.json (per-minute buckets)
  NTFY_URL              ntfy topic URL for pages, for example https://ntfy.sh/<secret-topic>. The topic name is
                        the only protection, so keep it in Secret Manager.
  RELAY_KEY             shared key that Cloud Scheduler sends in the X-Relay-Key header (from Secret Manager)
  GCP_PROJECT_ID        Google Cloud project of the Cloud Run services an order may move traffic on
  GCP_REGION            their region, for example us-central1
  STATE_BUCKET          Cloud Storage bucket for the relay's state. Required on Cloud Run, whose files do not
                        last. Leave empty for a local run: the state is then a local JSON file.
  STATE_OBJECT          object name in the bucket (default night-orders/state.json), or the local file path when
                        STATE_BUCKET is empty (default night-orders-state.json in the system temp folder)
  WATCH_ISSUE_IID       optional: the standing "Tonight's watch" issue. At the watch end the relay posts the watch
                        log there, starts the dawn flow on it, and notes the countersign result on it.
  DAWN_FLOW_CONSUMER_ID optional: numeric AI Catalog item consumer ID of the dawn flow

Set by the platform: CI_COMMIT_SHORT_SHA (image build), PORT and K_SERVICE (Cloud Run). Google credentials
come from the Cloud Run metadata server, so no Google key is stored anywhere.
"""

from __future__ import annotations

import hmac
import html
import logging
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, Header
from fastapi.responses import HTMLResponse, JSONResponse

from nightorders import morning, state
from nightorders.dawn import render_watch_log
from nightorders.decide import Night
from nightorders.gitlab_ports import GitLab, GitLabPorts, GoogleToken, Http, RelayError, push
from nightorders.orders import signature_problems, watch_window
from nightorders.sources import GitLabSources, Inputs
from nightorders.watch import Watch

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
# httpx logs every request URL at INFO, and the ntfy URL holds the secret topic. Keep those lines out.
for _noisy in ("httpx", "httpcore"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
log = logging.getLogger("nightorders.relay")

DEMO_LABEL = "DEMO: planted faults, simulated shop"
TICK_BUDGET_SECONDS = 15.0
FAILURES_BEFORE_PAGE = 3
PAGE_AGAIN_AFTER = timedelta(minutes=60)
REQUIRED = ("GITLAB_URL", "GITLAB_PROJECT_ID", "GITLAB_TOKEN", "FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT",
            "SHOP_METRICS_URL", "NTFY_URL", "RELAY_KEY", "GCP_PROJECT_ID", "GCP_REGION")
OPTIONAL_NUMBERS = ("WATCH_ISSUE_IID", "DAWN_FLOW_CONSUMER_ID")
PAGE_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'",
    "X-Content-Type-Options": "nosniff",
}


@dataclass(frozen=True)
class Config:
    """The relay's settings, read from the environment. repr never shows a value."""

    values: dict[str, str]
    on_cloud_run: bool = False

    @classmethod
    def from_env(cls, env: Any = None) -> "Config":
        env = os.environ if env is None else env
        names = REQUIRED + ("STATE_BUCKET", "STATE_OBJECT") + OPTIONAL_NUMBERS
        return cls(values={name: str(env.get(name, "")).strip() for name in names},
                   on_cloud_run=bool(env.get("K_SERVICE")))

    def __getitem__(self, name: str) -> str:
        return self.values[name]

    def __repr__(self) -> str:
        return f"Config(set: {', '.join(sorted(n for n, v in self.values.items() if v))})"

    def problems(self) -> list[str]:
        problems = [f"{name} is not set" for name in REQUIRED if not self.values[name]]
        for name in ("FLOW_CONSUMER_ID",) + OPTIONAL_NUMBERS:
            if self.values.get(name) and not self.values[name].isdigit():
                problems.append(f"{name} must be a number")
        return problems


@dataclass
class Relay:
    """What a tick works with. make_relay builds the real one; tests pass fakes."""

    sources: Any                        # .load(now) -> sources.Inputs
    store: Any                          # .load() -> (document or None, version); .save(document, version)
    make_ports: Callable[[dict], Any]   # saved port memory -> watch.Ports that also has .saved() -> dict
    pager: Callable[..., None]          # pager(title, lines, priority="urgent"): the relay's own pages
    watch_issue: int | None = None      # the standing watch issue for the morning, if one is set


@dataclass
class Health:
    """Failed ticks in a row, kept in this process."""

    failures: int = 0
    since: datetime | None = None
    paged_at: datetime | None = None


_client: httpx.Client | None = None


def http_client() -> httpx.Client:
    """One connection pool for the process. No default headers: each service gets only its own credentials."""
    global _client
    if _client is None:
        _client = httpx.Client(follow_redirects=False)
    return _client


def make_store(config: Config) -> Any:
    if config["STATE_BUCKET"]:
        plain = Http(http_client())
        return state.GcsStore(config["STATE_BUCKET"], config["STATE_OBJECT"] or "night-orders/state.json", plain,
                              GoogleToken(plain))
    if config.on_cloud_run:
        raise RelayError("STATE_BUCKET is required on Cloud Run, where local files do not last")
    return state.FileStore(config["STATE_OBJECT"] or os.path.join(tempfile.gettempdir(), "night-orders-state.json"))


def make_relay(config: Config, store: Any) -> Relay:
    problems = config.problems()
    if problems:
        raise RelayError("relay settings: " + "; ".join(problems))
    budget, plain = Http(http_client(), budget_seconds=TICK_BUDGET_SECONDS), Http(http_client())
    gitlab = GitLab(budget, config["GITLAB_URL"], config["GITLAB_PROJECT_ID"], config["GITLAB_TOKEN"])
    token = GoogleToken(plain)
    watch_issue = int(config["WATCH_ISSUE_IID"]) if config["WATCH_ISSUE_IID"] else None

    def make_ports(saved: dict) -> GitLabPorts:
        return GitLabPorts(gitlab, budget, flow_consumer_id=config["FLOW_CONSUMER_ID"],
                           flow_service_account=config["FLOW_SERVICE_ACCOUNT"], ntfy_url=config["NTFY_URL"],
                           gcp_project=config["GCP_PROJECT_ID"], gcp_region=config["GCP_REGION"],
                           google_token=token, memory=saved, dawn_consumer_id=config["DAWN_FLOW_CONSUMER_ID"],
                           watch_issue=watch_issue)

    def pager(title: str, lines: tuple[str, ...], priority: str = "urgent") -> None:
        push(plain, config["NTFY_URL"], title, lines, priority=priority)

    return Relay(sources=GitLabSources(gitlab, budget, config["SHOP_METRICS_URL"]), store=store,
                 make_ports=make_ports, pager=pager, watch_issue=watch_issue)


def reason(error: BaseException) -> str:
    """A short description of a failure that never carries a URL or a credential."""
    if isinstance(error, (RelayError, state.StateError)):
        return str(error)
    if isinstance(error, httpx.HTTPError):  # its message holds the URL, which can hold the push topic
        return type(error).__name__
    text = " ".join(str(error).split())[:120]
    return f"{type(error).__name__}: {text}" if text else type(error).__name__


def _local(moment: datetime, tz: Any) -> str:
    return moment.astimezone(tz).strftime("%H:%M")


def _timezone(doc: dict | None, inputs: Inputs | None) -> Any:
    if inputs is not None:
        return inputs.oncall.timezone
    name = (((doc or {}).get("relay") or {}).get("status") or {}).get("timezone")
    try:
        return ZoneInfo(name) if name else timezone.utc
    except (KeyError, ValueError):
        return timezone.utc


def status_of(inputs: Inputs, now: datetime) -> dict:
    """What the status page shows about tonight's orders, worked out by the core's own checks."""
    oncall, orders, signature = inputs.oncall, inputs.orders, inputs.signature
    status: dict = {"checked_at": now.isoformat(), "timezone": str(oncall.timezone), "orders": None,
                    "problems": list(inputs.orders_problems)}
    if orders is None:
        return status
    _, end = watch_window(orders, oncall)
    # Signed properly within the window, whether or not that window has ended yet.
    status["problems"] = signature_problems(orders, signature, oncall, min(now, end - timedelta(microseconds=1)))
    signer = None
    if signature is not None:
        signer = oncall.first_name if signature.user == oncall.user else signature.user
    status["orders"] = {
        "night": orders.night.isoformat(),
        "ends_at": end.isoformat(),
        "items": [{"id": o.id, "when": o.when.describe(), "do": o.do.describe(), "because": o.because}
                  for o in orders.orders],
        "signed_by": signer,
        "signed_at": signature.at.isoformat() if signature else None,
        "method": signature.method if signature else None,
    }
    return status


def orders_line(status: dict | None, now: datetime) -> str:
    status = status or {}
    orders = status.get("orders")
    if not orders or status.get("problems") or not orders["items"]:
        return "nothing signed"
    ends = datetime.fromisoformat(orders["ends_at"])
    local = _local(ends, ZoneInfo(status["timezone"]))
    return f"active until {local}" if now < ends else f"expired at {local}"


def _failed(relay: Relay, health: Health, now: datetime, problem: str, doc: dict | None, version: Any = None,
            inputs: Inputs | None = None, night: Night | None = None) -> tuple[int, dict]:
    """Count a failed tick, page the on-call person if failures persist, and save what can be saved."""
    log.error("tick failed: %s", problem)
    health.failures += 1
    health.since = health.since or now
    tz = _timezone(doc, inputs)
    paged = False
    if health.failures >= FAILURES_BEFORE_PAGE and (
            health.paged_at is None or now - health.paged_at >= PAGE_AGAIN_AFTER):
        lines = (f"The night watch relay has failed {health.failures} checks in a row since "
                 f"{_local(health.since, tz)}.",
                 f"Last problem: {problem[:160]}.",
                 "Alerts are not being handled until it works again.")
        try:
            relay.pager("Night Orders: relay problem", lines)
            paged = True
            health.paged_at = now
        except Exception as error:
            log.error("could not page about the relay problem: %s", reason(error))
        if paged and doc is not None:
            who = inputs.oncall.first_name if inputs else "the on-call person"
            ledger = night.ledger if night is not None else state.load_ledger(doc)
            ledger.record(now, "woke", f"Woke {who}: {lines[0]}", page=list(lines), reasons=[problem])
            doc["watch"]["ledger"] = [state.dump_event(e) for e in ledger.events]
            if night is not None:
                doc.setdefault("relay", {})["watch_log"] = {"night": doc["night"], "text": render_watch_log(night)}
    if doc is not None:
        doc.setdefault("relay", {})["error"] = {"since": health.since.isoformat(), "failures": health.failures,
                                                "at": now.isoformat()}
        try:
            relay.store.save(doc, version)
        except Exception as error:
            log.error("could not save the relay state after a failure: %s", reason(error))
    return 500, {"ok": False, "at": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
                 "error": problem, "failures_in_a_row": health.failures, "paged": paged}


def _working_again(relay: Relay, health: Health, now: datetime, tz: Any) -> None:
    if health.paged_at is not None:
        try:
            relay.pager("Night Orders: relay working again",
                        (f"The night watch relay is working again since {_local(now, tz)}.",
                         "Alerts are being handled."), priority="default")
        except Exception as error:
            log.warning("could not send the all-clear push: %s", reason(error))
    health.failures, health.since, health.paged_at = 0, None, None


def run_tick(relay: Relay, health: Health, now: datetime) -> tuple[int, dict]:
    """One pass: load the state and tonight's inputs, run the Watch once, save. Returns (HTTP status, summary)."""
    try:
        loaded, version = relay.store.load()
        doc = state.check(loaded)
    except Exception as error:
        return _failed(relay, health, now, f"could not read the relay state ({reason(error)})", None)
    try:
        inputs = relay.sources.load(now)
    except Exception as error:
        return _failed(relay, health, now, f"could not read tonight's inputs ({reason(error)})", doc, version)

    night_key = state.night_of(now, inputs.oncall)
    if doc is None:
        doc = state.new_document(night_key)
    elif doc["night"] != night_key:
        doc = state.next_night(doc, night_key, inputs.orders, inputs.oncall, now)
    ledger = state.load_ledger(doc)
    night = Night(oncall=inputs.oncall, targets=inputs.targets, orders=inputs.orders,
                  orders_problems=inputs.orders_problems, signature=inputs.signature, ledger=ledger)
    ports = relay.make_ports(doc.get("ports") or {})
    watch = Watch(night, ports, inputs.rules)
    state.restore(watch, doc)
    seen = len(ledger.events)
    relay_doc = doc.setdefault("relay", {})
    state_file = None
    awaited = relay_doc.get("dawn")
    if awaited and awaited.get("countersign") is None:
        # Only the morning needs this, so a failure here never stops the night watch: try again next tick.
        try:
            state_file = relay.sources.state_file(inputs.oncall.user)
        except Exception as error:
            log.warning("could not read the countersign: %s", reason(error))

    problem = None
    done: list[str] = []
    try:
        watch.tick(inputs.metrics, now)
        done = morning.step(relay_doc, night, watch.expired, state_file, ports, now, relay.watch_issue)
    except Exception as error:
        problem = f"stopped partway through a tick ({reason(error)})"
        if not isinstance(error, (RelayError, httpx.HTTPError)):
            log.error("unexpected error in a tick", exc_info=error)
    # Keep what the tick did before any failure, so nothing it did is done twice.
    state.capture(watch, doc)
    doc["ports"] = ports.saved()
    relay_doc["status"] = status_of(inputs, now)
    if ledger.events:
        relay_doc["watch_log"] = {"night": night_key, "text": render_watch_log(night)}
    if problem:
        return _failed(relay, health, now, problem, doc, version, inputs, night)

    relay_doc.pop("error", None)
    try:
        relay.store.save(doc, version)
    except Exception as error:
        return _failed(relay, health, now, f"could not save the relay state ({reason(error)})", None)
    _working_again(relay, health, now, inputs.oncall.timezone)
    return 200, {
        "ok": True,
        "at": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "night": night_key,
        "orders": orders_line(relay_doc["status"], now),
        "open_incidents": [i.number for i in watch.incidents if not i.closed],
        "events": [f"{e.kind}: {e.text}"[:240] for e in ledger.events[seen:]],
        "morning": done,
    }


def _e(text: Any) -> str:
    return html.escape(str(text), quote=True)


def render_status(doc: dict | None, now: datetime, unavailable: bool = False) -> str:
    """The public status page. Plain HTML, no scripts; every value from the state is escaped."""
    relay_doc = (doc or {}).get("relay") or {}
    status = relay_doc.get("status")
    body = [
        f'<p class="demo">{_e(DEMO_LABEL)}. The shop, its traffic and its faults are simulated. '
        "The decisions, the GitLab incidents and the pages are real.</p>",
        "<h1>Night Orders relay</h1>",
        "<p>Before bed, the on-call engineer signs what the agent may do alone tonight. "
        "Everything else wakes them. This page is read-only.</p>",
    ]
    if unavailable:
        body.append("<p>The relay's state cannot be read right now.</p>")
    elif not status:
        body.append("<p>No check has run yet.</p>")
    else:
        tz = ZoneInfo(status["timezone"])
        orders = status.get("orders")
        problems = status.get("problems") or []
        body.append("<h2>Tonight's orders</h2>")
        if orders and not problems and orders["items"]:
            ends = datetime.fromisoformat(orders["ends_at"])
            when = f"Active until {_local(ends, tz)}." if now < ends else f"Expired at {_local(ends, tz)}."
            signed = datetime.fromisoformat(orders["signed_at"])
            body.append(f"<p><strong>{_e(when)}</strong> Signed by {_e(orders['signed_by'])} at "
                        f"{_local(signed, tz)} ({_e(orders['method'])}), for the night of {_e(orders['night'])}.</p>")
            body.append("<ol>")
            for item in orders["items"]:
                body.append(f"<li>Order {_e(item['id'])}: when {_e(item['when'])}, {_e(item['do'])}."
                            f"<br>Because: {_e(item['because'])}</li>")
            body.append("</ol>")
        else:
            body.append("<p><strong>Nothing signed.</strong> Every alert wakes the on-call person.</p>")
            if orders and not problems:
                body.append("<p>The signed file has no orders.</p>")
            if problems:
                body.append("<ul>" + "".join(f"<li>{_e(p)}</li>" for p in problems) + "</ul>")
        body.append("<h2>Last watch log</h2>")
        watch_log = relay_doc.get("watch_log")
        if watch_log:
            body.append(f"<pre>{_e(watch_log['text'])}</pre>")
        else:
            body.append("<p>Nothing has happened yet tonight.</p>")
        dawn = relay_doc.get("dawn")
        if dawn:
            body.append("<h2>Morning countersign</h2>")
            if dawn.get("countersign_text"):
                body.append(f"<pre>{_e(dawn['countersign_text'])}</pre>")
            else:
                count = len(dawn.get("loose_ends") or [])
                body.append(f"<p>Waiting for the on-call person to keep or undo {count} change"
                            f"{'' if count == 1 else 's'} from the night of {_e(dawn['night'])}.</p>")
        checked = datetime.fromisoformat(status["checked_at"])
        body.append(f"<p>Last check {_local(checked, tz)} ({_e(status['timezone'])}).</p>")
        if relay_doc.get("error"):
            body.append("<p>The relay's latest check failed. It pages the on-call person if failures continue.</p>")
    style = (
        "body{font:16px/1.5 system-ui,sans-serif;max-width:46rem;margin:0 auto;padding:16px;color:#1b1b1b;"
        "background:#fff}"
        ".demo{background:#fff3cd;border:1px solid #c9a227;padding:8px 12px;font-weight:600}"
        "pre{white-space:pre-wrap;background:#f4f4f4;padding:12px}"
        "@media (prefers-color-scheme:dark){body{color:#e8e8e8;background:#121212}"
        ".demo{background:#3b3000;border-color:#8a7000}pre{background:#1e1e1e}}"
    )
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>Night Orders relay</title><style>{style}</style></head><body>\n"
            + "\n".join(body) + "\n</body></html>\n")


def _key_ok(given: str | None, expected: str) -> bool:
    return bool(expected) and given is not None and hmac.compare_digest(given.encode(), expected.encode())


def create_app(make_store: Callable[[Config], Any] = make_store,
               make_relay: Callable[[Config, Any], Relay] = make_relay,
               clock: Callable[[], datetime] | None = None, page_cache_seconds: float = 15.0) -> FastAPI:
    app = FastAPI(title="Night Orders relay", docs_url=None, redoc_url=None, openapi_url=None)
    health = Health()
    one_at_a_time = threading.Lock()
    now = clock or (lambda: datetime.now(timezone.utc))
    # The public page is cached briefly, so a burst of views cannot crowd out the tick.
    cached: dict = {"until": 0.0, "page": ""}

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True, "commit": os.environ.get("CI_COMMIT_SHORT_SHA") or "local"}

    @app.post("/tick")
    def tick(x_relay_key: str | None = Header(default=None)) -> JSONResponse:
        config = Config.from_env()
        if not _key_ok(x_relay_key, config["RELAY_KEY"]):
            if not config["RELAY_KEY"]:
                log.error("RELAY_KEY is not set, so every tick is refused")
            return JSONResponse({"ok": False, "error": "missing or wrong X-Relay-Key"}, status_code=401)
        if not one_at_a_time.acquire(blocking=False):
            return JSONResponse({"ok": False, "error": "a tick is already running"}, status_code=409)
        try:
            try:
                relay = make_relay(config, make_store(config))
            except Exception as error:
                log.error("tick refused: %s", reason(error))
                return JSONResponse({"ok": False, "error": reason(error)}, status_code=500)
            moment = now()
            try:
                code, summary = run_tick(relay, health, moment)
            except Exception as error:  # a bug, not an outage: it still counts, so it still wakes her
                log.error("unexpected error in a tick", exc_info=error)
                code, summary = _failed(relay, health, moment, f"unexpected error ({reason(error)})", None)
            return JSONResponse(summary, status_code=code)
        finally:
            one_at_a_time.release()

    @app.get("/", response_class=HTMLResponse)
    def status_page() -> HTMLResponse:
        if time.monotonic() < cached["until"]:
            return HTMLResponse(cached["page"], headers=PAGE_HEADERS)
        try:
            doc, _ = make_store(Config.from_env()).load()
            page = render_status(doc, now())
        except Exception as error:
            log.warning("status page: %s", reason(error))
            page = render_status(None, now(), unavailable=True)
        cached.update(until=time.monotonic() + page_cache_seconds, page=page)
        return HTMLResponse(page, headers=PAGE_HEADERS)

    return app


app = create_app()
