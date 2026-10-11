"""Real keyboard walks through the demo shop in Chromium. Code alone gives each verdict."""

from __future__ import annotations

import pytest

from nomouse.journey import Step, evidence, replay

pytestmark = pytest.mark.browser


def walk_once(walker, journey, variant=None):
    walk = walker.open(variant)
    try:
        return replay(walk, journey)
    finally:
        walk.close()


def test_recorded_journey_places_exactly_one_order_on_the_base_shop(walker, journey):
    result = walk_once(walker, journey)
    assert result.verdict == "clear", result.reason
    assert [o["item"] for o in result.orders] == ["ethiopia"]
    assert result.keys <= journey.key_budget


def test_a_renamed_pay_button_breaks_the_recorded_walk_and_is_heard(walker, journey):
    result = walk_once(walker, journey, "dev-rename")
    assert result.verdict == "broken" and result.failed_step == 13
    heard = [a.spoken() for a in result.heard]
    assert "Place order, $18.00, button" in heard
    assert heard[0] == "Demo Beans home, link"  # evidence starts from the top of the page
    assert result.orders == []


def test_unnamed_icon_buttons_are_heard_as_button_only(walker, journey):
    result = walk_once(walker, journey, "dev-icons")
    assert result.verdict == "broken" and result.failed_step == 13
    assert [a.spoken() for a in result.heard][-3:] == ["button", "button", "button"]
    block = evidence(journey, result)
    assert block["page"] == "/checkout" and block["heard_in_tab_order"][-1] == "button"


def test_a_path_that_presses_a_meaningless_control_is_refused(walker, journey):
    """Whoever wrote the path, replay refuses to press a control named like an icon file.

    t-junk is a test-only variant whose Pay button is announced as "icon-lock".
    """
    steps = list(journey.steps)
    steps[13] = Step(do="find", role="button", name="icon-lock")
    result = walk_once(walker, journey.with_steps(steps), "t-junk")
    assert result.verdict == "refused" and result.failed_step == 14
    assert "says nothing" in result.reason
    assert result.orders == []


def test_the_key_budget_is_enforced(walker, journey):
    tight = journey.__class__(**{**journey.__dict__, "key_budget": 5})
    result = walk_once(walker, tight)
    assert result.verdict == "over_budget"
    assert result.orders == []


def test_a_missing_heading_breaks_the_walk(walker, journey):
    steps = list(journey.steps)
    steps[2] = Step(do="expect_heading", name="Nothing here")
    result = walk_once(walker, journey.with_steps(steps))
    assert result.verdict == "broken" and result.failed_step == 2
    assert "Ethiopia Yirgacheffe, heading level 1" in result.reason


def test_the_walker_records_what_a_sighted_person_sees_on_a_control(walker):
    walk = walker.open()
    try:
        walk.goto("/product/ethiopia")
        for _ in range(6):
            heard = walk.press("Tab")
            if heard.name == "Add to cart":
                break
        assert heard.visible == "Add to cart"
        assert heard.spoken() == "Add to cart, button"  # the visible text is checked, never spoken
    finally:
        walk.close()


def test_a_path_through_a_button_announced_differently_from_its_label_is_refused(walker, journey):
    """t-mismatch is a test-only variant: the Pay button shows its price but is announced
    "Save for later". The order would go through, so only the label check stops it."""
    steps = list(journey.steps)
    steps[13] = Step(do="find", role="button", name="Save for later")
    result = walk_once(walker, journey.with_steps(steps), "t-mismatch")
    assert result.verdict == "refused" and result.failed_step == 14
    assert "visible label" in result.reason
    assert result.orders == []
