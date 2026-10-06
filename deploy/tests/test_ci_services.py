"""Run the real deployment helper with demo cloud commands and offline public health checks."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


DEPLOY = Path(__file__).resolve().parents[1]
COMMIT = "a" * 40
SHORT_COMMIT = COMMIT[:8]
DIGEST = "sha256:" + "b" * 64
BUILD_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
DEMO_PROJECT = "demo-project-123"
DEMO_PROJECT_ID = "99"
DEMO_SECRET_VALUES = {
    "GITLAB_OIDC_TOKEN": "demo-oidc-token-not-a-real-credential",
    "GITLAB_TOKEN": "demo-gitlab-token-not-a-real-credential",
    "RELAY_KEY": "demo-relay-key-not-a-real-credential",
    "NTFY_URL": "https://ntfy.sh/demo-unused-secret-topic",
    "DEMO_KEY": "demo-control-key-not-a-real-credential",
    "UNLEASH_INSTANCE_ID": "demo-unleash-id-not-a-real-credential",
}
DEMO_PUBLIC_CONFIG = {
    "GCP_PROJECT_ID": DEMO_PROJECT,
    "GCP_PROJECT_NUMBER": "123456789",
    "GCP_REGION": "us-central1",
    "GCP_WIF_POOL": "lac-99-pool",
    "GCP_WIF_PROVIDER": "gitlab",
    "GCP_SERVICE_ACCOUNT": f"lac-99-deploy@{DEMO_PROJECT}.iam.gserviceaccount.com",
    "GCP_BUILD_SERVICE_ACCOUNT": f"lac-99-build@{DEMO_PROJECT}.iam.gserviceaccount.com",
    "GCP_ARTIFACT_REPOSITORY": "lac-99",
    "GCP_SOURCE_BUCKET": f"{DEMO_PROJECT}-lac-99-source",
    "GCP_SHOP_SERVICE": "shop",
    "GCP_STAGING_SERVICE": "shop-staging",
    "GCP_RELAY_SERVICE": "relay",
    "GCP_SHOP_SERVICE_ACCOUNT": f"lac-99-shop@{DEMO_PROJECT}.iam.gserviceaccount.com",
    "GCP_STAGING_SERVICE_ACCOUNT": f"lac-99-staging@{DEMO_PROJECT}.iam.gserviceaccount.com",
    "GCP_RELAY_SERVICE_ACCOUNT": f"lac-99-relay@{DEMO_PROJECT}.iam.gserviceaccount.com",
    "GITLAB_PROJECT_ID": DEMO_PROJECT_ID,
    "GITLAB_PROJECT_PATH": "demo/project",
    "GITLAB_URL": "https://gitlab.com",
    "SHOP_URL": "https://shop-demo-123.run.app",
    "SHOP_STAGING_URL": "https://shop-staging-demo-123.run.app",
    "RELAY_URL": "https://relay-demo-123.run.app",
    "SHOP_METRICS_URL": "https://shop-demo-123.run.app/metrics.json",
    "STATE_BUCKET": f"{DEMO_PROJECT}-night-orders-state",
    "STATE_OBJECT": "night-orders/state.json",
    "UNLEASH_URL": "https://gitlab.com/api/v4/feature_flags/unleash/99",
    "FLOW_CONSUMER_ID": "",
    "FLOW_SERVICE_ACCOUNT": "",
    "DAWN_FLOW_CONSUMER_ID": "",
    "WATCH_ISSUE_IID": "",
}

FAKE_GCLOUD = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
record = {'args': args}
def value(prefix):
    return next((arg[len(prefix):] for arg in args if arg.startswith(prefix)), '')
if args[:2] == ['run', 'deploy']:
    record['public_env'] = json.loads(Path(value('--env-vars-file=')).read_text())
with Path(os.environ['DEMO_CALL_LOG']).open('a') as log:
    log.write(json.dumps(record) + '\n')
if args[:3] == ['iam', 'workload-identity-pools', 'create-cred-config']:
    Path(value('--output-file=')).write_text('{"type":"external_account"}')
elif args[:3] == ['run', 'services', 'describe']:
    if value('--format=') == 'json':
        print(json.dumps({'metadata': {'labels': {'lac-owner': os.environ.get('DEMO_OWNER', '99')}}}))
    else:
        print('https://' + args[3] + '-demo-123.run.app')
elif args[:2] == ['builds', 'submit']:
    print('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
elif args[:2] == ['builds', 'describe']:
    print('sha256:' + 'b' * 64)
elif args[:2] in (['auth', 'login'], ['config', 'set'], ['run', 'deploy']):
    pass
elif args[:3] == ['run', 'services', 'update-traffic']:
    pass
else:
    raise SystemExit('Unexpected cloud command in offline deployment test: ' + repr(args))
'''

# This patches only the public HTTP operation. Inline ownership, JSON environment,
# health validation and receipt code still execute with the real Python runtime.
HEALTH_STUB = r'''import io, json, os, urllib.request
from pathlib import Path
def demo_health(url, timeout=None):
    if not isinstance(url, str) or not url.startswith('https://') or not url.endswith('.run.app/healthz'):
        raise AssertionError('Only the public Cloud Run health URL is allowed in this offline test')
    if timeout != 20:
        raise AssertionError('The public health request needs a bounded timeout')
    with Path(os.environ['DEMO_HEALTH_LOG']).open('a') as log:
        log.write(json.dumps({'url': url, 'timeout': timeout}) + '\n')
    commit = os.environ.get('DEMO_HEALTH_COMMIT', os.environ['CI_COMMIT_SHORT_SHA'])
    return io.BytesIO(json.dumps({'ok': True, 'commit': commit}).encode())
urllib.request.urlopen = demo_health
'''


class DeploymentServicesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lac-demo-ci-services-")
        self.root = Path(self.temporary.name)
        self.deploy = self.root / "deploy"
        self.deploy.mkdir()
        for name in ("ci_deploy.sh", "gcp_config.sh"):
            shutil.copyfile(DEPLOY / name, self.deploy / name)
        (self.deploy / "gcp.env").write_text("# Demo public identifiers only\n" + "".join(
            f"{key}={value}\n" for key, value in DEMO_PUBLIC_CONFIG.items()))
        self.binary = self.root / "bin"
        self.binary.mkdir()
        (self.binary / "gcloud").write_text(FAKE_GCLOUD)
        (self.binary / "gcloud").chmod(0o700)
        (self.root / "sitecustomize.py").write_text(HEALTH_STUB)
        self.call_log = self.root / "cloud-calls.jsonl"
        self.health_log = self.root / "health-calls.jsonl"
        prefixes = ("GCP_", "GITLAB_", "CI_", "FLOW_", "DAWN_", "WATCH_", "SHOP_",
                    "STATE_", "UNLEASH_", "RELAY_", "DEMO_", "NTFY_", "APP_ENV")
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith(prefixes)}
        self.environment.update({
            "PATH": str(self.binary) + os.pathsep + self.environment["PATH"],
            "PYTHONPATH": str(self.root),
            "DEMO_CALL_LOG": str(self.call_log), "DEMO_HEALTH_LOG": str(self.health_log),
            "CI_PROJECT_ID": DEMO_PROJECT_ID, "CI_PROJECT_PATH": "demo/project",
            "CI_COMMIT_SHA": COMMIT, "CI_COMMIT_SHORT_SHA": SHORT_COMMIT,
            "CI_COMMIT_BRANCH": "main", "CI_DEFAULT_BRANCH": "main",
            "CI_COMMIT_REF_PROTECTED": "true", "CI_DEBUG_TRACE": "false",
        })
        self.environment.update(DEMO_SECRET_VALUES)

    def tearDown(self):
        self.temporary.cleanup()

    def run_deploy(self, target="shop", overrides=None):
        for path in (self.call_log, self.health_log, self.deploy / "result.json", self.deploy / "result.env"):
            path.unlink(missing_ok=True)
        return subprocess.run(["bash", "deploy/ci_deploy.sh", target], cwd=self.root,
                              env=self.environment | (overrides or {}),
                              capture_output=True, text=True, timeout=15)

    def calls(self):
        return [json.loads(line) for line in self.call_log.read_text().splitlines()] if self.call_log.exists() else []

    def one_call(self, prefix):
        matching = [call for call in self.calls() if call["args"][:len(prefix)] == prefix]
        self.assertEqual(len(matching), 1, matching)
        return matching[0]

    def test_all_three_services_use_their_own_build_and_runtime_settings(self):
        settings = {
            "shop": ("shop", "production", "GCP_SHOP_SERVICE_ACCOUNT", "--no-cpu-throttling", "512Mi", "30s"),
            "shop-staging": ("shop", "staging", "GCP_STAGING_SERVICE_ACCOUNT", "--no-cpu-throttling", "512Mi", "30s"),
            "relay": ("relay", None, "GCP_RELAY_SERVICE_ACCOUNT", "--cpu-throttling", "256Mi", "60s"),
        }
        for target, (app_dir, app_env, account_key, cpu, memory, timeout) in settings.items():
            with self.subTest(service=target):
                result = self.run_deploy(target)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                tagged_image = f"us-central1-docker.pkg.dev/{DEMO_PROJECT}/lac-99/{target}:{COMMIT}"
                immutable_image = f"us-central1-docker.pkg.dev/{DEMO_PROJECT}/lac-99/{target}@{DIGEST}"
                build = self.one_call(["builds", "submit"])["args"]
                self.assertIn(f"--substitutions=_IMAGE_URI={tagged_image},_COMMIT={SHORT_COMMIT},_APP_DIR={app_dir}", build)
                self.assertIn(f"--service-account=projects/{DEMO_PROJECT}/serviceAccounts/{DEMO_PUBLIC_CONFIG['GCP_BUILD_SERVICE_ACCOUNT']}", build)
                self.assertIn(f"--gcs-source-staging-dir=gs://{DEMO_PUBLIC_CONFIG['GCP_SOURCE_BUCKET']}/source", build)
                deployed = self.one_call(["run", "deploy"])
                args = deployed["args"]
                self.assertEqual(args[2], target)
                for flag in (f"--image={immutable_image}", f"--service-account={DEMO_PUBLIC_CONFIG[account_key]}",
                             cpu, f"--memory={memory}", f"--timeout={timeout}", "--cpu=1", "--max-instances=1",
                             "--min=0", "--min-instances=0", "--no-cpu-boost"):
                    self.assertIn(flag, args)
                self.assertFalse(any(arg.startswith("--max=") for arg in args))
                self.assertNotIn("--allow-unauthenticated", args)
                self.assertNotIn("--no-invoker-iam-check", args)
                public_env = deployed["public_env"]
                if target == "relay":
                    expected = {key: DEMO_PUBLIC_CONFIG[key] for key in (
                        "GITLAB_URL", "GITLAB_PROJECT_ID", "FLOW_CONSUMER_ID", "FLOW_SERVICE_ACCOUNT",
                        "DAWN_FLOW_CONSUMER_ID", "WATCH_ISSUE_IID", "SHOP_METRICS_URL", "GCP_PROJECT_ID",
                        "GCP_REGION", "STATE_BUCKET", "STATE_OBJECT")}
                    references = "GITLAB_TOKEN=gitlab-token:latest,RELAY_KEY=relay-key:latest,NTFY_URL=ntfy-url:latest,DEMO_KEY=demo-key:latest"
                else:
                    expected = {"APP_ENV": app_env, "UNLEASH_URL": DEMO_PUBLIC_CONFIG["UNLEASH_URL"]}
                    references = "UNLEASH_INSTANCE_ID=unleash-instance-id:latest,DEMO_KEY=demo-key:latest"
                expected["CI_COMMIT_SHORT_SHA"] = SHORT_COMMIT
                self.assertEqual(public_env, expected)
                self.assertIn(f"--set-secrets={references}", args)
                traffic = self.one_call(["run", "services", "update-traffic"])["args"]
                self.assertEqual(traffic[3], target)
                self.assertIn("--to-latest", traffic)
                self.assertEqual(json.loads((self.deploy / "result.json").read_text()), {
                    "url": f"https://{target}-demo-123.run.app", "commit": COMMIT,
                    "image": immutable_image, "build_id": BUILD_ID, "service": target,
                })
                self.assertEqual((self.deploy / "result.env").read_text(),
                                 f"DYNAMIC_ENVIRONMENT_URL=https://{target}-demo-123.run.app\n")
                self.assertEqual(json.loads(self.health_log.read_text()), {
                    "url": f"https://{target}-demo-123.run.app/healthz", "timeout": 20,
                })
                federation = self.one_call(["iam", "workload-identity-pools", "create-cred-config"])["args"]
                self.assertIn("projects/123456789/locations/global/workloadIdentityPools/lac-99-pool/providers/gitlab", federation)
                self.assertIn(f"--service-account={DEMO_PUBLIC_CONFIG['GCP_SERVICE_ACCOUNT']}", federation)
                token_path = Path(next(arg.removeprefix("--credential-source-file=") for arg in federation
                                       if arg.startswith("--credential-source-file=")))
                self.assertFalse(token_path.is_relative_to(self.root))
                self.assertFalse(token_path.exists(), "Temporary federation credentials must be removed")
                self.assertFalse(any(call["args"][0] == "secrets" for call in self.calls()))
                exposed = (result.stdout + result.stderr + (self.deploy / "result.json").read_text()
                           + (self.deploy / "result.env").read_text() + self.call_log.read_text())
                for fixture_secret in DEMO_SECRET_VALUES.values():
                    self.assertNotIn(fixture_secret, exposed)
                self.assertNotIn("access-token", exposed)

    def test_unprotected_or_nondefault_branch_stops_before_authentication(self):
        for override in ({"CI_COMMIT_BRANCH": "feature/demo"}, {"CI_COMMIT_REF_PROTECTED": "false"}):
            with self.subTest(override=override):
                result = self.run_deploy(overrides=override)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Only the protected default branch may deploy", result.stderr)
                self.assertEqual(self.calls(), [])

    def test_wrong_project_or_service_identity_stops_before_authentication(self):
        for override in ({"CI_PROJECT_ID": "100"}, {"GCP_SHOP_SERVICE": "another-shop"}):
            with self.subTest(override=override):
                result = self.run_deploy(overrides=override)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])

    def test_unowned_cloud_service_is_not_built_or_changed(self):
        result = self.run_deploy(overrides={"DEMO_OWNER": "100"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ownership does not match", result.stderr)
        self.assertFalse(any(call["args"][:2] == ["builds", "submit"] for call in self.calls()))
        self.assertFalse(any(call["args"][:2] == ["run", "deploy"] for call in self.calls()))

    def test_health_commit_mismatch_fails_without_a_success_receipt(self):
        result = self.run_deploy("relay", {"DEMO_HEALTH_COMMIT": "cccccccc"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("health response differs from this candidate", result.stderr)
        self.assertFalse((self.deploy / "result.json").exists())
        self.assertFalse((self.deploy / "result.env").exists())

    def test_yaml_exposes_three_manual_environments_on_the_protected_default_branch(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed in this interpreter")
        config = yaml.safe_load((DEPLOY / "gitlab-ci-deploy.yml").read_text())
        base = config[".deploy_cloud_run"]
        self.assertEqual(base["stage"], "deploy")
        self.assertEqual(base["id_tokens"]["GITLAB_OIDC_TOKEN"]["aud"], "https://gitlab.com")
        self.assertEqual(base["rules"], [
            {"if": '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH && $CI_COMMIT_REF_PROTECTED == "true"',
             "when": "manual", "allow_failure": False}, {"when": "never"},
        ])
        self.assertEqual(base["artifacts"]["when"], "on_success")
        self.assertEqual(base["resource_group"], "google-cloud-run-$GCP_DEPLOY_TARGET")
        for job, target, environment in (
            ("deploy_shop", "shop", "production"),
            ("deploy_shop_staging", "shop-staging", "staging"),
            ("deploy_relay", "relay", "relay"),
        ):
            self.assertEqual(config[job]["extends"], ".deploy_cloud_run")
            self.assertEqual(config[job]["variables"]["GCP_DEPLOY_TARGET"], target)
            self.assertEqual(config[job]["environment"]["name"], environment)
            self.assertEqual(config[job]["environment"]["url"], "$DYNAMIC_ENVIRONMENT_URL")


if __name__ == "__main__":
    unittest.main()
