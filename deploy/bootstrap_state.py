#!/usr/bin/env python3
"""Keep bootstrap ownership metadata. This file never handles credentials."""

import json
import os
import pathlib
import sys


def read(path):
    return json.loads(pathlib.Path(path).read_text())


def write(path, value):
    destination = pathlib.Path(path)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(destination)


def lookup(value, dotted):
    for key in dotted.split("."):
        value = value[key]
    return value


def main():
    command, path, *arguments = sys.argv[1:]
    if command == "new":
        keys = (
            "GCP_PROJECT_ID", "GCP_PROJECT_NUMBER", "GCP_REGION",
            "GITLAB_PROJECT_ID", "GITLAB_PROJECT_PATH", "GITLAB_NAMESPACE_ID",
            "GITLAB_DEFAULT_BRANCH", "GCP_WIF_POOL", "GCP_WIF_PROVIDER",
            "GCP_SERVICE_ACCOUNT", "GCP_BUILD_SERVICE_ACCOUNT",
            "GCP_SHOP_SERVICE_ACCOUNT", "GCP_STAGING_SERVICE_ACCOUNT", "GCP_RELAY_SERVICE_ACCOUNT",
            "GCP_ARTIFACT_REPOSITORY", "GCP_SOURCE_BUCKET", "GCP_SHOP_SERVICE",
            "GCP_STAGING_SERVICE", "GCP_RELAY_SERVICE", "STATE_BUCKET", "GCP_BILLING_ACCOUNT_ID",
        )
        write(path, {"version": 1, "config": {key: os.environ[key] for key in keys},
                     "enabled_apis": [], "resources": [], "project_label_added": False,
                     "budget_name": None, "ops": {}, "complete": False})
        return
    state = read(path)
    if command == "verify":
        expected = ("GCP_PROJECT_ID", "GITLAB_PROJECT_ID", "GITLAB_PROJECT_PATH")
        for key in expected:
            if state["config"][key] != os.environ[key]:
                raise SystemExit("Saved ownership metadata does not match " + key)
        if state["version"] != 1:
            raise SystemExit("Unsupported bootstrap metadata version")
    elif command == "get":
        value = lookup(state, arguments[0])
        if isinstance(value, (dict, list, bool)) or value is None:
            print(json.dumps(value))
        else:
            print(value)
    elif command == "set":
        state[arguments[0]] = json.loads(arguments[1])
        write(path, state)
    elif command == "config":
        state["config"][arguments[0]] = arguments[1]
        write(path, state)
    elif command == "append":
        if arguments[1] not in state[arguments[0]]:
            state[arguments[0]].append(arguments[1])
        write(path, state)
    elif command == "contains":
        raise SystemExit(0 if arguments[1] in lookup(state, arguments[0]) else 1)
    elif command == "equals":
        try:
            actual = lookup(state, arguments[0])
        except (KeyError, TypeError):
            raise SystemExit(1) from None
        raise SystemExit(0 if actual == json.loads(arguments[1]) else 1)
    elif command == "assert":
        try:
            actual = lookup(state, arguments[0])
        except (KeyError, TypeError):
            raise SystemExit("Ownership collision: missing " + arguments[0]) from None
        if str(actual) != arguments[1]:
            raise SystemExit("Ownership collision: " + arguments[0])
    elif command == "budget":
        project_id, project_number, display = arguments
        matches = [item for item in state if item.get("displayName") == display]
        if len(matches) > 1:
            raise SystemExit("Several budgets have the expected display name")
        if matches:
            projects = matches[0].get("budgetFilter", {}).get("projects", [])
            if projects not in (["projects/" + project_id], ["projects/" + project_number]):
                raise SystemExit("Budget name belongs to a different project filter")
            print(matches[0]["name"])
    else:
        raise SystemExit("Unknown metadata command")


if __name__ == "__main__":
    main()
