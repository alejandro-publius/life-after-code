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
            are read at the merge request's head commit, the version that was approved. This relies on
            GitLab's default of removing approvals when commits are added to the source branch.

When several signatures exist, the on-call person's newest one counts; if she signed none, the newest
one counts, so the reason she is woken names who signed. orders.signature_problems then checks the person
and the time. A file pushed straight to the default branch has no signature.

Sources, read on 2026-10-06:
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/repository_files.md (raw file, ref)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/commits.md (path filter; merge requests of a commit)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_requests.md (merge_user, merged_at, diffs)
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_request_approvals.md (approved_by, approved_at)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import yaml

from .gitlab_ports import GitLab, Http, RelayError, parse_time
from .model import OnCall, Orders, Signature, Targets
from .morning import StateFile
from .orders import OrdersError, parse_oncall, parse_orders, parse_targets
from .signals import Metrics
from .watch import AlertRule, parse_alert_rules

ORDERS_PATH = "ops/night-orders.yml"
STATE_PATH = "ops/state.yml"
OPEN_MERGE_REQUESTS_READ = 5


@dataclass(frozen=True)
class Inputs:
    oncall: OnCall
    targets: Targets
    rules: list[AlertRule]
    orders: Orders | None
    orders_problems: tuple[str, ...]
    signature: Signature | None
    metrics: Metrics


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


class GitLabSources:
    def __init__(self, gitlab: GitLab, http: Http, metrics_url: str):
        self.gitlab = gitlab
        self.http = http
        self.metrics_url = metrics_url

    def load(self, now: datetime) -> Inputs:
        branch = str(self.gitlab.json("read project", "GET", "")["default_branch"])
        oncall = self._config("ops/oncall.yml", branch, parse_oncall)
        targets = self._config("ops/targets.yml", branch, parse_targets)
        rules = self._config("ops/alerts.yml", branch, parse_alert_rules)
        signature = self.signature(branch, oncall.user)
        text = self.gitlab.raw_file(ORDERS_PATH, signature.commit if signature else branch)
        orders, problems = parse_orders_text(text, targets, oncall)
        return Inputs(oncall=oncall, targets=targets, rules=rules, orders=orders, orders_problems=problems,
                      signature=signature, metrics=self.metrics())

    def _config(self, path: str, ref: str, parse: Any) -> Any:
        """A file the relay cannot work without. Any problem stops the tick, and the relay's error path pages."""
        text = self.gitlab.raw_file(path, ref)
        if text is None:
            raise RelayError(f"{path} is missing on {ref}")
        try:
            return parse(yaml.safe_load(text) or {})
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
        found = self._merged(branch, path) + self._approved(branch, path)
        if not found:
            return None
        return max(found, key=lambda s: (s.user == oncall_user, s.at))

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

    def _merged(self, branch: str, path: str = ORDERS_PATH) -> list[Signature]:
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
                return [Signature(method="merge", user=str(user), at=at, commit=sha)] if user and at else []
            if detail.get("state") == "opened":
                return self._approvals(int(detail["iid"]), sha)
            return []
        return []

    def _approved(self, branch: str, path: str = ORDERS_PATH) -> list[Signature]:
        requests = self.gitlab.json("list open merge requests", "GET", "/merge_requests",
                                    params={"state": "opened", "target_branch": branch, "order_by": "created_at",
                                            "sort": "desc", "per_page": OPEN_MERGE_REQUESTS_READ})
        found: list[Signature] = []
        for request in requests[:OPEN_MERGE_REQUESTS_READ]:
            iid = int(request["iid"])
            diffs = self.gitlab.json("read merge request changes", "GET", f"/merge_requests/{iid}/diffs",
                                     params={"per_page": 100})
            if any(path in (d.get("new_path"), d.get("old_path")) for d in diffs):
                found.extend(self._approvals(iid, str(request["sha"])))
        return found

    def _approvals(self, iid: int, commit: str) -> list[Signature]:
        state = self.gitlab.json("read approvals", "GET", f"/merge_requests/{iid}/approvals")
        approvals = []
        for approval in state.get("approved_by") or []:
            user = (approval.get("user") or {}).get("username")
            at = parse_time(approval.get("approved_at"))
            if user and at:
                approvals.append(Signature(method="approval", user=str(user), at=at, commit=commit))
        return approvals
