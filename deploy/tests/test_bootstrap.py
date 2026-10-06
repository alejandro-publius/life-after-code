"""Test ownership and cleanup using labelled demo cloud responses, not an account."""

import errno
import hashlib
import json
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_APIS = {"storage.googleapis.com", "cloudresourcemanager.googleapis.com",
                 "serviceusage.googleapis.com"}
DEMO_SECRETS = {"gitlab-token": "labelled-demo-gitlab-value-not-a-real-token",
                "unleash-instance-id": "labelled-demo-unleash-value-not-a-real-key"}

# Only the REST transport is replaced here. Its payload and ownership tests live
# with the Monitoring helper. This fixture keeps these shell tests off the network.
DEMO_OPS_HELPER = '''\
import json
import os
from pathlib import Path
import sys

path = Path(os.environ["LAC_OPS_STATE_FILE"])
state = json.loads(path.read_text())
remote = Path(os.environ["LAC_MOCK_REMOTE"])
cloud = json.loads(remote.read_text())
resources = ("scheduler-job", "uptime-check", "notification-channel", "alert-policy")
if sys.argv[1] == "setup":
    for resource in resources:
        if resource not in state["resources"]:
            state["resources"].append(resource)
        state.setdefault("ops", {})[resource] = "labelled-demo-" + resource
        cloud["resources"].setdefault("ops:" + resource, {"description": os.environ["LAC_OPS_OWNER_DESCRIPTION"]})
elif sys.argv[1] == "teardown":
    for resource in resources:
        if resource in state["resources"]:
            cloud["resources"].pop("ops:" + resource, None)
    state["ops"] = {}
else:
    raise SystemExit("Unknown demo operation")
path.write_text(json.dumps(state))
remote.write_text(json.dumps(cloud))
'''


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lac-demo-cloud-")
        self.directory = Path(self.temporary.name)
        binary = self.directory / "bin"
        binary.mkdir()
        shutil.copyfile(Path(__file__).with_name("demo_gcloud.py"), binary / "gcloud")
        (binary / "gcloud").chmod(0o700)
        self.remote = self.directory / "demo-cloud.json"
        self.state = self.directory / "demo-state.json"
        ops_helper = self.directory / "demo_ops.py"
        ops_helper.write_text(DEMO_OPS_HELPER)
        self.environment = os.environ.copy()
        self.environment.update(
            PATH=str(binary) + os.pathsep + self.environment["PATH"],
            LAC_MOCK_REMOTE=str(self.remote), LAC_STATE_FILE=str(self.state),
            LAC_OPS_HELPER=str(ops_helper), ALERT_EMAIL="alex@example.invalid",
            GCP_PROJECT_ID="demo-project-123", GITLAB_PROJECT_ID="99",
            GITLAB_PROJECT_PATH="demo/project", GITLAB_NAMESPACE_ID="88",
            GCP_DEDICATED_PROJECT="true", GCP_REGION="us-central1",
            GITLAB_DEFAULT_BRANCH="main",
        )
        self.environment.pop("LAC_MOCK_PERMISSION", None)

    def tearDown(self):
        self.temporary.cleanup()

    def interactive_script(self, command, demo_values):
        """Exercise /dev/tty reads with an actual controlling terminal."""
        process, master = pty.fork()
        if process == 0:
            os.chdir(ROOT.parent)
            os.execvpe(command[0], command, self.environment)
        output = bytearray()
        supplied = set()
        deadline = time.monotonic() + 60
        status = None
        try:
            while status is None:
                if time.monotonic() > deadline:
                    os.killpg(process, signal.SIGKILL)
                    os.waitpid(process, 0)
                    self.fail("Demo bootstrap timed out: " + output.decode(errors="replace"))
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError as error:
                        if error.errno != errno.EIO:
                            raise
                        chunk = b""
                    output.extend(chunk)
                    for secret_id, value in demo_values.items():
                        prompt = ("Paste " + secret_id + " (hidden), then press Enter: ").encode()
                        if secret_id not in supplied and prompt in output:
                            os.write(master, value.encode() + b"\n")
                            supplied.add(secret_id)
                completed, process_status = os.waitpid(process, os.WNOHANG)
                if completed:
                    status = process_status
            # Read the final bytes, which can arrive with the process exit.
            while select.select([master], [], [], 0)[0]:
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno != errno.EIO:
                        raise
                    break
                if not chunk:
                    break
                output.extend(chunk)
        finally:
            os.close(master)
        return subprocess.CompletedProcess(command, os.waitstatus_to_exitcode(status),
                                           output.decode(errors="replace").replace("\r\n", "\n"), "")

    def run_script(self, name, *arguments, success=True, interactive=True, demo_values=None):
        command = ["bash", str(ROOT / name), *arguments]
        if interactive:
            result = self.interactive_script(command, DEMO_SECRETS if demo_values is None else demo_values)
        else:
            result = subprocess.run(command, cwd=ROOT.parent, env=self.environment,
                                    text=True, capture_output=True, timeout=60)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        for value in DEMO_SECRETS.values():
            self.assertNotIn(value, result.stdout + result.stderr)
        return result

    def cloud(self):
        return json.loads(self.remote.read_text())

    def setup_cloud(self, **options):
        return self.run_script("setup_gcp.sh", **options)

    def teardown_cloud(self):
        self.run_script("teardown_gcp.sh", "--confirm-project", "demo-project-123")

    @staticmethod
    def resource_creates(cloud):
        return [command for command in cloud["commands"]
                if command[:3] != ["beta", "services", "identity"]
                and ("create" in command or "create-oidc" in command
                     or command[:2] == ["run", "deploy"])]

    @staticmethod
    def secret_versions(cloud):
        return {identity: resource["versions"] for identity, resource in cloud["resources"].items()
                if identity.startswith("secret:")}

    @staticmethod
    def member(kind):
        return "serviceAccount:lac-99-" + kind + "@demo-project-123.iam.gserviceaccount.com"

    def bindings_for(self, role, member):
        return {binding["scope"] for binding in self.cloud()["bindings"]
                if binding["role"] == role and member in binding["members"]}

    def test_second_setup_creates_no_duplicate_resources(self):
        self.setup_cloud()
        first = self.resource_creates(self.cloud())
        self.setup_cloud(interactive=False)
        self.assertEqual(first, self.resource_creates(self.cloud()))

    def test_restore_missing_local_state_from_owned_bucket(self):
        self.setup_cloud()
        before = json.loads(self.state.read_text())
        self.state.unlink()
        self.setup_cloud(interactive=False)
        self.assertEqual(before, json.loads(self.state.read_text()))

    def test_wrong_project_confirmation_deletes_nothing(self):
        self.setup_cloud()
        before = self.cloud()
        self.run_script("teardown_gcp.sh", "--confirm-project", "other-project", success=False)
        self.assertEqual(before, self.cloud())

    def test_teardown_removes_owned_resources_and_preserves_original_apis(self):
        self.setup_cloud()
        self.teardown_cloud()
        cloud = self.cloud()
        self.assertFalse(cloud["project"]["labels"])
        self.assertFalse(cloud["budgets"])
        self.assertFalse(cloud["bindings"])
        self.assertFalse(cloud["objects"])
        self.assertEqual(set(cloud["apis"]), ORIGINAL_APIS)
        self.assertTrue(all(value.get("state") == "DELETED"
                            for value in cloud["resources"].values()))

    def test_second_teardown_is_safe(self):
        self.setup_cloud()
        self.teardown_cloud()
        before = self.cloud()
        self.teardown_cloud()
        self.assertEqual(before, self.cloud())

    def test_setup_after_teardown_restores_soft_deleted_wif(self):
        self.setup_cloud()
        self.teardown_cloud()
        self.setup_cloud()
        self.assertEqual(self.cloud()["resources"]["pool"]["state"], "ACTIVE")
        self.assertEqual(self.cloud()["resources"]["provider"]["state"], "ACTIVE")

    def test_permission_error_is_not_treated_as_a_missing_service_account(self):
        self.environment["LAC_MOCK_PERMISSION"] = "iam service-accounts describe"
        result = self.run_script("setup_gcp.sh", success=False)
        self.assertIn("PERMISSION_DENIED", result.stdout + result.stderr)
        self.assertFalse(any(command[:3] == ["iam", "service-accounts", "create"]
                             for command in self.cloud()["commands"]))

    def test_budget_permission_error_stops_before_app_resources(self):
        self.environment["LAC_MOCK_PERMISSION"] = "billing budgets list"
        result = self.run_script("setup_gcp.sh", success=False)
        self.assertIn("PERMISSION_DENIED", result.stdout + result.stderr)
        self.assertFalse(self.cloud()["resources"])

    def seed_foreign(self, identity, value):
        subprocess.run(["gcloud", "projects", "describe", "demo-project-123"],
                       env=self.environment, check=True, capture_output=True)
        cloud = self.cloud()
        cloud["resources"][identity] = value
        self.remote.write_text(json.dumps(cloud))

    def assert_foreign_preserved(self, identity, foreign):
        self.seed_foreign(identity, foreign)
        result = self.run_script("setup_gcp.sh", success=False)
        self.assertIn("Ownership collision", result.stdout + result.stderr)
        self.teardown_cloud()
        self.assertEqual(self.cloud()["resources"][identity], foreign)

    def test_foreign_service_account_collision_is_never_deleted(self):
        self.assert_foreign_preserved("sa:lac-99-deploy@demo-project-123.iam.gserviceaccount.com",
                                      {"description": "Demo service account owned by someone else"})

    def test_foreign_secret_collision_is_never_deleted(self):
        self.assert_foreign_preserved("secret:gitlab-token",
                                      {"labels": {"lac-owner": "someone-else"}, "versions": []})

    def test_foreign_state_bucket_collision_is_never_deleted(self):
        self.assert_foreign_preserved("bucket:gs://demo-project-123-night-orders-state",
                                      {"labels": {"lac-owner": "someone-else"}})

    def test_three_services_have_separate_runtime_accounts_and_limits(self):
        self.setup_cloud()
        commands = {command[2]: command for command in self.cloud()["commands"]
                    if command[:2] == ["run", "deploy"]}
        self.assertEqual(set(commands), {"shop", "shop-staging", "relay"})
        for service, command in commands.items():
            account = {"shop": "shop", "shop-staging": "staging", "relay": "relay"}[service]
            self.assertIn("--service-account=" + self.member(account).split(":", 1)[1], command)
            self.assertIn("--max-instances=1", command)
            self.assertFalse(any(flag.startswith("--max=") for flag in command))
            if service == "relay":
                self.assertIn("--timeout=60", command)
                self.assertIn("--memory=256Mi", command)
                self.assertIn("--cpu-throttling", command)
            else:
                self.assertIn("--memory=512Mi", command)
                self.assertIn("--no-cpu-throttling", command)

    def test_relay_permissions_are_scoped_to_shop_resources_and_state(self):
        self.setup_cloud()
        relay = self.member("relay")
        self.assertEqual(self.bindings_for("roles/run.developer", relay),
                         {"run:shop", "run:shop-staging"})
        self.assertEqual(self.bindings_for("roles/iam.serviceAccountUser", relay),
                         {"sa:" + self.member(kind).split(":", 1)[1] for kind in ("shop", "staging")})
        self.assertEqual(self.bindings_for("roles/storage.objectUser", relay),
                         {"bucket:gs://demo-project-123-night-orders-state"})
        self.assertEqual(self.bindings_for("roles/logging.viewer", relay), {"project"})
        self.assertFalse(any(binding["role"] in {"roles/owner", "roles/editor", "roles/run.admin"}
                             for binding in self.cloud()["bindings"]))

    def test_secret_accessor_matches_only_service_manifest(self):
        self.setup_cloud()
        self.assertEqual(self.bindings_for("roles/secretmanager.secretAccessor", self.member("relay")),
                         {"secret:" + name for name in ("gitlab-token", "relay-key", "ntfy-url", "demo-key")})
        for account in ("shop", "staging"):
            self.assertEqual(self.bindings_for("roles/secretmanager.secretAccessor", self.member(account)),
                             {"secret:unleash-instance-id", "secret:demo-key"})
        for account in ("deploy", "build"):
            self.assertFalse(self.bindings_for("roles/secretmanager.secretAccessor", self.member(account)))

    def test_private_versions_use_mode_0600_and_never_rotate_on_rerun(self):
        result = self.setup_cloud()
        versions = self.secret_versions(self.cloud())
        self.assertEqual(len(versions), 5)
        for value in versions.values():
            self.assertEqual(len(value), 1)
            self.assertEqual(value[0]["mode"], "0600")
            self.assertGreater(value[0]["length"], 0)
        for secret_id, demo_value in DEMO_SECRETS.items():
            self.assertEqual(versions["secret:" + secret_id][0]["sha256"],
                             hashlib.sha256(demo_value.encode()).hexdigest())
        self.assertNotIn("https://ntfy.sh/", result.stdout + result.stderr)
        for demo_value in DEMO_SECRETS.values():
            self.assertNotIn(demo_value, self.remote.read_text())
        self.setup_cloud(interactive=False)
        self.assertEqual(versions, self.secret_versions(self.cloud()))
        self.assertFalse(any(command[:3] == ["secrets", "versions", "access"]
                             for command in self.cloud()["commands"]))

    def test_empty_interactive_value_is_refused_without_a_version(self):
        result = self.setup_cloud(success=False, demo_values={"gitlab-token": ""})
        self.assertIn("An empty private value was refused", result.stdout + result.stderr)
        self.assertFalse(self.cloud()["resources"]["secret:gitlab-token"]["versions"])
        self.teardown_cloud()

    def test_disabled_newest_version_is_not_silently_rotated(self):
        self.setup_cloud()
        cloud = self.cloud()
        cloud["resources"]["secret:gitlab-token"]["versions"].append(
            {"name": "secret:gitlab-token/versions/2", "state": "DISABLED"})
        self.remote.write_text(json.dumps(cloud))
        before = self.secret_versions(cloud)
        result = self.setup_cloud(success=False, interactive=False)
        self.assertIn("latest secret version is disabled", result.stdout + result.stderr)
        self.assertEqual(before, self.secret_versions(self.cloud()))


if __name__ == "__main__":
    unittest.main()
