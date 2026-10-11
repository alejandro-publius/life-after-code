"""The public status page at / and /status.json: the demo's look, the night's facts, links into GitLab. Offline.

The demo night is demo data; every URL and number here is test data.
"""

from __future__ import annotations

from datetime import timedelta, timezone

from nightorders import status_page
from nightorders.signals import Metrics
from test_relay_app import (ONCALL, QuietSources, Rig, TARGETS, demo_signature, local, main, relay_key,  # noqa: F401
                            replayed)

PROJECT = "https://gitlab.example/hackathon/night-orders"


def doc_with(**status) -> dict:
    base = {"checked_at": local("03:30").isoformat(), "timezone": "America/Los_Angeles", "orders": None,
            "problems": []}
    base.update(status)
    return {"version": 1, "night": "2026-10-20", "watch": {"incidents": [], "ledger": []}, "ports": {},
            "relay": {"status": base}}


def test_before_any_tick_the_page_points_at_the_demo_and_has_no_script(tmp_path):
    rig = Rig(tmp_path, QuietSources())
    page = rig.client.get("/")
    text = page.text
    assert "Nothing signed yet. Here is the demo." in text and 'href="/demo"' in text
    assert "<script" not in text and page.headers["content-security-policy"].startswith("default-src 'none'; style-src 'self'")
    assert "(link pending)" in text  # no project address yet, so no link pretends to exist


def test_links_come_from_the_project_address_and_numbers_only():
    doc = doc_with(project_url=PROJECT, watch_issue=12, orders={
        "night": "2026-10-20", "ends_at": local("07:00").isoformat(), "signed_by": "Priya",
        "signed_at": local("22:06").isoformat(), "method": "merge", "merge_request": 36,
        "items": [{"id": 1, "when": "x above 5%", "do": "new_checkout off in production", "because": "MR !31"}]})
    doc["watch"]["ledger"] = [
        {"at": local("03:12").isoformat(), "kind": "alert", "text": 'Night watch: <a href="https://evil.example">x</a>',
         "incident": 7, "order": None, "data": {}},
        {"at": local("03:13").isoformat(), "kind": "acted", "text": "Order 1 carried out", "incident": 7, "order": 1,
         "data": {}},
        {"at": local("03:14").isoformat(), "kind": "woke", "text": "Woke Priya", "incident": 8, "order": None, "data": {}},
    ]
    doc["ports"]["links"] = {"7": f"{PROJECT}/-/issues/7", "8": "javascript:alert(1)"}
    text = status_page.render(doc, local("03:30"))
    assert f'href="{PROJECT}/-/issues/12"' in text and f'href="{PROJECT}/-/merge_requests/36"' in text
    assert f'href="{PROJECT}/-/issues/7"' in text
    assert f'href="{PROJECT}/-/issues/8"' in text and "javascript:" not in text  # a stored link that is not https is ignored
    assert "evil.example\">" not in text and "&lt;a href=&quot;https://evil.example&quot;&gt;" in text
    assert "Signed until 07:00. Code is keeping watch." in text and "Ends in 3 h 30 min." in text
    for path in ("/-/automate/agent-sessions", "/-/pipelines", "/-/feature_flags", "/-/incidents"):
        assert f'href="{PROJECT}{path}"' in text


def test_a_pending_suggestion_says_until_when_it_waits_for_a_thumbs_up():
    doc = doc_with()
    doc["watch"]["incidents"] = [{"number": 1, "paged_at": local("01:52").isoformat(), "closed": False,
                                  "suggest": {"kind": "flag_set", "flag": "stock_from_cache"}}]
    text = status_page.render(doc, local("02:00"))
    assert "Incident #1: one suggestion is awaiting a thumbs-up from the on-call person until 02:52." in text


def test_the_chart_draws_zero_one_and_sixty_minutes():
    tz = ONCALL.timezone
    assert "No shop numbers yet." in status_page.chart([], [], tz)
    one = [{"at": local("03:00").astimezone(timezone.utc).isoformat(), "old": 0.003, "new": 0.079, "all": 0.04,
            "checkouts": 60}]
    svg = status_page.chart(one, [], tz)
    assert svg.count('class="chart-line') == 2 and "7.9%" in svg
    metrics = Metrics()
    start = local("02:30")
    for i in range(70):
        at = start + timedelta(minutes=i)
        metrics.put("checkout_error_rate.old", at, 0.003)
        metrics.put("checkout_error_rate.new", at, 0.079 if i > 40 else 0.004)
        metrics.put("checkouts.all", at, 60)
    samples = status_page.samples_of(metrics, local("03:40"))
    assert len(samples) == 60 and samples[-1]["at"] == local("03:39").astimezone(timezone.utc).isoformat(timespec="minutes")
    events = [{"at": local("03:13").isoformat(), "kind": "acted"}, {"at": local("03:23").isoformat(), "kind": "recovered"},
              {"at": local("01:00").isoformat(), "kind": "woke"}]  # outside the hour: not drawn
    svg = status_page.chart(samples, events, tz)
    assert svg.count('class="marker-badge"') == 2 and "03:13 order ran" in svg and "03:23 re-check passed" in svg


def test_status_json_serves_the_facts_and_never_a_setting(tmp_path, relay_key, monkeypatch):
    monkeypatch.setenv("GITLAB_TOKEN", "fake-gitlab-token-value")
    monkeypatch.setenv("NTFY_URL", "https://ntfy.example/secret-topic-value")
    rig = Rig(tmp_path, QuietSources())
    assert rig.client.get("/status.json").json()["available"] is True
    rig.tick()
    answer = rig.client.get("/status.json")
    body = answer.json()
    assert answer.headers["cache-control"] == "no-store"
    assert body["mode"] == "flow" and body["label"] == "Live relay. Demo shop, planted faults."
    assert "fake-gitlab-token-value" not in answer.text and "secret-topic-value" not in answer.text


def test_the_demo_night_through_the_relay_fills_the_page(replayed):
    *_, rig = replayed
    text = rig.client.get("/").text
    assert "Tonight so far" in text and "Order ran" in text and "Woke her" in text
    body = rig.client.get("/status.json").json()
    kinds = [event["kind"] for event in body["events"]]
    assert kinds.count("alert") == 2 and "acted" in kinds and "expired" in kinds
    assert body["orders"]["signed_by"] == "Priya"
