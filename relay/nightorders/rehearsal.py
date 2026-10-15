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

import time
from datetime import datetime
from typing import Any, Callable

import yaml

from .dawn import action_from
from .gitlab_ports import GitLab, Http, RelayError
from .model import Action, Change, OnCall, Signature, Targets, describe_before
from .orders import OrdersError, parse_orders, signature_problems, watch_window
from .sources import ORDERS_PATH, OPEN_MERGE_REQUESTS_READ

MAX_TRIES_PER_HEAD = 3
MAX_RESTORE_TRIES = 10        # a staging restore that keeps failing is left for a person, and said so
SHOP_FETCH_WAIT_SECONDS = 25  # the staging shop refreshes its flags at most every 15 s
SHOP_POLL_EVERY = 2.0
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


def shop_mark(http: Http, base_url: str) -> str | None:
    """When the staging shop last fetched its flags (a string to compare, "" for never), or None when the shop
    has no /flags route. Read before the apply, so the check can wait for the fetch that follows it."""
    try:
        answer = http.call("staging shop flags", "GET", base_url.rstrip("/") + "/flags", expect=(200, 404))
    except RelayError:
        return None
    if answer.status_code != 200:
        return None
    return str(answer.json().get("fetched_at") or "")


def check_shop(http: Http, base_url: str, mark: str | None = None,
               sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic) -> str:
    """One line on whether the staging shop still serves a checkout under the applied change. Never raises.

    The shop caches its flags for 15 seconds and refreshes them in the background when asked, so the check
    first polls /flags until the fetch time moves past the mark taken before the apply (at most 25 s), and
    only then sends a checkout. Without that wait the checkout would run under the earlier flags.
    """
    base = base_url.rstrip("/")
    try:
        health = http.call("staging shop health", "GET", base + "/healthz").json()
        if not health.get("ok"):
            return "staging shop /healthz did not answer ok"
        if mark is None:
            seen = "flags not checked (the staging shop has no /flags route)"
        else:
            seen = f"the staging shop did not fetch the change within {SHOP_FETCH_WAIT_SECONDS} s"
            deadline = clock() + SHOP_FETCH_WAIT_SECONDS
            while True:
                fetched = str(http.call("staging shop flags", "GET", base + "/flags").json().get("fetched_at") or "")
                if fetched and fetched != mark:
                    seen = "the staging shop fetched the change"
                    break
                if clock() >= deadline:
                    break
                sleep(SHOP_POLL_EVERY)
        checkout = http.call("staging shop checkout", "POST", base + "/checkout", json=CHECKOUT,
                             expect=(200, 500, 502, 504))
        if checkout.status_code == 200:
            return f"{seen}, checkout ok on the {checkout.json().get('path', '?')} path"
        return f"{seen}, but a checkout failed with HTTP {checkout.status_code}"
    except RelayError as error:
        return f"staging shop not checked ({error})"


def rehearse_order(order, ports: Any, targets: Targets, http: Http, staging_url: str, pending: list[dict],
                   iid: int, sha: str, sleep: Callable[[float], None] = time.sleep, now: datetime | None = None) -> str:
    action = order.do
    if action.kind == "traffic_to_revision":
        exists = ports.revision_exists(action.service, action.revision)
        return (f"order {order.id}: revision {action.revision} exists on {action.service}" if exists
                else f"order {order.id}: revision {action.revision} is NOT on {action.service}, this order cannot run")
    twin = staging_twin(action, targets)
    if twin is None:
        return f"order {order.id}: {action.describe()} has no staging scope to rehearse on"
    # The snapshot is taken and kept in the relay's state before anything changes, so whatever fails after
    # this line, the next ticks can put staging back from it (restore_pending).
    before = ports.snapshot(twin)
    entry = {"iid": iid, "sha": sha, "order": order.id, "action": twin.as_dict(), "before": before, "tries": 0}
    pending.append(entry)
    mark = shop_mark(http, staging_url) if staging_url else None
    change = ports.apply(twin, now)
    if not isinstance(change, Change) or not change.changed:
        pending.remove(entry)
        return f"order {order.id}: {twin.describe()} was already so on staging, nothing to rehearse"
    shop = check_shop(http, staging_url, mark, sleep) if staging_url else "no staging shop URL set, not checked"
    ports.restore(twin, before, now)
    pending.remove(entry)
    return f"order {order.id}: {twin.describe()} applied, {shop}, restored"


def _why(error: BaseException) -> str:
    return str(error) if isinstance(error, RuntimeError) else type(error).__name__


def _note(lines: list[str]) -> str:
    """The note text: each entry on one line of its own. Entries can echo the drafted file (its problems, its
    targets), and GitLab runs a line that starts with / as a quick action with the relay's token, so whitespace in
    an entry is collapsed and no line may start with /."""
    shown = [" ".join(str(line).split()) for line in lines]
    return "\n".join("'" + line if line.startswith("/") else line for line in shown) + "\n"


def restore_pending(relay_doc: dict, ports: Any) -> list[str]:
    """Put staging back after a rehearsal that stopped between its apply and its restore. Tried every tick,
    at most MAX_RESTORE_TRIES times per change; after that the change is left for a person and shown on the
    status page (rehearsal_left)."""
    pending = relay_doc.get("rehearsal_pending") or []
    if not pending:
        return []
    reported, still = [], []
    for entry in pending:
        action = action_from(entry["action"])
        try:
            ports.restore(action, entry["before"], None)
            reported.append(f"restored staging after an unfinished rehearsal of !{entry['iid']}: "
                            f"{action.describe()} is {describe_before(entry['before'])} again")
        except Exception as error:
            entry["tries"] = int(entry.get("tries", 0)) + 1
            if entry["tries"] >= MAX_RESTORE_TRIES:
                relay_doc["rehearsal_left"] = {"what": action.describe(), "before": describe_before(entry["before"]),
                                               "iid": entry["iid"], "reason": _why(error)[:160]}
            else:
                still.append(entry)
    relay_doc["rehearsal_pending"] = still
    return reported


def rehearse(gitlab: GitLab, ports: Any, http: Http, oncall: OnCall, targets: Targets, staging_url: str,
             iid: int, sha: str, now: datetime, pending: list[dict] | None = None,
             sleep: Callable[[float], None] = time.sleep) -> str:
    """Rehearse one merge request head and return the note text posted on it."""
    pending = [] if pending is None else pending
    text = gitlab.raw_file(ORDERS_PATH, sha)
    when = oncall.hhmm(now)
    lines = [f"Rehearsal on staging at {when}, written by code for commit {sha[:8]}.", ""]
    if text is None:
        lines.append("This draft removes the orders file: merging it signs nothing, so every alert wakes you.")
        return _note(lines)
    try:
        data = yaml.safe_load(text or "") or {}
        orders = parse_orders(data, targets, oncall)
    except (OrdersError, yaml.YAMLError, KeyError, TypeError, ValueError, AttributeError) as error:
        problems = error.problems if isinstance(error, OrdersError) else [f"the file could not be read ({type(error).__name__})"]
        lines.append("Code refuses this draft, so it cannot be signed:")
        lines += [f"- {' '.join(str(p).split())}" for p in problems]
        return _note(lines)
    would_sign = Signature(method="merge", user=oncall.user, at=now, commit=sha)
    problems = signature_problems(orders, would_sign, oncall, now)
    if problems:
        start, end = watch_window(orders, oncall)
        lines.append(f"Code refuses this draft, so it cannot be signed now: its night is {orders.night.isoformat()}, "
                     f"and a signature at {when} on {oncall.local(now):%d %b} would fall outside its window "
                     f"({oncall.hhmm(start)} on {oncall.local(start):%d %b} to {oncall.hhmm(end)} on "
                     f"{oncall.local(end):%d %b}). Set night to tonight's local date.")
        lines += [f"- {' '.join(str(p).split())}" for p in problems]
        return _note(lines)
    if not orders.orders:
        lines.append("No orders in this draft: nothing to rehearse. Merging it signs nothing, so every alert wakes you.")
        return _note(lines)
    for order in orders.orders:
        try:
            lines.append("- " + rehearse_order(order, ports, targets, http, staging_url, pending, iid, sha, sleep, now))
        except Exception as error:  # the note still says what happened; anything left on staging is restored
            text = f"- order {order.id}: rehearsal stopped ({_why(error)})"
            left = [e for e in pending if e["iid"] == iid and e["sha"] == sha and e["order"] == order.id]
            if left:
                text += (f"; staging may be left with {action_from(left[0]['action']).describe()} applied, "
                         "code restores it on the next ticks")
            lines.append(text)
    lines += ["", f"{len(orders.orders)} order(s) checked. Merge to sign; the orders end at {orders.expires:%H:%M}."]
    return _note(lines)


def step(relay_doc: dict, now: datetime, oncall: OnCall, targets: Targets, gitlab: GitLab, ports: Any,
         http: Http, staging_url: str, sleep: Callable[[float], None] = time.sleep) -> list[str]:
    """Called by the relay's tick, outside the watch's failure accounting: rehearse new orders merge requests."""
    reported = restore_pending(relay_doc, ports)
    branch = str(gitlab.json("read project", "GET", "")["default_branch"])
    done_heads: dict = relay_doc.setdefault("rehearsed", {})
    tries: dict = relay_doc.setdefault("rehearsal_tries", {})
    pending: list[dict] = relay_doc.setdefault("rehearsal_pending", [])
    heads = open_orders_requests(gitlab, branch)
    open_iids = {str(iid) for iid, _ in heads}
    for sha in [s for s in tries if s not in {h for _, h in heads}]:
        del tries[sha]  # a head that is gone (pushed over, merged or closed) needs no counter
    for iid in [i for i in done_heads if i not in open_iids]:
        del done_heads[iid]  # a merged or closed request needs no record
    for iid, sha in heads:
        if done_heads.get(str(iid)) == sha or tries.get(sha, 0) >= MAX_TRIES_PER_HEAD:
            continue
        tries[sha] = tries.get(sha, 0) + 1
        note = rehearse(gitlab, ports, http, oncall, targets, staging_url, iid, sha, now, pending, sleep)
        gitlab.json("post the rehearsal note", "POST", f"/merge_requests/{iid}/notes", expect=(200, 201),
                    json={"body": note})
        done_heads[str(iid)] = sha
        tries.pop(sha, None)
        reported.append(f"rehearsed !{iid} at {sha[:8]}")
    return reported
