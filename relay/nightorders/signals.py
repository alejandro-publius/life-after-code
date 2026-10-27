"""Per-minute metrics and condition checks. Pure code: no model involved.

A sample for minute M is the value measured during that minute. At a tick at time T,
the last complete minute is T minus one minute, so a condition "for 5 minutes" looks at
the five complete minutes before T. Missing data never counts as a breach.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .model import Condition, count_noun, fmt_value


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
        """One dict lookup per minute of the window. The minutes are whole already, so get() would only
        normalise them again (a datetime.replace each); the series is read once instead."""
        end = minute(now)
        series = self._series.get(key)
        if not series:
            return [None] * minutes
        return [series.get(end - timedelta(minutes=i)) for i in range(minutes, 0, -1)]

    def keys(self) -> list[str]:
        return sorted(self._series)


def condition_holds(condition: Condition, metrics: Metrics, now: datetime) -> tuple[bool, str]:
    """Whether the condition held for every one of its last N complete minutes, and why.

    A condition with a min_count also needs that much traffic behind the number in every one of those
    minutes: one failed checkout out of two is 50%, and code does not act on that.
    """
    values = metrics.window(condition.key, now, condition.for_minutes)
    missing = sum(1 for v in values if v is None)
    if missing:
        return False, f"no data for {missing} of the last {condition.for_minutes} minutes of {condition.key}"
    if condition.min_count and condition.count_key:
        counts = metrics.window(condition.count_key, now, condition.for_minutes)
        if any(c is None for c in counts):
            return False, (f"no traffic count for {condition.label} in some of the last {condition.for_minutes} "
                           "minutes, so code cannot tell whether the number means anything")
        low = min(counts)  # type: ignore[type-var]
        if low < condition.min_count:  # type: ignore[operator]
            return False, (f"only {count_noun(condition.signal, low)} a minute behind {condition.label}, too few "
                           f"to judge (needs {condition.min_count})")
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
    if condition.breached_by(value):
        return False, f"{condition.label} still {shown} (limit {limit})"
    return True, f"{condition.label} back to {shown} (limit {limit})"


def whole_shop(condition: Condition) -> Condition | None:
    """The same condition on the whole shop, for a signal measured per path (checkout_error_rate.new ->
    checkout_error_rate.all). None when the condition already covers the whole shop."""
    if condition.path in (None, "all"):
        return None
    return Condition(signal=condition.signal, for_minutes=condition.for_minutes, path="all", above=condition.above,
                     below=condition.below, min_count=condition.min_count)


def recheck_after_action(condition: Condition, metrics: Metrics, now: datetime) -> tuple[bool, str]:
    """The re-check ten minutes after an order ran. It cannot grade itself on an emptied path.

    Turning a checkout path off empties it, and an empty path reads 0% errors. So the order's own signal
    passes when it is back on the safe side or carries too little traffic to judge (it was switched off),
    and then the whole shop must be back on the safe side too, on enough checkouts to mean something.
    Without counts (a condition with no min_count), only the order's own signal is judged, as before.
    """
    own_ok, own = recovered(condition, metrics, now)
    if not condition.min_count or not condition.count_key:
        return own_ok, own
    count = metrics.last_complete(condition.count_key, now)
    limit = fmt_value(condition.signal, condition.threshold)
    emptied = count is not None and count < condition.min_count
    whole = whole_shop(condition)
    if count is None:
        return False, f"no traffic count for {condition.label} in the last minute, so recovery cannot be confirmed"
    if emptied and whole is None:
        return False, (f"{condition.label} had {count_noun(condition.signal, count)} in the last minute, too few to "
                       "confirm it recovered")
    if not emptied and not own_ok:
        return False, own
    if emptied:
        mine = f"the {condition.path} path carries {count_noun(condition.signal, count)} now"
    else:
        value = metrics.last_complete(condition.key, now)
        mine = (f"{condition.label} back to {fmt_value(condition.signal, value or 0.0)} on "
                f"{count_noun(condition.signal, count)} (limit {limit})")
    if whole is None:
        return True, mine
    whole_value = metrics.last_complete(whole.key, now)
    whole_count = metrics.last_complete(whole.count_key, now) if whole.count_key else None
    if whole_value is None:
        return False, f"no data for {whole.key} in the last minute, though {mine}"
    shown = fmt_value(whole.signal, whole_value)
    if whole.breached_by(whole_value):
        return False, f"{whole.label} still {shown} (limit {limit}), though {mine}"
    if whole_count is None or whole_count < (whole.min_count or 0):
        return False, (f"the whole shop had {count_noun(whole.signal, whole_count)} in the last minute, too few to "
                       f"confirm it recovered, though {mine}")
    return True, f"{mine}; {whole.label} back to {shown} on {count_noun(whole.signal, whole_count)} (limit {limit})"
