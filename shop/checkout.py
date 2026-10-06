"""Juniper Market checkout (demo shop): two paths behind the new_checkout flag, and the demo services
they call. Nothing is charged or shipped.

Both paths take the US dollar list price of each item through the region step (the price in the region's
currency, at a fixed demo rate). The old path then rounds half up to the cent. The new path (MR !31 in the
demo story, "New checkout: price rounding per region") rounds with round_price() to the region's step.

Planted demo faults (see faults.py): rounding_bug makes round_price() reject a price with more than two
decimals after the region step, the way the demo story's bug does ("price 12.345 cannot be rounded").
inventory_slow makes stock lookups slow, and every fifth one times out.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Awaitable, Callable

from demo_catalog import REGIONS, STOCK_CACHE
from faults import Faults, planted

CENT = Decimal("0.01")
Sleep = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class Line:
    sku: str
    price: Decimal  # USD list price, as the customer's cart sent it
    qty: int


@dataclass(frozen=True)
class Receipt:
    order: str
    path: str
    region: str
    currency: str
    total: Decimal
    stock_from: str
    payment: str


class PaymentError(Exception):
    """The demo payment provider did not take the payment."""


def region_price(price: Decimal, region: str) -> Decimal:
    """The region step: a USD list price in the region's currency."""
    return price * REGIONS[region].rate


def old_round(amount: Decimal) -> Decimal:
    """Old path: half up to the cent, in every region."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def round_price(amount: Decimal, region: str, *, planted_bug: bool = False) -> Decimal:
    """New path: round to the region's step, half up (to 0.05 in Canada, to the cent elsewhere)."""
    if planted_bug and amount != amount.quantize(CENT):
        # Planted demo fault rounding_bug: this version assumes every price already has two decimals.
        raise planted(ValueError(f"price {amount.normalize():f} cannot be rounded"), "rounding_bug")
    step = REGIONS[region].step
    return ((amount / step).quantize(Decimal(1), rounding=ROUND_HALF_UP) * step).quantize(CENT)


def price_cart(lines: list[Line], region: str, path: str, *, planted_bug: bool = False) -> Decimal:
    total = Decimal("0.00")
    for line in lines:
        amount = region_price(line.price, region)
        rounded = round_price(amount, region, planted_bug=planted_bug) if path == "new" else old_round(amount)
        total += rounded * line.qty
    return total


class Inventory:
    """Demo inventory service, asked once per checkout for the whole cart."""

    TIMEOUT = 1.0  # seconds the shop waits for an answer
    SLOW_EVERY = 5  # with inventory_slow on, every fifth lookup does not answer in time

    def __init__(self, sleep: Sleep, rng: random.Random) -> None:
        self._sleep = sleep
        self._rng = rng
        self.slow_lookups = 0

    async def stock(self, skus: list[str], *, slow: bool) -> dict[str, int]:
        if slow:
            number = self.slow_lookups
            self.slow_lookups += 1
            if number % self.SLOW_EVERY == self.SLOW_EVERY - 1:
                await self._sleep(self.TIMEOUT)
                raise planted(TimeoutError(f"stock lookup timed out after {self.TIMEOUT:.1f} s"), "inventory_slow")
            await self._sleep(self._rng.uniform(0.70, 0.90))
        else:
            await self._sleep(self._rng.uniform(0.04, 0.08))
        return dict.fromkeys(skus, 25)


class PaymentStub:
    """Demo payment provider. Charges nothing. One payment in 500 fails: a tiny baseline, as real ones have."""

    FAIL_EVERY = 500

    def __init__(self, sleep: Sleep, rng: random.Random) -> None:
        self._sleep = sleep
        self._rng = rng
        self.attempts = 0

    async def pay(self, amount: Decimal, currency: str) -> str:
        number = self.attempts
        self.attempts += 1
        await self._sleep(self._rng.uniform(0.15, 0.35))
        if number % self.FAIL_EVERY == self.FAIL_EVERY - 1:
            raise PaymentError("the demo payment provider did not answer (baseline: 1 payment in 500)")
        return f"demo-pay-{number + 1:06d}"


class Store:
    """Runs one checkout: price the cart, check stock, take the payment."""

    def __init__(self, faults: Faults, sleep: Sleep, rng: random.Random) -> None:
        self.faults = faults
        self.inventory = Inventory(sleep, rng)
        self.payments = PaymentStub(sleep, rng)
        self.orders = 0

    async def checkout(self, lines: list[Line], region: str, *, path: str, stock_from_cache: bool) -> Receipt:
        total = price_cart(lines, region, path, planted_bug=self.faults.on("rounding_bug"))
        skus = [line.sku for line in lines]
        missing = [sku for sku in skus if sku not in STOCK_CACHE] if stock_from_cache else skus
        if missing:
            await self.inventory.stock(missing, slow=self.faults.on("inventory_slow"))
        currency = REGIONS[region].currency
        payment = await self.payments.pay(total, currency)
        self.orders += 1
        return Receipt(order=f"JM-{self.orders:06d}", path=path, region=region, currency=currency, total=total,
                       stock_from="inventory" if missing else "cache", payment=payment)
