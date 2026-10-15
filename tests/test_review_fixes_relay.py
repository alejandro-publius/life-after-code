"""Fixes from the 11 Oct review of what the relay posts and reads. Offline.

Text the relay did not write itself (a drafted orders file, a state file, a loose end) can never start a line
with / in a note or a merge request description, where GitLab would run it as a quick action with the relay's
token; /status.json reads the same cached state as the page; and one kept change that cannot be checked does not
stall the others.

The demo night is demo data (planted faults, simulated shop). Every other name, number and time is test data.
"""

from __future__ import annotations

import copy

import pytest
import yaml
from fastapi.testclient import TestClient

from conftest import OPS, ORDERS
from nightorders import kept
from nightorders.gitlab_ports import RelayError
from nightorders.morning import StateFile, countersign_request, step
from nightorders.orders import OrdersError, load_context, parse_orders
from nightorders.state import FileStore
from test_kept import KEEP_OFF, LeasePorts, countersigned
from test_morning import FakePorts, local, night, signed  # noqa: F401
from test_rehearsal import World, run
from test_relay_app import main
from test_relay_ports import FLAG, Server, flag, ports_for


def quick_actions(text: str) -> list[str]:
    """Every line GitLab could read as a quick action."""
    return [line for line in text.splitlines() if line.lstrip().startswith("/")]


# B1: a drafted orders file whose values hold newlines used to put a standalone /approve line in the rehearsal note.

def drafted(change) -> str:
    data = copy.deepcopy(ORDERS)
    change(data["orders"][0])
    return yaml.safe_dump(data, sort_keys=False)


ATTACKS = {
    "id": lambda order: order.update(id="1\n\n/approve", when=dict(order["when"], below=0.01)),
    "id on its own line": lambda order: order.update(id="1\n\n/approve\n", when=dict(order["when"], below=0.01)),
    "action": lambda order: order["do"].update(action="x\n\n/approve\n"),
}


@pytest.mark.parametrize("attack", sorted(ATTACKS))
def test_a_drafted_file_cannot_put_a_quick_action_in_the_rehearsal_note(attack):
    text = drafted(ATTACKS[attack])
    order = yaml.safe_load(text)["orders"][0]
    assert "\n/approve" in f"{order['id']} {order['do']['action']}"  # the file really carries the newline
    world = World(orders_text=text)
    run(world)
    [note] = world.notes
    assert quick_actions(note["body"]) == []
    assert "Code refuses this draft, so it cannot be signed:" in note["body"]
    assert "/approve" in note["body"]  # still shown, as plain words inside a line


def test_the_exact_attack_reads_as_one_line_in_the_note():
    world = World(orders_text=drafted(ATTACKS["id"]))  # id: "1\n\n/approve"
    run(world)
    lines = world.notes[0]["body"].splitlines()
    assert "- order 1 /approve: give exactly one of above or below" in lines


def test_every_problem_from_an_orders_file_is_one_line(oncall, targets):
    data = copy.deepcopy(ORDERS)
    data["orders"][0]["do"]["action"] = "x\n\n/approve\n"
    with pytest.raises(OrdersError) as error:
        parse_orders(data, targets, oncall)
    assert error.value.problems and all("\n" not in problem for problem in error.value.problems)
    assert error.value.problems[0] == "order 1: action x /approve is not on the menu (flag_set, traffic_to_revision)"


def test_a_state_file_cannot_put_a_quick_action_in_the_countersign_note(night):
    relay_doc, ports = {}, FakePorts()
    step(relay_doc, night, True, None, ports, local(night, "2026-10-21T07:00"), 7)
    for data in ({"night": "2026-10-19\n/close", "flags": []},
                 {"night": "2026-10-20", "flags": [], "other\n/close\n": 1},
                 {"night": "2026-10-20", "flags": [{"flag": "x\n/close\n", "environment": "production", "keep": "off"}]}):
        state = StateFile(data, signed(night, "2026-10-21T07:42"))
        step(relay_doc, night, True, state, ports, local(night, "2026-10-21T07:43"), 7)
        relay_doc["dawn"].pop("refused")  # the next file is read as a new signature
        assert ports.notes[-1].startswith("Countersign by Priya") and quick_actions(ports.notes[-1]) == []
    kept_file = {"night": "2026-10-20", "flags": [dict(KEEP_OFF, until="the fix\n\n/close\nships")]}
    step(relay_doc, night, True, StateFile(kept_file, signed(night, "2026-10-21T07:50")), ports,
         local(night, "2026-10-21T07:51"), 7)
    assert "- Kept: new_checkout off in production, until the fix /close ships" in ports.notes[-1].splitlines()
    assert quick_actions(ports.notes[-1]) == []


def test_a_loose_end_cannot_put_a_quick_action_in_the_countersign_merge_request():
    record = {"night": "2026-10-20", "loose_ends": [
        {"action": {"action": "traffic_to_revision", "service": "shop", "revision": "shop-00041\n\n/close"},
         "why": "approved by thumbs-up, 02:10, failed and may be in place",
         "before": {"kind": "traffic", "service": "shop", "traffic": [{"percent": 100, "revision": "shop-0\n/merge"}]}}]}
    state_text, title, description = countersign_request(record)
    assert quick_actions(description) == [] and quick_actions(title) == []
    assert "- shop traffic to revision shop-00041 /close (approved by thumbs-up, 02:10" in description


# B4: /status.json used to read the state store on every request, while / used a 15 s cache.

def test_the_status_json_and_the_page_share_one_cached_read_of_the_state(tmp_path):
    loads = []

    class CountingStore(FileStore):
        def load(self):
            loads.append(1)
            return super().load()

    client = TestClient(main.create_app(make_store=lambda config: CountingStore(tmp_path / "state.json")))
    for path in ("/status.json", "/", "/status.json", "/status.json", "/"):
        assert client.get(path).status_code == 200
    assert len(loads) == 1
    assert client.get("/status.json").json()["available"] is True


def test_the_status_json_still_says_when_the_state_cannot_be_read():
    def broken(config):
        raise RelayError("Cloud Storage read state: HTTP 403")

    client = TestClient(main.create_app(make_store=broken))
    answer = client.get("/status.json")
    assert answer.status_code == 503 and answer.json() == {"available": False}
    assert answer.headers["cache-control"] == "no-store"
    assert "cannot be read right now" in client.get("/").text


# C5: holds() used to raise on a * scope or an inactive flag, and the kept list then stalled for good.

def test_holds_reads_a_wide_scope_or_an_inactive_flag_as_a_plain_answer():
    off, on = parse_state_action("off"), parse_state_action("on")
    wide = flag(True, (11, "default", [(21, "*")]))  # on everywhere through *: not off in production
    assert ports_for(Server({("GET", FLAG): wide})).holds(off) is False
    inactive = flag(False, (12, "default", [(22, "production"), (23, "staging")]))  # inactive: on for nobody
    assert ports_for(Server({("GET", FLAG): inactive})).holds(on) is False
    assert ports_for(Server({("GET", FLAG): inactive})).holds(off) is True


def parse_state_action(keep: str):
    from nightorders.countersign import parse_state

    return parse_state({"flags": [dict(KEEP_OFF, keep=keep)]}, load_context(OPS)[1])[0].action


class OneBadTarget(LeasePorts):
    def holds(self, action):
        if action.flag == "new_checkout":
            raise RelayError("GitLab read flag new_checkout: HTTP 503")
        return True


def test_one_kept_change_that_cannot_be_checked_does_not_stall_the_others(night):
    relay_doc, _ = countersigned(night)
    first = relay_doc["kept"][0]
    second = dict(first, action={"action": "flag_set", "flag": "stock_from_cache", "environment": "production",
                                 "to": "on"},
                  before={"kind": "flag", "flag": "stock_from_cache", "environment": "production", "value": "off"},
                  until_deployed=39)
    relay_doc["kept"] = [first, second]
    ports = OneBadTarget(shipped=("shipped", "!39 is in production (deployment 90, commit 39f1c0de)"))
    done = kept.step(relay_doc, local(night, "2026-10-21T15:40"), night.oncall, ports)
    assert done == ["lease on stock_from_cache on in production ended"]
    assert ports.restored == [("stock_from_cache on in production", second["before"])]
    assert relay_doc["kept"] == [first]
    assert relay_doc["kept_problem"]["reason"] == ("new_checkout off in production: GitLab read flag new_checkout: "
                                                   "HTTP 503")
    ports = LeasePorts()
    kept.step(relay_doc, local(night, "2026-10-21T15:50"), night.oncall, ports)
    assert "kept_problem" not in relay_doc  # every kept change could be checked this time
