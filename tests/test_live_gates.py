"""The live gates page claims only what evidence shows: day-one results, the relay's own status, and links a
person confirmed. Offline."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from scripts.live_gates import from_day_one, from_done, from_relay, main, render
from test_relay_app import relay_key, replayed  # noqa: F401

AT = datetime(2026, 10, 18, 14, 0, tzinfo=timezone.utc)


def test_nothing_is_claimed_without_evidence():
    gates = from_day_one(None) + from_relay(None, None, None) + from_done({})
    text = render(gates, AT)
    assert "**0 of 13 passed.**" in text and "| passed |" not in text


def test_day_one_results_become_gates_with_their_reason():
    data = {"at": "2026-10-18T13:55:00+00:00", "results": [
        {"step": "whoami", "status": "PASS", "lines": ["user alex, Maintainer"]},
        {"step": "flow", "status": "FAIL", "reason": "HTTP 403 | not allowed"},
        {"step": "catalog", "status": "SKIP", "reason": "no consumer id"}]}
    gates = {g.name: g for g in from_day_one(data)}
    assert (gates["whoami"].state, gates["whoami"].evidence) == ("passed", "day_one.py at 2026-10-18T13:55: user alex, Maintainer")
    assert (gates["flow"].state, gates["flow"].evidence) == ("failed", "HTTP 403 | not allowed")
    assert (gates["catalog"].state, gates["catalog"].evidence) == ("pending", "skipped: no consumer id")
    assert "| failed | HTTP 403 / not allowed |" in render(list(gates.values()), AT)  # no stray table cell


def test_a_night_through_the_relay_passes_the_night_gate_and_links_the_status(replayed):  # noqa: F811
    *_, rig = replayed
    status = rig.client.get("/status.json").json()
    gates = {g.name: g for g in from_relay("https://relay.example", status, True)}
    assert gates["relay"].state == "passed" and gates["night"].state == "passed"
    assert gates["night"].evidence == "night of 2026-10-20, https://relay.example/status.json"
    assert gates["morning"].state == "pending"  # the demo replay through the relay has no countersign


def test_the_command_takes_only_https_links_and_writes_the_page(tmp_path, capsys):
    out = tmp_path / "LIVE_GATES.md"
    assert main(["--done", "video=http://youtu.be/x"]) == 2
    assert main(["--relay", "https://user:pw@relay.example"]) == 2
    assert "pw" not in capsys.readouterr().err
    saved = tmp_path / "day-one.json"
    saved.write_text(json.dumps({"at": "2026-10-18T13:55", "results": [{"step": "publish", "status": "PASS"}]}))
    assert main(["--day-one", str(saved), "--done", "video=https://youtu.be/abc", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "**2 of 13 passed.**" in text and "[https://youtu.be/abc](https://youtu.be/abc)" in text
