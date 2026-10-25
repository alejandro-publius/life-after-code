"""The model side of the local bench: the frozen judge prompt and who answers it.

The real answerer will be a GitLab Duo flow. Until then the bench asks a stand-in: the
Claude Code CLI run headless with no tools, or answers recorded earlier in a JSON file.
Both only return a candidate answer. proposal.parse checks it and replay decides if it works.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
from typing import Any

from nomouse.journey import evidence_text
from nomouse.proposal import SCHEMA

PROMPT = Path(__file__).parent / "prompts" / "judge.md"
SYSTEM_HEADING = "## System"
USER_HEADING = "## User"
PLACEHOLDER = re.compile(r"\{(evidence|template_path|template_source)\}")
# Never handed to the model's process: the stand-in needs none of these to answer.
SECRET_ENV = ("GITLAB_TOKEN", "GITLAB_OAUTH_TOKEN", "RELAY_KEY", "DEMO_KEY", "NTFY_URL")
MAX_RETRIES = 3
KILL_GRACE_SECONDS = 5


def render_prompt(block: dict, template_path: str, template_source: str) -> tuple[str, str]:
    """(system, user) from the frozen judge prompt, with the evidence and template filled in."""
    text = PROMPT.read_text(encoding="utf-8")
    system_at, user_at = text.find(SYSTEM_HEADING), text.find(USER_HEADING)
    if system_at < 0 or user_at < system_at:
        raise ValueError(f"{PROMPT} needs a {SYSTEM_HEADING!r} section followed by a {USER_HEADING!r} section")
    system = text[system_at + len(SYSTEM_HEADING):user_at].strip()
    template = text[user_at + len(USER_HEADING):].strip()
    values = {"evidence": evidence_text(block), "template_path": template_path,
              "template_source": template_source}
    # One pass over the template only (never str.format): page text inside the evidence may
    # contain braces, or even "{template_source}", and must reach the model unchanged.
    user = PLACEHOLDER.sub(lambda match: values[match.group(1)], template)
    return system, user.strip()


@dataclass
class ModelReply:
    answer: dict | None  # the structured answer, not yet checked by proposal.parse
    error: str = ""  # short reason when there is no answer
    meta: dict = field(default_factory=dict)


class StandInModel:
    """A clearly labelled stand-in for the Duo flow's model, for the local bench only."""

    def __init__(self, model_id: str = "claude-sonnet-4-6", timeout: float = 180, retries: int = 1,
                 command: str = "claude"):
        self.model_id = model_id
        self.timeout = timeout
        self.retries = max(0, min(int(retries), MAX_RETRIES))
        self.command = command

    @property
    def label(self) -> str:
        return f"stand-in {self.model_id} via claude -p (not GitLab Duo)"

    def argv(self, system: str, user: str) -> list[str]:
        return [self.command, "-p", "--model", self.model_id, "--tools", "", "--no-session-persistence",
                "--strict-mcp-config", "--setting-sources", "", "--system-prompt", system,
                "--output-format", "json", "--json-schema", json.dumps(SCHEMA), user]

    def ask(self, system: str, user: str, key: str) -> ModelReply:
        """One answer, or the reason there is none. Never raises for a model failure."""
        meta: dict[str, Any] = {"models": [], "total_cost_usd": 0.0, "duration_ms": 0, "attempts": 0,
                                "errors": []}
        env = {name: value for name, value in os.environ.items() if name not in SECRET_ENV}
        for _ in range(1 + self.retries):
            meta["attempts"] += 1
            try:
                answer, error, report = self._attempt(self.argv(system, user), env)
            except OSError as exc:
                # The CLI could not be started at all; trying again will not help.
                meta["errors"].append(f"could not start {self.command}: {exc.strerror or exc}")
                break
            _add_usage(meta, report)
            if answer is not None:
                return ModelReply(answer=answer, error="", meta=meta)
            meta["errors"].append(error)
        return ModelReply(answer=None, error=meta["errors"][-1], meta=meta)

    def _attempt(self, argv: list[str], env: dict[str, str]) -> tuple[dict | None, str, dict]:
        """Run the CLI once: (answer, error, the CLI's JSON report or {})."""
        # An empty working directory, so no project file (CLAUDE.md, AGENTS.md) reaches the
        # stand-in: like the Duo judge, it sees only the evidence and the template.
        with tempfile.TemporaryDirectory(prefix="nomouse-standin-") as empty:
            process = subprocess.Popen(argv, env=env, cwd=empty, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       start_new_session=True)
            try:
                stdout, _ = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                _kill(process)
                return None, f"timed out after {self.timeout:g}s", {}
            except BaseException:
                _kill(process)
                raise
        report = _parse_report(stdout)
        if process.returncode != 0:
            return None, f"exit status {process.returncode}", report or {}
        if report is None:
            return None, "stdout was not a JSON object", {}
        if report.get("is_error"):
            detail = str(report.get("subtype") or report.get("result") or "unknown")[:120]
            return None, f"the CLI reported an error: {detail}", report
        answer = report.get("structured_output")
        if not isinstance(answer, dict):
            return None, "no structured_output in the CLI result", report
        return answer, "", report


def _parse_report(stdout: str) -> dict | None:
    """The CLI's single JSON result; the last line is tried too in case of a stray log line."""
    text = (stdout or "").strip()
    for candidate in (text, text.rsplit("\n", 1)[-1]):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def _add_usage(meta: dict, report: dict) -> None:
    usage = report.get("modelUsage")
    if isinstance(usage, dict):
        meta["models"] = sorted(set(meta["models"]) | {str(name) for name in usage})
    for name, kind in (("total_cost_usd", float), ("duration_ms", int)):
        value = report.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            meta[name] = kind(meta[name] + value)


def _kill(process: subprocess.Popen) -> None:
    """Stop the CLI and anything it started (it runs in its own process group)."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        process.kill()
    try:
        process.communicate(timeout=KILL_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        pass


class RecordedModel:
    """Answers recorded earlier, so a bench run can be repeated without calling any model.

    File format: {"label": str, "answers": {key: answer object or null}}. The bench asks
    with the key "<variant id>#<run>", for example "dev-icons#1".
    """

    def __init__(self, path: Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
            raise ValueError(f"{path}: a recording needs an \"answers\" object")
        bad = [key for key, answer in data["answers"].items() if answer is not None and not isinstance(answer, dict)]
        if bad:
            raise ValueError(f"{path}: recorded answers must be objects or null: {sorted(bad)[:5]}")
        self.path = Path(path)
        self._label = str(data.get("label") or self.path.stem)
        self.answers: dict[str, dict | None] = data["answers"]

    @property
    def label(self) -> str:
        return f"recorded: {self._label}"

    def ask(self, system: str, user: str, key: str) -> ModelReply:
        answer = self.answers.get(key)
        if answer is None:
            return ModelReply(answer=None, error=f"no recorded answer for {key}", meta={})
        return ModelReply(answer=answer, error="", meta={"recorded": True, "attempts": 0})
