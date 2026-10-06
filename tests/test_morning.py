"""The live morning: log and dawn flow once, and the countersign applied once, only when the on-call person signs."""

from __future__ import annotations

from datetime import datetime

import pytest

from conftest import REPO
from nightorders import Signature
from nightorders.demo_night import run
from nightorders.morning import StateFile, step

KEEP_FLAG_OFF = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                            "until": "the fix for !31 is in production"}]}


class FakePorts:
    def __init__(self, fail_apply: bool = False):
        self.notes: list[str] = []
        self.flows: list[str] = []
        self.applied: list[str] = []
        self.fail_apply = fail_apply

    def watch_note(self, text, at):
        self.notes.append(text)

    def start_dawn_flow(self, goal, at):
        self.flows.append(goal)

    def apply(self, action, at):
        if self.fail_apply:
            raise RuntimeError("flag service down")
        self.applied.append(action.describe())


@pytest.fixture
def night():
    _ports, night = run(REPO / "demo" / "night-2026-10-20")
    return night


def local(night, text):
    return datetime.fromisoformat(text).replace(tzinfo=night.oncall.timezone)


def signed(night, at, user="alex-velazquez"):
    return Signature(method="merge", user=user, at=local(night, at), commit="c0ffee")


def test_nothing_happens_before_the_watch_ends(night):
    relay_doc, ports = {}, FakePorts()
    assert step(relay_doc, night, False, None, ports, local(night, "2026-10-21T06:59"), 7) == []
    assert relay_doc == {} and ports.notes == [] and ports.flows == []


def test_at_the_watch_end_the_log_is_posted_and_the_dawn_flow_started_once(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:01"), 7)
    assert len(ports.notes) == 1 and ports.notes[0].startswith("## Watch log, night of Tue 20 Oct")
    assert len(ports.flows) == 1 and ports.flows[0].startswith("Watch issue #7, night of Tue 20 Oct.")
    assert [item["action"]["flag"] for item in relay_doc["dawn"]["loose_ends"]] == ["stock_from_cache", "new_checkout"]


def test_without_a_watch_issue_the_relay_keeps_the_record_but_posts_nothing(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), None)
    assert relay_doc["dawn"]["night"] == "2026-10-20"
    assert ports.notes == [] and ports.flows == []


def test_no_countersign_yet_changes_nothing(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, StateFile({"flags": []}, None), ports, local(night, "2026-10-21T07:00"), 7)
    assert ports.applied == [] and relay_doc["dawn"]["countersign"] is None


def test_an_old_state_file_from_before_the_night_ended_changes_nothing(night):
    relay_doc, ports = {}, FakePorts()
    old = StateFile({"flags": []}, signed(night, "2026-10-20T09:00"))
    step(relay_doc, night, True, old, ports, local(night, "2026-10-21T07:00"), 7)
    assert ports.applied == [] and relay_doc["dawn"]["countersign"] is None


def test_countersign_by_the_on_call_person_undoes_what_was_not_kept_once(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    state = StateFile(KEEP_FLAG_OFF, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:44"), 7)
    assert ports.applied == ["stock_from_cache off in production"]
    note = ports.notes[-1]
    assert note.startswith("Countersign by Priya at 07:42 (merge), applied by code.")
    assert "- Kept: new_checkout off in production, until the fix for !31 is in production" in note
    assert "- Undone: stock_from_cache off in production" in note


def test_countersign_by_someone_else_changes_nothing(night):
    relay_doc, ports = {}, FakePorts()
    state = StateFile({"flags": []}, signed(night, "2026-10-21T07:42", user="teammate"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    assert ports.applied == []
    assert "not by the on-call person" in relay_doc["dawn"]["countersign"]["problems"][0]


def test_a_state_file_that_makes_a_new_change_is_refused(night):
    relay_doc, ports = {}, FakePorts()
    bad = {"flags": [{"flag": "stock_from_cache", "environment": "staging", "keep": "on", "until": "x"}]}
    state = StateFile(bad, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    assert ports.applied == []
    assert "nothing changed it last night" in relay_doc["dawn"]["countersign"]["problems"][0]
    assert ports.notes[-1].splitlines()[-1] == "- Refused: Nothing was changed."


def test_a_failed_change_is_tried_again_next_tick(night):
    relay_doc = {}
    state = StateFile(KEEP_FLAG_OFF, signed(night, "2026-10-21T07:42"))
    with pytest.raises(RuntimeError):
        step(relay_doc, night, True, state, FakePorts(fail_apply=True), local(night, "2026-10-21T07:43"), 7)
    assert relay_doc["dawn"]["countersign"] is None
    ports = FakePorts()
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:44"), 7)
    assert ports.applied == ["stock_from_cache off in production"]
