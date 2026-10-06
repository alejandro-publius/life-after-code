"""The relay's GitLab, Cloud Run and ntfy ports, against fake servers (httpx.MockTransport). Offline.

Every name, token, topic and time here is test data.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from nightorders.gitlab_ports import GitLab, GitLabPorts, GoogleToken, Http, RelayError, flag_changes
from nightorders.model import Action

TOKEN = "fake-token-not-real"
TOPIC_URL = "https://ntfy.example/test-topic-not-real"
FLOW_ACCOUNT = "duo-watch-night-orders"
NOW = datetime(2026, 10, 21, 10, 12, tzinfo=timezone.utc)  # 03:12 in Los Angeles


class Server:
    """A fake for GitLab, Google and ntfy. Answers by (method, path) and records every request."""

    def __init__(self, routes: dict | None = None):
        self.routes = dict(routes or {})
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        answer = self.routes.get((request.method, request.url.path))
        if callable(answer):
            answer = answer(request)
        if answer is None:
            return httpx.Response(404, json={"message": "404 Not Found"})
        if isinstance(answer, httpx.Response):
            return answer
        status, body = answer if isinstance(answer, tuple) else (200, answer)
        if isinstance(body, str):
            return httpx.Response(status, text=body)
        return httpx.Response(status, json=body)

    def http(self, **kwargs) -> Http:
        return Http(httpx.Client(transport=httpx.MockTransport(self)), **kwargs)

    def sent(self, method: str, path: str) -> list[httpx.Request]:
        return [r for r in self.requests if r.method == method and r.url.path == path]


def body(request: httpx.Request):
    return json.loads(request.content)


def ports_for(server: Server, memory: dict | None = None) -> GitLabPorts:
    http = server.http()
    gitlab = GitLab(http, "https://gitlab.example", "123", TOKEN)
    return GitLabPorts(gitlab, http, flow_consumer_id="77", flow_service_account=FLOW_ACCOUNT, ntfy_url=TOPIC_URL,
                       gcp_project="demo-project", gcp_region="us-central1", google_token=GoogleToken(http),
                       memory=memory)


API = "/api/v4/projects/123"


# Incidents and notes.

def test_open_incident_creates_an_incident_with_the_evidence_pack():
    server = Server({("POST", f"{API}/issues"): (201, {"iid": 7, "web_url": "https://gitlab.example/g/p/-/issues/7"})})
    ports = ports_for(server)
    assert ports.open_incident("Night watch: checkout errors", "Evidence pack (written by code).", NOW) == 7
    [request] = server.requests
    assert body(request) == {"title": "Night watch: checkout errors", "description": "Evidence pack (written by code).",
                             "issue_type": "incident"}
    assert request.headers["PRIVATE-TOKEN"] == TOKEN
    assert ports.saved()["links"] == {"7": "https://gitlab.example/g/p/-/issues/7"}


def test_close_incident_posts_the_note_then_closes():
    server = Server({("POST", f"{API}/issues/7/notes"): (201, {"id": 900}),
                     ("PUT", f"{API}/issues/7"): {"iid": 7, "state": "closed"}})
    ports_for(server).close_incident(7, "Signals back to normal at 03:40.", NOW)
    note, close = server.requests
    assert (note.method, note.url.path, body(note)) == ("POST", f"{API}/issues/7/notes",
                                                         {"body": "Signals back to normal at 03:40."})
    assert (close.method, close.url.path, body(close)) == ("PUT", f"{API}/issues/7", {"state_event": "close"})


# The watch flow.

def test_start_watch_flow_sends_the_flows_api_body_and_records_the_ask():
    server = Server({("POST", "/api/v4/ai/duo_workflows/workflows"): (201, {"id": 1, "status": "running"})})
    ports = ports_for(server)
    ports.start_watch_flow(7, "Incident #7. Signed orders whose numbers match right now: order 1.", NOW)
    [request] = server.requests
    assert body(request) == {
        "project_id": "123",
        "ai_catalog_item_consumer_id": 77,
        "goal": "Incident #7. Signed orders whose numbers match right now: order 1.",
        "issue_id": 7,
        "start_workflow": True,
        "allow_agent_to_request_user": False,
        "agent_privileges": [2, 3],
        "pre_approved_agent_privileges": [2, 3],
    }
    assert ports.memory.asked == {7: NOW}


def note(note_id: int, author: str, minutes: float, text: str, system: bool = False) -> dict:
    created = (NOW + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")
    return {"id": note_id, "body": text, "author": {"username": author}, "created_at": created, "system": system}


BLOCK = '```night-orders-request\n{"order": %d, "fits_because": "new path only"}\n```'


def test_request_note_is_the_newest_flow_note_after_the_ask_with_a_request_block():
    notes = [  # newest first, as GitLab sorts them
        note(6, "teammate", 4, BLOCK % 2),                  # someone else: never an answer
        note(5, FLOW_ACCOUNT, 3, "Still looking at the diff."),  # the flow, but no request block
        note(4, FLOW_ACCOUNT, 2, BLOCK % 1),                # the answer
        note(3, FLOW_ACCOUNT, 1, BLOCK % 9),                # an older answer
        note(2, FLOW_ACCOUNT, 2.5, BLOCK % 8, system=True), # a system note
        note(1, FLOW_ACCOUNT, -5, BLOCK % 7),               # before the ask
    ]
    server = Server({("GET", f"{API}/issues/7/notes"): notes})
    ports = ports_for(server, {"asked": {"7": NOW.isoformat()}})
    assert ports.request_note(7, NOW + timedelta(minutes=5)) == BLOCK % 1
    [request] = server.requests
    assert request.url.params["sort"] == "desc" and request.url.params["order_by"] == "created_at"


def test_request_note_waits_when_there_is_no_answer_and_never_reads_an_unasked_incident():
    server = Server({("GET", f"{API}/issues/7/notes"): [note(5, "teammate", 1, BLOCK % 1)]})
    ports = ports_for(server, {"asked": {"7": NOW.isoformat()}})
    assert ports.request_note(7, NOW) is None
    assert ports.request_note(8, NOW) is None
    assert len(server.requests) == 1


# Feature flags: one environment's scope changes, and nothing else.

FLAG = f"{API}/feature_flags/new_checkout"


def flag(active: bool, *strategies: tuple[int, str, list[tuple[int, str]]]) -> dict:
    return {"name": "new_checkout", "active": active, "version": "new_version_flag", "strategies": [
        {"id": sid, "name": name, "parameters": {}, "scopes": [{"id": i, "environment_scope": e} for i, e in scopes]}
        for sid, name, scopes in strategies]}


def test_flag_off_in_production_removes_only_the_production_scope():
    before = flag(True, (11, "default", [(21, "production"), (22, "staging")]))
    after = flag(True, (11, "default", [(22, "staging")]))
    server = Server({("GET", FLAG): before, ("PUT", FLAG): after})
    ports_for(server).apply(Action(kind="flag_set", flag="new_checkout", environment="production", to="off"), NOW)
    [put] = server.sent("PUT", FLAG)
    assert body(put) == {"strategies": [{"id": 11, "scopes": [{"id": 21, "_destroy": True}]}]}
    assert put.headers["PRIVATE-TOKEN"] == TOKEN


def test_flag_off_removes_a_strategy_whose_only_scope_is_that_environment():
    before = flag(True, (11, "default", [(21, "production")]), (12, "default", [(22, "staging")]))
    assert flag_changes(before, "production", "off") == {"strategies": [{"id": 11, "_destroy": True}]}


def test_flag_on_in_production_adds_a_default_strategy_for_production_only():
    before = flag(True, (12, "default", [(23, "staging")]))
    after = flag(True, (12, "default", [(23, "staging")]), (13, "default", [(24, "production")]))
    server = Server({("GET", FLAG): before, ("PUT", FLAG): after})
    ports_for(server).apply(Action(kind="flag_set", flag="new_checkout", environment="production", to="on"), NOW)
    [put] = server.sent("PUT", FLAG)
    assert body(put) == {"strategies": [{"name": "default", "parameters": {},
                                         "scopes": [{"environment_scope": "production"}]}]}


def test_flag_already_in_the_wanted_state_is_left_alone():
    server = Server({("GET", FLAG): flag(True, (11, "default", [(21, "production")]))})
    ports_for(server).apply(Action(kind="flag_set", flag="new_checkout", environment="production", to="on"), NOW)
    assert server.sent("PUT", FLAG) == []
    assert flag_changes(flag(False, (11, "default", [(21, "production")])), "production", "off") is None


def test_flag_change_that_would_reach_other_environments_is_refused():
    everywhere = flag(True, (11, "default", [(21, "*")]))
    with pytest.raises(RelayError, match="cannot be turned off in production alone"):
        flag_changes(everywhere, "production", "off")
    inactive = flag(False, (11, "default", [(22, "staging")]))
    with pytest.raises(RelayError, match="would also turn it on for staging"):
        flag_changes(inactive, "production", "on")
    assert flag_changes(flag(False), "production", "on")["active"] is True


def test_flag_change_that_gitlab_does_not_confirm_is_an_error():
    before = flag(True, (11, "default", [(21, "production")]))
    server = Server({("GET", FLAG): before, ("PUT", FLAG): before})
    with pytest.raises(RelayError, match="did not report it off"):
        ports_for(server).apply(Action(kind="flag_set", flag="new_checkout", environment="production", to="off"), NOW)


# Cloud Run traffic.

SERVICE = "/v2/projects/demo-project/locations/us-central1/services/shop"
TOKEN_PATH = "/computeMetadata/v1/instance/service-accounts/default/token"


def test_traffic_to_revision_sends_all_traffic_to_the_named_revision():
    current = {
        "name": "projects/demo-project/locations/us-central1/services/shop",
        "uid": "abc", "generation": "5", "etag": "etag-5", "ingress": "INGRESS_TRAFFIC_ALL",
        "invokerIamDisabled": True, "conditions": [{"type": "Ready"}], "latestReadyRevision": "shop-00042",
        "template": {"containers": [{"image": "example/shop@sha256:1"}]},
        "traffic": [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}],
    }
    server = Server({("GET", TOKEN_PATH): {"access_token": "test-google-token", "expires_in": 3599},
                     ("GET", SERVICE): current,
                     ("PATCH", SERVICE): {"name": "projects/demo-project/locations/us-central1/operations/1"}})
    ports_for(server).apply(Action(kind="traffic_to_revision", service="shop", revision="shop-00041"), NOW)
    [token] = server.sent("GET", TOKEN_PATH)
    assert token.url.host == "metadata.google.internal" and token.headers["Metadata-Flavor"] == "Google"
    [patch] = server.sent("PATCH", SERVICE)
    assert patch.url.host == "run.googleapis.com" and patch.url.params["updateMask"] == "traffic"
    sent = body(patch)
    assert sent["traffic"] == [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": "shop-00041",
                                "percent": 100}]
    assert sent["template"] == current["template"] and sent["etag"] == "etag-5" and sent["invokerIamDisabled"]
    assert not {"uid", "generation", "conditions", "latestReadyRevision"} & set(sent)
    assert patch.headers["Authorization"] == "Bearer test-google-token"
    assert all("PRIVATE-TOKEN" not in r.headers for r in server.requests)


def test_traffic_change_that_google_refuses_is_an_error():
    server = Server({("GET", TOKEN_PATH): {"access_token": "t"}, ("GET", SERVICE): {"template": {}},
                     ("PATCH", SERVICE): (403, {"error": {"code": 403, "message": "Permission denied on shop."}})})
    with pytest.raises(RelayError, match=r"Cloud Run send shop traffic: HTTP 403 \(Permission denied on shop.\)"):
        ports_for(server).apply(Action(kind="traffic_to_revision", service="shop", revision="shop-00041"), NOW)


# Pages and the thumbs-up.

def test_page_pushes_to_ntfy_and_posts_the_page_note_for_the_thumbs_up():
    server = Server({("POST", f"{API}/issues/7/notes"): (201, {"id": 555}),
                     ("POST", "/test-topic-not-real"): {"id": "x"}})
    ports = ports_for(server, {"links": {"7": "https://gitlab.example/g/p/-/issues/7"}})
    lines = ("Checkout failing on both paths since 01:45.", "Not the `new` checkout.",
             "Thumbs-up the note on #7 to: stock_from_cache on in production.")
    ports.page(7, lines, NOW)
    [posted] = server.sent("POST", f"{API}/issues/7/notes")
    assert body(posted)["body"] == ("Page sent to the on-call person:\n\n```text\n" + lines[0] + "\n"
                                    "Not the 'new' checkout.\n" + lines[2] + "\n```")
    [pushed] = server.sent("POST", "/test-topic-not-real")
    assert str(pushed.url) == TOPIC_URL
    assert pushed.content.decode() == "\n".join(lines)
    assert pushed.headers["Title"] == "Night Orders: incident #7" and pushed.headers["Priority"] == "urgent"
    assert pushed.headers["Click"] == "https://gitlab.example/g/p/-/issues/7#note_555"
    assert "PRIVATE-TOKEN" not in pushed.headers
    assert ports.memory.page_notes == {7: 555}


def test_page_still_pushes_when_the_note_fails_and_then_reports_the_failure():
    server = Server({("POST", f"{API}/issues/7/notes"): (502, {"message": "Bad gateway"}),
                     ("POST", "/test-topic-not-real"): {"id": "x"}})
    with pytest.raises(RelayError, match="GitLab post note: HTTP 502") as error:
        ports_for(server).page(7, ("Wake up.",), NOW)
    assert server.sent("POST", "/test-topic-not-real")
    assert TOKEN not in str(error.value) and "test-topic" not in str(error.value)


def reaction(name: str, user: str, minutes: int) -> dict:
    return {"name": name, "user": {"username": user},
            "created_at": (NOW + timedelta(minutes=minutes)).isoformat().replace("+00:00", ".000Z")}


def test_thumbs_up_lists_every_thumbsup_on_the_page_note_oldest_first():
    reactions = [reaction("rocket", "alex-velazquez", 1), reaction("thumbsup", "teammate", 3),
                 reaction("thumbsup_tone2", "alex-velazquez", 2)]
    server = Server({("GET", f"{API}/issues/7/notes/555/award_emoji"): reactions})
    ports = ports_for(server, {"page_notes": {"7": 555}})
    assert ports.thumbs_up(7, NOW) == [("alex-velazquez", NOW + timedelta(minutes=2)),
                                       ("teammate", NOW + timedelta(minutes=3))]


def test_no_thumbs_up_without_a_page_note_or_a_thumbsup():
    server = Server({("GET", f"{API}/issues/7/notes/555/award_emoji"): [reaction("eyes", "alex-velazquez", 1)]})
    ports = ports_for(server, {"page_notes": {"7": 555}})
    assert ports.thumbs_up(7, NOW) == []
    assert ports.thumbs_up(8, NOW) == []
    assert len(server.requests) == 1


# Errors and time limits.

def test_errors_never_carry_the_token_or_the_push_topic():
    server = Server({("POST", "/test-topic-not-real"): (403, {"error": "forbidden test-topic-not-real"}),
                     ("POST", f"{API}/issues/7/notes"): (401, {"message": "401 Unauthorized"})})
    ports = ports_for(server)
    with pytest.raises(RelayError) as pushed:
        ports.page(7, ("Wake up.",), NOW)
    text = str(pushed.value)
    assert "HTTP 401 (401 Unauthorized)" in text and "push to the on-call phone: HTTP 403" in text
    assert TOKEN not in text and "test-topic" not in text and "ntfy.example" not in text


def test_a_slow_server_and_a_spent_budget_stop_the_call():
    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    server = Server({("GET", f"{API}/issues/7/notes"): slow})
    ports = ports_for(server, {"asked": {"7": NOW.isoformat()}})
    with pytest.raises(RelayError, match="GitLab read notes: no answer within 10 s"):
        ports.request_note(7, NOW)
    spent = server.http(budget_seconds=0)
    with pytest.raises(RelayError, match="ran out of time"):
        spent.call("anything", "GET", "https://gitlab.example/api/v4/projects/123")
    assert len(server.requests) == 1


def test_raw_file_paths_are_url_encoded_and_a_missing_file_is_none():
    server = Server({("GET", f"{API}/repository/files/ops/oncall.yml/raw"): "user: alex-velazquez\n"})
    gitlab = GitLab(server.http(), "https://gitlab.example/", "123", TOKEN)
    assert gitlab.raw_file("ops/oncall.yml", "main") == "user: alex-velazquez\n"
    assert gitlab.raw_file("ops/night-orders.yml", "main") is None
    first = server.requests[0]
    assert b"/repository/files/ops%2Foncall.yml/raw?ref=main" in first.url.raw_path
