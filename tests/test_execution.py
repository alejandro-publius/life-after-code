"""Captured executions preserve provenance, failure states and the artifact boundary."""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from nightorders import execution
from scripts.capture_runs import Capture
from scripts.day_one import RelayError

BASE = "https://gitlab.example/group/project"


def workflow():
    return {"id": "gid://gitlab/Ai::DuoWorkflows::Workflow/17", "title": "Actual dusk run",
            "project": {"id": "gid://gitlab/Project/9"}, "aiCatalogItem": {"name": "night-orders-dusk"},
            "status": "FINISHED", "webUrl": BASE + "/-/automate/agent-sessions/17",
            "latestCheckpoint": {"executionStatus": "Completed", "errors": [], "duoMessages": [
                {"content": "Read orders", "messageType": "tool", "status": "success", "componentName": "scout",
                 "toolInfo": json.dumps({"name": "get_repository_file", "args": {"secret": "never-copy-args"},
                                          "tool_response": "never-copy-response"})}]},
            "mergeRequestLinks": {"nodes": []}}


class Run:
    def __init__(self, node=None):
        self.node = deepcopy(node if node is not None else workflow())
        self.calls = []
        self.gitlab = SimpleNamespace(json=self.get)
        self.elapsed = 0

    def project(self):
        return {"id": 9, "name": "Project", "visibility": "public", "web_url": BASE}

    def graphql(self, what, query, variables):
        assert "mutation" not in query
        assert variables["projectId"] == "gid://gitlab/Project/9"
        return {"duoWorkflowWorkflows": {"nodes": [self.node], "pageInfo": {"hasNextPage": False}}}

    def get(self, what, method, path, **kwargs):
        assert method == "GET"
        self.calls.append(path)
        return {"iid": 4, "title": "Orders", "web_url": BASE + "/-/merge_requests/4", "state": "opened",
                "draft": True, "sha": "abc", "overflow": True,
                "changes": [{"new_path": "ops/night-orders.yml"}]}

    def clock(self):
        return self.elapsed

    def now(self):
        return datetime(2026, 10, 27, tzinfo=timezone.utc)


def test_capture_keeps_visible_tools_but_never_raw_arguments_or_responses():
    result = Capture(Run()).collect()
    encoded = json.dumps(result)
    assert "get_repository_file" in encoded
    assert "never-copy" not in encoded
    assert result["runs"][0]["id"] == 17
    assert result["runs"][0]["status"] == "finished"


def test_workflow_mr_links_are_used_even_when_the_author_is_not_the_flow_account():
    run = Run()
    run.node["mergeRequestLinks"]["nodes"] = [{"mergeRequest": {"iid": "4", "webUrl": BASE + "/-/merge_requests/4"}}]
    result = Capture(run).collect()
    artifact = result["runs"][0]["artifacts"][0]
    assert artifact["iid"] == 4 and artifact["draft"] is True
    assert "incomplete" in artifact["validation"]
    assert run.calls == ["/merge_requests/4/changes"]  # incomplete diffs cannot earn validation


def test_failed_execution_remains_failed_and_keeps_its_error():
    node = workflow()
    node["status"] = "FAILED"
    node["latestCheckpoint"]["errors"] = ["Runner stopped"]
    result = Capture(Run(node)).collect()["runs"][0]
    assert result["status"] == "failed" and result["errors"] == ["Runner stopped"]


def test_cross_project_execution_is_rejected():
    node = workflow()
    node["project"]["id"] = "gid://gitlab/Project/99"
    with pytest.raises(RelayError, match="different project"):
        Capture(Run(node)).collect()


def test_non_application_chat_sessions_are_not_published():
    node = workflow()
    node["aiCatalogItem"] = {"name": "Personal chat"}
    assert Capture(Run(node)).collect()["runs"] == []


def test_links_cannot_carry_credentials_or_escape_the_project():
    for url in ("javascript:alert(1)", "https://elsewhere.example/x", BASE + "-other/-/issues/1",
                "https://user:password@gitlab.example/group/project", BASE + "?token=secret"):
        assert execution.project_link(url, BASE) == ""
    note = BASE + "/-/issues/3#note_42"
    assert execution.project_link(note, BASE) == note


def test_capture_has_a_wall_clock_budget():
    run = Run()
    capture = Capture(run)
    run.elapsed = 121
    with pytest.raises(RelayError, match="two-minute"):
        capture.collect()


def test_recording_has_bounded_steps_and_redacts_recognized_credentials():
    node = workflow()
    node["latestCheckpoint"]["duoMessages"] *= 100
    node["latestCheckpoint"]["duoMessages"][0]["content"] = "glpat-not-a-real-secret"
    result = execution.recording(node, BASE)
    assert len(result["steps"]) == execution.MAX_STEPS
    assert result["steps_truncated"]
    assert "glpat-" not in json.dumps(result)


def test_missing_snapshot_is_empty_and_invalid_snapshot_is_not_success(tmp_path):
    path = tmp_path / "recording.json"
    assert execution.load_recording(path)["runs"] == []
    path.write_text('{"version":99,"runs":[]}')
    with pytest.raises(ValueError):
        execution.load_recording(path)


def test_activity_endpoint_reads_the_recording_without_gitlab_credentials(monkeypatch):
    from fastapi.testclient import TestClient
    from test_relay_app import main

    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    client = TestClient(main.create_app())
    assert client.get("/activity").status_code == 200
    response = client.get("/activity.json")
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert Path(execution.RECORDING).exists()
