# Ideation brief

Internal input for Part 5 (docs/IDEAS.md). It condenses the research so far. Sources are the files linked in each line; follow them for the primary links.

## The contest in brief

- Event: Life After Code, the GitLab Transcend Hackathon (GitLab calls it Transcend III). Deadline Oct 27, 2026, 13:00 UTC per Devpost (14:00 UTC per GitLab's guide; use the earlier). Judging Oct 28 to Nov 11. Winners about Nov 16. ([RULES.md](../RULES.md))
- Path A, "Start Fresh": "Build a new AI-powered project on GitLab that shows agentic automation of the post-code lifecycle. You create the app, the CI/CD pipeline, and the automation from scratch." ([RULES.md](../RULES.md), search excerpt of Devpost)
- Required: "Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients." A pass/fail gate first checks the project fits the theme and "genuinely uses GitLab AI features". ([RULES.md](../RULES.md))
- Five equally weighted criteria: Technological Implementation (how thoroughly and skilfully it uses GitLab to automate the post-code lifecycle; Google Cloud deployment scores higher), Design (a complete, coherent end-to-end workflow, not a proof of concept), Potential Impact (a credible, specific case for a real problem for a real audience), Innovation (novel concept, inventive use of agentic automation), Presentation (video shows the automation running end to end; what problem, who it is for, why it matters). ([RULES.md](../RULES.md))
- Bonus: up to 0.2 points once after judging for a live Google Cloud deployment with the deploy code in the public GitLab repo.
- Submission: public GitLab project with an MIT licence visible in About, text description, visible CI/CD pipeline history, video under 3 minutes on YouTube, no copyrighted music.
- Prizes ($45,000, 10 winners): Path A Assisted $4,000, Path A Supervised $4,000, Path A Hands-off $5,000 (same three for Path B); Most Stages Covered $5,000, one per path ("the Projects from each Path which touch the most post-code DevSecOps lifecycle stages in the most creative way"; "touching the stage counts"); Most Creative $4,000 (either path); Most Environmentally Impactful $5,000 (opt-in, needs Software Carbon Intensity numbers).
- Autonomy levels (Devpost, search excerpts):
  - Assisted: "You approve every step."
  - Supervised: "You approve the outcome, not the individual steps... You review the end result, not every individual action." Example: agents review, fix a failing pipeline, remediate a finding, deploy to staging; "You get a summary and approve the production deployment."
  - Hands-off: "You set the intent and walk away. A full loop from code to production with no human in the middle."
- Stages named on the Devpost page: plan, create, verify, package, secure, release, configure, monitor, govern.
- GitLab's internal theme for October (epic #40): "Hands Off. How far can your agents go without you?" ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md))

## How GitLab judged the last edition (June 2026, primary source)

From GitLab's own status update ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md), team-task#1137):
- 1,576 registered, 318 submissions, 265 judged.
- Each entry was packaged as "write-up plus an evidence bundle pulled from the actual repo code" and pre-scored by three models (Opus 4.8, GPT 5.5, Gemini 3.1). Humans picked every winner.
- "69 built pre-merge impact review, 36 built onboarding aids", but "Five of the eight winners came from those rare tiers" (one-of-a-kind or two-of-a-kind concepts).
- "110 of 265 had silent or missing demos." A clear, narrated demo is a real edge.
- June winners: Sankofa, Stayed Shipped (Technological Implementation); Carver, Marshal (Design); CrossCut, OrbitWeaver (Impact); Transcend, Universal Agent OS (Idea).

## The judges' baseline

GitLab's reference project hello-world-showcase, built by judge and event lead Missy Davies, already runs: issue assigned to the Duo Developer flow, draft MR, CI arms auto-merge, Duo Code Review, critical-finding gate, tests and scans, Cloud Run staging, smoke test, production, release, comment on the issue. About 15 minutes, one human action. It uses a JSON key for Google Cloud, not keyless auth. Matching this loop is the floor, not a differentiator. ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md))

## Past winners (2025 and 2026), short

- GitLab AI Hackathon, Feb to Mar 2026 (same Duo platform, Google Cloud and Anthropic co-sponsors, about 7,000 developers, $65,000): Grand Prize LORE (organizational memory: eight agents, a router, a knowledge graph, a dashboard, carbon tracking, 43 tests); Google Cloud prize Gitdefender (finds and fixes security issues in code review); Anthropic prize GraphDev (maps code relationships and change impact). (search excerpt of GitLab's winners post)
- Google ADK Hackathon 2025: all 8 winners were multi-agent with named roles and an architecture diagram; most had generate, check and retry loops; 6 of 8 only suggested; GreenOps (APAC) had the shape we want: agent recommends, person approves, plain code checks safety; solo builders won 4 of 8. ([google-adk-hackathon-2025.md](winners/google-adk-hackathon-2025.md))
- Google Cloud Run Hackathon 2025: grand prize to a consumer multi-agent app; the agent-category winner drafted, self-checked, then waited for a human "Approve"; winners collected easy bonus points; small teams. ([google-cloud-run-hackathon.md](winners/google-cloud-run-hackathon.md))
- Anthropic Claude Code hackathons 2026: winners served named, real people (medical residents, repair technicians, students, tradespeople), wrote specs and evals early, and used verifier or adversarial agents. MCP's 1st Birthday Best Overall went to a human-in-the-loop safety layer. ([_discovery_anthropic.md](winners/_discovery_anthropic.md))
- Alex's own Blackbox won DataHub's Grand Prize: rigorous evidence gates, but little human element.

## The current field (as of Oct 6, day 2)

Crowded, avoid as the main idea ([code_hosts.md](field/code_hosts.md), [social.md](field/social.md)):
1. Post-merge release gatekeepers (scan, test, deploy, health check, ship, hold or roll back). 4 of 7 known October entries, and the judges' own reference project.
2. Evidence receipts and tamper-evident attestation of agent actions.
3. Security review and auto-fix on merge requests (132 projects in the Feb hackathon's AI Catalog by keyword; a Feb winner).
4. Pre-merge blast radius or "what could this break" (69 teams in June).
5. Code review agents (95 in Feb), issue triage (81), carbon footprint of pipelines (73), CI failure fixers (56), incident root cause from deploy to MR (56).
6. "All nine stages" multi-agent meshes with ten agents.
7. Onboarding aids (36 in June).
8. Proof of Fix (another entrant): "an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears."

Open, not anyone's main idea yet: on-call alert handling and the human handoff at night (0 catalog items); user feedback and support tickets flowing back into issues after release; feature flags and progressive rollout (the configure stage); database migration safety; dependency upgrades; flaky tests; compliance evidence for auditors; package and registry hygiene.

## Hard exclusions

- Nothing from Alex's earlier ideas: Second Look, creeks, citizen science, FHIR.
- Not Proof of Fix.
- No release-notes generators, no CI failure fixers, no generic incident chatbots, no dashboards as the main idea.

## What Alex wants

- Make a person feel something: an on-call engineer who gets to sleep, a developer who feels trusted, a user who feels heard.
- The model chooses where to look, code decides what is true, a human controls when the agent acts on anything that matters.
- Verification only as much as the product needs. Novelty and a human element over rigor.

## Building blocks and limits (verified so far)

- Duo Agent Platform flows are YAML (components, prompts, routers), each run is a CI pipeline, flows cannot read CI/CD variables, flows reach the network only through an allowlist. Triggers: mention, assign, assign reviewer, pipeline events, merge request events (created, marked ready, approved, merge conflict), work item. Only a human action can fire a trigger, so a flow cannot start another flow; other events can start a flow through the REST API. Skills live in `skills/<name>/SKILL.md`. ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md))
- Claude Code runs in GitLab CI headless (`claude -p`, `--json-schema`, `--max-turns`, `--max-budget-usd`). A `PreToolUse` hook can return "defer" to pause a run at a tool call so a human can approve, and `--resume` continues it. ([anthropic.md](sponsors/anthropic.md))
- Workspace: GitLab provisions a public subgroup and a `showcase` project per entrant with the Developer role plus an "AI member role". In the staff test project only Maintainers can push or merge to `main`, and creating flows may need Maintainer. This is the biggest unknown. ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md))
- New GitLab accounts cannot run CI on shared runners without a credit card on file (June lesson).
- Cloud Run with min instances 0 stays near zero cost; keyless auth from GitLab CI to Google Cloud uses Workload Identity Federation with `id_tokens`.

## Build window

Alex is busy with another hackathon until Oct 23 and works from his phone. The build is done by Claude Code and Codex with Alex copying messages between them. Build complete by Oct 24; video and submission Oct 24 to 26.
