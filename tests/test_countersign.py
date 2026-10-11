"""The morning countersign: code restores what the on-call person did not keep, and nothing else."""

from __future__ import annotations

import pytest

from conftest import OPS
from nightorders import Action, OrdersError
from nightorders.countersign import describe_restored, parse_state, plan_morning
from nightorders.dawn import LooseEnd
from nightorders.orders import load_yaml

FLAG_OFF = Action(kind="flag_set", flag="new_checkout", environment="production", to="off")
CACHE_ON = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")
TRAFFIC = Action(kind="traffic_to_revision", service="shop", revision="shop-00041")
PILOT = {"kind": "flag", "flag": "new_checkout", "environment": "production", "active": True, "strategies": [
    {"name": "userWithId", "parameters": {"userIds": ",".join(f"pilot-{n:02d}" for n in range(1, 11))},
     "scopes": [{"environment_scope": "production"}]}]}
CACHE_WAS_OFF = {"kind": "flag", "flag": "stock_from_cache", "environment": "production", "active": True,
                 "strategies": []}
TRAFFIC_WAS = {"kind": "traffic", "service": "shop",
               "traffic": [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}]}
LOOSE = [LooseEnd(CACHE_ON, "approved by thumbs-up, 01:53", CACHE_WAS_OFF), LooseEnd(FLAG_OFF, "order 1, 03:13", PILOT)]


def keep_flag_off():
    return {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                       "until": "the fix for !31 is in production"}]}


def test_repo_state_file_is_valid(targets):
    assert parse_state(load_yaml(OPS / "state.yml"), targets) == []


def test_kept_change_stays_and_the_rest_is_restored_from_its_snapshot(targets):
    plan = plan_morning(LOOSE, parse_state(keep_flag_off(), targets))
    assert plan.undo == ((CACHE_ON, CACHE_WAS_OFF,
                          "not kept at the countersign; the night set stock_from_cache on in production "
                          "(approved by thumbs-up, 01:53)"),)
    assert [k.action.describe() for k in plan.kept] == ["new_checkout off in production"]
    assert plan.kept[0].until == "the fix for !31 is in production"
    assert plan.by_hand == ()


def test_empty_state_restores_every_night_change_to_its_snapshot(targets):
    plan = plan_morning(LOOSE, parse_state({"flags": []}, targets))
    assert [(action, before) for action, before, _ in plan.undo] == [(CACHE_ON, CACHE_WAS_OFF), (FLAG_OFF, PILOT)]
    # The pilot rollout comes back, not a flag on for everyone.
    assert describe_restored(FLAG_OFF, PILOT) == (
        "new_checkout in production to how it was before the night (on for 10 listed users)")
    assert describe_restored(CACHE_ON, CACHE_WAS_OFF) == (
        "stock_from_cache in production to how it was before the night (off)")


def test_a_quiet_night_needs_nothing(targets):
    plan = plan_morning([], parse_state({"flags": []}, targets))
    assert plan.undo == () and plan.by_hand == ()


def test_traffic_change_with_a_snapshot_is_restored_by_code(targets):
    plan = plan_morning([LooseEnd(TRAFFIC, "order 2, 04:10", TRAFFIC_WAS)], parse_state({"flags": []}, targets))
    assert [(action, before) for action, before, _ in plan.undo] == [(TRAFFIC, TRAFFIC_WAS)]
    assert plan.by_hand == ()
    assert describe_restored(TRAFFIC, TRAFFIC_WAS) == (
        "shop traffic to its earlier allocation (100% to the latest revision)")


def test_traffic_change_without_a_snapshot_is_never_guessed_back(targets):
    plan = plan_morning([LooseEnd(TRAFFIC, "order 2, 04:10")], parse_state({"flags": []}, targets))
    assert plan.undo == ()
    assert plan.by_hand == ("shop traffic to revision shop-00041 (order 2, 04:10) is not kept. Undo it by hand in Cloud Run.",)


def test_flag_change_without_a_snapshot_is_still_turned_back(targets):
    plan = plan_morning([LooseEnd(FLAG_OFF, "order 1, 03:13")], parse_state({"flags": []}, targets))
    assert plan.undo == ((FLAG_OFF, None,
                          "not kept at the countersign; the night set new_checkout off in production (order 1, 03:13)"),)


def test_state_file_cannot_make_a_new_change(targets):
    state = {"flags": [{"flag": "stock_from_cache", "environment": "staging", "keep": "on", "until": "x"}]}
    with pytest.raises(OrdersError) as error:
        plan_morning(LOOSE, parse_state(state, targets))
    assert "nothing changed it last night" in error.value.problems[0]


def test_state_file_cannot_flip_a_night_change(targets):
    state = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "on", "until": "x"}]}
    with pytest.raises(OrdersError) as error:
        plan_morning(LOOSE, parse_state(state, targets))
    assert "last night set it off" in error.value.problems[0]


def test_unknown_flag_refused(targets):
    state = {"flags": [{"flag": "delete_everything", "environment": "production", "keep": "off"}]}
    with pytest.raises(OrdersError) as error:
        parse_state(state, targets)
    assert "flag delete_everything is not in ops/targets.yml" in error.value.problems[0]


def test_unknown_key_refused(targets):
    state = keep_flag_off()
    state["flags"][0]["also_run"] = "rm -rf /"
    with pytest.raises(OrdersError) as error:
        parse_state(state, targets)
    assert "unknown keys also_run" in error.value.problems[0]


def test_bare_yaml_off_is_accepted(targets):
    state = keep_flag_off()
    state["flags"][0]["keep"] = False
    assert parse_state(state, targets)[0].action.to == "off"


def test_same_flag_twice_refused(targets):
    state = keep_flag_off()
    state["flags"].append(dict(state["flags"][0]))
    with pytest.raises(OrdersError) as error:
        parse_state(state, targets)
    assert "twice" in error.value.problems[0]


def test_cli_checks_the_state_file(tmp_path, capsys):
    from nightorders import cli

    assert cli.main(["state", str(OPS / "state.yml"), "--ops", str(OPS)]) == 0
    bad = tmp_path / "state.yml"
    bad.write_text('flags:\n  - {flag: delete_everything, environment: production, keep: "off"}\n')
    assert cli.main(["state", str(bad), "--ops", str(OPS)]) == 1
    assert "cannot be countersigned" in capsys.readouterr().out


def test_demo_morning_keeps_the_flag_off_and_restores_the_fallback():
    from conftest import REPO
    from nightorders.demo_night import countersign, run

    folder = REPO / "demo" / "night-2026-10-20"
    ports, night = run(folder)
    lines = countersign(folder, ports, night)
    assert any("KEEP new_checkout off in production" in line for line in lines)
    assert lines[-1] == ("07:42  RESTORE stock_from_cache to off in production: not kept at the countersign; "
                         "the night set stock_from_cache on in production (approved by thumbs-up, 01:53)")
    assert not any("UNDO" in line for line in lines)
    assert ports.log[-1] == "07:42  RESTORE stock_from_cache to off in production"
    assert ports.shop.flags == {"new_checkout": "off", "stock_from_cache": "off"}
    restored = ports.actions[-1]
    assert restored["action"] == {"action": "flag_set", "flag": "stock_from_cache", "environment": "production",
                                  "to": "off"}
    assert restored["restored_to"] == {"kind": "flag", "flag": "stock_from_cache", "environment": "production",
                                       "value": "off"}


def test_dawn_goal_lists_the_loose_ends_from_the_ledger():
    from conftest import REPO
    from nightorders.dawn import dawn_goal
    from nightorders.demo_night import run

    _ports, night = run(REPO / "demo" / "night-2026-10-20")
    goal = dawn_goal(night, watch_issue=7)
    assert goal.splitlines()[0] == "Watch issue #7, night of Tue 20 Oct. Code posted the watch log there."
    assert "- stock_from_cache on in production (approved by thumbs-up, 01:53)" in goal
    assert "- new_checkout off in production (order 1, 03:13)" in goal
