"""The morning countersign: undo what the on-call person did not keep.

At dawn the flow lists the loose ends (changes made overnight and still in place) and proposes keep
or undo for each. It writes the kept ones to ops/state.yml in the countersign merge request, and the
on-call person decides by merging. Code then works out what happens: every loose end that is not
kept is undone, and kept ones are left alone. Until the merge, nothing changes.

Code refuses a state file that keeps something nobody changed last night, so the file can only keep
or undo the night's changes, never make a new one. The menu has no undo for traffic_to_revision
(code does not know which revision should serve next), so a traffic change that is not kept is
listed for a person to undo by hand, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Action, Targets
from .orders import OrdersError, action_problems

STATE_KEYS = frozenset({"flag", "environment", "keep", "until"})


@dataclass(frozen=True)
class Kept:
    action: Action
    until: str


@dataclass(frozen=True)
class MorningPlan:
    undo: tuple[tuple[Action, str], ...]  # what to apply, and why
    kept: tuple[Kept, ...]
    by_hand: tuple[str, ...]  # what a person has to do, because the menu cannot undo it


def parse_state(data: dict | None, targets: Targets) -> list[Kept]:
    """Read ops/state.yml, or raise OrdersError listing every problem."""
    entries = (data or {}).get("flags") or []
    if not isinstance(entries, list):
        raise OrdersError(["ops/state.yml: flags must be a list"])
    problems: list[str] = []
    kept: list[Kept] = []
    for number, entry in enumerate(entries, start=1):
        label = f"ops/state.yml entry {number}"
        if not isinstance(entry, dict):
            problems.append(f"{label}: must be a mapping with flag, environment, keep and until")
            continue
        extra = sorted(set(entry) - STATE_KEYS)
        if extra:
            problems.append(f"{label}: unknown keys {', '.join(extra)}")
        keep = entry.get("keep")
        if isinstance(keep, bool):  # YAML reads a bare off/on as false/true
            keep = "on" if keep else "off"
        if keep not in ("on", "off"):
            problems.append(f'{label}: keep must be "on" or "off"')
            continue
        if not entry.get("flag") or not entry.get("environment"):
            problems.append(f"{label}: needs a flag and an environment")
            continue
        action = Action(kind="flag_set", flag=str(entry["flag"]), environment=str(entry["environment"]), to=keep)
        problems.extend(f"{label}: {p}" for p in action_problems(action, targets))
        kept.append(Kept(action=action, until=str(entry.get("until") or "").strip()))
    for index, first in enumerate(kept):
        for second in kept[index + 1:]:
            if first.action.same_target(second.action):
                problems.append(f"ops/state.yml lists {first.action.flag} in {first.action.environment} twice")
    if problems:
        raise OrdersError(problems)
    return kept


def undo(action: Action) -> Action | None:
    """The action that reverses a night change, or None when the menu has no safe reverse."""
    if action.kind == "flag_set":
        return Action(kind="flag_set", flag=action.flag, environment=action.environment,
                      to="on" if action.to == "off" else "off")
    return None


def plan_morning(loose: list[tuple[Action, str]], kept: list[Kept]) -> MorningPlan:
    """What the countersign does, given last night's loose ends and the merged ops/state.yml."""
    problems = []
    for item in kept:
        match = next((action for action, _ in loose if action.same_target(item.action)), None)
        if match is None:
            problems.append(f"ops/state.yml keeps {item.action.describe()}, but nothing changed it last night")
        elif match.to != item.action.to:
            problems.append(f"ops/state.yml keeps {item.action.describe()}, but last night set it {match.to}")
    if problems:
        raise OrdersError(problems)

    undo_list: list[tuple[Action, str]] = []
    by_hand: list[str] = []
    for action, why in loose:
        if any(item.action.same_target(action) for item in kept):
            continue
        reverse = undo(action)
        if reverse is None:
            by_hand.append(f"{action.describe()} ({why}) is not kept. Undo it by hand in Cloud Run.")
        else:
            undo_list.append((reverse, f"not kept at the countersign; the night set {action.describe()} ({why})"))
    return MorningPlan(undo=tuple(undo_list), kept=tuple(kept), by_hand=tuple(by_hand))
