"""The morning: a watch log written by code from the night's record, and the loose ends.

The dawn flow (the model) reads this log and proposes keep or undo for each loose end in
ops/state.yml. The facts in the log come from the ledger, not from the model.
"""

from __future__ import annotations

from .decide import Night
from .model import Action

SHOWN = ("alert", "asked", "acted", "declined", "woke", "approved", "refused", "recovered", "stood_down", "expired")


def loose_ends(night: Night) -> list[tuple[Action, str]]:
    """State changed tonight and not changed back: (action, why) in the order they happened."""
    latest: dict[tuple, tuple[Action, str]] = {}
    for event in night.ledger.events:
        if event.kind not in ("acted", "approved"):
            continue
        data = event.data.get("action")
        if not data:
            continue
        if data["action"] == "flag_set":
            action = Action(kind="flag_set", flag=data["flag"], environment=data["environment"], to=data["to"])
            target = ("flag", action.flag, action.environment)
        else:
            action = Action(kind="traffic_to_revision", service=data["service"], revision=data["revision"])
            target = ("service", action.service)
        when = night.oncall.hhmm(event.at)
        why = f"order {event.order}, {when}" if event.kind == "acted" else f"approved by thumbs-up, {when}"
        latest[target] = (action, why)
    return list(latest.values())


def render_watch_log(night: Night) -> str:
    oncall = night.oncall
    ledger = night.ledger
    lines = []
    title_night = night.orders.night.strftime("%a %d %b") if night.orders else "tonight"
    lines.append(f"## Watch log, night of {title_night}")
    lines.append("")
    lines.append("Written by code from the night's record. Times are local to the on-call person.")
    lines.append("")
    if night.signature and night.orders:
        count = len(night.orders.orders)
        lines.append(
            f"Signed: {count} order{'s' if count != 1 else ''}, by {oncall.first_name} at "
            f"{oncall.hhmm(night.signature.at)} ({night.signature.method})."
        )
    else:
        lines.append("Signed: nothing, so every alert woke the on-call person.")
    lines.append("")
    lines.append("| Time | What happened |")
    lines.append("|---|---|")
    for event in ledger.events:
        if event.kind in SHOWN:
            text = event.text.replace("|", "/")
            prefix = f"Incident #{event.incident}: " if event.incident is not None and event.kind == "alert" else ""
            lines.append(f"| {oncall.hhmm(event.at)} | {prefix}{text} |")
    lines.append("")

    woke = ledger.of("woke")
    acted = ledger.of("acted")
    lines.append(
        f"Woken: {len(woke)} time{'s' if len(woke) != 1 else ''}"
        + (f" ({', '.join(oncall.hhmm(e.at) for e in woke)})." if woke else ".")
    )
    if acted:
        slept = ", ".join(f"incident #{e.incident} (order {e.order})" for e in acted)
        lines.append(f"Handled while you slept: {slept}.")
    lines.append("")

    ends = loose_ends(night)
    if ends:
        lines.append("Loose ends: changed tonight and still in place.")
        lines.append("")
        for action, why in ends:
            lines.append(f"- {action.describe()} ({why})")
        lines.append("")
        lines.append("The dawn flow proposes keep or undo for each in ops/state.yml. You decide by merging.")
    else:
        lines.append("Loose ends: none.")
    return "\n".join(lines) + "\n"
