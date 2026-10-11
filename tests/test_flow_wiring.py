"""The Duo flows are wired so each step can do its job: every placeholder is fed, nothing waits on a person
at bedtime, and the steps that write see their tool results and pass the branch on. Offline: reads flows/*.yml.
"""

from __future__ import annotations

import re

import pytest
import yaml

from conftest import REPO

FLOWS = sorted((REPO / "flows").glob("*.yml"))


def load(name: str) -> dict:
    return yaml.safe_load((REPO / "flows" / name).read_text(encoding="utf-8"))


def component(flow: dict, name: str) -> dict:
    return next(c for c in flow["components"] if c["name"] == name)


def prompt(flow: dict, prompt_id: str) -> str:
    template = next(p for p in flow["prompts"] if p["prompt_id"] == prompt_id)["prompt_template"]
    return template["system"] + template.get("user", "")


def route(flow: dict) -> list[tuple[str, str]]:
    return [(r["from"], r["to"]) for r in flow["routers"] if "to" in r]


@pytest.mark.parametrize("path", FLOWS, ids=lambda p: p.name)
def test_every_placeholder_in_a_prompt_is_an_input_of_each_component_that_uses_it(path):
    flow = yaml.safe_load(path.read_text(encoding="utf-8"))
    for item in flow["components"]:
        if "prompt_id" not in item:
            continue
        given = {i["as"] for i in item.get("inputs") or []}
        wanted = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", prompt(flow, item["prompt_id"])))
        assert wanted <= given, f"{path.name} {item['name']}: {sorted(wanted - given)} not wired"


@pytest.mark.parametrize("path", FLOWS, ids=lambda p: p.name)
def test_every_input_comes_from_the_goal_the_project_or_a_component_that_runs_before(path):
    flow = yaml.safe_load(path.read_text(encoding="utf-8"))
    names = {c["name"] for c in flow["components"]}
    for item in flow["components"]:
        for wire in item.get("inputs") or []:
            source = wire["from"].removeprefix("context:").split(".")[0]
            assert source in {"goal", "project_id", "inputs"} | names, f"{path.name} {item['name']}: {wire['from']}"


def test_dusk_never_waits_on_a_person_and_puts_its_question_in_the_merge_request():
    dusk = load("dusk.yml")
    assert not [c for c in dusk["components"] if c["type"] == "HumanInputComponent"]
    assert ("scout", "critic_1") in route(dusk)
    assert "One question" in prompt(dusk, "dusk_mr") and "Merge or approve to sign." in prompt(dusk, "dusk_mr")
    assert "nobody answers it tonight" in prompt(dusk, "dusk_scout")


def test_dusk_critics_can_read_the_targets_file():
    dusk = load("dusk.yml")
    for name in ("critic_1", "critic_2"):
        item = component(dusk, name)
        assert item["toolset"] == ["get_repository_file"]
        assert "project_id" in {i["as"] for i in item["inputs"]}
    assert "ops/targets.yml (read it" in prompt(dusk, "dusk_critic")


def test_the_writing_steps_see_their_tool_results_and_hand_the_branch_on():
    dusk, dawn = load("dusk.yml"), load("dawn.yml")
    assert component(dusk, "commit_writer")["type"] == "AgentComponent"
    assert component(dawn, "state_commit")["type"] == "AgentComponent"
    assert {"from": "context:commit_writer.final_answer", "as": "branch"} in component(dusk, "mr_writer")["inputs"]
    assert {"from": "context:state_commit.final_answer", "as": "branch"} in component(dawn, "state_mr")["inputs"]
    for text in (prompt(dusk, "dusk_commit"), prompt(dawn, "dawn_commit")):
        assert "add -2 (then -3, up to -5)" in text and "reply with the branch name only" in text
    for text in (prompt(dusk, "dusk_mr"), prompt(dawn, "dawn_mr")):
        assert "If the branch below starts with failed, open nothing." in text


def test_dusk_writes_who_drafted_the_orders():
    assert "night-orders dusk flow, watch issue #" in prompt(load("dusk.yml"), "dusk_commit")


def test_dawn_opens_the_countersign_first_and_notes_it_last():
    dawn = load("dawn.yml")
    assert route(dawn) == [("reporter", "state_commit"), ("state_commit", "state_mr"), ("state_mr", "log_writer"),
                           ("log_writer", "end")]
    assert "gitlab_merge_request_search" in component(dawn, "reporter")["toolset"]


def test_dawn_writes_the_state_file_the_morning_code_reads():
    commit = prompt(load("dawn.yml"), "dawn_commit")
    assert "night (the proposal's night value" in commit and "until_deployed" in commit
    from nightorders.countersign import SERVICE_KEYS, STATE_KEYS, TOP_KEYS
    assert TOP_KEYS == {"night", "flags", "services"}
    for key in sorted(STATE_KEYS | SERVICE_KEYS):
        assert key in commit, key
