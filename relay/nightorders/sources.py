"""Tonight's inputs, read fresh from GitLab and the shop on every tick.

  ops/oncall.yml, ops/targets.yml, ops/alerts.yml   from the default branch
  ops/night-orders.yml                                at the signed commit (below)
  the Signature                                       who merged or approved it, read from GitLab
  metrics                                             the shop's /metrics.json, one bucket per minute

The signature never comes from the orders file. Two routes can sign it:

  merge     The last commit on the default branch that changed ops/night-orders.yml belongs to a merge
            request into the default branch. If it was merged: merge_user and merged_at. If it is still open:
            its approvals. The orders are read at that commit.
  approval  An open merge request into the default branch that changes ops/night-orders.yml and has an
            approval. The hackathon subgroups let only Maintainers merge to the default branch, while
            Developers can approve (docs/SPONSORS.md, point 4), so this is the route Alex can use. The orders
            are read at the merge request's head commit. An approval counts only if it was given at or after
            the push of that commit: the merge request's versions say when each head commit was pushed. So a
            commit pushed after the approval is never signed by it, whether or not the project removes
            approvals on a push (a setting the relay cannot see).

When several signatures exist, the on-call person's newest one counts; if she signed none, the newest
one counts, so the reason she is woken names who signed. orders.signature_problems then checks the person
and the time. A file pushed straight to the default branch has no signature. When an approval given before
the commit it would sign outranks the signature that counts, and the orders are not signed tonight without it,
the reason goes in orders_problems, so the page and the status page say why.

Sources, read on 2026-10-06:
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/repository_files.md (raw file, ref)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/commits.md (path filter; merge requests of a commit)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_requests.md (merge_user, merged_at, diffs)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_request_approvals.md (approved_by, approved_at)
Read on 2026-10-14:
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_requests.md (diff versions, newest first:
  head_commit_sha, created_at)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import yaml

from .gitlab_ports import GitLab, Http, RelayError, parse_time
from .model import OnCall, Orders, Signature, Targets
from .morning import StateFile
from .orders import OrdersError, parse_oncall, parse_orders, parse_targets, signature_problems, watch_window
from .signals import Metrics
from .watch import AlertRule, parse_alert_rules

ORDERS_PATH = "ops/night-orders.yml"
STATE_PATH = "ops/state.yml"
OPEN_MERGE_REQUESTS_READ = 10  # the newest open merge requests the rehearsal and the signature look at


@dataclass(frozen=True)
class Inputs:
    oncall: OnCall
    targets: Targets
    rules: list[AlertRule]
    orders: Orders | None
    orders_problems: tuple[str, ...]
    signature: Signature | None
    metrics: Metrics
    project_url: str | None = None  # the GitLab project's web page, for the status page's links


def parse_metrics(data: Any) -> Metrics:
    """The shop's {"minutes": [{"at": ISO minute, "<metric key>": value, ...}]}. Bad buckets are skipped:
    missing data never counts as a breach."""
    if not isinstance(data, dict) or not isinstance(data.get("minutes"), list):
        raise RelayError("shop metrics: the answer has no list of minutes")
    metrics = Metrics()
    for bucket in data["minutes"]:
        if not isinstance(bucket, dict):
            continue
        try:
            at = datetime.fromisoformat(str(bucket.get("at")))
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        for key, value in bucket.items():
            if key == "at" or isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            if math.isfinite(value):
                metrics.put(str(key), at, value)
    return metrics


def parse_orders_text(text: str | None, targets: Targets, oncall: OnCall) -> tuple[Orders | None, tuple[str, ...]]:
    """Orders, or None with the reasons they cannot be used. A bad file never stops the relay: it wakes her."""
    if text is None:
        return None, ()
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None, (f"{ORDERS_PATH} is not valid YAML",)
    if not isinstance(data, dict):
        return None, (f"{ORDERS_PATH} is not a YAML mapping",)
    try:
        return parse_orders(data, targets, oncall), ()
    except OrdersError as error:
        return None, tuple(error.problems)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return None, (f"{ORDERS_PATH} could not be read ({type(error).__name__})",)


def signed_tonight(orders: Orders | None, signature: Signature | None, oncall: OnCall, now: datetime) -> bool:
    """Whether the orders were signed properly within their window, whether or not that window has ended yet."""
    if orders is None:
        return False
    _, end = watch_window(orders, oncall)
    return not signature_problems(orders, signature, oncall, min(now, end - timedelta(microseconds=1)))


class GitLabSources:
    def __init__(self, gitlab: GitLab, http: Http, metrics_url: str):
        self.gitlab = gitlab
        self.http = http
        self.metrics_url = metrics_url

    def load(self, now: datetime) -> Inputs:
        project = self.gitlab.json("read project", "GET", "")
        branch = str(project["default_branch"])
        oncall = self._config("ops/oncall.yml", branch, parse_oncall)
        targets = self._config("ops/targets.yml", branch, parse_targets)
        rules = self._config("ops/alerts.yml", branch, parse_alert_rules)
        signature, too_old = self.signed(branch, oncall.user)
        text = self.gitlab.raw_file(ORDERS_PATH, signature.commit if signature else branch)
        orders, problems = parse_orders_text(text, targets, oncall)
        if too_old and not signed_tonight(orders, signature, oncall, now):
            problems = (too_old,) + problems
        web = project.get("web_url")
        return Inputs(oncall=oncall, targets=targets, rules=rules, orders=orders, orders_problems=problems,
                      signature=signature, metrics=self.metrics(),
                      project_url=str(web) if isinstance(web, str) and web.startswith("https://") else None)

    def _config(self, path: str, ref: str, parse: Any) -> Any:
        """A file the relay cannot work without. Any problem stops the tick, and the relay's error path pages."""
        text = self.gitlab.raw_file(path, ref)
        if text is None:
            raise RelayError(f"{path} is missing on {ref}")
        try:
            return parse(yaml.safe_load(text) or {})
        except OrdersError as error:  # a value code refuses, said in plain words
            raise RelayError("; ".join(error.problems)) from None
        except (yaml.YAMLError, KeyError, TypeError, ValueError, AttributeError) as error:
            raise RelayError(f"{path} could not be read ({type(error).__name__})") from None

    def metrics(self) -> Metrics:
        response = self.http.call("read shop metrics", "GET", self.metrics_url)
        try:
            data = response.json()
        except ValueError:
            raise RelayError("shop metrics: the answer is not JSON") from None
        return parse_metrics(data)

    # The signature.

    def signature(self, branch: str, oncall_user: str, path: str = ORDERS_PATH) -> Signature | None:
        return self.signed(branch, oncall_user, path)[0]

    def signed(self, branch: str, oncall_user: str, path: str = ORDERS_PATH) -> tuple[Signature | None, str | None]:
        """The signature that counts, and why an approval that would outrank it does not count (None if none does)."""
        found = self._merged(branch, path) + self._approved(branch, path)

        def rank(item: tuple[Signature, str | None]) -> tuple[bool, datetime]:
            return item[0].user == oncall_user, item[0].at

        counted = max((item for item in found if item[1] is None), key=rank, default=None)
        top = max(found, key=rank, default=None)
        return (counted[0] if counted else None), (top[1] if top else None)

    def state_file(self, oncall_user: str) -> StateFile:
        """The morning countersign: ops/state.yml as signed, read at the signed commit, and who signed it."""
        branch = str(self.gitlab.json("read project", "GET", "")["default_branch"])
        signature = self.signature(branch, oncall_user, STATE_PATH)
        text = self.gitlab.raw_file(STATE_PATH, signature.commit if signature else branch)
        try:
            data = yaml.safe_load(text) if text else None
        except yaml.YAMLError:
            return StateFile(None, signature, f"{STATE_PATH} is not valid YAML")
        if data is not None and not isinstance(data, dict):
            return StateFile(None, signature, f"{STATE_PATH} is not a YAML mapping")
        return StateFile(data, signature)

    def _merged(self, branch: str, path: str = ORDERS_PATH) -> list[tuple[Signature, str | None]]:
        commits = self.gitlab.json(f"find the last change to {path}", "GET", "/repository/commits",
                                   params={"ref_name": branch, "path": path, "per_page": 1})
        if not commits:
            return []
        sha = str(commits[0]["id"])
        requests = self.gitlab.json(f"find the merge request for {path}", "GET",
                                    f"/repository/commits/{sha}/merge_requests")
        for request in requests:
            if request.get("target_branch") != branch:
                continue
            detail = self.gitlab.json(f"read the merge request for {path}", "GET",
                                      f"/merge_requests/{request['iid']}")
            if detail.get("state") == "merged":
                user = (detail.get("merge_user") or detail.get("merged_by") or {}).get("username")
                at = parse_time(detail.get("merged_at"))
                return ([(Signature(method="merge", user=str(user), at=at, commit=sha,
                                    merge_request=int(detail["iid"])), None)] if user and at else [])
            if detail.get("state") == "opened":
                return self._approvals(int(detail["iid"]), sha)
            return []
        return []

    def _approved(self, branch: str, path: str = ORDERS_PATH) -> list[tuple[Signature, str | None]]:
        requests = self.gitlab.json("list open merge requests", "GET", "/merge_requests",
                                    params={"state": "opened", "target_branch": branch, "order_by": "created_at",
                                            "sort": "desc", "per_page": OPEN_MERGE_REQUESTS_READ})
        found: list[tuple[Signature, str | None]] = []
        for request in requests[:OPEN_MERGE_REQUESTS_READ]:
            iid = int(request["iid"])
            diffs = self.gitlab.json("read merge request changes", "GET", f"/merge_requests/{iid}/diffs",
                                     params={"per_page": 100})
            if any(path in (d.get("new_path"), d.get("old_path")) for d in diffs):
                found.extend(self._approvals(iid, str(request["sha"])))
        return found

    def _approvals(self, iid: int, commit: str) -> list[tuple[Signature, str | None]]:
        """Each approval as a signature of commit, with why it does not count, or None when it does: it counts only
        if it was given at or after the push of commit (the newest version whose head it is)."""
        state = self.gitlab.json("read approvals", "GET", f"/merge_requests/{iid}/approvals")
        approvals = []
        for approval in state.get("approved_by") or []:
            user = (approval.get("user") or {}).get("username")
            at = parse_time(approval.get("approved_at"))
            if user and at:
                approvals.append(Signature(method="approval", user=str(user), at=at, commit=commit, merge_request=iid))
        if not approvals:
            return []
        versions = self.gitlab.json("read merge request versions", "GET", f"/merge_requests/{iid}/versions")
        pushed = next((parse_time(v.get("created_at")) for v in versions
                       if isinstance(v, dict) and v.get("head_commit_sha") == commit), None)
        if pushed is None:
            why = (f"!{iid} has no version at commit {commit[:8]}, so code cannot tell if it was approved after "
                   "that commit")
            return [(approval, why) for approval in approvals]
        why = f"!{iid} was approved before commit {commit[:8]} was pushed to it, so approve it again"
        return [(approval, None if approval.at >= pushed else why) for approval in approvals]
