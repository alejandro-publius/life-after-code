"""The same demo night, three ways, counted by the same code: signed with the watch flow, signed under
standing orders (no model at night), and unsigned. Every number comes from the Watch's own ledger.

    python -m nightorders.compare ../demo/night-2026-10-20
"""

from __future__ import annotations

import sys
from pathlib import Path

from .decide import Night
from .demo_night import REPO, run

WAYS = (
    ("signed", "Signed, the watch flow checks the reason (as designed)", {"signed": True, "approved": True}),
    ("standing", "Signed, standing orders: no model at night", {"signed": True, "approved": True, "standing": True}),
    ("unsigned", "Nothing signed", {"signed": False, "approved": True}),
)
COLUMNS = (
    ("wake_ups", "Wake-ups"),
    ("fix_offered", "Wake-ups with a fix to approve"),
    ("handled_asleep", "Faults handled while she slept"),
    ("did_not_help", "Changes that did not help"),
)


def counts(night: Night) -> dict[str, int]:
    """What one replayed night did, from its ledger."""
    events = night.ledger.events
    woke = [e for e in events if e.kind == "woke"]
    acted = {e.incident for e in events if e.kind == "acted"}
    recovered = {e.incident for e in events if e.kind == "recovered"}
    woken_after = {e.incident for e in woke if e.incident in acted}
    return {
        "wake_ups": len(woke),
        "fix_offered": sum(1 for e in woke if any(str(line).startswith("Thumbs-up") for line in e.data.get("page", []))),
        "handled_asleep": len((acted & recovered) - woken_after),
        "did_not_help": len(woken_after),
    }


def compare(folder: Path | str | None = None, ops: Path | str | None = None) -> list[dict]:
    folder = Path(folder) if folder else REPO / "demo" / "night-2026-10-20"
    rows = []
    for key, label, options in WAYS:
        _ports, night = run(folder, ops, **options)
        rows.append({"way": key, "label": label, **counts(night)})
    return rows


def table(rows: list[dict]) -> str:
    """A Markdown table, the same text the README carries between its compare markers."""
    head = "| The same demo night | " + " | ".join(title for _key, title in COLUMNS) + " |"
    rule = "|---|" + "---|" * len(COLUMNS)
    body = [f"| {row['label']} | " + " | ".join(str(row[key]) for key, _title in COLUMNS) + " |" for row in rows]
    return "\n".join([head, rule, *body])


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    rows = compare(args[0] if args else None)
    print("DEMO NIGHT, THREE WAYS (demo data, planted faults, recorded agent notes). Counted by the real Watch code.\n")
    print(table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
