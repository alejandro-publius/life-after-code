"""B1 and B2, the baselines the model has to beat.

The B1 rules and B2's limits are checked first without a browser. Then both run on real
walks: a renamed Pay button (a path exists), unnamed icon buttons (no honest path exists)
and a test-only variant that adds a review page before paying (only B2's search finds it).
"""

from __future__ import annotations

import pytest

from nomouse.announce import Announcement
from nomouse.baselines import NO_PATH, NOT_FOUND, b1, b2, find_named_path
from nomouse.journey import Result, Step, replay
from nomouse.proposal import apply_path, parse

PAY = 13  # the recorded journey's step 'Tab to "Pay now, $18.00, button"'
PLACE_ORDER = Step(do="find", role="button", name="Place order, $18.00")

# t-b2-review: the checkout form goes to a review page, and the order is placed from there.
REVIEW_CHECKOUT = """<h1>Checkout</h1>
<form method="post" action="/review" class="card">
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="email" required>
<label for="card">Card number</label>
<input id="card" name="card" inputmode="numeric" autocomplete="cc-number" required>
<button type="submit">Continue to review</button>
</form>
"""
REVIEW_PAGE = """<h1>Review your order</h1>
<form method="post" action="/pay" class="card">
<p>$product_name, $product_size, $price. Receipt to $email.</p>
<input type="hidden" name="email" value="$email">
<input type="hidden" name="card" value="$card">
<button type="submit">Place order, $price</button>
</form>
"""


def checkout_heard(*extra: Announcement) -> list[Announcement]:
    """The tab order on a checkout page that kept every field, plus whatever stands where Pay was."""
    return [Announcement("link", "Demo Beans home"), Announcement("link", "Cart, 1 item"),
            Announcement("textbox", "Email", value="robin@example.test"), Announcement("textbox", "Card number"),
            Announcement("combobox", "Delivery"), *extra]


def broken_at(step: int, heard: list[Announcement], verdict: str = "broken") -> Result:
    return Result(verdict=verdict, failed_step=step, reason="test", heard=list(heard), page="/checkout")


def reparse(proposal, journey, result):
    """A baseline's proposal must pass the same checks as a model's answer, and come back unchanged."""
    answer = {key: value for key, value in proposal.as_dict().items() if key != "source"}
    return parse(answer, source=proposal.source, journey=journey, failed_step=result.failed_step, template_files=[])


class NoBrowser:
    """A walker that fails the test if the search opens a walk."""

    def open(self, variant=None, session=None):
        raise AssertionError("the search opened a walk it should not have")


def test_b1_calls_an_unnamed_button_a_barrier(journey):
    result = broken_at(PAY, checkout_heard(Announcement("button")))
    proposal = b1(journey, result)
    assert (proposal.source, proposal.route, proposal.control, proposal.wcag) == ("B1", "barrier", "button", "4.1.2")
    assert "cannot tell what it does" in proposal.problem
    assert proposal.fix is None and proposal.steps == ()
    assert reparse(proposal, journey, result) == proposal


def test_b1_calls_a_junk_name_a_barrier_even_next_to_a_plausible_rename(journey):
    heard = checkout_heard(Announcement("button", "Place order, $18.00"), Announcement("button", "icon-lock"))
    proposal = b1(journey, broken_at(PAY, heard))
    assert (proposal.route, proposal.control, proposal.wcag) == ("barrier", "icon-lock, button", "4.1.2")
    assert "icon-lock" in proposal.problem


def test_b1_follows_a_renamed_control_of_the_same_role(journey):
    # The link still has the old wording, but the walk pressed a button; the renamed button wins.
    heard = checkout_heard(Announcement("link", "Pay now, $18.00"), Announcement("button", "Place order, $18.00"))
    result = broken_at(PAY, heard)
    proposal = b1(journey, result)
    assert proposal.route == "still_usable"
    assert (proposal.replace_from, proposal.replace_to, proposal.steps) == (PAY, PAY + 1, (PLACE_ORDER,))
    patched = apply_path(journey, proposal)
    assert patched.steps == journey.steps[:PAY] + (PLACE_ORDER,) + journey.steps[PAY + 1:]
    assert reparse(proposal, journey, result) == proposal


def test_b1_takes_the_closest_name_when_several_are_close(journey):
    heard = checkout_heard(Announcement("button", "Place order, $18.00"),
                           Announcement("button", "Pay now, $18.00 total"))
    assert b1(journey, broken_at(PAY, heard)).steps[0].name == "Pay now, $18.00 total"


def test_b1_reports_the_missing_control_when_no_name_is_close(journey):
    result = broken_at(PAY, checkout_heard(Announcement("button", "Continue to review")))
    proposal = b1(journey, result)
    assert (proposal.route, proposal.problem, proposal.wcag) == ("barrier", NOT_FOUND, "")
    assert proposal.control == "Pay now, $18.00, button"
    assert reparse(proposal, journey, result) == proposal


@pytest.mark.parametrize("failed, verdict", [(2, "broken"), (15, "no_order")])
def test_b1_does_not_guess_a_path_when_the_walk_did_not_break_at_a_find(journey, failed, verdict):
    # Step 2 listens for a heading. Step 15 is the final check, which no path may replace.
    proposal = b1(journey, broken_at(failed, checkout_heard(Announcement("button", "Pay now, $18.00")), verdict))
    assert (proposal.route, proposal.problem, proposal.wcag) == ("barrier", NOT_FOUND, "")
    assert proposal.steps == ()


@pytest.mark.parametrize("failed, limits", [
    (2, {}),  # a heading broke: there is no control to swap
    (15, {}),  # the final check: no path may replace it
    (PAY, {"max_replays": 0}),
    (PAY, {"max_seconds": 0}),
])
def test_b2_opens_no_walk_without_a_find_to_replace_or_without_budget(journey, failed, limits):
    result = broken_at(failed, checkout_heard(Announcement("button", "Place order, $18.00"), Announcement("button")))
    assert find_named_path(NoBrowser(), journey, result, "dev-rename", **limits) == (None, 0)
    proposal = b2(NoBrowser(), journey, result, "dev-rename", **limits)
    assert (proposal.source, proposal.route, proposal.control, proposal.wcag) == ("B2", "barrier", "button", "4.1.2")


def test_b2_without_a_path_or_an_unnamed_control_says_no_path_was_found(journey):
    result = broken_at(PAY, checkout_heard(Announcement("button", "Continue to review")))
    proposal = b2(NoBrowser(), journey, result, None, max_replays=0)
    assert (proposal.route, proposal.problem, proposal.wcag) == ("barrier", NO_PATH, "")
    assert proposal.control == "Pay now, $18.00, button"
    assert reparse(proposal, journey, result) == proposal


# Real walks from here on.


def walk_once(walker, journey, variant=None) -> Result:
    walk = walker.open(variant)
    try:
        return replay(walk, journey)
    finally:
        walk.close()


def placed(result: Result) -> list[tuple[str, int]]:
    return [(order["item"], order["quantity"]) for order in result.orders]


class Watched:
    """Wraps the walker: counts walks, checks each one is closed, and keeps every order they placed."""

    def __init__(self, walker):
        self.walker, self.opened, self.closed, self.orders = walker, 0, 0, []

    def open(self, variant=None, session=None):
        walk = self.walker.open(variant, session)
        self.opened += 1
        close = walk.close

        def close_and_count():
            self.orders.extend(walk.orders())
            self.closed += 1
            close()

        walk.close = close_and_count
        return walk


@pytest.fixture(scope="module")
def served_variants(served_variants):
    """The shared variants plus t-b2-review, written only into this module's temporary copy."""
    templates = served_variants / "t-b2-review" / "templates"
    templates.mkdir(parents=True)
    (templates / "checkout.html").write_text(REVIEW_CHECKOUT, encoding="utf-8")
    (templates / "review.html").write_text(REVIEW_PAGE, encoding="utf-8")
    return served_variants


@pytest.fixture(scope="module")
def broken(walker, journey):
    """The recorded journey replayed once per variant, as the bench does before asking anyone."""
    results: dict[str, Result] = {}

    def get(variant: str) -> Result:
        if variant not in results:
            results[variant] = walk_once(walker, journey, variant)
        result = results[variant]
        assert (result.verdict, result.failed_step) == ("broken", PAY), result.reason
        return result

    return get


@pytest.mark.browser
def test_both_baselines_follow_the_renamed_pay_button_and_the_path_places_the_order(walker, journey, broken):
    result = broken("dev-rename")
    first, second = b1(journey, result), b2(walker, journey, result, "dev-rename")
    assert first.route == second.route == "still_usable"
    assert first.steps == second.steps == (PLACE_ORDER,)
    assert (first.replace_from, first.replace_to) == (second.replace_from, second.replace_to) == (PAY, PAY + 1)
    assert reparse(second, journey, result) == second
    replayed = walk_once(walker, apply_path(journey, second), "dev-rename")
    assert replayed.verdict == "clear", replayed.reason
    assert placed(replayed) == [("ethiopia", 1)]


@pytest.mark.browser
def test_both_baselines_call_unnamed_icon_buttons_a_barrier_and_b2_accepts_no_path(walker, journey, broken):
    result = broken("dev-icons")
    first = b1(journey, result)
    assert (first.route, first.control, first.wcag) == ("barrier", "button", "4.1.2")
    watched = Watched(walker)
    second = b2(watched, journey, result, "dev-icons")
    assert (second.route, second.control, second.wcag) == ("barrier", "button", "4.1.2")
    assert 1 < watched.opened <= 40 and watched.closed == watched.opened
    assert f"{watched.opened} replay(s)" in second.why
    # No walk in the search placed an order, so it never reached the unnamed submit button
    # some other way (see the next test).
    assert watched.orders == []


@pytest.mark.browser
def test_enter_in_a_named_field_submits_through_the_unnamed_button(walker, journey):
    """Why B2 presses Enter only on buttons and links: this path places the order on dev-icons,
    yet the person never hears what they pressed. Replay alone would call it clear."""
    steps = list(journey.steps)
    steps[PAY] = Step(do="find", role="textbox", name="Card number")
    result = walk_once(walker, journey.with_steps(steps), "dev-icons")
    assert result.verdict == "clear" and placed(result) == [("ethiopia", 1)]


@pytest.mark.browser
def test_b2_stops_at_max_replays(walker, journey, broken):
    watched = Watched(walker)
    assert find_named_path(watched, journey, broken("dev-icons"), "dev-icons", max_replays=1) == (None, 1)
    assert watched.opened == watched.closed == 1


@pytest.mark.browser
def test_b2_finds_the_path_through_an_added_review_page_where_b1_gives_up(walker, journey, broken):
    result = broken("t-b2-review")
    assert b1(journey, result).problem == NOT_FOUND
    watched = Watched(walker)
    proposal = b2(watched, journey, result, "t-b2-review")
    assert proposal.route == "still_usable", proposal.why
    assert proposal.steps == (Step(do="find", role="button", name="Continue to review"),
                              Step(do="press", key="Enter"), PLACE_ORDER)
    assert (proposal.replace_from, proposal.replace_to) == (PAY, PAY + 1)
    assert watched.closed == watched.opened <= 40
    assert len(watched.orders) == 1  # only the accepted replay placed an order
    replayed = walk_once(walker, apply_path(journey, proposal), "t-b2-review")
    assert replayed.verdict == "clear", replayed.reason
    assert placed(replayed) == [("ethiopia", 1)]
