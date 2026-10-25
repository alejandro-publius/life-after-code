"""Demo Beans: a small demo shop for walking a checkout by keyboard. Not a real store.

Pages are plain HTML templates. A variant (a planted change used by the bench) overrides
templates by file name; the variant is chosen per browser session with a cookie, so one
server can serve every variant. No payment is taken and no data leaves the process.

Run: uv run uvicorn nomouse.shop.app:app --port 8090
"""

from __future__ import annotations

import os
import re
import string
from html import escape
from pathlib import Path

from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

TEMPLATES = Path(__file__).parent / "templates"
VARIANT_COOKIE = "nm_variant"
SESSION_COOKIE = "nm_session"
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")

PRODUCT = {"id": "ethiopia", "name": "Ethiopia Yirgacheffe", "size": "12 ounces", "price": "$18.00"}


def create_app(variants_dir: Path | None = None) -> FastAPI:
    """Build the shop. variants_dir holds <variant>/templates/<page>.html overrides."""
    app = FastAPI(title="Demo Beans (demo shop)", docs_url=None, redoc_url=None, openapi_url=None)
    carts: dict[str, int] = {}
    orders: dict[str, list[dict]] = {}

    def session_of(request: Request) -> str:
        value = request.cookies.get(SESSION_COOKIE, "")
        return value if _NAME.match(value) else "anonymous"

    def load(request: Request, name: str) -> string.Template:
        variant = request.cookies.get(VARIANT_COOKIE, "")
        if variants_dir is not None and _NAME.match(variant):
            candidate = variants_dir / variant / "templates" / name
            if candidate.is_file():
                return string.Template(candidate.read_text(encoding="utf-8"))
        path = TEMPLATES / name
        if not path.is_file():
            raise FileNotFoundError(name)
        return string.Template(path.read_text(encoding="utf-8"))

    async def form(request: Request) -> dict[str, str]:
        # The shop's forms are small URL-encoded posts; no multipart parser is needed.
        body = (await request.body())[:16_384].decode("utf-8", "replace")
        return {key: values[0] for key, values in parse_qs(body).items()}

    def has_template(request: Request, name: str) -> bool:
        try:
            load(request, name)
        except FileNotFoundError:
            return False
        return True

    def render(request: Request, name: str, title: str, **values: str) -> HTMLResponse:
        count = carts.get(session_of(request), 0)
        common = {
            "product_id": PRODUCT["id"], "product_name": PRODUCT["name"], "product_size": PRODUCT["size"],
            "price": PRODUCT["price"], "cart_count": str(count),
            "cart_label": f"Cart, {count} item" + ("" if count == 1 else "s"),
        }
        common.update({key: escape(value) for key, value in values.items()})
        body = load(request, name).safe_substitute(common)
        page = load(request, "layout.html").safe_substitute(common, title=escape(title), body=body)
        return HTMLResponse(page, headers={"Cache-Control": "no-store"})

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return render(request, "home.html", "Demo Beans")

    @app.get("/product/ethiopia", response_class=HTMLResponse)
    def product(request: Request) -> HTMLResponse:
        return render(request, "product.html", PRODUCT["name"])

    @app.post("/cart/add")
    def add_to_cart(request: Request) -> Response:
        session = session_of(request)
        carts[session] = carts.get(session, 0) + 1
        return RedirectResponse("/cart", status_code=303)

    @app.get("/cart", response_class=HTMLResponse)
    def cart(request: Request) -> HTMLResponse:
        if not carts.get(session_of(request)):
            return render(request, "cart_empty.html", "Your cart")
        return render(request, "cart.html", "Your cart", quantity=str(carts[session_of(request)]))

    @app.get("/checkout", response_class=HTMLResponse)
    def checkout(request: Request) -> Response:
        if not carts.get(session_of(request)):
            return RedirectResponse("/cart", status_code=303)
        return render(request, "checkout.html", "Checkout")

    @app.post("/review", response_class=HTMLResponse)
    async def review(request: Request) -> Response:
        # Only variants that add a review step provide review.html.
        fields = await form(request)
        if not carts.get(session_of(request)) or not has_template(request, "review.html"):
            return RedirectResponse("/cart", status_code=303)
        return render(request, "review.html", "Review your order",
                      email=fields.get("email", ""), card=fields.get("card", ""))

    @app.post("/pay")
    async def pay(request: Request) -> Response:
        fields = await form(request)
        email, card = fields.get("email", ""), fields.get("card", "")
        session = session_of(request)
        quantity = carts.get(session, 0)
        if not quantity or not email.strip() or not card.strip():
            return render(request, "checkout_error.html", "Checkout")
        number = f"DB-{len(orders.get(session, [])) + 1:04d}"
        orders.setdefault(session, []).append({"number": number, "item": PRODUCT["id"], "quantity": quantity})
        carts[session] = 0
        return RedirectResponse(f"/confirm?order={number}", status_code=303)

    @app.get("/confirm", response_class=HTMLResponse)
    def confirm(request: Request, order: str = "") -> HTMLResponse:
        return render(request, "confirm.html", "Order placed", order_number=order[:16])

    @app.get("/test/orders")
    def test_orders(session: str) -> JSONResponse:
        """Test oracle for the walker: orders placed in one walk session. Demo data only."""
        return JSONResponse({"session": session, "orders": orders.get(session, []) if _NAME.match(session) else []})

    return app


def _variants_from_env() -> Path | None:
    value = os.environ.get("NOMOUSE_VARIANTS_DIR", "")
    return Path(value) if value else None


app = create_app(_variants_from_env())
