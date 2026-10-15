"""The relay's memory between ticks, kept as one JSON document.

The Watch keeps its incidents and the ledger in memory, but Cloud Run scales to zero between ticks. Each
tick restores a Watch from this document, runs one tick and saves the document again. Times are stored as
ISO 8601 text with their offset.

A night's record runs from noon to noon in the on-call person's time zone: noon is when orders may first
be signed (orders.watch_window). At noon a new record starts with an empty ledger. Open incidents carry
over, so an alert that is still firing does not open a second incident or page twice. If no good tick came
between the watch end and noon, the morning has not made its record of that night yet: the night's ledger,
orders and signature are then kept under watch.earlier until it has (earlier_nights, forget_recorded).

Document layout:

    {"version": 1, "night": "2026-10-20",
     "watch": {"expired": false, "expired_orders": null, "incidents": [...], "ledger": [...],
               "orders": {...}, "signature": {...}, "earlier": [...]},
     "ports": {...},   # the ports' own memory, maps keyed by incident number
     "relay": {...}}   # the relay's status and last watch log, for the status page

Stores:
  FileStore  a local JSON file, for tests and local runs
  GcsStore   one object in a Cloud Storage bucket, through the JSON API with the metadata-server token.
             A save only succeeds if nobody saved since this tick loaded (ifGenerationMatch), so two ticks
             never silently overwrite each other.
             API: https://storage.googleapis.com/$discovery/rest?version=v1 (objects.get, objects.insert,
             objects.delete)

Both stores also hold the tick lease: acquire(now) gives a token to one tick at a time, across Cloud Run
instances, and release(token) frees it. A lease older than LEASE_SECONDS counts as left behind by a crashed
tick and may be taken over, so it never blocks the relay for good.
"""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from .decide import Ask, Night, Wake
from .ledger import Event, Ledger
from .model import Action, Alert, Condition, OnCall, Order, Orders, Signature, Targets
from .orders import watch_window
from .watch import Incident, Watch

VERSION = 1
STORAGE_API = "https://storage.googleapis.com"
LEASE_SECONDS = 90


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


def _dump_orders(orders: Orders) -> dict:
    return {"night": orders.night.isoformat(), "expires": orders.expires.strftime("%H:%M"),
            "orders": [_dump_order(o) for o in orders.orders], "drafted_by": orders.drafted_by}


def _load_orders(data: dict) -> Orders:
    return Orders(night=date.fromisoformat(data["night"]), expires=time.fromisoformat(data["expires"]),
                  orders=tuple(_load_order(o) for o in data["orders"]), drafted_by=data.get("drafted_by"))


def _dump_signature(signature: Signature | None) -> dict | None:
    return None if signature is None else {**asdict(signature), "at": signature.at.isoformat()}


def _load_signature(data: dict | None) -> Signature | None:
    return None if data is None else Signature(**{**data, "at": datetime.fromisoformat(data["at"])})


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
        "unsent_page": None if incident.unsent_page is None else _dump_wake(incident.unsent_page),
        "orders_end": _time(incident.orders_end),
    }


def _dump_wake(wake: Wake) -> dict:
    return {"reasons": list(wake.reasons), "page": list(wake.page),
            "suggest": None if wake.suggest is None else asdict(wake.suggest)}


def _load_wake(data: dict) -> Wake:
    return Wake(reasons=tuple(data["reasons"]), page=tuple(data["page"]),
                suggest=None if data.get("suggest") is None else Action(**data["suggest"]))


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
        unsent_page=None if data.get("unsent_page") is None else _load_wake(data["unsent_page"]),
        orders_end=_moment(data.get("orders_end")),
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
        # What the morning needs to make its record of the night, should no good tick come before noon.
        saved["orders"], saved["signature"] = _dump_orders(orders), _dump_signature(watch.night.signature)


def _recorded(doc: dict, night: str) -> bool:
    """Whether the morning has made its record of this night, or of a later one (which carries it)."""
    dawn = (doc.get("relay") or {}).get("dawn") or {}
    return str(dawn.get("night") or "") >= night


def next_night(doc: dict, night: str, orders: Orders | None, oncall: OnCall, now: datetime) -> dict:
    """Start a new night's record. Open incidents and their port memory carry over; the ledger starts empty.

    Orders that had already ended before this record began count as expired, so their old expiry is not
    written into the new night's log. A night whose orders ended without the morning making its record (no
    good tick from the watch end to noon) keeps its ledger, orders and signature under watch.earlier, so its
    loose ends still reach the countersign.
    """
    fresh = new_document(night)
    earlier = list(doc["watch"].get("earlier") or [])
    ended = doc["watch"].get("orders")
    if ended is not None and ended["night"] == doc["night"] and not _recorded(doc, ended["night"]):
        earlier.append({"orders": ended, "signature": doc["watch"].get("signature"), "ledger": doc["watch"]["ledger"]})
    if earlier:
        fresh["watch"]["earlier"] = earlier
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


def earlier_nights(doc: dict, oncall: OnCall, targets: Targets) -> list[Night]:
    """The nights kept under watch.earlier, oldest first, each with its own orders, signature and ledger, for
    the morning to make its record of."""
    nights = []
    for item in doc["watch"].get("earlier") or []:
        ledger = Ledger()
        ledger.events = [load_event(event) for event in item["ledger"]]
        nights.append(Night(oncall=oncall, targets=targets, orders=_load_orders(item["orders"]), orders_problems=(),
                            signature=_load_signature(item.get("signature")), ledger=ledger))
    return nights


def forget_recorded(doc: dict, finished: list[Night]) -> None:
    """Drop the earlier nights whose morning step ran to the end: their record is made, and the watch log, the push
    and the dawn flow, which are written from that night's own ledger and orders, have been tried. A step that
    raised partway keeps its night for the next tick."""
    done = {night.orders.night.isoformat() for night in finished if night.orders is not None}
    earlier = doc["watch"].get("earlier")
    if earlier:
        doc["watch"]["earlier"] = [item for item in earlier if item["orders"]["night"] not in done]


def encode(doc: dict) -> bytes:
    return json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False).encode("utf-8")


def new_lease(now: datetime) -> tuple[str, bytes]:
    """A fresh lease: its token and the JSON body that records when it was taken."""
    token = secrets.token_hex(8)
    return token, encode({"since": now.isoformat(), "token": token})


def lease_stale(body: bytes | None, now: datetime, fallback: datetime | None = None) -> bool:
    """Whether a lease is old enough to take over. An unreadable lease counts by its fallback time, else as stale."""
    since = fallback
    try:
        since = datetime.fromisoformat(json.loads(body or b"")["since"])
    except (ValueError, TypeError, KeyError):
        pass
    if since is None:
        return True
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    return now - since >= timedelta(seconds=LEASE_SECONDS)


class FileStore:
    """The state as a local JSON file. The version token is unused. The lease is a file next to it."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.lease_path = self.path.with_name(self.path.name + ".lease")

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

    def acquire(self, now: datetime) -> str | None:
        """Take the tick lease: a token, or None while another tick holds a fresh one."""
        token, body = new_lease(now)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.lease_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            try:
                existing = self.lease_path.read_bytes()
                touched = datetime.fromtimestamp(self.lease_path.stat().st_mtime, timezone.utc)
            except FileNotFoundError:  # released just now; the next tick is a minute away
                return None
            if not lease_stale(existing, now, touched):
                return None
            self.lease_path.write_bytes(body)  # left behind by a crashed tick: take it over
            return token
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
        return token

    def release(self, token: str) -> None:
        """Free the lease, unless another tick has taken it over meanwhile."""
        try:
            held = json.loads(self.lease_path.read_bytes()).get("token")
        except (FileNotFoundError, ValueError, AttributeError):
            return
        if held == token:
            try:
                self.lease_path.unlink()
            except FileNotFoundError:
                pass


class GcsStore:
    """The state as one Cloud Storage object. The version token is the object's generation ("0": none yet).

    The lease is a second object, <name>.lease, created only when it does not exist (ifGenerationMatch=0).
    """

    def __init__(self, bucket: str, name: str, http: Any, token: Callable[[], str]):
        self.bucket = bucket
        self.name = name
        self.http = http      # gitlab_ports.Http: 10 second timeout, safe error messages
        self.token = token    # gitlab_ports.GoogleToken: the metadata-server access token
        self._leases: dict[str, str] = {}  # lease token -> the generation this store created

    def _object_url(self, name: str | None = None) -> str:
        return f"{STORAGE_API}/storage/v1/b/{quote(self.bucket, safe='')}/o/{quote(name or self.name, safe='')}"

    def load(self) -> tuple[dict | None, str]:
        headers = {"Authorization": f"Bearer {self.token()}"}
        meta = self.http.call("Cloud Storage read state", "GET", self._object_url(), headers=headers,
                              expect=(200, 404))
        if meta.status_code == 404:
            if "bucket does not exist" in meta.text.lower():
                raise StateError("the state bucket does not exist")
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

    def _put_lease(self, body: bytes, generation: str) -> str | None:
        """Write the lease object if it is at that generation ("0": absent). The new generation, or None on 412."""
        headers = {"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"}
        params = {"uploadType": "media", "name": self.name + ".lease", "ifGenerationMatch": generation}
        response = self.http.call("Cloud Storage take the tick lease", "POST",
                                  f"{STORAGE_API}/upload/storage/v1/b/{quote(self.bucket, safe='')}/o",
                                  headers=headers, params=params, content=body, expect=(200, 412))
        return None if response.status_code == 412 else str(response.json()["generation"])

    def acquire(self, now: datetime) -> str | None:
        """Take the tick lease: a token, or None while another instance holds a fresh one."""
        token, body = new_lease(now)
        generation = self._put_lease(body, "0")
        if generation is None:
            headers = {"Authorization": f"Bearer {self.token()}"}
            url = self._object_url(self.name + ".lease")
            meta = self.http.call("Cloud Storage read the tick lease", "GET", url, headers=headers,
                                  expect=(200, 404))
            if meta.status_code == 404:  # released just now; the next tick is a minute away
                return None
            held = str(meta.json()["generation"])
            existing = self.http.call("Cloud Storage read the tick lease", "GET", url, headers=headers,
                                      params={"alt": "media", "generation": held}, expect=(200, 404))
            if existing.status_code == 404:  # released or taken over between the two reads
                return None
            if not lease_stale(existing.content, now):
                return None
            generation = self._put_lease(body, held)  # left behind by a crashed tick: take it over
            if generation is None:
                return None
        self._leases[token] = generation
        return token

    def release(self, token: str) -> None:
        """Delete the lease this store created. Gone already (404) or taken over (412) is fine."""
        generation = self._leases.pop(token, None)
        if generation is None:
            return
        self.http.call("Cloud Storage release the tick lease", "DELETE", self._object_url(self.name + ".lease"),
                       headers={"Authorization": f"Bearer {self.token()}"},
                       params={"ifGenerationMatch": generation}, expect=(204, 404, 412))
