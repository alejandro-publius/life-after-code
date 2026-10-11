"""Release notes for the tagged GitLab Release the pipeline cuts on the default branch.

    python scripts/release_notes.py --out release-notes.md

Every number in them is computed here by the project's own code: the refusal gallery (attempts, production
changes, the control) and the same demo night three ways. Links come from GitLab's CI variables, so the notes
point at this pipeline, this project's Pages demo and its container registry.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "relay")]

from nightorders.compare import compare, table  # noqa: E402
from nightorders.refusals import rows, summary  # noqa: E402


def notes(env: dict) -> str:
    sha = env.get("CI_COMMIT_SHORT_SHA", "local")
    title = env.get("CI_COMMIT_TITLE", "").strip()
    pages, project, pipeline = env.get("CI_PAGES_URL"), env.get("CI_PROJECT_URL"), env.get("CI_PIPELINE_URL")
    lines = [f"Built from `{sha}`" + (f": {title}" if title else "") + ".", ""]
    if pages:
        lines += [f"**Try the demo night in the browser:** {pages}", ""]
    lines += ["## What this release checked", "",
              f"- Refusals: {summary(rows())} The table: [docs/REFUSALS.md]({project}/-/blob/{sha}/docs/REFUSALS.md)."
              if project else f"- Refusals: {summary(rows())}",
              "- The pipeline ran the unit tests with coverage, lint, the phone and laptop browser walk, SAST, IaC "
              "scanning, secret detection, dependency and container scanning, and a hash-checked dependency audit.",
              "", "## The same demo night, three ways", "", table(compare()), "",
              "Demo data: an invented night with planted faults, replayed by the real decision code.", ""]
    if pipeline:
        lines.append(f"Pipeline: {pipeline}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="write the notes here instead of printing them")
    args = parser.parse_args(argv)
    text = notes(dict(os.environ))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
