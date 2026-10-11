"""A captioned screen recording of the browser demo, following Plan B in docs/VIDEO.md, ready to upload.

    uv run --with playwright==1.62.0 python scripts/record_demo.py --out dist/night-orders-demo.mp4

It starts the demo locally, walks the same night the shot list describes (sign, approve the fallback, the
checkout order, the evidence, the unsigned night, the morning), shows each scene's narration as a caption at
the bottom and the demo label at the top, and encodes 1280x720 H.264 with ffmpeg. The captions also go to a
SubRip file next to the video, for YouTube. Nothing in it is live: it is the local replay, labelled as such on
every frame. Set CHROMIUM_EXECUTABLE to use a browser already on the machine.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from scripts.browser_smoke import application, ready  # noqa: E402
from scripts.video_pace import VIDEO, scenes, srt  # noqa: E402

WIDTH, HEIGHT = 1280, 720   # the video
VIEW_W, VIEW_H = 1120, 630   # the browser, scaled up to the video so text reads at 720p
LABEL = "Local demo replay. Simulated shop. Planted faults. Recorded agent replies. Priya is a demo persona."
REPO = "github.com/alejandro-publius/life-after-code"

OVERLAY = """([label, text]) => {
  const make = (id) => {
    let node = document.getElementById(id);
    if (!node) { node = document.createElement('div'); node.id = id; document.body.appendChild(node); }
    return node;
  };
  const chip = make('rec-label');
  Object.assign(chip.style, {position: 'fixed', top: '64px', right: '12px', zIndex: 99999, padding: '6px 10px',
    borderRadius: '6px', background: 'rgba(36,56,67,.88)', color: '#f4f1e9', font: '600 13px system-ui, sans-serif',
    pointerEvents: 'none'});
  chip.textContent = label;
  const bar = make('rec-caption');
  Object.assign(bar.style, {position: 'fixed', left: '50%', bottom: '18px', transform: 'translateX(-50%)',
    zIndex: 99999, maxWidth: '1100px', width: 'calc(100% - 80px)', padding: '12px 18px', borderRadius: '10px',
    background: 'rgba(17,24,28,.86)', color: '#ffffff', font: '500 19px/1.35 system-ui, sans-serif',
    textAlign: 'center', display: text ? 'block' : 'none', pointerEvents: 'none'});
  bar.textContent = text;
}"""

TITLE = """([title, line, repo]) => {
  const card = document.createElement('div');
  Object.assign(card.style, {position: 'fixed', inset: '0', zIndex: 100000, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center', gap: '18px', background: '#243843', color: '#f4f1e9',
    font: '500 24px system-ui, sans-serif', textAlign: 'center', padding: '40px'});
  const h = document.createElement('div');
  Object.assign(h.style, {font: '800 64px system-ui, sans-serif', color: '#edba59'});
  h.textContent = title;
  const p = document.createElement('div');
  p.textContent = line;
  const r = document.createElement('div');
  Object.assign(r.style, {font: '500 20px ui-monospace, monospace', color: '#d5e5d2'});
  r.textContent = repo;
  card.append(h, p, r);
  document.body.appendChild(card);
}"""

SCROLL = """([selector, ms]) => new Promise((done) => {
  const node = selector ? document.querySelector(selector) : null;
  const target = selector === 'top' ? 0 : node ? node.getBoundingClientRect().top + scrollY - 90 : scrollY;
  const start = scrollY, began = performance.now();
  const step = (now) => {
    const t = Math.min(1, (now - began) / ms), eased = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    scrollTo(0, start + (target - start) * eased);
    if (t < 1) requestAnimationFrame(step); else done();
  };
  requestAnimationFrame(step);
})"""


class Walk:
    def __init__(self, page, base: str):
        self.page, self.base = page, base

    def caption(self, text: str) -> None:
        self.page.evaluate(OVERLAY, [LABEL, text])

    def scroll(self, selector: str, ms: int = 1600) -> None:
        self.page.evaluate(SCROLL, [selector, ms])

    def click(self, selector: str, scene: str | None = None) -> None:
        self.page.locator(selector).first.click()
        if scene:
            ready(self.page, scene)

    def fresh(self) -> None:
        self.page.goto(self.base + "/demo", wait_until="networkidle")
        ready(self.page, "dusk")


def plan_b(walk: Walk) -> list:
    """One action list per Plan B scene, in order. Each runs at the start of its slot; the slot's time is held."""
    def signed_night():
        walk.fresh()
        walk.click("#sign-orders", "inventory")
        walk.click("#approve-fallback", "inventory")

    def s0():  # cold open at 03:12: the chart and the dark phone
        signed_night()
        walk.click("#next-step", "checkout")
        walk.scroll(".metric-card", 600)
        time.sleep(3)
        walk.scroll(".phone.dark", 1200)

    def s1():  # before bed
        walk.fresh()
        walk.caption(walk_caption[1])
        walk.scroll(".order-list", 2200)
        time.sleep(5)
        walk.scroll("#primary-action", 1200)
        time.sleep(1)
        walk.click("#sign-orders", "inventory")
        walk.scroll("top", 600)

    def s2():  # 01:52, the decline and the one wake-up
        walk.scroll(".veto-card", 1800)
        time.sleep(5)
        walk.scroll("#wake-message", 1500)
        time.sleep(5)
        walk.scroll("#primary-action", 800)
        walk.click("#approve-fallback", "inventory")

    def s3():  # 03:13, the order runs
        walk.click("#next-step", "checkout")
        walk.scroll("top", 400)
        time.sleep(3)
        walk.scroll(".metric-card", 1800)
        time.sleep(5)
        walk.scroll(".phone.dark", 1500)

    def s4():  # the evidence and the planted log line
        walk.click("#evidence-details > summary")
        walk.scroll("#evidence-details", 1600)
        time.sleep(4)
        walk.scroll(".proof-log mark", 1800)
        time.sleep(5)
        walk.scroll(".ledger-list", 2000)

    def s5():  # the same night, unsigned
        walk.fresh()
        walk.caption(walk_caption[5])
        walk.scroll("#primary-action", 1000)
        walk.click("#leave-unsigned", "inventory")
        time.sleep(3)
        walk.click("#next-step", "checkout")
        walk.scroll("top", 400)

    def s6():  # over coffee
        signed_night()
        walk.caption(walk_caption[6])
        walk.click("#next-step", "checkout")
        walk.click("#next-step", "dawn")
        walk.scroll("top", 400)
        time.sleep(3)
        walk.scroll(".quiet-push", 1200)
        time.sleep(4)
        walk.scroll(".stat-grid", 1200)
        time.sleep(4)
        walk.scroll(".morning-list", 1800)

    def s7():  # what lands in GitLab
        walk.scroll(".gitlab-objects", 1500)
        time.sleep(6)
        walk.click("#evidence-details > summary")
        walk.scroll(".ledger-list", 2000)
        time.sleep(4)
        walk.page.locator("summary", has_text="Read the morning record").first.click()
        walk.scroll("summary:has(+ pre)", 1500)

    def s8():  # close
        walk.click("#evidence-details > summary")
        walk.scroll("top", 1500)
        time.sleep(8)
        walk.page.evaluate(TITLE, ["Night Orders", "Before bed, you sign what the agent may do alone tonight. "
                                   "Everything else wakes you.", REPO])

    return [s0, s1, s2, s3, s4, s5, s6, s7, s8]


walk_caption: list[str] = []


def record(out: Path, url: str | None) -> Path:
    global walk_caption
    found = scenes(VIDEO.read_text(encoding="utf-8"), "B")
    walk_caption = [scene.narration for scene in found]
    with tempfile.TemporaryDirectory() as folder, application(url) as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"],
                                             executable_path=os.environ.get("CHROMIUM_EXECUTABLE") or None)
        context = browser.new_context(viewport={"width": VIEW_W, "height": VIEW_H}, device_scale_factor=1,
                                      record_video_dir=folder, record_video_size={"width": VIEW_W, "height": VIEW_H})
        opened = time.monotonic()
        page = context.new_page()
        walk = Walk(page, base)
        walk.fresh()
        actions = plan_b(walk)
        if len(actions) != len(found):
            raise SystemExit(f"Plan B has {len(found)} scenes; this walk knows {len(actions)}")
        start = time.monotonic()
        for scene, action in zip(found, actions):
            walk.caption(scene.narration)
            action()
            walk.caption(scene.narration)
            left = start + scene.end - time.monotonic()
            if left < 0:
                print(f"warning: the scene at {scene.start} s ran {-left:.1f} s over its slot")
            time.sleep(max(0.0, left))
        video = page.video.path() if page.video else None
        context.close()
        browser.close()
        if video is None:
            raise SystemExit("no video was recorded")
        offset = start - opened
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{offset:.2f}", "-i", str(video), "-t",
                        str(found[-1].end), "-vf", f"scale={WIDTH}:{HEIGHT}:flags=lanczos,fps=30", "-c:v", "libx264", "-preset",
                        "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out)],
                       check=True)
    captions = out.with_suffix(".srt")
    captions.write_text(srt(found), encoding="utf-8")
    return captions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / "night-orders-demo.mp4")
    parser.add_argument("--url", help="a running relay's base URL; defaults to a temporary local server")
    args = parser.parse_args(argv)
    if not shutil.which("ffmpeg"):
        print("ffmpeg is needed to encode the video", file=sys.stderr)
        return 2
    captions = record(args.out, args.url)
    length = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                             str(args.out)], capture_output=True, text=True).stdout.strip()
    print(f"wrote {args.out} ({float(length):.1f} s) and {captions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
