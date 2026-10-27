# Execution explorer

The [public explorer](https://showcase-700ee4.gitlab.io/activity.html) shows what the Night Orders Duo flows actually did on GitLab. Select dusk, watch or dawn, choose a session, inspect the component/tool sequence, expand an answer and open its linked artifact. Capture time is visible, and a missing run is shown as missing rather than inferred from installation.

The relay serves the same page at `/activity` and the snapshot at `/activity.json`. Neither route reads a credential or starts an agent. The static Pages build bundles the same JSON and assets. The guided browser night is still a simulated shop; the explorer records actual GitLab execution with any demo inputs kept labelled.

## Refresh from GitLab

Set `GITLAB_TOKEN` in the process environment, then run:

```sh
uv run --locked python scripts/capture_runs.py --project 88050495 \
  --out relay/nightorders/agent_runs.json
```

Use repeated `--workflow <id>` arguments to select particular sessions. The capture is read-only: the POST is a GraphQL query, and artifact requests are GETs. It records at most eight application sessions, 80 visible events per session and two linked merge requests per session, with a two-minute request budget and 20-second request timeouts.

The source is GitLab's saved workflow checkpoints and artifact links, not MR-author guessing. Tool arguments and raw tool responses are omitted. Recognized token strings are redacted. Artifact URLs stay inside the selected public project. Orders-only and countersign-only MRs are checked through the actual parsers using files fetched at the MR's source SHA; an incomplete diff cannot earn a successful validation. A failed workflow remains failed in the snapshot. Private-project captures are rejected because this output is intended for a public explorer.

The first recording includes [Dusk 10124688](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10124688), its zero-order draft [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/merge_requests/1), and [Watch 10120703](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703), including the posted request that declined automatic action. The watch response passed the relay's own request parser.

Execution completion, valid YAML and a draft MR do not establish a human signature, a deployed relay or a production remediation. Countersign parsing checks structure and targets; it does not establish that a keep matches a real night's loose ends. These distinctions are preserved in the interface and capture.

Implementation: [capture command](../scripts/capture_runs.py), [recording projection](../relay/nightorders/execution.py), [browser](../relay/demo_web/activity.js), [recorded snapshot](../relay/nightorders/agent_runs.json).
