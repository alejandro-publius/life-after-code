"""The relay's ports to the outside world: GitLab, Cloud Run and a push service.

GitLabPorts implements nightorders.watch.Ports against real services. It decides nothing: it does what
the Watch asks and reports what it finds. Every request has a 10 second timeout, a tick can also have an
overall time budget, and every failure is a RelayError whose message is safe to log and to page: it never
holds a URL, a token or the push topic.

  open_incident     POST /projects/:id/issues with issue_type incident; the evidence pack is the description
  note              POST /projects/:id/issues/:iid/notes
  start_watch_flow  POST /ai/duo_workflows/workflows (Flows API) with the incident as issue_id, or with FLOW_START
                    mention a note on the incident that mentions the flow's service account (its Mention trigger)
  request_note      the newest note by the watch flow's service account, written after the ask, that holds
                    a night-orders-request block
  apply             flag_set: the Feature Flags API, changing only the named environment's scopes;
                    traffic_to_revision: the Cloud Run Admin API v2, 100% of traffic to the named revision, done
                    once its operation is done and the service reports that traffic as serving.
                    Both return a Change with a snapshot of the target from before the action
  restore           the target back exactly as that snapshot says: the environment's earlier strategies, or
                    the earlier traffic allocation
  page              a push to an ntfy topic, and the page as a note on the incident (the thumbs-up target)
  thumbs_up         every thumbsup reaction on that page note, oldest first; decide.approve_suggestion checks
                    who and when, so a teammate's reaction cannot block the on-call person's. A page note that
                    failed while the push went out is posted here first, on a later tick
  close_incident    a closing note, then state_event close
  watch_note        a note on the standing watch issue (the watch log, the countersign result)
  start_dawn_flow   the same for the dawn flow, on the watch issue

Sources, read on 2026-10-06 (GitLab docs from their source files, since docs.gitlab.com is blocked here):
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/issues.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/notes.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/emoji_reactions.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/feature_flags.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/feature_flags.rb (strategies, scopes: id, _destroy)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/concerns/has_environment_scope.rb (* is a wildcard)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/award_emoji.rb (thumbs-up is named thumbsup)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md (Mention: the
    flow receives the comment; read 2026-10-14)
  https://run.googleapis.com/$discovery/rest?version=v2 (services.patch, updateMask, TrafficTarget; read again on
    2026-10-14 for operations.get, reconciling, terminalCondition and trafficStatuses)
  https://github.com/binwiederhier/ntfy/blob/main/docs/publish.md (Title, Priority, Tags and Click headers)
"""

from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterator
from urllib.parse import quote

import httpx
import yaml

from .model import Action, Change, describe_before, shipped_words

TIMEOUT_SECONDS = 10.0
CLOUD_RUN_POLL_SECONDS = 1.0   # a traffic change's operation is read this often until Cloud Run says it is done
CLOUD_RUN_WAIT_SECONDS = 30.0  # and for this long at most, never past the tick's budget
METADATA_TOKEN_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
CLOUD_RUN_API = "https://run.googleapis.com/v2"
STATE_FILE = "ops/state.yml"  # the morning countersign
REQUEST_MARK = "```night-orders-request"
REQUEST_MARKS = (REQUEST_MARK, "```json")  # a flow note labelled json is read too; notes.py still checks the keys
# Agent privileges for the night watch flow: 2 read_only_gitlab, 3 read_write_gitlab. No files, commands,
# git or MCP tools (Flows API, "List all agent privileges"). They are still sent, but GitLab ignores them, and
# allow_agent_to_request_user, for a catalog flow (ee/lib/api/ai/duo_workflows/workflows.rb, read 2026-10-14):
# what limits a catalog flow is the toolset in its flows/*.yml.
WATCH_FLOW_PRIVILEGES = (2, 3)
# Fields of a Cloud Run v2 Service marked "Output only" in the discovery document. They are dropped before
# the service is sent back with its new traffic.
CLOUD_RUN_OUTPUT_ONLY = frozenset({
    "conditions", "createTime", "creator", "deleteTime", "expireTime", "generation", "lastModifier",
    "latestCreatedRevision", "latestReadyRevision", "observedGeneration", "reconciling", "satisfiesPzs",
    "terminalCondition", "threatDetectionEnabled", "trafficStatuses", "uid", "updateTime", "uri", "urls",
})


class RelayError(RuntimeError):
    """A call to the outside world failed. The message is safe to log and to page."""


class NotSent(RelayError):
    """The tick ran out of time before the call, so nothing went out and it is safe to make the call again."""

    sent = False


class Refused(RelayError):
    """The service answered with an HTTP 4xx, so the request did not take effect. status is that HTTP status."""

    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status


class ApplyFailed(RelayError):
    """A production change failed after the port read its target. before is that snapshot: the change may have
    gone through all the same, so the night records it and the morning can put the target back."""

    def __init__(self, message: str, before: dict):
        super().__init__(message)
        self.before = before


@contextmanager
def _keeps_before(before: dict, what: str) -> Iterator[None]:
    """Errors from a production write carry the snapshot read before it. A call never sent changed nothing."""
    try:
        yield
    except (NotSent, ApplyFailed):
        raise
    except RelayError as error:
        raise ApplyFailed(str(error), before) from None
    except (ValueError, TypeError, AttributeError, KeyError):  # an answer that is not the JSON expected
        raise ApplyFailed(f"{what}: unexpected answer", before) from None


def _detail(response: httpx.Response) -> str:
    """A short reason from an error body, if the body says one."""
    try:
        data = response.json()
    except ValueError:
        return ""
    if not isinstance(data, dict):
        return ""
    message: Any = data.get("message") or data.get("error")
    if isinstance(message, dict):
        message = message.get("message") or json.dumps(message, sort_keys=True)
    if not message:
        return ""
    return f" ({' '.join(str(message).split())[:160]})"


class Http:
    """Outbound calls: a 10 second timeout each, and an optional budget for the whole tick. sleep waits between
    the reads of a change that is still running."""

    def __init__(self, client: httpx.Client, budget_seconds: float | None = None,
                 clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
        self.client = client
        self.clock = clock
        self.sleep = sleep
        self.deadline = None if budget_seconds is None else clock() + budget_seconds

    def call(self, what: str, method: str, url: str, *, expect: tuple[int, ...] = (200,), detail: bool = True,
             **kwargs: Any) -> httpx.Response:
        timeout = TIMEOUT_SECONDS
        if self.deadline is not None:
            left = self.deadline - self.clock()
            if left <= 0:
                raise NotSent(f"{what}: skipped, the tick ran out of time")
            timeout = min(timeout, left)
        try:
            response = self.client.request(method, url, timeout=timeout, **kwargs)
        except httpx.TimeoutException:
            raise RelayError(f"{what}: no answer within {timeout:.0f} s") from None
        except httpx.HTTPError as error:
            raise RelayError(f"{what}: could not connect ({type(error).__name__})") from None
        if response.status_code not in expect:
            raise RelayError(f"{what}: HTTP {response.status_code}{_detail(response) if detail else ''}")
        return response


class GitLab:
    """The GitLab REST API v4 for one project. The token goes only in the PRIVATE-TOKEN header."""

    def __init__(self, http: Http, base_url: str, project_id: str, token: str):
        self.http = http
        self.api = base_url.rstrip("/") + "/api/v4"
        self.project_id = str(project_id)
        self.project = f"{self.api}/projects/{quote(self.project_id, safe='')}"
        self._token = token

    def __repr__(self) -> str:
        return f"GitLab({self.api!r}, project {self.project_id})"

    def call(self, what: str, method: str, path: str, *, in_project: bool = True, **kwargs: Any) -> httpx.Response:
        url = (self.project if in_project else self.api) + path
        headers = {**kwargs.pop("headers", {}), "PRIVATE-TOKEN": self._token}
        return self.http.call(f"GitLab {what}", method, url, headers=headers, **kwargs)

    def json(self, what: str, method: str, path: str, **kwargs: Any) -> Any:
        return self.call(what, method, path, **kwargs).json()

    def raw_file(self, path: str, ref: str) -> str | None:
        """A file's text at a branch or commit, or None if it is not there."""
        response = self.call(f"read {path}", "GET", f"/repository/files/{quote(path, safe='')}/raw",
                             params={"ref": ref}, expect=(200, 404))
        return None if response.status_code == 404 else response.text


class GoogleToken:
    """An access token for the relay's own service account, from the Cloud Run metadata server."""

    def __init__(self, http: Http):
        self.http = http
        self._token: str | None = None

    def __call__(self) -> str:
        if self._token is None:
            data = self.http.call("Google token", "GET", METADATA_TOKEN_URL,
                                  headers={"Metadata-Flavor": "Google"}).json()
            self._token = str(data["access_token"])
        return self._token


def push(http: Http, url: str, title: str, lines: tuple[str, ...] | list[str], *, click: str | None = None,
         priority: str = "urgent") -> None:
    """Send a push through ntfy. Urgent is ntfy's highest priority: long vibration bursts, to wake a person."""
    headers = {"Title": title, "Priority": priority, "Tags": "rotating_light" if priority == "urgent" else "ok"}
    if click:
        headers["Click"] = click
    http.call("push to the on-call phone", "POST", url, headers=headers, content="\n".join(lines).encode("utf-8"),
              detail=False)


TIMELINE_CHARS = 250


def timeline(text: str, at: datetime) -> str:
    """A /timeline quick action for an incident note, so the incident's timeline in GitLab shows the night.

    Only code-written text goes in it (the first sentence, on one line, with no "|", which the quick action
    reads as the separator before the time). The time is written in UTC. If GitLab does not run the quick
    action for this token, the line stays visible in the note and nothing else changes.
    """
    words = " ".join(str(text).split()).replace("|", "/")
    first = words.split(". ")[0].rstrip(".")[:TIMELINE_CHARS]
    return f"\n\n/timeline {first} | {at.astimezone(timezone.utc):%Y-%m-%d %H:%M}"


def parse_time(text: Any) -> datetime | None:
    """A GitLab timestamp such as 2026-10-21T10:13:05.120Z, as an aware datetime."""
    if not isinstance(text, str):
        return None
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    return moment if moment.tzinfo is not None else None


def mention_note(account: str, goal: str) -> str:
    """The note that starts a flow by its Mention trigger: the flow's service account, then the goal. The goal is
    code's text, but it is defused all the same: a line that starts with / would run as a quick action with the
    relay's token, and another @ mention could start another flow or notify a person."""
    lines = goal.replace("@", "(at)").splitlines()
    return f"@{account} " + "\n".join("'" + line.lstrip() if line.lstrip().startswith("/") else line for line in lines)


def _names_night(text: str | None, night: str) -> bool:
    """Whether a countersign file's text says night: "<night>" (quoted or not)."""
    try:
        data = yaml.safe_load(text or "")
    except yaml.YAMLError:
        return False
    return isinstance(data, dict) and str(data.get("night")) == night


def is_thumbs_up(name: Any) -> bool:
    """GitLab names the thumbs-up reaction thumbsup; skin-tone variants add a _tone suffix."""
    return isinstance(name, str) and (name == "thumbsup" or name.startswith("thumbsup_tone"))


def scope_covers(scope: str, environment: str) -> bool:
    """Whether a flag strategy's environment scope applies to an environment. * matches anything."""
    pattern = ".*".join(re.escape(part) for part in scope.split("*"))
    return re.fullmatch(pattern, environment) is not None


def _scopes(strategy: dict) -> list[dict]:
    return [s for s in strategy.get("scopes") or [] if isinstance(s, dict)]


def flag_reaches(flag: dict, environment: str) -> bool:
    """Whether any strategy of an active flag applies in this environment (Unleash then serves it)."""
    return bool(flag.get("active")) and any(
        scope_covers(str(scope.get("environment_scope", "")), environment)
        for strategy in flag.get("strategies") or [] for scope in _scopes(strategy))


def flag_on_for_all(flag: dict, environment: str) -> bool:
    """Whether the flag is on for every user in this environment: active, with a default strategy there."""
    return bool(flag.get("active")) and any(
        strategy.get("name") == "default"
        and any(scope_covers(str(scope.get("environment_scope", "")), environment) for scope in _scopes(strategy))
        for strategy in flag.get("strategies") or [])


def flag_changes(flag: dict, environment: str, to: str) -> dict | None:
    """The Feature Flags API update that sets one environment on or off, touching no other environment.

    Returns None when nothing needs to change. Raises RelayError when the change cannot be limited to
    that environment, for example when a * scope also covers it.
    """
    name = flag.get("name", "the flag")
    strategies = [s for s in flag.get("strategies") or [] if isinstance(s, dict)]
    if to == "off":
        if not flag_reaches(flag, environment):
            return None
        changes = _drop_environment(strategies, environment)
        for strategy in strategies:
            for scope in _scopes(strategy):
                wide = str(scope.get("environment_scope", ""))
                if wide != environment and scope_covers(wide, environment):
                    raise RelayError(f"flag {name}: its {wide} scope also covers {environment}, "
                                     f"so it cannot be turned off in {environment} alone")
        return {"strategies": changes}
    if flag_on_for_all(flag, environment):
        return None
    has_default = any(strategy.get("name") == "default"
                      and any(s.get("environment_scope") == environment for s in _scopes(strategy))
                      for strategy in strategies)
    update: dict = {} if has_default else {
        "strategies": [{"name": "default", "parameters": {}, "scopes": [{"environment_scope": environment}]}]}
    if not flag.get("active"):
        others = sorted({str(s.get("environment_scope")) for strategy in strategies for s in _scopes(strategy)
                         if s.get("environment_scope") != environment})
        if others:
            raise RelayError(f"flag {name} is inactive; turning it on would also turn it on for {', '.join(others)}")
        update["active"] = True
    return update


def _drop_environment(strategies: list[dict], environment: str) -> list[dict]:
    """Strategy changes that remove the environment's exact scopes: a whole strategy when that is all it has."""
    changes = []
    for strategy in strategies:
        scopes = _scopes(strategy)
        exact = [s for s in scopes if s.get("environment_scope") == environment]
        if not exact:
            continue
        if len(exact) == len(scopes):
            changes.append({"id": strategy["id"], "_destroy": True})
        else:
            changes.append({"id": strategy["id"], "scopes": [{"id": s["id"], "_destroy": True} for s in exact]})
    return changes


def _environment_strategies(flag: dict, environment: str) -> list[dict]:
    """The strategies that reach this environment, ids dropped, with only the scopes that cover it."""
    found = []
    for strategy in flag.get("strategies") or []:
        if not isinstance(strategy, dict):
            continue
        scopes = [{"environment_scope": str(s.get("environment_scope", ""))} for s in _scopes(strategy)
                  if scope_covers(str(s.get("environment_scope", "")), environment)]
        if scopes:
            record = {"name": strategy.get("name"), "parameters": dict(strategy.get("parameters") or {}),
                      "scopes": scopes}
            user_list = strategy.get("user_list")
            if isinstance(user_list, dict) and user_list.get("id") is not None:
                record["user_list_id"] = user_list["id"]  # a gitlabUserList strategy is nothing without it
            found.append(record)
    return found


def flag_snapshot(flag: dict, name: str, environment: str) -> dict:
    """The JSON-safe record of what a flag does in one environment, kept so the morning can put it back."""
    return {"kind": "flag", "flag": name, "environment": environment, "active": bool(flag.get("active")),
            "strategies": _environment_strategies(flag, environment)}


def served(strategies: list[dict]) -> set[str]:
    """What an environment is served by these strategies: each strategy's name, parameters and user list.

    Scopes are left out on purpose. After a restore, a strategy that covered the environment through a wider
    scope (* say) and its exact scope comes back as two records that serve the same thing, and that is fine.
    """
    return {json.dumps({"name": s.get("name"), "parameters": s.get("parameters") or {},
                        "user_list_id": s.get("user_list_id")}, sort_keys=True) for s in strategies}


def _same_strategies(first: list[dict], second: list[dict]) -> bool:
    return served(first) == served(second)


def same_flag_state(first: dict, second: dict) -> bool:
    return bool(first.get("active")) == bool(second.get("active")) and _same_strategies(
        first.get("strategies") or [], second.get("strategies") or [])


def flag_restore_changes(flag: dict, environment: str, before: dict) -> tuple[dict | None, dict]:
    """The Feature Flags API update that puts one environment back as the snapshot says, and the state
    expected afterwards.

    The environment's exact scopes are removed (as for "off") and the snapshot's strategies re-created with a
    scope for this environment only. A strategy that reached the environment through a wider scope (* say) was
    never touched at night, so it is left alone. A snapshot with no strategies means off in this environment.
    Returns (None, wanted) when the flag is already as the snapshot says.
    """
    strategies = [s for s in flag.get("strategies") or [] if isinstance(s, dict)]
    wanted_strategies = [dict(s) for s in before.get("strategies") or []]
    update: dict = {}
    if not _same_strategies(_environment_strategies(flag, environment), wanted_strategies):
        changes = _drop_environment(strategies, environment)
        for s in wanted_strategies:
            if not any(scope.get("environment_scope") == environment for scope in s.get("scopes") or []):
                continue
            created = {"name": s["name"], "parameters": dict(s.get("parameters") or {}),
                       "scopes": [{"environment_scope": environment}]}
            if s.get("user_list_id") is not None:
                created["user_list_id"] = s["user_list_id"]
            changes.append(created)
        if changes:
            update["strategies"] = changes
    active_now = bool(flag.get("active"))
    wanted_active = bool(before.get("active"))
    if not wanted_active and active_now:
        others = {str(s.get("environment_scope")) for strategy in strategies for s in _scopes(strategy)
                  if s.get("environment_scope") != environment}
        if others:
            wanted_active = True  # the flag serves other environments now, so it stays active
    if wanted_active != active_now:
        update["active"] = wanted_active
    wanted = {**before, "active": wanted_active, "strategies": wanted_strategies}
    return (update or None), wanted


REVISION_TARGET = "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION"


def _serving(traffic: list) -> list[dict]:
    """The traffic targets that get any traffic, as plain dicts."""
    return [dict(t) for t in traffic or [] if isinstance(t, dict) and t.get("percent")]


def traffic_all_on(traffic: list, revision: str) -> bool:
    """Whether every bit of traffic already goes to this revision."""
    serving = _serving(traffic)
    return (len(serving) == 1 and serving[0].get("type") == REVISION_TARGET
            and serving[0].get("revision") == revision and serving[0].get("percent") == 100)


def _allocation(traffic: list) -> list[str]:
    """Who gets the traffic, in a form a service's traffic and its trafficStatuses share. A target that sends traffic
    to the latest revision may be reported with that revision's name, so the name counts only for a revision target."""
    return sorted(json.dumps([t.get("type"), t.get("revision") if t.get("type") == REVISION_TARGET else None,
                              t.get("percent"), t.get("tag") or None]) for t in _serving(traffic))


def traffic_snapshot(service: str, current: dict) -> dict:
    return {"kind": "traffic", "service": service,
            "traffic": [dict(t) for t in current.get("traffic") or [] if isinstance(t, dict)]}


@dataclass
class PortMemory:
    """What the ports must remember between ticks. Each map is keyed by incident number."""

    asked: dict[int, datetime] = field(default_factory=dict)   # when the watch flow was asked
    page_notes: dict[int, int] = field(default_factory=dict)   # the note that holds the page
    links: dict[int, str] = field(default_factory=dict)        # the incident's web page
    unposted: dict[int, dict] = field(default_factory=dict)    # a page that went out without its note: at, lines

    def dump(self) -> dict:
        return {
            "asked": {str(k): v.isoformat() for k, v in self.asked.items()},
            "page_notes": {str(k): v for k, v in self.page_notes.items()},
            "links": {str(k): v for k, v in self.links.items()},
            "unposted": {str(k): v for k, v in self.unposted.items()},
        }

    @classmethod
    def load(cls, data: dict | None) -> "PortMemory":
        data = data or {}
        return cls(
            asked={int(k): datetime.fromisoformat(v) for k, v in (data.get("asked") or {}).items()},
            page_notes={int(k): int(v) for k, v in (data.get("page_notes") or {}).items()},
            links={int(k): str(v) for k, v in (data.get("links") or {}).items()},
            unposted={int(k): dict(v) for k, v in (data.get("unposted") or {}).items()},
        )


class GitLabPorts:
    """Ports for the Watch, against GitLab, Cloud Run and ntfy."""

    def __init__(self, gitlab: GitLab, http: Http, *, flow_consumer_id: str, flow_service_account: str,
                 ntfy_url: str, gcp_project: str = "", gcp_region: str = "",
                 google_token: Callable[[], str] | None = None, memory: dict | None = None,
                 dawn_consumer_id: str = "", watch_issue: int | None = None, errors_url: str = "",
                 flow_start: str = "api", dawn_flow_service_account: str = ""):
        self.gitlab = gitlab
        self.errors_url = errors_url
        self.flow_start = flow_start  # "api" (the Flows API) or "mention" (a note that mentions the flow's account)
        self.dawn_consumer_id = dawn_consumer_id
        self.dawn_flow_service_account = dawn_flow_service_account
        self.watch_issue = watch_issue
        self.http = http
        self.flow_consumer_id = flow_consumer_id
        self.flow_service_account = flow_service_account
        self._ntfy_url = ntfy_url
        self.gcp_project = gcp_project
        self.gcp_region = gcp_region
        self.google_token = google_token
        self.memory = PortMemory.load(memory)

    def __repr__(self) -> str:
        return f"GitLabPorts({self.gitlab!r})"

    def saved(self) -> dict:
        """The memory to keep until the next tick."""
        return self.memory.dump()

    # Incidents and notes.

    def open_incident(self, title: str, description: str, at: datetime) -> int:
        issue = self.gitlab.json("create incident", "POST", "/issues", expect=(200, 201),
                                 json={"title": title[:255], "description": description, "issue_type": "incident"})
        number = int(issue["iid"])
        if issue.get("web_url"):
            self.memory.links[number] = str(issue["web_url"])
        return number

    def _post_note(self, incident: int, body: str) -> dict:
        return self.gitlab.json("post note", "POST", f"/issues/{incident}/notes", expect=(200, 201),
                                json={"body": body})

    def note(self, incident: int, text: str, at: datetime) -> None:
        self._post_note(incident, text + timeline(text, at))

    def close_incident(self, incident: int, text: str, at: datetime) -> None:
        self._post_note(incident, text + timeline(text, at))
        self.gitlab.call("close incident", "PUT", f"/issues/{incident}", json={"state_event": "close"})

    # The watch flow: the model's only way in is one note that code reads.

    def _start_flow(self, what: str, consumer_id: str, account: str, goal: str, issue: int) -> None:
        """Start a flow on an issue: through the Flows API, or with FLOW_START mention by a note on the issue that
        mentions the flow's service account. Raises Refused on an HTTP 4xx (the flow did not start) and NotSent when
        the tick had no time left for the call; any other failure may have started the flow all the same."""
        if self.flow_start == "mention":
            path, in_project, body = f"/issues/{issue}/notes", True, {"body": mention_note(account, goal)}
        else:
            path, in_project, body = "/ai/duo_workflows/workflows", False, {
                "project_id": self.gitlab.project_id,
                "ai_catalog_item_consumer_id": int(consumer_id),
                "goal": goal,
                "issue_id": issue,
                "start_workflow": True,
                "allow_agent_to_request_user": False,
                "agent_privileges": list(WATCH_FLOW_PRIVILEGES),
                "pre_approved_agent_privileges": list(WATCH_FLOW_PRIVILEGES),
            }
        response = self.gitlab.call(what, "POST", path, in_project=in_project, expect=(200, 201, *range(400, 500)),
                                    json=body)
        if response.status_code >= 400:
            raise Refused(f"GitLab {what}: HTTP {response.status_code}{_detail(response)}", response.status_code)

    def start_watch_flow(self, incident: int, goal: str, at: datetime) -> None:
        # Recorded before the call: if the call times out after the flow started, its answer still counts.
        self.memory.asked[incident] = at
        try:
            self._start_flow("start the watch flow", self.flow_consumer_id, self.flow_service_account, goal, incident)
        except (NotSent, Refused):
            del self.memory.asked[incident]  # no flow started, so no answer can come
            raise

    def request_note(self, incident: int, at: datetime) -> str | None:
        asked = self.memory.asked.get(incident)
        if asked is None:
            return None
        notes = self.gitlab.json("read notes", "GET", f"/issues/{incident}/notes",
                                 params={"sort": "desc", "order_by": "created_at", "per_page": 100})
        answers = []
        for note in notes:
            author = str((note.get("author") or {}).get("username") or "")
            created = parse_time(note.get("created_at"))
            body = note.get("body") or ""
            if note.get("system") or author.lower() != self.flow_service_account.lower():
                continue
            if created is None or created < asked or not any(mark in body for mark in REQUEST_MARKS):
                continue
            answers.append((created, body))
        if not answers:
            return None
        return max(answers, key=lambda answer: answer[0])[1]

    def recent_log_lines(self, at: datetime) -> list[tuple[datetime, str]]:
        """The shop's recent warnings and errors from its /errors.json, (when, "SEVERITY message"), oldest first.
        Only time, severity and message are read; the watch fences and labels them as data."""
        if not self.errors_url:
            return []
        data = self.http.call("read the shop's error lines", "GET", self.errors_url).json()
        lines = []
        for item in (data.get("errors") or []) if isinstance(data, dict) else []:
            if not isinstance(item, dict):
                continue
            when = parse_time(item.get("time"))
            if when is not None:
                lines.append((when, f"{str(item.get('severity') or '')[:10]} {str(item.get('message') or '')}".strip()))
        return sorted(lines, key=lambda line: line[0])

    # The morning: the watch log and the dawn flow on the standing watch issue. Without one, both do nothing.

    def _project(self) -> dict:
        if getattr(self, "_project_json", None) is None:
            self._project_json = self.gitlab.json("read project", "GET", "")
        return self._project_json

    def quiet_push(self, title: str, lines: tuple[str, ...], at: datetime) -> None:
        """A push at ntfy's default priority (no alarm), opening the watch issue."""
        link = None
        web = str(self._project().get("web_url") or "")
        if self.watch_issue is not None and web.startswith("https://"):
            link = f"{web.rstrip('/')}/-/issues/{self.watch_issue}"
        push(self.http, self._ntfy_url, title, lines, click=link, priority="default")

    def morning_push(self, lines: tuple[str, ...], at: datetime) -> None:
        """One quiet push in the morning, opening the watch issue."""
        self.quiet_push("Night Orders: good morning", lines, at)

    # Kept changes (kept.py): is the target still as kept, and has the merge request that ends it shipped?

    def holds(self, action: Action) -> bool:
        """Whether the target is still as the action left it: the flag at that value, all traffic on that revision.

        The flag's state is read as it is, never through the change that would make it: a * scope or an inactive
        flag makes some changes impossible, but it is still a plain answer here."""
        if action.kind == "flag_set" and action.flag and action.environment and action.to:
            flag = self.gitlab.json(f"read flag {action.flag}", "GET", self._flag_path(action.flag))
            if action.to == "on":
                return flag_on_for_all(flag, action.environment)
            return not flag_reaches(flag, action.environment)
        if action.kind == "traffic_to_revision" and action.service and action.revision:
            _url, _headers, current = self._service(action.service)
            return traffic_all_on(current.get("traffic") or [], action.revision)
        raise RelayError(f"holds: {action.kind} is not on the menu")

    def as_before(self, action: Action, before: dict) -> bool:
        """Whether the target is already as the snapshot says, so a restore would change nothing. A snapshot that
        does not fit the action (restore refuses it) is never as before."""
        kind = (before or {}).get("kind")
        if (action.kind == "flag_set" and action.flag and action.environment and kind == "flag" and "active" in before
                and isinstance(before.get("strategies"), list)):
            flag = self.gitlab.json(f"read flag {action.flag}", "GET", self._flag_path(action.flag))
            return flag_restore_changes(flag, action.environment, before)[0] is None
        if action.kind == "traffic_to_revision" and action.service and kind == "traffic" and isinstance(
                before.get("traffic"), list):
            _url, _headers, current = self._service(action.service)
            return _serving(current.get("traffic") or []) == _serving(before["traffic"])
        return False

    def shipped(self, merge_request: int, environment: str) -> tuple[str, str]:
        """("shipped" | "waiting" | "closed", plain words): whether the merge request's commit is in the last
        successful deployment to the environment. Merged and deployed are facts GitLab states; nothing is guessed."""
        request = self.gitlab.json(f"read !{merge_request}", "GET", f"/merge_requests/{int(merge_request)}")
        state = str(request.get("state") or "")
        if state == "closed":
            return "closed", f"!{merge_request} was closed without merging"
        if state != "merged":
            return "waiting", f"!{merge_request} is not merged yet"
        commit = str(request.get("merge_commit_sha") or request.get("squash_commit_sha") or request.get("sha") or "")
        found = self.gitlab.json(f"list deployments to {environment}", "GET", "/deployments",
                                 params={"environment": environment, "status": "success", "order_by": "finished_at",
                                         "sort": "desc", "per_page": 1})
        if not commit or not found:
            return "waiting", f"!{merge_request} is merged, and nothing has been deployed to {environment} since"
        deployed = str(found[0].get("sha") or "")
        if deployed != commit:
            answer = self.gitlab.call("find the merge base", "GET", "/repository/merge_base",
                                      params={"refs[]": [commit, deployed]}, expect=(200, 400, 404))
            base = answer.json() if answer.status_code == 200 else None
            if not isinstance(base, dict) or base.get("id") != commit:  # the merge commit is not under the deploy
                return "waiting", (f"!{merge_request} is merged; the last deployment to {environment} "
                                   f"({deployed[:8]}) does not include it yet")
        return "shipped", shipped_words(merge_request, environment, found[0].get("iid") or found[0].get("id"),
                                        deployed)

    def dawn_flow_ready(self) -> bool:
        """Whether the dawn flow can be started: a watch issue, and the dawn flow's consumer ID, or its service account
        when it is started by a mention."""
        started_by = self.dawn_flow_service_account if self.flow_start == "mention" else self.dawn_consumer_id
        return self.watch_issue is not None and bool(started_by)

    def countersign_request_open(self, night: str) -> tuple[int | None, list[int]]:
        """The open countersign merge requests into the default branch, by anyone: (the newest whose ops/state.yml,
        read at its head, names this night, or None; every other one that changes ops/state.yml). Only the first
        can countersign this night: the morning refuses a file that names another night."""
        branch = str(self._project()["default_branch"])
        requests = self.gitlab.json("list open merge requests", "GET", "/merge_requests",
                                    params={"state": "opened", "target_branch": branch, "order_by": "created_at",
                                            "sort": "desc", "per_page": 10})
        found, others = None, []
        for request in requests[:10]:
            diffs = self.gitlab.json("read merge request changes", "GET", f"/merge_requests/{request['iid']}/diffs",
                                     params={"per_page": 100})
            if not any(STATE_FILE in (d.get("new_path"), d.get("old_path")) for d in diffs):
                continue
            head = request.get("sha")
            if found is None and head and _names_night(self.gitlab.raw_file(STATE_FILE, str(head)), night):
                found = int(request["iid"])
            else:
                others.append(int(request["iid"]))
        return found, others

    def open_countersign_request(self, night: str, state_text: str, title: str, description: str) -> int:
        """Branch, commit and merge request for a countersign written by code. The commit creates its own branch
        from the default branch; a name already taken gets -2, -3 and so on."""
        branch = str(self._project()["default_branch"])
        exists = self.gitlab.raw_file(STATE_FILE, branch) is not None
        action = {"action": "update" if exists else "create", "file_path": STATE_FILE, "content": state_text}
        for attempt in range(1, 6):
            name = f"countersign/{night}-code" + ("" if attempt == 1 else f"-{attempt}")
            answer = self.gitlab.call("commit the countersign file", "POST", "/repository/commits", expect=(201, 400),
                                      json={"branch": name, "start_branch": branch, "commit_message": title,
                                            "actions": [action]})
            if answer.status_code == 201:
                break
        else:
            raise RelayError("commit the countersign file: every branch name was taken")
        request = self.gitlab.json("open the countersign merge request", "POST", "/merge_requests", expect=(201,),
                                   json={"source_branch": name, "target_branch": branch, "title": title,
                                         "description": description, "remove_source_branch": True})
        return int(request["iid"])

    def watch_note(self, text: str, at: datetime) -> None:
        if self.watch_issue is not None:
            self._post_note(self.watch_issue, text)

    def start_dawn_flow(self, goal: str, at: datetime) -> None:
        """Raises NotSent when nothing went out (safe to start again) and Refused on an HTTP 4xx."""
        if self.watch_issue is not None and self.dawn_flow_ready():
            self._start_flow("start the dawn flow", self.dawn_consumer_id, self.dawn_flow_service_account, goal,
                             self.watch_issue)

    # Production changes. The action and its target come from the Watch, which takes them from the signed file.
    # Every change returns a snapshot of the target from before it, and restore puts that snapshot back.

    def apply(self, action: Action, at: datetime) -> Change:
        if action.kind == "flag_set" and action.flag and action.environment and action.to:
            return self._set_flag(action.flag, action.environment, action.to)
        if action.kind == "traffic_to_revision" and action.service and action.revision:
            return self._send_traffic(action.service, action.revision)
        raise RelayError(f"apply: {action.kind} is not on the menu")

    def snapshot(self, action: Action) -> dict:
        """What the action's target is right now, in the shape restore reads. The rehearsal takes it before
        the apply, so a change that fails halfway (GitLab answered 5xx after changing the flag) can still be
        put back from it."""
        if action.kind == "flag_set" and action.flag and action.environment:
            flag = self.gitlab.json(f"read flag {action.flag}", "GET", self._flag_path(action.flag))
            return flag_snapshot(flag, action.flag, action.environment)
        if action.kind == "traffic_to_revision" and action.service:
            _url, _headers, current = self._service(action.service)
            return traffic_snapshot(action.service, current)
        raise RelayError(f"snapshot: {action.kind} is not on the menu")

    def restore(self, action: Action, before: dict, at: datetime) -> Change:
        kind = (before or {}).get("kind")
        flag_shape = kind == "flag" and "active" in before and isinstance(before.get("strategies"), list)
        traffic_shape = kind == "traffic" and isinstance(before.get("traffic"), list)
        if action.kind == "flag_set" and flag_shape and action.flag and action.environment:
            return self._restore_flag(action.flag, action.environment, before)
        if action.kind == "traffic_to_revision" and traffic_shape and action.service:
            return self._restore_traffic(action.service, before)
        raise RelayError(f"restore: the snapshot ({kind}) does not fit {action.kind}")

    def _flag_path(self, name: str) -> str:
        return f"/feature_flags/{quote(name, safe='')}"

    def _set_flag(self, name: str, environment: str, to: str) -> Change:
        path = self._flag_path(name)
        flag = self.gitlab.json(f"read flag {name}", "GET", path)
        before = flag_snapshot(flag, name, environment)
        update = flag_changes(flag, environment, to)
        if update is None:
            return Change(changed=False, before=before, detail=f"already {to} in {environment}, nothing changed")
        with _keeps_before(before, f"GitLab set flag {name}"):
            after = self.gitlab.json(f"set flag {name}", "PUT", path, json=update)
            done = flag_on_for_all(after, environment) if to == "on" else not flag_reaches(after, environment)
            if not done:
                raise RelayError(f"flag {name}: GitLab did not report it {to} in {environment} after the change")
        return Change(changed=True, before=before, detail=f"{name} was {describe_before(before)} in {environment}")

    def _restore_flag(self, name: str, environment: str, before: dict) -> Change:
        path = self._flag_path(name)
        flag = self.gitlab.json(f"read flag {name}", "GET", path)
        now = flag_snapshot(flag, name, environment)
        update, wanted = flag_restore_changes(flag, environment, before)
        words = describe_before(wanted)
        if update is None:
            return Change(changed=False, before=now, detail=f"{name} already {words} in {environment}, nothing changed")
        after = self.gitlab.json(f"restore flag {name}", "PUT", path, json=update)
        if not same_flag_state(flag_snapshot(after, name, environment), wanted):
            raise RelayError(f"flag {name}: GitLab did not report it back as before in {environment} after the change")
        return Change(changed=True, before=now, detail=f"{name} is {words} in {environment} again")

    def _service(self, service: str) -> tuple[str, dict, dict]:
        """The Cloud Run service's URL, auth header and current description."""
        if not (self.gcp_project and self.gcp_region and self.google_token):
            raise RelayError("Cloud Run traffic: GCP_PROJECT_ID and GCP_REGION are not set")
        url = f"{CLOUD_RUN_API}/projects/{self.gcp_project}/locations/{self.gcp_region}/services/{service}"
        headers = {"Authorization": f"Bearer {self.google_token()}"}
        current = self.http.call(f"Cloud Run read {service}", "GET", url, headers=headers).json()
        return url, headers, current

    def revision_exists(self, service: str, revision: str) -> bool:
        """Whether a Cloud Run revision is there to receive traffic (the rehearsal checks traffic orders this way)."""
        if not (self.gcp_project and self.gcp_region and self.google_token):
            raise RelayError("Cloud Run revisions: GCP_PROJECT_ID and GCP_REGION are not set")
        url = (f"{CLOUD_RUN_API}/projects/{self.gcp_project}/locations/{self.gcp_region}/services/{service}"
               f"/revisions/{revision}")
        response = self.http.call(f"Cloud Run read revision {revision}", "GET", url,
                                  headers={"Authorization": f"Bearer {self.google_token()}"}, expect=(200, 404))
        return response.status_code == 200

    def _patch_traffic(self, service: str, url: str, headers: dict, current: dict, traffic: list[dict]) -> None:
        """Send the traffic, wait for Cloud Run's operation to finish and read the service back. The change is done
        only when the service is not reconciling, its terminal condition succeeded and its trafficStatuses are the
        traffic sent. A change still running when the time is up may land later, so that is an error too."""
        what = f"Cloud Run send {service} traffic"
        late = f"{what}: Cloud Run had not finished the change when the time ran out"
        # Send the whole service back with only the traffic changed, so nothing else can be reset even if the
        # update mask were ignored. The etag makes the update fail if someone changed the service meanwhile.
        body = {key: value for key, value in current.items() if key not in CLOUD_RUN_OUTPUT_ONLY}
        body["traffic"] = traffic
        operation = self.http.call(what, "PATCH", url, headers=headers, params={"updateMask": "traffic"},
                                   json=body).json()
        until = self.http.clock() + CLOUD_RUN_WAIT_SECONDS
        if self.http.deadline is not None:
            until = min(until, self.http.deadline)
        try:
            while not operation.get("done"):
                if self.http.clock() + CLOUD_RUN_POLL_SECONDS >= until:
                    raise RelayError(late)
                self.http.sleep(CLOUD_RUN_POLL_SECONDS)
                operation = self.http.call(f"{what}, read its progress", "GET", f"{CLOUD_RUN_API}/{operation['name']}",
                                           headers=headers).json()
            error = operation.get("error")
            if error:
                message = error.get("message", "failed") if isinstance(error, dict) else "failed"
                raise RelayError(f"{what}: {' '.join(str(message).split())[:160]}")
            after = self.http.call(f"Cloud Run read {service}", "GET", url, headers=headers).json()
        except NotSent:  # the change went out; only the wait for it had no time left
            raise RelayError(late) from None
        condition = after.get("terminalCondition") or {}
        if (after.get("reconciling") or condition.get("state") != "CONDITION_SUCCEEDED"
                or _allocation(after.get("trafficStatuses") or []) != _allocation(traffic)):
            raise RelayError(f"{what}: Cloud Run does not report the new traffic as serving")

    def _send_traffic(self, service: str, revision: str) -> Change:
        url, headers, current = self._service(service)
        before = traffic_snapshot(service, current)
        if traffic_all_on(before["traffic"], revision):
            return Change(changed=False, before=before,
                          detail=f"{service} traffic already all on revision {revision}, nothing changed")
        with _keeps_before(before, f"Cloud Run send {service} traffic"):
            self._patch_traffic(service, url, headers, current,
                                [{"type": REVISION_TARGET, "revision": revision, "percent": 100}])
        return Change(changed=True, before=before, detail=f"{service} traffic was {describe_before(before)}")

    def _restore_traffic(self, service: str, before: dict) -> Change:
        url, headers, current = self._service(service)
        now = traffic_snapshot(service, current)
        words = describe_before(before)
        if _serving(now["traffic"]) == _serving(before.get("traffic") or []):
            return Change(changed=False, before=now, detail=f"{service} traffic already {words}, nothing changed")
        with _keeps_before(now, f"Cloud Run send {service} traffic"):
            self._patch_traffic(service, url, headers, current, [dict(t) for t in before.get("traffic") or []])
        return Change(changed=True, before=now, detail=f"{service} traffic is {words} again")

    # Waking a person, and the one tap she can answer with.

    def _page_note(self, incident: int, lines: tuple[str, ...] | list[str], at: datetime, again: bool = False) -> None:
        """The page as a note on the incident, the thumbs-up target. It is posted inside a code block, so text the
        agent wrote cannot mention people or add links. Posted again, it is first looked for: a post that got no
        answer in time may have created the note all the same, and her thumbs-up is on that one."""
        shown = "\n".join(line.replace("`", "'") for line in lines)
        text = f"Page sent to the on-call person:\n\n```text\n{shown}\n```"
        try:
            note = self._find_note(incident, text) if again else None
            if note is None:
                note = self._post_note(incident, text + timeline("Paged the on-call person", at))
            self.memory.page_notes[incident] = int(note["id"])
        except (KeyError, TypeError, ValueError):
            raise RelayError("GitLab post note: unexpected answer") from None
        self.memory.unposted.pop(incident, None)

    def _find_note(self, incident: int, text: str) -> dict | None:
        """The incident's first note that starts with text (GitLab drops the quick action lines it ran), or None."""
        notes = self.gitlab.json("read notes", "GET", f"/issues/{incident}/notes",
                                 params={"sort": "asc", "order_by": "created_at", "per_page": 100})
        return next((note for note in notes if not note.get("system") and str(note.get("body") or "").startswith(text)),
                    None)

    def page(self, incident: int, lines: tuple[str, ...], at: datetime) -> None:
        """The push wakes her; the note is the thumbs-up target. A page tried again after its push failed posts its
        note once (an incident is paged once). A push that went out counts as sent even if the note failed: the note
        is then kept, and thumbs_up posts it on a later tick."""
        problems = []
        if incident not in self.memory.page_notes:
            try:
                self._page_note(incident, lines, at)
            except RelayError as error:
                self.memory.unposted[incident] = {"at": at.isoformat(), "lines": list(lines)}
                problems.append(str(error))
        link = self.memory.links.get(incident)
        if link and incident in self.memory.page_notes:
            link = f"{link}#note_{self.memory.page_notes[incident]}"
        try:
            push(self.http, self._ntfy_url, f"Night Orders: incident #{incident}", lines, click=link)
        except RelayError as error:
            raise RelayError("; ".join(problems + [str(error)])) from None

    def thumbs_up(self, incident: int, at: datetime) -> list[tuple[str, datetime]]:
        unposted = self.memory.unposted.get(incident)
        if unposted is not None and incident not in self.memory.page_notes:
            # The page went out but its note did not, so there is nothing to give the thumbs-up on yet: post it now.
            # A failure raises, so the tick says why the approval cannot work, and the next tick tries again.
            self._page_note(incident, unposted["lines"], datetime.fromisoformat(unposted["at"]), again=True)
        note = self.memory.page_notes.get(incident)
        if note is None:
            return []
        reactions = self.gitlab.json("read reactions", "GET", f"/issues/{incident}/notes/{note}/award_emoji",
                                     params={"per_page": 100})
        found = []
        for reaction in reactions:
            user = (reaction.get("user") or {}).get("username")
            when = parse_time(reaction.get("created_at"))
            if is_thumbs_up(reaction.get("name")) and user and when:
                found.append((when, str(user)))
        return [(user, when) for when, user in sorted(found)]
