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


def series(oncall, key: str, start: str, values: list[float]) -> Metrics:
    """Per-minute samples for one key, starting at a local time."""
    metrics = Metrics()
    first = at(oncall, start)
    for i, value in enumerate(values):
        metrics.put(key, first + timedelta(minutes=i), value)
    return metrics
