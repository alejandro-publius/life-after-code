"""The rehearsal: before the on-call person signs, each drafted order is tried on staging and put back.

When the dusk flow opens the orders merge request, the relay finds it on its next tick, reads the orders
at the merge request's head commit, and for each order:

  flag_set              applies the same change to the flag's staging scope, checks the staging shop still
                        answers (/healthz, and one demo checkout), then restores the flag from its snapshot
  traffic_to_revision   checks that the named revision exists on the service (there is no staging twin of a
                        production revision, so nothing is moved)

Then it posts one note on the merge request, written by code: what was applied, what the staging shop said,
what was restored. A draft that code refuses (parse_orders) gets a note saying why instead. Each merge
request head is rehearsed once; a failed try is counted and tried again next tick, a few times at most.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
import yaml

from .gitlab_ports import GitLab, Http, RelayError
from .model import Action, Change, OnCall, Signature, Targets
from .orders import OrdersError, parse_orders, signature_problems, watch_window
from .sources import ORDERS_PATH, OPEN_MERGE_REQUESTS_READ

MAX_TRIES_PER_HEAD = 3
CHECKOUT = {"user": "pilot-01", "region": "us", "items": [{"sku": "juniper-tea", "price": 8.0, "qty": 1}]}


def open_orders_requests(gitlab: GitLab, branch: str) -> list[tuple[int, str]]:
    """(iid, head sha) of every open merge request into the default branch that changes the orders file."""
    requests = gitlab.json("list open merge requests", "GET", "/merge_requests",
                           params={"state": "opened", "target_branch": branch, "order_by": "created_at",
                                   "sort": "desc", "per_page": OPEN_MERGE_REQUESTS_READ})
    found = []
    for request in requests[:OPEN_MERGE_REQUESTS_READ]:
        iid = int(request["iid"])
        diffs = gitlab.json("read merge request changes", "GET", f"/merge_requests/{iid}/diffs",
                            params={"per_page": 100})
        if any(ORDERS_PATH in (d.get("new_path"), d.get("old_path")) for d in diffs):
            found.append((iid, str(request["sha"])))
    return found


def staging_twin(action: Action, targets: Targets) -> Action | None:
    """The same flag change in staging, or None when the flag has no staging scope."""
    if action.kind != "flag_set" or "staging" not in targets.flags.get(action.flag or "", ()):
        return None
    return Action(kind="flag_set", flag=action.flag, environment="staging", to=action.to)


def check_shop(http: Http, base_url: str) -> str:
    """One line on whether the staging shop still serves a checkout. Never raises."""
    try:
        health = http.call("staging shop health", "GET", base_url.rstrip("/") + "/healthz").json()
        if not health.get("ok"):
            return "staging shop /healthz did not answer ok"
        checkout = http.call("staging shop checkout", "POST", base_url.rstrip("/") + "/checkout", json=CHECKOUT,
                             expect=(200, 500, 502, 504))
        if checkout.status_code == 200:
            return f"staging shop healthy, checkout ok on the {checkout.json().get('path', '?')} path"
        return f"staging shop healthy, but a checkout failed with HTTP {checkout.status_code}"
    except RelayError as error:
        return f"staging shop not checked ({error})"


def rehearse_order(order, ports: Any, targets: Targets, http: Http, staging_url: str) -> str:
    action = order.do
    if action.kind == "traffic_to_revision":
        exists = ports.revision_exists(action.service, action.revision)
        return (f"order {order.id}: revision {action.revision} exists on {action.service}" if exists
                else f"order {order.id}: revision {action.revision} is NOT on {action.service}, this order cannot run")
    twin = staging_twin(action, targets)
    if twin is None:
        return f"order {order.id}: {action.describe()} has no staging scope to rehearse on"
    change = ports.apply(twin, None)
    if not isinstance(change, Change) or not change.changed:
        return f"order {order.id}: {twin.describe()} was already so on staging, nothing to rehearse"
    shop = check_shop(http, staging_url) if staging_url else "no staging shop URL set, not checked"
    restored = ports.restore(twin, change.before, None)
    back = "restored" if isinstance(restored, Change) else "restore attempted"
    return f"order {order.id}: {twin.describe()} applied, {shop}, {back}"


def rehearse(gitlab: GitLab, ports: Any, http: Http, oncall: OnCall, targets: Targets, staging_url: str,
             iid: int, sha: str, now: datetime) -> str:
    """Rehearse one merge request head and return the note text posted on it."""
    text = gitlab.raw_file(ORDERS_PATH, sha)
    when = oncall.hhmm(now)
    lines = [f"Rehearsal on staging at {when}, written by code for commit {sha[:8]}.", ""]
    try:
        data = yaml.safe_load(text or "") or {}
        orders = parse_orders(data, targets, oncall)
    except (OrdersError, yaml.YAMLError, KeyError, TypeError, ValueError, AttributeError) as error:
        problems = error.problems if isinstance(error, OrdersError) else [f"the file could not be read ({type(error).__name__})"]
        lines.append("Code refuses this draft, so it cannot be signed:")
        lines += [f"- {p}" for p in problems]
        return "\n".join(lines) + "\n"
    would_sign = Signature(method="merge", user=oncall.user, at=now, commit=sha)
    problems = signature_problems(orders, would_sign, oncall, now)
    if problems:
        start, end = watch_window(orders, oncall)
        lines.append(f"Code refuses this draft, so it cannot be signed now: its night is {orders.night.isoformat()}, "
                     f"and a signature at {when} on {oncall.local(now):%d %b} would fall outside its window "
                     f"({oncall.hhmm(start)} on {oncall.local(start):%d %b} to {oncall.hhmm(end)} on "
                     f"{oncall.local(end):%d %b}). Set night to tonight's local date.")
        lines += [f"- {p}" for p in problems]
        return "\n".join(lines) + "\n"
    if not orders.orders:
        lines.append("No orders in this draft: nothing to rehearse. Merging it signs nothing, so every alert wakes you.")
        return "\n".join(lines) + "\n"
    for order in orders.orders:
        try:
            lines.append("- " + rehearse_order(order, ports, targets, http, staging_url))
        except RelayError as error:
            lines.append(f"- order {order.id}: rehearsal stopped ({error})")
    lines += ["", f"{len(orders.orders)} order(s) checked. Merge to sign; the orders end at {orders.expires:%H:%M}."]
    return "\n".join(lines) + "\n"


def step(relay_doc: dict, now: datetime, oncall: OnCall, targets: Targets, gitlab: GitLab, ports: Any,
         http: Http, staging_url: str) -> list[str]:
    """Called by the relay's tick, outside the watch's failure accounting: rehearse new orders merge requests."""
    branch = str(gitlab.json("read project", "GET", "")["default_branch"])
    done_heads: dict = relay_doc.setdefault("rehearsed", {})
    tries: dict = relay_doc.setdefault("rehearsal_tries", {})
    reported = []
    heads = open_orders_requests(gitlab, branch)
    for sha in [s for s in tries if s not in {h for _, h in heads}]:
        del tries[sha]  # a head that is gone (pushed over, merged or closed) needs no counter
    for iid, sha in heads:
        if done_heads.get(str(iid)) == sha or tries.get(sha, 0) >= MAX_TRIES_PER_HEAD:
            continue
        tries[sha] = tries.get(sha, 0) + 1
        note = rehearse(gitlab, ports, http, oncall, targets, staging_url, iid, sha, now)
        gitlab.json("post the rehearsal note", "POST", f"/merge_requests/{iid}/notes", expect=(200, 201),
                    json={"body": note})
        done_heads[str(iid)] = sha
        tries.pop(sha, None)
        reported.append(f"rehearsed !{iid} at {sha[:8]}")
    return reported
