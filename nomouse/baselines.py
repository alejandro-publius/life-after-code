"""Two baselines that judge a broken walk without a model, so the model has something to beat.

B1 is a simple rule over what was heard on the page where the walk broke: a control with no
meaningful name is a barrier, and a control of the same role with a similar name is the new
path. It never opens a browser.

B2 searches with the browser. It swaps the failed step for each named control it heard (a
rename), or for a named control followed by one on the next page (an added step), replays
the whole journey each time and keeps the first replay that code calls clear. The search has
hard limits on replays and seconds, and every walk it opens is closed.

B2 presses Enter only on buttons, links and similar controls. Enter in a field, a select or a
check box submits the form through its default button, which may be the very button that has
no name, so a path through it would hide the barrier instead of finding a way round it.
"""

from __future__ import annotations

from difflib import SequenceMatcher
import time

from nomouse.announce import Announcement
from nomouse.guards import ACTIONABLE, FIELDS, is_junk_name
from nomouse.journey import Journey, Result, Step, replay
from nomouse.proposal import Proposal, parse

MATCH_THRESHOLD = 0.6
MAX_CANDIDATES = 8  # controls tried in place of the failed step
MAX_INTERMEDIATE = 5  # controls tried as an added step before the expected one
MAX_NEXT = 5  # controls tried on the page that an added step leads to
SYNONYMS = {
    "pay": ("place order", "complete purchase", "buy now", "confirm order", "submit order", "pay"),
    "checkout": ("proceed to checkout", "continue to checkout", "go to checkout", "checkout"),
    "add to cart": ("add to bag", "add to basket", "add to cart"),
}
# Roles where Enter activates the control itself rather than submitting a form around it.
ENTER_ROLES = frozenset({"button", "link", "menuitem", "menuitemcheckbox", "menuitemradio", "tab", "treeitem"})
PRESS_ENTER = Step(do="press", key="Enter")
NOT_FOUND = "the expected control was not found"
NO_PATH = "no path with named controls places the order"


def _fold(text: str) -> str:
    return " ".join((text or "").split()).casefold()


def _find(item: Announcement) -> Step:
    return Step(do="find", role=item.role, name=item.name)


def _patchable(journey: Journey, failed: int | None) -> bool:
    """A path may replace the failed step only if it is not the final check (proposal.parse)."""
    return failed is not None and 0 <= failed < len(journey.steps) - 1


def _unnamed(heard: list[Announcement]) -> Announcement | None:
    """The first control a person would press but could not identify by its name."""
    return next((item for item in heard if item.role in ACTIONABLE and is_junk_name(item.name)), None)


def _unnamed_problem(item: Announcement) -> str:
    if not item.name.strip():
        return f'a {item.role} is announced only as "{item.spoken()}", so a screen reader user cannot tell what it does'
    return f'a {item.role} is announced as "{item.name}", a name that does not say what it does'


def _expected_control(journey: Journey, failed: int | None) -> str:
    if failed is None or not 0 <= failed < len(journey.steps) or journey.steps[failed].do != "find":
        return ""
    step = journey.steps[failed]
    return Announcement(role=step.role, name=step.name).spoken()


def _answer(source: str, journey: Journey, result: Result, answer: dict) -> Proposal:
    """Build the proposal through the same strict checks a model's answer goes through."""
    failed = result.failed_step if result.failed_step is not None else -1
    return parse(answer, source=source, journey=journey, failed_step=failed, template_files=[])


def _path(source: str, journey: Journey, result: Result, steps: list[Step], why: str) -> Proposal:
    failed = result.failed_step
    return _answer(source, journey, result, {
        "route": "still_usable", "why": why,
        "path": {"replace_from": failed, "replace_to": failed + 1, "steps": [s.as_dict() for s in steps]},
    })


def _barrier(source: str, journey: Journey, result: Result, *, control: str, problem: str, wcag: str,
             why: str) -> Proposal:
    barrier = {"control": control, "problem": problem}
    if wcag:
        barrier["wcag"] = wcag
    return _answer(source, journey, result, {"route": "barrier", "why": why, "barrier": barrier})


def _closest(step: Step, heard: list[Announcement]) -> Announcement | None:
    """The heard control of the same role whose name is most like the expected one, if close enough."""
    best, best_ratio = None, 0.0
    for item in heard:
        if item.role != step.role or not item.name.strip():
            continue
        ratio = SequenceMatcher(None, _fold(step.name), _fold(item.name)).ratio()
        if ratio > best_ratio:  # strictly greater, so the earlier control in tab order wins a tie
            best, best_ratio = item, ratio
    return best if best_ratio >= MATCH_THRESHOLD else None


def b1(journey: Journey, result: Result) -> Proposal:
    """A simple rule over the tab order on the page where the walk broke. No browser."""
    unnamed = _unnamed(result.heard)
    if unnamed is not None:
        return _barrier("B1", journey, result, control=unnamed.spoken(), problem=_unnamed_problem(unnamed),
                        wcag="4.1.2", why="B1 rule: a control on the page where the walk broke has no meaningful name.")
    failed = result.failed_step
    step = journey.steps[failed] if _patchable(journey, failed) else None
    if step is not None and step.do == "find":
        match = _closest(step, result.heard)
        if match is not None:
            why = f'B1 rule: every control is named, and "{match.name}" is the {match.role} closest to "{step.name}".'
            return _path("B1", journey, result, [_find(match)], why)
    return _barrier("B1", journey, result, control=_expected_control(journey, failed), problem=NOT_FOUND, wcag="",
                    why="B1 rule: no heard control of the expected role has a name close to the expected one.")


def _synonyms(name: str) -> tuple[str, ...]:
    text = _fold(name)
    return tuple(word for key, words in SYNONYMS.items() if key in text for word in words)


def _fits(role: str, after: Step, expected_role: str) -> bool:
    """Whether a control with this role can stand in for the expected one, given the step after it."""
    if after.do == "type":
        return role in FIELDS
    if after.do == "press" and after.key == "Enter":
        return role in ENTER_ROLES
    if after.do == "press" and after.key == "Space":
        return role in ACTIONABLE - FIELDS
    return role == expected_role


def _ranked(heard: list[Announcement], expected: Step, after: Step) -> list[Announcement]:
    """Named, meaningful controls that could take the expected step's place, most likely first.

    The expected control itself first, then the same role, then names that contain a synonym
    of the expected name, then tab order.
    """
    words = _synonyms(expected.name)
    usable: list[Announcement] = []
    seen: set[tuple[str, str]] = set()
    for item in heard:
        if _key(item) in seen or item.role not in ACTIONABLE | FIELDS or is_junk_name(item.name):
            continue
        if _fits(item.role, after, expected.role):
            seen.add(_key(item))
            usable.append(item)

    def rank(pair: tuple[int, Announcement]) -> tuple:
        index, item = pair
        name = _fold(item.name)
        return (name != _fold(expected.name), item.role != expected.role, not any(w in name for w in words), index)

    return [item for _, item in sorted(enumerate(usable), key=rank)]


def _key(item: Announcement) -> tuple[str, str]:
    return item.role, _fold(item.name)


def _browser_failures() -> tuple[type[BaseException], ...]:
    """Errors that mean one replay could not run, not that the search itself went wrong."""
    try:
        from playwright.sync_api import Error
    except ImportError:  # B1 and the limits work without Playwright installed
        return (OSError,)
    return (Error, OSError)


class _Replays:
    """Runs replays in fresh walks, counts them and refuses to start one past either limit."""

    def __init__(self, walker, variant: str | None, max_replays: int, max_seconds: float):
        self.walker = walker
        self.variant = variant
        self.max_replays = max_replays
        self.deadline = time.monotonic() + max_seconds
        self.used = 0

    @property
    def spent(self) -> bool:
        return self.used >= self.max_replays or time.monotonic() >= self.deadline

    def run(self, journey: Journey, *, evidence: bool = False) -> Result | None:
        """One replay, always closed afterwards. None when a limit is reached or the browser failed."""
        if self.spent:
            return None
        self.used += 1
        walk = None
        try:
            walk = self.walker.open(self.variant)
            return replay(walk, journey, collect_evidence=evidence)
        except _browser_failures():
            return None
        finally:
            if walk is not None:
                walk.close()


def _replaced(journey: Journey, failed: int, segment: list[Step]) -> Journey:
    return journey.with_steps(list(journey.steps[:failed]) + segment + list(journey.steps[failed + 1:]))


def _swaps(replays: _Replays, journey: Journey, failed: int,
           heard: list[Announcement]) -> tuple[list[Step] | None, dict[tuple[str, str], list[Announcement]]]:
    """Attempt 1: the control was renamed or replaced. Swap in each candidate and replay.

    Also returns, per candidate, what Tab reached on the page that pressing it led to, when the
    replay broke right after that press. Attempt 2 reuses it instead of replaying a prefix.
    """
    expected, after = journey.steps[failed], journey.steps[failed + 1]
    landed: dict[tuple[str, str], list[Announcement]] = {}
    unchanged = (expected.role, _fold(expected.name))  # swapping it in would replay the same journey
    candidates = [c for c in _ranked(heard, expected, after) if _key(c) != unchanged]
    for item in candidates[:MAX_CANDIDATES]:
        outcome = replays.run(_replaced(journey, failed, [_find(item)]), evidence=True)
        if outcome is None:
            continue
        if outcome.clear:
            return [_find(item)], landed
        # Broken or refused at the step after Enter: that step changed nothing, so the evidence
        # is the tab order of the page Enter led to.
        if after == PRESS_ENTER and outcome.failed_step == failed + 2 and outcome.verdict in ("broken", "refused"):
            landed[_key(item)] = outcome.heard
    return None, landed


def _heard_after(replays: _Replays, prefix: Journey) -> list[Announcement]:
    """What Tab reaches once the prefix has run, or nothing if it broke or already placed the order."""
    outcome = replays.run(prefix, evidence=True)
    return outcome.heard if outcome is not None and outcome.verdict == "no_order" else []


def _added_steps(replays: _Replays, journey: Journey, failed: int, heard: list[Announcement],
                 landed: dict[tuple[str, str], list[Announcement]]) -> list[Step] | None:
    """Attempt 2: a step was added. Press X, then find the expected control or its replacement
    among the controls heard on the page X leads to."""
    expected, after = journey.steps[failed], journey.steps[failed + 1]
    for x in _ranked(heard, expected, PRESS_ENTER)[:MAX_INTERMEDIATE]:
        press_x = [_find(x), PRESS_ENTER]
        heard_next = landed.get(_key(x))
        if heard_next is None:
            heard_next = _heard_after(replays, journey.with_steps(list(journey.steps[:failed]) + press_x))
        for y in [c for c in _ranked(heard_next, expected, after) if _key(c) != _key(x)][:MAX_NEXT]:
            outcome = replays.run(_replaced(journey, failed, press_x + [_find(y)]))
            if outcome is not None and outcome.clear:
                return press_x + [_find(y)]
    return None


def _search(walker, journey: Journey, result: Result, variant: str | None, max_replays: int,
            max_seconds: float) -> tuple[list[Step] | None, int]:
    """The first accepted replacement for the failed step, and the number of replays used."""
    failed = result.failed_step
    if not _patchable(journey, failed) or journey.steps[failed].do != "find":
        return None, 0
    replays = _Replays(walker, variant, max_replays, max_seconds)
    segment, landed = _swaps(replays, journey, failed, result.heard)
    if segment is None:
        segment = _added_steps(replays, journey, failed, result.heard, landed)
    return segment, replays.used


def find_named_path(walker, journey: Journey, result: Result, variant: str | None, *, max_replays: int = 40,
                    max_seconds: float = 180) -> tuple[Journey | None, int]:
    """A journey that replays clear on this variant pressing only named controls, or None.

    Also returns how many replays the search used. Limits are checked before each replay.
    """
    segment, used = _search(walker, journey, result, variant, max_replays, max_seconds)
    if segment is None:
        return None, used
    return _replaced(journey, result.failed_step, segment), used


def b2(walker, journey: Journey, result: Result, variant: str | None, *, max_replays: int = 40,
       max_seconds: float = 180) -> Proposal:
    """The bounded search as a proposal: the accepted path, or a barrier when none was found."""
    segment, used = _search(walker, journey, result, variant, max_replays, max_seconds)
    if segment is not None:
        why = (f"B2 search: replay {used} placed the order pressing only named controls: "
               + "; ".join(step.describe() for step in segment) + ".")
        return _path("B2", journey, result, segment, why)
    why = f"B2 search: {used} replay(s) that press only named controls; none placed the order."
    unnamed = _unnamed(result.heard)
    if unnamed is not None:
        return _barrier("B2", journey, result, control=unnamed.spoken(), problem=_unnamed_problem(unnamed),
                        wcag="4.1.2", why=why)
    return _barrier("B2", journey, result, control=_expected_control(journey, result.failed_step), problem=NO_PATH,
                    wcag="", why=why)
