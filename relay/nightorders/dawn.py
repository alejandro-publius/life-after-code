"""The morning: a watch log written by code from the night's record, and the loose ends.

The dawn flow (the model) reads this log and proposes keep or undo for each loose end in
ops/state.yml. The facts in the log come from the ledger, not from the model.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decide import Night
from .model import Action, describe_before

SHOWN = ("alert", "asked", "acted", "failed", "declined", "woke", "approved", "refused", "recovered", "stood_down",
         "expired")


@dataclass(frozen=True)
class LooseEnd:
    """A change made tonight and still in place: what was done, why, and the target's state before the night.

    before is the snapshot the port took before the first night action on this target (None for records
    written before snapshots existed). The morning restores from it, never by guessing.
    """

    action: Action
    why: str
    before: dict | None = None


def action_from(data: dict) -> Action:
    """An Action from its as_dict form."""
    if data["action"] == "flag_set":
        return Action(kind="flag_set", flag=data["flag"], environment=data["environment"], to=data["to"])
    return Action(kind="traffic_to_revision", service=data["service"], revision=data["revision"])


def loose_ends(night: Night) -> list[LooseEnd]:
    """State changed tonight and not changed back, in the order the targets were first changed.

    An action that changed nothing (changed is False in its record) leaves no loose end. Records without
    the key, from before changes were recorded, count as changed.
    """
    latest: dict[tuple, LooseEnd] = {}
    first_before: dict[tuple, dict | None] = {}
    for event in night.ledger.events:
        if event.kind not in ("acted", "approved"):
            continue
        data = event.data.get("action")
        if not data:
            continue
        action = action_from(data)
        target = ("flag", action.flag, action.environment) if action.kind == "flag_set" else ("service", action.service)
        if target not in first_before:  # the first change of the night is the state before the night
            first_before[target] = event.data.get("before")
        if event.data.get("changed") is False:
            continue
        when = night.oncall.hhmm(event.at)
        why = f"order {event.order}, {when}" if event.kind == "acted" else f"approved by thumbs-up, {when}"
        latest[target] = LooseEnd(action=action, why=why, before=first_before[target])
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
        for end in ends:
            lines.append(f"- {end.action.describe()} ({end.why})")
        lines.append("")
        lines.append("The dawn flow proposes keep or undo for each in ops/state.yml. You decide by merging or approving. "
                     "What is not kept, code restores to how it was before the night.")
    else:
        lines.append("Loose ends: none.")
    return "\n".join(lines) + "\n"


def dawn_goal(night: Night, watch_issue: int, ends: list[LooseEnd] | None = None) -> str:
    """The goal the relay gives the dawn flow at the watch end. Facts come from the ledger, not the model.

    ends defaults to this night's loose ends; the morning passes its record's, which also carries any earlier
    night that was never countersigned.
    """
    title_night = night.orders.night.strftime("%a %d %b") if night.orders else "last night"
    ends = loose_ends(night) if ends is None else ends
    lines = [f"Watch issue #{watch_issue}, night of {title_night}. Code posted the watch log there."]
    if night.orders:
        lines.append(f'Night date: {night.orders.night.isoformat()}. Write night: "{night.orders.night.isoformat()}" '
                     "at the top of ops/state.yml.")
    if ends:
        lines.append("Loose ends, changed overnight and still in place. Propose keep or restore for each:")
        lines += [f"- {end.action.describe()} ({end.why}). Before the night: {describe_before(end.before)}."
                  for end in ends]
    else:
        lines.append("Loose ends: none. Post one note saying nothing needs a countersign, and open no merge request.")
    return "\n".join(lines)
