"""The public Pages check records every result, failures included, one page per check. Offline, with fakes."""

from __future__ import annotations

import pytest

from scripts import claude_pages_check as check


class Page:
    def __init__(self, context):
        self.context = context
        self.closed = False

    def close(self):
        self.closed = True


class Context:
    def __init__(self, browser, **options):
        self.browser = browser
        self.options = options
        self.pages: list[Page] = []
        self.closed = False

    def new_page(self):
        page = Page(self)
        self.pages.append(page)
        return page

    def close(self):
        self.closed = True


class Browser:
    def __init__(self):
        self.contexts: list[Context] = []

    def new_context(self, **options):
        context = Context(self, **options)
        self.contexts.append(context)
        return context


def test_every_path_and_screen_is_tried_and_a_failure_is_written_down_not_dropped():
    browser = Browser()
    walked = []

    def walk(page, base, *, signed, approved, screenshots, screen):
        walked.append((screen, signed, approved))
        assert base == "https://demo.example" and screenshots is None
        if screen == "phone" and not signed:
            raise AssertionError("Page overflows its viewport")

    def explorer(page, base, *, static):
        assert static is True

    results = check.run_checks("https://demo.example", browser, walk, explorer)
    assert len(results) == 8 and len(walked) == 6
    assert [r["result"] for r in results] == ["passed", "passed", "failed", "passed"] + ["passed"] * 4
    assert results[2] == {"check": "phone: unsigned", "result": "failed",
                          "error": "AssertionError: Page overflows its viewport"}
    assert {context.options["viewport"]["width"] for context in browser.contexts} == {390, 1440}
    assert all(context.closed and all(page.closed for page in context.pages) for context in browser.contexts)
    assert [len(context.pages) for context in browser.contexts] == [4, 4]


def test_an_explorer_that_is_not_deployed_yet_is_a_recorded_failure():
    def explorer(page, base, *, static):
        raise TimeoutError("waiting for locator('#activity-root')")

    results = check.run_checks("https://demo.example", Browser(), lambda *a, **k: None, explorer)
    failed = [r for r in results if r["result"] == "failed"]
    assert [r["check"] for r in failed] == ["phone: execution explorer", "laptop: execution explorer"]
    assert failed[0]["error"].startswith("TimeoutError: waiting for locator")


@pytest.mark.parametrize("url", ["http://demo.example", "https://user:pw@demo.example", "https://demo.example/?x=1",
                                 "https://demo.example/#top", "demo.example"])
def test_only_a_clean_public_https_url_is_opened(url):
    with pytest.raises(ValueError):
        check.public_url(url)
    assert check.public_url("https://demo.example/") == "https://demo.example"
