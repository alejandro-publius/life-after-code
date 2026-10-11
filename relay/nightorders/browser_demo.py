"""A fixed, labelled browser story replayed by the real Watch decision code.

Every call owns a fresh in-memory shop and ledger. Bundled files are read-only.
No GitLab, model, push service or production shop is contacted.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import httpx

from .compare import compare
from .countersign import parse_state, plan_morning
from .dawn import loose_ends, render_watch_log
from .countersign import undo
from .demo_night import DemoShop, RecordingPorts, countersign, restored_action, run
from .gitlab_ports import Http
from .model import Action, OnCall, Targets
from .orders import load_yaml, watch_window
from .rehearsal import rehearse

DATA = Path(__file__).with_name("demo_story_data")
FIXTURE = DATA / "night-2026-10-20"
OPS = DATA / "ops"
LABEL = "Demo data: simulated shop, planted faults and recorded model replies. Real decision code."

TITLES = {
    "alert": "Checkout alert opened an incident",
    "asked": "Code found an eligible signed order",
    "declined": "The recorded model reply declined the order",
    "woke": "Priya gets a necessary wake",
    "approved": "Priya approves the one suggested change",
    "acted": "Both keys agree. The signed order runs",
    "recovered": "The recovery check passes",
    "refused": "The suggestion was dropped without a change",
    "expired": "Tonight's authority expires",
    "stood_down": "The alert recovered before an action",
}


def _json_file(name: str) -> dict:
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def three_ways() -> tuple[dict, ...]:
    """The same night signed, under standing orders and unsigned, counted by the real Watch. It does not depend
    on the browser's choices, so it is computed once per process."""
    return tuple(compare(FIXTURE, OPS))


class _OrdersFile:
    """Stands in for GitLab's raw file read: the drafted orders file at the merge request's head."""

    def raw_file(self, path: str, ref: str) -> str:
        return (FIXTURE / "orders.yml").read_text(encoding="utf-8")


def rehearsal(oncall: OnCall, targets: Targets, scenario: dict, objects: dict) -> dict:
    """The rehearsal note the drafted orders merge request would get, written by the real rehearsal code against
    a simulated staging shop (its own flags, no faults) and the demo's Cloud Run revisions."""
    at = datetime.fromisoformat(objects["rehearsed_at"]).replace(tzinfo=oncall.timezone)
    staging = DemoShop(flags={k: ("on" if v is True else "off" if v is False else str(v)) for k, v in scenario["flags"].items()},
                       faults=[], new_share=float(scenario.get("new_path_share", 0.5)))
    ports = RecordingPorts(oncall_tz=oncall.timezone, shop=staging, notes={}, reactions={},
                           revisions={k: list(v) for k, v in objects["revisions"].items()})
    fetches = itertools.count()

    def staging_shop(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True, "commit": "demo"})
        if request.url.path == "/flags":
            return httpx.Response(200, json={"fetched_at": f"{objects['rehearsed_at']}:{next(fetches):02d}Z"})
        if request.url.path == "/checkout":
            path = "new" if staging.flags.get("new_checkout") == "on" else "old"
            return httpx.Response(200, json={"ok": True, "path": path, "label": "demo order"})
        return httpx.Response(404, json={})

    http = Http(httpx.Client(transport=httpx.MockTransport(staging_shop)))
    note = rehearse(_OrdersFile(), ports, http, oncall, targets, "https://shop-staging.demo", int(objects["orders_mr"]),
                    str(objects["orders_head"]), at, sleep=lambda _seconds: None)
    lines = {}
    for line in note.splitlines():
        if line.startswith("- order "):
            number = line[len("- order "):].split(":", 1)[0]
            lines[number] = line[2:]
    return {"at": at.isoformat(), "time": oncall.hhmm(at), "note": note, "lines": lines,
            "staging_flags_after": dict(staging.flags),
            "source": "written by the rehearsal code against the simulated staging shop (demo)"}


def gitlab_objects(night, ports: RecordingPorts, objects: dict, signed: bool, morning: dict, rehearsed: dict) -> dict:
    """The GitLab objects each chapter would leave behind, from the replay's own ledger and port record."""
    oncall = night.oncall
    sig = night.signature
    watch = f"#{objects['watch_issue']}"
    orders = f"!{objects['orders_mr']}"
    dusk = [
        {"ref": watch, "kind": "issue", "title": "Tonight's watch", "state": "open", "time": "21:00",
         "detail": "Day sheet note posted by code"},
        {"ref": orders, "kind": "merge request", "title": f"Night orders {night.orders.night.isoformat()}",
         "state": "merged" if signed else "open", "time": oncall.hhmm(sig.at) if sig else rehearsed["time"],
         "detail": (f"Rehearsal note by code at {rehearsed['time']}; merged by {oncall.first_name} at "
                    f"{oncall.hhmm(sig.at)}, which is the signature") if sig
         else f"Rehearsal note by code at {rehearsed['time']}; never merged, so nothing is signed"},
    ]
    night_rows = []
    closed = {e.incident for e in night.ledger.of("alert")}  # every demo incident closes before morning
    for event in night.ledger.of("alert"):
        notes = [e for e in night.ledger.events if e.incident == event.incident and e.kind != "alert"]
        night_rows.append({"ref": f"incident #{event.incident}", "kind": "incident",
                           "title": event.text.replace("Night watch: ", ""), "state": "closed" if event.incident in closed else "open",
                           "time": oncall.hhmm(event.at),
                           "detail": f"Evidence pack by code, then {len(notes)} note(s): " + ", ".join(e.kind for e in notes)})
    for item in ports.actions:
        when = datetime.fromisoformat(item["at"])
        if when >= datetime.fromisoformat(morning["at"]):
            continue
        action = item["action"]
        if action.get("action") != "flag_set":
            continue
        why = next((("order " + str(e.order)) if e.kind == "acted" else f"{oncall.first_name}'s thumbs-up"
                    for e in night.ledger.events if e.kind in ("acted", "approved") and e.at == when), "the relay")
        night_rows.append({"ref": "feature flag", "kind": "feature flag",
                           "title": f"{action['flag']} in {action['environment']}", "state": f"now {action['to']}",
                           "time": oncall.hhmm(when), "detail": f"Changed by the relay's token under {why}"})
    dawn_rows = [{"ref": watch, "kind": "issue note", "title": "Watch log", "state": "posted",
                  "time": oncall.hhmm(datetime.fromisoformat(night.ledger.of("expired")[0].at.isoformat()))
                  if night.ledger.of("expired") else "07:00",
                  "detail": "Written by code from the night's record"}]
    if morning["status"] == "merged":
        dawn_rows.append({"ref": f"!{objects['countersign_mr']}", "kind": "merge request",
                          "title": f"Countersign {night.orders.night.isoformat()}", "state": "merged",
                          "time": morning["time"], "detail": f"ops/state.yml merged by {oncall.first_name}; code restored "
                          f"{len(morning['undone'])} change(s) and kept {len(morning['kept'])}"})
    return {"label": "Demo objects. Links go live after the first real night.",
            "dusk": dusk, "night": night_rows, "dawn": dawn_rows}


def replay(*, signed: bool = True, approved: bool = True) -> dict:
    """Run the single bundled night with two explicit demo human choices.

    Selectors must be booleans. There is no path, action, target or credential
    input. Error rates are ratios. Each sample is the last complete minute;
    at is the decision tick and sampled_at is that minute's timestamp.
    """
    for name, value in (("signed", signed), ("approved", approved)):
        if type(value) is not bool:
            raise TypeError(f"{name} must be a boolean")

    ports, night = run(FIXTURE, OPS, signed=signed, approved=approved, collect_samples=True)
    assert night.orders is not None
    _, expires = watch_window(night.orders, night.oncall)
    scenario = load_yaml(FIXTURE / "scenario.yml")
    source_orders = load_yaml(FIXTURE / "orders.yml")
    dusk = _json_file("dusk_recorded.json")
    changes = _json_file("today.json")["merged_today"]
    notes = _json_file("notes.json")["incidents"]
    signature_source = _json_file("signature.json")
    samples = {sample["at"]: sample for sample in ports.samples}
    initial_flags = dict(ports.samples[0]["flags_before"])
    after_night = dict(ports.shop.flags)
    watch_log = render_watch_log(night)

    def step(key: str, phase: str, kind: str, at: str, title: str, text: str, *,
             incident: int | None = None, order: int | None = None, data: dict | None = None,
             flags_before: dict | None = None, flags_after: dict | None = None) -> dict:
        sample = samples.get(at)
        before = flags_before if flags_before is not None else sample["flags_before"] if sample else initial_flags
        after = flags_after if flags_after is not None else sample["flags_after"] if sample else before
        return {
            "id": key, "phase": phase, "kind": kind, "at": at,
            "time": night.oncall.hhmm(datetime.fromisoformat(at)), "title": title, "text": text,
            "incident": incident, "order": order, "data": data or {},
            "flags_before": dict(before), "flags_after": dict(after),
            "metrics": {"old_rate": sample["old_rate"], "new_rate": sample["new_rate"]} if sample else None,
        }

    draft_at = datetime.fromisoformat(scenario["start"]).replace(tzinfo=night.oncall.timezone).isoformat()
    steps = [step(
        "dusk-draft", "dusk", "drafted", draft_at, "Before bed, Priya sets the boundary",
        "Two demo orders are drafted from today's changes. The database migration is left out because it cannot be safely undone tonight.",
        data={"source": "recorded dusk reply", "orders": source_orders["orders"],
              "left_out": dusk["left_out"], "question": dusk["question"]},
    )]
    steps.append(step(
        "dusk-choice", "dusk", "signed" if signed else "unsigned", signature_source["at"],
        "Priya signs tonight's orders" if signed else "Priya leaves the draft unsigned",
        "Demo signature recorded at 22:06. The two orders expire at 07:00." if signed
        else "No signature is recorded. Every alert must wake Priya and the draft grants no authority.",
        data={"signed": signed, "source": "demo human choice"},
    ))

    timeline = []
    asked_incidents = {event.incident for event in night.ledger.of("asked")}
    for number, event in enumerate(night.ledger.events):
        data = dict(event.data)
        if event.kind in ("declined", "acted") and event.incident in asked_incidents:
            note = notes.get(str(event.incident))
            if note:
                data["recorded_reply"] = note["request"]
                data["reply_source"] = "recorded demo reply, no model API call"
        item = step(
            f"ledger-{number}", "dawn" if event.kind == "expired" else "night", event.kind,
            event.at.isoformat(), TITLES.get(event.kind, event.kind.replace("_", " ").capitalize()),
            event.text, incident=event.incident, order=event.order, data=data,
        )
        timeline.append(item)
    steps.extend(timeline)

    messages = []
    for event in night.ledger.of("woke"):
        suggestion = None
        if event.incident in asked_incidents:
            note = notes.get(str(event.incident))
            if note:
                suggestion = note["request"].get("suggest")
        was_approved = any(other.incident == event.incident for other in night.ledger.of("approved"))
        messages.append({
            "incident": event.incident, "at": event.at.isoformat(), "time": night.oncall.hhmm(event.at),
            "lines": event.data["page"], "suggestion": suggestion,
            "approval": "approved" if was_approved else "declined" if suggestion else "unavailable",
        })

    # Capture the night's evidence before the actual countersign restores anything.
    ends = loose_ends(night)
    morning_source = load_yaml(FIXTURE / "countersign.yml")
    morning_at = datetime.fromisoformat(morning_source["merged_at"]).replace(tzinfo=night.oncall.timezone).isoformat()
    morning = {
        "at": morning_at, "time": night.oncall.hhmm(datetime.fromisoformat(morning_at)),
        "status": "not_needed", "lines": [], "kept": [], "undone": [], "by_hand": [],
    }
    steps.append(step(
        "dawn-log", "dawn", "watch_log", ports.samples[-1]["at"], "The morning record comes from code",
        f"Priya was woken {len(night.ledger.of('woke'))} time(s). {len(night.ledger.of('acted'))} incident(s) were handled automatically.",
        data={"watch_log": watch_log}, flags_before=after_night, flags_after=after_night,
    ))
    if ends:
        # Use the same morning validator and executor used by the CLI demo.
        plan = plan_morning(ends, parse_state(morning_source["state"], night.targets))
        action_start = len(ports.actions)
        morning["lines"] = countersign(FIXTURE, ports, night)
        morning["status"] = "merged"
        morning["kept"] = [{"action": item.action.as_dict(), "until": item.until} for item in plan.kept]
        morning["undone"] = []
        for action, before, why in plan.undo:
            applied = restored_action(action, before) if before is not None else undo(action)
            assert applied is not None
            morning["undone"].append({"action": applied.as_dict(), "before": before, "why": why})
        morning["by_hand"] = list(plan.by_hand)
        state = dict(after_night)
        undos = iter(ports.actions[action_start:])
        for number, line in enumerate(morning["lines"]):
            text = line.split("  ", 1)[1]
            kind = ("kept" if text.startswith("KEEP ") else "undone" if text.startswith(("UNDO ", "RESTORE "))
                    else "countersigned")
            before = dict(state)
            if kind == "undone":
                operation = next(undos)
                state = dict(operation["flags_after"])
            steps.append(step(
                f"morning-{number}", "dawn", kind, morning_at,
                "Keep the new checkout off" if kind == "kept"
                else "Restore the cache flag to how it was before the night" if kind == "undone"
                else "Priya merges the demo countersign", text,
                data={"source": "actual countersign result, demo merge"}, flags_before=before, flags_after=state,
            ))
    else:
        steps.append(step(
            "morning-none", "dawn", "no_countersign", morning_at, "No overnight change needs a countersign",
            "Nothing changed overnight. The recorded keep proposal is not applied because it cannot keep an action that never happened.",
            flags_before=after_night, flags_after=after_night,
        ))

    sig = night.signature
    objects = load_yaml(FIXTURE / "gitlab.yml")
    rehearsed = rehearsal(night.oncall, night.targets, scenario, objects)
    return {
        "label": LABEL, "choices": {"signed": signed, "approved": approved},
        "rehearsal": rehearsed,
        "objects": gitlab_objects(night, ports, objects, signed, morning, rehearsed),
        "three_ways": list(three_ways()),
        "persona": {"name": night.oncall.first_name, "display_name": night.oncall.display_name, "user": night.oncall.user},
        "night": night.orders.night.isoformat(), "timezone": str(night.oncall.timezone),
        "signature": {"signed": sig is not None, "method": sig.method if sig else None,
                      "user": sig.user if sig else None, "at": sig.at.isoformat() if sig else None,
                      "commit": sig.commit if sig else None},
        "expiry": {"at": expires.isoformat(), "time": night.oncall.hhmm(expires),
                   "expired": bool(night.ledger.of("expired")), "no_automatic_revert": True},
        "orders": source_orders["orders"], "changes": changes, "left_out": dusk["left_out"],
        "dusk_question": dusk["question"],
        "counts": {"pages": len(night.ledger.of("woke")), "automatic_incidents_handled": len(night.ledger.of("acted")),
                   "approved_actions": len(night.ledger.of("approved")), "incidents": len(night.ledger.of("alert")),
                   "model_requests": len(night.ledger.of("asked"))},
        "steps": steps, "timeline": timeline, "messages": messages, "metrics": ports.samples,
        "logs": list(ports.log), "watch_log": watch_log,
        "evidence": {str(number): text for number, text in sorted(ports.evidence.items())},
        "flags": {"initial": initial_flags, "after_night": after_night, "after_morning": dict(ports.shop.flags)},
        "morning": morning,
    }
