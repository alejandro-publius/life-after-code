"""Run the demo shop in this process on a free local port, for tests and the bench."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import socket
import threading
import time
from typing import Iterator
import urllib.error
import urllib.request

import uvicorn

from nomouse.shop.app import create_app


@contextmanager
def serve(variants_dir: Path | None = None, *, ready_seconds: float = 15) -> Iterator[str]:
    """Yield the base URL of a running shop; stop it afterwards."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    config = uvicorn.Config(create_app(variants_dir), host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="nomouse-shop", daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + ready_seconds
    try:
        while True:
            try:
                with opener.open(base + "/healthz", timeout=1) as response:
                    if json.load(response).get("ok"):
                        break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass
            if time.monotonic() > deadline or not thread.is_alive():
                raise RuntimeError("the demo shop did not start")
            time.sleep(0.05)
        yield base
    finally:
        server.should_exit = True
        thread.join(timeout=10)
