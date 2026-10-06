"""The relay's tick: one pass a minute through the night.

The same Watch runs in production (ports that talk to GitLab, Cloud Run and a push service)
and in the demo replay (ports that record what would have happened). Nothing here calls a
model directly: the model is the watch flow on GitLab, started through a port, and its only
output is a request note that code checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol

from .decide import (APPROVAL_WINDOW_MINUTES, Act, Ask, Night, StandDown, Waiting, Wake, approve_suggestion,
                     check_request, recheck, triage)
from .model import Action, Alert, Order, fmt_value
from .orders import watch_window
from .signals import Metrics, condition_holds
from .model import Condition


@dataclass(frozen=True)
class AlertRule:
    key: str
    for_minutes: int
    above: float | None = None
    below: float | None = None

    @property
    def condition(self) -> Condition:
        signal, _, path = self.key.partition(".")
        return Condition(signal=signal, path=path or None, above=self.above, below=self.below,
                         for_minutes=self.for_minutes)


def parse_alert_rules(data: dict) -> list[AlertRule]:
    return [
        AlertRule(key=str(r["key"]), for_minutes=int(r["for_minutes"]), above=r.get("above"), below=r.get("below"))
        for r in data.get("rules", [])
    ]


class Ports(Protocol):
    """Everything the watch does to the outside world."""

    def open_incident(self, title: str, description: str, at: datetime) -> int: ...
    def note(self, incident: int, text: str, at: datetime) -> None: ...
    def start_watch_flow(self, incident: int, goal: str, at: datetime) -> None: ...
    def request_note(self, incident: int, at: datetime) -> str | None: ...
    def apply(self, action: Action, at: datetime) -> None: ...
    def page(self, incident: int, lines: tuple[str, ...], at: datetime) -> None: ...
    def thumbs_up(self, incident: int, at: datetime) -> list[tuple[str, datetime]]: ...  # oldest first
    def close_incident(self, incident: int, text: str, at: datetime) -> None: ...


@dataclass
class Incident:
    number: int
    alerts: list[Alert]
    opened_at: datetime
    ask: Ask | None = None
    asked_at: datetime | None = None
    paged_at: datetime | None = None
    suggest: Action | None = None
    acted: Order | None = None
    acted_at: datetime | None = None
    closed: bool = False
    keys: set[str] = field(default_factory=set)


class Watch:
    def __init__(self, night: Night, ports: Ports, rules: list[AlertRule]):
        self.night = night
        self.ports = ports
        self.rules = rules
        self.incidents: list[Incident] = []
        self.expired = False

    # The order of steps matters: answers and re-checks for open incidents come before new alerts,
    # so a new alert during a re-check is seen as exactly that.
    def tick(self, metrics: Metrics, now: datetime) -> None:
        self._expire(now)
        for incident in self._open():
            self._answer(incident, metrics, now)
            self._recheck(incident, metrics, now)
            self._approval(incident, now)
            self._maybe_close(incident, metrics, now)
        self._new_alerts(metrics, now)

    def _open(self) -> list[Incident]:
        return [i for i in self.incidents if not i.closed]

    def _expire(self, now: datetime) -> None:
        orders = self.night.orders
        if self.expired or orders is None:
            return
        _, end = watch_window(orders, self.night.oncall)
        if now >= end:
            self.expired = True
            self.night.ledger.record(now, "expired", f"Tonight's orders ended at {self.night.oncall.hhmm(end)}.")

    def _firing(self, metrics: Metrics, now: datetime) -> list[Alert]:
        alerts = []
        for rule in self.rules:
            holds, _ = condition_holds(rule.condition, metrics, now)
            if holds:
                value = metrics.last_complete(rule.key, now)
                alerts.append(Alert(key=rule.key, value=value if value is not None else 0.0, at=now))
        return alerts

    def _new_alerts(self, metrics: Metrics, now: datetime) -> None:
        busy = set().union(*(i.keys for i in self._open())) if self._open() else set()
        fresh = [a for a in self._firing(metrics, now) if a.key not in busy]
        if not fresh:
            return
        ledger = self.night.ledger
        title = "Night watch: " + ", ".join(a.describe() for a in fresh)
        number = self.ports.open_incident(title, self._evidence(fresh, metrics, now), now)
        incident = Incident(number=number, alerts=fresh, opened_at=now, keys={a.key for a in fresh})
        self.incidents.append(incident)
        ledger.record(now, "alert", title, incident=number)

        decision = triage(fresh, self.night, metrics, now)
        if isinstance(decision, Wake):
            self._wake(incident, decision, now)
            return
        incident.ask, incident.asked_at = decision, now
        goal = (
            f"Incident #{number}. Signed orders whose numbers match right now: "
            + ", ".join(f"order {i} ({decision.checks[i]})" for i in decision.eligible)
            + ". Decide whether one of them fits the evidence. If unsure, choose none."
        )
        self.ports.start_watch_flow(number, goal, now)
        which = ", ".join(map(str, decision.eligible))
        noun = "order" if len(decision.eligible) == 1 else "orders"
        ledger.record(now, "asked", f"Asked the agent about {noun} {which}.", incident=number)

    def _evidence(self, alerts: list[Alert], metrics: Metrics, now: datetime) -> str:
        lines = ["Evidence pack (written by code).", ""]
        for key in metrics.keys():
            value = metrics.last_complete(key, now)
            if value is not None:
                lines.append(f"- {key}: {fmt_value(key.split('.')[0], value)}")
        return "\n".join(lines)

    def _answer(self, incident: Incident, metrics: Metrics, now: datetime) -> None:
        if incident.ask is None or incident.acted is not None or incident.paged_at is not None:
            return
        assert incident.asked_at is not None
        note = self.ports.request_note(incident.number, now)
        result = check_request(note, incident.ask, incident.asked_at, incident.alerts, self.night, metrics, now)
        ledger = self.night.ledger
        if isinstance(result, Waiting):
            return
        if isinstance(result, Wake):
            if result.reasons and result.reasons[0].startswith("The agent declined"):
                ledger.record(now, "declined", result.reasons[0], incident=incident.number)
            self._wake(incident, result, now)
            return
        if isinstance(result, StandDown):
            ledger.record(now, "stood_down", result.reason, incident=incident.number)
            self.ports.note(incident.number, result.reason, now)
            incident.ask = None
            return
        assert isinstance(result, Act)
        self.ports.apply(result.order.do, now)
        incident.acted, incident.acted_at = result.order, now
        text = (
            f"Order {result.order.id} carried out {self.night.oncall.hhmm(now)}: {result.order.do.describe()}. "
            f"Checks: {'; '.join(result.checks)}."
        )
        ledger.record(now, "acted", text, incident=incident.number, order=result.order.id,
                      action=result.order.do.as_dict())
        self.ports.note(incident.number, text, now)

    def _recheck(self, incident: Incident, metrics: Metrics, now: datetime) -> None:
        if incident.acted is None or incident.acted_at is None or incident.paged_at is not None:
            return
        ledger = self.night.ledger
        if any(e.kind == "recovered" and e.incident == incident.number for e in ledger.events):
            return
        if now < incident.acted_at + timedelta(minutes=self.night.oncall.recheck_minutes):
            return
        ok, detail = recheck(incident.acted, self.night, metrics, now)
        if ok:
            text = f"Re-check {self.night.oncall.hhmm(now)}: {detail}. No page."
            ledger.record(now, "recovered", text, incident=incident.number, order=incident.acted.id)
            self.ports.note(incident.number, text, now)
        else:
            reasons = (f"Order {incident.acted.id} ran but {detail}.",)
            page = (f"Order {incident.acted.id} ran at {self.night.oncall.hhmm(incident.acted_at)} but {detail}.",
                    "Nothing else is signed for this.", "The incident has the evidence.")
            self._wake(incident, Wake(reasons, page), now)

    def _approval(self, incident: Incident, now: datetime) -> None:
        if incident.suggest is None or incident.paged_at is None:
            return
        ledger = self.night.ledger
        for user, at in self.ports.thumbs_up(incident.number, now):
            ok, text = approve_suggestion(incident.suggest, user, at, incident.paged_at, self.night)
            if ok:
                self.ports.apply(incident.suggest, now)
                text = f"{text} Done {self.night.oncall.hhmm(now)}: {incident.suggest.describe()}."
                ledger.record(now, "approved", text, incident=incident.number, action=incident.suggest.as_dict())
                self.ports.note(incident.number, text, now)
                incident.suggest = None
                return
            # A reaction code refuses (a teammate's, say) is noted once, and the suggestion keeps waiting for
            # the on-call person.
            if not any(e.kind == "refused" and e.incident == incident.number and e.text == text
                       for e in ledger.events):
                ledger.record(now, "refused", text, incident=incident.number)
                self.ports.note(incident.number, text, now)
        if now >= incident.paged_at + timedelta(minutes=APPROVAL_WINDOW_MINUTES):
            text = (f"Nobody approved the suggestion within {APPROVAL_WINDOW_MINUTES} minutes of the page, "
                    "so it was dropped. Nothing was changed.")
            ledger.record(now, "refused", text, incident=incident.number)
            self.ports.note(incident.number, text, now)
            incident.suggest = None

    def _wake(self, incident: Incident, wake: Wake, now: datetime) -> None:
        incident.paged_at = now
        incident.suggest = wake.suggest
        lines = wake.page
        if wake.suggest is not None:
            lines = tuple(lines) + (f"Thumbs-up the note on #{incident.number} to: {wake.suggest.describe()}.",)
        self.ports.page(incident.number, tuple(lines), now)
        self.night.ledger.record(now, "woke", f"Woke {self.night.oncall.first_name}: {lines[0]}",
                                 incident=incident.number, page=list(lines), reasons=list(wake.reasons))

    def _maybe_close(self, incident: Incident, metrics: Metrics, now: datetime) -> None:
        if incident.ask is not None and incident.acted is None and incident.paged_at is None:
            return  # still waiting for the agent
        if incident.suggest is not None:
            return  # still waiting for a thumbs-up
        if incident.acted is not None and incident.paged_at is None:
            if not any(e.kind == "recovered" and e.incident == incident.number for e in self.night.ledger.events):
                return  # re-check not done yet
        quiet = all(
            not condition_holds(rule.condition, metrics, now)[0]
            for rule in self.rules if rule.key in incident.keys
        )
        latest_ok = all(
            (metrics.last_complete(rule.key, now) is not None
             and not rule.condition.breached_by(metrics.last_complete(rule.key, now)))  # type: ignore[arg-type]
            for rule in self.rules if rule.key in incident.keys
        )
        if quiet and latest_ok:
            incident.closed = True
            self.ports.close_incident(incident.number, f"Signals back to normal at {self.night.oncall.hhmm(now)}.", now)
