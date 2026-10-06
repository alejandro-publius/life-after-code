"""Command line checks used by CI.

    python -m nightorders.cli validate ../ops/night-orders.yml --ops ../ops
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .orders import validate_file

REPO = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nightorders")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate", help="check an orders file against the schema, targets and floor")
    check.add_argument("orders", type=Path)
    check.add_argument("--ops", type=Path, default=REPO / "ops")
    args = parser.parse_args(argv)

    problems = validate_file(args.orders, args.ops)
    if problems:
        print(f"{args.orders}: cannot be signed")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"{args.orders}: ok, ready to sign")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
