"""A kept change is a lease: it ends when the merge request it waits for is in production.

At the morning countersign the on-call person can keep a night change and name the merge request that makes
it unnecessary (until_deployed: 38 in ops/state.yml). Code then holds the kept change, with the snapshot from
before the night, on the relay's kept list. In daytime, every LEASE_CHECK_EVERY, it asks GitLab two questions
with plain answers: is !38 merged, and is its commit in the last successful deployment to the target's
environment? When both are yes, code restores the snapshot, then says so on the watch issue and in a quiet
push. The person signed that ending at the countersign; code only decides when it has come.

Every kept change, with a lease or without, is also checked against GitLab and Cloud Run: once its target is no
longer as kept (a person changed it), it leaves the list and code changes nothing. A lease never ends at night,
and never on a target whose newer night change still waits for its own countersign.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from .countersign import Kept, describe_restored
from .dawn import action_from
from .model import Action, OnCall

LEASE_CHECK_EVERY = timedelta(minutes=10)
DAY_STARTS, DAY_ENDS = time(8, 0), time(20, 0)  # local time: a lease ends only while people are up
ENDED_SHOWN = 10  # the last few ended keeps, for the status page
UNTIL_CHARS = 120
ALREADY_BACK = " (already as before the night)"


def target(action: dict) -> tuple:
    return (("flag", action.get("flag"), action.get("environment")) if action.get("action") == "flag_set"
            else ("service", action.get("service")))


def environment_of(action: Action, services: dict[str, str]) -> str:
    """Where the merge request must be deployed: the flag's environment, or the service's own."""
    return str(action.environment) if action.kind == "flag_set" else str(services.get(action.service or "", ""))


def entry(kept: Kept, before: dict | None, why: str, night: str, at: datetime, environment: str) -> dict:
    """One kept change as the relay stores it."""
    until = " ".join(kept.until.replace("`", "'").split())[:UNTIL_CHARS]  # one plain line, wherever it is shown
    return {"action": kept.action.as_dict(), "before": before, "why": why, "since": night, "until": until,
            "until_deployed": kept.until_deployed, "environment": environment, "kept_at": at.isoformat(),
            "lease": None}


def add(relay_doc: dict, entries: list[dict]) -> None:
    """Put kept changes on the kept list. A target already on it keeps its older snapshot and night: how it was
    before the first night that changed it, which is what a lease puts back."""
    kept = relay_doc.setdefault("kept", [])
    for new in entries:
        old = next((item for item in kept if target(item["action"]) == target(new["action"])), None)
        if old is not None:
            new = dict(new, before=old.get("before"), since=old.get("since", new["since"]))
            kept.remove(old)
        kept.append(new)


def what(item: dict) -> str:
    """A kept change in plain words: "new_checkout off in production"."""
    return action_from(item["action"]).describe()


def summary(item: dict) -> str:
    """One line per kept change, for the day sheet and the status page."""
    line = f"{what(item)}, kept since the night of {item.get('since')}"
    if item.get("until"):
        line += f", until {item['until']}"
    number = item.get("until_deployed")
    if number:
        line += f". Ends by itself when !{number} is in {item.get('environment')}"
        line += f" (last check: {item['lease']})." if item.get("lease") else "."
    else:
        line += ". No lease: it stays until a person changes it."
    return line


def _waiting(relay_doc: dict) -> set[tuple]:
    """Targets a newer night changed again, whose countersign has not been applied yet."""
    dawn = relay_doc.get("dawn") or {}
    if dawn.get("countersign") is not None:
        return set()
    return {target(item["action"]) for item in dawn.get("loose_ends") or []}


def _ended(relay_doc: dict, item: dict, text: str, now: datetime) -> None:
    ended = relay_doc.setdefault("kept_ended", [])
    ended.append({"at": now.isoformat(), "what": what(item), "text": text})
    del ended[:-ENDED_SHOWN]


def step(relay_doc: dict, now: datetime, oncall: OnCall, ports: Any) -> list[str]:
    """Called by the relay's tick, as a chore: check the kept list in daytime and end the leases that are due.

    Ports: holds(action), shipped(merge_request, environment) -> (state, words), restore(action, before, at),
    watch_note(text, at) and quiet_push(title, lines, at). A failure stops the pass and the next check tries
    again; restoring a target that is already as its snapshot changes nothing.
    """
    kept = relay_doc.get("kept") or []
    if not kept:
        return []
    if not DAY_STARTS <= now.astimezone(oncall.timezone).time() < DAY_ENDS:
        return []
    last = relay_doc.get("kept_checked_at")
    if last and now - datetime.fromisoformat(last) < LEASE_CHECK_EVERY:
        return []
    relay_doc["kept_checked_at"] = now.isoformat()
    waiting = _waiting(relay_doc)
    done: list[str] = []
    for item in list(kept):
        if target(item["action"]) in waiting:
            continue
        action = action_from(item["action"])
        if not ports.holds(action):
            kept.remove(item)
            text = (f"No longer kept: {what(item)} was changed after the countersign, so it is off the kept list. "
                    "Code changed nothing.")
            _ended(relay_doc, item, text, now)
            ports.watch_note(text, now)
            done.append(f"{what(item)} changed by hand, off the kept list")
            continue
        number = item.get("until_deployed")
        if not number:
            continue
        state, words = ports.shipped(int(number), str(item.get("environment") or ""))
        item["lease"] = words
        if state == "closed":
            item["until_deployed"] = None  # nothing can ship now; say so once and stop asking
            ports.watch_note(f"The lease on {what(item)} cannot end by itself: {words}. It stays kept until a "
                             "person changes it.", now)
            done.append(f"lease on {what(item)} has no merge request left to wait for")
            continue
        if state != "shipped":
            continue
        before = item.get("before")
        if before is None:
            kept.remove(item)
            result = (f"There is no snapshot from before the night of {item.get('since')}, so a person restores "
                      f"{what(item)}.")
        else:
            change = ports.restore(action, before, now)
            kept.remove(item)
            back = ALREADY_BACK if getattr(change, "changed", True) is False else ""
            result = f"Restored {describe_restored(action, before)}{back}."
        why = (f"It was kept since the night of {item.get('since')}"
               + (f", until {item['until']}" if item.get("until") else "") + ".")
        text = f"Lease ended: {words}. {result} {why}"
        _ended(relay_doc, item, text, now)
        ports.watch_note(text, now)
        ports.quiet_push("Night Orders: a kept change ended", (f"Lease ended: {words}.", result), now)
        done.append(f"lease on {what(item)} ended")
    return done
