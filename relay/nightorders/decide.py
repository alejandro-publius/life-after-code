"""The night decisions. Two keys must turn before anything changes in production:

  * code checks the numbers: a signed, unexpired, unused order whose condition holds right now;
  * the model checks the reason: the watch flow names that order in its request note.

Either key alone can wake the on-call person. Neither alone can act. The model can decline an
order or add a reason to wake; it can never add an order, widen one, or remove a reason to wake.
The action and its target always come from the signed file, never from the model's note.

Standing Orders is the fallback for a night without a model (the Flows API refused to start a
flow for this account, say): code's key alone turns. The first signed order whose numbers hold
runs as soon as triage finds it, with the same signature, expiry, numbers and first-use checks,
and the note on the incident says that no model looked at the reason.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from .ledger import Ledger
from .model import Action, Alert, OnCall, Order, Orders, Signature, Targets
from .notes import Malformed, parse_request, suggestion_action
from .orders import MENU, action_problems, floor_signals, signature_problems, watch_window
from .signals import Metrics, condition_holds, recheck_after_action

APPROVAL_WINDOW_MINUTES = 60
STANDING = "standing orders: no model tonight, so nobody checked the reason"


@dataclass(frozen=True)
class Night:
    oncall: OnCall
    targets: Targets
    orders: Orders | None
    orders_problems: tuple[str, ...]
    signature: Signature | None
    ledger: Ledger


@dataclass(frozen=True)
class Wake:
    reasons: tuple[str, ...]
    page: tuple[str, ...]
    suggest: Action | None = None


@dataclass(frozen=True)
class Ask:
    eligible: tuple[int, ...]
    checks: dict


@dataclass(frozen=True)
class Act:
    order: Order
    checks: tuple[str, ...]


@dataclass(frozen=True)
class StandDown:
    reason: str
    order: int | None = None  # the order whose numbers dipped; the watch wakes her if the incident stays open


@dataclass(frozen=True)
class Waiting:
    """No answer from the agent yet, and the time limit has not passed."""


def default_page(alerts: list[Alert], reasons: list[str], night: Night) -> tuple[str, ...]:
    """A three-line page written by code, used whenever the agent did not write one."""
    first = alerts[0] if alerts else None
    what = first.describe() if first else "An alert fired"
    since = f" since {night.oncall.hhmm(first.at)}" if first else ""
    lines = [f"{what[0].upper()}{what[1:]}{since}.", reasons[0] if reasons else "No signed order covers this."]
    lines.append("The incident has the evidence.")
    return tuple(lines)


def floor_reasons(alerts: list[Alert], night: Night, now: datetime) -> list[str]:
    """Reasons that always wake the on-call person, whatever was signed."""
    reasons = []
    floor = floor_signals(night.targets)
    for alert in alerts:
        if alert.signal in floor:
            label = "Payment errors" if alert.signal == "payment_error_rate" else alert.signal.replace("_", " ")
            reasons.append(f"{label} always wake you.")
            break
    if night.ledger.pending_recheck() is not None:
        reasons.append("A new alert arrived while an earlier action was still being re-checked.")
    if night.orders is not None:
        _, end = watch_window(night.orders, night.oncall)
        if now >= end:
            reasons.append(f"Tonight's orders expired at {night.oncall.hhmm(end)}.")
    return reasons


def thin_traffic(order: Order, detail: str, metrics: Metrics, now: datetime) -> str | None:
    """The reason to wake when an order's numbers match but the traffic behind them is too thin to act on."""
    if order.when.min_count and condition_holds(replace(order.when, min_count=None), metrics, now)[0]:
        return f"Order {order.id} matches the numbers, but {detail}."
    return None


def unusable(night: Night) -> list[str]:
    """Why there are no orders to use tonight, or nothing: no file, a file code refuses, or a reason the sources
    found that the file is not signed (an approval given before the commit it would sign)."""
    if night.orders is None or night.orders_problems:
        why = "; ".join(night.orders_problems) if night.orders_problems else "there is no orders file"
        return [f"No usable orders tonight ({why})."]
    return []


def triage(alerts: list[Alert], night: Night, metrics: Metrics, now: datetime) -> Wake | Ask:
    """Code's key. Decide whether to wake now, or ask the agent about the eligible orders."""
    reasons = floor_reasons(alerts, night, now)
    if reasons:
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    reasons = unusable(night)
    if reasons:
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    problems = signature_problems(night.orders, night.signature, night.oncall, now)
    if problems:
        return Wake(tuple(problems), default_page(alerts, problems, night))

    if not night.orders.orders:
        reasons = ["Nothing was signed for tonight, so every alert wakes you."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    eligible: list[int] = []
    checks: dict[int, str] = {}
    used: list[int] = []
    thin: list[str] = []
    for order in night.orders.orders:
        holds, detail = condition_holds(order.when, metrics, now)
        if not holds:
            # The numbers match but the traffic behind them is too thin to act on: say so on the page.
            reason = thin_traffic(order, detail, metrics, now)
            if reason:
                thin.append(reason)
            continue
        if night.ledger.used(order.id):
            used.append(order.id)
            continue
        eligible.append(order.id)
        checks[order.id] = detail

    if not eligible:
        if used:
            reasons = [f"Order {used[0]} already ran tonight; an order runs once."]
        elif thin:
            reasons = thin
        else:
            reasons = ["No signed order covers this alert."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    if night.ledger.model_runs() >= night.oncall.model_runs_per_night:
        reasons = [f"The agent was already asked {night.oncall.model_runs_per_night} times tonight."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    return Ask(eligible=tuple(eligible), checks=checks)


def check_request(note_text: str | None, ask: Ask, asked_at: datetime, alerts: list[Alert], night: Night,
                  metrics: Metrics, now: datetime) -> Act | Wake | StandDown | Waiting:
    """The model's key, checked by code. The note can only name an order or decline."""
    timeout = timedelta(minutes=night.oncall.answer_timeout_minutes)
    if note_text is None:
        if now - asked_at >= timeout:
            reasons = [f"The agent did not answer within {night.oncall.answer_timeout_minutes} minutes."]
            return Wake(tuple(reasons), default_page(alerts, reasons, night))
        return Waiting()

    request = parse_request(note_text)
    if isinstance(request, Malformed):
        reasons = [f"The agent's answer could not be read ({request.reason})."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    if request.order is None:
        reasons = []
        if request.declined_id is not None:
            reasons.append(f"The agent declined order {request.declined_id}: {request.declined_why}")
        else:
            reasons.append("The agent found no order that fits.")
        suggest = suggestion_action(request.suggest)
        if request.suggest and suggest is None:
            reasons.append("The agent suggested something code could not read, so there is nothing to approve.")
        elif suggest is not None and (suggest.kind not in MENU or action_problems(suggest, night.targets)):
            reasons.append(f"The agent suggested {suggest.describe()}, which is not a listed target, "
                           "so there is nothing to approve.")
            suggest = None
        page = request.page or default_page(alerts, reasons, night)
        return Wake(tuple(reasons), tuple(page), suggest)

    if request.order not in ask.eligible:
        reasons = [f"The agent asked for order {request.order}, which is not eligible right now."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    # Re-check everything at the moment of acting: time has passed since the ask, and the orders read now may
    # not be the ones that were signed then (a commit pushed after the approval, say).
    orders = night.orders
    problems = unusable(night)
    if orders is not None and not problems:
        problems = signature_problems(orders, night.signature, night.oncall, now)
    problems += floor_reasons(alerts, night, now)
    if problems:
        return Wake(tuple(problems), default_page(alerts, problems, night))
    assert orders is not None
    order = orders.get(request.order)
    assert order is not None
    if night.ledger.used(order.id):
        reasons = [f"Order {order.id} already ran tonight; an order runs once."]
        return Wake(tuple(reasons), default_page(alerts, reasons, night))
    holds, detail = condition_holds(order.when, metrics, now)
    if not holds:
        failed = [e.text for e in night.ledger.of("failed") if e.order == order.id]
        if failed:
            # The change raised when it was tried and may have gone through, so code cannot say nothing changed.
            reasons = [failed[-1]]
        else:
            thin = thin_traffic(order, detail, metrics, now)
            if not thin:
                return StandDown(f"Order {order.id} is no longer needed: {detail}. Nothing was changed.", order=order.id)
            reasons = [thin]  # the numbers did not dip: there is too little traffic to judge, as triage says
        return Wake(tuple(reasons), default_page(alerts, reasons, night))

    signature = night.signature
    assert signature is not None
    _, end = watch_window(orders, night.oncall)
    checks = (
        f"signed by {night.oncall.first_name} at {night.oncall.hhmm(signature.at)} ({signature.method})",
        f"not expired (ends {night.oncall.hhmm(end)})",
        detail,
        "action and target taken from the signed file",
        "first use tonight",
    )
    return Act(order=order, checks=checks)


def standing_order(ask: Ask, night: Night) -> Act:
    """Standing Orders: with no model at night, the first eligible order runs on code's key alone.

    triage checked the signature, the expiry, the numbers and the first use a moment ago; the checks
    name them, and say plainly that no model checked the reason.
    """
    orders, signature = night.orders, night.signature
    assert orders is not None and signature is not None
    order = orders.get(ask.eligible[0])
    assert order is not None
    _, end = watch_window(orders, night.oncall)
    checks = (
        f"signed by {night.oncall.first_name} at {night.oncall.hhmm(signature.at)} ({signature.method})",
        f"not expired (ends {night.oncall.hhmm(end)})",
        ask.checks[order.id],
        "action and target taken from the signed file",
        "first use tonight",
        STANDING,
    )
    return Act(order=order, checks=checks)


def recheck(order: Order, night: Night, metrics: Metrics, now: datetime) -> tuple[bool, str]:
    """After an action: recovered means no page; anything else wakes the on-call person. An emptied path never
    counts as recovered on its own: the whole shop has to be back too (signals.recheck_after_action)."""
    return recheck_after_action(order.when, metrics, now)


def approve_suggestion(suggestion: Action, reaction_user: str, reaction_at: datetime, paged_at: datetime,
                       night: Night, now: datetime | None = None) -> tuple[bool, str]:
    """A thumbs-up on the page note approves the one suggested action, if code agrees it may.

    now is when code would make the change. Once tonight's orders have ended it never does: the morning makes its
    record of the night then, and a change made later would reach neither the record nor the countersign.
    """
    if reaction_user != night.oncall.user:
        return False, f"The reaction came from {reaction_user}, not the on-call person."
    if reaction_at < paged_at:
        return False, "The reaction is older than the page."
    if reaction_at > paged_at + timedelta(minutes=APPROVAL_WINDOW_MINUTES):
        return False, f"The reaction came more than {APPROVAL_WINDOW_MINUTES} minutes after the page."
    if now is not None and night.orders is not None:
        _, end = watch_window(night.orders, night.oncall)
        if now >= end:
            return False, f"Tonight's orders ended at {night.oncall.hhmm(end)}; approve it by hand."
    if suggestion.kind not in MENU:
        return False, f"{suggestion.kind} is not on the menu."
    problems = action_problems(suggestion, night.targets)
    if problems:
        return False, problems[0]
    return True, f"Approved by {night.oncall.first_name} at {night.oncall.hhmm(reaction_at)}."
