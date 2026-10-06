"""Per-minute metrics and condition checks. Pure code: no model involved.

A sample for minute M is the value measured during that minute. At a tick at time T,
the last complete minute is T minus one minute, so a condition "for 5 minutes" looks at
the five complete minutes before T. Missing data never counts as a breach.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .model import Condition, fmt_value


def minute(moment: datetime) -> datetime:
    return moment.replace(second=0, microsecond=0)


class Metrics:
    """Per-minute samples keyed by metric key, for example checkout_error_rate.new."""

    def __init__(self, series: dict[str, dict[datetime, float]] | None = None):
        self._series: dict[str, dict[datetime, float]] = {}
        for key, samples in (series or {}).items():
            for at, value in samples.items():
                self.put(key, at, value)

    def put(self, key: str, at: datetime, value: float) -> None:
        self._series.setdefault(key, {})[minute(at)] = float(value)

    def get(self, key: str, at: datetime) -> float | None:
        return self._series.get(key, {}).get(minute(at))

    def last_complete(self, key: str, now: datetime) -> float | None:
        return self.get(key, minute(now) - timedelta(minutes=1))

    def window(self, key: str, now: datetime, minutes: int) -> list[float | None]:
        end = minute(now)
        return [self.get(key, end - timedelta(minutes=i)) for i in range(minutes, 0, -1)]

    def keys(self) -> list[str]:
        return sorted(self._series)


def condition_holds(condition: Condition, metrics: Metrics, now: datetime) -> tuple[bool, str]:
    """Whether the condition held for every one of its last N complete minutes, and why."""
    values = metrics.window(condition.key, now, condition.for_minutes)
    missing = sum(1 for v in values if v is None)
    if missing:
        return False, f"no data for {missing} of the last {condition.for_minutes} minutes of {condition.key}"
    breached = [v for v in values if condition.breached_by(v)]  # type: ignore[arg-type]
    latest = values[-1]
    shown = fmt_value(condition.signal, latest)  # type: ignore[arg-type]
    limit = fmt_value(condition.signal, condition.threshold)
    word = "above" if condition.above is not None else "below"
    label = condition.signal.replace("_", " ") + (f" ({condition.path} path)" if condition.path else "")
    if len(breached) == len(values):
        return True, f"{label} {shown}, {word} {limit} for {condition.for_minutes} min"
    return False, f"{label} {shown}, not {word} {limit} for all of the last {condition.for_minutes} min"


def recovered(condition: Condition, metrics: Metrics, now: datetime) -> tuple[bool, str]:
    """After an action: is the last complete minute back on the safe side of the threshold?"""
    value = metrics.last_complete(condition.key, now)
    if value is None:
        return False, f"no data for {condition.key} in the last minute"
    shown = fmt_value(condition.signal, value)
    limit = fmt_value(condition.signal, condition.threshold)
    label = condition.signal.replace("_", " ") + (f" ({condition.path} path)" if condition.path else "")
    if condition.breached_by(value):
        return False, f"{label} still {shown} (limit {limit})"
    return True, f"{label} back to {shown} (limit {limit})"
