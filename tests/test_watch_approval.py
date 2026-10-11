"""The thumbs-up after a page, as the Watch handles it over several ticks."""

from __future__ import annotations

from conftest import OPS, at
from nightorders import Action, Change, Metrics
from nightorders.orders import load_yaml
from nightorders.watch import Incident, Watch, parse_alert_rules

FALLBACK = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")


class ReactionPorts:
    """Serves the thumbs-up reactions visible at each moment, and records what the Watch does."""

    def __init__(self, reactions, already_on: bool = False):
        self.reactions, self.applied, self.notes, self.closed = reactions, [], [], []
        self.already_on = already_on

    def thumbs_up(self, incident, at):
        return [r for r in self.reactions if r[1] <= at]

    def apply(self, action, at):
        self.applied.append(action.describe())
        before = {"kind": "flag", "flag": action.flag, "environment": action.environment,
                  "value": "on" if self.already_on else "off"}
        return Change(changed=not self.already_on, before=before, detail="")

    def note(self, incident, text, at):
        self.notes.append(text)

    def close_incident(self, incident, text, at):
        self.closed.append(incident)


def paged(make_night, oncall, reactions, already_on: bool = False):
    """An incident paged at 01:52 on the old-path alert. The ticks pass no metrics, so its signal never reads as
    recovered and the incident stays open with its suggestion (a recovered one would drop it)."""
    night = make_night()
    ports = ReactionPorts(reactions, already_on)
    watch = Watch(night, ports, rules=parse_alert_rules(load_yaml(OPS / "alerts.yml")))
    watch.incidents.append(Incident(number=1, alerts=[], opened_at=at(oncall, "01:50"),
                                    paged_at=at(oncall, "01:52"), suggest=FALLBACK,
                                    keys={"checkout_error_rate.old"}))
    return watch, ports, night


def test_a_teammates_thumbs_up_is_refused_once_and_the_on_call_person_can_still_approve(make_night, oncall):
    watch, ports, night = paged(make_night, oncall, [("teammate", at(oncall, "01:53")),
                                                     ("alex-velazquez", at(oncall, "01:56"))])
    watch.tick(Metrics(), at(oncall, "01:54"))
    watch.tick(Metrics(), at(oncall, "01:55"))
    assert ports.applied == []
    assert [(e.kind, e.text) for e in night.ledger.events] == [
        ("refused", "The reaction came from teammate, not the on-call person.")]
    watch.tick(Metrics(), at(oncall, "01:57"))
    assert ports.applied == ["stock_from_cache on in production"]
    assert [e.kind for e in night.ledger.events] == ["refused", "approved"]
    assert ports.notes[-1] == "Approved by Priya at 01:56. Done 01:57: stock_from_cache on in production."
    approved = night.ledger.events[-1]
    assert approved.data["changed"] is True
    assert approved.data["before"] == {"kind": "flag", "flag": "stock_from_cache", "environment": "production",
                                       "value": "off"}


def test_an_approved_change_that_was_already_in_place_is_recorded_as_a_no_op(make_night, oncall):
    watch, ports, night = paged(make_night, oncall, [("alex-velazquez", at(oncall, "01:56"))], already_on=True)
    watch.tick(Metrics(), at(oncall, "01:57"))
    assert ports.applied == ["stock_from_cache on in production"]
    assert ports.notes[-1] == ("Approved by Priya at 01:56. Done 01:57: stock_from_cache on in production. "
                               "(already in place, nothing changed)")
    approved = night.ledger.events[-1]
    assert approved.kind == "approved" and approved.data["changed"] is False
    assert approved.text.endswith(" (already in place, nothing changed)")


def test_an_unapproved_suggestion_is_dropped_after_the_window(make_night, oncall):
    watch, ports, night = paged(make_night, oncall, [])
    watch.tick(Metrics(), at(oncall, "02:51"))
    assert watch.incidents[0].suggest == FALLBACK
    watch.tick(Metrics(), at(oncall, "02:52"))
    assert watch.incidents[0].suggest is None and ports.applied == []
    assert night.ledger.events[-1].text.startswith("Nobody approved the suggestion within 60 minutes")
