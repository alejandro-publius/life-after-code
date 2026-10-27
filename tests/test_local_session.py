"""Real child-process HTTP shop sessions; no mocked metrics, flag writes or checkout replies."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from local_main import create_app
from nightorders.local_session import MAX_REQUESTS, LocalError, LocalSession

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def shop(tmp_path):
    """Run the production checkout code plus disposable controls on an actual loopback socket."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    key, identity = secrets.token_urlsafe(32), secrets.token_hex(16)
    environment = dict(os.environ, LOCAL_SHOP_KEY=key, LOCAL_SHOP_ID=identity,
                       PYTHONPATH=str(ROOT / "shop"), PYTHONDONTWRITEBYTECODE="1")
    log_path = tmp_path / "shop.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "local_shop:app", "--host", "127.0.0.1",
             "--port", str(port), "--no-access-log"], cwd=ROOT / "shop", env=environment,
            stdout=log, stderr=log)
        url = f"http://127.0.0.1:{port}"
        try:
            with httpx.Client(base_url=url, trust_env=False, timeout=1) as client:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        pytest.fail(f"Disposable shop exited: {log_path.read_text()}")
                    try:
                        if client.get("/healthz").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(.05)
                else:
                    pytest.fail("Disposable shop did not become ready within ten seconds")
            yield {"url": url, "key": key, "identity": identity, "directory": tmp_path / "state"}
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def session_for(shop):
    return LocalSession(shop["url"], shop["key"], shop["identity"], shop["directory"])


def actual_state(shop):
    with httpx.Client(base_url=shop["url"], trust_env=False, timeout=3) as client:
        response = client.get("/local/state", headers={"X-Local-Shop-Key": shop["key"]})
        response.raise_for_status()
        return response.json()


@pytest.mark.parametrize("choice", ["keep", "restore"])
def test_signed_session_measures_real_failure_applies_once_and_finishes_cleanly(shop, choice):
    session = session_for(shop)
    try:
        started = session.run("start")
        assert started["baseline"]["healthy"] and started["baseline"]["checkouts"] == 10
        assert started["original"]["flags"]["new_checkout"] == "on"
        authorized = session.run("authorize")
        assert authorized["authorization"]["method"] == "local browser consent"
        observed = session.run("observe")
        assert observed["decision"]["allowed"] and observed["decision"]["applied"]
        assert observed["authorization"]["used"]
        assert len(observed["metrics"]["before"]) == 5
        assert all(bucket["checkouts.new"] == 10 and bucket["checkout_error_rate.new"] == 1
                   for bucket in observed["metrics"]["before"])
        assert sum(item["http"] == 500 for item in observed["checkout_requests"]) == 50
        assert actual_state(shop)["flags"]["new_checkout"] == "off"
        authorized_writes = [i for i in observed["intents"] if i["kind"] == "authorized new_checkout off"]
        assert len(authorized_writes) == 1
        assert authorized_writes[0]["before"]["flags"]["new_checkout"] == "on"
        assert authorized_writes[0]["readback"]["flags"]["new_checkout"] == "off"

        verified = session.run("verify")
        assert verified["verification"]["healthy"] and verified["verification"]["checkouts"] == 10
        sample = verified["metrics"]["after"][-1]
        assert sample["checkouts.new"] == 0 and sample["checkouts.all"] == 10
        assert sample["checkout_error_rate.all"] == 0
        morning = session.run("morning", choice)
        assert morning["morning"]["healthy"] is (choice == "keep")
        assert morning["morning"]["restored"] == (1 if choice == "restore" else 0)
        assert "rounding_bug" in actual_state(shop)["faults"]
        assert actual_state(shop)["flags"]["new_checkout"] == ("off" if choice == "keep" else "on")

        finished = session.run("finish")
        assert finished["phase"] == "finished" and finished["cleanup"]["healthy"]
        real = actual_state(shop)
        assert real["flags"] == started["original"]["flags"] and real["faults"] == []
        assert finished["request_count"] < 200
        count = len(finished["intents"])
        assert len(session.run("finish")["intents"]) == count
        receipt = json.loads((shop["directory"] / "receipt.json").read_text())
        assert "csrf_token" not in receipt and "shop_id" not in receipt
        assert shop["key"] not in json.dumps(receipt)
        assert finished["csrf_token"] not in json.dumps(receipt)
    finally:
        session.close()


def test_unsigned_session_observes_real_fault_but_refuses_the_flag_write(shop):
    session = session_for(shop)
    try:
        session.run("start")
        observed = session.run("observe")
        assert observed["phase"] == "observed" and not observed["decision"]["allowed"]
        assert not observed["decision"]["applied"]
        assert not any(i["path"] == "/local/flag" for i in observed["intents"])
        assert actual_state(shop)["flags"]["new_checkout"] == "on"
        verified = session.run("verify")
        assert not verified["verification"]["healthy"]
        assert verified["metrics"]["after"][-1]["checkout_error_rate.all"] == 1
        assert session.run("finish")["cleanup"]["healthy"]
        assert actual_state(shop)["faults"] == []
    finally:
        session.close()


def test_lost_flag_response_preserves_snapshot_and_reload_never_repeats_mutation(shop, monkeypatch):
    session = session_for(shop)
    reconstructed = None
    try:
        session.run("start")
        session.run("authorize")
        request = session.client.request
        lost = []

        def lose_first_flag_response(method, path, **kwargs):
            response = request(method, path, **kwargs)
            if method == "POST" and path == "/local/flag" and not lost:
                lost.append(response.status_code)
                raise httpx.ReadTimeout("Injected lost response after actual HTTP flag write", request=response.request)
            return response

        monkeypatch.setattr(session.client, "request", lose_first_flag_response)
        with pytest.raises(LocalError, match="lost"):
            session.run("observe")
        assert lost == [200]
        durable = json.loads(session.path.read_text())
        assert durable["phase"] == "uncertain" and durable["authorization"]["used"]
        intent = durable["intents"][-1]
        assert intent["path"] == "/local/flag" and intent["status"] == "pending"
        assert intent["before"]["flags"]["new_checkout"] == "on"
        assert actual_state(shop)["flags"]["new_checkout"] == "off"

        reconstructed = session_for(shop)
        before_count = len(reconstructed.data["intents"])
        reloaded = reconstructed.run("reload")
        assert reloaded["phase"] == "uncertain" and reloaded["flags"]["new_checkout"] == "off"
        assert len(reloaded["intents"]) == before_count
        with pytest.raises(LocalError, match="uncertain"):
            reconstructed.run("observe")
        assert len(reconstructed.data["intents"]) == before_count
        finished = reconstructed.run("finish")
        assert finished["cleanup"]["healthy"]
        assert actual_state(shop)["flags"]["new_checkout"] == "on"
        assert actual_state(shop)["faults"] == []
        assert len([i for i in finished["intents"] if i["kind"] == "authorized new_checkout off"]) == 1
        reconstructed.close()
        reconstructed = session_for(shop)
        assert reconstructed.data["phase"] == "finished"
        assert reconstructed.run("reload")["phase"] == "finished"
    finally:
        session.close()
        if reconstructed:
            reconstructed.close()


def test_expired_browser_consent_cannot_authorize_the_real_flag_write(shop):
    session = session_for(shop)
    try:
        session.run("start")
        session.run("authorize")
        session.data["authorization"]["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        session.save()
        observed = session.run("observe")
        assert not observed["decision"]["allowed"]
        assert any("expired" in reason for reason in observed["decision"]["reasons"])
        assert actual_state(shop)["flags"]["new_checkout"] == "on"
        assert not any(i["path"] == "/local/flag" for i in observed["intents"])
        session.run("finish")
    finally:
        session.close()


def test_cleanup_has_a_separate_bounded_budget_after_regular_requests_are_exhausted(shop):
    session = session_for(shop)
    try:
        session.run("start")
        session.run("observe")
        assert "rounding_bug" in actual_state(shop)["faults"]
        session.data["request_count"] = MAX_REQUESTS
        session.save()
        with pytest.raises(LocalError, match="limit"):
            session.run("verify")
        finished = session.run("finish")
        assert finished["phase"] == "finished" and finished["cleanup"]["healthy"]
        assert 0 < finished["cleanup_request_count"] <= finished["limits"]["cleanup_http_requests"]
        assert finished["request_count"] > MAX_REQUESTS
        assert actual_state(shop)["flags"] == finished["original"]["flags"]
        assert actual_state(shop)["faults"] == []
    finally:
        session.close()


@pytest.mark.parametrize("url", ["https://127.0.0.1:8080", "http://localhost:8080", "http://example.com:8080",
                                 "http://127.0.0.1:8080/path", "http://user:pass@127.0.0.1:8080",
                                 "http://127.0.0.1:8080?target=example.com"])
def test_arbitrary_shop_targets_are_refused_before_any_request(tmp_path, url):
    with pytest.raises(ValueError, match="owned loopback"):
        LocalSession(url, "unused", "unused", tmp_path)


def test_http_surface_rejects_cross_origin_csrf_and_production_tick(shop):
    session = session_for(shop)
    try:
        with TestClient(create_app(session), base_url="http://127.0.0.1:8082") as client:
            state = client.get("/local/api/state")
            assert state.status_code == 200
            key = state.json()["csrf_token"]
            assert client.post("/local/api/start").status_code == 403
            assert client.post("/local/api/start", headers={"X-Local-Key": key, "Origin": "https://example.com"}).status_code == 403
            assert client.post("/local/api/start", headers={"X-Local-Key": key, "Sec-Fetch-Site": "cross-site"}).status_code == 403
            assert client.get("/local/api/state", headers={"Host": "example.com"}).status_code == 403
            assert client.post("/tick", headers={"X-Local-Key": key}).status_code == 404
            assert session.data["request_count"] == 0
            receipt = client.get("/local/api/receipt")
            assert receipt.status_code == 200 and "csrf_token" not in receipt.json()
            assert "attachment" in receipt.headers["Content-Disposition"]
    finally:
        session.close()
