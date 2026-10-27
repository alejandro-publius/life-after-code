"""Walk the real disposable shop from a laptop and phone browser.

Run: uv run --with playwright==1.62.0 python scripts/local_browser_smoke.py
Optional: --screenshots /tmp/local-layout (still layout checks only).
Each case owns a fresh local shop and removes its temporary state afterward.
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
import tempfile
import time
import urllib.error
import urllib.request

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def local_shop():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name in ("GITLAB_TOKEN", "RELAY_KEY", "DEMO_KEY", "NTFY_URL", "STATE_BUCKET", "K_SERVICE"):
        environment.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="night-orders-browser-") as directory:
        log_path = Path(directory) / "runner.log"
        with log_path.open("w") as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "scripts/run_local.py"), "--port", str(port),
                 "--state-dir", str(Path(directory) / "state")],
                cwd=ROOT, env=environment, stdout=log, stderr=log,
            )
            base = f"http://127.0.0.1:{port}"
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise RuntimeError("The disposable shop stopped before startup: " + log_path.read_text())
                    try:
                        with opener.open(base + "/local/api/state", timeout=1) as response:
                            if json.load(response)["phase"] == "idle":
                                break
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(0.1)
                else:
                    raise RuntimeError("The disposable shop was not ready within 20 seconds")
                yield base
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def ready(page, phase):
    expect(page.locator("#local-stage")).to_have_attribute("data-phase", phase)
    expect(page.locator("#local-stage")).to_have_attribute("aria-busy", "false")
    expect(page.locator("#local-error")).to_be_hidden()


def action(page, operation, phase):
    page.locator(f'#local-stage button[data-operation="{operation}"]').click()
    ready(page, phase)
    expect(page.locator("#local-stage-title")).to_be_focused()


def state(page, base):
    response = page.request.get(base + "/local/api/state")
    assert response.ok
    return response.json()


def layout(page):
    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), "Horizontal overflow"
    for control in page.locator("button:visible, summary:visible, .local-choice:visible").all():
        box = control.bounding_box()
        assert box and box["height"] >= 44, "A visible control is smaller than 44px"
    small = page.evaluate("""() => [...document.querySelectorAll('body *')].filter(node => {
      const own = [...node.childNodes].some(child => child.nodeType === 3 && child.textContent.trim());
      const box = node.getBoundingClientRect(), style = getComputedStyle(node);
      return own && box.width && box.height && style.visibility !== 'hidden'
        && parseFloat(style.fontSize) < 12;
    }).map(node => node.className || node.tagName)""")
    assert not small, f"Text smaller than 12px: {small[:5]}"


def capture(page, directory, name):
    if directory:
        directory.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(directory / (name + ".png")), full_page=True)


def walk(browser, name, viewport, signed, choice, screenshots):
    with local_shop() as base:
        context = browser.new_context(viewport=viewport, reduced_motion="reduce", accept_downloads=True)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        try:
            page.goto(base + "/local")
            ready(page, "idle")
            expect(page.get_by_role("heading", name="Run a real local night.")).to_be_visible()
            layout(page)
            capture(page, screenshots, name + "-ready")
            action(page, "start", "started")
            baseline = state(page, base)
            assert baseline["baseline"]["healthy"] is True
            assert baseline["baseline"]["checkouts"] >= 10
            assert baseline["flags"] == baseline["starting_flags"]
            assert len(baseline["checkout_requests"]) >= 10
            session_id = baseline["session_id"]
            if signed:
                action(page, "authorize", "authorized")
                page.reload()
                ready(page, "authorized")
                assert state(page, base)["session_id"] == session_id
            action(page, "observe", "applied" if signed else "observed")
            watched = state(page, base)
            assert watched["decision"]["applied"] is signed
            assert watched["flags"]["new_checkout"] == ("off" if signed else "on")
            assert watched["request_count"] > baseline["request_count"]
            assert sum(item["http"] == 500 for item in watched["checkout_requests"]) >= 50
            if signed:
                assert watched["authorization"]["used"] is True
                assert watched["decision"]["readback"] == watched["flags"]
            else:
                expect(page.locator("#local-stage-title")).to_have_text("The order was refused.")
            page.get_by_role("button", name="Reload saved run", exact=True).click()
            ready(page, "applied" if signed else "observed")
            reloaded = state(page, base)
            assert reloaded["session_id"] == session_id
            assert len(reloaded["checkout_requests"]) == len(watched["checkout_requests"])
            assert reloaded["flags"] == watched["flags"]
            action(page, "verify", "verified")
            verified = state(page, base)
            assert verified["verification"]["healthy"] is signed
            assert verified["verification"]["checkouts"] >= 10
            assert verified["metrics"]["after"][-1]["checkouts.all"] >= 10
            if signed:
                assert verified["metrics"]["after"][-1]["checkouts.new"] == 0
                expect(page.locator("#local-stage-title")).to_have_text("Fresh traffic confirms recovery.")
            else:
                expect(page.locator("#local-stage-title")).to_have_text("The shop still needs attention.")
            layout(page)
            capture(page, screenshots, name + "-morning-choice")
            page.locator(f'input[name="morning-choice"][value="{choice}"]').check()
            action(page, "morning", "morning")
            morning = state(page, base)
            assert morning["morning"]["choice"] == choice
            assert morning["morning"]["healthy"] is (signed and choice == "keep")
            assert morning["flags"]["new_checkout"] == ("off" if signed and choice == "keep" else "on")
            action(page, "finish", "finished")
            finished = state(page, base)
            assert finished["cleanup"]["healthy"] is True
            assert finished["flags"] == baseline["starting_flags"]
            assert finished["request_count"] > morning["request_count"]
            with page.expect_download() as pending:
                page.get_by_role("link", name="Download the run receipt", exact=True).click()
            receipt = json.loads(Path(pending.value.path()).read_text())
            assert receipt["session_id"] == session_id and receipt["phase"] == "finished"
            assert "csrf_token" not in receipt
            assert receipt["checkout_requests"] == finished["checkout_requests"]
            assert all(intent["status"] == "confirmed" for intent in receipt["intents"])
            page.reload()
            ready(page, "finished")
            layout(page)
            assert not errors, errors
            print(f"PASS {name}: real traffic, {'permission' if signed else 'refusal'}, {choice}, saved reload, cleanup and receipt")
        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots", type=Path, help="Save still screenshots for layout inspection")
    args = parser.parse_args()
    expect.set_options(timeout=15000)
    with sync_playwright() as playwright:
        executable = os.environ.get("CHROMIUM_EXECUTABLE")
        browser = playwright.chromium.launch(executable_path=executable) if executable else playwright.chromium.launch()
        try:
            walk(browser, "laptop-keep", {"width": 1280, "height": 900}, True, "keep", args.screenshots)
            walk(browser, "phone-restore", {"width": 390, "height": 844}, True, "restore", args.screenshots)
            walk(browser, "phone-unsigned", {"width": 360, "height": 780}, False, "restore", args.screenshots)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
