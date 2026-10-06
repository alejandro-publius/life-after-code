"""DEMO DATA for Juniper Market: the products, the regions with their fixed demo rates, and the stock cache.

None of this is a real shop's data. Every price except the jam is a multiple of 0.20, so it keeps two
decimals in every region. The jam does not: 16.46 USD is 12.345 GBP after the region step, the price the
planted demo fault rounding_bug cannot round.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Region:
    currency: str
    rate: Decimal  # the region step: list price in USD times this demo rate
    step: Decimal  # the new checkout path rounds to a multiple of this


REGIONS: dict[str, Region] = {
    "us": Region("USD", Decimal("1.00"), Decimal("0.01")),
    "uk": Region("GBP", Decimal("0.75"), Decimal("0.01")),
    "eu": Region("EUR", Decimal("0.90"), Decimal("0.01")),
    "ca": Region("CAD", Decimal("1.40"), Decimal("0.05")),
}


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: Decimal  # USD list price


CATALOG: dict[str, Product] = {p.sku: p for p in (
    Product("juniper-tea", "Juniper berry tea", Decimal("8.00")),
    Product("cedar-candle", "Cedar candle", Decimal("14.00")),
    Product("trail-mix", "Trail mix", Decimal("6.40")),
    Product("wool-socks", "Wool socks", Decimal("18.00")),
    Product("camp-mug", "Enamel camp mug", Decimal("12.20")),
    Product("juniper-jam", "Juniper jam", Decimal("16.46")),
)}

# The small stock cache read when stock_from_cache is on (demo numbers, as of the last sync).
STOCK_CACHE: dict[str, int] = dict.fromkeys(CATALOG, 40)
