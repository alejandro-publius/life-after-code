"""Standing Orders: the fallback night without a model. Code's key alone turns, and the record says so.

Every time, name and number here is test data; the demo night is labelled demo data.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from conftest import OPS, REPO, at, put, series, switched_off
from nightorders import Act, Alert, Ask, Change, Metrics, Request, render_request, standing_order, triage
from nightorders import demo_night
from nightorders.decide import STANDING
from nightorders.orders import load_yaml, parse_orders
from nightorders.watch import Watch, parse_alert_rules
from test_relay_app import (FULL_SETTINGS, ONCALL, TARGETS, Rig, QuietSources, ThroughTheRelay, demo_signature,
                            local, main, relay_key)  # noqa: F401  (relay_key is a fixture)

NEW = "checkout_error_rate.new"
OLD = "checkout_error_rate.old"
DEMO = REPO / "demo" / "night-2026-10-20"


class Ports:
    """Records what the watch does. request_note serves one recorded reply, if given."""

    def __init__(self, reply: str | None = None):
        self.reply = reply
        self.started: list[tuple[int, str]] = []
        self.applied: list[str] = []
        self.notes: list[str] = []
        self.pages: list[tuple[str, ...]] = []
        self.closed: list[int] = []

    def saved(self):
        return {}

    def open_incident(self, title, description, at):
        return 1

    def note(self, incident, text, at):
        self.notes.append(text)

    def start_watch_flow(self, incident, goal, at):
        self.started.append((incident, goal))

    def request_note(self, incident, at):
        return self.reply if self.started else None

    def apply(self, action, at):
        self.applied.append(action.describe())
        return Change(changed=True, before={"kind": "flag", "flag": action.flag, "environment": action.environment,
                                            "active": True, "strategies": [{"name": "default", "parameters": {}}]},
                      detail="")

    def page(self, incident, lines, at):
        self.pages.append(tuple(lines))

    def thumbs_up(self, incident, at):
        return []

    def close_incident(self, incident, text, at):
        self.closed.append(incident)


def rules():
    return parse_alert_rules(load_yaml(OPS / "alerts.yml"))


def bad_minutes(metrics: Metrics, oncall, key: str, start: str, minutes: int, value: float, count: int = 30) -> None:
    first = at(oncall, start)
    for i in range(minutes):
        put(metrics, key, first + timedelta(minutes=i), value, count)


# The decision.

def test_a_standing_order_is_the_first_eligible_order_with_the_same_checks_and_a_plain_warning(oncall, make_night):
    night = make_night()
    metrics = series(oncall, NEW, "03:07", [0.079] * 6)
    decision = triage([Alert(key=NEW, value=0.079, at=at(oncall, "03:12"))], night, metrics, at(oncall, "03:12"))
    assert isinstance(decision, Ask)
    result = standing_order(decision, night)
    assert isinstance(result, Act) and result.order.id == 1
    assert result.checks == (
        "signed by Priya at 22:06 (merge)",
        "not expired (ends 07:00)",
        "checkout error rate (new path) 7.9%, above 5.0% for 5 min",
        "action and target taken from the signed file",
        "first use tonight",
        STANDING,
    )
    assert "no model tonight" in STANDING


# The watch.

def test_under_standing_orders_no_flow_starts_and_the_order_runs_at_the_first_eligible_tick(oncall, make_night):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    for hhmm in ("03:08", "03:09", "03:10", "03:11"):
        watch.tick(metrics, at(oncall, hhmm))
    assert ports.applied == [] and ports.started == []  # fewer than five bad minutes: nothing fires yet
    watch.tick(metrics, at(oncall, "03:12"))
    assert ports.started == []
    assert ports.applied == ["new_checkout off in production"]
    assert [e.kind for e in night.ledger.events] == ["alert", "acted"]
    acted = night.ledger.events[-1]
    assert acted.order == 1 and acted.data["before"]["strategies"] == [{"name": "default", "parameters": {}}]
    assert ports.notes[-1].startswith("Order 1 carried out 03:12: new_checkout off in production. Checks: ")
    assert ports.notes[-1].endswith(f"first use tonight; {STANDING}.")
    assert night.ledger.model_runs() == 0 and watch.incidents[0].ask is None
    # One order runs once: the same alert later tonight wakes her instead.
    assert night.ledger.used(1)


def test_under_standing_orders_everything_code_refuses_still_wakes(oncall, make_night):
    night, ports = make_night(signer=None), Ports()
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    watch.tick(metrics, at(oncall, "03:12"))
    assert ports.applied == [] and ports.started == []
    assert ports.pages == [("Checkout error rate (new path) at 7.9% since 03:12.", "Nobody signed tonight's orders.",
                            "The incident has the evidence.")]
    assert [e.kind for e in night.ledger.events] == ["alert", "woke"]


@pytest.mark.parametrize("standing", [True, False])
def test_the_re_check_wakes_when_another_alert_of_the_incident_still_fires(oncall, make_night, standing):
    """Both paths fail. Order 1 turns the new path off, so its own signal falls to zero (no traffic), but the
    old path is still failing: the action did not help, and the re-check says so instead of "No page"."""
    reply = render_request(Request(order=1, fits_because="Errors on the new path.", declined_id=None,
                                   declined_why=None, page=(), suggest=None))
    night, ports = make_night(), Ports(reply=None if standing else reply)
    watch = Watch(night, ports, rules(), standing=standing)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "01:45", 6, 0.204)
    bad_minutes(metrics, oncall, OLD, "01:45", 20, 0.203)
    watch.tick(metrics, at(oncall, "01:50"))
    if not standing:
        assert ports.started and ports.applied == []
        watch.tick(metrics, at(oncall, "01:51"))  # the reply arrives, code checks it, the order runs
    acted_at = "01:50" if standing else "01:51"
    assert ports.applied == ["new_checkout off in production"]
    # the whole shop still fails as much as the old path, which now carries every checkout
    switched_off(metrics, oncall, acted_at, 12, whole_rate=0.203)
    for minute in range(1, 11):
        watch.tick(metrics, at(oncall, acted_at) + timedelta(minutes=minute))
    assert ports.pages == [(
        f"Order 1 ran at {acted_at} but checkout error rate (whole shop) still 20.3% (limit 5.0%), though the new "
        "path carries no checkouts now.",
        "Nothing else is signed for this.", "The incident has the evidence.")]
    kinds = [e.kind for e in night.ledger.events]
    assert kinds == (["alert", "acted", "woke"] if standing else ["alert", "asked", "acted", "woke"])
    assert not any("No page" in n for n in ports.notes)


def test_the_re_check_still_says_no_page_when_the_incident_fired_on_the_order_signal_alone(oncall, make_night):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    bad_minutes(metrics, oncall, OLD, "03:07", 20, 0.004)
    watch.tick(metrics, at(oncall, "03:12"))
    assert ports.applied == ["new_checkout off in production"]
    switched_off(metrics, oncall, "03:12", 12, whole_rate=0.004)
    for minute in range(1, 11):
        watch.tick(metrics, at(oncall, "03:12") + timedelta(minutes=minute))
    assert ports.pages == []
    assert ports.notes[-1] == ("Re-check 03:22: the new path carries no checkouts now; checkout error rate (whole shop) "
                               "back to 0.4% on 60 checkouts (limit 5.0%). No page.")
    assert ports.closed == [1]


# The demo night, replayed without its recorded agent replies.

def test_the_demo_night_under_standing_orders_acts_on_the_numbers_and_the_re_check_wakes_her():
    ports, night = demo_night.run(DEMO, standing=True)
    log = "\n".join(ports.log)
    assert "recorded watch reply requested" not in log and "agent note" not in log
    assert "01:50  APPLY new_checkout off in production" in log
    assert f"first use tonight; {STANDING}." in log
    assert "02:00  PAGE (phone lights up) for #1: Order 1 ran at 01:50 but checkout error rate (whole shop) still" in log
    assert [e.kind for e in night.ledger.events] == ["alert", "acted", "woke", "expired"]
    # With the new checkout already off, the 03:07 rounding bug never reaches a customer: no second incident.
    assert "incident #2" not in log
    plain_ports, _ = demo_night.run(DEMO)
    assert "03:13  APPLY new_checkout off in production" in "\n".join(plain_ports.log)  # the model night is unchanged


def test_the_demo_night_cli_takes_a_standing_flag(capsys):
    assert demo_night.main([str(DEMO), "--standing"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("DEMO NIGHT under STANDING ORDERS (demo data, planted faults, no agent). Real decision code.")
    assert "Woken: 1 time (02:00)." in out


# The relay.

def test_standing_mode_needs_no_flow_settings_and_refuses_an_unknown_mode():
    without_flow = {k: v for k, v in FULL_SETTINGS.items() if k not in ("FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT")}
    assert main.Config.from_env(without_flow).problems() == ["FLOW_CONSUMER_ID is not set",
                                                              "FLOW_SERVICE_ACCOUNT is not set"]
    standing = main.Config.from_env({**without_flow, "WATCH_MODE": "standing"})
    assert standing.problems() == [] and standing.standing is True
    assert main.Config.from_env({**FULL_SETTINGS, "WATCH_MODE": "flow"}).standing is False
    assert main.Config.from_env({**FULL_SETTINGS, "WATCH_MODE": "nightly"}).problems() == [
        "WATCH_MODE must be one of flow, standing"]


def test_a_standing_relay_acts_without_a_flow_and_says_so_on_its_status_page(tmp_path, relay_key):
    orders = parse_orders(load_yaml(DEMO / "orders.yml"), TARGETS, ONCALL)
    metrics = Metrics()
    bad_minutes(metrics, ONCALL, NEW, "03:07", 6, 0.079)
    ports = Ports()
    rig = Rig(tmp_path, QuietSources(orders=orders, signature=demo_signature(), metrics=metrics), ports,
              standing=True)
    rig.now = local("03:12")
    summary = rig.tick().json()
    assert summary["mode"] == "standing" and summary["orders"] == "active until 07:00"
    assert ports.started == [] and ports.applied == ["new_checkout off in production"]
    assert summary["events"][1].startswith("acted: Order 1 carried out 03:12")  # the summary line is cut at 240
    assert rig.doc()["watch"]["ledger"][1]["text"].endswith(f"first use tonight; {STANDING}.")
    page = rig.client.get("/").text
    assert "Standing orders tonight." in page and "No model at night" in page
    assert rig.doc()["relay"]["status"]["standing"] is True


def test_the_demo_night_through_a_standing_relay_matches_the_in_memory_replay(tmp_path_factory, monkeypatch):
    plain_ports, plain_night = demo_night.run(DEMO, standing=True)
    ThroughTheRelay.tmp_path = tmp_path_factory.mktemp("standing-relay")
    monkeypatch.setenv("RELAY_KEY", "test-relay-key")
    monkeypatch.setattr(demo_night, "Watch", ThroughTheRelay)
    relay_ports, _ = demo_night.run(DEMO, standing=True)
    rig = ThroughTheRelay.rig
    assert relay_ports.log == plain_ports.log
    assert all(s["mode"] == "standing" for s in rig.summaries)
    saved = [(e["kind"], e["text"]) for e in rig.doc()["watch"]["ledger"]]
    assert saved == [(e.kind, e.text) for e in plain_night.ledger.events]
    assert "Standing orders tonight." in rig.client.get("/").text
