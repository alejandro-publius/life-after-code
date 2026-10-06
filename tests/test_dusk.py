"""The dusk drafter: the recorded answer drafts valid orders and a readable MR description."""

from __future__ import annotations

import yaml

from conftest import OPS, REPO
import dusk
from nightorders.orders import validate_file


def test_recorded_draft_passes_code_validation(tmp_path):
    out, mr = tmp_path / "orders.yml", tmp_path / "mr.md"
    code = dusk.main([str(REPO / "demo/night-2026-10-20/today.json"), "--mode", "recorded",
                      "--out", str(out), "--mr", str(mr)])
    assert code == 0
    assert validate_file(out, OPS) == []
    text = out.read_text()
    assert text.startswith("# Tonight's orders") and "DEMO DATA" in text
    orders = yaml.safe_load(text)
    assert [o["do"]["action"] for o in orders["orders"]] == ["flag_set", "traffic_to_revision"]
    description = mr.read_text()
    assert "Left out (these wake you)" in description and "!34" in description
    assert "Merge to sign" in description


def test_live_mode_is_used_only_with_credentials(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    assert dusk.has_credentials() is False


def test_draft_schema_cannot_cover_payment_errors():
    signals = dusk.DRAFT_SCHEMA["properties"]["orders"]["items"]["properties"]["when"]["properties"]["signal"]["enum"]
    assert "payment_error_rate" not in signals


def test_system_prompt_carries_the_skill_and_targets():
    prompt = dusk.system_prompt()
    assert "Payment errors always wake the engineer" in prompt
    assert "stock_from_cache" in prompt
