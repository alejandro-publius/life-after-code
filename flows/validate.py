"""Check our Duo flow files before anyone pastes them into GitLab.

    python flows/validate.py            # validate every flows/*.yml
    python flows/validate.py --refresh  # re-download GitLab's schema and tool list first

Checks, per file: ASCII only (June entrants saw long dashes silently corrupted in the flow
editor), under 40 KiB, GitLab's flow_v2.json schema, every tool name in GitLab's tools.json,
every prompt_id defined, every router naming real components, and the entry point existing.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "schema" / "flow_v2.json"
TOOLS = HERE / "schema" / "tools.json"
MAX_BYTES = 40 * 1024
SOURCES = {
    SCHEMA: "https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/files/"
            "app%2Fvalidators%2Fjson_schemas%2Fai_catalog%2Fflow_v2.json/raw?ref=master",
    TOOLS: "https://gitlab.com/api/v4/projects/components%2Fai-catalog/repository/files/"
           "schemas%2Fcomponent%2Ftools.json/raw?ref=main",
}


def refresh() -> None:
    for path, url in SOURCES.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            path.write_bytes(response.read())


def check(path: Path) -> list[str]:
    raw = path.read_bytes()
    problems = []
    if len(raw) > MAX_BYTES:
        problems.append(f"{len(raw)} bytes, over the 40 KiB limit")
    bad = [(i, ch) for i, ch in enumerate(raw.decode("utf-8")) if ord(ch) > 127]
    if bad:
        problems.append(f"non-ASCII character {bad[0][1]!r} at offset {bad[0][0]} (the flow editor corrupts these)")

    data = yaml.safe_load(raw)
    data["yaml_definition"] = raw.decode("utf-8")  # GitLab stores the source next to the parsed flow
    validator = Draft7Validator(json.loads(SCHEMA.read_text()))
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in error.absolute_path) or "flow"
        problems.append(f"schema: {where}: {error.message[:200]}")

    tools = set(json.loads(TOOLS.read_text())["enum"])
    names = {c["name"] for c in data.get("components", [])}
    prompt_ids = {p["prompt_id"] for p in data.get("prompts", [])}
    for component in data.get("components", []):
        for tool in component.get("toolset") or []:
            if tool not in tools:
                problems.append(f"{component['name']}: unknown tool {tool}")
        if "prompt_id" in component and component["prompt_id"] not in prompt_ids:
            problems.append(f"{component['name']}: prompt {component['prompt_id']} is not defined")
        target = component.get("sends_response_to")
        if target and target not in names:
            problems.append(f"{component['name']}: sends_response_to {target}, which does not exist")
    for router in data.get("routers", []):
        ends = [router.get("to")] + list((router.get("condition") or {}).get("routes", {}).values())
        for end in [router.get("from")] + ends:
            if end and end != "end" and end not in names:
                problems.append(f"router names {end}, which is not a component")
    entry = (data.get("flow") or {}).get("entry_point")
    if entry not in names:
        problems.append(f"entry point {entry} is not a component")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--refresh" in args:
        refresh()
    failed = 0
    for path in sorted(HERE.glob("*.yml")):
        problems = check(path)
        status = "ok" if not problems else "FAILED"
        print(f"{path.name}: {status}")
        for problem in problems:
            print(f"  - {problem}")
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
