"""Bounded offline verification of the real HTTP tick, persistence and morning loop.

DEMO DATA: external adapters, people, faults, signatures and model replies are simulated.
HTTP authentication, FileStore leases, Watch decisions and countersign parsing are real code.
Nothing contacts GitLab, Duo, Cloud Run, a payment service or an on-call person.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from functools import lru_cache
from time import monotonic

import httpx
import yaml
from fastapi.testclient import TestClient

from . import demo_night
from .gitlab_ports import GitLab, Http
from .orders import load_yaml
from .signals import Metrics
from .sources import GitLabSources, Inputs
from .state import FileStore

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "demo" / "night-2026-10-20"
LABEL = "DEMO DATA: simulated external adapters; real relay HTTP, persistence and decision code."
CASES = ("signed_approved", "unsigned", "missing_approval", "insufficient_traffic",
         "failed_recovery", "interrupted_action")
MAX_CASE_REQUESTS = demo_night.MAX_DEMO_STEPS + 12
MAX_TOTAL_SECONDS = 90
MAX_CASE_SECONDS = 30
DEMO_KEY = "operational-verification-only"


@lru_cache(maxsize=1)
def relay_module():
    """Load the application without depending on test modules or the shop's main.py."""
    name = "_nightorders_operational_relay"
    spec = importlib.util.spec_from_file_location(name, ROOT / "relay" / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source_identity() -> dict:
    """The commit plus content digest identify dirty and committed verification code alike."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, check=True, timeout=5).stdout.strip()
    paths = [ROOT / "relay" / "main.py", ROOT / "scripts" / "verify_night.py"]
    for folder in (ROOT / "relay" / "nightorders", FIXTURE, ROOT / "ops"):
        paths.extend(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                     and "output" not in p.parts)
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        digest.update(str(path.relative_to(ROOT)).encode() + b"\0" + path.read_bytes() + b"\0")
    return {"commit": commit, "content_sha256": digest.hexdigest(),
            "content_scope": "relay/main.py, relay/nightorders, demo fixture, ops, scripts/verify_night.py"}


class SimulatedPorts(demo_night.RecordingPorts):
    """Only external effects are simulated; the relay reconstructs this adapter every tick."""

    def saved(self):
        return {"asked_at": {str(k): v.isoformat() for k, v in self.asked_at.items()},
                "next_incident": self.next_incident}

    def start_dawn_flow(self, goal, at):
        self.log.append(f"{self._t(at)}  recorded dawn request (demo, no API call): {goal}")

    def apply(self, action, at):
        change = super().apply(action, at)
        if self.disruption["armed"] and action.flag == "new_checkout":
            self.disruption["armed"] = False
            error = httpx.ReadTimeout("Simulated response lost after the flag changed")
            error.before = change.before
            raise error
        return change


class CountersignServer:
    """GitLab API fixtures read by the actual GitLabSources signature and YAML parsers."""

    def __init__(self):
        self.signer = None
        self.at = None
        self.data = {"flags": [], "services": []}
        self.commit = "demo-no-countersign"
        self.reads = []

    def __call__(self, request):
        self.reads.append({"method": request.method, "path": request.url.path,
                           "ref": request.url.params.get("ref")})
        suffix = request.url.path.removeprefix("/api/v4/projects/123")
        answer = None
        if suffix == "":
            answer = {"id": 123, "default_branch": "main"}
        elif suffix == "/repository/commits":
            answer = [{"id": self.commit}] if self.signer else []
        elif suffix == f"/repository/commits/{self.commit}/merge_requests":
            answer = [{"iid": 52, "target_branch": "main"}]
        elif suffix == "/merge_requests/52":
            answer = {"iid": 52, "state": "merged", "merge_user": {"username": self.signer},
                      "merged_at": self.at.isoformat()}
        elif suffix == "/merge_requests":
            answer = []
        elif suffix == "/repository/files/ops/state.yml/raw":
            return httpx.Response(200, text=yaml.safe_dump(self.data))
        return httpx.Response(200 if answer is not None else 404, json=answer or [])


class RelayNight:
    def __init__(self, night, ports, rules, directory, case, deadline, standing=False):
        self.night, self.world, self.rules = night, ports, rules
        self.directory, self.case, self.standing = directory, case, standing
        self.deadline = deadline
        self.metrics = Metrics()
        self.now = datetime.fromisoformat(load_yaml(FIXTURE / "scenario.yml")["start"]).replace(
            tzinfo=night.oncall.timezone)
        self.requests = 0
        self.minute_steps = 0
        self.cold_starts = 0
        self.statuses = {}
        self.checks = []
        self.interruption = None
        self.server = CountersignServer()
        self.gitlab_client = httpx.Client(transport=httpx.MockTransport(self.server))
        http = Http(self.gitlab_client)
        self.countersign_source = GitLabSources(
            GitLab(http, "https://gitlab.invalid", "123", "demo-placeholder"), http,
            "https://shop.invalid/metrics.json")
        self.client = None
        self.reconstruct()

    def check_boundaries(self):
        self.check("HTTP rejects a wrong key", self.request(key="wrong").status_code == 401)
        self.check("unauthorized request creates no state", self.store.load()[0] is None)
        token = self.store.acquire(self.now)
        try:
            self.check("HTTP refuses a competing lease", self.request().status_code == 409)
        finally:
            self.store.release(token)

    def check(self, name, condition):
        self.checks.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    def reconstruct(self):
        if self.client:
            self.client.close()
        self.store = FileStore(self.directory / "state.json")
        main = relay_module()

        def make_ports(saved):
            adapter = copy.copy(self.world)
            adapter.asked_at = {int(k): datetime.fromisoformat(v) for k, v in saved.get("asked_at", {}).items()}
            adapter.next_incident = saved.get("next_incident", 1)
            return adapter

        app = main.create_app(
            make_store=lambda config: self.store,
            make_relay=lambda config, store: main.Relay(
                sources=self, store=store, make_ports=make_ports, pager=lambda *args, **kwargs: None,
                watch_issue=7, standing=self.standing),
            clock=lambda: self.now, page_cache_seconds=0,
            config_factory=lambda: main.Config.from_env({"RELAY_KEY": DEMO_KEY}))
        self.client = TestClient(app)
        self.cold_starts += 1

    def request(self, key=DEMO_KEY):
        if monotonic() >= self.deadline:
            raise TimeoutError("Operational verification exceeded its time budget")
        self.requests += 1
        if self.requests > MAX_CASE_REQUESTS:
            raise TimeoutError("Operational case exceeded its HTTP request budget")
        response = self.client.post("/tick", headers={"X-Relay-Key": key})
        self.statuses[str(response.status_code)] = self.statuses.get(str(response.status_code), 0) + 1
        return response

    def load(self, now):
        night = self.night
        return Inputs(oncall=night.oncall, targets=night.targets, rules=self.rules, orders=night.orders,
                      orders_problems=night.orders_problems, signature=night.signature, metrics=self.metrics)

    def state_file(self, user):
        return self.countersign_source.state_file(user)

    def document(self):
        return self.store.load()[0]

    def tick(self, metrics, now):
        self.minute_steps += 1
        self.metrics, self.now = metrics, now
        response = self.request()
        if response.status_code == 500 and self.case == "interrupted_action" and self.interruption is None:
            doc = self.document()
            failed = [e for e in doc["watch"]["ledger"] if e["kind"] == "failed"]
            self.check("interrupted action snapshot persisted", bool(failed) and
                       failed[-1]["data"]["before"]["value"] == "on")
            self.check("interrupted response releases the lease", not self.store.lease_path.exists())
            self.interruption = {"at": now.isoformat(), "failed_event": failed[-1],
                                 "flags_after_lost_response": dict(self.world.shop.flags),
                                 "state_sha256": hashlib.sha256(self.store.path.read_bytes()).hexdigest()}
            self.reconstruct()
            self.check("new FileStore reloads the same interrupted state", self.document() == doc)
        else:
            self.check_http(response)

    @staticmethod
    def check_http(response):
        if response.status_code != 200:
            raise AssertionError(f"Unexpected tick HTTP {response.status_code}: {response.text}")

    def morning(self, restore_all=False):
        before = len(self.world.actions)
        self.reconstruct()
        self.now += timedelta(minutes=5)
        self.server.data = ({"night": self.night.orders.night.isoformat(), "flags": [], "services": []}
                            if restore_all else load_yaml(FIXTURE / "countersign.yml")["state"])
        self.server.at = self.now - timedelta(minutes=1)
        self.server.signer = "demo-wrong-signer"
        self.server.commit = "demo-wrong-signature"
        self.check_http(self.request())
        wrong = copy.deepcopy(self.document()["relay"]["dawn"].get("refused"))
        self.check("wrong countersigner makes no change", len(self.world.actions) == before and
                   wrong is not None and bool(wrong["problems"]))
        self.now += timedelta(minutes=4)
        self.server.signer = self.night.oncall.user
        self.server.commit = "demo-authorized-signature"
        self.server.at = self.now - timedelta(minutes=1)
        self.check_http(self.request())
        result = copy.deepcopy(self.document()["relay"]["dawn"]["countersign"])
        self.check("authorized countersign applied", result is not None and not result["problems"])
        expected = {"new_checkout": "on" if restore_all else "off", "stock_from_cache": "off"}
        self.check("morning restored the exact earlier values", self.world.shop.flags == expected)
        count = len(self.world.actions)
        self.reconstruct()
        self.now += timedelta(minutes=4)
        self.check_http(self.request())
        self.check("repeated morning tick is idempotent after restart", len(self.world.actions) == count and
                   self.document()["relay"]["dawn"]["countersign"] == result)
        return {"wrong_signer_refused": wrong, "authorized": result,
                "signature_reads": self.server.reads, "actions_after_morning": count}

    def close(self):
        if self.client:
            self.client.close()
        self.gitlab_client.close()


def verify_case(case: str, directory: Path, deadline: float | None = None) -> dict:
    if case not in CASES:
        raise ValueError(f"Unknown operational case: {case}")
    started = monotonic()
    deadline = min(deadline if deadline is not None else started + MAX_CASE_SECONDS, started + MAX_CASE_SECONDS)
    holder = []

    def ports_factory(**kwargs):
        ports = SimulatedPorts(**kwargs)
        ports.disruption = {"armed": case == "interrupted_action"}
        if case == "insufficient_traffic":
            ports.shop.per_minute = 2
        return ports

    def watch_factory(night, ports, rules, standing=False):
        driver = RelayNight(night, ports, rules, directory, case, deadline, standing)
        holder.append(driver)
        driver.check_boundaries()
        return driver

    result = {"case": case, "passed": False, "label": LABEL}
    try:
        ports, _ = demo_night.run(FIXTURE, signed=case != "unsigned", approved=case != "missing_approval",
                                 standing=case == "failed_recovery", ports_factory=ports_factory,
                                 watch_factory=watch_factory, max_seconds=MAX_CASE_SECONDS)
        driver = holder[0]
        ledger = copy.deepcopy(driver.document()["watch"]["ledger"])
        kinds = {kind: [e for e in ledger if e["kind"] == kind]
                 for kind in ("woke", "acted", "approved", "recovered", "declined", "failed", "expired")}
        driver.check("authority expires", len(kinds["expired"]) == 1)
        if case == "signed_approved":
            driver.check("signed night has one page, approved action and recovered order",
                         [len(kinds[k]) for k in ("woke", "approved", "acted", "recovered")] == [1, 1, 1, 1])
            driver.check("recorded model can decline eligible numbers", len(kinds["declined"]) == 1)
        elif case in ("unsigned", "insufficient_traffic"):
            driver.check("permission or traffic cannot be bypassed", not ports.actions and not kinds["acted"]
                         and not kinds["approved"] and bool(kinds["woke"]))
        elif case == "missing_approval":
            driver.check("suggestion without approval does not act", not kinds["approved"] and
                         all(a["action"].get("flag") != "stock_from_cache" for a in ports.actions))
        elif case == "failed_recovery":
            acted = kinds["acted"][0]
            pages = [e for e in kinds["woke"] if e["incident"] == acted["incident"] and e["at"] > acted["at"]]
            driver.check("failed whole-service recheck pages instead of claiming recovery", bool(pages) and
                         not any(e["incident"] == acted["incident"] for e in kinds["recovered"]))
            result["failed_recovery_page"] = pages[0]
        else:
            driver.check("lost response observed with persisted pre-action snapshot", driver.interruption is not None)
            mutations = [a for a in ports.actions if a["action"].get("flag") == "new_checkout" and a["changed"]]
            driver.check("restart never repeats the external mutation", len(mutations) == 1)
        if case in ("signed_approved", "interrupted_action"):
            result["morning"] = driver.morning(restore_all=case == "interrupted_action")
        result.update(passed=True, checks=driver.checks, counts={k: len(v) for k, v in kinds.items()},
                      ledger=ledger, actions=ports.actions, final_flags=dict(ports.shop.flags),
                      persisted_state=driver.document(), interruption=driver.interruption,
                      requests=driver.requests, minute_steps=driver.minute_steps,
                      http_statuses=driver.statuses, cold_starts=driver.cold_starts)
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
        if holder:
            driver = holder[0]
            result.update(checks=driver.checks, requests=driver.requests, http_statuses=driver.statuses,
                          minute_steps=driver.minute_steps, persisted_state=driver.document(),
                          actions=driver.world.actions)
    finally:
        for driver in holder:
            driver.close()
    result["elapsed_seconds"] = round(monotonic() - started, 3)
    return result


def verify(cases=CASES) -> dict:
    chosen = tuple(cases)
    if not chosen or len(chosen) > len(CASES) or len(set(chosen)) != len(chosen) or set(chosen) - set(CASES):
        raise ValueError("Select distinct known operational cases")
    started = monotonic()
    results = []
    with tempfile.TemporaryDirectory(prefix="night-orders-operational-") as directory:
        for case in chosen:
            if monotonic() - started >= MAX_TOTAL_SECONDS:
                results.append({"case": case, "passed": False, "not_run": True, "error": {"type": "TimeoutError",
                                "message": "Operational verification exceeded its total time budget"}})
                continue
            results.append(verify_case(case, Path(directory) / case, started + MAX_TOTAL_SECONDS))
    elapsed = monotonic() - started
    return {"label": LABEL, "source": source_identity(), "passed": all(r["passed"] for r in results)
            and len(results) == len(chosen) and elapsed <= MAX_TOTAL_SECONDS,
            "limits": {"cases": len(CASES), "minute_steps_per_case": demo_night.MAX_DEMO_STEPS,
                       "seconds_per_case": MAX_CASE_SECONDS,
                       "http_requests_per_case": MAX_CASE_REQUESTS, "total_seconds": MAX_TOTAL_SECONDS},
            "elapsed_seconds": round(elapsed, 3), "total_requests": sum(r.get("requests", 0) for r in results),
            "total_minute_steps": sum(r.get("minute_steps", 0) for r in results), "cases": results}


def markdown(report: dict) -> str:
    lines = ["# Operational verification", "", LABEL, "",
             f"Source commit: `{report['source']['commit']}`.",
             f"Source content SHA-256: `{report['source']['content_sha256']}`.", "",
             "| Case | Result | HTTP requests | Seconds |", "| --- | --- | ---: | ---: |"]
    for case in report["cases"]:
        lines.append(f"| {case['case']} | {'passed' if case['passed'] else 'FAILED'} | "
                     f"{case.get('requests', 0)} | {case.get('elapsed_seconds', 0)} |")
        if not case["passed"]:
            lines.append(f"\nFailure: {case['error']['type']}: {case['error']['message']}\n")
    lines += ["", f"Overall: {'passed' if report['passed'] else 'FAILED'}. "
              f"Elapsed: {report['elapsed_seconds']} seconds (limit {MAX_TOTAL_SECONDS}).",
              "", "JSON output includes checks, HTTP outcomes, ledger, actions, snapshots and countersign evidence.",
              "This is offline verification, not a live GitLab, Duo, Google Cloud or production run."]
    return "\n".join(lines) + "\n"
