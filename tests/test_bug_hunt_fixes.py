"""Fixes from the 11 Oct bug hunt over the rehearsal, the day sheet, the watch and the scripts. Offline.

Every name, commit and time here is test data; the orders are the demo night's orders.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from conftest import OPS, at
from nightorders import Metrics, Request, render_request
from nightorders.daysheet import collect, render, step as daysheet_step
from nightorders.gitlab_ports import GitLab, Http, RelayError
from nightorders.orders import load_context
from nightorders.rehearsal import MAX_RESTORE_TRIES, SHOP_FETCH_WAIT_SECONDS
from nightorders.watch import Watch
from test_daysheet import API as DAY_API, NOW as DAY_NOW, Server, gitlab_for, routes
from test_rehearsal import ORDERS, SHA, World, run, staging_scopes
from test_standing_orders import Ports, bad_minutes, rules

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import day_one  # noqa: E402
import test_night  # noqa: E402

NEW = "checkout_error_rate.new"
OLD = "checkout_error_rate.old"


# The rehearsal puts staging back when it stops halfway, and waits for the shop to see its change.

class RestoreDown(World):
    """GitLab answers 503 to the second PUT (the restore) for `failures` rehearsals, then recovers."""

    def __init__(self, failures: int = 1):
        super().__init__()
        self.failures = failures
        self.puts = 0

    def __call__(self, request):
        if request.method == "PUT" and request.url.path.endswith("/feature_flags/new_checkout"):
            self.puts += 1
            if self.puts >= 2 and self.failures:  # the first PUT is the apply; every later one is a restore
                self.failures -= 1
                self.requests.append(request)
                return httpx.Response(503, json={"message": "down"})
        return super().__call__(request)


def test_a_restore_that_fails_is_said_in_the_note_and_done_on_the_next_tick():
    world = RestoreDown(failures=1)
    before = staging_scopes(world)
    reported, doc = run(world)
    assert reported == ["rehearsed !31 at abc123de"]
    body = world.notes[0]["body"]
    assert ("- order 1: rehearsal stopped (GitLab restore flag new_checkout: HTTP 503 (down)); staging may be left "
            "with new_checkout off in staging applied, code restores it on the next ticks") in body
    assert staging_scopes(world) == []  # staging is still changed after this tick
    [entry] = doc["rehearsal_pending"]
    assert entry["iid"] == 31 and entry["order"] == 1 and entry["before"]["strategies"][0]["name"] == "userWithId"
    reported, doc = run(world, doc)
    assert reported == ["restored staging after an unfinished rehearsal of !31: new_checkout off in staging is "
                        "on for 2 listed users again"]
    assert staging_scopes(world) == before and doc["rehearsal_pending"] == []
    assert len(world.notes) == 1  # the head was rehearsed once; only the restore was repeated


def test_a_restore_that_keeps_failing_is_left_for_a_person_and_shown():
    world = RestoreDown(failures=MAX_RESTORE_TRIES + 1)
    _, doc = run(world)
    for _ in range(MAX_RESTORE_TRIES - 1):
        run(world, doc)
    assert len(doc["rehearsal_pending"]) == 1 and "rehearsal_left" not in doc  # still trying
    run(world, doc)
    assert doc["rehearsal_pending"] == []
    left = doc["rehearsal_left"]
    assert left["what"] == "new_checkout off in staging" and left["iid"] == 31
    assert left["before"] == "on for 2 listed users" and left["reason"].startswith("GitLab restore flag new_checkout")


def test_the_checkout_waits_until_the_staging_shop_fetched_the_change():
    world = World()
    run(world)
    flag_reads = [r for r in world.requests if r.url.host == "shop-staging.example" and r.url.path == "/flags"]
    checkouts = [r for r in world.requests if r.url.host == "shop-staging.example" and r.url.path == "/checkout"]
    assert len(flag_reads) == 2 and len(checkouts) == 1  # the mark before the apply, one poll that saw it move
    assert world.requests.index(checkouts[0]) > world.requests.index(flag_reads[-1])


def test_a_shop_that_never_fetches_is_said_so_after_the_wait():
    world = World(shop_fetches=False)
    slept: list[float] = []
    oncall, targets = load_context(OPS)
    from nightorders.gitlab_ports import GitLabPorts, GoogleToken
    from nightorders.rehearsal import step
    clock = {"t": 0.0}

    def sleep(seconds):
        slept.append(seconds)
        clock["t"] += seconds

    http = Http(httpx.Client(transport=httpx.MockTransport(world)))
    gitlab = GitLab(http, "https://gitlab.example", "123", "test-token")
    ports = GitLabPorts(gitlab, http, flow_consumer_id="77", flow_service_account="duo-watch",
                        ntfy_url="https://ntfy.example/t", gcp_project="demo-project", gcp_region="us-central1",
                        google_token=GoogleToken(http))
    import nightorders.rehearsal as rehearsal_module
    original = rehearsal_module.check_shop

    def check_with_fake_clock(http, base_url, mark=None, sleep_=sleep, clock_=lambda: clock["t"]):
        return original(http, base_url, mark, sleep_, clock_)

    rehearsal_module.check_shop = check_with_fake_clock
    try:
        step({}, datetime(2026, 10, 21, 4, 35, tzinfo=timezone.utc), oncall, targets, gitlab, ports, http,
             "https://shop-staging.example", sleep=sleep)
    finally:
        rehearsal_module.check_shop = original
    assert sum(slept) >= SHOP_FETCH_WAIT_SECONDS
    assert (f"the staging shop did not fetch the change within {SHOP_FETCH_WAIT_SECONDS} s, checkout ok on the old "
            "path, restored") in world.notes[0]["body"]
    assert staging_scopes(world) == [("userWithId", "staging")]


def test_a_draft_that_removes_the_orders_file_is_said_plainly():
    class Removed(World):
        def __call__(self, request):
            if request.url.path.startswith("/api/v4/projects/123/repository/files/"):
                self.requests.append(request)
                return httpx.Response(404, json={"message": "404 File Not Found"})
            return super().__call__(request)

    world = Removed()
    run(world)
    assert "This draft removes the orders file: merging it signs nothing, so every alert wakes you." in world.notes[0]["body"]
    assert not any(r.method == "PUT" for r in world.requests)


def test_a_closed_request_leaves_the_rehearsed_record():
    class NoneOpen(World):
        def __call__(self, request):
            if request.url.path == "/api/v4/projects/123/merge_requests" and request.method == "GET":
                self.requests.append(request)
                return httpx.Response(200, json=[])
            return super().__call__(request)

    world = World()
    _, doc = run(world)
    assert doc["rehearsed"] == {"31": SHA}
    run(NoneOpen(), doc)
    assert doc["rehearsed"] == {}


# The day sheet tries again every five minutes until midnight, and shows what GitLab lacks.

class Flaky(Server):
    def __init__(self, routes, failures):
        super().__init__(routes)
        self.failures = failures

    def __call__(self, request):
        if request.url.path == f"{DAY_API}/merge_requests" and self.failures:
            self.failures -= 1
            self.requests.append(request)
            return httpx.Response(503, json={"message": "down"})
        return super().__call__(request)


def test_the_day_sheet_is_tried_every_five_minutes_after_a_failure():
    oncall, targets = load_context(OPS)
    server = Flaky(routes(), failures=1)
    gitlab = gitlab_for(server)
    doc: dict = {}
    first = DAY_NOW  # 21:30 local
    with pytest.raises(RelayError):
        daysheet_step(doc, first, oncall, targets, gitlab, 7)
    for minute in (1, 2, 4):
        assert daysheet_step(doc, first + timedelta(minutes=minute), oncall, targets, gitlab, 7) == []
    lists = [r for r in server.requests if r.url.path == f"{DAY_API}/merge_requests"]
    assert len(lists) == 1  # nothing tried in between
    posted = daysheet_step(doc, first + timedelta(minutes=5), oncall, targets, gitlab, 7)
    assert posted == ["day sheet posted on the watch issue: 1 merge(s), 1 deployment(s)"]
    assert doc["daysheet"] == "2026-10-20" and doc["daysheet_tries"] == {"2026-10-20": 2}


def test_the_day_sheet_lists_a_flag_gitlab_does_not_have_and_quotes_deployment_refs():
    oncall, targets = load_context(OPS)
    data = routes()
    data[f"{DAY_API}/feature_flags"] = [f for f in data[f"{DAY_API}/feature_flags"] if f["name"] != "stock_from_cache"]
    data[f"{DAY_API}/deployments"][0]["ref"] = "feature/@everyone #1"
    sheet = collect(gitlab_for(Server(data)), DAY_NOW, oncall, targets)
    missing = [f for f in sheet["flags"] if f["name"] == "stock_from_cache"]
    assert missing and all(f["state"] == "not in GitLab" for f in missing)
    text = render(sheet)
    assert "- stock_from_cache in production: not in GitLab" in text
    assert "from `feature/@everyone #1`" in text


def test_a_busy_day_is_read_across_pages():
    oncall, targets = load_context(OPS)
    data = routes()
    full_page = [{"iid": 100 + i, "title": f"Change {i}", "merged_at": "2026-10-20T23:12:00Z",
                  "author": {"username": "x"}} for i in range(25)]
    data[f"{DAY_API}/merge_requests"] = full_page
    for item in full_page:
        data[f"{DAY_API}/merge_requests/{item['iid']}/diffs"] = []
    server = Server(data)
    sheet = collect(gitlab_for(server), DAY_NOW, oncall, targets)
    pages = [r.url.params.get("page") for r in server.requests if r.url.path == f"{DAY_API}/merge_requests"]
    assert pages == ["1", "2", "3", "4"] and len(sheet["merged_today"]) == 100


# A paged incident whose suggestion nobody answered closes when the signals recover.

def test_an_unanswered_suggestion_is_dropped_when_the_signals_recover_and_a_later_fault_still_reaches_the_order(
        oncall, make_night):
    decline = render_request(Request(order=None, fits_because=None, declined_id=1, declined_why="both paths fail",
                                     page=("Both paths fail.",),
                                     suggest={"action": "flag_set", "flag": "stock_from_cache", "environment": "production",
                                              "to": "on"}))
    night, ports = make_night(), Ports(reply=decline)
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "01:45", 15, 0.204)
    bad_minutes(metrics, oncall, OLD, "01:45", 15, 0.203)
    bad_minutes(metrics, oncall, NEW, "02:00", 20, 0.0)
    bad_minutes(metrics, oncall, OLD, "02:00", 20, 0.0)
    for minute in range(0, 21):
        watch.tick(metrics, at(oncall, "01:50") + timedelta(minutes=minute))
    assert len(ports.pages) == 1 and ports.pages[0][-1].startswith("Thumbs-up the note on #1")
    assert ports.closed == [1]
    assert [e.kind for e in night.ledger.events] == ["alert", "asked", "declined", "woke", "refused"]
    assert night.ledger.events[-1].text == ("The signals recovered at 02:01 before anyone approved the suggestion, "
                                            "so it was dropped. Nothing was changed.")
    bad_minutes(metrics, oncall, NEW, "02:20", 8, 0.079)
    for minute in range(0, 8):
        watch.tick(metrics, at(oncall, "02:20") + timedelta(minutes=minute))
    assert len(ports.started) == 2 and ports.started[1][0] == 1  # the stub numbers every incident 1
    # a new incident opened and the agent was asked about order 1 again (the stub then serves the same decline)
    assert [e.kind for e in night.ledger.events][5:7] == ["alert", "asked"]


# The test-night runner.

class FakeShop:
    def __init__(self, status: int = 200, interrupt_at: dict | None = None):
        self.requests: list[httpx.Request] = []
        self.status, self.interrupt_at = status, interrupt_at

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = json.loads(request.content) if request.content else None
        if self.interrupt_at is not None and body == self.interrupt_at:
            raise KeyboardInterrupt  # the person stops the runner mid-night
        return httpx.Response(self.status, json={"ok": True})


class Clock:
    def __init__(self, start: datetime):
        self.now, self.slept = start, []

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += timedelta(seconds=seconds)


def play(fake: FakeShop, start: datetime):
    client = httpx.Client(transport=httpx.MockTransport(fake))
    clock = Clock(start)
    shop = test_night.Shop("https://shop.example/", "demo-key-for-tests", client=client, sleep=clock.sleep)
    out = io.StringIO()
    code = test_night.run(shop, test_night.timeline(3, 16, 20, 45), start, lambda: clock.now, clock.sleep, out=out)
    return code, out.getvalue(), clock


def test_the_runner_turns_the_faults_off_and_stops_traffic_on_every_exit():
    fake = FakeShop(interrupt_at={"rounding_bug": True})
    with pytest.raises(KeyboardInterrupt):
        play(fake, datetime(2026, 10, 18, 1, 40, tzinfo=timezone.utc))
    bodies = [json.loads(r.content) if r.content else dict(r.url.params) for r in fake.requests]
    assert bodies[-3] == {"rounding_bug": True}  # the step that was interrupted
    assert bodies[-2] == {"inventory_slow": False, "rounding_bug": False} and bodies[-1] == {"minutes": "0"}
    fine = FakeShop()
    code, printed, _ = play(fine, datetime(2026, 10, 18, 1, 40, tzinfo=timezone.utc))
    assert code == 0 and "planted faults off: ok" in printed and "demo traffic stopped: ok" in printed


def test_the_runner_stops_at_once_when_the_shop_refuses_the_key():
    fake = FakeShop(status=401)
    code, printed, clock = play(fake, datetime(2026, 10, 18, 1, 40, tzinfo=timezone.utc))
    assert code == 1 and len(fake.requests) == 1 and clock.slept == []
    assert "stopping: the shop refuses the demo key" in printed


def test_the_waits_are_real_minutes_across_a_clock_change():
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Los_Angeles")
    start = datetime(2026, 11, 1, 1, 40, tzinfo=timezone.utc).astimezone(tz)  # the night the clocks fall back
    _, _, clock = play(FakeShop(), start)
    assert sum(clock.slept) == 45 * 60


def test_the_runner_starts_in_the_named_minute_and_checks_the_time_argument():
    now = datetime(2026, 10, 17, 1, 40, 30, tzinfo=timezone.utc)
    assert test_night.next_occurrence("01:40", now) == datetime(2026, 10, 17, 1, 40, tzinfo=timezone.utc)
    with pytest.raises(SystemExit):
        test_night.main(["--shop", "https://shop.example", "--at", "25:00", "--dry-run"])
    with pytest.raises(SystemExit):
        test_night.main(["--shop", "https://shop.example", "--end", "10", "--dry-run"])


def test_the_default_slowdown_outlasts_the_standing_orders_re_check(capsys):
    assert test_night.main(["--shop", "https://shop.example", "--at", "01:40", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "01:59  planted fault inventory_slow off" in out


# The day-one script's probe step.

def test_the_probe_answer_comes_from_a_flow_account_oldest_first():
    notes = [  # newest first, as GitLab lists them
        {"id": 3, "body": "probe ok (me, copying it)", "author": {"username": "alex"}},
        {"id": 2, "body": "PROBE OK", "author": {"username": "ai-flow-bot"}},
        {"id": 1, "body": "probe ok", "author": {"username": "ai-flow-bot"}, "system": True},
    ]
    note, _elapsed, problem = day_one.wait_for_note(lambda: notes, "probe ok", clock=lambda: 0.0,
                                                    sleep=lambda s: None, ignore_authors={"alex"})
    assert note["id"] == 2 and problem == ""
