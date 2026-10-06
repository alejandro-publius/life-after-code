"""One phone and laptop walk through the isolated demo, against the real HTTP app.

Run: uv run --with playwright==1.62.0 python scripts/browser_smoke.py
Optional: --screenshots docs/images, or --url https://YOUR_RELAY.run.app
Screenshots capture the browser as rendered. They are not generated artwork.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def application(url: str | None):
    if url:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.netloc or parts.username or parts.password:
            raise ValueError("Use the public base URL without credentials")
        yield url.rstrip("/")
        return
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    environment = dict(os.environ, PYTHONPATH=str(ROOT / "relay"), PYTHONDONTWRITEBYTECODE="1")
    # These values are not needed for the demo and must not be inherited by this test.
    for name in ("GITLAB_TOKEN", "RELAY_KEY", "DEMO_KEY", "NTFY_URL", "STATE_BUCKET", "K_SERVICE"):
        environment.pop(name, None)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT / "relay", env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("The local demo server stopped before becoming ready")
            try:
                with opener.open(base + "/healthz", timeout=1) as response:
                    if json.load(response)["ok"]:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.1)
        else:
            raise RuntimeError("The local demo server did not become ready within 20 seconds")
        yield base
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def ready(page, scene: str):
    expect(page.locator(f'#replay-root[data-scene="{scene}"]')).to_have_attribute("aria-busy", "false")


def fits_screen(page):
    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), "Page overflows its viewport"
    for button in page.locator("button:visible").all():
        box = button.bounding_box()
        assert box and box["height"] >= 44, "A visible button is smaller than a phone tap target"


def capture(page, directory: Path | None, name: str):
    if directory:
        directory.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(directory / name), full_page=True)


def walk(page, base: str, *, signed: bool, approved: bool, screenshots: Path | None, screen: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + "/demo", wait_until="networkidle")
    ready(page, "dusk")
    expect(page.get_by_role("heading", name="Priya wants to sleep.")).to_be_visible()
    expect(page.get_by_text("Your choices stay in this demo.", exact=True)).to_be_visible()
    fits_screen(page)
    if signed and approved:
        capture(page, screenshots, f"demo-{screen}-dusk.png")
    # Keyboard activation exercises the same controls as touch and mouse.
    choice = page.locator("#sign-orders" if signed else "#leave-unsigned")
    choice.focus()
    page.keyboard.press("Enter")
    ready(page, "inventory")
    expect(page.locator("#chapter-heading")).to_be_focused()
    expect(page.locator("#wake-message li")).to_have_count(3)
    expect(page.locator("#wake-message")).to_contain_text("Checkout")
    if signed:
        page.locator("#approve-fallback" if approved else "#decline-fallback").click()
        expect(page.locator("#chapter-heading")).to_have_text(
            "Priya approves one different action." if approved else "Priya keeps that permission to herself."
        )
        ready(page, "inventory")
    else:
        expect(page.locator("#approve-fallback")).to_have_count(0)
        expect(page.locator("#decline-fallback")).to_have_count(0)
    fits_screen(page)
    page.locator("#next-step").click()
    ready(page, "checkout")
    expect(page.locator("#chapter-heading")).to_have_text(
        "This time, Priya stays asleep." if signed else "Without a signature, Priya is needed again."
    )
    expect(page.locator("#metrics-chart")).to_be_visible()
    expect(page.get_by_text("Dashed line: 5% limit for signed new checkout order.", exact=True)).to_be_visible()
    fits_screen(page)
    if signed and approved:
        capture(page, screenshots, f"demo-{screen}.png")
    page.locator("#next-step").click()
    ready(page, "dawn")
    expected = ["1" if signed else "2", "1" if signed else "0", "1" if signed and approved else "0"]
    assert page.locator(".stat-value").all_text_contents() == expected
    expect(page.get_by_text("Tonight's permission expires.", exact=True)).to_be_visible()
    page.locator("#evidence-details > summary").click()
    expect(page.get_by_role("heading", name="Demo signature and expiry")).to_be_visible()
    expect(page.get_by_text("What was checked", exact=True)).to_be_visible()
    fits_screen(page)
    page.locator("#evidence-details > summary").click()
    if signed and approved:
        capture(page, screenshots, f"demo-{screen}-morning.png")
    page.locator("#restart-demo").click()
    ready(page, "dusk")
    expect(page.locator("#sign-orders")).to_be_enabled()
    assert errors == [], errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Public base URL; defaults to a temporary local server")
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    with application(args.url) as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            for screen, width, height in (("phone", 390, 844), ("laptop", 1440, 900)):
                context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
                for signed, approved in ((True, True), (True, False), (False, True)):
                    page = context.new_page()
                    walk(page, base, signed=signed, approved=approved, screenshots=args.screenshots, screen=screen)
                    page.close()
                context.close()
                print(f"{screen}: signed, declined and unsigned paths passed")
            context = browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
            page = context.new_page()
            page.goto(base + "/demo")
            expect(page.get_by_role("heading", name="This guided replay needs JavaScript.")).to_be_visible()
            expect(page.locator("#replay-root")).to_be_hidden()
            context.close()
            context = browser.new_context(viewport={"width": 390, "height": 844})
            page = context.new_page()
            page.route("**/demo/replay?*", lambda route: route.fulfill(status=503, body="Unavailable"))
            page.goto(base + "/demo")
            expect(page.get_by_role("heading", name="The demo could not load.")).to_be_visible()
            page.unroute("**/demo/replay?*")
            page.get_by_role("button", name="Retry the replay").click()
            ready(page, "dusk")
            expect(page.locator("#sign-orders")).to_be_enabled()
            context.close()
            print("JavaScript fallback and failed-load retry passed")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
