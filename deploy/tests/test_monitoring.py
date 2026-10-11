"""Ops ownership, secret handling, and paused-first scheduling without cloud calls."""

import base64
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import urllib.error
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "deployment_monitoring", Path(__file__).resolve().parents[1] / "monitoring.py")
monitoring = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitoring)

DEMO_KEY = "labelled-demo-relay-key-not-real-0123456789"
DEMO_EMAIL = "labelled-demo@example.invalid"
PROJECT = "labelled-demo-project"
NUMBER = "123456789"
OWNER = "Life After Code bootstrap: GitLab labelled-demo/project, project 456."


class MemoryJournal:
    def __init__(self):
        self.value = {"config": {"GCP_PROJECT_ID": PROJECT}, "resources": [], "ops": {}}
        self.snapshots = []

    def save(self):
        self.snapshots.append(json.dumps(self.value))

    def owns(self, kind):
        return kind in self.value["resources"]

    def intent(self, kind):
        if not self.owns(kind):
            self.value["resources"].append(kind)
            self.save()

    def record(self, kind, name):
        self.value["ops"][kind] = name
        self.save()


class MemoryCloud:
    def __init__(self):
        self.resources, self.requests = {}, []
        self.fail_pause_once = False
        self.use_project_number = False

    def call(self, api, method, path, body=None, query=None, missing_ok=False):
        self.requests.append((api, method, path, copy.deepcopy(body)))
        if api == "secrets":
            return {"payload": {"data": base64.b64encode(DEMO_KEY.encode()).decode()}}
        if method == "GET":
            return copy.deepcopy(self.resources.get(path))
        if method == "POST" and path.endswith(":pause"):
            if self.fail_pause_once:
                self.fail_pause_once = False
                raise monitoring.SetupError("Labelled demo interruption after creation")
            self.resources[path.removesuffix(":pause")]["state"] = "PAUSED"
            return copy.deepcopy(self.resources[path.removesuffix(":pause")])
        if method == "POST":
            name = body.get("name") or path + "/demo-" + str(len(self.resources) + 1)
            if self.use_project_number:
                name = name.replace("projects/" + PROJECT + "/", "projects/" + NUMBER + "/")
            value = copy.deepcopy(dict(body, name=name))
            if api == "scheduler":
                value["state"] = "ENABLED"
            self.resources[name] = value
            return copy.deepcopy(value)
        if method == "PATCH":
            self.resources[path].update(copy.deepcopy(body))
            return copy.deepcopy(self.resources[path])
        if method == "DELETE":
            del self.resources[path]
            return {}
        raise AssertionError("Unknown labelled demo API method")

    def listing(self, api, path, field):
        # A real Google response can normalize project ID to project number.
        matches = (path + "/", path.replace(PROJECT, NUMBER) + "/")
        return [copy.deepcopy(value) for name, value in self.resources.items()
                if any(name.startswith(prefix) for prefix in matches)]


class OpsTests(unittest.TestCase):
    def setUp(self):
        self.journal, self.cloud = MemoryJournal(), MemoryCloud()
        self.ops = monitoring.Operations(self.cloud, self.journal, PROJECT,
                                         "us-central1", "456", OWNER, NUMBER)

    def setup_resources(self):
        self.ops.setup("https://labelled-demo-relay-abc.a.run.app", DEMO_EMAIL, "relay-key")

    def test_new_job_is_paused_then_gets_minute_schedule(self):
        self.setup_resources()
        name = self.journal.value["ops"]["scheduler-job"]
        job = self.cloud.resources[name]
        self.assertEqual(job["state"], "PAUSED")
        self.assertEqual(job["schedule"], "* * * * *")
        self.assertEqual(job["httpTarget"]["httpMethod"], "POST")
        self.assertEqual(job["httpTarget"]["headers"]["X-Relay-Key"], DEMO_KEY)
        self.assertTrue(job["httpTarget"]["uri"].endswith("/tick"))
        self.assertEqual(job["retryConfig"], {"retryCount": 0, "maxRetryDuration": "0s"})
        self.assertEqual(job["attemptDeadline"], "60s")
        creation = next(r for r in self.cloud.requests if r[0] == "scheduler" and r[1] == "POST"
                        and not r[2].endswith(":pause"))
        self.assertEqual(creation[3]["schedule"], "0 0 1 1 *")
        self.assertFalse(self.journal.value["ops_scheduler_pending"])

    def test_rerun_updates_without_recreating_or_resuming(self):
        self.setup_resources()
        creates = sum(r[1] == "POST" for r in self.cloud.requests)
        self.setup_resources()
        self.assertEqual(sum(r[1] == "POST" for r in self.cloud.requests), creates)
        job = self.cloud.resources[self.journal.value["ops"]["scheduler-job"]]
        self.assertEqual(job["state"], "PAUSED")
        self.assertEqual(len(self.cloud.resources), 4)

    def test_rerun_preserves_an_enabled_scheduler(self):
        self.setup_resources()
        job_name = self.journal.value["ops"]["scheduler-job"]
        self.cloud.resources[job_name]["state"] = "ENABLED"
        pauses_before = sum(r[2].endswith(":pause") for r in self.cloud.requests)
        self.setup_resources()
        self.assertEqual(self.cloud.resources[job_name]["state"], "ENABLED")
        self.assertEqual(sum(r[2].endswith(":pause") for r in self.cloud.requests), pauses_before)

    def test_recovers_an_interruption_before_initial_pause(self):
        self.cloud.fail_pause_once = True
        with self.assertRaises(monitoring.SetupError):
            self.setup_resources()
        job_name = self.journal.value["ops"]["scheduler-job"]
        self.assertEqual(self.cloud.resources[job_name]["schedule"], "0 0 1 1 *")
        self.assertTrue(self.journal.value["ops_scheduler_pending"])
        self.setup_resources()
        self.assertEqual(self.cloud.resources[job_name]["state"], "PAUSED")
        self.assertEqual(self.cloud.resources[job_name]["schedule"], "* * * * *")

    def test_journal_contains_neither_key_nor_email(self):
        self.setup_resources()
        for snapshot in self.journal.snapshots:
            self.assertNotIn(DEMO_KEY, snapshot)
            self.assertNotIn(DEMO_EMAIL, snapshot)
        self.assertEqual(set(self.journal.value["ops"]),
                         {"scheduler-job", "uptime-check", "notification-channel", "alert-policy"})
        self.assertTrue(all(isinstance(name, str) for name in self.journal.value["ops"].values()))

    def test_check_and_policy_cover_only_relay_health(self):
        self.setup_resources()
        check = self.cloud.resources[self.journal.value["ops"]["uptime-check"]]
        self.assertEqual(check["httpCheck"]["path"], "/healthz")
        self.assertEqual(check["httpCheck"]["port"], 443)
        self.assertTrue(check["httpCheck"]["validateSsl"])
        self.assertEqual(check["selectedRegions"], ["USA"])
        self.assertEqual(check["period"], "60s")
        policy = self.cloud.resources[self.journal.value["ops"]["alert-policy"]]
        threshold = policy["conditions"][0]["conditionThreshold"]
        check_id = check["name"].rsplit("/", 1)[1]
        self.assertIn(check_id, threshold["filter"])
        self.assertEqual(threshold["duration"], "120s")
        self.assertEqual(policy["notificationChannels"],
                         [self.journal.value["ops"]["notification-channel"]])

    def test_owned_resource_with_missing_journal_is_not_adopted(self):
        self.setup_resources()
        self.journal.value["resources"].remove("scheduler-job")
        before = copy.deepcopy(self.cloud.resources)
        with self.assertRaisesRegex(monitoring.SetupError, "ownership collision"):
            self.setup_resources()
        self.assertEqual(self.cloud.resources, before)

    def test_teardown_refuses_a_changed_owner(self):
        self.setup_resources()
        name = self.journal.value["ops"]["scheduler-job"]
        self.cloud.resources[name]["description"] = "Someone else's resource"
        before = copy.deepcopy(self.cloud.resources)
        with self.assertRaisesRegex(monitoring.SetupError, "ownership collision"):
            self.ops.teardown()
        self.assertEqual(self.cloud.resources, before)

    def test_teardown_is_idempotent_and_keeps_unrelated_resources(self):
        self.setup_resources()
        unrelated = "projects/" + PROJECT + "/alertPolicies/other"
        self.cloud.resources[unrelated] = {"name": unrelated, "displayName": "Someone else"}
        self.ops.teardown()
        self.ops.teardown()
        self.assertEqual(set(self.cloud.resources), {unrelated})
        self.assertEqual(self.journal.value["ops"], {})

    def test_project_number_names_are_accepted_but_other_projects_are_not(self):
        self.cloud.use_project_number = True
        self.setup_resources()
        self.ops.validate_name("uptime-check", "projects/" + NUMBER + "/uptimeCheckConfigs/demo")
        with self.assertRaises(monitoring.SetupError):
            self.ops.validate_name("uptime-check", "projects/999/uptimeCheckConfigs/demo")

    def test_invalid_relay_host_is_rejected_before_any_api_request(self):
        with self.assertRaises(monitoring.SetupError):
            self.ops.setup("https://labelled-demo.run.app.attacker.invalid", DEMO_EMAIL, "relay-key")
        self.assertEqual(self.cloud.requests, [])


class TransportTests(unittest.TestCase):
    def fake_cloud(self):
        fake = subprocess.CompletedProcess(["gcloud"], 0, "labelled-demo-token", "")
        with patch.object(monitoring.subprocess, "run", return_value=fake):
            return monitoring.CloudApi(PROJECT)

    def test_auth_token_never_enters_arguments(self):
        fake = subprocess.CompletedProcess(["gcloud"], 0, "labelled-demo-token", "")
        with patch.object(monitoring.subprocess, "run", return_value=fake) as command:
            cloud = monitoring.CloudApi(PROJECT)
        self.assertEqual(cloud.token, "labelled-demo-token")
        self.assertEqual(command.call_args.args[0],
                         ["gcloud", "auth", "print-access-token", "--quiet"])
        self.assertNotIn("labelled-demo-token", str(command.call_args.args))

    def test_api_error_body_is_not_printed_and_only_404_is_missing(self):
        cloud = self.fake_cloud()
        error = urllib.error.HTTPError("https://labelled-demo.invalid", 403,
                                       DEMO_KEY, {}, io.BytesIO(DEMO_EMAIL.encode()))
        with patch.object(cloud.opener, "open", side_effect=error):
            with self.assertRaises(monitoring.SetupError) as caught:
                cloud.call("scheduler", "GET", "projects/" + PROJECT + "/jobs/demo", missing_ok=True)
        self.assertIn("403", str(caught.exception))
        self.assertNotIn(DEMO_KEY, str(caught.exception))
        self.assertNotIn(DEMO_EMAIL, str(caught.exception))
        missing = urllib.error.HTTPError("https://labelled-demo.invalid", 404, "demo", {}, io.BytesIO())
        with patch.object(cloud.opener, "open", side_effect=missing):
            self.assertIsNone(cloud.call("scheduler", "GET", "projects/" + PROJECT + "/jobs/demo",
                                        missing_ok=True))

    def test_time_limit_stops_before_a_request(self):
        cloud = self.fake_cloud()
        cloud.deadline = 0
        with patch.object(cloud.opener, "open") as request:
            with self.assertRaisesRegex(monitoring.SetupError, "time limit"):
                cloud.call("scheduler", "GET", "projects/" + PROJECT + "/jobs/demo")
        request.assert_not_called()

    def test_redirect_refuses_to_forward_authorization(self):
        with self.assertRaises(monitoring.SetupError):
            monitoring.NoRedirect().redirect_request(None, None, 302, "demo", {},
                                                      "https://labelled-demo-attacker.invalid")

    def test_backup_contains_only_the_journal_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"config": {"GCP_PROJECT_ID": PROJECT}, "resources": []}))
            journal = monitoring.Journal(path, "labelled-demo-source-bucket")
            journal.value["ops"]["scheduler-job"] = "projects/" + PROJECT + "/locations/us-central1/jobs/relay-tick"
            response = subprocess.CompletedProcess(["gcloud"], 0, "", "")
            with patch.object(monitoring.subprocess, "run", return_value=response) as command:
                journal.save()
            self.assertNotIn(DEMO_EMAIL, path.read_text())
            self.assertNotIn(DEMO_KEY, path.read_text())
            self.assertEqual(command.call_args.args[0][:3], ["gcloud", "storage", "cp"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
