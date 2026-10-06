"""Check public config defaults and override behavior using only demo identifiers."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


DEPLOY = Path(__file__).resolve().parents[1]
KEYS = (
    "GCP_PROJECT_ID", "GCP_PROJECT_NUMBER", "GCP_REGION", "GCP_WIF_POOL",
    "GCP_WIF_PROVIDER", "GCP_SERVICE_ACCOUNT", "GCP_BUILD_SERVICE_ACCOUNT",
    "GCP_RUNTIME_SERVICE_ACCOUNT", "GCP_ARTIFACT_REPOSITORY", "GCP_SOURCE_BUCKET",
    "GCP_RUN_SERVICE", "GITLAB_PROJECT_ID", "GITLAB_PROJECT_PATH",
)


class PublicConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lac-demo-config-")
        self.directory = Path(self.temporary.name)
        self.config = self.directory / "gcp.env"
        self.environment = {k: v for k, v in os.environ.items() if k not in KEYS}

    def tearDown(self):
        self.temporary.cleanup()

    def load(self, text, overrides=None):
        self.config.write_bytes(text.encode())
        command = (
            'set -euo pipefail; source "$1"; load_gcp_config "$2"; '
            'python3 -c "import json, os; '
            "print(json.dumps({k: os.environ.get(k) for k in "
            "('GCP_PROJECT_ID','GCP_REGION')}))\""
        )
        return subprocess.run(
            ["bash", "-c", command, "demo", str(DEPLOY / "gcp_config.sh"), str(self.config)],
            env=self.environment | (overrides or {}), capture_output=True, text=True, timeout=10,
        )

    def test_file_defaults_and_ci_override(self):
        result = self.load("# Demo identifiers\r\nGCP_PROJECT_ID=demo-project-123\r\nGCP_REGION=us-central1",
                           {"GCP_REGION": "us-east1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "GCP_PROJECT_ID": "demo-project-123", "GCP_REGION": "us-east1",
        })

    def test_explicit_empty_ci_value_overrides_file(self):
        result = self.load("GCP_PROJECT_ID=demo-project-123\n", {"GCP_PROJECT_ID": ""})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["GCP_PROJECT_ID"], "")

    def test_shell_expression_is_rejected_without_execution(self):
        marker = self.directory / "should-not-exist"
        result = self.load("GCP_PROJECT_ID=$(touch " + str(marker) + ")\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())

    def test_secret_key_and_duplicate_key_are_rejected(self):
        for text in ("GITLAB_OIDC_TOKEN=demo-not-a-real-token\n",
                     "GCP_REGION=us-central1\nGCP_REGION=us-east1\n"):
            with self.subTest(text=text):
                self.assertNotEqual(self.load(text).returncode, 0)

    def test_ci_helper_loads_committed_file_before_authentication(self):
        for name in ("ci_deploy.sh", "gcp_config.sh"):
            shutil.copyfile(DEPLOY / name, self.directory / name)
        values = dict(zip(KEYS, (
            "demo-project-123", "123456789", "us-central1", "lac-99-pool", "gitlab",
            "lac-99-deploy@demo-project-123.iam.gserviceaccount.com",
            "lac-99-build@demo-project-123.iam.gserviceaccount.com",
            "lac-99-runtime@demo-project-123.iam.gserviceaccount.com",
            "lac-99", "demo-project-123-lac-99-source", "lac-99", "99", "demo/project",
        )))
        self.config.write_text("# Demo identifiers only\n" + "".join(
            f"{key}={value}\n" for key, value in values.items()))
        binary = self.directory / "bin"
        binary.mkdir()
        fake = binary / "gcloud"
        fake.write_text('#!/usr/bin/env bash\nprintf "demo-auth-reached:%s:%s\\n" "$GCP_PROJECT_ID" "$GCP_REGION"\nexit 42\n')
        fake.chmod(0o700)
        environment = self.environment | {
            "PATH": str(binary) + os.pathsep + self.environment["PATH"],
            "GCP_REGION": "us-east1", "GITLAB_OIDC_TOKEN": "demo-not-a-real-token",
            "CI_PROJECT_ID": "99", "CI_PROJECT_PATH": "demo/project",
            "CI_COMMIT_SHA": "a" * 40, "CI_COMMIT_SHORT_SHA": "a" * 8,
            "CI_COMMIT_BRANCH": "main", "CI_DEFAULT_BRANCH": "main",
            "CI_COMMIT_REF_PROTECTED": "true", "CI_DEBUG_TRACE": "false",
        }
        result = subprocess.run(["bash", str(self.directory / "ci_deploy.sh")],
                                env=environment, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 42, result.stdout + result.stderr)
        self.assertIn("demo-auth-reached:demo-project-123:us-east1", result.stdout)


if __name__ == "__main__":
    unittest.main()
