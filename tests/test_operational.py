"""Operational guarantees through the real authenticated relay, using labelled simulated adapters."""

from time import monotonic

import pytest

from nightorders.operational import verify, verify_case


@pytest.fixture(scope="module")
def report():
    result = verify()
    failures = [(case["case"], case.get("error")) for case in result["cases"] if not case["passed"]]
    assert result["passed"], failures
    return {case["case"]: case for case in result["cases"]}


def test_signed_night_uses_http_authentication_and_persisted_lease(report):
    case = report["signed_approved"]
    assert case["http_statuses"]["401"] == case["http_statuses"]["409"] == 1
    assert case["http_statuses"]["200"] >= 546
    assert case["counts"]["approved"] == case["counts"]["acted"] == case["counts"]["recovered"] == 1
    assert case["counts"]["declined"] == case["counts"]["expired"] == 1


def test_countersign_parser_uses_actual_signer_and_exact_signed_file(report):
    case = report["signed_approved"]
    morning = case["morning"]
    assert morning["wrong_signer_refused"]["user"] == "demo-wrong-signer"
    assert morning["wrong_signer_refused"]["problems"]
    assert morning["authorized"]["user"] == "alex-velazquez"
    assert morning["authorized"]["kept"] and morning["authorized"]["restored"]
    refs = {request["ref"] for request in morning["signature_reads"] if request["path"].endswith("/raw")}
    assert {"demo-wrong-signature", "demo-authorized-signature"} <= refs
    restored = [a for a in case["actions"] if "restored_to" in a]
    assert len(restored) == 1 and restored[0]["restored_to"]["value"] == "off"
    assert case["final_flags"] == {"new_checkout": "off", "stock_from_cache": "off"}


def test_lost_response_keeps_original_snapshot_across_cold_restart_and_morning(report):
    case = report["interrupted_action"]
    assert case["http_statuses"]["500"] == 1
    assert case["cold_starts"] >= 4
    failed = case["interruption"]["failed_event"]
    assert failed["data"]["before"] == {
        "kind": "flag", "flag": "new_checkout", "environment": "production", "value": "on"}
    assert case["interruption"]["flags_after_lost_response"]["new_checkout"] == "off"
    assert failed in case["persisted_state"]["watch"]["ledger"]
    changes = [a for a in case["actions"] if a["changed"] and a["action"].get("flag") == "new_checkout"]
    assert len(changes) == 2
    assert "restored_to" not in changes[0] and changes[1]["restored_to"]["value"] == "on"
    assert case["final_flags"] == {"new_checkout": "on", "stock_from_cache": "off"}
    assert len(case["morning"]["authorized"]["restored"]) == 2


def test_missing_authority_or_traffic_never_becomes_an_action(report):
    for name in ("unsigned", "insufficient_traffic"):
        assert report[name]["actions"] == []
        assert report[name]["counts"]["woke"] == 2
    assert report["missing_approval"]["counts"]["approved"] == 0
    assert all(a["action"].get("flag") != "stock_from_cache" for a in report["missing_approval"]["actions"])
    reasons = [reason for event in report["insufficient_traffic"]["ledger"]
               for reason in event["data"].get("reasons", [])]
    assert any("too few to judge" in reason for reason in reasons)


def test_recheck_observes_the_whole_service_and_pages_after_an_unhelpful_action(report):
    case = report["failed_recovery"]
    assert case["counts"]["acted"] == 1 and case["counts"]["recovered"] == 0
    action = next(event for event in case["ledger"] if event["kind"] == "acted")
    page = case["failed_recovery_page"]
    assert action["incident"] == page["incident"] and page["at"] > action["at"]
    assert case["persisted_state"]["watch"]["ledger"] == case["ledger"]


def test_exhausted_global_budget_fails_before_any_authenticated_action(tmp_path):
    case = verify_case("signed_approved", tmp_path, deadline=monotonic() - 1)
    assert not case["passed"] and case["error"]["type"] == "TimeoutError"
    assert case["requests"] == 0 and case["actions"] == []


@pytest.mark.parametrize("budget", [True, 0, -1, 31, float("nan"), float("inf")])
def test_replay_budget_cannot_be_unbounded(budget):
    from nightorders.demo_night import run

    with pytest.raises(ValueError, match="max_seconds"):
        run("unused", max_seconds=budget)
