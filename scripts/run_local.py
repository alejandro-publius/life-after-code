"""Start an isolated loopback-only Night Orders session and its real disposable shop."""

import argparse
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time

import httpx
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "relay"))
from local_main import create_app  # noqa: E402
from nightorders.local_session import LocalSession  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument("--state-dir", type=Path, help="new directory for saved state and the receipt")
    args = parser.parse_args(argv)
    directory = args.state_dir or Path(tempfile.mkdtemp(prefix="night-orders-local-"))
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "session.json").exists():
        parser.error("Use a fresh state directory; existing session evidence is preserved.")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    key, identity = secrets.token_urlsafe(32), secrets.token_hex(16)
    environment = dict(os.environ, LOCAL_SHOP_KEY=key, LOCAL_SHOP_ID=identity,
                       PYTHONPATH=str(ROOT / "shop"), PYTHONDONTWRITEBYTECODE="1")
    session = None
    with (directory / "shop.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-m", "uvicorn", "local_shop:app", "--host", "127.0.0.1",
                                    "--port", str(port), "--no-access-log"], cwd=ROOT / "shop", env=environment,
                                   stdout=log, stderr=log)
        try:
            base = f"http://127.0.0.1:{port}"
            with httpx.Client(trust_env=False, timeout=1) as client:
                for _ in range(100):
                    if process.poll() is not None:
                        raise RuntimeError("Disposable shop failed to start; inspect its local log")
                    try:
                        if client.get(base + "/healthz").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(.1)
                else:
                    raise RuntimeError("Disposable shop did not become ready")
            session = LocalSession(base, key, identity, directory)
            print(f"Local session: http://127.0.0.1:{args.port}  Evidence: {directory}", flush=True)
            uvicorn.run(create_app(session), host="127.0.0.1", port=args.port, access_log=False)
        finally:
            if session:
                try:
                    session.run("finish")
                except Exception as error:
                    print(f"Cleanup did not complete: {type(error).__name__}. Evidence kept in {directory}.", file=sys.stderr)
                session.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
