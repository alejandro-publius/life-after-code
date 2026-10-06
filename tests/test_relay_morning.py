"""The relay's morning: the watch log and the dawn flow at the watch end, then the countersign. Offline.

The demo night is demo data (planted faults, simulated shop). Every key, name and commit here is test data.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from conftest import REPO
from nightorders import demo_night
from nightorders.gitlab_ports import GitLab, GitLabPorts, Http
from nightorders.model import Signature
from nightorders.morning import StateFile
from nightorders.signals import Metrics
from nightorders.sources import GitLabSources, Inputs
from nightorders.state import FileStore


def load_relay_main():
    spec = importlib.util.spec_from_file_location("relay_main_for_morning", REPO / "relay" / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["relay_main_for_morning"] = module
    spec.loader.exec_module(module)
    return module


main = load_relay_main()
KEY = "test-relay-key"
DEMO = REPO / "demo" / "night-2026-10-20"
API = "/api/v4/projects/123"
NOW = datetime(2026, 10, 21, 14, 0, tzinfo=timezone.utc)
KEEP_FLAG_OFF = {"flags": [{"flag": "new_checkout", "environment": "production", "keep": "off",
                            "until": "the fix for !31 is in production"}]}


class Server:
    """A fake GitLab that answers every POST with a new note and records every request."""

    def __init__(self, routes: dict | None = None, files: dict | None = None):
        self.routes, self.files, self.requests = dict(routes or {}), dict(files or {}), []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if path.startswith(f"{API}/repository/files/") and path.endswith("/raw"):
            name = path[len(f"{API}/repository/files/"):-len("/raw")]
            text = self.files.get((name, request.url.params["ref"]))
            return httpx.Response(200, text=text) if text is not None else httpx.Response(404, json={})
        if request.method == "POST":
            return httpx.Response(201, json={"id": 501})
        answer = self.routes.get((request.method, path))
        return httpx.Response(200, json=answer) if answer is not None else httpx.Response(404, json={})

    def http(self) -> Http:
        return Http(httpx.Client(transport=httpx.MockTransport(self)))

    def sent(self, method: str, path: str) -> list[httpx.Request]:
        return [r for r in self.requests if r.method == method and r.url.path == path]


def morning_ports(server: Server, **kwargs) -> GitLabPorts:
    http = server.http()
    gitlab = GitLab(http, "https://gitlab.example", "123", "test-token")
    return GitLabPorts(gitlab, http, flow_consumer_id="77", flow_service_account="duo-watch",
                       ntfy_url="https://ntfy.example/test-topic", **kwargs)


def test_the_morning_ports_post_on_the_watch_issue_and_start_the_dawn_flow():
    server = Server()
    ports = morning_ports(server, dawn_consumer_id="88", watch_issue=7)
    ports.watch_note("## Watch log, night of Tue 20 Oct", NOW)
    ports.start_dawn_flow("Watch issue #7, night of Tue 20 Oct. Code posted the watch log there.", NOW)
    [note] = server.sent("POST", f"{API}/issues/7/notes")
    assert json.loads(note.content) == {"body": "## Watch log, night of Tue 20 Oct"}
    [flow] = server.sent("POST", "/api/v4/ai/duo_workflows/workflows")
    body = json.loads(flow.content)
    assert body["ai_catalog_item_consumer_id"] == 88 and body["issue_id"] == 7 and body["project_id"] == "123"
    assert body["allow_agent_to_request_user"] is False and body["goal"].startswith("Watch issue #7")


def test_without_a_watch_issue_or_dawn_flow_the_morning_ports_do_nothing():
    server = Server()
    morning_ports(server).watch_note("log", NOW)
    morning_ports(server, watch_issue=7).start_dawn_flow("goal", NOW)  # no dawn flow configured
    assert server.requests == []


def countersign_routes(user: str = "alex-velazquez") -> dict:
    return {
        ("GET", API): {"id": 123, "default_branch": "main"},
        ("GET", f"{API}/repository/commits"): [{"id": "cs0001"}],
        ("GET", f"{API}/repository/commits/cs0001/merge_requests"): [{"iid": 52, "target_branch": "main"}],
        ("GET", f"{API}/merge_requests/52"): {"iid": 52, "state": "merged", "merge_user": {"username": user},
                                              "merged_at": "2026-10-21T14:42:00Z"},
        ("GET", f"{API}/merge_requests"): [],
    }


def state_sources(server: Server) -> GitLabSources:
    http = server.http()
    return GitLabSources(GitLab(http, "https://gitlab.example", "123", "test-token"), http,
                         "https://shop.example/metrics.json")


def test_the_countersign_is_read_at_its_signed_commit_with_its_signer():
    text = 'flags:\n  - {flag: new_checkout, environment: production, keep: "off", until: "fix ships"}\n'
    server = Server(countersign_routes(), {("ops/state.yml", "cs0001"): text})
    state = state_sources(server).state_file("alex-velazquez")
    assert state.signature == Signature(method="merge", user="alex-velazquez",
                                        at=datetime(2026, 10, 21, 14, 42, tzinfo=timezone.utc), commit="cs0001")
    assert state.data["flags"][0]["keep"] == "off" and state.problem is None
    commits = next(r for r in server.requests if r.url.path == f"{API}/repository/commits")
    assert commits.url.params["path"] == "ops/state.yml"


def test_a_broken_countersign_file_is_a_problem_not_an_empty_list():
    server = Server(countersign_routes(), {("ops/state.yml", "cs0001"): "flags: [unclosed"})
    state = state_sources(server).state_file("alex-velazquez")
    assert state.data is None and state.problem == "ops/state.yml is not valid YAML"


class NightThroughTheRelay:
    """Stands in for the Watch inside demo_night.run and sends every minute through POST /tick.

    demo_night's recording ports play GitLab, Cloud Run and the phone; they also record the morning notes.
    """

    current: "NightThroughTheRelay | None" = None
    tmp_path = None

    def __init__(self, night, ports, rules):
        self.night, self.rules, self.metrics, self.ports = night, rules, Metrics(), ports
        self.countersign = StateFile(None, None)
        ports.saved = lambda: {}
        ports.watch_notes, ports.dawn_goals = [], []
        ports.watch_note = lambda text, at: ports.watch_notes.append(text)
        ports.start_dawn_flow = lambda goal, at: ports.dawn_goals.append(goal)
        self.store = FileStore(NightThroughTheRelay.tmp_path / "state.json")
        self.now = None

        def make_relay(config, store):
            return main.Relay(sources=self, store=store, make_ports=lambda saved: ports,
                              pager=lambda *args, **kwargs: None, watch_issue=7)

        app = main.create_app(make_store=lambda config: self.store, make_relay=make_relay, clock=lambda: self.now)
        self.client = TestClient(app)
        NightThroughTheRelay.current = self

    def load(self, now):
        night = self.night
        return Inputs(oncall=night.oncall, targets=night.targets, rules=self.rules, orders=night.orders,
                      orders_problems=night.orders_problems, signature=night.signature, metrics=self.metrics)

    def state_file(self, oncall_user):
        return self.countersign

    def tick(self, metrics, now):
        self.metrics, self.now = metrics, now
        response = self.client.post("/tick", headers={"X-Relay-Key": KEY})
        assert response.status_code == 200, response.text
        return response.json()


@pytest.fixture
def morning(tmp_path, monkeypatch):
    monkeypatch.setenv("RELAY_KEY", KEY)
    NightThroughTheRelay.tmp_path = tmp_path
    monkeypatch.setattr(demo_night, "Watch", NightThroughTheRelay)
    ports, night = demo_night.run(DEMO)
    return ports, night, NightThroughTheRelay.current


def test_at_the_watch_end_the_relay_posts_the_log_and_starts_the_dawn_flow_once(morning):
    ports, _night, _relay = morning
    assert len(ports.watch_notes) == 1 and ports.watch_notes[0].startswith("## Watch log, night of Tue 20 Oct")
    assert len(ports.dawn_goals) == 1 and ports.dawn_goals[0].startswith("Watch issue #7, night of Tue 20 Oct.")


def test_the_countersign_undoes_what_was_not_kept_once_and_says_so(morning):
    ports, night, relay = morning
    tz = night.oncall.timezone
    relay.countersign = StateFile(KEEP_FLAG_OFF, Signature(method="merge", user="alex-velazquez",
                                                           at=datetime(2026, 10, 21, 7, 42, tzinfo=tz),
                                                           commit="cs0001"))
    summary = relay.tick(relay.metrics, datetime(2026, 10, 21, 7, 43, tzinfo=tz))
    relay.tick(relay.metrics, datetime(2026, 10, 21, 7, 44, tzinfo=tz))
    assert [line for line in ports.log if "APPLY" in line][-1] == "07:43  APPLY stock_from_cache off in production"
    assert sum("APPLY stock_from_cache off" in line for line in ports.log) == 1
    assert summary["morning"] == ["Countersign by Priya at 07:42 (merge), applied by code."]
    note = ports.watch_notes[-1]
    assert "- Kept: new_checkout off in production, until the fix for !31 is in production" in note
    assert "- Undone: stock_from_cache off in production" in note
    assert ports.shop.flags == {"new_checkout": "off", "stock_from_cache": "off"}
    page = relay.client.get("/").text
    assert "Countersign by Priya at 07:42 (merge), applied by code." in page
