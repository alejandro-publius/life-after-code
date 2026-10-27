"""A viewer's morning choice changes actual snapshot restoration, never the preceding night."""

import pytest

from nightorders.browser_demo import replay


def test_restoring_every_change_uses_the_original_snapshots_and_does_not_rewrite_the_night():
    kept = replay()
    restored = replay(keep_checkout=False)
    for key in ("timeline", "metrics", "counts", "signature", "incident_memory"):
        assert restored[key] == kept[key]
    assert restored["flags"]["after_morning"] == restored["flags"]["initial"]
    assert kept["flags"]["after_morning"]["new_checkout"] == "off"
    assert restored["morning"]["kept"] == [] and "lease" not in restored["morning"]
    assert {item["action"]["flag"] for item in restored["morning"]["undone"]} == {
        "new_checkout", "stock_from_cache"}
    assert restored["steps"][-1]["flags_after"] == restored["flags"]["initial"]
    assert any("RESTORE new_checkout to on" in line for line in restored["morning"]["lines"])


def test_morning_choice_cannot_restore_a_change_that_never_happened():
    unsigned = replay(signed=False, keep_checkout=False)
    assert unsigned["morning"]["status"] == "not_needed"
    assert unsigned["morning"]["undone"] == []
    assert unsigned["flags"]["after_morning"] == unsigned["flags"]["initial"]
    declined = replay(approved=False, keep_checkout=False)
    assert [item["action"]["flag"] for item in declined["morning"]["undone"]] == ["new_checkout"]
    assert not any("RESTORE stock_from_cache" in line for line in declined["morning"]["lines"])


@pytest.mark.parametrize("value", [None, "false", 0, 1, {}, []])
def test_morning_choice_only_accepts_an_explicit_boolean(value):
    with pytest.raises(TypeError, match="keep_checkout must be a boolean"):
        replay(keep_checkout=value)
