"""The public Pages check records every result, failures included, one page per check. Offline, with fakes."""

from __future__ import annotations

import pytest

from scripts import claude_pages_check as check


class Page:
    def __init__(self, context, html="<h1>Priya wants to sleep.</h1>", url="https://demo.example/"):
        self.context = context
        self.html = html
        self.url = url
        self.closed = False

    def content(self):
        return self.html

    def title(self):
        return "Night Orders"

    def close(self):
        self.closed = True


class Context:
    def __init__(self, browser, **options):
        self.browser = browser
        self.options = options
        self.pages: list[Page] = []
        self.closed = False

    def new_page(self):
        page = Page(self, self.browser.html, self.browser.url)
        self.pages.append(page)
        return page

    def close(self):
        self.closed = True


class Browser:
    def __init__(self, html="<h1>Priya wants to sleep.</h1>", url="https://demo.example/"):
        self.html = html
        self.url = url
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


def test_a_bot_check_page_is_named_as_the_cause_and_never_answered():
    html = '<title>Just a moment...</title><script src="https://challenges.cloudflare.com/turnstile/v0/api.js">'
    browser = Browser(html)

    def walk(page, base, **kwargs):
        raise TimeoutError("Page.goto: Timeout 30000ms exceeded")

    results = check.run_checks("https://demo.example", browser, walk, lambda *a, **k: None)
    failed = [r for r in results if r["result"] == "failed"]
    assert len(failed) == 6
    assert all(r["cause"].startswith("the host answered with a Cloudflare challenge page") for r in failed)
    assert all("not bypassed" in r["cause"] for r in failed)
    assert "cause" not in results[3]  # the explorer check passed on that page: no cause to record
    plain = check.run_checks("https://demo.example", Browser(), walk, lambda *a, **k: None)
    assert all("cause" not in r for r in plain)  # an ordinary timeout names no challenge


def test_a_redirect_to_gitlab_sign_in_is_named_as_pages_access_control_and_nobody_signs_in():
    browser = Browser("<h1>gitlab.com</h1>", url="https://gitlab.com/users/sign_in?redirect_to_referer=yes")

    def walk(page, base, **kwargs):
        raise TimeoutError("Page.goto: Timeout 30000ms exceeded")

    results = check.run_checks("https://demo.example", browser, walk, lambda *a, **k: None)
    failed = [r for r in results if r["result"] == "failed"]
    assert len(failed) == 6
    assert all(r["cause"].startswith("the host redirected to GitLab sign-in (Pages access control)") for r in failed)
    assert all(r["cause"].endswith("not signed in") for r in failed)
