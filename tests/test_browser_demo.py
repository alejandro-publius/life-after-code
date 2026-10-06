"""The browser replay uses recorded demo data and the real two-key decisions."""

from __future__ import annotations

import builtins
import copy
import io
import json
import os
import socket
from datetime import datetime, timedelta
from itertools import groupby
from pathlib import Path

import pytest

from conftest import REPO
from nightorders import browser_demo, demo_night

DEMO = REPO / "demo" / "night-2026-10-20"
INITIAL_FLAGS = {"new_checkout": "on", "stock_from_cache": "off"}


def _events(result: dict, kind: str) -> list[dict]:
    return [event for event in result["timeline"] if event["kind"] == kind]


def _sample(result: dict, time: str) -> dict:
    return next(sample for sample in result["metrics"] if sample["time"] == time)


def test_signed_approved_replay_has_a_complete_json_contract():
    result = browser_demo.replay()

    # A response must survive a strict JSON encoder before it reaches the browser.
    assert json.loads(json.dumps(result, allow_nan=False)) == result
    assert "DEMO" in result["label"].upper()
    assert result["choices"] == {"signed": True, "approved": True}
    assert "Priya" in str(result["persona"])
    assert result["night"] == "2026-10-20"
    assert result["timezone"] == "America/Los_Angeles"
    assert result["signature"]["signed"] is True
    assert [order["id"] for order in result["orders"]] == [1, 2]
    assert [phase for phase, _ in groupby(step["phase"] for step in result["steps"])] == ["dusk", "night", "dawn"]
    assert result["counts"] == {
        "pages": 1,
        "automatic_incidents_handled": 1,
        "approved_actions": 1,
        "incidents": 2,
        "model_requests": 2,
    }
    for event in result["timeline"]:
        assert {"at", "time", "kind", "text", "incident", "order", "data"} <= event.keys()
        assert datetime.fromisoformat(event["at"]).tzinfo is not None
    assert result["flags"] == {
        "initial": INITIAL_FLAGS,
        "after_night": {"new_checkout": "off", "stock_from_cache": "on"},
        "after_morning": {"new_checkout": "off", "stock_from_cache": "off"},
    }
    assert "\u2013" not in json.dumps(result, ensure_ascii=False)
    assert "\u2014" not in json.dumps(result, ensure_ascii=False)


def test_first_incident_needs_a_person_despite_an_eligible_signed_order():
    result = browser_demo.replay()
    first_asked = _events(result, "asked")[0]
    declined = _events(result, "declined")
    page = _events(result, "woke")

    assert first_asked["incident"] == 1
    assert "order 1" in first_asked["text"]
    assert len(declined) == 1 and declined[0]["incident"] == 1
    assert declined[0]["data"]["recorded_reply"]["declined"]["id"] == 1
    assert "old path" in declined[0]["text"]
    assert "20.3%" in declined[0]["text"]
    assert len(page) == 1 and page[0]["incident"] == 1
    assert not any(event["incident"] == 1 for event in _events(result, "acted"))

    # Both paths fail. The model's recorded decline prevents the eligible rollback.
    at_decline = _sample(result, declined[0]["time"])
    assert at_decline["old_rate"] > 0.2
    assert at_decline["new_rate"] > 0.2
    assert at_decline["flags_before"] == at_decline["flags_after"] == INITIAL_FLAGS

    messages = result["messages"]
    assert len(messages) == 1
    assert {"incident", "at", "time", "lines", "suggestion", "approval"} <= messages[0].keys()
    assert messages[0]["incident"] == 1
    assert len(messages[0]["lines"]) >= 3
    assert "both paths" in messages[0]["lines"][0]
    assert messages[0]["suggestion"] == {
        "action": "flag_set", "flag": "stock_from_cache", "environment": "production", "to": "on",
    }
    assert messages[0]["approval"] == "approved"


def test_second_incident_acts_only_with_code_checks_and_a_recorded_request():
    result = browser_demo.replay()
    automatic = _events(result, "acted")
    approvals = _events(result, "approved")

    assert len(automatic) == len(approvals) == 1
    assert automatic[0]["incident"] == 2 and automatic[0]["order"] == 1
    assert automatic[0]["data"]["recorded_reply"]["order"] == 1
    assert "recorded" in automatic[0]["data"]["reply_source"]
    assert automatic[0]["data"]["action"] == result["orders"][0]["do"]
    assert automatic[0]["data"]["action"] == {
        "action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off",
    }
    assert approvals[0]["data"]["action"]["flag"] == "stock_from_cache"
    assert any(event["incident"] == 2 for event in _events(result, "asked"))
    assert "Checks:" in automatic[0]["text"]
    assert "signed" in automatic[0]["text"]
    assert "action and target taken from the signed file" in automatic[0]["text"]
    recovered = _events(result, "recovered")
    assert len(recovered) == 1 and recovered[0]["incident"] == 2
    assert recovered[0]["time"] == "03:23" and "No page." in recovered[0]["text"]
    # The planted request to roll back every service cannot widen either action.
    assert all(event["data"]["action"]["action"] == "flag_set" for event in automatic + approvals)


def test_samples_describe_the_completed_minute_and_the_action_that_follows():
    result = browser_demo.replay()
    assert 500 < len(result["metrics"]) <= demo_night.MAX_DEMO_STEPS
    first_at = datetime.fromisoformat(result["metrics"][0]["at"])
    for minute, sample in enumerate(result["metrics"]):
        assert {"minute", "at", "sampled_at", "time", "old_rate", "new_rate", "all_rate",
                "flags_before", "flags_after"} <= sample.keys()
        at = datetime.fromisoformat(sample["at"])
        sampled_at = datetime.fromisoformat(sample["sampled_at"])
        assert at.tzinfo is not None and sampled_at.tzinfo is not None
        assert sample["minute"] == minute
        assert at == first_at + timedelta(minutes=minute)
        assert sampled_at == at - timedelta(minutes=1)
        assert 0 <= sample["all_rate"] <= 1

    cache_action = _sample(result, "01:53")
    assert cache_action["old_rate"] == pytest.approx(0.203)
    assert cache_action["new_rate"] == pytest.approx(0.204)
    assert cache_action["all_rate"] == pytest.approx(0.2035)
    assert cache_action["flags_before"]["stock_from_cache"] == "off"
    assert cache_action["flags_after"]["stock_from_cache"] == "on"
    assert _sample(result, "01:54")["old_rate"] == pytest.approx(0.003)
    assert _sample(result, "01:54")["new_rate"] == pytest.approx(0.004)

    checkout_action = _sample(result, "03:13")
    assert checkout_action["old_rate"] == pytest.approx(0.003)
    assert checkout_action["new_rate"] == pytest.approx(0.079)
    assert checkout_action["flags_before"]["new_checkout"] == "on"
    assert checkout_action["flags_after"]["new_checkout"] == "off"
    assert _sample(result, "03:14")["new_rate"] == 0.0
    assert _sample(result, "03:14")["all_rate"] == pytest.approx(0.003)


def test_expiry_does_not_revert_night_changes_and_morning_keeps_and_undoes():
    result = browser_demo.replay()
    assert result["expiry"]["expired"] is True
    assert result["expiry"]["time"] == "07:00"
    assert result["expiry"]["no_automatic_revert"] is True
    assert len(_events(result, "expired")) == 1
    assert _sample(result, "07:00")["flags_after"] == result["flags"]["after_night"]

    morning = result["morning"]
    assert morning["time"] == "07:42" and morning["status"] == "merged"
    assert datetime.fromisoformat(morning["at"]).tzinfo is not None
    assert len(morning["kept"]) == len(morning["undone"]) == 1
    assert morning["kept"][0]["action"]["flag"] == "new_checkout"
    assert morning["kept"][0]["action"]["to"] == "off"
    assert morning["kept"][0]["until"]
    assert morning["undone"][0]["action"]["flag"] == "stock_from_cache"
    assert morning["undone"][0]["action"]["to"] == "off"
    assert morning["undone"][0]["why"]
    assert morning["by_hand"] == []
    assert any("KEEP new_checkout off" in line for line in morning["lines"])
    assert any("UNDO stock_from_cache off" in line for line in morning["lines"])


def test_declining_the_suggestion_never_changes_the_cache():
    result = browser_demo.replay(signed=True, approved=False)
    assert result["counts"]["pages"] == 1
    assert result["counts"]["automatic_incidents_handled"] == 1
    assert result["counts"]["approved_actions"] == 0
    assert result["messages"][0]["approval"] == "declined"
    assert _events(result, "approved") == []
    assert len(_events(result, "acted")) == 1
    assert all(sample["flags_before"]["stock_from_cache"] == "off"
               and sample["flags_after"]["stock_from_cache"] == "off" for sample in result["metrics"])
    assert result["flags"]["after_night"] == result["flags"]["after_morning"] == {
        "new_checkout": "off", "stock_from_cache": "off",
    }
    assert len(result["morning"]["kept"]) == 1
    assert result["morning"]["undone"] == []
    assert not any("UNDO" in line for line in result["morning"]["lines"])


@pytest.mark.parametrize("approved", [False, True])
def test_unsigned_orders_page_both_incidents_without_asking_or_changing_flags(approved):
    result = browser_demo.replay(signed=False, approved=approved)
    assert result["signature"]["signed"] is False
    assert result["counts"] == {
        "pages": 2, "automatic_incidents_handled": 0, "approved_actions": 0,
        "incidents": 2, "model_requests": 0,
    }
    assert _events(result, "asked") == _events(result, "acted") == _events(result, "approved") == []
    assert len(result["messages"]) == 2
    assert all(message["suggestion"] is None and message["approval"] == "unavailable"
               for message in result["messages"])
    assert all(flags == INITIAL_FLAGS for flags in result["flags"].values())
    assert all(sample["flags_before"] == sample["flags_after"] == INITIAL_FLAGS
               for sample in result["metrics"])
    assert result["morning"]["status"] == "not_needed"
    assert result["morning"]["kept"] == result["morning"]["undone"] == result["morning"]["by_hand"] == []
    assert result["morning"]["lines"] == []


@pytest.mark.parametrize("option", ["signed", "approved"])
@pytest.mark.parametrize("value", [None, 0, 1, "false", "true", [], {}])
def test_replay_choices_must_be_actual_booleans(option, value):
    with pytest.raises((TypeError, ValueError)):
        browser_demo.replay(**{option: value})


def test_replay_options_are_keyword_only():
    with pytest.raises(TypeError):
        browser_demo.replay(False, True)


def test_replays_are_deterministic_and_return_independent_sessions():
    baseline = browser_demo.replay(signed=True, approved=True)
    expected = copy.deepcopy(baseline)
    browser_demo.replay(signed=False, approved=False)
    browser_demo.replay(signed=True, approved=False)
    baseline["flags"]["after_night"]["new_checkout"] = "on"
    baseline["timeline"].clear()
    baseline["metrics"][0]["flags_before"]["stock_from_cache"] = "on"
    baseline["messages"][0]["lines"].clear()
    assert browser_demo.replay(signed=True, approved=True) == expected


def test_existing_demo_run_is_compatible_and_samples_match_the_browser():
    ports, night = demo_night.run(DEMO)
    assert ports.samples == []
    assert len(night.ledger.of("acted")) == 1
    sampled, sampled_night = demo_night.run(DEMO, signed=True, approved=True, collect_samples=True)
    assert sampled.samples == browser_demo.replay()["metrics"]
    assert sampled_night.ledger.events == night.ledger.events
    assert sampled.log == ports.log


def test_demo_refuses_an_oversized_scenario_before_entering_the_watch_loop(monkeypatch):
    assert isinstance(demo_night.MAX_DEMO_STEPS, int)
    assert 0 < demo_night.MAX_DEMO_STEPS <= 1000
    original_load = demo_night.load_yaml

    def oversized_scenario(path):
        data = original_load(path)
        if Path(path).name == "scenario.yml":
            data = copy.deepcopy(data)
            data["end"] = "2036-10-21T07:05"
        return data

    def must_not_tick(*args, **kwargs):
        pytest.fail("An oversized replay must be rejected before its first watch tick.")

    monkeypatch.setattr(demo_night, "load_yaml", oversized_scenario)
    monkeypatch.setattr(demo_night.Watch, "tick", must_not_tick)
    with pytest.raises(ValueError, match=r"(?i)(limit|steps|bounded|minutes)"):
        demo_night.run(DEMO)


def test_demo_stops_before_a_watch_tick_when_its_time_budget_expires(monkeypatch):
    assert 0 < demo_night.MAX_DEMO_SECONDS <= 60
    times = iter([0.0, demo_night.MAX_DEMO_SECONDS + 1.0])

    def must_not_tick(*args, **kwargs):
        pytest.fail("An expired time budget must prevent the next watch tick.")

    monkeypatch.setattr(demo_night, "monotonic", lambda: next(times))
    monkeypatch.setattr(demo_night.Watch, "tick", must_not_tick)
    with pytest.raises(TimeoutError, match=r"(?i)(seconds|time|budget)"):
        demo_night.run(DEMO)


@pytest.mark.parametrize("signed,approved", [(True, True), (True, False), (False, True), (False, False)])
def test_browser_replay_needs_no_network_credentials_or_filesystem_writes(monkeypatch, signed, approved):
    def prohibited(*args, **kwargs):
        pytest.fail("The bundled browser replay must not use external access or write files.")

    original_open = builtins.open
    original_io_open = io.open

    def read_only_open(opener):
        def open_file(file, mode="r", *args, **kwargs):
            if any(character in mode for character in "wax+"):
                prohibited()
            return opener(file, mode, *args, **kwargs)
        return open_file

    class NoCredentialEnvironment(dict):
        def __getitem__(self, key):
            prohibited()

        def get(self, key, default=None):
            prohibited()

    # Modules are already imported. Within the replay even environment reads are unnecessary.
    with monkeypatch.context() as access:
        access.setattr(builtins, "open", read_only_open(original_open))
        access.setattr(io, "open", read_only_open(original_io_open))
        access.setattr(Path, "write_text", prohibited)
        access.setattr(Path, "write_bytes", prohibited)
        access.setattr(os, "getenv", prohibited)
        access.setattr(os, "environ", NoCredentialEnvironment())
        access.setattr(socket, "create_connection", prohibited)
        access.setattr(socket, "getaddrinfo", prohibited)
        access.setattr(socket.socket, "connect", prohibited)
        access.setattr(socket.socket, "connect_ex", prohibited)
        result = browser_demo.replay(signed=signed, approved=approved)
    assert result["counts"]["automatic_incidents_handled"] == int(signed)
