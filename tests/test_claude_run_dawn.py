"""The Dawn demonstration: a labelled demo log, a real flow run, a verified draft countersign. Offline here, against
a fake GitLab; every id, name, time and token is test data."""

from __future__ import annotations

from datetime import datetime, timezone
import io
import json
from urllib.parse import unquote

import pytest

from conftest import REPO
from scripts import claude_run_dawn as demo
from test_day_one import API, PROJECT, TOKEN, Clock, Server, body

NOW = datetime(2026, 10, 27, 12, 59, 0, tzinfo=timezone.utc)
SESSION = "https://gitlab.example/g/sub/p/-/automate/agent-sessions/555"
ISSUE_URL = "https://gitlab.example/g/sub/p/-/issues/7"
MR_URL = "https://gitlab.example/g/sub/p/-/merge_requests/9"
STATE = ('night: "2026-10-20"\nflags:\n  - {flag: new_checkout, environment: production, keep: "off", '
         'until: "the rounding fix ships", until_deployed: 39}\nservices: []\n')
TARGETS = (REPO / "ops" / "targets.yml").read_text(encoding="utf-8")


class FakeGitLab:
    """Issues, notes, one dawn session and its merge request, with the state the script changes."""

    def __init__(self, *, state=STATE, files=("ops/state.yml",), draft=False, final="FINISHED", errors=(),
                 polls_until_done=2, link=True, issue_title=demo.ISSUE_TITLE):
        self.issues: list[dict] = []
        self.notes: list[dict] = []
        self.started: list[dict] = []
        self.graphql_calls = 0
        self.issue_title = issue_title
        self.mr = {"iid": 9, "title": "Countersign 2026-10-20", "web_url": MR_URL, "state": "opened", "draft": draft,
                   "merged_at": None, "source_branch": "countersign/2026-10-20", "target_branch": "main",
                   "sha": "abc123", "author": {"username": "alex-velazquez"}}
        self.state, self.files, self.final = state, list(files), final
        self.errors, self.polls, self.link = list(errors), polls_until_done, link
        self.server = Server({
            ("GET", API): PROJECT,
            ("GET", f"{API}/issues"): lambda request: list(self.issues),
            ("POST", f"{API}/issues"): self.create_issue,
            ("GET", f"{API}/issues/7"): lambda request: {"iid": 7, "title": self.issue_title, "web_url": ISSUE_URL},
            ("GET", f"{API}/issues/7/notes"): lambda request: list(self.notes),
            ("POST", f"{API}/issues/7/notes"): self.post_note,
            ("POST", "/api/v4/ai/duo_workflows/workflows"): self.start,
            ("POST", "/api/graphql"): self.graphql,
            ("GET", f"{API}/merge_requests"): [],
            ("GET", f"{API}/merge_requests/9"): lambda request: dict(self.mr),
            ("GET", f"{API}/merge_requests/9/changes"): lambda request: {
                **self.mr, "changes": [{"new_path": path, "old_path": path} for path in self.files]},
            ("GET", f"{API}/merge_requests/9/approvals"): {"approved_by": []},
            ("PUT", f"{API}/merge_requests/9"): self.update_mr,
        }, fallback=self.files_route)

    def create_issue(self, request):
        sent = body(request)
        issue = {"iid": 7, "title": sent["title"], "description": sent["description"], "web_url": ISSUE_URL}
        self.issues.append(issue)
        return 201, issue

    def post_note(self, request):
        note = {"id": 100 + len(self.notes), "body": body(request)["body"], "system": False,
                "author": {"username": "alex-velazquez"}}
        self.notes.append(note)
        return 201, note

    def start(self, request):
        self.started.append(body(request))
        return 201, {"id": 555, "status": "created", "web_url": SESSION}

    def graphql(self, request):
        self.graphql_calls += 1
        sent = body(request)
        assert "duoWorkflowWorkflows" in sent["query"]
        assert sent["variables"]["projectId"] == "gid://gitlab/Project/123"
        running = self.graphql_calls < self.polls
        done = not running
        node = {"id": "gid://gitlab/Ai::DuoWorkflows::Workflow/555", "status": "RUNNING" if running else self.final,
                "createdAt": "2026-10-27T13:00:00Z", "updatedAt": "2026-10-27T13:02:00Z", "webUrl": SESSION,
                "aiCatalogItem": {"name": "night-orders-dawn"},
                "latestCheckpoint": {"executionStatus": "Running" if running else "Completed",
                                     "errors": self.errors if done else []},
                "mergeRequestLinks": {"nodes": [{"mergeRequest": {"iid": 9, "title": self.mr["title"],
                                                                  "webUrl": MR_URL}}] if done and self.link else []},
                "noteLinks": {"nodes": [{"note": {"id": 77, "url": f"{ISSUE_URL}#note_77"}}] if done else []}}
        return {"data": {"duoWorkflowWorkflows": {"nodes": [node]}}}

    def update_mr(self, request):
        sent = body(request)
        self.mr["title"] = sent["title"]
        self.mr["draft"] = sent["title"].startswith("Draft:")
        return dict(self.mr)

    def files_route(self, request):
        path = unquote(request.url.path)
        if "/repository/files/" in path and path.endswith("/raw"):
            name = path.split("/repository/files/", 1)[1].removesuffix("/raw")
            if name == "ops/state.yml":
                return self.state
            if name == "ops/targets.yml":
                return TARGETS
        return None


def run(fake: FakeGitLab, tmp_path, *args, token=TOKEN):
    out = io.StringIO()
    clock = Clock()
    target = tmp_path / "dawn-run.json"
    argv = ["--project", "123", "--base-url", "https://gitlab.example", "--out", str(target),
            "--source-commit", "abc1234abcd", *args]
    code = demo.main(argv, env={"GITLAB_TOKEN": token} if token else {}, client=fake.server.client(), out=out,
                     now=lambda: NOW, clock=clock, sleep=clock.sleep)
    report = json.loads(target.read_text(encoding="utf-8")) if target.exists() else None
    return code, out.getvalue(), report, clock


# Rendering, offline.

def test_render_labels_the_log_as_demo_data_and_lists_the_nights_loose_ends():
    text = demo.render_document()
    assert text.startswith("# Demo watch log for the Dawn demonstration (demo data)")
    assert "DEMO DATA." in text and demo.LOG_HEADER in text
    assert "- stock_from_cache on in production (approved by thumbs-up, 01:53)" in text
    assert "- new_checkout off in production (order 1, 03:13)" in text
    assert "Watch issue #<the demo issue>, night of Tue 20 Oct." in text
    assert 'Night date: 2026-10-20. Write night: "2026-10-20" at the top of ops/state.yml.' in text
    assert "Before the night: off." in text and "Before the night: on." in text
    assert demo.GOAL_LABEL in text
    assert "@" not in text and not [line for line in text.splitlines() if line.startswith("/")]


def test_the_committed_render_is_what_the_script_renders():
    kept = (REPO / "docs" / "claude" / "dawn-demo-watch-log.md").read_text(encoding="utf-8")
    assert kept == demo.render_document()


def test_posted_text_cannot_mention_anyone_or_run_a_quick_action():
    text = demo.note_text("## Watch log\n/merge\n  /close now\n@someone\n")
    assert text.splitlines()[-3:] == ["'/merge", "'/close now", "(at)someone"]
    assert text.startswith("DEMO DATA.")


# The live run, against the fake GitLab.

def test_apply_posts_the_labelled_log_starts_dawn_waits_and_verifies_the_draft_countersign(tmp_path):
    fake = FakeGitLab()
    code, text, report, clock = run(fake, tmp_path, "--apply", "--consumer-id", "13304393")
    assert code == 0, text
    [issue] = fake.issues
    assert issue["title"] == demo.ISSUE_TITLE and issue["description"].startswith("DEMO DATA.")
    [note] = fake.notes
    assert note["body"].startswith("DEMO DATA.") and demo.LOG_HEADER in note["body"]
    assert "Rendered at source commit abc1234abcd." in note["body"]
    [sent] = fake.started
    assert sent["project_id"] == "123" and sent["ai_catalog_item_consumer_id"] == 13304393 and sent["issue_id"] == 7
    assert sent["goal"].startswith("Watch issue #7, night of Tue 20 Oct. Code posted the watch log there.")
    assert sent["goal"].endswith(demo.GOAL_LABEL) and sent["start_workflow"] is True
    assert clock.slept == [15.0]  # one poll found it running, the next found it finished
    assert report["project_id"] == 123 and report["workflow_id"] == 555 and report["web_url"] == SESSION
    assert report["status"] == "finished" and report["execution_status"] == "Completed" and report["errors"] == []
    assert report["demo_issue"] == {"iid": 7, "web_url": ISSUE_URL, "title": demo.ISSUE_TITLE, "created": True}
    assert report["watch_log_note"] == {"id": 100, "url": f"{ISSUE_URL}#note_100", "posted": True}
    assert report["merge_request_url"] == MR_URL
    assert report["merge_request"]["changed_files"] == ["ops/state.yml"]
    assert report["merge_request"]["draft"] is True and report["merge_request"]["title"] == "Draft: Countersign 2026-10-20"
    assert report["merge_request"]["state"] == "opened" and report["merge_request"]["approved_by"] == []
    assert report["state_file"]["validation"] == "passed" and report["state_file"]["night"] == "2026-10-20"
    assert report["state_file"]["kept"] == [
        "new_checkout off in production, until the rounding fix ships (until_deployed !39)"]
    assert report["state_file"]["restored"] == [
        "stock_from_cache on in production: not kept at the countersign; the night set stock_from_cache on in "
        "production (approved by thumbs-up, 01:53)"]
    assert report["state_file"]["by_hand"] == []
    assert report["review_adjustment"].startswith("The flow opened the merge request without the draft flag.")
    assert report["flow_notes"] == [f"{ISSUE_URL}#note_77"]
    assert report["result"] == "verified" and report["observation"].startswith("Dawn read the labelled demo watch log")
    assert report["demo_data_label"] == demo.DEMO_LABEL and report["source_commit"] == "abc1234abcd"
    assert "No human countersign" in " ".join(report["limitations"])
    # Nothing was approved or merged, and the token is not in the evidence.
    assert fake.server.sent("PUT", f"{API}/merge_requests/9/merge") == []
    assert fake.server.sent("POST", f"{API}/merge_requests/9/approve") == []
    assert [body(request)["title"] for request in fake.server.sent("PUT", f"{API}/merge_requests/9")] == [
        "Draft: Countersign 2026-10-20"]
    assert TOKEN not in (tmp_path / "dawn-run.json").read_text(encoding="utf-8") and TOKEN not in text


def test_a_rerun_reuses_the_demo_issue_and_the_log_already_posted(tmp_path):
    fake = FakeGitLab(draft=True)
    first = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    fake.graphql_calls = 0
    second = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    assert first[0] == 0 and second[0] == 0, second[1]
    assert len(fake.server.sent("POST", f"{API}/issues")) == 1
    assert len(fake.server.sent("POST", f"{API}/issues/7/notes")) == 1
    assert second[2]["demo_issue"]["created"] is False and second[2]["watch_log_note"]["posted"] is False
    assert len(fake.started) == 2  # a rerun is a new session on the same log
    assert second[2]["review_adjustment"] == ""  # already a draft: the title was left alone
    assert fake.server.sent("PUT", f"{API}/merge_requests/9") == []


def test_a_failed_session_is_recorded_with_gitlabs_errors_not_manufactured(tmp_path):
    fake = FakeGitLab(final="FAILED", errors=["create_branch: 403 Forbidden"], link=False)
    code, text, report, _ = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    assert code == 1
    assert report["status"] == "failed" and report["result"] == "failed"
    assert report["errors"] == ["create_branch: 403 Forbidden"]
    assert report["merge_request"] is None and report["merge_request_url"] == ""
    assert report["validation"] == "not checked"
    assert report["observation"].startswith("The run ended as failed")
    assert fake.server.sent("PUT", f"{API}/merge_requests/9") == []


def test_a_session_still_running_at_the_limit_is_left_as_it_is(tmp_path):
    fake = FakeGitLab(polls_until_done=10 ** 6)
    code, _, report, clock = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    assert code == 1
    assert report["status"] == "running" and report["result"] == "timed_out"
    assert sum(clock.slept) == demo.POLL_LIMIT
    assert fake.graphql_calls <= demo.POLL_LIMIT / demo.POLL_EVERY + 2
    assert any("still running after 15 minutes" in problem for problem in report["problems"])


def test_a_finished_session_without_a_merge_request_is_a_recorded_problem(tmp_path):
    fake = FakeGitLab(link=False)
    code, _, report, _ = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    assert code == 1
    assert report["result"] == "finished_without_merge_request"
    assert "no countersign merge request was found" in report["problems"][0]


@pytest.mark.parametrize("problem", ["keeps_the_wrong_value", "names_another_night", "changes_another_file",
                                     "unknown_key"])
def test_a_countersign_the_repository_parser_refuses_fails_validation(problem, tmp_path):
    if problem == "keeps_the_wrong_value":
        fake = FakeGitLab(state=STATE.replace('keep: "off"', 'keep: "on"'))
    elif problem == "names_another_night":
        fake = FakeGitLab(state=STATE.replace("2026-10-20", "2026-10-21"))
    elif problem == "changes_another_file":
        fake = FakeGitLab(files=("ops/state.yml", "README.md"))
    else:
        fake = FakeGitLab(state=STATE + "extra: 1\n")
    code, _, report, _ = run(fake, tmp_path, "--apply", "--consumer-id", "1")
    assert code == 1
    assert report["result"] == "finished_with_problems"
    assert report["validation"].startswith("failed: ")
    expected = {"keeps_the_wrong_value": "but last night set it off", "names_another_night": "names night 2026-10-21",
                "changes_another_file": "not only ops/state.yml", "unknown_key": "unknown keys extra"}[problem]
    assert expected in report["validation"]
    # Still a draft, still unmerged: validation never touches the merge request's content.
    assert fake.server.sent("PUT", f"{API}/merge_requests/9/merge") == []


def test_verify_mode_reads_an_existing_session_without_posting_or_starting_anything(tmp_path):
    fake = FakeGitLab(draft=True, polls_until_done=1)
    code, text, report, _ = run(fake, tmp_path, "--workflow", "555")
    assert code == 0, text
    assert fake.issues == [] and fake.notes == [] and fake.started == []
    assert report["workflow_id"] == 555 and report["result"] == "verified" and report["goal"] is None


def test_mention_start_posts_the_goal_as_a_note_and_finds_the_session_it_started(tmp_path):
    fake = FakeGitLab(draft=True)
    code, text, report, _ = run(fake, tmp_path, "--apply", "--start", "mention", "--account", "ai-dawn-account")
    assert code == 0, text
    assert fake.started == []
    assert fake.notes[1]["body"].startswith("@ai-dawn-account Watch issue #7, night of Tue 20 Oct.")
    assert fake.notes[1]["body"].count("@") == 1
    assert report["workflow_id"] == 555 and report["result"] == "verified"
    first = body(fake.server.sent("POST", "/api/graphql")[0])["variables"]
    assert first["ids"] is None and first["first"] == 10


def test_an_issue_that_is_not_the_demo_issue_gets_no_demo_log(tmp_path):
    fake = FakeGitLab(issue_title="Tonight's watch")
    code, _, report, _ = run(fake, tmp_path, "--apply", "--consumer-id", "1", "--issue", "7")
    assert code == 1
    assert fake.notes == [] and fake.started == []
    assert report["result"] == "blocked" and "refusing to post a demo log on another issue" in report["problems"][0]


def test_without_a_token_or_a_mode_nothing_is_called(tmp_path):
    fake = FakeGitLab()
    assert run(fake, tmp_path, "--apply", "--consumer-id", "1", token="")[0] == 2
    assert run(fake, tmp_path)[0] == 2
    assert run(fake, tmp_path, "--apply")[0] == 2
    assert run(fake, tmp_path, "--apply", "--start", "mention")[0] == 2
    assert fake.server.requests == []
