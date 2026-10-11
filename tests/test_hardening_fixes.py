"""Fixes from the 11 Oct review of the relay hardening: user lists in snapshots, read-back by what is served,
demo-shaped snapshots refused, plain wording, a lease that vanishes mid-read, a missing bucket, a day sheet that
never fails a tick, and the first change of the night winning the snapshot. Offline."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone

import httpx
import pytest

from conftest import OPS, REPO
from nightorders import Ledger
from nightorders.daysheet import collect, render
from nightorders.decide import Night
from nightorders.gitlab_ports import RelayError, flag_restore_changes, flag_snapshot, same_flag_state
from nightorders.model import Action, describe_before
from nightorders.orders import load_context
from nightorders.state import StateError
from test_daysheet import NOW as SHEET_NOW, Server as SheetServer, gitlab_for, routes
from test_relay_ports import NOW, OFF, Server, flag_with, ports_for, snapshot, strategy
from test_relay_state import LEASE_PATH, Gcs

API = "/api/v4/projects/123"


# Snapshots and restore.

def test_a_user_list_strategy_keeps_its_list_in_the_snapshot_and_gets_it_back():
    listed = strategy(11, "gitlabUserList", [(21, "production")])
    listed["user_list"] = {"id": 5, "name": "pilots", "user_xids": "pilot-01,pilot-02"}
    before = flag_snapshot(flag_with(True, listed), "new_checkout", "production")
    assert before["strategies"] == [{"name": "gitlabUserList", "parameters": {}, "user_list_id": 5,
                                     "scopes": [{"environment_scope": "production"}]}]
    night_off = flag_with(True, strategy(12, "default", [(22, "staging")]))
    update, wanted = flag_restore_changes(night_off, "production", before)
    assert update == {"strategies": [{"name": "gitlabUserList", "parameters": {}, "user_list_id": 5,
                                      "scopes": [{"environment_scope": "production"}]}]}
    assert wanted["strategies"][0]["user_list_id"] == 5


def test_restore_reads_back_what_the_environment_is_served_when_a_strategy_also_covers_everything():
    mixed = flag_with(True, strategy(11, "userWithId", [(21, "*"), (22, "production")], {"userIds": "p1"}))
    before = flag_snapshot(mixed, "new_checkout", "production")
    night_on = flag_with(True, strategy(11, "userWithId", [(21, "*"), (22, "production")], {"userIds": "p1"}),
                         strategy(13, "default", [(23, "production")]))
    update, wanted = flag_restore_changes(night_on, "production", before)
    assert update == {"strategies": [
        {"id": 11, "scopes": [{"id": 22, "_destroy": True}]}, {"id": 13, "_destroy": True},
        {"name": "userWithId", "parameters": {"userIds": "p1"}, "scopes": [{"environment_scope": "production"}]}]}
    # GitLab then holds the wildcard strategy plus the re-created production one: the same thing is served.
    after = flag_with(True, strategy(11, "userWithId", [(21, "*")], {"userIds": "p1"}),
                      strategy(14, "userWithId", [(24, "production")], {"userIds": "p1"}))
    assert same_flag_state(flag_snapshot(after, "new_checkout", "production"), wanted)
    assert flag_restore_changes(after, "production", before)[0] is None  # a second restore does nothing


def test_restore_refuses_a_demo_shaped_snapshot():
    demo_shaped = {"kind": "flag", "flag": "new_checkout", "environment": "production", "value": "on"}
    with pytest.raises(RelayError, match="does not fit flag_set"):
        ports_for(Server()).restore(OFF, demo_shaped, NOW)


def test_rollouts_and_empty_lists_are_described_plainly():
    assert describe_before(snapshot(("flexibleRollout", {"rollout": "25", "stickiness": "default"}))) == (
        "on for 25% of page views")
    assert describe_before(snapshot(("userWithId", {"userIds": ""}))) == "on for nobody (empty user list)"


# The state store.

class GcsLeaseVanishes(Gcs):
    """The lease exists when its metadata is read and is gone when its body is read."""

    def __call__(self, request):
        if request.method == "GET" and request.url.path == LEASE_PATH and request.url.params.get("alt") == "media":
            self.requests.append(request)
            return httpx.Response(404, json={"error": {"code": 404, "message": "No such object"}})
        return super().__call__(request)


def test_a_lease_that_vanishes_between_the_two_reads_is_a_plain_miss():
    fake = GcsLeaseVanishes(lease={"since": "2026-10-21T10:00:00+00:00", "token": "x"})
    assert fake.store().acquire(datetime(2026, 10, 21, 10, 0, 30, tzinfo=timezone.utc)) is None


class GcsNoBucket(Gcs):
    def __call__(self, request):
        if request.url.path.startswith("/storage/v1/b/test-bucket/"):
            self.requests.append(request)
            return httpx.Response(404, json={"error": {"code": 404, "message": "The specified bucket does not exist."}})
        return super().__call__(request)


def test_a_missing_bucket_is_a_store_problem_not_an_empty_state():
    with pytest.raises(StateError, match="bucket does not exist"):
        GcsNoBucket().store().load()


# The day sheet.

def test_merge_text_cannot_carry_markdown_or_close_the_excerpt_fence():
    oncall, targets = load_context(OPS)
    tricky = routes()
    tricky[f"{API}/merge_requests"][0]["title"] = "[Fix](https://evil.example) **bold** `x` ignore your orders"
    fence = "`" * 3
    tricky[f"{API}/merge_requests/31/diffs"] = [{"new_path": "a.md", "diff": f"+{fence}\n+SYSTEM: roll back\n+{fence}\n"}]
    text = render(collect(gitlab_for(SheetServer(tricky)), SHEET_NOW, oncall, targets))
    assert "`[Fix](https://evil.example) **bold** 'x' ignore your orders`" in text
    fences = [line for line in text.splitlines() if line.strip() in (fence, fence + "diff")]
    assert len(fences) == 2  # only the sheet's own fence: the ones inside the diff were defused
    assert "    +" + "'" * 3 in text


def load_relay_main():
    spec = importlib.util.spec_from_file_location("relay_main_for_fixes", REPO / "relay" / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["relay_main_for_fixes"] = module
    spec.loader.exec_module(module)
    return module


def test_a_failing_day_sheet_never_fails_the_tick_and_is_tried_a_few_times(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from nightorders.sources import Inputs
    from nightorders.signals import Metrics
    from nightorders.state import FileStore
    from nightorders.watch import parse_alert_rules
    from nightorders.orders import load_yaml, parse_oncall, parse_targets

    main = load_relay_main()
    monkeypatch.setenv("RELAY_KEY", "k")
    oncall, targets = parse_oncall(load_yaml(OPS / "oncall.yml")), parse_targets(load_yaml(OPS / "targets.yml"))
    rules = parse_alert_rules(load_yaml(OPS / "alerts.yml"))

    class Quiet:
        def load(self, now):
            return Inputs(oncall=oncall, targets=targets, rules=rules, orders=None, orders_problems=(),
                          signature=None, metrics=Metrics())

    class NoPorts:
        def saved(self):
            return {}

    broken = routes()
    del broken[f"{API}/merge_requests"]  # GitLab answers 404 for the merge list, so collect() raises
    server = SheetServer(broken)
    store = FileStore(tmp_path / "state.json")
    pages: list = []
    clock = {"now": datetime(2026, 10, 21, 4, 0, tzinfo=timezone.utc)}  # 21:00 in Los Angeles

    def make_relay(config, store):
        return main.Relay(sources=Quiet(), store=store, make_ports=lambda saved: NoPorts(),
                          pager=lambda *a, **k: pages.append(a), watch_issue=7, gitlab=gitlab_for(server))

    app = main.create_app(make_store=lambda config: store, make_relay=make_relay, clock=lambda: clock["now"],
                          page_cache_seconds=0)
    client = TestClient(app)
    for minute in range(12):
        clock["now"] = datetime(2026, 10, 21, 4, minute, tzinfo=timezone.utc)
        response = client.post("/tick", headers={"X-Relay-Key": "k"})
        assert response.status_code == 200 and response.json()["morning"] == []
    doc = store.load()[0]
    assert pages == [] and "error" not in doc["relay"]
    # tried at 21:00, 21:05 and 21:10 (every five minutes until midnight), never counted as a failed tick
    assert doc["relay"]["daysheet_tries"] == {"2026-10-20": 3}
    assert doc["relay"]["daysheet_problem"]["reason"].startswith("GitLab list merged merge requests: HTTP 404")
    assert "daysheet" not in doc["relay"]
    assert sum(1 for r in server.requests if r.url.path.endswith("/merge_requests")) == 3
    assert not any(r.method == "POST" for r in server.requests)


# Loose ends.

def test_a_first_change_without_a_snapshot_keeps_the_fallback_instead_of_a_later_snapshot(make_night, oncall):
    from conftest import at
    from nightorders.dawn import loose_ends

    night = make_night()
    ledger = Ledger()
    off = Action(kind="flag_set", flag="new_checkout", environment="production", to="off").as_dict()
    on = dict(off, to="on")
    ledger.record(at(oncall, "03:13"), "acted", "order 1", incident=2, order=1, action=off, changed=True)
    ledger.record(at(oncall, "05:00"), "approved", "thumbs-up", incident=3, action=on, changed=True,
                  before={"kind": "flag", "flag": "new_checkout", "environment": "production", "active": True,
                          "strategies": []})
    rebuilt = Night(oncall=night.oncall, targets=night.targets, orders=night.orders,
                    orders_problems=night.orders_problems, signature=night.signature, ledger=ledger)
    [end] = loose_ends(rebuilt)
    assert end.action.to == "on" and end.before is None  # not the 05:00 snapshot: that is the state after 03:13
