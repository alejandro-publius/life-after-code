"""The Night Orders day-one test: the live gate (docs/PLAN.md, decision D1) against the GitLab project.

    GITLAB_TOKEN=... python scripts/day_one.py --project 12345 --yes
    GITLAB_TOKEN=... python scripts/day_one.py --project group/sub/project --step whoami --step catalog
    GITLAB_TOKEN=... python scripts/day_one.py --project 12345 --step flow --consumer-id 77 --yes

Steps, in order. Each prints PASS, FAIL (with the HTTP status and GitLab's message) or SKIP (with why):

  whoami     who the token is, our role, the default branch, whether it is protected, and whether this role
             may push to it or merge into it
  publish    read-only: the project is public and GitLab detects the MIT licence (prints the clicks if not)
  issue      the standing watch issue "Tonight's watch" from .gitlab/issue_templates/Night watch.md
             (found or created); its iid is WATCH_ISSUE_IID
  flags      the two feature flags from ops/targets.yml: new_checkout on for the pilot customers in
             production, stock_from_cache off with no strategy; the production and staging environments
  catalog    every flow enabled in the project with its consumer id (GraphQL aiCatalogConfiguredItems);
             with --create-probe it creates and enables flows/probe.yml through GraphQL
  incident   the probe incident "Day-one probe incident" (found or created)
  flow       starts the probe flow on the incident through the Flows API, then watches the incident's notes
             for "probe ok" for up to six minutes; the note's author is FLOW_SERVICE_ACCOUNT
  signature  a branch, a one-line comment change to ops/night-orders.yml, a merge request, then an approve
             and a merge attempt: which one the role allows decides whether the signature is a merge or an
             approval; the merge request is closed and the branch deleted afterwards unless --keep
  cleanup    closes the probe incident

Safe to rerun: every step finds before it creates. Every HTTP call has a 20 second timeout. The token comes
only from the GITLAB_TOKEN environment variable and is never printed. Exit code 1 if any step fails, 2 if the
script could not start. --out writes the result table as JSON.

Sources (GitLab docs read from their source files on 2026-10-11, since docs.gitlab.com is blocked here):
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/graphql/reference/_index.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/feature_flags.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/environments.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/issues.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/notes.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/projects.md (license=true, permissions)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/protected_branches.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/commits.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_requests.md (merge, detailed_merge_status)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_request_approvals.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md (the clicks)
  docs/research/gitlab_day_one_api.md in this repository (what is verified and what is not)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TextIO
from urllib.parse import quote

import httpx
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "relay"))

from nightorders.gitlab_ports import WATCH_FLOW_PRIVILEGES, GitLab, Http, RelayError  # noqa: E402
from nightorders.gitlab_ports import _detail as error_detail  # noqa: E402

TIMEOUT_SECONDS = 20.0
STEPS = ("whoami", "publish", "issue", "flags", "catalog", "incident", "flow", "signature", "cleanup")
WRITE_STEPS = frozenset({"issue", "flags", "catalog", "incident", "flow", "signature", "cleanup"})
WATCH_TITLE = "Tonight's watch"
WATCH_LABEL = "night-watch"
WATCH_TEMPLATE = REPO / ".gitlab" / "issue_templates" / "Night watch.md"
INCIDENT_TITLE = "Day-one probe incident"
PROBE_NAME = "night-orders-probe"
PROBE_FLOW = REPO / "flows" / "probe.yml"
PROBE_TEXT = "probe ok"
ORDERS_FILE = "ops/night-orders.yml"
PROBE_LINE = "# day-one signature probe "
TARGETS_FILE = REPO / "ops" / "targets.yml"
PILOTS = tuple(f"pilot-{i:02d}" for i in range(1, 11))
PILOT_FLAG = "new_checkout"
PILOT_ENVIRONMENT = "production"
OFF_FLAG = "stock_from_cache"
DEFAULT_ENVIRONMENTS = ("production", "staging")
POLL_EVERY = 15.0
POLL_LIMIT = 6 * 60.0
MERGE_CHECK_EVERY = 5.0
MERGE_CHECK_LIMIT = 90.0
MERGE_PENDING = frozenset({"checking", "unchecked", "preparing", "approvals_syncing"})
ROLES = {0: "no access", 5: "Minimal Access", 10: "Guest", 15: "Planner", 20: "Reporter", 30: "Developer",
         40: "Maintainer", 50: "Owner"}
DEVELOPER = 30

CONFIGURED_ITEMS_QUERY = """
query($projectId: ProjectID!) {
  aiCatalogConfiguredItems(projectId: $projectId) {
    nodes { id enabled item { id name } serviceAccount { username } }
  }
}"""
FIND_ITEM_QUERY = """
query($search: String!) {
  aiCatalogItems(search: $search, itemType: FLOW) { nodes { id name project { id } } }
}"""
CREATE_FLOW_MUTATION = """
mutation($input: AiCatalogFlowCreateInput!) {
  aiCatalogFlowCreate(input: $input) { item { id name } errors }
}"""
ENABLE_FLOW_MUTATION = """
mutation($input: AiCatalogItemConsumerCreateInput!) {
  aiCatalogItemConsumerCreate(input: $input) {
    itemConsumer { id serviceAccount { username } } errors warnings
  }
}"""
WORKFLOW_STATUS_QUERY = """
query($workflowId: AiDuoWorkflowsWorkflowID!) {
  duoWorkflowWorkflows(workflowId: $workflowId) { nodes { id status humanStatus } }
}"""

# From doc/user/duo_agent_platform/flows/custom.md, "Create a flow" and "Enable a flow" (read 2026-10-11).
# Both say "You must have the Maintainer or Owner role for the project"; whether the hackathon's AI member
# role lets a Developer do this is the day-one question (unverified).
PROBE_CLICKS = (
    "To create the probe flow in the GitLab UI (the docs ask for the Maintainer or Owner role):",
    "  1. In the project's left sidebar select AI > Flows, then New flow.",
    f"  2. Display name: {PROBE_NAME}. Description: Day-one probe, reads an issue and posts one note."
    " Visibility: Private.",
    "  3. Under Configuration select Flow, paste flows/probe.yml into the editor, select Create flow.",
    "To enable it: AI > Flows > Managed tab > the flow > Enable (upper right) > Project: this project"
    " > Add triggers: Assign > Enable.",
    "Then rerun with --step catalog --step incident --step flow (or pass --consumer-id).",
)


class Http20(Http):
    """The relay's Http with a 20 second timeout on every call and no tick budget."""

    def __init__(self, client: httpx.Client):
        super().__init__(client)

    def call(self, what: str, method: str, url: str, *, expect: tuple[int, ...] = (200,), detail: bool = True,
             **kwargs: Any) -> httpx.Response:
        try:
            response = self.client.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
        except httpx.TimeoutException:
            raise RelayError(f"{what}: no answer within {TIMEOUT_SECONDS:.0f} s") from None
        except httpx.HTTPError as error:
            raise RelayError(f"{what}: could not connect ({type(error).__name__})") from None
        if response.status_code not in expect:
            raise RelayError(f"{what}: HTTP {response.status_code}{error_detail(response) if detail else ''}")
        return response


# Small helpers, pure.

def refused(response: httpx.Response) -> str:
    """'HTTP 401 (401 Unauthorized)' from an error answer."""
    return f"HTTP {response.status_code}{error_detail(response)}"


def gid_number(gid: Any) -> int | None:
    """The numeric suffix of a GitLab global ID such as gid://gitlab/Ai::Catalog::ItemConsumer/12."""
    try:
        return int(str(gid).rstrip("/").rsplit("/", 1)[-1])
    except ValueError:
        return None


def access_level(project: dict) -> int:
    """The highest access level in a project's permissions block, 0 when there is no membership."""
    levels = []
    for kind in ("project_access", "group_access"):
        entry = (project.get("permissions") or {}).get(kind) or {}
        if isinstance(entry.get("access_level"), int):
            levels.append(entry["access_level"])
    return max(levels, default=0)


def role_name(level: int) -> str:
    return ROLES.get(level, f"level {level}")


def level_allows(entries: list[dict], level: int, user_id: int | None) -> bool:
    """Whether a protected branch's merge or push access levels let this role (or this user) through.

    An entry with access_level 0 means "No one". Group and deploy key entries cannot be judged from here
    and do not count.
    """
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        if user_id is not None and entry.get("user_id") == user_id:
            return True
        if entry.get("user_id") is None and entry.get("group_id") is None and entry.get("deploy_key_id") is None:
            wanted = entry.get("access_level")
            if isinstance(wanted, int) and wanted > 0 and level >= wanted:
                return True
    return False


def pilot_flag_body(name: str = PILOT_FLAG, pilots: tuple[str, ...] = PILOTS,
                    environment: str = PILOT_ENVIRONMENT) -> dict:
    """POST /feature_flags body: the flag on for the pilot customers in one environment (demo data)."""
    return {
        "name": name,
        "version": "new_version_flag",
        "description": "Demo data: the Night Orders pilot customers take the new checkout path.",
        "active": True,
        "strategies": [{"name": "userWithId", "parameters": {"userIds": ",".join(pilots)},
                        "scopes": [{"environment_scope": environment}]}],
    }


def off_flag_body(name: str = OFF_FLAG) -> dict:
    """POST /feature_flags body: an inactive flag with no strategy, so the relay can turn it on in one
    environment alone (nightorders.gitlab_ports.flag_changes refuses to activate a flag whose strategies
    already reach another environment)."""
    return {
        "name": name,
        "version": "new_version_flag",
        "description": "Demo data: stock from the cache. Off until the relay or a person turns it on.",
        "active": False,
    }


def _user_ids(strategy: dict) -> set[str]:
    raw = str((strategy.get("parameters") or {}).get("userIds") or "")
    return {part.strip() for part in raw.split(",") if part.strip()}


def pilot_flag_update(flag: dict, pilots: tuple[str, ...] = PILOTS, environment: str = PILOT_ENVIRONMENT) -> dict | None:
    """PUT body that makes an existing flag match pilot_flag_body, or None when it already does.

    Keeps other environments' strategies. Removes a default (all users) strategy from the pilot environment:
    with it every checkout would take the new path and the demo would lose its old-path comparison.
    """
    changes: list[dict] = []
    found = False
    for strategy in flag.get("strategies") or []:
        if not isinstance(strategy, dict):
            continue
        scopes = [s for s in strategy.get("scopes") or [] if isinstance(s, dict)]
        here = [s for s in scopes if s.get("environment_scope") == environment]
        if not here:
            continue
        if strategy.get("name") == "userWithId" and not found:
            found = True
            if _user_ids(strategy) != set(pilots):
                changes.append({"id": strategy["id"], "parameters": {"userIds": ",".join(pilots)}})
        elif strategy.get("name") == "default":
            if len(here) == len(scopes):
                changes.append({"id": strategy["id"], "_destroy": True})
            else:
                changes.append({"id": strategy["id"], "scopes": [{"id": s["id"], "_destroy": True} for s in here]})
    if not found:
        changes.append(pilot_flag_body(pilots=pilots, environment=environment)["strategies"][0])
    update: dict = {}
    if changes:
        update["strategies"] = changes
    if not flag.get("active"):
        update["active"] = True
    return update or None


def off_flag_update(flag: dict) -> dict | None:
    """PUT body that makes an existing flag inactive with no strategy, or None when it already is."""
    update: dict = {}
    strategies = [s for s in flag.get("strategies") or [] if isinstance(s, dict) and "id" in s]
    if strategies:
        update["strategies"] = [{"id": s["id"], "_destroy": True} for s in strategies]
    if flag.get("active"):
        update["active"] = False
    return update or None


def describe_flag(flag: dict, pilots: tuple[str, ...] = PILOTS) -> str:
    """One line a person can read: name, active or not, each strategy with its scopes."""
    parts = []
    for strategy in flag.get("strategies") or []:
        if not isinstance(strategy, dict):
            continue
        scopes = ", ".join(str(s.get("environment_scope")) for s in strategy.get("scopes") or []) or "no scope"
        extra = ""
        if strategy.get("name") == "userWithId":
            ids = _user_ids(strategy)
            extra = f" ({pilots[0]}..{pilots[-1]})" if ids == set(pilots) else f" ({', '.join(sorted(ids)) or 'nobody'})"
        parts.append(f"{strategy.get('name')}{extra} in {scopes}")
    state = "active" if flag.get("active") else "inactive"
    return f"{flag.get('name')}: {state}, {'; '.join(parts) if parts else 'no strategies'}"


def flag_environments() -> tuple[str, ...]:
    """Every environment named under flags in ops/targets.yml, or the defaults when the file is not here."""
    try:
        data = yaml.safe_load(TARGETS_FILE.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return DEFAULT_ENVIRONMENTS
    found = sorted({str(env) for flag in data.get("flags") or [] for env in (flag.get("environments") or [])})
    return tuple(found) or DEFAULT_ENVIRONMENTS


def watch_template() -> str:
    """The watch issue's description from the repository's template."""
    try:
        return WATCH_TEMPLATE.read_text(encoding="utf-8")
    except OSError:
        return f"## {WATCH_TITLE}\n\nThis issue stays open. Each evening the on-call person assigns it to the dusk flow.\n"


def flow_body(project_id: str, consumer_id: int, issue_iid: int, goal: str) -> dict:
    """The Flows API body, the same shape the relay sends for the watch flow (gitlab_ports.start_watch_flow)."""
    return {
        "project_id": str(project_id),
        "ai_catalog_item_consumer_id": int(consumer_id),
        "goal": goal,
        "issue_id": int(issue_iid),
        "start_workflow": True,
        "allow_agent_to_request_user": False,
        "agent_privileges": list(WATCH_FLOW_PRIVILEGES),
        "pre_approved_agent_privileges": list(WATCH_FLOW_PRIVILEGES),
    }


def probe_content(current: str, stamp: str) -> str:
    """ops/night-orders.yml with one probe comment line at the end: an earlier run's line is replaced, not
    kept, so repeated merges do not make the file grow."""
    kept = [line for line in current.splitlines() if not line.startswith(PROBE_LINE)]
    return "\n".join(kept).rstrip("\n") + f"\n{PROBE_LINE}{stamp}: this comment line tests merge and approve rights.\n"


def wait_for_note(fetch: Callable[[], list[dict]], text: str, *, clock: Callable[[], float],
                  sleep: Callable[[float], None], ignore: set[int] | frozenset[int] = frozenset(),
                  ignore_authors: set[str] | frozenset[str] = frozenset(),
                  every: float = POLL_EVERY, limit: float = POLL_LIMIT) -> tuple[dict | None, float, str]:
    """Poll the notes until one that is not a system note, not in ignore, not by an ignored author (the person
    running this script, say), holds the text (any case). Notes are scanned oldest first, so the first answer
    wins when GitLab lists newest first.

    Returns (note or None, seconds elapsed, last fetch error or ""). A failed fetch does not end the wait.
    """
    start = clock()
    wanted = text.lower()
    skip_authors = {a.lower() for a in ignore_authors}
    problem = ""
    while True:
        try:
            notes = fetch()
            problem = ""
        except RelayError as error:
            notes = []
            problem = str(error)
        for note in reversed(notes):
            if not isinstance(note, dict) or note.get("system") or note.get("id") in ignore:
                continue
            author = str((note.get("author") or {}).get("username") or "").lower()
            if author in skip_authors:
                continue
            if wanted in str(note.get("body") or "").lower():
                return note, clock() - start, problem
        elapsed = clock() - start
        if elapsed >= limit:
            return None, elapsed, problem
        sleep(min(every, limit - elapsed))


@dataclass
class Result:
    step: str
    status: str                       # PASS, FAIL or SKIP
    reason: str = ""                  # why, for FAIL and SKIP
    lines: list[str] = field(default_factory=list)

    def dump(self) -> dict:
        return {"step": self.step, "status": self.status, "reason": self.reason, "lines": list(self.lines)}


class Skip(Exception):
    """A step that cannot run here; the message says why."""


class DayOne:
    """One run of the day-one test. Every line printed goes through say(), which redacts the token."""

    def __init__(self, gitlab: GitLab, *, token: str, out: TextIO, options: argparse.Namespace,
                 now: Callable[[], datetime], clock: Callable[[], float], sleep: Callable[[float], None]):
        self.gitlab = gitlab
        self._token = token
        self.out = out
        self.options = options
        self.now = now
        self.clock = clock
        self.sleep = sleep
        self.results: list[Result] = []
        self.values: dict[str, Any] = {}
        self._me: dict | None = None
        self._project: dict | None = None

    # Printing.

    def redact(self, text: str) -> str:
        return text.replace(self._token, "[GITLAB_TOKEN]") if self._token else text

    def say(self, text: str = "") -> None:
        self.out.write(self.redact(text) + "\n")
        self.out.flush()

    # What most steps need.

    def me(self) -> dict:
        if self._me is None:
            self._me = self.gitlab.json("read user", "GET", "/user", in_project=False)
        return self._me

    def project(self) -> dict:
        if self._project is None:
            self._project = self.gitlab.json("read project", "GET", "", params={"license": "true"})
        return self._project

    def project_id(self) -> str:
        return str(self.project()["id"])

    def default_branch(self) -> str:
        return str(self.project().get("default_branch") or "main")

    def graphql(self, what: str, query: str, variables: dict | None = None) -> dict:
        data = self.gitlab.json(what, "POST", "/graphql", in_project=False,
                                json={"query": query, "variables": variables or {}})
        if not isinstance(data, dict):
            raise RelayError(f"GitLab {what}: GraphQL answered with no object")
        errors = data.get("errors")
        if errors:
            messages = "; ".join(str(e.get("message") if isinstance(e, dict) else e) for e in errors)
            raise RelayError(f"GitLab {what}: GraphQL error ({' '.join(messages.split())[:300]})")
        return data.get("data") or {}

    def find_issue(self, title: str, issue_type: str | None = None) -> dict | None:
        """The oldest open issue with exactly this title, so a rerun finds the same one."""
        params: dict[str, Any] = {"search": title, "in": "title", "state": "opened", "per_page": 100,
                                  "order_by": "created_at", "sort": "asc"}
        if issue_type:
            params["issue_type"] = issue_type
        for issue in self.gitlab.json(f"find issue {title!r}", "GET", "/issues", params=params):
            if isinstance(issue, dict) and str(issue.get("title") or "").strip().lower() == title.lower():
                return issue
        return None

    # The steps.

    def step_whoami(self, lines: list[str]) -> None:
        me = self.me()
        project = self.project()
        user_id = me.get("id") if isinstance(me.get("id"), int) else None
        lines.append(f"user {me.get('username')} (id {me.get('id')}, {me.get('name')}, state {me.get('state')})")
        level = access_level(project)
        role = role_name(level)
        lines.append(f"project {project.get('path_with_namespace')} (id {project.get('id')}), visibility "
                     f"{project.get('visibility')}, our role {role}" + ("" if level else " (no membership found)"))
        member = self.gitlab.call("read membership", "GET", f"/members/all/{user_id}", expect=(200, 403, 404)) \
            if user_id is not None else None
        if member is not None and member.status_code == 200:
            custom = (member.json() or {}).get("member_role")
            if isinstance(custom, dict) and custom.get("name"):
                lines.append(f"custom role {custom.get('name')} (id {custom.get('id')}) on top of {role}")
        if "duo_remote_flows_enabled" in project:
            lines.append(f"flows in this project (duo_remote_flows_enabled): {project.get('duo_remote_flows_enabled')}")
        default = self.default_branch()
        answer = self.gitlab.call("read protected branch", "GET", f"/protected_branches/{quote(default, safe='')}",
                                  expect=(200, 403, 404))
        if answer.status_code == 200:
            protection = answer.json() or {}
            can_push = level_allows(protection.get("push_access_levels") or [], level, user_id)
            can_merge = level_allows(protection.get("merge_access_levels") or [], level, user_id)
            needs = ", ".join(role_name(e.get("access_level", 0)) for e in protection.get("merge_access_levels") or []
                              if isinstance(e, dict)) or "nobody"
            lines.append(f"default branch {default}: protected (merge allowed for {needs})")
            protected: bool | None = True
        elif answer.status_code == 404:
            protected = False
            can_push = can_merge = level >= DEVELOPER
            lines.append(f"default branch {default}: not protected")
        else:
            protected = None
            can_push = can_merge = False
            lines.append(f"default branch {default}: protection not readable with this role ({refused(answer)}); "
                         "assume GitLab's default, Maintainers only")
        lines.append(f"push to {default} as {role}: {'allowed' if can_push else 'not allowed'}")
        lines.append(f"merge into {default} as {role}: {'allowed' if can_merge else 'not allowed'}"
                     + ("" if can_merge else " (the signature would be an approval)"))
        self.values.update({"USER": me.get("username"), "USER_ID": user_id, "PROJECT_ID": project.get("id"),
                            "PROJECT_PATH": project.get("path_with_namespace"), "ACCESS_LEVEL": level, "ROLE": role,
                            "DEFAULT_BRANCH": default, "DEFAULT_BRANCH_PROTECTED": protected,
                            "CAN_PUSH_DEFAULT": can_push, "CAN_MERGE_DEFAULT": can_merge})

    def step_publish(self, lines: list[str]) -> None:
        project = self.project()
        visibility = str(project.get("visibility") or "unknown")
        licence = project.get("license") if isinstance(project.get("license"), dict) else {}
        key = str(licence.get("key") or "")
        lines.append(f"visibility: {visibility}")
        lines.append(f"licence detected: {licence.get('name') or 'none'}" + (f" ({project['license_url']})" if project.get("license_url") else ""))
        problems = []
        if visibility != "public":
            problems.append("project is not public")
            lines.append("Alex: Settings > General > Visibility, project features, permissions > Project visibility: "
                         "Public > Save changes. GitLab lets only the Owner role change visibility; with a lower "
                         "role ask the organizers.")
        if key.lower() != "mit":
            problems.append("MIT licence not detected")
            lines.append(f"Alex: push the repository so LICENSE (MIT) is at the root of {self.default_branch()}; "
                         "GitLab detects the licence from that file and shows it on the project page.")
        if problems:
            raise RelayError("; ".join(problems))

    def step_issue(self, lines: list[str]) -> None:
        issue = self.find_issue(WATCH_TITLE)
        if issue is None:
            issue = self.gitlab.json("create watch issue", "POST", "/issues", expect=(200, 201),
                                     json={"title": WATCH_TITLE, "description": watch_template(), "labels": WATCH_LABEL})
            lines.append(f"created issue #{issue.get('iid')} from .gitlab/issue_templates/Night watch.md")
        else:
            lines.append(f"found open issue #{issue.get('iid')} {WATCH_TITLE!r}")
        if issue.get("web_url"):
            lines.append(str(issue["web_url"]))
        self.values["WATCH_ISSUE_IID"] = int(issue["iid"])
        lines.append(f"WATCH_ISSUE_IID={issue['iid']}")

    def _ensure_environments(self, lines: list[str]) -> None:
        existing = self.gitlab.json("list environments", "GET", "/environments", params={"per_page": 100})
        names = {str(e.get("name")) for e in existing if isinstance(e, dict)}
        for name in flag_environments():
            if name in names:
                lines.append(f"environment {name}: exists")
            else:
                self.gitlab.call("create environment", "POST", "/environments", expect=(200, 201),
                                 json={"name": name, "tier": name if name in ("production", "staging") else "other"})
                lines.append(f"environment {name}: created")

    def _ensure_flag(self, name: str, create: Callable[[], dict], update: Callable[[dict], dict | None],
                     lines: list[str]) -> None:
        path = f"/feature_flags/{quote(name, safe='')}"
        answer = self.gitlab.call(f"read flag {name}", "GET", path, expect=(200, 404))
        if answer.status_code == 404:
            self.gitlab.call(f"create flag {name}", "POST", "/feature_flags", expect=(200, 201), json=create())
            lines.append(f"flag {name}: created")
        else:
            change = update(answer.json() or {})
            if change is None:
                lines.append(f"flag {name}: already as wanted")
            else:
                self.gitlab.call(f"update flag {name}", "PUT", path, json=change)
                lines.append(f"flag {name}: updated ({', '.join(sorted(change))})")

    def step_flags(self, lines: list[str]) -> None:
        self._ensure_environments(lines)
        self._ensure_flag(PILOT_FLAG, pilot_flag_body, pilot_flag_update, lines)
        self._ensure_flag(OFF_FLAG, off_flag_body, off_flag_update, lines)
        for name in (PILOT_FLAG, OFF_FLAG):
            flag = self.gitlab.json(f"read back flag {name}", "GET", f"/feature_flags/{quote(name, safe='')}")
            lines.append("read back: " + describe_flag(flag))
        lines.append("What the shop's Unleash client would see cannot be checked from here: GitLab serves flags to "
                     "clients only with the instance ID from Deploy > Feature flags > Configure, which no REST or "
                     "GraphQL call exposes.")

    def step_catalog(self, lines: list[str]) -> None:
        gid = f"gid://gitlab/Project/{self.project_id()}"
        data = self.graphql("list configured flows", CONFIGURED_ITEMS_QUERY, {"projectId": gid})
        nodes = ((data.get("aiCatalogConfiguredItems") or {}).get("nodes")) or []
        probe_consumer = None
        for node in nodes:
            if not isinstance(node, dict):
                continue
            consumer = gid_number(node.get("id"))
            name = str((node.get("item") or {}).get("name") or "?")
            account = str((node.get("serviceAccount") or {}).get("username") or "")
            state = "" if node.get("enabled", True) else " (disabled)"
            lines.append(f"flow {name}: consumer id {consumer}{state}" + (f", service account {account}" if account else ""))
            if name == PROBE_NAME and consumer is not None and node.get("enabled", True):
                probe_consumer = consumer
                self.values["FLOW_CONSUMER_ID"] = consumer
                if account:
                    self.values["FLOW_SERVICE_ACCOUNT_HINT"] = account
            elif name == PROBE_NAME and consumer is not None:
                lines.append(f"{PROBE_NAME} is in the project but disabled: enable it under AI, Flows "
                             "(docs/FLOWS_SETUP.md) before the flow step; its consumer id is not used")
        if not nodes:
            lines.append("no flows are enabled in this project yet")
        if probe_consumer is None and self.options.create_probe:
            probe_consumer = self._create_probe(gid, lines)
            if probe_consumer is not None:
                self.values["FLOW_CONSUMER_ID"] = probe_consumer
        if probe_consumer is None:
            lines.extend(PROBE_CLICKS)
            if not self.options.create_probe:
                lines.append("Or rerun with --create-probe to try the GraphQL mutations with this token.")

    def _create_probe(self, project_gid: str, lines: list[str]) -> int | None:
        definition = PROBE_FLOW.read_text(encoding="utf-8")
        found = self.graphql("find the probe flow item", FIND_ITEM_QUERY, {"search": PROBE_NAME})
        item_id = None
        for node in ((found.get("aiCatalogItems") or {}).get("nodes")) or []:
            # Only this project's item: the catalog search also finds other projects' items with the same name.
            if isinstance(node, dict) and node.get("name") == PROBE_NAME \
                    and (node.get("project") or {}).get("id") == project_gid:
                item_id = node.get("id")
                lines.append(f"catalog item {PROBE_NAME} exists: {item_id}")
                break
        if item_id is None:
            created = self.graphql("create the probe flow (aiCatalogFlowCreate)", CREATE_FLOW_MUTATION, {"input": {
                "projectId": project_gid, "name": PROBE_NAME,
                "description": "Day-one probe: reads the issue in the goal and posts one note that says probe ok.",
                "definition": definition, "release": True, "visibility": "PRIVATE"}})
            payload = created.get("aiCatalogFlowCreate") or {}
            if payload.get("errors"):
                raise RelayError(f"aiCatalogFlowCreate refused: {'; '.join(map(str, payload['errors']))[:300]}")
            item_id = (payload.get("item") or {}).get("id")
            lines.append(f"created catalog item {PROBE_NAME}: {item_id}")
        if not item_id:
            raise RelayError("aiCatalogFlowCreate returned no item id")
        enabled = self.graphql("enable the probe flow (aiCatalogItemConsumerCreate)", ENABLE_FLOW_MUTATION, {"input": {
            "itemId": item_id, "target": {"projectId": project_gid}, "triggerTypes": ["assign"]}})
        payload = enabled.get("aiCatalogItemConsumerCreate") or {}
        if payload.get("errors"):
            raise RelayError(f"aiCatalogItemConsumerCreate refused: {'; '.join(map(str, payload['errors']))[:300]}")
        for warning in payload.get("warnings") or []:
            lines.append(f"warning from GitLab: {warning}")
        consumer = payload.get("itemConsumer") or {}
        number = gid_number(consumer.get("id"))
        account = str((consumer.get("serviceAccount") or {}).get("username") or "")
        lines.append(f"enabled {PROBE_NAME} in the project: consumer id {number}"
                     + (f", service account {account}" if account else ""))
        if account:
            self.values["FLOW_SERVICE_ACCOUNT_HINT"] = account
        return number

    def step_incident(self, lines: list[str]) -> None:
        incident = self.find_issue(INCIDENT_TITLE, issue_type="incident")
        if incident is None:
            stamp = self.now().astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            description = (
                f"Evidence pack (demo data, written by scripts/day_one.py at {stamp}): no production signal "
                "breached; this incident only tests that a flow started through the Flows API can read it.\n"
                f"Expected: the probe flow posts one note here that says exactly: {PROBE_TEXT}\n")
            incident = self.gitlab.json("create probe incident", "POST", "/issues", expect=(200, 201),
                                        json={"title": INCIDENT_TITLE, "description": description,
                                              "issue_type": "incident"})
            lines.append(f"created incident #{incident.get('iid')}")
        else:
            lines.append(f"found open incident #{incident.get('iid')}")
        if incident.get("web_url"):
            lines.append(str(incident["web_url"]))
        self.values["INCIDENT_IID"] = int(incident["iid"])

    def _incident_iid(self) -> int:
        iid = self.values.get("INCIDENT_IID")
        if iid is None:
            incident = self.find_issue(INCIDENT_TITLE, issue_type="incident")
            if incident is None:
                raise Skip("no open probe incident: run the incident step first")
            iid = int(incident["iid"])
            self.values["INCIDENT_IID"] = iid
        return int(iid)

    def step_flow(self, lines: list[str]) -> None:
        consumer = self.options.consumer_id or self.values.get("FLOW_CONSUMER_ID")
        if not consumer:
            raise Skip("no consumer id for the probe flow: enable it and run the catalog step, or pass --consumer-id")
        iid = self._incident_iid()
        notes_path = f"/issues/{iid}/notes"
        params = {"sort": "desc", "order_by": "created_at", "per_page": 100}

        def fetch() -> list[dict]:
            return self.gitlab.json("read incident notes", "GET", notes_path, params=params)

        before = {n.get("id") for n in fetch() if isinstance(n, dict)}
        goal = (f"Issue #{iid} in project {self.project().get('path_with_namespace') or self.project_id()}. "
                f"Read it and post one note that says exactly: {PROBE_TEXT}")
        started = self.gitlab.json("start the probe flow", "POST", "/ai/duo_workflows/workflows", in_project=False,
                                   expect=(200, 201), json=flow_body(self.project_id(), int(consumer), iid, goal))
        workflow = started.get("id")
        lines.append(f"flow started: workflow {workflow}, status {started.get('status')}, consumer id {consumer}")
        if started.get("web_url"):
            lines.append(str(started["web_url"]))
        self.values["WORKFLOW_ID"] = workflow
        try:
            me = str(self.me().get("username") or "").lower()
        except RelayError:
            me = ""  # the person's own notes are then told apart by the hint below, not skipped
        note, elapsed, problem = wait_for_note(fetch, PROBE_TEXT, clock=self.clock, sleep=self.sleep, ignore=before,
                                               ignore_authors={me} if me else frozenset())
        if problem:
            lines.append(f"last problem while polling: {problem}")
        status = self._workflow_status(workflow)
        if status:
            lines.append(f"workflow status now: {status}")
        if note is None:
            raise RelayError(f"no note with {PROBE_TEXT!r} on incident #{iid} within {elapsed:.0f} s "
                             f"(workflow {workflow}" + (f", status {status}" if status else "") + ")")
        author = str((note.get("author") or {}).get("username") or "?")
        lines.append(f"note {note.get('id')} by {author} after {elapsed:.0f} s: {str(note.get('body') or '').strip()[:80]!r}")
        self.values["FLOW_SERVICE_ACCOUNT"] = author
        self.values["FLOW_SECONDS"] = round(elapsed)
        lines.append(f"FLOW_SERVICE_ACCOUNT={author}")
        if not any(hint in author.lower() for hint in ("duo", "flow", "ai-", "bot", "agent")):
            lines.append(f"{author} does not look like a flow's service account: check the flow session in GitLab "
                         "(AI, Sessions) before using this value")
        expected = self.options.flow_account
        if expected and expected.lower() != author.lower():
            lines.append(f"--flow-account {expected} does not match the note's author {author}")

    def _workflow_status(self, workflow: Any) -> str:
        if workflow is None:
            return ""
        try:
            data = self.graphql("read workflow status", WORKFLOW_STATUS_QUERY,
                                {"workflowId": f"gid://gitlab/Ai::DuoWorkflows::Workflow/{workflow}"})
        except RelayError as error:
            return f"not readable ({error})"
        for node in ((data.get("duoWorkflowWorkflows") or {}).get("nodes")) or []:
            if isinstance(node, dict):
                return str(node.get("humanStatus") or node.get("status") or "")
        return ""

    def _wait_mergeable(self, iid: int) -> str:
        start = self.clock()
        while True:
            mr = self.gitlab.json("read merge request", "GET", f"/merge_requests/{iid}")
            status = str(mr.get("detailed_merge_status") or mr.get("merge_status") or "")
            if status not in MERGE_PENDING or self.clock() - start >= MERGE_CHECK_LIMIT:
                return status
            self.sleep(MERGE_CHECK_EVERY)

    def step_signature(self, lines: list[str]) -> None:
        default = self.default_branch()
        stamp = self.now().strftime("%Y%m%d-%H%M%S")
        branch = f"day-one/{stamp}"
        current = self.gitlab.raw_file(ORDERS_FILE, default)
        if current is None:
            raise Skip(f"{ORDERS_FILE} is not on {default}: push the repository first")
        content = probe_content(current, stamp)
        title = f"Day-one signature probe {stamp}"
        self.gitlab.call("create branch and commit", "POST", "/repository/commits", expect=(200, 201), json={
            "branch": branch, "start_branch": default, "commit_message": title,
            "actions": [{"action": "update", "file_path": ORDERS_FILE, "content": content}]})
        mr = self.gitlab.json("open merge request", "POST", "/merge_requests", expect=(200, 201), json={
            "source_branch": branch, "target_branch": default, "title": title, "remove_source_branch": True,
            "description": "Day-one test of the signature. Opened by scripts/day_one.py; closed by it unless --keep."})
        iid = int(mr["iid"])
        lines.append(f"branch {branch}, merge request !{iid}" + (f" {mr['web_url']}" if mr.get("web_url") else ""))
        merged = approved = False
        try:
            approve = self.gitlab.call("approve", "POST", f"/merge_requests/{iid}/approve",
                                       expect=(200, 201, 401, 403, 404, 405, 409, 422))
            approved = approve.status_code in (200, 201)
            if approved:
                lines.append(f"approve: allowed (HTTP {approve.status_code})")
            else:
                lines.append(f"approve: refused ({refused(approve)})")
                if approve.status_code in (401, 403):
                    lines.append("  GitLab blocks an author approving their own merge request unless the project allows "
                                 "it, so this refusal does not settle the role. The dusk flow's merge request is opened "
                                 "by its service account; Alex approving that one is the real test.")
            status = self._wait_mergeable(iid)
            merge = self.gitlab.call("merge", "PUT", f"/merge_requests/{iid}/merge",
                                     expect=(200, 400, 401, 403, 405, 406, 409, 422))
            merged = merge.status_code == 200
            if merged:
                lines.append(f"merge: done (HTTP 200) into {default}")
            elif merge.status_code in (401, 403):
                lines.append(f"merge: refused ({refused(merge)}): this role may not merge into {default}")
            else:
                lines.append(f"merge: not possible now ({refused(merge)}), detailed_merge_status {status or 'unknown'}")
        finally:
            if not self.options.keep:
                self._tidy_signature(iid, branch, merged, lines)
        if merged:
            method = "merge"
        elif approved:
            method = "approval"
        else:
            method = "undecided"
        self.values["SIGNATURE_METHOD"] = method
        lines.append(f"SIGNATURE_METHOD={method}")
        if method == "undecided":
            raise RelayError("neither merge nor approve worked for this account on its own merge request; "
                             "settle the approval right on a merge request opened by someone else")

    def _tidy_signature(self, iid: int, branch: str, merged: bool, lines: list[str]) -> None:
        try:
            if not merged:
                self.gitlab.call("close merge request", "PUT", f"/merge_requests/{iid}", json={"state_event": "close"})
            self.gitlab.call("delete branch", "DELETE", f"/repository/branches/{quote(branch, safe='')}",
                             expect=(200, 204, 404))
            lines.append(("" if merged else f"merge request !{iid} closed and ") + f"branch {branch} deleted")
        except RelayError as error:
            lines.append(f"tidy up failed: {error} (close !{iid} and delete {branch} by hand)")

    def step_cleanup(self, lines: list[str]) -> None:
        incident = self.find_issue(INCIDENT_TITLE, issue_type="incident")
        if incident is None:
            raise Skip("no open probe incident to close")
        iid = int(incident["iid"])
        self.gitlab.call("post closing note", "POST", f"/issues/{iid}/notes", expect=(200, 201),
                         json={"body": "Day-one probe over. Closed by scripts/day_one.py."})
        self.gitlab.call("close incident", "PUT", f"/issues/{iid}", json={"state_event": "close"})
        lines.append(f"incident #{iid} closed")

    # Running.

    def run_step(self, name: str, skip_because: str = "") -> Result:
        lines: list[str] = []
        if skip_because:
            result = Result(name, "SKIP", skip_because)
        else:
            try:
                getattr(self, f"step_{name}")(lines)
                result = Result(name, "PASS", "", lines)
            except Skip as why:
                result = Result(name, "SKIP", str(why), lines)
            except RelayError as error:
                result = Result(name, "FAIL", str(error), lines)
            except (AttributeError, KeyError, TypeError, ValueError) as error:
                result = Result(name, "FAIL", f"unexpected answer from GitLab ({type(error).__name__}: {error})", lines)
        result.lines = [self.redact(line) for line in result.lines]
        result.reason = self.redact(result.reason)
        self.results.append(result)
        self.say(f"{name}: {result.status}" + (f" ({result.reason})" if result.reason else ""))
        for line in result.lines:
            self.say(f"  {line}")
        return result

    def summary(self) -> None:
        self.say()
        self.say("Result")
        width = max(len(r.step) for r in self.results) if self.results else 8
        for result in self.results:
            self.say(f"  {result.step.ljust(width)}  {result.status}" + (f"  {result.reason}" if result.reason else ""))
        keys = ("WATCH_ISSUE_IID", "FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT", "FLOW_SECONDS", "SIGNATURE_METHOD",
                "CAN_MERGE_DEFAULT", "ROLE")
        shown = [(k, self.values[k]) for k in keys if k in self.values]
        if shown:
            self.say("Values for the relay's settings")
            for key, value in shown:
                self.say(f"  {key}={value}")

    def dump(self) -> dict:
        return {"project": self.gitlab.project_id, "at": self.now().isoformat(),
                "results": [r.dump() for r in self.results],
                "values": {k: v for k, v in self.values.items()},
                "failed": any(r.status == "FAIL" for r in self.results)}


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="day_one.py", description="The Night Orders day-one test against GitLab.")
    parser.add_argument("--project", required=True, help="numeric project id or full path (group/sub/project)")
    parser.add_argument("--step", action="append", choices=STEPS, metavar="NAME",
                        help="run only this step (repeatable); one of " + ", ".join(STEPS))
    parser.add_argument("--consumer-id", type=int, help="AI catalog item consumer id of the probe flow")
    parser.add_argument("--flow-account", help="username the probe flow is expected to post as")
    parser.add_argument("--create-probe", action="store_true", help="catalog step: create and enable flows/probe.yml")
    parser.add_argument("--keep", action="store_true", help="signature step: keep the merge request and branch")
    parser.add_argument("--yes", action="store_true", help="run the steps that write without asking")
    parser.add_argument("--out", help="write the result table as JSON to this file")
    parser.add_argument("--base-url", default=None, help="GitLab base URL (default: GITLAB_URL or https://gitlab.com)")
    return parser.parse_args(argv)


def confirm(out: TextIO, steps: list[str]) -> bool:
    """Ask before writing. Without a terminal the answer is no: pass --yes."""
    writes = ", ".join(s for s in steps if s in WRITE_STEPS)
    if not sys.stdin or not sys.stdin.isatty():
        out.write(f"Steps that write to GitLab ({writes}) need --yes when there is no terminal.\n")
        return False
    out.write(f"These steps write to the GitLab project: {writes}. Go on? [y/N] ")
    out.flush()
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = ""
    return answer in ("y", "yes")


def main(argv: list[str] | None = None, *, env: dict[str, str] | None = None, out: TextIO | None = None,
         client: httpx.Client | None = None, now: Callable[[], datetime] | None = None,
         clock: Callable[[], float] | None = None, sleep: Callable[[float], None] | None = None,
         ask: Callable[[list[str]], bool] | None = None) -> int:
    args = parse_args(argv)
    env = dict(os.environ) if env is None else env
    out = sys.stdout if out is None else out
    token = (env.get("GITLAB_TOKEN") or "").strip()
    if not token:
        out.write("GITLAB_TOKEN is not set. Put a personal access token with the api scope in that environment "
                  "variable (never as an argument).\n")
        return 2
    base_url = args.base_url or env.get("GITLAB_URL") or "https://gitlab.com"
    gitlab = GitLab(Http20(client or httpx.Client()), base_url, args.project, token)
    run = DayOne(gitlab, token=token, out=out, options=args,
                 now=now or (lambda: datetime.now(timezone.utc)), clock=clock or time.monotonic,
                 sleep=sleep or time.sleep)
    steps = list(args.step) if args.step else list(STEPS)
    allowed_to_write = args.yes
    if not allowed_to_write and any(s in WRITE_STEPS for s in steps):
        allowed_to_write = (ask or (lambda names: confirm(out, names)))(steps)
    run.say(f"Day-one test, project {args.project} at {base_url}, {run.now().strftime('%Y-%m-%d %H:%M %Z')}")
    for name in steps:
        why = "" if allowed_to_write or name not in WRITE_STEPS else "writes to GitLab: not confirmed (pass --yes)"
        run.run_step(name, why)
    run.summary()
    if args.out:
        Path(args.out).write_text(run.redact(json.dumps(run.dump(), indent=2, sort_keys=True)) + "\n", encoding="utf-8")
        run.say(f"written: {args.out}")
    return 1 if any(r.status == "FAIL" for r in run.results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
