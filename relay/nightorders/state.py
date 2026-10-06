"""The relay's memory between ticks, kept as one JSON document.

The Watch keeps its incidents and the ledger in memory, but Cloud Run scales to zero between ticks. Each
tick restores a Watch from this document, runs one tick and saves the document again. Times are stored as
ISO 8601 text with their offset.

A night's record runs from noon to noon in the on-call person's time zone: noon is when orders may first
be signed (orders.watch_window). At noon a new record starts with an empty ledger. Open incidents carry
over, so an alert that is still firing does not open a second incident or page twice.

Document layout:

    {"version": 1, "night": "2026-10-20",
     "watch": {"expired": false, "expired_orders": null, "incidents": [...], "ledger": [...]},
     "ports": {...},   # the ports' own memory, maps keyed by incident number
     "relay": {...}}   # the relay's status and last watch log, for the status page

Stores:
  FileStore  a local JSON file, for tests and local runs
  GcsStore   one object in a Cloud Storage bucket, through the JSON API with the metadata-server token.
             A save only succeeds if nobody saved since this tick loaded (ifGenerationMatch), so two ticks
             never silently overwrite each other.
             API: https://storage.googleapis.com/$discovery/rest?version=v1 (objects.get, objects.insert)
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from .decide import Ask
from .ledger import Event, Ledger
from .model import Action, Alert, Condition, OnCall, Order, Orders
from .orders import watch_window
from .watch import Incident, Watch

VERSION = 1
STORAGE_API = "https://storage.googleapis.com"


class StateError(RuntimeError):
    """The saved state cannot be used."""


class StateConflict(StateError):
    """Someone else saved the state after this tick loaded it."""


def night_of(now: datetime, oncall: OnCall) -> str:
    """The night a moment belongs to: from noon on that date to noon the next day, local time."""
    return (oncall.local(now) - timedelta(hours=12)).date().isoformat()


def new_document(night: str) -> dict:
    return {
        "version": VERSION,
        "night": night,
        "watch": {"expired": False, "expired_orders": None, "incidents": [], "ledger": []},
        "ports": {},
        "relay": {},
    }


def check(doc: Any) -> dict | None:
    """A loaded document, or None for a first run. Refuses a document this code cannot read."""
    if doc is None:
        return None
    if not isinstance(doc, dict) or doc.get("version") != VERSION:
        version = doc.get("version") if isinstance(doc, dict) else None
        raise StateError(f"the saved state has version {version}, this relay reads version {VERSION}")
    return doc


def _time(moment: datetime | None) -> str | None:
    return None if moment is None else moment.isoformat()


def _moment(text: str | None) -> datetime | None:
    return None if text is None else datetime.fromisoformat(text)


def dump_event(event: Event) -> dict:
    return {"at": _time(event.at), "kind": event.kind, "text": event.text, "incident": event.incident,
            "order": event.order, "data": event.data}


def load_event(data: dict) -> Event:
    return Event(at=datetime.fromisoformat(data["at"]), kind=data["kind"], text=data["text"],
                 incident=data.get("incident"), order=data.get("order"), data=dict(data.get("data") or {}))


def _dump_order(order: Order) -> dict:
    return {"id": order.id, "because": order.because, "when": asdict(order.when), "do": asdict(order.do)}


def _load_order(data: dict) -> Order:
    return Order(id=int(data["id"]), because=data["because"], when=Condition(**data["when"]), do=Action(**data["do"]))


def dump_incident(incident: Incident) -> dict:
    ask = incident.ask
    return {
        "number": incident.number,
        "alerts": [{"key": a.key, "value": a.value, "at": _time(a.at)} for a in incident.alerts],
        "opened_at": _time(incident.opened_at),
        "ask": None if ask is None else {"eligible": list(ask.eligible),
                                         "checks": {str(k): v for k, v in ask.checks.items()}},
        "asked_at": _time(incident.asked_at),
        "paged_at": _time(incident.paged_at),
        "suggest": None if incident.suggest is None else asdict(incident.suggest),
        "acted": None if incident.acted is None else _dump_order(incident.acted),
        "acted_at": _time(incident.acted_at),
        "closed": incident.closed,
        "keys": sorted(incident.keys),
    }


def load_incident(data: dict) -> Incident:
    ask = data.get("ask")
    return Incident(
        number=int(data["number"]),
        alerts=[Alert(key=a["key"], value=float(a["value"]), at=datetime.fromisoformat(a["at"]))
                for a in data["alerts"]],
        opened_at=datetime.fromisoformat(data["opened_at"]),
        ask=None if ask is None else Ask(eligible=tuple(int(i) for i in ask["eligible"]),
                                         checks={int(k): v for k, v in ask["checks"].items()}),
        asked_at=_moment(data.get("asked_at")),
        paged_at=_moment(data.get("paged_at")),
        suggest=None if data.get("suggest") is None else Action(**data["suggest"]),
        acted=None if data.get("acted") is None else _load_order(data["acted"]),
        acted_at=_moment(data.get("acted_at")),
        closed=bool(data.get("closed")),
        keys=set(data.get("keys") or []),
    )


def load_ledger(doc: dict) -> Ledger:
    ledger = Ledger()
    ledger.events = [load_event(item) for item in doc["watch"]["ledger"]]
    return ledger


def restore(watch: Watch, doc: dict) -> None:
    """Put the saved incidents and expired flag into a Watch built with load_ledger(doc).

    The expired flag belongs to one orders file: if tonight's file is a different night, it starts unset.
    """
    saved = doc["watch"]
    watch.incidents = [load_incident(item) for item in saved["incidents"]]
    orders = watch.night.orders
    watch.expired = (bool(saved.get("expired")) and orders is not None
                     and saved.get("expired_orders") == orders.night.isoformat())


def capture(watch: Watch, doc: dict) -> None:
    """Write the Watch's incidents, ledger and expired flag into the document."""
    saved = doc["watch"]
    saved["incidents"] = [dump_incident(i) for i in watch.incidents]
    saved["ledger"] = [dump_event(e) for e in watch.night.ledger.events]
    orders = watch.night.orders
    if orders is not None:  # with no orders file the flag cannot change, so keep what it was about
        saved["expired"] = watch.expired
        saved["expired_orders"] = orders.night.isoformat() if watch.expired else None


def next_night(doc: dict, night: str, orders: Orders | None, oncall: OnCall, now: datetime) -> dict:
    """Start a new night's record. Open incidents and their port memory carry over; the ledger starts empty.

    Orders that had already ended before this record began count as expired, so their old expiry is not
    written into the new night's log.
    """
    fresh = new_document(night)
    still_open = [item for item in doc["watch"]["incidents"] if not item.get("closed")]
    fresh["watch"]["incidents"] = still_open
    keep = {str(item["number"]) for item in still_open}
    fresh["ports"] = {name: {k: v for k, v in entries.items() if k in keep}
                      for name, entries in (doc.get("ports") or {}).items() if isinstance(entries, dict)}
    fresh["relay"] = dict(doc.get("relay") or {})
    if orders is not None and now >= watch_window(orders, oncall)[1]:
        fresh["watch"]["expired"] = True
        fresh["watch"]["expired_orders"] = orders.night.isoformat()
    return fresh


def encode(doc: dict) -> bytes:
    return json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False).encode("utf-8")


class FileStore:
    """The state as a local JSON file. The version token is unused."""

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def load(self) -> tuple[dict | None, None]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None, None
        return json.loads(text), None

    def save(self, doc: dict, version: object = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        partial = self.path.with_name(self.path.name + ".partial")
        partial.write_bytes(encode(doc))
        partial.replace(self.path)


class GcsStore:
    """The state as one Cloud Storage object. The version token is the object's generation ("0": none yet)."""

    def __init__(self, bucket: str, name: str, http: Any, token: Callable[[], str]):
        self.bucket = bucket
        self.name = name
        self.http = http      # gitlab_ports.Http: 10 second timeout, safe error messages
        self.token = token    # gitlab_ports.GoogleToken: the metadata-server access token

    def _object_url(self) -> str:
        return f"{STORAGE_API}/storage/v1/b/{quote(self.bucket, safe='')}/o/{quote(self.name, safe='')}"

    def load(self) -> tuple[dict | None, str]:
        headers = {"Authorization": f"Bearer {self.token()}"}
        meta = self.http.call("Cloud Storage read state", "GET", self._object_url(), headers=headers,
                              expect=(200, 404))
        if meta.status_code == 404:
            return None, "0"
        generation = str(meta.json()["generation"])
        body = self.http.call("Cloud Storage read state", "GET", self._object_url(), headers=headers,
                              params={"alt": "media", "generation": generation})
        return json.loads(body.content), generation

    def save(self, doc: dict, version: object = "0") -> None:
        headers = {"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"}
        params = {"uploadType": "media", "name": self.name, "ifGenerationMatch": str(version or "0")}
        response = self.http.call("Cloud Storage save state", "POST",
                                  f"{STORAGE_API}/upload/storage/v1/b/{quote(self.bucket, safe='')}/o",
                                  headers=headers, params=params, content=encode(doc), expect=(200, 412))
        if response.status_code == 412:
            raise StateConflict("another tick saved the state first; this tick's record was not saved")
