"""Local product HTTP surface. It deliberately has no production tick endpoint."""

import hmac
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from nightorders.local_session import LocalError, LocalSession
from nightorders import browser_demo, execution

WEB = Path(__file__).with_name("demo_web")
demo_replay = lru_cache(maxsize=8)(browser_demo.replay)


def create_app(session: LocalSession):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    def recorded_page(name):
        back = ('<nav aria-label="Return to local execution" style="padding:14px 24px;background:#fff8e9">'
                '<a href="/local">Return to your real local run</a>'
                ' · This view contains simulated replay or previously recorded sessions.</nav>')
        return HTMLResponse((WEB / name).read_text().replace("</header>", "</header>" + back, 1))

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        host = urlsplit("http://" + request.headers.get("host", "")).hostname
        if host not in ("127.0.0.1", "localhost"):
            return JSONResponse({"detail": "Loopback host required"}, status_code=403)
        if request.method == "POST":
            origin = request.headers.get("origin")
            if origin and origin != str(request.base_url).rstrip("/"):
                return JSONResponse({"detail": "Cross-origin write refused"}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "Cross-site write refused"}, status_code=403)
            if not hmac.compare_digest(request.headers.get("x-local-key", ""), session.data["csrf_token"]):
                return JSONResponse({"detail": "Local session key required"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/")
    @app.get("/local")
    def index():
        return FileResponse(WEB / "local.html")

    app.mount("/demo/assets", StaticFiles(directory=WEB), name="local-assets")
    app.mount("/local/assets", StaticFiles(directory=WEB), name="local-product-assets")

    @app.get("/demo")
    @app.get("/demo/")
    def demo():
        return recorded_page("index.html")

    @app.get("/demo/replay")
    def replay(signed: bool = True, approved: bool = True, keep_checkout: bool = True):
        return demo_replay(signed=signed, approved=approved, keep_checkout=keep_checkout)

    @app.get("/activity")
    @app.get("/activity/")
    def activity():
        return recorded_page("activity.html")

    @app.get("/activity.json")
    def activity_record():
        return execution.load_recording()

    @app.get("/local/api/state")
    def state():
        return session.view()

    @app.get("/local/api/receipt")
    def receipt():
        return JSONResponse(session.receipt(), headers={"Content-Disposition": "attachment; filename=local-session.json"})

    @app.post("/local/api/{operation}")
    async def act(operation: str, request: Request):
        if operation not in {"start", "authorize", "observe", "verify", "morning", "finish", "reload"}:
            raise HTTPException(404, "Unknown operation")
        try:
            body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        except ValueError as error:
            raise HTTPException(422, "Expected a JSON object") from error
        if not isinstance(body, dict) or set(body) - ({"choice"} if operation == "morning" else set()):
            raise HTTPException(422, "Unexpected local action fields")
        try:
            # FastAPI executes sync work in a worker so the state endpoint remains responsive between actions.
            from starlette.concurrency import run_in_threadpool
            return await run_in_threadpool(session.run, operation, body.get("choice"))
        except LocalError as error:
            raise HTTPException(409, str(error)) from error

    return app
