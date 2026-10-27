"""Resource results count only when the same bounded demo outcome was completed."""

from copy import deepcopy
import subprocess

import pytest

from scripts import benchmark_resources as benchmark


def response():
    return {"label": "Demo data: test fixture", "choices": {"signed": True, "approved": True},
            "counts": dict(benchmark.EXPECTED_COUNTS), "signature": {"signed": True},
            "expiry": {"expired": True},
            "timeline": [{"kind": kind} for kind in ("acted", "recovered", "approved", "declined", "expired")],
            "morning": {"status": "merged", "choice": "keep_checkout", "kept": [1], "undone": [1]},
            "flags": {"after_morning": {"new_checkout": "off", "stock_from_cache": "off"}}}


def samples():
    outcome = benchmark.verify_response(response())
    return [{"mode": mode, "wall_ns": 100, "process_cpu_ns": 80, "response_bytes": 123,
             "response_sha256": "same", "verified_outcome": outcome,
             "cache_hits": int(mode == "warm"), "cache_misses": int(mode == "cold")}
            for mode in ("cold", "warm")]


@pytest.mark.parametrize("change", ["missing_recovery", "unexpired", "wrong_morning", "wrong_counts", "unlabelled"])
def test_incomplete_or_different_nights_cannot_be_counted_as_functional_units(change):
    payload = response()
    if change == "missing_recovery":
        payload["timeline"] = [event for event in payload["timeline"] if event["kind"] != "recovered"]
    elif change == "unexpired":
        payload["expiry"]["expired"] = False
    elif change == "wrong_morning":
        payload["flags"]["after_morning"]["new_checkout"] = "on"
    elif change == "wrong_counts":
        payload["counts"]["pages"] = 0
    else:
        payload["label"] = "Live production"
    with pytest.raises(ValueError):
        benchmark.verify_response(payload)


@pytest.mark.parametrize("change", ["bytes", "hash", "outcome", "cache", "missing_sample", "order"])
def test_faster_but_unequal_or_unproven_cached_results_are_rejected(change):
    found = deepcopy(samples())
    if change == "bytes":
        found[1]["response_bytes"] -= 1
    elif change == "hash":
        found[1]["response_sha256"] = "different"
    elif change == "outcome":
        found[1]["verified_outcome"] = {"completed_demo_nights": 0}
    elif change == "cache":
        found[1]["cache_hits"] = 0
    elif change == "missing_sample":
        found.pop()
    else:
        found.reverse()
    with pytest.raises(ValueError):
        benchmark.validate_samples(found, 1)


@pytest.mark.parametrize("repetitions,seconds", [(0, 60), (9, 60), (True, 60), (1, 0), (1, 121),
                                                (1, float("inf")), (1, float("nan")), (1, True)])
def test_unbounded_or_invalid_workloads_are_rejected_before_start(repetitions, seconds):
    with pytest.raises(ValueError):
        benchmark.benchmark(repetitions, seconds)


def test_worker_timeout_is_a_failed_report_with_no_resource_savings_claim(monkeypatch):
    monkeypatch.setattr(benchmark, "source_identity", lambda: {"commit": "demo", "content_sha256": "demo"})
    monkeypatch.setattr(benchmark, "environment", lambda: {"platform": "test"})

    def timeout(*args, **kwargs):
        assert 0 < kwargs["timeout"] <= benchmark.WORKER_SECONDS
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(benchmark.subprocess, "run", timeout)
    report = benchmark.benchmark(1, 1)
    assert not report["passed"] and report["samples"] == []
    assert report["error"]["type"] == "TimeoutExpired"
    assert "summary" not in report and "outcomes_equal" not in report
    assert report["carbon"] == {"status": "not_measured", "energy_kwh": None, "carbon_gco2e": None,
                                "sci": None, "reason": "No measured energy, grid intensity or embodied emissions "
                                "with provenance."}


def test_changed_source_invalidates_even_identical_completed_results(monkeypatch):
    identities = iter([{"commit": "before", "content_sha256": "before"},
                       {"commit": "after", "content_sha256": "after"}])
    monkeypatch.setattr(benchmark, "source_identity", lambda: next(identities))
    monkeypatch.setattr(benchmark, "environment", lambda: {"platform": "test"})
    import json
    result = subprocess.CompletedProcess([], 0, stdout=json.dumps({"samples": samples()}))
    monkeypatch.setattr(benchmark.subprocess, "run", lambda *args, **kwargs: result)
    report = benchmark.benchmark(1)
    assert not report["passed"] and "source content changed" in report["error"]["message"]
    assert "summary" not in report
