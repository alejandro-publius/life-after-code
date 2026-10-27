"""The GitLab Pages build of the browser demo: static files, relative paths, and replays computed by the same
code the relay serves. Offline."""

from __future__ import annotations

import json

from nightorders import browser_demo
from scripts.build_pages import COMBINATIONS, build, name
from scripts.release_notes import notes


def test_the_static_site_has_the_page_its_assets_and_the_four_replays(tmp_path):
    out = tmp_path / "public"
    build(out, "https://gitlab.com/group/night-orders")
    page = (out / "index.html").read_text(encoding="utf-8")
    assert 'data-static="1"' in page and 'href="assets/style.css"' in page and 'src="assets/app.js"' in page
    assert "/demo/assets" not in page and 'href="/demo"' not in page
    assert 'href="activity.html"' in page
    activity = (out / "activity.html").read_text()
    assert 'data-static="1"' in activity and "/demo/assets" not in activity
    assert json.loads((out / "activity.json").read_text())["version"] == 1
    for asset in ("app.js", "style.css", "og.png"):
        assert (out / "assets" / asset).exists()
    for signed, approved in COMBINATIONS:
        data = json.loads((out / name(signed, approved)).read_text(encoding="utf-8"))
        expected = browser_demo.replay(signed=signed, approved=approved)
        assert data["choices"] == {"signed": signed, "approved": approved}
        assert data["repo_url"] == "https://gitlab.com/group/night-orders"
        assert data["counts"] == expected["counts"] and data["timeline"] == expected["timeline"]
    assert sorted(p.name for p in (out / "gallery").glob("*.png"))[:1] == ["01-dusk.png"]


def test_the_page_script_reads_the_static_replays_by_the_same_names():
    from conftest import REPO
    script = (REPO / "relay" / "demo_web" / "app.js").read_text(encoding="utf-8")
    assert 'document.body.dataset.static === "1"' in script
    assert '`replay-${signed ? "signed" : "unsigned"}-${approved ? "approved" : "declined"}.json`' in script
    assert name(True, False) == "replay-signed-declined.json"


def test_release_notes_carry_the_computed_numbers_and_the_links():
    text = notes({"CI_COMMIT_SHORT_SHA": "abc1234", "CI_PAGES_URL": "https://g.gitlab.io/night-orders",
                  "CI_PROJECT_URL": "https://gitlab.com/g/night-orders", "CI_PIPELINE_URL": "https://gitlab.com/p/1"})
    assert "**Try the demo night in the browser:** https://g.gitlab.io/night-orders" in text
    assert "23 attempts, 0 production changes." in text and "| Nothing signed | 2 | 0 | 0 | 0 |" in text
    assert text.rstrip().endswith("Pipeline: https://gitlab.com/p/1")
