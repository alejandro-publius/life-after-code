"""Bounded incident memory built from observed ledger events, never model summaries.

Memory helps the next engineer draft a new plan. It grants no permission and is
not consulted by the action gate. An approval is not a verified recovery.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json

from .ledger import Event
from .model import Orders

MAX_INCIDENTS = 60
MAX_STEPS = 24
MAX_BRIEFING = 8
ACTION_KEYS = ("action", "flag", "environment", "to", "service", "revision")
OUTCOMES = {
    "recovered": ("Recovery observed", "The re-check passed after the recorded action. A future night still needs fresh evidence and a new signature."),
    "human_action": ("A person chose the fix", "A person approved this action. The ledger does not independently verify recovery after that approval."),
    "needs_review": ("Action followed by a page", "The automatic action did not finish the incident without human attention. Read the page before proposing it again."),
    "action_failed": ("Action result uncertain", "An action call failed. Check its actual state before retrying; a failed call does not prove nothing changed."),
    "escalated": ("Human attention needed", "No automatic recovery is recorded. Keep the reason for escalation in the next briefing."),
    "stood_down": ("Recovered before acting", "The alert recovered before an action. Do not credit a fix that never ran."),
    "open": ("Outcome still open", "There is not enough recorded evidence to call this incident recovered."),
}


def _plain(value: object, limit: int = 600) -> str:
    return " ".join(str(value).split())[:limit]


def _step(event: Event, orders: Orders | None) -> dict:
    action = event.data.get("action")
    item = {"at": event.at.isoformat(), "kind": event.kind, "text": _plain(event.text), "order": event.order}
    if isinstance(action, dict):
        item["action"] = {key: _plain(action[key], 160) for key in ACTION_KEYS if key in action}
    if isinstance(event.data.get("changed"), bool):
        item["changed"] = event.data["changed"]
    # Optional enrichment must not change the identity when repository access fails.
    item["id"] = sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()[:16]
    if orders is not None and event.order is not None:
        order = orders.get(event.order)
        if order is not None:
            item["because"] = _plain(order.because, 300)
    return item


def _outcome(steps: list[dict]) -> str:
    """Use event order, not a guessed causal explanation or an incident's closed flag."""
    outcome = "open"
    acted = False
    for step in steps:
        kind = step["kind"]
        if kind == "acted":
            acted, outcome = True, "open"
        elif kind == "failed":
            outcome = "action_failed"
        elif kind == "approved":
            acted, outcome = False, "human_action"
        elif kind == "recovered" and acted:
            outcome = "recovered"
        elif kind == "woke":
            if outcome != "action_failed":
                outcome = "needs_review" if acted else "escalated"
        elif kind == "stood_down" and not acted and outcome not in ("human_action", "action_failed"):
            outcome = "stood_down"
    return outcome


def remember(relay: dict, night: str, events: list[Event], orders: Orders | None = None) -> dict:
    """Upsert observed incidents into the existing leased state document.

    GitLab incident numbers identify an episode across noon rollover. Repeated
    ticks add no duplicate events. The newest 60 incidents and 24 steps survive.
    """
    saved = relay.get("incident_memory") or {}
    if orders is not None and orders.night.isoformat() != night:
        orders = None
    episodes = {entry["incident"]: deepcopy(entry) for entry in saved.get("episodes", [])}
    for event in events:
        if event.incident is None:
            continue
        episode = episodes.setdefault(event.incident, {
            "id": f"incident-{event.incident}", "incident": event.incident,
            "night": night, "title": f"Incident #{event.incident}", "steps": [],
        })
        if event.kind == "alert":
            episode["title"] = _plain(event.text, 240)
        step = _step(event, orders)
        previous = next((old for old in episode["steps"] if old["id"] == step["id"]), None)
        if previous is None:
            episode["steps"].append(step)
        else:
            previous.update(step)
        episode["steps"].sort(key=lambda item: datetime.fromisoformat(item["at"]))
    for episode in episodes.values():
        steps = episode["steps"]
        if not steps:
            continue
        episode["last_seen"] = steps[-1]["at"]
        episode["outcome"] = _outcome(steps)
        episode["outcome_label"], episode["lesson"] = OUTCOMES[episode["outcome"]]
        episode["action"] = next((step["action"] for step in reversed(steps) if "action" in step), None)
        episode["human_attention"] = any(step["kind"] == "woke" for step in steps)
        # Retain the latest of every event kind, so compacting a long incident
        # never drops the action that explains its recovery or later page.
        episode["truncated"] = bool(episode.get("truncated") or len(steps) > MAX_STEPS)
        if len(steps) > MAX_STEPS:
            selected = {step["kind"]: step["id"] for step in steps}
            retained = set(selected.values()) | {steps[0]["id"]}
            for step in reversed(steps):
                if len(retained) >= MAX_STEPS:
                    break
                retained.add(step["id"])
            episode["steps"] = [step for step in steps if step["id"] in retained]
    kept = sorted(episodes.values(), key=lambda entry: datetime.fromisoformat(entry["last_seen"]),
                  reverse=True)[:MAX_INCIDENTS]
    relay["incident_memory"] = {"version": 1, "episodes": kept}
    return view(relay)


def view(relay: dict) -> dict:
    """A detached JSON view for the live status page, replay and downloadable handoff."""
    episodes = deepcopy((relay.get("incident_memory") or {}).get("episodes", []))
    counts = Counter(episode["outcome"] for episode in episodes)
    return {"version": 1, "episodes": episodes, "counts": dict(counts),
            "limits": {"incidents": MAX_INCIDENTS, "steps_per_incident": MAX_STEPS},
            "authority": "Historical evidence only. New orders require fresh evidence and a new human signature."}


def briefing(relay: dict, before_night: str | None = None) -> list[dict]:
    """Prioritize unresolved or unsuccessful actions in the next dusk briefing."""
    episodes = view(relay)["episodes"]
    if before_night is not None:
        episodes = [episode for episode in episodes if episode["night"] < before_night]
    priority = {"action_failed": 0, "needs_review": 1, "escalated": 2, "open": 3,
                "human_action": 4, "recovered": 5, "stood_down": 6}
    episodes.sort(key=lambda entry: priority[entry["outcome"]])
    return [{key: episode[key] for key in ("incident", "night", "title", "outcome_label", "lesson", "action")}
            for episode in episodes[:MAX_BRIEFING]]


def handoff(data: dict, label: str) -> str:
    """A portable handoff from the same public observations the status page shows."""
    lines = ["# Night Orders shift handoff", "", _plain(label), "", data["authority"], ""]
    if not data["episodes"]:
        lines.append("No incident outcomes have been recorded yet.")
    for episode in data["episodes"]:
        lines += [f"## Incident #{episode['incident']}: {episode['outcome_label']}", "",
                  f"Night: {episode['night']}", "", episode["title"], "", episode["lesson"], ""]
        for step in episode["steps"]:
            lines.append(f"- {step['at']} [{step['kind']}] {step['text']}")
        if episode.get("truncated"):
            lines += ["", "Long history compacted; the latest event of each kind is retained."]
        lines.append("")
    return "\n".join(lines) + "\n"
