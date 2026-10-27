"""Disposable loopback shop controls. This module is never used by the production app."""

import hmac
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from main import Settings, create_app

KEY = os.environ.get("LOCAL_SHOP_KEY", "")
IDENTITY = os.environ.get("LOCAL_SHOP_ID", "")
if not KEY or not IDENTITY:
    raise RuntimeError("Start the disposable shop with scripts/run_local.py")

clock = [datetime.now(timezone.utc).replace(hour=22, minute=0, second=0, microsecond=0)]
app = create_app(Settings(environment="local", flags_override={"new_checkout": True, "stock_from_cache": False}),
                 clock=lambda: clock[0], seed=1)


def authorize(request: Request):
    if request.client.host not in ("127.0.0.1", "::1") or not hmac.compare_digest(
            request.headers.get("x-local-shop-key", ""), KEY):
        raise HTTPException(403, "Disposable shop control refused")


def snapshot():
    shop = app.state.shop
    return {"identity": IDENTITY, "clock": clock[0].isoformat(),
            "flags": {name: "on" if shop.flags.is_on(name) else "off"
                      for name in ("new_checkout", "stock_from_cache")},
            "faults": shop.faults.active()}


class Flag(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: bool


class Advance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: int = 1


@app.get("/local/state", dependencies=[Depends(authorize)])
def state():
    return snapshot()


@app.post("/local/flag", dependencies=[Depends(authorize)])
def flag(body: Flag):
    app.state.shop.flags.overrides["new_checkout"] = body.value
    return snapshot()


@app.post("/local/fault", dependencies=[Depends(authorize)])
def fault(body: Flag):
    app.state.shop.faults.set({"rounding_bug": body.value}, source="local disposable session")
    return snapshot()


@app.post("/local/advance", dependencies=[Depends(authorize)])
def advance(body: Advance):
    if body.minutes != 1 or clock[0].hour == 23:
        raise HTTPException(409, "The local clock advances one minute within a bounded hour")
    clock[0] += timedelta(minutes=1)
    return snapshot()
