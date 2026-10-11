"""Structured log lines: one JSON object per line on stdout, the shape Cloud Logging reads.

Cloud Run sends each stdout line to Cloud Logging. A line that is a JSON object becomes a structured
entry, and `severity`, `time` and `logging.googleapis.com/sourceLocation` (file, line, function) are
read as entry fields. Field names are taken from Google's own logging library:
https://github.com/googleapis/google-cloud-python/blob/main/packages/google-cloud-logging/google/cloud/logging_v2/handlers/structured_log.py
"""

from __future__ import annotations

import json
import sys
import traceback
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

SERVICE = "juniper-market (demo shop)"
HERE = Path(__file__).resolve().parent
RECENT_MAX = 50
# The last warnings and errors, newest last, served at GET /errors.json so the relay can copy recent error
# lines into an incident's evidence pack. Kept in memory only, like the metrics.
RECENT: deque[dict] = deque(maxlen=RECENT_MAX)


def emit(severity: str, message: str, **fields: object) -> dict:
    """Write one log line and return it (tests read it back)."""
    entry: dict = {"severity": severity, "message": message, "time": _now(), "service": SERVICE}
    entry.update(fields)
    sys.stdout.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    if severity in ("WARNING", "ERROR", "CRITICAL"):
        RECENT.append({"time": entry["time"], "severity": severity, "message": message})
    return entry


def recent(limit: int = RECENT_MAX) -> list[dict]:
    """The newest warnings and errors, oldest first: time, severity and message only (no stack, no user)."""
    return list(RECENT)[-limit:]


def error(exc: BaseException, where: str, **fields: object) -> dict:
    """Log an exception as one line, with the file, line and function that raised it."""
    frames = traceback.extract_tb(exc.__traceback__)
    if frames:
        last = frames[-1]
        file, line, function = _repo_path(last.filename), last.lineno or 0, last.name
    else:
        file, line, function = "unknown", 0, "unknown"
    message = f"{type(exc).__name__}: {exc} ({file}:{line} in {function}, {where})"
    location = {"file": file, "line": line, "function": function}
    stack = "".join(traceback.format_exception(exc)).rstrip()
    return emit("ERROR", message, **{"logging.googleapis.com/sourceLocation": location, "stack_trace": stack},
                **fields)


def _repo_path(filename: str) -> str:
    """shop/checkout.py for files in this folder (the path in the repository), else the file name."""
    path = Path(filename).resolve()
    return f"shop/{path.name}" if path.parent == HERE else path.name


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
