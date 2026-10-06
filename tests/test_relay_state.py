"""The relay's memory between ticks: a JSON round trip of the Watch, the noon rollover, and the two stores.

The demo night is demo data (planted faults, simulated shop). Every other value here is test data.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from conftest import REPO, at
from nightorders import demo_night
from nightorders.gitlab_ports import GoogleToken, Http
from nightorders.ledger import Ledger
from nightorders.state import (
    FileStore, GcsStore, StateConflict, StateError, capture, check, load_ledger, new_document, next_night, night_of,
    restore,
)
from nightorders.watch import Watch

DEMO = REPO / "demo" / "night-2026-10-20"


class RoundTripWatch(Watch):
    """The real Watch, which after every tick checks that a JSON round trip of its state changes nothing."""

    ticks = 0

    def tick(self, metrics, now):
        super().tick(metrics, now)
        doc = new_document("2026-10-20")
        capture(self, doc)
        again = json.loads(json.dumps(doc))  # plain JSON, nothing else
        twin = Watch(dataclasses.replace(self.night, ledger=load_ledger(again)), self.ports, self.rules)
        restore(twin, again)
        assert twin.incidents == self.incidents
        assert twin.night.ledger.events == self.night.ledger.events
        assert twin.expired == self.expired
        RoundTripWatch.ticks += 1


def test_watch_state_survives_a_json_round_trip_at_every_minute_of_the_demo_night(monkeypatch):
    monkeypatch.setattr(demo_night, "Watch", RoundTripWatch)
    RoundTripWatch.ticks = 0
    ports, night = demo_night.run(DEMO)
    assert RoundTripWatch.ticks == 546  # 22:00 to 07:05
    # The night itself is unchanged by the checks: one page, two changes.
    assert [e.kind for e in night.ledger.events if e.kind in ("acted", "approved", "woke")] == [
        "woke", "approved", "acted"]


def test_incident_fields_round_trip_while_a_suggestion_waits(monkeypatch, oncall):
    seen = {}

    class Snapshot(Watch):
        def tick(self, metrics, now):
            super().tick(metrics, now)
            if now == at(oncall, "01:52"):
                seen["doc"] = new_document("2026-10-20")
                capture(self, seen["doc"])

    monkeypatch.setattr(demo_night, "Watch", Snapshot)
    demo_night.run(DEMO)
    [incident] = seen["doc"]["watch"]["incidents"]
    assert incident["suggest"] == {"kind": "flag_set", "flag": "stock_from_cache", "environment": "production",
                                   "to": "on", "service": None, "revision": None}
    assert incident["ask"]["eligible"] == [1] and incident["paged_at"].startswith("2026-10-21T01:52")
    assert incident["keys"] == ["checkout_error_rate.new", "checkout_error_rate.old", "http_5xx_ratio"]


def test_a_night_runs_from_noon_to_noon_local_time(oncall):
    assert night_of(at(oncall, "11:59"), oncall) == "2026-10-20"  # the morning of Oct 21
    assert night_of(at(oncall, "12:00").replace(day=21), oncall) == "2026-10-21"
    assert night_of(datetime(2026, 10, 21, 10, 12, tzinfo=timezone.utc), oncall) == "2026-10-20"  # 03:12 local


def test_a_new_night_keeps_open_incidents_and_starts_an_empty_ledger(make_night, oncall):
    night = make_night()
    doc = new_document("2026-10-20")
    doc["watch"]["incidents"] = [{"number": 1, "closed": True}, {"number": 2, "closed": False}]
    doc["watch"]["ledger"] = [{"at": at(oncall, "03:12").isoformat(), "kind": "alert", "text": "x"}]
    doc["ports"] = {"page_notes": {"1": 10, "2": 20}, "links": {"2": "https://gitlab.example/i/2"}}
    doc["relay"] = {"watch_log": {"night": "2026-10-20", "text": "## Watch log"}}
    fresh = next_night(doc, "2026-10-21", night.orders, oncall, at(oncall, "12:00").replace(day=21))
    assert fresh["night"] == "2026-10-21" and fresh["watch"]["ledger"] == []
    assert fresh["watch"]["incidents"] == [{"number": 2, "closed": False}]
    assert fresh["ports"] == {"page_notes": {"2": 20}, "links": {"2": "https://gitlab.example/i/2"}}
    assert fresh["relay"]["watch_log"]["text"] == "## Watch log"
    # Last night's orders ended at 07:00, before this record began, so their expiry is not logged again.
    assert fresh["watch"]["expired"] is True and fresh["watch"]["expired_orders"] == "2026-10-20"


def test_the_expired_flag_belongs_to_one_orders_file(make_night, orders_data):
    doc = new_document("2026-10-20")
    doc["watch"].update(expired=True, expired_orders="2026-10-20")
    same = Watch(make_night(), ports=None, rules=[])
    restore(same, doc)
    assert same.expired is True
    orders_data["night"] = "2026-10-21"
    other = Watch(make_night(orders_data), ports=None, rules=[])
    restore(other, doc)
    assert other.expired is False


def test_an_unknown_state_version_is_refused():
    assert check(None) is None
    with pytest.raises(StateError, match="version 99"):
        check({"version": 99})


def test_file_store_round_trip(tmp_path):
    store = FileStore(tmp_path / "state" / "night.json")
    assert store.load() == (None, None)
    doc = new_document("2026-10-20")
    doc["relay"] = {"watch_log": {"night": "2026-10-20", "text": "Woken: 1 time (01:52)."}}
    store.save(doc)
    assert store.load() == (doc, None)


class Gcs:
    """A fake Cloud Storage JSON API and metadata server for one object."""

    def __init__(self, stored: dict | None = None, generation: str = "1700000000000001", conflict: bool = False):
        self.stored, self.generation, self.conflict, self.requests = stored, generation, conflict, []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if request.url.host == "metadata.google.internal":
            return httpx.Response(200, json={"access_token": "test-google-token", "expires_in": 3599})
        if request.method == "GET" and path == "/storage/v1/b/test-bucket/o/night-orders/state.json":
            if self.stored is None:
                return httpx.Response(404, json={"error": {"code": 404, "message": "No such object"}})
            if request.url.params.get("alt") == "media":
                return httpx.Response(200, content=json.dumps(self.stored).encode())
            return httpx.Response(200, json={"name": "night-orders/state.json", "generation": self.generation})
        if request.method == "POST" and path == "/upload/storage/v1/b/test-bucket/o":
            if self.conflict:
                return httpx.Response(412, json={"error": {"code": 412, "message": "Precondition Failed"}})
            self.stored = json.loads(request.content)
            return httpx.Response(200, json={"generation": "1700000000000002"})
        return httpx.Response(404, json={})

    def store(self) -> GcsStore:
        http = Http(httpx.Client(transport=httpx.MockTransport(self)))
        return GcsStore("test-bucket", "night-orders/state.json", http, GoogleToken(http))


def test_gcs_store_reads_and_saves_one_object_only_if_nobody_saved_meanwhile():
    empty = Gcs()
    assert empty.store().load() == (None, "0")
    doc = new_document("2026-10-20")
    empty.store().save(doc, "0")
    upload = empty.requests[-1]
    assert upload.url.params["uploadType"] == "media" and upload.url.params["name"] == "night-orders/state.json"
    assert upload.url.params["ifGenerationMatch"] == "0" and upload.headers["Content-Type"] == "application/json"
    assert upload.headers["Authorization"] == "Bearer test-google-token"
    assert empty.stored == doc
    assert b"/o/night-orders%2Fstate.json" in empty.requests[1].url.raw_path

    full = Gcs(stored=doc)
    loaded, generation = full.store().load()
    assert (loaded, generation) == (doc, "1700000000000001")
    media = full.requests[-1]
    assert media.url.params["alt"] == "media" and media.url.params["generation"] == "1700000000000001"

    with pytest.raises(StateConflict):
        Gcs(stored=doc, conflict=True).store().save(doc, "1700000000000001")


def test_restored_ledger_answers_the_same_questions(oncall):
    ledger = Ledger()
    ledger.record(at(oncall, "03:13"), "acted", "Order 1 carried out.", incident=2, order=1,
                  action={"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"})
    doc = new_document("2026-10-20")
    doc["watch"]["ledger"] = [
        {"at": e.at.isoformat(), "kind": e.kind, "text": e.text, "incident": e.incident, "order": e.order,
         "data": e.data} for e in ledger.events]
    restored = load_ledger(json.loads(json.dumps(doc)))
    assert restored.used(1) and restored.pending_recheck() == ledger.pending_recheck()
    assert restored.recheck_due(at(oncall, "03:23"), 10) is not None
    assert restored.events[0].at == at(oncall, "03:13") and restored.events[0].at.utcoffset() == timedelta(hours=-7)
