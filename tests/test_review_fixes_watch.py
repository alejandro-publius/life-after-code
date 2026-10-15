"""Fixes from the 11 Oct review of the night watch. Offline.

A page that fails is sent on the next tick; a stand-down cannot hide a live alert; an apply that fails after it
reached production leaves a loose end and wakes her; a failing apply cannot block the rest of the night; a flow the
Flows API refuses wakes her at once, and an ask that never went out is sent again. From the 14 Oct review: only a
failed change of the incident's own that may have gone through stops a stand-down.

Every time, name and number here is test data; the orders are the test night's orders (conftest.ORDERS).
"""

from __future__ import annotations

import dataclasses
import json
from datetime import timedelta

import pytest

from conftest import at, put, switched_off
from nightorders import Metrics, Request, render_request
from nightorders.dawn import loose_ends
from nightorders.model import Action, Change
from nightorders.state import capture, load_ledger, new_document, restore
from nightorders.watch import Watch
from test_standing_orders import bad_minutes, rules

NEW = "checkout_error_rate.new"
PAY = "payment_error_rate"
BEFORE = {"kind": "flag", "flag": "new_checkout", "environment": "production", "active": True,
          "strategies": [{"name": "default", "parameters": {}, "scopes": [{"environment_scope": "production"}]}]}
CACHE_BEFORE = {"kind": "flag", "flag": "stock_from_cache", "environment": "production", "active": False,
                "strategies": []}
FLAG_OFF = {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}
CACHE_ON = {"action": "flag_set", "flag": "stock_from_cache", "environment": "production", "to": "on"}


def reply(order: int | None = 1, declined: tuple[int, str] | None = None, page: tuple[str, ...] = (),
          suggest: dict | None = None) -> str:
    return render_request(Request(order=order, fits_because="Only the new path fails." if order else None,
                                  declined_id=declined[0] if declined else None,
                                  declined_why=declined[1] if declined else None, page=page, suggest=suggest))


class PortError(RuntimeError):
    """A port's failure, with what the port knows: before (the snapshot it read before it wrote), sent (False when
    nothing went out) and status (the HTTP status of a refusal). gitlab_ports raises errors with the same fields."""

    def __init__(self, text: str, before: dict | None = None, sent: bool = True, status: int | None = None):
        super().__init__(text)
        self.before, self.sent, self.status = before, sent, status


class Ports:
    """Records what the watch does. Each list of errors is raised by that call, one per call, before it works."""

    def __init__(self, reply: str | None = None, page_errors=(), apply_errors=(), flow_errors=(), reactions=None):
        self.reply = reply
        self.page_errors, self.apply_errors, self.flow_errors = list(page_errors), list(apply_errors), list(flow_errors)
        self.reactions = reactions or {}
        self.opened = 0
        self.flow_calls: list[int] = []
        self.started: list[int] = []
        self.tried: list[str] = []
        self.applied: list[str] = []
        self.notes: list[tuple[int, str]] = []
        self.pages: list[tuple[int, tuple[str, ...]]] = []
        self.closed: list[int] = []

    def saved(self):
        return {}

    def open_incident(self, title, description, at):
        self.opened += 1
        return self.opened

    def note(self, incident, text, at):
        self.notes.append((incident, text))

    def start_watch_flow(self, incident, goal, at):
        self.flow_calls.append(incident)
        error = self.flow_errors.pop(0) if self.flow_errors else None
        if error is None or getattr(error, "sent", True):
            self.started.append(incident)  # it went out; a timeout may still have started the flow
        if error is not None:
            raise error

    def request_note(self, incident, at):
        return self.reply if incident in self.started else None

    def apply(self, action, at):
        self.tried.append(action.describe())
        if self.apply_errors:
            raise self.apply_errors.pop(0)
        self.applied.append(action.describe())
        return Change(changed=True, before=BEFORE if action.flag == "new_checkout" else CACHE_BEFORE, detail="")

    def page(self, incident, lines, at):
        if self.page_errors:
            raise self.page_errors.pop(0)
        self.pages.append((incident, tuple(lines)))

    def thumbs_up(self, incident, at):
        return [(user, when) for user, when in self.reactions.get(incident, []) if when <= at]

    def close_incident(self, incident, text, at):
        self.closed.append(incident)


def tick_through(watch: Watch, metrics: Metrics, oncall, start: str, end: str) -> list[str]:
    """Tick every minute from start to end; the minutes whose tick raised, as HH:MM."""
    raised = []
    moment, last = at(oncall, start), at(oncall, end)
    while moment <= last:
        try:
            watch.tick(metrics, moment)
        except Exception:  # noqa: BLE001 (a failed tick, as the relay sees it)
            raised.append(oncall.hhmm(moment))
        moment += timedelta(minutes=1)
    return raised


def kinds(night) -> list[str]:
    return [e.kind for e in night.ledger.events]


# A1: a page that fails is kept and sent on the next tick, for every kind of wake.

PUSH_DOWN = PortError("push to the on-call phone: no answer within 10 s")


@pytest.mark.parametrize("wake", ["triage", "declined", "recheck"])
def test_a_page_that_fails_is_sent_on_the_next_tick_and_only_then_recorded(oncall, make_night, wake):
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    if wake == "triage":  # nothing signed: triage wakes her when the incident opens
        night, ports, standing, fails = make_night(signer=None), Ports(page_errors=[PUSH_DOWN]), False, "03:12"
    elif wake == "declined":  # the agent declines order 1 at 03:13
        ports = Ports(reply=reply(order=None, declined=(1, "Old path fails too."), page=("Checkout failing.",)),
                      page_errors=[PUSH_DOWN])
        night, standing, fails = make_night(), False, "03:13"
    else:  # standing orders act at 03:12; the re-check at 03:22 finds the whole shop still failing
        night, ports, standing, fails = make_night(), Ports(page_errors=[PUSH_DOWN]), True, "03:22"
        metrics = Metrics()
        bad_minutes(metrics, oncall, NEW, "03:07", 5, 0.079)
        switched_off(metrics, oncall, "03:12", 20, whole_rate=0.2)
    watch = Watch(night, ports, rules(), standing=standing)
    assert tick_through(watch, metrics, oncall, "03:12", fails) == [fails]
    incident = watch.incidents[0]
    assert incident.paged_at is None and "woke" not in kinds(night) and ports.pages == []

    # Cloud Run scales to zero between ticks: the next tick starts from the saved state document.
    doc = new_document("2026-10-20")
    capture(watch, doc)
    doc = json.loads(json.dumps(doc))
    again = Watch(dataclasses.replace(night, ledger=load_ledger(doc)), ports, rules(), standing=standing)
    restore(again, doc)
    sent = at(oncall, fails) + timedelta(minutes=1)
    again.tick(metrics, sent)

    assert len(ports.pages) == 1 and ports.opened == 1
    [woke] = again.night.ledger.of("woke")
    assert woke.at == sent and woke.data["page"] == list(ports.pages[0][1])
    assert again.incidents[0].paged_at == sent
    if wake == "declined":
        assert len(again.night.ledger.of("declined")) == 1
    tick_through(again, metrics, oncall, oncall.hhmm(sent + timedelta(minutes=1)), "03:40")
    assert len(ports.pages) == 1  # one page, never two


# A2: a stand-down can no longer leave an incident open with nobody paged.

def test_too_little_traffic_at_the_reply_wakes_her_with_the_triage_words(oncall, make_night):
    night, ports = make_night(), Ports(reply=reply(order=1))
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 5, 0.079)
    put(metrics, NEW, at(oncall, "03:12"), 0.5, count=2)  # one of two checkouts failed in the minute before the reply
    tick_through(watch, metrics, oncall, "03:12", "03:13")
    assert ports.applied == [] and night.ledger.of("stood_down") == []
    assert kinds(night) == ["alert", "asked", "woke"]
    reason = ("Order 1 matches the numbers, but only 2 checkouts a minute behind checkout error rate (new path), "
              "too few to judge (needs 10).")
    assert night.ledger.of("woke")[0].data["reasons"] == [reason]
    assert ports.pages == [(1, ("Checkout error rate (new path) at 7.9% since 03:12.", reason,
                                "The incident has the evidence."))]


def test_a_stand_down_while_the_alert_still_fires_wakes_her_after_the_orders_minutes(oncall, make_night):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 5, 0.079)
    put(metrics, NEW, at(oncall, "03:12"), 0.01)  # one good minute, so order 1's numbers no longer hold at the reply
    bad_minutes(metrics, oncall, NEW, "03:13", 30, 0.079)  # and then the new path fails again
    tick_through(watch, metrics, oncall, "03:12", "03:14")
    ports.reply = reply(order=1)  # the agent answers at 03:15
    tick_through(watch, metrics, oncall, "03:15", "03:19")
    [stood] = night.ledger.of("stood_down")
    assert stood.at == at(oncall, "03:15") and stood.text.endswith("Nothing was changed.")
    assert ports.pages == [] and ports.applied == [] and ports.closed == []
    tick_through(watch, metrics, oncall, "03:20", "03:40")  # order 1's for_minutes (5) after the stand-down
    reason = ("Order 1 stood down at 03:15 when its numbers dipped, but the signals are not back to normal "
              "5 minutes later.")
    assert ports.pages == [(1, ("Checkout error rate (new path) at 7.9% since 03:12.", reason,
                                "The incident has the evidence."))]
    assert night.ledger.of("woke")[0].at == at(oncall, "03:20")
    assert ports.opened == 1 and ports.applied == []


def test_a_stand_down_that_really_recovered_closes_without_a_page(oncall, make_night):
    night, ports = make_night(), Ports(reply=reply(order=1))
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 5, 0.079)
    bad_minutes(metrics, oncall, NEW, "03:12", 30, 0.01)
    tick_through(watch, metrics, oncall, "03:12", "03:40")
    assert kinds(night) == ["alert", "asked", "stood_down"] and ports.closed == [1] and ports.pages == []


# A3: an apply that raised keeps its snapshot, leaves a loose end, and never stands down as "nothing changed".

def test_a_failed_apply_keeps_its_snapshot_for_the_morning(oncall, make_night):
    timeout = PortError("GitLab set flag new_checkout: no answer within 10 s", before=BEFORE)
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[timeout])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    assert tick_through(watch, metrics, oncall, "03:12", "03:13") == ["03:13"]
    [failed] = night.ledger.of("failed")
    assert failed.data["action"] == FLAG_OFF and failed.data["before"] == BEFORE
    [end] = loose_ends(night)
    assert end.action.as_dict() == FLAG_OFF and end.before == BEFORE
    assert end.why == "order 1, 03:13, failed and may be in place"
    # Tried once more a minute later, it works: the loose end keeps the earliest snapshot.
    tick_through(watch, metrics, oncall, "03:14", "03:14")
    assert ports.applied == ["new_checkout off in production"]
    [end] = loose_ends(night)
    assert end.why == "order 1, 03:14" and end.before == BEFORE


def test_a_failed_apply_that_went_through_wakes_her_instead_of_standing_down(oncall, make_night):
    timeout = PortError("GitLab set flag new_checkout: no answer within 10 s", before=BEFORE)
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[timeout])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    switched_off(metrics, oncall, "03:13", 20)  # the PUT timed out, but GitLab had turned the flag off
    assert tick_through(watch, metrics, oncall, "03:12", "03:14") == ["03:13"]
    assert night.ledger.of("stood_down") == []
    [woke] = night.ledger.of("woke")
    assert woke.at == at(oncall, "03:14")
    assert woke.data["reasons"][0] == "Order 1 could not be carried out (GitLab set flag new_checkout: no answer within 10 s)."
    assert [end.before for end in loose_ends(night)] == [BEFORE]


def test_a_failed_approved_change_is_recorded_with_its_snapshot(oncall, make_night):
    down = PortError("GitLab set flag stock_from_cache: HTTP 502", before=CACHE_BEFORE)
    note = reply(order=None, declined=(1, "Old path fails too."), page=("Checkout failing.",), suggest=CACHE_ON)
    night = make_night()
    ports = Ports(reply=note, apply_errors=[down], reactions={1: [(night.oncall.user, at(oncall, "03:14"))]})
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    assert tick_through(watch, metrics, oncall, "03:12", "03:14") == ["03:14"]
    [failed] = night.ledger.of("failed")
    assert failed.text == ("The approved change, stock_from_cache on in production, could not be carried out "
                           "(GitLab set flag stock_from_cache: HTTP 502).")
    assert failed.data["action"] == CACHE_ON and failed.data["before"] == CACHE_BEFORE
    [end] = loose_ends(night)
    assert end.why == "approved by thumbs-up, 03:14, failed and may be in place" and end.before == CACHE_BEFORE
    tick_through(watch, metrics, oncall, "03:15", "03:15")  # the thumbs-up still stands: tried again, it works
    assert ports.applied == ["stock_from_cache on in production"]
    [end] = loose_ends(night)
    assert end.why == "approved by thumbs-up, 03:15" and end.before == CACHE_BEFORE


# A4: under the watch flow, a failing apply is tried once more, then wakes her; it never blocks other incidents.

def test_under_the_watch_flow_a_failing_apply_is_tried_once_more_then_wakes_her(oncall, make_night):
    down = PortError("GitLab set flag new_checkout: HTTP 502")
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[down] * 10)
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    assert tick_through(watch, metrics, oncall, "03:12", "03:20") == ["03:13", "03:14"]
    assert ports.applied == [] and len(ports.tried) == 2
    assert ports.pages == [(1, ("Checkout error rate (new path) at 7.9% since 03:12.",
                                "Order 1 could not be carried out (GitLab set flag new_checkout: HTTP 502).",
                                "The incident has the evidence."))]
    assert kinds(night) == ["alert", "asked", "failed", "failed", "woke"]


def test_an_incident_whose_apply_fails_does_not_stop_a_payment_alert_from_waking_her(oncall, make_night):
    down = PortError("GitLab set flag new_checkout: HTTP 502")
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[down] * 10)
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    bad_minutes(metrics, oncall, PAY, "03:08", 30, 0.08)
    watch.tick(metrics, at(oncall, "03:12"))
    with pytest.raises(PortError, match="HTTP 502"):  # the tick still counts as failed
        watch.tick(metrics, at(oncall, "03:13"))
    assert [(number, lines[1]) for number, lines in ports.pages] == [(2, "Payment errors always wake you.")]
    assert [e.incident for e in night.ledger.of("alert")] == [1, 2]


# A11 and C3: the watch flow that cannot start.

def test_a_flow_the_flows_api_refuses_to_start_wakes_her_at_once(oncall, make_night):
    refused = PortError("GitLab start the watch flow: HTTP 403 (403 Forbidden)", status=403)
    night, ports = make_night(), Ports(flow_errors=[refused])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    watch.tick(metrics, at(oncall, "03:12"))  # handled: she is woken, so the tick does not fail
    assert kinds(night) == ["alert", "asked", "woke"] and night.ledger.model_runs() == 1
    assert ports.pages == [(1, ("Checkout error rate (new path) at 7.9% since 03:12.",
                                "The watch flow could not be started (HTTP 403).", "The incident has the evidence."))]


def test_a_flow_start_that_timed_out_counts_and_waits_for_the_answer(oncall, make_night):
    slow = PortError("GitLab start the watch flow: no answer within 10 s")
    night, ports = make_night(), Ports(reply=reply(order=1), flow_errors=[slow])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    assert tick_through(watch, metrics, oncall, "03:12", "03:13") == ["03:12"]
    assert night.ledger.model_runs() == 1 and ports.flow_calls == [1]  # the flow started after all, and answered
    assert ports.applied == ["new_checkout off in production"] and ports.pages == []


def test_an_ask_that_never_went_out_is_sent_on_the_next_tick(oncall, make_night):
    skipped = PortError("GitLab start the watch flow: skipped, the tick ran out of time", sent=False)
    night, ports = make_night(), Ports(reply=reply(order=1), flow_errors=[skipped])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    assert tick_through(watch, metrics, oncall, "03:12", "03:12") == ["03:12"]
    assert night.ledger.model_runs() == 0 and watch.incidents[0].asked_at is None
    doc = new_document("2026-10-20")
    capture(watch, doc)
    doc = json.loads(json.dumps(doc))
    again = Watch(dataclasses.replace(night, ledger=load_ledger(doc)), ports, rules())
    restore(again, doc)
    assert tick_through(again, metrics, oncall, "03:13", "03:14") == []
    assert ports.flow_calls == [1, 1] and again.night.ledger.model_runs() == 1
    assert again.night.ledger.of("asked")[0].at == at(oncall, "03:13")
    assert ports.applied == ["new_checkout off in production"] and ports.pages == []


def test_an_unsent_ask_under_standing_orders_wakes_her_and_acts_on_nothing(oncall, make_night):
    skipped = PortError("GitLab start the watch flow: skipped, the tick ran out of time", sent=False)
    night, ports = make_night(), Ports(reply=reply(order=1), flow_errors=[skipped])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    tick_through(watch, metrics, oncall, "03:12", "03:12")
    watch.standing = True  # the relay was switched to standing orders before the next tick
    tick_through(watch, metrics, oncall, "03:13", "03:13")
    assert ports.applied == [] and ports.pages[0][1][1] == (
        "The relay switched to standing orders while the agent was being asked; nothing was done.")


def test_a_payment_alert_that_cannot_be_paged_does_not_lose_its_incident(oncall, make_night):
    night, ports = make_night(), Ports(page_errors=[PUSH_DOWN, PUSH_DOWN])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, PAY, "03:07", 30, 0.08)
    assert tick_through(watch, metrics, oncall, "03:12", "03:15") == ["03:12", "03:13"]
    assert ports.opened == 1 and len(ports.pages) == 1 and night.ledger.of("woke")[0].at == at(oncall, "03:14")


def test_loose_ends_skip_a_failure_with_no_snapshot_and_keep_the_earliest_one(make_night, oncall):
    night = make_night()
    ledger = night.ledger
    action = Action(kind="flag_set", flag="new_checkout", environment="production", to="off")
    ledger.record(at(oncall, "03:13"), "failed", "Order 1 could not be carried out (GitLab read flag: HTTP 502).",
                  incident=1, order=1, action=action.as_dict(), before=None)
    assert loose_ends(night) == []  # the flag was never read, so nothing was written
    ledger.record(at(oncall, "03:14"), "failed", "Order 1 could not be carried out (no answer within 10 s).",
                  incident=1, order=1, action=action.as_dict(), before=BEFORE)
    later = {**BEFORE, "strategies": []}
    ledger.record(at(oncall, "03:15"), "acted", "Order 1 carried out 03:15.", incident=1, order=1,
                  action=action.as_dict(), changed=False, before=later)
    [end] = loose_ends(night)  # the retry found it already off: the timed-out change had gone through
    assert end.before == BEFORE and end.why == "order 1, 03:15"  # it took, so it no longer says it may have failed


# 14 Oct review: a failure that wrote nothing, or another incident's, used to turn a stand-down into a page.

def test_a_change_the_tick_had_no_time_to_send_does_not_stop_a_stand_down(oncall, make_night):
    skipped = PortError("GitLab set flag new_checkout: skipped, the tick ran out of time", sent=False)
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[skipped])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    bad_minutes(metrics, oncall, NEW, "03:13", 30, 0.01)  # the numbers dip from 03:13 on
    assert tick_through(watch, metrics, oncall, "03:12", "03:14") == ["03:13"]
    assert loose_ends(night) == []  # nothing was written
    [stood] = night.ledger.of("stood_down")
    assert stood.at == at(oncall, "03:14") and stood.text.endswith("Nothing was changed.")
    assert ports.pages == [] and ports.applied == []


def test_another_incidents_failed_change_does_not_stop_a_stand_down(oncall, make_night):
    timeout = PortError("GitLab set flag new_checkout: no answer within 10 s", before=BEFORE)
    night, ports = make_night(), Ports(reply=reply(order=1), apply_errors=[timeout, timeout])
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 9, 0.079)  # incident 1: its change fails twice, she is woken at 03:15
    bad_minutes(metrics, oncall, NEW, "03:16", 10, 0.01)  # and it closes once the signals are back
    bad_minutes(metrics, oncall, NEW, "03:26", 5, 0.079)  # incident 2 opens at 03:31; order 1 has not run tonight
    bad_minutes(metrics, oncall, NEW, "03:31", 30, 0.01)  # and its numbers dip before the agent answers
    tick_through(watch, metrics, oncall, "03:12", "03:33")
    assert [number for number, _ in ports.pages] == [1]
    [stood] = night.ledger.of("stood_down")
    assert stood.incident == 2 and stood.text.endswith("Nothing was changed.")
    assert ports.closed == [1, 2]
