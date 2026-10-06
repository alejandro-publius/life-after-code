"""The relay app: /healthz, /tick and the status page, with fake sources and ports and a file store. Offline.

The demo night is demo data (planted faults, simulated shop). Every key and name here is test data.
relay/main.py is loaded from its file under its own module name, because shop/main.py exists too.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from conftest import OPS, REPO
from nightorders import demo_night
from nightorders.gitlab_ports import RelayError
from nightorders.model import Signature
from nightorders.orders import load_yaml, parse_oncall, parse_orders, parse_targets
from nightorders.signals import Metrics
from nightorders.sources import Inputs
from nightorders.state import FileStore
from nightorders.watch import parse_alert_rules


def load_relay_main():
    spec = importlib.util.spec_from_file_location("relay_main", REPO / "relay" / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["relay_main"] = module
    spec.loader.exec_module(module)
    return module


main = load_relay_main()
KEY = "test-relay-key"
DEMO = REPO / "demo" / "night-2026-10-20"
ONCALL = parse_oncall(load_yaml(OPS / "oncall.yml"))
TARGETS = parse_targets(load_yaml(OPS / "targets.yml"))
RULES = parse_alert_rules(load_yaml(OPS / "alerts.yml"))


def local(text: str) -> datetime:
    """A local time on the demo night: evening times are Oct 20, morning times Oct 21."""
    hours, minutes = (int(x) for x in text.split(":"))
    return datetime(2026, 10, 20 if hours >= 12 else 21, hours, minutes, tzinfo=ONCALL.timezone)


def demo_signature() -> Signature:
    sig = json.loads((DEMO / "signature.json").read_text())
    return Signature(method=sig["method"], user=sig["user"], at=datetime.fromisoformat(sig["at"]), commit=sig["commit"])


class QuietSources:
    """A quiet night (no orders file unless given), or failures on demand."""

    def __init__(self, failures: int = 0, orders=None, signature=None, metrics=None):
        self.failures, self.orders, self.signature = failures, orders, signature
        self.metrics = metrics or Metrics()

    def load(self, now):
        if self.failures:
            self.failures -= 1
            raise RelayError("GitLab read project: HTTP 503")
        return Inputs(oncall=ONCALL, targets=TARGETS, rules=RULES, orders=self.orders, orders_problems=(),
                      signature=self.signature, metrics=self.metrics)


class NoPorts:
    def saved(self):
        return {}


class Rig:
    """An app with fakes injected, a file store, a recorded pager and a settable clock."""

    def __init__(self, tmp_path, sources, ports=None):
        self.store = FileStore(tmp_path / "state.json")
        self.pages: list[tuple] = []
        self.now = local("22:00")
        self.ports = ports or NoPorts()

        def make_relay(config, store):
            return main.Relay(sources=sources, store=store, make_ports=lambda saved: self.ports,
                              pager=lambda title, lines, priority="urgent": self.pages.append((title, lines, priority)))

        app = main.create_app(make_store=lambda config: self.store, make_relay=make_relay, clock=lambda: self.now,
                              page_cache_seconds=0)
        self.client = TestClient(app)

    def tick(self, key: str | None = KEY):
        return self.client.post("/tick", headers={} if key is None else {"X-Relay-Key": key})

    def doc(self) -> dict:
        return self.store.load()[0]


@pytest.fixture
def relay_key(monkeypatch):
    monkeypatch.setenv("RELAY_KEY", KEY)


def test_healthz_follows_the_deploy_contract(monkeypatch):
    client = TestClient(main.create_app())
    monkeypatch.delenv("CI_COMMIT_SHORT_SHA", raising=False)
    assert client.get("/healthz").json() == {"ok": True, "commit": "local"}
    monkeypatch.setenv("CI_COMMIT_SHORT_SHA", "1a2b3c4d")
    assert client.get("/healthz").json() == {"ok": True, "commit": "1a2b3c4d"}


def test_tick_needs_the_relay_key(tmp_path, monkeypatch):
    rig = Rig(tmp_path, QuietSources())
    monkeypatch.delenv("RELAY_KEY", raising=False)
    assert rig.tick().status_code == 401  # no key configured: every tick is refused
    monkeypatch.setenv("RELAY_KEY", KEY)
    assert rig.tick(key=None).status_code == 401
    assert rig.tick(key="wrong-key").status_code == 401
    assert rig.doc() is None  # nothing ran
    assert rig.tick().status_code == 200


def test_a_tick_saves_state_and_returns_a_summary(tmp_path, relay_key):
    rig = Rig(tmp_path, QuietSources())
    response = rig.tick()
    assert response.status_code == 200
    assert response.json() == {"ok": True, "at": "2026-10-21T05:00:00+00:00", "night": "2026-10-20",
                               "orders": "nothing signed", "open_incidents": [], "events": [], "morning": []}
    doc = rig.doc()
    assert doc["version"] == 1 and doc["night"] == "2026-10-20"
    assert doc["relay"]["status"]["problems"] == [] and doc["relay"]["status"]["orders"] is None


class ThroughTheRelay:
    """Stands in for the Watch inside demo_night.run, and sends every minute through POST /tick instead.

    The relay rebuilds its own Watch from the saved file each minute. demo_night's recording ports play GitLab,
    Cloud Run and the phone, and its simulated shop reacts to the flags the relay changes.
    """

    rig: Rig | None = None
    tmp_path = None

    def __init__(self, night, ports, rules):
        self.night, self.rules, self.metrics = night, rules, Metrics()
        ports.saved = lambda: {}  # the recording ports keep their own record, like GitLab would
        self.summaries: list[dict] = []
        ThroughTheRelay.rig = Rig(ThroughTheRelay.tmp_path, self, ports)
        ThroughTheRelay.rig.summaries = self.summaries

    def load(self, now):
        night = self.night
        return Inputs(oncall=night.oncall, targets=night.targets, rules=self.rules, orders=night.orders,
                      orders_problems=night.orders_problems, signature=night.signature, metrics=self.metrics)

    def tick(self, metrics, now):
        rig = ThroughTheRelay.rig
        self.metrics, rig.now = metrics, now
        response = rig.tick()
        assert response.status_code == 200, response.text
        self.summaries.append(response.json())


@pytest.fixture(scope="module")
def replayed(tmp_path_factory):
    plain_ports, plain_night = demo_night.run(DEMO)
    ThroughTheRelay.tmp_path = tmp_path_factory.mktemp("relay")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("RELAY_KEY", KEY)
        patch.setattr(demo_night, "Watch", ThroughTheRelay)
        relay_ports, _ = demo_night.run(DEMO)
    return plain_ports, plain_night, relay_ports, ThroughTheRelay.rig


def test_the_demo_night_through_the_relay_matches_the_in_memory_replay(replayed):
    plain_ports, plain_night, relay_ports, rig = replayed
    assert relay_ports.log == plain_ports.log
    saved = [(e["kind"], e["text"], datetime.fromisoformat(e["at"])) for e in rig.doc()["watch"]["ledger"]]
    assert saved == [(e.kind, e.text, e.at) for e in plain_night.ledger.events]
    by_time = {s["at"]: s for s in rig.summaries}
    paged = by_time[local("01:52").astimezone(timezone.utc).isoformat()]
    assert paged["open_incidents"] == [1] and any(e.startswith("woke: Woke Priya") for e in paged["events"])
    assert any(e.startswith("acted: Order 1 carried out 03:13") for e in by_time[
        local("03:13").astimezone(timezone.utc).isoformat()]["events"])
    assert rig.summaries[-1]["orders"] == "expired at 07:00" and rig.pages == []


def test_status_page_shows_the_demo_label_the_orders_and_the_watch_log(replayed):
    *_, rig = replayed
    page = rig.client.get("/")
    assert page.status_code == 200 and page.headers["content-security-policy"].startswith("default-src 'none'")
    text = page.text
    assert "DEMO: planted faults, simulated shop" in text
    assert "Expired at 07:00." in text and "Signed by Priya at 22:06 (merge)" in text
    assert "Order 1: when checkout error rate (new path) above 5.0% for 5 min, new_checkout off in production." in text
    assert "Woken: 1 time (01:52)." in text and "Handled while you slept: incident #2 (order 1)." in text
    assert "&lt;script" not in text and "<script" not in text
    rig.now = local("03:00")
    assert "Active until 07:00." in rig.client.get("/").text


def test_status_page_escapes_text_from_files_and_notes(tmp_path, relay_key):
    data = load_yaml(DEMO / "orders.yml")
    data["orders"][0]["because"] = "MR !31 <script>alert(1)</script> turned on new_checkout."
    orders = parse_orders(data, TARGETS, ONCALL)
    rig = Rig(tmp_path, QuietSources(orders=orders, signature=demo_signature()))
    rig.now = local("23:00")
    rig.tick()
    text = rig.client.get("/").text
    assert "<script>" not in text and "Because: MR !31 &lt;script&gt;alert(1)&lt;/script&gt; turned on" in text
    unsigned = Rig(tmp_path / "unsigned", QuietSources(orders=orders))
    unsigned.tick()
    text = unsigned.client.get("/").text
    assert "Nothing signed." in text and "Nobody signed tonight&#x27;s orders." in text and "Because:" not in text


def test_status_page_before_any_tick_and_when_the_state_cannot_be_read(tmp_path):
    assert "No check has run yet." in Rig(tmp_path, QuietSources()).client.get("/").text

    def broken(config):
        raise RelayError("Cloud Storage read state: HTTP 403")

    text = TestClient(main.create_app(make_store=broken)).get("/").text
    assert "cannot be read right now" in text and "DEMO: planted faults, simulated shop" in text


def test_a_burst_of_page_views_reads_the_state_once(tmp_path):
    loads = []

    class CountingStore(FileStore):
        def load(self):
            loads.append(1)
            return super().load()

    client = TestClient(main.create_app(make_store=lambda config: CountingStore(tmp_path / "state.json")))
    assert all(client.get("/").status_code == 200 for _ in range(5))
    assert len(loads) == 1


def test_a_relay_that_keeps_failing_pages_once_then_says_when_it_works_again(tmp_path, relay_key):
    sources = QuietSources()
    rig = Rig(tmp_path, sources)
    assert rig.tick().status_code == 200
    sources.failures = 4
    for minute in range(4):
        rig.now = local("22:01") + timedelta(minutes=minute)
        response = rig.tick()
        assert response.status_code == 500
        assert response.json()["error"] == "could not read tonight's inputs (GitLab read project: HTTP 503)"
    # A hiccup does not wake her; the third failure in a row does, and only once within the hour.
    assert [p[0] for p in rig.pages] == ["Night Orders: relay problem"]
    title, lines, priority = rig.pages[0]
    assert priority == "urgent" and lines[0] == "The night watch relay has failed 3 checks in a row since 22:01."
    woke = [e for e in rig.doc()["watch"]["ledger"] if e["kind"] == "woke"]
    assert len(woke) == 1 and woke[0]["text"].startswith("Woke the on-call person: The night watch relay")
    assert rig.doc()["relay"]["error"]["failures"] == 4
    assert "latest check failed" in rig.client.get("/").text
    rig.now = local("22:05")
    assert rig.tick().status_code == 200
    assert rig.pages[-1][0] == "Night Orders: relay working again" and rig.pages[-1][2] == "default"
    assert "error" not in rig.doc()["relay"]


def test_a_port_failure_mid_tick_keeps_what_was_done(tmp_path, relay_key):
    class FailingFlow(NoPorts):
        opened = 0

        def open_incident(self, title, description, at):
            FailingFlow.opened += 1
            return 7

        def start_watch_flow(self, incident, goal, at):
            raise RelayError("GitLab start the watch flow: HTTP 403")

    metrics = Metrics()
    for i in range(6):
        metrics.put("checkout_error_rate.new", local("03:07") + timedelta(minutes=i), 0.079)
    orders = parse_orders(load_yaml(DEMO / "orders.yml"), TARGETS, ONCALL)
    rig = Rig(tmp_path, QuietSources(orders=orders, signature=demo_signature(), metrics=metrics), FailingFlow())
    rig.now = local("03:12")
    response = rig.tick()
    assert response.status_code == 500 and "start the watch flow: HTTP 403" in response.json()["error"]
    # The incident was opened and recorded, so the next tick does not open a second one.
    assert [i["number"] for i in rig.doc()["watch"]["incidents"]] == [7]
    rig.now = local("03:13")
    rig.tick()
    assert FailingFlow.opened == 1


def test_settings_are_named_but_never_shown(monkeypatch):
    config = main.Config.from_env({"GITLAB_TOKEN": "fake-gitlab-token-for-tests", "RELAY_KEY": "k", "FLOW_CONSUMER_ID": "x7"})
    assert "fake-gitlab-token-for-tests" not in repr(config)
    problems = config.problems()
    assert "GITLAB_URL is not set" in problems and "FLOW_CONSUMER_ID must be a number" in problems
    assert not any("fake-gitlab-token" in p for p in problems)
    with pytest.raises(RelayError, match="STATE_BUCKET is required on Cloud Run"):
        main.make_store(main.Config.from_env({"K_SERVICE": "night-orders-relay"}))
