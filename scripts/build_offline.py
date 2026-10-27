"""Build the interactive replay and execution explorer as a portable offline ZIP."""

from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_pages import build  # noqa: E402


def source() -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=5).strip()
    paths = [ROOT / "scripts/build_pages.py", ROOT / "scripts/build_offline.py", ROOT / "scripts/offline_server.py"]
    for folder in (ROOT / "relay/nightorders", ROOT / "relay/demo_web", ROOT / "docs/images/gallery"):
        paths.extend(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(ROOT)).encode() + b"\0" + path.read_bytes() + b"\0")
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--",
                                     *[str(p.relative_to(ROOT)) for p in paths]], cwd=ROOT, text=True, timeout=5)
    return {"commit": commit, "content_sha256": digest.hexdigest(), "includes_uncommitted_content": bool(dirty)}


def bundle(out: Path) -> dict:
    before = source()
    with tempfile.TemporaryDirectory(prefix="night-orders-offline-") as folder:
        root = Path(folder) / "night-orders-offline"
        build(root, None)
        shutil.copyfile(ROOT / "scripts/offline_server.py", root / "serve.py")
        banner = ('<aside style="padding:12px 24px;background:#243843;color:#fff8e9;font:14px system-ui" '
                  'aria-label="Offline snapshot">Offline snapshot · ' + before["commit"][:8]
                  + ' · Simulated night and recorded GitLab sessions. <a style="color:inherit" '
                  'href="snapshot.json">Revision and file inventory</a></aside>')
        for name in ("index.html", "activity.html"):
            text = (root / name).read_text()
            position = text.index(">", text.index("<body")) + 1
            (root / name).write_text(text[:position] + banner + text[position:])
        (root / "START_HERE.txt").write_text(
            "Night Orders offline app\n\nExtract the complete ZIP. In that folder run:\n"
            "  python3 serve.py\n\nPython 3.11+ is enough; no packages or credentials are required.\n"
            "Open the address printed by the command. Do not open index.html directly: browsers restrict "
            "local file data requests. Use --port 0 if the default port is occupied.\n\n"
            "Explore the signed/unsigned night, morning keep/restore, incident memory and two recorded "
            "Duo sessions. All playback files are included; source/artifact links need Internet access.\n"
            "This snapshot does not execute local shop actions or contact GitLab. The separate repository "
            "command scripts/run_local.py runs the real disposable local shop.\n\n"
            "snapshot.json records source revision, content digest and file hashes. Hashes detect accidental "
            "changes; they are not an independent signature. No deployment is implied.\n")
        if source()["content_sha256"] != before["content_sha256"]:
            raise ValueError("Source changed during the build; retry after the current edit finishes")
        files = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(root.rglob("*")) if p.is_file()}
        manifest = {"schema": 1, "created_at": datetime.now(timezone.utc).isoformat(), "source": before,
                    "execution": "Offline simulated replay and previously captured real GitLab sessions",
                    "requires_network_for_playback": False, "files": files}
        (root / "snapshot.json").write_text(json.dumps(manifest, indent=2) + "\n")
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    archive.write(path, str(path.relative_to(root.parent)))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = bundle(args.out)
    print(f"Wrote {args.out}: {len(manifest['files'])} files from {manifest['source']['commit']}")


if __name__ == "__main__":
    main()
