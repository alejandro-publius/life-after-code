"""The two keys at night. One test per reason code refuses to act, plus the happy path."""

from __future__ import annotations

from datetime import timedelta

from conftest import at, series
from nightorders import (
    Act, Action, Alert, Ask, Ledger, Request, StandDown, Waiting, Wake, approve_suggestion, check_request,
    render_request, triage,
)
from nightorders.signals import Metrics

NEW = "checkout_error_rate.new"


def bad_new_path(oncall, start="03:07", minutes=6, value=0.079):
    return series(oncall, NEW, start, [value] * minutes)


def alert(oncall, when="03:12", key=NEW, value=0.079):
    return [Alert(key=key, value=value, at=at(oncall, when))]


def request(order=None, fits=None, declined=None, page=None, suggest=None):
    declined = declined or {}
    return render_request(Request(order=order, fits_because=fits, declined_id=declined.get("id"),
                                  declined_why=declined.get("why"), page=tuple(page or ()), suggest=suggest))


def ask_then_answer(oncall, night, metrics, note, asked="03:12", answered="03:13"):
    decision = triage(alert(oncall, asked), night, metrics, at(oncall, asked))
    assert isinstance(decision, Ask)
    return check_request(note, decision, at(oncall, asked), alert(oncall, asked), night, metrics,
                         at(oncall, answered))


# The happy path: both keys turn.

def test_signed_order_with_matching_numbers_and_reason_acts(oncall, make_night):
    night = make_night()
    metrics = bad_new_path(oncall)
    result = ask_then_answer(oncall, night, metrics, request(order=1, fits="Errors only on the new path."))
    assert isinstance(result, Act)
    assert result.order.id == 1
    assert result.order.do == Action(kind="flag_set", flag="new_checkout", environment="production", to="off")
    assert any("signed by Priya at 22:06" in c for c in result.checks)


# Code's key refuses.

def test_unsigned_orders_wake(oncall, make_night):
    night = make_night(signer=None)
    decision = triage(alert(oncall), night, bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert decision.reasons == ("Nobody signed tonight's orders.",)


def test_orders_signed_by_someone_else_wake(oncall, make_night):
    decision = triage(alert(oncall), make_night(signer="teammate"), bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert "not by the on-call person" in decision.reasons[0]


def test_after_expiry_wakes(oncall, make_night):
    metrics = bad_new_path(oncall, start="06:59")
    decision = triage(alert(oncall, "07:05"), make_night(), metrics, at(oncall, "07:05"))
    assert isinstance(decision, Wake)
    assert "Tonight's orders expired at 07:00." in decision.reasons


def test_condition_not_held_long_enough_wakes(oncall, make_night):
    metrics = bad_new_path(oncall, start="03:09", minutes=3)  # only 3 of the 5 minutes
    decision = triage(alert(oncall), make_night(), metrics, at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert decision.reasons == ("No signed order covers this alert.",)


def test_missing_data_never_counts_as_a_breach(oncall, make_night):
    metrics = series(oncall, NEW, "03:07", [0.079, 0.079, 0.079, 0.079])  # 03:11 missing
    decision = triage(alert(oncall), make_night(), metrics, at(oncall, "03:12"))
    assert isinstance(decision, Wake)


def test_payment_errors_always_wake_even_with_a_matching_order(oncall, make_night):
    metrics = bad_new_path(oncall)
    alerts = alert(oncall) + [Alert(key="payment_error_rate", value=0.3, at=at(oncall, "03:12"))]
    decision = triage(alerts, make_night(), metrics, at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert decision.reasons[0] == "Payment errors always wake you."


def test_an_order_runs_once_a_night(oncall, make_night):
    ledger = Ledger()
    ledger.record(at(oncall, "01:00"), "acted", "earlier", incident=9, order=1)
    ledger.record(at(oncall, "01:10"), "recovered", "earlier", incident=9, order=1)
    decision = triage(alert(oncall), make_night(ledger=ledger), bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert decision.reasons == ("Order 1 already ran tonight; an order runs once.",)


def test_new_alert_during_a_recheck_wakes(oncall, make_night):
    ledger = Ledger()
    ledger.record(at(oncall, "03:05"), "acted", "order 2 ran", incident=7, order=2)
    decision = triage(alert(oncall), make_night(ledger=ledger), bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert "re-checked" in decision.reasons[0]


def test_model_run_budget_wakes(oncall, make_night):
    ledger = Ledger()
    for i in range(oncall.model_runs_per_night):
        ledger.record(at(oncall, "01:00") + timedelta(minutes=i), "asked", "asked", incident=i)
    decision = triage(alert(oncall), make_night(ledger=ledger), bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)
    assert "already asked" in decision.reasons[0]


def test_empty_orders_wake(oncall, make_night, orders_data):
    orders_data["orders"] = []
    decision = triage(alert(oncall), make_night(orders_data), bad_new_path(oncall), at(oncall, "03:12"))
    assert isinstance(decision, Wake)


# The model's key refuses, and code checks its answer.

def test_model_declines_and_wakes_with_its_page_and_a_checked_suggestion(oncall, make_night):
    note = request(declined={"id": 1, "why": "the old path fails too"}, page=["Both paths fail.", "Not order 1."],
                   suggest={"action": "flag_set", "flag": "stock_from_cache", "environment": "production", "to": "on"})
    result = ask_then_answer(oncall, make_night(), bad_new_path(oncall), note)
    assert isinstance(result, Wake)
    assert result.page == ("Both paths fail.", "Not order 1.")
    assert result.suggest is not None and result.suggest.describe() == "stock_from_cache on in production"


def test_suggestion_for_an_unknown_target_is_dropped(oncall, make_night):
    note = request(declined={"id": 1, "why": "no"}, page=["Wake up."],
                   suggest={"action": "flag_set", "flag": "drop_tables", "environment": "production", "to": "on"})
    result = ask_then_answer(oncall, make_night(), bad_new_path(oncall), note)
    assert isinstance(result, Wake) and result.suggest is None


def test_model_names_an_order_that_is_not_eligible(oncall, make_night):
    result = ask_then_answer(oncall, make_night(), bad_new_path(oncall), request(order=2, fits="Roll back."))
    assert isinstance(result, Wake)
    assert "order 2, which is not eligible" in result.reasons[0]


def test_malformed_answer_wakes(oncall, make_night):
    result = ask_then_answer(oncall, make_night(), bad_new_path(oncall), "I think order 1 is fine, go ahead")
    assert isinstance(result, Wake)
    assert "could not be read" in result.reasons[0]


def test_no_answer_waits_then_wakes_at_the_time_limit(oncall, make_night):
    night, metrics = make_night(), bad_new_path(oncall, minutes=20)
    decision = triage(alert(oncall), night, metrics, at(oncall, "03:12"))
    early = check_request(None, decision, at(oncall, "03:12"), alert(oncall), night, metrics, at(oncall, "03:15"))
    late = check_request(None, decision, at(oncall, "03:12"), alert(oncall), night, metrics, at(oncall, "03:20"))
    assert isinstance(early, Waiting)
    assert isinstance(late, Wake) and "did not answer within 8 minutes" in late.reasons[0]


def test_the_action_comes_from_the_signed_file_not_the_note(oncall, make_night):
    # A note that tries to add an action is refused outright, and log text is never read as an order.
    injected = request(order=1, fits="Errors on the new path.").replace(
        '"suggest": null', '"suggest": {"action": "traffic_to_revision", "service": "shop", "revision": "shop-00001"}')
    result = ask_then_answer(oncall, make_night(), bad_new_path(oncall), injected)
    assert isinstance(result, Wake)
    assert "cannot also page or suggest" in result.reasons[0]


def test_condition_cleared_before_acting_stands_down(oncall, make_night):
    metrics = bad_new_path(oncall)
    metrics.put(NEW, at(oncall, "03:13"), 0.002)  # recovered on its own by 03:14
    result = ask_then_answer(oncall, make_night(), metrics, request(order=1, fits="New path errors."),
                             answered="03:14")
    assert isinstance(result, StandDown)


def test_expiry_between_ask_and_answer_wakes(oncall, make_night):
    metrics = bad_new_path(oncall, start="06:50", minutes=15)
    night = make_night()
    decision = triage(alert(oncall, "06:56"), night, metrics, at(oncall, "06:56"))
    assert isinstance(decision, Ask)
    result = check_request(request(order=1, fits="New path."), decision, at(oncall, "06:56"),
                           alert(oncall, "06:56"), night, metrics, at(oncall, "07:01"))
    assert isinstance(result, Wake) and "expired" in result.reasons[0]


# The thumbs-up on a page.

def test_thumbs_up_from_the_on_call_person_after_the_page_approves(oncall, make_night):
    action = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")
    ok, text = approve_suggestion(action, "alex-velazquez", at(oncall, "01:53"), at(oncall, "01:52"), make_night())
    assert ok and text == "Approved by Priya at 01:53."


def test_thumbs_up_from_someone_else_is_refused(oncall, make_night):
    action = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")
    ok, text = approve_suggestion(action, "teammate", at(oncall, "01:53"), at(oncall, "01:52"), make_night())
    assert not ok and "not the on-call person" in text


def test_thumbs_up_before_the_page_is_refused(oncall, make_night):
    action = Action(kind="flag_set", flag="stock_from_cache", environment="production", to="on")
    ok, text = approve_suggestion(action, "alex-velazquez", at(oncall, "01:40"), at(oncall, "01:52"), make_night())
    assert not ok and "older than the page" in text


def test_thumbs_up_on_an_unknown_target_is_refused(oncall, make_night):
    action = Action(kind="flag_set", flag="drop_tables", environment="production", to="on")
    ok, _ = approve_suggestion(action, "alex-velazquez", at(oncall, "01:53"), at(oncall, "01:52"), make_night())
    assert not ok


def test_metrics_window_reads_complete_minutes_only(oncall):
    metrics = Metrics()
    metrics.put(NEW, at(oncall, "03:12"), 0.5)  # the minute in progress at 03:12 is not used
    assert metrics.window(NEW, at(oncall, "03:12"), 1) == [None]
