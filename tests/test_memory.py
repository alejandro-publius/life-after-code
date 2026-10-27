"""Incident memory keeps observations across nights without inventing a recovery."""

from datetime import datetime, timedelta, timezone

from nightorders import memory, state
from nightorders.daysheet import render
from nightorders.ledger import Event
from nightorders.status_page import public, render as status_html

START = datetime(2026, 10, 21, 8, tzinfo=timezone.utc)
ACTION = {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}


def event(kind, minute=0, incident=7, **data):
    return Event(START + timedelta(minutes=minute), kind, f"Observed {kind}", incident,
                 order=1 if kind in ("acted", "recovered") else None, data=data)


def test_recovery_requires_an_action_and_its_observed_recheck():
    relay = {}
    memory.remember(relay, "2026-10-20", [event("alert"), event("acted", 1, action=ACTION)])
    assert memory.view(relay)["episodes"][0]["outcome"] == "open"
    memory.remember(relay, "2026-10-20", [event("recovered", 11)])
    episode = memory.view(relay)["episodes"][0]
    assert episode["outcome"] == "recovered"
    assert episode["action"] == ACTION
    assert "new signature" in episode["lesson"]


def test_approval_does_not_masquerade_as_a_verified_recovery():
    relay = {}
    data = memory.remember(relay, "2026-10-20",
                           [event("alert"), event("woke", 1), event("approved", 2, action=ACTION)])
    assert data["counts"] == {"human_action": 1}
    assert "does not independently verify" in data["episodes"][0]["lesson"]


def test_failed_action_and_action_followed_by_page_have_distinct_outcomes():
    relay = {}
    memory.remember(relay, "2026-10-20",
                    [event("acted", 1, action=ACTION), event("woke", 11),
                     event("failed", 1, incident=8, action=ACTION), event("woke", 2, incident=8)])
    assert memory.view(relay)["counts"] == {"needs_review": 1, "action_failed": 1}
    memory.remember(relay, "2026-10-20", [event("stood_down", 12, incident=8)])
    uncertain = next(item for item in memory.view(relay)["episodes"] if item["incident"] == 8)
    assert uncertain["outcome"] == "action_failed"  # the failed call might have changed the target


def test_repeated_ticks_are_idempotent_and_views_cannot_edit_saved_memory(make_night):
    relay = {}
    events = [event("alert"), event("acted", 1, action=ACTION), event("recovered", 11)]
    memory.remember(relay, "2026-10-20", events, make_night().orders)
    first = memory.view(relay)
    memory.remember(relay, "2026-10-20", events)  # temporary loss of repository access
    assert memory.view(relay) == first
    first["episodes"][0]["steps"].clear()
    assert len(memory.view(relay)["episodes"][0]["steps"]) == 3


def test_memory_survives_noon_and_a_restarted_state_store(tmp_path, oncall, make_night):
    doc = state.new_document("2026-10-20")
    doc["watch"]["ledger"] = [state.dump_event(e) for e in
                              [event("alert"), event("acted", 1, action=ACTION), event("recovered", 11)]]
    rolled = state.next_night(doc, "2026-10-21", make_night().orders, oncall,
                             START + timedelta(hours=12))
    store = state.FileStore(tmp_path / "state.json")
    store.save(rolled, None)
    loaded, _ = store.load()
    assert loaded["watch"]["ledger"] == []
    assert memory.view(loaded["relay"])["episodes"][0]["outcome"] == "recovered"
    memory.remember(loaded["relay"], "2026-10-21", [event("woke", 1440)])
    assert len(memory.view(loaded["relay"])["episodes"]) == 1
    assert memory.view(loaded["relay"])["episodes"][0]["night"] == "2026-10-20"


def test_long_incidents_keep_decisive_events_and_bounded_storage():
    relay = {}
    events = [event("alert"), event("acted", 1, action=ACTION), event("recovered", 11)]
    events += [event("refused", minute) for minute in range(12, 100)]
    data = memory.remember(relay, "2026-10-20", events)
    episode = data["episodes"][0]
    assert len(episode["steps"]) == memory.MAX_STEPS
    assert episode["truncated"] and episode["outcome"] == "recovered"
    memory.remember(relay, "2026-10-21", [event("refused", 1440)])
    assert memory.view(relay)["episodes"][0]["outcome"] == "recovered"
    memory.remember(relay, "2026-10-21", [event("alert", i, incident=i + 100) for i in range(80)])
    assert len(memory.view(relay)["episodes"]) == memory.MAX_INCIDENTS


def test_next_dusk_gets_earlier_outcomes_with_failures_first():
    relay = {}
    memory.remember(relay, "2026-10-20", [event("acted", 1), event("recovered", 11),
                                        event("failed", 2, incident=8, action=ACTION)])
    memory.remember(relay, "2026-10-21", [event("woke", 1440, incident=9)])
    brief = memory.briefing(relay, before_night="2026-10-21")
    assert [entry["incident"] for entry in brief] == [8, 7]
    assert brief[0]["action"] == ACTION
    sheet = {"date": "2026-10-21", "timezone": "UTC", "_label": "Demo", "merged_today": [],
             "deployments": [], "flags": [], "incident_memory": brief}
    text = render(sheet)
    assert "What earlier nights taught us" in text
    assert "Historical observations, never permission" in text
    assert "Incident #8" in text


def test_history_orders_real_instants_across_a_timezone_offset_change():
    relay = {}
    later = Event(datetime.fromisoformat("2026-11-01T01:10:00-08:00"), "recovered", "Observed recovery", 7, order=1)
    earlier = Event(datetime.fromisoformat("2026-11-01T01:55:00-07:00"), "acted", "Observed action", 7, order=1)
    data = memory.remember(relay, "2026-10-31", [later, earlier])
    assert data["episodes"][0]["outcome"] == "recovered"


def test_public_history_escapes_text_and_download_retains_evidence():
    relay = {}
    memory.remember(relay, "2026-10-20", [Event(START, "alert", "<script>alert(1)</script>", 7)])
    doc = {"relay": relay}
    data = public(doc, START)["incident_memory"]
    assert "Incident #7" in memory.handoff(data, "Demo data")
    page = status_html(doc, START)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
    assert "/handoff.md" in page


def test_live_handoff_uses_persisted_observations_and_is_downloadable(tmp_path):
    from fastapi.testclient import TestClient
    from test_relay_app import main

    store = state.FileStore(tmp_path / "memory-state.json")
    doc = state.new_document("2026-10-20")
    memory.remember(doc["relay"], "2026-10-20",
                    [event("acted", 1, action=ACTION), event("recovered", 11)])
    store.save(doc, None)
    client = TestClient(main.create_app(make_store=lambda _: store, clock=lambda: START))
    response = client.get("/handoff.md")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert "Recovery observed" in response.text
    assert "Observed recovered" in response.text
    assert "new human signature" in response.text


def test_handoff_returns_unavailable_when_state_cannot_be_read():
    from fastapi.testclient import TestClient
    from test_relay_app import main

    def broken(_):
        raise RuntimeError("state read failed")

    response = TestClient(main.create_app(make_store=broken)).get("/handoff.md")
    assert response.status_code == 503
    assert "unavailable" in response.text
