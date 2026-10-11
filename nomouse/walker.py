"""Drive a page with the keyboard only, and hear what a screen reader would announce.

The walker never clicks, never reads pixels or HTML, and never looks up elements by
selector. It presses keys and reads Chromium's accessibility node for whatever has focus.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from nomouse.announce import Announcement, from_ax_node
from nomouse.shop.app import SESSION_COOKIE, VARIANT_COOKIE

NAVIGATION_GRACE_MS = 400  # how long to wait after a key press to see whether a page load starts
MOVE_KEYS = {"Tab", "Shift+Tab"}  # keys that only move focus


class Walker:
    """Owns one headless Chromium. Use as a context manager."""

    def __init__(self, base_url: str, *, headless: bool = True):
        self.base_url = base_url.rstrip("/")
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    def __enter__(self) -> "Walker":
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, *exc) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def open(self, variant: str | None = None, session: str | None = None) -> "Walk":
        """A fresh browser context and shop session, so walks never share a cart or orders."""
        assert self._browser, "use Walker as a context manager"
        session = session or f"walk-{uuid.uuid4().hex[:16]}"
        context = self._browser.new_context(viewport={"width": 1280, "height": 900})
        cookies = [{"name": SESSION_COOKIE, "value": session, "url": self.base_url}]
        if variant:
            cookies.append({"name": VARIANT_COOKIE, "value": variant, "url": self.base_url})
        context.add_cookies(cookies)
        return Walk(self.base_url, context, session)


class Walk:
    """One keyboard session in its own browser context. Counts every key pressed."""

    def __init__(self, base_url: str, context: BrowserContext, session: str):
        self.base_url = base_url
        self.session = session
        self.context = context
        self.page: Page = context.new_page()
        self.keys = 0
        self._navigations = 0
        self.page.on("framenavigated", self._on_navigation)
        self.cdp = context.new_cdp_session(self.page)
        self.cdp.send("Accessibility.enable")

    def _on_navigation(self, frame) -> None:
        if frame == self.page.main_frame:
            self._navigations += 1

    def close(self) -> None:
        self.context.close()

    @property
    def path(self) -> str:
        parts = urllib.parse.urlsplit(self.page.url)
        return parts.path or "/"

    def goto(self, path: str) -> None:
        self.page.goto(self.base_url + path, wait_until="load")

    def _settle(self, before: int) -> None:
        deadline = time.monotonic() + NAVIGATION_GRACE_MS / 1000
        while time.monotonic() < deadline and self._navigations == before:
            self.page.wait_for_timeout(25)
        if self._navigations != before:
            self.page.wait_for_load_state("load")

    def press(self, key: str) -> Announcement:
        before = self._navigations
        self.page.keyboard.press(key)
        self.keys += 1
        if key in MOVE_KEYS and self._navigations == before:
            # Moving focus does not load a page; a page that navigates on focus is still caught
            # by the next key that settles.
            self.page.wait_for_timeout(10)
        else:
            self._settle(before)
        return self.focused()

    def type(self, text: str) -> None:
        self.page.keyboard.type(text)
        self.keys += 1  # one entry, however long the text

    def focused(self) -> Announcement:
        """The accessibility node of the focused element, as Chromium computes it."""
        result = self.cdp.send("Runtime.evaluate", {"expression": "document.activeElement"})
        object_id = (result.get("result") or {}).get("objectId")
        if not object_id:
            return Announcement(role="document", name=self.page.title())
        tree = self.cdp.send("Accessibility.getPartialAXTree", {"objectId": object_id, "fetchRelatives": False})
        nodes = [node for node in tree.get("nodes", []) if not node.get("ignored")]
        if not nodes:
            return Announcement(role="document", name=self.page.title())
        return from_ax_node(nodes[0])

    def headings(self) -> list[Announcement]:
        tree = self.cdp.send("Accessibility.getFullAXTree")
        found = []
        for node in tree.get("nodes", []):
            if not node.get("ignored") and (node.get("role") or {}).get("value") == "heading":
                found.append(from_ax_node(node))
        return found

    def tab_order(self, limit: int = 60) -> list[Announcement]:
        """Everything Tab reaches on this page, in order, starting from the top.

        Used for evidence only. It does not count toward the journey's key budget.
        """
        self._focus_top()
        heard: list[Announcement] = []
        seen: set[str] = set()
        for _ in range(limit):
            self.page.keyboard.press("Tab")
            now = self.focused()
            if now.is_page:
                break
            if now.node and now.node in seen:
                break
            seen.add(now.node)
            heard.append(now)
        self._focus_top()
        return heard

    def _focus_top(self) -> None:
        """Move the sequential focus starting point to the top of the page, as on a fresh load."""
        self.page.evaluate(
            """() => { const b = document.body; if (!b) return; const had = b.hasAttribute('tabindex');
            if (!had) b.setAttribute('tabindex', '-1'); b.focus({preventScroll: true});
            b.blur(); if (!had) b.removeAttribute('tabindex'); }"""
        )

    def orders(self) -> list[dict]:
        """Ask the demo shop's test oracle which orders this walk placed."""
        query = urllib.parse.urlencode({"session": self.session})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"{self.base_url}/test/orders?{query}", timeout=5) as response:
            return json.load(response).get("orders", [])
