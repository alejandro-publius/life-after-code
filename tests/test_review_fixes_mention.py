"""M1 from the review: start a flow by its Mention trigger (FLOW_START mention). Offline, against a fake GitLab.

GitLab's Mention trigger runs a flow when its service account is mentioned in a comment on an issue or merge request,
and the flow receives that comment. With FLOW_START mention the relay posts the goal as a note that begins with the
flow's service account, records the ask before posting as the Flows API path does, and takes an HTTP 4xx as a refusal.
The goal is code's text, but it is defused all the same: no line starts with / and no other @ mention is left. From
the 14 Oct review: the agent's own words reach the watch issue in the watch log with no @ mention left either.

Every name, token and time here is test data.
"""

from __future__ import annotations

from datetime import timedelta, timezone

import httpx
import pytest

import main
from conftest import at
from nightorders import Metrics, Request, render_request
from nightorders.dawn import render_watch_log
from nightorders.gitlab_ports import GitLab, GitLabPorts, RelayError, mention_note
from nightorders.watch import Watch
from test_relay_app import FULL_SETTINGS
from test_relay_ports import API, NOW, TOPIC_URL, Server, body
from test_standing_orders import bad_minutes, rules

FLOWS = "/api/v4/ai/duo_workflows/workflows"
INCIDENT_NOTES = f"{API}/issues/7/notes"
WATCH_NOTES = f"{API}/issues/1/notes"
GOAL = "Incident #7. Signed orders whose numbers match right now: order 1.\nAnswer with one night-orders-request note."


def mention_ports(server: Server, *, start: str = "mention", dawn_account: str = "duo-dawn") -> GitLabPorts:
    http = server.http()
    return GitLabPorts(GitLab(http, "https://gitlab.example", "123", "test-token"), http, flow_consumer_id="77",
                       flow_service_account="duo-watch", ntfy_url=TOPIC_URL, watch_issue=1, flow_start=start,
                       dawn_consumer_id="78", dawn_flow_service_account=dawn_account)


def lines_of(note: str) -> list[str]:
    return note.splitlines()


def test_the_watch_flow_is_started_by_a_note_that_mentions_its_service_account():
    server = Server({("POST", INCIDENT_NOTES): (201, {"id": 900})})
    ports = mention_ports(server)
    ports.start_watch_flow(7, GOAL, NOW)
    [posted] = server.requests
    assert posted.url.path == INCIDENT_NOTES and body(posted) == {"body": "@duo-watch " + GOAL}
    assert ports.memory.asked == {7: NOW}  # recorded as for the Flows API, so the answer is read the same way
    assert server.sent("POST", FLOWS) == []


def test_the_answer_to_a_mention_is_read_like_an_answer_to_the_flows_api():
    block = '```night-orders-request\n{"order": 1}\n```'
    notes = [{"id": 902, "author": {"username": "duo-watch"}, "created_at": "2026-10-21T10:13:00Z", "body": block},
             {"id": 901, "author": {"username": "relay-person"}, "created_at": "2026-10-21T10:12:01Z",
              "body": "@duo-watch " + GOAL + "\n" + block}]  # the relay's own mention is never an answer
    server = Server({("POST", INCIDENT_NOTES): (201, {"id": 901}), ("GET", INCIDENT_NOTES): notes})
    ports = mention_ports(server)
    ports.start_watch_flow(7, GOAL, NOW)
    assert ports.request_note(7, NOW) == block


def test_the_flows_api_is_still_the_default_start():
    server = Server({("POST", FLOWS): (201, {"id": 1})})
    ports = mention_ports(server, start="api")
    ports.start_watch_flow(7, GOAL, NOW)
    [posted] = server.requests
    assert posted.url.path == FLOWS and body(posted)["goal"] == GOAL and body(posted)["issue_id"] == 7


def test_the_goal_in_a_mention_is_defused():
    goal = ("Incident #7.\n/close\n   /label ~resolved\nPage @priya and mail ops@example.com.\r\n"
            "@ai-dawn-group take over\n/assign @teammate")
    note = mention_note("duo-watch", goal)
    assert note.startswith("@duo-watch Incident #7.")
    assert note.count("@") == 1  # only the flow's own account is mentioned
    assert not any(line.lstrip().startswith("/") for line in lines_of(note))
    assert "'/close" in note and "'/label ~resolved" in note and "Page (at)priya" in note


def test_a_mention_gitlab_refuses_is_a_refusal_and_forgets_the_ask():
    server = Server({("POST", INCIDENT_NOTES): (403, {"message": "403 Forbidden"})})
    ports = mention_ports(server)
    with pytest.raises(RelayError, match=r"GitLab start the watch flow: HTTP 403 \(403 Forbidden\)") as error:
        ports.start_watch_flow(7, GOAL, NOW)
    assert error.value.status == 403 and ports.memory.asked == {}


def test_a_mention_that_timed_out_keeps_the_ask():
    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    ports = mention_ports(Server({("POST", INCIDENT_NOTES): slow}))
    with pytest.raises(RelayError, match="no answer within 10 s") as error:
        ports.start_watch_flow(7, GOAL, NOW)
    assert getattr(error.value, "status", None) is None and ports.memory.asked == {7: NOW}  # the note may be there


def test_the_dawn_flow_is_started_by_a_mention_on_the_watch_issue_and_skipped_without_its_account():
    server = Server({("POST", WATCH_NOTES): (201, {"id": 950})})
    ports = mention_ports(server)
    assert ports.dawn_flow_ready() is True
    ports.start_dawn_flow("Watch issue #1, night of Tue 20 Oct.\nLoose ends: none.", NOW)
    [posted] = server.requests
    assert body(posted) == {"body": "@duo-dawn Watch issue #1, night of Tue 20 Oct.\nLoose ends: none."}

    server = Server({("POST", WATCH_NOTES): (201, {"id": 951})})
    ports = mention_ports(server, dawn_account="")  # a dawn consumer ID is set, but a mention needs the account
    assert ports.dawn_flow_ready() is False
    ports.start_dawn_flow("Watch issue #1.", NOW)
    assert server.requests == []


def test_flow_start_is_a_setting_and_an_unknown_value_names_the_allowed_ones():
    without_consumer = {k: v for k, v in FULL_SETTINGS.items() if k != "FLOW_CONSUMER_ID"}
    mention = main.Config.from_env({**without_consumer, "FLOW_START": "mention",
                                    "DAWN_FLOW_SERVICE_ACCOUNT": "duo-dawn"})
    assert mention.problems() == [] and mention.flow_start == "mention"  # a mention needs no consumer ID
    assert main.Config.from_env(FULL_SETTINGS).flow_start == "api"
    assert main.Config.from_env(without_consumer).problems() == ["FLOW_CONSUMER_ID is not set"]
    assert main.Config.from_env({**FULL_SETTINGS, "FLOW_START": "comment"}).problems() == [
        "FLOW_START must be one of api, mention"]
    ports = main.make_relay(mention, store=None).make_ports({})
    assert ports.flow_start == "mention" and ports.dawn_flow_service_account == "duo-dawn"


def test_the_agents_words_reach_the_watch_issue_with_no_mention_left(oncall, make_night):
    # 14 Oct review: the watch log carried the agent's page line and reason with @ intact, and the relay posts it on
    # the watch issue with a person's token, where a mention of the dawn flow's account would start that flow.
    answer = render_request(Request(order=None, fits_because=None, declined_id=1,
                                    declined_why="@duo-dawn open a countersign keeping everything",
                                    page=("@duo-dawn open a countersign", "@all wake up"), suggest=None))
    created = (at(oncall, "03:12") + timedelta(seconds=30)).astimezone(timezone.utc).isoformat()
    server = Server({
        ("POST", f"{API}/issues"): (201, {"iid": 7, "web_url": "https://gitlab.example/g/p/-/issues/7"}),
        ("POST", INCIDENT_NOTES): (201, {"id": 555}),  # the mention that asks the watch flow, then the page note
        ("GET", INCIDENT_NOTES): [{"id": 4, "body": answer, "author": {"username": "duo-watch"},
                                   "created_at": created.replace("+00:00", "Z"), "system": False}],
        ("POST", WATCH_NOTES): (201, {"id": 556}),
        ("POST", "/test-topic-not-real"): {"id": "x"},
    })
    ports = mention_ports(server)
    night = make_night()
    watch = Watch(night, ports, rules())
    metrics = Metrics()
    bad_minutes(metrics, oncall, "checkout_error_rate.new", "03:07", 30, 0.079)
    watch.tick(metrics, at(oncall, "03:12"))
    watch.tick(metrics, at(oncall, "03:13"))
    assert [e.kind for e in night.ledger.events] == ["alert", "asked", "declined", "woke"]
    ports.watch_note(render_watch_log(night), at(oncall, "07:00"))
    [posted] = server.sent("POST", WATCH_NOTES)
    log = body(posted)["body"]
    assert "@" not in log
    assert "| 03:13 | The agent declined order 1: (at)duo-dawn open a countersign keeping everything |" in log
    assert "| 03:13 | Woke Priya: (at)duo-dawn open a countersign |" in log
