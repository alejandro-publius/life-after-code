#!/usr/bin/env python3
"""Demo cloud responses for destructive-script tests. No Google calls occur."""

import hashlib
import json
import os
from pathlib import Path
import stat
import sys


ARGS = sys.argv[1:]
REMOTE = Path(os.environ["LAC_MOCK_REMOTE"])
STATE = json.loads(REMOTE.read_text()) if REMOTE.exists() else {
    "project": {"projectNumber": "123456789012", "labels": {}},
    "apis": ["storage.googleapis.com", "cloudresourcemanager.googleapis.com",
             "serviceusage.googleapis.com"],
    "resources": {}, "budgets": [], "bindings": [], "commands": [], "objects": {},
}
STATE["commands"].append(ARGS)


def save():
    REMOTE.write_text(json.dumps(STATE))


def out(value):
    save()
    print(json.dumps(value))
    raise SystemExit(0)


def flag(key, default=None):
    return next((arg.split("=", 1)[1] for arg in ARGS
                 if arg.startswith("--" + key + "=")), default)


def error(message, status=1):
    save()
    print(message, file=sys.stderr)
    raise SystemExit(status)


def missing():
    error("ERROR: (NOT_FOUND) resource was not found")


def labels(value):
    return dict(item.split("=", 1) for item in value.split(",")) if value else {}


def add_binding(scope):
    binding = {"scope": scope, "role": flag("role"), "members": [flag("member")]}
    if binding not in STATE["bindings"]:
        STATE["bindings"].append(binding)
    out({})


def remove_resource(identity):
    STATE["resources"].pop(identity, None)
    STATE["bindings"] = [binding for binding in STATE["bindings"]
                         if binding["scope"] != identity]


if ARGS[:2] == ["billing", "budgets"] and "billingbudgets.googleapis.com" not in STATE["apis"]:
    error("ERROR: (SERVICE_DISABLED) budget API disabled")
if ARGS[:3] == ["billing", "projects", "describe"] and "cloudbilling.googleapis.com" not in STATE["apis"]:
    error("ERROR: (SERVICE_DISABLED) billing API disabled")
if os.environ.get("LAC_MOCK_PERMISSION") and os.environ["LAC_MOCK_PERMISSION"] in " ".join(ARGS):
    error("ERROR: (PERMISSION_DENIED) permission rejected")
if ARGS[:2] == ["projects", "describe"]:
    out(STATE["project"])
if ARGS[:3] == ["billing", "projects", "describe"]:
    out({"billingEnabled": True, "billingAccountName": "billingAccounts/ABCDEF-123456-UVWXYZ"})
if ARGS[:3] == ["billing", "budgets", "list"]:
    out(STATE["budgets"])
if ARGS[:3] == ["billing", "budgets", "create"]:
    value = {"name": "billingAccounts/ABCDEF-123456-UVWXYZ/budgets/demo",
             "displayName": flag("display-name"),
             "budgetFilter": {"projects": [flag("filter-projects")]}}
    STATE["budgets"].append(value)
    out(value)
if ARGS[:3] == ["billing", "budgets", "update"]:
    out({})
if ARGS[:3] == ["billing", "budgets", "delete"]:
    STATE["budgets"] = []
    out({})
if ARGS[:2] == ["services", "list"]:
    out([{"config": {"name": api}} for api in STATE["apis"]])
if ARGS[:2] == ["services", "enable"]:
    STATE["apis"] = sorted(set(STATE["apis"]) | {arg for arg in ARGS[2:] if not arg.startswith("--")})
    out({})
if ARGS[:2] == ["services", "disable"]:
    STATE["apis"] = [api for api in STATE["apis"] if api not in ARGS[2:]]
    out({})
if ARGS[:3] == ["alpha", "projects", "update"]:
    STATE["project"]["labels"].update(labels(flag("update-labels")))
    if flag("remove-labels"):
        STATE["project"]["labels"].pop(flag("remove-labels"), None)
    out({})
if ARGS[:3] == ["beta", "services", "identity"]:
    out({})
if ARGS[:2] == ["projects", "add-iam-policy-binding"]:
    add_binding("project")
if ARGS[:2] == ["projects", "get-iam-policy"]:
    out({"bindings": [binding for binding in STATE["bindings"] if binding["scope"] == "project"]})
if ARGS[:2] == ["projects", "remove-iam-policy-binding"]:
    STATE["bindings"] = [binding for binding in STATE["bindings"]
                         if not (binding["scope"] == "project" and binding["role"] == flag("role")
                                 and flag("member") in binding["members"])]
    out({})
if ARGS[:2] == ["builds", "list"]:
    out([])
if ARGS[:2] == ["storage", "cp"]:
    source, destination = ARGS[2:4]
    if source.startswith("gs://"):
        if source not in STATE["objects"]:
            missing()
        Path(destination).write_text(json.dumps(STATE["objects"][source]))
    else:
        STATE["objects"][destination] = json.loads(Path(source).read_text())
    out({})
if ARGS[:3] == ["storage", "objects", "describe"]:
    if ARGS[3] not in STATE["objects"]:
        missing()
    out({"name": ARGS[3]})
if ARGS[:2] == ["storage", "rm"]:
    bucket = next(arg for arg in ARGS[2:] if arg.startswith("gs://"))
    remove_resource("bucket:" + bucket)
    STATE["objects"] = {name: value for name, value in STATE["objects"].items()
                        if not name.startswith(bucket + "/")}
    out({})
if ARGS[:3] == ["secrets", "versions", "list"]:
    identity = "secret:" + ARGS[3]
    if identity not in STATE["resources"]:
        missing()
    out(STATE["resources"][identity].get("versions", []))
if ARGS[:3] == ["secrets", "versions", "add"]:
    identity = "secret:" + ARGS[3]
    if identity not in STATE["resources"]:
        missing()
    path = Path(flag("data-file"))
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        error("Demo mock refused a secret file without mode 0600", 2)
    value = path.read_bytes()
    if not value:
        error("Demo mock refused an empty secret version", 2)
    # This is intentionally only metadata. Never persist the private value.
    version = {"name": identity + "/versions/1", "state": "ENABLED",
               "length": len(value), "sha256": hashlib.sha256(value).hexdigest(), "mode": "0600"}
    STATE["resources"][identity].setdefault("versions", []).append(version)
    out(version)

for prefix, kind in [
    (["storage", "buckets"], "bucket"), (["iam", "service-accounts"], "sa"),
    (["iam", "workload-identity-pools", "providers"], "provider"),
    (["iam", "workload-identity-pools"], "pool"),
    (["artifacts", "repositories"], "artifact"), (["run", "services"], "run"),
    (["secrets"], "secret"),
]:
    if ARGS[:len(prefix)] != prefix:
        continue
    operation = ARGS[len(prefix)]
    name = ARGS[len(prefix) + 1] if len(ARGS) > len(prefix) + 1 else ""
    identity = kind + ":" + name if kind not in ("pool", "provider", "artifact") else kind
    if operation == "add-iam-policy-binding":
        add_binding(identity)
    if operation == "describe":
        if identity not in STATE["resources"]:
            missing()
        out(STATE["resources"][identity])
    if operation in ("create", "create-oidc"):
        value = {"description": flag("description"), "labels": labels(flag("labels"))}
        if kind == "artifact":
            value["format"] = "DOCKER"
        if kind == "sa":
            identity = "sa:" + name + "@demo-project-123.iam.gserviceaccount.com"
        if kind in ("pool", "provider"):
            value["state"] = "ACTIVE"
        if kind == "secret":
            value["versions"] = []
        STATE["resources"][identity] = value
        out(value)
    if operation in ("update", "update-oidc"):
        if identity not in STATE["resources"]:
            missing()
        STATE["resources"][identity]["labels"].update(labels(flag("update-labels")))
        out({})
    if operation == "delete":
        if kind in ("pool", "provider"):
            STATE["resources"][identity]["state"] = "DELETED"
        else:
            remove_resource(identity)
        out({})
    if operation == "undelete":
        STATE["resources"][identity]["state"] = "ACTIVE"
        out({})
if ARGS[:2] == ["run", "deploy"]:
    name = ARGS[2]
    STATE["resources"]["run:" + name] = {
        "metadata": {"labels": labels(flag("labels"))},
        "status": {"url": "https://" + name + "-demo.run.app"},
    }
    out({})
error("Unknown mock command: " + repr(ARGS), 2)
