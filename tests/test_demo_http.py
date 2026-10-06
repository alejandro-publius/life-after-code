"""The public replay is usable without access to a connected night watch."""

import importlib.util
from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest


RELAY = Path(__file__).resolve().parents[1] / "relay"
spec = importlib.util.spec_from_file_location("demo_http_relay_main", RELAY / "main.py")
main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = main
spec.loader.exec_module(main)


@pytest.fixture
def client():
    def forbidden(*args, **kwargs):
        raise AssertionError("A demo must not open a production state store or relay")

    return TestClient(main.create_app(make_store=forbidden, make_relay=forbidden))


def test_demo_is_a_connected_path_even_when_night_state_is_unavailable(client):
    status = client.get("/")
    assert status.status_code == 200
    assert 'href="/demo"' in status.text
    assert "cannot be read right now" in status.text
    assert "GitLab incidents and the pages are real" not in status.text
    page = client.get("/demo")
    assert page.status_code == 200
    assert "Priya wants to sleep" in page.text
    assert "Recorded agent replies" in page.text
    assert 'href="/demo/assets/style.css"' in page.text
    assert 'src="/demo/assets/app.js"' in page.text
    assert client.get("/demo/").text == page.text


def test_assets_work_with_the_demo_content_security_policy(client):
    response = client.get("/demo")
    policy = response.headers["content-security-policy"]
    assert "script-src 'self'" in policy
    assert "connect-src 'self'" in policy
    assert "unsafe-inline" not in policy
    assert client.get("/demo/assets/style.css").headers["content-type"].startswith("text/css")
    assert "Checking" in client.get("/demo/assets/app.js").text
    assert client.get("/demo/assets/%2e%2e/main.py").status_code == 404


@pytest.mark.parametrize("signed,approved,pages,automatic,accepted", [
    (True, True, 1, 1, 1), (True, False, 1, 1, 0),
    (False, True, 2, 0, 0), (False, False, 2, 0, 0),
])
def test_http_choices_use_the_real_replay_without_production_ports(
    client, signed, approved, pages, automatic, accepted, monkeypatch,
):
    fixture_secret = "labelled-demo-runtime-secret-not-a-real-token"
    monkeypatch.setenv("GITLAB_TOKEN", fixture_secret)
    response = client.get("/demo/replay", params={
        "signed": str(signed).lower(), "approved": str(approved).lower(),
    })
    assert response.status_code == 200
    body = response.json()
    assert body["choices"] == {"signed": signed, "approved": approved}
    assert body["counts"]["pages"] == pages
    assert body["counts"]["automatic_incidents_handled"] == automatic
    assert body["counts"]["approved_actions"] == accepted
    assert len(body["metrics"]) == 546
    assert fixture_secret not in response.text
    assert "recorded model replies" in body["label"]
    assert response.headers["cache-control"] == "no-store"


def test_invalid_choices_do_not_run_a_replay(client):
    assert client.get("/demo/replay?signed=run-a-production-action").status_code == 422
    assert client.post("/demo/replay", json={"signed": True}).status_code == 405
    assert client.post("/tick").status_code == 401
