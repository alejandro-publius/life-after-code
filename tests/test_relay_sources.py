"""Tonight's inputs from GitLab and the shop: the ops files, the signature, the metrics. Offline (MockTransport).

Every name, commit and time here is test data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
import pytest

from conftest import OPS, REPO
from nightorders.gitlab_ports import GitLab, Http, RelayError
from nightorders.model import Signature
from nightorders.sources import GitLabSources, parse_metrics

API = "/api/v4/projects/123"
NOW = datetime(2026, 10, 21, 10, 12, tzinfo=timezone.utc)
DEMO_ORDERS = (REPO / "demo" / "night-2026-10-20" / "orders.yml").read_text()


def raw(path: str) -> str:
    return f"{API}/repository/files/{path}/raw"


class GitLabFake:
    """Answers by (method, path); a raw file answers by (path, ref). Records every request."""

    def __init__(self, routes: dict, files: dict[tuple[str, str], str]):
        self.routes, self.files, self.requests = routes, files, []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if path.startswith(f"{API}/repository/files/") and path.endswith("/raw"):
            name = path[len(f"{API}/repository/files/"):-len("/raw")]
            text = self.files.get((name, request.url.params["ref"]))
            return httpx.Response(200, text=text) if text is not None else httpx.Response(404, json={})
        answer = self.routes.get((request.method, path))
        return httpx.Response(200, json=answer) if answer is not None else httpx.Response(404, json={})

    def refs(self, name: str) -> list[str]:
        return [r.url.params["ref"] for r in self.requests if r.url.path == raw(name)]


def shop_minutes() -> dict:
    return {"label": "DEMO", "minutes": [
        {"at": "2026-10-21T10:10:00Z", "checkout_error_rate.new": 0.079, "checkout_error_rate.old": 0.003,
         "p95_latency_ms": 420.0},
        {"at": "2026-10-21T10:11:00Z", "checkout_error_rate.new": 0.081, "checkout_error_rate.old": 0.004,
         "p95_latency_ms": 430.0},
    ]}


def base_files(orders_ref: str = "main", orders: str | None = DEMO_ORDERS) -> dict:
    files = {(f"ops/{name}", "main"): (OPS / name).read_text() for name in ("oncall.yml", "targets.yml", "alerts.yml")}
    if orders is not None:
        files[("ops/night-orders.yml", orders_ref)] = orders
    return files


def merged_by(user: str, at: str, iid: int = 31, sha: str = "abc123") -> dict:
    return {
        ("GET", API): {"id": 123, "default_branch": "main"},
        ("GET", f"{API}/repository/commits"): [{"id": sha}],
        ("GET", f"{API}/repository/commits/{sha}/merge_requests"): [{"iid": iid, "target_branch": "main"}],
        ("GET", f"{API}/merge_requests/{iid}"): {"iid": iid, "state": "merged", "merge_user": {"username": user},
                                                 "merged_at": at},
        ("GET", f"{API}/merge_requests"): [],
    }


def load(routes: dict, files: dict, shop=None):
    fake = GitLabFake(routes, files)

    def shop_or_gitlab(request: httpx.Request) -> httpx.Response:
        if request.url.host == "shop.example":
            return httpx.Response(200, json=shop if shop is not None else shop_minutes())
        return fake(request)

    http = Http(httpx.Client(transport=httpx.MockTransport(shop_or_gitlab)))
    sources = GitLabSources(GitLab(http, "https://gitlab.example", "123", "test-token"), http,
                            "https://shop.example/metrics.json")
    return sources.load(NOW), fake


def test_a_merged_orders_change_is_signed_by_its_merger_and_read_at_that_commit():
    inputs, fake = load(merged_by("alex-velazquez", "2026-10-21T05:06:00Z"), base_files("abc123"))
    assert inputs.signature == Signature(method="merge", user="alex-velazquez",
                                         at=datetime(2026, 10, 21, 5, 6, tzinfo=timezone.utc), commit="abc123")
    assert [o.id for o in inputs.orders.orders] == [1, 2] and inputs.orders_problems == ()
    assert fake.refs("ops/night-orders.yml") == ["abc123"]
    assert fake.refs("ops/oncall.yml") == fake.refs("ops/targets.yml") == fake.refs("ops/alerts.yml") == ["main"]
    commits = next(r for r in fake.requests if r.url.path == f"{API}/repository/commits")
    assert commits.url.params["path"] == "ops/night-orders.yml" and commits.url.params["ref_name"] == "main"
    assert inputs.oncall.user == "alex-velazquez" and [r.key for r in inputs.rules][0] == "checkout_error_rate.new"
    assert inputs.metrics.get("checkout_error_rate.new", datetime(2026, 10, 21, 10, 11, tzinfo=timezone.utc)) == 0.081


def test_an_approved_open_merge_request_signs_and_its_head_commit_is_read():
    routes = merged_by("group-maintainer", "2026-10-20T17:00:00Z", iid=20, sha="old000")  # yesterday's merge
    routes[("GET", f"{API}/merge_requests")] = [{"iid": 41, "sha": "head41"}, {"iid": 40, "sha": "head40"}]
    routes[("GET", f"{API}/merge_requests/41/diffs")] = [{"old_path": "ops/night-orders.yml",
                                                         "new_path": "ops/night-orders.yml"}]
    routes[("GET", f"{API}/merge_requests/40/diffs")] = [{"old_path": "README.md", "new_path": "README.md"}]
    routes[("GET", f"{API}/merge_requests/41/approvals")] = {"approved_by": [
        {"user": {"username": "alex-velazquez"}, "approved_at": "2026-10-21T05:06:00.000Z"},
        {"user": {"username": "teammate"}, "approved_at": "2026-10-21T05:30:00.000Z"},
    ]}
    inputs, fake = load(routes, base_files("head41"))
    # The on-call person's approval counts, even though a teammate approved later.
    assert inputs.signature == Signature(method="approval", user="alex-velazquez",
                                         at=datetime(2026, 10, 21, 5, 6, tzinfo=timezone.utc), commit="head41")
    assert fake.refs("ops/night-orders.yml") == ["head41"]
    listed = next(r for r in fake.requests if r.url.path == f"{API}/merge_requests")
    assert listed.url.params["state"] == "opened" and listed.url.params["target_branch"] == "main"


def test_an_orders_file_pushed_without_a_merge_request_has_no_signature():
    routes = merged_by("alex-velazquez", "2026-10-21T05:06:00Z", sha="push01")
    routes[("GET", f"{API}/repository/commits/push01/merge_requests")] = []
    inputs, fake = load(routes, base_files("main"))
    assert inputs.signature is None
    assert fake.refs("ops/night-orders.yml") == ["main"]


def test_a_merge_by_someone_else_is_reported_as_that_person():
    inputs, _ = load(merged_by("teammate", "2026-10-21T05:06:00Z"), base_files("abc123"))
    assert inputs.signature.user == "teammate"  # orders.signature_problems then refuses it


def test_a_broken_orders_file_wakes_rather_than_stopping_the_relay():
    inputs, _ = load(merged_by("alex-velazquez", "2026-10-21T05:06:00Z"), base_files("abc123", "orders: [unclosed"))
    assert inputs.orders is None and inputs.orders_problems == ("ops/night-orders.yml is not valid YAML",)
    bad = DEMO_ORDERS.replace("flag: new_checkout", "flag: drop_tables")
    inputs, _ = load(merged_by("alex-velazquez", "2026-10-21T05:06:00Z"), base_files("abc123", bad))
    assert inputs.orders is None and any("drop_tables" in p for p in inputs.orders_problems)
    inputs, _ = load(merged_by("alex-velazquez", "2026-10-21T05:06:00Z"), base_files("abc123", None))
    assert inputs.orders is None and inputs.orders_problems == ()


def test_a_missing_ops_file_stops_the_tick():
    files = base_files("abc123")
    del files[("ops/oncall.yml", "main")]
    with pytest.raises(RelayError, match="ops/oncall.yml is missing on main"):
        load(merged_by("alex-velazquez", "2026-10-21T05:06:00Z"), files)


def test_shop_metrics_skip_what_cannot_be_trusted():
    metrics = parse_metrics({"minutes": [
        {"at": "2026-10-21T10:10:00Z", "checkout_error_rate.new": 0.08, "flag": True, "note": "x",
         "payment_error_rate": None, "http_5xx_ratio": float("nan")},
        {"at": "not a time", "checkout_error_rate.new": 0.5},
        {"at": "2026-10-21T10:11:00", "checkout_error_rate.new": 0.09},  # no offset: read as UTC
        "junk",
    ]})
    assert metrics.keys() == ["checkout_error_rate.new"]
    assert metrics.get("checkout_error_rate.new", datetime(2026, 10, 21, 10, 11, tzinfo=timezone.utc)) == 0.09
    with pytest.raises(RelayError, match="no list of minutes"):
        parse_metrics({"label": "DEMO"})
    assert json.dumps(shop_minutes())  # the test shape is plain JSON, like the shop's /metrics.json
