"""Check deployment flags against the installed gcloud command help.

Run inside the pinned CI image to test its actual parser without credentials.
"""

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path


DEPLOY = Path(__file__).resolve().parents[1]
COMMANDS = """
iam workload-identity-pools create-cred-config
auth login
config set
run services describe
builds submit
builds describe
run deploy
run services update-traffic
projects describe
projects update
alpha projects update
services list
services enable
services disable
billing projects describe
billing budgets list
billing budgets create
billing budgets update
billing budgets delete
beta services identity create
storage buckets describe
storage buckets create
storage buckets update
storage buckets add-iam-policy-binding
storage objects describe
storage cp
storage rm
iam service-accounts describe
iam service-accounts create
iam service-accounts delete
iam service-accounts add-iam-policy-binding
iam workload-identity-pools describe
iam workload-identity-pools undelete
iam workload-identity-pools create
iam workload-identity-pools delete
iam workload-identity-pools providers describe
iam workload-identity-pools providers undelete
iam workload-identity-pools providers update-oidc
iam workload-identity-pools providers create-oidc
iam workload-identity-pools providers delete
artifacts repositories describe
artifacts repositories create
artifacts repositories add-iam-policy-binding
artifacts repositories delete
run services add-iam-policy-binding
run services delete
projects get-iam-policy
projects add-iam-policy-binding
projects remove-iam-policy-binding
builds list
builds cancel
""".strip().splitlines()


def command_flags():
    """Read executable command lines, including describe_optional wrappers."""
    flags_by_command = {}
    ordered = sorted(COMMANDS, key=len, reverse=True)
    for filename in ("ci_deploy.sh", "setup_gcp.sh", "teardown_gcp.sh", "lib.sh"):
        source = (DEPLOY / filename).read_text().replace("\\\n", " ")
        for line in source.splitlines():
            if line.lstrip().startswith("#") or "command -v gcloud" in line:
                continue
            match = re.search(r"\bgcloud\s+([a-z].*)", line)
            if not match:
                continue
            invocation = match.group(1)
            command = next(
                (c for c in ordered if invocation.startswith(c + " ")),
                None,
            )
            if command is None:
                raise AssertionError(f"Uncatalogued gcloud command in {filename}: {line}")
            flags = set(re.findall(r"--[a-z][a-z0-9-]*", invocation))
            flags_by_command.setdefault(command, set()).update(flags)
    return flags_by_command


def help_flags(help_text):
    """Expand documented boolean pairs such as --[no-]cpu-boost."""
    return set(re.findall(r"--[a-z][a-z0-9-]*", help_text)) | {
        prefix + name
        for name in re.findall(r"--\[no-\]([a-z][a-z0-9-]*)", help_text)
        for prefix in ("--", "--no-")
    }


class CliFlagsTests(unittest.TestCase):
    def test_cloud_run_max_uses_revision_flag(self):
        flags = command_flags()["run deploy"]
        self.assertNotIn("--max", flags)
        self.assertIn("--max-instances", flags)

    @unittest.skipUnless(shutil.which("gcloud"), "gcloud is not installed")
    def test_every_gcloud_flag_is_in_actual_help(self):
        environment = dict(os.environ, CLOUDSDK_PAGER="cat", PAGER="cat")
        for command, used_flags in sorted(command_flags().items()):
            with self.subTest(command=command):
                result = subprocess.run(
                    ["gcloud", *command.split(), "--help"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=environment,
                    timeout=30,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(
                    used_flags - help_flags(result.stdout),
                    f"gcloud {command}: undocumented flags {used_flags - help_flags(result.stdout)}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
