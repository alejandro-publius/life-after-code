"""The relay's ports to the outside world: GitLab, Cloud Run and a push service.

GitLabPorts implements nightorders.watch.Ports against real services. It decides nothing: it does what
the Watch asks and reports what it finds. Every request has a 10 second timeout, a tick can also have an
overall time budget, and every failure is a RelayError whose message is safe to log and to page: it never
holds a URL, a token or the push topic.

  open_incident     POST /projects/:id/issues with issue_type incident; the evidence pack is the description
  note              POST /projects/:id/issues/:iid/notes
  start_watch_flow  POST /ai/duo_workflows/workflows (Flows API) with the incident as issue_id
  request_note      the newest note by the watch flow's service account, written after the ask, that holds
                    a night-orders-request block
  apply             flag_set: the Feature Flags API, changing only the named environment's scopes;
                    traffic_to_revision: the Cloud Run Admin API v2, 100% of traffic to the named revision
  page              a push to an ntfy topic, and the page as a note on the incident (the thumbs-up target)
  thumbs_up         every thumbsup reaction on that page note, oldest first; decide.approve_suggestion checks
                    who and when, so a teammate's reaction cannot block the on-call person's
  close_incident    a closing note, then state_event close
  watch_note        a note on the standing watch issue (the watch log, the countersign result)
  start_dawn_flow   POST /ai/duo_workflows/workflows for the dawn flow, on the watch issue

Sources, read on 2026-10-06 (GitLab docs from their source files, since docs.gitlab.com is blocked here):
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/issues.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/notes.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/emoji_reactions.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/feature_flags.md
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/feature_flags.rb (strategies, scopes: id, _destroy)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/concerns/has_environment_scope.rb (* is a wildcard)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/models/award_emoji.rb (thumbs-up is named thumbsup)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md
  https://run.googleapis.com/$discovery/rest?version=v2 (services.patch, updateMask, TrafficTarget)
  https://github.com/binwiederhier/ntfy/blob/main/docs/publish.md (Title, Priority, Tags and Click headers)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from urllib.parse import quote

import httpx

from .model import Action

TIMEOUT_SECONDS = 10.0
METADATA_TOKEN_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
CLOUD_RUN_API = "https://run.googleapis.com/v2"
REQUEST_MARK = "```night-orders-request"
# Agent privileges for the night watch flow: 2 read_only_gitlab, 3 read_write_gitlab. No files, commands,
# git or MCP tools (Flows API, "List all agent privileges").
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
    """Outbound calls: a 10 second timeout each, and an optional budget for the whole tick."""

    def __init__(self, client: httpx.Client, budget_seconds: float | None = None,
                 clock: Callable[[], float] = time.monotonic):
        self.client = client
        self.clock = clock
        self.deadline = None if budget_seconds is None else clock() + budget_seconds

    def call(self, what: str, method: str, url: str, *, expect: tuple[int, ...] = (200,), detail: bool = True,
             **kwargs: Any) -> httpx.Response:
        timeout = TIMEOUT_SECONDS
        if self.deadline is not None:
            left = self.deadline - self.clock()
            if left <= 0:
                raise RelayError(f"{what}: skipped, the tick ran out of time")
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


def parse_time(text: Any) -> datetime | None:
    """A GitLab timestamp such as 2026-10-21T10:13:05.120Z, as an aware datetime."""
    if not isinstance(text, str):
        return None
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    return moment if moment.tzinfo is not None else None


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


@dataclass
class PortMemory:
    """What the ports must remember between ticks. Each map is keyed by incident number."""

    asked: dict[int, datetime] = field(default_factory=dict)   # when the watch flow was asked
    page_notes: dict[int, int] = field(default_factory=dict)   # the note that holds the page
    links: dict[int, str] = field(default_factory=dict)        # the incident's web page

    def dump(self) -> dict:
        return {
            "asked": {str(k): v.isoformat() for k, v in self.asked.items()},
            "page_notes": {str(k): v for k, v in self.page_notes.items()},
            "links": {str(k): v for k, v in self.links.items()},
        }

    @classmethod
    def load(cls, data: dict | None) -> "PortMemory":
        data = data or {}
        return cls(
            asked={int(k): datetime.fromisoformat(v) for k, v in (data.get("asked") or {}).items()},
            page_notes={int(k): int(v) for k, v in (data.get("page_notes") or {}).items()},
            links={int(k): str(v) for k, v in (data.get("links") or {}).items()},
        )


class GitLabPorts:
    """Ports for the Watch, against GitLab, Cloud Run and ntfy."""

    def __init__(self, gitlab: GitLab, http: Http, *, flow_consumer_id: str, flow_service_account: str,
                 ntfy_url: str, gcp_project: str = "", gcp_region: str = "",
                 google_token: Callable[[], str] | None = None, memory: dict | None = None,
                 dawn_consumer_id: str = "", watch_issue: int | None = None):
        self.gitlab = gitlab
        self.dawn_consumer_id = dawn_consumer_id
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
        self._post_note(incident, text)

    def close_incident(self, incident: int, text: str, at: datetime) -> None:
        self._post_note(incident, text)
        self.gitlab.call("close incident", "PUT", f"/issues/{incident}", json={"state_event": "close"})

    # The watch flow: the model's only way in is one note that code reads.

    def start_watch_flow(self, incident: int, goal: str, at: datetime) -> None:
        # Recorded before the call: if the call times out after the flow started, its answer still counts.
        self.memory.asked[incident] = at
        body = {
            "project_id": self.gitlab.project_id,
            "ai_catalog_item_consumer_id": int(self.flow_consumer_id),
            "goal": goal,
            "issue_id": incident,
            "start_workflow": True,
            "allow_agent_to_request_user": False,
            "agent_privileges": list(WATCH_FLOW_PRIVILEGES),
            "pre_approved_agent_privileges": list(WATCH_FLOW_PRIVILEGES),
        }
        self.gitlab.call("start the watch flow", "POST", "/ai/duo_workflows/workflows", in_project=False,
                         expect=(200, 201), json=body)

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
            if created is None or created < asked or REQUEST_MARK not in body:
                continue
            answers.append((created, body))
        if not answers:
            return None
        return max(answers, key=lambda answer: answer[0])[1]

    # The morning: the watch log and the dawn flow on the standing watch issue. Without one, both do nothing.

    def watch_note(self, text: str, at: datetime) -> None:
        if self.watch_issue is not None:
            self._post_note(self.watch_issue, text)

    def start_dawn_flow(self, goal: str, at: datetime) -> None:
        if self.watch_issue is None or not self.dawn_consumer_id:
            return
        body = {
            "project_id": self.gitlab.project_id,
            "ai_catalog_item_consumer_id": int(self.dawn_consumer_id),
            "goal": goal,
            "issue_id": self.watch_issue,
            "start_workflow": True,
            "allow_agent_to_request_user": False,
            "agent_privileges": list(WATCH_FLOW_PRIVILEGES),
            "pre_approved_agent_privileges": list(WATCH_FLOW_PRIVILEGES),
        }
        self.gitlab.call("start the dawn flow", "POST", "/ai/duo_workflows/workflows", in_project=False,
                         expect=(200, 201), json=body)

    # Production changes. The action and its target come from the Watch, which takes them from the signed file.

    def apply(self, action: Action, at: datetime) -> None:
        if action.kind == "flag_set" and action.flag and action.environment and action.to:
            self._set_flag(action.flag, action.environment, action.to)
        elif action.kind == "traffic_to_revision" and action.service and action.revision:
            self._send_traffic(action.service, action.revision)
        else:
            raise RelayError(f"apply: {action.kind} is not on the menu")

    def _set_flag(self, name: str, environment: str, to: str) -> None:
        path = f"/feature_flags/{quote(name, safe='')}"
        flag = self.gitlab.json(f"read flag {name}", "GET", path)
        update = flag_changes(flag, environment, to)
        if update is None:
            return
        after = self.gitlab.json(f"set flag {name}", "PUT", path, json=update)
        done = flag_on_for_all(after, environment) if to == "on" else not flag_reaches(after, environment)
        if not done:
            raise RelayError(f"flag {name}: GitLab did not report it {to} in {environment} after the change")

    def _send_traffic(self, service: str, revision: str) -> None:
        if not (self.gcp_project and self.gcp_region and self.google_token):
            raise RelayError("Cloud Run traffic: GCP_PROJECT_ID and GCP_REGION are not set")
        url = f"{CLOUD_RUN_API}/projects/{self.gcp_project}/locations/{self.gcp_region}/services/{service}"
        headers = {"Authorization": f"Bearer {self.google_token()}"}
        current = self.http.call(f"Cloud Run read {service}", "GET", url, headers=headers).json()
        # Send the whole service back with only the traffic changed, so nothing else can be reset even if the
        # update mask were ignored. The etag makes the update fail if someone changed the service meanwhile.
        body = {key: value for key, value in current.items() if key not in CLOUD_RUN_OUTPUT_ONLY}
        body["traffic"] = [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": revision, "percent": 100}]
        operation = self.http.call(f"Cloud Run send {service} traffic", "PATCH", url, headers=headers,
                                   params={"updateMask": "traffic"}, json=body).json()
        error = operation.get("error") if isinstance(operation, dict) else None
        if error:
            message = error.get("message", "failed") if isinstance(error, dict) else "failed"
            raise RelayError(f"Cloud Run send {service} traffic: {' '.join(str(message).split())[:160]}")

    # Waking a person, and the one tap she can answer with.

    def page(self, incident: int, lines: tuple[str, ...], at: datetime) -> None:
        problems = []
        # The note is posted inside a code block, so text the agent wrote cannot mention people or add links.
        shown = "\n".join(line.replace("`", "'") for line in lines)
        try:
            note = self._post_note(incident, f"Page sent to the on-call person:\n\n```text\n{shown}\n```")
            self.memory.page_notes[incident] = int(note["id"])
        except (RelayError, KeyError, TypeError, ValueError) as error:
            problems.append(str(error) if isinstance(error, RelayError) else "GitLab post note: unexpected answer")
        link = self.memory.links.get(incident)
        if link and incident in self.memory.page_notes:
            link = f"{link}#note_{self.memory.page_notes[incident]}"
        try:
            push(self.http, self._ntfy_url, f"Night Orders: incident #{incident}", lines, click=link)
        except RelayError as error:
            problems.append(str(error))
        if problems:
            raise RelayError("; ".join(problems))

    def thumbs_up(self, incident: int, at: datetime) -> list[tuple[str, datetime]]:
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
