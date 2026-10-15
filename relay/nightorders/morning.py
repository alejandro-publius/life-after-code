"""The morning, live: the watch log on the watch issue, the dawn flow, and the countersign applied.

At the first tick after the watch end, the relay keeps the night's loose ends in its own record (they
outlive the noon rollover of the ledger), posts the watch log on the watch issue and starts the dawn flow.
The dawn flow proposes keep or undo in a countersign merge request that changes ops/state.yml. When the
on-call person merges or approves it, the relay applies the plan from countersign.plan_morning once:
every loose end that is not kept is restored, through the restore port, to the snapshot the night's
apply took of it, and the result is noted on the watch issue. A target a person changed after the night
is left as it is. The plan is kept in the record until it is done, so a restore that fails is tried again
on the next ticks (at most MAX_RESTORE_TRIES times, then it is left for a person) while the others are done.

Nothing here decides what the night meant: the loose ends come from the ledger, the plan from
countersign.py, and the person decides by signing the countersign.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from datetime import timedelta

from . import kept
from .countersign import describe_restored, parse_state, plan_morning, target_words, undo
from .dawn import FAILED, LooseEnd, action_from, dawn_goal, loose_ends, may_be_in_place, render_watch_log
from .decide import Night
from .model import Action, Change, Signature, describe_before
from .orders import OrdersError, watch_window
ALREADY_BACK = " (already as before the night)"
DAWN_GRACE = timedelta(minutes=20)  # after this, with no countersign request open, code opens one itself
STATE_PATH = "ops/state.yml"
MAX_RESTORE_TRIES = 5  # a restore that keeps failing is left for a person, and the countersign note says so


class MorningPorts(Protocol):
    def watch_note(self, text: str, at: datetime) -> None: ...
    def start_dawn_flow(self, goal: str, at: datetime) -> None: ...
    def apply(self, action: Action, at: datetime) -> Change: ...
    def restore(self, action: Action, before: dict, at: datetime) -> Change: ...
    def holds(self, action: Action) -> bool: ...  # whether the target is still as the action left it
    # Optional: as_before(action, before) -> bool, whether the target is already as the snapshot says. A port without
    # it never counts a restore tried again as done already.


def _one_line(text: object) -> str:
    """Text on one line. Notes and merge request descriptions are read by GitLab, which runs a line starting with
    / as a quick action with the relay's token, so nothing the relay did not write itself may start a line."""
    return " ".join(str(text).split())


@dataclass(frozen=True)
class StateFile:
    """ops/state.yml as signed: its parsed YAML, who signed it (None when nobody did), and why it cannot
    be read, if it cannot. A file that cannot be read never counts as "keep nothing"."""

    data: dict | None
    signature: Signature | None
    problem: str | None = None


def _target(action: dict) -> tuple:
    return ("flag", action.get("flag"), action.get("environment")) if action.get("action") == "flag_set" \
        else ("service", action.get("service"))


def new_record(night: Night, carried: dict | None = None) -> dict:
    """What the relay keeps about one finished night until its countersign is applied.

    ended_at is the watch end itself, not the tick that noticed it, so a countersign signed while the
    relay was down still counts when it comes back. When the night before was never countersigned, its
    loose ends are carried into this record: nothing is forgotten, and for a target changed on both nights
    the earlier snapshot is kept, because that is how it was before the first night.
    """
    assert night.orders is not None
    _, end = watch_window(night.orders, night.oncall)
    ends: dict[tuple, dict] = {}
    nights: list[str] = []
    if carried and carried.get("countersign") is None:
        nights = list(carried.get("nights") or [carried["night"]])
        for item in carried.get("loose_ends") or []:
            ends[_target(item["action"])] = dict(item)
    for loose in loose_ends(night):
        item = {"action": loose.action.as_dict(), "why": loose.why, "before": loose.before}
        also = [other.as_dict() for other in loose.also]
        key = _target(item["action"])
        if key in ends:
            item["before"] = ends[key].get("before")  # how it was before the first of these nights
            if FAILED in loose.why:  # tonight's change may never have taken, so the earlier one may be in place
                also += [other for other in [ends[key]["action"], *(ends[key].get("also") or [])]
                         if other != item["action"] and other not in also]
        if also:
            item["also"] = also
        ends[key] = item
    return {
        "night": night.orders.night.isoformat(),
        "nights": nights + [night.orders.night.isoformat()],
        "ended_at": end.isoformat(),
        "loose_ends": list(ends.values()),
        "log_posted": False,
        "flow_started": False,
        "pushed": False,
        "code_request": None,
        "countersign": None,
    }


def push_lines(night: Night, loose: int) -> tuple[str, ...]:
    """The quiet good-morning push: what the night did, and what waits for her."""
    woke = len(night.ledger.of("woke"))
    handled = len({e.incident for e in night.ledger.of("acted")} - {e.incident for e in night.ledger.of("woke")})
    first = f"Woken {woke} time{'' if woke == 1 else 's'}. Handled while you slept: {handled}."
    second = (f"{loose} change{'' if loose == 1 else 's'} to keep or restore. The countersign merge request is on "
              "the watch issue." if loose else "Nothing changed overnight, so nothing needs a countersign.")
    return first, second


def countersign_request(record: dict, replaces: list[int] | tuple[int, ...] = ()) -> tuple[str, str, str]:
    """The countersign merge request code opens when no model proposed one: (state file, title, description).

    The file keeps nothing, so merging it as it is restores every change; the description says how to keep one.
    replaces lists the open countersign merge requests whose file does not name this night, so code did not count
    them; the description says to close them.
    """
    night = record["night"]
    state_text = (f"# Countersign for the night of {night}, written by code: no model proposed anything this "
                  "morning.\n# Merged as it is, it keeps nothing, and code restores every change below to how it "
                  "was before the night.\n# To keep a change, add it under flags or services (see the merge "
                  f'request).\nnight: "{night}"\nflags: []\nservices: []\n')
    lines = [f"Countersign for the night of {night}. Written by code: no model proposed anything this morning.", "",
             "Changed overnight and still in place:", ""]
    for item in record["loose_ends"]:
        action = action_from(item["action"])
        also = [action_from(other) for other in item.get("also") or []]
        lines.append("- " + _one_line(f"{action.describe()} ({item.get('why', '')}). Before the night: "
                                      f"{describe_before(item.get('before'))}." + may_be_in_place(also)))
    if replaces:
        older = ", ".join(f"!{int(number)}" for number in replaces)
        lines += ["", f"This replaces {older}: still open, but its ops/state.yml does not name the night of {night}. "
                      "Close it, so that only this merge request countersigns the night."]
    lines += ["", "Merged as it is, this restores every change above to how it was before the night.",
              "To keep one, add it to ops/state.yml in this merge request before merging, for example:", "",
              "```yaml",
              "flags:",
              '  - {flag: new_checkout, environment: production, keep: "off", until: "the fix ships", until_deployed: 38}',
              "services:",
              "  - {service: shop, keep: shop-00041, until: \"the image cache is reverted\"}",
              "```", "",
              "until_deployed is optional: the merge request whose deployment ends the keep. Once it is in "
              "production, code restores the change by itself, in daytime, and notes it on the watch issue.", "",
              "Merge (or approve) to countersign. Nothing changes until it is signed."]
    return state_text, f"Countersign {night} (written by code)", "\n".join(lines)


def loose_from(record: dict) -> list[LooseEnd]:
    return [LooseEnd(action=action_from(item["action"]), why=str(item.get("why", "")), before=item.get("before"),
                     also=tuple(action_from(other) for other in item.get("also") or []))
            for item in record.get("loose_ends") or []]


def step(relay_doc: dict, night: Night, watch_expired: bool, state_file: StateFile | None,
         ports: Any, now: datetime, watch_issue: int | None, earlier: bool = False) -> list[str]:
    """One morning pass. Returns short lines saying what happened, for the tick summary.

    For an earlier night (one that ended with no good tick before noon) it makes the record and does the steps
    written from that night's own ledger, then returns: the countersign request and the countersign that follow are
    the record's, and the current night's step does them in the same tick."""
    done: list[str] = []
    orders = night.orders
    record = relay_doc.get("dawn")
    if watch_expired and orders is not None and (record is None or record.get("night") != orders.night.isoformat()):
        record = relay_doc["dawn"] = new_record(night, carried=record)
        carried = len(record["nights"]) - 1
        done.append(f"night of {record['night']} ended with {len(record['loose_ends'])} loose end(s) awaiting the "
                    "countersign" + (f", including {carried} earlier night(s) never countersigned" if carried else ""))
    if record is None:
        return done

    if watch_issue is not None and not record["log_posted"]:
        record["log_posted"] = True  # set first: a log posted twice is noise, a log never posted is worse than once
        ports.watch_note(render_watch_log(night), now)
        done.append("watch log posted")
    if not record.get("pushed", True) and hasattr(ports, "morning_push"):
        record["pushed"] = True  # once a night; a quiet push, never an urgent one
        ports.morning_push(push_lines(night, len(record["loose_ends"])), now)
        done.append("good-morning push sent")
    if watch_issue is not None and not record["flow_started"] and record["loose_ends"]:
        record["flow_started"] = True
        ports.start_dawn_flow(dawn_goal(night, watch_issue, loose_from(record)), now)
        done.append("dawn flow started")
    if earlier:
        return done
    # code_request is None until code has looked (a record from before this existed has no key: left alone).
    if (record["loose_ends"] and record["countersign"] is None and record.get("code_request", 0) is None
            and hasattr(ports, "open_countersign_request")):
        flow_ready = getattr(ports, "dawn_flow_ready", lambda: False)()
        ended = datetime.fromisoformat(record["ended_at"])
        if not flow_ready or now >= ended + DAWN_GRACE:
            # Only a request whose file names this night counts: one left open for an earlier night (a carried
            # record's, say) would be refused when merged, so code opens a fresh one that says what it replaces.
            found, others = ports.countersign_request_open(record["night"])
            if found is None:
                state_text, title, description = countersign_request(record, replaces=others)
                record["code_request"] = ports.open_countersign_request(record["night"], state_text, title, description)
                done.append(f"countersign merge request !{record['code_request']} opened by code")
            else:
                record["code_request"] = -1  # the dawn flow opened one; nothing for code to do

    if record["countersign"] is None and (state_file is not None or record.get("applying")):
        result = countersign(record, state_file, night, ports, now)
        if result is not None:
            keep = result.pop("keep", [])
            text = render_countersign(result, night)
            if not result["problems"]:
                kept.add(relay_doc, keep)  # kept changes go on the kept list, with their leases
            if result["problems"]:
                # Refused once, said once. The countersign stays open: a corrected file, or the on-call person's
                # own signature after someone else's, is a new signature and is read the next time the file is.
                record["refused"], record["refused_text"] = result, text
            else:
                record["countersign"], record["countersign_text"] = result, text
            if watch_issue is not None:
                ports.watch_note(text, now)
            done.append(text.splitlines()[0])
    return done


def _same_signature(refused: dict | None, signature: Signature) -> bool:
    return bool(refused) and (refused["commit"], refused["user"], refused["method"]) == (
        signature.commit, signature.user, signature.method)


def countersign(record: dict, state_file: StateFile | None, night: Night, ports: Any, now: datetime) -> dict | None:
    """Apply the countersign once, if the on-call person signed ops/state.yml after the night ended.

    A signed file is checked and planned once. The plan waits in the record (applying) until every loose end is
    done, so the next ticks carry on from it without reading the file again. Returns the result once there is
    nothing left to do, or at once when the file is refused; None while nothing is signed. A restore that failed
    and will be tried again raises its error after the others were done.
    """
    if record.get("applying") is None:
        if state_file is None:
            return None
        refused = _accept(record, state_file, night)
        if refused is not None or record.get("applying") is None:
            return refused
    return _carry_out(record, ports, now)


def _accept(record: dict, state_file: StateFile, night: Night) -> dict | None:
    """Check a signed ops/state.yml and plan the morning from it. Returns the refusal, or None: nothing signed
    since the night ended (record unchanged), or the plan is now waiting in record["applying"]."""
    signature = state_file.signature
    ended = datetime.fromisoformat(record["ended_at"])
    if signature is None or signature.at < ended:
        return None  # not countersigned yet: nothing changes
    if _same_signature(record.get("refused"), signature):
        return None  # already refused and said so; only a new signature is read again
    result: dict = {"commit": signature.commit, "user": signature.user, "at": signature.at.isoformat(),
                    "method": signature.method, "restored": [], "undone": [], "left": [], "kept": [], "by_hand": [],
                    "problems": []}
    if signature.user != night.oncall.user:
        result["problems"] = [f"ops/state.yml was signed by {signature.user}, not by the on-call person "
                              f"({night.oncall.user}). Nothing was changed."]
        return result
    if state_file.problem:
        result["problems"] = [state_file.problem, "Nothing was changed."]
        return result
    named = (state_file.data or {}).get("night")
    if named is not None and str(named) != record["night"]:
        result["problems"] = [f"ops/state.yml is the countersign for the night of {named}, not of {record['night']}.",
                              "Nothing was changed."]
        return result
    try:
        plan = plan_morning(loose_from(record), parse_state(state_file.data, night.targets))
    except OrdersError as error:
        result["problems"] = list(error.problems) + ["Nothing was changed."]
        return result
    result["kept"] = [_kept_words(item, night) for item in plan.kept]
    loose = loose_from(record)
    result["keep"] = [kept.entry(item, end.before, end.why, record["night"], signature.at,
                                  kept.environment_of(item.action, night.targets.services))
                      for item in plan.kept for end in loose if end.action.same_target(item.action)]
    result["by_hand"] = list(plan.by_hand)
    record["applying"] = {"result": result, "undo": [_undo_item(action, before, why, loose)
                                                     for action, before, why in plan.undo]}
    return None


def _undo_item(action: Action, before: dict | None, why: str, loose: list[LooseEnd]) -> dict:
    """One restore of the plan, kept in the record until it is done, with the night's other changes to its target
    that may be in place instead (also)."""
    item: dict = {"action": action.as_dict(), "before": before, "why": why, "tries": 0}
    also = next((end.also for end in loose if end.action == action), ())
    if also:
        item["also"] = [other.as_dict() for other in also]
    return item


def _carry_out(record: dict, ports: Any, now: datetime) -> dict:
    """Put back every loose end of the plan that is not done yet. One that fails stays for the next tick, and after
    MAX_RESTORE_TRIES it is handed to a person with the reason; the rest are done meanwhile, each once."""
    applying = record["applying"]
    result = applying["result"]
    again: Exception | None = None
    for item in list(applying["undo"]):
        action = action_from(item["action"])
        also = tuple(action_from(other) for other in item.get("also") or [])
        try:
            _put_back(action, item["before"], item["why"], result, ports, now, also,
                      retry=int(item.get("tries", 0)) > 0)
        except Exception as error:
            if getattr(error, "sent", True):  # a call the tick had no time left to send was not a try
                item["tries"] = int(item.get("tries", 0)) + 1
            if item["tries"] < MAX_RESTORE_TRIES:
                again = again or error
                continue
            result["by_hand"].append(_given_up(action, item["before"], item["tries"], error))
        applying["undo"].remove(item)
    if again is not None:
        raise again
    del record["applying"]
    return result


def _put_back(action: Action, before: dict | None, why: str, result: dict, ports: Any, now: datetime,
              also: tuple[Action, ...] = (), retry: bool = False) -> None:
    """Restore one loose end, unless its target is no longer as the night left it (by this action, or by another
    night change to it in also): then a person changed it after the night (or a change that failed never took), and
    code leaves it as it is. On a retry, a target already as the snapshot says was put back by the try before, whose
    write went through although it raised."""
    if not any(ports.holds(each) for each in (action, *also)):
        if retry and before is not None and hasattr(ports, "as_before") and ports.as_before(action, before):
            result["restored"].append(describe_restored(action, before) + ALREADY_BACK)
            return
        if FAILED in why:
            result["left"].append(f"{action.describe()} did not take, or was changed after the night, so code left "
                                  "it as it is")
        else:
            result["left"].append(f"{target_words(action)} was changed after the night, so code left it as it is")
        return
    if before is not None:
        change = ports.restore(action, before, now)
        text = describe_restored(action, before)
        if isinstance(change, Change) and not change.changed:
            text += ALREADY_BACK
        result["restored"].append(text)
        return
    # A record from before snapshots existed: a flag is turned the other way (plan_morning sends a traffic change
    # without a snapshot to a person instead).
    reverse = undo(action)
    assert reverse is not None
    ports.apply(reverse, now)
    result["undone"].append(reverse.describe())


def _given_up(action: Action, before: dict | None, tries: int, error: Exception) -> str:
    """What a person has to do about a restore code tried MAX_RESTORE_TRIES times."""
    why = str(error) if isinstance(error, RuntimeError) else type(error).__name__
    if before is not None:
        what = f"restore {describe_restored(action, before)}"
    else:
        what = f"set {(undo(action) or action).describe()}"  # plan_morning gives a snapshot or a reverse
    return f"Code could not {what} after {tries} tries ({_one_line(why)[:160]}). Do it by hand."


def _kept_words(item: Any, night: Night) -> str:
    words = item.action.describe() + (f", until {item.until}" if item.until else "")
    if item.until_deployed:
        where = kept.environment_of(item.action, night.targets.services)
        words += f" (code restores it when !{item.until_deployed} is in {where})"
    return words


SECTIONS = (("Kept", "kept"), ("Restored", "restored"), ("Undone", "undone"), ("Not restored", "left"),
            ("For a person", "by_hand"), ("Refused", "problems"))


def render_countersign(result: dict, night: Night) -> str:
    """The countersign note for the watch issue. Each item is one line: it can carry text from the state file."""
    at = datetime.fromisoformat(result["at"])
    who = night.oncall.first_name if result["user"] == night.oncall.user else result["user"]
    lines = [f"Countersign by {who} at {night.oncall.hhmm(at)} ({result['method']}), applied by code."]
    for label, key in SECTIONS:
        lines += [f"- {label}: {_one_line(text)}" for text in result.get(key) or []]
    if len(lines) == 1:
        lines.append("- Nothing to change.")
    return "\n".join(lines)
