"""Per-minute signals for the relay: checkout error rate per path, 5xx ratio, p95 latency, payment errors.

Kept in memory only. Cloud Run may scale the shop to zero between demo nights; the counters then start
again from empty, and minutes before the start are not reported at all (no data, rather than invented zeros).
A request counts in the minute it finishes, so a minute that has ended never changes again.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

PATHS = ("old", "new")
REPORT_MINUTES = 60
MAX_SAMPLES = 5000  # latency samples kept per minute, so a flood of requests cannot use up memory


def floor_minute(at: datetime) -> datetime:
    return at.astimezone(timezone.utc).replace(second=0, microsecond=0)


def iso_minute(at: datetime) -> str:
    return floor_minute(at).strftime("%Y-%m-%dT%H:%M:00Z")


def rate(errors: int, requests: int) -> float:
    return round(errors / max(requests, 1), 4)


def p95(samples: list[float]) -> float:
    """Nearest-rank 95th percentile. 0.0 for a minute without checkouts."""
    if not samples:
        return 0.0
    ordered = sorted(samples)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


@dataclass
class Minute:
    checkouts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(PATHS, 0))
    failed: dict[str, int] = field(default_factory=lambda: dict.fromkeys(PATHS, 0))
    latencies_ms: list[float] = field(default_factory=list)
    requests: int = 0
    server_errors: int = 0
    payments: int = 0
    payment_errors: int = 0

    def signals(self) -> dict[str, float]:
        """The keys the relay reads, with rates as errors / max(requests, 1)."""
        return {
            "checkout_error_rate.old": rate(self.failed["old"], self.checkouts["old"]),
            "checkout_error_rate.new": rate(self.failed["new"], self.checkouts["new"]),
            "checkout_error_rate.all": rate(sum(self.failed.values()), sum(self.checkouts.values())),
            "http_5xx_ratio": rate(self.server_errors, self.requests),
            "p95_latency_ms": round(p95(self.latencies_ms), 1),
            "payment_error_rate": rate(self.payment_errors, self.payments),
        }


class Metrics:
    def __init__(self, clock: Callable[[], datetime]) -> None:
        self._clock = clock
        self.started = floor_minute(clock())
        self._minutes: dict[datetime, Minute] = {}

    def _current(self) -> Minute:
        at = floor_minute(self._clock())
        bucket = self._minutes.get(at)
        if bucket is None:
            bucket = self._minutes[at] = Minute()
            cutoff = at - timedelta(minutes=REPORT_MINUTES + 1)
            for old in [m for m in self._minutes if m < cutoff]:
                del self._minutes[old]
        return bucket

    def http(self, status: int) -> None:
        bucket = self._current()
        bucket.requests += 1
        if status >= 500:
            bucket.server_errors += 1

    def checkout(self, path: str, ok: bool, latency_ms: float) -> None:
        if path not in PATHS:
            raise ValueError(f"unknown checkout path {path!r}")
        bucket = self._current()
        bucket.checkouts[path] += 1
        if not ok:
            bucket.failed[path] += 1
        if len(bucket.latencies_ms) < MAX_SAMPLES:
            bucket.latencies_ms.append(latency_ms)

    def payment(self, ok: bool) -> None:
        bucket = self._current()
        bucket.payments += 1
        if not ok:
            bucket.payment_errors += 1

    def complete(self, count: int = REPORT_MINUTES) -> list[tuple[datetime, Minute]]:
        """The last `count` minutes that have ended, oldest first, since this process started."""
        now = floor_minute(self._clock())
        at = max(self.started, now - timedelta(minutes=count))
        out = []
        while at < now:
            out.append((at, self._minutes.get(at) or Minute()))
            at += timedelta(minutes=1)
        return out

    def report(self) -> list[dict]:
        """The body of /metrics.json: one entry per complete minute, at most the last 60."""
        return [{"at": iso_minute(at), **bucket.signals()} for at, bucket in self.complete()]
