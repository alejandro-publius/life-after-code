"""Public, bounded recordings of real GitLab Duo executions for the explorer."""

from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import urlsplit

RECORDING = Path(__file__).with_name("agent_runs.json")
MAX_STEPS = 80
MAX_RUNS = 8
LABEL = "Recorded GitLab executions. Shop incidents may use labelled demo inputs."


def clean(value: object, limit: int = 4000) -> str:
    text = str(value or "")
    text = text.replace("\u2014", " - ").replace("\u2013", "-")
    text = re.sub(r"(?:glpat-|gh[pousr]_)[A-Za-z0-9._-]+", "[redacted credential]", text)
    return text[:limit]


def project_link(value: object, project_url: str) -> str:
    """Links must stay in the recorded HTTPS project and contain no credentials or query."""
    value = str(value or "")
    url, base = urlsplit(value), urlsplit(project_url)
    if (url.scheme == base.scheme == "https" and url.netloc == base.netloc
            and not url.username and not url.password and not url.query
            and (not url.fragment or re.fullmatch(r"note_\d+", url.fragment))
            and (url.path == base.path.rstrip("/") or url.path.startswith(base.path.rstrip("/") + "/"))):
        return value
    return ""


def flow_name(node: dict) -> str:
    name = str((node.get("aiCatalogItem") or {}).get("name") or node.get("agentName") or "").lower()
    for key in ("dusk", "watch", "dawn"):
        if name == f"night-orders-{key}":
            return key
    return "other"


def steps_of(node: dict) -> list[dict]:
    messages = ((node.get("latestCheckpoint") or {}).get("duoMessages") or [])[:MAX_STEPS]
    steps = []
    for message in messages:
        kind = str(message.get("messageType") or "")
        if kind not in ("tool", "agent"):
            continue
        info = message.get("toolInfo")
        try:
            tool = json.loads(info) if isinstance(info, str) else info
        except (ValueError, TypeError):
            tool = None
        name = clean(tool.get("name"), 100) if isinstance(tool, dict) else ""
        content = clean(message.get("content"))
        component = clean(message.get("componentName"), 100)
        title = content.splitlines()[0][:180] if kind == "tool" else f"{component or 'Agent'} response"
        steps.append({"index": len(steps) + 1, "kind": kind, "component": component,
                      "name": name, "title": title, "status": clean(message.get("status"), 40),
                      "text": content})
    return steps


def recording(node: dict, project_url: str) -> dict:
    checkpoint = node.get("latestCheckpoint") or {}
    return {"id": int(str(node["id"]).rsplit("/", 1)[-1]), "flow": flow_name(node),
            "title": clean(node.get("title") or node.get("agentName") or "Duo session", 240),
            "status": str(node.get("status") or "unknown").lower(),
            "execution_status": clean(checkpoint.get("executionStatus"), 100),
            "created_at": node.get("createdAt"), "updated_at": node.get("updatedAt"),
            "web_url": project_link(node.get("webUrl"), project_url),
            "source_url": project_link(node.get("resourceWebUrl"), project_url),
            "steps": steps_of(node), "artifacts": [],
            "steps_truncated": len(checkpoint.get("duoMessages") or []) > MAX_STEPS,
            "errors": [clean(error, 600) for error in (checkpoint.get("errors") or [])[:8]]}


def load_recording(path: Path = RECORDING) -> dict:
    """The public endpoint never reads credentials or makes authenticated API calls."""
    if not path.exists():
        return {"version": 1, "captured_at": None, "label": LABEL, "project": {}, "runs": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("runs"), list) or len(data["runs"]) > MAX_RUNS:
        raise ValueError("The execution recording is not a supported snapshot")
    return data
