"""The morning countersign: code undoes what the on-call person did not keep, and nothing else."""

from __future__ import annotations

import pytest

from conftest import OPS
from nightorders import Action, OrdersError
from nightorders.countersign import parse_state, plan_morning
from nightorders.orders import load_yaml

FLAG_OFF = Action(kind="flag_set", flag="new_checkout", environment="production", to="off")
CACHE_ON = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")
TRAFFIC = Action(kind="traffic_to_revision", service="shop", revision="shop-00041")
LOOSE = [(CACHE_ON, "approved by thumbs-up, 01:53"), (FLAG_OFF, "order 1, 03:13")]


def keep_flag_off():
    return {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                       "until": "the fix for !31 is in production"}]}


def test_repo_state_file_is_valid(targets):
    assert parse_state(load_yaml(OPS / "state.yml"), targets) == []


def test_kept_change_stays_and_the_rest_is_undone(targets):
    plan = plan_morning(LOOSE, parse_state(keep_flag_off(), targets))
    assert [a.describe() for a, _ in plan.undo] == ["stock_from_cache off in production"]
    assert [k.action.describe() for k in plan.kept] == ["new_checkout off in production"]
    assert plan.kept[0].until == "the fix for !31 is in production"
    assert plan.by_hand == ()


def test_empty_state_undoes_every_flag_change(targets):
    plan = plan_morning(LOOSE, parse_state({"flags": []}, targets))
    assert [a.describe() for a, _ in plan.undo] == [
        "stock_from_cache off in production", "new_checkout on in production"]


def test_a_quiet_night_needs_nothing(targets):
    plan = plan_morning([], parse_state({"flags": []}, targets))
    assert plan.undo == () and plan.by_hand == ()


def test_traffic_change_is_never_guessed_back(targets):
    plan = plan_morning([(TRAFFIC, "order 2, 04:10")], parse_state({"flags": []}, targets))
    assert plan.undo == ()
    assert plan.by_hand == ("shop traffic to revision shop-00041 (order 2, 04:10) is not kept. Undo it by hand in Cloud Run.",)


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


def test_demo_morning_keeps_the_flag_off_and_undoes_the_fallback():
    from conftest import REPO
    from nightorders.demo_night import countersign, run

    folder = REPO / "demo" / "night-2026-10-20"
    ports, night = run(folder)
    lines = countersign(folder, ports, night)
    assert any("KEEP new_checkout off in production" in line for line in lines)
    assert any("UNDO stock_from_cache off in production" in line for line in lines)
    assert ports.shop.flags == {"new_checkout": "off", "stock_from_cache": "off"}
