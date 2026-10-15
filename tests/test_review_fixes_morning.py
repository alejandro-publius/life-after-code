"""Fixes from the 11 Oct review of the morning. Offline.

A thumbs-up after the watch end changes nothing; a night with no good tick before noon still gets its record;
a target a person changed after the night is left alone; a restore that keeps failing neither fails the tick
nor holds up the rest; the countersign file is read after the watch, on the chores budget; and a countersign
merge request left open for an earlier night does not stop code from opening one for this night.

The demo night is demo data (planted faults, simulated shop). Every other name, number and time is test data.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time

import pytest

from conftest import OPS, REPO, at
from nightorders import Metrics, demo_night, morning, state
from nightorders.decide import Night
from nightorders.gitlab_ports import RelayError
from nightorders.ledger import Ledger
from nightorders.morning import StateFile, step
from nightorders.orders import OrdersError, load_yaml, parse_oncall
from nightorders.sources import GitLabSources, Inputs
from nightorders.watch import Incident, Watch, parse_alert_rules
from test_morning import FakePorts, local, night, signed  # noqa: F401
from test_relay_morning import KEY, NightThroughTheRelay, main
from test_relay_ports import API, Server, body, ports_for
from test_watch_approval import FALLBACK, ReactionPorts

KEEP_NOTHING = {"night": "2026-10-20", "flags": [], "services": []}


# A5: an approval that lands after the watch end would change production behind the morning record.

def test_a_thumbs_up_seen_after_the_watch_end_changes_nothing_and_says_why(make_night, oncall):
    night = make_night()
    ports = ReactionPorts([("alex-velazquez", at(oncall, "07:01"))])
    watch = Watch(night, ports, rules=parse_alert_rules(load_yaml(OPS / "alerts.yml")))
    watch.incidents.append(Incident(number=1, alerts=[], opened_at=at(oncall, "06:40"), paged_at=at(oncall, "06:42"),
                                    suggest=FALLBACK, keys={"checkout_error_rate.old"}))
    relay_doc: dict = {}
    watch.tick(Metrics(), at(oncall, "07:00"))
    step(relay_doc, night, watch.expired, None, FakePorts(), at(oncall, "07:00"), 7)  # the record is made now
    watch.tick(Metrics(), at(oncall, "07:02"))
    watch.tick(Metrics(), at(oncall, "07:03"))
    assert ports.applied == []  # production is as the record says
    assert ports.notes == ["Tonight's orders ended at 07:00; approve it by hand."]  # said once
    assert relay_doc["dawn"]["loose_ends"] == []


# A6: no good tick from the watch end to noon used to drop the night's ledger before its record was made.

def test_watch_ends_at_or_after_noon_is_refused_and_the_relay_says_why():
    data = load_yaml(OPS / "oncall.yml")
    assert parse_oncall(dict(data, watch_ends="11:59")).watch_ends == time(11, 59)
    for late in ("12:00", "13:30"):
        with pytest.raises(OrdersError) as error:
            parse_oncall(dict(data, watch_ends=late))
        assert error.value.problems == [f"ops/oncall.yml: watch_ends {late} must be before 12:00, when the next "
                                        "night's record starts"]
    server = Server({("GET", f"{API}/repository/files/ops/oncall.yml/raw"): (200, "user: alex\ntimezone: UTC\n"
                                                                                 "watch_ends: \"12:30\"\n")})
    http = server.http()
    sources = GitLabSources(ports_for(server).gitlab, http, "https://shop.example/metrics.json")
    with pytest.raises(RelayError) as refused:
        sources._config("ops/oncall.yml", "main", parse_oncall)
    assert str(refused.value) == ("ops/oncall.yml: watch_ends 12:30 must be before 12:00, when the next night's "
                                  "record starts")


class DownAtDawn(NightThroughTheRelay):
    """The demo night through the relay, with no tick from the watch end on (the relay is down until after noon)."""

    def tick(self, metrics, now):
        self.metrics, self.now = metrics, now
        if now < datetime(2026, 10, 21, 7, 0, tzinfo=self.night.oncall.timezone):
            return super().tick(metrics, now)
        return None


@pytest.fixture
def down_at_dawn(tmp_path, monkeypatch):
    monkeypatch.setenv("RELAY_KEY", KEY)
    NightThroughTheRelay.tmp_path = tmp_path
    monkeypatch.setattr(demo_night, "Watch", DownAtDawn)
    ports, night = demo_night.run(REPO / "demo" / "night-2026-10-20")
    return ports, night, NightThroughTheRelay.current


def test_a_night_with_no_good_tick_before_noon_still_gets_its_record_from_its_own_ledger(down_at_dawn):
    ports, night, relay = down_at_dawn
    assert ports.watch_notes == []  # nothing ran from 07:00 on
    summary = NightThroughTheRelay.tick(relay, relay.metrics, datetime(2026, 10, 21, 12, 5, tzinfo=night.oncall.timezone))
    assert summary["night"] == "2026-10-21"  # the noon rollover happened in this tick
    assert summary["morning"][:4] == ["night of 2026-10-20 ended with 2 loose end(s) awaiting the countersign",
                                      "watch log posted", "good-morning push sent", "dawn flow started"]
    [log] = ports.watch_notes
    assert log.startswith("## Watch log, night of Tue 20 Oct")
    assert "Signed: 2 orders, by Priya at 22:06 (merge)." in log
    assert "- stock_from_cache on in production (approved by thumbs-up, 01:53)" in log
    assert "- new_checkout off in production (order 1, 03:13)" in log
    doc = relay.store.load()[0]
    record = doc["relay"]["dawn"]
    assert record["night"] == "2026-10-20" and record["ended_at"].startswith("2026-10-21T07:00")
    assert [item["before"]["value"] for item in record["loose_ends"]] == ["off", "on"]
    assert doc["watch"]["earlier"] == [] and doc["watch"]["ledger"] == []  # used once, then dropped
    again = NightThroughTheRelay.tick(relay, relay.metrics, datetime(2026, 10, 21, 12, 6, tzinfo=night.oncall.timezone))
    assert again["morning"] == [] and len(ports.watch_notes) == 1


def test_a_night_whose_record_was_made_in_the_morning_is_not_kept_at_noon(make_night, oncall):
    watch = Watch(make_night(), ports=None, rules=[])
    doc = state.new_document("2026-10-20")
    state.capture(watch, doc)
    doc["relay"] = {"dawn": {"night": "2026-10-20"}}
    fresh = state.next_night(doc, "2026-10-21", watch.night.orders, oncall, at(oncall, "12:00").replace(day=21))
    assert "earlier" not in fresh["watch"]
    del doc["relay"]["dawn"]
    kept = state.next_night(doc, "2026-10-21", watch.night.orders, oncall, at(oncall, "12:00").replace(day=21))
    [earlier] = state.earlier_nights(kept, oncall, watch.night.targets)
    assert earlier.orders == watch.night.orders and earlier.signature == watch.night.signature


# A7: the countersign used to put the night's snapshot back over a change a person made after the night.

class ChangedByHand(FakePorts):
    def __init__(self, changed: set[str]):
        super().__init__()
        self.changed = changed

    def holds(self, action):
        return action.flag not in self.changed


def test_a_target_changed_after_the_night_is_left_as_it_is_and_the_note_says_so(night):
    relay_doc, ports = {}, ChangedByHand({"stock_from_cache"})
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    step(relay_doc, night, True, StateFile(KEEP_NOTHING, signed(night, "2026-10-21T07:42")), ports,
         local(night, "2026-10-21T07:43"), 7)
    assert [name for name, _ in ports.restored] == ["new_checkout off in production"]
    note = ports.notes[-1].splitlines()
    assert "- Not restored: stock_from_cache in production was changed after the night, so code left it as it is" in note
    assert "- Restored: new_checkout in production to how it was before the night (on)" in note
    assert relay_doc["dawn"]["countersign"]["left"] == [
        "stock_from_cache in production was changed after the night, so code left it as it is"]


def test_a_failed_change_that_is_not_in_place_is_left_and_said_plainly(make_night, oncall):
    ledger = Ledger()
    flag_off = {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}
    ledger.record(at(oncall, "03:13"), "failed", "Order 1 could not be carried out (HTTP 502).", incident=2, order=1,
                  action=flag_off, before={"kind": "flag", "flag": "new_checkout", "value": "on"})
    later = make_night(ledger=ledger)
    relay_doc, ports = {}, ChangedByHand({"new_checkout"})
    step(relay_doc, later, True, None, ports, at(oncall, "07:00"), 7)
    step(relay_doc, later, True, StateFile(KEEP_NOTHING, signed(later, "2026-10-21T07:42")), ports,
         at(oncall, "07:43"), 7)
    assert ports.restored == []
    assert ("- Not restored: new_checkout off in production did not take, or was changed after the night, so code "
            "left it as it is") in ports.notes[-1]


# A8: a restore that keeps failing used to fail every tick, stop the chores and page her hourly.

class FlagDown(FakePorts):
    """Restoring new_checkout always fails; everything else works."""

    def __init__(self):
        super().__init__()
        self.tries = 0

    def restore(self, action, before, at):
        if action.flag == "new_checkout":
            self.tries += 1
            raise RelayError("GitLab restore flag new_checkout: HTTP 503")
        return super().restore(action, before, at)


def test_a_restore_that_keeps_failing_is_handed_to_a_person_after_five_tries_and_the_rest_is_done_once(night):
    relay_doc, ports = {}, FlagDown()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    signed_file = StateFile(KEEP_NOTHING, signed(night, "2026-10-21T07:42"))
    for minute in range(43, 47):  # tries 1 to 4: the error is raised, the record keeps the plan
        with pytest.raises(RelayError):
            step(relay_doc, night, True, signed_file, ports, local(night, f"2026-10-21T07:{minute}"), 7)
    assert relay_doc["dawn"]["countersign"] is None and len(ports.notes) == 1  # only the watch log so far
    done = step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:47"), 7)  # no new read needed
    assert ports.tries == 5
    assert ports.restored == [("stock_from_cache on in production",
                               {"kind": "flag", "flag": "stock_from_cache", "environment": "production",
                                "value": "off"})]  # once, on the first try
    assert done == ["Countersign by Priya at 07:42 (merge), applied by code."]
    note = ports.notes[-1].splitlines()
    assert "- Restored: stock_from_cache in production to how it was before the night (off)" in note
    assert ("- For a person: Code could not restore new_checkout in production to how it was before the night (on) "
            "after 5 tries (GitLab restore flag new_checkout: HTTP 503). Do it by hand.") in note
    assert "applying" not in relay_doc["dawn"]
    step(relay_doc, night, True, signed_file, ports, local(night, "2026-10-21T07:48"), 7)
    assert ports.tries == 5 and len(ports.notes) == 2  # done: noted once


class NoTimeLeft(RelayError):
    sent = False  # as gitlab_ports.NotSent: the tick had no time left, so nothing went out


def test_a_restore_the_tick_had_no_time_to_send_is_not_counted_as_a_try(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    signed_file = StateFile(KEEP_NOTHING, signed(night, "2026-10-21T07:42"))

    def no_time(action, before, at):
        raise NoTimeLeft("GitLab read flag: skipped, the tick ran out of time")

    ports.restore = no_time
    for minute in range(43, 50):
        with pytest.raises(RelayError):
            step(relay_doc, night, True, signed_file, ports, local(night, f"2026-10-21T07:{minute}"), 7)
    assert [item["tries"] for item in relay_doc["dawn"]["applying"]["undo"]] == [0, 0]


class MorningSources:
    """The demo night's inputs at any moment, and a countersign that keeps nothing."""

    def __init__(self, night, state_file=None):
        self.night, self.file, self.reads = night, state_file, 0

    def load(self, now):
        n = self.night
        return Inputs(oncall=n.oncall, targets=n.targets, rules=[], orders=n.orders, orders_problems=(),
                      signature=n.signature, metrics=Metrics())

    def state_file(self, user):
        self.reads += 1
        return self.file


class StoredPorts(FlagDown):
    def saved(self):
        return {}


def awaiting_countersign(night, tmp_path) -> state.FileStore:
    """A store whose state is the demo night at 07:00: its record made, the watch log posted, a countersign due."""
    relay_doc: dict = {}
    step(relay_doc, night, True, None, FakePorts(), local(night, "2026-10-21T07:00"), 7)
    doc = state.new_document("2026-10-20")
    doc["watch"].update(expired=True, expired_orders="2026-10-20")
    doc["relay"] = relay_doc
    store = state.FileStore(tmp_path / "state.json")
    store.save(doc)
    return store


def test_a_failing_restore_never_fails_the_tick_never_pages_and_the_chores_still_run(night, tmp_path):
    store = awaiting_countersign(night, tmp_path)
    pages, chores = [], []
    ports = StoredPorts()
    relay = main.Relay(sources=MorningSources(night, StateFile(KEEP_NOTHING, signed(night, "2026-10-21T07:42"))),
                       store=store, make_ports=lambda saved: ports, pager=lambda *a, **k: pages.append(a),
                       watch_issue=7, rehearse=lambda doc, now, inputs: chores.append(now) or [])
    health = main.Health()
    for minute in range(43, 47):
        code, summary = main.run_tick(relay, health, local(night, f"2026-10-21T07:{minute}"))
        assert code == 200 and summary["ok"] is True
    assert pages == [] and len(chores) == 4 and health.failures == 0
    doc = store.load()[0]
    assert doc["relay"]["morning_problem"]["reason"] == "GitLab restore flag new_checkout: HTTP 503"
    assert "error" not in doc["relay"] and ports.tries == 4
    assert ports.restored[0][0] == "stock_from_cache on in production" and len(ports.restored) == 1
    main.run_tick(relay, health, local(night, "2026-10-21T07:47"))
    doc = store.load()[0]
    assert "morning_problem" not in doc["relay"] and doc["relay"]["dawn"]["countersign"]["by_hand"]


# A9: the countersign file used to be read before the watch, on the watch's 15 s budget, every tick.

def test_the_countersign_file_is_read_after_the_watch_on_the_chores_budget_every_few_minutes(night, tmp_path,
                                                                                           monkeypatch):
    store = awaiting_countersign(night, tmp_path)
    order: list[str] = []

    class Recorded(Watch):
        def tick(self, metrics, now):
            order.append("watch")
            super().tick(metrics, now)

    class WatchBudget(MorningSources):
        def state_file(self, user):
            raise AssertionError("read on the watch's budget")

    class ChoresBudget(MorningSources):
        def state_file(self, user):
            order.append("countersign file")
            return super().state_file(user)

    monkeypatch.setattr(main, "Watch", Recorded)
    chores = ChoresBudget(night, StateFile(None, None))
    relay = main.Relay(sources=WatchBudget(night), store=store, make_ports=lambda saved: StoredPorts(),
                       pager=lambda *a, **k: None, watch_issue=7)
    relay.chores_sources = chores  # make_relay builds it on the chores Http
    for minute in range(1, 8):
        code, _ = main.run_tick(relay, main.Health(), local(night, f"2026-10-21T07:{minute:02d}"))
        assert code == 200
    # Read at 07:01, 07:04 and 07:07: never before the watch, never more often than every three minutes.
    assert chores.reads == 3
    assert order[:2] == ["watch", "countersign file"] and order.count("watch") == 7


# A10: a countersign merge request left open for an earlier night used to stop code from opening this night's.

def test_an_open_countersign_for_an_earlier_night_does_not_count_and_code_opens_one_that_replaces_it(night):
    relay_doc: dict = {}
    step(relay_doc, night, True, None, FakePorts(), local(night, "2026-10-21T07:00"), 7)
    relay_doc["dawn"]["code_request"] = 50  # code opened !50 for the night of 20 Oct; nobody merged it
    later = dataclasses.replace(night, orders=dataclasses.replace(night.orders, night=date(2026, 10, 21)))
    server = Server({
        ("GET", API): {"id": 123, "default_branch": "main", "web_url": "https://gitlab.example/g/p"},
        ("GET", f"{API}/merge_requests"): [{"iid": 50, "sha": "c50"}],
        ("GET", f"{API}/merge_requests/50/diffs"): [{"new_path": "ops/state.yml", "old_path": "ops/state.yml"}],
        ("GET", f"{API}/repository/files/ops/state.yml/raw"): (200, 'night: "2026-10-20"\nflags: []\nservices: []\n'),
        ("POST", f"{API}/repository/commits"): (201, {"id": "c61"}),
        ("POST", f"{API}/merge_requests"): (201, {"iid": 61}),
        ("POST", f"{API}/issues/7/notes"): (201, {"id": 900}),
        ("POST", "/test-topic-not-real"): {"id": "push"},
    })
    ports = ports_for(server)
    ports.watch_issue = 7
    done = step(relay_doc, later, True, None, ports, local(night, "2026-10-22T07:00"), 7)
    assert relay_doc["dawn"]["nights"] == ["2026-10-20", "2026-10-21"]
    assert "countersign merge request !61 opened by code" in done
    [opened] = server.sent("POST", f"{API}/merge_requests")
    assert body(opened)["title"] == "Countersign 2026-10-21 (written by code)"
    assert ("This replaces !50: still open, but its ops/state.yml does not name the night of 2026-10-21. Close it, "
            "so that only this merge request countersigns the night.") in body(opened)["description"]
    raw = [r for r in server.requests if r.url.path.endswith("/raw")]
    assert raw[0].url.params["ref"] == "c50"  # the file was read at the merge request's head


def test_an_open_countersign_that_names_this_night_still_counts():
    server = Server({("GET", API): {"id": 123, "default_branch": "main"},
                     ("GET", f"{API}/merge_requests"): [{"iid": 52, "sha": "c52"}, {"iid": 50, "sha": "c50"}],
                     ("GET", f"{API}/merge_requests/52/diffs"): [{"new_path": "ops/state.yml"}],
                     ("GET", f"{API}/merge_requests/50/diffs"): [{"old_path": "ops/state.yml"}],
                     ("GET", f"{API}/repository/files/ops/state.yml/raw"): (200, "night: 2026-10-21\nflags: []\n")})
    assert ports_for(server).countersign_request_open("2026-10-21") == (52, [50])
    assert ports_for(server).countersign_request_open("2026-10-22") == (None, [52, 50])


def test_the_earlier_ledger_rebuilds_the_same_loose_ends(night):
    doc = state.new_document("2026-10-20")
    watch = Watch(night, ports=None, rules=[])
    state.capture(watch, doc)
    fresh = state.next_night(doc, "2026-10-21", night.orders, night.oncall, local(night, "2026-10-21T12:05"))
    [earlier] = state.earlier_nights(fresh, night.oncall, night.targets)
    assert earlier.ledger.events == night.ledger.events
    assert morning.loose_from(morning.new_record(earlier)) == morning.loose_from(morning.new_record(night))
    assert isinstance(earlier, Night) and earlier.orders.expires == time(7, 0)
    state.forget_recorded(fresh)
    assert len(fresh["watch"]["earlier"]) == 1  # nothing recorded yet
    fresh["relay"]["dawn"] = {"night": "2026-10-20"}
    state.forget_recorded(fresh)
    assert fresh["watch"]["earlier"] == []
