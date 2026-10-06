# Anthropic: what to build on (sponsor research)

Research date: 2026-10-06. Written for Alex Velazquez, Life After Code (GitLab Transcend Hackathon, Path A).

Scope: what Anthropic launched and promoted in 2025 and 2026 that a GitLab post-code automation project could use, and the exact facts a builder needs.

How this was checked:

- Claude Code docs were read as raw markdown, starting from the index at [code.claude.com/docs/llms.txt](https://code.claude.com/docs/llms.txt).
- Claude API docs were read from [platform.claude.com/llms.txt](https://platform.claude.com/llms.txt). docs.claude.com now redirects to platform.claude.com (see "Moved or broken links").
- MCP spec facts came from the spec repository on GitHub, because modelcontextprotocol.io is blocked from this session.
- GitLab doc pages were read from their source files on gitlab.com, because docs.gitlab.com is blocked from this session.
- Package versions came from PyPI and npm on 2026-10-06.
- Anything not read on the live web is marked (unverified). Quotes keep the source wording; any em dash or en dash in a quote is replaced with " - ".

## Summary

1. Claude Code has an official GitLab CI/CD page. It is in beta and "maintained by GitLab". It is one job in `.gitlab-ci.yml` that runs `claude -p` headless with a masked `ANTHROPIC_API_KEY` ([doc](https://code.claude.com/docs/en/gitlab-ci-cd)).
2. Plain GitLab CI does not react to `@claude` comments by itself. Either use GitLab Duo Agent Platform's "Claude Code Agent by GitLab" (Premium or Ultimate, feature-flagged for verified customers), or run your own webhook listener that calls the pipeline trigger API with `AI_FLOW_*` variables ([Claude doc](https://code.claude.com/docs/en/gitlab-ci-cd), [GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md)).
3. Current models: `claude-opus-5-5` ($4 / $20 per million tokens), `claude-sonnet-5-5` ($2 / $10), `claude-fable-5-1` ($10 / $50), `claude-haiku-4-5` ($1 / $5) ([models overview](https://platform.claude.com/docs/en/models/overview)).
4. Human control in headless runs: a `PreToolUse` hook can return `"defer"`, which stops the run at that tool call so a person can decide, then `claude -p --resume` continues ([hooks](https://code.claude.com/docs/en/hooks)). Time boxes: `--max-turns`, `--max-budget-usd` ([CLI reference](https://code.claude.com/docs/en/cli-reference)).
5. Keyless auth: the GitLab CI doc has a Google Cloud's Agent Platform (formerly Vertex AI) job that uses GitLab OIDC and Workload Identity Federation, with no stored keys ([doc](https://code.claude.com/docs/en/gitlab-ci-cd)).
6. MCP's current spec revision is `2026-07-28` (stateless). MCP was donated to the Agentic AI Foundation under the Linux Foundation on 2025-12-09 ([releases](https://github.com/modelcontextprotocol/modelcontextprotocol/releases), [news](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).
7. GitLab Duo itself uses Claude: the default model for most Duo features is "Claude Sonnet 4.6 Gemini Enterprise Agent Platform", meaning Claude served through Google ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/gitlab_duo/model_selection.md)). That links all three sponsors.

## Launches 2025-2026

Release notes link: [platform release notes](https://platform.claude.com/docs/en/release-notes/overview) (anchors are by date). Claude Code weekly digest: [What's new](https://code.claude.com/docs/en/whats-new/index).

| What | Date | Link | Why it would showcase well |
|---|---|---|---|
| Web search tool in the API | 2025-05-07 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-7-2025) | Agent can check current advisories or docs. $10 per 1,000 searches ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)). |
| Claude Opus 4 and Sonnet 4; Files API, code execution tool and MCP connector betas | 2025-05-22 | [news](https://www.anthropic.com/news/claude-4), [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-22-2025) | Start of the API agent toolkit used below. Opus 4 and Sonnet 4 are now retired on the API (2026-06-15). |
| "Our framework for developing safe and trustworthy agents" | 2025-08-04 | [news](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents) | Anthropic's own yardstick: human control before high-stakes decisions, transparency, privacy, security. |
| Web fetch tool (beta) | 2025-09-10 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-10-2025) | Read a runbook, status page or changelog URL. No charge beyond tokens. |
| Claude Sonnet 4.5; Claude Agent SDK ("formerly the Claude Code SDK") with subagents and hooks; Claude Code 2.0 with checkpoints; memory tool and context editing betas | 2025-09-29 | [Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5), [Claude Code update](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously), [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-29-2025) | The Agent SDK is Claude Code as a library: a natural core for a custom post-code agent. |
| Claude Haiku 4.5 | 2025-10-15 | [news](https://www.anthropic.com/news/claude-haiku-4-5) | Cheap, fast model ($1 / $5) for triage or classification subagents. |
| Agent Skills (published as an open standard on 2025-12-18) | 2025-10-16 | [news](https://www.anthropic.com/news/skills), [engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Ship runbooks as `SKILL.md` folders in the repo. Claude Code and the API load them. |
| Claude Code sandboxing | 2025-10-20 | [engineering](https://www.anthropic.com/engineering/claude-code-sandboxing) | Shows how Anthropic wants autonomous runs contained. |
| Structured outputs (beta; GA on 2026-01-29) | 2025-11-14 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#november-14-2025) | Schema-guaranteed JSON, so code (not prose) decides what happens next. |
| Claude Opus 4.5; tool search tool; programmatic tool calling; effort parameter | 2025-11-24 | [news](https://www.anthropic.com/news/claude-opus-4-5), [engineering](https://www.anthropic.com/engineering/advanced-tool-use) | Handle big tool sets (the GitLab API is big) without filling the context window. |
| MCP spec revision 2025-11-25 | 2025-11-25 | [GitHub releases](https://github.com/modelcontextprotocol/modelcontextprotocol/releases) | Async tasks, URL elicitation. GitLab's MCP server supports this revision. |
| Claude Code at $1B run-rate; Anthropic acquires Bun | 2025-12-03 | [news](https://www.anthropic.com/news/anthropic-acquires-bun-as-claude-code-reaches-usd1b-milestone) | Context: Claude Code is Anthropic's flagship developer product. |
| MCP donated to the Agentic AI Foundation (Linux Foundation) | 2025-12-09 | [news](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) | MCP is now a neutral standard, co-founded with Block and OpenAI, supported by Google and others. |
| Claude Opus 4.6; compaction API (beta); data residency (`inference_geo`) | 2026-02-05 | [news](https://www.anthropic.com/news/claude-opus-4-6), [release notes](https://platform.claude.com/docs/en/release-notes/overview#february-5-2026) | Long-running agent context management. |
| Claude Sonnet 4.6; code execution free with web search or web fetch; web fetch, tool search and memory tool out of beta | 2026-02-17 | [news](https://www.anthropic.com/news/claude-sonnet-4-6), [release notes](https://platform.claude.com/docs/en/release-notes/overview#february-17-2026) | Sonnet 4.6 is GitLab Duo's default model for most features ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/gitlab_duo/model_selection.md)). |
| Automatic prompt caching | 2026-02-19 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#february-19-2026) | One top-level `cache_control` field cuts the cost of repeated repo context. |
| Claude Code Security (research preview) | 2026-02-20 | [news](https://www.anthropic.com/news/claude-code-security) | Scans code and "suggests targeted software patches for human review": a post-code task. |
| Claude Code auto mode (research preview) | week of 2026-03-23; engineering post 2026-03-25 | [What's new week 13](https://code.claude.com/docs/en/whats-new/2026-w13), [engineering](https://www.anthropic.com/engineering/claude-code-auto-mode) | A classifier reviews actions. Anthropic's current approach to autonomy with oversight. |
| Claude Managed Agents (public beta) and the `ant` CLI | 2026-04-08 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#april-8-2026), [engineering](https://www.anthropic.com/engineering/managed-agents) | Anthropic-hosted agent loop and sandbox, with webhooks and cron. One way to host the agent. |
| Advisor tool (beta) | 2026-04-09 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#april-9-2026) | A cheaper executor model asks a stronger advisor model at hard decisions. |
| Claude Opus 4.7; task budgets (beta); `xhigh` effort | 2026-04-16 | [news](https://www.anthropic.com/news/claude-opus-4-7), [release notes](https://platform.claude.com/docs/en/release-notes/overview#april-16-2026) | Task budgets give the model a token countdown for a whole agent loop: a built-in time box. |
| Workload Identity Federation for the Claude API | 2026-05-04 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-4-2026), [docs](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) | Short-lived OIDC tokens instead of a stored `sk-ant-` key. |
| Managed Agents: multiagent orchestration, outcomes (rubric grader), webhooks, dreams | 2026-05-06 (API); blog dated 2026-05-19 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-6-2026), [blog](https://claude.com/blog/new-in-claude-managed-agents) | A separate grader checks the agent's work against a rubric. |
| Anthropic acquires Stainless ("a leader in SDKs and MCP server tooling") | 2026-05-18 | [news](https://www.anthropic.com/news/anthropic-acquires-stainless) | Shows where Anthropic is investing: tools and MCP servers. |
| MCP tunnels (research preview); Managed Agents self-hosted sandboxes | 2026-05-19 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-19-2026), [blog](https://claude.com/blog/claude-managed-agents-updates) | Reach MCP servers on a private network; run tools on your own infrastructure. |
| Claude Opus 4.8; Workflows (research preview) in Claude Code | 2026-05-28 | [news](https://www.anthropic.com/news/claude-opus-4-8), [release notes](https://platform.claude.com/docs/en/release-notes/overview#may-28-2026) | Dynamic workflows run many subagents from a script Claude writes. |
| Claude Fable 5 (Mythos 5 for Project Glasswing); Managed Agents scheduled deployments | 2026-06-09 | [news](https://www.anthropic.com/news/claude-fable-5-mythos-5), [release notes](https://platform.claude.com/docs/en/release-notes/overview#june-9-2026) | Top capability tier. Access was suspended on 2026-06-12 under a US export-control directive and restored 2026-06-30 ([statement](https://www.anthropic.com/news/fable-mythos-access), [restored](https://www.anthropic.com/news/redeploying-fable-5)). |
| Claude Tag (Claude joins Slack channels; anyone can tag @Claude to delegate) | 2026-06-23 | [news](https://www.anthropic.com/news/introducing-claude-tag) | The chat-ops shape of an `@claude` mention. |
| Claude Sonnet 5 | 2026-06-30 | [news](https://www.anthropic.com/news/claude-sonnet-5) | $2 / $10 with a 1M context window. |
| Claude Opus 5 | 2026-07-24 | [news](https://www.anthropic.com/news/claude-opus-5) | Now superseded by Opus 5.5. |
| MCP spec revision 2026-07-28 (stateless) | 2026-07-28 | [GitHub releases](https://github.com/modelcontextprotocol/modelcontextprotocol/releases) | Current MCP revision. Claude Code supports it. |
| Managed Agents session budgets and advisor | 2026-08-07 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#august-7-2026) | Hard spend cap per session. |
| Computer use toolset GA; browser use tool; Files API GA; Agent Skills GA | 2026-08-19 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#august-19-2026) | Fewer beta headers. |
| Claude Code GitLab work: GitLab token redaction and gitlab.com plugin marketplaces (v2.1.232, 2026-08-13); MR URLs in `--worktree` and agent view (v2.1.233, 2026-08-14); MR badge (v2.1.234, 2026-08-17); `/code-review --comment` posts to GitLab MRs through `glab` (v2.1.257, 2026-09-01) | 2026-08-13 to 2026-09-01 | [changelog](https://code.claude.com/docs/en/changelog), [code review doc](https://code.claude.com/docs/en/code-review) | Anthropic is actively improving Claude Code on GitLab. A GitLab-native demo is timely. |
| Claude Fable 5.1 | 2026-09-01 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-1-2026) | Highest capability model open to all; $10 / $50. |
| `ant apply`: agents, environments, skills and deployments as files in the repo | 2026-09-03 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-3-2026) | Agent config reviewed in MRs and applied from CI. |
| Managed Agents permission policy `auto` | 2026-09-10 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-10-2026) | Server evaluates each tool call: run it, deny it, or pause for approval. |
| Claude Opus 5.5 | 2026-09-22 | [news](https://www.anthropic.com/news/claude-opus-5-5) | Current default model. It "costs 40% less to run than Opus 5"; cache reads $0.20 per million tokens. |
| Claude Sonnet 5.5 | 2026-09-28 | [release notes](https://platform.claude.com/docs/en/release-notes/overview#september-28-2026) | Same price as Sonnet 5. |
| Claude Code mods (TypeScript functions, shipped in plugins) | 2026-10-01 | [blog](https://claude.com/blog/claude-code-mods) | Newest Claude Code launch. |

Not usable with GitLab-hosted repos (worth knowing before planning):

- Claude Code on the web (cloud sessions): "repository cloning and pull request creation require GitHub" ([doc](https://code.claude.com/docs/en/claude-code-on-the-web)).
- Routines (scheduled, API or GitHub-triggered cloud agents) run as Claude Code cloud sessions, so the same GitHub limit should apply (inference) ([routines](https://code.claude.com/docs/en/routines)).
- Managed Code Review service: "analyzes your GitHub pull requests", Team and Enterprise only ([doc](https://code.claude.com/docs/en/code-review)). The local `/code-review --comment` does work on GitLab MRs.
- Managed Agents documents repository mounting for GitHub only; no GitLab mount is documented. For GitLab, an agent would clone over the network or use an MCP server ([GitHub page](https://platform.claude.com/docs/en/managed-agents/github), [environments](https://platform.claude.com/docs/en/managed-agents/environments)). `gitlab.com` is in the package-manager host list for `limited` networking.

## Claude Code in GitLab CI/CD (exact)

Source: [code.claude.com/docs/en/gitlab-ci-cd](https://code.claude.com/docs/en/gitlab-ci-cd).

Status, quoted from the page:

- "Claude Code for GitLab CI/CD is currently in beta. Features and functionality may evolve as we refine the experience."
- "This integration is maintained by GitLab." Support issue: [gitlab-org/gitlab#573776](https://gitlab.com/gitlab-org/gitlab/-/issues/573776). Through the GitLab API that issue is titled "GitLab Headless CLI Agents - Feedback Issue" and was closed on 2025-12-09 ([API](https://gitlab.com/api/v4/projects/278964/issues/573776)).
- "This integration is built on top of the Claude Code CLI and Agent SDK".

How it works, per the page: GitLab listens for a trigger (for example a comment with `@claude`), the job collects context, builds a prompt and runs Claude Code. Provider is Claude API, Amazon Bedrock, or Google Cloud's Agent Platform. Each run is in a container, and "Every change flows through an MR so reviewers see the diff and approvals still apply."

### Quick setup (verbatim)

1. Settings > CI/CD > Variables: add `ANTHROPIC_API_KEY` ("masked, protected as needed").
2. Add this job to `.gitlab-ci.yml`:

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  # Adjust rules to fit how you want to trigger the job:
  # - manual runs
  # - merge request events
  # - web/API triggers when a comment contains '@claude'
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
    # The installer places claude in ~/.local/bin, which isn't on PATH in this image
    - export PATH="$HOME/.local/bin:$PATH"
  script:
    # Optional: start a GitLab MCP server if your setup provides one
    - /bin/gitlab-mcp-server || true
    # Use AI_FLOW_* variables when invoking via web/API triggers with context payloads
    - echo "$AI_FLOW_INPUT for $AI_FLOW_CONTEXT on $AI_FLOW_EVENT"
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
```

Builder notes on this job:

- Install alternative: `npm install -g @anthropic-ai/claude-code`, which needs Node.js 22 or later ([setup](https://code.claude.com/docs/en/setup)). GitLab's own Claude agent config uses npm on `node:22-slim` (below).
- `/bin/gitlab-mcp-server` is only "if your setup provides one". The page does not say where that binary comes from (unverified).
- `mcp__gitlab` "matches any tool provided by" an MCP server named `gitlab` ([permissions](https://code.claude.com/docs/en/permissions)). The CLI reference shows `--allowedTools` values as comma-separated or as separate quoted values; whether one space-separated string is split the same way is (unverified) ([CLI reference](https://code.claude.com/docs/en/cli-reference)).
- Trigger gotcha: the rules allow only `web` and `merge_request_event`. A pipeline started with a trigger token has `CI_PIPELINE_SOURCE` = `trigger`, and one started with the pipelines API has `api` ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/jobs/job_rules.md)). Add a rule for whichever one your listener uses.

### Manual setup (recommended for production), per the page

1. Provider access: `ANTHROPIC_API_KEY` as a masked variable, or AWS OIDC for Bedrock, or Workload Identity Federation for Google Cloud.
2. GitLab API credentials: "Use `CI_JOB_TOKEN` by default, or create a Project Access Token with `api` scope". "Store as `GITLAB_ACCESS_TOKEN` (masked) if using a PAT".
3. Add the job.
4. Optional mention-driven triggers: "Add a project webhook for "Comments (notes)" to your event listener (if you use one)" and "Have the listener call the pipeline trigger API with variables like `AI_FLOW_INPUT` and `AI_FLOW_CONTEXT` when a comment contains `@claude`".

The trigger API call from GitLab's docs ([source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/triggers/_index.md)), with the variable names from the Claude doc filled in:

```shell
curl --request POST \
     --form token=TOKEN \
     --form ref=main \
     --form "variables[AI_FLOW_INPUT]=..." \
     "https://gitlab.example.com/api/v4/projects/123456/trigger/pipeline"
```

(The `variables[key]=value` form is from the GitLab doc; the `AI_FLOW_INPUT` name in it is our substitution.)

### AI_FLOW variables

The Claude page names `AI_FLOW_INPUT`, `AI_FLOW_CONTEXT` and `AI_FLOW_EVENT`. These are the same names GitLab Duo Agent Platform injects into external agents. GitLab's definitions ([examples doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external_examples.md), [external agents doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md)):

| Variable | Meaning (GitLab docs) |
|---|---|
| `AI_FLOW_CONTEXT` | "the JSON-serialized parent object": in MRs "the diff and comments (up to a limit)", in issues or epics "the comments (up to a limit)" |
| `AI_FLOW_EVENT` | "the type of trigger event (for example, `mention`)" |
| `AI_FLOW_INPUT` | "the prompt the user enters as a comment in the merge request, issue, or epic" |
| `AI_FLOW_GITLAB_TOKEN` | "the OAuth token for authenticating to the GitLab API"; limited to the `ai_workflows` scope; send as `Authorization: Bearer` (a `PRIVATE-TOKEN` header returns 401) |
| `AI_FLOW_GITLAB_HOSTNAME` | "the hostname of the GitLab instance (for example, `gitlab.com`)" |
| `AI_FLOW_PROJECT_PATH` | "the full path of the project (for example, `my-group/my-project`)" |
| `AI_FLOW_AI_GATEWAY_TOKEN`, `AI_FLOW_AI_GATEWAY_HEADERS` | injected when `injectGatewayToken: true` (GitLab-managed credentials, "available for only Anthropic Claude and OpenAI Codex") |

In the Duo Agent Platform these are injected for you. In a plain `.gitlab-ci.yml` setup you pass them yourself as trigger variables.

### Limits, cost controls, troubleshooting (from the page)

- Flags and keywords the page lists: `-p`; `--max-turns` ("limit the number of back-and-forth iterations"); GitLab job `timeout` ("for example `timeout: 30m`"); `ANTHROPIC_API_KEY` ("not used for Amazon Bedrock or Google Cloud's Agent Platform"); provider variables. It adds: "Exact flags and parameters may vary by version of `@anthropic-ai/claude-code`. Run `claude --help` in your job".
- Costs: GitLab runner minutes plus API tokens. Tips: "Use specific `@claude` commands to reduce unnecessary turns", "Set appropriate `--max-turns` and job `timeout` values", "Limit concurrency to control parallel runs".
- Not covered by the page but available: `--max-budget-usd` and `--permission-prompts none` ([CLI reference](https://code.claude.com/docs/en/cli-reference), [headless](https://code.claude.com/docs/en/headless)).
- Troubleshooting: the comment must contain `@claude` "(not `/claude`)"; for comments and MRs, `CI_JOB_TOKEN` needs permissions or use a Project Access Token with `api` scope; "Check the `mcp__gitlab` tool is enabled in `--allowedTools`".
- Customizing: `CLAUDE.md` at the repo root plus per-job prompts via `-p`.

### Provider options

| Provider | CI/CD variables | Auth |
|---|---|---|
| Claude API | `ANTHROPIC_API_KEY` (masked) | API key |
| Amazon Bedrock | `AWS_ROLE_TO_ASSUME`, `AWS_REGION`, `CLAUDE_CODE_USE_BEDROCK: "1"` | GitLab OIDC `id_tokens` then `aws sts assume-role-with-web-identity` |
| Google Cloud's Agent Platform (formerly Vertex AI) | `GCP_WORKLOAD_IDENTITY_PROVIDER` (no `//iam.googleapis.com/` prefix), `GCP_SERVICE_ACCOUNT`, `GCP_PROJECT_ID`, `CLOUD_ML_REGION` (example `us-east5`), `CLAUDE_CODE_USE_VERTEX: "1"`, `ANTHROPIC_VERTEX_PROJECT_ID` | GitLab OIDC `id_tokens` plus Workload Identity Federation; "you do not need to store service account keys" |

Google Cloud's Agent Platform job (verbatim, most relevant for this hackathon):

```yaml
stages:
  - ai

claude-vertex:
  stage: ai
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  before_script:
    - apt-get update && apt-get install -y git && apt-get clean
    - curl -fsSL https://claude.ai/install.sh | bash
    # The installer places claude in ~/.local/bin, which isn't on PATH in this image
    - export PATH="$HOME/.local/bin:$PATH"
    # Write the job's OIDC token where credential_source expects it
    - printf "%s" "$GITLAB_OIDC_TOKEN" > /tmp/oidc_token
    # Write the WIF credential configuration to a file (no downloaded keys)
    - |
      cat > /tmp/cred.json <<EOF
      {
        "type": "external_account",
        "audience": "//iam.googleapis.com/${GCP_WORKLOAD_IDENTITY_PROVIDER}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
          "file": "/tmp/oidc_token"
        },
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_SERVICE_ACCOUNT}:generateAccessToken"
      }
      EOF
    # Expose the credentials to Claude Code via Application Default Credentials
    - export GOOGLE_APPLICATION_CREDENTIALS=/tmp/cred.json
    # Authenticate the gcloud CLI with the same credential configuration
    - gcloud auth login --cred-file=/tmp/cred.json
    - gcloud config set project "$GCP_PROJECT_ID"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      CLOUD_ML_REGION="${CLOUD_ML_REGION:-us-east5}"
      claude
      -p "${AI_FLOW_INPUT:-'Review and update code as requested'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    CLOUD_ML_REGION: "us-east5"
    CLAUDE_CODE_USE_VERTEX: "1"
    ANTHROPIC_VERTEX_PROJECT_ID: "$GCP_PROJECT_ID"
```

Amazon Bedrock job (verbatim):

```yaml
stages:
  - ai

claude-bedrock:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  before_script:
    - apk add --no-cache bash curl jq git aws-cli
    - curl -fsSL https://claude.ai/install.sh | bash
    # The installer places claude in ~/.local/bin, which isn't on PATH in this image
    - export PATH="$HOME/.local/bin:$PATH"
    # Exchange the job's OIDC token for AWS credentials
    - export AWS_WEB_IDENTITY_TOKEN_FILE="/tmp/oidc_token"
    - printf "%s" "$GITLAB_OIDC_TOKEN" > "$AWS_WEB_IDENTITY_TOKEN_FILE"
    - >
      aws sts assume-role-with-web-identity
      --role-arn "$AWS_ROLE_TO_ASSUME"
      --role-session-name "gitlab-claude-$(date +%s)"
      --web-identity-token "file://$AWS_WEB_IDENTITY_TOKEN_FILE"
      --duration-seconds 3600 > /tmp/aws_creds.json
    - export AWS_ACCESS_KEY_ID="$(jq -r .Credentials.AccessKeyId /tmp/aws_creds.json)"
    - export AWS_SECRET_ACCESS_KEY="$(jq -r .Credentials.SecretAccessKey /tmp/aws_creds.json)"
    - export AWS_SESSION_TOKEN="$(jq -r .Credentials.SessionToken /tmp/aws_creds.json)"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Implement the requested changes and open an MR'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    AWS_REGION: "us-west-2"
    CLAUDE_CODE_USE_BEDROCK: "1"
```

Provider notes:

- `CLOUD_ML_REGION` can be `global`, a multi-region such as `us` or `eu`, or a region; if unset, Claude Code falls back to `us-east5` ([Agent Platform setup](https://code.claude.com/docs/en/google-vertex-ai)).
- Alias resolution differs by provider: on Bedrock and Google Cloud's Agent Platform, `opus` is Opus 5.5 but `sonnet` is still Sonnet 4.5. Pass a full model name such as `--model claude-sonnet-5-5` to get a newer Sonnet ([model config](https://code.claude.com/docs/en/model-config)). Per-region availability on Google Cloud is (unverified).
- Bedrock model IDs carry a region prefix, for example `us.anthropic.claude-sonnet-4-6` (from the GitLab CI page).
- If the agent calls the Claude API directly (not through Claude Code) on Google Cloud, several server features are missing there: web fetch, Files API, code execution and the MCP connector are listed as not available on Google Cloud, and web search is the basic version only ([web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), [Files API](https://platform.claude.com/docs/en/build-with-claude/files), [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector), [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)). Managed Agents is "Not available on partner-operated cloud platforms" ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)).

### The GitLab-side path: "Claude Code Agent by GitLab" (GitLab docs)

From GitLab's [external agents doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md):

- Tier: Premium, Ultimate. Renamed from "CLI agents" in GitLab 18.6. A flag note says the feature is "enabled for verified customers" and otherwise "contact GitLab support".
- "The Claude Code Agent by GitLab uses GitLab-managed credentials and does not require additional configuration." AI Catalog entry: [agents/2337](https://gitlab.com/explore/ai-catalog/agents/2337/).
- On GitLab.com "you cannot create custom external agents"; use the GitLab-managed ones.
- Models allowed with GitLab-managed credentials: `claude-haiku-4-5-20251001`, `claude-opus-4-5-20251101`, `claude-opus-4-6`, `claude-sonnet-4-20250514`, `claude-sonnet-4-5-20250929`, `claude-sonnet-4-6`. No 5.x models in that list.
- Security warning from GitLab: "GitLab implements third-party prompt scanning to lower the risk of prompt injections. This scanning is not available for external agents."
- You use it by mentioning, assigning, or requesting review from the agent's service account in an issue, MR or epic.

Trigger types for agents and flows ([GitLab triggers doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)): Mention; Assign; Assign reviewer; Pipeline events (Running, Passed, Failed, Canceled); Merge request (Approved, Created, Marked ready, Merge conflict); Work item (Created, Status changed). The Pipeline events trigger set to Failed is a direct post-code hook.

GitLab's Claude Code agent config, excerpt with the exact lines that matter ([source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external_examples.md); the long `glab` install and config lines, and the rest of the prompt, are left out here):

```yaml
injectGatewayToken: true
image: node:22-slim
commands:
  - echo "Installing claude"
  - npm install -g @anthropic-ai/claude-code
  - git remote set-url origin https://gitlab-ci-token:$AI_FLOW_GITLAB_TOKEN@$AI_FLOW_GITLAB_HOSTNAME/$AI_FLOW_PROJECT_PATH.git
  - export ANTHROPIC_AUTH_TOKEN=$AI_FLOW_AI_GATEWAY_TOKEN
  - export ANTHROPIC_CUSTOM_HEADERS=$AI_FLOW_AI_GATEWAY_HEADERS
  - export ANTHROPIC_BASE_URL="https://cloud.gitlab.com/ai/v1/proxy/anthropic"
  - echo "Running claude"
  - |
    claude --allowedTools="Bash(glab:*),Bash(git:*)" --permission-mode acceptEdits --setting-sources '' --verbose --output-format stream-json -p "
    You are an AI assistant helping with GitLab operations.

    Context: $AI_FLOW_CONTEXT
    Task: $AI_FLOW_INPUT
    Event: $AI_FLOW_EVENT
```

Note the pattern: the agent talks to GitLab with the `glab` CLI and a scoped token, not through MCP, and turns off local settings with `--setting-sources ''`.

### GitLab MCP server with Claude Code (GitLab docs)

From the [GitLab MCP server doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/model_context_protocol/mcp_server.md): status Beta; tiers Free, Premium, Ultimate (moved to Free in GitLab 19.2); supports MCP revisions `2025-03-26`, `2025-06-18` and `2025-11-25` (added in 18.7). Endpoint `https://<gitlab.example.com>/api/v4/mcp`. Auth is OAuth 2.0 Dynamic Client Registration with browser approval. Claude Code setup:

```shell
claude mcp add -s user --transport http GitLab https://<gitlab.example.com>/api/v4/mcp
```

Then type `/mcp` in Claude Code and approve in the browser. Toolsets can be chosen with the `X-Gitlab-Enabled-Mcp-Server-Toolsets` header (`--header` on `claude mcp add`). Because auth needs a browser, this fits a developer laptop better than a CI job (inference). The doc warns: "You're responsible for guarding against prompt injection when you use these tools."

### Comparison with GitHub Actions

| | GitHub Actions ([doc](https://code.claude.com/docs/en/github-actions)) | GitLab CI/CD ([doc](https://code.claude.com/docs/en/gitlab-ci-cd)) |
|---|---|---|
| Packaging | `anthropics/claude-code-action@v1` | a job you paste into `.gitlab-ci.yml` |
| Maintainer | Anthropic repo [claude-code-action](https://github.com/anthropics/claude-code-action) | "maintained by GitLab" |
| Setup helper | `/install-github-app` (prints a notice and exits for gitlab.com remotes) | none |
| `@claude` trigger | built in: with no `prompt` input the action waits for the trigger phrase (`trigger_phrase`, default `@claude`) | not built in: Duo Agent Platform or your own webhook listener |
| Automation | `prompt` input | `-p` in `script` |
| CLI flags | `claude_args: "--max-turns 5 --model claude-sonnet-5 --mcp-config /path/to/config.json"` | flags directly on `claude` |
| Keyless Claude API | WIF inputs `anthropic_federation_rule_id`, `anthropic_organization_id`, optional `anthropic_service_account_id`, `anthropic_workspace_id`, plus `id-token: write` | not documented for the Claude API; Bedrock and Google examples are keyless |
| Subscription auth | `claude_code_oauth_token` from `claude setup-token` | `CLAUDE_CODE_OAUTH_TOKEN` env var works for the CLI in general ([auth](https://code.claude.com/docs/en/authentication)); not mentioned on the GitLab page |
| Abuse checks | write-access check on the triggering user, bot actors rejected unless in `allowed_bots` | none described on the GitLab page; rely on GitLab permissions and MR approvals |

### Keyless Claude API from GitLab CI (idea, untested)

- Claude Code selects federation credentials when `ANTHROPIC_FEDERATION_RULE_ID` and `ANTHROPIC_ORGANIZATION_ID` are set, and reads `ANTHROPIC_IDENTITY_TOKEN_FILE` during the exchange ([env vars](https://code.claude.com/docs/en/env-vars), [authentication](https://code.claude.com/docs/en/authentication)). The SDK path needs all of `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID` and `ANTHROPIC_IDENTITY_TOKEN_FILE` or `ANTHROPIC_IDENTITY_TOKEN` ([WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference)).
- Anthropic WIF accepts "any standards-compliant OIDC issuer"; the Console has a "Custom OIDC" tile for providers without a preset ([WIF](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)). GitLab is not named.
- GitLab ID tokens carry `iss`, `sub` (default `project_path:{group}/{project}:ref_type:{type}:ref:{branch_name}`), `aud`, `exp` and `jti` ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md)).
- Caveats: Claude Code does not read federation variables in `--bare` mode ([authentication](https://code.claude.com/docs/en/authentication)). Tokens with `jti` are single-use by default, so a refresh that re-reads the same job token fails with `jti_reused` ([WIF](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)); setting the federation rule's `token_lifetime_seconds` (60 to 86400, default 3600) above the job timeout should avoid a refresh (inference, untested).

## Headless mode, hooks, Agent SDK (exact)

Claude Code version on 2026-10-06: 2.1.290, released 2026-10-05 ([changelog](https://code.claude.com/docs/en/changelog); npm `@anthropic-ai/claude-code` is also 2.1.290).

### `claude -p` (non-interactive)

From [headless](https://code.claude.com/docs/en/headless) unless noted:

- `claude -p "..."` (or `--print`) runs without the interactive UI. "Claude Code exits with code 0 on success and a non-zero code when the run fails". A bad flag errors on stderr before the run; a failure inside the run is printed as the result on stdout.
- `--bare` skips auto-discovery of "hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md". "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release." Bare mode needs `ANTHROPIC_API_KEY` or an `apiKeyHelper`; it ignores OAuth and `CLAUDE_CODE_OAUTH_TOKEN`. Pass context with `--append-system-prompt-file`, `--settings`, `--mcp-config`, `--agents`, `--plugin-dir`.
- Security note: without `--bare`, "a `-p` session runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`, even in a folder you've never trusted". Matters for MR pipelines on branches you do not control.
- Output: `--output-format text|json|stream-json`. JSON includes `result`, `session_id`, `total_cost_usd` and a per-model cost breakdown (client-side estimates). `--json-schema '<schema>'` puts validated output in `structured_output`. `stream-json` is used with `--verbose` (add `--include-partial-messages` for token deltas); the last line is a `result` message.
- Piped stdin is capped at 10MB.
- Result message shape (TypeScript `SDKResultMessage`): `subtype` is `success`, `error_max_turns`, `error_during_execution`, `error_max_budget_usd` or `error_max_structured_output_retries`; fields include `is_error`, `num_turns`, `result`, `stop_reason`, `total_cost_usd`, `usage`, `permission_denials`, `structured_output`, `deferred_tool_use` ([TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript)).
- The `system/init` event lists loaded `plugins`, `plugin_errors`, `mcp_servers` and `mcp_server_errors`, so CI can fail when a plugin or MCP server did not load.
- Skills and custom commands work in `-p`: "Include `/skill-name` in the prompt string".

Key flags ([CLI reference](https://code.claude.com/docs/en/cli-reference)):

| Flag | Exact behavior |
|---|---|
| `--allowedTools`, `--allowed-tools` | "Tools that execute without prompting for permission." Uses permission rule syntax, for example `"Bash(git log *)" "Bash(git diff *)" "Read"` |
| `--disallowedTools` | Deny rules. A bare name removes the tool; `"mcp__*"` removes every MCP tool |
| `--tools` | Restricts built-in tools, for example `"Bash,Edit,Read"`; `""` disables all |
| `--permission-mode` | `default` (alias `manual`), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--permission-prompts none` | Unattended runs: anything that would prompt is denied and Claude is told not to retry. Needs v2.1.259 or later |
| `--max-turns` | "Limit the number of agentic turns (print mode only). Exits with an error when the limit is reached. No limit by default." |
| `--max-budget-usd` | "Maximum dollar amount to spend on API calls before stopping (print mode only)", checked against the client-side estimate; subagent spend counts |
| `--json-schema` | "Get validated JSON output matching a JSON Schema after the agent completes its workflow (print mode only)" |
| `--output-format` / `--input-format` | `text`, `json`, `stream-json` / `text`, `stream-json` |
| `--model` | alias (`sonnet`, `opus`, `haiku`, `fable`) or full name, for example `claude-sonnet-5` |
| `--fallback-model` | comma-separated list tried in order when the primary is overloaded or unavailable |
| `--effort` | `low`, `medium`, `high`, `xhigh`, `max`, or `ultracode` |
| `--mcp-config`, `--strict-mcp-config` | load MCP servers from JSON; strict ignores all other MCP config. With `-p`, waits up to `MCP_TIMEOUT` (30 seconds default) for servers |
| `--append-system-prompt[-file]`, `--system-prompt[-file]` | append to, or replace, the default system prompt |
| `--settings`, `--setting-sources` | settings file or JSON; which sources to load (`user`, `project`, `local`) |
| `--agents` | define subagents as JSON (a file path is accepted with `--print` from v2.1.281) |
| `--plugin-dir` | load a plugin directory or `.zip` for this session |
| `--no-session-persistence` | do not save the session to disk (print mode only) |
| `--continue`, `--resume <id>` | continue the latest or a specific session; `--resume` also accepts the absolute path to a session `.jsonl` file ([headless](https://code.claude.com/docs/en/headless)) |

Permission modes ([permission modes](https://code.claude.com/docs/en/permission-modes)):

| Mode | What runs without asking | Best for (doc wording) |
|---|---|---|
| `default` | Reads only | "Reviewing every action yourself, sensitive work" |
| `acceptEdits` | Reads, file edits, common filesystem commands | "Iterating on code you're reviewing" |
| `plan` | Reads (plus classifier-approved commands where auto mode is available) | "Exploring a codebase before changing it" |
| `auto` | "Everything, with background safety checks" | "Long tasks, reducing prompt fatigue" |
| `dontAsk` | Reads and pre-approved tools; anything that would prompt is denied | "Locked-down CI and scripts" |
| `bypassPermissions` | Everything | "Isolated containers and VMs only" |

Since v2.1.283, auto mode is the built-in starting mode for interactive sessions, and a `-p` run with nothing set can start in `auto`; so set the mode explicitly in CI ([permission modes](https://code.claude.com/docs/en/permission-modes), [headless](https://code.claude.com/docs/en/headless)). Deny rules block in every mode, including `bypassPermissions`.

Doc examples (verbatim):

```bash
claude -p "run the test suite" --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"
```

```bash
claude -p "Look at my staged changes and create an appropriate commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"
```

```bash
claude -p "Extract the main function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

The trailing ` *` is a prefix match, and "The space before `*` is important" (`Bash(git diff*)` would also match `git diff-index`).

Auth for CI: `ANTHROPIC_API_KEY` is "always used when present" in `-p` mode ([env vars](https://code.claude.com/docs/en/env-vars)). Alternative: `claude setup-token` makes "a one-year OAuth token" set as `CLAUDE_CODE_OAUTH_TOKEN`; it "requires a Pro, Max, Team, or Enterprise plan" and bare mode does not read it ([authentication](https://code.claude.com/docs/en/authentication)).

### Hooks

From the [hooks reference](https://code.claude.com/docs/en/hooks) and [hooks guide](https://code.claude.com/docs/en/hooks-guide):

- Config lives in `~/.claude/settings.json`, `.claude/settings.json` (shareable), `.claude/settings.local.json`, managed policy, a plugin's `hooks/hooks.json`, or skill and subagent frontmatter.
- Three levels: event, matcher group, handler. Handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent` (agent hooks "are experimental").
- Events: `SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `MessageDisplay`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`, `SessionEnd`.
- Default timeouts: 600 seconds for `command`, `http`, `mcp_tool`; 30 for `prompt`; 60 for `agent`.
- Exit code 0 is success; exit code 2 blocks, and "Exit 2's block is the one outcome JSON can't override".
- `PreToolUse` returns `permissionDecision`: `allow`, `deny`, `ask` or `defer`. Precedence across hooks: "`deny` > `defer` > `ask` > `allow`".

Config example (verbatim):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

The `defer` decision is the human-approval tool for headless runs. Per the docs, it works only with `-p`:

1. The hook returns `permissionDecision: "defer"`; the tool does not run.
2. The process exits with `stop_reason: "tool_deferred"`; the result carries `deferred_tool_use` with the tool's `id`, `name` and `input`.
3. Your code shows the request to a person.
4. Run `claude -p --resume <session-id>` again; the same `PreToolUse` hook fires and can now return `allow` or `deny`.

Limits: `defer` works only when Claude makes a single tool call in that turn (with several calls it is ignored with a warning); sessions stay on disk until `cleanupPeriodDays` (30 days by default); on resume with `-p`, pass `--permission-mode` again. A GitLab version could save the session `.jsonl` as a job artifact and resume it from a `when: manual` approval job (our idea, untested; `--resume` accepting a `.jsonl` path is documented in [headless](https://code.claude.com/docs/en/headless)).

### Subagents, skills, plugins, MCP, settings

- Subagents: markdown files in `.claude/agents/` with YAML frontmatter; "The body becomes the system prompt" ([subagents](https://code.claude.com/docs/en/sub-agents)). Verbatim example:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

- Skills: a folder with `SKILL.md` (YAML frontmatter, then instructions), for example `.claude/skills/deploy/SKILL.md` creates `/deploy`. "Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard". Custom commands in `.claude/commands/` were merged into skills ([skills](https://code.claude.com/docs/en/skills)).
- Plugins: a directory of skills, agents, hooks, MCP servers and more, with a manifest at `.claude-plugin/plugin.json` ([plugins](https://code.claude.com/docs/en/plugins/overview)). Install example: `claude plugin install code-review@claude-plugins-official` ([CLI reference](https://code.claude.com/docs/en/cli-reference)).
- MCP in Claude Code: `claude mcp add --transport http <name> <url>`; project-shared servers go in `.mcp.json`; the `type` field accepts `streamable-http` as an alias for `http` ([MCP](https://code.claude.com/docs/en/mcp)). Tool names are `mcp__<server>__<tool>`.
- Settings: precedence is managed settings, then command line arguments, then `.claude/settings.local.json`, then `.claude/settings.json`, then `~/.claude/settings.json` ([settings](https://code.claude.com/docs/en/settings)). Verbatim example:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

### Claude Agent SDK

- Packages: Python `claude-agent-sdk` 0.2.163 (2026-09-30, Python 3.10 or later) ([PyPI](https://pypi.org/project/claude-agent-sdk/)); TypeScript `@anthropic-ai/claude-agent-sdk` 0.3.290 ([npm](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)). "Both the TypeScript and Python SDKs bundle a native Claude Code binary" ([quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)).
- What it is: "the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript" ([overview](https://code.claude.com/docs/en/agent-sdk/overview)). To use the loop from another language, run the CLI with `-p` and `--output-format json`.
- Providers: `CLAUDE_CODE_USE_BEDROCK=1`, `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` (plus `ANTHROPIC_AWS_WORKSPACE_ID`), `CLAUDE_CODE_USE_VERTEX=1`, `CLAUDE_CODE_USE_FOUNDRY=1` ([quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)).

Minimal agent loop (verbatim, Python):

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],  # Auto-approve these tools
            permission_mode="acceptEdits",  # Auto-approve file edits
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)  # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


asyncio.run(main())
```

Custom tools (verbatim, Python): define with `@tool`, wrap in an in-process MCP server, pass it in `mcp_servers`, and allow `mcp__{server_name}__{tool_name}` ([custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools)).

```python
from typing import Annotated, Any
import httpx
from claude_agent_sdk import tool, create_sdk_mcp_server


# Define a tool: name, description, input schema, handler
@tool(
    "get_temperature",
    "Get the current temperature at a location",
    {
        "latitude": Annotated[float, "Latitude coordinate"],
        "longitude": Annotated[float, "Longitude coordinate"],
    },
)
async def get_temperature(args: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "current": "temperature_2m",
                "temperature_unit": "fahrenheit",
            },
        )
        data = response.json()

    # Return a content array - Claude sees this as the tool result
    return {
        "content": [
            {
                "type": "text",
                "text": f"Temperature: {data['current']['temperature_2m']}°F",
            }
        ]
    }


# Wrap the tool in an in-process MCP server
weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_temperature],
)
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        allowed_tools=["mcp__weather__get_temperature"],
    )

    async for message in query(
        prompt="What's the temperature in San Francisco?",
        options=options,
    ):
        # ResultMessage is the final message after all tool calls complete
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

Useful `ClaudeAgentOptions` fields (Python names; TypeScript uses camelCase such as `maxTurns`, `maxBudgetUsd`, `outputFormat`) ([Python reference](https://code.claude.com/docs/en/agent-sdk/python), [TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript)): `allowed_tools`, `disallowed_tools`, `tools`, `permission_mode`, `can_use_tool` (approval callback), `hooks` (Python callbacks via `HookMatcher`), `mcp_servers`, `strict_mcp_config`, `max_turns`, `max_budget_usd`, `model`, `fallback_model`, `effort`, `output_format` (`{"type": "json_schema", "schema": {...}}`, result in `ResultMessage.structured_output`), `system_prompt`, `setting_sources` (`[]` disables user, project and local settings), `agents`, `skills`, `plugins`, `sandbox`, `session_store`, `task_budget`, `cwd`, `env`. In TypeScript, "If you omit [`permissionMode`], the session can start in auto mode."

Approvals: `can_use_tool` "pauses execution until you return a response". For waits longer than the process can live, the docs point to a `PreToolUse` hook returning `defer` ([user input](https://code.claude.com/docs/en/agent-sdk/user-input)).

Hosting: "1 GiB RAM, 5 GiB disk, and 1 CPU per agent is a reasonable starting point"; transcripts live on local disk, so persist them with a `SessionStore` if a session must survive a restart ([hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Relevant for Cloud Run.

Rules to respect ([overview](https://code.claude.com/docs/en/agent-sdk/overview)):

- "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK." Use API keys for a product.
- Branding: allowed "Claude Agent", "Claude" inside an Agents menu, "{YourAgentName} Powered by Claude". Not permitted: "Claude Code" or "Claude Code Agent", or visuals that mimic Claude Code.

## Claude API facts

### Current models ([models overview](https://platform.claude.com/docs/en/models/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing))

Prices are USD per million tokens.

| Model | Claude API ID | Input | Output | Cache read | 5m / 1h cache write | Batch in / out | Context | Max output | Default effort |
|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | $10 | $50 | $0.25 | $12.50 / $20 | $5 / $25 | 1M | 128K | `high` |
| Claude Opus 5.5 | `claude-opus-5-5` | $4 | $20 | $0.20 | $5 / $8 | $2 / $10 | 1M | 128K | `medium` |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 | $10 | $0.20 | $2.50 / $4 | $1 / $5 | 1M | 128K | `high` |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` (alias `claude-haiku-4-5`) | $1 | $5 | $0.10 | $1.25 / $2 | $0.50 / $2.50 | 200K | 64K | not supported |

- The docs say: "If you're unsure which model to use, start with Claude Opus 5.5".
- Google Cloud IDs match the Claude API IDs for the 5.x models (`claude-opus-5-5`); Haiku is `claude-haiku-4-5@20251001`. Bedrock IDs add `anthropic.` (for example `anthropic.claude-opus-5-5`).
- Still available as legacy: Fable 5, Opus 5 ($5 / $25), Opus 4.8, 4.7, 4.6, 4.5 ($5 / $25), Sonnet 5 ($2 / $10), Sonnet 4.6 ($3 / $15). Sonnet 4.5 is deprecated and retires on the Claude API on 2026-11-30 ([deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)).
- Haiku 4.5 is "Active", retirement "Not sooner than October 15, 2026"; Anthropic gives "at least 60 days' notice before model retirement", and no notice had been given as of 2026-10-06, so it should stay available through the hackathon (inference) ([deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)).
- Opus 5.5 news: "Claude Sonnet 5.5 and Claude Haiku 5.5 will follow in the coming weeks" ([news](https://www.anthropic.com/news/claude-opus-5-5)). Sonnet 5.5 shipped on 2026-09-28; Haiku 5.5 had no release note by 2026-10-06.
- Claude 4.7 and later use a tokenizer that "produces approximately 30% more tokens for the same text" ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
- Claude Code aliases on the Claude API: `opus` is Opus 5.5, `sonnet` is Sonnet 5.5, `fable` is Fable 5.1, `best` is the Fable model where available, `opusplan` uses Opus to plan and Sonnet to execute ([model config](https://code.claude.com/docs/en/model-config)).

Breaking API behavior on the newest models ([release notes 2026-09-22](https://platform.claude.com/docs/en/release-notes/overview#september-22-2026), [2026-09-28](https://platform.claude.com/docs/en/release-notes/overview#september-28-2026), [2026-09-01](https://platform.claude.com/docs/en/release-notes/overview#september-1-2026)):

- Opus 5.5: thinking cannot be disabled; `thinking: {"type": "disabled"}` and `{"type": "enabled", ...}` return 400. Control depth with effort.
- Opus 5.5, Sonnet 5.5, Fable 5.1: `tool_choice` types `any` and `tool` return 400. Use `auto` with strict tool use, or structured outputs.
- Sonnet 5.5: `thinking: {"type": "disabled"}` returns 400; to turn off up-front thinking, send `thinking: {"type": "between_tools"}` instead, at `high` effort or below.
- Sonnet 5 and Opus 4.7 and later: non-default `temperature`, `top_p`, `top_k` return 400 ([release notes 2026-06-30](https://platform.claude.com/docs/en/release-notes/overview#june-30-2026), [2026-05-28](https://platform.claude.com/docs/en/release-notes/overview#may-28-2026)).
- Fable 5.1 and Opus 5.5 run "preserved thinking": for accounts created on or after 2026-08-31, editing earlier history before a replayed thinking block can return 400 ([news](https://www.anthropic.com/news/claude-opus-5-5)). Keep the message history append-only.
- Safety classifiers can end a request with `stop_reason: "refusal"`; check `stop_reason` before reading content ([release notes 2026-06-09](https://platform.claude.com/docs/en/release-notes/overview#june-9-2026)).

### Endpoint, keys, env vars

- Endpoint `POST https://api.anthropic.com/v1/messages` with headers `x-api-key: $ANTHROPIC_API_KEY`, `anthropic-version: 2023-06-01`, `content-type: application/json` ([get started](https://platform.claude.com/docs/en/get-started)).
- Keys are created at [Settings > API keys](https://platform.claude.com/settings/keys); the key "starts with `sk-ant-`" and is shown "only once". Key types: personal, service account (for CI), and legacy workspace keys; keys can have an expiration ([get API key](https://platform.claude.com/docs/en/get-api-key)).
- SDKs: `pip install anthropic` (1.11.0 on 2026-09-30, Python 3.10 or later, [PyPI](https://pypi.org/project/anthropic/)); `npm install @anthropic-ai/sdk` (0.131.0, [npm](https://www.npmjs.com/package/@anthropic-ai/sdk)). Python SDK 1.0 (2026-08-20) moved HTTP to `httpx2` and removed `temperature`, `top_p`, `top_k` from Messages methods ([release notes](https://platform.claude.com/docs/en/release-notes/overview#august-20-2026)).
- `ant` CLI: v1.38.0 in the Managed Agents quickstart; Linux tarball from [anthropics/anthropic-cli releases](https://github.com/anthropics/anthropic-cli/releases) ([quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart)).

Environment variables (sources: [env vars](https://code.claude.com/docs/en/env-vars), [model config](https://code.claude.com/docs/en/model-config), [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference), [monitoring](https://code.claude.com/docs/en/monitoring-usage)):

| Variable | Use |
|---|---|
| `ANTHROPIC_API_KEY` | API key (`x-api-key`) for SDKs and Claude Code |
| `ANTHROPIC_AUTH_TOKEN` | value for `Authorization: Bearer` |
| `ANTHROPIC_BASE_URL` | route through a proxy or gateway |
| `ANTHROPIC_CUSTOM_HEADERS` | extra headers, `Name: Value`, newline-separated |
| `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_MODEL` | model for a session; default for new sessions |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`, `_SONNET_MODEL`, `_HAIKU_MODEL`, `_FABLE_MODEL` | what each alias resolves to |
| `CLAUDE_CODE_OAUTH_TOKEN` | subscription token from `claude setup-token` |
| `CLAUDE_CODE_USE_VERTEX`, `ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION` | Google Cloud's Agent Platform |
| `CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION` | Amazon Bedrock |
| `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, `ANTHROPIC_IDENTITY_TOKEN_FILE` or `ANTHROPIC_IDENTITY_TOKEN`, `ANTHROPIC_WORKSPACE_ID`, `ANTHROPIC_PROFILE` | Workload Identity Federation |
| `MCP_TIMEOUT` | MCP server startup timeout, default 30000 ms |
| `BASH_DEFAULT_TIMEOUT_MS` | default Bash tool timeout, default 120000 ms |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_TELEMETRY` | turn off nonessential traffic and telemetry |
| `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT` | export Claude Code metrics and logs with OpenTelemetry |

### Tool use and structured outputs

- Strict tool use: put `"strict": true` on the tool, with `"additionalProperties": false` and `required` in `input_schema` ([strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use)).
- JSON outputs: `output_config: {"format": {"type": "json_schema", "schema": {...}}}`; GA, no beta header; supported on all current models ([structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). The old `output_format` parameter moved to `output_config.format` (2026-01-29 release note).
- SDK tool runner (beta) runs the loop for tools you define: Python `@beta_tool` plus `client.beta.messages.tool_runner(...)` ([tool runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner)). The docs say to use the manual loop instead "When you need human-in-the-loop approval".
- Tool use adds a system prompt of 286 tokens on Opus 5.5 and Sonnet 5.5 ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
- Task budgets (beta header `task-budgets-2026-03-13`): `output_config.task_budget: {"type": "tokens", "total": 64000}`; the model sees a running countdown. Supported on Fable 5.1, Opus 5.5, Sonnet 5.5 and others ([task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets)).
- Advisor tool (beta header `advisor-tool-2026-03-01`): an executor model consults a stronger advisor mid-task ([advisor](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool), [release notes](https://platform.claude.com/docs/en/release-notes/overview#april-9-2026)).

### Prompt caching ([prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [pricing](https://platform.claude.com/docs/en/about-claude/pricing))

- Automatic caching: one top-level `"cache_control": {"type": "ephemeral"}`; add `"ttl": "1h"` for the 1-hour cache. Up to 4 breakpoints per request.
- Multipliers: 5-minute write 1.25x, 1-hour write 2x, read 0.1x of base input (0.05x on Opus 5.5, 0.025x on Fable 5.1).
- Minimum cacheable prompt: 512 tokens on Fable 5.1, Opus 5.5, Opus 5, Sonnet 5.5; 1,024 on Sonnet 5; 4,096 on Haiku 4.5. Shorter prefixes do not cache.
- Rate limits: on most models only `input_tokens` plus `cache_creation_input_tokens` count toward the input-tokens-per-minute limit, so cache reads raise effective throughput ([rate limits](https://platform.claude.com/docs/en/api/rate-limits)).

### Batch, Files, web fetch, web search, code execution, MCP connector

- Message Batches: 50% off input and output; up to 100,000 requests or 256 MB per batch; "most batches completing within 1 hour"; expire after 24 hours; results kept 29 days ([batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing)).
- Files API: out of beta since 2026-08-19 (no `files-api-2025-04-14` header needed); 500 MB per file, 1 TB per organization; optional `expires_in_seconds` from 3,600 to 7,776,000 ([files](https://platform.claude.com/docs/en/build-with-claude/files)). Not on Bedrock or Google Cloud.
- Web fetch: `{"type": "web_fetch_20260318", "name": "web_fetch"}` (latest; `web_fetch_20260209` and later support dynamic filtering). Options `max_uses`, `allowed_domains`, `blocked_domains`, `citations`, `max_content_tokens`, `response_inclusion`. "no additional cost" beyond tokens. Claude "can only fetch URLs that have previously appeared in the conversation" ([web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)).
- Web search: $10 per 1,000 searches; on Google Cloud only the basic tool without dynamic filtering ([web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), [pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
- Code execution: free when the request includes `web_search_20260209` or `web_fetch_20260209` or later; otherwise 1,550 free hours per organization per month, then $0.05 per hour per container ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
- MCP connector: beta header `mcp-client-2025-11-20`; request needs both `mcp_servers` (`{"type": "url", "url": ..., "name": ..., "authorization_token": ...}`) and a `tools` entry `{"type": "mcp_toolset", "mcp_server_name": ...}`. Limits: "only tool calls are currently supported"; the server "must be publicly exposed through HTTP". Not on Bedrock or Google Cloud ([MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)).

### Claude Managed Agents (beta)

From the [overview](https://platform.claude.com/docs/en/managed-agents/overview), [quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) and [pricing](https://platform.claude.com/docs/en/about-claude/pricing):

- "Pre-built, configurable agent harness that runs in managed infrastructure". All endpoints need the `managed-agents-2026-04-01` beta header (the SDK sets it). Access is "enabled by default for all API accounts".
- Concepts: Agent (model, system prompt, tools, MCP servers, skills), Environment (cloud sandbox or self-hosted), Session, Events (streamed over SSE).
- Built-in toolset `agent_toolset_20260401`: bash, file read/write/edit/glob/grep, web search and fetch, plus MCP servers.
- Pricing: model tokens at normal rates plus "$0.08 per session-hour" of `running` time. No batch discount. Not on partner clouds.
- Controls: permission policies `always_allow`, `always_ask`, `auto` (MCP toolsets default to `always_ask`) ([permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies)); session budgets that pause at `budget_reached` ([budgets](https://platform.claude.com/docs/en/managed-agents/budgets)); outcomes with a rubric grader ([outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes)); webhooks such as `session.status_idled` ([webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks)); cron "scheduled deployments" ([scheduled](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)).
- Rate limits: create endpoints 300 requests per minute, read endpoints 1,200 per minute ([rate limits](https://platform.claude.com/docs/en/api/rate-limits)).
- Not eligible for Zero Data Retention.

Quickstart calls (verbatim, Python):

```python
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-opus-5-5",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```

```python
environment = client.beta.environments.create(
    name="quickstart-env",
    config={
        "type": "cloud",
        "networking": {"type": "limited", "allow_package_managers": True},
    },
)

print(f"Environment ID: {environment.id}")
```

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)

print(f"Session ID: {session.id}")
```

Then stream with `client.beta.sessions.events.stream(session.id)` and send `{"type": "user.message", ...}` events with `client.beta.sessions.events.send(...)`.

### Rate limits and how a new account gets credits

- Usage tiers Start, Build, Scale, plus Custom; monthly spend caps $500, $1,000 and $200,000. "New organizations and organizations with limited usage history may start in the Evaluation tier, with limits below the standard limits" ([rate limits](https://platform.claude.com/docs/en/api/rate-limits)).
- Start tier per model: Opus 5.5, Sonnet 5.5 and Haiku 4.5 each 1,000 requests per minute, 2,000,000 input tokens per minute, 400,000 output tokens per minute; Fable 5.x 1,000 / 500,000 / 100,000 ([rate limits](https://platform.claude.com/docs/en/api/rate-limits)).
- Credits: "New users receive a small amount of free credits to test the API" ([pricing FAQ](https://platform.claude.com/docs/en/about-claude/pricing)). The amount is not stated (unverified). Billing is monthly usage in USD, by credit card for standard accounts.
- Sign up at [platform.claude.com](https://platform.claude.com/) and create a key ([get API key](https://platform.claude.com/docs/en/get-api-key)).
- Subscription route: Claude Pro is $20 per month ($17 per month billed annually) and includes Claude Code ([claude.com/pricing](https://claude.com/pricing)). `claude setup-token` lets CI use that plan, but not for a product offered to others (Agent SDK rule above).
- Students: Claude Builder Club leaders share "resources (like API credits)" with members; Fall 2026 applications ran September 1 to 12 and "The program is closed for Fall 2026" ([Campus programs](https://claude.com/programs/campus)).
- Hackathon-provided Anthropic credits: (unverified; Devpost is blocked here).

## MCP

Current spec revision: `2026-07-28`, released as stable on 2026-07-28 (release candidate on 2026-05-29). The schema sets `LATEST_PROTOCOL_VERSION = "2026-07-28"` ([GitHub releases](https://github.com/modelcontextprotocol/modelcontextprotocol/releases), [schema.ts](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.ts)).

What changed, by revision (from the changelogs in the spec repo):

| Revision | Main changes |
|---|---|
| [2025-03-26](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/changelog.mdx) | Authorization framework "based on OAuth 2.1"; Streamable HTTP replaces HTTP+SSE; JSON-RPC batching; tool annotations (for example read-only or destructive); audio content |
| [2025-06-18](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-06-18/changelog.mdx) | Batching removed; structured tool output; servers are OAuth Resource Servers; RFC 8707 resource indicators; elicitation; resource links; protocol version header |
| [2025-11-25](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/changelog.mdx) | OpenID Connect discovery; icons; incremental scope consent; tool name guidance; URL-mode elicitation; tool calling in sampling; Client ID Metadata Documents; experimental tasks; JSON Schema 2020-12 as default dialect |
| [2026-07-28](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/changelog.mdx) | Stateless: no `initialize` handshake and no `Mcp-Session-Id`; every request carries version and capabilities in `_meta`; new `server/discover`; `subscriptions/listen` replaces the GET stream; Multi Round-Trip Requests replace server-initiated requests; tasks moved to an extension (`io.modelcontextprotocol/tasks`); `ttlMs` and `cacheScope` on list results; deterministic `tools/list` order recommended to "improve LLM prompt cache hit rates"; Roots, Sampling and Logging deprecated; Dynamic Client Registration deprecated in favor of Client ID Metadata Documents |

Governance: on 2025-12-09 Anthropic donated MCP to the Agentic AI Foundation, "a directed fund under the Linux Foundation, co-founded by Anthropic, Block and OpenAI, with support from Google, Microsoft, Amazon Web Services (AWS), Cloudflare, and Bloomberg". The same post cites "more than 10,000 active public MCP servers" and "97M+ monthly SDK downloads across Python and TypeScript", and mentions an official community Registry ([news](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).

SDK versions on 2026-10-06: Python `mcp` 2.3.0 (2026-10-02, [PyPI](https://pypi.org/project/mcp/)); TypeScript v2 packages `@modelcontextprotocol/server`, `/client`, `/core` 2.3.1; the 1.x package `@modelcontextprotocol/sdk` is 1.32.1 ([npm](https://www.npmjs.com/package/@modelcontextprotocol/sdk)). Which SDK versions implement `2026-07-28` was not checked (unverified).

Claude Code support: Claude Code has two MCP client runtimes; "The v2 runtime is the same code on MCP TypeScript SDK 2.0, which adds MCP protocol revision 2026-07-28" ([MCP](https://code.claude.com/docs/en/mcp)). Since v2.1.274 (2026-09-17), Bedrock, Vertex and Foundry installs also default to the v2 client and 2026-07-28 negotiation with HTTP servers ([changelog](https://code.claude.com/docs/en/changelog)).

GitLab MCP server: supports 2025-03-26, 2025-06-18 and 2025-11-25 ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/model_context_protocol/mcp_server.md)); 2026-07-28 support is not listed there (unverified). Claude Code should still connect, since it negotiates older revisions (inference).

Other Anthropic MCP surfaces: the API's MCP connector (above); MCP tunnels for private-network servers (research preview, request access) ([MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview)); MCP servers in Managed Agents; in-process MCP servers in the Agent SDK.

## What Anthropic would be proud to see

This section is our reading of what Anthropic publishes and promotes. Each point links to the source it rests on.

1. A human decides at the risky step. Anthropic's agent framework says humans "should retain control over how their goals are pursued, particularly before high-stakes decisions are made" ([framework](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)). Show it concretely: a `PreToolUse` hook that defers a rollback or deploy until a person approves, or a Managed Agents `always_ask` policy ([hooks](https://code.claude.com/docs/en/hooks), [permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies)). In GitLab, the agent proposes through an MR and approvals still apply, as the Claude GitLab doc stresses.
2. The agent shows its work. The framework cites Claude Code's "real-time to-do checklist" as the model for transparency. Post the plan, evidence and cost (`total_cost_usd`) as an MR or issue note.
3. Least privilege, contained. `--permission-mode dontAsk` with an exact `--allowedTools` list is the documented CI pattern; `bypassPermissions` is for "Isolated containers and VMs only" ([permission modes](https://code.claude.com/docs/en/permission-modes)). Treat MR text and fetched pages as untrusted: GitLab notes prompt scanning is "not available for external agents", and Anthropic warns about web fetch exfiltration ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md), [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)). Anthropic writes about this itself ([sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing), [how we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).
4. No long-lived secrets. Use the keyless Google Cloud's Agent Platform job (GitLab OIDC plus WIF) from the Claude GitLab doc, or Claude API WIF ([GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd), [WIF](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)).
5. Code decides what is true. Ask for `--json-schema` or `output_config.format` output and check it in code; measure with evals ([structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
6. Time-boxed and cost-aware. `--max-turns`, `--max-budget-usd`, task budgets, prompt caching. The Opus 5.5 post says cache reads "make up the majority of agentic and coding work costs" ([news](https://www.anthropic.com/news/claude-opus-5-5), [CLI reference](https://code.claude.com/docs/en/cli-reference)).
7. Current models, used deliberately. Opus 5.5 at an explicit effort for judgment calls, Sonnet 5.5 or Haiku 4.5 for cheap triage subagents, and handling of `stop_reason: "refusal"` ([models](https://platform.claude.com/docs/en/models/overview)).
8. Open standards. MCP (now at the Linux Foundation) and Agent Skills (open standard) rather than one-off glue; GitLab already ships an MCP server ([MCP news](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), [skills](https://www.anthropic.com/news/skills)).
9. Good tools for the agent. Follow [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
10. Correct branding: "{YourAgentName} Powered by Claude", never "Claude Code Agent" ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)).
11. A three-sponsor story that is true: Claude running on Google Cloud, inside GitLab pipelines, the same combination GitLab Duo uses for its defaults ([GitLab doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/gitlab_duo/model_selection.md)). GitLab's case study on claude.com reports "25-50% productivity gains across internal workflows with Claude" ([case study](https://claude.com/customers/gitlab); the page shows no date).

## Moved or broken links

| Old or expected URL | What happens on 2026-10-06 | Use instead |
|---|---|---|
| https://docs.claude.com/ | 301 to https://platform.claude.com/docs | platform.claude.com/docs |
| https://docs.claude.com/en/docs/about-claude/models/overview | 302 to platform.claude.com/docs/en/about-claude/models/overview, which 307s to the next column | https://platform.claude.com/docs/en/models/overview |
| https://platform.claude.com/docs/llms.txt | redirects | https://platform.claude.com/llms.txt |
| https://docs.claude.com/en/docs/claude-code/gitlab-ci-cd | 301 | https://code.claude.com/docs/en/gitlab-ci-cd |
| https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview | 4 redirects | https://code.claude.com/docs/en/agent-sdk/overview |
| https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | 307 to the Opus 5.5 "what's new" page, not a 4.7 page | release notes for 2026-04-16 |
| https://www.anthropic.com/customers/gitlab | redirects | https://claude.com/customers/gitlab |
| https://code.claude.com/docs/en/claude-tag.md (listed in llms.txt) | returns an HTML page, not markdown; canonical is on claude.com | https://claude.com/docs/claude-tag/overview |
| https://gitlab.com/gitlab-org/gitlab/-/issues/573776 | the API reports `web_url` as a work item; closed 2025-12-09 | https://gitlab.com/gitlab-org/gitlab/-/work_items/573776 |
| https://docs.gitlab.com/user/duo_agent_platform/agent_assistant/ (linked from that issue) | its source file `doc/user/duo_agent_platform/agent_assistant.md` is 404 on master; the feature was renamed "External agents" in GitLab 18.6 | https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md |
| https://www.anthropic.com/news/claude-sonnet-5-5 and https://www.anthropic.com/news/claude-fable-5-1 | 404; no news post at these slugs | release notes for 2026-09-28 and 2026-09-01 |
| console.anthropic.com | redirects to platform.claude.com since 2026-01-12 ([release notes](https://platform.claude.com/docs/en/release-notes/overview#january-12-2026)); blocked from this session | https://platform.claude.com |
| Console Workbench | renamed "playground" on 2026-08-18 ([release notes](https://platform.claude.com/docs/en/release-notes/overview#august-18-2026)) | https://platform.claude.com/playground |
| "Vertex AI" | Claude docs now say "Google Cloud's Agent Platform, formerly Vertex AI"; the URL is still `/google-vertex-ai` and the login menu still says "Google Vertex AI"; GitLab docs say "Gemini Enterprise Agent Platform" | https://code.claude.com/docs/en/google-vertex-ai |
| https://claude.ai/install.sh | redirects to https://downloads.claude.ai/claude-code-releases/bootstrap.sh (blocked from this session, so the installer was not tested) | `npm install -g @anthropic-ai/claude-code` as a fallback |

## Blocked

| URL | Error | Attempts |
|---|---|---|
| https://modelcontextprotocol.io/llms.txt | curl: `CONNECT tunnel failed, response 403` | 1 |
| https://modelcontextprotocol.io/specification/versioning | WebFetch: `EGRESS_BLOCKED` ("Access to modelcontextprotocol.io is blocked by the network egress proxy") | 1 (2 on the host); used the GitHub spec repo instead |
| https://docs.anthropic.com/en/docs/claude-code/gitlab-ci-cd | curl: `CONNECT tunnel failed, response 403` | 1; used code.claude.com |
| https://console.anthropic.com/ | curl: `CONNECT tunnel failed, response 403` | 1 |
| https://docs.gitlab.com/user/duo_agent_platform/agents/external/ | curl: `CONNECT tunnel failed, response 403` | 1; used the doc source on gitlab.com |
| https://docs.gitlab.com/user/gitlab_duo/model_selection/ | curl: `CONNECT tunnel failed, response 403` | 1; used the doc source on gitlab.com |
| https://about.gitlab.com/blog/gitlab-18-3-expanding-ai-orchestration-in-software-engineering/ | curl: `CONNECT tunnel failed, response 403` | 1 |
| https://about.gitlab.com/press/releases/ | curl: `CONNECT tunnel failed, response 403` | 1 |
| https://claude.ai/install.sh (redirects to https://downloads.claude.ai/claude-code-releases/bootstrap.sh) | curl: `CONNECT tunnel failed, response 403` | 1 |
| WebSearch tool | "this turn's web search budget is used up (limit: 200 WebSearch calls per turn, shared by every agent in it)" on the first query about GitLab and Anthropic partnership news | 1 |
| devpost.com, web.archive.org | not attempted (known blocked) | 0 |

Gap caused by the search block: 2026 GitLab and Anthropic partnership announcements (press releases, joint blog posts) could not be searched. The Anthropic news list on anthropic.com/news (264 entries read) has no GitLab item, and the claude.com blog index has no GitLab mention. The GitLab ties found are first-party docs: the Claude Code GitLab CI/CD page, GitLab's Claude Code external agent, GitLab Duo's Claude default models, and the claude.com GitLab case study.
