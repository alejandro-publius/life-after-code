"""Provisioning is read-only by default and cannot silently replace an existing Duo flow."""

import copy
import io
import json

import pytest

from scripts import setup_flows
from test_day_one import API, PROJECT, TOKEN, Server, body

GID = "gid://gitlab/Project/123"


class Catalog:
    def __init__(self):
        self.items = []
        self.nodes = []
        self.mutations = []
        self.hide_created = False

    def item(self, key, *, project=GID):
        item = {"id": f"gid://gitlab/Ai::Catalog::Item/{len(self.items) + 1}",
                "name": f"night-orders-{key}", "project": {"id": project},
                "latestVersion": {"id": f"version-{key}", "released": True,
                                  "definition": (setup_flows.ROOT / "flows" / f"{key}.yml").read_text()}}
        self.items.append(item)
        return item

    def enable(self, item):
        node = {"id": f"gid://gitlab/Ai::Catalog::ItemConsumer/{len(self.nodes) + 30}",
                "enabled": True, "item": item, "pinnedItemVersion": copy.deepcopy(item["latestVersion"]),
                "serviceAccount": None, "parentItemConsumer": None,
                "flowTriggers": [{"active": True, "user": {"username": "actual-" + item["name"]}}]}
        self.nodes.append(node)
        return node

    @staticmethod
    def connection(nodes):
        return {"nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}}

    def request(self, request):
        sent = body(request)
        query, variables = sent["query"], sent["variables"]
        if "aiCatalogConfiguredItems(" in query:
            return {"data": {"aiCatalogConfiguredItems": self.connection([] if self.hide_created else self.nodes)}}
        if "aiCatalogItems(" in query:
            return {"data": {"aiCatalogItems": self.connection(self.items)}}
        self.mutations.append(sent)
        data = variables["input"]
        if "aiCatalogFlowCreate(" in query:
            key = data["name"].removeprefix("night-orders-")
            item = self.item(key)
            item["latestVersion"]["definition"] = data["definition"]
            return {"data": {"aiCatalogFlowCreate": {"item": item, "errors": []}}}
        if "aiCatalogItemConsumerCreate(" in query:
            item = next(item for item in self.items if item["id"] == data["itemId"])
            return {"data": {"aiCatalogItemConsumerCreate": {"itemConsumer": self.enable(item), "errors": []}}}
        raise AssertionError(query)


def run(catalog, tmp_path, *args, graph=None):
    server = Server({("GET", API): PROJECT, ("POST", "/api/graphql"): graph or catalog.request})
    out = io.StringIO()
    target = tmp_path / "flows.json"
    code = setup_flows.main(["--project", "123", "--base-url", "https://gitlab.example",
                            "--out", str(target), *args],
                           env={"GITLAB_TOKEN": TOKEN}, client=server.client(), out=out)
    return code, out.getvalue(), json.loads(target.read_text()) if target.exists() else None, server


def test_check_reports_missing_flows_without_creating_anything(tmp_path):
    catalog = Catalog()
    catalog.enable(catalog.item("watch"))
    code, text, report, server = run(catalog, tmp_path)
    assert code == 1 and not report["ready"]
    assert [flow["status"] for flow in report["flows"]] == ["blocked", "ready", "blocked"]
    assert report["values"]["FLOW_SERVICE_ACCOUNT"] == "actual-night-orders-watch"
    assert catalog.mutations == []
    assert "--apply" in text and "Flow execution: not started" in text
    assert all(request.url.path in (API, "/api/graphql") for request in server.requests)


def test_apply_installs_dusk_and_dawn_once_reuses_watch_and_reports_real_accounts(tmp_path):
    catalog = Catalog()
    original = copy.deepcopy(catalog.enable(catalog.item("watch")))
    code, text, report, _ = run(catalog, tmp_path, "--apply")
    assert code == 0, text
    assert report["ready"] and len(report["operations"]) == 4
    assert catalog.nodes[0] == original
    assert {flow["execution"] for flow in report["flows"]} == {"not_run"}
    assert report["values"]["DUSK_FLOW_SERVICE_ACCOUNT"] == "actual-night-orders-dusk"
    assert report["values"]["DAWN_FLOW_SERVICE_ACCOUNT"] == "actual-night-orders-dawn"
    creates = [sent["variables"]["input"] for sent in catalog.mutations if "aiCatalogFlowCreate(" in sent["query"]]
    assert {item["name"] for item in creates} == {"night-orders-dusk", "night-orders-dawn"}
    assert all(item["projectId"] == GID and item["release"] and item["visibility"] == "PRIVATE" for item in creates)
    enables = [sent["variables"]["input"] for sent in catalog.mutations
               if "aiCatalogItemConsumerCreate(" in sent["query"]]
    assert [item["triggerTypes"] for item in enables] == [["assign"], ["mention"]]
    assert all(item["target"] == {"projectId": GID} for item in enables)
    count = len(catalog.mutations)
    code, text, rerun, _ = run(catalog, tmp_path, "--apply")
    assert code == 0, text
    assert rerun["operations"] == [] and len(catalog.mutations) == count


@pytest.mark.parametrize("problem", ["disabled", "changed", "foreign", "unreleased", "ambiguous_account", "inactive"])
def test_existing_flow_is_never_silently_replaced_or_reported_ready(problem, tmp_path):
    catalog = Catalog()
    node = catalog.enable(catalog.item("watch"))
    if problem == "disabled":
        node["enabled"] = False
    elif problem == "changed":
        node["pinnedItemVersion"]["definition"] = "version: different"
    elif problem == "foreign":
        node["item"]["project"]["id"] = "gid://gitlab/Project/999"
    elif problem == "unreleased":
        node["pinnedItemVersion"]["released"] = False
    elif problem == "inactive":
        node["serviceAccount"] = {"username": "actual-night-orders-watch"}
        node["flowTriggers"][0]["active"] = False
    else:
        node["serviceAccount"] = {"username": "a-different-user"}
    original = copy.deepcopy(node)
    code, _, report, _ = run(catalog, tmp_path, "--flow", "watch", "--apply")
    assert code == 1 and not report["ready"] and report["values"] == {}
    assert catalog.mutations == [] and node == original


def test_catalog_item_owned_by_another_project_is_not_enabled(tmp_path):
    catalog = Catalog()
    foreign = catalog.item("dawn", project="gid://gitlab/Project/999")
    code, text, report, _ = run(catalog, tmp_path, "--flow", "dawn", "--apply")
    assert code == 0, text
    assert report["ready"]
    assert catalog.nodes[0]["item"]["id"] != foreign["id"]
    assert catalog.nodes[0]["item"]["project"]["id"] == GID


def test_failed_readback_is_not_reported_as_success(tmp_path):
    catalog = Catalog()
    catalog.hide_created = True
    code, _, report, _ = run(catalog, tmp_path, "--flow", "dusk", "--apply")
    assert code == 1 and not report["ready"]
    assert len(report["operations"]) == 2 and report["values"] == {}


def test_discovery_reads_later_pages_before_deciding_to_create(tmp_path):
    catalog = Catalog()
    catalog.enable(catalog.item("watch"))
    cursors = []

    def graph(request):
        sent = body(request)
        if "aiCatalogConfiguredItems(" in sent["query"]:
            cursor = sent["variables"]["after"]
            cursors.append(cursor)
            if cursor is None:
                return {"data": {"aiCatalogConfiguredItems": {
                    "nodes": [], "pageInfo": {"hasNextPage": True, "endCursor": "page-2"}}}}
        return catalog.request(request)

    code, text, report, _ = run(catalog, tmp_path, "--flow", "watch", "--apply", graph=graph)
    assert code == 0, text
    assert report["ready"] and cursors == [None, "page-2"] and catalog.mutations == []


def test_incomplete_discovery_stops_before_mutation(tmp_path):
    catalog = Catalog()

    def graph(request):
        return {"data": {"aiCatalogConfiguredItems": {"nodes": [], "pageInfo": {"hasNextPage": True}}}}

    code, text, _, _ = run(catalog, tmp_path, "--apply", graph=graph)
    assert code == 1 and "pagination is incomplete" in text and catalog.mutations == []


def test_all_local_flows_are_validated_before_any_network_work(tmp_path, monkeypatch):
    catalog = Catalog()
    monkeypatch.setattr(setup_flows, "check_flow", lambda path: ["bad flow"] if path.stem == "dawn" else [])
    code, text, _, server = run(catalog, tmp_path, "--apply")
    assert code == 1 and "dawn.yml: bad flow" in text
    assert server.requests == []


def test_remote_error_cannot_leak_token_to_output_or_report(tmp_path):
    catalog = Catalog()

    def graph(request):
        sent = body(request)
        if "aiCatalogFlowCreate(" in sent["query"]:
            return {"data": {"aiCatalogFlowCreate": {"errors": [f"Denied {TOKEN}"]}}}
        return catalog.request(request)

    code, text, report, _ = run(catalog, tmp_path, "--flow", "dawn", "--apply", graph=graph)
    assert code == 1 and TOKEN not in text and TOKEN not in json.dumps(report)
    assert "[GITLAB_TOKEN]" in json.dumps(report)


def test_matching_released_item_is_reused_after_partial_setup(tmp_path):
    catalog = Catalog()
    item = catalog.item("dusk")
    code, text, report, _ = run(catalog, tmp_path, "--flow", "dusk", "--apply")
    assert code == 0, text
    assert report["operations"] == [{"flow": "dusk", "operation": "enabled", "consumer_id": 30}]
    assert catalog.nodes[0]["item"]["id"] == item["id"]
