"""Fixes from the 11 Oct review in the GitLab, Cloud Run and ntfy ports. Offline, against fake servers.

A page tried again pushes again without a second note; a failed write carries the snapshot it read; a flow the
Flows API refuses says its status; a call the tick had no time for says nothing went out. From the 14 Oct review: a
page note that failed while the push went out is posted on a later tick, so its thumbs-up can still count. From the
15 Oct review: a page note whose post timed out after GitLab created it is found, not posted again.

Every name, token, topic and time here is test data.
"""

from __future__ import annotations

from datetime import timedelta

import httpx
import pytest

from nightorders.gitlab_ports import GitLab, GitLabPorts, GoogleToken, RelayError, flag_snapshot
from nightorders.model import Action
from test_relay_ports import (API, FLAG, NOW, SERVICE, TOKEN_PATH, TOPIC_URL, Server, body, flag, ports_for,
                              reaction)

NOTES = f"{API}/issues/7/notes"
TOPIC = "/test-topic-not-real"
FLOWS = "/api/v4/ai/duo_workflows/workflows"
OFF = Action(kind="flag_set", flag="new_checkout", environment="production", to="off")
TRAFFIC = Action(kind="traffic_to_revision", service="shop", revision="shop-00041")
LINES = ("Checkout failing on both paths since 01:45.", "The incident has the evidence.")


def budget_ports(server: Server, budget: float | None = None) -> GitLabPorts:
    """Ports whose tick has a time budget (0: no time left), with a dawn flow on watch issue #1."""
    http = server.http(budget_seconds=budget)
    return GitLabPorts(GitLab(http, "https://gitlab.example", "123", "test-token"), http, flow_consumer_id="77",
                       flow_service_account="duo-watch", ntfy_url=TOPIC_URL, google_token=GoogleToken(http),
                       dawn_consumer_id="78", watch_issue=1)


# A1: a page that failed is sent again; its note is posted once, and a push that went out counts.

def test_a_page_whose_push_failed_is_pushed_again_without_a_second_note():
    pushes = iter([httpx.Response(503), httpx.Response(200, json={"id": "x"})])
    server = Server({("POST", NOTES): (201, {"id": 555}), ("POST", TOPIC): lambda request: next(pushes)})
    ports = ports_for(server, {"links": {"7": "https://gitlab.example/g/p/-/issues/7"}})
    with pytest.raises(RelayError, match="push to the on-call phone: HTTP 503"):
        ports.page(7, LINES, NOW)
    ports.page(7, LINES, NOW)
    assert len(server.sent("POST", NOTES)) == 1
    first, second = server.sent("POST", TOPIC)
    assert second.content == first.content == "\n".join(LINES).encode()
    assert second.headers["Click"] == "https://gitlab.example/g/p/-/issues/7#note_555"


def test_a_page_whose_note_failed_but_whose_push_went_out_counts_as_sent():
    server = Server({("POST", NOTES): (502, {"message": "Bad gateway"}), ("POST", TOPIC): {"id": "x"}})
    ports = ports_for(server)
    ports.page(7, LINES, NOW)  # she is woken; only the thumbs-up target is missing
    assert len(server.sent("POST", TOPIC)) == 1 and ports.memory.page_notes == {}


def test_a_page_note_that_failed_while_the_push_went_out_is_posted_on_the_next_tick_and_its_thumbs_up_counts():
    # 14 Oct review: the note was dropped, so "Thumbs-up the note on #7" pointed at nothing and nothing said why.
    notes = iter([httpx.Response(502, json={"message": "Bad gateway"}), httpx.Response(201, json={"id": 556})])
    server = Server({("POST", NOTES): lambda request: next(notes), ("POST", TOPIC): {"id": "x"}, ("GET", NOTES): [],
                     ("GET", f"{NOTES}/556/award_emoji"): [reaction("thumbsup", "alex-velazquez", 2)]})
    lines = LINES + ("Thumbs-up the note on #7 to: stock_from_cache on in production.",)
    paged = ports_for(server)
    paged.page(7, lines, NOW)  # she is woken; the note did not post
    later = ports_for(server, paged.saved())  # the next tick starts from the saved memory
    assert later.thumbs_up(7, NOW + timedelta(minutes=1)) == [("alex-velazquez", NOW + timedelta(minutes=2))]
    first, second = server.sent("POST", NOTES)
    assert body(second) == body(first)  # the same note, with the time she was paged in its timeline line
    assert later.memory.page_notes == {7: 556} and later.saved()["unposted"] == {}

    down = Server({("POST", NOTES): (502, {"message": "Bad gateway"}), ("POST", TOPIC): {"id": "x"},
                   ("GET", NOTES): []})
    paged = ports_for(down)
    paged.page(7, lines, NOW)
    with pytest.raises(RelayError, match="GitLab post note: HTTP 502"):  # the tick says why, and tries again
        ports_for(down, paged.saved()).thumbs_up(7, NOW + timedelta(minutes=1))


def test_a_page_note_whose_post_timed_out_after_gitlab_created_it_is_found_and_its_thumbs_up_counts():
    # 15 Oct review: the next tick posted the same note again, and her thumbs-up on the first one was never read.
    created = []

    def post(request):
        created.append({"id": 555 + len(created), "body": body(request)["body"], "system": False})
        if len(created) == 1:
            raise httpx.ReadTimeout("slow", request=request)  # GitLab created note 555; the answer came too late
        return httpx.Response(201, json=created[-1])

    server = Server({("POST", NOTES): post, ("POST", TOPIC): {"id": "x"},
                     ("GET", NOTES): lambda request: [{"id": 554, "body": "An earlier note.", "system": False},
                                                      *created],
                     ("GET", f"{NOTES}/555/award_emoji"): [reaction("thumbsup", "alex-velazquez", 2)],
                     ("GET", f"{NOTES}/556/award_emoji"): []})
    paged = ports_for(server)
    paged.page(7, LINES, NOW)
    later = ports_for(server, paged.saved())
    assert later.thumbs_up(7, NOW + timedelta(minutes=3)) == [("alex-velazquez", NOW + timedelta(minutes=2))]
    assert len(server.sent("POST", NOTES)) == 1 and later.memory.page_notes == {7: 555}
    assert later.saved()["unposted"] == {}


# A3: a write that fails after the target was read carries that snapshot; a read that fails carries none.

def test_a_flag_write_that_times_out_carries_the_snapshot_it_read():
    current = flag(True, (11, "default", [(21, "production")]))

    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    server = Server({("GET", FLAG): current, ("PUT", FLAG): slow})
    with pytest.raises(RelayError, match="GitLab set flag new_checkout: no answer within 10 s") as error:
        ports_for(server).apply(OFF, NOW)
    assert error.value.before == flag_snapshot(current, "new_checkout", "production")


def test_a_flag_write_gitlab_does_not_confirm_carries_the_snapshot_it_read():
    current = flag(True, (11, "default", [(21, "production")]))
    server = Server({("GET", FLAG): current, ("PUT", FLAG): current})
    with pytest.raises(RelayError, match="did not report it off") as error:
        ports_for(server).apply(OFF, NOW)
    assert error.value.before == flag_snapshot(current, "new_checkout", "production")


def test_a_flag_write_with_an_answer_that_is_not_a_flag_carries_the_snapshot_it_read():
    current = flag(True, (11, "default", [(21, "production")]))
    server = Server({("GET", FLAG): current, ("PUT", FLAG): ["not", "a", "flag"]})
    with pytest.raises(RelayError, match="GitLab set flag new_checkout: unexpected answer") as error:
        ports_for(server).apply(OFF, NOW)
    assert error.value.before == flag_snapshot(current, "new_checkout", "production")


def test_a_flag_read_that_fails_carries_no_snapshot():
    server = Server({("GET", FLAG): (502, {"message": "Bad gateway"})})
    with pytest.raises(RelayError, match="GitLab read flag new_checkout: HTTP 502") as error:
        ports_for(server).apply(OFF, NOW)
    assert getattr(error.value, "before", None) is None
    assert server.sent("PUT", FLAG) == []


def test_a_traffic_write_that_fails_carries_the_allocation_it_read():
    latest = [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}]
    server = Server({("GET", TOKEN_PATH): {"access_token": "t"}, ("GET", SERVICE): {"template": {}, "traffic": latest},
                     ("PATCH", SERVICE): (503, {"error": {"code": 503, "message": "Try again."}})})
    with pytest.raises(RelayError, match="Cloud Run send shop traffic: HTTP 503") as error:
        ports_for(server).apply(TRAFFIC, NOW)
    assert error.value.before == {"kind": "traffic", "service": "shop", "traffic": latest}


# A11 and C3: the Flows API that refuses, and a call the tick had no time for.

def test_a_watch_flow_the_flows_api_refuses_says_its_status_and_forgets_the_ask():
    server = Server({("POST", FLOWS): (403, {"message": "403 Forbidden"})})
    ports = ports_for(server)
    with pytest.raises(RelayError, match=r"GitLab start the watch flow: HTTP 403 \(403 Forbidden\)") as error:
        ports.start_watch_flow(7, "Incident #7.", NOW)
    assert error.value.status == 403 and ports.memory.asked == {}


def test_a_watch_flow_start_that_timed_out_keeps_the_ask():
    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    ports = ports_for(Server({("POST", FLOWS): slow}))
    with pytest.raises(RelayError, match="no answer within 10 s") as error:
        ports.start_watch_flow(7, "Incident #7.", NOW)
    assert getattr(error.value, "status", None) is None and getattr(error.value, "sent", True) is True
    assert ports.memory.asked == {7: NOW}  # the flow may have started: its answer still counts


def test_a_watch_flow_the_tick_had_no_time_for_was_not_sent_and_is_not_waited_for():
    server = Server({("POST", FLOWS): (201, {"id": 1})})
    ports = budget_ports(server, budget=0)
    with pytest.raises(RelayError, match="skipped, the tick ran out of time") as error:
        ports.start_watch_flow(7, "Incident #7.", NOW)
    assert error.value.sent is False and ports.memory.asked == {} and server.requests == []


def test_the_dawn_flow_says_when_it_was_not_sent_or_was_refused():
    server = Server({("POST", FLOWS): (201, {"id": 2})})
    with pytest.raises(RelayError, match="skipped") as error:
        budget_ports(server, budget=0).start_dawn_flow("Watch issue #1.", NOW)
    assert error.value.sent is False and server.requests == []
    server = Server({("POST", FLOWS): (404, {"message": "404 Not found"})})
    with pytest.raises(RelayError, match=r"GitLab start the dawn flow: HTTP 404") as error:
        budget_ports(server).start_dawn_flow("Watch issue #1.", NOW)
    assert error.value.status == 404 and body(server.requests[0])["issue_id"] == 1
