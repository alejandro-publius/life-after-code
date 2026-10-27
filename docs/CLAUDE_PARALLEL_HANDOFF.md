# Claude parallel handoff, 27 Oct 2026

Alex authorized both agents to improve this project and push completed work frequently. Codex is concurrently building the application and a browser explorer of real GitLab agent runs. Take the separate live-Dawn lane below now; no redesign or new project is needed.

## Repository and current state

- Clone or fetch **https://github.com/alejandro-publius/life-after-code**, starting from the newest `main`. Use a separate `claude/live-dawn` branch or worktree.
- GitLab target: **https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase**, project **88050495**. GitLab main has additional merge history; it is not safe to overwrite it with GitHub main.
- Public demo: **https://showcase-700ee4.gitlab.io**. Codex's environment blocks this host; public playback needs an independent browser check.
- Submission deadline recorded in the rules: **27 Oct 2026, 13:00 UTC**. Alex is making the video and submitting; do not spend this window making a video.
- Night Orders lets an on-call engineer sign up to three exact reversible actions before bed. Duo drafts and evaluates; deterministic code enforces the signature, target, threshold, traffic floor, expiry and one-use limit. At dawn a human decides what changes remain.
- The latest completed feature is incident memory: real ledger outcomes persist across nights, feed the next dusk briefing and appear as clickable incident histories with downloadable shift handoffs. Read `README.md` and `docs/INCIDENT_MEMORY.md`.
- Verified code checkpoint: GitHub `70aed2b`; GitLab `d0ebba81ba4a5305b0e256e949ef6d4342c96155`. Pipeline **2994340880** passed all 18 jobs, 651 application tests, 94% coverage. Pull newer work before committing.

## Your task: finish the live Dawn demonstration

1. Read `flows/dawn.yml`, `skills/night-orders/SKILL.md`, `relay/nightorders/morning.py`, `docs/FLOWS_SETUP.md` and `docs/codex/FLOW_SETUP.md`.
2. Create a clearly labelled demo watch log from the existing simulated night using the repository's actual ledger and watch-log renderer. Preserve the distinction between simulated shop data and a real GitLab Duo execution. Use a dedicated demo issue if writing that log to GitLab; do not present it as a production night.
3. Run the already enabled Dawn flow against that labelled log. Its normal output is a proposed countersign merge request and a note linking it. Leave the MR unapproved, unmerged and marked Draft. Check that only `ops/state.yml` changes and validate it using the repository's real countersign parser. Record concrete errors if GitLab or the flow fails; do not manufacture a successful result.
4. Fix any necessary Dawn-flow wiring within your paths, keeping loops bounded. If you change a released definition, update the GitLab catalog version deliberately and verify its read-back; the installer correctly refuses silent definition drift.
5. Save a short `docs/claude/DAWN_EVIDENCE.md` and `docs/claude/dawn-run.json` with `project_id`, `workflow_id`, `web_url`, `status` and any `merge_request_url`. Include the demo-data label, source commit, validation result and remaining limits. Codex will capture this run for the execution explorer.
6. If time remains, independently open the public Pages demo and exercise sign, approve, morning, incident memory and handoff download. Record the browser and result in your evidence file. Check Google Cloud deployment only if an authorized project and credentials are immediately available; the live Dawn artifact is the priority.

## Existing live GitLab configuration

| Flow | Consumer | Actual service account | Execution |
|---|---|---|---|
| Dusk | 13304391 | ai-night-orders-dusk-gitlab-ai-hackathon | Finished session **10124688**, created orders **MR !1**, a validated zero-order draft because no deployed change justified an action |
| Watch | 13303670 | ai-night-orders-watch-gitlab-ai-hackathon | Finished session **10120703** on demo incident **#3**, declined because no orders were signed |
| Dawn | 13304393 | ai-night-orders-dawn-gitlab-ai-hackathon | Installed and verified; execution not yet demonstrated |

Standing watch issue: **#2**. Keep existing orders MR !1 as evidence; do not merge or sign it. The installer is `scripts/setup_flows.py`; repeating `--apply` creates nothing when configuration is already correct. The Flows API startup helper is `scripts.day_one.flow_body`. GraphQL is **/api/graphql**, not /api/v4/graphql. Workflow artifact links can identify an MR even when its author is Alex rather than the flow account.

Use credentials already available in your environment or Alex's authorized session. Do not put tokens in files, logs, commits or Git remote URLs. Codex cannot transfer an environment credential through this document.

If GitLab credentials are unavailable, keep coding: build a bounded `scripts/claude_run_dawn.py` runner that generates the labelled demo log, starts the existing consumer, waits for completion and writes the evidence JSON. Read the token only from `GITLAB_TOKEN`, and make no changes when it is absent. Add targeted tests with mocked GitLab responses, push it to GitHub, and record the command for Codex to execute with its available access. Do not claim that implementing the runner demonstrates a live Dawn run.

## Avoid collisions and keep work current

You own `flows/`, `deploy/`, `docs/claude/`, new `scripts/claude_*` utilities and their tests. Codex owns `relay/`, `shop/`, the browser, shared docs and its scripts. Do not edit the shared README, Devpost draft, root pipeline or application while Codex is working; put requested edits in your evidence report.

After each meaningful chunk: commit, fetch GitHub main, merge its new commits into your task branch, then push normally to GitHub main. If main advances during the push, fetch and merge again. Never force-push. Codex is the single GitLab-main writer and will bring your GitHub commits across frequently. Send Alex the commit SHA and workflow/MR URLs as soon as they exist, without waiting for a long final report.

Local setup: `uv sync --locked`. Use targeted tests for changed behavior, `uv run --locked python -m flows.validate flows`, and Ruff. GitLab CI performs the full checks after the push. The managed Python 3.12 CI job uses `COVERAGE_CORE=sysmon` so coverage does not exhaust the existing ten-second replay bound.

No deployment or real overnight production remediation has been demonstrated. Keep that limit explicit. The current browser night is simulated; the Duo sessions and their GitLab artifacts are real.
