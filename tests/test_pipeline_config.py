"""The GitLab pipeline stays strict: locked dependencies, pinned tools and images, artifacts that expire, the
security scans included, and the same tool versions as the GitHub checks. Offline: reads the YAML files."""

from __future__ import annotations

import re

import yaml

from conftest import REPO

CI = yaml.safe_load((REPO / ".gitlab-ci.yml").read_text(encoding="utf-8"))
GITHUB = (REPO / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
RESERVED = {"workflow", "stages", "include", "default", "variables"}
JOBS = {name: job for name, job in CI.items() if name not in RESERVED and isinstance(job, dict)}


def resolved(name: str) -> dict:
    """A job with its extends merged in (one level of hidden templates is all this file uses)."""
    job = dict(JOBS[name])
    parent = job.pop("extends", None)
    if parent:
        job = {**JOBS[parent], **job}
    return job


def commands(job: dict) -> list[str]:
    lines = []
    for key in ("before_script", "script", "after_script"):
        lines += [str(line) for line in job.get(key) or []]
    return lines


REAL = [name for name in JOBS if not name.startswith(".")]


def test_merge_requests_get_merge_request_pipelines_and_a_push_never_runs_twice():
    rules = CI["workflow"]["rules"]
    assert rules[0] == {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'}
    assert rules[1]["when"] == "never" and "$CI_OPEN_MERGE_REQUESTS" in rules[1]["if"]
    assert CI["workflow"]["auto_cancel"] == {"on_new_commit": "interruptible"}


def test_every_uv_command_is_locked_and_every_tool_is_pinned():
    for name in REAL:
        for line in commands(resolved(name)):
            for match in re.finditer(r"\buv (sync|run|export)\b", line):
                assert "--locked" in line, f"{name}: {line}"
            if "uvx" in line:
                assert re.search(r"uvx --from [\w-]+==[\d.]+ ", line), f"{name}: {line}"
            if "pip install" in line:
                assert "==" in line, f"{name}: {line}"


def test_every_image_is_pinned_to_a_version_or_a_digest():
    for name in JOBS:
        image = resolved(name).get("image")
        if image is None:
            continue
        assert "@sha256:" in image or re.search(r":\d[\w.-]*$", image), f"{name}: {image}"
        assert not image.endswith(":latest"), name


def test_every_artifact_expires():
    for name in REAL:
        artifacts = resolved(name).get("artifacts")
        if artifacts:
            assert artifacts.get("expire_in"), name


def test_the_security_scans_are_included():
    templates = {item.get("template") for item in CI["include"]}
    assert {"Jobs/SAST.gitlab-ci.yml", "Jobs/SAST-IaC.gitlab-ci.yml", "Jobs/Secret-Detection.gitlab-ci.yml"} <= templates
    audit = commands(resolved("dependency_audit"))
    assert any("--require-hashes" in line and "-f cyclonedx-json" in line for line in audit)
    assert resolved("dependency_audit")["artifacts"]["reports"]["cyclonedx"] == "gl-sbom-python.cdx.json"


def test_checks_start_at_once_and_can_be_cancelled_but_deploys_cannot():
    assert CI["default"]["interruptible"] is True
    for name in REAL:
        job = resolved(name)
        if job.get("stage") in ("test", "verify", "audit", "report"):
            assert job.get("needs") == [], name
    deploy = yaml.safe_load((REPO / "deploy" / "gitlab-ci-deploy.yml").read_text(encoding="utf-8"))
    assert deploy[".deploy_cloud_run"]["interruptible"] is False


def test_the_tool_versions_match_the_github_checks_and_the_browser_walk():
    uv = CI["variables"]["UV_VERSION"]
    assert f'version: "{uv}"' in GITHUB
    playwright = CI["variables"]["PLAYWRIGHT_VERSION"]
    assert f"playwright=={playwright}" in GITHUB
    assert f"playwright=={playwright}" in (REPO / "scripts" / "browser_smoke.py").read_text(encoding="utf-8")
    ruff = re.search(r"ruff==([\d.]+)", " ".join(commands(resolved("lint")))).group(1)
    assert f"ruff=={ruff}" in GITHUB


def test_coverage_is_read_from_the_pytest_total_line():
    pattern = resolved("unit_tests")["coverage"].strip("/")
    assert re.search(pattern, "TOTAL                                4535    324    93%", re.M).group(1) == "93"
    assert resolved("unit_tests")["artifacts"]["reports"]["coverage_report"]["coverage_format"] == "cobertura"


def test_the_night_report_runs_only_on_its_schedule_and_the_checks_never_do():
    assert resolved("night_report")["rules"] == [
        {"if": '$CI_PIPELINE_SOURCE == "schedule" && $NIGHT_REPORT == "1" && $RELAY_URL'}]
    for name in REAL:
        if name != "night_report" and resolved(name).get("stage") in ("test", "verify"):
            rules = resolved(name).get("rules") or []
            assert {"if": '$CI_PIPELINE_SOURCE != "schedule"'} in rules, name


def test_the_code_owner_of_the_signed_files_is_the_on_call_person():
    owners = (REPO / ".gitlab" / "CODEOWNERS").read_text(encoding="utf-8")
    user = yaml.safe_load((REPO / "ops" / "oncall.yml").read_text(encoding="utf-8"))["user"]
    for path in ("/ops/night-orders.yml", "/ops/state.yml"):
        assert f"{path} @{user}\n" in owners
