"""Run the enabled Dawn flow against a clearly labelled demo watch log, then verify what it opened.

    uv run --locked python scripts/claude_run_dawn.py --render --out docs/claude/dawn-demo-watch-log.md
    GITLAB_TOKEN=... uv run --locked python scripts/claude_run_dawn.py --project 88050495 --consumer-id 13304393 \\
        --apply --out docs/claude/dawn-run.json
    GITLAB_TOKEN=... uv run --locked python scripts/claude_run_dawn.py --project 88050495 --workflow 10130001 \\
        --out docs/claude/dawn-run.json

The night is the repository's simulated demo night (demo/night-2026-10-20): the shop, its traffic and both faults
are demo data, and the agent replies in it are recorded notes. The watch log is rendered by the relay's own
renderer from the ledger the real decision code wrote during the replay. The Dawn flow execution and the branch,
commit, merge request and note it leaves in GitLab are real Duo artifacts. This script never signs, approves or
merges anything and changes no flag or traffic. The token is read from GITLAB_TOKEN only and is never printed.
A run that fails is recorded with GitLab's own words; nothing here invents a result.
"""

from __future__ import annotations

import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, TextIO
from urllib.parse import urlsplit

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "relay")]

from nightorders import demo_night  # noqa: E402
from nightorders.countersign import parse_state, plan_morning  # noqa: E402
from nightorders.dawn import dawn_goal, loose_ends, render_watch_log  # noqa: E402
from nightorders.gitlab_ports import mention_note  # noqa: E402
from nightorders.orders import OrdersError, parse_targets  # noqa: E402
from scripts.day_one import DayOne, GitLab, Http20, RelayError, flow_body  # noqa: E402

DEMO = ROOT / "demo" / "night-2026-10-20"
NIGHT = "2026-10-20"
STATE_PATH = "ops/state.yml"
TARGETS_PATH = "ops/targets.yml"
ISSUE_TITLE = f"[demo] Dawn demo: watch log of the simulated night of {NIGHT}"
LOG_HEADER = "## Watch log, night of Tue 20 Oct"
DEMO_LABEL = ("DEMO DATA. This watch log is rendered by code from the repository's simulated night of 20 Oct 2026 "
              "(demo/night-2026-10-20): the shop, its traffic and both faults are invented, and the agent replies in "
              "that night are recorded notes, not live model output. It is not a production night, and this issue is "
              "not the standing watch issue. What is real: the decision code that wrote this record, and the Dawn flow "
              "execution that reads it.")
GOAL_LABEL = ("Demo data: this is a labelled demonstration on the repository's simulated night and a dedicated demo "
              "issue, not a production night. Open the countersign merge request as a draft: start its title with "
              "Draft:.")
POLL_EVERY = 15.0
POLL_LIMIT = 15 * 60.0  # the live dusk run took about two minutes; dawn has four steps. Then the run is left as it is.
MAX_READ_FAILURES = 5  # consecutive status reads that fail before the wait gives up
RUNNING = frozenset({"created", "running"})
LIMITATIONS = [
    "The night is simulated demo data; the Duo session and its GitLab artifacts are real",
    "No human countersign: the merge request is left as a draft, unapproved and unmerged",
    "No production target changes: nothing restores or keeps a flag or traffic here",
    "No deployed relay took part: this script posted the log and started the flow",
]
WORKFLOW_QUERY = """
query($projectId: ProjectID!, $ids: [AiDuoWorkflowsWorkflowID!], $first: Int!) {
  duoWorkflowWorkflows(projectId: $projectId, ids: $ids, first: $first) {
    nodes {
      id status createdAt updatedAt webUrl
      aiCatalogItem { name }
      latestCheckpoint { executionStatus errors }
      mergeRequestLinks { nodes { mergeRequest { iid title webUrl } } }
      noteLinks { nodes { note { id url } } }
    }
  }
}"""


# The demo night, rendered by the repository's own code.

def demo_night_log() -> tuple[Any, list, str]:
    """(the replayed Night, its loose ends, the watch log the relay would post). All in memory."""
    _, night = demo_night.run(DEMO)
    return night, loose_ends(night), render_watch_log(night)


def defused(text: str) -> str:
    """Text posted with a person's token: no @ (a mention could start a flow or notify someone) and no line that
    starts with / (GitLab runs it as a quick action). The same rule the relay applies to its own notes."""
    lines = text.replace("@", "(at)").splitlines()
    return "\n".join("'" + line.lstrip() if line.lstrip().startswith("/") else line for line in lines)


def note_text(log: str, source_commit: str = "") -> str:
    """The watch log as posted on the demo issue: the demo label first, then the log exactly as rendered."""
    label = DEMO_LABEL + (f" Rendered at source commit {source_commit}." if source_commit else "")
    return defused(label + "\n\n" + log.rstrip("\n") + "\n")


def goal_text(night: Any, issue: int, ends: list) -> str:
    """The goal the relay would give the dawn flow, plus the demo label. Facts come from the ledger."""
    return dawn_goal(night, issue, ends) + "\n" + GOAL_LABEL


def issue_description(project_url: str, source_commit: str = "") -> str:
    folder = f"{project_url.rstrip('/')}/-/tree/main/demo/night-2026-10-20" if project_url else "demo/night-2026-10-20"
    return defused(
        f"{DEMO_LABEL}\n\nThe night's files are in {folder}. The watch log below is what the relay posts on the "
        "watch issue at 07:00; the Dawn flow reads it and proposes keep or restore for each loose end in a "
        "countersign merge request that changes only ops/state.yml. The merge request stays a draft, unapproved "
        "and unmerged: no person countersigns a demo night."
        + (f"\n\nSource commit: {source_commit}." if source_commit else "") + "\n")


def render_document(issue: int = 0) -> str:
    """The Markdown kept in docs/claude: the note and the goal exactly as the live run posts them."""
    night, ends, log = demo_night_log()
    goal = goal_text(night, issue, ends)
    if not issue:
        goal = goal.replace("Watch issue #0,", "Watch issue #<the demo issue>,", 1)
    return "\n".join([
        "# Demo watch log for the Dawn demonstration (demo data)",
        "",
        "Generated by `uv run --locked python scripts/claude_run_dawn.py --render --out "
        "docs/claude/dawn-demo-watch-log.md` from the simulated night in [demo/night-2026-10-20]"
        "(../../demo/night-2026-10-20/README.md), through the relay's own replay, ledger and watch-log renderer. "
        "A test keeps this file equal to what the script renders.",
        "",
        "## The note posted on the demo issue",
        "",
        note_text(log).rstrip("\n"),
        "",
        "## The goal given to the Dawn flow",
        "",
        "```text",
        goal,
        "```",
        "",
    ])


def source_commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"], capture_output=True,
                              text=True, timeout=10, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# The live demonstration.

class Demonstration:
    def __init__(self, run: DayOne, options: argparse.Namespace):
        self.run = run
        self.options = options
        self.night, self.ends, self.log = demo_night_log()
        self.started_at: datetime | None = None
        self.report: dict[str, Any] = {
            "checked_at": run.now().isoformat(), "demo_data_label": DEMO_LABEL, "flow": "dawn",
            "project_id": None, "consumer_id": options.consumer_id, "start": options.start,
            "source_commit": options.source_commit or source_commit(), "night": NIGHT,
            "loose_ends": [f"{end.action.describe()} ({end.why})" for end in self.ends],
            "demo_issue": None, "watch_log_note": None, "goal": None,
            "workflow_id": options.workflow, "web_url": "", "status": "not_started", "execution_status": "",
            "errors": [], "merge_request_url": "", "merge_request": None, "state_file": None, "flow_notes": [],
            "review_adjustment": "", "validation": "not checked", "result": "not_run", "problems": [],
            "limitations": list(LIMITATIONS),
        }

    def say(self, text: str) -> None:
        self.run.say(text)

    # Steps.

    def demo_issue(self) -> dict:
        """The dedicated demo issue, found by its exact title or created once. Never the standing watch issue."""
        if self.options.issue:
            issue = self.run.gitlab.json("read the demo issue", "GET", f"/issues/{int(self.options.issue)}")
            if str(issue.get("title") or "").strip().lower() != ISSUE_TITLE.lower():
                raise RelayError(f"issue #{self.options.issue} is not the demo issue ({ISSUE_TITLE!r}); refusing to "
                                 "post a demo log on another issue")
            created = False
        else:
            issue = self.run.find_issue(ISSUE_TITLE)
            created = issue is None
            if created:
                project_url = str(self.run.project().get("web_url") or "")
                issue = self.run.gitlab.json("create the demo issue", "POST", "/issues", expect=(200, 201), json={
                    "title": ISSUE_TITLE, "issue_type": "issue",
                    "description": issue_description(project_url, self.report["source_commit"]),
                })
        self.report["demo_issue"] = {"iid": int(issue["iid"]), "web_url": str(issue.get("web_url") or ""),
                                     "title": str(issue.get("title") or ""), "created": created}
        self.say(f"demo issue #{issue['iid']}{' created' if created else ' found'}: {issue.get('web_url') or ''}")
        return issue

    def watch_log_note(self, issue: dict) -> dict:
        """The watch log on the demo issue: posted once; a rerun finds the one already there."""
        iid = int(issue["iid"])
        notes = self.run.gitlab.json("read demo issue notes", "GET", f"/issues/{iid}/notes",
                                     params={"sort": "asc", "order_by": "created_at", "per_page": 100})
        found = next((n for n in notes if isinstance(n, dict) and not n.get("system")
                      and LOG_HEADER in str(n.get("body") or "")), None)
        posted = found is None
        if posted:
            found = self.run.gitlab.json("post the watch log", "POST", f"/issues/{iid}/notes", expect=(200, 201),
                                         json={"body": note_text(self.log, self.report["source_commit"])})
        url = f"{issue.get('web_url') or ''}#note_{found.get('id')}" if found.get("id") else ""
        self.report["watch_log_note"] = {"id": found.get("id"), "url": url, "posted": posted}
        self.say(f"watch log {'posted' if posted else 'already on the issue'}: {url}")
        return found

    def start(self, issue: dict) -> None:
        iid = int(issue["iid"])
        goal = goal_text(self.night, iid, self.ends)
        self.report["goal"] = goal
        self.started_at = self.run.now()
        if self.options.start == "mention":
            note = self.run.gitlab.json("start the dawn flow by a mention", "POST", f"/issues/{iid}/notes",
                                        expect=(200, 201), json={"body": mention_note(self.options.account, goal)})
            self.report["mention_note_id"] = note.get("id")
            self.say(f"mention note {note.get('id')} posted for {self.options.account}; waiting for its session")
            return
        started = self.run.gitlab.json("start the dawn flow", "POST", "/ai/duo_workflows/workflows",
                                       in_project=False, expect=(200, 201),
                                       json=flow_body(self.run.project_id(), int(self.options.consumer_id), iid, goal))
        self.report["workflow_id"] = started.get("id")
        self.report["status"] = str(started.get("status") or "started").lower()
        self.report["web_url"] = str(started.get("web_url") or "")
        self.say(f"dawn flow started: workflow {started.get('id')}, status {started.get('status')}: "
                 f"{started.get('web_url') or ''}")

    def read_workflows(self, ids: list[int] | None, first: int) -> list[dict]:
        project_gid = f"gid://gitlab/Project/{self.run.project_id()}"
        data = self.run.graphql("read the dawn session", WORKFLOW_QUERY, {
            "projectId": project_gid, "first": first,
            "ids": [f"gid://gitlab/Ai::DuoWorkflows::Workflow/{number}" for number in ids] if ids else None,
        })
        nodes = (data.get("duoWorkflowWorkflows") or {}).get("nodes")
        return [node for node in nodes if isinstance(node, dict)] if isinstance(nodes, list) else []

    def find_mention_session(self) -> dict | None:
        """The newest dawn session created since the mention; None while GitLab has not started one."""
        assert self.started_at is not None
        candidates = []
        for node in self.read_workflows(None, 10):
            name = str((node.get("aiCatalogItem") or {}).get("name") or "").lower()
            created = str(node.get("createdAt") or "")
            if name != "night-orders-dawn" or not created:
                continue
            try:
                when = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when >= self.started_at.replace(microsecond=0):
                candidates.append((when, node))
        return max(candidates, key=lambda pair: pair[0])[1] if candidates else None

    def wait(self) -> dict:
        """Poll the session until it is no longer created or running, within POLL_LIMIT. Returns the last node."""
        start = self.run.clock()
        failures = 0
        node: dict = {}
        while True:
            try:
                if self.report["workflow_id"] is None:
                    found = self.find_mention_session()
                    if found is not None:
                        self.report["workflow_id"] = int(str(found["id"]).rsplit("/", 1)[-1])
                        node = found
                else:
                    nodes = self.read_workflows([int(self.report["workflow_id"])], 1)
                    node = nodes[0] if nodes else node
                failures = 0
            except RelayError as error:
                failures += 1
                self.report["problems"].append(f"status read failed: {error}")
                if failures >= MAX_READ_FAILURES:
                    return node
            status = str(node.get("status") or "").lower()
            if status:
                self.report["status"] = status
            if status and status not in RUNNING:
                return node
            elapsed = self.run.clock() - start
            if elapsed >= POLL_LIMIT:
                self.report["problems"].append(f"the session was still {status or 'not found'} after "
                                               f"{POLL_LIMIT / 60:.0f} minutes; left as it is")
                return node
            self.run.sleep(min(POLL_EVERY, POLL_LIMIT - elapsed))

    def record_session(self, node: dict) -> None:
        checkpoint = node.get("latestCheckpoint") or {}
        self.report["web_url"] = str(node.get("webUrl") or self.report["web_url"] or "")
        self.report["execution_status"] = str(checkpoint.get("executionStatus") or "")
        self.report["errors"] = [str(error)[:600] for error in (checkpoint.get("errors") or [])[:8]]
        self.report["flow_notes"] = [str((item.get("note") or {}).get("url") or "")
                                     for item in (node.get("noteLinks") or {}).get("nodes") or []
                                     if (item.get("note") or {}).get("url")]
        self.say(f"session {self.report['workflow_id']}: status {self.report['status']}, execution "
                 f"{self.report['execution_status'] or 'unknown'}" + (f", errors: {self.report['errors']}"
                                                                      if self.report["errors"] else ""))

    def find_merge_request(self, node: dict) -> int | None:
        """The countersign merge request: the session's own link first, else an open countersign branch opened
        since the start (the author may be the person whose token started the flow, not the flow account)."""
        links = [(link.get("mergeRequest") or {}) for link in (node.get("mergeRequestLinks") or {}).get("nodes") or []]
        links = [mr for mr in links if mr.get("iid")]
        for mr in links:
            if "countersign" in str(mr.get("title") or "").lower():
                return int(mr["iid"])
        if links:
            return int(links[0]["iid"])
        branch = str(self.run.project().get("default_branch") or "main")
        opened = self.run.gitlab.json("list open merge requests", "GET", "/merge_requests", params={
            "state": "opened", "target_branch": branch, "order_by": "created_at", "sort": "desc", "per_page": 20})
        for mr in opened:
            if not isinstance(mr, dict) or not str(mr.get("source_branch") or "").startswith(f"countersign/{NIGHT}"):
                continue
            if self.started_at is not None:
                try:
                    created = datetime.fromisoformat(str(mr.get("created_at") or "").replace("Z", "+00:00"))
                except ValueError:
                    continue
                if created < self.started_at.replace(microsecond=0):
                    continue
            return int(mr["iid"])
        return None

    def verify(self, iid: int) -> None:
        """Read the merge request back: one changed file, ops/state.yml, that the repository's countersign parser
        accepts for this night's loose ends. Then make sure it stays a draft, unapproved and unmerged."""
        gitlab = self.run.gitlab
        mr = gitlab.json("read the countersign merge request", "GET", f"/merge_requests/{iid}")
        changes = gitlab.json("read merge request changes", "GET", f"/merge_requests/{iid}/changes")
        files = sorted({str(item.get("new_path") or item.get("old_path") or "") for item in changes.get("changes") or []})
        approvals = gitlab.json("read merge request approvals", "GET", f"/merge_requests/{iid}/approvals")
        approved_by = [str((item.get("user") or {}).get("username") or "") for item in approvals.get("approved_by") or []]
        info = {"iid": iid, "title": str(mr.get("title") or ""), "web_url": str(mr.get("web_url") or ""),
                "state": mr.get("state"), "draft": bool(mr.get("draft")), "merged_at": mr.get("merged_at"),
                "source_branch": mr.get("source_branch"), "target_branch": mr.get("target_branch"),
                "sha": mr.get("sha"), "author": str((mr.get("author") or {}).get("username") or ""),
                "changed_files": files, "approved_by": approved_by}
        self.report["merge_request"] = info
        self.report["merge_request_url"] = info["web_url"]
        self.say(f"merge request !{iid}: {info['title']!r}, {info['state']}, draft {info['draft']}, "
                 f"files {files}: {info['web_url']}")
        problems: list[str] = []
        if changes.get("overflow"):
            problems.append("the diff is incomplete (overflow), so the changed files cannot be checked")
        if files != [STATE_PATH]:
            problems.append(f"changed files are {files}, not only {STATE_PATH}")
        if mr.get("merged_at") or mr.get("state") == "merged":
            problems.append("the merge request was merged; this script never merges")
        if approved_by:
            problems.append(f"the merge request is approved by {approved_by}; this script never approves")
        state: dict[str, Any] = {"path": STATE_PATH}
        if files == [STATE_PATH] and mr.get("sha") and not changes.get("overflow"):
            content = gitlab.raw_file(STATE_PATH, str(mr["sha"]))
            targets_text = gitlab.raw_file(TARGETS_PATH, str(mr["sha"]))
            if content is None or targets_text is None:
                problems.append("ops/state.yml or ops/targets.yml could not be read at the merge request head")
            else:
                state.update(sha256=sha256(content), content=content)
                try:
                    data = yaml.safe_load(content)
                    kept = parse_state(data, parse_targets(yaml.safe_load(targets_text)))
                    named = str((data or {}).get("night")) if isinstance(data, dict) else None
                    state["night"] = named
                    if named != NIGHT:
                        problems.append(f"ops/state.yml names night {named}, not {NIGHT}; the morning would refuse it")
                    plan = plan_morning(self.ends, kept)
                    state["kept"] = [item.action.describe() + (f", until {item.until}" if item.until else "")
                                     + (f" (until_deployed !{item.until_deployed})" if item.until_deployed else "")
                                     for item in plan.kept]
                    state["restored"] = [f"{action.describe()}: {why}" for action, _, why in plan.undo]
                    state["by_hand"] = list(plan.by_hand)
                except OrdersError as error:
                    problems.extend(f"countersign parser: {text}" for text in error.problems)
                except (yaml.YAMLError, ValueError, TypeError, KeyError) as error:
                    problems.append(f"countersign parser: {type(error).__name__}: {str(error)[:300]}")
        state["validation"] = "passed" if not problems else "failed: " + "; ".join(problems)
        self.report["state_file"] = state
        self.report["validation"] = state["validation"]
        self.say(f"validation: {state['validation']}")
        if mr.get("state") == "opened" and not mr.get("draft") and not self.options.leave_title:
            title = f"Draft: {info['title']}"
            updated = gitlab.json("mark the merge request as a draft", "PUT", f"/merge_requests/{iid}",
                                  json={"title": title})
            info["draft"], info["title"] = bool(updated.get("draft")), str(updated.get("title") or title)
            self.report["review_adjustment"] = ("The flow opened the merge request without the draft flag. This script "
                                                "put Draft: in front of its title afterwards; the branch, commit and "
                                                "file are the flow's, unchanged.")
            self.say(f"marked !{iid} as a draft; nothing else changed")

    def execute(self) -> dict:
        report = self.report
        try:
            report["project_id"] = int(self.run.project()["id"])
            if self.options.workflow is None:
                issue = self.demo_issue()
                self.watch_log_note(issue)
                self.start(issue)
            node = self.wait()
            if node:
                self.record_session(node)
            if report["status"] == "finished":
                iid = self.find_merge_request(node)
                if iid is None:
                    report["problems"].append("the session finished but no countersign merge request was found")
                    report["result"] = "finished_without_merge_request"
                else:
                    self.verify(iid)
                    good = (report["validation"] == "passed" and report["merge_request"]["draft"]
                            and report["merge_request"]["state"] == "opened")
                    report["result"] = "verified" if good else "finished_with_problems"
            elif report["status"] in RUNNING or report["status"] == "not_started":
                report["result"] = "timed_out" if report["status"] in RUNNING else "not_started"
            else:
                report["result"] = report["status"]
        except RelayError as error:
            report["problems"].append(str(error))
            report["result"] = "blocked" if report["status"] == "not_started" else "error"
        report["observation"] = observation(report)
        self.say(f"result: {report['result']}" + (f" ({'; '.join(report['problems'])})" if report["problems"] else ""))
        return report


def observation(report: dict) -> str:
    """One plain sentence for the evidence file, from the recorded facts only."""
    mr = report.get("merge_request") or {}
    if report["result"] == "verified":
        kept = (report.get("state_file") or {}).get("kept") or []
        return (f"Dawn read the labelled demo watch log, opened countersign merge request !{mr.get('iid')} that "
                f"changes only {STATE_PATH}, and the repository's countersign parser accepted it: "
                f"{len(kept)} kept, {len((report.get('state_file') or {}).get('restored') or [])} to restore. "
                "The merge request is a draft, unapproved and unmerged.")
    if report["result"] in ("not_run", "not_started", "blocked"):
        return "The dawn flow was not started: " + ("; ".join(report["problems"]) or "nothing was sent.")
    return f"The run ended as {report['result']}: " + ("; ".join(report["problems"]) or "see the session and errors.")


def write_report(path: Path, text: str) -> None:
    json.loads(text)  # never leave partial JSON behind
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def main(argv=None, *, env=None, client=None, out: TextIO | None = None, now=None, clock=None, sleep=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="print the labelled demo log and goal; no network")
    parser.add_argument("--project", help="GitLab project id or path")
    parser.add_argument("--consumer-id", type=int, help="the dawn flow's consumer id (scripts/setup_flows.py)")
    parser.add_argument("--issue", type=int, help="an existing demo issue iid; by default found by title or created")
    parser.add_argument("--apply", action="store_true", help="post the log on the demo issue and start the dawn flow")
    parser.add_argument("--workflow", type=int, help="verify an existing dawn session instead of starting one")
    parser.add_argument("--start", choices=("api", "mention"), default="api",
                        help="start through the Flows API, or by a note that mentions the flow's account")
    parser.add_argument("--account", help="the dawn flow's service account, for --start mention")
    parser.add_argument("--leave-title", action="store_true", help="do not put Draft: in front of the merge request title")
    parser.add_argument("--source-commit", help="recorded in the evidence; defaults to git HEAD")
    parser.add_argument("--out", type=Path, help="write the evidence JSON (or the rendered Markdown with --render)")
    parser.add_argument("--base-url", help="GitLab HTTPS base URL; defaults to GITLAB_URL or gitlab.com")
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    out = sys.stdout if out is None else out
    if args.render:
        text = render_document(args.issue or 0)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            out.write(f"wrote {args.out}\n")
        else:
            out.write(text)
        return 0
    token = env.get("GITLAB_TOKEN", "").strip()
    base = args.base_url or env.get("GITLAB_URL") or "https://gitlab.com"
    url = urlsplit(base)
    if not token or url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        print("Set GITLAB_TOKEN and use an HTTPS GitLab base URL without credentials, query or fragment.", file=out)
        return 2
    if not args.project or not (args.apply or args.workflow):
        print("Give --project and either --apply (start a run) or --workflow (verify one).", file=out)
        return 2
    if args.apply and args.workflow is None and args.start == "api" and not args.consumer_id:
        print("--apply needs --consumer-id (the dawn flow's consumer id) with --start api.", file=out)
        return 2
    if args.apply and args.start == "mention" and not args.account:
        print("--start mention needs --account (the dawn flow's service account).", file=out)
        return 2
    try:
        with nullcontext(client) if client is not None else httpx.Client() as connection:
            run = DayOne(GitLab(Http20(connection), base, args.project, token), token=token, out=out, options=args,
                         now=now or (lambda: datetime.now(timezone.utc)), clock=clock or time.monotonic,
                         sleep=sleep or time.sleep)
            report = Demonstration(run, args).execute()
            if args.out:
                write_report(args.out, run.redact(json.dumps(report, indent=2)) + "\n")
                run.say(f"wrote {args.out}")
            return 0 if report["result"] == "verified" else 1
    except (RelayError, OSError, ValueError, yaml.YAMLError) as error:
        print(str(error).replace(token, "[GITLAB_TOKEN]"), file=out)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
