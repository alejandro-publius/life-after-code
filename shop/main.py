"""Juniper Market: the demo shop that Night Orders protects. DEMO DATA: simulated customers, planted faults.

Run from this folder, as the deploy image does:  python -m uvicorn main:app --port 8080

Two checkout paths sit behind the GitLab feature flag new_checkout, stock can come from a cache behind
stock_from_cache, two planted demo faults can be switched on, and /metrics.json reports per-minute signals
for the relay. Environment variables and endpoints are listed in README.md.
"""

import asyncio
import hmac
import os
import random
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Awaitable, Callable, Mapping

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

import jsonlog
import page
from checkout import Line, PaymentError, Store
from demo_catalog import CATALOG, REGIONS
from demo_traffic import LABEL as TRAFFIC_LABEL
from demo_traffic import MAX_MINUTES, PER_MINUTE, TrafficLoop
from faults import FAULTS, LABEL, Faults, UnknownFault
from flags import FlagClient
from metrics import Metrics

UNCOUNTED = ("/healthz", "/metrics.json")  # polled by machines, not customers
ON_WORDS = ("on", "true", "1", "yes")
OFF_WORDS = ("off", "false", "0", "no")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_switches(text: str | None, *, bare_means_on: bool = False) -> tuple[dict[str, bool], list[str]]:
    """Parse "new_checkout=on,stock_from_cache=off". With bare_means_on, "rounding_bug" alone means on."""
    values: dict[str, bool] = {}
    problems: list[str] = []
    for part in (text or "").split(","):
        part = part.strip()
        if not part:
            continue
        name, sep, value = (x.strip() for x in part.partition("="))
        if name and not sep and bare_means_on:
            values[name] = True
        elif name and value.lower() in ON_WORDS:
            values[name] = True
        elif name and value.lower() in OFF_WORDS:
            values[name] = False
        else:
            problems.append(f"ignored {part!r}: write name=on or name=off")
    return values, problems


@dataclass(frozen=True)
class Settings:
    unleash_url: str = ""
    unleash_instance_id: str = ""
    environment: str = "production"
    demo_key: str = ""
    flags_override: dict[str, bool] = field(default_factory=dict)
    faults: dict[str, bool] = field(default_factory=dict)
    problems: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Settings":
        overrides, bad_flags = parse_switches(env.get("FLAGS_OVERRIDE"))
        faults, bad_faults = parse_switches(env.get("FAULTS"), bare_means_on=True)
        unknown = sorted(set(faults) - set(FAULTS))
        return cls(
            unleash_url=env.get("UNLEASH_URL", "").strip(),
            unleash_instance_id=env.get("UNLEASH_INSTANCE_ID", "").strip(),
            environment=env.get("APP_ENV", "").strip() or "production",
            demo_key=env.get("DEMO_KEY", ""),
            flags_override=overrides,
            faults={name: on for name, on in faults.items() if name in FAULTS},
            problems=tuple([f"FLAGS_OVERRIDE {p}" for p in bad_flags] + [f"FAULTS {p}" for p in bad_faults]
                           + [f"FAULTS ignored unknown fault {name!r}" for name in unknown]),
        )


class ItemIn(BaseModel):
    sku: str = Field(min_length=1, max_length=40)
    price: float = Field(gt=0, le=10_000, description="US dollar list price")
    qty: int = Field(default=1, ge=1, le=20)


class CheckoutIn(BaseModel):
    user: str = Field(min_length=1, max_length=64)
    region: str = Field(description="us, uk, eu or ca")
    items: list[ItemIn] = Field(min_length=1, max_length=20)

    @field_validator("region")
    @classmethod
    def known_region(cls, value: str) -> str:
        if value not in REGIONS:
            raise ValueError(f"region must be one of {', '.join(REGIONS)}")
        return value


@dataclass
class ShopState:
    settings: Settings
    flags: FlagClient
    faults: Faults
    store: Store
    metrics: Metrics
    traffic: TrafficLoop
    clock: Callable[[], datetime]


class CountRequests:
    """ASGI middleware: every request except health checks and metrics polls counts toward http_5xx_ratio."""

    def __init__(self, app, metrics: Metrics) -> None:
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope["path"] in UNCOUNTED:
            await self.app(scope, receive, send)
            return
        status = 500

        async def send_and_note(message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_and_note)
        finally:
            self.metrics.http(status)


async def require_demo_key(request: Request) -> None:
    expected = request.app.state.shop.settings.demo_key
    if not expected:
        raise HTTPException(403, "Demo controls are off: DEMO_KEY is not set on this service.")
    given = request.headers.get("x-demo-key") or request.headers.get("demo_key") or ""
    if not hmac.compare_digest(given.encode(), expected.encode()):
        raise HTTPException(401, "Wrong or missing X-Demo-Key header.")


def _ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0


def create_app(
    settings: Settings | None = None,
    *,
    flags: FlagClient | None = None,
    clock: Callable[[], datetime] | None = None,
    sleep: Callable[[float], Awaitable[None]] | None = None,
    seed: int | None = None,
) -> FastAPI:
    """Build the shop. Tests pass their own settings, flag client, clock and sleep."""
    settings = settings or Settings.from_env()
    clock = clock or utcnow
    sleep = sleep or asyncio.sleep
    rng = random.Random(seed)
    flags = flags or FlagClient(settings.unleash_url, settings.unleash_instance_id, settings.environment,
                                overrides=settings.flags_override, now=clock, rng=rng)
    faults = Faults()
    metrics = Metrics(clock)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        for problem in settings.problems:
            jsonlog.emit("WARNING", f"Setting {problem}")
        if settings.unleash_url and not settings.unleash_instance_id:
            jsonlog.emit("WARNING", "UNLEASH_URL is set but UNLEASH_INSTANCE_ID is not: every flag stays off")
        jsonlog.emit("INFO", "Juniper Market demo shop started", environment=settings.environment,
                     flags={name: flags.source(name) for name in flags.names()}, faults=faults.active())
        if flags.configured:
            await flags.refresh()
        yield
        await shop.traffic.stop()

    app = FastAPI(title="Juniper Market (demo shop)", lifespan=lifespan,
                  description="DEMO SHOP: simulated customers and planted faults. Nothing is charged or shipped.")
    traffic = TrafficLoop(
        lambda: httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://juniper-market.demo",
                                  headers={"X-Demo-Traffic": TRAFFIC_LABEL}, timeout=30.0),
        lambda user: flags.is_on("new_checkout", user),
        now=clock)  # paced by real time; `sleep` only stands in for the simulated service latency
    shop = ShopState(settings=settings, flags=flags, faults=faults, store=Store(faults, sleep, rng),
                     metrics=metrics, traffic=traffic, clock=clock)
    app.state.shop = shop
    app.add_middleware(CountRequests, metrics=metrics)
    if settings.faults:
        faults.set(settings.faults, source="FAULTS env var")

    @app.get("/", response_class=HTMLResponse)
    async def home() -> HTMLResponse:
        flags.maybe_refresh()
        html = page.render(environment=settings.environment, commit=_commit(), flags=flags, faults=faults,
                           traffic=traffic, minutes=metrics.complete(10), started=metrics.started, now=clock())
        return HTMLResponse(html)

    @app.get("/products")
    async def products() -> dict:
        return {"label": "demo catalog", "currency": "USD",
                "products": [{"sku": p.sku, "name": p.name, "price": float(p.price)} for p in CATALOG.values()]}

    @app.post("/checkout")
    async def checkout(order: CheckoutIn, request: Request) -> JSONResponse:
        started = time.perf_counter()
        flags.maybe_refresh()
        path = "new" if flags.is_on("new_checkout", order.user) else "old"
        use_cache = flags.is_on("stock_from_cache", order.user)
        source = TRAFFIC_LABEL if request.headers.get("x-demo-traffic") else "manual request"
        lines = [Line(item.sku, Decimal(str(item.price)), item.qty) for item in order.items]
        try:
            receipt = await shop.store.checkout(lines, order.region, path=path, stock_from_cache=use_cache)
        except Exception as exc:  # every failure becomes one log line and one counted error
            status = 504 if isinstance(exc, TimeoutError) else 502 if isinstance(exc, PaymentError) else 500
            fault = getattr(exc, "planted_fault", None)
            tags = {"fault": fault, "label": LABEL} if fault else {}
            jsonlog.error(exc, f"{path} checkout path", path=path, user=order.user, region=order.region,
                          http_status=status, traffic=source, **tags)
            metrics.checkout(path, False, _ms(started))
            if isinstance(exc, PaymentError):
                metrics.payment(False)
            body = {"ok": False, "path": path, "error": str(exc)}
            if fault:
                body["fault"] = f"{fault} ({LABEL})"
            return JSONResponse(body, status_code=status)
        metrics.checkout(path, True, _ms(started))
        metrics.payment(True)
        return JSONResponse({
            "ok": True, "order": receipt.order, "path": path, "region": receipt.region,
            "currency": receipt.currency, "total": f"{receipt.total:.2f}", "stock_from": receipt.stock_from,
            "payment": receipt.payment, "label": "demo order: nothing is charged or shipped",
        })

    @app.get("/metrics.json")
    async def metrics_json() -> dict:
        return {"label": page.BANNER, "environment": settings.environment, "minutes": metrics.report()}

    @app.post("/demo/faults", dependencies=[Depends(require_demo_key)])
    async def set_faults(changes: dict[str, bool] = Body(..., examples=[{"rounding_bug": True}])) -> dict:
        try:
            state = faults.set(changes, source="POST /demo/faults")
        except UnknownFault as exc:
            raise HTTPException(400, str(exc)) from None
        return {"faults": state, "active": faults.active(), "label": LABEL}

    @app.post("/demo/traffic", dependencies=[Depends(require_demo_key)])
    async def demo_traffic(minutes: int = Query(..., ge=0, le=MAX_MINUTES)) -> dict:
        if minutes == 0:
            await traffic.stop()
            return {"label": TRAFFIC_LABEL, "running": False}
        until = traffic.start(minutes)
        return {"label": TRAFFIC_LABEL, "running": True, "minutes": traffic.minutes,
                "until": until.isoformat(timespec="seconds").replace("+00:00", "Z"),
                "checkouts_per_minute": PER_MINUTE}

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"ok": True, "commit": _commit()}

    return app


def _commit() -> str:
    return os.environ.get("CI_COMMIT_SHORT_SHA") or "local"


app = create_app()
