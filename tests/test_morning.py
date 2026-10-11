"""The live morning: log and dawn flow once, and the countersign applied once, only when the on-call person signs."""

from __future__ import annotations

from datetime import datetime

import pytest

from conftest import REPO, at
from nightorders import Change, Ledger, Signature
from nightorders.demo_night import run
from nightorders.morning import StateFile, step

KEEP_FLAG_OFF = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                            "until": "the fix for !31 is in production"}]}


class FakePorts:
    def __init__(self, fail_apply: bool = False):
        self.notes: list[str] = []
        self.flows: list[str] = []
        self.applied: list[str] = []
        self.restored: list[tuple[str, dict]] = []
        self.fail_apply = fail_apply

    def watch_note(self, text, at):
        self.notes.append(text)

    def start_dawn_flow(self, goal, at):
        self.flows.append(goal)

    def apply(self, action, at):
        if self.fail_apply:
            raise RuntimeError("flag service down")
        self.applied.append(action.describe())
        return Change(changed=True, before=None, detail="")

    def restore(self, action, before, at):
        if self.fail_apply:
            raise RuntimeError("flag service down")
        self.restored.append((action.describe(), before))
        return Change(changed=True, before=None, detail="")


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


def test_countersign_by_the_on_call_person_restores_what_was_not_kept_once(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    state = StateFile(KEEP_FLAG_OFF, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:44"), 7)
    assert ports.applied == []
    assert ports.restored == [("stock_from_cache on in production",
                               {"kind": "flag", "flag": "stock_from_cache", "environment": "production", "value": "off"})]
    note = ports.notes[-1]
    assert note.startswith("Countersign by Priya at 07:42 (merge), applied by code.")
    assert "- Kept: new_checkout off in production, until the fix for !31 is in production" in note
    assert "- Restored: stock_from_cache in production to how it was before the night (off)" in note
    assert "Undone" not in note


def test_countersign_by_someone_else_changes_nothing(night):
    relay_doc, ports = {}, FakePorts()
    state = StateFile({"flags": []}, signed(night, "2026-10-21T07:42", user="teammate"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    assert ports.applied == []
    assert relay_doc["dawn"]["countersign"] is None  # refused, and the morning stays open for her own signature
    assert "not by the on-call person" in relay_doc["dawn"]["refused"]["problems"][0]


def test_a_state_file_that_makes_a_new_change_is_refused(night):
    relay_doc, ports = {}, FakePorts()
    bad = {"flags": [{"flag": "stock_from_cache", "environment": "staging", "keep": "on", "until": "x"}]}
    state = StateFile(bad, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
    assert ports.applied == []
    assert relay_doc["dawn"]["countersign"] is None
    assert "nothing changed it last night" in relay_doc["dawn"]["refused"]["problems"][0]
    assert ports.notes[-1].splitlines()[-1] == "- Refused: Nothing was changed."


def test_a_failed_change_is_tried_again_next_tick(night):
    relay_doc = {}
    state = StateFile(KEEP_FLAG_OFF, signed(night, "2026-10-21T07:42"))
    with pytest.raises(RuntimeError):
        step(relay_doc, night, True, state, FakePorts(fail_apply=True), local(night, "2026-10-21T07:43"), 7)
    assert relay_doc["dawn"]["countersign"] is None
    ports = FakePorts()
    step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:44"), 7)
    assert [action for action, _ in ports.restored] == ["stock_from_cache on in production"]


# What the night recorded decides what the morning restores.

FLAG_OFF = {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}
TRAFFIC = {"action": "traffic_to_revision", "service": "shop", "revision": "shop-00041"}
PILOT = {"kind": "flag", "flag": "new_checkout", "environment": "production", "active": True, "strategies": [
    {"name": "userWithId", "parameters": {"userIds": ",".join(f"pilot-{n:02d}" for n in range(1, 11))},
     "scopes": [{"environment_scope": "production"}]}]}
TRAFFIC_WAS = {"kind": "traffic", "service": "shop",
               "traffic": [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}]}
KEEP_NOTHING = {"flags": []}


def morning_after(make_night, oncall, events: list[tuple[str, dict]]) -> tuple[dict, FakePorts]:
    """Run the morning for a night whose ledger holds these acted events, and a countersign keeping nothing."""
    ledger = Ledger()
    for text, data in events:
        ledger.record(at(oncall, "03:13"), "acted", text, incident=2, order=1, **data)
    night = make_night(ledger=ledger)
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, at(oncall, "07:00"), 7)
    state = StateFile(KEEP_NOTHING, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, state, ports, at(oncall, "07:43"), 7)
    return relay_doc, ports


def test_an_action_that_changed_nothing_is_not_restored(make_night, oncall):
    relay_doc, ports = morning_after(make_night, oncall, [
        ("Order 1 carried out 03:13 (already in place, nothing changed)",
         {"action": FLAG_OFF, "changed": False, "before": {**PILOT, "strategies": []}})])
    assert relay_doc["dawn"]["loose_ends"] == []
    assert ports.restored == [] and ports.applied == []
    assert ports.notes[-1].splitlines()[-1] == "- Nothing to change."


def test_a_flag_with_a_prior_pilot_rollout_is_restored_to_that_rollout(make_night, oncall):
    relay_doc, ports = morning_after(make_night, oncall, [
        ("Order 1 carried out 03:13", {"action": FLAG_OFF, "changed": True, "before": PILOT})])
    assert relay_doc["dawn"]["loose_ends"] == [{"action": FLAG_OFF, "why": "order 1, 03:13", "before": PILOT}]
    assert ports.restored == [("new_checkout off in production", PILOT)]
    assert ports.applied == []  # never "on for everyone"
    assert "- Restored: new_checkout in production to how it was before the night (on for 10 listed users)" in ports.notes[-1]


def test_an_old_record_without_a_snapshot_falls_back_to_turning_the_flag_back(make_night, oncall):
    relay_doc, ports = morning_after(make_night, oncall, [("Order 1 carried out 03:13", {"action": FLAG_OFF})])
    assert relay_doc["dawn"]["loose_ends"] == [{"action": FLAG_OFF, "why": "order 1, 03:13", "before": None}]
    assert ports.restored == [] and ports.applied == ["new_checkout on in production"]
    assert "- Undone: new_checkout on in production" in ports.notes[-1]


def test_a_traffic_change_with_a_snapshot_is_restored_and_without_one_is_left_to_a_person(make_night, oncall):
    _doc, ports = morning_after(make_night, oncall, [
        ("Order 1 carried out 03:13", {"action": TRAFFIC, "changed": True, "before": TRAFFIC_WAS})])
    assert ports.restored == [("shop traffic to revision shop-00041", TRAFFIC_WAS)]
    assert "- Restored: shop traffic to its earlier allocation (100% to the latest revision)" in ports.notes[-1]
    _doc, ports = morning_after(make_night, oncall, [("Order 1 carried out 03:13", {"action": TRAFFIC})])
    assert ports.restored == [] and ports.applied == []
    assert "- For a person: shop traffic to revision shop-00041 (order 1, 03:13) is not kept." in ports.notes[-1]


def test_the_snapshot_from_before_the_first_change_wins_when_a_target_changes_twice(make_night, oncall):
    flag_on = {**FLAG_OFF, "to": "on"}
    off_state = {**PILOT, "strategies": []}
    relay_doc, _ports = morning_after(make_night, oncall, [
        ("first", {"action": FLAG_OFF, "changed": True, "before": PILOT}),
        ("second", {"action": flag_on, "changed": True, "before": off_state})])
    assert relay_doc["dawn"]["loose_ends"] == [{"action": flag_on, "why": "order 1, 03:13", "before": PILOT}]
