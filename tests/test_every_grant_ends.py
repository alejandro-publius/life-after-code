"""Every grant ends: nothing changed overnight is forgotten, the morning is announced quietly, and a countersign
can be signed even when no model proposed one. Every name and time here is test data; the night is the demo's.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest
import yaml

from conftest import REPO, OPS
from nightorders.countersign import parse_state
from nightorders.morning import StateFile, countersign_request, push_lines, step
from nightorders.orders import load_context
from test_morning import FakePorts, local, night, signed  # noqa: F401
from test_relay_ports import API, Server, body, ports_for


class MorningPorts(FakePorts):
    def __init__(self, flow_ready=False, open_request=None):
        super().__init__()
        self.pushes, self.opened = [], []
        self.flow_ready, self.open_request = flow_ready, open_request

    def morning_push(self, lines, at):
        self.pushes.append(lines)

    def dawn_flow_ready(self):
        return self.flow_ready

    def countersign_request_open(self):
        return self.open_request

    def open_countersign_request(self, night, state_text, title, description):
        self.opened.append((night, state_text, title, description))
        return 40 + len(self.opened)


def test_a_night_never_countersigned_is_carried_into_the_next_one_with_its_first_snapshot(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=True)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    first = {tuple(sorted(item["action"].items())): item["before"] for item in relay_doc["dawn"]["loose_ends"]}
    # The next night: the same demo ledger, as if the same two changes happened again on 21 Oct.
    import dataclasses
    from datetime import date
    later = dataclasses.replace(night, orders=dataclasses.replace(night.orders, night=date(2026, 10, 21)))
    for event in later.ledger.events:
        if event.data.get("before"):
            event.data["before"] = {**event.data["before"], "value": "something else"}
    done = step(relay_doc, later, True, None, ports, local(night, "2026-10-22T07:00"), 7)
    record = relay_doc["dawn"]
    assert record["nights"] == ["2026-10-20", "2026-10-21"] and record["night"] == "2026-10-21"
    assert done[0].endswith("including 1 earlier night(s) never countersigned")
    assert {tuple(sorted(item["action"].items())): item["before"] for item in record["loose_ends"]} == first
    assert "Before the night: off." in ports.flows[-1] and 'Write night: "2026-10-21"' in ports.flows[-1]


def test_a_countersigned_night_is_not_carried(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=True)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    keep = {"night": "2026-10-20", "flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                                              "until": "the fix ships"}]}
    step(relay_doc, night, True, StateFile(keep, signed(night, "2026-10-21T07:42")), ports,
         local(night, "2026-10-21T07:43"), 7)
    assert relay_doc["dawn"]["countersign"]["problems"] == []
    import dataclasses
    from datetime import date
    later = dataclasses.replace(night, orders=dataclasses.replace(night.orders, night=date(2026, 10, 21)))
    step(relay_doc, later, True, None, ports, local(night, "2026-10-22T07:00"), 7)
    assert relay_doc["dawn"]["nights"] == ["2026-10-21"]


def test_a_state_file_for_another_night_is_refused_and_one_for_this_night_restores_everything(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=True)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    old = StateFile({"night": "2026-10-19", "flags": []}, signed(night, "2026-10-21T07:42"))
    step(relay_doc, night, True, old, ports, local(night, "2026-10-21T07:43"), 7)
    assert relay_doc["dawn"]["refused"]["problems"][0] == ("ops/state.yml is the countersign for the night of "
                                                           "2026-10-19, not of 2026-10-20.")
    assert ports.restored == []
    import dataclasses
    empty = StateFile({"night": "2026-10-20", "flags": [], "services": []},
                      dataclasses.replace(signed(night, "2026-10-21T07:50"), commit="d2"))
    step(relay_doc, night, True, empty, ports, local(night, "2026-10-21T07:51"), 7)
    assert sorted(name for name, _before in ports.restored) == ["new_checkout off in production",
                                                               "stock_from_cache on in production"]


def test_one_quiet_push_a_morning_says_what_the_night_did(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=True)
    for minute in ("07:00", "07:01", "07:02"):
        step(relay_doc, night, True, None, ports, local(night, f"2026-10-21T{minute}"), 7)
    assert ports.pushes == [("Woken 1 time. Handled while you slept: 1.",
                             "2 changes to keep or restore. The countersign merge request is on the watch issue.")]
    assert push_lines(night, 0)[1] == "Nothing changed overnight, so nothing needs a countersign."


def test_without_a_dawn_flow_code_opens_the_countersign_request_at_once(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=False)
    done = step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    assert "countersign merge request !41 opened by code" in done
    [(night_date, state_text, title, description)] = ports.opened
    assert night_date == "2026-10-20" and title == "Countersign 2026-10-20 (written by code)"
    parsed = yaml.safe_load(state_text)
    assert parsed == {"night": "2026-10-20", "flags": [], "services": []}
    _oncall, targets = load_context(OPS)
    assert parse_state(parsed, targets) == []  # merged as it is, it keeps nothing
    assert "- stock_from_cache on in production (approved by thumbs-up, 01:53). Before the night: off." in description
    assert "Written by code: no model proposed anything this morning." in description
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:30"), 7)
    assert len(ports.opened) == 1  # once


def test_with_a_dawn_flow_code_waits_twenty_minutes_and_steps_back_if_the_flow_opened_one(night):
    relay_doc, ports = {}, MorningPorts(flow_ready=True)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:19"), 7)
    assert ports.opened == []
    ports.open_request = 52  # the dawn flow's merge request
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:20"), 7)
    assert ports.opened == [] and relay_doc["dawn"]["code_request"] == -1
    silent = {}
    quiet_ports = MorningPorts(flow_ready=True)
    step(silent, night, True, None, quiet_ports, local(night, "2026-10-21T07:00"), 7)
    step(silent, night, True, None, quiet_ports, local(night, "2026-10-21T07:20"), 7)
    assert len(quiet_ports.opened) == 1


# The live ports, against a fake GitLab and ntfy.

PROJECT = {"id": 123, "default_branch": "main", "web_url": "https://gitlab.example/g/night-orders"}


def test_the_live_morning_push_is_quiet_and_opens_the_watch_issue():
    from urllib.parse import urlsplit
    from test_relay_ports import TOPIC_URL
    server = Server({("GET", API): PROJECT, ("POST", urlsplit(TOPIC_URL).path): (200, {"id": "x"})})
    ports = ports_for(server)
    ports.watch_issue = 12
    ports.morning_push(("Woken 0 times.", "Nothing changed."), datetime(2026, 10, 21, 14, 0, tzinfo=timezone.utc))
    [sent] = [r for r in server.requests if r.method == "POST"]
    assert sent.headers["Priority"] == "default" and sent.headers["Click"] == "https://gitlab.example/g/night-orders/-/issues/12"
    assert sent.headers["Title"] == "Night Orders: good morning"


def test_the_live_countersign_request_takes_a_free_branch_name_and_updates_the_file():
    branches = []

    def commit(request):
        data = body(request)
        branches.append(data["branch"])
        return (400, {"message": "A branch called this already exists"}) if len(branches) == 1 else (201, {"id": "c1"})

    server = Server({("GET", API): PROJECT, ("GET", f"{API}/repository/files/ops%2Fstate.yml/raw"): (200, "flags: []\n"),
                     ("GET", f"{API}/repository/files/ops/state.yml/raw"): (200, "flags: []\n"),
                     ("POST", f"{API}/repository/commits"): commit,
                     ("POST", f"{API}/merge_requests"): (201, {"iid": 44})})
    ports = ports_for(server)
    assert ports.open_countersign_request("2026-10-20", "night: \"2026-10-20\"\n", "Countersign 2026-10-20", "d") == 44
    assert branches == ["countersign/2026-10-20-code", "countersign/2026-10-20-code-2"]
    commits = server.sent("POST", f"{API}/repository/commits")
    assert body(commits[-1])["actions"][0]["action"] == "update" and body(commits[-1])["start_branch"] == "main"
    [request] = server.sent("POST", f"{API}/merge_requests")
    assert body(request)["source_branch"] == "countersign/2026-10-20-code-2" and body(request)["target_branch"] == "main"


def test_the_live_check_finds_an_open_countersign_request_by_its_file():
    server = Server({("GET", API): PROJECT,
                     ("GET", f"{API}/merge_requests"): [{"iid": 50}, {"iid": 52}],
                     ("GET", f"{API}/merge_requests/50/diffs"): [{"new_path": "README.md", "old_path": "README.md"}],
                     ("GET", f"{API}/merge_requests/52/diffs"): [{"new_path": "ops/state.yml", "old_path": "ops/state.yml"}]})
    assert ports_for(server).countersign_request_open() == 52
