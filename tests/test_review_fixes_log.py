"""Fixes from the 11 Oct review in the watch log and the model's text. Offline.

Text the model writes is one line before it reaches any record, so it cannot start a GitLab quick action in the
watch log or a note; and the watch log, the 07:00 push, the browser demo and the compare table count the same
incidents as handled while she slept.

The demo night is demo data (planted faults, simulated shop). Every other name and time here is test data.
"""

from __future__ import annotations

import json
from datetime import timedelta, timezone

from conftest import REPO, at
from nightorders import Metrics, Request, demo_night, render_request
from nightorders import browser_demo
from nightorders.compare import counts
from nightorders.dawn import render_watch_log
from nightorders.morning import push_lines
from nightorders.notes import parse_request
from nightorders.watch import Watch
from test_relay_ports import API, Server, ports_for
from test_standing_orders import bad_minutes, rules

DEMO = REPO / "demo" / "night-2026-10-20"
FLOW_ACCOUNT = "duo-watch-night-orders"  # test_relay_ports.ports_for's flow account
NEW = "checkout_error_rate.new"


def quick_actions(markdown: str) -> list[str]:
    """Lines GitLab would read as quick actions: a line starting with / outside a code block. The /timeline line
    code adds to its own notes is the one expected."""
    found, fenced = [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.lstrip().startswith("/") and not line.startswith("/timeline "):
            found.append(line)
    return found


# B2: the model's text is one line.

def test_the_reason_and_every_page_line_are_one_line_and_the_reason_is_capped():
    note = render_request(Request(order=None, fits_because=None, declined_id=1,
                                  declined_why="Not this.\n\n/close " + "x" * 400,
                                  page=("One\n\n/close", "two\t  three"), suggest=None))
    request = parse_request(note)
    assert request.declined_why is not None and len(request.declined_why) == 300
    assert request.declined_why.startswith("Not this. /close xxx")
    assert request.page == ("One /close", "two three")


def test_a_reply_with_quick_actions_cannot_start_a_line_in_any_note_or_in_the_watch_log(oncall, make_night):
    answer = render_request(Request(order=None, fits_because=None, declined_id=1,
                                    declined_why="Not the new checkout.\n\n/close\n/assign @teammate",
                                    page=("Checkout failing.\n\n/close", "Second line.\n/label ~night"), suggest=None))
    created = (at(oncall, "03:12") + timedelta(seconds=30)).astimezone(timezone.utc).isoformat()
    server = Server({
        ("POST", f"{API}/issues"): (201, {"iid": 7, "web_url": "https://gitlab.example/g/p/-/issues/7"}),
        ("POST", "/api/v4/ai/duo_workflows/workflows"): (201, {"id": 1}),
        ("GET", f"{API}/issues/7/notes"): [{"id": 4, "body": answer, "author": {"username": FLOW_ACCOUNT},
                                            "created_at": created.replace("+00:00", "Z"), "system": False}],
        ("POST", f"{API}/issues/7/notes"): (201, {"id": 555}),
        ("POST", f"{API}/issues/1/notes"): (201, {"id": 556}),
        ("POST", "/test-topic-not-real"): {"id": "x"},
    })
    ports = ports_for(server)
    ports.watch_issue = 1
    night = make_night()
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 30, 0.079)
    watch.tick(metrics, at(oncall, "03:12"))
    watch.tick(metrics, at(oncall, "03:13"))
    assert [e.kind for e in night.ledger.events] == ["alert", "asked", "declined", "woke"]
    log = render_watch_log(night)
    ports.watch_note(log, at(oncall, "07:00"))
    posted = [r for r in server.requests if r.method == "POST" and r.url.path.endswith("/notes")]
    assert len(posted) == 2  # the page note on #7 and the watch log on #1
    for request in posted:
        assert quick_actions(json.loads(request.content)["body"]) == []
    assert quick_actions(log) == []
    assert "The agent declined order 1: Not the new checkout. /close /assign @teammate |" in log


def test_the_watch_log_puts_every_record_on_one_line(make_night, oncall):
    night = make_night()
    night.ledger.record(at(oncall, "03:13"), "declined", "The agent declined order 1: no.\n\n/close", incident=1)
    log = render_watch_log(night)
    assert quick_actions(log) == []
    assert "| 03:13 | The agent declined order 1: no. /close |" in log


# D2: an order that ran and then woke her was not handled while she slept.

def test_the_watch_log_says_when_an_order_ran_and_then_woke_her():
    _, standing = demo_night.run(DEMO, standing=True)
    log = render_watch_log(standing)
    assert "Handled while you slept" not in log
    assert "Acted, then woke you: incident #1 (order 1)." in log
    assert push_lines(standing, 1)[0] == "Woken 1 time. Handled while you slept: 0."
    assert counts(standing)["handled_asleep"] == 0

    _, signed = demo_night.run(DEMO)
    log = render_watch_log(signed)
    assert "Handled while you slept: incident #2 (order 1)." in log and "Acted, then woke you" not in log
    assert push_lines(signed, 2)[0] == "Woken 1 time. Handled while you slept: 1."
    assert counts(signed)["handled_asleep"] == 1


def test_the_browser_demo_counts_only_what_was_handled_while_she_slept(monkeypatch):
    real = browser_demo.run
    monkeypatch.setattr(browser_demo, "run", lambda *args, **kwargs: real(*args, standing=True, **kwargs))
    result = browser_demo.replay()
    assert result["counts"]["pages"] == 1 and result["counts"]["automatic_incidents_handled"] == 0
    [step] = [s for s in result["steps"] if s["id"] == "dawn-log"]
    assert step["text"] == "Priya was woken 1 time(s). 0 incident(s) were handled automatically."
    assert "Acted, then woke you: incident #1 (order 1)." in result["watch_log"]
