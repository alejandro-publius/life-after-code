"""The sustainability benchmark measures the real replay, refuses to compare different outcomes and labels what it
records. Offline; the only numbers are test data or one quick in-process night."""

from __future__ import annotations

import io
import json
import math

from scripts import claude_sustainability_benchmark as bench


def test_the_functional_unit_is_deterministic_and_the_optimized_variant_changes_no_outcome():
    from nightorders import signals
    first = bench.fingerprint(bench.night_once())
    assert first == bench.fingerprint(bench.night_once())
    original = signals.Metrics.window
    try:
        bench.apply_variant("optimized")
        assert signals.Metrics.window is bench.optimized_window
        assert bench.fingerprint(bench.night_once()) == first
    finally:
        signals.Metrics.window = original


def test_a_variant_that_changes_a_decision_changes_the_fingerprint():
    from nightorders import signals
    original = signals.Metrics.window

    def shorter(self, key, now, minutes):  # drops the oldest minute: "for 5 minutes" becomes four
        return original(self, key, now, minutes)[1:]
    try:
        signals.Metrics.window = shorter
        broken = bench.fingerprint(bench.night_once())
    finally:
        signals.Metrics.window = original
    assert broken != bench.fingerprint(bench.night_once())


def test_the_counts_say_what_one_night_does_and_that_the_replies_are_recorded():
    counts = bench.counts()
    assert counts["ticks"] == 546 and counts["metrics_samples_stored"] == 546 * 11
    assert 2000 < counts["condition_evaluations"] < 4000
    assert counts["model_calls"] == 2 and counts["model_calls_budget_per_night"] == 3
    assert counts["model_calls_recorded_replies"] is True
    assert counts["answer_polls"] == 3 and counts["thumbs_up_polls"] == 2
    assert counts["http_requests"] == 0 and counts["retries"] == 0
    assert counts["goal_chars_sent"] > 500 and counts["reply_chars_received"] > 500
    assert counts["incidents_opened"] == 2 and counts["actions_applied"] == 2 and counts["restores"] == 2
    from nightorders import demo_night, watch
    assert not hasattr(demo_night.RecordingPorts, "calls")  # the counting port is gone again
    assert watch.condition_holds.__name__ == "condition_holds"


def test_a_child_measurement_has_timings_memory_and_a_fingerprint():
    record = bench.child("baseline")
    assert record["variant"] == "baseline" and len(record["fingerprint"]) == 64
    for phase in ("cold", "warm"):
        assert 0 < record[phase]["cpu_seconds"] < 5 and 0 < record[phase]["wall_seconds"] < 5
        assert record[phase]["user_seconds"] >= 0 and record[phase]["system_seconds"] >= 0
    assert record["python_peak_bytes_warm"] > 100_000 and record["process_peak_rss_bytes"] > 1_000_000
    assert record["import_seconds"] >= 0


def test_summary_statistics_and_the_interval():
    s = bench.summary([1.0, 2.0, 3.0, 4.0])
    assert (s["n"], s["mean"], s["median"], s["min"], s["max"]) == (4, 2.5, 2.5, 1.0, 4.0)
    assert math.isclose(s["stdev"], (5 / 3) ** 0.5)
    assert s["ci95_method"] == "t, df 3"
    assert math.isclose(s["ci95_high"] - s["ci95_low"], 2 * 3.182 * s["stdev"] / 2)
    one = bench.summary([2.0])
    assert one["stdev"] == 0.0 and math.isnan(one["ci95_low"])


def fake_record(variant: str, print_: str, cpu: float) -> dict:
    timing = {"wall_seconds": cpu, "cpu_seconds": cpu, "user_seconds": cpu, "system_seconds": 0.0}
    return {"variant": variant, "fingerprint": print_, "import_seconds": 0.01, "cold": dict(timing), "warm": dict(timing),
            "python_peak_bytes_warm": 500_000, "process_peak_rss_bytes": 30_000_000}


def test_different_outcomes_refuse_the_comparison(monkeypatch):
    monkeypatch.setattr(bench, "run_child", lambda variant: fake_record(variant, ("a" if variant == "baseline" else "b") * 64, 0.03))
    data = bench.benchmark(2, bench.VARIANTS, lambda text: None)
    assert data["outcomes_identical"] is False and data["comparison"] == {}
    text = bench.render(dict(data, counts=bench.counts()))
    assert "NO: comparison refused" in text


def test_identical_outcomes_are_compared_and_the_report_carries_its_labels(monkeypatch):
    calls = []

    def run_child(variant):
        calls.append(variant)
        return fake_record(variant, "c" * 64, 0.030 if variant == "baseline" else 0.028)
    monkeypatch.setattr(bench, "run_child", run_child)
    data = bench.benchmark(3, bench.VARIANTS, lambda text: None)
    assert calls == ["baseline", "optimized"] * 3  # interleaved
    assert data["outcomes_identical"] is True and data["runs_per_variant"] == 3
    saved = data["comparison"]["cold_cpu_seconds"]
    assert math.isclose(saved["saved_mean"], 0.002) and math.isclose(saved["saved_percent_of_mean"], 100 * 0.002 / 0.030)
    assert data["functional_unit"] == bench.FUNCTIONAL_UNIT and len(data["source_commit"]) in (0, 40)
    text = bench.render(dict(data, counts=bench.counts()))
    for label in ("recorded demo notes, not live model output", "no energy or carbon is measured here",
                  "post-submission measurement", "Baseline against optimized", "not a measured carbon reduction"):
        assert label in text, label


def test_the_command_line_writes_raw_records_results_and_the_report(tmp_path):
    out = tmp_path / "bench"
    text = io.StringIO()
    code = bench.main(["--runs", "1", "--out", str(out)], out=text)
    assert code == 0, text.getvalue()
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert results["outcomes_identical"] is True and results["runs_per_variant"] == 1
    assert "records" not in results and results["counts"]["model_calls"] == 2
    assert sorted(path.name.split("-", 1)[1] for path in (out / "raw").glob("*.json")) == ["baseline-01.json", "optimized-01.json"]
    assert (out / "RESULTS.md").read_text(encoding="utf-8").startswith("# Benchmark results (generated)")
    assert bench.main(["--runs", "0"], out=io.StringIO()) == 2


def test_the_committed_results_match_this_source_tree():
    """If the demo night or the decision code changes, the committed fingerprint goes stale: rerun the benchmark."""
    results = json.loads((bench.ROOT / "docs" / "claude" / "sustainability" / "results.json").read_text(encoding="utf-8"))
    assert results["functional_unit"] == bench.FUNCTIONAL_UNIT and results["outcomes_identical"] is True
    assert results["fingerprints"]["baseline"] == results["fingerprints"]["optimized"] == [bench.fingerprint(bench.night_once())]
    assert results["runs_per_variant"] >= 10
