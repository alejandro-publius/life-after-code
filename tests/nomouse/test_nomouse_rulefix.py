"""F0, the no-model rule fixer: pure tests on small templates, then real walks in Chromium.

Each barrier is the shop's own base template with one small change. The pure tests check what
every fix must keep, read with Python's own HTML parser rather than F0's: the find occurs
exactly once, $placeholders survive, and no visible word is lost. The browser tests replay the
recorded journey on the broken variant, apply F0's fix with fix.apply_fix as a new variant, and
replay again: only a clear walk that places one order counts.
"""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re

import pytest

from nomouse.announce import Announcement
from nomouse.bench import page_templates
from nomouse.fix import apply_fix
from nomouse.journey import Result, Step, replay
from nomouse.rulefix import MAX_SOURCE_CHARS, propose_fix

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "nomouse" / "shop" / "templates"
TEST_VARIANTS = REPO / "tests" / "nomouse" / "fixtures" / "variants"
PATH = "nomouse/variants/v-test/templates/checkout.html"
PLACEHOLDER = re.compile(r"\$\{?[_a-zA-Z][_a-zA-Z0-9]*\}?")

# Journey step numbers (nomouse/journeys/checkout.yml).
ADD_TO_CART, YOUR_CART, CHECKOUT, CHECKOUT_HEADING, EMAIL, CARD, PAY, ORDER_PLACED = 3, 5, 6, 8, 9, 11, 13, 15

PAY_BUTTON = '<button type="submit">Pay now, $price</button>'
CHECKOUT_LINK = '<a href="/checkout">Checkout</a>'
ADD_BUTTON = '<button type="submit">Add to cart</button>'
SVG = '<svg width="20" height="20" aria-hidden="true"><rect x="4" y="9" width="12" height="9"/></svg>'


def base(page: str) -> str:
    return (BASE / page).read_text(encoding="utf-8")


def changed(page: str, *swaps: tuple[str, str]) -> str:
    """A base template with exact replacements, each of which must find its text."""
    text = base(page)
    for old, new in swaps:
        assert old in text, old
        text = text.replace(old, new, 1)
    return text


# The barriers. Each is a real barrier for a keyboard and screen reader user.
CLICK_DIV = changed("checkout.html", (PAY_BUTTON, '<div class="pay" id="pay" data-price="$price" role="presentation" '
                                                  'tabindex="0" onclick="this.closest(\'form\').submit()">'
                                                  'Pay now, $price</div>'))
NAV_SPAN = changed("cart.html", (CHECKOUT_LINK, '<span class="go" onclick="location.href=\'/checkout\'">'
                                                'Checkout</span>'))
ROLE_LINK = changed("cart.html", (CHECKOUT_LINK, '<span role="link" onclick="window.location = \'/checkout\'">'
                                                 'Checkout</span>'))
FAKE_BUTTON = changed("product.html", (ADD_BUTTON, '<span class="btn" role="button" tabindex="0" '
                                                   'onclick="this.closest(\'form\').submit()">Add to cart</span>'))
KEYBOARD_READY = changed("product.html", (ADD_BUTTON, '<span role="button" tabindex="0" '
                                                      'onclick="this.closest(\'form\').submit()" '
                                                      'onkeydown="if (event.key === \'Enter\') this.click()">'
                                                      'Add to cart</span>'))
ICON_DIV = changed("checkout.html", (PAY_BUTTON, '<div class="pay" onclick="this.closest(\'form\').submit()">'
                                                 f"{SVG}</div>"))
ICONS = changed("checkout.html", (PAY_BUTTON, (
    '<div class="icon-row">\n'
    '<button type="button" onclick="history.back()"><svg aria-hidden="true"><path d="M1 1h9"/></svg></button>\n'
    f'<button type="submit">{SVG}</button>\n'
    '<button type="button" onclick="document.getElementById(\'help\').hidden = false">'
    '<svg aria-hidden="true"><circle cx="5" cy="5" r="4"/></svg></button>\n'
    '</div>')))
ICON_LINKS = changed("cart.html",
                     ("<h1>Your cart</h1>", '<h1>Your cart</h1>\n<p><a href="/help">' + SVG + "</a></p>"),
                     (CHECKOUT_LINK, f'<a href="/checkout" class="icon">{SVG}</a>'),
                     ('<a href="/">Keep shopping</a>', f'<a href="/">{SVG}</a>'))
JUNK_ALT = changed("checkout.html", (PAY_BUTTON, '<button type="submit"><img src="/static/lock.png" alt="lock.png">'
                                                 "</button>"))
JUNK_ALT_WITH_TEXT = changed("checkout.html", (PAY_BUTTON, '<button type="submit"><img src="/static/lock.png" '
                                                           'alt="lock.png"> Pay now, $price</button>'))
JUNK_LABEL = changed("checkout.html", (PAY_BUTTON, f'<button type="submit" aria-label="btn_pay">{SVG}</button>'))
LABELLEDBY = changed("checkout.html", (PAY_BUTTON, '<button type="submit" aria-labelledby="later">Pay now, $price'
                                                   '</button>\n<span id="later" hidden>Save for later</span>'))
SWAPPED = changed("checkout.html", ('<label for="email">Email</label>', '<label for="card">Email</label>'),
                  ('<label for="card">Card number</label>', '<label for="email">Card number</label>'))
LABEL_TYPO = changed("checkout.html", ('<label for="email">Email</label>', '<label for="card">Email</label>'))
TEXT_BEFORE = changed("checkout.html", ('<label for="email">Email</label>', '<span class="field-name">Email</span>'))
NO_LABEL = changed("checkout.html", ('<label for="card">Card number</label>\n', ""))
NO_LABELS = changed("checkout.html", ('<label for="email">Email</label>\n', ""),
                    ('<label for="card">Card number</label>\n', ""))
TABINDEX = changed("checkout.html", (PAY_BUTTON, '<button type="submit" tabindex="-1">Pay now, $price</button>'))
LINK_AS_BUTTON = changed("checkout.html", (PAY_BUTTON, '<a href="#" onclick="this.closest(\'form\').submit(); '
                                                       'return false;">Pay now, $price</a>'))
DIV_HEADING = changed("checkout.html", ("<h1>Checkout</h1>", '<div class="title">Checkout</div>'))
HIDDEN_HEADING = changed("checkout.html", ("<h1>Checkout</h1>", '<h1 aria-hidden="true">Checkout</h1>'))
TRAP = changed("checkout.html", ("<h1>Checkout</h1>", (
    "<h1>Checkout</h1>\n"
    '<div role="dialog" aria-modal="true" aria-labelledby="offer-title" id="offer">\n'
    '<h2 id="offer-title">Join our newsletter</h2>\n'
    "<p>Get 10 percent off your first bag.</p>\n"
    '<input id="news" type="email" aria-label="Newsletter email">\n'
    '<button type="button" onclick="join()">Join</button>\n'
    "</div>\n"
    "<script>\n"
    "document.getElementById('offer').addEventListener('keydown', function (event) {\n"
    "  if (event.key === 'Tab') { event.preventDefault(); this.querySelector('input').focus(); }\n"
    "});\n"
    "</script>")))


class _Reader(HTMLParser):
    """Python's own HTML parser: the text a person sees and every start tag, independent of F0."""

    def __init__(self) -> None:
        super().__init__()
        self.words: list[str] = []
        self.tags: list[tuple[str, dict[str, str]]] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, {key: value or "" for key, value in attrs}))
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.words.extend(data.split())


def read(source: str) -> _Reader:
    reader = _Reader()
    reader.feed(source)
    reader.close()
    return reader


def occurrences(text: str, sub: str) -> int:
    count, start = 0, text.find(sub)
    while start >= 0:
        count += 1
        start = text.find(sub, start + 1)
    return count


def check(source: str, fix, path: str = PATH) -> str:
    """Apply the fix as fix.apply_fix does and check what every fix must keep."""
    assert fix is not None
    assert fix.file == path
    assert occurrences(source, fix.find) == 1
    after = source.replace(fix.find, fix.replace, 1)
    assert Counter(PLACEHOLDER.findall(after)) == Counter(PLACEHOLDER.findall(source))
    assert not Counter(read(source).words) - Counter(read(after).words), "visible text was removed"
    assert not {chr(0x2013), chr(0x2014)} & set(fix.replace)  # no en or em dashes
    return after


def heard(*pairs: tuple[str, str], visible: dict[str, str] | None = None) -> list[Announcement]:
    visible = visible or {}
    return [Announcement(role=role, name=name, visible=visible.get(name, "")) for role, name in pairs]


CHECKOUT_HEARD = (("link", "Demo Beans home"), ("link", "Cart, 1 item"), ("textbox", "Email"),
                  ("textbox", "Card number"), ("combobox", "Delivery"))


def broken(step: int, *pairs: tuple[str, str], page: str = "/checkout", verdict: str = "broken",
           visible: dict[str, str] | None = None) -> Result:
    return Result(verdict=verdict, failed_step=step, reason="test", heard=heard(*pairs, visible=visible), page=page)


def tag_with(source: str, tag: str, **attrs: str) -> list[dict[str, str]]:
    return [found for name, found in read(source).tags
            if name == tag and all(found.get(key.replace("_", "-")) == value for key, value in attrs.items())]


# Rules 1 and 2: controls that Tab or Enter cannot use.

def test_rule1_a_click_only_div_that_submits_becomes_a_submit_button(journey):
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD), PATH, CLICK_DIV)
    after = check(CLICK_DIV, fix)
    assert why.startswith("rule 1:")
    assert "<button" in fix.replace and "</button>" in fix.replace and "<div" not in fix.replace
    button = tag_with(after, "button", type="submit")
    assert len(button) == 1
    assert button[0]["id"] == "pay" and button[0]["class"] == "pay" and button[0]["data-price"] == "$price"
    assert button[0]["onclick"] == "this.closest('form').submit()"
    assert "role" not in button[0] and "tabindex" not in button[0]


def test_rule1_a_click_only_span_that_navigates_becomes_a_link_when_a_link_is_expected(journey):
    fix, why = propose_fix(journey, broken(CHECKOUT, ("link", "Keep shopping"), page="/cart"), PATH, NAV_SPAN)
    after = check(NAV_SPAN, fix)
    assert why.startswith("rule 1:")
    assert tag_with(after, "a", href="/checkout", **{"class": "go"})


def test_rule1_a_click_only_control_that_does_not_submit_gets_type_button(journey):
    help_span = '\n<span class="help" onclick="openHelp()">Help</span>'
    source = changed("checkout.html", (PAY_BUTTON, PAY_BUTTON + help_span))
    source = source.replace('<form method="post" action="/pay" class="card">', '<div class="card">').replace(
        "</form>", "</div>")
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD), PATH, source)
    after = check(source, fix)
    assert why.startswith("rule 1:") and why.endswith("not matched to the control the walk expected")
    assert tag_with(after, "button", type="button", onclick="openHelp()")


def test_rule2_a_span_with_role_link_and_only_onclick_becomes_a_real_link(journey):
    fix, why = propose_fix(journey, broken(CHECKOUT, ("link", "Keep shopping"), page="/cart"), PATH, ROLE_LINK)
    after = check(ROLE_LINK, fix)
    assert why.startswith("rule 2:") and "Tab never reaches" in why
    link = tag_with(after, "a", href="/checkout")
    assert len(link) == 1 and "role" not in link[0]


def test_rule2_a_fake_button_that_enter_cannot_press_becomes_a_submit_button(journey):
    """Tab reaches the span and its name is right, but Enter does nothing, so the next heading never comes."""
    result = broken(YOUR_CART, ("link", "Demo Beans home"), ("button", "Add to cart"), page="/product/ethiopia")
    fix, why = propose_fix(journey, result, PATH, FAKE_BUTTON)
    after = check(FAKE_BUTTON, fix)
    assert why.startswith("rule 2:") and "Enter does not operate" in why
    button = tag_with(after, "button", type="submit", **{"class": "btn"})
    assert len(button) == 1 and "role" not in button[0] and "tabindex" not in button[0]


def test_rule2_a_fake_button_that_tab_and_enter_already_operate_is_left_alone(journey):
    result = broken(YOUR_CART, ("link", "Demo Beans home"), ("button", "Add to cart"), page="/product/ethiopia")
    fix, why = propose_fix(journey, result, PATH, KEYBOARD_READY)
    assert fix is None and why.startswith("no rule applies")


def test_rule2_extra_a_control_taken_out_of_the_tab_order_gets_back_in(journey):
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD), PATH, TABINDEX)
    after = check(TABINDEX, fix)
    assert "tabindex" in why and fix.replace == '<button type="submit">'
    assert after == base("checkout.html")


def test_rule2_extra_a_link_used_as_a_button_becomes_a_button(journey):
    result = broken(PAY, *CHECKOUT_HEARD, ("link", "Pay now, $18.00"))
    fix, why = propose_fix(journey, result, PATH, LINK_AS_BUTTON)
    after = check(LINK_AS_BUTTON, fix)
    assert why.startswith("rule 2 (extra): a link was used as a button")
    button = tag_with(after, "button", type="submit")
    assert len(button) == 1 and "href" not in button[0]


# Rules 3, 4 and 6: unnamed controls and names that say nothing.

def test_rule3_picks_the_submit_button_among_three_unnamed_icon_buttons(journey):
    result = broken(PAY, *CHECKOUT_HEARD, ("button", ""), ("button", ""), ("button", ""))
    fix, why = propose_fix(journey, result, PATH, ICONS)
    after = check(ICONS, fix)
    assert why.startswith("rule 3:") and "submit button" in why and "1 of 3" in why
    named = tag_with(after, "button", aria_label="Pay now, $18.00")
    assert len(named) == 1 and named[0]["type"] == "submit"
    assert len(tag_with(after, "button", type="button")) == 2  # the other two are untouched


def test_rule3_takes_the_first_unnamed_button_when_the_control_does_not_submit(journey):
    steps = list(journey.steps)
    steps[PAY + 1] = Step(do="press", key="Space")
    result = broken(PAY, *CHECKOUT_HEARD, ("button", ""), ("button", ""), ("button", ""))
    fix, _ = propose_fix(journey.with_steps(steps), result, PATH, ICONS)
    after = check(ICONS, fix)
    assert tag_with(after, "button", aria_label="Pay now, $18.00", onclick="history.back()")


def test_rule3_the_dev_icons_variant_gets_its_submit_button_named(journey):
    source = (REPO / "nomouse/variants/dev-icons/templates/checkout.html").read_text(encoding="utf-8")
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD), PATH, source)
    after = check(source, fix)
    assert why.startswith("rule 3:")
    assert tag_with(after, "button", type="submit", aria_label="Pay now, $18.00")


def test_rule3_picks_the_unnamed_link_whose_address_matches_the_expected_name(journey):
    result = broken(CHECKOUT, ("link", ""), ("link", ""), ("link", ""), page="/cart")
    fix, why = propose_fix(journey, result, PATH, ICON_LINKS)
    after = check(ICON_LINKS, fix)
    assert why.startswith("rule 3:") and "1 of 3" in why
    assert tag_with(after, "a", href="/checkout", aria_label="Checkout")
    assert len(tag_with(after, "a", aria_label="Checkout")) == 1


def test_rule3_never_names_a_control_of_another_role(journey):
    """The walk expected the Email field; an unnamed icon button must not be called "Email"."""
    source = changed("checkout.html", ('<label for="email">Email</label>\n', ""), (PAY_BUTTON, PAY_BUTTON + SVG.join(
        ['\n<button type="button">', "</button>"])))
    fix, why = propose_fix(journey, broken(EMAIL, ("textbox", ""), ("textbox", "Card number")), PATH, source)
    after = check(source, fix)
    assert why.startswith("rule 8:")
    assert tag_with(after, "input", id="email", aria_label="Email")
    assert not tag_with(after, "button", aria_label="Email")


def test_rules_1_and_3_an_unnamed_click_only_icon_becomes_a_named_submit_button(journey):
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD), PATH, ICON_DIV)
    after = check(ICON_DIV, fix)
    assert why.startswith("rules 1 and 3:")
    assert tag_with(after, "button", type="submit", aria_label="Pay now, $18.00", **{"class": "pay"})


def test_rule4_a_file_name_alt_gets_the_expected_name(journey):
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD, ("button", "lock.png")), PATH, JUNK_ALT)
    after = check(JUNK_ALT, fix)
    assert why.startswith("rule 4:")
    assert tag_with(after, "img", src="/static/lock.png", alt="Pay now, $18.00")


def test_rule4_a_file_name_alt_next_to_visible_text_becomes_empty(journey):
    result = broken(PAY, *CHECKOUT_HEARD, ("button", "lock.png Pay now, $18.00"))
    fix, why = propose_fix(journey, result, PATH, JUNK_ALT_WITH_TEXT)
    after = check(JUNK_ALT_WITH_TEXT, fix)
    assert why.startswith("rule 4:")
    assert tag_with(after, "img", src="/static/lock.png", alt="")


def test_rule6_a_junk_aria_label_on_an_icon_button_gets_the_expected_name(journey):
    fix, why = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD, ("button", "btn_pay")), PATH, JUNK_LABEL)
    after = check(JUNK_LABEL, fix)
    assert why.startswith("rule 6:")
    assert tag_with(after, "button", type="submit", aria_label="Pay now, $18.00")
    assert "btn_pay" not in after


def test_an_expected_name_with_quotes_and_ampersands_survives_as_an_attribute(journey):
    steps = list(journey.steps)
    steps[PAY] = Step(do="find", role="button", name='Pay & go "now"')
    fix, _ = propose_fix(journey.with_steps(steps), broken(PAY, *CHECKOUT_HEARD), PATH, JUNK_LABEL)
    after = check(JUNK_LABEL, fix)
    assert tag_with(after, "button", aria_label='Pay & go "now"')


# Rule 5: a spoken name that leaves out the visible label, or says nothing.

@pytest.mark.parametrize("variant, label", [("t-junk", "icon-lock"), ("t-mismatch", "Save for later")])
def test_rule5_an_aria_label_that_hides_the_visible_label_is_removed(journey, variant, label):
    source = (TEST_VARIANTS / variant / "templates" / "checkout.html").read_text(encoding="utf-8")
    result = broken(PAY, *CHECKOUT_HEARD, ("button", label), visible={label: "Pay now, $18.00"})
    fix, why = propose_fix(journey, result, PATH, source)
    after = check(source, fix)
    assert why.startswith("rule 5:") and label in why
    assert fix.replace == '<button type="submit">'
    assert after == base("checkout.html")


def test_rule5_an_aria_labelledby_that_hides_the_visible_label_is_removed(journey):
    result = broken(PAY, *CHECKOUT_HEARD, ("button", "Save for later"), visible={"Save for later": "Pay now, $18.00"})
    fix, why = propose_fix(journey, result, PATH, LABELLEDBY)
    after = check(LABELLEDBY, fix)
    assert why.startswith("rule 5:") and "aria-labelledby" in why
    assert tag_with(after, "button", type="submit") == [{"type": "submit"}]


def test_rule5_keeps_an_aria_label_that_contains_the_visible_label(journey):
    longer = '<button type="submit" aria-label="Pay now, $price, secure checkout">Pay now, $price</button>'
    source = changed("checkout.html", (PAY_BUTTON, longer))
    result = broken(PAY, *CHECKOUT_HEARD, ("button", "Pay now, $18.00, secure checkout"))
    fix, why = propose_fix(journey, result, PATH, source)
    assert fix is None and why.startswith("no rule applies")


# Rules 7 and 8: field labels.

def test_rule7_fixes_swapped_labels_in_one_span(journey):
    result = broken(EMAIL, ("textbox", "Card number"), ("textbox", "Email"))
    fix, why = propose_fix(journey, result, PATH, SWAPPED)
    after = check(SWAPPED, fix)
    assert why.startswith("rule 7:") and '"Email"' in why and '"Card number"' in why
    assert fix.find.startswith('<label for="card">Email</label>') and fix.find.endswith('<label for="email">')
    assert after == base("checkout.html")


def test_rule7_is_tied_to_a_walk_that_typed_into_the_wrong_field(journey):
    """With swapped labels the walk types the card number into the email field, so the form never
    submits; the field is heard as an invalid entry, which ties the labels to the failure."""
    invalid = Announcement(role="textbox", name="Card number", value="1111 2222 3333 4444",
                           states=("required", "invalid entry"))
    result = Result(verdict="broken", failed_step=ORDER_PLACED, reason="test", page="/checkout",
                    heard=[invalid, Announcement(role="textbox", name="Email"), Announcement(role="button",
                                                                                           name="Pay now, $18.00")])
    fix, why = propose_fix(journey, result, PATH, SWAPPED)
    assert why.startswith("rule 7:") and "not matched" not in why
    assert check(SWAPPED, fix) == base("checkout.html")


def test_rule7_fixes_a_label_that_points_at_the_wrong_field(journey):
    result = broken(EMAIL, ("textbox", ""), ("textbox", "Email Card number"))
    fix, why = propose_fix(journey, result, PATH, LABEL_TYPO)
    assert why.startswith("rule 7:")
    assert check(LABEL_TYPO, fix) == base("checkout.html")


def test_rule8_plain_text_before_an_unlabelled_field_becomes_its_label(journey):
    fix, why = propose_fix(journey, broken(EMAIL, ("textbox", ""), ("textbox", "Card number")), PATH, TEXT_BEFORE)
    after = check(TEXT_BEFORE, fix)
    assert why.startswith("rule 8:") and "label" in why
    assert fix.replace == '<label for="email" class="field-name">Email</label>'
    assert tag_with(after, "input", id="email") == tag_with(base("checkout.html"), "input", id="email")


def test_rule8_an_unlabelled_field_with_no_text_before_it_gets_an_aria_label(journey):
    fix, why = propose_fix(journey, broken(CARD, ("textbox", "Email"), ("textbox", "")), PATH, NO_LABEL)
    after = check(NO_LABEL, fix)
    assert why.startswith("rule 8:")
    assert tag_with(after, "input", id="card", aria_label="Card number")


def test_rule8_picks_the_unlabelled_field_whose_attributes_match_the_expected_name(journey):
    fix, why = propose_fix(journey, broken(CARD, ("textbox", ""), ("textbox", "")), PATH, NO_LABELS)
    after = check(NO_LABELS, fix)
    assert "1 of 2" in why
    assert tag_with(after, "input", id="card", aria_label="Card number")
    assert not tag_with(after, "input", id="email", aria_label="Card number")


# Rule 10 (extra): the heading the walk expected is on the page but not announced as one.

def test_rule10_text_that_only_looks_like_the_expected_heading_becomes_a_heading(journey):
    fix, why = propose_fix(journey, broken(CHECKOUT_HEADING, *CHECKOUT_HEARD), PATH, DIV_HEADING)
    after = check(DIV_HEADING, fix)
    assert why.startswith("rule 10 (extra):")
    assert fix.replace == '<h1 class="title">Checkout</h1>'
    assert tag_with(after, "h1", **{"class": "title"})


def test_rule10_a_heading_hidden_by_aria_hidden_is_shown_again(journey):
    fix, why = propose_fix(journey, broken(CHECKOUT_HEADING, *CHECKOUT_HEARD), PATH, HIDDEN_HEADING)
    assert why.startswith("rule 10 (extra):") and "aria-hidden" in why
    assert check(HIDDEN_HEADING, fix) == base("checkout.html")


def test_rule10_does_not_invent_a_heading_that_is_not_on_the_page(journey):
    source = changed("checkout.html", ("<h1>Checkout</h1>", "<h1>Payment details</h1>"))
    fix, why = propose_fix(journey, broken(CHECKOUT_HEADING, *CHECKOUT_HEARD), PATH, source)
    assert fix is None and 'the heading "Checkout"' in why


# Rule 9 and the cases where nothing should fire.

def test_rule9_a_dialog_that_traps_focus_gets_no_fix(journey):
    result = broken(PAY, ("textbox", "Newsletter email"), ("button", "Join"))
    fix, why = propose_fix(journey, result, PATH, TRAP)
    assert fix is None
    assert why.startswith("no rule applies:") and '"Pay now, $18.00, button"' in why


@pytest.mark.parametrize("page, step, path", [("checkout.html", PAY, "/checkout"),
                                              ("checkout.html", EMAIL, "/checkout"),
                                              ("cart.html", CHECKOUT, "/cart"),
                                              ("product.html", ADD_TO_CART, "/product/ethiopia"),
                                              ("home.html", 0, "/")])
def test_nothing_fires_on_the_clean_base_templates(journey, page, step, path):
    fix, why = propose_fix(journey, broken(step, page=path), f"nomouse/shop/templates/{page}", base(page))
    assert fix is None and why.startswith("no rule applies")


def test_a_harmless_rename_is_not_fixed(journey):
    source = (REPO / "nomouse/variants/dev-rename/templates/checkout.html").read_text(encoding="utf-8")
    fix, _ = propose_fix(journey, broken(PAY, *CHECKOUT_HEARD, ("button", "Place order, $18.00")), PATH, source)
    assert fix is None


def test_a_walk_that_did_not_break_or_an_oversized_template_gets_no_fix(journey):
    assert propose_fix(journey, Result(verdict="clear"), PATH, ICONS)[0] is None
    huge = ICONS + " " * MAX_SOURCE_CHARS
    fix, why = propose_fix(journey, broken(PAY), PATH, huge)
    assert fix is None and "longer than" in why


# Properties every fix keeps.

def test_the_find_grows_until_it_occurs_once_when_the_tag_repeats(journey):
    coupon = ('<form method="post" action="/coupon">\n<input id="code" name="code" aria-label="Coupon code">\n'
              f'<button type="submit">{SVG}</button>\n</form>\n')
    source = changed("checkout.html", ("<h1>Checkout</h1>\n", "<h1>Checkout</h1>\n" + coupon),
                     (PAY_BUTTON, f'<button type="submit">{SVG}</button>'))
    assert occurrences(source, f'<button type="submit">{SVG}</button>') == 2
    result = broken(PAY, ("textbox", "Coupon code"), ("button", ""), *CHECKOUT_HEARD, ("button", ""))
    fix, why = propose_fix(journey, result, PATH, source)
    after = check(source, fix)
    assert why.startswith("rule 3:")
    forms = after.split("</form>")
    assert 'aria-label="Pay now, $18.00"' in forms[1] and "aria-label=\"Pay" not in forms[0]


@pytest.mark.parametrize("source", [
    "<div onclick=\"go()\">Pay now, $price", "<p>Text</span></div><button type=submit><svg></button>",
    "<!-- open comment <button>", "<label for=a>Email</label><input id=b><input id=a",
    "<a href=/checkout><img alt=cart.png></a></a></p>", "<button aria-label='x'>Pay now, $price</button",
    "<script>if (a < b) document.write('<div onclick=x()>Pay</div>')</script>", "",
])
@pytest.mark.parametrize("step", [CHECKOUT, EMAIL, PAY, ORDER_PLACED])
def test_malformed_templates_never_crash_and_any_fix_still_occurs_once(journey, source, step):
    fix, why = propose_fix(journey, broken(step, ("button", ""), ("link", "")), PATH, source)
    assert why
    if fix is not None:
        assert occurrences(source, fix.find) == 1 and fix.file == PATH


def test_the_same_input_always_gives_the_same_fix(journey):
    result = broken(PAY, *CHECKOUT_HEARD, ("button", ""), ("button", ""), ("button", ""))
    assert propose_fix(journey, result, PATH, ICONS) == propose_fix(journey, result, PATH, ICONS)


@pytest.mark.parametrize("source, step, page", [
    (CLICK_DIV, PAY, "checkout.html"), (ICONS, PAY, "checkout.html"), (SWAPPED, EMAIL, "checkout.html"),
    (TEXT_BEFORE, EMAIL, "checkout.html"), (ROLE_LINK, CHECKOUT, "cart.html"),
])
def test_fix_apply_accepts_every_fix_as_a_new_variant(tmp_path, journey, source, step, page):
    (tmp_path / "v-test" / "templates").mkdir(parents=True)
    (tmp_path / "v-test" / "templates" / page).write_text(source, encoding="utf-8")
    path = f"nomouse/variants/v-test/templates/{page}"
    fix, _ = propose_fix(journey, broken(step, page="/"), path, source)
    name = apply_fix(tmp_path, "v-test", fix, REPO)
    assert (tmp_path / name / "templates" / page).read_text(encoding="utf-8") == check(source, fix, path)


# Real walks: replay, fix with F0, replay again.

BROWSER_VARIANTS = {
    "f0-click-div": ("checkout.html", CLICK_DIV),
    "f0-icon-div": ("checkout.html", ICON_DIV),
    "f0-span-link": ("cart.html", NAV_SPAN),
    "f0-role-link": ("cart.html", ROLE_LINK),
    "f0-fake-button": ("product.html", FAKE_BUTTON),
    "f0-tabindex": ("checkout.html", TABINDEX),
    "f0-link-as-button": ("checkout.html", LINK_AS_BUTTON),
    "f0-icon-buttons": ("checkout.html", ICONS),
    "f0-icon-links": ("cart.html", ICON_LINKS),
    "f0-junk-alt": ("checkout.html", JUNK_ALT),
    "f0-junk-label": ("checkout.html", JUNK_LABEL),
    "f0-labelledby": ("checkout.html", LABELLEDBY),
    "f0-label-typo": ("checkout.html", LABEL_TYPO),
    "f0-text-label": ("checkout.html", TEXT_BEFORE),
    "f0-no-label": ("checkout.html", NO_LABEL),
    "f0-swapped": ("checkout.html", SWAPPED),
    "f0-div-heading": ("checkout.html", DIV_HEADING),
    "f0-hidden-heading": ("checkout.html", HIDDEN_HEADING),
}


@pytest.fixture(scope="module")
def variants(served_variants: Path) -> Path:
    """The served variants plus this module's barriers, written next to them."""
    for name, (page, text) in BROWSER_VARIANTS.items():
        folder = served_variants / name / "templates"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / page).write_text(text, encoding="utf-8")
    return served_variants


def walk_once(walker, journey, variant):
    walk = walker.open(variant)
    try:
        return replay(walk, journey)
    finally:
        walk.close()


@pytest.mark.browser
@pytest.mark.parametrize("variant, failed_step, rule", [
    ("dev-icons", PAY, "rule 3:"),
    ("t-junk", PAY, "rule 5:"),
    ("t-mismatch", PAY, "rule 5:"),
    ("f0-click-div", PAY, "rule 1:"),
    ("f0-icon-div", PAY, "rules 1 and 3:"),
    ("f0-span-link", CHECKOUT, "rule 1:"),
    ("f0-role-link", CHECKOUT, "rule 2:"),
    ("f0-fake-button", YOUR_CART, "rule 2:"),
    ("f0-tabindex", PAY, "rule 2 (extra):"),
    ("f0-link-as-button", PAY, "rule 2 (extra):"),
    ("f0-icon-buttons", PAY, "rule 3:"),
    ("f0-icon-links", CHECKOUT, "rule 3:"),
    ("f0-junk-alt", PAY, "rule 4:"),
    ("f0-junk-label", PAY, "rule 6:"),
    ("f0-labelledby", PAY, "rule 5:"),
    ("f0-label-typo", EMAIL, "rule 7:"),
    ("f0-swapped", ORDER_PLACED, "rule 7:"),
    ("f0-div-heading", CHECKOUT_HEADING, "rule 10 (extra):"),
    ("f0-hidden-heading", CHECKOUT_HEADING, "rule 10 (extra):"),
    ("f0-text-label", EMAIL, "rule 8:"),
    ("f0-no-label", CARD, "rule 8:"),
])
def test_the_f0_fix_clears_the_recorded_walk(walker, shop_url, journey, variants, variant, failed_step, rule):
    before = walk_once(walker, journey, variant)
    assert before.verdict == "broken" and before.failed_step == failed_step, before.reason
    files, source = page_templates(variants, variant, before.page, REPO)
    fix, why = propose_fix(journey, before, files[0], source)
    assert fix is not None, why
    assert why.startswith(rule), why
    fixed = apply_fix(variants, variant, fix, REPO)
    after = walk_once(walker, journey, fixed)
    assert after.clear, f"{why} -> {after.verdict}: {after.reason}"
    assert [order["item"] for order in after.orders] == ["ethiopia"]
