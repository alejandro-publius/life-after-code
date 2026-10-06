"""Command line checks used by CI.

    python -m nightorders.cli validate ../ops/night-orders.yml --ops ../ops
    python -m nightorders.cli state ../ops/state.yml --ops ../ops
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .countersign import parse_state
from .orders import OrdersError, load_context, load_yaml, validate_file

REPO = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nightorders")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate", help="check an orders file against the schema, targets and floor")
    check.add_argument("orders", type=Path)
    check.add_argument("--ops", type=Path, default=REPO / "ops")
    state = sub.add_parser("state", help="check the countersign file (ops/state.yml) against the targets")
    state.add_argument("state", type=Path)
    state.add_argument("--ops", type=Path, default=REPO / "ops")
    args = parser.parse_args(argv)

    if args.command == "state":
        _oncall, targets = load_context(args.ops)
        try:
            kept = parse_state(load_yaml(args.state), targets)
        except OrdersError as error:
            return _report(args.state, "cannot be countersigned", error.problems)
        print(f"{args.state}: ok, keeps {len(kept)} change{'s' if len(kept) != 1 else ''}; every other night change is undone")
        return 0

    problems = validate_file(args.orders, args.ops)
    if problems:
        return _report(args.orders, "cannot be signed", problems)
    print(f"{args.orders}: ok, ready to sign")
    return 0


def _report(path: Path, verdict: str, problems: list[str]) -> int:
    print(f"{path}: {verdict}")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
