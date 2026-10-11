"""A kept change is a lease: it ends when the merge request named at the countersign is in production.

Every name, number and time here is test data; the night is the demo's.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta

import pytest

from conftest import OPS
from nightorders import kept
from nightorders.countersign import parse_state
from nightorders.daysheet import render
from nightorders.model import Change
from nightorders.morning import StateFile, step
from nightorders.orders import OrdersError, load_context
from nightorders.status_page import public, render as render_page
from test_morning import FakePorts, local, night, signed  # noqa: F401
from test_relay_ports import API, FLAG, NOW, Server, flag, ports_for

KEEP_OFF = {"flag": "new_checkout", "environment": "production", "keep": "off", "until": "the rounding fix ships"}


class LeasePorts(FakePorts):
    """The kept-list ports: whether a target still holds, whether a merge request shipped, and a quiet push."""

    def __init__(self, shipped=("waiting", "!38 is not merged yet"), holds=True, changed=True):
        super().__init__()
        self.answer, self.still, self.changed = shipped, holds, changed
        self.asked: list[tuple[int, str]] = []
        self.pushes: list[tuple[str, tuple]] = []

    def holds(self, action):
        return self.still

    def shipped(self, merge_request, environment):
        self.asked.append((merge_request, environment))
        return self.answer

    def restore(self, action, before, at):
        super().restore(action, before, at)
        return Change(changed=self.changed, before=None, detail="")

    def quiet_push(self, title, lines, at):
        self.pushes.append((title, lines))


def _targets():
    return load_context(OPS)[1]


def test_until_deployed_reads_a_merge_request_number_and_refuses_anything_else():
    for value in (38, "38", "!38", " !38 "):
        [item] = parse_state({"flags": [dict(KEEP_OFF, until_deployed=value)]}, _targets())
        assert item.until_deployed == 38
    [plain] = parse_state({"flags": [KEEP_OFF]}, _targets())
    assert plain.until_deployed is None
    for bad in ("soon", 0, -3, True, "!", 3.5):
        with pytest.raises(OrdersError) as error:
            parse_state({"flags": [dict(KEEP_OFF, until_deployed=bad)]}, _targets())
        assert error.value.problems == ["ops/state.yml entry 1: until_deployed must be a merge request number, like 38"]
    [service] = parse_state({"services": [{"service": "shop", "keep": "shop-00041", "until_deployed": 40}]}, _targets())
    assert service.until_deployed == 40


def countersigned(night, until_deployed=38):
    """The demo night ended and countersigned at 07:42: new_checkout kept off with a lease, the cache flag restored."""
    relay_doc, ports = {}, LeasePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    state = {"night": "2026-10-20", "flags": [dict(KEEP_OFF, until_deployed=until_deployed)]}
    step(relay_doc, night, True, StateFile(state, signed(night, "2026-10-21T07:42")), ports,
         local(night, "2026-10-21T07:43"), 7)
    assert relay_doc["dawn"]["countersign"]["problems"] == []
    return relay_doc, ports


def test_the_countersign_puts_a_kept_change_on_the_kept_list_with_its_snapshot_and_lease(night):
    relay_doc, ports = countersigned(night)
    [item] = relay_doc["kept"]
    assert item["action"] == {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}
    assert item["before"] == {"kind": "flag", "flag": "new_checkout", "environment": "production", "value": "on"}
    assert (item["since"], item["until_deployed"], item["environment"]) == ("2026-10-20", 38, "production")
    assert ("- Kept: new_checkout off in production, until the rounding fix ships (code restores it when !38 is in "
            "production)") in ports.notes[-1]
    assert kept.summary(item) == ("new_checkout off in production, kept since the night of 2026-10-20, until the "
                                  "rounding fix ships. Ends by itself when !38 is in production.")


def test_a_lease_never_ends_at_night_and_is_checked_at_most_every_ten_minutes(night):
    relay_doc, _ = countersigned(night)
    ports = LeasePorts()
    assert kept.step(relay_doc, local(night, "2026-10-21T07:59"), night.oncall, ports) == []
    assert kept.step(relay_doc, local(night, "2026-10-21T20:00"), night.oncall, ports) == []
    assert ports.asked == []
    kept.step(relay_doc, local(night, "2026-10-21T08:00"), night.oncall, ports)
    kept.step(relay_doc, local(night, "2026-10-21T08:09"), night.oncall, ports)
    assert ports.asked == [(38, "production")]
    assert relay_doc["kept"][0]["lease"] == "!38 is not merged yet" and ports.restored == []
    kept.step(relay_doc, local(night, "2026-10-21T08:10"), night.oncall, ports)
    assert len(ports.asked) == 2


def test_a_shipped_merge_request_ends_the_lease_restores_the_snapshot_and_says_so_quietly(night):
    relay_doc, _ = countersigned(night)
    words = "!38 is in production (deployment 88, commit 39f1c0de)"
    ports = LeasePorts(shipped=("shipped", words))
    done = kept.step(relay_doc, local(night, "2026-10-21T15:40"), night.oncall, ports)
    assert done == ["lease on new_checkout off in production ended"]
    assert ports.restored == [("new_checkout off in production",
                               {"kind": "flag", "flag": "new_checkout", "environment": "production", "value": "on"})]
    assert relay_doc["kept"] == []
    assert ports.notes[-1] == (f"Lease ended: {words}. Restored new_checkout in production to how it was before the "
                               "night (on). It was kept since the night of 2026-10-20, until the rounding fix ships.")
    assert ports.pushes == [("Night Orders: a kept change ended", (f"Lease ended: {words}.", "Restored new_checkout "
                             "in production to how it was before the night (on)."))]
    assert relay_doc["kept_ended"][0]["text"] == ports.notes[-1]
    # Nothing left to check: the next pass asks nothing.
    assert kept.step(relay_doc, local(night, "2026-10-21T16:00"), night.oncall, ports) == []


def test_a_restore_that_finds_the_target_already_back_says_so(night):
    relay_doc, _ = countersigned(night)
    ports = LeasePorts(shipped=("shipped", "!38 is in production (deployment 88, commit 39f1c0de)"), changed=False)
    kept.step(relay_doc, local(night, "2026-10-21T15:40"), night.oncall, ports)
    assert "(on) (already as before the night)." in ports.notes[-1]


def test_a_target_changed_by_hand_leaves_the_kept_list_and_nothing_is_restored(night):
    relay_doc, _ = countersigned(night)
    ports = LeasePorts(shipped=("shipped", "!38 is in production"), holds=False)
    done = kept.step(relay_doc, local(night, "2026-10-21T09:00"), night.oncall, ports)
    assert done == ["new_checkout off in production changed by hand, off the kept list"]
    assert relay_doc["kept"] == [] and ports.restored == [] and ports.asked == []
    assert ports.notes[-1] == ("No longer kept: new_checkout off in production was changed after the countersign, so "
                               "it is off the kept list. Code changed nothing.")


def test_a_closed_merge_request_is_said_once_and_the_change_stays_kept(night):
    relay_doc, _ = countersigned(night)
    ports = LeasePorts(shipped=("closed", "!38 was closed without merging"))
    kept.step(relay_doc, local(night, "2026-10-21T09:00"), night.oncall, ports)
    kept.step(relay_doc, local(night, "2026-10-21T09:30"), night.oncall, ports)
    assert ports.asked == [(38, "production")] and len(ports.notes) == 1  # said once
    assert ports.notes[-1] == ("The lease on new_checkout off in production cannot end by itself: !38 was closed "
                               "without merging. It stays kept until a person changes it.")
    [item] = relay_doc["kept"]
    assert item["until_deployed"] is None and kept.summary(item).endswith("No lease: it stays until a person changes it.")


def test_a_kept_target_a_newer_night_changed_waits_for_that_nights_countersign(night):
    relay_doc, _ = countersigned(night)
    relay_doc["dawn"] = {"night": "2026-10-21", "countersign": None, "loose_ends": [
        {"action": {"action": "flag_set", "flag": "new_checkout", "environment": "production", "to": "off"}}]}
    ports = LeasePorts(shipped=("shipped", "!38 is in production"), holds=False)
    assert kept.step(relay_doc, local(night, "2026-10-22T09:00"), night.oncall, ports) == []
    assert len(relay_doc["kept"]) == 1 and ports.asked == []


def test_keeping_a_target_again_keeps_the_older_snapshot(night):
    relay_doc, _ = countersigned(night)
    first = relay_doc["kept"][0]
    newer = dict(first, before={"kind": "flag", "value": "off"}, since="2026-10-21", until_deployed=41)
    kept.add(relay_doc, [newer])
    [item] = relay_doc["kept"]
    assert item["before"] == first["before"] and item["since"] == "2026-10-20" and item["until_deployed"] == 41


def test_a_kept_change_without_a_snapshot_is_handed_to_a_person(night):
    relay_doc, _ = countersigned(night)
    relay_doc["kept"][0]["before"] = None
    ports = LeasePorts(shipped=("shipped", "!38 is in production"))
    kept.step(relay_doc, local(night, "2026-10-21T15:40"), night.oncall, ports)
    assert ports.restored == [] and relay_doc["kept"] == []
    assert ("There is no snapshot from before the night of 2026-10-20, so a person restores new_checkout off in "
            "production.") in ports.notes[-1]


def test_until_text_is_one_plain_line(night):
    item = parse_state({"flags": [dict(KEEP_OFF, until="the `fix`\nships\n\n" + "x" * 300)]}, _targets())[0]
    entry = kept.entry(item, None, "", "2026-10-20", NOW, "production")
    assert "\n" not in entry["until"] and "`" not in entry["until"] and len(entry["until"]) == kept.UNTIL_CHARS


# The GitLab answers behind shipped() and holds().

MR = f"{API}/merge_requests/38"
DEPLOYS = f"{API}/deployments"
BASE = f"{API}/repository/merge_base"


def test_shipped_reads_merged_then_deployed_and_nothing_else():
    ports = ports_for(Server({("GET", MR): {"iid": 38, "state": "opened"}}))
    assert ports.shipped(38, "production") == ("waiting", "!38 is not merged yet")
    ports = ports_for(Server({("GET", MR): {"iid": 38, "state": "closed"}}))
    assert ports.shipped(38, "production") == ("closed", "!38 was closed without merging")
    server = Server({("GET", MR): {"iid": 38, "state": "merged", "merge_commit_sha": "a" * 40},
                     ("GET", DEPLOYS): []})
    assert ports_for(server).shipped(38, "production") == (
        "waiting", "!38 is merged, and nothing has been deployed to production since")
    [listed] = server.sent("GET", DEPLOYS)
    assert dict(listed.url.params) == {"environment": "production", "status": "success", "order_by": "finished_at",
                                       "sort": "desc", "per_page": "1"}


def test_shipped_when_the_deployed_commit_is_the_merge_commit_or_comes_after_it():
    merged = {"iid": 38, "state": "merged", "merge_commit_sha": "a" * 40}
    exact = Server({("GET", MR): merged, ("GET", DEPLOYS): [{"iid": 88, "sha": "a" * 40}]})
    assert ports_for(exact).shipped(38, "production") == (
        "shipped", "!38 is in production (deployment 88, commit aaaaaaaa)")
    assert exact.sent("GET", BASE) == []
    later = Server({("GET", MR): merged, ("GET", DEPLOYS): [{"iid": 89, "sha": "b" * 40}],
                    ("GET", BASE): {"id": "a" * 40}})
    assert ports_for(later).shipped(38, "production")[0] == "shipped"
    [asked] = later.sent("GET", BASE)
    assert asked.url.params.get_list("refs[]") == ["a" * 40, "b" * 40]
    before = Server({("GET", MR): merged, ("GET", DEPLOYS): [{"iid": 87, "sha": "c" * 40}],
                     ("GET", BASE): {"id": "d" * 40}})
    assert ports_for(before).shipped(38, "production") == (
        "waiting", "!38 is merged; the last deployment to production (cccccccc) does not include it yet")
    unknown = Server({("GET", MR): merged, ("GET", DEPLOYS): [{"iid": 87, "sha": "c" * 40}],
                      ("GET", BASE): (404, {"message": "404 Not found"})})
    assert ports_for(unknown).shipped(38, "production")[0] == "waiting"


def test_shipped_uses_the_squash_commit_or_the_head_when_there_is_no_merge_commit():
    squashed = {"iid": 38, "state": "merged", "merge_commit_sha": None, "squash_commit_sha": "e" * 40, "sha": "f" * 40}
    server = Server({("GET", MR): squashed, ("GET", DEPLOYS): [{"iid": 90, "sha": "e" * 40}]})
    assert ports_for(server).shipped(38, "production")[0] == "shipped"


def test_holds_reads_the_flag_as_it_is_now():
    off = flag(True, (12, "default", [(23, "staging")]))
    on = flag(True, (11, "default", [(21, "production")]))
    action = parse_state({"flags": [KEEP_OFF]}, _targets())[0].action
    assert ports_for(Server({("GET", FLAG): off})).holds(action) is True
    assert ports_for(Server({("GET", FLAG): on})).holds(action) is False


def test_the_quiet_push_has_default_priority():
    server = Server({("POST", "/test-topic-not-real"): {"id": "x"}, ("GET", API): {"web_url": "https://gitlab.example/g/p"}})
    ports = ports_for(server)
    ports.watch_issue = 12
    ports.quiet_push("Night Orders: a kept change ended", ("Lease ended.", "Restored."), NOW)
    [sent] = server.sent("POST", "/test-topic-not-real")
    assert sent.headers["Priority"] == "default" and sent.headers["Click"] == "https://gitlab.example/g/p/-/issues/12"


# Where the kept list shows.

def test_the_day_sheet_lists_the_kept_changes_when_the_relay_adds_them(night):
    relay_doc, _ = countersigned(night)
    sheet = {"_label": "label", "date": "2026-10-21", "timezone": "America/Los_Angeles", "written_at": "21:00",
             "merged_today": [], "deployments": [], "flags": []}
    assert "Kept from earlier nights" not in render(sheet)
    text = render(dict(sheet, kept=[kept.summary(item) for item in relay_doc["kept"]]))
    assert ("### Kept from earlier nights\n- new_checkout off in production, kept since the night of 2026-10-20, until "
            "the rounding fix ships. Ends by itself when !38 is in production.") in text
    assert "### Kept from earlier nights\n- nothing kept" in render(dict(sheet, kept=[]))


def test_the_status_page_and_its_json_show_the_kept_list_and_what_ended(night):
    relay_doc, _ = countersigned(night)
    relay_doc["status"] = {"checked_at": NOW.isoformat(), "timezone": "America/Los_Angeles"}
    doc = {"night": "2026-10-21", "relay": relay_doc}
    assert public(doc, NOW)["kept"] == [kept.summary(relay_doc["kept"][0])]
    page = render_page(doc, NOW)
    assert "Kept from earlier nights" in page and "Ends by itself when !38 is in production." in page
    ports = LeasePorts(shipped=("shipped", "!38 is in production (deployment 88, commit 39f1c0de)"))
    kept.step(relay_doc, local(night, "2026-10-21T15:40"), night.oncall, ports)
    data = public(doc, NOW)
    assert data["kept"] == [] and data["kept_ended"][0]["text"].startswith("Lease ended: !38 is in production")
    assert "21 Oct 15:40: Lease ended" in render_page(doc, NOW)


def test_the_relay_runs_the_kept_list_as_a_chore_that_never_fails_a_tick():
    import main
    source = open(main.__file__, encoding="utf-8").read()
    chore = source.split("relay.kept_ports is not None", 1)[1].split("# Keep what the tick did", 1)[0]
    assert "kept.step(relay_doc, now, inputs.oncall, relay.kept_ports)" in chore
    assert 'relay_doc["kept_problem"]' in chore and "except Exception" in chore
