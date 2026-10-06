# AGENTS.md

Rules for every AI agent working in this repo: Claude Code, Codex, and GitLab Duo.

## What this is

An entry for Life After Code, the GitLab Transcend Hackathon: https://gitlab-transcend.devpost.com/

Path A: a new AI project on GitLab that automates the post-code lifecycle with agents, with a human in control of anything that matters. Builder: Alex Velazquez, solo.

Concept selection was reopened on 6 Oct 2026. The existing code implements Night Orders (before bed, the on-call engineer signs what the agent may do alone tonight, and everything else wakes them). The current concept and its review state are in docs/STATUS.md and docs/IDEAS.md section 0. Do not delete working code until a replacement is selected and the change has been reviewed.

## Project rules

1. Plain words. No hype. Never use em dashes or en dashes anywhere: code, comments, docs, commit messages, UI text. Use commas, colons, parentheses or periods.
2. Real data, or demo data that is clearly labelled as demo data in the UI, in the README and in the file name.
3. The human moment comes first. Every feature should make a person's day better: an on-call engineer who gets to sleep, a developer who feels trusted, a user who feels heard. Verify only as much as the product needs.
4. The model chooses where to look. Code decides what is true. A human decides when the agent acts on anything that matters.
5. Time-boxed loops. Every agent loop has a hard limit on steps and time. At most two review rounds on any change, then ship it or drop it.
6. Never commit a secret. Keys live in GitLab CI/CD variables (masked, protected) or a local .env file (gitignored). Google Cloud uses keyless auth (Workload Identity Federation).
7. Cite facts in docs with links. Mark anything unverified as (unverified).
8. Small commits with clear messages.

## Who does what

Alex copies messages between Claude Code and Codex. Neither agent sees the other's terminal, local files or unpushed changes.

- Claude Code is the primary implementer: application code, tests, CI, deployment and docs, in agreed batches.
- Codex is the reviewer. It reviews the pushed source on GitHub across the whole repository (product behaviour, architecture, security, deployment, tests, CI and public claims) and returns findings and a next prompt. It does not normally edit the files under review.
- One owner per file within a batch. If a batch gives Codex a path to edit, the batch says so.
- docs/codex/ holds Codex's earlier evidence records. Leave them as written; record newer findings in docs/DECISIONS.md or docs/STATUS.md.

## Branches and review

- Work on a feature branch (claude/<task> or codex/<task>) with a draft pull request into main. Never push directly to main. Never force-push.
- Make sure the GitHub checks actually run for the pushed commit (they run on pull requests and on main).
- Codex reviews every commit since the last reviewed SHA and answers READY, CHANGES REQUIRED or NOT VERIFIED for one exact SHA. Approval of an older SHA does not cover newer commits.
- Merge only a SHA marked READY. After merging, check the resulting main commit and its CI.
- At most two review rounds per batch. If a material issue remains, simplify, cut scope or revert it.

## Report format

After each batch, Claude Code returns this packet for Alex to paste to Codex. Use full SHAs, and "not run", "pending", "unavailable" or "not applicable" where accurate.

```
FOR CODEX REVIEW

Phase:
Repository:
Branch / PR:
Previous reviewed SHA:
Comparison base SHA:
New pushed SHA:
Commits in this batch:
Goal and judging criterion:
What changed or what the research concluded:
Local start command and URL:
Tests run and results:
CI link, checked SHA and status:
Live evidence:
Simulated or unverified:
Known issues or blockers:
Decision needed from Codex:
Suggested next step:
```

Codex answers with a verdict for the exact SHA, findings with file and line, and the next prompt.

## Stack defaults

Python 3.11 or newer, FastAPI, uv, pytest. GitLab CI/CD runs everything. Google Cloud Run hosts the live service.
