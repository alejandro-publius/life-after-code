import json
import zipfile

import pytest

from scripts.build_offline import bundle
from scripts.offline_server import verify


@pytest.fixture(scope="module")
def snapshot(tmp_path_factory):
    folder = tmp_path_factory.mktemp("offline")
    archive = folder / "night.zip"
    manifest = bundle(archive)
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(folder)
    return folder / "night-orders-offline", manifest


def test_offline_app_contains_both_morning_choices_and_real_session_records(snapshot):
    root, manifest = snapshot
    assert verify(root) == manifest
    assert len(list(root.glob("replay-*.json"))) == 8
    keep = json.loads((root / "replay-signed-approved.json").read_text())
    restore = json.loads((root / "replay-signed-approved-restore.json").read_text())
    assert keep["flags"]["after_morning"] != restore["flags"]["after_morning"]
    assert keep["timeline"] == restore["timeline"]
    assert len(json.loads((root / "activity.json").read_text())["runs"]) == 2
    assert manifest["source"]["commit"] in (root / "snapshot.json").read_text()
    assert "Offline snapshot" in (root / "index.html").read_text()


def test_changed_asset_refuses_startup(snapshot):
    root, _ = snapshot
    path = root / "assets/app.js"
    original = path.read_bytes()
    try:
        path.write_bytes(original + b"\n// Changed after packaging\n")
        with pytest.raises(ValueError, match="Snapshot file has changed"):
            verify(root)
    finally:
        path.write_bytes(original)
