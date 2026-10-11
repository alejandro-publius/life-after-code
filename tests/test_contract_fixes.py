"""The contract between the flows and the code that reads what they write, after the 11 Oct review.

A model that fences twice, adds a sentence, or suggests in the wrong shape must never cost the on-call
person a night; a dawn flow must be able to keep a traffic change; a refused countersign must not end the
morning; a standing order whose apply fails must be seen. Every name and time here is test data.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest

from conftest import OPS, REPO, at, put, series, switched_off
from nightorders import Act, Action, Alert, Ask, Change, Metrics, OrdersError, Request, Wake, check_request, render_request, triage
from nightorders.countersign import parse_state, plan_morning
from nightorders.dawn import LooseEnd
from nightorders.decide import STANDING
from nightorders.gitlab_ports import GitLab, GitLabPorts, GoogleToken, Http
from nightorders.morning import StateFile, step
from nightorders.notes import Malformed, parse_request
from nightorders.orders import load_yaml
from nightorders.watch import Watch, parse_alert_rules
from test_standing_orders import Ports, bad_minutes, rules
from test_morning import FakePorts as MorningPorts, local, night as demo_night_fixture, signed  # noqa: F401

NEW = "checkout_error_rate.new"
OLD = "checkout_error_rate.old"
P95 = "p95_latency_ms"
CLEAN = '```night-orders-request\n{"order": 1, "fits_because": "new path only", "declined": null, "page": null, "suggest": null}\n```'


# The watch flow's note: what a model is likely to write is read, what it must not do is still refused.

@pytest.mark.parametrize("note", [
    CLEAN,
    "```night-orders-request\n```night-orders-request\n{\"order\": 1, \"fits_because\": \"new path only\"}\n```\n```",
    "```night-orders-request\n```json\n{\"order\": 1, \"fits_because\": \"new path only\"}\n```\n```",
    "```night-orders-request\nHere is my decision:\n{\"order\": 1, \"fits_because\": \"new path only\"}\n```",
    "Decision:\n```json\n{\"order\": 1, \"fits_because\": \"new path only\"}\n```",
])
def test_a_fence_inside_the_fence_or_a_sentence_before_the_json_is_still_read(note):
    request = parse_request(note)
    assert isinstance(request, Request) and request.order == 1


def test_two_blocks_an_unknown_key_and_no_object_are_still_refused():
    assert isinstance(parse_request(CLEAN + "\n" + CLEAN), Malformed)
    assert parse_request('```night-orders-request\n{"order": 1, "fits_because": "x", "extra": 1}\n```') == Malformed(
        "unexpected keys: extra")
    assert parse_request("```night-orders-request\nno object here\n```") == Malformed(
        "the block is not valid JSON (no JSON object in the block)")


def test_a_suggestion_code_cannot_read_is_said_not_dropped_in_silence(oncall, make_night):
    night = make_night()
    metrics = series(oncall, NEW, "01:45", [0.2] * 6)
    alerts = [Alert(key=NEW, value=0.2, at=at(oncall, "01:50"))]
    ask = triage(alerts, night, metrics, at(oncall, "01:50"))
    assert isinstance(ask, Ask)
    unreadable = render_request(Request(order=None, fits_because=None, declined_id=1, declined_why="both paths fail",
                                        page=("Both paths fail.",), suggest={"flag_set": {"flag": "stock_from_cache"}}))
    result = check_request(unreadable, ask, at(oncall, "01:50"), alerts, night, metrics, at(oncall, "01:52"))
    assert isinstance(result, Wake) and result.suggest is None
    assert result.reasons[1] == "The agent suggested something code could not read, so there is nothing to approve."
    elsewhere = render_request(Request(order=None, fits_because=None, declined_id=1, declined_why="both paths fail",
                                       page=(), suggest={"action": "flag_set", "flag": "nope", "environment": "production",
                                                         "to": "on"}))
    result = check_request(elsewhere, ask, at(oncall, "01:50"), alerts, night, metrics, at(oncall, "01:52"))
    assert isinstance(result, Wake) and result.suggest is None
    assert result.reasons[1].startswith("The agent suggested nope on in production, which is not a listed target")


def test_the_goal_names_each_order_action_reason_and_the_signed_commit(oncall, make_night):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 6, 0.079)
    watch.tick(metrics, at(oncall, "03:12"))
    [(incident, goal)] = ports.started
    assert incident == 1
    assert "order 1: new_checkout off in production, because MR !31 turned on new_checkout in production at 16:20." in goal
    assert "numbers now: checkout error rate (new path) 7.9%, above 5.0% for 5 min" in goal
    assert "ops/night-orders.yml at commit test" in goal and "ops/targets.yml" in goal
    assert goal.endswith("If unsure, choose none.")


# The live relay reads a json-labelled flow note too (notes.py still checks every key).

FLOW_ACCOUNT = "duo-watch"
NOW = datetime(2026, 10, 21, 10, 12, tzinfo=timezone.utc)


def test_request_note_reads_a_json_labelled_note_from_the_flow_account():
    def handler(request: httpx.Request) -> httpx.Response:
        created = (NOW + timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
        return httpx.Response(200, json=[{"id": 4, "body": 'Decision:\n```json\n{"order": 1, "fits_because": "x"}\n```',
                                          "author": {"username": FLOW_ACCOUNT}, "created_at": created, "system": False}])
    http = Http(httpx.Client(transport=httpx.MockTransport(handler)))
    gitlab = GitLab(http, "https://gitlab.example", "123", "test-token")
    ports = GitLabPorts(gitlab, http, flow_consumer_id="77", flow_service_account=FLOW_ACCOUNT,
                        ntfy_url="https://ntfy.example/t", gcp_project="p", gcp_region="r", google_token=GoogleToken(http),
                        memory={"asked": {"7": NOW.isoformat()}})
    note = ports.request_note(7, NOW + timedelta(minutes=5))
    assert note is not None and parse_request(note).order == 1


# Standing orders: an apply that raises is seen, tried once more, then paged.

class FlakyPorts(Ports):
    def __init__(self, failures: int):
        super().__init__()
        self.failures = failures

    def apply(self, action, at):
        if self.failures:
            self.failures -= 1
            raise RuntimeError("GitLab set the flag: HTTP 502")
        return super().apply(action, at)


def test_a_standing_apply_that_fails_once_is_tried_again_next_tick(oncall, make_night):
    night, ports = make_night(), FlakyPorts(failures=1)
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 8, 0.079)
    with pytest.raises(RuntimeError):
        watch.tick(metrics, at(oncall, "03:12"))
    incident = watch.incidents[0]
    assert incident.ask is not None and incident.acted is None and incident.paged_at is None
    assert [e.kind for e in night.ledger.events] == ["alert", "failed"]
    assert night.ledger.events[-1].text == "Order 1 could not be carried out (GitLab set the flag: HTTP 502)."
    watch.tick(metrics, at(oncall, "03:13"))
    assert ports.applied == ["new_checkout off in production"] and ports.pages == []
    assert incident.ask is None and incident.acted is not None
    assert [e.kind for e in night.ledger.events] == ["alert", "failed", "acted"]


def test_a_standing_apply_that_keeps_failing_wakes_her_with_the_reason(oncall, make_night):
    night, ports = make_night(), FlakyPorts(failures=5)
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:07", 8, 0.079)
    for minute in ("03:12", "03:13"):
        with pytest.raises(RuntimeError):
            watch.tick(metrics, at(oncall, minute))
    watch.tick(metrics, at(oncall, "03:14"))
    assert ports.applied == []
    assert ports.pages == [("Checkout error rate (new path) at 7.9% since 03:12.",
                            "Order 1 could not be carried out (GitLab set the flag: HTTP 502).",
                            "The incident has the evidence.")]
    assert [e.kind for e in night.ledger.events] == ["alert", "failed", "failed", "woke"]
    assert watch.incidents[0].ask is None


# The re-check judges the incident's other alerts on the last complete minute.

@pytest.mark.parametrize("dip", ["one_low_minute", "missing_minute"])
def test_one_dip_or_one_missing_minute_in_the_other_alert_does_not_hide_it_from_the_re_check(oncall, make_night, dip):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "01:45", 6, 0.204)
    bad_minutes(metrics, oncall, OLD, "01:45", 20, 0.203)
    if dip == "one_low_minute":
        put(metrics, OLD, at(oncall, "01:57"), 0.04)
    else:
        metrics._series[OLD].pop(at(oncall, "01:57"))
    watch.tick(metrics, at(oncall, "01:50"))
    assert ports.applied == ["new_checkout off in production"]
    # the whole shop reads healthy, so the incident's other alert is what the re-check has to catch
    switched_off(metrics, oncall, "01:50", 12, whole_rate=0.004)
    for minute in range(1, 11):
        watch.tick(metrics, at(oncall, "01:50") + timedelta(minutes=minute))
    assert len(ports.pages) == 1
    assert ports.pages[0][0] == ("Order 1 ran at 01:50 but checkout error rate (old path) still 20.3% (limit 5.0%), "
                                 "though the new path carries no checkouts now; checkout error rate (whole shop) "
                                 "back to 0.4% on 60 checkouts (limit 5.0%).")
    assert not any("No page" in n for n in ports.notes)


def test_a_signed_unused_order_on_the_signal_that_still_fails_is_offered_for_one_thumbs_up(oncall, make_night):
    night, ports = make_night(), Ports()
    watch = Watch(night, ports, rules(), standing=True)
    metrics = Metrics()
    bad_minutes(metrics, oncall, NEW, "03:00", 8, 0.079)
    bad_minutes(metrics, oncall, P95, "02:55", 40, 1800.0)
    watch.tick(metrics, at(oncall, "03:07"))
    assert ports.applied == ["new_checkout off in production"]  # order 1 is first in line; an incident acts once
    switched_off(metrics, oncall, "03:07", 12, whole_rate=0.004)
    for minute in range(1, 11):
        watch.tick(metrics, at(oncall, "03:07") + timedelta(minutes=minute))
    assert ports.pages == [(
        "Order 1 ran at 03:07 but p95 latency ms still 1,800 ms (limit 1,500 ms), though the new path carries no "
        "checkouts now; checkout error rate (whole shop) back to 0.4% on 60 checkouts (limit 5.0%).",
        "Order 2 is signed for this but did not run; an incident acts once.",
        "The incident has the evidence.",
        "Thumbs-up the note on #1 to: shop traffic to revision shop-00041.")]
    incident = watch.incidents[0]
    assert incident.suggest == Action(kind="traffic_to_revision", service="shop", revision="shop-00041")


# The countersign can keep a traffic change, refuses what it cannot read, and a refusal does not end the morning.

TRAFFIC = Action(kind="traffic_to_revision", service="shop", revision="shop-00041")
TRAFFIC_WAS = {"kind": "traffic", "service": "shop",
               "traffic": [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}]}


def test_a_services_entry_keeps_a_traffic_change(targets):
    kept = parse_state({"flags": [], "services": [{"service": "shop", "keep": "shop-00041", "until": "the fix ships"}]},
                       targets)
    assert [k.action for k in kept] == [TRAFFIC] and kept[0].until == "the fix ships"
    plan = plan_morning([LooseEnd(TRAFFIC, "order 2, 02:13", TRAFFIC_WAS)], kept)
    assert plan.undo == () and [k.action for k in plan.kept] == [TRAFFIC]


def test_a_services_entry_on_another_revision_or_an_unknown_section_is_refused(targets):
    with pytest.raises(OrdersError) as refused:
        plan_morning([LooseEnd(TRAFFIC, "order 2, 02:13", TRAFFIC_WAS)],
                     parse_state({"services": [{"service": "shop", "keep": "shop-00039", "until": "x"}]}, targets))
    assert refused.value.problems == ["ops/state.yml keeps shop traffic to revision shop-00039, but last night sent "
                                      "it to revision shop-00041"]
    with pytest.raises(OrdersError) as refused:
        parse_state({"flag": [{"flag": "new_checkout", "environment": "production", "keep": "off"}]}, targets)
    assert refused.value.problems == ["ops/state.yml: unknown keys flag (only flags and services are read)"]
    with pytest.raises(OrdersError) as refused:
        parse_state({"services": [{"service": "shop", "keep": "shop-00041"}, {"service": "shop", "keep": "shop-00041"}]},
                    targets)
    assert refused.value.problems == ["ops/state.yml lists shop traffic twice"]
    with pytest.raises(OrdersError) as refused:
        parse_state({"services": [{"service": "shop", "keep": "", "until": "x"}]}, targets)
    assert refused.value.problems == ["ops/state.yml services entry 1: needs a service and keep (the revision that stays)"]


def test_a_refused_countersign_is_said_once_and_a_corrected_file_signed_later_is_applied(demo_night_fixture):
    night = demo_night_fixture
    relay_doc, ports = {}, MorningPorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), watch_issue=5)
    wrong = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "on", "until": "x"}]}
    first = StateFile(wrong, signed(night, "2026-10-21T07:42"))
    for minute in ("07:43", "07:44"):
        step(relay_doc, night, True, first, ports, local(night, f"2026-10-21T{minute}"), watch_issue=5)
    record = relay_doc["dawn"]
    assert record["countersign"] is None and record["refused"]["commit"] == "c0ffee"
    assert ports.restored == [] and ports.applied == []
    refusals = [n for n in ports.notes if "Refused" in n]
    assert len(refusals) == 1 and "but last night set it off" in refusals[0]
    right = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off", "until": "the fix ships"}]}
    corrected = StateFile(right, signed(night, "2026-10-21T07:50"))
    corrected = StateFile(right, type(corrected.signature)(method="merge", user="alex-velazquez",
                                                            at=local(night, "2026-10-21T07:50"), commit="d00d"))
    step(relay_doc, night, True, corrected, ports, local(night, "2026-10-21T07:51"), watch_issue=5)
    assert record["countersign"]["commit"] == "d00d" and record["countersign"]["problems"] == []
    assert [name for name, _before in ports.restored] == ["stock_from_cache on in production"]
    assert ports.notes[-1].startswith("Countersign by Priya at 07:50 (merge), applied by code.")


# The day sheet and the rehearsal pin tonight's date.

def test_the_day_sheet_title_carries_the_local_date_and_time_zone():
    from nightorders.daysheet import render
    sheet = {"date": "2026-10-20", "timezone": "America/Los_Angeles", "written_at": "21:00", "_label": "DEMO.",
             "merged_today": [], "deployments": [], "flags": []}
    text = render(sheet)
    assert text.startswith("## Day sheet for 2026-10-20 (Tue 20 Oct), times in America/Los_Angeles\n")
    assert 'Tonight is 2026-10-20: the orders file says night: "2026-10-20".' in text


def test_the_rehearsal_refuses_a_draft_whose_night_a_signature_now_would_fall_outside_of():
    from test_rehearsal import ORDERS, World, run
    world = World(orders_text=ORDERS.replace('night: "2026-10-20"', 'night: "2026-10-21"'))
    reported, relay_doc = run(world)
    assert reported == ["rehearsed !31 at abc123de"]
    [note] = world.notes
    lines = note["body"].splitlines()
    assert lines[2].startswith("Code refuses this draft, so it cannot be signed now: its night is 2026-10-21, and a signature "
                               "at 21:35 on 20 Oct would fall outside its window (12:00 on 21 Oct to 07:00 on 22 Oct).")
    assert lines[3] == "- The orders were signed outside tonight's window."
    assert not any(r.url.path.endswith("/feature_flags/new_checkout") and r.method == "PUT" for r in world.requests)


# The prompts say what the parsers enforce, so a later edit cannot drift in silence.

def _words(path) -> str:
    """A file's text with every run of whitespace (YAML block line breaks included) as one space."""
    return " ".join(path.read_text().split())


def test_the_flow_prompts_and_the_skill_state_the_contract_the_code_reads():
    watch = _words(REPO / "flows" / "watch.yml")
    skill = _words(REPO / "skills" / "night-orders" / "SKILL.md")
    for text in (watch, skill.replace("`", "")):
        assert "fits_because is one sentence" in text
        assert "declined, page and suggest are null" in text
        assert "exactly two keys" in text and '"action": "flag_set"' in text and '"action": "traffic_to_revision"' in text
        assert "ops/night-orders.yml" in text and "ops/targets.yml" in text
    assert '"get_repository_file"' in watch
    assert "exactly as given, when it is already a fenced code block" in watch
    dusk = _words(REPO / "flows" / "dusk.yml")
    assert "exactly id, because, when and do" in dusk and "YYYY-MM-DD" in dusk
    assert "orders/ followed by the draft's night value" in dusk
    assert "`id` (an integer from 1 to 9" in skill and "copied from the day sheet title" in skill
    dawn = _words(REPO / "flows" / "dawn.yml")
    assert "flags and services" in dawn and "keep is the value the night set" in dawn
    assert "keep is the revision the night sent traffic to" in dawn
    orders_file = (REPO / "ops" / "night-orders.yml").read_text()
    assert "#   - id: 1" in orders_file and load_yaml(REPO / "ops" / "night-orders.yml")["orders"] == []
