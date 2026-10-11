"""Plain data types shared by the night-orders core.

Everything here is immutable. Times are timezone-aware datetimes; local times
for display come from the on-call person's time zone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Literal
from zoneinfo import ZoneInfo

RATE_SIGNALS = ("checkout_error_rate", "http_5xx_ratio", "payment_error_rate")


def fmt_value(signal: str, value: float) -> str:
    """Format a signal value the way a sleepy person reads it."""
    if signal in RATE_SIGNALS:
        return f"{value * 100:.1f}%"
    return f"{value:,.0f} ms"


@dataclass(frozen=True)
class Condition:
    signal: str
    for_minutes: int
    path: str | None = None
    above: float | None = None
    below: float | None = None

    @property
    def key(self) -> str:
        """Metric key, for example checkout_error_rate.new."""
        return f"{self.signal}.{self.path}" if self.path else self.signal

    @property
    def threshold(self) -> float:
        return self.above if self.above is not None else self.below  # type: ignore[return-value]

    def breached_by(self, value: float) -> bool:
        if self.above is not None:
            return value > self.above
        return value < self.below  # type: ignore[operator]

    def describe(self) -> str:
        what = self.signal.replace("_", " ")
        if self.path:
            what += f" ({self.path} path)"
        word = "above" if self.above is not None else "below"
        return f"{what} {word} {fmt_value(self.signal, self.threshold)} for {self.for_minutes} min"


@dataclass(frozen=True)
class Action:
    kind: Literal["flag_set", "traffic_to_revision"]
    flag: str | None = None
    environment: str | None = None
    to: Literal["off", "on"] | None = None
    service: str | None = None
    revision: str | None = None

    def describe(self) -> str:
        if self.kind == "flag_set":
            return f"{self.flag} {self.to} in {self.environment}"
        return f"{self.service} traffic to revision {self.revision}"

    def same_target(self, other: "Action") -> bool:
        if self.kind != other.kind:
            return False
        if self.kind == "flag_set":
            return (self.flag, self.environment) == (other.flag, other.environment)
        return self.service == other.service

    def as_dict(self) -> dict:
        if self.kind == "flag_set":
            return {"action": "flag_set", "flag": self.flag, "environment": self.environment, "to": self.to}
        return {"action": "traffic_to_revision", "service": self.service, "revision": self.revision}


@dataclass(frozen=True)
class Change:
    """What one action did to its target: whether anything changed, a JSON-safe snapshot of the target
    from before the action, and plain words. The morning restores from the snapshot, never by guessing."""

    changed: bool
    before: dict | None
    detail: str


def describe_before(before: dict | None) -> str:
    """A snapshot in plain words, for example "on for 10 listed users" or "100% to the latest revision"."""
    if not before:
        return "unknown"
    if before.get("kind") == "traffic":
        targets = [t for t in before.get("traffic") or [] if isinstance(t, dict) and t.get("percent")]
        if not targets:
            return "no traffic allocation recorded"
        return ", ".join(
            f"{t.get('percent')}% to "
            + (f"revision {t['revision']}" if t.get("revision") else "the latest revision") for t in targets)
    if "value" in before:
        return str(before["value"])
    strategies = before.get("strategies") or []
    if not before.get("active") or not strategies:
        return "off"
    return " and ".join(_strategy_words(s) for s in strategies)


def _strategy_words(strategy: dict) -> str:
    name = strategy.get("name")
    parameters = strategy.get("parameters") or {}
    if name == "default":
        return "on for every user"
    if name == "userWithId":
        count = len([u for u in str(parameters.get("userIds", "")).split(",") if u.strip()])
        if count == 0:
            return "on for nobody (empty user list)"
        return f"on for {count} listed user{'s' if count != 1 else ''}"
    if name == "gradualRolloutUserId":
        return f"on for {parameters.get('percentage', '?')}% of users"
    if name == "flexibleRollout":
        return f"on for {parameters.get('rollout', '?')}% of page views"
    if name == "gitlabUserList":
        return "on for a user list"
    return f"on by the {name} strategy"


@dataclass(frozen=True)
class Order:
    id: int
    because: str
    when: Condition
    do: Action


@dataclass(frozen=True)
class Orders:
    night: date
    expires: time
    orders: tuple[Order, ...]
    drafted_by: str | None = None

    def get(self, order_id: int) -> Order | None:
        for order in self.orders:
            if order.id == order_id:
                return order
        return None


@dataclass(frozen=True)
class Signature:
    """Who signed tonight's orders, and how. Read from GitLab, never from the orders file."""

    method: Literal["merge", "approval"]
    user: str
    at: datetime
    commit: str


@dataclass(frozen=True)
class OnCall:
    user: str
    display_name: str
    timezone: ZoneInfo
    watch_ends: time
    recheck_minutes: int = 10
    answer_timeout_minutes: int = 8
    model_runs_per_night: int = 3

    @property
    def first_name(self) -> str:
        return self.display_name.split(" ")[0]

    def local(self, moment: datetime) -> datetime:
        return moment.astimezone(self.timezone)

    def hhmm(self, moment: datetime) -> str:
        return self.local(moment).strftime("%H:%M")


@dataclass(frozen=True)
class Targets:
    flags: dict[str, frozenset[str]]
    services: dict[str, str]
    signals: dict[str, frozenset[str]]
    always_wake: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Alert:
    """A signal that crossed an alert rule. One incident groups the alerts of one tick."""

    key: str
    value: float
    at: datetime

    @property
    def signal(self) -> str:
        return self.key.split(".", 1)[0]

    def describe(self) -> str:
        signal = self.signal
        path = self.key.split(".", 1)[1] if "." in self.key else None
        what = signal.replace("_", " ") + (f" ({path} path)" if path else "")
        return f"{what} at {fmt_value(signal, self.value)}"
