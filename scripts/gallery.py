"""Devpost gallery images (3:2), made from the running demo: real components, captured by the browser.

    uv run --with playwright==1.62.0 python scripts/gallery.py --out docs/images/gallery

Each image pairs one headline with components captured from /demo at phone width (the order cards, the wake-up,
the chart, the morning countersign) or rendered from the code (the refusals). Nothing is drawn by hand, and
every image carries the demo label. Set CHROMIUM_EXECUTABLE to use a browser already on the machine.
"""

from __future__ import annotations

import argparse
import html
import os
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "relay"), str(ROOT)]

from scripts.browser_smoke import STILL, application, ready  # noqa: E402

LABEL = "Demo replay: simulated shop, planted faults, recorded agent replies. Decisions by the real Watch code."
SLIDES = [
    ("01-dusk", "Before bed", "She signs what the agent may do alone tonight.",
     "At most three orders, each one reversible action with a measured condition. Each was checked before she "
     "signed, and anything that cannot be undone is left out, so it wakes her.", ["dusk-orders"]),
    ("02-decline", "01:52", "Code allowed it. The watch flow said it was the wrong fix.",
     "Code would have allowed order 1. The model saw the old checkout failing too, declined, and woke her "
     "with three lines and one fix to approve with a thumbs-up.", ["wake-veto", "wake-phone"]),
    ("03-handled", "03:13", "The signed order ran. Her phone stayed dark.",
     "Only the new checkout failed, above 5% for five minutes on enough checkouts. Code checked the signature, "
     "the expiry, the numbers and first use, took the action from the signed file, and re-checked the whole shop.",
     ["checkout-chart", "checkout-phone"]),
    ("04-morning", "07:00", "Over coffee, every change is accounted for.",
     "One quiet push. The countersign keeps the new checkout off until its fix ships and restores the rest to "
     "how it was before the night. When the fix is deployed, code ends that keep too.",
     ["morning-push", "morning-list"]),
    ("05-refusals", "Rigor", "23 attempts. 0 production changes.",
     "Model replies, a log line, a teammate, the clock, thin traffic, a switched-off path that reads 0%, files "
     "people write: each tried against the real decision code. A control row, with everything in order, does act.",
     ["refusals"]),
]


def capture(page, base: str, shots: Path) -> None:
    """Walk the signed and approved night at phone width and screenshot the components the slides use."""
    def shot(selector: str, name: str) -> None:
        page.evaluate(STILL, True)
        node = page.locator(selector).first
        node.scroll_into_view_if_needed()
        node.screenshot(path=str(shots / f"{name}.png"))
        page.evaluate(STILL, False)

    page.goto(base + "/demo", wait_until="networkidle")
    ready(page, "dusk")
    shot(".order-list", "dusk-orders")
    page.locator("#sign-orders").click()
    ready(page, "inventory")
    shot(".veto-card", "wake-veto")
    shot("#wake-message", "wake-phone")
    page.locator("#approve-fallback").click()
    ready(page, "inventory")
    page.locator("#next-step").click()
    ready(page, "checkout")
    shot(".metric-card", "checkout-chart")
    shot(".phone.dark", "checkout-phone")
    page.locator("#next-step").click()
    ready(page, "dawn")
    expect(page.locator(".lease-line").first).to_be_visible()
    shot(".quiet-push", "morning-push")
    shot(".morning-list", "morning-list")


def cut(answer: str, limit: int = 145) -> str:
    """Code's own words, whole sentences only: never cut mid-word."""
    if len(answer) <= limit:
        return answer
    end = answer.rfind(". ", 0, limit)
    return answer[:end + 1] if end > 0 else answer[:limit - 3].rstrip() + "..."


def refusals_html() -> str:
    from nightorders.refusals import rows, summary
    found = rows()
    wanted = ("obeys a log line", "never answers", "gives the 01:52 suggestion", "payment errors", "2 checkouts a minute",
              "switched-off path")
    picked = [found[0]] + [next(row for row in found[1:] if key in row.tried) for key in wanted]
    body = "".join(
        f"<tr><td class='who'>{html.escape(row.who)}</td><td>{html.escape(row.tried)}</td>"
        f"<td>{html.escape(cut(row.answer))}</td>"
        f"<td class='{'yes' if row.changed else 'no'}'>{'yes' if row.changed else 'no'}</td></tr>" for row in picked)
    return (f"<table class='refusals'><thead><tr><th>Who</th><th>What was tried</th><th>What code did, in its own "
            f"words</th><th>Changed</th></tr></thead><tbody>{body}</tbody></table>"
            f"<p class='table-note'>{html.escape(summary(found))} Full table: docs/REFUSALS.md</p>")


STYLE = """
* { box-sizing: border-box; }
html, body { margin: 0; width: 1500px; height: 1000px; overflow: hidden; }
body { background: #f4f1e9; color: #22333d; font-family: ui-sans-serif, system-ui, sans-serif;
  display: grid; grid-template-columns: 560px 1fr; gap: 56px; padding: 72px 72px 64px; }
.text { display: flex; flex-direction: column; }
.brand { display: flex; align-items: center; gap: 12px; font-weight: 750; font-size: 22px; color: #243843; }
.brand svg { width: 40px; height: 40px; }
.eyebrow { margin: 64px 0 0; color: #2e6651; font-weight: 750; letter-spacing: .5px; text-transform: uppercase;
  font-size: 20px; }
h1 { margin: 14px 0 0; font-size: 54px; line-height: 1.08; letter-spacing: -.5px; }
.copy { margin: 26px 0 0; font-size: 24px; line-height: 1.45; color: #3c4a52; }
.label { margin-top: auto; font-size: 16px; line-height: 1.4; color: #637078; border-top: 1px solid #d9ded9;
  padding-top: 16px; }
.visual { display: flex; gap: 28px; align-items: center; justify-content: center; min-width: 0; }
.visual img { max-height: 860px; max-width: 100%; border-radius: 22px; background: #fffdf7;
  box-shadow: 0 18px 50px rgba(36, 56, 67, .16); }
.visual.two img { max-width: 48%; }
.refusals { border-collapse: collapse; background: #fffdf7; border-radius: 18px; overflow: hidden; font-size: 16px;
  line-height: 1.32; box-shadow: 0 18px 50px rgba(36, 56, 67, .16); }
.refusals td.who { white-space: nowrap; font-weight: 650; }
.refusals th { text-align: left; background: #243843; color: #f4f1e9; padding: 12px 14px; font-size: 16px; }
.refusals td { padding: 10px 14px; border-top: 1px solid #d9ded9; vertical-align: top; }
.refusals td.no { color: #2e6651; font-weight: 750; }
.refusals td.yes { color: #815e25; font-weight: 750; }
.refusals tr:first-child td { background: #fff1d3; }
.table-note { margin: 14px 0 0; font-size: 17px; color: #637078; }
.wrap { display: flex; flex-direction: column; }
"""
MOON = ('<svg viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#243843"/>'
        '<path d="M22 22A10 10 0 0 1 10 8a9 9 0 1 0 12 14Z" fill="#edba59"/></svg>')


def slide(eyebrow: str, headline: str, copy: str, images: list[str], shots: Path) -> str:
    if images == ["refusals"]:
        visual = f'<div class="visual"><div class="wrap">{refusals_html()}</div></div>'
    else:
        tags = "".join(f'<img src="{(shots / f"{name}.png").as_uri()}" alt="">' for name in images)
        visual = f'<div class="visual{" two" if len(images) > 1 else ""}">{tags}</div>'
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{STYLE}</style></head><body>"
            f"<div class='text'><div class='brand'>{MOON}Night Orders</div><p class='eyebrow'>{html.escape(eyebrow)}"
            f"</p><h1>{html.escape(headline)}</h1><p class='copy'>{html.escape(copy)}</p>"
            f"<p class='label'>{html.escape(LABEL)}</p></div>{visual}</body></html>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "images" / "gallery")
    parser.add_argument("--url", help="a running relay's base URL; defaults to a temporary local server")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder, application(args.url) as base, sync_playwright() as playwright:
        shots = Path(folder)
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"],
                                             executable_path=os.environ.get("CHROMIUM_EXECUTABLE") or None)
        try:
            phone = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                                        reduced_motion="reduce")
            capture(phone.new_page(), base, shots)
            phone.close()
            canvas = browser.new_context(viewport={"width": 1500, "height": 1000}, device_scale_factor=1)
            page = canvas.new_page()
            for name, eyebrow, headline, copy, images in SLIDES:
                source = shots / f"{name}.html"
                source.write_text(slide(eyebrow, headline, copy, images, shots), encoding="utf-8")
                page.goto(source.as_uri(), wait_until="load")
                page.screenshot(path=str(args.out / f"{name}.png"))
                print(f"wrote {args.out / f'{name}.png'}")
            canvas.close()
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
