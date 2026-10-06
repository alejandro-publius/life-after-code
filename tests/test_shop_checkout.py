"""Checkout paths, the two planted demo faults and stock_from_cache. Users, carts and prices are test data."""

import asyncio
import importlib.util
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from checkout import Line, PaymentError, Store, old_round, price_cart, region_price, round_price
from demo_catalog import CATALOG, REGIONS
from faults import Faults
from flags import FlagClient
from metrics import p95


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

JAM_TO_UK = {"region": "uk", "items": [{"sku": "juniper-jam", "price": 16.46, "qty": 1}]}
TEA_TO_US = {"region": "us", "items": [{"sku": "juniper-tea", "price": 8.00, "qty": 1}]}


async def no_wait(_seconds: float) -> None:
    return None


def pilot_flags(stock_from_cache: bool = False) -> FlagClient:
    """GitLab flags as the demo sets them: new_checkout on for the pilot users only."""
    features = [{"name": "new_checkout", "enabled": True,
                 "strategies": [{"name": "userWithId", "parameters": {"userIds": "pilot-01,pilot-02"}}]}]
    if stock_from_cache:
        features.append({"name": "stock_from_cache", "enabled": True,
                         "strategies": [{"name": "default", "parameters": {}}]})
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"version": 1, "features": features}))
    client = FlagClient("https://gitlab.example/api/v4/feature_flags/unleash/42", "glffct-test", "production",
                        transport=transport, monotonic=lambda: 0.0)
    return client


def shop(faults: dict[str, bool] | None = None, *, stock_from_cache: bool = False) -> TestClient:
    settings = main.Settings(demo_key="test-demo-key", faults=faults or {})
    return TestClient(main.create_app(settings, flags=pilot_flags(stock_from_cache), sleep=no_wait, seed=7))


def errors_logged(output: str) -> list[dict]:
    lines = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    return [line for line in lines if line["severity"] == "ERROR"]


def test_region_step_and_both_roundings():
    assert region_price(Decimal("16.46"), "uk") == Decimal("12.345")
    assert old_round(Decimal("12.345")) == Decimal("12.35")
    assert round_price(Decimal("12.345"), "uk") == Decimal("12.35")
    assert round_price(Decimal("8.96"), "ca") == Decimal("8.95")  # Canada rounds to 0.05 on the new path
    assert old_round(Decimal("8.96")) == Decimal("8.96")
    with pytest.raises(ValueError, match="price 12.345 cannot be rounded"):
        round_price(Decimal("12.345"), "uk", planted_bug=True)
    assert round_price(Decimal("12.30"), "uk", planted_bug=True) == Decimal("12.30")


def test_only_the_jam_gets_more_than_two_decimals_after_the_region_step():
    def three_decimals(price: Decimal, region: str) -> bool:
        amount = region_price(price, region)
        return amount != amount.quantize(Decimal("0.01"))

    for product in CATALOG.values():
        for region in REGIONS:
            expected = product.sku == "juniper-jam" and region != "us"
            assert three_decimals(product.price, region) is expected, (product.sku, region)


def test_cart_totals_on_both_paths():
    lines = [Line("trail-mix", Decimal("6.40"), 2), Line("juniper-tea", Decimal("8.00"), 1)]
    assert price_cart(lines, "ca", "old") == Decimal("29.12")  # 8.96 * 2 + 11.20
    assert price_cart(lines, "ca", "new") == Decimal("29.10")  # 8.95 * 2 + 11.20


def test_new_checkout_flag_picks_the_path_per_user():
    with shop() as client:
        pilot = client.post("/checkout", json={"user": "pilot-01", **TEA_TO_US}).json()
        other = client.post("/checkout", json={"user": "shopper-001", **TEA_TO_US}).json()
    assert pilot["path"] == "new" and pilot["ok"] is True
    assert other["path"] == "old" and other["ok"] is True
    assert pilot["total"] == "8.00" and pilot["currency"] == "USD"
    assert "nothing is charged" in pilot["label"]


def test_override_on_sends_everyone_to_the_new_path():
    settings = main.Settings(flags_override={"new_checkout": True})
    with TestClient(main.create_app(settings, sleep=no_wait)) as client:
        assert client.post("/checkout", json={"user": "shopper-001", **TEA_TO_US}).json()["path"] == "new"


def test_rounding_bug_fails_only_the_new_path_and_logs_where(capsys):
    with shop({"rounding_bug": True}) as client:
        capsys.readouterr()
        new = client.post("/checkout", json={"user": "pilot-01", **JAM_TO_UK})
        old = client.post("/checkout", json={"user": "shopper-001", **JAM_TO_UK})
        fine = client.post("/checkout", json={"user": "pilot-02", **TEA_TO_US})
    assert new.status_code == 500
    assert new.json() == {"ok": False, "path": "new", "error": "price 12.345 cannot be rounded",
                          "fault": "rounding_bug (planted demo fault)"}
    assert old.status_code == 200 and old.json()["total"] == "12.35"
    assert fine.status_code == 200 and fine.json()["path"] == "new"

    [line] = errors_logged(capsys.readouterr().out)
    assert line["message"].startswith("ValueError: price 12.345 cannot be rounded (shop/checkout.py:")
    location = line["logging.googleapis.com/sourceLocation"]
    assert location["file"] == "shop/checkout.py" and location["function"] == "round_price"
    assert isinstance(location["line"], int) and location["line"] > 0
    assert line["fault"] == "rounding_bug" and line["label"] == "planted demo fault"
    assert line["path"] == "new" and line["http_status"] == 500
    assert "Traceback" in line["stack_trace"]


def test_inventory_slow_fails_one_in_five_on_both_paths(capsys):
    with shop({"inventory_slow": True}) as client:
        results = [client.post("/checkout", json={"user": "pilot-01" if i % 2 == 0 else "shopper-001", **TEA_TO_US})
                   for i in range(20)]
    by_path: dict[str, list[int]] = {"old": [], "new": []}
    for response in results:
        by_path[response.json()["path"]].append(response.status_code)
    assert by_path["new"].count(504) == 2 and by_path["new"].count(200) == 8
    assert by_path["old"].count(504) == 2 and by_path["old"].count(200) == 8
    failed = next(r.json() for r in results if r.status_code == 504)
    assert failed["fault"] == "inventory_slow (planted demo fault)"
    assert failed["error"] == "stock lookup timed out after 1.0 s"
    lines = errors_logged(capsys.readouterr().out)
    assert len(lines) == 4
    assert all(line["logging.googleapis.com/sourceLocation"]["function"] == "stock" for line in lines)


def test_stock_from_cache_keeps_checkout_working_while_inventory_is_slow():
    with shop({"inventory_slow": True}, stock_from_cache=True) as client:
        results = [client.post("/checkout", json={"user": "pilot-01" if i % 2 == 0 else "shopper-001", **TEA_TO_US})
                   for i in range(20)]
    assert all(r.status_code == 200 for r in results)
    assert {r.json()["stock_from"] for r in results} == {"cache"}


def test_payment_stub_fails_one_payment_in_500():
    async def pay_many() -> list[int]:
        stub = Store(Faults(), no_wait, random.Random(1)).payments
        failures = []
        for n in range(1, 1001):
            try:
                await stub.pay(Decimal("8.00"), "USD")
            except PaymentError:
                failures.append(n)
        return failures

    assert asyncio.run(pay_many()) == [500, 1000]


def test_a_failed_payment_is_a_502_and_counts_as_a_payment_error():
    with shop() as client:
        client.app.state.shop.store.payments.attempts = 499  # the next payment is the baseline failure
        response = client.post("/checkout", json={"user": "shopper-001", **TEA_TO_US})
        buckets = list(client.app.state.shop.metrics._minutes.values())
    assert response.status_code == 502
    assert "fault" not in response.json()
    assert sum(b.payments for b in buckets) == 1 and sum(b.payment_errors for b in buckets) == 1
    assert sum(b.failed["old"] for b in buckets) == 1


@pytest.mark.parametrize("body", [
    {"user": "a", "region": "mars", "items": [{"sku": "x", "price": 1}]},
    {"user": "a", "region": "us", "items": []},
    {"user": "a", "region": "us", "items": [{"sku": "x", "price": -1}]},
    {"user": "", "region": "us", "items": [{"sku": "x", "price": 1}]},
    {"region": "us", "items": [{"sku": "x", "price": 1}]},
])
def test_bad_checkout_requests_are_rejected(body):
    with shop() as client:
        assert client.post("/checkout", json=body).status_code == 422


def test_latency_model_matches_the_demo_night_replay():
    """The replay uses p95 420 ms, and 1,320 ms while inventory is down: under the 1,500 ms alert."""

    async def p95_ms(slow: bool, cache: bool) -> float:
        waits: list[float] = []

        async def record(seconds: float) -> None:
            waits.append(seconds)

        faults = Faults()
        faults.set({"inventory_slow": slow}, source="test")
        store = Store(faults, record, random.Random(3))
        totals = []
        for _ in range(300):
            before = len(waits)
            try:
                await store.checkout([Line("juniper-tea", Decimal("8.00"), 1)], "us", path="old",
                                     stock_from_cache=cache)
            except TimeoutError:
                pass
            totals.append(sum(waits[before:]) * 1000)
        return p95(totals)

    assert 300 < asyncio.run(p95_ms(slow=False, cache=False)) < 500
    assert 1000 < asyncio.run(p95_ms(slow=True, cache=False)) < 1500
    assert asyncio.run(p95_ms(slow=True, cache=True)) < 500
