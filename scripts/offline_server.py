"""Serve a verified Night Orders offline snapshot using Python's standard library."""

import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path


def verify(root: Path) -> dict:
    manifest = json.loads((root / "snapshot.json").read_text())
    if manifest.get("schema") != 1 or not isinstance(manifest.get("files"), dict) or not manifest["files"]:
        raise ValueError("Snapshot manifest is missing its file inventory")
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Missing or invalid snapshot file: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Snapshot file has changed: {name}")
    for required in ("index.html", "activity.html", "activity.json", "assets/app.js", "serve.py"):
        if required not in manifest["files"]:
            raise ValueError(f"Snapshot inventory omits {required}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true", help="verify files without starting a server")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        manifest = verify(root)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Cannot open this snapshot: {error}\nExtract a fresh copy of the bundle.\n")
    print(f"Verified {len(manifest['files'])} files; source {manifest['source']['commit']}", flush=True)
    if args.check:
        return
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *values, **options):
            super().__init__(*values, directory=str(root), **options)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            super().end_headers()

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Cannot start local server: {error}\nTry python3 serve.py --port 0 for a free port.\n")
    print(f"Open http://127.0.0.1:{server.server_port} in your browser. Ctrl+C stops it.", flush=True)
    print("Offline replay and recorded executions. No live service or model calls.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
