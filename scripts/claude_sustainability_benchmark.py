"""A reproducible resource benchmark of one completed Night Orders night, through the real replay and decision code.

    uv run --locked python scripts/claude_sustainability_benchmark.py --runs 10 --out docs/claude/sustainability

Functional unit (R): one standard completed test night: the labelled demo night in demo/night-2026-10-20, signed and
with the fallback approved, replayed minute by minute through the same Watch class the relay runs (546 ticks), then
the morning countersign and the lease end, exactly what `python -m nightorders.demo_night` prints. The shop, its
faults and the agent's two replies are demo data (recorded notes); the decisions are the real code's.

Each repetition runs in a fresh child process and records wall time, CPU time (user and system), peak Python
allocations during the night, the child's peak resident set, the number of ticks, metrics samples, condition
evaluations, model calls, polls and port calls, and a fingerprint of every outcome. The optimized variant applies
one runtime patch (a proposed change to nightorders.signals.Metrics.window) inside the child only; its fingerprint
must equal the baseline's, or the comparison is refused. Nothing here measures energy or carbon: see SCI.md.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "relay")]

DEMO = ROOT / "demo" / "night-2026-10-20"
VARIANTS = ("baseline", "optimized")
FUNCTIONAL_UNIT = ("one standard completed test night: demo/night-2026-10-20, signed, fallback approved, replayed "
                   "through nightorders.demo_night.run, then countersign and lease_end (546 minute ticks, 22:00 to 07:05)")
COUNTED = ("open_incident", "note", "start_watch_flow", "request_note", "snapshot", "revision_exists", "apply",
           "restore", "page", "thumbs_up", "close_incident", "recent_log_lines", "holds", "shipped", "watch_note",
           "morning_push", "quiet_push")
# Student t critical values for a two-sided 95% interval, by degrees of freedom; 1.96 beyond the table.
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
       11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
       20: 2.086, 24: 2.064, 29: 2.045}


# The functional unit, and its fingerprint.

def night_once() -> dict:
    """One completed night, all in memory. Returns everything an outcome fingerprint needs."""
    from nightorders import demo_night
    from nightorders.dawn import render_watch_log
    ports, night = demo_night.run(DEMO)
    morning = demo_night.countersign(DEMO, ports, night)
    later = demo_night.lease_end(DEMO, ports, night)
    events = [{"at": e.at.isoformat(), "kind": e.kind, "text": e.text, "incident": e.incident, "order": e.order,
               "data": e.data} for e in night.ledger.events]
    return {"log": list(ports.log), "events": events, "watch_log": render_watch_log(night), "morning": morning,
            "later": later, "actions": list(ports.actions), "flags": dict(ports.shop.flags),
            "model_runs": night.ledger.model_runs(), "ports": ports, "night": night}


def fingerprint(outcome: dict) -> str:
    """SHA-256 of the night's observable outcome: every log line, ledger event, action, the watch log, the morning
    and the lease end. Two runs with the same fingerprint made the same decisions at the same times."""
    kept = {key: outcome[key] for key in ("log", "events", "watch_log", "morning", "later", "actions", "flags")}
    return hashlib.sha256(json.dumps(kept, sort_keys=True, default=str).encode("utf-8")).hexdigest()


# The proposed change, applied at runtime in the optimized child only. The file it belongs to is Codex's.

def optimized_window(self, key: str, now: datetime, minutes: int) -> list:
    """Metrics.window without re-normalising an already whole minute on every read: one dict lookup per minute
    of the window instead of a get() that calls minute() (a datetime.replace) each time. Same values, same order."""
    from nightorders.signals import minute
    series = self._series.get(key)
    end = minute(now)
    if not series:
        return [None] * minutes
    return [series.get(end - timedelta(minutes=i)) for i in range(minutes, 0, -1)]


def apply_variant(name: str) -> None:
    if name == "baseline":
        return
    if name == "optimized":
        from nightorders import signals
        signals.Metrics.window = optimized_window
        return
    raise ValueError(f"unknown variant {name}")


# Counting what the night does, with a port that counts every call (one extra dict increment per call).

def counting_ports(base: type) -> type:
    class Counting(base):  # type: ignore[misc, valid-type]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.calls: Counter = Counter()
    for name in COUNTED:
        def make(method_name: str) -> Callable:
            original = getattr(base, method_name)

            def method(self, *args, **kwargs):
                self.calls[method_name] += 1
                if method_name == "start_watch_flow":
                    self.calls["goal_chars"] += len(str(args[1]))
                return original(self, *args, **kwargs)
            return method
        setattr(Counting, name, make(name))
    return Counting


def counts() -> dict:
    """What one night does, counted: ticks, samples, condition evaluations, model calls, polls, port calls."""
    from nightorders import decide, demo_night, watch
    from nightorders.orders import load_yaml
    # watch.py and decide.py bind condition_holds by name at import, so the counter goes where they look.
    original_ports, original_holds = demo_night.RecordingPorts, watch.condition_holds
    evaluations = Counter()

    def counted_holds(condition, metrics, now):
        evaluations["condition_holds"] += 1
        return original_holds(condition, metrics, now)
    demo_night.RecordingPorts = counting_ports(original_ports)
    watch.condition_holds = counted_holds
    decide_original = getattr(decide, "condition_holds", None)
    if decide_original is not None:
        decide.condition_holds = counted_holds
    try:
        outcome = night_once()
    finally:
        demo_night.RecordingPorts, watch.condition_holds = original_ports, original_holds
        if decide_original is not None:
            decide.condition_holds = decide_original
    ports, night = outcome["ports"], outcome["night"]
    scenario = load_yaml(DEMO / "scenario.yml")
    start, end = datetime.fromisoformat(scenario["start"]), datetime.fromisoformat(scenario["end"])
    ticks = int((end - start).total_seconds() // 60) + 1
    calls = dict(ports.calls)
    replies = sum(len(text) for _, text in ports.notes.values())
    return {
        "ticks": ticks,
        "minutes_of_shop_metrics": ticks,
        "metrics_samples_stored": ticks * 11,  # DemoShop.minute_metrics writes 11 keys a minute
        "condition_evaluations": evaluations["condition_holds"],
        "model_calls": calls.get("start_watch_flow", 0),
        "model_calls_budget_per_night": night.oncall.model_runs_per_night,
        "model_calls_recorded_replies": True,
        "goal_chars_sent": calls.pop("goal_chars", 0),
        "reply_chars_received": replies,
        "answer_polls": calls.get("request_note", 0),
        "thumbs_up_polls": calls.get("thumbs_up", 0),
        "incidents_opened": calls.get("open_incident", 0),
        "actions_applied": calls.get("apply", 0),
        "restores": calls.get("restore", 0),
        "port_calls": calls,
        "ledger_events": len(night.ledger.events),
        "retries": 0,  # the replay's ports never fail, so nothing is retried; production retries are the relay's
        "http_requests": 0,  # the replay makes none; each poll above would be one GitLab request in production
    }


# One child measurement.

def child(variant: str) -> dict:
    import_wall = time.perf_counter()
    from nightorders import demo_night  # noqa: F401  (imports and YAML parsers are part of the cold cost)
    import_wall = time.perf_counter() - import_wall
    apply_variant(variant)  # after the imports are timed, so both variants pay the same import cost
    record: dict[str, Any] = {"variant": variant, "pid": os.getpid(), "import_seconds": round(import_wall, 6)}
    for label in ("cold", "warm"):
        ru0 = resource.getrusage(resource.RUSAGE_SELF)
        wall0, cpu0 = time.perf_counter(), time.process_time()
        outcome = night_once()
        wall, cpu = time.perf_counter() - wall0, time.process_time() - cpu0
        ru1 = resource.getrusage(resource.RUSAGE_SELF)
        record[label] = {"wall_seconds": round(wall, 6), "cpu_seconds": round(cpu, 6),
                         "user_seconds": round(ru1.ru_utime - ru0.ru_utime, 6),
                         "system_seconds": round(ru1.ru_stime - ru0.ru_stime, 6)}
        record.setdefault("fingerprint", fingerprint(outcome))
        if fingerprint(outcome) != record["fingerprint"]:
            raise RuntimeError("the warm run's outcome differs from the cold run's")
    tracemalloc.start()
    night_once()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    record["python_peak_bytes_warm"] = peak
    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record["process_peak_rss_bytes"] = maxrss if sys.platform == "darwin" else maxrss * 1024
    return record


# The parent: repetitions, statistics, records.

def machine() -> dict:
    info = {"platform": platform.platform(), "python": sys.version.split()[0], "cpu": platform.processor() or "",
            "cores": os.cpu_count()}
    if sys.platform == "darwin":
        for key, name in (("machdep.cpu.brand_string", "cpu"), ("hw.memsize", "memory_bytes")):
            try:
                value = subprocess.run(["sysctl", "-n", key], capture_output=True, text=True, timeout=5).stdout.strip()
                info[name] = int(value) if name == "memory_bytes" else value
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
        try:
            battery = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5).stdout
            info["power_source"] = " ".join(battery.split("\n")[0].split()) if battery else ""
            info["battery"] = " ".join(battery.split("\n")[1].split()[2:4]) if battery.count("\n") > 1 else ""
        except (OSError, subprocess.SubprocessError):
            pass
    return info


def source_commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True,
                              timeout=10, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def summary(values: list[float]) -> dict:
    n = len(values)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if n > 1 else 0.0
    df = n - 1
    t = T95.get(df) or (T95[max(k for k in T95 if k <= df)] if df > 1 else T95[1]) if df < 30 else 1.96
    half = t * sd / math.sqrt(n) if n > 1 else float("nan")
    return {"n": n, "mean": mean, "stdev": sd, "median": statistics.median(values), "min": min(values),
            "max": max(values), "ci95_low": mean - half, "ci95_high": mean + half,
            "ci95_method": f"t, df {df}" if df < 30 else "normal 1.96"}


def run_child(variant: str) -> dict:
    command = [sys.executable, str(Path(__file__).resolve()), "--child", "--variant", variant]
    done = subprocess.run(command, capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    if done.returncode != 0:
        raise RuntimeError(f"child {variant} failed: {done.stderr.strip()[-600:]}")
    return json.loads(done.stdout)


def benchmark(runs: int, variants: tuple[str, ...], say: Callable[[str], None]) -> dict:
    records: list[dict] = []
    for index in range(runs):
        for variant in variants:  # interleaved, so drift in the machine falls on both variants alike
            record = run_child(variant)
            record["run"] = index + 1
            records.append(record)
            say(f"run {index + 1}/{runs} {variant}: cold {record['cold']['wall_seconds'] * 1000:.1f} ms wall, "
                f"{record['cold']['cpu_seconds'] * 1000:.1f} ms cpu; warm {record['warm']['cpu_seconds'] * 1000:.1f} ms cpu")
    prints = {variant: {r["fingerprint"] for r in records if r["variant"] == variant} for variant in variants}
    baseline = prints.get("baseline") or next(iter(prints.values()))
    identical = all(p == baseline and len(p) == 1 for p in prints.values())
    results: dict[str, Any] = {}
    for variant in variants:
        mine = [r for r in records if r["variant"] == variant]
        results[variant] = {}
        for phase in ("cold", "warm"):
            for metric in ("wall_seconds", "cpu_seconds", "user_seconds", "system_seconds"):
                results[variant][f"{phase}_{metric}"] = summary([r[phase][metric] for r in mine])
        results[variant]["import_seconds"] = summary([r["import_seconds"] for r in mine])
        results[variant]["python_peak_bytes_warm"] = summary([float(r["python_peak_bytes_warm"]) for r in mine])
        results[variant]["process_peak_rss_bytes"] = summary([float(r["process_peak_rss_bytes"]) for r in mine])
        results[variant]["fingerprints"] = sorted(prints[variant])
    comparison = {}
    if identical and "baseline" in results and "optimized" in results:
        for key in ("cold_cpu_seconds", "warm_cpu_seconds", "cold_wall_seconds", "warm_wall_seconds"):
            b, o = results["baseline"][key]["mean"], results["optimized"][key]["mean"]
            comparison[key] = {"baseline_mean": b, "optimized_mean": o, "saved_mean": b - o,
                               "saved_percent_of_mean": (b - o) / b * 100 if b else float("nan"),
                               "ci_overlap": not (results["optimized"][key]["ci95_high"] < results["baseline"][key]["ci95_low"])}
    return {"version": 1, "functional_unit": FUNCTIONAL_UNIT, "source_commit": source_commit(),
            "measured_at": datetime.now(timezone.utc).isoformat(), "machine": machine(), "runs_per_variant": runs,
            "variants": list(variants), "outcomes_identical": identical, "fingerprints": {k: sorted(v) for k, v in prints.items()},
            "results": results, "comparison": comparison, "records": records,
            "labels": ["demo data: simulated shop, planted faults, recorded model replies; real decision code",
                       "no energy or carbon is measured here; CPU and wall seconds, memory and counts only",
                       "post-submission measurement: these numbers did not exist before the 27 Oct 2026 deadline"]}


def write_outputs(out: Path, data: dict, count: dict) -> list[Path]:
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    written = []
    stamp = data["measured_at"].replace(":", "").replace("-", "")[:15]
    for record in data["records"]:
        path = raw / f"{stamp}-{record['variant']}-{record['run']:02d}.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    data = dict(data, counts=count)
    (out / "results.json").write_text(json.dumps({k: v for k, v in data.items() if k != "records"}, indent=2) + "\n",
                                      encoding="utf-8")
    written.append(out / "results.json")
    (out / "RESULTS.md").write_text(render(data), encoding="utf-8")
    written.append(out / "RESULTS.md")
    return written


def ms(stat: dict) -> str:
    return f"{stat['mean'] * 1000:.2f} ms (sd {stat['stdev'] * 1000:.2f}, 95% CI {stat['ci95_low'] * 1000:.2f} to {stat['ci95_high'] * 1000:.2f}, min {stat['min'] * 1000:.2f}, max {stat['max'] * 1000:.2f})"


def mib(stat: dict) -> str:
    return f"{stat['mean'] / 1048576:.2f} MiB (min {stat['min'] / 1048576:.2f}, max {stat['max'] / 1048576:.2f})"


def render(data: dict) -> str:
    m, c = data["machine"], data["counts"]
    lines = ["# Benchmark results (generated)", "",
             f"Generated by `scripts/claude_sustainability_benchmark.py` at {data['measured_at']} from source commit "
             f"`{data['source_commit'][:12]}`. {data['runs_per_variant']} runs per variant, interleaved, each in a fresh "
             "child process. Post-submission measurement.", "",
             f"Functional unit: {data['functional_unit']}.", "",
             f"Machine: {m.get('cpu', '')}, {m.get('cores')} cores, "
             f"{(m.get('memory_bytes') or 0) / 1073741824:.0f} GiB, {m.get('platform', '')}, Python {m.get('python', '')}. "
             f"Power: {m.get('power_source', 'unknown')}" + (f", battery {m['battery']}" if m.get("battery") else "") + ".", "",
             "Labels: " + "; ".join(data["labels"]) + ".", "",
             "## What one night does (counted, baseline)", "",
             "| Count | Value |", "|---|---|",
             f"| Minute ticks | {c['ticks']} |",
             f"| Metrics samples stored | {c['metrics_samples_stored']} |",
             f"| Alert condition evaluations | {c['condition_evaluations']} |",
             f"| Model calls (watch flow starts) | {c['model_calls']} of a budget of {c['model_calls_budget_per_night']} per night; the replies are recorded demo notes, not live model output |",
             f"| Characters sent in goals / received in replies | {c['goal_chars_sent']} / {c['reply_chars_received']} (no provider token counts exist for recorded replies) |",
             f"| Polls for the agent's answer | {c['answer_polls']} (each would be one GitLab notes request in production) |",
             f"| Polls for a thumbs-up | {c['thumbs_up_polls']} (each would be one GitLab reactions request in production) |",
             f"| Incidents opened / actions applied / restores | {c['incidents_opened']} / {c['actions_applied']} / {c['restores']} |",
             f"| Retries / HTTP requests in the replay | {c['retries']} / {c['http_requests']} (the replay's ports never fail and never call out) |",
             f"| Ledger events | {c['ledger_events']} |", "",
             f"Outcomes identical across every run and variant: **{'yes' if data['outcomes_identical'] else 'NO: comparison refused'}** "
             f"(fingerprint{'s' if sum(len(v) for v in data['fingerprints'].values()) > 1 else ''} "
             + ", ".join(f"{k}: {', '.join(p[:12] for p in v)}" for k, v in data["fingerprints"].items()) + ").", ""]
    for variant in data["variants"]:
        r = data["results"][variant]
        lines += [f"## {variant}", "", "| Measure | Value |", "|---|---|",
                  f"| Cold night, wall | {ms(r['cold_wall_seconds'])} |",
                  f"| Cold night, CPU (user + system) | {ms(r['cold_cpu_seconds'])} |",
                  f"| Warm night, wall | {ms(r['warm_wall_seconds'])} |",
                  f"| Warm night, CPU | {ms(r['warm_cpu_seconds'])} |",
                  f"| Imports before the night | {ms(r['import_seconds'])} |",
                  f"| Peak Python allocations during a warm night | {mib(r['python_peak_bytes_warm'])} |",
                  f"| Child process peak resident set | {mib(r['process_peak_rss_bytes'])} |", ""]
    if data["comparison"]:
        lines += ["## Baseline against optimized", "", "| Measure | Baseline mean | Optimized mean | Saved | 95% CIs overlap |",
                  "|---|---|---|---|---|"]
        for key, cmp in data["comparison"].items():
            lines.append(f"| {key.replace('_', ' ')} | {cmp['baseline_mean'] * 1000:.2f} ms | {cmp['optimized_mean'] * 1000:.2f} ms | "
                         f"{cmp['saved_mean'] * 1000:.2f} ms ({cmp['saved_percent_of_mean']:.0f}% of the mean) | "
                         f"{'yes' if cmp['ci_overlap'] else 'no'} |")
        lines += ["", "A saving whose confidence intervals overlap is not established by this many runs. Fewer CPU "
                  "milliseconds is a resource saving, not a measured carbon reduction: see SCI.md.", ""]
    return "\n".join(lines)


def main(argv=None, *, out=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=10, help="repetitions per variant (each a fresh process)")
    parser.add_argument("--variant", choices=VARIANTS, action="append", help="repeat to choose; default both")
    parser.add_argument("--out", type=Path, help="directory for raw records, results.json and RESULTS.md")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--counts", action="store_true", help="print what one night does, counted, and exit")
    args = parser.parse_args(argv)
    out = sys.stdout if out is None else out
    if args.child:
        print(json.dumps(child(args.variant[0] if args.variant else "baseline")))
        return 0
    if args.counts:
        print(json.dumps(counts(), indent=2), file=out)
        return 0
    if args.runs < 1 or args.runs > 200:
        print("Choose between 1 and 200 runs.", file=out)
        return 2
    variants = tuple(dict.fromkeys(args.variant)) if args.variant else VARIANTS
    data = benchmark(args.runs, variants, lambda text: print(text, file=out))
    count = counts()
    if not data["outcomes_identical"]:
        print("Outcomes differ between runs or variants; the comparison is refused.", file=out)
    if args.out:
        written = write_outputs(args.out, data, count)
        print(f"wrote {len(written)} files under {args.out}", file=out)
    else:
        print(render(dict(data, counts=count)), file=out)
    return 0 if data["outcomes_identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
