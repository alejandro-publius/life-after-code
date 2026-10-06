"""Per-minute signals of the demo shop and the /metrics.json contract the relay reads. Times are test data."""

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from metrics import Metrics, iso_minute, p95, rate


def _load_shop_main():
    """shop/main.py under a unique name: relay/main.py exists too, and "relay" comes first on the test path."""
    if "shop_main" not in sys.modules:
        path = Path(__file__).resolve().parents[1] / "shop" / "main.py"
        spec = importlib.util.spec_from_file_location("shop_main", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["shop_main"] = module
        spec.loader.exec_module(module)
    return sys.modules["shop_main"]


main = _load_shop_main()

START = datetime(2026, 10, 21, 10, 0, 5, tzinfo=timezone.utc)
KEYS = {"at", "checkout_error_rate.old", "checkout_error_rate.new", "checkout_error_rate.all", "http_5xx_ratio",
        "p95_latency_ms", "payment_error_rate"}


class WallClock:
    def __init__(self, start: datetime = START) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


def test_rates_are_errors_over_requests_per_path_and_overall():
    clock = WallClock()
    metrics = Metrics(clock)
    for i in range(30):
        metrics.checkout("old", ok=(i != 0), latency_ms=100.0)
        metrics.checkout("new", ok=(i % 10 != 0), latency_ms=200.0)
    clock.advance(minutes=1)
    [minute] = metrics.report()
    assert minute["checkout_error_rate.old"] == round(1 / 30, 4)
    assert minute["checkout_error_rate.new"] == 0.1
    assert minute["checkout_error_rate.all"] == round(4 / 60, 4)


def test_a_minute_without_requests_reports_zero_not_an_error():
    clock = WallClock()
    metrics = Metrics(clock)
    clock.advance(minutes=1)
    [minute] = metrics.report()
    assert set(minute) == KEYS
    assert all(value == 0.0 for key, value in minute.items() if key != "at")


def test_only_complete_minutes_are_reported():
    clock = WallClock()
    metrics = Metrics(clock)
    metrics.checkout("old", ok=True, latency_ms=50.0)
    assert metrics.report() == []  # 10:00 has not ended yet
    clock.advance(seconds=55)
    metrics.checkout("old", ok=False, latency_ms=50.0)  # finishes at 10:01:00, so it counts in 10:01
    [minute] = metrics.report()
    assert minute["at"] == "2026-10-21T10:00:00Z"
    assert minute["checkout_error_rate.old"] == 0.0


def test_reports_the_last_60_minutes_and_nothing_before_the_start():
    clock = WallClock()
    metrics = Metrics(clock)
    clock.advance(minutes=5)
    assert [m["at"] for m in metrics.report()] == [f"2026-10-21T10:0{n}:00Z" for n in range(5)]
    for _ in range(90):
        metrics.checkout("new", ok=True, latency_ms=10.0)
        clock.advance(minutes=1)
    report = metrics.report()
    assert len(report) == 60
    assert report[0]["at"] == iso_minute(clock.now - timedelta(minutes=60))
    assert report[-1]["at"] == iso_minute(clock.now - timedelta(minutes=1))


def test_p95_is_nearest_rank():
    assert p95([]) == 0.0
    assert p95([7.0]) == 7.0
    assert p95([float(n) for n in range(1, 101)]) == 95.0
    assert p95([float(n) for n in range(100, 160)]) == 156.0  # 60 samples: the 57th smallest


def test_5xx_ratio_latency_and_payment_rate():
    clock = WallClock()
    metrics = Metrics(clock)
    for status in [200] * 95 + [500, 502, 503, 504, 404]:
        metrics.http(status)
    for ms in range(1, 101):
        metrics.checkout("old", ok=True, latency_ms=float(ms))
    for ok in [True] * 499 + [False]:
        metrics.payment(ok)
    clock.advance(minutes=1)
    [minute] = metrics.report()
    assert minute["http_5xx_ratio"] == 0.04
    assert minute["p95_latency_ms"] == 95.0
    assert minute["payment_error_rate"] == 0.002


def test_rate_never_divides_by_zero():
    assert rate(0, 0) == 0.0
    assert rate(3, 0) == 3.0


async def _no_wait(_seconds: float) -> None:
    return None


def test_metrics_json_contract_and_what_counts_as_a_request():
    clock = WallClock(datetime(2026, 10, 21, 10, 0, 0, tzinfo=timezone.utc))
    settings = main.Settings(flags_override={"new_checkout": False})
    app = main.create_app(settings, clock=clock, sleep=_no_wait, seed=1)
    with TestClient(app) as client:
        for _ in range(4):
            assert client.post("/checkout", json={"user": "shopper-001", "region": "us",
                                                  "items": [{"sku": "juniper-tea", "price": 8.0}]}).status_code == 200
        client.get("/products")
        assert client.post("/checkout", json={"user": "x", "region": "mars", "items": []}).status_code == 422
        client.get("/healthz")
        client.get("/metrics.json")
        clock.advance(minutes=1)
        body = client.get("/metrics.json").json()
    assert body["label"] == "DEMO SHOP: simulated customers and planted faults"
    [minute] = body["minutes"]
    assert set(minute) == KEYS
    assert minute["at"] == "2026-10-21T10:00:00Z"
    datetime.fromisoformat(minute["at"])  # the relay parses it with fromisoformat
    assert minute["checkout_error_rate.old"] == 0.0
    assert minute["checkout_error_rate.new"] == 0.0
    shop = app.state.shop
    [(_, bucket)] = shop.metrics.complete()
    assert bucket.checkouts == {"old": 4, "new": 0}
    assert bucket.requests == 6  # 4 checkouts, 1 product list, 1 rejected checkout; not healthz or metrics
