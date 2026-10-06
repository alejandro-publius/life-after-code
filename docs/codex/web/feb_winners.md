# GitLab AI Hackathon winners, February to March 2026 edition

These are plain-text research notes. Quotations appear in quotation marks. Other descriptions are paraphrases. Long dashes in source names or short quotations are normalized to " - ". Prize names, project names and technology tags are factual labels. No winner code was copied.

## Sources and time

Core source pages were reread at 2026-10-06T02:15:52.218Z UTC through the browser:
- Event: https://gitlab.devpost.com/
- Rules: https://gitlab.devpost.com/rules
- Winner gallery: https://gitlab.devpost.com/project-gallery
- GitLab sponsor write-up: https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/

Official winner update: https://gitlab.devpost.com/updates/41783-meet-the-winners
Read time: 2026-10-06T02:17:26.763Z UTC.

The sponsor write-up also returned HTTP 200 directly at 2026-10-06T02:13:35.116397Z. Direct Python fetches of the event and all 19 software pages returned HTTP 403, including the attempted ?amp=1 variants. The browser successfully read all 19 software pages. Each entry below records its own browser read time. Video identity comes from the embedded iframe URL on that software page. YouTube embeds were throttled by the browser, so a video link is not a claim that the video was watched.

## Edition and dates

This event opened February 9 and closed March 25, 2026. The official rules place judging March 30 to April 17 and the winner announcement on or around April 22, 2026. The sponsor blog says it was published April 22, 2026. Calling this the February hackathon is shorthand for its start date. It is separate from the June Transcend edition and the current October Life After Code event.

## Every prize

The event overview supplies amounts and swag points; the official winner update and each software page supply winners. Amounts are USD per winner. The amounts total $65,000 across 19 winning projects.

| Exact category label from event overview | Cash per winner | Winners | Swag points per winner |
| --- | ---: | --- | ---: |
| Grand Prize | $15,000 | LORE | 1000 |
| Most Technically Impressive | $5,000 | Time-Traveler | 1000 |
| Most Impactful | $5,000 | RedAgent | 1000 |
| Easiest to Use | $5,000 | Launch Control | 1000 |
| Honorable Mention | $500 | SecurityMonkey; stregent; Compliance Sentinel; Carbon Tracker; RepoWarden; MR Compliance Auditor | 320 |
| Sustainable Design Bonus | $500 | BugFlow; DELTA Cyber Reasoning System; CarbonLint; TFGuardian | 320 |
| Most Impactful on GitLab & Google - Grand Prize | $10,000 | Gitdefender | 500 |
| Most impactful on GitLab & Google Runner Up | $3,500 | Aegis | 500 |
| Most Impactful on GitLab & Anthropic- Grand Prize | $10,000 | GraphDev | 500 |
| Most Impactful on GitLab & Anthropic- Runner Up | $3,500 | DocSync | 500 |
| Green Agent Prize | $3,000 | GreenPipe | 500 |

## GitLab's explanation, paraphrased

Source for this section: https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/
Read time: 2026-10-06T02:15:52.218Z UTC. These are the sponsor author's explanations, not full scoring sheets.

| Project | Sponsor emphasis |
| --- | --- |
| LORE | Retained engineering knowledge, complete product, 43 tests. |
| Gitdefender | Security discovery, repair and review without developer intervention. |
| Aegis | Explained decisions and production-ready Google Cloud deployment. |
| GraphDev | Visible change impact; alignment with GitLab's knowledge graph. |
| DocSync | Three-agent repair with human escalation for uncertainty. |
| Time-Traveler | Real migration rehearsals, data and Google Cloud deployment. |
| RedAgent | Verification of AI security findings before developer action. |
| Launch Control | Polished user experience, infrastructure and sustainability. |
| GreenPipe | Pipeline carbon reports. |
| BugFlow | Multiple repairs from one bug report. |
| DELTA Cyber Reasoning System | Automated security fuzzing. |
| CarbonLint | Energy-aware code analysis. |
| TFGuardian | Carbon analysis; substantial cost reduction. |
| SecurityMonkey | Measured scanner performance using known injected vulnerabilities. |
| stregent | Investigation and repairs through a phone. |
| Compliance Sentinel | Compliance scoring and merge blocking. |
| Carbon Tracker | Per-job carbon accounting and optimization guidance. |
| RepoWarden | Capturing why code exists. |
| MR Compliance Auditor | SOC 2 evidence and live compliance tracking. |

One exact short quote, attributed by GitLab to Anthropic judge April Guo about LORE: "This feels like a product, not a hackathon project."

## Every winner's software page

The following summaries and Built With tags come from entrants' own Devpost pages. They describe submitted capabilities; this research did not execute or audit the projects. Carbon savings, model accuracy and test counts remain entrant or sponsor claims unless explicitly identified above.

### LORE - Living Organizational Record Engine

Source: https://devpost.com/software/lore-living-organizational-record-engine
Read time: 2026-10-06T02:14:49.721Z UTC

What it does (paraphrase): Keeps decisions from issues, reviews and merges as reusable memory; checks later changes against earlier decisions and helps new engineers onboard.

Built With labels: `agent`, `anthropic`, `ci/cd`, `claude`, `duo`, `gitlab`, `mermaid.js`, `pages`, `platform`, `python`.

Video: https://www.youtube.com/watch?v=LLC6875SEKw

### Gitdefender

Source: https://devpost.com/software/gitdefender
Read time: 2026-10-06T02:14:50.497Z UTC

What it does (paraphrase): Ranks and reviews merge requests for OSS maintainers using contribution signals, learned heuristics and code context, then supports review and merge decisions.

Built With labels: `adaptive-random-forest`, `claude-(via-ai-gateway)`, `cloud-sql-(postgres)`, `docker`, `fastapi`, `gitlab-custom-flows`, `gitlab-custom-ide-agents`, `gitlab-duo-agent-platform`, `gitlab-graphql-api`, `google-cloud`, `google-cloud-run`, `python`, `river`, `terraform`.

Video: https://www.youtube.com/watch?v=6PBTyVam0sU

### Aegis

Source: https://devpost.com/software/aegis-2m1oq0
Read time: 2026-10-06T02:14:51.087Z UTC

What it does (paraphrase): Combines seven triggered agents for security, dependencies, compliance, likely pipeline failure and reviewer ownership into an explained release confidence score.

Built With labels: `artifact-registry`, `bigquery`, `claude-(anthropic)`, `cloud-storage`, `docker`, `fastapi`, `framermotion`, `gitlab-duo-agent-platform`, `gke`, `google-cloud-(vertex-ai`, `pub/sub`, `python`, `react`, `scikit-learn`, `secret-manager)`, `shap`, `tailwind-css`, `terraform`, `typescript`, `vite`, `xgboost`.

Video: https://www.youtube.com/watch?v=XhKkh3-5fqY

### GraphDev

Source: https://devpost.com/software/graphdev
Read time: 2026-10-06T02:14:51.649Z UTC

What it does (paraphrase): Builds a semantic dependency graph, finds changed and indirectly affected code, posts merge request impact reports and offers an interactive architecture view.

Built With labels: `anthropic-claude`, `fastapi`, `fly.io`, `gitlab`, `gitlab-ai-gateway`, `gitlab-duo-agent-platform`, `hdbscan`, `next.js`, `numpy`, `openai-api`, `python`, `react`, `scikit-learn`, `shadcn/ui`, `sqlite`, `sqlmodel`, `tailwind-css`, `three.js`, `tree-sitter`, `typescript`, `umap`, `zustand`.

Video: https://www.youtube.com/watch?v=s3d6DrzzuA4

### DocSync

Source: https://devpost.com/software/pipeheal
Read time: 2026-10-06T02:14:52.225Z UTC

What it does (paraphrase): Chains Detector, Writer and Reviewer after merges to find stale documentation. Confident corrections become merge requests; uncertain cases become issues.

Built With labels: `duo`, `express.js`, `flow`, `gitlab`, `javascript`.

Video: https://www.youtube.com/watch?v=UbaGM_jp4Yo

### Time-Traveler

Source: https://devpost.com/software/time-traveler-w3cxp0
Read time: 2026-10-06T02:14:52.923Z UTC

What it does (paraphrase): Audits proposed SQL migrations, prepares rollback SQL, deploys isolated Docker previews with seed data, runs smoke tests, and asks before production deployment.

Built With labels: `bash`, `docker`, `fastapi`, `gitlab-ai-catalog`, `gitlab-duo-agent-platform`, `gitlab-duo-chat`, `gitlab-rest-api`, `gitlab.com`, `google-cloud-platform-(gcp)`, `javascript`, `postgresql`, `python`, `sql`, `yaml`.

Video: https://www.youtube.com/watch?v=P1qz01YiME4

### RedAgent

Source: https://devpost.com/software/redagent
Read time: 2026-10-06T02:14:53.583Z UTC

What it does (paraphrase): Intercepts an agent's tool results and introduces controlled attacks to test prompt injection, false data trust, state corruption and privilege escalation; files confirmed failures.

Built With labels: `claude`, `css`, `gitlab`, `gitlab-duo`, `javascript`, `python`, `tsx`, `typescript`.

Video: https://www.youtube.com/watch?v=9Kb1JsBs7ZM

### Launch Control

Source: https://devpost.com/software/launch-control-bgp8az
Read time: 2026-10-06T02:14:54.139Z UTC

What it does (paraphrase): Chains four agents to gather release evidence, apply security and compliance policy, and post a release verdict with blockers and remediation issues.

Built With labels: `api`, `duo`, `express.js`, `framer`, `gitlab`, `motion`, `node.js`, `react`, `typescript`, `vite`, `workflow`, `yaml`, `zod`.

Video: https://www.youtube.com/watch?v=b3Yy3hIO30E

### GreenPipe

Source: https://devpost.com/software/greenpipe
Read time: 2026-10-06T02:14:54.680Z UTC

What it does (paraphrase): Estimates pipeline carbon using runner region and energy assumptions; posts job breakdowns, regional comparisons and suggestions on merge requests.

Built With labels: `anthropic`, `azure-1.185`, `carbon`, `claude`, `eia`, `eia-egrid-for-the-us`, `entso-e`, `gcp-1.1`, `gitlab`, `iea`, `iso/iec`, `yaml`.

Video: https://www.youtube.com/watch?v=jKHOzhY7-BY

### BugFlow: AI Regression Detective & CI Optimizer

Source: https://devpost.com/software/bugflow-ai-regression-detective-ci-optimizer
Read time: 2026-10-06T02:14:55.272Z UTC

What it does (paraphrase): Tracks a reported regression to its source change, searches for related bugs, generates fixes and regression tests; a separate flow reduces wasted CI work.

Built With labels: `ci/cd`, `claude`, `gitlab`, `go`, `javascript`, `python`, `yaml`.

Video: https://www.youtube.com/watch?v=Ae6xQecySV8

### DELTA Cyber Reasoning System

Source: https://devpost.com/software/delta-cyber-reasoning-system
Read time: 2026-10-06T02:14:55.829Z UTC

What it does (paraphrase): Analyzes changed C/C++ code, generates libFuzzer harnesses, runs sanitizer-backed fuzzing, reproduces crashes and posts patches plus security reports.

Built With labels: `claude`, `duo-agent`, `duo-flow`, `gitlab`, `libfuzzer`, `python`.

Video: https://www.youtube.com/watch?v=-3GzUdy-cJQ

### CarbonLint

Source: https://devpost.com/software/carbonlint
Read time: 2026-10-06T02:14:56.408Z UTC

What it does (paraphrase): Audits CI configuration and job data for wasted compute, scores sustainability, suggests validated YAML changes and can open an optimization merge request.

Built With labels: `ai-catalog`, `ci/cd`, `duo-agent`, `gitlab`, `yaml`.

Video: https://www.youtube.com/watch?v=SPiKza5wHeQ

### TFGuardian

Source: https://devpost.com/software/tfguardian
Read time: 2026-10-06T02:14:56.962Z UTC

What it does (paraphrase): Coordinates five Terraform reviewers for dependencies, security, cost, carbon and architectural governance, with CLI evidence and a live review dashboard.

Built With labels: `checkov`, `claude-(anthropic)`, `fastapi`, `gitlab-duo-agent-platform`, `gitleaks`, `go`, `google-cloud-run`, `infracost`, `python`, `react`, `terraform`, `tfsec`, `workload-identity-federation`.

Video: https://www.youtube.com/watch?v=TACASbXfytM

### SecurityMonkey

Source: https://devpost.com/software/securitymonkey
Read time: 2026-10-06T02:14:57.574Z UTC

What it does (paraphrase): Tests scanner coverage by injecting known weaknesses into a test branch, audits project policy, triages actual findings and checks remediation.

Built With labels: `git`, `gitlabs`, `yaml`.

Video: https://www.youtube.com/watch?v=yXT84dTgT94

### stregent

Source: https://devpost.com/software/stregent
Read time: 2026-10-06T02:14:58.244Z UTC

What it does (paraphrase): Sends pipeline-failure notifications to WhatsApp, investigates through MCP tools, invokes a fixing agent, and merges after a person's request.

Built With labels: `gitlab`, `mcp`, `python`, `typescript`.

Video: https://www.youtube.com/watch?v=HRvG3QXwrgc

### Compliance Sentinel  -  Autonomous DevSecOps Governance Agent

Source: https://devpost.com/software/compliance-sentinel-autonomous-devsecops-governance
Read time: 2026-10-06T02:14:58.981Z UTC

What it does (paraphrase): Applies SOC 2, HIPAA, PCI-DSS and GDPR policy to merge requests, scores findings, creates repair requests and provides cloud-backed compliance analytics.

Built With labels: `agent`, `bigquery`, `claude`, `duo`, `fastmcp`, `functions`, `gitlab`, `google`, `looker`, `mcp`, `mermaid`, `node.js`, `platform`, `python`, `studio`, `yaml`.

Video: https://www.youtube.com/watch?v=jFLsVCluqQw

### Carbon Tracker

Source: https://devpost.com/software/carbon-tracker-ij25kf
Read time: 2026-10-06T02:14:59.551Z UTC

What it does (paraphrase): Fetches CI job data, estimates emissions from explicit power and intensity assumptions, identifies waste and posts a sustainability report.

Built With labels: `anthropic-claude`, `gitlab-api`, `gitlab-duo-agent-platform`, `gitlab-flows`, `markdown`, `yaml`.

Video: https://www.youtube.com/watch?v=rqPu8VN6S_c

### RepoWarden

Source: https://devpost.com/software/docuguard
Read time: 2026-10-06T02:15:00.088Z UTC

What it does (paraphrase): Extracts change intent, contracts, decisions and dangers into a SPEC directory, then uses that record for reviews, documentation, audits and onboarding.

Built With labels: `anthropic-claude`, `gitlab`, `gitlab-ci/cd`, `gitlab-duo-agent-platform`, `markdown`, `restapi`, `yaml`.

Video: https://www.youtube.com/watch?v=QAa-et4K2YQ

### MR Compliance Auditor

Source: https://devpost.com/software/mr-compliance-auditor
Read time: 2026-10-06T02:15:00.646Z UTC

What it does (paraphrase): Collects merge request authorization, implementation, tests and review evidence; maps it to SOC 2 controls and follows scores through cloud dashboards and alerts.

Built With labels: `claude-sonnet-4.6-(anthropic)`, `flask`, `gitlab-duo-agent-platform`, `gitlab-graphql-api`, `gitlab-rest-api`, `google-bigquery`, `google-cloud-run`, `google-cloud-scheduler`, `google-pub/sub`, `looker-studio`, `python`, `yaml`.

Video: https://www.youtube.com/watch?v=r3jD0Z23AQU

## Differences and limits

- Time-Traveler's sponsor summary describes five agents connected by a bridge; the entrant's current software page lists eight custom agents. The submitted five-step orchestration flow is distinct from the broader eight-agent set. Treat the counts as referring to different descriptions, not a verified execution trace. Sources: sponsor blog above and https://devpost.com/software/time-traveler-w3cxp0.
- Gitdefender's sponsor blurb emphasizes security repair, while its current software page focuses on OSS maintainer triage, reputation signals and review guidance. Both descriptions are recorded separately rather than silently substituted.
- DocSync's page uses the legacy slug /pipeheal; RepoWarden's page uses /docuguard. The visible project titles and awards confirm their identity.
- Several Built With fields split product names into unusual tags. Those labels are preserved rather than repaired into an invented stack. For example Aegis lists `google-cloud-(vertex-ai` and `secret-manager)` separately.
- Winner project descriptions are primary sources for what entrants claimed, not independent evidence of production use or universal correctness.
- The phone workflow of stregent, memory-based prevention of LORE and RepoWarden, four-agent release gate of Launch Control, migration previews of Time-Traveler, and regression tests of BugFlow already appeared among winners. An originality claim needs a concrete difference from these systems.
