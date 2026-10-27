# Dawn demonstration: evidence from the Claude lane

Written by Claude Code on Tue 27 Oct 2026, 13:13 UTC, on branch `claude/live-dawn`, merged into GitHub main. The task is [docs/CLAUDE_PARALLEL_HANDOFF.md](../CLAUDE_PARALLEL_HANDOFF.md). Machine-readable record: [dawn-run.json](dawn-run.json).

## Status in one line

**Not demonstrated, after two attempts.** The first found no GitLab credential in Claude Code's environment. For the second, Alex sent a personal access token at 13:17 UTC; the runner's first write, creating the demo issue, was refused with HTTP 403, and GitLab's GraphQL `project.userPermissions` says why: every write ability (`createIssue`, `createMergeRequestIn`, `pushCode`) is false for that token while reads work. No watch log was posted, no Dawn session was started and no countersign merge request exists. The bounded runner, its tests and the labelled demo log are ready: one command with a token GitLab lets write runs the demonstration and writes [dawn-run.json](dawn-run.json). Implementing the runner is not a live Dawn run, and this file does not claim one.

## What the handoff asked, and where each item stands

| Item | State |
|---|---|
| 1. Read `flows/dawn.yml`, the skill, `morning.py`, both flow setup docs | Done. |
| 2. A clearly labelled demo watch log from the simulated night, through the real ledger and renderer | Rendered: [dawn-demo-watch-log.md](dawn-demo-watch-log.md). Not posted to GitLab (no credential). |
| 3. Run the enabled Dawn flow against that log; leave the merge request a draft, unapproved, unmerged; check only `ops/state.yml` changes; validate with the real countersign parser | Blocked twice: no credential, then a token GitLab treats as read-only (403 on the first write). The runner does every step and recorded the refusal in GitLab's own words. |
| 4. Fix Dawn wiring if needed, update the catalog version deliberately | No change was needed from reading the flow and the morning code. `flows/dawn.yml` is unchanged: its SHA-256 `f1c0b656eff70528dfde9ed8939a3f0e6f8ea532c1239e83b538d3eae2fb2a8c` matches Codex's GitLab read-back in [flow-setup-evidence.json](../codex/flow-setup-evidence.json). No catalog version was touched. Whether the released flow proposes a valid file is exactly what the run will show. |
| 5. `docs/claude/DAWN_EVIDENCE.md` and `docs/claude/dawn-run.json` | This file, and [dawn-run.json](dawn-run.json) as the runner wrote it (`"result": "blocked"`, the 403, GitLab's permission verdict, the command, what is needed). |
| 6. Open the public Pages demo independently | Attempted in a real headless Chromium. Blocked before the demo loaded: the host now redirects anonymous visitors to GitLab sign-in. Details below; this needs Alex. |

## Why the run is blocked

Attempt 1, 12:50 UTC: `GITLAB_TOKEN` was not set in Claude Code's shell, the repository has no gitignored `.env`, and the Claude in Chrome extension was not connected, so Alex's signed-in browser session could not be used either. Nothing was tried against GitLab with a guessed or borrowed credential.

Attempt 2, 13:18 UTC, with the token Alex sent (name `CLAUDE`, created 13:17 UTC, legacy type, `granular: false`, scopes including `api` and `ai_features`, user `alejandro-publius`, project member through the group's custom role "Developer+" with base access 30):

- Reads work: the project, its members, the notes on watch issue #2 (4 notes), the token's own record.
- `POST /projects/88050495/issues` with the demo issue answered `403 {"message":"403 Forbidden"}`, twice (the runner, then a direct check with the same body).
- GraphQL `project(fullPath: ...) { userPermissions }` for that token: `readProject true`, `createIssue false`, `createMergeRequestIn false`, `pushCode false`, `adminProject false`.

So the token is read-only in this project, whatever its scopes say. The same user created issues #2 and #3 and the dusk run's merge request today with the access Codex uses, so the project does accept writes from this account; the difference is the token. (unverified) The likeliest cause is a token policy on the hackathon's top-level group that limits legacy personal access tokens to read access, which is why a granular token is asked for below. The runner wrote [dawn-run.json](dawn-run.json) with the 403 in GitLab's words and stopped; it changed nothing.

What is needed: a token GitLab lets write in project 88050495 (issues, notes, merge requests, the Flows API). Either a **granular** personal access token (GitLab: Preferences > Access tokens > Add new token, granular, with issues, notes, merge requests and AI features for this project or group), or the access Codex used today. After that, revoke the `CLAUDE` token: it was pasted into a chat and should not stay valid.

## The command for Codex (or Alex) to run

From the repository root, with the token in the process environment and nowhere else:

```sh
GITLAB_TOKEN=... uv run --locked python scripts/claude_run_dawn.py --project 88050495 --consumer-id 13304393 --apply --out docs/claude/dawn-run.json
```

What it does, in order, and the bound on each step:

1. Replays `demo/night-2026-10-20` through `relay/nightorders/demo_night.py`, the same Watch the relay runs, and renders the watch log with `render_watch_log` and the goal with `dawn_goal` (both in `relay/nightorders/dawn.py`). The facts come from the ledger the real decision code wrote; the model never wrote them.
2. Finds the dedicated demo issue by its exact title, `[demo] Dawn demo: watch log of the simulated night of 2026-10-20`, or creates it once with the demo label in its description. It refuses to post on any other issue, including the standing watch issue #2.
3. Posts the watch log as one note, with the demo label first. A rerun finds the note already there and does not post it again. The note has no `@` and no line starting with `/`, the same defusing the relay applies.
4. Starts the Dawn flow through the Flows API (`POST /api/v4/ai/duo_workflows/workflows`, the body from `scripts.day_one.flow_body`) on consumer `13304393` with the goal. `--start mention --account ai-night-orders-dawn-gitlab-ai-hackathon` starts it instead by a note that mentions the flow's account, for a person's token when the Flows API refuses; GitLab's triggers page says a bot or service account cannot set off a trigger ([FLOWS_SETUP.md](../FLOWS_SETUP.md)).
5. Polls the session through GraphQL (`/api/graphql`, `duoWorkflowWorkflows`) every 15 seconds for at most 15 minutes, and gives up after five consecutive failed reads. A session still running at the limit is recorded as `timed_out` and left as it is.
6. Finds the countersign merge request from the session's own merge request links (the `Countersign` title first), or from an open `countersign/2026-10-20...` branch created after the start, since the author may be the person whose token started the flow rather than the flow account.
7. Reads the merge request back: the changed files must be exactly `ops/state.yml`; the file at the merge request head is parsed with `parse_state` against `ops/targets.yml` at that head, its `night` must be `2026-10-20`, and `plan_morning` must accept it for the demo night's two loose ends. Approvals and the merge state are read, never written.
8. If the flow opened the merge request without the draft flag, it puts `Draft:` in front of the title, as Codex did for the dusk run, and says so in `review_adjustment`. `--leave-title` skips that. It never approves, merges, signs, or changes a flag or traffic.
9. Writes the evidence JSON with the token redacted: `project_id`, `workflow_id`, `web_url`, `status`, `execution_status`, `errors`, `merge_request_url`, the merge request read-back, the state file with its SHA-256 and the parser's verdict, the demo label, the source commit, the problems, and the limits. Exit code 0 only when the result is `verified`.

Without `GITLAB_TOKEN` the script exits with code 2 before any network call. A rerun after a refused start finds nothing to reuse and starts clean; a rerun after a posted log finds the issue and the note and starts a new session on them. `--workflow <id>` verifies an existing session without posting or starting anything. `--render` prints the note and goal offline. After a run, commit `docs/claude/dawn-run.json`; Codex can then capture the session for the execution explorer with its own `scripts/capture_runs.py --workflow <id>`.

Tests: `uv run --locked python -m pytest -q tests/test_claude_run_dawn.py` covers the labelled render, the full run against a fake GitLab, a rerun that reuses the issue and note, a failed session recorded with GitLab's errors, a session that times out, a finished session with no merge request, four countersign files the parser refuses, verify mode, the mention start, the guard against another issue, and the no-token path. None of this is a substitute for the live run.

## What the run reads, and what a good result looks like

The watch log and goal are in [dawn-demo-watch-log.md](dawn-demo-watch-log.md). The night has two loose ends: `stock_from_cache on in production` (approved by thumbs-up at 01:53, off before the night) and `new_checkout off in production` (order 1 at 03:13, on before the night). The model proposes keep or restore for each; code only checks the file it writes. A file the parser accepts keeps nothing that the night did not change, keeps a flag only at the value the night set, names the night, and uses only `night`, `flags` and `services` at the top level. The demo folder's own [countersign.yml](../../demo/night-2026-10-20/countersign.yml) shows one acceptable answer (keep the new checkout off until the rounding fix ships), but the flow is free to propose differently, and the record will say what it did.

## Simulated and real, kept apart

The shop, its traffic, both faults and the recorded agent replies are demo data, labelled in the demo folder, in the issue title (`[demo]`), in the issue description, in the first paragraph of the posted note and in the goal. The Duo session, its branch, commit, merge request and note are real GitLab artifacts. No production target changes on any path through the runner. The relay was not deployed and took no part.

## Public Pages demo: independent browser check

Browser: headless Chromium through Playwright 1.62.0 on macOS, driven by `scripts/claude_pages_check.py`, which runs the pipeline's own walk from `scripts/browser_smoke.py` (sign, approve, the morning, the permission boundary, incident memory, the shift handoff download, the execution explorer) on a phone and a laptop viewport. Record: [pages-check.json](pages-check.json).

Result: every check failed before the demo loaded, and the reason is not the demo.

- At 12:49 UTC a plain `curl` of `https://showcase-700ee4.gitlab.io/` answered HTTP 200 with 4930 bytes, the size of `relay/demo_web/index.html` at `6311445` (4931 bytes). The demo was public then.
- By 13:10 UTC (the time in the Pages cookie that came with the redirect) every path (`/`, `/activity.html`, `/app.js`, a replay JSON) answers HTTP 302 to `https://projects.gitlab.io/auth?domain=https://showcase-700ee4.gitlab.io&...`, which is GitLab Pages access control sending an anonymous visitor to sign in. The headless browser then sat on gitlab.com's sign-in page behind a Cloudflare challenge. Nothing signed in and no challenge was answered.
- Read with Alex's token at 13:19 UTC: the project's `pages_access_level` is `enabled` ("Everyone with access"). On gitlab.com, where Pages access control is on, that level makes the Pages server send every visitor to sign in first, even for a public project; only `public` ("Everyone") serves the site without a login. The anonymous API hides this field (it returns null).

What to do (Alex, as a Maintainer; a Developer token gets 403 on project settings): in the GitLab project open **Settings > General > Visibility, project features, permissions**, set **Pages** to **Everyone**, save, then check that `curl -sI https://showcase-700ee4.gitlab.io/` answers 200, not 302. The same change through the API is `PUT /api/v4/projects/88050495` with `pages_access_level=public`. Until then the "Try one night in the browser" link in the README and the Devpost form opens a sign-in page for a judge who is not a project member. Claude did not change the setting: it is a project setting, and the handoff asked only for a check.

Once the host answers 200 again, rerun the same check and commit its record:

```sh
uv run --locked --with playwright==1.62.0 python scripts/claude_pages_check.py --url https://showcase-700ee4.gitlab.io --out docs/claude/pages-check.json
```

## Requested shared-file edits, for Codex to integrate

Claude did not edit these files.

- `docs/STATUS.md`, Pages row: public playback was checked from outside the proxy. The host served the demo at 12:49 UTC and redirects anonymous visitors to GitLab sign-in since about 13:10 UTC; the Pages access setting needs fixing before the link is judged. Link this file.
- `docs/STATUS.md`, "What still needs to happen": the live Dawn run is one command away, in the section above; it needs `GITLAB_TOKEN`.
- `docs/codex/FLOW_SETUP.md`, last sentence of "Live dusk execution" ("Dawn execution and a deployed relay remain unverified"): link [dawn-run.json](dawn-run.json) once it holds a result.
- `docs/CLAUDE_PARALLEL_HANDOFF.md`: the runner is `scripts/claude_run_dawn.py`, as the updated handoff asks.

## Remaining limits

- No live Dawn run yet, so no evidence that the released flow writes a file the morning code accepts.
- The night is simulated; the countersign, when it exists, is for a demo night and must stay unmerged.
- No production flag or traffic changed, and no relay is deployed; nothing here is overnight remediation.
- The rules check records a submission freeze after 27 Oct 13:00 UTC ([RULES_CHECK.md](../codex/RULES_CHECK.md), "After the deadline"). This work landed after that time on GitHub; what is synced to GitLab is Alex's call.

## Checks run

- `uv run --locked python -m pytest -q` on the merged tree (GitHub main `f63a933` plus this branch): 688 passed, including the 25 new tests for the two scripts.
- `uv run --locked python -m flows.validate flows`: no problems.
- Ruff on `scripts/` and the new tests: clean.
