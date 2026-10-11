"""Check that every scene's narration in docs/VIDEO.md fits its time slot, and write captions for YouTube.

    python scripts/video_pace.py                  # a table: scene, seconds, words, words per minute
    python scripts/video_pace.py --srt plan-b.srt --plan B

Narration is read at about 150 words a minute; a slot that needs more than MAX_WPM is too full to say calmly,
and the whole video must stay under 3:00 (the official rules). Reads the two shot tables in docs/VIDEO.md:
"Plan A" and "Plan B". The captions are the narration of each row, timed to its slot, in SubRip format.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VIDEO = Path(__file__).resolve().parents[1] / "docs" / "VIDEO.md"
MAX_WPM = 170
LIMIT_SECONDS = 180
ROW = re.compile(r"^\| (\d+):(\d\d) to (\d+):(\d\d) \| (.*?) \| (.*) \|$")


@dataclass(frozen=True)
class Scene:
    start: int
    end: int
    screen: str
    narration: str

    @property
    def seconds(self) -> int:
        return self.end - self.start

    @property
    def words(self) -> int:
        return len(re.findall(r"[A-Za-z0-9']+", self.narration))

    @property
    def wpm(self) -> float:
        return self.words * 60 / self.seconds if self.seconds else 0.0


def scenes(text: str, plan: str) -> list[Scene]:
    """The rows of one plan's shot table, in order."""
    marker = f"## Plan {plan}"
    if marker not in text:
        raise ValueError(f"docs/VIDEO.md has no section starting with {marker!r}")
    section = text.split(marker, 1)[1].split("\n## Plan ", 1)[0]
    found = []
    for line in section.splitlines():
        match = ROW.match(line.strip())
        if match:
            m1, s1, m2, s2, screen, narration = match.groups()
            spoken = narration.strip().strip('"') if narration.strip() != "(none)" else ""
            found.append(Scene(int(m1) * 60 + int(s1), int(m2) * 60 + int(s2), screen.strip(), spoken))
    return found


def problems(found: list[Scene]) -> list[str]:
    out = []
    for before, after in zip(found, found[1:]):
        if after.start != before.end:
            out.append(f"gap or overlap between {clock(before.end)} and {clock(after.start)}")
    for scene in found:
        if scene.seconds <= 0:
            out.append(f"{clock(scene.start)}: the slot has no length")
        elif scene.wpm > MAX_WPM:
            out.append(f"{clock(scene.start)}: {scene.words} words in {scene.seconds} s is {scene.wpm:.0f} words a "
                       f"minute (at most {MAX_WPM})")
    if found and found[-1].end >= LIMIT_SECONDS:
        out.append(f"ends at {clock(found[-1].end)}, not under 3:00")
    return out


def clock(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def srt(found: list[Scene]) -> str:
    def stamp(seconds: int) -> str:
        return f"00:{seconds // 60:02d}:{seconds % 60:02d},000"
    blocks = []
    for number, scene in enumerate([s for s in found if s.narration], start=1):
        blocks.append(f"{number}\n{stamp(scene.start)} --> {stamp(scene.end)}\n{scene.narration}\n")
    return "\n".join(blocks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", choices=["A", "B"], action="append", help="which shot table (default: both)")
    parser.add_argument("--srt", type=Path, help="write captions for the one plan given with --plan")
    args = parser.parse_args(argv)
    text = VIDEO.read_text(encoding="utf-8")
    plans = args.plan or ["A", "B"]
    failed = False
    for plan in plans:
        found = scenes(text, plan)
        print(f"Plan {plan}: {len(found)} scenes, ends at {clock(found[-1].end)}")
        for scene in found:
            print(f"  {clock(scene.start)}-{clock(scene.end)}  {scene.seconds:>3} s  {scene.words:>3} words  "
                  f"{scene.wpm:>4.0f} wpm")
        for problem in problems(found):
            print(f"  PROBLEM: {problem}")
            failed = True
    if args.srt:
        if len(plans) != 1:
            print("--srt needs exactly one --plan", file=sys.stderr)
            return 2
        args.srt.write_text(srt(scenes(text, plans[0])), encoding="utf-8")
        print(f"wrote {args.srt}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
