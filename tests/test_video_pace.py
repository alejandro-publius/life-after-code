"""The video script can be said in time: no gaps, under 3:00, no scene too full to narrate calmly. Offline."""

from __future__ import annotations

from scripts.video_pace import MAX_WPM, VIDEO, problems, scenes, srt


def test_both_shot_tables_fit_their_slots_and_the_three_minute_limit():
    text = VIDEO.read_text(encoding="utf-8")
    for plan in ("A", "B"):
        found = scenes(text, plan)
        assert len(found) >= 8 and found[0].start == 0
        assert problems(found) == [], plan
        assert max(scene.wpm for scene in found) <= MAX_WPM


def test_a_scene_that_is_too_full_is_reported():
    from scripts.video_pace import Scene
    crowded = [Scene(0, 5, "screen", " ".join(["word"] * 30)), Scene(6, 10, "screen", "")]
    found = problems(crowded)
    assert found[0] == "gap or overlap between 0:05 and 0:06"
    assert found[1] == "0:00: 30 words in 5 s is 360 words a minute (at most 170)"


def test_captions_are_timed_to_the_slots_and_skip_silent_scenes():
    found = scenes(VIDEO.read_text(encoding="utf-8"), "A")
    captions = srt(found)
    assert captions.startswith("1\n00:00:04,000 --> 00:00:09,000\nAt 3:12 the new checkout starts failing.\n")
    assert captions.count(" --> ") == len([s for s in found if s.narration])
