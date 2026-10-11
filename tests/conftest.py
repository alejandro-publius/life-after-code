"""Shared helpers. Every time and name here is test data."""

from __future__ import annotations

import copy
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from nightorders import Ledger, Metrics, Night, Signature, parse_oncall, parse_orders, parse_targets
from nightorders.orders import load_yaml

REPO = Path(__file__).resolve().parents[1]
OPS = REPO / "ops"

ORDERS = {
    "night": "2026-10-20",
    "expires": "07:00",
    "orders": [
        {
            "id": 1,
            "because": "MR !31 turned on new_checkout in production at 16:20.",
            "when": {"signal": "checkout_error_rate", "path": "new", "above": 0.05, "for_minutes": 5},
            "do": {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"},
        },
        {
            "id": 2,
            "because": "MR !33 deployed revision shop-00042 at 18:40.",
            "when": {"signal": "p95_latency_ms", "above": 1500, "for_minutes": 10},
            "do": {"action": "traffic_to_revision", "service": "shop", "revision": "shop-00041"},
        },
    ],
}


@pytest.fixture
def oncall():
    return parse_oncall(load_yaml(OPS / "oncall.yml"))


@pytest.fixture
def targets():
    return parse_targets(load_yaml(OPS / "targets.yml"))


@pytest.fixture
def orders_data():
    return copy.deepcopy(ORDERS)


def at(oncall, text: str) -> datetime:
    """A local time on the demo night: '22:06' is Oct 20, anything before noon is Oct 21."""
    hours, minutes = (int(x) for x in text.split(":"))
    day = 20 if hours >= 12 else 21
    return datetime(2026, 10, day, hours, minutes, tzinfo=oncall.timezone)


@pytest.fixture
def make_night(oncall, targets, orders_data):
    def build(data=None, signer="alex-velazquez", signed="22:06", method="merge", ledger=None):
        orders = parse_orders(copy.deepcopy(data or orders_data), targets, oncall)
        signature = None if signer is None else Signature(method=method, user=signer, at=at(oncall, signed),
                                                           commit="test")
        return Night(oncall=oncall, targets=targets, orders=orders, orders_problems=(), signature=signature,
                     ledger=ledger or Ledger())
    return build


def put(metrics: Metrics, key: str, moment: datetime, value: float, count: int = 30) -> None:
    """One minute of a signal and the traffic behind it (checkouts.new for checkout_error_rate.new, say).
    Orders act only on minutes with enough traffic, so test minutes carry a realistic count by default."""
    from nightorders.model import count_key

    metrics.put(key, moment, value)
    signal, _, path = key.partition(".")
    counted = count_key(signal, path or None)
    if counted:
        metrics.put(counted, moment, count)


def switched_off(metrics: Metrics, oncall, start: str, minutes: int, path: str = "new", whole_rate: float = 0.003,
                 whole_count: int = 60) -> None:
    """After an order turned a checkout path off: that path carries nothing, and the whole shop reads whole_rate."""
    first = at(oncall, start)
    for i in range(minutes):
        moment = first + timedelta(minutes=i)
        put(metrics, f"checkout_error_rate.{path}", moment, 0.0, count=0)
        put(metrics, "checkout_error_rate.all", moment, whole_rate, count=whole_count)


def series(oncall, key: str, start: str, values: list[float], count: int = 30) -> Metrics:
    """Per-minute samples for one key, starting at a local time, each with `count` checkouts or requests behind it."""
    metrics = Metrics()
    first = at(oncall, start)
    for i, value in enumerate(values):
        put(metrics, key, first + timedelta(minutes=i), value, count)
    return metrics
