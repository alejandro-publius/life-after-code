"""Test ownership and cleanup using demo cloud responses, never a live account."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_APIS = {"storage.googleapis.com", "cloudresourcemanager.googleapis.com",
                 "serviceusage.googleapis.com"}


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
        self.environment = os.environ.copy()
        self.environment.update(
            PATH=str(binary) + os.pathsep + self.environment["PATH"],
            LAC_MOCK_REMOTE=str(self.remote), LAC_STATE_FILE=str(self.state),
            GCP_PROJECT_ID="demo-project-123", GITLAB_PROJECT_ID="99",
            GITLAB_PROJECT_PATH="demo/project", GITLAB_NAMESPACE_ID="88",
            GCP_DEDICATED_PROJECT="true", GCP_REGION="us-central1",
            GITLAB_DEFAULT_BRANCH="main",
        )
        self.environment.pop("LAC_MOCK_PERMISSION", None)

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, name, *arguments, success=True):
        result = subprocess.run(
            ["bash", str(ROOT / name), *arguments], cwd=ROOT.parent,
            env=self.environment, text=True, capture_output=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def cloud(self):
        return json.loads(self.remote.read_text())

    def setup_cloud(self):
        self.run_script("setup_gcp.sh")

    def teardown_cloud(self):
        self.run_script("teardown_gcp.sh", "--confirm-project", "demo-project-123")

    @staticmethod
    def resource_creates(cloud):
        return [command for command in cloud["commands"]
                if command[:3] != ["beta", "services", "identity"]
                and ("create" in command or "create-oidc" in command
                     or command[:2] == ["run", "deploy"])]

    def test_second_setup_creates_no_duplicate_resources(self):
        self.setup_cloud()
        first = self.resource_creates(self.cloud())
        self.setup_cloud()
        self.assertEqual(first, self.resource_creates(self.cloud()))

    def test_restore_missing_local_state_from_owned_bucket(self):
        self.setup_cloud()
        before = json.loads(self.state.read_text())
        self.state.unlink()
        self.setup_cloud()
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
        self.assertIn("PERMISSION_DENIED", result.stderr)
        self.assertFalse(any(command[:3] == ["iam", "service-accounts", "create"]
                             for command in self.cloud()["commands"]))

    def test_budget_permission_error_stops_before_app_resources(self):
        self.environment["LAC_MOCK_PERMISSION"] = "billing budgets list"
        result = self.run_script("setup_gcp.sh", success=False)
        self.assertIn("PERMISSION_DENIED", result.stderr)
        self.assertFalse(self.cloud()["resources"])

    def test_foreign_service_account_collision_is_never_deleted(self):
        subprocess.run(["gcloud", "projects", "describe", "demo-project-123"],
                       env=self.environment, check=True, capture_output=True)
        cloud = self.cloud()
        identity = "sa:lac-99-deploy@demo-project-123.iam.gserviceaccount.com"
        foreign = {"description": "Demo service account owned by someone else"}
        cloud["resources"][identity] = foreign
        self.remote.write_text(json.dumps(cloud))
        result = self.run_script("setup_gcp.sh", success=False)
        self.assertIn("Ownership collision", result.stderr)
        self.teardown_cloud()
        self.assertEqual(self.cloud()["resources"][identity], foreign)


if __name__ == "__main__":
    unittest.main()
