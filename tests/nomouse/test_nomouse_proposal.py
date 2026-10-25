"""How strictly an answer is checked before anything is replayed, and how a path is swapped in.

The journey is the recorded checkout. Step 13 is "Tab to Pay now, $18.00, button", the step
that breaks on the development variants. Answers here are hand-written test data.
"""

from __future__ import annotations

import copy
import json

import pytest

from nomouse.journey import Step
from nomouse.proposal import MAX_NEW_STEPS, Fix, ProposalError, apply_path, parse

FAILED = 13
TEMPLATE = "nomouse/variants/dev-icons/templates/checkout.html"
TEMPLATES = [TEMPLATE]

STILL_USABLE = {
    "route": "still_usable",
    "why": "The pay button was renamed to Place order; it is clearly named.",
    "path": {"replace_from": 13, "replace_to": 14,
             "steps": [{"do": "find", "role": "button", "name": "Place order, $18.00"}]},
}
BARRIER = {
    "route": "barrier",
    "why": "The submit button is an unnamed lock icon.",
    "barrier": {"control": "button", "problem": "Heard only as button; a listener cannot tell it pays.",
                "wcag": "4.1.2"},
    "fix": {"file": TEMPLATE, "find": '<button type="submit">',
            "replace": '<button type="submit" aria-label="Pay now, $18.00">'},
}


def check(answer, journey, template_files=TEMPLATES):
    return parse(answer, source="test", journey=journey, failed_step=FAILED, template_files=template_files)


def changed(base: dict, *path_and_value):
    """A deep copy of base with one nested value set (or removed when the value is DROP)."""
    *keys, value = path_and_value
    answer = copy.deepcopy(base)
    target = answer
    for key in keys[:-1]:
        target = target[key]
    if value is DROP:
        del target[keys[-1]]
    else:
        target[keys[-1]] = value
    return answer


DROP = object()


def test_a_valid_still_usable_answer_becomes_a_path_proposal(journey):
    proposal = check(STILL_USABLE, journey)
    assert proposal.route == "still_usable" and proposal.source == "test"
    assert (proposal.replace_from, proposal.replace_to) == (13, 14)
    assert proposal.steps == (Step(do="find", role="button", name="Place order, $18.00"),)
    assert proposal.fix is None


def test_the_same_answer_as_a_json_string_parses_the_same(journey):
    assert check(json.dumps(STILL_USABLE), journey) == check(STILL_USABLE, journey)


def test_a_valid_barrier_answer_keeps_its_fix(journey):
    proposal = check(BARRIER, journey)
    assert proposal.route == "barrier" and proposal.wcag == "4.1.2"
    assert proposal.problem.startswith("Heard only as button")
    assert proposal.fix == Fix(file=TEMPLATE, find='<button type="submit">',
                               replace='<button type="submit" aria-label="Pay now, $18.00">')
    assert proposal.steps == ()


def test_a_barrier_may_come_without_a_fix_and_unsure_needs_only_why(journey):
    assert check(changed(BARRIER, "fix", DROP), journey).fix is None
    unsure = check({"route": "unsure", "why": "Check whether the icon buttons have tooltips."}, journey)
    assert unsure.route == "unsure" and unsure.steps == () and unsure.fix is None


def test_a_path_may_end_just_before_the_last_step(journey):
    last = len(journey.steps) - 1
    proposal = check(changed(STILL_USABLE, "path", "replace_to", last), journey)
    assert proposal.replace_to == last


@pytest.mark.parametrize("answer, message", [
    ('{"route": "barrier", "why": ', "not JSON"),
    ("[1, 2]", "JSON object"),
    (["still_usable"], "JSON object"),
    (None, "JSON object"),
    ({**STILL_USABLE, "confidence": 0.9}, "unknown keys"),
    ({"why": "no route"}, "route must be"),
    ({"route": "ship_it", "why": "x"}, "route must be"),
    ({"route": "unsure", "why": "   "}, "why is required"),
    ({"route": "still_usable", "why": "the page changed"}, "needs a path"),
])
def test_malformed_answers_are_refused(journey, answer, message):
    with pytest.raises(ProposalError, match=message):
        check(answer, journey)


@pytest.mark.parametrize("start, end", [
    (10, 13),  # stops before the failed step
    (14, 15),  # starts after the failed step
    (13, 13),  # an empty range
    (13, 16),  # replaces the last step, the order heading
    (9, 14),   # starts too far before the failed step
    (13, 18),  # past the end of the journey
    (-1, 14),
])
def test_a_path_must_cover_the_failed_step_and_leave_the_last_step(journey, start, end):
    answer = changed(changed(STILL_USABLE, "path", "replace_from", start), "path", "replace_to", end)
    with pytest.raises(ProposalError, match="around step 13"):
        check(answer, journey)


@pytest.mark.parametrize("start, end", [(True, 14), (13, True), ("13", 14), (13.0, 14)])
def test_step_numbers_must_be_real_integers(journey, start, end):
    answer = changed(changed(STILL_USABLE, "path", "replace_from", start), "path", "replace_to", end)
    with pytest.raises(ProposalError, match="must be integers"):
        check(answer, journey)


def test_a_path_has_one_to_eight_steps(journey):
    step = {"do": "press", "key": "Enter"}
    with pytest.raises(ProposalError, match="1 to 8 steps"):
        check(changed(STILL_USABLE, "path", "steps", [step] * (MAX_NEW_STEPS + 1)), journey)
    with pytest.raises(ProposalError, match="1 to 8 steps"):
        check(changed(STILL_USABLE, "path", "steps", []), journey)
    assert len(check(changed(STILL_USABLE, "path", "steps", [step] * MAX_NEW_STEPS), journey).steps) == 8


@pytest.mark.parametrize("step", [
    {"do": "find", "role": "button", "name": "Pay", "selector": "#pay"},  # no selectors, ever
    {"do": "press", "key": "Tab"},  # Tab belongs to find, so the key budget stays honest
    {"do": "press", "key": "Return"},
    {"do": "click", "name": "Pay"},
    {"do": "find", "role": "button"},
    {"do": "type", "text": ""},
    "find the pay button",
])
def test_bad_steps_are_refused(journey, step):
    with pytest.raises(ProposalError, match="bad step"):
        check(changed(STILL_USABLE, "path", "steps", [step]), journey)


@pytest.mark.parametrize("answer, message", [
    (changed(BARRIER, "barrier", DROP), "barrier needs"),
    (changed(BARRIER, "barrier", "problem", DROP), "barrier needs"),
    (changed(BARRIER, "barrier", "problem", "  "), "barrier needs"),
    (changed(BARRIER, "barrier", "wcag", "4.1"), "wcag"),
    (changed(BARRIER, "barrier", "wcag", "WCAG 4.1.2"), "wcag"),
    (changed(BARRIER, "fix", "not a fix"), "fix must be an object"),
    (changed(BARRIER, "fix", "file", "nomouse/shop/templates/checkout.html"), "template files"),
    (changed(BARRIER, "fix", "file", "../../etc/passwd"), "template files"),
    (changed(BARRIER, "fix", "find", ""), "fix.find must be non-empty"),
    (changed(BARRIER, "fix", "replace", "x" * 2_001), "at most 2000"),
])
def test_bad_barrier_answers_are_refused(journey, answer, message):
    with pytest.raises(ProposalError, match=message):
        check(answer, journey)


def test_apply_path_swaps_in_exactly_the_proposed_segment(journey):
    proposal = check(STILL_USABLE, journey)
    walked = apply_path(journey, proposal)
    assert len(walked.steps) == len(journey.steps)
    assert walked.steps[:13] == journey.steps[:13]
    assert walked.steps[13] == Step(do="find", role="button", name="Place order, $18.00")
    assert walked.steps[14:] == journey.steps[14:]
    assert walked.steps[-1] == Step(do="expect_heading", name="Order placed")
    assert (walked.name, walked.start, walked.key_budget, walked.order_item) == \
        (journey.name, journey.start, journey.key_budget, journey.order_item)
    # The recorded journey itself is untouched.
    assert journey.steps[13] == Step(do="find", role="button", name="Pay now, $18.00")


def test_apply_path_can_insert_more_steps_than_it_removes(journey):
    longer = changed(STILL_USABLE, "path", {
        "replace_from": 13, "replace_to": 15,
        "steps": [{"do": "find", "role": "button", "name": "Review order"}, {"do": "press", "key": "Enter"},
                  {"do": "expect_heading", "name": "Review your order"},
                  {"do": "find", "role": "button", "name": "Place order, $18.00"}, {"do": "press", "key": "Enter"}]})
    walked = apply_path(journey, check(longer, journey))
    assert len(walked.steps) == len(journey.steps) + 3
    assert [s.describe() for s in walked.steps[13:]] == [
        'Tab to "Review order, button"', "press Enter", 'hear heading "Review your order"',
        'Tab to "Place order, $18.00, button"', "press Enter", 'hear heading "Order placed"']
