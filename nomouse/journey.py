"""A journey is a recorded keyboard path written in what a screen reader announces.

Replay is code only. It decides whether a person relying on a screen reader could finish:
every control is reached by Tab and recognised by its announced role and name, nothing
unnamed is pressed, the key budget holds, and the shop's test oracle confirms the order.

When a replay breaks, evidence() returns a short, bounded block for whoever has to judge
it next (a person, a baseline or a model). Page text inside it is data, not instructions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import json
from pathlib import Path
import re
from typing import Any

import yaml

from nomouse.announce import Announcement
from nomouse.guards import FIELDS, press_violation

MAX_TABS_PER_FIND = 40
EVIDENCE_LIMIT = 8_000  # bytes; the Duo flow reads the end of a job log, so keep this small
EVIDENCE_BEGIN = "NOMOUSE-EVIDENCE-BEGIN"
EVIDENCE_END = "NOMOUSE-EVIDENCE-END"
KEYS = {"Enter", "Space", "Escape", "ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight", "Home", "End"}
PAGE_TEMPLATES = {"/": "home.html", "/product/ethiopia": "product.html", "/cart": "cart.html",
                  "/checkout": "checkout.html", "/review": "review.html", "/pay": "checkout_error.html",
                  "/confirm": "confirm.html"}


class JourneyError(ValueError):
    """A journey file or a proposed path is malformed. Nothing is replayed."""


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().casefold()


@dataclass(frozen=True)
class Step:
    do: str  # find | press | type | expect_heading
    role: str = ""
    name: str = ""
    key: str = ""
    text: str = ""

    def describe(self) -> str:
        if self.do == "find":
            return f'Tab to "{self.name}, {self.role}"'
        if self.do == "press":
            return f"press {self.key}"
        if self.do == "type":
            return f'type "{self.text}"'
        return f'hear heading "{self.name}"'

    def as_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if value}


def parse_step(raw: Any) -> Step:
    if not isinstance(raw, dict):
        raise JourneyError("each step must be a mapping")
    allowed = {"do", "role", "name", "key", "text"}
    extra = set(raw) - allowed
    if extra:
        raise JourneyError(f"unknown step keys: {sorted(extra)}")
    step = Step(**{key: str(value) for key, value in raw.items()})
    if step.do == "find":
        if not step.role or not step.name:
            raise JourneyError("find needs a role and a name")
    elif step.do == "press":
        if step.key not in KEYS:
            raise JourneyError(f"press key must be one of {sorted(KEYS)}")
    elif step.do == "type":
        if not step.text or len(step.text) > 200:
            raise JourneyError("type needs text of at most 200 characters")
    elif step.do == "expect_heading":
        if not step.name:
            raise JourneyError("expect_heading needs a name")
    else:
        raise JourneyError(f"unknown step: {step.do!r}")
    return step


@dataclass(frozen=True)
class Journey:
    name: str
    start: str
    steps: tuple[Step, ...]
    order_item: str
    order_quantity: int
    key_budget: int

    def with_steps(self, steps: list[Step]) -> "Journey":
        return replace(self, steps=tuple(steps))


def load_journey(path: Path) -> Journey:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list) or not data["steps"]:
        raise JourneyError("a journey needs a name, a start path and steps")
    order = data.get("order") or {}
    return Journey(
        name=str(data.get("name", path.stem)), start=str(data.get("start", "/")),
        steps=tuple(parse_step(step) for step in data["steps"]),
        order_item=str(order.get("item", "")), order_quantity=int(order.get("quantity", 1)),
        key_budget=int(data.get("key_budget", 120)),
    )


@dataclass
class Result:
    verdict: str  # clear | broken | refused | no_order | over_budget
    failed_step: int | None = None
    reason: str = ""
    keys: int = 0
    trace: list[str] = field(default_factory=list)
    heard: list[Announcement] = field(default_factory=list)  # tab order on the page where it broke
    headings: list[Announcement] = field(default_factory=list)
    page: str = ""
    orders: list[dict] = field(default_factory=list)

    @property
    def clear(self) -> bool:
        return self.verdict == "clear"


def _matches(heard: Announcement, step: Step) -> bool:
    return heard.role == step.role and _norm(heard.name) == _norm(step.name)


def replay(walk, journey: Journey, *, collect_evidence: bool = True) -> Result:
    """Walk the journey with the keyboard. Code alone decides the verdict."""
    result = Result(verdict="clear")
    walk.goto(journey.start)
    result.trace.append(f"open {journey.start}: {walk.focused().spoken()}")
    for index, step in enumerate(journey.steps):
        problem = _do(walk, step, result)
        if walk.keys > journey.key_budget:
            result.verdict, result.failed_step = "over_budget", index
            result.reason = f"used {walk.keys} keys; the budget is {journey.key_budget}"
        elif problem:
            result.verdict, result.failed_step, result.reason = problem[0], index, problem[1]
        if result.verdict != "clear":
            break
    result.keys = walk.keys
    result.page = walk.path
    if result.verdict == "clear":
        result.orders = walk.orders()
        placed = [o for o in result.orders
                  if o.get("item") == journey.order_item and o.get("quantity") == journey.order_quantity]
        if len(placed) != 1:
            result.verdict, result.failed_step = "no_order", len(journey.steps) - 1
            result.reason = f"the shop recorded {len(result.orders)} order(s), not one {journey.order_item}"
    if not result.clear and collect_evidence:
        result.headings = walk.headings()
        result.heard = walk.tab_order()
    return result


def _do(walk, step: Step, result: Result) -> tuple[str, str] | None:
    if step.do == "find":
        now = walk.focused()
        seen: set[str] = set()
        for _ in range(MAX_TABS_PER_FIND):
            if _matches(now, step):
                result.trace.append(f"heard {now.spoken()}")
                return None
            if now.node and now.node in seen and not now.is_page:
                break  # focus came back round without the control
            if now.node:
                seen.add(now.node)
            now = walk.press("Tab")
        return "broken", f'never heard "{step.name}, {step.role}" while tabbing through {walk.path}'
    if step.do == "press":
        focused = walk.focused()
        if step.key in ("Enter", "Space"):
            refused = press_violation(focused)
            if refused:
                return "refused", refused
        after = walk.press(step.key)
        result.trace.append(f"pressed {step.key} on {focused.spoken()}; now {after.spoken()} at {walk.path}")
        return None
    if step.do == "type":
        focused = walk.focused()
        if focused.role not in FIELDS:
            return "broken", f'tried to type into "{focused.spoken()}", which is not a field'
        walk.type(step.text)
        result.trace.append(f'typed into {focused.name or "an unnamed field"}')
        return None
    headings = walk.headings()
    if any(h.role == "heading" and _norm(h.name) == _norm(step.name) for h in headings):
        result.trace.append(f'heard heading "{step.name}"')
        return None
    names = ", ".join(h.spoken() for h in headings) or "no headings"
    return "broken", f'expected heading "{step.name}" at {walk.path}; heard {names}'


def evidence(journey: Journey, result: Result, *, template_files: list[str] | None = None) -> dict:
    """A bounded, structured summary of a failed walk. Page text inside it is untrusted data."""
    failed = result.failed_step
    block = {
        "journey": journey.name,
        "verdict": result.verdict,
        "reason": result.reason,
        "failed_step": failed,
        "expected": journey.steps[failed].describe() if failed is not None else None,
        "steps": [f"{i}: {s.describe()}" for i, s in enumerate(journey.steps)],
        "page": result.page,
        "template_files": template_files or ([f"nomouse/shop/templates/{PAGE_TEMPLATES[result.page]}"]
                                             if result.page in PAGE_TEMPLATES else []),
        "headings": [h.spoken() for h in result.headings][:12],
        "heard_in_tab_order": [h.spoken() for h in result.heard][:40],
        "heard_total": len(result.heard),
        "keys_used": result.keys,
        "key_budget": journey.key_budget,
        "last_events": result.trace[-6:],
    }
    if len(result.heard) > len(block["heard_in_tab_order"]):
        block["truncated"] = True  # never drop announcements without saying so
    text = json.dumps(block, ensure_ascii=False)
    while len(text.encode("utf-8")) > EVIDENCE_LIMIT and block["heard_in_tab_order"]:
        block["heard_in_tab_order"] = block["heard_in_tab_order"][:-1]
        block["truncated"] = True
        text = json.dumps(block, ensure_ascii=False)
    return block


def evidence_text(block: dict) -> str:
    """The block as printed at the end of a job log, between fixed markers."""
    return f"{EVIDENCE_BEGIN}\n{json.dumps(block, ensure_ascii=False, indent=1)}\n{EVIDENCE_END}"
