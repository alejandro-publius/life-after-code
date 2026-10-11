"""The live gates page: what has really run on GitLab and Google Cloud, with a link for each, or "pending".

    python scripts/live_gates.py --day-one day-one.json --relay https://YOUR_RELAY.run.app \
        --done pipeline=https://gitlab.com/.../-/pipelines/123 --done video=https://youtu.be/... \
        --out docs/LIVE_GATES.md

Inputs, all optional: the JSON that scripts/day_one.py --out writes, the relay's public base URL (its /healthz
and /status.json; no token), and --done NAME=URL for the gates only a person can confirm. Anything without
evidence stays "pending", so the page never claims more than was run. It prints no setting and reads no token.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.night_report import fetch  # noqa: E402

DAY_ONE = [  # (day_one.py step, the gate in plain words)
    ("whoami", "The token works and the role on the project is known"),
    ("publish", "The GitLab project is public and its MIT licence is detected"),
    ("issue", "The standing watch issue exists"),
    ("flags", "The feature flags an order may touch exist, per environment"),
    ("catalog", "The flows are enabled in the project"),
    ("flow", "A flow started through the Flows API ran and posted its note (decision D1)"),
    ("signature", "The on-call person can sign by merge or by approval"),
]
MANUAL = [  # (--done name, the gate)
    ("pipeline", "A GitLab pipeline on the default branch passed"),
    ("pages", "The browser demo is public on GitLab Pages"),
    ("release", "A tagged GitLab Release links the demo, the images and the pipeline"),
    ("deploy", "The relay and the shop were deployed to Cloud Run by the pipeline"),
    ("video", "The video is public on YouTube, under 3:00"),
]


@dataclass(frozen=True)
class Gate:
    name: str
    words: str
    state: str          # passed, failed, pending
    evidence: str = ""  # a link or a short fact


def from_day_one(data: dict | None) -> list[Gate]:
    results = {r.get("step"): r for r in (data or {}).get("results") or []}
    gates = []
    for step, words in DAY_ONE:
        result = results.get(step)
        if result is None or result.get("status") == "SKIP":
            why = f"skipped: {result.get('reason')}" if result else ""
            gates.append(Gate(step, words, "pending", why))
        elif result.get("status") == "PASS":
            lines = [line for line in result.get("lines") or [] if line]
            gates.append(Gate(step, words, "passed", f"day_one.py at {data.get('at', '')[:16]}"
                              + (f": {lines[-1]}" if lines else "")))
        else:
            gates.append(Gate(step, words, "failed", str(result.get("reason") or "")))
    return gates


def from_relay(base: str | None, status: dict | None, healthy: bool | None) -> list[Gate]:
    live = Gate("relay", "The relay answers in public (/healthz)", "pending")
    if healthy is True:
        live = Gate("relay", live.words, "passed", f"{base}/healthz")
    elif healthy is False:
        live = Gate("relay", live.words, "failed", f"{base}/healthz did not answer ok")
    night = Gate("night", "A real night: a signed order ran and the re-check passed", "pending")
    morning = Gate("morning", "A real countersign was applied by code", "pending")
    if status:
        kinds = [e.get("kind") for e in status.get("events") or []]
        where = f"{base}/status.json" if base else "the relay's /status.json"
        if "acted" in kinds and "recovered" in kinds:
            night = Gate("night", night.words, "passed", f"night of {status.get('night')}, {where}")
        if (status.get("morning") or {}).get("countersign"):
            morning = Gate("morning", morning.words, "passed", f"night of {status.get('night')}, {where}")
    return [live, night, morning]


def from_done(done: dict[str, str]) -> list[Gate]:
    return [Gate(name, words, "passed", done[name]) if name in done else Gate(name, words, "pending")
            for name, words in MANUAL]


def _cell(text: str) -> str:
    return " ".join(str(text).replace("|", "/").split())


def render(gates: list[Gate], at: datetime) -> str:
    passed = sum(g.state == "passed" for g in gates)
    lines = ["# Live gates", "",
             f"What has really run on GitLab and Google Cloud. Written by [scripts/live_gates.py](../scripts/live_gates.py) "
             f"at {at.astimezone(timezone.utc):%Y-%m-%d %H:%M} UTC. **{passed} of {len(gates)} passed.** A gate without "
             "evidence stays pending; the offline checks are in [STATUS.md](STATUS.md).", "",
             "| Gate | State | Evidence |", "|---|---|---|"]
    for gate in gates:
        evidence = gate.evidence
        shown = f"[{_cell(evidence)}]({evidence})" if evidence.startswith("https://") else _cell(evidence)
        lines.append(f"| {_cell(gate.words)} | {gate.state} | {shown} |")
    return "\n".join(lines) + "\n"


def healthz(base: str) -> bool:
    try:
        with urllib.request.urlopen(base.rstrip("/") + "/healthz", timeout=20) as response:
            return bool(json.load(response).get("ok"))
    except (OSError, ValueError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--day-one", type=Path, help="the JSON written by scripts/day_one.py --out")
    parser.add_argument("--relay", help="the relay's public base URL (https)")
    parser.add_argument("--status", type=Path, help="a saved /status.json, instead of reading the relay's")
    parser.add_argument("--done", action="append", default=[], metavar="NAME=URL",
                        help="a gate a person confirmed: " + ", ".join(name for name, _ in MANUAL))
    parser.add_argument("--out", type=Path, help="write the page here instead of printing it")
    args = parser.parse_args(argv)
    done = {}
    for item in args.done:
        name, _, url = item.partition("=")
        if name not in dict(MANUAL) or not url.startswith("https://"):
            print(f"--done {name}: needs one of {', '.join(dict(MANUAL))} and an https link", file=sys.stderr)
            return 2
        done[name] = url
    base = None
    if args.relay:
        parts = urlsplit(args.relay)
        if parts.scheme != "https" or parts.username or parts.password:
            print("--relay: use the public https base URL, without credentials", file=sys.stderr)
            return 2
        base = args.relay.rstrip("/")
    day_one = json.loads(args.day_one.read_text(encoding="utf-8")) if args.day_one else None
    status = fetch(str(args.status)) if args.status else (fetch(base) if base else None)
    gates = from_day_one(day_one) + from_relay(base, status, healthz(base) if base else None) + from_done(done)
    text = render(gates, datetime.now(timezone.utc))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
