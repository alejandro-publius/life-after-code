"""Gate a release on two successful scans of the exact images pushed by this pipeline.

The GitLab container report has no image field when it contains no findings. Each scanner job therefore
records its immutable input, exit status and report hash alongside the unmodified analyzer report.
These are CI provenance receipts, not signatures or proof against a compromised runner.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any

SERVICES = ("relay", "shop")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SEVERITIES = {"Info", "Low", "Medium", "High", "Critical"}


def _json(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    return json.loads(raw), raw


def inspect_image(root: Path, service: str, registry: str, commit: str, pipeline: str) -> dict:
    errors: list[str] = []
    result = {"service": service, "image": None, "status": "failed", "findings": 0,
              "high_or_critical": 0, "errors": errors}
    try:
        built, _ = _json(root / "receipts" / f"{service}.json")
        readback, _ = _json(root / "receipts" / f"{service}-repo-digests.json")
        invocation, _ = _json(root / "scans" / service / "invocation.json")
        report, raw_report = _json(root / "scans" / service / "report.json")
    except (OSError, ValueError) as error:
        errors.append(f"Missing or unreadable evidence: {error}")
        return result

    if not all(isinstance(value, dict) for value in (built, invocation, report)):
        errors.append("Build receipt, scanner receipt and report must be JSON objects")
        return result
    digest = built.get("digest")
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        errors.append("Build receipt has no valid SHA256 manifest digest")
        return result
    image = f"{registry}/{service}@{digest}"
    result["image"] = image
    for name, receipt in (("Build", built), ("Scanner", invocation)):
        for key, expected in (("schema", 1), ("service", service), ("commit", commit),
                              ("pipeline", pipeline), ("image", image)):
            if type(receipt.get(key)) is not type(expected) or receipt.get(key) != expected:
                errors.append(f"{name} receipt {key} does not match this pipeline's {service} image")
    if built.get("tag") != f"{registry}/{service}:{commit}":
        errors.append("Build tag does not name this full commit SHA")
    if not isinstance(readback, list) or image not in readback:
        errors.append("Registry pull/readback does not confirm the pushed manifest digest")
    if type(invocation.get("exit_code")) is not int or invocation.get("exit_code") != 0:
        errors.append("Container analyzer did not exit successfully")
    actual_hash = hashlib.sha256(raw_report).hexdigest()
    if invocation.get("report_sha256") != actual_hash:
        errors.append("Scanner receipt does not match the report bytes")

    version = report.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"15\.\d+\.\d+", version):
        errors.append("Expected GitLab container report schema version 15")
    scan = report.get("scan")
    if not isinstance(scan, dict):
        errors.append("Container report is missing scan metadata")
        return result
    if scan.get("type") != "container_scanning" or scan.get("status") != "success":
        errors.append("Container report does not describe a successful container scan")
    try:
        start = datetime.strptime(scan["start_time"], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(scan["end_time"], "%Y-%m-%dT%H:%M:%S")
        if end < start:
            errors.append("Container scan ends before it starts")
    except (KeyError, TypeError, ValueError):
        errors.append("Container report has missing or invalid scan timestamps")
    for key in ("analyzer", "scanner"):
        tool = scan.get(key)
        if not isinstance(tool, dict) or not all(isinstance(tool.get(field), str) and tool[field]
                                                for field in ("id", "name", "version")):
            errors.append(f"Container report is missing its {key} identity/version")
    if "partial_scan" in scan:
        errors.append("A partial scan cannot approve a complete image")
    messages = scan.get("messages", [])
    if not isinstance(messages, list) or any(not isinstance(message, dict) or message.get("level") == "fatal"
                                             for message in messages):
        errors.append("Container scan contains a fatal or malformed diagnostic")

    findings = report.get("vulnerabilities")
    if not isinstance(findings, list):
        errors.append("Container report is missing the vulnerabilities array")
        return result
    result["findings"] = len(findings)
    for number, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"Finding {number} is malformed")
            continue
        location = finding.get("location")
        if not isinstance(location, dict) or location.get("image") != image:
            errors.append(f"Finding {number} is for a different or missing immutable image")
        severity = finding.get("severity")
        if not isinstance(severity, str) or severity not in SEVERITIES:
            errors.append(f"Finding {number} has an unknown or missing severity")
        if isinstance(severity, str) and severity in {"High", "Critical"}:
            result["high_or_critical"] += 1
    if result["high_or_critical"]:
        errors.append(f"{result['high_or_critical']} High/Critical findings block release")
    if not errors:
        result["status"] = "passed"
    return result


def evaluate(root: Path, registry: str, commit: str, pipeline: str) -> dict:
    errors = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9.:-]*(?:/[a-z0-9][a-z0-9._-]*)+", registry):
        errors.append("Registry image must be a registry hostname and repository path")
    if not COMMIT.fullmatch(commit):
        errors.append("A full commit SHA is required")
    if not re.fullmatch(r"[1-9][0-9]*", pipeline):
        errors.append("A numeric current pipeline ID is required")
    images = [] if errors else [inspect_image(root, service, registry, commit, pipeline) for service in SERVICES]
    return {"schema": 1, "status": "passed" if images and all(row["status"] == "passed" for row in images) else "failed",
            "commit": commit, "pipeline": pipeline, "images": images, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("container-evidence"))
    parser.add_argument("--registry-image", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--pipeline", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(args.root, args.registry_image, args.commit, args.pipeline)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
