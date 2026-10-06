"""The night's record: what fired, what the agent asked, what code did, who was woken.

In production the relay keeps this as notes and timeline events on GitLab incidents, so the
record lives where the team already looks. Here it is a plain list, the same data in memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

KINDS = (
    "alert",      # an alert rule fired; an incident opened
    "asked",      # the watch flow was started for an incident
    "acted",      # code carried out a signed order
    "declined",   # the agent declined an order whose numbers matched
    "woke",       # the on-call person was paged
    "recovered",  # a re-check after an action found the signal back to normal
    "stood_down", # nothing to do any more (recovered before acting)
    "approved",   # the on-call person approved a suggestion with a thumbs-up
    "refused",    # code refused a request or an approval
    "expired",    # the orders ended at the watch end
)


@dataclass(frozen=True)
class Event:
    at: datetime
    kind: str
    text: str
    incident: int | None = None
    order: int | None = None
    data: dict = field(default_factory=dict)


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def record(self, at: datetime, kind: str, text: str, *, incident: int | None = None,
               order: int | None = None, **data) -> Event:
        if kind not in KINDS:
            raise ValueError(f"unknown ledger event kind: {kind}")
        event = Event(at=at, kind=kind, text=text, incident=incident, order=order, data=data)
        self.events.append(event)
        return event

    def of(self, kind: str) -> list[Event]:
        return [e for e in self.events if e.kind == kind]

    def used(self, order_id: int) -> bool:
        return any(e.kind == "acted" and e.order == order_id for e in self.events)

    def model_runs(self) -> int:
        return len(self.of("asked"))

    def pending_recheck(self) -> Event | None:
        """The latest action whose re-check has not finished (no recovery or page after it)."""
        for event in reversed(self.events):
            if event.kind != "acted":
                continue
            closed = any(
                e.kind in ("recovered", "woke") and e.incident == event.incident and e.at >= event.at
                for e in self.events
            )
            return None if closed else event
        return None

    def recheck_due(self, now: datetime, recheck_minutes: int) -> Event | None:
        """The pending action whose re-check time has come."""
        event = self.pending_recheck()
        if event and now >= event.at + timedelta(minutes=recheck_minutes):
            return event
        return None
