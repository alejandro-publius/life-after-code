"""Open the public GitLab Pages demo in a real browser and walk it: sign, approve, the morning, incident memory
and the handoff download, on a phone and a laptop viewport, then the execution explorer. Read-only against the
public site. Records the browser and every result as JSON, failures included: a check that fails is written
down with the error, never dropped.

    uv run --locked --with playwright==1.62.0 python scripts/claude_pages_check.py \\
        --url https://showcase-700ee4.gitlab.io --out docs/claude/pages-check.json

The checks themselves are scripts/browser_smoke.py's, the same walk the pipeline runs on the static build.
CHROMIUM_EXECUTABLE points at a browser already on the machine when Playwright's own is absent.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import partial
from importlib import metadata
import json
import os
from pathlib import Path
import sys
from typing import Callable
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PATHS = ((True, True, "signed and approved"), (True, False, "signed, approval declined"), (False, True, "unsigned"))
SCREENS = (("phone", 390, 844), ("laptop", 1440, 900))
COVERS = ("sign the orders (or leave them unsigned)", "approve or decline the suggested action", "the morning: watch "
          "log, countersign, lease", "the permission boundary cases", "incident memory", "the shift handoff download "
          "(signed and approved path)", "the execution explorer page")


def public_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Use the public HTTPS base URL without credentials, query or fragment")
    return url.rstrip("/")


def one_line(text: object, limit: int = 600) -> str:
    return " ".join(str(text).split())[:limit]


CHALLENGE_MARKS = ("challenges.cloudflare.com", "cf-chl", "Just a moment")
SIGN_IN_MARKS = ("projects.gitlab.io/auth", "/users/sign_in", "/oauth/authorize")


def cause(page) -> str:
    """What the browser was looking at when a check failed, when it is not the demo: a sign-in page or a bot-check
    page, say. Nothing here signs in or answers a challenge; the cause is only named, so the record says why
    playback could not be checked."""
    try:
        url = str(page.url or "")
        text = str(page.content() or "")[:200_000]
        title = str(page.title() or "")
    except Exception:  # noqa: BLE001  (a page that is gone has no cause to read)
        return ""
    if any(mark in url for mark in SIGN_IN_MARKS):
        return ("the host redirected to GitLab sign-in (Pages access control), so the demo is not public for an "
                "anonymous visitor; not signed in")
    if any(mark in text or mark in title for mark in CHALLENGE_MARKS):
        return "the host answered with a Cloudflare challenge page (a bot check) instead of the demo; not bypassed"
    return ""


def attempt(name: str, action: Callable[[], None], page=None) -> dict:
    try:
        action()
        return {"check": name, "result": "passed"}
    except Exception as error:  # noqa: BLE001  (every failure is evidence; the name says what failed)
        result = {"check": name, "result": "failed", "error": one_line(f"{type(error).__name__}: {error}")}
        why = cause(page) if page is not None else ""
        if why:
            result["cause"] = why
        return result


def run_checks(base: str, browser, walk: Callable, explorer: Callable) -> list[dict]:
    """The three demo paths on each screen, then the explorer. One page per check, so a failure cannot leak."""
    results = []
    for screen, width, height in SCREENS:
        context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
        try:
            for signed, approved, label in PATHS:
                page = context.new_page()
                results.append(attempt(f"{screen}: {label}", partial(walk, page, base, signed=signed, approved=approved,
                                                                     screenshots=None, screen=screen), page))
                page.close()
            page = context.new_page()
            results.append(attempt(f"{screen}: execution explorer", partial(explorer, page, base, static=True), page))
            page.close()
        finally:
            context.close()
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", required=True, help="the public Pages base URL")
    parser.add_argument("--out", type=Path, required=True, help="where to write the JSON record")
    args = parser.parse_args(argv)
    base = public_url(args.url)
    import browser_smoke  # noqa: E402  (the pipeline's own walk; Playwright is imported there)
    from playwright.sync_api import sync_playwright
    browser_smoke.DEMO_PATH = "/"  # the static Pages build serves the demo at the root
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"],
                                             executable_path=os.environ.get("CHROMIUM_EXECUTABLE") or None)
        try:
            checks = run_checks(base, browser, browser_smoke.walk, browser_smoke.execution_explorer)
            report = {"checked_at": datetime.now(timezone.utc).isoformat(), "url": base,
                      "browser": f"Chromium {browser.version}, headless, through Playwright "
                                 f"{metadata.version('playwright')}",
                      "source_commit_of_the_checks": browser_smoke_commit(), "covers": list(COVERS), "checks": checks,
                      "passed": all(check["result"] == "passed" for check in checks),
                      "blocked_before_the_demo": any(check.get("cause") for check in checks)}
        finally:
            browser.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for check in checks:
        print(f"{check['result']:6} {check['check']}" + (f": {check['error']}" if check.get("error") else "")
              + (f" [{check['cause']}]" if check.get("cause") else ""))
    print(f"{'all passed' if report['passed'] else 'some failed'}; wrote {args.out}")
    return 0 if report["passed"] else 1


def browser_smoke_commit() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"], capture_output=True,
                              text=True, timeout=10, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
