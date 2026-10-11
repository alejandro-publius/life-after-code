"""The test-night runner: timeline, the shop calls it makes, and that the demo key never shows. Offline."""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import test_night  # noqa: E402

KEY = "demo-key-for-tests"


def test_timeline_has_the_two_faults_and_renews_traffic():
    steps = test_night.timeline(3, 13, 20, 45)
    whats = [(s.minute, s.faults) for s in steps]
    assert whats[0] == (0.0, None)
    assert (3, {"inventory_slow": True}) in whats and (16, {"inventory_slow": False}) in whats
    assert (20, {"rounding_bug": True}) in whats
    assert whats[-1] == (45, {"inventory_slow": False, "rounding_bug": False})
    assert [s.minute for s in steps if s.faults is None and s.coupon is None] == [0.0, 25.0]  # traffic, renewed once
    assert [s.minute for s in steps if s.coupon] == [21.5]  # the planted injection, once
    assert [s.minute for s in steps] == sorted(s.minute for s in steps)


def test_next_occurrence_is_tonight_or_tomorrow():
    now = datetime(2026, 10, 17, 22, 0, tzinfo=timezone.utc)
    assert test_night.next_occurrence("01:40", now) == datetime(2026, 10, 18, 1, 40, tzinfo=timezone.utc)
    assert test_night.next_occurrence("23:10", now) == datetime(2026, 10, 17, 23, 10, tzinfo=timezone.utc)


class FakeShop:
    def __init__(self, status: int = 200):
        self.requests: list[httpx.Request] = []
        self.status = status

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(self.status, json={"ok": True})


class Clock:
    def __init__(self, start: datetime):
        self.now = start
        self.slept: list[float] = []

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += timedelta(seconds=seconds)


def run_night(status: int = 200):
    fake = FakeShop(status)
    client = httpx.Client(transport=httpx.MockTransport(fake))
    clock = Clock(datetime(2026, 10, 18, 1, 40, tzinfo=timezone.utc))
    shop = test_night.Shop("https://shop.example/", KEY, client=client, sleep=clock.sleep)
    out = io.StringIO()
    code = test_night.run(shop, test_night.timeline(3, 13, 20, 45), clock.now, lambda: clock.now, clock.sleep, out=out)
    return code, fake, clock, out.getvalue()


def test_the_runner_plays_the_night_in_order_with_the_key_in_a_header_only():
    code, fake, clock, printed = run_night()
    assert code == 0
    calls = [(r.url.path, dict(r.url.params), json.loads(r.content) if r.content else None) for r in fake.requests]
    assert calls[0] == ("/demo/traffic", {"minutes": "30"}, None)
    assert calls[1] == ("/demo/faults", {}, {"inventory_slow": True})
    assert calls[-1] == ("/demo/traffic", {"minutes": "0"}, None)  # the last step stops the traffic loop
    keyed = [r for r in fake.requests if r.url.path != "/checkout"]
    assert all(r.headers["X-Demo-Key"] == KEY for r in keyed)
    [planted] = [r for r in fake.requests if r.url.path == "/checkout"]
    assert "X-Demo-Key" not in planted.headers  # /checkout is public: the key goes only where it is needed
    assert KEY not in printed and "inventory_slow on" in printed and "night over" in printed
    assert sum(clock.slept) == 45 * 60  # it waited exactly through the night


def test_a_refused_call_is_reported_and_fails_the_run():
    code, fake, clock, printed = run_night(status=403)
    assert code == 1 and "DEMO_KEY is not set on the shop service" in printed


def test_dry_run_prints_the_timeline_without_a_key(monkeypatch, capsys):
    monkeypatch.delenv("DEMO_KEY", raising=False)
    assert test_night.main(["--shop", "https://shop.example", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "rounding_bug on" in out and "demo traffic starts" in out


def test_without_a_key_it_refuses_to_start(monkeypatch, capsys):
    monkeypatch.delenv("DEMO_KEY", raising=False)
    assert test_night.main(["--shop", "https://shop.example"]) == 2
    assert "DEMO_KEY is not set" in capsys.readouterr().out
