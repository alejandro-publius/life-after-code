"""B3 from the review: an approval signs only the commit it was given after. Offline, against a fake GitLab.

An approval route signature used to trust the merge request's head commit and rely on GitLab removing approvals on
a push, a project setting an operator can turn off and the relay cannot see. Now the merge request's versions say
when the commit the orders are read at was pushed, and an approval counts only at or after that. When the orders
end up unsigned because of it, the relay says why in plain words.

Every name, commit and time here is test data.
"""

from __future__ import annotations

from datetime import datetime

import httpx

from conftest import at
from main import status_of
from nightorders.decide import Ask, Night, Wake, check_request, triage
from nightorders.gitlab_ports import GitLab, Http
from nightorders.ledger import Ledger
from nightorders.model import Alert, Signature
from nightorders.notes import Request, render_request
from nightorders.sources import GitLabSources
from test_relay_sources import API, NOW, GitLabFake, base_files, load, merged_by

PUSHED = [{"id": 3, "head_commit_sha": "head41", "created_at": "2026-10-21T05:30:00.000Z"},  # 22:30 in Los Angeles
          {"id": 2, "head_commit_sha": "old41", "created_at": "2026-10-21T05:00:00.000Z"}]   # newest first
STALE = "!41 was approved before commit head41 was pushed to it, so approve it again"
NEW = "checkout_error_rate.new"


def open_request(approved_at: str, versions: list | None = None, merged: dict | None = None) -> dict:
    """!41 changes the orders and is open, its head commit head41. Unless merged says otherwise, nothing about the
    orders was ever merged."""
    routes = dict(merged) if merged else {("GET", API): {"id": 123, "default_branch": "main"},
                                          ("GET", f"{API}/repository/commits"): []}
    routes[("GET", f"{API}/merge_requests")] = [{"iid": 41, "sha": "head41"}]
    routes[("GET", f"{API}/merge_requests/41/diffs")] = [{"old_path": "ops/night-orders.yml",
                                                         "new_path": "ops/night-orders.yml"}]
    routes[("GET", f"{API}/merge_requests/41/approvals")] = {"approved_by": [
        {"user": {"username": "alex-velazquez"}, "approved_at": approved_at}]}
    routes[("GET", f"{API}/merge_requests/41/versions")] = PUSHED if versions is None else versions
    return routes


def night_of(inputs) -> Night:
    return Night(oncall=inputs.oncall, targets=inputs.targets, orders=inputs.orders,
                 orders_problems=inputs.orders_problems, signature=inputs.signature, ledger=Ledger())


def woken_for(inputs) -> tuple[str, ...]:
    alert = [Alert(key=NEW, value=0.079, at=NOW)]
    decision = triage(alert, night_of(inputs), inputs.metrics, NOW)
    assert isinstance(decision, Wake)
    return decision.reasons


def test_an_approval_after_the_last_push_signs_the_head_commit():
    for approved in ("2026-10-21T05:30:00.000Z", "2026-10-21T05:40:00.000Z"):  # at the push, or after it
        inputs, fake = load(open_request(approved), base_files("head41"))
        assert inputs.signature == Signature(method="approval", user="alex-velazquez",
                                             at=datetime.fromisoformat(approved), commit="head41", merge_request=41)
        assert inputs.orders is not None and inputs.orders_problems == ()
        assert fake.refs("ops/night-orders.yml") == ["head41"]


def test_an_approval_before_a_later_push_does_not_sign_and_the_relay_says_why():
    # Approved at 22:06, then a commit pushed at 22:30: the approval never saw what is now in the file.
    inputs, fake = load(open_request("2026-10-21T05:06:00.000Z"), base_files("head41"))
    assert inputs.signature is None and inputs.orders is None
    assert fake.refs("ops/night-orders.yml") == ["main"]  # the pushed file is not read as signed
    assert inputs.orders_problems == (STALE,)
    assert woken_for(inputs) == (f"No usable orders tonight ({STALE}).",)
    assert status_of(inputs, NOW)["problems"] == [STALE]


def test_with_an_older_merge_on_the_default_branch_the_page_still_says_why():
    yesterday = merged_by("alex-velazquez", "2026-10-20T05:00:00Z", iid=20, sha="old000")  # the night before
    inputs, _ = load(open_request("2026-10-21T05:06:00.000Z", merged=yesterday), base_files("old000"))
    assert inputs.signature.commit == "old000" and inputs.orders is not None
    assert inputs.orders_problems == (STALE,)
    assert woken_for(inputs) == (f"No usable orders tonight ({STALE}).",)
    assert status_of(inputs, NOW)["problems"] == [STALE, "The orders were signed outside tonight's window."]


def test_a_merge_signed_tonight_still_counts_when_a_newer_approval_is_too_old():
    tonight = merged_by("alex-velazquez", "2026-10-21T04:00:00Z", iid=20, sha="mrg000")  # 21:00 in Los Angeles
    inputs, _ = load(open_request("2026-10-21T05:06:00.000Z", merged=tonight), base_files("mrg000"))
    assert inputs.signature.commit == "mrg000" and inputs.orders_problems == ()
    assert status_of(inputs, NOW)["problems"] == []


def test_a_merge_request_with_no_version_for_the_commit_does_not_sign():
    for versions in ([], [{"id": 2, "head_commit_sha": "old41", "created_at": "2026-10-21T05:00:00.000Z"}]):
        inputs, _ = load(open_request("2026-10-21T05:40:00.000Z", versions=versions), base_files("head41"))
        assert inputs.signature is None
        assert inputs.orders_problems == ("!41 has no version at commit head41, so code cannot tell if it was "
                                          "approved after that commit",)


def test_an_approval_that_goes_too_old_after_the_ask_wakes_her_with_the_reason(oncall):
    # Asked at 03:12 while the orders were signed; a push before the answer means they no longer are.
    inputs, _ = load(open_request("2026-10-21T05:06:00.000Z"), base_files("head41"))
    alert = [Alert(key=NEW, value=0.079, at=at(oncall, "03:12"))]
    ask = Ask(eligible=(1,), checks={1: "new checkout errors above 5% for 5 minutes"})
    note = render_request(Request(order=1, fits_because="Only the new path fails.", declined_id=None,
                                  declined_why=None, page=(), suggest=None))
    result = check_request(note, ask, at(oncall, "03:12"), alert, night_of(inputs), inputs.metrics, at(oncall, "03:13"))
    assert isinstance(result, Wake) and result.reasons == (f"No usable orders tonight ({STALE}).",)


def test_a_countersign_approved_before_a_later_push_is_not_a_countersign():
    routes = {("GET", API): {"id": 123, "default_branch": "main"}, ("GET", f"{API}/repository/commits"): [],
              ("GET", f"{API}/merge_requests"): [{"iid": 52, "sha": "cs0002"}],
              ("GET", f"{API}/merge_requests/52/diffs"): [{"old_path": "ops/state.yml", "new_path": "ops/state.yml"}],
              ("GET", f"{API}/merge_requests/52/approvals"): {"approved_by": [
                  {"user": {"username": "alex-velazquez"}, "approved_at": "2026-10-21T14:42:00Z"}]},
              ("GET", f"{API}/merge_requests/52/versions"): [
                  {"head_commit_sha": "cs0002", "created_at": "2026-10-21T14:50:00Z"}]}
    fake = GitLabFake(routes, {("ops/state.yml", "cs0002"): "night: \"2026-10-20\"\n"})
    http = Http(httpx.Client(transport=httpx.MockTransport(fake)))
    sources = GitLabSources(GitLab(http, "https://gitlab.example", "123", "test-token"), http,
                            "https://shop.example/metrics.json")
    assert sources.state_file("alex-velazquez").signature is None
