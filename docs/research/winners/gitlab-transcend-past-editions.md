# GitLab's earlier Transcend hackathons: what won and why

Compiled 2026-10-06 for Alex Velazquez (solo entrant, Life After Code, the October 2026 "Transcend III" edition).

Everything here comes from gitlab.com (readable: repos, REST API, GraphQL, issues) plus search excerpts. Devpost, YouTube, about.gitlab.com, the GitLab forum, X, LinkedIn, Medium and dev.to were blocked. The WebSearch budget shared by all agents in this session ran out early in my run, so I could not search for anything after that (see "Blocked").

Scope: the coordinator narrowed this file to the Transcend editions, mainly June 2026. The GitLab AI Hackathon (Feb to Mar 2026) and Google Cloud's AI in Action 2025 GitLab challenge have their own files. I keep a short cross-reference to the AI Hackathon winners near the end, because their repos are the only GitLab-judged winners I could open, and the June winners list was out of reach.

| Tag | Meaning |
|---|---|
| [D] | Read directly on gitlab.com (repo file, API, issue). Quotes are exact, except that an em or en dash becomes " - " (see docs/DECISIONS.md). |
| [P] | Written by a participant in their own repo, for example their copy of the Devpost criteria. Exact for what they wrote; not proof of what Devpost said. |
| [S] | Search-engine excerpt (unverified wording). Most were saved earlier in this repo by other agents, in [RULES.md](../../RULES.md) and [rules_discussions.md](../rules_discussions.md). |
| (unverified) | Not confirmed by any source I could open. |

## Read this first

1. **The June 2026 (Transcend II) winners are not in this file.** GitLab's results post is [about.gitlab.com/blog/gitlab-transcend-hackathon-orbit](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/) (published 2026-07-20 according to the coordinator; I could not open it). about.gitlab.com and all Devpost pages are blocked by the proxy, and WebSearch answered "budget used up" for every query after the coordinator's update. No gitlab.com source I checked names a June winner: team-task issues and their comments, the contributors platform code and history, the 312 June workspaces (READMEs, late commits, issues and MRs touched after judging), the AI Catalog, GitLab achievements, and community content issues. I did not guess.
2. **What is solid about June:** dates, tracks, judging stages, the four criteria, the size of the field, what the 312 workspaces contain, and GitLab's own after-event notes. See "Transcend II".
3. **Best available evidence of what GitLab judges reward** comes from the 9 AI Hackathon winners whose repos I opened (the same GitLab developer relations team ran that event), GitLab's written instructions for June and October, and GitLab staff comments. The repeated traits: a named, felt pain told as a story; agents that act on GitLab objects when triggered, not chat; several specialist agents with clear jobs; real engineering under the prompts (tests, models, policy files); a human gate before anything risky; proof that it ran, visible in MR and issue threads; and sponsor technology used for real when a sponsor prize is the target.
4. **June's field was crowded.** 76 of the 148 June workspaces with a real README use the phrase "blast radius" [D, my scan]. Whatever won in June, a 77th blast-radius tool would start behind.

## Editions

| Edition | Devpost site | Dates | Prize pool | Size | Judging | Winners | Coverage here |
|---|---|---|---|---|---|---|---|
| "Transcend I" | not found under that name | see note below | | | | | note only |
| GitLab AI Hackathon, "You Orchestrate. AI Accelerates." | [gitlab.devpost.com](https://gitlab.devpost.com/) | Feb 9 to Mar 25, 2026 [S] | $65,000 in 11 categories, 19 prize slots [S][P] | "Nearly 7,000 developers" and "600+" agents and flows [S]; 1,788 provisioned workspaces and 1,807 public catalog items from 506 of them [D] | 4 criteria as copied by entrants: Technological Implementation, Design (and usability), Potential Impact, Quality of the Idea [P]; weights (unverified) | LORE (Grand Prize) and 8 more named below; 6 Honorable Mentions and 4 Sustainable Design Bonus winners not retrieved | short cross-reference; full coverage in the separate AI Hackathon file |
| **Transcend II**, June 2026, "GitLab Orbit" | [gitlab-transcend.devpost.com](https://gitlab-transcend.devpost.com/) (same URL as October) | Jun 10 to 24, 2026; judging Jun 25 to Jul 8; page promised winners "on or around July 10"; results post 2026-07-20 (coordinator) [D][S] | cash amounts not retrieved (unverified); swag credits on top [D] | 1,576 registered and 265 eligible Showcase projects [S]; 318 submissions in both tracks [D]; 312 Showcase workspaces [D]; 61 merged Contribute-track MRs [D] | Stage 1 pass/fail on theme fit and use of GitLab Orbit; Stage 2 four equally weighted criteria [S][P] | **not retrieved** | full section below |
| Transcend III, Oct 2026, "Life After Code" (current) | same URL | Oct 5 to 27, 2026; winners about Nov 16 [D] | $45,000, 9 categories [S] | 621 participants when indexed [S] | pass/fail, then 5 equal criteria including Presentation; up to +0.2 for Google Cloud deployment [D][S] | not yet | comparison only; see [RULES.md](../../RULES.md) |
| Google Cloud "AI in Action" 2025, GitLab challenge | Google's Devpost site | 2025 [S] | not researched here | | | one entrant self-labels "Pipeline Doctor" as "[AI in Action Hackathon Gitlab Track Winner]" ([content issue #78](https://gitlab.com/gitlab-community/community-members/content/-/work_items/78) [D]) | pointer only, separate file |

**Note on "Transcend I".** No gitlab.com source uses the names "Transcend I" or "Transcend II". GitLab's October group description says "GitLab Transcend III hackathon (October 2026)" ([group API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026) [D]). GitLab held its first "GitLab Transcend" virtual event on Feb 10, 2026 ([press release](https://about.gitlab.com/press/releases/2026-02-03-gitlab-to-host-gitlab-transcend-global-virtual-event/) [S]), one day after the GitLab AI Hackathon opened, and one AI Hackathon entrant wrote "Built by Approxiom Research for the GitLab Transcend AI Hackathon 2026" ([README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34578745) [P], weak evidence). The June page said "In honor of GitLab Transcend, the Transcend Hackathon kicks off on June 10th" [D]. The most likely reading is: I = the Feb 2026 AI Hackathon held around the first Transcend event, II = June 2026, III = October 2026 (inference, unverified).

## Transcend II: June 2026, "GitLab Orbit"

### What it was

| Item | Value | Source |
|---|---|---|
| Devpost title | "GitLab Transcend Hackathon: Intelligent orchestration, now with context." | [S], /rules as indexed (see [RULES.md](../../RULES.md)) |
| Purpose | "An event for community contributors to celebrate Transcend, running June 10th - June 24th 2026. The event drives contributions to the GitLab Knowledge Graph and Orbit CLI while helping users learn both tools." | [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137) [D] |
| Submission window | "It runs for **two weeks** (June 10 - 24, 2026 UTC)." Devpost rules: June 10, 10:00 am ET to June 24, 2:00 pm ET. | GitLab page text removed in [contributors-gitlab-com!2389](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2389) [D]; rules [S] |
| Judging | "June 25, 2026 (10:00 am Eastern Time) - July 8, 2026 (5:00 pm Eastern Time)" | same MR, TranscendHackathonPage.vue [D] |
| Winners | Page: "On or around July 10, 2026 (2:00 pm Eastern Time)". Results post: 2026-07-20 (coordinator). GitLab's own retro later says "Don't leave the results/winner date "for later"", which fits a slipped date (inference). | [D]; [team-task#1260](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1260) [D] |
| Tracks | **Contribute:** merge requests on issues labelled `orbit::hackathon`; "Your MR must be merged before June 25th to qualify." **Showcase:** "Build agents, flows, or skills that interact with GitLab Orbit and publish them to the AI Catalog, and share your work via a blog post, video, or social media." "Participants are welcome to enter both tracks." | [!2389](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2389) DetailsSection.md [D] |
| The challenge (Showcase) | "Build something that solves a real problem. Your submission should tell a story: What is the pain point? How does your agent, flow, or skill fix it? What changes for the developer who uses it?" Then: "Publish at least one agent or flow to the AI Catalog." "Then share your work. A blog post, video, or social media post all count." | same file [D] |
| Cash prizes | "Required to be eligible for cash prizes: you must both register for the hackathon and submit your work on Devpost." Amounts were on Devpost only and were not retrieved (unverified). Early planning said "We want this on Devpost. No monetary reward." (Apr 30); the final page offered cash prizes. | [!2389](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2389) [D]; [#1137 comments](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137) [D] |
| Swag credits | Contribute: first merged MR 40, each additional 20. Showcase: reusable agent 20, social post 20, blog or public video 40. "Only the information published on the Devpost event page is legally binding." | RewardsSection.vue in [!2389](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2389) [D] |
| Workspaces | 312 projects in [gitlab-ai-hackathon/transcend](https://gitlab.com/gitlab-ai-hackathon/transcend), created 2026-06-04 to 06-24, one per approved Showcase registrant; each description maps the GitLab user to the Devpost user | group API [D] |
| Submissions | "318 submissions across the Showcase and Contribute tracks"; 219 filled in the challenges and learnings sections "with substantive detail" | [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D] |
| Registrations | "1,576 registered developers", "265 eligible Showcase Track projects" | results post [S], as saved in [rules_discussions.md](../rules_discussions.md) |
| Contribute track output | 61 merged MRs labelled `orbit::hackathon` in [gitlab-org/orbit/knowledge-graph](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/merge_requests?label_name%5B%5D=orbit%3A%3Ahackathon&state=merged) from 28 authors (merged Jun 8 to 23), 20 closed unmerged, 47 labelled issues | REST API [D] |
| Showcase output | 250 public AI Catalog items (168 agents, 82 flows) from 140 of the 312 workspaces | AI Catalog GraphQL [D] |
| Satisfaction | Transcend/Devpost hackathon rated 4.15/5 (13 ratings). "The Transcend/Devpost format was particularly appreciated for its multiple tracks, freedom to choose projects, cash prizes, and opportunities to build in public." | [team-task#1329](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1329) [D] |

### How it was judged

- **Stage One, pass/fail:** "Stage One will determine via pass/fail whether the ideas meet a baseline level of viability, in that the Project reasonably fits the theme and reasonably uses GitLab Orbit." [S] (June /rules as indexed, quoted in [RULES.md](../../RULES.md)).
- **Stage Two:** "All Submissions that pass Stage One will be evaluated in Stage Two based on the following equally weighted criteria." [S]. Three entrants copied the same four criteria into their READMEs: Technological Implementation; Design and Usability; Potential Impact; Quality of the Idea ([Aftershock](https://gitlab.com/gitlab-ai-hackathon/transcend/39516010), [Tremor](https://gitlab.com/gitlab-ai-hackathon/transcend/39301572), [Merge Radar](https://gitlab.com/gitlab-ai-hackathon/transcend/3214092) [P]). Tremor titled its idea section "Quality of the Idea - *beyond blast radius*", so entrants knew the theme was crowded.
- **Ties:** highest score on the first criterion, then the next, then a judges' vote [S].
- **Judges:** not retrieved for June. The names that search returned for the shared URL (Missy Davies, Mattias Michaux, Dennis Meister, Lee Tickett of GitLab; Rajesh Agadi of Google) may belong to either edition (unverified).
- **No video criterion.** Unlike October, there was no separate "Presentation" score; a video was one of three ways to "share your work" [D].

### Winners

| Prize | Project | Team | Repo | Video | Status |
|---|---|---|---|---|---|
| all June prizes, both tracks | not retrieved | | | | Results post on about.gitlab.com and the Devpost gallery are blocked; WebSearch budget exhausted. Nothing on gitlab.com names a winner. |

Leads that are **not** evidence of winning, listed so a later search can check them quickly:

- GitLab's own post-event review quoted six June submissions by name, for the friction they reported, not for quality: Orbit Memory, Switchyard, Downwind, NEXUS, Orbit AI Engineering Manager, Dead Code Finder ([#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D]).
- One March prize winner entered June: Prateek Srivastava (Time-Traveler, Most Technically Impressive) built [Impact Engine](https://gitlab.com/gitlab-ai-hackathon/transcend/34562572) [D]. 49 people held workspaces in both events (same GitLab user id) [D].
- The most active June workspaces by Duo flow sessions (pipelines with source `duo_workflow`): [Contributor Compass](https://gitlab.com/gitlab-ai-hackathon/transcend/39109018) 94, [AFTERMATH](https://gitlab.com/gitlab-ai-hackathon/transcend/35450945) 64, [Semantic Bug Hunter](https://gitlab.com/gitlab-ai-hackathon/transcend/39290068) 42, [Sankofa](https://gitlab.com/gitlab-ai-hackathon/transcend/34570711) 38, [CompatGuard](https://gitlab.com/gitlab-ai-hackathon/transcend/34816704) 37, [Downwind](https://gitlab.com/gitlab-ai-hackathon/transcend/35554492) 36 [D].

### What GitLab said after June

From Mattias Michaux's review of 318 submissions ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D]):

- "The headline is not new friction, it is the same three themes recurring: developers cannot self-diagnose failures, time to first success is too long because behavior is undocumented, and silent failures erode trust."
- Orbit's query language and docs were the biggest friction: "Teams routinely spent iterations on 400 errors and reverse-engineered the correct query shapes from validation errors." "Multiple teams baked "READ TWICE" warnings and known-good JSON templates into their own agent/flow prompts".
- Duo Agent Platform contract: "Flow YAML requires exact field names (`prompt_id` not `id`, `entry_point` not `entry`, `unit_primitives`) not found in docs." "Inter-agent data must flow through `conversation_history`; direct output references are not valid." "Custom flows require a group namespace, not personal". "Em dashes in flow YAML get silently corrupted in the editor (multiple teams)."
- Missing in June: "Multiple teams noted there is still no "merge request opened" trigger"; flows "have no native MR-note tool"; "Flows cannot make outbound HTTP calls; teams routed scanning through CI and passed results back via an issue."
- Access gates: "New GitLab accounts cannot run CI without a credit card on file; several teams dropped CI or moved it to GitHub Actions." "`CI_JOB_TOKEN` cannot post MR notes (scoped to package registry only)."

From Dennis Meister's retro ([team-task#1260](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1260) [D]): the DevPost checklist for next time includes "Judging criteria defined" and an "Explainer video produced: how to participate + how to do the work", and the don'ts include "Don't leave the results/winner date "for later"".

On noise: Lee Tickett on a June onboarding issue, 2026-06-24: "Please avoid mentioning us unless you need support ... We have a lot of people participating in the hackathon and need as little noise as possible" ([onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend/21418861/-/work_items/1) [D]).

### What the 312 June workspaces contain (my scan, [D])

Method: GitLab REST API for every project in [gitlab-ai-hackathon/transcend](https://gitlab.com/gitlab-ai-hackathon/transcend): file tree, pipelines (first 100) and commits (first 100), plus the README and the AI Catalog (GraphQL). Counts are lower bounds; some entrants kept code elsewhere (for example on GitHub) and only published to the catalog from here.

| Signal | Workspaces |
|---|---|
| Never used beyond the platform's initial commit (2 files or fewer, no human commit) | 132 of 312 (42%) |
| README rewritten (not the provisioning template) | 150 of 312 |
| Published at least one public AI Catalog item | 140 (250 items: 168 agents, 82 flows) |
| Contains at least one `skills/<name>/SKILL.md` | 118 |
| Has flow YAML in the repo / has agent YAML in the repo | 61 / 42 |
| Has `.gitlab-ci.yml` / ran any pipeline | 81 / 103 |
| Ran at least one Duo flow session (pipeline source `duo_workflow`) | 66 |
| Has tests / a Dockerfile / Terraform | 89 / 15 / 0 |
| Custom README (300+ characters) that says "blast radius" | 76 of 148 |
| Custom README that links a YouTube video / a hosted app / mentions Cloud Run | 11 / 7 / 2 of 148 |

Takeaways: almost half the workspaces were abandoned; only about one in five shows a flow actually running on GitLab; very few linked a live app or a video from the repo; and change-impact analysis ("blast radius", ripple, downstream) was the default idea because Orbit makes it easy.

### June entries sampled (winner status unknown)

See "Non-winners sampled" below. Because the June winners list was out of reach, these 14 entries are a cross-section of the field, not a confirmed set of losers.

## Transcend III (October 2026): what changed from June

| | June 2026 (II) | October 2026 (III) | Source |
|---|---|---|---|
| Theme | build on GitLab Orbit (knowledge graph) | automate the post-code lifecycle; "Code generation is solved. What happens next is the challenge." | [D] above; [RULES.md](../../RULES.md) [S] |
| Tracks | Contribute (MRs to Orbit) and Showcase (agents, flows, skills) | Path A (start fresh) or Path B (bring an MIT project), each with Assisted, Supervised and Hands-off prizes, plus cross-path prizes | [RULES.md](../../RULES.md) [S] |
| Criteria | 4, equal: Technological Implementation, Design and Usability, Potential Impact, Quality of the Idea [P][S] | 5, equal: Technological implementation, Design, Potential impact, Innovation, Presentation; Google Cloud deploy adds up to 0.2 | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Video | optional way to "share your work" | required, under 3 minutes, scored as Presentation: "how clearly the video demonstrates the automation running end to end" | same [D] |
| Workspace | one project per person, Developer role | a subgroup plus project, Developer role, can add projects, optional OpenTelemetry endpoint | same [D] |
| Flow triggers | mention, assign, reviewer; no "MR opened" trigger in June ([#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)) | "Flows can run when that user is mentioned in a comment, assigned to an issue or merge request, or added as a reviewer, and on pipeline, merge request, and work item events." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |

October's "Design - a complete, coherent workflow rather than a proof of concept" and its video criterion are the two biggest shifts. Both reward the same things the AI Hackathon winners already did well (below).

## Cross-reference: GitLab AI Hackathon winners I opened (Feb to Mar 2026)

Kept short; a separate file covers this event. Prize names and amounts come from search excerpts of the winners post and Devpost [S], confirmed by a participant's copy of the prize list ([GraphDev hackathon-context.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827/-/blob/main/hackathon-context.md) [P]). Repos moved from `gitlab-ai-hackathon/participants/` to [gitlab-community/community-projects/2026-02-ai-hackathon](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon) on 2026-05-28 ([team-task#1155](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1155) [D]). Each winner was matched to its repo through the public AI Catalog [D]. YouTube was blocked, so no video was watched; where a repo holds a script or video source, I note it. "Committers" counts people in the git history after removing GitLab's template authors; the Devpost team may be larger (unverified).

| Prize [S] | Project | Repo [D] | Committers [D] | Duo flow sessions [D] | Live URL in repo |
|---|---|---|---|---|---|
| Grand Prize, $15,000 | LORE | [35153311](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311) | 2 (Karan Doshi, Khushi Sidana) | 24 of 70 pipelines | GitLab Pages dashboard (not checked) |
| Most Technically Impressive, $5,000 | Time-Traveler | [34562572](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572) | 1 (Prateek Srivastava) | 0 in the latest 100 of 110 pipelines (agents are run from chat) | preview URLs on a GCP VM (not checked) |
| Most Impactful, $5,000 | RedAgent | [35629156](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156) | 1 (Akshat Shende) | 19 of 67 | none |
| Easiest to Use, $5,000 | Launch Control | [19053258](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258) | 1 (GharsallahDev) | 7 of 42 | [launch-control-six.vercel.app](https://launch-control-six.vercel.app) (blocked here) |
| GitLab + Google Grand, $10,000 | Gitdefender | [35458144](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144) | 1 (Kavish Sathia) | 7 of 52 | Cloud Run scoring server (URL not published) |
| GitLab + Google Runner Up, $3,500 | "Aegis" (which repo is unverified) | likely [35550883](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35550883) or [35647665](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35647665) | 1 each | 0 / 1 | none checked |
| GitLab + Anthropic Grand, $10,000 | GraphDev | [35368827](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827) | 1 (Zelong Wang) | 2 of 26 | [graphdev-demo.fly.dev](https://graphdev-demo.fly.dev) (blocked here) |
| GitLab + Anthropic Runner Up, $3,500 | DocSync | [2125704](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704) | 2 (Felix Detry, Nicola Invernizzi) | 20 of 91 | none |
| Green Agent, $3,000 | GreenPipe | [34754046](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34754046) (another catalog "GreenPipe" has no project; unverified which won) | 1 (Noura Hosny) | 15 of 87 | none |
| Honorable Mention (6 x $500), Sustainable Design Bonus (4 x $500) | not retrieved | | | | |

**LORE (Grand Prize).** A "multi-agent system on the GitLab Duo Agent Platform that gives your codebase institutional memory" [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311/-/blob/main/README.md)]. A triage router dispatches to specialist agents (pre-mortem on new issues, five-layer MR review, decision extraction after merge, health audit, onboarding brief, commit ledger), plus "LORE Ask" and "LORE Migrate"; memory lives in the project wiki; a Python CLI ships "43 passing tests" and a Pages dashboard; decisions carry carbon estimates. Story: "Teams don't break architecture because they're careless. They break it because: The people who understood the original decisions leave". Persona: Claude lets "LORE speak as a slightly haunted senior engineer who has seen things break." Autonomy: it reviews and records on its own but "LORE doesn't block the merge"; the developer answers `lore: intentional`, `lore: accidental` or `lore: discuss`. Proof: [MR !10](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311/-/merge_requests/10) shows the flow flagging a cache change against "Memory #001", then superseding it after the developer's reply. Why it likely won: a real, human problem (knowledge loss), a full issue-to-merge loop, visible proof, and engineering beyond prompts.

**Time-Traveler (Most Technically Impressive).** Eight agents plus a flow that clone a production stack per MR on a GCP VM through an MCP bridge, score each SQL migration 1 to 10 with rollback SQL, seed realistic data, smoke-test, and only then deploy; the deployer "confirms with you first" [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572/-/blob/main/README.md)]. Story in [DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572/-/blob/main/DEVPOST.md): "Picture this: it's 11pm. You've been staring at the same PR for 20 minutes. CI is green, the diff looks fine, your team approved it. You hit merge. Then your phone lights up." The README notes that the video shows an earlier MR and lists "Updates Since Demo Recording". Why it likely won: real infrastructure doing real migrations, with a human gate at the dangerous step.

**RedAgent (Most Impactful).** An adversarial testing framework: a Python SDK intercepts an AI agent's tool calls and injects crafted responses to expose prompt injection, false data trust, state corruption and privilege escalation; three catalog agents and a flow map the attack surface and post findings; a CI job runs on every MR [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156/-/blob/main/README.md)]. Uses Claude Sonnet 4 through the GitLab AI Gateway and Gemini 2.0 Flash locally. GitLab staff had to warn the author: "your flow has been posting comments on production issues ... please avoid commenting etc" ([issue #24](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156/-/work_items/24) [D]). It still won, so judges weighed the idea (testing AI agents) above that slip.

**Launch Control (Easiest to Use).** A four-agent release gate (Planner, Security Analyst, Compliance Analyst, Release Coordinator) triggered by one MR mention; it posts GO, NEEDS_REVIEW or BLOCK with a risk score from policy-as-code YAML and opens one remediation issue per blocker; a React dashboard runs on Vercel [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/README.md)]. Story in [docs/DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/docs/DEVPOST.md): "Every engineering team has shipped a release they shouldn't have." The video was rendered in code with Remotion: 5,393 frames at 30 fps (179.8 seconds), 12 scenes, background music; the opening shows a "73%" figure "of production incidents trace back to inadequate release checks" (no source given) and asks "What if one @mention could replace it all?" ([Root.tsx](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/remotion-video/src/Root.tsx), [DemoVideo.tsx](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/remotion-video/src/DemoVideo.tsx), [demo-script.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/docs/demo-script.md) [D]). The search excerpt praised "polished UX and solid infrastructure" [S].

**Gitdefender (GitLab + Google Grand).** Scores open-source MRs for "AI-generated slop": a five-agent flow extracts 58 features and posts a review plus an internal note; an IDE agent sends the features to a FastAPI scoring server on Cloud Run (River adaptive random forest, Cloud SQL, GCS, Terraform), pre-trained on "896 real GitLab MRs", and learns from each merge or close [D, [DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144/-/blob/main/DEVPOST.md)]. Autonomy: "The maintainer just keeps saying "yes" to move to the next step." The video script opens: "You've probably seen the headlines - open source maintainers drowning in AI-generated slop MRs, burning out, GitHub even floating the idea of a PR kill switch." ([SCRIPT.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144/-/blob/main/SCRIPT.md) [D]). It also documents a constraint Alex should expect: "All agents and flows running in GitLab's cloud cannot make outbound HTTP requests".

**GraphDev (GitLab + Anthropic Grand).** Turns a codebase into a semantic graph (tree-sitter, embeddings, HDBSCAN clusters, UMAP layout), then a flow posts structural impact analysis on MRs and a chat agent "suggests fixes, developer approves, agent commits"; Claude runs through the GitLab AI Gateway with `injectGatewayToken`; a 3D graph runs on Fly.io [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827/-/blob/main/README.md)]. Opening problem line: "Vibe coding teams ship fast, but nobody fully understands what they built." The README ends with a "Prize Tracks" section mapping the build to each prize, and the plan called for a "3-min story: problem, graph visualization, agent in action, before/after" ([PLAN.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827/-/blob/main/PLAN.md) [D]). Its first pipeline ran on 2026-03-24, the day before the deadline, and its commit dates start 2026-03-19 [D], so it was built in about a week.

**DocSync (GitLab + Anthropic Runner Up).** Three agents run after a merge: Detector finds doc drift with a confidence score, Writer opens a doc-fix MR when confidence is at least 0.5 or files an issue otherwise, Reviewer checks the fix against the code; "No auto-merge - human approval is always required on the doc-fix MR" [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704/-/blob/main/README.md)]. [MR !16](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704/-/merge_requests/16) shows the loop: five drifts fixed, then "DocSync Review: APPROVED". Small, clear, honest scope.

**GreenPipe (Green Agent).** Computes a Software Carbon Intensity score (ISO/IEC 21031:2024) for a CI pipeline, detects 13 waste patterns, benchmarks against 200 real pipelines, and opens an optimized `.gitlab-ci.yml` MR validated with the CI linter; it also reports its own carbon cost [D, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34754046/-/blob/main/README.md)]. Directly relevant to October's environmental prize, which asks for SCI numbers.

**Aegis (GitLab + Google Runner Up, repo unverified).** The AI Catalog lists at least six "Aegis" projects. The two built on Google Cloud are [Aegis release safety](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35550883) (seven agents, XGBoost failure prediction with SHAP, Vertex AI, BigQuery, GKE, Terraform) and [Aegis Contextual Architect](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35647665) ("performs deep reasoning on Google Cloud") [D]. Which one won is unverified.

## Non-winners sampled

June entries from [gitlab-ai-hackathon/transcend](https://gitlab.com/gitlab-ai-hackathon/transcend). Winner status is unknown for every one of them (see "Winners"); most of the 265 eligible Showcase projects did not win anything, so each line is mainly a contrast with the AI Hackathon winners' traits. Metrics are from my scan [D]; "catalog" is public AI Catalog items, "sessions" is Duo flow session pipelines.

1. [Impact Engine](https://gitlab.com/gitlab-ai-hackathon/transcend/34562572) (Prateek Srivastava, March winner): pre-merge risk oracle on Orbit with an adversarial critic that re-checks every claim, one GO/REVIEW/NO-GO verdict, then "stops and waits for a human to approve"; 12 catalog items, 43 pipelines but 0 flow sessions, solo. Has every winner trait except visible flow runs.
2. [NEXUS](https://gitlab.com/gitlab-ai-hackathon/transcend/39330880) (monika_k1): decisions anchored to the code graph, migration coordinator that opened "7 child issues across 2 projects", reorg simulator, return-from-leave catch-up; strong personas ("She comes back from three months of maternity leave"); 8 catalog items, 16 sessions, Pages dashboard. Very close to LORE in concept and demo, so weaker on originality.
3. [AFTERMATH](https://gitlab.com/gitlab-ai-hackathon/transcend/35450945) (Rudra Veer Singh Rathore): autonomous post-mortem that walks Orbit from incident back to the decision; 11 catalog items, 64 sessions, 163 pipelines. Strong activity; its claim that a post-mortem costs 8 to 40 hours has no source.
4. [Aftershock](https://gitlab.com/gitlab-ai-hackathon/transcend/39516010) (AmanM006): cross-repo blast radius with three demo repos, MR comment, heads-up issues downstream and a radar issue; README maps itself to each criterion; 2:30 scripted demo; 5 catalog items but only 4 sessions. Crowded theme.
5. [Switchyard](https://gitlab.com/gitlab-ai-hackathon/transcend/19746610) (Rithish-Kesav): reasons across all open MRs to find logical collisions Git cannot see and proposes a merge order; sharp pain example; 5 sessions; no catalog items found under this project although the README says 3 agents and a flow were published.
6. [Downwind](https://gitlab.com/gitlab-ai-hackathon/transcend/35554492) (Mark Brazinski): forward impact walk across packages with ownership blind spots, "70-scenario eval, 207 tests", cold-tested on psf/requests; 36 sessions. Rigorous, but it is a "scout, not a gate" in a crowded theme.
7. [Dead Code Finder](https://gitlab.com/gitlab-ai-hackathon/transcend/39335192) (Needy4u): deliberately picked "a narrower, less crowded question" ("is anyone calling this at all?") and is explicit about what static analysis cannot prove; 17 sessions, 1 catalog item. Honest and narrow, but read-only with small impact.
8. [Evidence-First Reviewer](https://gitlab.com/gitlab-ai-hackathon/transcend/3757837) (fongse): every review claim backed by a runnable Orbit query; links a "2-minute demo"; 16 sessions; the author also landed 4 Contribute-track MRs. Clear idea, thin product (9 files).
9. [Backtrace](https://gitlab.com/gitlab-ai-hackathon/transcend/7963149) (Vani Chitkara): incident to deploy to MR to author, posts a ranked root cause and takes mitigation actions; 2 a.m. on-call story also told on dev.to ([content issue #79](https://gitlab.com/gitlab-community/community-members/content/-/work_items/79)); 17 sessions. Good story; small repo (13 files).
10. [Orbit AI Engineering Manager](https://gitlab.com/gitlab-ai-hackathon/transcend/26431636) (Rishikesh63): chases stalled reviews, rebalances work, predicts sprint completion; opens with an unsourced "60% of their time" claim; 7 sessions, 9 commits. Broad promise, little proof.
11. [ReachGate](https://gitlab.com/gitlab-ai-hackathon/transcend/39037247) (MoAz06): vulnerability reachability triage with graph-path evidence and a deterministic policy engine, cites a Datadog study; 71 push pipelines but no flow sessions. Strong engineering whose agent run is not visible in GitLab.
12. [PatchCascade](https://gitlab.com/gitlab-ai-hackathon/transcend/38828481) (Samfresh-ai): "A proof layer for autonomous coding agents"; 90 files and one of the longest READMEs, but zero pipelines. Nothing shows it running on GitLab.
13. [Transcend](https://gitlab.com/gitlab-ai-hackathon/transcend/26388507) (poojapatel97): a generic bootstrapped Python template ("AI-assisted development with GitLab Duo") with no Orbit use; 8 files. Fails the theme check.
14. [xeer](https://gitlab.com/gitlab-ai-hackathon/transcend/39125811) (theRealNexa): a PDF and EPUB reader whose commits start 2026-05-27, before the event; off-theme. Plus 132 workspaces like [25337378](https://gitlab.com/gitlab-ai-hackathon/transcend/25337378) that never went past the initial commit.

What the weaker entries lacked, compared with the March winners: no visible run on GitLab (no flow sessions, no agent-written MR or issue), a crowded idea told without a sharper angle, unsourced statistics instead of a concrete scene, read-only output with no action, or no Orbit use at all.

## What GitLab judges rewarded (from evidence)

Evidence base: the 9 AI Hackathon winners above (same GitLab team, with Google and Anthropic), GitLab's written briefs for March, June and October, and GitLab staff notes. June winners could not be checked, so treat these as the best available pattern, not a June result.

1. **A felt pain told as a story.** GitLab asked for it every time. March: "The best submissions will tell a story: here's the pain, here's how the agent solves it, here's what changes for developers." ([onboarding template](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2012) [D]). June: "Your submission should tell a story" [D]. Winners opened on a person or a scene: maintainers "drowning in AI-generated slop MRs" (Gitdefender), "it's 11pm" (Time-Traveler), "The people who understood the original decisions leave" (LORE), "shipped a release they shouldn't have" (Launch Control).
2. **Act on triggers, not chat.** March: "Chat alone won't qualify. We want to see agents that react to triggers and take action." [D]. Every winner writes into GitLab: MR reviews and memory (LORE), doc-fix MRs (DocSync), remediation issues (Launch Control), optimized CI MRs (GreenPipe).
3. **Several specialists with clear jobs.** LORE (router plus specialists), Time-Traveler (8 agents), Gitdefender (5), Launch Control (4), DocSync (3), Aegis (7). Each agent has a named role and a short tool list.
4. **Real engineering under the prompts.** Tests (LORE "43 passing tests"), a trained model (Gitdefender on 896 MRs), a parser and graph (GraphDev), policy-as-code (Launch Control), real Postgres migrations (Time-Traveler), a standard metric (GreenPipe's SCI). October now says this outright: "a complete, coherent workflow rather than a proof of concept" [D].
5. **A human gate on risky steps.** No winner I opened merges or deploys without a person: LORE "doesn't block the merge" and waits for a reply, DocSync has "No auto-merge", Time-Traveler's deployer "confirms with you first", Gitdefender's maintainer "keeps saying "yes"". In October terms these are Assisted or Supervised designs; I found no fully hands-off March winner, so a credible hands-off loop would be new ground (and is worth $5,000 per path in October [S]).
6. **Proof inside GitLab.** Winners left agent-written MRs, notes and issues that judges can click (LORE !10, DocSync !16, Launch Control's issues #2 to #7, GreenPipe's flow-written SCI report issues #13 to #20) and many flow sessions (LORE 24, DocSync 20, RedAgent 19, GreenPipe 15). In June, only 66 of 312 workspaces (about one in five) show any flow session.
7. **Sponsor tech used for real.** The Google prize went to Cloud Run plus Cloud SQL, GCS and Terraform (Gitdefender); the Anthropic prizes went to Claude run through the GitLab AI Gateway (GraphDev's `injectGatewayToken`, DocSync). October scores Google Cloud deployment directly (up to +0.2).
8. **Measured sustainability.** GreenPipe won the green prize with ISO SCI numbers and self-accounting; LORE and Launch Control added carbon or "Green Metrics" views. October's environmental prize asks for SCI numbers.
9. **Presentation that is easy to follow.** Launch Control rendered a timed, scene-by-scene video in code and deployed a live dashboard "Judges can visit this URL right now" ([demo-script.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/docs/demo-script.md) [D]); Gitdefender scripted every line. GraphDev's README mapped the build to each prize. October scores the video on its own.
10. **Solo builders win.** 7 of the 9 winners I opened show one committer.
11. **Noise is tolerated once, not liked.** RedAgent won despite a staff warning about commenting on production issues; in June Lee Tickett asked entrants to stop pinging the team. Keep agents inside your own projects.

## Practical lessons for Alex from June

- Use the provisioned group workspace: "Custom flows require a group namespace, not personal" [D].
- Keep em dashes out of flow YAML: they "get silently corrupted in the editor" [D]. Our no-dash rule already covers this.
- Flows on GitLab's runners could not make outbound HTTP calls in March or June (Gitdefender, [#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D]). Route external calls through CI jobs or a deployed service, and check whether October's platform changed this (unverified).
- `CI_JOB_TOKEN` could not post MR notes in June [D]. Plan a token stored as a masked CI/CD variable for agent comments.
- New accounts needed a credit card to run CI in June [D]. Check this before the first pipeline.
- Make sure flows actually run in GitLab, and leave the runs and the agent-written MRs and issues in place for judges.

## Blocked

| URL or resource | Result |
|---|---|
| https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/ (June results) | curl: CONNECT 403; WebFetch: EGRESS_BLOCKED for about.gitlab.com |
| https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/ | WebFetch: EGRESS_BLOCKED |
| awskws.duckdns.org, thenote.app, backiee.wasmer.app (copies of GitLab pages seen in search results) | CONNECT 403 or EGRESS_BLOCKED |
| https://forum.gitlab.com/t/gitlab-ai-hackathon-2026-meet-the-winners/133590 | EGRESS_BLOCKED |
| devpost.com, gitlab.devpost.com, gitlab-transcend.devpost.com (all pages) | blocked (known in advance; one connectivity check only) |
| youtube.com, youtu.be, m.youtube.com, i.ytimg.com, noembed.com, piped and invidious front ends | CONNECT 403 or EGRESS_BLOCKED; YouTube Data API answered 403 (needs an API key) |
| contributors.gitlab.com | CONNECT 403 |
| graphdev-demo.fly.dev, launch-control-six.vercel.app, *.gitlab.io Pages sites | CONNECT failed, so live demos were not checked |
| dev.to, medium.com, linkedin.com, x.com, reddit.com | CONNECT failed |
| gitlab.com: notes via REST (401, GraphQL worked), team-task #1133 and #1157 (404, likely confidential), about-gitlab-com repo (repository 404, MRs 403), blog pitch project (404), blob search (401), user and achievement lookups via GraphQL (no permission) | refused |
| WebSearch | "this turn's web search budget is used up (limit: 200 WebSearch calls per turn, shared by every agent in it)" from my third query onward |

### Searches to run when budget allows (to fill the June winners table)

1. `"gitlab-transcend-hackathon-orbit"` and `"GitLab Transcend Hackathon" winners Orbit` (the July 20 post).
2. `site:devpost.com/software "GitLab Transcend Hackathon" winner` and `"gitlab-transcend.devpost.com" prizes Showcase Contribute`.
3. Name checks against the leads above: `"Switchyard" GitLab Orbit`, `"Downwind" GitLab Orbit`, `"AFTERMATH" GitLab Orbit post-mortem`, `"Impact Engine" GitLab Orbit`, `"NEXUS" GitLab Orbit hackathon`, `"Contributor Compass" GitLab`.
4. For each June winner found: open the repo under [gitlab-ai-hackathon/transcend](https://gitlab.com/gitlab-ai-hackathon/transcend) (the workspace description gives the Devpost username) and rerun the checks in this file.
