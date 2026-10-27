"""One bounded local session against a real disposable HTTP shop, with durable mutation intent."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import threading
from datetime import datetime, time, timedelta, timezone
from time import monotonic
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import httpx

from .countersign import parse_state, plan_morning
from .dawn import LooseEnd
from .decide import Ask, Night, triage
from .ledger import Ledger
from .model import Action, Alert, Condition, OnCall, Order, Orders, Signature, Targets
from .signals import recheck_after_action
from .sources import parse_metrics

LABEL = "Local disposable shop: real HTTP requests and flag changes. No live GitLab, Duo or production service."
MAX_REQUESTS = 200
MAX_CLEANUP_REQUESTS = 60
MAX_ACTION_SECONDS = 30
CONDITION = Condition("checkout_error_rate", 5, path="new", above=.05, min_count=10)
ACTION = Action("flag_set", flag="new_checkout", environment="local", to="off")
TARGETS = Targets(flags={"new_checkout": frozenset({"local"})}, services={},
                  signals={"checkout_error_rate": frozenset({"new", "old", "all"})},
                  min_per_minute={"checkout_error_rate": 10})
BODY = {"user": "local-operator", "region": "uk",
        "items": [{"sku": "juniper-jam", "price": 16.46, "qty": 1}]}


class LocalError(RuntimeError):
    pass


def source_identity():
    root = Path(__file__).resolve().parents[2]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                            text=True, check=True, timeout=5).stdout.strip()
    paths = [root / "relay" / "local_main.py", root / "scripts" / "run_local.py"]
    paths += list((root / "shop").glob("*.py")) + list((root / "relay" / "nightorders").glob("*.py"))
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes() + b"\0")
    return {"commit": commit, "content_sha256": digest.hexdigest(),
            "scope": "shop/*.py, relay/nightorders/*.py, relay/local_main.py, scripts/run_local.py"}


class LocalSession:
    def __init__(self, shop_url: str, shop_key: str, shop_id: str, directory: Path):
        parts = urlsplit(shop_url)
        if parts.scheme != "http" or parts.hostname != "127.0.0.1" or not parts.port or parts.path \
                or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError("The session requires its owned loopback shop")
        self.shop_id, self.directory = shop_id, Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "session.json"
        self.client = httpx.Client(base_url=shop_url, headers={"X-Local-Shop-Key": shop_key},
                                   trust_env=False, timeout=3, follow_redirects=False)
        self.lock = threading.RLock()
        self.deadline = float("inf")
        self.cleaning = False
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
            if self.data["shop_id"] != shop_id:
                raise LocalError("Saved session belongs to another shop. Use a new state directory.")
            self._reconcile_pending()
        else:
            self.data = {"session_id": secrets.token_hex(8), "shop_id": shop_id, "phase": "idle",
                         "csrf_token": secrets.token_urlsafe(24), "label": LABEL, "mode": "standing_orders",
                         "infrastructure": "Accelerated minute clock; real loopback HTTP shop and checkout code.",
                         "authorization": None, "flags": {}, "metrics": {"before": [], "after": []},
                         "decision": None, "verification": None, "morning": None, "events": [],
                         "intents": [], "request_count": 0, "error": None, "original": None,
                         "receipt_url": "/local/api/receipt", "checkout_requests": [], "http_requests": [],
                         "cleanup_request_count": 0, "source": source_identity(),
                         "limits": {"regular_http_requests": MAX_REQUESTS, "cleanup_http_requests": MAX_CLEANUP_REQUESTS,
                                    "action_seconds": MAX_ACTION_SECONDS}}
            self.save()

    def save(self):
        temp = self.path.with_suffix(".partial")
        with temp.open("w", encoding="utf-8") as stream:
            json.dump(self.data, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temp.replace(self.path)
        descriptor = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def event(self, kind, message):
        self.data["events"].append({"at": datetime.now(timezone.utc).isoformat(), "kind": kind, "message": message})

    def view(self):
        with self.lock:
            return copy.deepcopy({k: v for k, v in self.data.items() if k not in ("shop_id",)})

    def receipt(self):
        result = self.view()
        result.pop("csrf_token", None)
        return result

    def _reconcile_pending(self):
        if any(i["status"] == "pending" for i in self.data["intents"]):
            self.data.update(phase="uncertain", error="A saved mutation has no confirmed response. It will not be repeated.")
            self.save()

    def _request(self, method, path, **kwargs):
        cleanup = self.data.get("cleanup_request_count", 0)
        exhausted = cleanup >= MAX_CLEANUP_REQUESTS if self.cleaning else self.data["request_count"] - cleanup >= MAX_REQUESTS
        if exhausted or monotonic() >= self.deadline:
            raise LocalError("The local session reached its bounded request or time limit")
        self.data["request_count"] += 1
        if self.cleaning:
            self.data["cleanup_request_count"] = cleanup + 1
        observation = {"method": method, "path": path, "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                       "logical_at": self.data.get("logical_clock")}
        self.data.setdefault("http_requests", []).append(observation)
        try:
            response = self.client.request(method, path, **kwargs)
            observation["status"] = response.status_code
            return response
        except Exception as error:
            observation["transport_error"] = type(error).__name__
            raise

    def _state(self):
        response = self._request("GET", "/local/state")
        response.raise_for_status()
        state = response.json()
        if state.get("identity") != self.shop_id:
            raise LocalError("Disposable shop identity changed; refusing further action")
        self.data["flags"] = state["flags"]
        self.data["logical_clock"] = state["clock"]
        return state

    def _mutate(self, path, body, kind):
        before = self._state()
        intent = {"kind": kind, "path": path, "body": body, "before": before,
                  "status": "pending", "at": datetime.now(timezone.utc).isoformat()}
        self.data["intents"].append(intent)
        self.save()  # durable snapshot precedes the HTTP write, including injected faults and clock changes
        try:
            response = self._request("POST", path, json=body)
            response.raise_for_status()
            observed = self._state()  # independent read, never trust the mutation response as verification
            if path == "/local/flag" and (observed["flags"]["new_checkout"] == "on") != body["value"]:
                raise LocalError("Flag readback disagrees with the requested value")
            if path == "/local/fault" and ("rounding_bug" in observed["faults"]) != body["value"]:
                raise LocalError("Fault readback disagrees with the requested value")
            intent.update(status="confirmed", readback=observed)
            self.save()
            return observed
        except Exception as error:
            self.data.update(phase="uncertain", error=f"{kind}: response or independent readback was lost ({type(error).__name__}).")
            self.event("uncertain", self.data["error"])
            self.save()
            raise LocalError(self.data["error"]) from error

    def _traffic(self, minutes=1):
        for _ in range(minutes):
            for _ in range(10):
                response = self._request("POST", "/checkout", json=BODY)
                if response.status_code not in (200, 500, 502, 504):
                    raise LocalError(f"Checkout returned unexpected HTTP {response.status_code}")
                answer = response.json()
                self.data["checkout_requests"].append({"at": self.data["logical_clock"],
                                                        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                                                        "http": response.status_code,
                                                        "path": answer.get("path"), "ok": answer.get("ok")})
            self._mutate("/local/advance", {"minutes": 1}, "advance logical minute")
        response = self._request("GET", "/metrics.json")
        response.raise_for_status()
        return response.json()["minutes"]

    def _health(self):
        buckets = self._traffic()
        metrics = parse_metrics({"minutes": buckets})
        now = datetime.fromisoformat(self.data["logical_clock"])
        healthy, reason = recheck_after_action(CONDITION, metrics, now)
        return {"healthy": healthy, "reason": reason, "checkouts": buckets[-1]["checkouts.all"],
                "measured_at": buckets[-1]["at"]}, buckets

    def run(self, operation, choice=None):
        with self.lock:
            self.deadline = monotonic() + MAX_ACTION_SECONDS
            self.cleaning = operation == "finish"
            try:
                handler = getattr(self, "do_" + operation, None)
                if handler is None:
                    raise LocalError("Unknown local operation")
                handler(choice) if operation == "morning" else handler()
                self.save()
                return self.view()
            except Exception as error:
                self.data["error"] = str(error) if isinstance(error, LocalError) else type(error).__name__
                self.save()
                raise LocalError(self.data["error"]) from error
            finally:
                self.deadline = float("inf")
                self.cleaning = False

    def require(self, *phases):
        if self.data["phase"] not in phases:
            raise LocalError(f"This operation is not available while the session is {self.data['phase']}")

    def do_start(self):
        self.require("idle")
        self.data["original"] = self._state()
        self.data["starting_flags"] = self.data["original"]["flags"]
        self.data["phase"] = "started"
        self.save()
        health, buckets = self._health()
        self.data["baseline"] = health
        self.data["metrics"]["before"] = buckets
        self.event("started", "The disposable shop answered real checkout requests. Original flags are saved.")

    def do_authorize(self):
        self.require("started")
        now = datetime.now(timezone.utc)
        self.data["authorization"] = {"scope": "new_checkout off", "method": "local browser consent",
                                      "signed_at": self.data["logical_clock"], "expires_at": (now + timedelta(minutes=10)).isoformat(),
                                      "used": False, "environment": "local", "shop_id": self.shop_id}
        self.data["phase"] = "authorized"
        self.event("authorized", "You permitted new_checkout off once in this disposable shop, for ten real minutes.")

    def do_observe(self):
        self.require("started", "authorized")
        self._mutate("/local/fault", {"value": True}, "plant local rounding fault")
        buckets = self._traffic(5)
        self.data["metrics"]["before"] = buckets[-5:]
        now = datetime.fromisoformat(self.data["logical_clock"])
        auth = self.data["authorization"]
        consent = None
        reasons = []
        if auth and datetime.now(timezone.utc) < datetime.fromisoformat(auth["expires_at"]) and not auth["used"]:
            # The core checks the same person/time bounds; the method explicitly records local consent, not GitLab.
            consent = Signature(method="local browser consent", user="local-operator",
                                at=datetime.fromisoformat(auth["signed_at"]), commit=self.data["session_id"])
        elif auth:
            reasons.append("Local consent expired or was already used.")
        order = Order(1, "The local rounding fault affects the new checkout path.", CONDITION, ACTION)
        oncall = OnCall("local-operator", "Local operator", ZoneInfo("UTC"), time(7))
        ledger = Ledger()
        night = Night(oncall, TARGETS, Orders(now.date(), time(7), (order,)), (), consent, ledger)
        answer = triage([Alert(CONDITION.key, buckets[-1][CONDITION.key], now)], night,
                        parse_metrics({"minutes": buckets}), now)
        allowed = isinstance(answer, Ask) and not reasons
        reasons += list(answer.checks.values()) if isinstance(answer, Ask) else list(answer.reasons)
        self.data["decision"] = {"allowed": allowed, "reasons": reasons, "applied": False, "readback": None}
        self.data["phase"] = "observed"
        if allowed:
            auth["used"] = True
            self.save()  # consumed before attempting the one authorized write; uncertain outcomes never retry
            observed = self._mutate("/local/flag", {"value": False}, "authorized new_checkout off")
            self.data["decision"].update(applied=True, readback=observed["flags"])
            self.data["phase"] = "applied"
            self.event("applied", "Code turned off the real disposable shop flag and independently read it back.")
        else:
            self.event("refused", "Code left the flag unchanged: " + " ".join(reasons))

    def do_verify(self):
        self.require("observed", "applied")
        health, buckets = self._health()
        self.data["verification"] = health
        self.data["metrics"]["after"] = buckets[-1:]
        self.data["phase"] = "verified"
        self.event("verified", health["reason"])

    def do_morning(self, choice):
        self.require("verified")
        if choice not in ("keep", "restore"):
            raise LocalError("Choose keep or restore")
        changed = bool(self.data["decision"] and self.data["decision"]["applied"])
        before = {"kind": "flag", "flag": "new_checkout", "environment": "local",
                  "value": self.data["original"]["flags"]["new_checkout"]}
        loose = [LooseEnd(ACTION, "One locally authorized change", before)] if changed else []
        keep = [{"flag": "new_checkout", "environment": "local", "keep": "off",
                 "until": "this disposable session finishes"}] if choice == "keep" and changed else []
        plan = plan_morning(loose, parse_state({"flags": keep}, TARGETS))
        for action, snapshot, _ in plan.undo:
            self._mutate("/local/flag", {"value": snapshot["value"] == "on"}, "morning snapshot restore")
        health, buckets = self._health()
        self.data["morning"] = {"choice": choice, **health, "changed": changed,
                                "kept": len(plan.kept), "restored": len(plan.undo)}
        self.data["metrics"]["after"] = buckets[-1:]
        self.data["phase"] = "morning"
        self.event("morning", f"You chose {choice}. {health['reason']}")

    def do_finish(self):
        if self.data["phase"] == "finished":
            return
        if self.data["original"] is None:
            self.data["original"] = self._state()
        self._mutate("/local/fault", {"value": False}, "cleanup injected rounding fault")
        self._mutate("/local/flag", {"value": self.data["original"]["flags"]["new_checkout"] == "on"},
                     "cleanup restore original snapshot")
        health, buckets = self._health()
        self.data["cleanup"] = health
        self.data["metrics"]["after"] = buckets[-1:]
        if not health["healthy"] or self.data["flags"] != self.data["original"]["flags"]:
            raise LocalError("Cleanup readback or checkout health did not match the original shop")
        for intent in self.data["intents"]:
            if intent["status"] == "pending":
                intent.update(status="resolved_by_cleanup", cleanup_flags=copy.deepcopy(self.data["flags"]),
                              cleanup_health=health)
        self.data.update(phase="finished", error=None)
        self.event("finished", "Injected fault cleared, original flags restored and fresh real checkouts passed.")
        self.save()
        receipt = self.directory / "receipt.partial"
        receipt.write_text(json.dumps(self.receipt(), indent=2), encoding="utf-8")
        receipt.replace(self.directory / "receipt.json")

    def do_reload(self):
        self.data = json.loads(self.path.read_text())
        self._reconcile_pending()
        self._state()  # independent read only; never repeat a pending mutation
        self.event("reloaded", "Saved record reloaded. No pending action was repeated.")

    def close(self):
        self.client.close()
