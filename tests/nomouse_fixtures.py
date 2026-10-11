"""Fixtures for the No Mouse tests in tests/nomouse. Browser tests need Playwright's Chromium.

Loaded from tests/conftest.py through pytest_plugins. It is not a conftest.py of its own,
because the Night Orders tests import helpers with "from conftest import ...", and a second
module named conftest would shadow theirs when the whole suite runs.

The Python checks job has no browser, so browser tests skip there. The browser job sets
NOMOUSE_REQUIRE_BROWSER=1, which turns a missing browser into a failure instead of a skip.

Playwright's sync API allows one running instance per thread, so the shop and walker are
scoped to a test module. A test that needs its own Walker belongs in a module that does not
use these fixtures. The served variants are a temporary copy of nomouse/variants plus the
test-only variants in tests/nomouse/fixtures/variants (for example t-junk).
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

import pytest

from nomouse.journey import load_journey

REPO = Path(__file__).resolve().parents[1]
VARIANTS = REPO / "nomouse" / "variants"
JOURNEY = REPO / "nomouse" / "journeys" / "checkout.yml"
TEST_VARIANTS = REPO / "tests" / "nomouse" / "fixtures" / "variants"


def _playwright_or_skip():
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        if os.environ.get("NOMOUSE_REQUIRE_BROWSER") == "1":
            pytest.fail("Playwright is required in this job but is not installed")
        pytest.skip("Playwright is not installed; the browser job runs these tests")


@pytest.fixture(scope="session")
def journey():
    return load_journey(JOURNEY)


@pytest.fixture(scope="module")
def served_variants(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("variants")
    shutil.copytree(VARIANTS, root, dirs_exist_ok=True)
    shutil.copytree(TEST_VARIANTS, root, dirs_exist_ok=True)
    return root


@pytest.fixture(scope="module")
def shop_url(served_variants):
    _playwright_or_skip()
    from nomouse.server import serve

    with serve(served_variants) as base:
        yield base


@pytest.fixture(scope="module")
def walker(shop_url):
    from nomouse.walker import Walker

    try:
        with Walker(shop_url) as instance:
            yield instance
    except Exception as exc:  # the Chromium binary itself may be missing
        if os.environ.get("NOMOUSE_REQUIRE_BROWSER") == "1":
            raise
        pytest.skip(f"Chromium is not available: {exc}")
