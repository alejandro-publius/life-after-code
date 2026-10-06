"""DEMO DATA: simulated customers for a demo night, labelled "demo traffic" in logs, the page and the API.

About 60 checkouts a minute, plus two product views for every three checkouts. Every second checkout comes
from a pilot customer (pilot-01 to pilot-10), the users the new checkout is switched on for in the demo,
so about half the checkouts are eligible for the new path. The loop stops after at most 30 minutes.

One cart in 13 is a jar of juniper jam shipped to the UK: 16.46 USD becomes 12.345 GBP after the region
step, which the new rounding cannot handle while the planted fault rounding_bug is on. To keep each path's
error rate steady from minute to minute, the loop asks the flag client which path a customer will get and
gives every 13th cart on each path the jam. With the 1 in 500 payment baseline this matches the demo night
replay: about 7.9% errors on the new path while rounding_bug is on.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable

import httpx

import jsonlog

LABEL = "demo traffic"
MAX_MINUTES = 30
PER_MINUTE = 60
MAX_IN_FLIGHT = 40
PROBLEM_EVERY = 13

PILOT_USERS = tuple(f"pilot-{n:02d}" for n in range(1, 11))
SHOPPERS = tuple(f"shopper-{n:03d}" for n in range(1, 51))

PROBLEM_CART = {"region": "uk", "items": [{"sku": "juniper-jam", "price": 16.46, "qty": 1}]}
CART_REGIONS = ("us", "us", "uk", "eu", "ca", "us", "uk")
CART_ITEMS = (
    [{"sku": "juniper-tea", "price": 8.00, "qty": 1}],
    [{"sku": "cedar-candle", "price": 14.00, "qty": 1}, {"sku": "trail-mix", "price": 6.40, "qty": 2}],
    [{"sku": "wool-socks", "price": 18.00, "qty": 1}],
    [{"sku": "camp-mug", "price": 12.20, "qty": 2}],
    [{"sku": "trail-mix", "price": 6.40, "qty": 1}, {"sku": "juniper-tea", "price": 8.00, "qty": 1}],
)


def customer(i: int) -> str:
    """Even checkouts come from pilot customers, odd ones from everyone else."""
    return PILOT_USERS[(i // 2) % len(PILOT_USERS)] if i % 2 == 0 else SHOPPERS[(i // 2) % len(SHOPPERS)]


def normal_cart(i: int) -> dict:
    return {"region": CART_REGIONS[i % len(CART_REGIONS)], "items": CART_ITEMS[i % len(CART_ITEMS)]}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TrafficLoop:
    """One background loop at a time, time-boxed to MAX_MINUTES."""

    def __init__(
        self,
        client: Callable[[], httpx.AsyncClient],
        new_path_for: Callable[[str], bool],
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        now: Callable[[], datetime] = utcnow,
    ) -> None:
        self._client = client
        self._new_path_for = new_path_for
        self._sleep = sleep
        self._monotonic = monotonic
        self._now = now
        self._task: asyncio.Task | None = None
        self.minutes = 0
        self.until: datetime | None = None
        self.checkouts = self.views = self.failed = self.skipped = 0
        self._per_path = {"old": 0, "new": 0}

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self, minutes: int) -> datetime:
        """Start (or restart) the loop for 1 to 30 minutes. Returns when it will stop."""
        if self.running:
            self._task.cancel()  # type: ignore[union-attr]
        self.minutes = max(1, min(int(minutes), MAX_MINUTES))
        self.until = self._now() + timedelta(minutes=self.minutes)
        self.checkouts = self.views = self.failed = self.skipped = 0
        self._per_path = {"old": 0, "new": 0}
        self._task = asyncio.get_running_loop().create_task(self.run(self.minutes))
        return self.until

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def run(self, minutes: int) -> None:
        minutes = max(1, min(int(minutes), MAX_MINUTES))
        interval = 60.0 / PER_MINUTE
        start = self._monotonic()
        stop_at = start + minutes * 60.0  # the time box holds even if the schedule slips
        in_flight: set[asyncio.Task] = set()
        jsonlog.emit("INFO", f"Demo traffic started: {minutes} min, about {PER_MINUTE} checkouts a minute",
                     label=LABEL, minutes=minutes)
        async with self._client() as client:
            try:
                for i in range(minutes * PER_MINUTE):
                    wait = start + i * interval - self._monotonic()
                    if wait > 0:
                        await self._sleep(wait)
                    if self._monotonic() >= stop_at:
                        break
                    if len(in_flight) >= MAX_IN_FLIGHT:
                        self.skipped += 1
                        continue
                    task = asyncio.create_task(self._customer(client, i))
                    in_flight.add(task)
                    task.add_done_callback(in_flight.discard)
                if in_flight:
                    await asyncio.wait(set(in_flight), timeout=15)
            finally:
                for task in in_flight:
                    task.cancel()
                if in_flight:
                    await asyncio.gather(*in_flight, return_exceptions=True)
                jsonlog.emit("INFO", f"Demo traffic stopped after {self.checkouts} checkouts ({self.failed} failed)",
                             label=LABEL, checkouts=self.checkouts, failed=self.failed, skipped=self.skipped)

    async def _customer(self, client: httpx.AsyncClient, i: int) -> None:
        user = customer(i)
        path = "new" if self._new_path_for(user) else "old"
        number = self._per_path[path]
        self._per_path[path] += 1
        cart = PROBLEM_CART if number % PROBLEM_EVERY == PROBLEM_EVERY // 2 else normal_cart(i)
        self.checkouts += 1
        try:
            if i % 3 != 2:
                await client.get("/products")
                self.views += 1
            response = await client.post("/checkout", json={"user": user, **cart})
        except Exception:  # the shop logs its own errors; the loop keeps going
            self.failed += 1
            return
        if response.status_code >= 400:
            self.failed += 1
