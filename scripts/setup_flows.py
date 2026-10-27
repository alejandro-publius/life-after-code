"""Install the dusk, watch and dawn Duo flows, then read back their actual configuration.

    GITLAB_TOKEN=... uv run python scripts/setup_flows.py --project 123 --apply --out /tmp/flows.json

Without --apply this only checks GitLab. Repeated runs reuse this project's matching flows.
It never starts a flow, writes an issue note, changes an existing definition or changes a flag.
"""

from __future__ import annotations

import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import TextIO
from urllib.parse import urlsplit

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flows.validate import check as check_flow  # noqa: E402
from scripts.day_one import (  # noqa: E402
    CREATE_FLOW_MUTATION, ENABLE_FLOW_MUTATION, DayOne, GitLab, Http20, RelayError, gid_number,
)

SPECS = {
    "dusk": ("Drafts tonight's bounded orders from the day sheet and opens an orders merge request.",
             ["assign"], "DUSK_FLOW_CONSUMER_ID", "DUSK_FLOW_SERVICE_ACCOUNT"),
    "watch": ("Reads incident evidence and names a signed order or declines with a suggestion.",
              ["mention"], "FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT"),
    "dawn": ("Proposes which overnight changes to keep and opens the morning countersign merge request.",
             ["mention"], "DAWN_FLOW_CONSUMER_ID", "DAWN_FLOW_SERVICE_ACCOUNT"),
}
VERSION = """id released ... on AiCatalogFlowVersion { definition }"""
CONFIGURED = """
query($projectId: ProjectID!, $after: String) {
  aiCatalogConfiguredItems(projectId: $projectId, first: 100, after: $after) {
    nodes { id enabled item { id name project { id } latestVersion { VERSION } }
      pinnedItemVersion { VERSION }
      serviceAccount { username }
      parentItemConsumer { serviceAccount { username } }
      flowTriggers { active user { username } }
    }
    pageInfo { hasNextPage endCursor }
  }
}""".replace("VERSION", VERSION)
FIND = """
query($search: String!, $after: String) {
  aiCatalogItems(search: $search, itemType: FLOW, first: 100, after: $after) {
    nodes { id name project { id } latestVersion { VERSION } }
    pageInfo { hasNextPage endCursor }
  }
}""".replace("VERSION", VERSION)


def matching_definition(version: dict | None, definition: str) -> bool:
    if not version or version.get("released") is not True or not isinstance(version.get("definition"), str):
        return False
    try:
        return yaml.safe_load(version["definition"]) == yaml.safe_load(definition)
    except yaml.YAMLError:
        return False


def actual_account(node: dict) -> str:
    """GitLab's direct configurations hold the account on the trigger, not always on the consumer."""
    users = {str(account["username"]) for account in [
        node.get("serviceAccount") or {},
        (node.get("parentItemConsumer") or {}).get("serviceAccount") or {},
        *((trigger.get("user") or {}) for trigger in node.get("flowTriggers") or []
          if trigger.get("active") is True),
    ] if account.get("username")}
    return next(iter(users)) if len(users) == 1 else ""


class Installer:
    def __init__(self, run: DayOne):
        self.run = run
        self.project_gid = f"gid://gitlab/Project/{run.project_id()}"
        self.operations: list[dict] = []

    def connection(self, query: str, field: str, variables: dict) -> list[dict]:
        nodes: list[dict] = []
        after = None
        seen = set()
        for _ in range(10):
            data = self.run.graphql(f"read {field}", query, {**variables, "after": after})
            connection = data.get(field)
            if not isinstance(connection, dict) or not isinstance(connection.get("nodes"), list):
                raise RelayError(f"{field} returned no list; no safe discovery result")
            nodes.extend(node for node in connection["nodes"] if isinstance(node, dict))
            page = connection.get("pageInfo") or {}
            if page.get("hasNextPage") is False:
                return nodes
            after = page.get("endCursor")
            if not after or after in seen:
                raise RelayError(f"{field} pagination is incomplete")
            seen.add(after)
        raise RelayError(f"{field} exceeds the 1000-item discovery limit")

    def configured(self) -> list[dict]:
        return self.connection(CONFIGURED, "aiCatalogConfiguredItems", {"projectId": self.project_gid})

    def install_missing(self, key: str, definition: str) -> None:
        name = f"night-orders-{key}"
        description, triggers, _, _ = SPECS[key]
        found = self.connection(FIND, "aiCatalogItems", {"search": name})
        owned = [item for item in found if item.get("name") == name
                 and (item.get("project") or {}).get("id") == self.project_gid]
        if len(owned) > 1:
            raise RelayError(f"{name}: multiple catalog items owned by this project; choose one in GitLab")
        if owned:
            item = owned[0]
            if not matching_definition(item.get("latestVersion"), definition):
                raise RelayError(f"{name}: existing released definition differs or cannot be verified; left unchanged")
        else:
            data = self.run.graphql(f"create {name}", CREATE_FLOW_MUTATION, {"input": {
                "projectId": self.project_gid, "name": name, "description": description,
                "definition": definition, "release": True, "visibility": "PRIVATE",
            }})
            payload = data.get("aiCatalogFlowCreate") or {}
            if payload.get("errors"):
                raise RelayError(f"{name}: {'; '.join(map(str, payload['errors']))[:300]}")
            item = payload.get("item") or {}
            self.operations.append({"flow": key, "operation": "created", "item_id": item.get("id")})
        if not item.get("id"):
            raise RelayError(f"{name}: GitLab returned no catalog item ID")
        data = self.run.graphql(f"enable {name}", ENABLE_FLOW_MUTATION, {"input": {
            "itemId": item["id"], "target": {"projectId": self.project_gid}, "triggerTypes": triggers,
        }})
        payload = data.get("aiCatalogItemConsumerCreate") or {}
        if payload.get("errors"):
            raise RelayError(f"{name}: {'; '.join(map(str, payload['errors']))[:300]}")
        for warning in payload.get("warnings") or []:
            self.run.say(f"{name}: warning from GitLab: {warning}")
        consumer = gid_number((payload.get("itemConsumer") or {}).get("id"))
        if consumer is None:
            raise RelayError(f"{name}: enabling returned no consumer ID")
        self.operations.append({"flow": key, "operation": "enabled", "consumer_id": consumer})

    def execute(self, definitions: dict[str, str], apply: bool) -> dict:
        nodes = self.configured()
        problems: dict[str, str] = {}
        for key, definition in definitions.items():
            named = [node for node in nodes if (node.get("item") or {}).get("name") == f"night-orders-{key}"]
            if not named and apply:
                try:
                    self.install_missing(key, definition)
                except RelayError as error:
                    problems[key] = str(error)
        if apply and self.operations:
            nodes = self.configured()  # Never infer readiness from the mutation response.
        results, values = [], {}
        for key, definition in definitions.items():
            name = f"night-orders-{key}"
            named = [node for node in nodes if (node.get("item") or {}).get("name") == name]
            result = {"flow": key, "name": name, "status": "blocked", "execution": "not_run",
                      "definition_sha256": hashlib.sha256(definition.encode()).hexdigest()}
            reason = problems.get(key, "")
            if not reason and len(named) != 1:
                reason = "not enabled; rerun with --apply" if not named else "multiple configurations with this name"
            if not reason:
                node = named[0]
                item = node.get("item") or {}
                version = node.get("pinnedItemVersion") or item.get("latestVersion")
                consumer, account = gid_number(node.get("id")), actual_account(node)
                result.update(consumer_id=consumer, service_account=account,
                              version_id=(version or {}).get("id"), item_id=item.get("id"))
                if (item.get("project") or {}).get("id") != self.project_gid:
                    reason = "same name belongs to another project; left unchanged"
                elif node.get("enabled") is not True or consumer is None:
                    reason = "existing configuration is disabled or missing its ID; left unchanged"
                elif not matching_definition(version, definition):
                    reason = "released definition differs or cannot be verified; left unchanged"
                elif not any(trigger.get("active") is True for trigger in node.get("flowTriggers") or []):
                    reason = "no active flow trigger; left unchanged"
                elif not account:
                    reason = "GitLab did not return one unambiguous service account; no username guessed"
                else:
                    result["status"] = "ready"
                    _, _, id_key, account_key = SPECS[key]
                    values.update({id_key: consumer, account_key: account})
            if reason:
                result["reason"] = reason
            results.append(result)
        return {"project": self.run.project_id(), "at": self.run.now().isoformat(),
                "ready": all(result["status"] == "ready" for result in results),
                "flows": results, "values": values, "operations": self.operations}


def main(argv=None, *, env=None, client=None, out: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True)
    parser.add_argument("--flow", action="append", choices=SPECS, help="repeat to select flows; defaults to all three")
    parser.add_argument("--apply", action="store_true", help="create and enable missing flows, without starting them")
    parser.add_argument("--out", type=Path, help="write non-secret configuration and verification results as JSON")
    parser.add_argument("--base-url", help="GitLab HTTPS base URL; defaults to GITLAB_URL or gitlab.com")
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    out = sys.stdout if out is None else out
    token = env.get("GITLAB_TOKEN", "").strip()
    base = args.base_url or env.get("GITLAB_URL") or "https://gitlab.com"
    url = urlsplit(base)
    if not token or url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        print("Set GITLAB_TOKEN and use an HTTPS GitLab base URL without credentials, query or fragment.", file=out)
        return 2
    try:
        definitions = {}
        for key in dict.fromkeys(args.flow or SPECS):
            path = ROOT / "flows" / f"{key}.yml"
            problems = check_flow(path)
            if problems:
                raise ValueError(f"{key}.yml: {'; '.join(problems)}")
            definitions[key] = path.read_text(encoding="utf-8")
        with nullcontext(client) if client is not None else httpx.Client() as connection:
            run = DayOne(GitLab(Http20(connection), base, args.project, token), token=token, out=out,
                         options=args, now=lambda: datetime.now(timezone.utc), clock=time.monotonic, sleep=time.sleep)
            report = Installer(run).execute(definitions, args.apply)
            for flow in report["flows"]:
                run.say(f"{flow['name']}: {flow['status']}" + (f" ({flow['reason']})" if flow.get("reason") else ""))
            for name, value in report["values"].items():
                run.say(f"{name}={value}")
            run.say(f"GitLab changes: {len(report['operations'])}. Flow execution: not started.")
            if args.out:
                args.out.write_text(run.redact(json.dumps(report, indent=2)) + "\n", encoding="utf-8")
            return 0 if report["ready"] else 1
    except (RelayError, OSError, ValueError, yaml.YAMLError) as error:
        print(str(error).replace(token, "[GITLAB_TOKEN]"), file=out)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
