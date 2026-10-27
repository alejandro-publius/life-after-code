# AGENTS.md

Rules for every AI agent working in this repo: Claude Code, Codex, and GitLab Duo.

## What this is

An entry for Life After Code, the GitLab Transcend Hackathon: https://gitlab-transcend.devpost.com/

Path A: a new AI project on GitLab that automates the post-code lifecycle with agents, with a human in control of anything that matters. Builder: Alex Velazquez, solo. The concept is Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight, and everything else wakes them (README.md, docs/IDEAS.md, docs/PLAN.md).

## Project rules

1. Plain words. No hype. Never use em dashes or en dashes anywhere: code, comments, docs, commit messages, UI text. Use commas, colons, parentheses or periods.
2. Real data, or demo data that is clearly labelled as demo data in the UI, in the README and in the file name.
3. The human moment comes first. Every feature should make a person's day better: an on-call engineer who gets to sleep, a developer who feels trusted, a user who feels heard. Verify only as much as the product needs.
4. The model chooses where to look. Code decides what is true. A human decides when the agent acts on anything that matters.
5. Time-boxed loops. Every agent loop has a hard limit on steps and time. At most two review rounds on any change, then ship it or drop it.
6. Never commit a secret. Keys live in GitLab CI/CD variables (masked, protected) or a local .env file (gitignored). Google Cloud uses keyless auth (Workload Identity Federation).
7. Cite facts in docs with links. Mark anything unverified as (unverified).
8. Small commits with clear messages.

## Who owns what

Updated 27 Oct 2026 with Alex's explicit authorization for parallel work and frequent pushes. This replaces the earlier deploy-only Codex assignment and the earlier restriction on pushing main.

- Codex owns the application, browser, incident memory, execution explorer, shared README/submission docs, and GitLab main synchronization.
- Claude Code owns `flows/`, `deploy/`, `docs/claude/`, new `scripts/claude_*` utilities and their tests. The current task is in [docs/CLAUDE_PARALLEL_HANDOFF.md](docs/CLAUDE_PARALLEL_HANDOFF.md).
- Both may push completed work to GitHub main after fetching and incorporating its latest commits. Work on separate task branches or worktrees; do not reset another agent's work.
- Codex syncs GitHub changes to GitLab through ordinary merges that preserve GitLab's additional history. Never force-push either main branch.
- Keep changes within the assigned paths. Record a needed shared-file change in `docs/claude/` so Codex can integrate it without a concurrent edit.
- Alex handles the video and Devpost submission. Do not start another video project.

## Report format

End every session with this, kept short, so Alex can paste it to the other agent:

```
REPORT FROM <CLAUDE or CODEX>
Branch:
Done:
Tested (commands and results):
Not done or blocked:
Needs from Alex:
Questions for <the other agent>:
```

## Stack defaults

Python 3.11 or newer, FastAPI, uv, pytest. GitLab CI/CD runs everything. Google Cloud Run hosts the live service.
