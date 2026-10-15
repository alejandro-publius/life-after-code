"""Night Orders relay: a small FastAPI service on Cloud Run, and the only part that changes production.

Routes:
  GET  /healthz  The deploy contract: {"ok": true, "commit": CI_COMMIT_SHORT_SHA or "local"}.
  GET  /readyz   Whether a tick could run: 200 {"ready": true, "store": "ok"} when every setting is there and
                 the state store answers, else 503 {"ready": false, "problems": [...]} naming settings only.
  POST /tick     Cloud Scheduler calls it once a minute with the X-Relay-Key header. It reads tonight's inputs
                 from GitLab and the shop, restores the Watch from the saved state, runs one tick of
                 nightorders.watch.Watch, saves the state and returns a short JSON summary. The relay does only
                 what the core decides; it adds no decision of its own. One tick runs at a time, across
                 instances: a tick takes a lease in the state store first, and answers 409 if one is held.
  GET  /         A public, read-only status page: tonight's signed orders or "Nothing signed", whether they
                 are active or expired, and the last watch log written by nightorders.dawn.render_watch_log.

When the relay itself fails (GitLab, the shop, the state store, a production change, a missing setting), the
tick returns 500 and is tried again a minute later. After 3 failed ticks in a row the relay pages the on-call
person, then again every 60 minutes while it keeps failing, and sends a quiet push when it works again. A
relay error always wakes her; a single network hiccup does not.

Settings come only from environment variables. The relay never prints, logs or returns their values.

  GITLAB_URL            GitLab base URL, for example https://gitlab.com
  GITLAB_PROJECT_ID     numeric ID (or full path) of the project that holds ops/ and the incidents
  GITLAB_TOKEN          GitLab access token with the api scope (from Secret Manager). Sent only to GITLAB_URL,
                        only in the PRIVATE-TOKEN header.
  FLOW_CONSUMER_ID      numeric AI Catalog item consumer ID of the night watch flow, enabled for the project
                        (Flows API: ai_catalog_item_consumer_id). Not needed with FLOW_START=mention.
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
  FLOW_START            optional: "api" (default) starts the watch and dawn flows through the Flows API; "mention"
                        starts them through their Mention trigger instead: a note on the incident (or the watch
                        issue) that begins with @ and the flow's service account, then the goal. GitLab runs a
                        trigger only for a person, so GITLAB_TOKEN must then be a person's token, not a bot's
                        (doc/user/duo_agent_platform/triggers/_index.md).
  DAWN_FLOW_SERVICE_ACCOUNT optional: GitLab username of the dawn flow's service account. With FLOW_START=mention
                        the dawn flow starts only when it is set.
  SHOP_STAGING_URL      optional: the staging shop's base URL. The rehearsal of a drafted order applies it on
                        staging, checks this shop still serves a checkout, and restores the flag.
  SHOP_ERRORS_URL       optional: the shop's /errors.json. When an incident opens, its recent error lines are
                        copied into the evidence pack, fenced and labelled as data. Defaults to SHOP_METRICS_URL
                        with /metrics.json replaced by /errors.json.
  WATCH_MODE            optional: "flow" (default) starts the watch flow and lets the model check the reason;
                        "standing" is Standing Orders, the fallback for an account whose Flows API refuses to
                        start a flow: no model at night, code carries out the first signed order whose numbers
                        hold and says so on the incident. In this mode FLOW_CONSUMER_ID and
                        FLOW_SERVICE_ACCOUNT may be empty.

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
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, Header
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from nightorders import daysheet, kept, morning, rehearsal, state, status_page
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
CHORES_BUDGET_SECONDS = 50.0  # the day sheet and the rehearsal, after the watch: well inside the 90 s lease
COUNTERSIGN_READ_EVERY = timedelta(minutes=3)  # ops/state.yml is read this often at most while a countersign waits
FAILURES_BEFORE_PAGE = 3
PAGE_AGAIN_AFTER = timedelta(minutes=60)
REQUIRED = ("GITLAB_URL", "GITLAB_PROJECT_ID", "GITLAB_TOKEN", "FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT",
            "SHOP_METRICS_URL", "NTFY_URL", "RELAY_KEY", "GCP_PROJECT_ID", "GCP_REGION")
OPTIONAL_NUMBERS = ("WATCH_ISSUE_IID", "DAWN_FLOW_CONSUMER_ID")
WATCH_MODES = ("flow", "standing")
FLOW_STARTS = ("api", "mention")
FLOW_ONLY = ("FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT")  # not needed under standing orders
PAGE_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; style-src 'self'; img-src 'self' data:; base-uri 'none'; "
                               "form-action 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
}
DEMO_PAGE_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; "
                               "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
                               "form-action 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
}


@lru_cache(maxsize=4)
def demo_replay(signed: bool, approved: bool) -> dict:
    from nightorders.browser_demo import replay

    return replay(signed=signed, approved=approved)


@dataclass(frozen=True)
class Config:
    """The relay's settings, read from the environment. repr never shows a value."""

    values: dict[str, str]
    on_cloud_run: bool = False

    @classmethod
    def from_env(cls, env: Any = None) -> "Config":
        env = os.environ if env is None else env
        names = REQUIRED + ("STATE_BUCKET", "STATE_OBJECT", "SHOP_STAGING_URL", "SHOP_ERRORS_URL",
                            "WATCH_MODE", "FLOW_START", "DAWN_FLOW_SERVICE_ACCOUNT") + OPTIONAL_NUMBERS
        return cls(values={name: str(env.get(name, "")).strip() for name in names},
                   on_cloud_run=bool(env.get("K_SERVICE")))

    def __getitem__(self, name: str) -> str:
        return self.values[name]

    def __repr__(self) -> str:
        return f"Config(set: {', '.join(sorted(n for n, v in self.values.items() if v))})"

    @property
    def errors_url(self) -> str:
        """The shop's /errors.json: SHOP_ERRORS_URL, or the metrics URL's sibling."""
        if self.values.get("SHOP_ERRORS_URL"):
            return self.values["SHOP_ERRORS_URL"]
        metrics = self.values.get("SHOP_METRICS_URL", "")
        return metrics[: -len("/metrics.json")] + "/errors.json" if metrics.endswith("/metrics.json") else ""

    @property
    def standing(self) -> bool:
        """Standing Orders: no model at night, code alone carries out the signed orders."""
        return self.values.get("WATCH_MODE", "") == "standing"

    @property
    def flow_start(self) -> str:
        """How the relay starts a flow: "api" (the Flows API), or "mention" (a note that mentions the flow's
        service account)."""
        return self.values.get("FLOW_START", "") or "api"

    def problems(self) -> list[str]:
        mode = self.values.get("WATCH_MODE", "")
        problems = []
        if mode and mode not in WATCH_MODES:
            problems.append("WATCH_MODE must be one of " + ", ".join(WATCH_MODES))
        if self.flow_start not in FLOW_STARTS:
            problems.append("FLOW_START must be one of " + ", ".join(FLOW_STARTS))
        skip = FLOW_ONLY if self.standing else ("FLOW_CONSUMER_ID",) if self.flow_start == "mention" else ()
        problems += [f"{name} is not set" for name in REQUIRED if not self.values[name] and name not in skip]
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
    gitlab: Any = None                  # gitlab_ports.GitLab, for the day sheet at dusk
    rehearse: Callable[[dict, datetime, Inputs], list[str]] | None = None  # the rehearsal of drafted orders
    standing: bool = False              # Standing Orders: no model at night, code alone acts on signed orders
    kept_ports: Any = None              # ports for the kept list (kept.py), on the chores budget
    chores_sources: Any = None          # .state_file(user) on the chores budget, for the countersign (else sources)


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


def make_pager(config: Config) -> Callable[..., None]:
    """The relay's own pager. It needs only NTFY_URL, so a missing setting elsewhere can still wake someone."""

    def pager(title: str, lines: tuple[str, ...], priority: str = "urgent") -> None:
        if not config["NTFY_URL"]:
            raise RelayError("NTFY_URL is not set, so nobody can be paged")
        push(Http(http_client()), config["NTFY_URL"], title, lines, priority=priority)

    return pager


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
                           watch_issue=watch_issue, errors_url=config.errors_url, flow_start=config.flow_start,
                           dawn_flow_service_account=config["DAWN_FLOW_SERVICE_ACCOUNT"])

    # The day sheet and the rehearsal read and write a lot, so they get a budget of their own, large enough
    # for the rehearsal's wait on the staging shop and still inside the tick lease.
    chores = Http(http_client(), budget_seconds=CHORES_BUDGET_SECONDS)
    gitlab_plain = GitLab(chores, config["GITLAB_URL"], config["GITLAB_PROJECT_ID"], config["GITLAB_TOKEN"])
    rehearsal_ports = GitLabPorts(gitlab_plain, chores, flow_consumer_id=config["FLOW_CONSUMER_ID"],
                                  flow_service_account=config["FLOW_SERVICE_ACCOUNT"], ntfy_url=config["NTFY_URL"],
                                  gcp_project=config["GCP_PROJECT_ID"], gcp_region=config["GCP_REGION"],
                                  google_token=token)

    def rehearse(relay_doc: dict, now: datetime, inputs: Inputs) -> list[str]:
        return rehearsal.step(relay_doc, now, inputs.oncall, inputs.targets, gitlab_plain, rehearsal_ports, chores,
                              config["SHOP_STAGING_URL"])

    kept_ports = GitLabPorts(gitlab_plain, chores, flow_consumer_id=config["FLOW_CONSUMER_ID"],
                              flow_service_account=config["FLOW_SERVICE_ACCOUNT"], ntfy_url=config["NTFY_URL"],
                              gcp_project=config["GCP_PROJECT_ID"], gcp_region=config["GCP_REGION"],
                              google_token=token, watch_issue=watch_issue)
    return Relay(sources=GitLabSources(gitlab, budget, config["SHOP_METRICS_URL"]), store=store,
                 make_ports=make_ports, pager=make_pager(config), watch_issue=watch_issue, gitlab=gitlab_plain,
                 rehearse=rehearse, standing=config.standing, kept_ports=kept_ports,
                 chores_sources=GitLabSources(gitlab_plain, chores, config["SHOP_METRICS_URL"]))


def readiness(config: Config, make_store: Callable[[Config], Any]) -> list[str]:
    """What stops a tick from running: missing settings, or a state store that does not answer. Names only."""
    problems = config.problems()
    try:
        make_store(config).load()
    except (RelayError, state.StateError) as error:
        problems.append(f"state store: {str(error).split(' (')[0]}")  # the what and the status, never the server's text
    except Exception as error:
        problems.append(f"state store: {type(error).__name__}")
    return problems


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
                    "problems": list(inputs.orders_problems), "daysheet_at": oncall.daysheet_at.strftime("%H:%M")}
    if orders is None:
        return status
    _, end = watch_window(orders, oncall)
    # Signed properly within the window, whether or not that window has ended yet. A reason the sources found (an
    # approval given before the commit it would sign) comes first.
    status["problems"] = list(inputs.orders_problems) + signature_problems(orders, signature, oncall,
                                                                           min(now, end - timedelta(microseconds=1)))
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
        "merge_request": signature.merge_request if signature else None,
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


def countersign_file(relay: Relay, relay_doc: dict, user: str, now: datetime) -> morning.StateFile | None:
    """ops/state.yml as signed, while the morning waits for a countersign. It is read after the watch, on the chores
    budget, and at most every COUNTERSIGN_READ_EVERY, so it never takes the night watch's time. A failure is logged
    and the file is read again COUNTERSIGN_READ_EVERY later. While a signed plan is being carried out, the record
    holds it and nothing is read."""
    record = relay_doc.get("dawn")
    if not record or record.get("countersign") is not None or record.get("applying"):
        return None
    last = relay_doc.get("countersign_read_at")
    if last and now - datetime.fromisoformat(last) < COUNTERSIGN_READ_EVERY:
        return None
    relay_doc["countersign_read_at"] = now.isoformat()
    try:
        return (relay.chores_sources or relay.sources).state_file(user)
    except Exception as error:
        log.warning("could not read the countersign: %s", reason(error))
        return None


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
    watch = Watch(night, ports, inputs.rules, standing=relay.standing)
    state.restore(watch, doc)
    seen = len(ledger.events)
    relay_doc = doc.setdefault("relay", {})

    problem = None
    done: list[str] = []
    try:
        watch.tick(inputs.metrics, now)
    except Exception as error:
        problem = f"stopped partway through a tick ({reason(error)})"
        if not isinstance(error, (RelayError, httpx.HTTPError)):
            log.error("unexpected error in a tick", exc_info=error)
    if not problem:
        # The morning comes after the watch and, like the chores below, never fails a tick or pages: a restore that
        # keeps failing is logged, kept in the state and tried again (morning.py hands it to a person in the end).
        # A night that ended with no good tick before noon gets its record first, from the ledger kept for it.
        try:
            for earlier in state.earlier_nights(doc, inputs.oncall, inputs.targets):
                done += morning.step(relay_doc, earlier, True, None, ports, now, relay.watch_issue)
            state_file = countersign_file(relay, relay_doc, inputs.oncall.user, now)
            done += morning.step(relay_doc, night, watch.expired, state_file, ports, now, relay.watch_issue)
            relay_doc.pop("morning_problem", None)
        except Exception as error:
            relay_doc["morning_problem"] = {"at": now.isoformat(), "reason": reason(error)}
            log.warning("morning not finished: %s", reason(error))
        state.forget_recorded(doc)
    if not problem and relay.gitlab is not None and relay.watch_issue is not None:
        # The day sheet is a convenience for the dusk flow, not the watch: a failure is logged, kept in the
        # state so the next tick tries again, and never counted as a failed tick or paged.
        try:
            posted = daysheet.step(relay_doc, now, inputs.oncall, inputs.targets, relay.gitlab, relay.watch_issue)
            done += posted
            if posted:
                relay_doc.pop("daysheet_problem", None)
        except Exception as error:
            relay_doc["daysheet_problem"] = {"at": now.isoformat(), "reason": reason(error),
                                             "date": now.astimezone(inputs.oncall.timezone).date().isoformat()}
            log.warning("day sheet not posted: %s", reason(error))
    if not problem and relay.rehearse is not None:
        # The rehearsal of a drafted orders merge request, the same way: never a failed tick, tried again.
        try:
            done += relay.rehearse(relay_doc, now, inputs)
            relay_doc.pop("rehearsal_problem", None)
        except Exception as error:
            relay_doc["rehearsal_problem"] = {"at": now.isoformat(), "reason": reason(error)}
            log.warning("rehearsal not done: %s", reason(error))
    if not problem and relay.kept_ports is not None and relay_doc.get("kept"):
        # The kept list: a lease that is due ends in daytime. The same way: never a failed tick, tried again.
        # kept.step says itself which kept change could not be checked (kept_problem), and clears it when all could.
        try:
            done += kept.step(relay_doc, now, inputs.oncall, relay.kept_ports)
        except Exception as error:
            relay_doc["kept_problem"] = {"at": now.isoformat(), "reason": reason(error)}
            log.warning("kept list not checked: %s", reason(error))
    # Keep what the tick did before any failure, so nothing it did is done twice.
    state.capture(watch, doc)
    doc["ports"] = ports.saved()
    relay_doc["status"] = status_of(inputs, now)
    relay_doc["status"].update(standing=relay.standing, project_url=inputs.project_url, watch_issue=relay.watch_issue,
                               samples=status_page.samples_of(inputs.metrics, now))
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
        "mode": "standing" if relay.standing else "flow",
        "orders": orders_line(relay_doc["status"], now),
        "open_incidents": [i.number for i in watch.incidents if not i.closed],
        "events": [f"{e.kind}: {e.text}"[:240] for e in ledger.events[seen:]],
        "morning": done,
    }


def _e(text: Any) -> str:
    return html.escape(str(text), quote=True)


def render_status(doc: dict | None, now: datetime, unavailable: bool = False) -> str:
    """The public status page: plain HTML drawn with the demo's stylesheet, no scripts, every value escaped."""
    return status_page.render(doc, now, unavailable)


def _key_ok(given: str | None, expected: str) -> bool:
    return bool(expected) and given is not None and hmac.compare_digest(given.encode(), expected.encode())


def create_app(make_store: Callable[[Config], Any] = make_store,
               make_relay: Callable[[Config, Any], Relay] = make_relay,
               clock: Callable[[], datetime] | None = None, page_cache_seconds: float = 15.0,
               make_pager: Callable[[Config], Callable[..., None]] = make_pager) -> FastAPI:
    app = FastAPI(title="Night Orders relay", docs_url=None, redoc_url=None, openapi_url=None)
    health = Health()
    one_at_a_time = threading.Lock()
    now = clock or (lambda: datetime.now(timezone.utc))
    # The public page and its JSON share one snapshot of the state, read at most every page_cache_seconds, so a
    # burst of views cannot crowd out the tick.
    cached: dict = {"until": 0.0, "page": "", "public": None}

    def snapshot() -> dict:
        if time.monotonic() >= cached["until"]:
            moment = now()
            try:
                doc, _ = make_store(Config.from_env()).load()
                page, public = render_status(doc, moment), {"available": True, **status_page.public(doc, moment)}
            except Exception as error:
                log.warning("status page: %s", reason(error))
                page, public = render_status(None, moment, unavailable=True), {"available": False}
            cached.update(until=time.monotonic() + page_cache_seconds, page=page, public=public)
        return cached
    demo_files = Path(__file__).with_name("demo_web")

    @app.get("/demo", response_class=HTMLResponse)
    @app.get("/demo/", response_class=HTMLResponse, include_in_schema=False)
    def guided_demo() -> FileResponse:
        return FileResponse(demo_files / "index.html", media_type="text/html", headers=DEMO_PAGE_HEADERS)

    @app.get("/demo/replay")
    def replay_night(signed: bool = True, approved: bool = True) -> JSONResponse:
        # Fixed fixture selectors only. This route never reads runtime credentials,
        # GitLab, a production state store or the tick's action ports.
        return JSONResponse(demo_replay(signed, approved), headers=DEMO_PAGE_HEADERS)

    app.mount("/demo/assets", StaticFiles(directory=demo_files, check_dir=False), name="demo-assets")

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True, "commit": os.environ.get("CI_COMMIT_SHORT_SHA") or "local"}

    @app.get("/readyz")
    def readyz() -> JSONResponse:
        problems = readiness(Config.from_env(), make_store)
        if problems:
            return JSONResponse({"ready": False, "problems": problems}, status_code=503)
        return JSONResponse({"ready": True, "store": "ok"})

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
                # A missing setting or store counts like any failed tick, so after three it wakes her too.
                # Only the pager is needed for that; the error names settings, never their values.
                bare = Relay(sources=None, store=None, make_ports=None, pager=make_pager(config))
                code, summary = _failed(bare, health, now(), reason(error), None)
                return JSONResponse(summary, status_code=code)
            moment = now()
            try:
                lease = relay.store.acquire(moment)
            except Exception as error:
                code, summary = _failed(relay, health, moment, f"could not take the tick lease ({reason(error)})",
                                        None)
                return JSONResponse(summary, status_code=code)
            if lease is None:  # another instance is mid-tick: nothing counted, Scheduler comes back in a minute
                return JSONResponse({"ok": False, "error": "a tick is already running"}, status_code=409)
            try:
                code, summary = run_tick(relay, health, moment)
            except Exception as error:  # a bug, not an outage: it still counts, so it still wakes her
                log.error("unexpected error in a tick", exc_info=error)
                code, summary = _failed(relay, health, moment, f"unexpected error ({reason(error)})", None)
            finally:
                try:
                    relay.store.release(lease)
                except Exception as error:  # a stale lease is taken over after LEASE_SECONDS
                    log.warning("could not release the tick lease: %s", reason(error))
            return JSONResponse(summary, status_code=code)
        finally:
            one_at_a_time.release()

    @app.get("/status.json")
    def status_json() -> JSONResponse:
        public = snapshot()["public"]
        return JSONResponse(public, status_code=200 if public["available"] else 503,
                            headers={"Cache-Control": "no-store"})

    @app.get("/", response_class=HTMLResponse)
    def status_html() -> HTMLResponse:
        return HTMLResponse(snapshot()["page"], headers=PAGE_HEADERS)

    return app


app = create_app()
