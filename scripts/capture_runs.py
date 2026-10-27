"""Capture real Duo sessions and their MR artifacts without changing GitLab.

    uv run python scripts/capture_runs.py --project 88050495 --out relay/nightorders/agent_runs.json

Reads GITLAB_TOKEN from the process environment. Captures at most eight sessions,
80 visible steps per session and two merge requests per session. Raw tool
responses, tool arguments and the access token are never published.
"""

from __future__ import annotations

import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import quote, urlsplit

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "relay")]

from nightorders import execution  # noqa: E402
from nightorders.countersign import parse_state  # noqa: E402
from nightorders.orders import parse_oncall, parse_orders, parse_targets  # noqa: E402
from nightorders.notes import Request, parse_request  # noqa: E402
from scripts.day_one import DayOne, GitLab, Http20, RelayError  # noqa: E402

QUERY = """
query($projectId: ProjectID!, $ids: [AiDuoWorkflowsWorkflowID!], $first: Int!) {
  duoWorkflowWorkflows(projectId: $projectId, ids: $ids, first: $first) {
    nodes {
      id title agentName status createdAt updatedAt webUrl resourceWebUrl
      project { id }
      aiCatalogItem { name }
      latestCheckpoint {
        executionStatus errors
        duoMessages { content messageType componentName status toolInfo }
      }
      mergeRequestLinks { nodes { mergeRequest { iid title webUrl } } }
      noteLinks { nodes { note { id body url } } }
    }
    pageInfo { hasNextPage }
  }
}
"""


class Capture:
    def __init__(self, run: DayOne):
        self.run = run
        self.deadline = run.clock() + 120

    def remaining(self) -> None:
        if self.run.clock() >= self.deadline:
            raise RelayError("Execution capture exceeded its two-minute request budget")

    def get(self, path: str, **kwargs):
        self.remaining()
        return self.run.gitlab.json("read execution artifact", "GET", path, **kwargs)

    def file(self, path: str, ref: str) -> dict:
        data = self.get(f"/repository/files/{quote(path, safe='')}", params={"ref": ref})
        import base64
        return yaml.safe_load(base64.b64decode(data["content"]))

    def artifact(self, iid: int, base: str) -> dict:
        data = self.get(f"/merge_requests/{iid}/changes")
        files = [str(item["new_path"]) for item in data.get("changes") or []]
        result = {"kind": "merge_request", "iid": iid, "title": execution.clean(data.get("title"), 240),
                  "web_url": execution.project_link(data.get("web_url"), base),
                  "state": data.get("state"), "draft": bool(data.get("draft")), "sha": data.get("sha"),
                  "changed_files": files[:30], "validation": "Not an orders or countersign-only change"}
        if data.get("overflow"):
            result["validation"] = "Diff incomplete; validation not claimed"
            return result
        if files not in (["ops/night-orders.yml"], ["ops/state.yml"]):
            return result
        try:
            targets = parse_targets(self.file("ops/targets.yml", data["sha"]))
            contents = self.file(files[0], data["sha"])
            if files[0] == "ops/night-orders.yml":
                oncall = parse_oncall(self.file("ops/oncall.yml", data["sha"]))
                orders = parse_orders(contents, targets, oncall)
                result["validation"] = f"Orders parser passed: {len(orders.orders)} bounded orders"
            else:
                entries = parse_state(contents, targets)
                result["validation"] = f"Countersign parser passed: {len(entries)} kept changes; runtime context not checked"
        except (ValueError, KeyError, TypeError, yaml.YAMLError, RelayError) as error:
            result["validation"] = "Validation unavailable or failed: " + execution.clean(error, 300)
        return result

    def collect(self, workflows: list[int] | None = None) -> dict:
        project = self.run.project()
        if project.get("visibility") != "public":
            raise RelayError("The public execution explorer only captures public projects")
        project_gid = f"gid://gitlab/Project/{project['id']}"
        base = str(project["web_url"]).rstrip("/")
        if not execution.project_link(base, base):
            raise RelayError("Project did not return a clean HTTPS URL")
        self.remaining()
        answer = self.run.graphql("read recorded Duo executions", QUERY, {
            "projectId": project_gid,
            "ids": [f"gid://gitlab/Ai::DuoWorkflows::Workflow/{number}" for number in workflows] if workflows else None,
            "first": execution.MAX_RUNS,
        })
        connection = answer.get("duoWorkflowWorkflows") or {}
        if not isinstance(connection.get("nodes"), list):
            raise RelayError("GitLab returned no workflow list")
        runs = []
        for node in connection["nodes"][:execution.MAX_RUNS]:
            if (node.get("project") or {}).get("id") != project_gid:
                raise RelayError("A returned execution belongs to a different project")
            if execution.flow_name(node) == "other":
                continue
            entry = execution.recording(node, base)
            if not entry["web_url"]:
                raise RelayError("A returned execution has no link inside this project")
            links = (node.get("mergeRequestLinks") or {}).get("nodes") or []
            for link in links[:2]:
                mr = link.get("mergeRequest") or {}
                if not execution.project_link(mr.get("webUrl"), base):
                    continue
                entry["artifacts"].append(self.artifact(int(mr["iid"]), base))
            entry["artifacts_truncated"] = len(links) > 2
            notes = (node.get("noteLinks") or {}).get("nodes") or []
            for item in notes[:2]:
                note = item.get("note") or {}
                url = execution.project_link(note.get("url"), base)
                if not url:
                    continue
                artifact = {"kind": "note", "title": "Agent response on the incident", "web_url": url,
                            "state": "posted", "text": execution.clean(note.get("body"))}
                if entry["flow"] == "watch":
                    request = parse_request(str(note.get("body") or ""))
                    choice = (f"requested order {request.order}" if isinstance(request, Request) and request.order is not None
                              else "no automatic order requested")
                    artifact["validation"] = (f"Watch request parser passed: {choice}"
                                               if isinstance(request, Request) else "Not a structured watch request")
                entry["artifacts"].append(artifact)
            runs.append(entry)
        return {"version": 1, "captured_at": self.run.now().isoformat(), "label": execution.LABEL,
                "project": {"id": project["id"], "name": project.get("name_with_namespace") or project["name"],
                            "web_url": base}, "runs": runs,
                "more_runs_available": bool((connection.get("pageInfo") or {}).get("hasNextPage")),
                "source": "Read-only GitLab GraphQL checkpoints and REST merge-request read-back",
                "limits": "Recorded execution is not proof of a deployed relay or production remediation."}


def main(argv=None, *, env=None, client=None, out=None) -> int:
    env, out = os.environ if env is None else env, sys.stdout if out is None else out
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True)
    parser.add_argument("--workflow", type=int, action="append", help="repeat for specific session IDs")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base-url", default=env.get("GITLAB_URL", "https://gitlab.com"))
    args = parser.parse_args(argv)
    token = str(env.get("GITLAB_TOKEN") or "").strip()
    base = urlsplit(args.base_url)
    if not token or base.scheme != "https" or not base.netloc or base.username or base.password or base.query or base.fragment:
        out.write("Set GITLAB_TOKEN and use a clean HTTPS GitLab base URL.\n")
        return 2
    if args.workflow and (len(args.workflow) > execution.MAX_RUNS or min(args.workflow) < 1):
        out.write("Choose one to eight positive workflow IDs.\n")
        return 2
    try:
        with nullcontext(client) if client is not None else httpx.Client(follow_redirects=False) as http:
            run = DayOne(GitLab(Http20(http), args.base_url, args.project, token), token=token, out=out,
                         options=args, now=lambda: datetime.now(timezone.utc), clock=time.monotonic, sleep=time.sleep)
            data = Capture(run).collect(args.workflow)
            text = execution.clean(run.redact(json.dumps(data, indent=2)), 2_000_000) + "\n"
            # Parse once more before replacing an existing recording; never leave partial JSON.
            json.loads(text)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            temporary = args.out.with_suffix(args.out.suffix + ".tmp")
            temporary.write_text(text, encoding="utf-8")
            temporary.replace(args.out)
            run.say(f"Captured {len(data['runs'])} real GitLab sessions to {args.out}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RelayError) as error:
        out.write(execution.clean(str(error).replace(token, "[redacted]"), 600) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
