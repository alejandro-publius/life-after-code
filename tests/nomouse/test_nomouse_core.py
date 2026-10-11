"""No Mouse core rules that need no browser: what is announced, what may be pressed,
which journeys are valid, how much evidence is printed, and the demo shop's own rules."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from nomouse.announce import Announcement, from_ax_node
from nomouse.guards import is_junk_name, label_not_in_name, press_violation
from nomouse.journey import (EVIDENCE_BEGIN, EVIDENCE_END, EVIDENCE_LIMIT, JourneyError, Result,
                             evidence, evidence_text, load_journey, parse_step)
from nomouse.shop.app import SESSION_COOKIE, create_app


def node(role, name="", value=None, **props):
    data = {"role": {"value": role}, "name": {"value": name}, "backendDOMNodeId": 7,
            "properties": [{"name": key, "value": {"value": val}} for key, val in props.items()]}
    if value is not None:
        data["value"] = {"value": value}
    return data


def test_announcement_reads_role_name_value_and_states():
    field = from_ax_node(node("textbox", "Email", value="robin@example.test", required=True))
    assert field.spoken() == "Email, robin@example.test, edit text, required"
    menu = from_ax_node(node("combobox", "Delivery", value="Standard, free", expanded=False))
    assert menu.spoken() == "Delivery, Standard, free, combo box, collapsed"
    assert from_ax_node(node("heading", "Checkout", level=1)).spoken() == "Checkout, heading level 1"


def test_an_unnamed_button_is_heard_as_its_role_only():
    assert from_ax_node(node("button")).spoken() == "button"
    assert from_ax_node(node("RootWebArea", "Checkout")).is_page


@pytest.mark.parametrize("name", ["", "button", "icon-lock", "lock_icon", "pay.svg", "cta_primary",
                                  "cta-primary-2", "button3", "x", "...", "Click here"])
def test_meaningless_names_are_junk(name):
    assert is_junk_name(name)


@pytest.mark.parametrize("name", ["Pay now, $18.00", "Place order", "Sign-in", "Add to cart", "Submit",
                                  "Checkout", "e-mail"])
def test_ordinary_names_are_not_junk(name):
    assert not is_junk_name(name)


def test_pressing_is_refused_only_for_unnamed_or_meaningless_controls():
    assert "no name" in press_violation(Announcement(role="button"))
    assert "says nothing" in press_violation(Announcement(role="link", name="icon-cart"))
    assert press_violation(Announcement(role="button", name="Place order, $18.00")) is None
    # Fields are typed into, not pressed; their labels are judged elsewhere.
    assert press_violation(Announcement(role="textbox")) is None


@pytest.mark.parametrize("raw, message", [
    ({"do": "find", "role": "button"}, "role and a name"),
    ({"do": "press", "key": "Tab"}, "press key"),
    ({"do": "type", "text": "x" * 201}, "at most 200"),
    ({"do": "expect_heading"}, "needs a name"),
    ({"do": "click", "name": "Pay"}, "unknown step"),
    ({"do": "find", "role": "button", "name": "Pay", "selector": "#pay"}, "unknown step keys"),
    ("find Pay", "mapping"),
])
def test_malformed_steps_are_rejected(raw, message):
    with pytest.raises(JourneyError, match=message):
        parse_step(raw)


def test_a_journey_without_steps_is_rejected(tmp_path: Path):
    path = tmp_path / "empty.yml"
    path.write_text("name: nothing\nstart: /\nsteps: []\n")
    with pytest.raises(JourneyError):
        load_journey(path)


def test_recorded_journey_loads(journey):
    assert journey.steps[-1].do == "expect_heading" and journey.steps[-1].name == "Order placed"
    assert journey.order_item == "ethiopia" and journey.key_budget == 60


def test_evidence_is_bounded_and_marked(journey):
    many = [Announcement(role="link", name=f"Coffee number {i} with a long descriptive name " * 3) for i in range(400)]
    result = Result(verdict="broken", failed_step=13, reason="never heard it", keys=30, heard=many, page="/checkout")
    block = evidence(journey, result)
    assert len(json.dumps(block, ensure_ascii=False).encode()) <= EVIDENCE_LIMIT
    assert block["truncated"] is True and block["heard_total"] == 400
    assert 0 < len(block["heard_in_tab_order"]) <= 40
    short = evidence(journey, Result(verdict="broken", failed_step=13, heard=many[:3], page="/checkout"))
    assert "truncated" not in short and short["heard_total"] == 3
    assert block["expected"] == 'Tab to "Pay now, $18.00, button"'
    assert block["template_files"] == ["nomouse/shop/templates/checkout.html"]
    text = evidence_text(block)
    assert text.startswith(EVIDENCE_BEGIN) and text.endswith(EVIDENCE_END)


def test_shop_records_an_order_only_with_an_email_and_card():
    client = TestClient(create_app())
    client.cookies.set(SESSION_COOKIE, "test-session-1")
    assert client.get("/checkout", follow_redirects=False).status_code == 303  # empty cart
    client.post("/cart/add")
    refused = client.post("/pay", content="email=&card=1", headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert "could not place the order" in refused.text
    placed = client.post("/pay", content="email=robin%40example.test&card=1111",
                         headers={"Content-Type": "application/x-www-form-urlencoded"}, follow_redirects=False)
    assert placed.status_code == 303 and placed.headers["location"].startswith("/confirm?order=DB-0001")
    orders = client.get("/test/orders", params={"session": "test-session-1"}).json()["orders"]
    assert orders == [{"number": "DB-0001", "item": "ethiopia", "quantity": 1}]
    assert client.get("/test/orders", params={"session": "../etc"}).json()["orders"] == []


def test_shop_ignores_unknown_or_unsafe_variant_names(tmp_path: Path):
    (tmp_path / "ok" / "templates").mkdir(parents=True)
    (tmp_path / "ok" / "templates" / "home.html").write_text("<h1>Variant home</h1>")
    client = TestClient(create_app(tmp_path))
    client.cookies.set("nm_variant", "ok")
    assert "Variant home" in client.get("/").text
    client.cookies.set("nm_variant", "../ok")
    assert "Variant home" not in client.get("/").text


@pytest.mark.parametrize("name, visible, mismatch", [
    ("Save for later", "Pay now, $18.00", True),            # spoken name hides what the button does
    ("Pay now, $18.00", "Pay now, $18.00", False),
    ("Pay now, $18.00, opens the payment step", "Pay now, $18.00", False),  # extra words are fine
    ("Close", "\u00d7", False),                              # an icon character is not a text label
    ("Checkout", "", False),                                # nothing visible to compare
    ("", "Pay now", False),                                 # no name at all is judged elsewhere
])
def test_spoken_name_must_contain_the_visible_label(name, visible, mismatch):
    assert label_not_in_name(Announcement(role="button", name=name, visible=visible)) is mismatch


def test_pressing_a_control_whose_name_contradicts_its_label_is_refused():
    refused = press_violation(Announcement(role="button", name="Save for later", visible="Pay now, $18.00"))
    assert refused and "visible label" in refused and "Save for later" in refused
    # A meaningless name is still reported as such, before the label check.
    assert "says nothing" in press_violation(Announcement(role="button", name="icon-lock", visible="Pay now"))
