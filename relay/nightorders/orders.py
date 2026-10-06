"""Load and check tonight's orders. Code decides what is valid; the model only drafts.

An orders file is trusted only when:
  1. it passes the JSON schema (fixed menu of two actions, at most three orders),
  2. every target and signal is listed in ops/targets.yml,
  3. no order covers a signal on the always-wake floor,
  4. it expires no later than the on-call watch end (07:00),
  5. it was signed (merged or approved) by the on-call person, tonight, before it expired.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match

from .model import Action, Condition, OnCall, Order, Orders, Signature, Targets

# The schema ships inside the package so the relay container can load it.
SCHEMA_PATH = Path(__file__).with_name("night-orders.schema.json")

# The floor. Alerts on these signals always wake the on-call person, and no order may cover them.
# ops/targets.yml can add signals to this set, never remove these.
CODE_FLOOR = frozenset({"payment_error_rate"})
MENU = ("flag_set", "traffic_to_revision")


class OrdersError(ValueError):
    """Raised when an orders file cannot be trusted. Holds every problem found, in plain words."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def load_yaml(path: Path | str) -> dict:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if data is not None else {}


def _hhmm(text: str) -> time:
    hours, minutes = text.split(":")
    return time(int(hours), int(minutes))


def parse_oncall(data: dict) -> OnCall:
    return OnCall(
        user=str(data["user"]),
        display_name=str(data.get("display_name", data["user"])),
        timezone=ZoneInfo(str(data["timezone"])),
        watch_ends=_hhmm(str(data.get("watch_ends", "07:00"))),
        recheck_minutes=int(data.get("recheck_minutes", 10)),
        answer_timeout_minutes=int(data.get("answer_timeout_minutes", 8)),
        model_runs_per_night=int(data.get("model_runs_per_night", 3)),
    )


def parse_targets(data: dict) -> Targets:
    flags = {str(f["name"]): frozenset(str(e) for e in f.get("environments", [])) for f in data.get("flags", [])}
    services = {str(s["name"]): str(s["environment"]) for s in data.get("services", [])}
    signals = {
        str(name): frozenset(str(p) for p in (spec or {}).get("paths", []))
        for name, spec in (data.get("signals") or {}).items()
    }
    always_wake = frozenset(str(s) for s in data.get("always_wake", []))
    return Targets(flags=flags, services=services, signals=signals, always_wake=always_wake)


def floor_signals(targets: Targets) -> frozenset[str]:
    return CODE_FLOOR | targets.always_wake


def _schema_problems(data: dict) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    problems = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        if error.context:  # a oneOf failed: report the most relevant reason, not the whole object
            error = best_match(error.context)
        where = "/".join(str(p) for p in error.absolute_path) or "file"
        if "should not be valid under" in error.message and "above" in error.message + "below":
            continue  # covered by the plain check for exactly one threshold
        problems.append(f"{where}: {error.message}")
    return problems


def _plain_problems(data: dict) -> list[str]:
    """Plain-language checks that read better than the schema's own messages."""
    problems = []
    for item in data.get("orders") or []:
        when = item.get("when") if isinstance(item, dict) else None
        if isinstance(when, dict) and ("above" in when) == ("below" in when):
            problems.append(f"order {item.get('id')}: give exactly one of above or below")
        do = item.get("do") if isinstance(item, dict) else None
        if isinstance(do, dict) and do.get("action") not in MENU:
            problems.append(f"order {item.get('id')}: action {do.get('action')} is not on the menu ({', '.join(MENU)})")
    return problems


def parse_action(data: dict) -> Action:
    if data["action"] == "flag_set":
        return Action(kind="flag_set", flag=data["flag"], environment=data["environment"], to=data["to"])
    return Action(kind="traffic_to_revision", service=data["service"], revision=data["revision"])


def action_problems(action: Action, targets: Targets) -> list[str]:
    """Check an action against the known targets. Used for orders and for suggestions."""
    if action.kind == "flag_set":
        if action.flag not in targets.flags:
            return [f"flag {action.flag} is not in ops/targets.yml"]
        if action.environment not in targets.flags[action.flag]:
            return [f"flag {action.flag} has no {action.environment} environment in ops/targets.yml"]
        return []
    if action.kind == "traffic_to_revision":
        if action.service not in targets.services:
            return [f"service {action.service} is not in ops/targets.yml"]
        if not (action.revision or "").startswith(f"{action.service}-"):
            return [f"revision {action.revision} does not belong to service {action.service}"]
        return []
    return [f"action {action.kind} is not on the menu ({', '.join(MENU)})"]


def parse_orders(data: dict, targets: Targets, oncall: OnCall) -> Orders:
    """Turn a loaded YAML document into Orders, or raise OrdersError listing every problem."""
    # YAML reads a bare off/on as false/true. Accept that spelling for the flag value only.
    for item in data.get("orders") or []:
        do = item.get("do") if isinstance(item, dict) else None
        if isinstance(do, dict) and isinstance(do.get("to"), bool):
            do["to"] = "on" if do["to"] else "off"
    problems = _plain_problems(data) + _schema_problems(data)
    if problems:
        raise OrdersError(problems)

    floor = floor_signals(targets)
    orders: list[Order] = []
    seen: set[int] = set()
    for item in data["orders"]:
        order_id = int(item["id"])
        label = f"order {order_id}"
        if order_id in seen:
            problems.append(f"{label}: the id is used twice")
        seen.add(order_id)

        when = item["when"]
        condition = Condition(
            signal=when["signal"],
            path=when.get("path"),
            above=when.get("above"),
            below=when.get("below"),
            for_minutes=int(when["for_minutes"]),
        )
        if condition.signal in floor:
            problems.append(
                f"{label}: {condition.signal.replace('_', ' ')} always wakes the on-call person, so no order may cover it"
            )
        if condition.signal not in targets.signals:
            problems.append(f"{label}: signal {condition.signal} is not in ops/targets.yml")
        else:
            paths = targets.signals[condition.signal]
            if paths and condition.path not in paths:
                problems.append(f"{label}: {condition.signal} needs a path, one of {', '.join(sorted(paths))}")
            if not paths and condition.path:
                problems.append(f"{label}: {condition.signal} has no paths")

        action = parse_action(item["do"])
        problems.extend(f"{label}: {p}" for p in action_problems(action, targets))
        orders.append(Order(id=order_id, because=str(item["because"]).strip(), when=condition, do=action))

    expires = _hhmm(data["expires"])
    if expires > oncall.watch_ends:
        problems.append(f"expires {data['expires']} is later than the watch end {oncall.watch_ends:%H:%M}")

    for first in orders:
        for second in orders:
            if first.id < second.id and first.do.same_target(second.do):
                problems.append(f"orders {first.id} and {second.id} both change {first.do.describe()}")

    if problems:
        raise OrdersError(problems)
    return Orders(
        night=date.fromisoformat(data["night"]),
        expires=expires,
        orders=tuple(orders),
        drafted_by=data.get("drafted_by"),
    )


def watch_window(orders: Orders, oncall: OnCall) -> tuple[datetime, datetime]:
    """Orders can be signed from noon on the night's date and end at the expiry the next morning."""
    start = datetime.combine(orders.night, time(12, 0), tzinfo=oncall.timezone)
    end = datetime.combine(orders.night + timedelta(days=1), orders.expires, tzinfo=oncall.timezone)
    return start, end


def signature_problems(orders: Orders, signature: Signature | None, oncall: OnCall, now: datetime) -> list[str]:
    """Why these orders may not be used right now. An empty list means they may."""
    start, end = watch_window(orders, oncall)
    if now >= end:
        return [f"Tonight's orders expired at {oncall.hhmm(end)}."]
    if signature is None:
        return ["Nobody signed tonight's orders."]
    problems = []
    if signature.user != oncall.user:
        problems.append(f"The orders were signed by {signature.user}, not by the on-call person ({oncall.user}).")
    if not start <= signature.at < end:
        problems.append("The orders were signed outside tonight's window.")
    if signature.at > now:
        problems.append("The signature is dated in the future.")
    return problems


def load_context(ops_dir: Path | str):
    """Load on-call and targets from an ops directory. Returns (oncall, targets)."""
    ops = Path(ops_dir)
    return parse_oncall(load_yaml(ops / "oncall.yml")), parse_targets(load_yaml(ops / "targets.yml"))


def validate_file(orders_path: Path | str, ops_dir: Path | str) -> list[str]:
    """For CI: every problem with an orders file, or an empty list when it can be signed."""
    oncall, targets = load_context(ops_dir)
    try:
        parse_orders(load_yaml(orders_path), targets, oncall)
    except OrdersError as error:
        return error.problems
    return []
