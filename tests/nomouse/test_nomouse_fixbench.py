"""The fix bench's scoring and its rule that deleting a feature is not a repair."""

from __future__ import annotations

from nomouse.fixbench import MAX_REMOVED_WORDS, evaluate_fix_criteria, fix_ok, removed_words
from nomouse.proposal import Fix


def test_attribute_changes_remove_no_visible_words():
    fix = Fix(file="f", find='<button type="submit">', replace='<button type="submit" aria-label="Pay now">')
    assert removed_words(fix) == 0
    swap = Fix(file="f", find='<span class="x" onclick="go()">Add to cart</span>',
               replace='<button type="button" class="x" onclick="go()">Add to cart</button>')
    assert removed_words(swap) == 0


def test_deleting_a_dialog_counts_its_words():
    dialog = '<div role="dialog"><h2>Join our newsletter</h2><p>Ten percent off your first bag.</p></div>'
    assert removed_words(Fix(file="f", find=dialog, replace="")) >= 9


def test_a_fix_is_green_only_when_walkable_safe_and_content_kept():
    walkable = {"fix_green": True}
    assert fix_ok(walkable, 0)
    assert fix_ok(walkable, MAX_REMOVED_WORDS)
    assert not fix_ok(walkable, MAX_REMOVED_WORDS + 1)
    assert not fix_ok({"fix_green": True, "fix_path_unsafe": True}, 0)
    assert not fix_ok({"fix_green": False}, 0)
    assert not fix_ok(walkable, None)


def record(vid, f0_ok, model_oks, valid=True):
    return {"id": vid, "kind": "barrier", "valid": valid, "f0": {"source": "F0", "ok": f0_ok, "outcome": {}},
            "model": [{"source": "m", "run": i + 1, "ok": ok, "outcome": {}} for i, ok in enumerate(model_oks)]}


def test_the_model_must_beat_the_rules_on_two_barriers_and_fix_two_thirds():
    passing = [record("a", False, [True, True, False]), record("b", False, [True, True, True]),
               record("c", True, [True, True, True])]
    scored = evaluate_fix_criteria(passing)
    assert scored["F1"]["passed"] and scored["F1"]["variants"] == ["a", "b"]
    assert scored["F2"]["passed"] and scored["overall"] == "PASS"

    one_win = [record("a", False, [True, True, False]), record("b", True, [True, True, True]),
               record("c", True, [True, False, False])]
    scored = evaluate_fix_criteria(one_win)
    assert not scored["F1"]["passed"] and scored["overall"] == "FAIL"
    assert scored["notes"] and "does not repair barriers better" in scored["notes"][0]
    assert scored["report"]["rules_beat_model"] == ["c"]


def test_f2_needs_two_thirds_and_excluded_variants_do_not_count():
    records = [record("a", False, [True, True, True]), record("b", False, [True, True, True]),
               record("c", False, [False, False, False]), record("d", False, [False, False, False]),
               record("x", False, [True, True, True], valid=False)]
    scored = evaluate_fix_criteria(records)
    assert scored["F2"]["count"] == 2 and scored["F2"]["of"] == 4 and not scored["F2"]["passed"]
    assert scored["report"]["excluded"] == ["x"]


def test_an_unsafe_walk_of_a_fixed_page_fails_f3():
    bad = record("a", False, [True, True, True])
    bad["model"][0]["outcome"] = {"fix_green": True, "fix_path_unsafe": True}
    assert not evaluate_fix_criteria([bad])["F3"]["passed"]


def test_nothing_to_score_is_a_fail():
    assert evaluate_fix_criteria([])["overall"] == "FAIL"
