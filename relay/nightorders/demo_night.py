"""Replay a labelled demo night through the same Watch the relay runs in production.

    cd relay && python -m nightorders.demo_night ../demo/night-2026-10-20

The shop, its traffic and both faults are simulated (demo data). The watch flow's answers are
recorded notes in the format the real flow writes. The decisions are made by the real code.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from time import monotonic

from .countersign import parse_state, plan_morning
from .dawn import loose_ends, render_watch_log
from .decide import Night
from .ledger import Ledger
from .model import Action, Signature
from .notes import Request, render_request
from .orders import OrdersError, load_yaml, parse_oncall, parse_orders, parse_targets
from .signals import Metrics
from .watch import Watch, parse_alert_rules

REPO = Path(__file__).resolve().parents[2]
MAX_DEMO_STEPS = 960
MAX_DEMO_SECONDS = 10


@dataclass
class DemoShop:
    """A tiny model of the demo shop: error rates per checkout path given flags and faults."""

    flags: dict[str, str]
    faults: list[tuple[str, datetime, datetime]]
    new_share: float

    def active(self, name: str, at: datetime) -> bool:
        return any(n == name and start <= at < end for n, start, end in self.faults)

    def minute_metrics(self, at: datetime) -> dict[str, float]:
        new_on = self.flags.get("new_checkout") == "on"
        cache_on = self.flags.get("stock_from_cache") == "on"
        inventory_down = self.active("inventory_slow", at) and not cache_on
        old = 0.003 + (0.200 if inventory_down else 0.0)
        new = (0.004 + (0.075 if self.active("rounding_bug", at) else 0.0) + (0.200 if inventory_down else 0.0)) if new_on else 0.0
        share = self.new_share if new_on else 0.0
        overall = old * (1 - share) + new * share
        return {
            "checkout_error_rate.old": round(old, 4),
            "checkout_error_rate.new": round(new, 4),
            "checkout_error_rate.all": round(overall, 4),
            "payment_error_rate": 0.002,
            "http_5xx_ratio": round(overall * 0.6, 4),
            "p95_latency_ms": 420.0 + (900.0 if inventory_down else 0.0),
        }


@dataclass
class RecordingPorts:
    """Ports that record what the relay would do, and serve the recorded watch-flow notes."""

    oncall_tz: object
    shop: DemoShop
    notes: dict[int, tuple[int, str]]
    reactions: dict[int, tuple[str, datetime]]
    log: list[str] = field(default_factory=list)
    asked_at: dict[int, datetime] = field(default_factory=dict)
    next_incident: int = 1
    samples: list[dict] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)

    def _t(self, at: datetime) -> str:
        return at.astimezone(self.oncall_tz).strftime("%H:%M")

    def open_incident(self, title: str, description: str, at: datetime) -> int:
        number = self.next_incident
        self.next_incident += 1
        self.log.append(f"{self._t(at)}  incident #{number} opened: {title}")
        return number

    def note(self, incident: int, text: str, at: datetime) -> None:
        self.log.append(f"{self._t(at)}  note on #{incident}: {text}")

    def start_watch_flow(self, incident: int, goal: str, at: datetime) -> None:
        self.asked_at[incident] = at
        self.log.append(f"{self._t(at)}  recorded watch reply requested for #{incident} (demo, no API call)")

    def request_note(self, incident: int, at: datetime) -> str | None:
        if incident not in self.notes or incident not in self.asked_at:
            return None
        delay, text = self.notes[incident]
        if at >= self.asked_at[incident] + timedelta(minutes=delay):
            if not any(line.endswith(f"agent note on #{incident} (recorded)") for line in self.log):
                self.log.append(f"{self._t(at)}  agent note on #{incident} (recorded)")
            return text
        return None

    def apply(self, action: Action, at: datetime) -> None:
        before = dict(self.shop.flags)
        if action.kind == "flag_set":
            self.shop.flags[action.flag] = action.to  # type: ignore[index]
        self.actions.append({"at": at.isoformat(), "action": action.as_dict(),
                             "flags_before": before, "flags_after": dict(self.shop.flags)})
        self.log.append(f"{self._t(at)}  APPLY {action.describe()}")

    def page(self, incident: int, lines: tuple[str, ...], at: datetime) -> None:
        self.log.append(f"{self._t(at)}  PAGE (phone lights up) for #{incident}: " + " | ".join(lines))

    def thumbs_up(self, incident: int, at: datetime) -> list[tuple[str, datetime]]:
        reaction = self.reactions.get(incident)
        return [reaction] if reaction and at >= reaction[1] else []

    def close_incident(self, incident: int, text: str, at: datetime) -> None:
        self.log.append(f"{self._t(at)}  incident #{incident} closed: {text}")


def _local(text: str, tz) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=tz)


def run(folder: Path | str, ops: Path | str | None = None, *, signed: bool = True,
        approved: bool = True, collect_samples: bool = False) -> tuple[RecordingPorts, Night]:
    """Replay files with optional human choices. All side effects stay in memory."""
    for name, value in (("signed", signed), ("approved", approved), ("collect_samples", collect_samples)):
        if type(value) is not bool:
            raise TypeError(f"{name} must be a boolean")
    folder = Path(folder)
    ops = Path(ops) if ops else REPO / "ops"
    oncall = parse_oncall(load_yaml(ops / "oncall.yml"))
    targets = parse_targets(load_yaml(ops / "targets.yml"))
    rules = parse_alert_rules(load_yaml(ops / "alerts.yml"))
    tz = oncall.timezone

    problems: tuple[str, ...] = ()
    try:
        orders = parse_orders(load_yaml(folder / "orders.yml"), targets, oncall)
    except OrdersError as error:
        orders, problems = None, tuple(error.problems)
    signature = None
    if signed:
        sig = json.loads((folder / "signature.json").read_text())
        signature = Signature(method=sig["method"], user=sig["user"], at=datetime.fromisoformat(sig["at"]),
                              commit=sig["commit"])
    night = Night(oncall=oncall, targets=targets, orders=orders, orders_problems=problems,
                  signature=signature, ledger=Ledger())

    scenario = load_yaml(folder / "scenario.yml")
    shop = DemoShop(
        flags={k: ("on" if v is True else "off" if v is False else str(v)) for k, v in scenario["flags"].items()},
        faults=[(f["name"], _local(f["from"], tz), _local(f["to"], tz)) for f in scenario["faults"]],
        new_share=float(scenario.get("new_path_share", 0.5)),
    )
    raw_notes = json.loads((folder / "notes.json").read_text())["incidents"]
    notes = {}
    for number, item in raw_notes.items():
        r = item["request"]
        declined = r.get("declined") or {}
        request = Request(order=r.get("order"), fits_because=r.get("fits_because"),
                          declined_id=declined.get("id"), declined_why=declined.get("why"),
                          page=tuple(r.get("page") or ()), suggest=r.get("suggest"))
        notes[int(number)] = (int(item["arrives_after_minutes"]), render_request(request))
    raw_reactions = json.loads((folder / "reactions.json").read_text())["incidents"] if approved else {}
    reactions = {int(k): (v["user"], datetime.fromisoformat(v["at"])) for k, v in raw_reactions.items()}

    ports = RecordingPorts(oncall_tz=tz, shop=shop, notes=notes, reactions=reactions)
    watch = Watch(night, ports, rules)
    metrics = Metrics()
    now = _local(scenario["start"], tz)
    end = _local(scenario["end"], tz)
    steps = int((end - now).total_seconds() // 60) + 1
    if not 1 <= steps <= MAX_DEMO_STEPS:
        raise ValueError(f"A demo night must contain between 1 and {MAX_DEMO_STEPS} minute steps")
    deadline = monotonic() + MAX_DEMO_SECONDS
    for minute in range(steps):
        if monotonic() >= deadline:
            raise TimeoutError(f"Demo replay exceeded {MAX_DEMO_SECONDS} seconds")
        # The minute that just ended, as the shop experienced it with the flags of that minute.
        sampled_at = now - timedelta(minutes=1)
        values = shop.minute_metrics(sampled_at)
        before = dict(shop.flags)
        for key, value in values.items():
            metrics.put(key, now - timedelta(minutes=1), value)
        watch.tick(metrics, now)
        if collect_samples:
            ports.samples.append({
                "minute": minute, "at": now.isoformat(), "sampled_at": sampled_at.isoformat(),
                "time": ports._t(now), "old_rate": values["checkout_error_rate.old"],
                "new_rate": values["checkout_error_rate.new"], "all_rate": values["checkout_error_rate.all"],
                "flags_before": before, "flags_after": dict(shop.flags),
            })
        now += timedelta(minutes=1)
    return ports, night


def countersign(folder: Path | str, ports: RecordingPorts, night: Night) -> list[str]:
    """The morning: apply the merged countersign (countersign.yml in the demo folder) the way the relay does."""
    path = Path(folder) / "countersign.yml"
    if not path.exists():
        return []
    data = load_yaml(path)
    at = _local(data["merged_at"], night.oncall.timezone)
    plan = plan_morning(loose_ends(night), parse_state(data.get("state"), night.targets))
    lines = [f"{ports._t(at)}  countersign merged by {night.oncall.first_name} ({data['merged_by']})"]
    lines += [f"{ports._t(at)}  KEEP {item.action.describe()}, until {item.until}" for item in plan.kept]
    for action, why in plan.undo:
        ports.apply(action, at)
        lines.append(f"{ports._t(at)}  UNDO {action.describe()}: {why}")
    lines += [f"{ports._t(at)}  FOR A PERSON: {text}" for text in plan.by_hand]
    return lines


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    folder = Path(args[0]) if args else REPO / "demo" / "night-2026-10-20"
    ports, night = run(folder)
    print("DEMO NIGHT (demo data, planted faults, recorded agent notes). Real decision code.\n")
    for line in ports.log:
        print(line)
    print()
    print(render_watch_log(night).rstrip("\n"))
    morning = countersign(folder, ports, night)
    if morning:
        print()
        print("## Countersign (demo data: merged in the morning)")
        print()
        for line in morning:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
