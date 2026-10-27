"""The dependencies Docker installs must be versions and artifacts covered by the tested lock."""

import re
import tomllib

import pytest

from conftest import REPO


@pytest.mark.parametrize("service", ["relay", "shop"])
def test_packaged_dependency_versions_and_hashes_match_the_tested_lock(service):
    lock = tomllib.loads((REPO / "uv.lock").read_text())
    locked = {(p["name"], p["version"]): p for p in lock["package"]}
    contents = (REPO / service / "requirements.txt").read_text().replace("\\\n", " ")
    distributions = set()
    for line in contents.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pin = re.match(r"([a-zA-Z0-9_.-]+)==([^\s;]+)", line)
        assert pin, f"{service} has an unpinned runtime dependency: {line}"
        name, version = pin.groups()
        name = re.sub(r"[-_.]+", "-", name).lower()
        assert (name, version) in locked, f"{service} packages {name} {version}, outside the tested uv.lock"
        package = locked[name, version]
        artifacts = package.get("wheels", []) + ([package["sdist"]] if "sdist" in package else [])
        allowed = {artifact["hash"] for artifact in artifacts}
        hashes = set(re.findall(r"--hash=(sha256:[a-f0-9]{64})", line))
        assert hashes and hashes <= allowed, f"{service} has missing or unverified {name} artifact hashes"
        distributions.add(name)
    required = {"fastapi", "uvicorn", "httpx"}
    if service == "relay":
        required |= {"pyyaml", "jsonschema"}
    assert required <= distributions, f"{service} is missing runtime dependencies"
