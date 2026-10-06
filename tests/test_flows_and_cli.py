"""The Duo flow files pass GitLab's schema and tool list, and the CI checks work."""

from __future__ import annotations

import sys

from conftest import OPS, REPO

sys.path.insert(0, str(REPO / "flows"))
import validate  # noqa: E402
from nightorders import cli  # noqa: E402


def test_every_flow_passes_gitlab_schema_and_tools():
    for path in sorted((REPO / "flows").glob("*.yml")):
        assert validate.check(path) == [], path.name


def test_flow_validator_catches_a_long_dash(tmp_path):
    text = (REPO / "flows" / "watch.yml").read_text().replace("You keep watch", "You keep watch —")
    bad = tmp_path / "bad.yml"
    bad.write_text(text, encoding="utf-8")
    assert any("non-ASCII" in p for p in validate.check(bad))


def test_flow_validator_catches_an_unknown_tool(tmp_path):
    text = (REPO / "flows" / "watch.yml").read_text().replace('"create_issue_note"', '"delete_project"')
    bad = tmp_path / "bad.yml"
    bad.write_text(text, encoding="utf-8")
    assert any("unknown tool delete_project" in p for p in validate.check(bad))


def test_cli_validates_the_demo_orders(capsys):
    assert cli.main(["validate", str(REPO / "demo/night-2026-10-20/orders.yml"), "--ops", str(OPS)]) == 0
    assert "ready to sign" in capsys.readouterr().out


def test_cli_rejects_a_bad_file(tmp_path, capsys):
    bad = tmp_path / "orders.yml"
    bad.write_text('night: "2026-10-20"\nexpires: "09:00"\norders: []\n')
    assert cli.main(["validate", str(bad), "--ops", str(OPS)]) == 1
    assert "later than the watch end" in capsys.readouterr().out
