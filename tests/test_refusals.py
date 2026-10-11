"""The refusal gallery: every attempt is refused by the real decision code, the control acts, and
docs/REFUSALS.md is exactly what the code prints. Offline."""

from __future__ import annotations

from conftest import REPO
from nightorders.refusals import rows, summary, table


def test_every_attempt_is_refused_and_the_control_acts():
    found = rows()
    assert found[0].who == "Control" and found[0].changed and found[0].answer.startswith("Acts: order 1")
    assert [row for row in found[1:] if row.changed] == []
    assert len(found) >= 20
    assert summary(found) == f"{len(found) - 1} attempts, 0 production changes. The control row, with everything in order, does act."


def test_the_page_is_what_the_code_prints():
    text = (REPO / "docs" / "REFUSALS.md").read_text(encoding="utf-8")
    block = text.split("<!-- refusals:start -->\n", 1)[1].split("\n<!-- refusals:end -->", 1)[0]
    found = rows()
    assert block == table(found)
    assert f"**{summary(found)}**" in text


def test_every_answer_is_short_enough_to_read_in_a_table():
    for row in rows():
        assert len(row.answer) < 400, row.tried


def test_the_readme_and_the_judge_guide_quote_the_same_count():
    attempts = len(rows()) - 1
    assert f"**{attempts} attempts, 0 production changes.**" in (REPO / "README.md").read_text(encoding="utf-8")
    assert f"({attempts} attempts, 0 production changes" in (REPO / "docs" / "GUIDE.md").read_text(encoding="utf-8")
