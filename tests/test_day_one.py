"""The day-one test script against a fake GitLab (httpx.MockTransport). Offline, no real sleeping.

Every name, token, id and time here is test data.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import day_one  # noqa: E402
from nightorders.gitlab_ports import RelayError  # noqa: E402

TOKEN = "fake-day-one-token-not-real"
NOW = datetime(2026, 10, 12, 15, 0, 0, tzinfo=timezone.utc)
API = "/api/v4/projects/123"
PILOT_IDS = "pilot-01,pilot-02,pilot-03,pilot-04,pilot-05,pilot-06,pilot-07,pilot-08,pilot-09,pilot-10"
PROJECT = {
    "id": 123, "path_with_namespace": "g/sub/p", "visibility": "public", "default_branch": "main",
    "permissions": {"project_access": None, "group_access": {"access_level": 30}},
    "duo_remote_flows_enabled": True, "license_url": "https://gitlab.example/g/sub/p/-/blob/main/LICENSE",
    "license": {"key": "mit", "name": "MIT License"},
}
ME = {"id": 10, "username": "alex-velazquez", "name": "Alex Velazquez", "state": "active"}


class Server:
    """A fake GitLab. Answers by (method, path); an answer may be a callable of the request, for state."""

    def __init__(self, routes: dict | None = None, fallback=None):
        self.routes = dict(routes or {})
        self.fallback = fallback
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        answer = self.routes.get((request.method, request.url.path), self.fallback)
        if callable(answer):
            answer = answer(request)
        if answer is None:
            return httpx.Response(404, json={"message": "404 Not Found"})
        status, body = answer if isinstance(answer, tuple) else (200, answer)
        if isinstance(body, str):
            return httpx.Response(status, text=body)
        return httpx.Response(status, json=body)

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self))

    def sent(self, method: str, path: str) -> list[httpx.Request]:
        return [r for r in self.requests if r.method == method and r.url.path == path]


class Clock:
    """A clock that only moves when the script sleeps."""

    def __init__(self):
        self.seconds = 1000.0
        self.slept: list[float] = []

    def __call__(self) -> float:
        return self.seconds

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.seconds += seconds


def body(request: httpx.Request):
    return json.loads(request.content)


def run(server: Server, *args: str, token: str = TOKEN, clock: Clock | None = None, ask=None, out_json: Path | None = None):
    """main() with the fake server, an injected clock and the token in the environment. Returns (code, text, json)."""
    clock = clock or Clock()
    out = io.StringIO()
    argv = ["--project", "123", "--base-url", "https://gitlab.example", *args]
    if out_json is not None:
        argv += ["--out", str(out_json)]
    env = {"GITLAB_TOKEN": token} if token else {}
    code = day_one.main(argv, env=env, out=out, client=server.client(), now=lambda: NOW, clock=clock,
                        sleep=clock.sleep, ask=ask)
    data = json.loads(out_json.read_text()) if out_json is not None and out_json.exists() else None
    return code, out.getvalue(), data


# whoami.

def test_whoami_reads_the_role_the_default_branch_and_the_merge_rights(tmp_path):
    server = Server({
        ("GET", "/api/v4/user"): ME,
        ("GET", API): PROJECT,
        ("GET", f"{API}/members/all/10"): {"access_level": 30, "member_role": {"id": 5, "name": "AI member"}},
        ("GET", f"{API}/protected_branches/main"): {"name": "main", "push_access_levels": [{"access_level": 40}],
                                                    "merge_access_levels": [{"access_level": 40}]},
    })
    code, text, data = run(server, "--step", "whoami", out_json=tmp_path / "r.json")
    assert code == 0 and "whoami: PASS" in text
    assert "user alex-velazquez (id 10" in text
    assert "project g/sub/p (id 123), visibility public, our role Developer" in text
    assert "custom role AI member (id 5) on top of Developer" in text
    assert "default branch main: protected (merge allowed for Maintainer)" in text
    assert "push to main as Developer: not allowed" in text
    assert "merge into main as Developer: not allowed (the signature would be an approval)" in text
    assert data["values"]["CAN_MERGE_DEFAULT"] is False and data["values"]["ROLE"] == "Developer"
    assert data["values"]["DEFAULT_BRANCH_PROTECTED"] is True and data["failed"] is False
    assert server.sent("GET", "/api/v4/user")[0].headers["PRIVATE-TOKEN"] == TOKEN
    assert server.sent("GET", API)[0].url.params["license"] == "true"


def test_whoami_with_an_unprotected_branch_and_the_level_rules():
    server = Server({("GET", "/api/v4/user"): ME, ("GET", API): PROJECT,
                     ("GET", f"{API}/members/all/10"): (404, {"message": "404 Not found"})})
    code, text, _ = run(server, "--step", "whoami")
    assert code == 0 and "default branch main: not protected" in text and "merge into main as Developer: allowed" in text
    assert day_one.level_allows([{"access_level": 30}], 30, 10) is True
    assert day_one.level_allows([{"access_level": 40}], 30, 10) is False
    assert day_one.level_allows([{"access_level": 0}], 50, 10) is False          # No one
    assert day_one.level_allows([{"access_level": 40, "user_id": 10}], 30, 10) is True
    assert day_one.level_allows([{"access_level": 30, "group_id": 7}], 30, 10) is False
    assert day_one.level_allows([{"access_level": 40, "deploy_key_id": 1}], 50, 10) is False  # a key, not a role
    assert day_one.access_level({"permissions": {"project_access": {"access_level": 40}, "group_access": {"access_level": 30}}}) == 40
    assert day_one.access_level({}) == 0


# publish.

def test_publish_prints_the_clicks_when_the_project_is_private_or_has_no_licence():
    private = {**PROJECT, "visibility": "private", "license": None, "license_url": None}
    code, text, _ = run(Server({("GET", API): private}), "--step", "publish")
    assert code == 1 and "publish: FAIL (project is not public; MIT licence not detected)" in text
    assert "Settings > General > Visibility" in text and "push the repository so LICENSE (MIT)" in text
    code, text, _ = run(Server({("GET", API): PROJECT}), "--step", "publish")
    assert code == 0 and "publish: PASS" in text and "licence detected: MIT License" in text


# issue and incident: find before create.

def test_issue_creates_the_watch_issue_from_the_template_once():
    created: list[dict] = []

    def issues(request):
        if request.method == "POST":
            created.append(body(request))
            return 201, {"iid": 3, "web_url": "https://gitlab.example/g/sub/p/-/issues/3"}
        return [{"iid": 3, "title": "Tonight's watch"}] if created else []

    server = Server({("GET", f"{API}/issues"): issues, ("POST", f"{API}/issues"): issues})
    code, text, _ = run(server, "--step", "issue", "--yes")
    assert code == 0 and "created issue #3" in text and "WATCH_ISSUE_IID=3" in text
    [sent] = created
    assert sent["title"] == "Tonight's watch" and sent["labels"] == "night-watch"
    assert sent["description"].startswith("## Tonight's watch") and "/label ~\"night-watch\"" in sent["description"]
    find = server.sent("GET", f"{API}/issues")[0]
    assert find.url.params["in"] == "title" and find.url.params["state"] == "opened" and find.url.params["sort"] == "asc"
    code, text, _ = run(server, "--step", "issue", "--yes")
    assert code == 0 and "found open issue #3" in text and len(created) == 1


def test_incident_and_cleanup_open_and_close_the_probe_incident():
    state = {"open": False}

    def issues(request):
        if request.method == "POST":
            state["open"] = True
            return 201, {"iid": 9, "web_url": "https://gitlab.example/g/sub/p/-/issues/9"}
        return [{"iid": 9, "title": "Day-one probe incident"}] if state["open"] else []

    server = Server({("GET", f"{API}/issues"): issues, ("POST", f"{API}/issues"): issues,
                     ("POST", f"{API}/issues/9/notes"): (201, {"id": 1}), ("PUT", f"{API}/issues/9"): {"state": "closed"}})
    code, text, _ = run(server, "--step", "incident", "--step", "cleanup", "--yes")
    assert code == 0 and "created incident #9" in text and "incident #9 closed" in text
    [posted] = [r for r in server.sent("POST", f"{API}/issues")]
    sent = body(posted)
    assert sent["issue_type"] == "incident" and sent["title"] == "Day-one probe incident"
    assert sent["description"].count("\n") == 2 and "probe ok" in sent["description"] and "demo data" in sent["description"]
    assert server.sent("GET", f"{API}/issues")[0].url.params["issue_type"] == "incident"
    assert body(server.sent("PUT", f"{API}/issues/9")[0]) == {"state_event": "close"}
    assert body(server.sent("POST", f"{API}/issues/9/notes")[0])["body"].startswith("Day-one probe over")


# flags.

def test_flags_create_the_pilot_strategy_and_the_off_flag_then_read_them_back():
    flags: dict[str, dict] = {}

    def create(request):
        sent = body(request)
        stored = dict(sent)
        stored["strategies"] = [{"id": 1, **s, "scopes": [{"id": 11, **sc} for sc in s.get("scopes", [])]}
                                for s in sent.get("strategies", [])]
        flags[sent["name"]] = stored
        return 201, stored

    def read(name):
        return lambda request: flags[name] if name in flags else (404, {"message": "404 Not found"})

    server = Server({
        ("GET", f"{API}/environments"): [{"name": "production"}],
        ("POST", f"{API}/environments"): (201, {"name": "staging"}),
        ("POST", f"{API}/feature_flags"): create,
        ("GET", f"{API}/feature_flags/new_checkout"): read("new_checkout"),
        ("GET", f"{API}/feature_flags/stock_from_cache"): read("stock_from_cache"),
    })
    code, text, _ = run(server, "--step", "flags", "--yes")
    assert code == 0, text
    assert body(server.sent("POST", f"{API}/environments")[0]) == {"name": "staging", "tier": "staging"}
    pilot, off = (body(r) for r in server.sent("POST", f"{API}/feature_flags"))
    assert pilot["name"] == "new_checkout" and pilot["version"] == "new_version_flag" and pilot["active"] is True
    assert pilot["strategies"] == [{"name": "userWithId", "parameters": {"userIds": PILOT_IDS},
                                    "scopes": [{"environment_scope": "production"}]}]
    assert off["name"] == "stock_from_cache" and off["version"] == "new_version_flag" and off["active"] is False
    assert "strategies" not in off
    assert "environment production: exists" in text and "environment staging: created" in text
    assert "flag new_checkout: created" in text and "flag stock_from_cache: created" in text
    assert "read back: new_checkout: active, userWithId (pilot-01..pilot-10) in production" in text
    assert "read back: stock_from_cache: inactive, no strategies" in text
    assert "instance ID from Deploy > Feature flags > Configure" in text
    assert all(r.headers["PRIVATE-TOKEN"] == TOKEN for r in server.requests)


def test_flag_updates_fix_an_existing_flag_and_leave_a_right_one_alone():
    existing = {"name": "new_checkout", "active": False, "strategies": [
        {"id": 1, "name": "default", "parameters": {}, "scopes": [{"id": 11, "environment_scope": "production"},
                                                                  {"id": 12, "environment_scope": "staging"}]},
        {"id": 2, "name": "userWithId", "parameters": {"userIds": "pilot-01"}, "scopes": [{"id": 13, "environment_scope": "production"}]},
    ]}
    assert day_one.pilot_flag_update(existing) == {
        "strategies": [{"id": 1, "scopes": [{"id": 11, "_destroy": True}]}, {"id": 2, "parameters": {"userIds": PILOT_IDS}}],
        "active": True}
    right = {"name": "new_checkout", "active": True, "strategies": [
        {"id": 2, "name": "userWithId", "parameters": {"userIds": PILOT_IDS}, "scopes": [{"id": 13, "environment_scope": "production"}]}]}
    assert day_one.pilot_flag_update(right) is None
    missing = {"name": "new_checkout", "active": True, "strategies": [
        {"id": 3, "name": "default", "parameters": {}, "scopes": [{"id": 14, "environment_scope": "staging"}]}]}
    assert day_one.pilot_flag_update(missing) == {"strategies": [
        {"name": "userWithId", "parameters": {"userIds": PILOT_IDS}, "scopes": [{"environment_scope": "production"}]}]}
    on = {"name": "stock_from_cache", "active": True, "strategies": [{"id": 5, "name": "default", "scopes": []}]}
    assert day_one.off_flag_update(on) == {"strategies": [{"id": 5, "_destroy": True}], "active": False}
    assert day_one.off_flag_update({"name": "stock_from_cache", "active": False, "strategies": []}) is None
    assert day_one.describe_flag(existing) == "new_checkout: inactive, default in production, staging; userWithId (pilot-01) in production"


# catalog.

def graphql_router(answers: dict[str, dict]):
    """Answers a GraphQL request by the first operation name found in its query text."""
    calls: list[dict] = []

    def route(request):
        sent = body(request)
        calls.append(sent)
        for name, answer in answers.items():
            if name in sent["query"]:
                return {"data": answer}
        return {"errors": [{"message": f"no fake for {sent['query'][:40]}"}]}

    route.calls = calls  # type: ignore[attr-defined]
    return route


def test_catalog_lists_the_enabled_flows_and_prints_the_clicks_without_the_probe(tmp_path):
    nodes = [{"id": "gid://gitlab/Ai::Catalog::ItemConsumer/12", "enabled": True,
              "item": {"id": "gid://gitlab/Ai::Catalog::Item/3", "name": "night-watch"},
              "serviceAccount": {"username": "ai-night-watch-g"}}]
    route = graphql_router({"aiCatalogConfiguredItems": {"aiCatalogConfiguredItems": {"nodes": nodes}}})
    server = Server({("GET", API): PROJECT, ("POST", "/api/v4/graphql"): route})
    code, text, data = run(server, "--step", "catalog", "--yes", out_json=tmp_path / "r.json")
    assert code == 0 and "flow night-watch: consumer id 12, service account ai-night-watch-g" in text
    assert "AI > Flows, then New flow" in text and "--create-probe" in text
    assert route.calls[0]["variables"] == {"projectId": "gid://gitlab/Project/123"}
    assert "FLOW_CONSUMER_ID" not in data["values"]
    nodes.append({"id": "gid://gitlab/Ai::Catalog::ItemConsumer/31", "enabled": True,
                  "item": {"id": "gid://gitlab/Ai::Catalog::Item/4", "name": "night-orders-probe"}, "serviceAccount": None})
    code, text, data = run(server, "--step", "catalog", "--yes", out_json=tmp_path / "r2.json")
    assert code == 0 and "flow night-orders-probe: consumer id 31" in text and "New flow" not in text
    assert data["values"]["FLOW_CONSUMER_ID"] == 31


def test_create_probe_sends_the_flow_yaml_then_enables_it_and_reports_a_permission_error():
    route = graphql_router({
        "aiCatalogConfiguredItems": {"aiCatalogConfiguredItems": {"nodes": []}},
        # Another project's item with our name: not ours, so the flow is still created.
        "aiCatalogItems": {"aiCatalogItems": {"nodes": [{"id": "gid://gitlab/Ai::Catalog::Item/2", "name": "night-orders-probe",
                                                         "project": {"id": "gid://gitlab/Project/999"}}]}},
        "aiCatalogFlowCreate": {"aiCatalogFlowCreate": {"item": {"id": "gid://gitlab/Ai::Catalog::Item/9", "name": "night-orders-probe"}, "errors": []}},
        "aiCatalogItemConsumerCreate": {"aiCatalogItemConsumerCreate": {
            "itemConsumer": {"id": "gid://gitlab/Ai::Catalog::ItemConsumer/44", "serviceAccount": {"username": "ai-night-orders-probe-g"}},
            "errors": [], "warnings": ["trigger created without a goal"]}},
    })
    server = Server({("GET", API): PROJECT, ("POST", "/api/v4/graphql"): route})
    code, text, _ = run(server, "--step", "catalog", "--create-probe", "--yes")
    assert code == 0, text
    assert "project { id }" in next(c for c in route.calls if "aiCatalogItems(" in c["query"])["query"]
    create = next(c for c in route.calls if "aiCatalogFlowCreate" in c["query"])["variables"]["input"]
    assert create["definition"] == (Path(__file__).resolve().parents[1] / "flows" / "probe.yml").read_text()
    assert create["projectId"] == "gid://gitlab/Project/123" and create["name"] == "night-orders-probe"
    assert create["release"] is True and create["visibility"] == "PRIVATE"
    enable = next(c for c in route.calls if "aiCatalogItemConsumerCreate" in c["query"])["variables"]["input"]
    assert enable == {"itemId": "gid://gitlab/Ai::Catalog::Item/9", "target": {"projectId": "gid://gitlab/Project/123"},
                      "triggerTypes": ["assign"]}
    assert "enabled night-orders-probe in the project: consumer id 44, service account ai-night-orders-probe-g" in text
    assert "warning from GitLab: trigger created without a goal" in text
    refused = graphql_router({
        "aiCatalogConfiguredItems": {"aiCatalogConfiguredItems": {"nodes": []}},
        "aiCatalogItems": {"aiCatalogItems": {"nodes": []}},
        "aiCatalogFlowCreate": {"aiCatalogFlowCreate": {"item": None, "errors": ["You don't have permission to create flows"]}},
    })
    code, text, _ = run(Server({("GET", API): PROJECT, ("POST", "/api/v4/graphql"): refused}), "--step", "catalog", "--create-probe", "--yes")
    assert code == 1 and "catalog: FAIL (aiCatalogFlowCreate refused: You don't have permission to create flows)" in text


# flow: the Flows API body and the note polling.

def note(note_id: int, author: str, text: str, system: bool = False) -> dict:
    return {"id": note_id, "body": text, "author": {"username": author}, "system": system}


def test_flow_sends_the_flows_api_body_and_waits_for_the_probe_note():
    started = []
    fetches = []

    def notes(request):
        fetches.append(1)
        old = [note(1, "alex-velazquez", "probe ok from an earlier run")]        # there before the start: ignored
        if started and len(fetches) >= 4:
            return [note(2, "ai-night-orders-probe-g", "Probe ok"), *old]
        return old

    def start(request):
        started.append(body(request))
        return 201, {"id": 42, "status": "created", "web_url": "https://gitlab.example/g/sub/p/-/automate/agent-sessions/42"}

    graphql = graphql_router({"duoWorkflowWorkflows": {"duoWorkflowWorkflows": {"nodes": [
        {"id": "gid://gitlab/Ai::DuoWorkflows::Workflow/42", "status": "FINISHED", "humanStatus": "finished"}]}}})
    server = Server({("GET", API): PROJECT, ("GET", f"{API}/issues"): [{"iid": 9, "title": "Day-one probe incident"}],
                     ("GET", f"{API}/issues/9/notes"): notes, ("POST", "/api/v4/ai/duo_workflows/workflows"): start,
                     ("POST", "/api/v4/graphql"): graphql})
    clock = Clock()
    code, text, _ = run(server, "--step", "flow", "--consumer-id", "77", "--flow-account", "other-account", "--yes", clock=clock)
    assert code == 0, text
    [sent] = started
    assert sent == {
        "project_id": "123",
        "ai_catalog_item_consumer_id": 77,
        "goal": "Issue #9 in project g/sub/p. Read it and post one note that says exactly: probe ok",
        "issue_id": 9,
        "start_workflow": True,
        "allow_agent_to_request_user": False,
        "agent_privileges": [2, 3],
        "pre_approved_agent_privileges": [2, 3],
    }
    assert server.sent("POST", "/api/v4/ai/duo_workflows/workflows")[0].headers["PRIVATE-TOKEN"] == TOKEN
    assert "flow started: workflow 42, status created, consumer id 77" in text
    assert clock.slept == [15.0, 15.0] and "after 30 s" in text
    assert "FLOW_SERVICE_ACCOUNT=ai-night-orders-probe-g" in text
    assert "--flow-account other-account does not match the note's author ai-night-orders-probe-g" in text
    assert "workflow status now: finished" in text
    assert graphql.calls[0]["variables"] == {"workflowId": "gid://gitlab/Ai::DuoWorkflows::Workflow/42"}
    polls = server.sent("GET", f"{API}/issues/9/notes")
    assert polls[0].url.params["sort"] == "desc" and polls[0].url.params["order_by"] == "created_at"


def test_flow_skips_without_a_consumer_id_and_fails_when_no_note_comes():
    code, text, _ = run(Server({("GET", API): PROJECT}), "--step", "flow", "--yes")
    assert code == 0 and "flow: SKIP (no consumer id for the probe flow" in text
    server = Server({("GET", API): PROJECT, ("GET", f"{API}/issues"): [{"iid": 9, "title": "Day-one probe incident"}],
                     ("GET", f"{API}/issues/9/notes"): [], ("POST", "/api/v4/ai/duo_workflows/workflows"): (201, {"id": 42, "status": "running"}),
                     ("POST", "/api/v4/graphql"): (500, {"message": "boom"})})
    clock = Clock()
    code, text, _ = run(server, "--step", "flow", "--consumer-id", "77", "--yes", clock=clock)
    assert code == 1 and "flow: FAIL (no note with 'probe ok' on incident #9 within 360 s (workflow 42, status not readable" in text
    assert clock.slept == [15.0] * 24


def test_wait_for_note_polls_every_15_seconds_tolerates_a_bad_fetch_and_gives_up_after_six_minutes():
    clock = Clock()
    answers = iter([[note(1, "a", "probe ok")] , RelayError("GitLab read notes: HTTP 502"),
                    [note(2, "bot", "PROBE OK", system=True)], [note(3, "ai-probe", "well: probe ok")]])

    def fetch():
        answer = next(answers)
        if isinstance(answer, Exception):
            raise answer
        return answer

    found, elapsed, problem = day_one.wait_for_note(fetch, "probe ok", clock=clock, sleep=clock.sleep, ignore={1})
    assert found["id"] == 3 and elapsed == 45.0 and clock.slept == [15.0, 15.0, 15.0] and problem == ""
    never = Clock()
    found, elapsed, problem = day_one.wait_for_note(lambda: [], "probe ok", clock=never, sleep=never.sleep)
    assert found is None and elapsed == 360.0 and never.slept == [15.0] * 24


# signature.

def signature_server(approve, merge, merge_status="mergeable"):
    return Server({
        ("GET", API): PROJECT,
        ("GET", f"{API}/repository/files/ops/night-orders.yml/raw"):
            'night: "2026-10-06"\nexpires: "07:00"\norders: []\n# day-one signature probe 20261001-000000: an earlier run.\n',
        ("POST", f"{API}/repository/commits"): (201, {"id": "abc123"}),
        ("POST", f"{API}/merge_requests"): (201, {"iid": 5, "web_url": "https://gitlab.example/g/sub/p/-/merge_requests/5"}),
        ("POST", f"{API}/merge_requests/5/approve"): approve,
        ("GET", f"{API}/merge_requests/5"): {"iid": 5, "detailed_merge_status": merge_status},
        ("PUT", f"{API}/merge_requests/5/merge"): merge,
        ("PUT", f"{API}/merge_requests/5"): {"iid": 5, "state": "closed"},
        ("DELETE", f"{API}/repository/branches/day-one/20261012-150000"): (204, ""),
    })


def test_signature_is_an_approval_when_the_role_may_approve_but_not_merge():
    server = signature_server(approve=(201, {"approved": True}), merge=(403, {"message": "403 Forbidden"}))
    code, text, _ = run(server, "--step", "signature", "--yes")
    assert code == 0, text
    commit = body(server.sent("POST", f"{API}/repository/commits")[0])
    assert commit["branch"] == "day-one/20261012-150000" and commit["start_branch"] == "main"
    [action] = commit["actions"]
    assert action["action"] == "update" and action["file_path"] == "ops/night-orders.yml"
    assert action["content"].startswith('night: "2026-10-06"\nexpires: "07:00"\norders: []\n# day-one signature probe 20261012-150000')
    assert action["content"].count("\n") == 4 and "20261001" not in action["content"]   # one probe line, not two
    mr = body(server.sent("POST", f"{API}/merge_requests")[0])
    assert mr["source_branch"] == "day-one/20261012-150000" and mr["target_branch"] == "main" and mr["remove_source_branch"] is True
    assert "approve: allowed (HTTP 201)" in text
    assert "merge: refused (HTTP 403 (403 Forbidden)): this role may not merge into main" in text
    assert "SIGNATURE_METHOD=approval" in text
    assert body(server.sent("PUT", f"{API}/merge_requests/5")[0]) == {"state_event": "close"}
    assert server.sent("DELETE", f"{API}/repository/branches/day-one/20261012-150000")
    assert "merge request !5 closed and branch day-one/20261012-150000 deleted" in text


def test_signature_keeps_the_approval_when_the_merge_needs_a_sha():
    server = signature_server(approve=(201, {"approved": True}), merge=(400, {"message": "SHA must be provided when merging"}))
    code, text, _ = run(server, "--step", "signature", "--yes")
    assert code == 0 and "merge: not possible now (HTTP 400 (SHA must be provided when merging))" in text
    assert "SIGNATURE_METHOD=approval" in text


def test_signature_is_undecided_on_a_405_merge_and_an_author_refusal_and_still_tidies_up():
    server = signature_server(approve=(401, {"message": "401 Unauthorized"}), merge=(405, {"message": "405 Method Not Allowed"}),
                              merge_status="ci_must_pass")
    code, text, _ = run(server, "--step", "signature", "--yes")
    assert code == 1
    assert "approve: refused (HTTP 401 (401 Unauthorized))" in text and "author approving their own merge request" in text
    assert "merge: not possible now (HTTP 405 (405 Method Not Allowed)), detailed_merge_status ci_must_pass" in text
    assert "SIGNATURE_METHOD=undecided" in text and "signature: FAIL (neither merge nor approve worked" in text
    assert server.sent("PUT", f"{API}/merge_requests/5") and server.sent("DELETE", f"{API}/repository/branches/day-one/20261012-150000")
    kept = signature_server(approve=(401, {"message": "401 Unauthorized"}), merge=(405, {"message": "405 Method Not Allowed"}))
    code, text, _ = run(kept, "--step", "signature", "--yes", "--keep")
    assert code == 1 and not kept.sent("PUT", f"{API}/merge_requests/5") and not kept.sent("DELETE", f"{API}/repository/branches/day-one/20261012-150000")


def test_signature_merges_when_the_role_may_and_waits_while_gitlab_checks():
    checks = iter(["checking", "checking", "mergeable"])
    server = signature_server(approve=(401, {"message": "401 Unauthorized"}), merge=(200, {"iid": 5, "state": "merged"}))
    server.routes[("GET", f"{API}/merge_requests/5")] = lambda request: {"iid": 5, "detailed_merge_status": next(checks)}
    clock = Clock()
    code, text, _ = run(server, "--step", "signature", "--yes", clock=clock)
    assert code == 0 and "merge: done (HTTP 200) into main" in text and "SIGNATURE_METHOD=merge" in text
    assert clock.slept == [5.0, 5.0] and not server.sent("PUT", f"{API}/merge_requests/5")


def test_signature_skips_when_the_orders_file_is_not_pushed_yet():
    code, text, _ = run(Server({("GET", API): PROJECT}), "--step", "signature", "--yes")
    assert code == 0 and "signature: SKIP (ops/night-orders.yml is not on main: push the repository first)" in text


# Safety: the token, the confirmation, the exit codes.

def test_the_token_never_appears_in_any_printed_line_even_when_gitlab_echoes_it(tmp_path):
    server = Server(fallback=(500, {"message": f"server error while checking {TOKEN}"}))
    clock = Clock()
    code, text, data = run(server, "--yes", clock=clock, out_json=tmp_path / "r.json")
    assert code == 1
    assert TOKEN not in text and "[GITLAB_TOKEN]" in text
    assert TOKEN not in json.dumps(data)
    assert server.requests and all(r.headers["PRIVATE-TOKEN"] == TOKEN for r in server.requests)
    statuses = {r["step"]: r["status"] for r in data["results"]}
    assert statuses.pop("flow") == "SKIP"                   # no consumer id: the flow step cannot even start
    assert statuses == dict.fromkeys(["whoami", "publish", "issue", "flags", "catalog", "incident", "signature", "cleanup"], "FAIL")
    assert "whoami: FAIL (GitLab read user: HTTP 500 (server error while checking [GITLAB_TOKEN]))" in text
    assert clock.slept == []


def test_the_json_file_and_a_list_shaped_answer_are_safe_too(tmp_path):
    server = Server({("GET", "/api/v4/user"): ME, ("GET", API): {**PROJECT, "path_with_namespace": f"g/{TOKEN}"},
                     ("GET", f"{API}/members/all/10"): (404, {"message": "404 Not found"}),
                     ("POST", "/api/v4/ai/duo_workflows/workflows"): (201, ["not", "an", "object"]),
                     ("GET", f"{API}/issues"): [{"iid": 9, "title": "Day-one probe incident"}], ("GET", f"{API}/issues/9/notes"): []})
    code, text, data = run(server, "--step", "whoami", "--step", "flow", "--consumer-id", "7", "--yes", out_json=tmp_path / "r.json")
    assert code == 1 and TOKEN not in text and TOKEN not in json.dumps(data)
    assert data["values"]["PROJECT_PATH"] == "g/[GITLAB_TOKEN]"
    assert "flow: FAIL (unexpected answer from GitLab (AttributeError" in text


def test_write_steps_wait_for_yes_and_the_token_comes_only_from_the_environment():
    server = Server({("GET", API): PROJECT})
    code, text, _ = run(server, "--step", "publish", "--step", "issue", ask=lambda steps: False)
    assert code == 0 and "publish: PASS" in text
    assert "issue: SKIP (writes to GitLab: not confirmed (pass --yes))" in text
    assert not server.sent("GET", f"{API}/issues")
    code, text, _ = run(server, "--step", "whoami", token="")
    assert code == 2 and "GITLAB_TOKEN is not set" in text and len(server.requests) == 1
    with pytest.raises(SystemExit):
        day_one.parse_args(["--project", "1", "--token", "x"])


def test_a_slow_server_is_a_fail_with_the_20_second_timeout():
    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    code, text, _ = run(Server({("GET", API): slow}), "--step", "publish")
    assert code == 1 and "publish: FAIL (GitLab read project: no answer within 20 s)" in text
    assert day_one.TIMEOUT_SECONDS == 20.0


def test_the_probe_flow_file_matches_what_the_brief_asks_for():
    import yaml

    data = yaml.safe_load(day_one.PROBE_FLOW.read_text())
    [component] = data["components"]
    assert component["type"] == "AgentComponent" and component["toolset"] == ["get_issue", "create_issue_note"]
    assert data["coding_environment"] == "none"
    [prompt] = data["prompts"]
    assert "post one note that says exactly: probe ok" in prompt["prompt_template"]["system"]
