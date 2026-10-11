"""Run a test night against the live demo shop: start demo traffic and plant the two faults on a timeline.

    DEMO_KEY=... python scripts/test_night.py --shop https://shop-xxxx.run.app --at 01:40
    python scripts/test_night.py --shop https://shop-xxxx.run.app --dry-run

The relay watches the shop on its own (Cloud Scheduler ticks it every minute), so this script only plays
the part of a bad night: about 60 demo checkouts a minute, an inventory slowdown that fails both checkout
paths for a while (the page), then the price rounding bug in the new checkout (the signed order). The
timeline uses the real alert windows from ops/alerts.yml (5 and 10 minutes), so a test night takes about
45 real minutes. With --at it waits until that local time first, so the faults start while the on-call
person is really asleep. Everything it touches is labelled demo data by the shop itself.

The demo key comes only from the DEMO_KEY environment variable and is never printed.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import httpx
import yaml

REPO = Path(__file__).resolve().parents[1]
TRAFFIC_MINUTES = 30          # the shop's own cap per request; the loop is renewed before it ends
TRAFFIC_RENEW_EVERY = 25.0
TIMEOUT_SECONDS = 10.0
RETRIES = 3


@dataclass(frozen=True)
class Step:
    minute: float   # minutes after the start
    what: str       # plain words, printed
    faults: dict[str, bool] | None = None   # body for POST /demo/faults, or None for a traffic renewal


def timeline(inventory_from: float, inventory_minutes: float, rounding_from: float, end: float) -> list[Step]:
    """The night, as minutes after the start. Order matters only for printing; the runner sorts by minute."""
    steps = [
        Step(0.0, "demo traffic starts (about 60 checkouts a minute)"),
        Step(inventory_from, "planted fault inventory_slow on: both checkout paths start failing", {"inventory_slow": True}),
        Step(inventory_from + inventory_minutes, "planted fault inventory_slow off", {"inventory_slow": False}),
        Step(rounding_from, "planted fault rounding_bug on: the new checkout path starts failing", {"rounding_bug": True}),
        Step(end, "night over: faults off, traffic stops", {"inventory_slow": False, "rounding_bug": False}),
    ]
    minute = TRAFFIC_RENEW_EVERY
    while minute < end:
        steps.append(Step(minute, "demo traffic renewed"))
        minute += TRAFFIC_RENEW_EVERY
    return sorted(steps, key=lambda s: (s.minute, s.faults is None))


def local_timezone() -> ZoneInfo:
    data = yaml.safe_load((REPO / "ops" / "oncall.yml").read_text(encoding="utf-8")) or {}
    return ZoneInfo(str(data.get("timezone", "UTC")))


def next_occurrence(hhmm: str, now: datetime) -> datetime:
    hours, minutes = (int(x) for x in hhmm.split(":"))
    candidate = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
    return candidate if candidate > now else candidate + timedelta(days=1)


class Shop:
    """The two demo endpoints of the shop. Every call is retried a few times and never prints the key."""

    def __init__(self, base_url: str, demo_key: str, client: httpx.Client | None = None, sleep: Callable[[float], None] = time.sleep):
        self.base_url = base_url.rstrip("/")
        self._headers = {"X-Demo-Key": demo_key}
        self.client = client or httpx.Client(timeout=TIMEOUT_SECONDS)
        self.sleep = sleep

    def _post(self, path: str, **kwargs) -> httpx.Response:
        last = "no attempt"
        for attempt in range(RETRIES):
            try:
                response = self.client.post(self.base_url + path, headers=self._headers, timeout=TIMEOUT_SECONDS, **kwargs)
            except httpx.HTTPError as error:
                last = type(error).__name__
            else:
                if response.status_code < 500:
                    return response
                last = f"HTTP {response.status_code}"
            self.sleep(2.0 * (attempt + 1))
        raise RuntimeError(f"{path}: {last} after {RETRIES} attempts")

    def traffic(self, minutes: int) -> httpx.Response:
        return self._post("/demo/traffic", params={"minutes": minutes})

    def faults(self, changes: dict[str, bool]) -> httpx.Response:
        return self._post("/demo/faults", json=changes)


def describe(response: httpx.Response) -> str:
    if response.status_code == 401:
        return "refused: wrong or missing demo key"
    if response.status_code == 403:
        return "refused: DEMO_KEY is not set on the shop service"
    return f"HTTP {response.status_code}"


def run(shop: Shop, steps: list[Step], start: datetime, now: Callable[[], datetime], sleep: Callable[[float], None],
        out=sys.stdout) -> int:
    """Play the steps at their minutes after start. Returns 1 if the shop refused anything."""
    refused = 0
    for step in steps:
        due = start + timedelta(minutes=step.minute)
        wait = (due - now()).total_seconds()
        if wait > 0:
            sleep(wait)
        at = now().astimezone(start.tzinfo).strftime("%H:%M")
        try:
            response = shop.faults(step.faults) if step.faults is not None else shop.traffic(TRAFFIC_MINUTES)
        except RuntimeError as error:
            print(f"{at}  {step.what}: FAILED ({error})", file=out)
            refused += 1
            continue
        verdict = "ok" if response.status_code == 200 else describe(response)
        print(f"{at}  {step.what}: {verdict}", file=out)
        if response.status_code != 200:
            refused += 1
        if step.faults is not None and step.minute >= steps[-1].minute:
            # the last step also stops the traffic loop
            shop.traffic(0)
    return 1 if refused else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shop", required=True, help="the shop's base URL")
    parser.add_argument("--at", help="wait until this local time (HH:MM, on-call time zone) before starting")
    parser.add_argument("--inventory-from", type=float, default=3.0, help="minutes after start (default 3)")
    parser.add_argument("--inventory-minutes", type=float, default=13.0, help="how long the slowdown lasts (default 13)")
    parser.add_argument("--rounding-from", type=float, default=20.0, help="minutes after start (default 20)")
    parser.add_argument("--end", type=float, default=45.0, help="minutes after start when everything is turned off (default 45)")
    parser.add_argument("--dry-run", action="store_true", help="print the timeline and exit")
    args = parser.parse_args(argv)

    tz = local_timezone()
    steps = timeline(args.inventory_from, args.inventory_minutes, args.rounding_from, args.end)
    now = lambda: datetime.now(tz)  # noqa: E731
    start = next_occurrence(args.at, now()) if args.at else now()
    print(f"Test night against {args.shop}, starting {start:%a %H:%M %Z}. Steps:")
    for step in steps:
        print(f"  {(start + timedelta(minutes=step.minute)):%H:%M}  {step.what}")
    if args.dry_run:
        return 0
    key = os.environ.get("DEMO_KEY", "")
    if not key:
        print("DEMO_KEY is not set. Put the shop's demo key in that environment variable (never on the command line).")
        return 2
    return run(Shop(args.shop, key), steps, start, now, time.sleep)


if __name__ == "__main__":
    raise SystemExit(main())
