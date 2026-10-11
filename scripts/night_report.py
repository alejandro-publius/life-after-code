"""The night report: one night's record, from the relay's public /status.json, as Markdown.

    python scripts/night_report.py https://YOUR_RELAY.run.app --out night-report.md
    python scripts/night_report.py saved-status.json

The relay keeps one night at a time. The scheduled `night_report` job in .gitlab-ci.yml runs this each morning
and keeps the file as a job artifact, so every night stays readable in GitLab after the relay moves on. It reads
only the public status JSON (no token), and copies text from it as data: inside code spans or a code fence.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

KIND_WORDS = {"alert": "Alert", "asked": "Agent asked", "acted": "Order ran", "failed": "Change failed",
              "declined": "Agent declined", "woke": "Woke the on-call person", "approved": "Approved by thumbs-up",
              "refused": "Refused", "recovered": "Re-check passed", "stood_down": "Stood down",
              "expired": "Orders ended"}


def fetch(source: str) -> dict:
    """The status JSON from a relay base URL (or its /status.json), or from a saved file."""
    parts = urlsplit(source)
    if parts.scheme in ("http", "https"):
        if parts.username or parts.password:
            raise ValueError("Use the public relay URL without credentials")
        url = source.rstrip("/")
        url = url if url.endswith("/status.json") else url + "/status.json"
        with urllib.request.urlopen(url, timeout=20) as response:
            return json.load(response)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def _cell(text: object) -> str:
    return " ".join(str(text or "").replace("|", "/").replace("`", "'").split())


def _code(text: object) -> str:
    return "`" + _cell(text) + "`"


def _fence(text: str) -> list[str]:
    return ["```text", text.rstrip("\n").replace("```", "'''"), "```"]


def render(data: dict) -> str:
    tz = ZoneInfo(data.get("timezone") or "UTC")

    def hhmm(text: str | None) -> str:
        return datetime.fromisoformat(text).astimezone(tz).strftime("%H:%M") if text else ""

    night = data.get("night") or "unknown"
    lines = [f"# Night report: the night of {night}", "",
             f"{_cell(data.get('label'))} Read from the relay's /status.json, last check {hhmm(data.get('checked_at'))} "
             f"({_cell(data.get('timezone'))}). Written by code, no model.", ""]
    if data.get("relay_failing"):
        lines += ["**The relay's latest check had failed when this was read.**", ""]
    if data.get("mode") == "standing":
        lines += ["Standing orders: no model at night; code alone carried out signed orders.", ""]

    lines += ["## Orders", ""]
    orders, problems = data.get("orders"), data.get("problems") or []
    if orders and orders.get("items") and not problems:
        via = f" in !{int(orders['merge_request'])}" if orders.get("merge_request") else ""
        lines.append(f"Signed by {_cell(orders.get('signed_by'))} at {hhmm(orders.get('signed_at'))} "
                     f"({_cell(orders.get('method'))}){via}, ending {hhmm(orders.get('ends_at'))}.")
        lines.append("")
        for item in orders["items"]:
            lines.append(f"- Order {int(item['id'])}: when {_code(item.get('when'))}, {_code(item.get('do'))}. "
                         f"Because: {_code(item.get('because'))}")
    else:
        lines.append("Nothing signed. Every alert woke the on-call person.")
        lines += [f"- {_code(problem)}" for problem in problems]
    lines.append("")

    lines += ["## What happened", ""]
    events = data.get("events") or []
    if events:
        lines += ["| Time | What | Incident | Detail |", "|---|---|---|---|"]
        for event in events:
            incident = f"#{int(event['incident'])}" if event.get("incident") is not None else ""
            lines.append(f"| {hhmm(event.get('at'))} | {KIND_WORDS.get(event.get('kind'), _cell(event.get('kind')))} "
                         f"| {incident} | {_cell(event.get('text'))} |")
    else:
        lines.append("Nothing happened.")
    lines.append("")

    if data.get("watch_log"):
        lines += ["## Watch log", ""] + _fence(data["watch_log"]) + [""]
    countersign = (data.get("morning") or {}).get("countersign")
    lines += ["## Morning countersign", ""]
    lines += (_fence(countersign) if countersign else ["Not countersigned yet when this was read."]) + [""]
    kept, ended = data.get("kept") or [], data.get("kept_ended") or []
    if kept or ended:
        lines += ["## Kept from earlier nights", ""]
        lines += [f"- {_cell(line)}" for line in kept]
        lines += [f"- Ended {_cell(item.get('at', ''))[:16]}: {_cell(item.get('text'))}" for item in ended]
        lines.append("")
    return "\n".join(lines)


def _shown(source: str) -> str:
    """The source as it may be printed: a URL without any user name or password in it."""
    parts = urlsplit(source)
    if parts.scheme in ("http", "https") and (parts.username or parts.password):
        return f"{parts.scheme}://{parts.hostname or ''}{parts.path}"
    return source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="the relay's base URL, its /status.json, or a saved status JSON file")
    parser.add_argument("--out", type=Path, help="write the report here instead of printing it")
    args = parser.parse_args(argv)
    try:
        text = render(fetch(args.source))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"night report: could not read {_shown(args.source)} ({type(error).__name__}: {error})", file=sys.stderr)
        return 2
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
