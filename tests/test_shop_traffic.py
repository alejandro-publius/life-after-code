"""Demo traffic against the demo shop, in simulated time, read back the way the relay reads it.

The point: the live shop must trip the same alert rules (ops/alerts.yml) as the demo night replay's
DemoShop. Each scenario runs six simulated minutes of demo traffic, then feeds /metrics.json through the
relay's own reader (parse_metrics) and condition code. Users, carts and times are test data.
"""

import asyncio
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

import demo_traffic
from flags import FlagClient
from nightorders.orders import load_yaml
from nightorders.signals import condition_holds
from nightorders.sources import parse_metrics
from nightorders.watch import parse_alert_rules


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

REPO = Path(__file__).resolve().parents[1]
RULES = parse_alert_rules(load_yaml(REPO / "ops" / "alerts.yml"))
START = datetime(2026, 10, 21, 10, 0, 0, tzinfo=timezone.utc)


class FakeTime:
    """Simulated time: sleeping lets every in-flight customer finish, then moves the clock on."""

    def __init__(self) -> None:
        self.wall = START
        self.mono = 0.0

    def now(self) -> datetime:
        return self.wall

    def monotonic(self) -> float:
        return self.mono

    async def sleep(self, seconds: float) -> None:
        for _ in range(10_000):
            if len(asyncio.all_tasks()) <= 1:
                break
            await asyncio.sleep(0)
        self.mono += seconds
        self.wall += timedelta(seconds=seconds)


async def latency(_seconds: float) -> None:
    await asyncio.sleep(0)


def gitlab_flags(new_checkout: bool, stock_from_cache: bool) -> FlagClient:
    features = [
        {"name": "new_checkout", "enabled": new_checkout,
         "strategies": [{"name": "userWithId", "parameters": {"userIds": ",".join(demo_traffic.PILOT_USERS)}}]},
        {"name": "stock_from_cache", "enabled": stock_from_cache,
         "strategies": [{"name": "default", "parameters": {}}]},
    ]
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"version": 1, "features": features}))
    return FlagClient("https://gitlab.example/api/v4/feature_flags/unleash/42", "glffct-test", "production",
                      transport=transport, monotonic=lambda: 0.0)


def run_night(minutes: int, faults: dict[str, bool], *, new_checkout: bool = True,
              stock_from_cache: bool = False) -> tuple[dict, object, demo_traffic.TrafficLoop]:
    clock = FakeTime()
    flags = gitlab_flags(new_checkout, stock_from_cache)
    app = main.create_app(main.Settings(faults=faults), flags=flags, clock=clock.now, sleep=latency, seed=5)

    def client() -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://shop.test",
                                 headers={"X-Demo-Traffic": demo_traffic.LABEL})

    loop = demo_traffic.TrafficLoop(client, lambda user: flags.is_on("new_checkout", user),
                               sleep=clock.sleep, monotonic=clock.monotonic, now=clock.now)

    async def scenario() -> dict:
        await flags.refresh()
        await loop.run(minutes)
        clock.wall = START + timedelta(minutes=minutes)  # the last minute has ended
        async with client() as c:
            return (await c.get("/metrics.json")).json()

    return asyncio.run(scenario()), app, loop


def alerts(body: dict) -> set[str]:
    """Which ops/alerts.yml rules the relay's own code would see firing at the end of the run."""
    relay = parse_metrics(body)  # the relay's reader of /metrics.json
    now = datetime.fromisoformat(body["minutes"][-1]["at"]) + timedelta(minutes=1)
    return {rule.key for rule in RULES if condition_holds(rule.condition, relay, now)[0]}


def test_customers_alternate_between_pilots_and_other_shoppers():
    assert [demo_traffic.customer(i) for i in range(4)] == ["pilot-01", "shopper-001", "pilot-02", "shopper-002"]


@pytest.mark.parametrize("faults,new_checkout,stock_from_cache,expected", [
    ({}, True, False, set()),
    ({"rounding_bug": True}, True, False, {"checkout_error_rate.new"}),
    ({"rounding_bug": True}, False, False, set()),  # after the relay turns new_checkout off
    ({"inventory_slow": True}, True, False, {"checkout_error_rate.old", "checkout_error_rate.new",
                                              "http_5xx_ratio"}),
    ({"inventory_slow": True}, True, True, set()),  # after stock_from_cache is turned on
])
def test_demo_traffic_trips_the_same_alerts_as_the_replay(faults, new_checkout, stock_from_cache, expected):
    body, app, loop = run_night(6, faults, new_checkout=new_checkout, stock_from_cache=stock_from_cache)
    assert len(body["minutes"]) == 6
    assert alerts(body) == expected
    for _, bucket in app.state.shop.metrics.complete():
        total = bucket.checkouts["old"] + bucket.checkouts["new"]
        assert total == demo_traffic.PER_MINUTE
        assert bucket.requests == demo_traffic.PER_MINUTE + 40  # checkouts plus two product views per three
        if new_checkout:
            assert bucket.checkouts == {"old": 30, "new": 30}  # half the customers are pilots
    assert loop.checkouts == 6 * demo_traffic.PER_MINUTE


def test_rates_match_the_replay_numbers():
    rounding, _, _ = run_night(6, {"rounding_bug": True})
    new = [m["checkout_error_rate.new"] for m in rounding["minutes"]]
    assert all(0.06 <= rate <= 0.11 for rate in new)  # replay: 7.9%
    assert 0.07 <= sum(new) / len(new) <= 0.09
    assert all(m["checkout_error_rate.old"] < 0.01 for m in rounding["minutes"])  # replay: 0.3%

    slow, _, _ = run_night(6, {"inventory_slow": True})
    for minute in slow["minutes"]:
        assert minute["checkout_error_rate.old"] == pytest.approx(0.2, abs=0.01)  # replay: 20.3%
        assert minute["checkout_error_rate.new"] == pytest.approx(0.2, abs=0.01)  # replay: 20.4%
        assert minute["http_5xx_ratio"] == pytest.approx(0.12, abs=0.01)  # replay: 12.2%


def test_the_loop_stops_at_its_time_box():
    _, _, loop = run_night(2, {})
    assert loop.checkouts == 2 * demo_traffic.PER_MINUTE
    assert not loop.running


def test_start_caps_minutes_at_30():
    async def scenario() -> int:
        loop = demo_traffic.TrafficLoop(lambda: httpx.AsyncClient(), lambda user: False)
        loop.start(45)
        minutes = loop.minutes
        await loop.stop()
        return minutes

    assert asyncio.run(scenario()) == demo_traffic.MAX_MINUTES
