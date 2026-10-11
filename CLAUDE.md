# CLAUDE.md

@AGENTS.md

Claude Code notes:

- Work on a claude/<task> branch with a draft pull request. Do not push to main; merge only a SHA that Codex marked READY (see AGENTS.md, Branches and review).
- Commit and push the feature branch after every coherent step (a module with passing tests, a doc update, a result), not only at the end of a batch. Codex sees only pushed commits.
- Fetch before trusting a local main. Earlier workspaces had a stale local main.
- Keep messages to Alex short and plain. Alex reads on a phone and copies text between Claude Code and Codex.
- Read a codex/* branch's diff and run its tests before reusing or merging it.
