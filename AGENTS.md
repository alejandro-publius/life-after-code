# AGENTS.md

Rules for every AI agent working in this repo: Claude Code, Codex, and GitLab Duo.

## What this is

An entry for Life After Code, the GitLab Transcend Hackathon: https://gitlab-transcend.devpost.com/

Path A: a new AI project on GitLab that automates the post-code lifecycle with agents, with a human in control of anything that matters. Builder: Alex Velazquez, solo. The concept is being chosen; see docs/IDEAS.md once it exists.

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

Alex copies messages between Claude Code and Codex.

- Claude Code owns: docs/ (except docs/codex/), the agent and app code, the root .gitlab-ci.yml, AGENTS.md, CLAUDE.md, README.md.
- Codex owns: deploy/ and docs/codex/.
- Edit only your own paths. If you need a change somewhere else, ask for it in your report.
- Codex works on branches named codex/<task> and does not merge to main. Claude Code reviews and merges.

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
