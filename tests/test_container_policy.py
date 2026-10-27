"""Release policy uses actual GitLab report fields and pipeline-bound synthetic CI receipts. No registry calls."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from conftest import REPO
from scripts.container_policy import evaluate, main

REGISTRY = "registry.gitlab.example/group/night-orders"
COMMIT = "a" * 40
PIPELINE = "12345"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def change_json(path: Path, change) -> None:
    value = json.loads(path.read_text())
    change(value)
    write_json(path, value)


def bind_report(root: Path, service: str = "relay") -> None:
    folder = root / "scans" / service
    report_hash = hashlib.sha256((folder / "report.json").read_bytes()).hexdigest()
    change_json(folder / "invocation.json", lambda value: value.update(report_sha256=report_hash))


@pytest.fixture
def evidence(tmp_path):
    for service, digit in (("relay", "1"), ("shop", "2")):
        digest = "sha256:" + digit * 64
        image = f"{REGISTRY}/{service}@{digest}"
        common = {"schema": 1, "service": service, "commit": COMMIT, "pipeline": PIPELINE, "image": image}
        write_json(tmp_path / "receipts" / f"{service}.json",
                   {**common, "digest": digest, "tag": f"{REGISTRY}/{service}:{COMMIT}"})
        write_json(tmp_path / "receipts" / f"{service}-repo-digests.json", [image])
        tool = {"id": "trivy", "name": "Trivy", "version": "0.69.3", "vendor": {"name": "Aqua Security"}}
        write_json(tmp_path / "scans" / service / "report.json", {
            "version": "15.0.6", "scan": {"type": "container_scanning", "status": "success",
                                           "analyzer": tool, "scanner": tool,
                                           "start_time": "2026-10-27T11:00:00", "end_time": "2026-10-27T11:01:00"},
            "vulnerabilities": [],
        })
        write_json(tmp_path / "scans" / service / "invocation.json", {**common, "exit_code": 0})
        bind_report(tmp_path, service)
    return tmp_path


def result(root):
    return evaluate(root, REGISTRY, COMMIT, PIPELINE)


def errors(root):
    report = result(root)
    assert report["status"] == "failed"
    return " ".join(report["errors"] + [error for image in report["images"] for error in image["errors"]])


def add_finding(root, severity="High", image=None, service="relay"):
    expected = json.loads((root / "receipts" / f"{service}.json").read_text())["image"]
    change_json(root / "scans" / service / "report.json", lambda value: value["vulnerabilities"].append({
        "id": "synthetic-finding", "severity": severity, "identifiers": [{"type": "cve", "name": "CVE-DEMO", "value": "DEMO"}],
        "location": {"image": image or expected, "operating_system": "debian 12", "dependency": {
            "package": {"name": "demo-package"}, "version": "1.0"}},
    }))
    bind_report(root, service)


def test_two_clean_images_pass_without_inventing_a_native_scan_target(evidence):
    report = result(evidence)
    assert report["status"] == "passed"
    assert [item["service"] for item in report["images"]] == ["relay", "shop"]
    assert all(item["image"].startswith(f"{REGISTRY}/{item['service']}@sha256:") for item in report["images"])
    assert all(item["findings"] == 0 for item in report["images"])


@pytest.mark.parametrize("service", ["relay", "shop"])
@pytest.mark.parametrize("severity", ["High", "Critical"])
def test_high_or_critical_findings_in_either_image_block_release(evidence, service, severity):
    add_finding(evidence, severity, service=service)
    assert "High/Critical findings" in errors(evidence)


@pytest.mark.parametrize("severity", ["Info", "Low", "Medium"])
def test_classified_findings_below_policy_threshold_are_recorded(evidence, severity):
    add_finding(evidence, severity)
    report = result(evidence)
    assert report["status"] == "passed"
    assert report["images"][0]["findings"] == 1


@pytest.mark.parametrize("relative", ["scans/shop/report.json", "scans/relay/invocation.json",
                                       "receipts/shop.json", "receipts/relay-repo-digests.json"])
def test_missing_evidence_is_a_failure_even_for_otherwise_clean_images(evidence, relative):
    (evidence / relative).unlink()
    assert "Missing or unreadable evidence" in errors(evidence)


@pytest.mark.parametrize("exit_code", [1, 2, "0", False, None])
def test_scanner_failure_or_invalid_exit_status_cannot_pass(evidence, exit_code):
    change_json(evidence / "scans/relay/invocation.json", lambda value: value.update(exit_code=exit_code))
    assert "analyzer did not exit successfully" in errors(evidence)


def test_failed_report_cannot_pass_even_when_process_exited_zero(evidence):
    change_json(evidence / "scans/relay/report.json", lambda value: value["scan"].update(status="failure"))
    bind_report(evidence)
    assert "successful container scan" in errors(evidence)


@pytest.mark.parametrize("field,value", [("image", f"{REGISTRY}/shop@sha256:" + "1" * 64),
                                        ("commit", "b" * 40), ("pipeline", "999")])
def test_wrong_image_commit_or_pipeline_receipt_cannot_approve_a_clean_report(evidence, field, value):
    change_json(evidence / "scans/relay/invocation.json", lambda data: data.update({field: value}))
    assert f"Scanner receipt {field}" in errors(evidence)


def test_changed_report_bytes_invalidate_the_scanner_receipt(evidence):
    report = evidence / "scans/relay/report.json"
    report.write_text(report.read_text() + "\n")
    assert "does not match the report bytes" in errors(evidence)


def test_wrong_image_in_native_vulnerability_location_is_rejected(evidence):
    add_finding(evidence, "Low", f"{REGISTRY}/relay@sha256:" + "9" * 64)
    assert "different or missing immutable image" in errors(evidence)


def test_registry_readback_must_confirm_exact_manifest_digest(evidence):
    write_json(evidence / "receipts/relay-repo-digests.json", [f"{REGISTRY}/relay@sha256:" + "9" * 64])
    assert "readback does not confirm" in errors(evidence)


@pytest.mark.parametrize("digest", ["sha256:short", "sha256:" + "G" * 64, 7, None])
def test_manifest_digest_is_a_typed_sha256_value(evidence, digest):
    change_json(evidence / "receipts/relay.json", lambda value: value.update(digest=digest))
    assert "valid SHA256 manifest digest" in errors(evidence)


@pytest.mark.parametrize("change,reason", [
    (lambda value: value.pop("vulnerabilities"), "missing the vulnerabilities array"),
    (lambda value: value["scan"].update(partial_scan={"mode": "differential"}), "partial scan"),
    (lambda value: value["scan"].update(messages=[{"level": "fatal", "value": "scan failed"}]), "fatal"),
    (lambda value: value["scan"].pop("scanner"), "scanner identity/version"),
    (lambda value: value["scan"].pop("end_time"), "scan timestamps"),
    (lambda value: value["scan"].update(end_time="2026-10-27T10:00:00"), "ends before it starts"),
])
def test_incomplete_scan_evidence_fails_closed(evidence, change, reason):
    change_json(evidence / "scans/relay/report.json", change)
    bind_report(evidence)
    assert reason in errors(evidence)


@pytest.mark.parametrize("severity", ["Unknown", None, ["Low"]])
def test_unknown_severity_is_not_silently_treated_as_low(evidence, severity):
    add_finding(evidence, severity)
    assert "unknown or missing severity" in errors(evidence)


def test_cli_exit_status_and_artifact_follow_policy_result(evidence, tmp_path):
    out = tmp_path / "policy.json"
    args = ["--root", str(evidence), "--registry-image", REGISTRY, "--commit", COMMIT,
            "--pipeline", PIPELINE, "--out", str(out)]
    assert main(args) == 0
    assert json.loads(out.read_text())["status"] == "passed"
    add_finding(evidence)
    assert main(args) == 1
    assert json.loads(out.read_text())["status"] == "failed"


@pytest.fixture
def shell_ci(tmp_path):
    """Execute the CI shell with local process doubles, not real Docker, registry or analyzer services."""
    commands = tmp_path / "bin"
    commands.mkdir()
    docker = commands / "docker"
    docker.write_text(f"#!{sys.executable}\n" + '''
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ['CONTAINER_TEST_EVENTS'], 'a') as output:
    output.write(json.dumps(['docker', *args]) + '\\n')
if args[0] == os.environ.get('FAIL_DOCKER_OPERATION'):
    sys.exit(9)
if args[0] == 'push':
    service = args[1].rsplit('/', 1)[1].split(':', 1)[0]
    digest = 'sha256:' + ('1' if service == 'relay' else '2') * 64
    print(args[1].rsplit(':', 1)[1] + ': digest: ' + digest + ' size: 1234')
elif args[:2] == ['image', 'inspect']:
    print(json.dumps([args[-1]]))
''', encoding="utf-8")
    docker.chmod(0o755)
    analyzer = commands / "gtcs"
    analyzer.write_text(f"#!{sys.executable}\n" + '''
import json, os, sys
from pathlib import Path
image = os.environ['CS_IMAGE']
with open(os.environ['CONTAINER_TEST_EVENTS'], 'a') as output:
    output.write(json.dumps(['gtcs', *sys.argv[1:], image]) + '\\n')
tool = {'id': 'trivy', 'name': 'Trivy', 'version': '0.69.3', 'vendor': {'name': 'Aqua Security'}}
report = {'version': '15.0.6', 'scan': {'type': 'container_scanning', 'status': 'success',
          'analyzer': tool, 'scanner': tool, 'start_time': '2026-10-27T11:00:00',
          'end_time': '2026-10-27T11:01:00'}, 'vulnerabilities': []}
Path('gl-container-scanning-report.json').write_text(json.dumps(report))
sys.exit(int(os.environ.get('ANALYZER_TEST_EXIT', '0')))
''', encoding="utf-8")
    analyzer.chmod(0o755)
    env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ["PATH"],
               CI_REGISTRY_IMAGE=REGISTRY, CI_REGISTRY="registry.gitlab.example",
               CI_REGISTRY_PASSWORD="synthetic-test-value", CI_REGISTRY_USER="test-user",
               CI_COMMIT_SHA=COMMIT, CI_COMMIT_SHORT_SHA=COMMIT[:8], CI_PIPELINE_ID=PIPELINE,
               RELAY_IMAGE=f"{REGISTRY}/relay:{COMMIT}", SHOP_IMAGE=f"{REGISTRY}/shop:{COMMIT}",
               CONTAINER_TEST_EVENTS=str(tmp_path / "commands.jsonl"))
    ci = yaml.safe_load((REPO / ".gitlab-ci.yml").read_text())

    def run(job, **overrides):
        return subprocess.run(["sh", "-eu", "-c", "\n".join(ci[job]["script"])],
                              cwd=tmp_path, env={**env, **overrides}, capture_output=True, text=True)

    return tmp_path, env, run


def test_real_ci_scripts_bind_two_registry_readbacks_to_two_analyzer_reports(shell_ci):
    folder, env, run = shell_ci
    packaged = run("package_images")
    assert packaged.returncode == 0, packaged.stderr
    root = folder / "container-evidence"
    for line in (root / "images.env").read_text().splitlines():
        key, value = line.split("=", 1)
        env[key] = value
    for service in ("relay", "shop"):
        scanned = run("container_scanning", SCAN_SERVICE=service)
        assert scanned.returncode == 0, scanned.stderr
    assert result(root)["status"] == "passed"
    events = [json.loads(line) for line in (folder / "commands.jsonl").read_text().splitlines()]
    builds = [event for event in events if event[:2] == ["docker", "build"]]
    assert len(builds) == 2
    for service, build in zip(("relay", "shop"), builds):
        assert build[build.index("--file") + 1] == "deploy/Dockerfile"
        assert f"APP_DIR={service}" in build
        assert build[build.index("--tag") + 1] == f"{REGISTRY}/{service}:{COMMIT}"
    scans = [event for event in events if event[0] == "gtcs"]
    assert [event[-1] for event in scans] == [env["RELAY_SCAN_IMAGE"], env["SHOP_SCAN_IMAGE"]]


@pytest.mark.parametrize("operation", ["build", "push", "pull"])
def test_packaging_shell_preserves_failed_docker_exit_status(shell_ci, operation):
    folder, _, run = shell_ci
    packaged = run("package_images", FAIL_DOCKER_OPERATION=operation)
    assert packaged.returncode != 0
    assert result(folder / "container-evidence")["status"] == "failed"


def test_analyzer_shell_keeps_failed_status_even_when_a_report_exists(shell_ci):
    folder, env, run = shell_ci
    assert run("package_images").returncode == 0
    for line in (folder / "container-evidence/images.env").read_text().splitlines():
        key, value = line.split("=", 1)
        env[key] = value
    scanned = run("container_scanning", SCAN_SERVICE="relay", ANALYZER_TEST_EXIT="7")
    assert scanned.returncode == 7
    receipt = json.loads((folder / "container-evidence/scans/relay/invocation.json").read_text())
    assert receipt["exit_code"] == 7
    assert receipt["report_sha256"]
    assert "analyzer did not exit successfully" in errors(folder / "container-evidence")
