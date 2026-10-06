"""Read the agent's request note and write the relay's notes, pages and watch log.

The agent answers with exactly one fenced block:

    ```night-orders-request
    {"order": 1, "fits_because": "...", "declined": null, "page": null, "suggest": null}
    ```

Only the order id is ever used to act, and the action always comes from the signed file.
Anything else in the note is ignored. A note that does not parse wakes the on-call person.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .model import Action

FENCE = re.compile(r"```night-orders-request[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL)
ALLOWED_KEYS = {"order", "fits_because", "declined", "page", "suggest"}
MAX_PAGE_LINES = 3
MAX_LINE = 160


@dataclass(frozen=True)
class Request:
    order: int | None
    fits_because: str | None
    declined_id: int | None
    declined_why: str | None
    page: tuple[str, ...]
    suggest: dict | None


@dataclass(frozen=True)
class Malformed:
    reason: str


def parse_request(text: str) -> Request | Malformed:
    blocks = FENCE.findall(text or "")
    if len(blocks) != 1:
        return Malformed(f"expected one night-orders-request block, found {len(blocks)}")
    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as error:
        return Malformed(f"the block is not valid JSON ({error.msg})")
    if not isinstance(data, dict):
        return Malformed("the block is not a JSON object")
    extra = set(data) - ALLOWED_KEYS
    if extra:
        return Malformed(f"unexpected keys: {', '.join(sorted(extra))}")

    order = data.get("order")
    if order is not None and (isinstance(order, bool) or not isinstance(order, int)):
        return Malformed("order must be an integer or null")

    fits = data.get("fits_because")
    if fits is not None and not isinstance(fits, str):
        return Malformed("fits_because must be text or null")
    if order is not None and not (fits or "").strip():
        return Malformed("a request for an order must say why it fits")

    declined = data.get("declined")
    declined_id = declined_why = None
    if declined is not None:
        if not isinstance(declined, dict) or set(declined) - {"id", "why"}:
            return Malformed("declined must be an object with id and why")
        declined_id, declined_why = declined.get("id"), declined.get("why")
        if not isinstance(declined_id, int) or isinstance(declined_id, bool) or not isinstance(declined_why, str):
            return Malformed("declined needs an integer id and a reason")

    page = data.get("page") or []
    if isinstance(page, str):
        page = [line for line in page.splitlines() if line.strip()]
    if not isinstance(page, list) or not all(isinstance(line, str) for line in page):
        return Malformed("page must be a list of short lines")
    if len(page) > MAX_PAGE_LINES:
        return Malformed(f"page has {len(page)} lines; the limit is {MAX_PAGE_LINES}")
    page = [line.strip()[:MAX_LINE] for line in page]

    suggest = data.get("suggest")
    if suggest is not None and not isinstance(suggest, dict):
        return Malformed("suggest must be an object or null")
    if order is not None and (suggest or page):
        return Malformed("a request for an order cannot also page or suggest")

    return Request(
        order=order,
        fits_because=fits.strip() if isinstance(fits, str) else None,
        declined_id=declined_id,
        declined_why=declined_why.strip() if isinstance(declined_why, str) else None,
        page=tuple(page),
        suggest=suggest,
    )


def render_request(request: Request) -> str:
    """The note format the watch flow writes. Used by tests and the recorded demo notes."""
    body = {
        "order": request.order,
        "fits_because": request.fits_because,
        "declined": None
        if request.declined_id is None
        else {"id": request.declined_id, "why": request.declined_why},
        "page": list(request.page) or None,
        "suggest": request.suggest,
    }
    return "```night-orders-request\n" + json.dumps(body, indent=1) + "\n```"


def suggestion_action(suggest: dict | None) -> Action | None:
    """Turn a suggestion dict into an Action if it names a menu action with all its fields."""
    if not suggest:
        return None
    kind = suggest.get("action")
    if kind == "flag_set" and suggest.get("to") in ("on", "off"):
        if isinstance(suggest.get("flag"), str) and isinstance(suggest.get("environment"), str):
            return Action(kind="flag_set", flag=suggest["flag"], environment=suggest["environment"], to=suggest["to"])
    if kind == "traffic_to_revision":
        if isinstance(suggest.get("service"), str) and isinstance(suggest.get("revision"), str):
            return Action(kind="traffic_to_revision", service=suggest["service"], revision=suggest["revision"])
    return None
