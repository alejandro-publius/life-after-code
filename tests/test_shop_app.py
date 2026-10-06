"""The demo shop's HTTP surface: health check contract, DEMO_KEY checks, settings and the shop page.

Keys, users and settings here are test data.
"""

import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _load_shop_main():
    """shop/main.py under a unique name: relay/main.py exists too, and "relay" comes first on the test path."""
    if "shop_main" not in sys.modules:
        path = Path(__file__).resolve().parents[1] / "shop" / "main.py"
        spec = importlib.util.spec_from_file_location("shop_main", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["shop_main"] = module
        spec.loader.exec_module(module)
    return sys.modules["shop_main"]


main = _load_shop_main()


KEY = {"X-Demo-Key": "test-demo-key"}


async def no_wait(_seconds: float) -> None:
    return None


def client(**settings) -> TestClient:
    settings.setdefault("demo_key", "test-demo-key")
    return TestClient(main.create_app(main.Settings(**settings), sleep=no_wait, seed=3))


def test_healthz_follows_the_deploy_contract(monkeypatch):
    monkeypatch.delenv("CI_COMMIT_SHORT_SHA", raising=False)
    with client() as c:
        assert c.get("/healthz").json() == {"ok": True, "commit": "local"}
        monkeypatch.setenv("CI_COMMIT_SHORT_SHA", "abc1234")
        assert c.get("/healthz").json() == {"ok": True, "commit": "abc1234"}


def test_module_app_is_what_the_image_runs():
    assert isinstance(main.app, FastAPI)
    assert TestClient(main.app).get("/healthz").status_code == 200


def test_demo_controls_need_the_demo_key():
    with client() as c:
        assert c.post("/demo/faults", json={"rounding_bug": True}).status_code == 401
        assert c.post("/demo/faults", json={"rounding_bug": True}, headers={"X-Demo-Key": "nope"}).status_code == 401
        assert c.post("/demo/traffic?minutes=1").status_code == 401
        assert c.app.state.shop.faults.active() == []
        answer = c.post("/demo/faults", json={"rounding_bug": True}, headers=KEY)
        assert answer.status_code == 200
        assert answer.json() == {"faults": {"rounding_bug": True, "inventory_slow": False},
                                 "active": ["rounding_bug"], "label": "planted demo fault"}
        assert c.post("/demo/faults", json={"rounding_bug": False}, headers={"DEMO_KEY": "test-demo-key"}).json()[
            "active"] == []


def test_demo_controls_are_off_without_a_demo_key():
    with client(demo_key="") as c:
        assert c.post("/demo/faults", json={"rounding_bug": True}, headers={"X-Demo-Key": ""}).status_code == 403
        assert c.post("/demo/traffic?minutes=1", headers=KEY).status_code == 403


def test_unknown_faults_change_nothing():
    with client() as c:
        answer = c.post("/demo/faults", json={"rounding_bug": True, "disk_full": True}, headers=KEY)
        assert answer.status_code == 400
        assert "disk_full" in answer.json()["detail"]
        assert c.app.state.shop.faults.active() == []


def test_fault_switches_are_logged_as_planted_demo_faults(capsys):
    with client() as c:
        c.post("/demo/faults", json={"inventory_slow": True}, headers=KEY)
    out = capsys.readouterr().out
    assert '"message": "planted demo fault inventory_slow switched on (POST /demo/faults)"' in out


def test_settings_from_env():
    settings = main.Settings.from_env({
        "UNLEASH_URL": "https://gitlab.example/api/v4/feature_flags/unleash/42 ",
        "UNLEASH_INSTANCE_ID": "glffct-test",
        "APP_ENV": "staging",
        "DEMO_KEY": "k",
        "FLAGS_OVERRIDE": "new_checkout=on, stock_from_cache=off, broken",
        "FAULTS": "rounding_bug,inventory_slow=off,disk_full",
    })
    assert settings.unleash_url == "https://gitlab.example/api/v4/feature_flags/unleash/42"
    assert settings.environment == "staging"
    assert settings.flags_override == {"new_checkout": True, "stock_from_cache": False}
    assert settings.faults == {"rounding_bug": True, "inventory_slow": False}
    assert any("broken" in p for p in settings.problems)
    assert any("disk_full" in p for p in settings.problems)
    assert main.Settings.from_env({}).environment == "production"


def test_faults_env_var_switches_faults_on_at_start():
    with client(faults={"rounding_bug": True}) as c:
        assert c.app.state.shop.faults.active() == ["rounding_bug"]


def test_parse_switches():
    assert main.parse_switches("a=on,b=OFF, c = true ,d=0") == ({"a": True, "b": False, "c": True, "d": False}, [])
    values, problems = main.parse_switches("a,b=maybe")
    assert values == {} and len(problems) == 2
    assert main.parse_switches("a", bare_means_on=True) == ({"a": True}, [])
    assert main.parse_switches(None) == ({}, [])


def test_shop_page_is_labelled_and_shows_flags_faults_and_minutes():
    with client(flags_override={"new_checkout": True, "<b>odd</b>": False}, faults={"rounding_bug": True}) as c:
        c.post("/checkout", json={"user": "pilot-01", "region": "us", "items": [{"sku": "juniper-tea", "price": 8}]})
        html = c.get("/").text
    assert "DEMO SHOP: simulated customers and planted faults" in html
    assert "Juniper Market" in html
    assert "FLAGS_OVERRIDE (local override)" in html
    assert "default off (no flag service set)" in html
    assert "planted demo fault" in html and "rounding_bug" in html
    assert "Planted demo faults (active: rounding_bug)" in html
    assert "Last 10 minutes" in html
    assert "demo traffic" in html
    assert "&lt;b&gt;odd&lt;/b&gt;" in html and "<b>odd</b>" not in html


def test_traffic_endpoint_is_time_boxed_to_30_minutes():
    with client() as c:
        assert c.post("/demo/traffic?minutes=31", headers=KEY).status_code == 422
        assert c.post("/demo/traffic?minutes=-1", headers=KEY).status_code == 422
        started = c.post("/demo/traffic?minutes=30", headers=KEY)
        assert started.status_code == 200
        assert started.json()["running"] is True and started.json()["minutes"] == 30
        assert started.json()["label"] == "demo traffic"
        stopped = c.post("/demo/traffic?minutes=0", headers=KEY)
        assert stopped.json() == {"label": "demo traffic", "running": False}
        assert not c.app.state.shop.traffic.running


def test_products_are_the_demo_catalog():
    with client() as c:
        body = c.get("/products").json()
    assert body["label"] == "demo catalog"
    assert {p["sku"] for p in body["products"]} >= {"juniper-jam", "juniper-tea"}
