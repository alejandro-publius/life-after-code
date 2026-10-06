"""Code decides which orders can be signed. One test per reason an orders file is refused."""

from __future__ import annotations

import pytest

from conftest import OPS, at
from nightorders import OrdersError, Signature, parse_orders, signature_problems
from nightorders.orders import validate_file


def problems(data, targets, oncall):
    with pytest.raises(OrdersError) as error:
        parse_orders(data, targets, oncall)
    return " | ".join(error.value.problems)


def test_valid_orders_parse(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    assert [o.id for o in orders.orders] == [1, 2]
    assert orders.get(1).do.describe() == "new_checkout off in production"
    assert orders.get(2).do.describe() == "shop traffic to revision shop-00041"


def test_bare_yaml_off_is_accepted_for_flag_value(orders_data, targets, oncall):
    orders_data["orders"][0]["do"]["to"] = False  # what YAML makes of an unquoted off
    assert parse_orders(orders_data, targets, oncall).get(1).do.to == "off"


def test_more_than_three_orders_refused(orders_data, targets, oncall):
    extra = [dict(orders_data["orders"][0], id=i) for i in (3, 4)]
    orders_data["orders"].extend(extra)
    assert "is too long" in problems(orders_data, targets, oncall)


def test_action_off_the_menu_refused(orders_data, targets, oncall):
    orders_data["orders"][0]["do"] = {"action": "restart_database", "service": "shop"}
    assert "restart_database" in problems(orders_data, targets, oncall)


def test_unknown_flag_refused(orders_data, targets, oncall):
    orders_data["orders"][0]["do"]["flag"] = "delete_everything"
    assert "flag delete_everything is not in ops/targets.yml" in problems(orders_data, targets, oncall)


def test_unknown_service_refused(orders_data, targets, oncall):
    orders_data["orders"][1]["do"]["service"] = "billing"
    orders_data["orders"][1]["do"]["revision"] = "billing-00001"
    assert "service billing is not in ops/targets.yml" in problems(orders_data, targets, oncall)


def test_revision_of_another_service_refused(orders_data, targets, oncall):
    orders_data["orders"][1]["do"]["revision"] = "billing-00041"
    assert "does not belong to service shop" in problems(orders_data, targets, oncall)


def test_payment_errors_cannot_be_covered(orders_data, targets, oncall):
    orders_data["orders"][0]["when"] = {"signal": "payment_error_rate", "above": 0.05, "for_minutes": 5}
    assert "always wakes the on-call person" in problems(orders_data, targets, oncall)


def test_expiry_after_watch_end_refused(orders_data, targets, oncall):
    orders_data["expires"] = "09:30"
    assert "later than the watch end 07:00" in problems(orders_data, targets, oncall)


def test_duplicate_ids_refused(orders_data, targets, oncall):
    orders_data["orders"][1]["id"] = 1
    assert "the id is used twice" in problems(orders_data, targets, oncall)


def test_two_orders_on_the_same_target_refused(orders_data, targets, oncall):
    second = dict(orders_data["orders"][0], id=3)
    second["when"] = {"signal": "http_5xx_ratio", "above": 0.05, "for_minutes": 5}
    orders_data["orders"].append(second)
    assert "both change new_checkout off in production" in problems(orders_data, targets, oncall)


def test_path_required_for_checkout_errors(orders_data, targets, oncall):
    del orders_data["orders"][0]["when"]["path"]
    assert "needs a path" in problems(orders_data, targets, oncall)


def test_condition_needs_exactly_one_threshold(orders_data, targets, oncall):
    orders_data["orders"][0]["when"]["below"] = 0.01
    assert "give exactly one of above or below" in problems(orders_data, targets, oncall)


def test_unexpected_field_refused(orders_data, targets, oncall):
    orders_data["orders"][0]["do"]["also_run"] = "rm -rf /"
    assert "Additional properties are not allowed" in problems(orders_data, targets, oncall)


def test_signed_by_the_on_call_person_is_usable(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    sig = Signature(method="merge", user="alex-velazquez", at=at(oncall, "22:06"), commit="x")
    assert signature_problems(orders, sig, oncall, at(oncall, "03:12")) == []


def test_unsigned_orders_are_not_usable(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    assert signature_problems(orders, None, oncall, at(oncall, "03:12")) == ["Nobody signed tonight's orders."]


def test_signed_by_someone_else_is_not_usable(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    sig = Signature(method="merge", user="teammate", at=at(oncall, "22:06"), commit="x")
    assert "not by the on-call person" in signature_problems(orders, sig, oncall, at(oncall, "03:12"))[0]


def test_signed_yesterday_is_not_usable(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    sig = Signature(method="merge", user="alex-velazquez", at=at(oncall, "11:00").replace(day=19), commit="x")
    assert "outside tonight's window" in signature_problems(orders, sig, oncall, at(oncall, "03:12"))[0]


def test_expired_orders_are_not_usable(orders_data, targets, oncall):
    orders = parse_orders(orders_data, targets, oncall)
    sig = Signature(method="merge", user="alex-velazquez", at=at(oncall, "22:06"), commit="x")
    assert signature_problems(orders, sig, oncall, at(oncall, "07:00")) == ["Tonight's orders expired at 07:00."]


def test_repo_orders_file_is_valid():
    assert validate_file(OPS / "night-orders.yml", OPS) == []
