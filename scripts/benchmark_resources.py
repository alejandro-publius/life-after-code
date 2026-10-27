"""Bounded local resource measurements for identical completed demo-night responses.

Demo data and simulated external adapters only. This measures CPU, time and memory,
not energy, carbon, production traffic or live model use.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
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

ROOT = Path(__file__).resolve().parents[1]
MAX_REPETITIONS = 8
MAX_SECONDS = 120
WORKER_SECONDS = 30
EXPECTED_COUNTS = {"pages": 1, "automatic_incidents_handled": 1, "approved_actions": 1, "incidents": 2}


def source_identity() -> dict:
    paths = {Path(__file__).resolve(), ROOT / "relay/main.py", ROOT / "pyproject.toml", ROOT / "uv.lock"}
    paths.update((ROOT / "relay/nightorders").rglob("*.py"))
    for folder in (ROOT / "relay/nightorders/demo_story_data", ROOT / "demo/night-2026-10-20", ROOT / "ops"):
        paths.update(path for path in folder.rglob("*") if path.suffix in (".json", ".yml", ".yaml"))
    files = sorted(str(path.relative_to(ROOT)) for path in paths if path.is_file())
    digest = hashlib.sha256()
    for name in files:
        digest.update(name.encode() + b"\0" + (ROOT / name).read_bytes() + b"\0")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                            capture_output=True, text=True, timeout=5).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *files], cwd=ROOT,
                           check=True, capture_output=True, text=True, timeout=5).stdout
    return {"commit": commit, "content_sha256": digest.hexdigest(), "content_files": files,
            "includes_uncommitted_content": bool(dirty)}


def environment() -> dict:
    versions = {name: importlib.metadata.version(name) for name in ("fastapi", "starlette", "httpx", "pyyaml")}
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(), "executable": sys.executable,
            "logical_cpus": os.cpu_count(),
            "affinity_cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            "packages": versions}


def memory() -> dict:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    unit = "KiB" if sys.platform.startswith("linux") else "bytes" if sys.platform == "darwin" else "platform_native"
    peak_bytes = peak * 1024 if unit == "KiB" else peak if unit == "bytes" else None
    current = None
    if sys.platform.startswith("linux"):
        try:
            current = int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
        except (OSError, ValueError, IndexError):
            pass
    return {"current_rss_bytes": current, "peak_rss_bytes": peak_bytes,
            "peak_rss_native": peak, "peak_rss_native_unit": unit}


def verify_response(payload: dict) -> dict:
    """A faster incomplete or different result must not qualify as a functional unit."""
    if not payload.get("label", "").startswith("Demo data:"):
        raise ValueError("Response must identify its synthetic demo data")
    if payload.get("choices") != {"signed": True, "approved": True}:
        raise ValueError("Response has different bedtime or approval choices")
    if any(payload.get("counts", {}).get(key) != value for key, value in EXPECTED_COUNTS.items()):
        raise ValueError("Response has unexpected completed-night outcomes")
    if not payload.get("signature", {}).get("signed") or not payload.get("expiry", {}).get("expired"):
        raise ValueError("Night has not completed its signed authority and expiry")
    kinds = {event.get("kind") for event in payload.get("timeline", [])}
    if not {"acted", "recovered", "approved", "declined", "expired"} <= kinds:
        raise ValueError("Night lacks the required action, refusal or measured recovery evidence")
    morning = payload.get("morning", {})
    if (morning.get("status") != "merged" or morning.get("choice") != "keep_checkout"
            or not morning.get("kept") or not morning.get("undone")):
        raise ValueError("Morning has not completed the expected keep and restore")
    if payload.get("flags", {}).get("after_morning") != {"new_checkout": "off", "stock_from_cache": "off"}:
        raise ValueError("Morning flag outcome differs from the verified functional unit")
    return {"counts": {key: payload["counts"][key] for key in EXPECTED_COUNTS},
            "authority_expired": True, "morning_choice": "keep_checkout", "completed_demo_nights": 1}


def worker() -> dict:
    """One fresh process, one cold computation followed by its cached delivery."""
    sys.path.insert(0, str(ROOT / "relay"))
    name = "_nightorders_resource_relay"
    spec = importlib.util.spec_from_file_location(name, ROOT / "relay/main.py")
    relay = importlib.util.module_from_spec(spec)
    sys.modules[name] = relay
    spec.loader.exec_module(relay)
    from fastapi.responses import JSONResponse
    from nightorders import browser_demo

    relay.demo_replay.cache_clear()
    browser_demo.three_ways.cache_clear()
    browser_demo.permission_checks.cache_clear()
    samples = []
    for mode in ("cold", "warm"):
        before_cache = relay.demo_replay.cache_info()
        before_memory = memory()
        start_wall, start_cpu = time.perf_counter_ns(), time.process_time_ns()
        response = JSONResponse(relay.demo_replay(True, True, True)).body
        cpu_ns, wall_ns = time.process_time_ns() - start_cpu, time.perf_counter_ns() - start_wall
        after_memory = memory()
        after_cache = relay.demo_replay.cache_info()
        verified = verify_response(json.loads(response))
        samples.append({"mode": mode, "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
                        "rss_before": before_memory, "rss_after": after_memory,
                        "response_bytes": len(response), "response_sha256": hashlib.sha256(response).hexdigest(),
                        "cache_hits": after_cache.hits - before_cache.hits,
                        "cache_misses": after_cache.misses - before_cache.misses,
                        "verified_outcome": verified})
    validate_samples(samples, 1)
    return {"samples": samples}


def validate_samples(samples: list[dict], repetitions: int) -> None:
    if len(samples) != 2 * repetitions:
        raise ValueError("Incomplete cold/warm sample pairs")
    first = samples[0]
    for index, sample in enumerate(samples):
        mode = "cold" if index % 2 == 0 else "warm"
        if sample["mode"] != mode:
            raise ValueError("Sample order must be paired cold then warm")
        if (sample["response_sha256"], sample["response_bytes"], sample["verified_outcome"]) != (
                first["response_sha256"], first["response_bytes"], first["verified_outcome"]):
            raise ValueError("Cold and warm responses or verified outcomes are unequal")
        if (sample["cache_hits"], sample["cache_misses"]) != ((0, 1) if mode == "cold" else (1, 0)):
            raise ValueError("Cache evidence does not match the measured workload")
        if any(type(sample[key]) is not int or sample[key] < 0 for key in ("wall_ns", "process_cpu_ns")):
            raise ValueError("Invalid resource timing sample")


def benchmark(repetitions: int = 3, max_seconds: float = 60) -> dict:
    if type(repetitions) is not int or not 1 <= repetitions <= MAX_REPETITIONS:
        raise ValueError(f"repetitions must be an integer from 1 to {MAX_REPETITIONS}")
    if (type(max_seconds) not in (int, float) or not math.isfinite(max_seconds)
            or not 1 <= max_seconds <= MAX_SECONDS):
        raise ValueError(f"max_seconds must be finite and between 1 and {MAX_SECONDS}")
    started = time.monotonic()
    source = source_identity()
    report = {
        "schema": 1, "label": "DEMO DATA: local simulated adapters; no live external service or model calls.",
        "passed": False, "source": source, "environment": environment(),
        "functional_unit": "One serialized, completed and outcome-verified signed/approved demo-night response, "
                           "with keep_checkout=true. Warm samples deliver the previously computed night.",
        "boundary": "Actual relay demo_replay LRU call plus JSONResponse serialization. Validation, imports, "
                    "subprocess startup, HTTP, browser rendering, network and compression are outside timing.",
        "cold_definition": "Fresh Python process per pair; all three application replay caches cleared. "
                           "OS page caches are not cleared. Fixed comparisons and permission checks are included.",
        "ordering": "Sequential pairs: cold then warm, no parallel workers or discarded samples.",
        "limits": {"repetitions": repetitions, "max_repetitions": MAX_REPETITIONS,
                   "max_seconds": max_seconds, "worker_timeout_seconds": WORKER_SECONDS},
        "units": {"wall_ns": "nanoseconds", "process_cpu_ns": "nanoseconds", "response_bytes": "bytes",
                  "rss": "bytes after conversion; native ru_maxrss units are also recorded per sample"},
        "carbon": {"status": "not_measured", "energy_kwh": None, "carbon_gco2e": None, "sci": None,
                   "reason": "No measured energy, grid intensity or embodied emissions with provenance."},
        "samples": [],
        "limitations": [
            "Cached delivery is not a new independent night or a live agent run.",
            "Cold includes fixed comparison replays and permission checks needed by the response.",
            "Warm follows cold in each process; order, filesystem cache and host load can affect timings.",
            "Peak RSS is the process lifetime high-water mark, includes imports and cannot be subtracted "
            "to infer a warm-request allocation. Current RSS is available only where supported.",
            "Few local samples establish no production, energy, carbon or live model-token saving.",
        ],
    }
    try:
        for pair in range(repetitions):
            remaining = max_seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("Benchmark global deadline exhausted")
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker"],
                                    cwd=ROOT, capture_output=True, text=True, check=True,
                                    timeout=min(WORKER_SECONDS, remaining))
            samples = json.loads(result.stdout)["samples"]
            validate_samples(samples, 1)
            for sample in samples:
                sample["pair"] = pair + 1
                sample["sequence"] = len(report["samples"]) + 1
                report["samples"].append(sample)
        validate_samples(report["samples"], repetitions)
        after = source_identity()
        report["source_after"] = after
        if after["content_sha256"] != source["content_sha256"]:
            raise ValueError("Relevant source content changed during the measurement")
        if time.monotonic() - started > max_seconds:
            raise TimeoutError("Benchmark exceeded its global deadline")
        report["outcomes_equal"] = True
        report["summary"] = {}
        for mode in ("cold", "warm"):
            samples = [sample for sample in report["samples"] if sample["mode"] == mode]
            report["summary"][mode] = {"samples": len(samples), **{
                f"median_{key}": statistics.median(sample[key] for sample in samples)
                for key in ("wall_ns", "process_cpu_ns", "response_bytes")}}
        report["passed"] = True
    except (ValueError, KeyError, TimeoutError, subprocess.SubprocessError) as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    report["elapsed_seconds"] = round(time.monotonic() - started, 6)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--max-seconds", type=float, default=60)
    parser.add_argument("--out", type=Path, help="JSON report path outside the repository, or stdout if omitted")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        print(json.dumps(worker()))
        return 0
    try:
        report = benchmark(args.repetitions, args.max_seconds)
    except ValueError as error:
        parser.error(str(error))
    text = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
