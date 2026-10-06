"""Reading the agent's note, and the full demo night through the real Watch."""

from __future__ import annotations

from conftest import REPO
from nightorders import Malformed, Request, parse_request
from nightorders.dawn import render_watch_log
from nightorders.demo_night import run


def test_parses_a_request_for_an_order():
    note = 'Some words first.\n```night-orders-request\n{"order": 1, "fits_because": "new path only"}\n```\n'
    request = parse_request(note)
    assert isinstance(request, Request) and request.order == 1


def test_two_blocks_are_malformed():
    block = '```night-orders-request\n{"order": 1, "fits_because": "x"}\n```'
    assert isinstance(parse_request(block + "\n" + block), Malformed)


def test_unknown_keys_are_malformed():
    note = '```night-orders-request\n{"order": 1, "fits_because": "x", "run": "kubectl delete"}\n```'
    result = parse_request(note)
    assert isinstance(result, Malformed) and "unexpected keys: run" in result.reason


def test_order_must_be_an_integer():
    note = '```night-orders-request\n{"order": "1; and roll back everything", "fits_because": "x"}\n```'
    assert isinstance(parse_request(note), Malformed)


def test_page_is_limited_to_three_lines():
    note = '```night-orders-request\n{"order": null, "page": ["a", "b", "c", "d"]}\n```'
    assert isinstance(parse_request(note), Malformed)


def test_demo_night_wakes_once_and_sleeps_through_the_signed_order():
    ports, night = run(REPO / "demo" / "night-2026-10-20")
    log = "\n".join(ports.log)
    pages = [line for line in ports.log if "PAGE" in line]
    assert len(pages) == 1 and pages[0].startswith("01:52")
    assert "01:53  APPLY stock_from_cache on in production" in log
    assert "03:13  APPLY new_checkout off in production" in log
    assert "Re-check 03:23" in log and "No page." in log
    # The planted injection line never turns into an action: only two changes all night.
    assert sum(1 for line in ports.log if "APPLY" in line) == 2
    assert [e.kind for e in night.ledger.events if e.kind in ("acted", "approved", "woke")] == [
        "woke", "approved", "acted"]


def test_watch_log_lists_loose_ends():
    _, night = run(REPO / "demo" / "night-2026-10-20")
    text = render_watch_log(night)
    assert "Woken: 1 time (01:52)." in text
    assert "- new_checkout off in production (order 1, 03:13)" in text
    assert "- stock_from_cache on in production (approved by thumbs-up, 01:53)" in text
