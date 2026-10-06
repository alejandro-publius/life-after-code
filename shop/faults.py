"""Planted demo faults: switches that make the demo shop fail on purpose during a demo night.

Each fault is labelled "planted demo fault" wherever it shows: log lines, the shop page and API answers.
Switch them with POST /demo/faults (needs DEMO_KEY) or, for scripted runs, the FAULTS env var.
"""

from __future__ import annotations

import jsonlog

LABEL = "planted demo fault"

FAULTS: dict[str, str] = {
    "rounding_bug": (
        "The new checkout path cannot round a price that has more than two decimals after the region step."
    ),
    "inventory_slow": (
        "Stock lookups take about a second and one in five times out. Checkout fails on both paths "
        "unless stock_from_cache is on."
    ),
}


class UnknownFault(ValueError):
    """A fault name that is not in FAULTS."""


def planted(exc: Exception, fault: str) -> Exception:
    """Mark an exception as caused by a planted demo fault, so its log line and API answer say so."""
    exc.planted_fault = fault  # type: ignore[attr-defined]
    return exc


class Faults:
    """Which planted faults are on. Everything starts off unless FAULTS or a demo call says otherwise."""

    def __init__(self) -> None:
        self._on = {name: False for name in FAULTS}

    def on(self, name: str) -> bool:
        return self._on.get(name, False)

    def active(self) -> list[str]:
        return [name for name, on in self._on.items() if on]

    def as_dict(self) -> dict[str, bool]:
        return dict(self._on)

    def set(self, changes: dict[str, bool], source: str) -> dict[str, bool]:
        """Switch faults on or off. Unknown names change nothing and raise UnknownFault."""
        unknown = sorted(set(changes) - set(FAULTS))
        if unknown:
            raise UnknownFault(f"Unknown fault: {', '.join(unknown)}. Known faults: {', '.join(FAULTS)}.")
        for name, value in changes.items():
            value = bool(value)
            if self._on[name] != value:
                self._on[name] = value
                jsonlog.emit("NOTICE", f"{LABEL} {name} switched {'on' if value else 'off'} ({source})",
                             fault=name, label=LABEL, on=value, source=source)
        return self.as_dict()
