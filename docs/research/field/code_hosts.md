# Field scan: code hosts (GitLab and GitHub)

Compiled 2026-10-06, between about 01:05 and 01:35 UTC (day 2 of the build window), for Alex Velazquez. Goal: find what other Life After Code entrants are building, so our idea is not crowded.

Read this first:

- **The official GitLab group is still almost empty.** At 01:17 UTC on Oct 6, [gitlab-ai-hackathon/transcend-october-2026](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) held 3 subgroups and 2 projects, all GitLab staff test workspaces with the default README ([subgroups API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/subgroups), [projects API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true)). Approvals are manual, so this will fill up over the next days. Re-run those two API links daily.
- **Entrants are building in their own namespaces.** I found 4 entries with code (3 on GitLab, 1 on GitHub), 2 public planning issues on GitHub, and 6 GitLab onboarding requests that name the hackathon. That is a small, early sample.
- **The most crowded space already:** a post-merge "release gatekeeper" that walks a change through review, scans, tests, deploy and a health check, then decides ship, hold or roll back. 4 of the 7 known ideas are this, and the judges' own reference project does it too.
- **Alex's own repo is public.** [alejandro-publius/life-after-code](https://github.com/alejandro-publius/life-after-code) is the first result of a GitHub search for "Life After Code" ([search](https://github.com/search?q=%22Life+After+Code%22&type=repositories&s=updated&o=desc)). Anyone can read our research and idea notes. Consider making it private until submission, or keep idea docs out of it.

## Searched

Times are UTC on 2026-10-06. "Relevant" means the result is an October 2026 Life After Code entry, plan or signal.

### GitLab, official hackathon group (REST API, no token)

| Query or URL | Result |
|---|---|
| [groups/gitlab-ai-hackathon%2Ftranscend-october-2026](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026) | Group exists, public, created 2026-09-17. Description: "GitLab Transcend III hackathon (October 2026) - showcase track. One subgroup per participant is provisioned under here by contributors.gitlab.com." |
| [.../subgroups?per_page=100](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/subgroups?per_page=100) (01:08 and 01:17) | 3 subgroups: [1933526 leetickett](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/1933526), [12687636 leetickett-gitlab](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/12687636), [8659557 missy-davies](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/8659557). All created Oct 2. |
| [.../projects?include_subgroups=true](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true&per_page=100) | 2 projects (leetickett-gitlab has none visible). |
| [.../descendant_groups](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/descendant_groups) | 3 |
| [missy-davies/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase): tree, commits, issues, MRs, pipelines | 1 file (default README), 1 commit, 1 issue (onboarding, closed by missy-davies on Oct 5), 0 MRs, 0 pipelines. No flow or agent files. |
| [leetickett/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase): same checks | 1 file (default README), 1 commit, 1 open onboarding issue, 0 MRs, 0 pipelines. No flow or agent files. |
| [Onboarding issue #1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) | Template welcome text. Mentions optional per-workspace observability and Discord `#transcend-hackathon`. Notes API needs a token (401). |

### GitLab, past editions (counts only)

| Group | Projects visible | Note |
|---|---|---|
| [gitlab-ai-hackathon](https://gitlab.com/gitlab-ai-hackathon) (root) | 345 in all, 7 direct subgroups, 10 descendant groups | [projects API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon/projects?include_subgroups=true&per_page=1) |
| [transcend](https://gitlab.com/groups/gitlab-ai-hackathon/transcend) (June 2026, Orbit edition) | 312 | One project per entrant directly in the group, no subgroups |
| [gitlab-devsecops-flow-hackathon](https://gitlab.com/groups/gitlab-ai-hackathon/gitlab-devsecops-flow-hackathon) (created 2026-03-16) | 0 | Empty or private |
| participants-test-lee / participants-test-mattias / project-templates / test | 2 / 24 / 1 / 1 | Staff test groups |
| [gitlab-community/community-projects/2026-02-ai-hackathon](https://gitlab.com/groups/gitlab-community/community-projects/2026-02-ai-hackathon) (Feb to Mar 2026 AI Hackathon, moved out of `gitlab-ai-hackathon/participants`) | 1,788 | Found by following the redirect of [participants/621485](https://gitlab.com/api/v4/projects/gitlab-ai-hackathon%2Fparticipants%2F621485) |

### GitLab, public project search (API equivalent of Explore)

All via `https://gitlab.com/api/v4/projects?search=<term>`. Counts are the API's `x-total`.

| Search | Total | Relevant hits |
|---|---|---|
| [transcend](https://gitlab.com/api/v4/projects?search=transcend&order_by=created_at&sort=desc) | 438 | receipted-pipeline, receipted-pipeline-demo, the 2 staff showcases |
| [life after code](https://gitlab.com/api/v4/projects?search=life%20after%20code&order_by=created_at&sort=desc) | 15 | sam1054/aftermerge, babydov-release-sentinel |
| [life-after-code](https://gitlab.com/api/v4/projects?search=life-after-code) | 0 | none |
| [transcend hackathon](https://gitlab.com/api/v4/projects?search=transcend%20hackathon&order_by=created_at&sort=desc) | 342 | same as "transcend" |
| [gitlab-transcend](https://gitlab.com/api/v4/projects?search=gitlab-transcend) | 3 | none (all June 2026) |
| Topic [gitlab-transcend](https://gitlab.com/api/v4/projects?topic=gitlab-transcend) | 1 | receipted-pipeline |
| Topics transcend / transcend-hackathon / duo-agent-platform / GitLab-Duo-Agent-Platform / GitLab AI Hackathon / lifecycle | 2 / 4 / 8 / 3 / 1 / 16 | none from October |
| 31 keywords on projects created since about Sep 27 (`id_after=86950000`): hackathon 26, devsecops 68, post-code 1, post-merge 1, "post code" 8, "duo agent" 2, duo 15, agentic 21, lifecycle 46, hands-off 3, autonomous 18, self-healing 2, sentinel 3, incident 19, on-call 6, rollback 16, canary 6, release 180, triage 21, compliance 14, SBOM 1, changelog 11, postmortem 1, runbook 8, SRE 16, pipeline 221, deploy 204, "cloud run" 8, mcp 87, flow 165, agent 281 | see left | Only the 3 entries above plus the receipted demo. Adjacent non-entries listed under Details. |
| 19 more keywords since about Sep 28 (`id_after=86990000`): "path a" 92, "path b" 92, devpost 2, showcase 17, post-deploy 0, "after merge" 1, "after code" 3, "duo flow" 1, "custom flow" 2, ambient 1, orbit 9, "release notes" 1, flaky 1, vulnerability 5, remediation 4, observability 18, postmortem 0, "change risk" 2, "blast radius" 3 | see left | Same entries. No new ones. |
| Name checks since about Sep 25: nexus 13, "proof of fix" 0, proof-of-fix 0, a2a 5, aftermerge 1, receipted 2, "release sentinel" 1, hvfr 0, omega 1 | see left | No GitLab copy of NEXUS, Proof of Fix or A2A Omega |
| [explore/projects?search=transcend](https://gitlab.com/explore/projects?search=transcend), [explore/projects?search=life+after+code](https://gitlab.com/explore/projects?search=life+after+code) | HTTP 200, 0 visible | Results are drawn by JavaScript, so curl and WebFetch see no list. Used the API searches above instead. |

### GitLab, issues

| Query or URL | Result |
|---|---|
| [issues?scope=all&search=Life After Code&created_after=2026-09-01](https://gitlab.com/api/v4/issues?scope=all&search=Life%20After%20Code&created_after=2026-09-01T00:00:00Z) | Word match, not phrase: 100+ results, mostly noise. Led to the onboarding project below. |
| [gitlab-community/community-members/onboarding](https://gitlab.com/gitlab-community/community-members/onboarding) issues created since 2026-09-25 ([API](https://gitlab.com/api/v4/projects/60607268/issues?created_after=2026-09-25T00:00:00Z&per_page=100)) | 70 onboarding requests. Each has a "Reason:" line. 6 name Transcend or Life After Code, 1 more says "AI agent project for the hackathon", 4 more name a hackathon without saying which (likely the separate Community Hackathon). |
| User project lists for those 7 people ([example](https://gitlab.com/api/v4/users/williamleewilliam1-star/projects)) | 0 public projects each, except iykyk-vedant (1 unrelated) |

### GitHub (WebFetch of github.com pages)

| Query or URL | Count | Relevant |
|---|---|---|
| [topics/gitlab-transcend](https://github.com/topics/gitlab-transcend) | 0 repos | none |
| [repos: "Life After Code" gitlab](https://github.com/search?q=%22Life+After+Code%22+gitlab&type=repositories) | 1 | jamesparser/a2a-omega-hvfr |
| [repos: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=repositories&s=updated&o=desc) | 7 | alejandro-publius/life-after-code (ours), Cubiczan/aftermerge, icohangar-ops/aftermerge, jamesparser/a2a-omega-hvfr |
| [repos: "GitLab Transcend"](https://github.com/search?q=%22GitLab+Transcend%22&type=repositories) | 8 | a2a-omega-hvfr (other 7 are June) |
| [repos: transcend hackathon gitlab](https://github.com/search?q=transcend+hackathon+gitlab&type=repositories&s=updated&o=desc) | 4 | none (all June) |
| [repos: "Life After Code" OR "gitlab-transcend" OR "GitLab Transcend"](https://github.com/search?q=%22Life+After+Code%22+OR+%22gitlab-transcend%22+OR+%22GitLab+Transcend%22&type=repositories&s=updated&o=desc) | 14 | same 4 as above |
| [repos: "Duo Agent Platform"](https://github.com/search?q=%22Duo+Agent+Platform%22&type=repositories&s=updated&o=desc) | 12 | none (newest Aug 14) |
| [repos: gitlab duo created after Sep 28](https://github.com/search?q=gitlab+duo+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 0 | none |
| [repos: gitlab hackathon created after Sep 28](https://github.com/search?q=gitlab+hackathon+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 0 | none |
| [repos: gitlab devsecops agent created after Sep 28](https://github.com/search?q=gitlab+devsecops+agent+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 3 | a2a-omega-hvfr; Akhyame/ai-telegram-devsecops-agent (no hackathon mention) |
| [issues: "gitlab-transcend.devpost.com"](https://github.com/search?q=%22gitlab-transcend.devpost.com%22&type=issues&s=created&o=desc) | 1 | JannetEkka/DSProjects#18 |
| [issues: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=issues&s=created&o=desc) | 225 | DSProjects#18, TSAMBALI/Ariadne_Tsambali#218 (rest unrelated) |
| [issues: "GitLab Transcend"](https://github.com/search?q=%22GitLab+Transcend%22&type=issues&s=created&o=desc) | 38 | same 2 (rest are bot article digests) |
| [issues: "Transcend Hackathon"](https://github.com/search?q=%22Transcend+Hackathon%22&type=issues&s=created&o=desc) | 37 | Ariadne_Tsambali#218 |
| [issues: "Duo Agent Platform" hackathon](https://github.com/search?q=%22Duo+Agent+Platform%22+hackathon&type=issues&s=created&o=desc) | 33 | Ariadne_Tsambali#218 |
| Owner pages: [JannetEkka repos](https://github.com/JannetEkka?tab=repositories) (16, none for Proof of Fix), [DSProjects hackathon issues](https://github.com/JannetEkka/DSProjects/issues?q=is%3Aissue+label%3Ahackathon) (14), [TSAMBALI repos](https://github.com/TSAMBALI?tab=repositories) (11, none for NEXUS), [Ariadne_Tsambali](https://github.com/TSAMBALI/Ariadne_Tsambali) (empty repo, about 218 issues) | | |

### Web search (5 queries, then the shared search budget ran out)

| Query | Results | Relevant |
|---|---|---|
| `site:github.com "gitlab-transcend"` | 10 | 0 (June gitlab.com workspaces) |
| `site:github.com "Life After Code" GitLab hackathon` | 10 | 0 |
| `site:github.com "GitLab Transcend" hackathon` | 10 | 0 (June blog and June workspaces) |
| `"Duo Agent Platform" hackathon 2026 "Life After Code"` | 10 | 0 (Feb 2026 winners blog) |
| `"gitlab-transcend.devpost.com"` | 10 | 0 (June items) |

Not run (budget exhausted): `"Life After Code" GitLab hackathon agent project October 2026`, `site:gitlab.com "Life After Code"`, `"GitLab Transcend" "Path A" OR "Path B" agent "hands-off" 2026`. The web index had nothing from October yet, so code host searches carried this scan.

## Projects found

"Duo use" means GitLab Duo Agent Platform features (flows, agents, MCP) visible in the repo. Every entry must use them ([RULES.md](../../RULES.md)).

| # | Name | Link | Author | What it does | Lifecycle stages | Idea space | Path, autonomy | Duo use | State on Oct 6 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Receipted Pipeline | [GitLab](https://gitlab.com/rambozambodotdev/receipted-pipeline), [demo target](https://gitlab.com/rambozambodotdev/receipted-pipeline-demo) | @rambozambodotdev, display name "Rambo (AI, director of ops for Zambo)" | Agent opens an MR, gates review, security and tests, merges, checks the Pages deploy and a health probe, and mints one "verifiable receipt" per stage | create (review), secure, verify, release, monitor | Full post-merge pipeline orchestrator with evidence receipts | Path B (its own text), hands-off | Yes: custom flow YAML, AGENTS.md, MCP config. Its README says the flow is "inert until it is registered" | Working run: MR !1 merged, green pipelines on Oct 5 |
| 2 | AfterMerge | [GitLab](https://gitlab.com/sam1054/aftermerge), [GitHub](https://github.com/Cubiczan/aftermerge), [GitHub copy](https://github.com/icohangar-ops/aftermerge) | @sam1054 (GitLab), Cubiczan (GitHub), Sam Desigan | Browser-only simulated console: after a merge, an agent runs SAST, dependency reachability, staging deploy, smoke tests, release notes, risk-based human approval, promote | secure, verify, release, govern | Post-merge release gatekeeper with a human gate (simulated) | Path A, auto at low risk, human at medium or high | None found. "Nothing in the loop calls the network" | Demo UI and YouTube video done |
| 3 | BABYDOV Release Sentinel | [GitLab](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel) | Ivan Babydov, group babydov-life-after-code | Deterministic "release authority": evidence ledger, risk and "autonomy budget" scores, canary, rollback rehearsal, GO, HOLD or ROLLBACK, attestation, Pages dashboard | verify, secure, package (SBOM), release, monitor (prod check), govern | Release gatekeeper with rollback and deploy verification | Path B, hands-off | None found. No LLM at all | Green pipelines, Pages dashboard, 58-second video |
| 4 | A2A Omega HVFR | [GitHub](https://github.com/jamesparser/a2a-omega-hvfr) | @jamesparser | Hunter agent scans MRs and commits, Verifier confirms and fixes or blocks, Triage closes false positives, hourly poller | secure, verify, govern | Security triage and auto-fix | Path B, hands-off | None found (no CI file, no `.gitlab/duo`) | 11 commits, updated about Oct 2 |
| 5 | NEXUS DevSecOps AI | [GitHub issue #218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218) | @TSAMBALI | Plan for a "10-agent mesh" with a falsification agent, Gemini model router, SANS SIFT forensics; demo finds the real cause of a staging 503 | claims all 9 stages; focus on incident root cause, security, compliance | Multi-agent "everything" mesh with incident root cause | claims all 3 autonomy levels, Cloud Run | Claimed (unverified: no code public) | Plan text only; repo empty; named GitLab repo returns 404 |
| 6 | Proof of Fix | [GitHub issue #18](https://github.com/JannetEkka/DSProjects/issues/18) | @JannetEkka | "an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears" | monitor, plan (reopen issue), release check | Fix verification in production | not stated | not stated | Plan only, no repo yet |
| 7 | (unnamed) post-code release agent | [onboarding #5528](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5528) | @williamleewilliam1-star | "build and validate an autonomous post-code release agent with GitLab Duo Agent Platform" | release | Release agent | not stated | stated | Intent only, no public project |
| 8 | (no idea stated) | onboarding [#5524](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5524), [#5523](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5523), [#5525](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5525), [#5488](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5488), [#5520](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5520) | @1Hilal7, @mhamzanadeem2000003, @matthewjameswatkins1978, @tusharaggarwal274, @hawk-2221 | Say they are entering; no idea given | n/a | n/a | n/a | n/a | No public projects |
| 9 | Staff workspaces (not entries) | [leetickett](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase), [missy-davies](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase), [leetickett-gitlab](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/12687636) | GitLab staff (Missy Davies is a listed judge per [RULES.md](../../RULES.md)) | Default template, nothing built | none | n/a | n/a | none | Empty |

## Details

### 1. Receipted Pipeline (@rambozambodotdev)

- Description: "Receipted Pipeline: an AI agent runs the full post-code DevSecOps lifecycle (review, security, test, deploy, monitor) hands-off on GitLab, and every stage leaves a verifiable execution receipt (AER-1). GitLab Transcend hackathon Path B entry." Topics include `gitlab-transcend`, `mcp`, `verifiable-receipts`. MIT. Created 2026-10-05 ([project API](https://gitlab.com/api/v4/projects/87252421)).
- Two layers. (a) An external Python orchestrator using a personal access token: creates a branch and a real code change, opens an MR, posts a review note, downloads SAST and secret-detection artifacts and triages new findings against the base branch, parses JUnit, merges only if gates pass, then checks the GitLab Pages deploy (HTTP 200, content marker, deployed SHA) and a monitor probe SLO ([orchestrator/README.md](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/orchestrator/README.md), [config.yaml](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/orchestrator/config.yaml)). (b) A Duo custom flow with five `AgentComponent` stages (review, security, test, deploy, monitor) chained by routers that stop at the first failing gate, triggered by pipeline events ([flow YAML](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/.gitlab/duo/flows/receipted-pipeline.yaml), [AGENTS.md](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/AGENTS.md)). Receipts are minted through the author's own "Zambo" MCP server ([mcp.json](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/.gitlab/duo/mcp.json)).
- The README says the flow is not yet live: "The flow YAML above is inert until it is registered." ([README](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/README.md)). The working run was done by the external orchestrator: [MR !1](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/merge_requests/1) merged Oct 5 with 5 notes, and the latest 10 [pipelines](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/pipelines) are all green.
- AGENTS.md: "Hands-off: the flow runs ambient on pipeline events. No human in the loop and no interactive prompts." Also: "a receipt proves the saved result was not changed. It does NOT prove the agent was right."
- The owner account looks like an AI-run account entering many hackathons at once: 20 projects, including six `hackathon-blitz-*` entries for other contests created Oct 4, all built around the same "AER-1 receipts" idea ([user projects API](https://gitlab.com/api/v4/users/rambozambodotdev/projects)). It also filed [onboarding #5529](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5529): "Participating in the GitLab Transcend hackathon (October 2026) with the receipted-pipeline project".
- Deploy target is GitLab Pages, not Google Cloud, so no Cloud Run bonus as of now.

### 2. AfterMerge (@sam1054 on GitLab, Cubiczan on GitHub)

- Description: "AfterMerge - post-merge DevSecOps agent for Life After Code" ([GitLab](https://gitlab.com/sam1054/aftermerge)); GitHub: "Post-merge agent console demo (FieldClear / Life After Code Path A)" ([Cubiczan/aftermerge](https://github.com/Cubiczan/aftermerge)). A second GitHub copy sits at [icohangar-ops/aftermerge](https://github.com/icohangar-ops/aftermerge).
- README: "When a merge request lands, an agent owns the life after the code: security scan, dependency audit, staging deploy, smoke tests, release notes, a human approval gate, and production promote. The demo is fully simulated. No GitLab token and no paid API." Policy: "Medium risk stops at a person. A critical, reachable advisory on an older run never leaves the dependency stage." It states Path A: "This is a **new repo and a new demo**." ([README](https://gitlab.com/sam1054/aftermerge/-/blob/main/README.md)).
- Setting is a fictional field-service company ("Northline Mechanical", product "FieldClear"). Next.js, state in the browser, hosted at [aftermerge.vercel.app](https://aftermerge.vercel.app), video at [youtu.be/jl3muP7JNEE](https://youtu.be/jl3muP7JNEE) (both unverified, not opened).
- [architecture.md](https://gitlab.com/sam1054/aftermerge/-/blob/main/docs/architecture.md): "The hackathon build runs entirely in the browser. A later plug-in replaces the player with GitLab webhooks and CI job APIs." Its sample `.gitlab-ci.yml` is marked "Illustrative. Not wired in this demo."
- No Duo Agent Platform use in any file I read (AGENTS.md is the Next.js generated block). GitLab project: 1 commit, 0 pipelines. As it stands it would likely fail the "genuinely use GitLab AI features" check (unverified, they may add it).

### 3. BABYDOV Release Sentinel (Ivan Babydov)

- Description: "Evidence-first autonomous release authority for GitLab Life After Code 2026 · Path B Hands-off Agent." ([project](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel)). Group created Oct 3, commits Oct 5 and 6.
- README: "Release Sentinel takes over the post-code path and will only promote a build when it can prove three things": evidence intact, canary correct, previous release restorable. "If any of those proofs are missing, the agent does not improvise. It **HOLDs**. If production verification fails, it **ROLLBACKs**." Pipeline chain: tests, provenance, SAST, secret scan, dependency inventory, SBOM, build, canary, rollback rehearsal, "2M stress", release decision, promotion, production verification, attestation, Pages dashboard ([README](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/README.md)).
- Self-reported claims (unverified): a "2,000,000-agent adversarial fleet" with "0 unsafe GO decisions"; a judge-triggerable `rollback-drill` job ([SUBMISSION_DRAFT.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/SUBMISSION_DRAFT.md)).
- Targets "Path B · Best Hands-off Agent", and says it is "also optimized for" Most Stages Covered, Most Impactful and Most Creative ([JUDGING_MATRIX.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/JUDGING_MATRIX.md)).
- No model and no Duo Agent Platform in the code: the agent returns `"llm_can_override": False`, and [ARCHITECTURE.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/ARCHITECTURE.md) says "Any future model or heuristic advisor may summarize a diff or propose risk signals, but it cannot change the deterministic safety kernel." Built with "Python standard library + GitLab CI/CD". Same pass/fail risk as AfterMerge (unverified).
- Live links from the README (not opened): [Pages dashboard](https://babydov-release-sentinel-e52f53.gitlab.io), [video](https://youtu.be/6d7QBKYO29I), [pipelines](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/pipelines) (5 runs: the first failed, the other 4 green, latest on Oct 6 UTC, per the [pipelines API](https://gitlab.com/api/v4/projects/87191977/pipelines)).

### 4. A2A Omega HVFR (@jamesparser)

- About text: "A2A Omega HVFR - Hunt · Verify · Fix/Block · Report. Hands-off multi-agent DevSecOps lifecycle automation for GitLab Transcend (Life After Code)." ([repo](https://github.com/jamesparser/a2a-omega-hvfr)).
- README, as summarised by WebFetch: Hunter (Secure) scans MRs and commits and files findings; Verifier "Independently confirms findings; fixes or blocks"; Triage (Govern) auto-closes false positives; hourly schedule; reuses the author's "A2A Omega" routing hub, "redirect[ing] agent-to-agent orchestration from external bounty hunting toward GitLab's post-code lifecycle"; labelled "Path B: Bring Your Own · Hands-off Agent" ([raw README](https://raw.githubusercontent.com/jamesparser/a2a-omega-hvfr/main/README.md)).
- Files: `a2a_hub.py`, `a2a_agentverse.py`, `a2a_e2a.py`, `a2a_client.py`, `poller.py`, `mesh_test.py`, `config/`. No `.gitlab-ci.yml`, no `.gitlab/duo`, no flow files, model not named. No GitLab copy found.

### 5. NEXUS DevSecOps AI (@TSAMBALI), planning issue

- [Issue #218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218), title "GitLab Transcend Hackathon", opened Oct 5, no labels, no comments. The repo has no code; the owner uses it as a notebook with about 218 issues, many of them other "NEXUS" hackathon plans (for example #217 "Case Closed & Atlantic Nexus AI Platform", #216 "Dublin Nexus AI", #209 "Protocol SIFT", per the [issue list](https://github.com/TSAMBALI/Ariadne_Tsambali/issues?q=is%3Aissue+sort%3Acreated-desc)).
- Plan: a "governed 10-agent mesh built on the GitLab Duo Agent Platform and Model Context Protocol": Lifecycle Orchestrator, Code Intelligence, Security, Verification, Compliance, Deployment, Monitoring, Risk and Scenario, a "Challenge/Falsification Agent (Popperian Disproof Gate)", Executive Decision. Gemini model routing for cost and carbon ("Green SCI Model Router"), SANS SIFT forensic tools, read-only mounts, SHA-256 evidence checks. Demo: a staging HTTP 503 where the falsification agent rejects "code regression" and finds Redis connection-pool config drift. Claims the 3 autonomy levels and all 9 stages, plus a Cloud Run deployment.
- Key line: "Trust in autonomous DevSecOps does not come from an LLM claiming '99% confidence.' Trust comes from falsifiability and architectural containment."
- All accuracy numbers in the issue (for example 99.4% recall, "cutting carbon intensity by 64.2%") are self-reported (unverified). The GitHub search snippet says it targets both the "GitLab Transcend 3:00 limit and SIFT 5:00 limit", so the same project seems aimed at a SANS SIFT contest too. The GitLab repo it names, `gitlab.com/gitlab-transcend/nexus-devsecops-ai`, returns 404 ([API](https://gitlab.com/api/v4/projects/gitlab-transcend%2Fnexus-devsecops-ai)).

### 6. Proof of Fix (@JannetEkka), planning issue (the idea we must avoid)

- [Issue #18](https://github.com/JannetEkka/DSProjects/issues/18), title "Oct 27 · GitLab: Life After Code - "Proof of Fix"", label `hackathon`, opened Oct 5, open, zero comments, no linked PRs or repos.
- Body, verbatim: "**Plan:** "Proof of Fix", an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears." Then an unticked checklist (Registered, Rules read, Devpost page, Repo, Working build, Demo video, Submission text, Submitted, Result) and "Waiting on Jannet: Start session S4." Footer: "Every session ticks this checklist and comments at each milestone. This issue is the single place for status."
- Context: the same repo has 14 `hackathon` tracking issues opened Oct 5, one per contest from Oct 8 to Dec 2 ([list](https://github.com/JannetEkka/DSProjects/issues?q=is%3Aissue+label%3Ahackathon)). It looks like agent sessions run a hackathon pipeline for the owner. No Proof of Fix repo among the owner's 16 repos yet ([repos](https://github.com/JannetEkka?tab=repositories)).
- What to steer clear of: an agent that watches production logs or telemetry after a merge to confirm a promised fix, and reopens or updates the issue when it is not confirmed.

### 7. Onboarding requests that name the hackathon

The GitLab community onboarding form asks for a "Reason". From the 70 requests since Sep 25 ([API](https://gitlab.com/api/v4/projects/60607268/issues?created_after=2026-09-25T00:00:00Z&per_page=100)):

- @williamleewilliam1-star ([#5528](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5528)): "Life After Code hackathon: build and validate an autonomous post-code release agent with GitLab Duo Agent Platform."
- @1Hilal7 ([#5524](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5524)): "Participating in the Life After Code: Transcend Hackathon and learning to build agentic DevSecOps workflows with GitLab Duo Agent Platform."
- @mhamzanadeem2000003 ([#5523](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5523)): "...build an AI-powered DevSecOps project using GitLab Duo Agent Platform."
- @matthewjameswatkins1978 ([#5525](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5525)): "...an open-source project that uses GitLab Duo Agent Platform and CI/CD"
- @tusharaggarwal274 ([#5488](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5488)): "...build an agentic solution that automates meaningful parts of the software delivery lifecycle."
- @hawk-2221 ([#5520](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5520)): "build an AI agent project for the hackathon" (hackathon not named).
- @rambozambodotdev ([#5529](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5529)): Receipted Pipeline, see above.

None of these people has a public GitLab project yet.

### Adjacent projects checked and excluded (no hackathon mention)

- [rodripn91/pipeline-doctor](https://gitlab.com/rodripn91/pipeline-doctor) (Oct 5): static analysis and critical-path simulation for `.gitlab-ci.yml`. CI tooling, no AI agent, no hackathon mention.
- [Akhyame/ai-telegram-devsecops-agent](https://github.com/Akhyame/ai-telegram-devsecops-agent): Telegram control of GitLab CI security gate and staging deploy; "The deterministic Security Gate makes security decisions, not the AI model".
- [Qivoxe/Codegenome](https://gitlab.com/Qivoxe/Codegenome) (Oct 4): change blast-radius graph, "hackathon MVP" badge, no contest named, not GitLab-based.
- [jyoshise1/ai-security-deepscan-orbit](https://gitlab.com/jyoshise1/ai-security-deepscan-orbit) (Oct 5): Japanese validation report of Duo custom agents and flows with Orbit for security review on self-managed GitLab. A test write-up, not an entry.
- [gl-demo-premium-mushijima/custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo) (Oct 5): GitLab demo account with sample flows for release notes, coding-standards review and issue triage. Shows what GitLab field teams demo, so these three ideas look "stock".
- Judges' reference: [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) (GitLab staff). Its hands-off loop: Duo Developer flow opens an MR, Duo Code Review, auto-merge, tests, image build, SAST, dependency, secret and container scans, staging deploy, smoke test, promote to production, tagged release, summary on the issue. "Nothing in steps 2 to 4 requires a human."

## Crowded idea spaces

Early signal only: 7 known ideas on day 2 (4 entries with code, 2 planning issues, 1 onboarding request), against 621 Devpost participants at last index ([RULES.md](../../RULES.md)). Ranked by how many known entries sit in each space.

1. **Post-merge release gatekeeper (review, scan, test, deploy, health check, then ship, hold or roll back).** Receipted Pipeline, AfterMerge, Release Sentinel, and @williamleewilliam1-star's "post-code release agent". The judges' own [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) already does this loop. Most crowded. Avoid as the main idea.
2. **Evidence, receipts and attestation** (hash-chained ledgers, "verifiable receipts", SHA-256 proofs that the agent's record was not changed). Receipted Pipeline, Release Sentinel, NEXUS. Three of seven. Do not lead with "auditable agent decisions".
3. **Security triage and auto-fix** (find, verify, fix or block, close false positives). A2A Omega HVFR as the main idea; NEXUS, AfterMerge and Release Sentinel include it as a stage. The Feb 2026 Google Cloud prize went to a security fixer, Gitdefender (per a search result summary of the [Feb 2026 winners post](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/), unverified).
4. **Post-deploy verification and rollback.** Proof of Fix (log line after merge, reopen issue), Release Sentinel (canary, rollback rehearsal, production check), Receipted Pipeline (monitor probe), AfterMerge (smoke tests). Proof of Fix is the one we were told to avoid.
5. **"All nine stages" multi-agent meshes.** NEXUS (10 agents), Receipted Pipeline (5 stage agents), A2A Omega (3 agents). Broad and claim-heavy.
6. **Stock Duo demo flows:** release notes, coding-standards review, issue triage, fix-the-pipeline, shown in GitLab's own [custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo) and in the [Duo Agent Platform repo search](https://github.com/search?q=%22Duo+Agent+Platform%22&type=repositories&s=updated&o=desc) (code review and security agents). Judges have likely seen these many times (inference).
7. **History, June 2026 Orbit edition:** a search summary of GitLab's [June recap post](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/) said "Seventy teams built a version of the same tool: Tell me what this change could break before I merge it." (unverified, about.gitlab.com is blocked here). Blast-radius tools were the crowded space last time.

Not seen yet as anyone's main idea on code hosts (small sample, re-check later): on-call incident response with a human in the loop (paging, runbook steps, postmortem drafts), user feedback or support tickets turned into issues, feature flags and progressive rollout (configure), package and registry hygiene, dependency upgrade flows, flaky-test handling, compliance evidence for auditors, and cost or carbon as the main product. NEXUS touches incident root cause and carbon only as parts of a large plan.

## Blocked

| URL | Tool | Error |
|---|---|---|
| devpost.com, web.archive.org | not tried | Blocked per the access notes |
| https://github.com/topics/gitlab-transcend, https://github.com/search?q=gitlab-transcend&type=repositories | curl | 403 from the proxy: "GitHub access to this repository is not enabled for this session" and "This GitHub API path is not available". WebFetch of github.com worked. |
| https://api.github.com/search/repositories?q=gitlab-transcend | curl | 403, same message |
| https://contributors.gitlab.com/api/v1/transcend_hackathon and `/registrations` | curl | "CONNECT tunnel failed, response 403". The route exists in the [site source](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/config/routes/api_routes.rb). |
| https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/ | WebFetch | EGRESS_BLOCKED |
| https://gitlab.com/api/v4/projects/87183213/issues/1/notes | curl | 401 Unauthorized (notes need a token) |
| https://gitlab.com/api/v4/search?scope=issues&search=Life%20After%20Code | curl | 401 Unauthorized (global search needs a token). The `/issues?scope=all` endpoint worked. |
| https://gitlab.com/api/v4/projects/gitlab-com%2Fmarketing%2Fdigital-experience%2Fabout-gitlab-com/search | curl | 401 Unauthorized |
| https://gitlab.com/explore/projects?search=transcend and ?search=life+after+code | curl, WebFetch | HTTP 200 but the list is drawn by JavaScript, so no results visible |
| WebSearch | tool | Shared budget ran out after 5 queries; 3 planned queries not run (listed under Searched) |
