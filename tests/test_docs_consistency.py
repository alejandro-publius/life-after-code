"""The documents a judge reads agree with each other and with the code: the same night's numbers, the same
tagline, and all nine of GitLab's lifecycle stages named in GitLab's words. Offline."""

from __future__ import annotations

import re

from conftest import REPO
from nightorders.compare import compare, table

README = (REPO / "README.md").read_text(encoding="utf-8")
DEVPOST = (REPO / "docs" / "DEVPOST.md").read_text(encoding="utf-8")
SUBMIT = (REPO / "docs" / "SUBMIT.md").read_text(encoding="utf-8")
STAGES = ["Plan", "Create", "Verify", "Package", "Secure", "Release", "Configure", "Monitor", "Govern"]


def test_the_devpost_story_shows_the_same_three_ways_table_the_code_computes():
    assert table(compare()) in DEVPOST


def test_the_readme_and_devpost_name_all_nine_gitlab_stages_in_order():
    for text in (README, DEVPOST):
        named = re.findall(r"^\| (" + "|".join(STAGES) + r") \|", text, flags=re.M)
        assert named == STAGES


def test_the_tagline_is_the_same_wherever_it_is_pasted_from():
    tagline = re.search(r"^\| Tagline \| (.+?) \|$", DEVPOST, flags=re.M).group(1)
    assert f"| Tagline | {tagline} |" in SUBMIT


def test_duo_is_named_on_the_readme_first_screen():
    first_screen = README.split("## Try one night in the browser", 1)[0]
    assert "GitLab Duo Agent Platform" in first_screen
