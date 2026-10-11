"""The one answer format shared by the baselines and the model (later the Duo flow).

A proposal is only a proposal. Code checks its shape here, then replays it: a new path
counts only if the replay is clear, and a fix counts only if the fixed page can be walked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any

from nomouse.journey import Journey, JourneyError, Step, parse_step

ROUTES = ("still_usable", "barrier", "unsure")
MAX_NEW_STEPS = 8
MAX_FIX_CHARS = 2_000
WCAG = re.compile(r"^\d\.\d{1,2}\.\d{1,2}$")

# JSON Schema for the structured answer. The Duo flow's final answer must match it too.
SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["route", "why"],
    "properties": {
        "route": {"type": "string", "enum": list(ROUTES)},
        "why": {"type": "string", "maxLength": 600},
        "path": {
            "type": "object", "additionalProperties": False,
            "required": ["replace_from", "replace_to", "steps"],
            "properties": {
                "replace_from": {"type": "integer", "minimum": 0},
                "replace_to": {"type": "integer", "minimum": 0},
                "steps": {"type": "array", "maxItems": MAX_NEW_STEPS, "items": {
                    "type": "object", "additionalProperties": False, "required": ["do"],
                    "properties": {"do": {"type": "string", "enum": ["find", "press", "type", "expect_heading"]},
                                   "role": {"type": "string"}, "name": {"type": "string"},
                                   "key": {"type": "string"}, "text": {"type": "string"}}}},
            },
        },
        "barrier": {
            "type": "object", "additionalProperties": False, "required": ["control", "problem"],
            "properties": {"control": {"type": "string", "maxLength": 200},
                           "problem": {"type": "string", "maxLength": 400},
                           "wcag": {"type": "string", "maxLength": 12}},
        },
        "fix": {
            "type": "object", "additionalProperties": False, "required": ["file", "find", "replace"],
            "properties": {"file": {"type": "string", "maxLength": 200},
                           "find": {"type": "string", "maxLength": MAX_FIX_CHARS},
                           "replace": {"type": "string", "maxLength": MAX_FIX_CHARS}},
        },
    },
}


class ProposalError(ValueError):
    """The answer is malformed. It is recorded as unusable; nothing is replayed."""


@dataclass(frozen=True)
class Fix:
    file: str
    find: str
    replace: str


@dataclass(frozen=True)
class Proposal:
    source: str  # "B1", "B2" or a model label
    route: str
    why: str
    replace_from: int | None = None
    replace_to: int | None = None
    steps: tuple[Step, ...] = field(default_factory=tuple)
    control: str = ""
    problem: str = ""
    wcag: str = ""
    fix: Fix | None = None

    def as_dict(self) -> dict:
        data: dict[str, Any] = {"source": self.source, "route": self.route, "why": self.why}
        if self.steps:
            data["path"] = {"replace_from": self.replace_from, "replace_to": self.replace_to,
                            "steps": [s.as_dict() for s in self.steps]}
        if self.control or self.problem:
            data["barrier"] = {"control": self.control, "problem": self.problem, "wcag": self.wcag}
        if self.fix:
            data["fix"] = {"file": self.fix.file, "find": self.fix.find, "replace": self.fix.replace}
        return data


def parse(answer: Any, *, source: str, journey: Journey, failed_step: int,
          template_files: list[str]) -> Proposal:
    """Check an answer strictly. Raises ProposalError rather than guessing what was meant."""
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)
        except json.JSONDecodeError as exc:
            raise ProposalError(f"not JSON: {exc.msg}") from None
    if not isinstance(answer, dict):
        raise ProposalError("the answer must be a JSON object")
    extra = set(answer) - set(SCHEMA["properties"])
    if extra:
        raise ProposalError(f"unknown keys: {sorted(extra)}")
    route = answer.get("route")
    if route not in ROUTES:
        raise ProposalError(f"route must be one of {ROUTES}")
    why = answer.get("why")
    if not isinstance(why, str) or not why.strip():
        raise ProposalError("why is required")
    proposal = Proposal(source=source, route=route, why=why.strip()[:600])

    if route == "still_usable":
        path = answer.get("path")
        if not isinstance(path, dict):
            raise ProposalError("still_usable needs a path")
        start, end = path.get("replace_from"), path.get("replace_to")
        if not (isinstance(start, int) and isinstance(end, int)) or isinstance(start, bool) or isinstance(end, bool):
            raise ProposalError("replace_from and replace_to must be integers")
        last = len(journey.steps) - 1
        # The answer may only rewrite the broken part of the walk, never the final check.
        if not (0 <= start <= failed_step < end <= last) or start < failed_step - 3 or end > failed_step + 4:
            raise ProposalError(f"the path may only replace steps around step {failed_step}, before the last step")
        raw_steps = path.get("steps")
        if not isinstance(raw_steps, list) or not 1 <= len(raw_steps) <= MAX_NEW_STEPS:
            raise ProposalError(f"a path needs 1 to {MAX_NEW_STEPS} steps")
        try:
            steps = tuple(parse_step(step) for step in raw_steps)
        except (JourneyError, TypeError) as exc:
            raise ProposalError(f"bad step: {exc}") from None
        proposal = Proposal(source=source, route=route, why=proposal.why,
                            replace_from=start, replace_to=end, steps=steps)
    elif route == "barrier":
        barrier = answer.get("barrier")
        if not isinstance(barrier, dict) or not str(barrier.get("problem", "")).strip():
            raise ProposalError("barrier needs barrier.control and barrier.problem")
        wcag = str(barrier.get("wcag", "") or "")
        if wcag and not WCAG.match(wcag):
            raise ProposalError("barrier.wcag must look like 4.1.2")
        fix = None
        raw_fix = answer.get("fix")
        if raw_fix is not None:
            if not isinstance(raw_fix, dict):
                raise ProposalError("fix must be an object")
            file, find, replace_ = (str(raw_fix.get(k, "")) for k in ("file", "find", "replace"))
            if file not in template_files:
                raise ProposalError("fix.file must be one of the page's template files")
            if not find or len(find) > MAX_FIX_CHARS or len(replace_) > MAX_FIX_CHARS:
                raise ProposalError(f"fix.find must be non-empty and both sides at most {MAX_FIX_CHARS} characters")
            fix = Fix(file=file, find=find, replace=replace_)
        proposal = Proposal(source=source, route=route, why=proposal.why,
                            control=str(barrier.get("control", ""))[:200],
                            problem=str(barrier.get("problem", ""))[:400], wcag=wcag, fix=fix)
    return proposal


def apply_path(journey: Journey, proposal: Proposal) -> Journey:
    """The journey with the proposed segment swapped in. Replay decides whether it works."""
    assert proposal.route == "still_usable" and proposal.replace_from is not None
    steps = list(journey.steps)
    steps[proposal.replace_from:proposal.replace_to] = list(proposal.steps)
    return journey.with_steps(steps)
