"""The morning, live: the watch log on the watch issue, the dawn flow, and the countersign applied.

At the first tick after the watch end, the relay keeps the night's loose ends in its own record (they
outlive the noon rollover of the ledger), posts the watch log on the watch issue and starts the dawn flow.
The dawn flow proposes keep or undo in a countersign merge request that changes ops/state.yml. When the
on-call person merges or approves it, the relay applies the plan from countersign.plan_morning once:
every loose end that is not kept is restored, through the restore port, to the snapshot the night's
apply took of it, and the result is noted on the watch issue.

Nothing here decides what the night meant: the loose ends come from the ledger, the plan from
countersign.py, and the person decides by signing the countersign.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from .countersign import describe_restored, parse_state, plan_morning, undo
from .dawn import LooseEnd, action_from, dawn_goal, loose_ends, render_watch_log
from .decide import Night
from .model import Action, Change, Signature
from .orders import OrdersError, watch_window
from .watch import NOTHING_CHANGED


class MorningPorts(Protocol):
    def watch_note(self, text: str, at: datetime) -> None: ...
    def start_dawn_flow(self, goal: str, at: datetime) -> None: ...
    def apply(self, action: Action, at: datetime) -> Change: ...
    def restore(self, action: Action, before: dict, at: datetime) -> Change: ...


@dataclass(frozen=True)
class StateFile:
    """ops/state.yml as signed: its parsed YAML, who signed it (None when nobody did), and why it cannot
    be read, if it cannot. A file that cannot be read never counts as "keep nothing"."""

    data: dict | None
    signature: Signature | None
    problem: str | None = None


def new_record(night: Night) -> dict:
    """What the relay keeps about one finished night until its countersign is applied.

    ended_at is the watch end itself, not the tick that noticed it, so a countersign signed while the
    relay was down still counts when it comes back.
    """
    assert night.orders is not None
    _, end = watch_window(night.orders, night.oncall)
    return {
        "night": night.orders.night.isoformat(),
        "ended_at": end.isoformat(),
        "loose_ends": [{"action": end.action.as_dict(), "why": end.why, "before": end.before}
                       for end in loose_ends(night)],
        "log_posted": False,
        "flow_started": False,
        "countersign": None,
    }


def loose_from(record: dict) -> list[LooseEnd]:
    return [LooseEnd(action=action_from(item["action"]), why=str(item.get("why", "")), before=item.get("before"))
            for item in record.get("loose_ends") or []]


def step(relay_doc: dict, night: Night, watch_expired: bool, state_file: StateFile | None,
         ports: Any, now: datetime, watch_issue: int | None) -> list[str]:
    """One morning pass. Returns short lines saying what happened, for the tick summary."""
    done: list[str] = []
    orders = night.orders
    record = relay_doc.get("dawn")
    if watch_expired and orders is not None and (record is None or record.get("night") != orders.night.isoformat()):
        record = relay_doc["dawn"] = new_record(night)
        done.append(f"night of {record['night']} ended with {len(record['loose_ends'])} loose end(s) awaiting the countersign")
    if record is None:
        return done

    if watch_issue is not None and not record["log_posted"]:
        record["log_posted"] = True  # set first: a log posted twice is noise, a log never posted is worse than once
        ports.watch_note(render_watch_log(night), now)
        done.append("watch log posted")
    if watch_issue is not None and not record["flow_started"] and record["loose_ends"]:
        record["flow_started"] = True
        ports.start_dawn_flow(dawn_goal(night, watch_issue), now)
        done.append("dawn flow started")

    if record["countersign"] is None and state_file is not None:
        result = countersign(record, state_file, night, ports, now)
        if result is not None:
            record["countersign"] = result
            text = record["countersign_text"] = render_countersign(result, night)
            if watch_issue is not None:
                ports.watch_note(text, now)
            done.append(text.splitlines()[0])
    return done


def countersign(record: dict, state_file: StateFile, night: Night, ports: Any, now: datetime) -> dict | None:
    """Apply the countersign once, if the on-call person signed ops/state.yml after the night ended."""
    signature = state_file.signature
    ended = datetime.fromisoformat(record["ended_at"])
    if signature is None or signature.at < ended:
        return None  # not countersigned yet: nothing changes
    result: dict = {"commit": signature.commit, "user": signature.user, "at": signature.at.isoformat(),
                    "method": signature.method, "restored": [], "undone": [], "kept": [], "by_hand": [],
                    "problems": []}
    if signature.user != night.oncall.user:
        result["problems"] = [f"ops/state.yml was signed by {signature.user}, not by the on-call person "
                              f"({night.oncall.user}). Nothing was changed."]
        return result
    if state_file.problem:
        result["problems"] = [state_file.problem, "Nothing was changed."]
        return result
    try:
        plan = plan_morning(loose_from(record), parse_state(state_file.data, night.targets))
    except OrdersError as error:
        result["problems"] = list(error.problems) + ["Nothing was changed."]
        return result
    result["kept"] = [f"{item.action.describe()}, until {item.until}" if item.until else item.action.describe()
                      for item in plan.kept]
    result["by_hand"] = list(plan.by_hand)
    # If a change fails, the error stops this pass and the whole countersign is tried again next tick.
    # That is safe: restoring a target that is already as its snapshot says changes nothing.
    for action, before, _why in plan.undo:
        if before is not None:
            change = ports.restore(action, before, now)
            text = describe_restored(action, before)
            if isinstance(change, Change) and not change.changed:
                text += NOTHING_CHANGED
            result["restored"].append(text)
        else:
            # A record from before snapshots existed: a flag is turned the other way (plan_morning sends
            # a traffic change without a snapshot to a person instead).
            reverse = undo(action)
            assert reverse is not None
            ports.apply(reverse, now)
            result["undone"].append(reverse.describe())
    return result


def render_countersign(result: dict, night: Night) -> str:
    at = datetime.fromisoformat(result["at"])
    who = night.oncall.first_name if result["user"] == night.oncall.user else result["user"]
    lines = [f"Countersign by {who} at {night.oncall.hhmm(at)} ({result['method']}), applied by code."]
    lines += [f"- Kept: {text}" for text in result["kept"]]
    lines += [f"- Restored: {text}" for text in result.get("restored") or []]
    lines += [f"- Undone: {text}" for text in result["undone"]]
    lines += [f"- For a person: {text}" for text in result["by_hand"]]
    lines += [f"- Refused: {text}" for text in result["problems"]]
    if len(lines) == 1:
        lines.append("- Nothing to change.")
    return "\n".join(lines)
