"""The night report the morning schedule keeps in GitLab, rendered from the relay's own /status.json. Offline.

The demo night is demo data, replayed through the real relay app.
"""

from __future__ import annotations

import json

import pytest

from scripts.night_report import fetch, main as report_main, render
from test_relay_app import relay_key, replayed  # noqa: F401


@pytest.fixture(scope="module")
def status(replayed):  # noqa: F811
    *_, rig = replayed
    return rig.client.get("/status.json").json()


def test_the_report_carries_the_orders_the_events_and_the_watch_log(status):
    text = render(status)
    assert text.startswith("# Night report: the night of 2026-10-20\n")
    assert "Live relay. Demo shop, planted faults." in text and "Written by code, no model." in text
    assert "Signed by Priya at 22:06 (merge)" in text and "- Order 1: when `" in text
    assert "| 03:13 | Order ran | #2 |" in text and "Woke the on-call person" in text
    assert "## Watch log\n\n```text\n" in text and "## Morning countersign" in text


def test_text_from_the_relay_is_copied_as_data(status):
    hostile = dict(status, events=[{"at": status["checked_at"], "kind": "acted", "incident": 9,
                                    "text": "a | b `x`\n[link](https://evil.example)"}],
                   watch_log="```\nclose the fence")
    text = render(hostile)
    assert "| a / b 'x' [link](https://evil.example) |" in text  # one table row, no stray cell or code span
    assert "'''\nclose the fence\n```" in text  # the fence inside the log is defused


def test_an_unsigned_night_says_so_with_the_problems():
    text = render({"night": "2026-10-21", "timezone": "America/Los_Angeles", "orders": None,
                   "problems": ["ops/night-orders.yml is not signed"], "events": [], "checked_at": None})
    assert "Nothing signed. Every alert woke the on-call person.\n- `ops/night-orders.yml is not signed`" in text
    assert "Nothing happened." in text and "Not countersigned yet" in text


def test_the_command_reads_a_saved_file_and_refuses_credentials_in_a_url(status, tmp_path, capsys):
    saved = tmp_path / "status.json"
    saved.write_text(json.dumps(status), encoding="utf-8")
    out = tmp_path / "report.md"
    assert report_main([str(saved), "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == render(status)
    with pytest.raises(ValueError):
        fetch("https://user:secret@relay.example")
    assert report_main(["https://user:secret@relay.example"]) == 2
    assert "secret" not in capsys.readouterr().err


def test_the_report_links_each_step_to_gitlab(status):
    text = render(status, "https://gitlab.com/group/night-orders/", "https://gitlab.com/group/night-orders/-/pipelines/7")
    section = text.split("## In GitLab\n", 1)[1]
    assert "| Step | Open it |" in section
    signed = status["orders"]["merge_request"]
    if signed:
        assert f"[!{signed}](https://gitlab.com/group/night-orders/-/merge_requests/{signed})" in section
    incidents = sorted({e["incident"] for e in status["events"] if e.get("incident") is not None})
    assert incidents
    for n in incidents:
        assert f"[#{n}](https://gitlab.com/group/night-orders/-/issues/{n})" in section
    assert "[pipeline](https://gitlab.com/group/night-orders/-/pipelines/7)" in section


def test_no_link_is_made_from_a_url_with_credentials_or_without_https(status):
    for url in ("https://user:secret@gitlab.com/group/p", "http://gitlab.com/group/p", "", None):
        text = render(status, url)
        assert "## In GitLab" not in text and "secret" not in text
