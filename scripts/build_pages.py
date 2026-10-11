"""The browser demo as a static site for GitLab Pages: a public link judges can open, no server needed.

    python scripts/build_pages.py --out public

The demo's four fixed combinations (signed or not, fallback approved or declined) are computed here by the same
code the relay runs (nightorders.browser_demo.replay) and written as JSON next to the page, which reads them
instead of asking a server. Everything else is the demo's own HTML, script and stylesheet, with paths made
relative so the site works under the project's Pages address. In CI, CI_PROJECT_URL points the demo's code
links at the GitLab project.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "relay")]

from nightorders import browser_demo  # noqa: E402

WEB = ROOT / "relay" / "demo_web"
COMBINATIONS = [(True, True), (True, False), (False, True), (False, False)]
ASSETS = ("app.js", "style.css", "og.png")
GALLERY = ROOT / "docs" / "images" / "gallery"


def name(signed: bool, approved: bool) -> str:
    return f"replay-{'signed' if signed else 'unsigned'}-{'approved' if approved else 'declined'}.json"


def page() -> str:
    text = (WEB / "index.html").read_text(encoding="utf-8")
    text = text.replace('href="/demo/assets/', 'href="assets/').replace('src="/demo/assets/', 'src="assets/')
    text = text.replace('content="/demo/assets/og.png"', 'content="assets/og.png"')
    text = text.replace('<a class="brand" href="/demo"', '<a class="brand" href="./"')
    text = text.replace('<body class="no-js">', '<body class="no-js" data-static="1">')
    return text


def build(out: Path, project_url: str | None) -> list[Path]:
    if out.exists():
        shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    written = []
    index = out / "index.html"
    index.write_text(page(), encoding="utf-8")
    written.append(index)
    for asset in ASSETS:
        shutil.copyfile(WEB / asset, out / "assets" / asset)
        written.append(out / "assets" / asset)
    for signed, approved in COMBINATIONS:
        data = browser_demo.replay(signed=signed, approved=approved)
        if project_url and project_url.startswith("https://"):
            data["repo_url"] = project_url  # the demo's code links open the GitLab project
        target = out / name(signed, approved)
        target.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        written.append(target)
    if GALLERY.exists():
        (out / "gallery").mkdir()
        for image in sorted(GALLERY.glob("*.png")):
            shutil.copyfile(image, out / "gallery" / image.name)
            written.append(out / "gallery" / image.name)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "public")
    args = parser.parse_args(argv)
    written = build(args.out, os.environ.get("CI_PROJECT_URL"))
    print(f"wrote {len(written)} files to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
