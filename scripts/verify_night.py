"""Verify the bounded operational loop with simulated external adapters, never live services."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "relay"))

from nightorders.operational import CASES, markdown, verify  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, action="append", help="run selected cases (default: all six)")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--out", type=Path, help="save the report instead of printing it")
    args = parser.parse_args(argv)
    report = verify(args.case or CASES)
    text = json.dumps(report, indent=2) + "\n" if args.format == "json" else markdown(report)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
