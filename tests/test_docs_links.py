"""Every relative link in the README and the docs a judge reads points at a file that exists. Offline."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

from conftest import REPO

PAGES = [REPO / "README.md", REPO / "relay" / "README.md", REPO / "shop" / "README.md"] + sorted(
    (REPO / "docs").glob("*.md"))
LINK = re.compile(r"\]\(([^)\s]+)\)")


def relative_links(page: Path) -> list[str]:
    text = page.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # links inside code blocks are examples
    found = []
    for target in LINK.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        found.append(unquote(target.split("#", 1)[0]))
    return [link for link in found if link]


@pytest.mark.parametrize("page", [p for p in PAGES if p.exists()], ids=lambda p: str(p.relative_to(REPO)))
def test_relative_links_resolve(page):
    missing = [link for link in relative_links(page) if not (page.parent / link).exists()]
    assert missing == [], missing
