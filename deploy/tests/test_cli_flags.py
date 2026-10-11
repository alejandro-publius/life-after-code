"""Check deployment flags against the installed gcloud command help.

Run inside the pinned CI image to test its actual parser without credentials.
"""

import ast
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
auth print-access-token
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
secrets describe
secrets create
secrets versions list
secrets versions add
secrets add-iam-policy-binding
secrets delete
scheduler jobs pause
scheduler jobs resume
scheduler jobs run
""".strip().splitlines()


SHELL_FILES = (
    "ci_deploy.sh", "setup_gcp.sh", "teardown_gcp.sh", "lib.sh",
    "bootstrap_secrets.sh", "bootstrap_ops.sh",
)
PYTHON_FILES = ("monitoring.py",)
# Only these flag-carrying expansions may supply flags to a shell invocation.
# Literal assignments are read from source, not copied into this allowlist.
FLAG_VARIABLE_COMMANDS = {
    "cpu_flag": "run deploy",
    "settings": "run deploy",
}
# Alex can use these documented commands without changing the saved request body.
MANUAL_COMMAND_FLAGS = {
    "scheduler jobs pause": {"--project", "--location", "--quiet"},
    "scheduler jobs resume": {"--project", "--location", "--quiet"},
    "scheduler jobs run": {"--project", "--location", "--quiet", "--format"},
}
FLAG = re.compile(r"--[a-z][a-z0-9-]*")


def catalog_command(invocation, filename):
    for command in sorted(COMMANDS, key=len, reverse=True):
        if invocation == command or invocation.startswith(command + " "):
            return command
    raise AssertionError(f"Uncatalogued gcloud command in {filename}: {invocation}")


def shell_flags(source, filename):
    """Include literal flags supplied by constrained shell variables or arrays."""
    source = source.replace("\\\n", " ")
    variable_flags = {}
    # Arrays can span lines. They contain literal flags and values, no shell eval.
    for match in re.finditer(r"(?m)^\s*(?:local\s+)?([A-Za-z_]\w*)=\((.*?)\)",
                             source, re.DOTALL):
        variable_flags.setdefault(match[1], set()).update(FLAG.findall(match[2]))
    for match in re.finditer(
        r"(?m)(?:^|;)\s*(?:local\s+)?([A-Za-z_]\w*)=([^;\n]+)", source
    ):
        if re.match(r"[\"\']?--[a-z]", match[2]):
            variable_flags.setdefault(match[1], set()).update(FLAG.findall(match[2]))
    flags_by_command = {}
    for line in source.splitlines():
        if line.lstrip().startswith("#") or "command -v gcloud" in line:
            continue
        match = re.search(r"\bgcloud\s+([a-z].*)", line)
        if not match:
            continue
        invocation = match[1]
        command = catalog_command(invocation, filename)
        flags = set(FLAG.findall(invocation))
        references = set(re.findall(r"\$\{?([A-Za-z_]\w*)", invocation))
        for name in references:
            supplied = variable_flags.get(name, set())
            if not supplied:
                continue
            if FLAG_VARIABLE_COMMANDS.get(name) != command:
                raise AssertionError(
                    f"Uncatalogued flag variable {name} for gcloud {command} in {filename}"
                )
            flags.update(supplied)
        flags_by_command.setdefault(command, set()).update(flags)
    return flags_by_command


def python_flags(source, filename):
    """Read executable subprocess argument lists, including joined flag values."""
    flags_by_command = {}
    for node in ast.walk(ast.parse(source, filename=filename)):
        if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
            continue
        first = node.elts[0]
        if not isinstance(first, ast.Constant) or first.value != "gcloud":
            continue
        words, flags, path_open = [], set(), True
        for argument in node.elts[1:]:
            # Only literal arguments before the first dynamic value form the path.
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                if path_open and not argument.value.startswith("--"):
                    words.append(argument.value)
                else:
                    path_open = False
            else:
                path_open = False
            for part in ast.walk(argument):
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    flags.update(FLAG.findall(part.value))
        invocation = " ".join(words)
        # Positional literal arguments may follow the command path.
        command = catalog_command(invocation, filename)
        flags_by_command.setdefault(command, set()).update(flags)
    return flags_by_command


def command_flags():
    flags_by_command = {c: set(flags) for c, flags in MANUAL_COMMAND_FLAGS.items()}
    for filenames, scanner in ((SHELL_FILES, shell_flags), (PYTHON_FILES, python_flags)):
        for filename in filenames:
            scanned = scanner((DEPLOY / filename).read_text(), filename)
            for command, flags in scanned.items():
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
    def test_dynamic_flags_and_python_calls_are_discovered(self):
        source = """app_dir=shop; cpu_flag=--no-cpu-throttling; memory=512Mi
settings=(--memory=512Mi --timeout=60)
gcloud run deploy shop "$cpu_flag" "${settings[@]}" --max-instances=1
"""
        flags = shell_flags(source, "fixture.sh")["run deploy"]
        self.assertEqual(flags, {"--no-cpu-throttling", "--memory", "--timeout", "--max-instances"})
        flags = python_flags(
            '["gcloud", "storage", "cp", path, "--project=" + project, "--quiet"]',
            "fixture.py",
        )
        self.assertEqual(flags["storage cp"], {"--project", "--quiet"})

    def test_unknown_commands_and_flag_variables_fail(self):
        for source in ("gcloud nonexistent edit --quiet",
                       'other_flags=(--made-up)\ngcloud run deploy shop "${other_flags[@]}"'):
            with self.subTest(source=source), self.assertRaises(AssertionError):
                shell_flags(source, "fixture.sh")
        with self.assertRaises(AssertionError):
            python_flags('["gcloud", "nonexistent", "edit", "--quiet"]', "fixture.py")

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
