"""The rehearsal: a drafted orders merge request is tried on staging and the result posted on it. Offline.

Every name, commit and time here is test data; the orders are the demo night's orders.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from conftest import OPS, REPO
from nightorders.gitlab_ports import GitLab, GitLabPorts, GoogleToken, Http
from nightorders.orders import load_context
from nightorders.rehearsal import step

API = "/api/v4/projects/123"
NOW = datetime(2026, 10, 21, 4, 35, tzinfo=timezone.utc)  # 21:35 in Los Angeles
SHA = "abc123def4567890"
ORDERS = (REPO / "demo" / "night-2026-10-20" / "orders.yml").read_text()
SERVICE = "/v2/projects/demo-project/locations/us-central1/services/shop"


class World:
    """A fake GitLab, Cloud Run, metadata server and staging shop in one transport."""

    def __init__(self, orders_text: str = ORDERS, revision_exists: bool = True):
        self.requests: list[httpx.Request] = []
        self.flag = {"name": "new_checkout", "active": True, "version": "new_version_flag", "strategies": [
            {"id": 11, "name": "userWithId", "parameters": {"userIds": "pilot-01,pilot-02"},
             "scopes": [{"id": 21, "environment_scope": "production"}, {"id": 22, "environment_scope": "staging"}]}]}
        self.orders_text = orders_text
        self.revision_exists = revision_exists
        self.notes: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path, method = request.url.path, request.method
        if request.url.host == "metadata.google.internal":
            return httpx.Response(200, json={"access_token": "test-google-token", "expires_in": 3599})
        if request.url.host == "shop-staging.example":
            if path == "/healthz":
                return httpx.Response(200, json={"ok": True, "commit": "abc"})
            if path == "/checkout":
                return httpx.Response(200, json={"ok": True, "path": "old"})
        if request.url.host == "run.googleapis.com":
            if path == f"{SERVICE}/revisions/shop-00041":
                return httpx.Response(200 if self.revision_exists else 404, json={"name": "shop-00041"})
        if path == API:
            return httpx.Response(200, json={"id": 123, "default_branch": "main"})
        if path == f"{API}/merge_requests" and method == "GET":
            return httpx.Response(200, json=[{"iid": 31, "sha": SHA, "title": "Night orders, Tue 20 Oct"}])
        if path == f"{API}/merge_requests/31/diffs":
            return httpx.Response(200, json=[{"new_path": "ops/night-orders.yml", "old_path": "ops/night-orders.yml"}])
        if path.startswith(f"{API}/repository/files/") and path.endswith("/raw"):  # httpx decodes %2F
            assert request.url.params["ref"] == SHA
            return httpx.Response(200, text=self.orders_text)
        if path == f"{API}/feature_flags/new_checkout":
            if method == "PUT":
                self.apply_update(json.loads(request.content))
            return httpx.Response(200, json=self.flag)
        if path == f"{API}/merge_requests/31/notes" and method == "POST":
            self.notes.append(json.loads(request.content))
            return httpx.Response(201, json={"id": 77})
        return httpx.Response(404, json={"message": "404 Not Found"})

    def apply_update(self, update: dict) -> None:
        """A small model of GitLab's PUT: destroy scopes or strategies, add new strategies."""
        for change in update.get("strategies", []):
            if "id" in change:
                target = next(s for s in self.flag["strategies"] if s["id"] == change["id"])
                if change.get("_destroy"):
                    self.flag["strategies"].remove(target)
                else:
                    gone = {s["id"] for s in change.get("scopes", []) if s.get("_destroy")}
                    target["scopes"] = [s for s in target["scopes"] if s["id"] not in gone]
            else:
                new_id = max([s["id"] for s in self.flag["strategies"]] + [100]) + 1
                self.flag["strategies"].append({"id": new_id, "name": change["name"], "parameters": change["parameters"],
                                                "scopes": [{"id": new_id * 10 + i, "environment_scope": s["environment_scope"]}
                                                           for i, s in enumerate(change["scopes"])]})
        if "active" in update:
            self.flag["active"] = update["active"]


def run(world: World, relay_doc: dict | None = None, staging_url: str = "https://shop-staging.example"):
    http = Http(httpx.Client(transport=httpx.MockTransport(world)))
    gitlab = GitLab(http, "https://gitlab.example", "123", "test-token")
    ports = GitLabPorts(gitlab, http, flow_consumer_id="77", flow_service_account="duo-watch",
                        ntfy_url="https://ntfy.example/t", gcp_project="demo-project", gcp_region="us-central1",
                        google_token=GoogleToken(http))
    oncall, targets = load_context(OPS)
    relay_doc = {} if relay_doc is None else relay_doc
    return step(relay_doc, NOW, oncall, targets, gitlab, ports, http, staging_url), relay_doc


def staging_scopes(world: World) -> list[tuple[str, str]]:
    return sorted((s["name"], sc["environment_scope"]) for s in world.flag["strategies"] for sc in s["scopes"]
                  if sc["environment_scope"] == "staging")


def test_each_order_is_tried_on_staging_restored_and_reported_on_the_merge_request():
    world = World()
    before = staging_scopes(world)
    reported, doc = run(world)
    assert reported == ["rehearsed !31 at abc123de"]
    [note] = world.notes
    lines = note["body"].splitlines()
    assert lines[0] == "Rehearsal on staging at 21:35, written by code for commit abc123de."
    assert "- order 1: new_checkout off in staging applied, staging shop healthy, checkout ok on the old path, restored" in lines
    assert "- order 2: revision shop-00041 exists on shop" in lines
    assert lines[-1] == "2 order(s) checked. Merge to sign; the orders end at 07:00."
    assert staging_scopes(world) == before  # the staging flag is back as it was: the pilot list for staging
    puts = [r for r in world.requests if r.method == "PUT"]
    assert len(puts) == 2  # one to apply, one to restore
    assert doc["rehearsed"] == {"31": SHA} and doc["rehearsal_tries"] == {}
    assert not any(r.url.path.startswith(SERVICE) and r.method == "PATCH" for r in world.requests)


def test_a_head_is_rehearsed_once():
    world = World()
    _, doc = run(world)
    reported, doc = run(world, doc)
    assert reported == [] and len(world.notes) == 1


def test_a_missing_revision_is_reported_and_a_refused_draft_explains_why():
    world = World(revision_exists=False)
    run(world)
    assert "- order 2: revision shop-00041 is NOT on shop, this order cannot run" in world.notes[0]["body"]
    bad = World(orders_text=ORDERS.replace("flag: new_checkout", "flag: delete_everything"))
    run(bad)
    body = bad.notes[0]["body"]
    assert "Code refuses this draft, so it cannot be signed:" in body
    assert "- order 1: flag delete_everything is not in ops/targets.yml" in body
    assert not any(r.method == "PUT" for r in bad.requests)


def test_without_a_staging_shop_the_flag_is_still_tried_and_restored():
    world = World()
    run(world, staging_url="")
    assert "no staging shop URL set, not checked, restored" in world.notes[0]["body"]
    assert not any(r.url.host == "shop-staging.example" for r in world.requests)


def test_a_failed_rehearsal_is_tried_again_a_few_times_then_left():
    class NotesDown(World):
        def __call__(self, request):
            if request.url.path.endswith("/merge_requests/31/notes"):
                self.requests.append(request)
                return httpx.Response(503, json={"message": "down"})
            return super().__call__(request)

    import pytest
    from nightorders.gitlab_ports import RelayError

    world = NotesDown()
    doc: dict = {}
    for _ in range(3):
        with pytest.raises(RelayError):
            run(world, doc)
    assert doc["rehearsal_tries"] == {SHA: 3} and "31" not in doc["rehearsed"]
    assert run(world, doc)[0] == []  # the fourth tick leaves it for a person


def test_the_relay_tick_runs_the_rehearsal_outside_the_watch_failure_path(tmp_path, monkeypatch):
    import importlib.util
    import sys

    from fastapi.testclient import TestClient
    from nightorders.gitlab_ports import RelayError
    from nightorders.orders import load_yaml, parse_oncall, parse_targets
    from nightorders.signals import Metrics
    from nightorders.sources import Inputs
    from nightorders.state import FileStore
    from nightorders.watch import parse_alert_rules

    spec = importlib.util.spec_from_file_location("relay_main_for_rehearsal", REPO / "relay" / "main.py")
    main = importlib.util.module_from_spec(spec)
    sys.modules["relay_main_for_rehearsal"] = main
    spec.loader.exec_module(main)
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

    calls = {"n": 0}

    def rehearse(relay_doc, now, inputs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RelayError("GitLab list open merge requests: HTTP 503")
        return ["rehearsed !31 at abc123de"]

    store = FileStore(tmp_path / "state.json")
    app = main.create_app(make_store=lambda config: store,
                          make_relay=lambda config, store: main.Relay(sources=Quiet(), store=store,
                                                                      make_ports=lambda saved: NoPorts(),
                                                                      pager=lambda *a, **k: None, rehearse=rehearse),
                          clock=lambda: NOW, page_cache_seconds=0)
    client = TestClient(app)
    first = client.post("/tick", headers={"X-Relay-Key": "k"})
    assert first.status_code == 200 and first.json()["morning"] == []
    assert store.load()[0]["relay"]["rehearsal_problem"]["reason"] == "GitLab list open merge requests: HTTP 503"
    second = client.post("/tick", headers={"X-Relay-Key": "k"})
    assert second.status_code == 200 and second.json()["morning"] == ["rehearsed !31 at abc123de"]
