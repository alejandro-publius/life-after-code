# Patterns: what past winners shared, and what it means for us

Part 2 of the research handoff. Written 2026-10-06 for Alex Velazquez (solo, Path A), entering Life After Code, the GitLab Transcend Hackathon (judges from GitLab, Google and Anthropic). Submissions close on 2026-10-27 at 13:00 UTC per the [official rules](https://gitlab-transcend.devpost.com/rules) (see [DECISIONS.md](DECISIONS.md)).

Inputs: every note in [research/winners/](research/winners/), the June lessons in [research/gitlab_guide_and_reference.md](research/gitlab_guide_and_reference.md), [FIELD.md](FIELD.md) and [codex/RULES_CHECK.md](codex/RULES_CHECK.md). No new web research was done. `docs/codex/web/` does not exist. Every count below was computed with Python from the coded table in Appendix A.

How to read it: "(inference)" marks my own conclusion. Links are the ones the notes give. Quotes keep the source words, except that long dashes in sources become " - " ([DECISIONS.md](DECISIONS.md)). A count reads "x of y known", because many fields could not be seen.

## Read this first

- **86 winners from 12 events are coded; 23 of them won at GitLab's own two events.**
- **GitLab winners left proof inside GitLab.** 16 of 21 known had flow runs, bot commits or agent-written MRs and issues in their own project. In June, all 4 Technological Implementation and Design winners had flow runs. None of the 4 Impact and Idea winners did.
- **They kept a human at the step that matters.** Of 22 known GitLab winners, 15 act only after a human yes: 9 at the outcome (mostly a human merge), 6 at each step. Only 1 acts alone. 15 of 21 known show the human control point as a feature.
- **They picked jobs outside the crowd.** 5 of 8 June winners came from the rare idea tiers, while 105 of 265 June entries sat in just two ideas.
- **They were solo and not flawless.** 17 of 21 known GitLab winners had one builder. 20 of 21 known had at least one flaw that the notes flag.
- **Losers lacked a run, a sharp idea or a voice.** 110 of 265 June entries had silent or missing demos. 12 of 14 known Feb non-winners in the sample showed no agent-made artifacts or published nothing.
- **Ten rules for our entry close the document (section 7).**

## 1. Method and denominators

### 1.1 Which projects count

Every project that the notes name as a winner and describe in at least one line is in the table. That gives 86 projects:

| Event | Sponsor group | Winners in the table | Evidence (A / B / C) | Official winner list | Notes file |
|---|---|---|---|---|---|
| GitLab Transcend, Jun 2026 | GitLab | 8 | 8 / 0 / 0 | GitLab's record in [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137), read directly | [gitlab-transcend-june-2026-winners.md](research/winners/gitlab-transcend-june-2026-winners.md) |
| GitLab AI Hackathon, Feb to Mar 2026 | GitLab | 15 | 0 / 13 / 2 | [winners post](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/), search excerpts only | [part 1](research/winners/gitlab-ai-hackathon-2026-part1.md), [part 2](research/winners/gitlab-ai-hackathon-2026-part2.md) |
| Google AI in Action 2025 (GitLab track) | Google (GitLab track) | 3 | 0 / 2 / 1 | [GitLab blog](https://about.gitlab.com/blog/ai-in-action-hackathon-celebrating-the-gitlab-innovations/), search excerpts only | [google-ai-in-action-2025.md](research/winners/google-ai-in-action-2025.md) |
| Built with Opus 4.6, Feb 2026 | Anthropic | 5 | 5 / 0 / 0 | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon), read | [anthropic-claude-code-hackathons-4-6-and-4-7.md](research/winners/anthropic-claude-code-hackathons-4-6-and-4-7.md) |
| Built with Opus 4.7, Apr 2026 | Anthropic | 6 | 5 / 0 / 1 | [claude.com post](https://claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon), read | same file |
| Claude Opus 4.8 Build Day, Jun 2026 | Anthropic | 3 | 3 / 0 / 0 | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon), read | [anthropic-build-day-mcp-datahub.md](research/winners/anthropic-build-day-mcp-datahub.md) |
| MCP's 1st Birthday, Nov 2025 | Anthropic (with Gradio) | 8 | 3 / 0 / 5 | [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte), read | same file |
| Build with DataHub, Jul to Aug 2026 | Other (DataHub) | 4 | 0 / 4 / 0 | winners post blocked; names from search excerpts and the repos | same file |
| Gemini Live Agent Challenge, 2026 | Google | 12 | 7 / 0 / 5 | [cloud.google.com post](https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-of-the-gemini-live-agent-challenge), read | [google-gemini-live-and-gke.md](research/winners/google-gemini-live-and-gke.md) |
| GKE Turns 10, 2025 | Google | 8 | 7 / 0 / 1 | [cloud.google.com post](https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-from-gke-hackathon), read | same file |
| ADK Hackathon, 2025 | Google | 8 | 8 / 0 / 0 | [cloud.google.com post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights), read | [google-adk-hackathon-2025.md](research/winners/google-adk-hackathon-2025.md) |
| Cloud Run Hackathon, 2025 | Google | 6 | 0 / 6 / 0 | [Devpost updates](https://run.devpost.com/updates), search excerpts only | [google-cloud-run-hackathon.md](research/winners/google-cloud-run-hackathon.md) |
| **All** | | **86** | 46 / 25 / 15 | | |

Named in the notes but not described, so not counted: 4 of the 6 Feb honorable mentions (not found), the 3 AI in Action MongoDB-track winners (not found), 3 of the 7 DataHub prize winners (not found), Cloud Run's Forge (name only), 9 more MCP's 1st Birthday places known only by name and handle (DevRel Campaign Generator, DataPass, FleetMind AI Agent, Drone Control MCP Server, Director's Cut, Snowman AI, The Emergent Show, Reachy Mini Choreography Generator, MYTHFORGE), and names from the discovery notes with no description (Zenith, Active Pulse, Dragonfruit, MCPHackers, Geo Calculator MCP, Modern Multiplayer RPG with MCP, Snoopfeed, OncOmix AI, SpeakAura AI, TriLink) ([_discovery_anthropic.md](research/winners/_discovery_anthropic.md), [_discovery_gitlab_google.md](research/winners/_discovery_gitlab_google.md)).

Two GitLab rows rest on notes that disagree: part 1 names SecurityMonkey and stregent as Feb honorable mentions from search excerpts, while part 2 says no excerpt named any. Both stay in the table at evidence level C.

### 1.2 Denominators

- **(a) GitLab events:** the two events GitLab ran, June 2026 Transcend (8 winners) and the Feb to Mar 2026 AI Hackathon (15 winners): n = 23. The 3 winners of the GitLab track inside Google's AI in Action 2025 sit in the Google group, because Google hosted that event. Adding them to (a) changes no finding below; where it adds something, I say so.
- **(b) All events:** n = 86.
- Each count reads "x of y known", where y leaves out unknowns. The total n is in the column header or in brackets.

### 1.3 Evidence levels

- **A (46):** an official post or record was read, and the repo was read. For 3 of these the repo is a copy or a probable match (PostVisit.ai, Maieutic, CrossCut), and V-Commerce Studio's repo affiliation is unverified.
- **B (25):** the repo was read; the winner list came from search excerpts, the repo's own claim or a copy of the repo.
- **C (15):** a description only (a post line or a search excerpt).

### 1.4 How each column was coded

- **Team size:** visible human committers, or the post's credits when no repo was read. Devpost team lists were not seen.
- **Live URL:** "yes" when the notes list a public hosted URL for the product (README, repo About, post or config). None could be opened, because the hosts were blocked. "no" when the notes say none, localhost only, a placeholder, or links that return 404.
- **Personal story** (the brief's "named human story"): "yes" when the write-up tells the story of a specific real person: the builder, a relative, or a named or met user. A **role scene** (a group, a role, or a "you" scene such as "it's 11pm") and **none** (statistics, money, technical framing) both count as "no", and the table shows which. C rows with one line of text are "unknown".
- **Autonomy**, mapped to the brief's three labels:
  - **suggests:** advice, reports, drafts, or low-risk records only (comments, issues, metadata). No change to code, deploys or outside systems.
  - **acts with approval, each step:** a human yes before each consequential action, or the agent acts only on a human command.
  - **acts with approval, outcome:** the agent does the multi-step work alone, and a human approves the result, mostly by merging an MR only a human can merge.
  - **acts alone:** a consequential action happens with no human yes (merge, deploy, account lock, phone call, flight).
  - In October's terms (inference): "each step" is close to Assisted, "outcome" to Supervised, "acts alone" to Hands-off.
- **Approval as a feature:** the write-up presents a point where a human approves, rejects, overrides or decides, as part of the product.
- **Proof it ran:** the repo or its project holds artifacts the agent produced on real inputs: flow-run pipelines, bot commits, agent-written MRs, issues or notes, committed session logs, recorded runs or cached real results. Canned inputs do not count.
- **Tests or evals:** a test suite, a validator, or a measured eval, as the notes report it.
- **Arch. diagram:** "yes" when the notes mention a diagram (image, ASCII or Mermaid); "heading only" when the notes list an Architecture heading but say nothing of a diagram (counted as unknown); "no" when the notes say there is no diagram.
- **Video length:** only what the notes state. Nothing was watched.
- Extra fields used for the patterns but kept out of the table: sponsor tool depth (the notes' own rating: deep, medium or light), stated limits, flaws the notes flag, sustainability angle, video link in the README, and what is known of the video's opening.

### 1.5 What could not be measured

- **Devpost was blocked.** The write-ups of nearly all GitLab and Google winners were not read, except where the repo keeps a copy (Gitdefender, Time-Traveler, Launch Control, Aegis, GraphDev, DELTA, VibeCat, PermitScan AI, Hindsight). So were team lists, and which repo each June submission linked (CrossCut's repo match is "probable, not confirmed").
- **YouTube was blocked.** No video was watched. The opening of the video is known for 5 of 86 winners, all from scripts, plans or the video's source code. Length is known or claimed for 4 of 86.
- **Live demos were blocked.** No live URL was opened, so "live" means "listed".
- **about.gitlab.com was blocked.** The Feb winners come from search excerpts of the post, whose one-liners differ from the repos for Gitdefender and RedAgent. Repos were trusted.
- **Losers are GitLab only.** The notes sample non-winners from June 2026 and Feb to Mar 2026. No Google or Anthropic non-winners were sampled.
- **Depth of checking differs by event.** The GitLab notes audited each repo (flow runs, bot commits, CI jobs). The others did lighter checks. So "proof it ran" and "flaw" are mostly unknown outside GitLab, and low flaw counts there do not mean cleaner entries (inference).

## 2. The table

Appendix A holds all 86 rows, one per winner, with the 12 fields the brief asked for plus prize and a short note. Every count in section 3 comes from that table.

## 3. Patterns

### 3.1 Problem framing: one plain job, outside the crowd, with a number

| Measure | GitLab events | All events |
|---|---|---|
| June winners from the rare idea tiers (GitLab's count) | 5 of 8 | not measured elsewhere |
| June entries in the two crowded ideas | 105 of 265 (69 pre-merge impact review, 36 onboarding aids) | |
| June READMEs that open with a plain job and a number or a person (June notes) | 6 of 8 | |
| A human in the framing (personal story or role scene) | 10 of 21 known | 38 of 69 known |

What winners did:

- **They chose a job outside the crowd.** GitLab's June note: "Most submissions clustered into a few crowded problem spaces (69 built pre-merge impact review, 36 built onboarding aids), but the field still produced genuinely novel work: 17 one-of-a-kind concepts and 20 two-of-a-kind. Five of the eight winners came from those rare tiers." ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)). The rare tiers held 37 to 57 projects at most, 14% to 22% of the field ([FIELD.md](FIELD.md)).
- **They stated one plain job, often with a number.** Carver "estimates what a legacy migration will cost before you commit to one", with "human ≈$54k · gen ≈$10" ([README](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946/-/blob/main/README.md)). CrossCut: "Run only the tests a change can possibly break", "Execution drops from 38 minutes to 2 minutes" ([README](https://gitlab.com/rahulgunwanistudy-2005/Crosscut/-/blob/master/README.md)). Stayed Shipped: "Merged is not done. Shipped and stayed shipped is done." ([README](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648/-/blob/main/README.md)). BugFlow: "Report one bug. Get nine fixes, forty tests, and a faster pipeline." ([README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34708497/-/blob/main/README.md)).
- **Each won on one axis.** In June a project could win only one prize, and the winners won on different axes: breadth of platform use (Sankofa), rigor (Stayed Shipped), a one-command interaction (Carver), a gated conversation (Marshal), a measurable saving (CrossCut, OrbitWeaver), novelty plus proof (Transcend), a new framing (Universal Agent OS) ([June notes](research/winners/gitlab-transcend-june-2026-winners.md), inference).
- **Feb winners took narrow angles in a crowded field** (inference from [FIELD.md](FIELD.md) keyword counts): 132 of 506 catalog projects did security review on merge requests, while winners did team memory (LORE), AI-slop scoring (Gitdefender), migration rehearsal on a copy of production (Time-Traveler; database migration safety appeared in 5 of 506), adversarial testing of AI agents (RedAgent), hidden sibling bugs (BugFlow) and a five-role Terraform review (TFGuardian).
- **Other sponsors framed it the same way.** Every Gemini Live and GKE post description "leads with a situation: a surgeon 'without breaking scrub', a family history, a driver reporting potholes, 'what to make for dinner'" ([Gemini and GKE notes](research/winners/google-gemini-live-and-gke.md)). 9 of 11 Claude Code winners came from the builder's own work, family or community ([Anthropic notes](research/winners/anthropic-claude-code-hackathons-4-6-and-4-7.md)).

What did not decide it:

- Strong execution can still win inside a crowded space: Sankofa, a blast-radius variant, won Technological Implementation 1st ([FIELD.md](FIELD.md), inference).
- A good story with a broad scope did not win: NEXUS had "The best human story in this set" but "a broad, many-agent scope instead of one job" ([June notes](research/winners/gitlab-transcend-june-2026-winners.md)).

October now: the crowded space is the post-merge release gatekeeper, 4 of the 7 known October ideas, and the judges' own reference project runs that loop ([FIELD.md](FIELD.md)).

### 3.2 The opening of the video and the write-up

| Measure | GitLab events | All events |
|---|---|---|
| Video opening known (script, plan or video source code; none watched) | 4 of 23 | 5 of 86 |
| ... of those, the pain or the problem within the first 25 seconds | 3 of 4 (the 4th planned silent text) | 4 of 5 |
| Video structure known, but not its opening | 3 of 23 | 5 of 86 |
| Video length known or claimed | 2 of 23 | 4 of 86 |
| Video link in the README | 4 of 15 known | 16 of 55 known |

The five known openings:

1. **Launch Control** (Feb, Easiest to Use). The repo holds a video coded in Remotion, 5,393 frames at 30 fps, "179.8s" ([DemoVideo.tsx](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/remotion-video/src/DemoVideo.tsx)). About 13 s of animated title scenes, then on screen "73%" / "of production incidents trace back to inadequate release checks" / "What if one @mention could replace it all?" ([TheProblem.tsx](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/remotion-video/src/scenes/TheProblem.tsx)); the voiceover starts at about 25 s. Whether this cut was submitted is unverified. The script's 0:00 to 0:15 line: "Release approvals are slow because teams manually gather security, compliance, and deployment evidence across multiple GitLab surfaces. Launch Control fixes this with AI-powered release orchestration." ([demo-script.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/docs/demo-script.md)).
2. **Gitdefender** (Feb, Google Cloud Grand Prize): "You've probably seen the headlines - open source maintainers drowning in AI-generated slop MRs, burning out, GitHub even floating the idea of a PR kill switch." ([SCRIPT.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144/-/blob/main/SCRIPT.md)).
3. **Marshal** (June, Design 2nd), a "Screen recording with voiceover": "Every large engineering org has the same story - a migration that's been '80% done' for six months." ([DEMO.md](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992/-/blob/main/DEMO.md)).
4. **Hindsight** (DataHub): "Opens with the real on-call pain (first 20 seconds → applicability criterion)" ([SUBMISSION.md](https://github.com/gmassello/hindsight/blob/main/SUBMISSION.md)).
5. **Universal Agent OS** (June, Idea 2nd): its script (in Turkish) planned "a silent, text-on-screen walkthrough with background music"; whether the final video has narration is unverified ([demo_video_script.md](https://gitlab.com/zyganali/universal-agent-os-gitlab-edition/-/blob/main/docs/demo_video_script.md)).

Structure known, not the opening: BugFlow's README lists six beats, starting with "one bug on a Go codebase with Chinese comments"; Medkit's spec says "Show a full patient encounter in 90 s" ([spec.md](https://raw.githubusercontent.com/bedriyan/medkit-app/main/spec.md)); GraphDev planned a "3-min story: problem, graph visualization, agent in action, before/after" ([PLAN.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827/-/blob/main/PLAN.md)); Time-Traveler's video "shows the core workflow (MR !6 - appointments feature, end-to-end)" ([README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572/-/blob/main/README.md)); CrossBeam's video had "Mayor Connor on camera, real contractor Cameron" (ARIA's planning notes, [win plan](https://raw.githubusercontent.com/zestones/Aria/main/docs/planning/M9-polish-e2e/win-plan-48h.md)).

Length known or claimed: Launch Control 179.8 s (coded), Hindsight "2:33" (stated), BugFlow "3-minute" (README), Wrench Board "3-minute" (README link). All sit at the 3-minute cap.

Sound: in June "110 of 265 had silent or missing demos", and the models could not settle Design, so "the panel resolved both by hand" ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)). The one June Design winner whose demo plan is in its repo (Marshal) planned a voiceover.

The write-up's opening:

- Six Feb winners keep their submission text in the repo (Gitdefender, Time-Traveler, Launch Control, Aegis, GraphDev, and most likely DELTA). The notes quote the framing of four, but not where in the text each line sits. Three frame a scene or a pain: "Picture this: it's 11pm. You've been staring at the same PR for 20 minutes." ([Time-Traveler DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572/-/blob/main/DEVPOST.md)); "Every engineering team has shipped a release they shouldn't have." ([Launch Control DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/docs/DEVPOST.md)); maintainers "getting bombarded with AI-generated MRs" ([Gitdefender DEVPOST.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144/-/blob/main/DEVPOST.md)). One frames a report: "The DORA 2025 report revealed a paradox" (Aegis, [SUBMISSION.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35550883/-/blob/main/SUBMISSION.md)).
- In June, 6 of 8 READMEs open with a plain job and a number or a person ([June notes](research/winners/gitlab-transcend-june-2026-winners.md)).

Inference: the evidence is thin (5 openings, all from scripts, plans or source code), but it points one way: the pain within the first 20 to 25 seconds, spoken. Launch Control's 13-second title sequence did not stop it winning Easiest to Use.

### 3.3 Live demo versus mockup

| Measure | GitLab events | All events |
|---|---|---|
| Hosted live URL listed | 6 of 21 known (June 1 of 8, Feb 5 of 13) | 41 of 73 known (Anthropic 15 of 19, Google 18 of 30) |
| Field baseline: custom READMEs linking a hosted app | June 7 of 148; Feb 6% of 496 | |
| A no-setup path for judges (replay of real runs, cached results, simulator, local or no-key mode) | at least 5 | at least 11 |
| Demo on a seeded or synthetic target | at least 10 | at least 13 |

- **On GitLab, the project itself was the demo.** Few June winners had a separate app (1 of 8: Marshal's Pages dashboard). Judges could click real issues, MRs and flow runs instead (section 3.4). Feb winners still linked a hosted app far more often than their field: 5 of 13 (Gitdefender's Cloud Run scorer, GraphDev, Time-Traveler, Launch Control, TFGuardian) against 6% of 496 custom READMEs.
- **No-setup paths for judges were common.** At least 11 winners gave judges a way in that needs no setup, several of them replays of real runs: an offline replay of a real live capture (Stayed Shipped), "Local Demo (No GitLab Required)" (Marshal), "No GCP account required - the API falls back gracefully" (Aegis), copy-paste curl steps (GraphDev), `./demo.sh quick` (DELTA), "Showcase" and "Run Live" buttons (CrossBeam), cached results "without an API key" (TARA), a simulator Space (Vehicle Diagnostic Assistant), a replay mode so "judges need no drone" (drone-copilot), a static replay of recorded runs (Hindsight), and "See it without a key" (Culprit).
- **Seeded targets were normal, and the honest ones said so.** At least 13 winners demoed on planted problems: a fake CVE story (Sankofa), an AngularJS app with "planted problems" (Carver), planted regressions (BugFlow), "intentionally stale documentation" (DocSync), a deliberately wasteful pipeline (CarbonLint), a clinic app with seeded fake data (Time-Traveler), 4 seeded CWEs (DELTA), an intentionally vulnerable app (Aegis), a fake assistant agent (RedAgent), an embedded target app (GraphDev), synthetic patients (ORION, PostVisit.ai), and "deliberately seeded, disclosed defects" (Paracelsus). Two did not label it: Aegis's headline model is trained on generated data and "The README does not say so", and BugFlow calls its built scenario "A real bug report from a customer support escalation" ([part 1](research/winners/gitlab-ai-hackathon-2026-part1.md), [part 2](research/winners/gitlab-ai-hackathon-2026-part2.md)).
- **A mock can win where humans judge the pitch.** CrossCut (Impact 1st) has no runnable Duo flow and its CI never ran. Its dashboard "Judge Mode" plays 8 timed scenes in about 32 seconds on localhost ([run/page.tsx](https://gitlab.com/rahulgunwanistudy-2005/Crosscut/-/blob/master/dashboard/src/app/run/page.tsx)), and its committed output is a no-op: "Running 0 of 91 tests (100% fewer)" ([crosscut-comment.md](https://gitlab.com/rahulgunwanistudy-2005/Crosscut/-/blob/master/crosscut-comment.md)). Impact was "resolved by hand". No such winner appears in Technological Implementation or Design (inference).
- **October rules make the video carry the proof.** Judges "may choose to judge based solely on the text description, images, and video provided in the Submission" ([rules](https://gitlab-transcend.devpost.com/rules)). If the live project goes down "you are not disqualified. But you may score lower, because judges will rely only on your video and repository" ([resources](https://gitlab-transcend.devpost.com/resources)). The Google Cloud bonus needs a public live URL.
- **Simulated October entries are at risk.** AfterMerge says "The demo is fully simulated" and no Duo use was found, so it "would likely fail" the pass or fail check as it stands (unverified) ([FIELD.md](FIELD.md)).

### 3.4 Proof that the agent really ran

| Measure | GitLab events | All events |
|---|---|---|
| Agent-made artifacts in the repo (flow runs, bot commits, agent MRs, issues or notes, committed run logs) | 16 of 21 known (June 4 of 8, Feb 12 of 13) | 25 of 32 known |
| June Technological Implementation and Design winners with flow runs | 4 of 4 | |
| June Impact and Idea winners with flow runs | 0 of 4 | |
| Field baseline | June: 66 of 312 workspaces ran any flow. Feb: 506 of 1,788 projects published anything to the AI Catalog | |

- **June was scored from the repo.** "Each eligible submission was packaged into a self-contained packet (write-up plus an evidence bundle pulled from the actual repo code) and scored by three models in independent sessions: Opus 4.8, GPT 5.5, and Gemini 3.1." Consensus gave "clear shortlists" for Technological Implementation and Quality of the Idea; humans settled Impact and Design, and "Humans picked every winner." ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)).
- **Winners left proof a judge can click.** LORE's bot opened [issue 9](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311/-/work_items/9), "LORE - Your institutional memory is at risk". [DocSync MR !16](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704/-/merge_requests/16) shows five drifts fixed, then "DocSync Review: APPROVED". Launch Control's README shows "Real output from MR !3 (posted automatically by the flow)". [Marshal issue #23](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992/-/work_items/23) shows analysis, "/approve", preview, "start phase 1", "start phase 2", "/status". TFGuardian's flow account wrote 64 of its 100 most recent commits; BugFlow's opened 53 of its 69 issues; Pipeline Doctor's bot made 97 branches.
- **Volume did not decide.** Contributor Compass ran 481 flows and did not win; Carver won Design with 2 flow runs and 8 commits ([June notes](research/winners/gitlab-transcend-june-2026-winners.md)).
- **Outside GitLab, proof was rarely checked** (11 known of 63). Where checked, it was usually there (9 of 11): committed session logs and kept failure reports at Build Day, where "a logged fail→revise→pass cycle is the autonomy evidence; do not delete it" ([Tekton kickoff prompt](https://github.com/tangxiya-star/Tekton/blob/main/docs/KICKOFF_PROMPT.md)); recorded runs (Hindsight, Culprit, drone-copilot); cached real results (TARA); a real pull request (Project Blackbox); linked generated reports (GreenOps). The Build Day rubric scored Autonomy "from the session log" ([guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md)).
- **October requires it.** "The project's CI/CD pipeline history must be visible and show the automation running." ([rules](https://gitlab-transcend.devpost.com/rules)).

### 3.5 Depth of sponsor tools

| Measure | GitLab events | All events |
|---|---|---|
| Deep use, as the notes rate it | 11 of 21 known | 44 of 71 known |
| Light use | 3 of 21 known (all June Impact or Idea winners) | 5 of 71 known |
| June Technological Implementation and Design winners rated deep or medium | 4 of 4 | |

- **On GitLab, deep meant triggers and narrow agents, not chat.** The Feb brief: "Chat alone won't qualify. We want to see agents that react to triggers and take action." ([onboarding issue](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/621485/-/work_items/1)). Winners used several narrow agents with scoped tools (Launch Control: "Each agent is scoped to exactly 5 tools", [flow](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258/-/blob/main/.gitlab/duo/flows/release-evaluation.yaml)), native tools (Stayed Shipped's `get_graph_schema` and `query_graph`, "VERIFIED 2026-06-17 against the tool dropdown", [flow](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648/-/blob/main/duo/flow/stayed-shipped-audit.yaml)), execution config with `setup_script` and `network_policy` (Marshal, DELTA, TFGuardian), catalog versions that show iteration (TFGuardian v1.26.0, DELTA v1.10.0) and time boxes (of the five Feb green winners, "Every flow except CarbonLint's sets a 120 to 600 s timeout per step"; TFGuardian: "Do NOT repeat a step more than 3 times", [flow](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/159555/-/blob/main/flows/terraguard-upgrade.yml)).
- **Sponsor prizes went to sponsor depth.** The Google prizes went to Cloud Run plus Cloud SQL, GCS and Terraform (Gitdefender) and to GKE, Vertex AI and BigQuery through Terraform (Aegis). The Anthropic prizes went to Claude running inside GitLab through the AI Gateway: GraphDev's Claude Code external agent with `injectGatewayToken: true` ([graphdev.yaml](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827/-/blob/main/.gitlab/duo/flows/graphdev.yaml)) and DocSync: "All three agents use Claude via the GitLab AI Gateway" ([README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704/-/blob/main/README.md)).
- **At GitLab events, light use won only where the idea or pitch was judged:** CrossCut, OrbitWeaver and Universal Agent OS, all June Impact or Idea winners. The other two light winners placed lower elsewhere: Agent Anansi (3rd in AI in Action's GitLab track) and NeroFashion (a GKE regional prize).
- **Google winners named each feature.** ADK sub-agents and tool callbacks, Live API barge-in, context window compression, session resumption, affective dialog, the official A2A SDK. All 7 Gemini repos read deploy to Cloud Run; all 7 GKE repos read ship Kubernetes manifests ([Gemini and GKE notes](research/winners/google-gemini-live-and-gke.md)).
- **Anthropic winners made the model do something only it can do, visibly** (vision on plans, schematics and roads; 1M context; long-running hosted agents). At Build Day the runtime model did not even have to be Claude; judges scored how Claude built it ([Build Day notes](research/winners/anthropic-build-day-mcp-datahub.md)).
- **Counterexample:** in AI in Action's GitLab track, "The Google side was light" for both readable winners (Gemini through an API key, one Cloud Run service) ([notes](research/winners/google-ai-in-action-2025.md)).
- **Baseline:** 26% of 496 Feb custom READMEs mention Google Cloud; 4 of 13 Feb winners used it (Gitdefender, Aegis, Time-Traveler's VM, TFGuardian's Cloud Run dashboard).
- **October:** "Projects deployed on Google Cloud are eligible for up to 0.2 bonus points", with the deploy code in the repo and a public live URL ([rules](https://gitlab-transcend.devpost.com/rules), [resources](https://gitlab-transcend.devpost.com/resources)).

### 3.6 Autonomy shown, and human approval as a feature

| Measure | GitLab events | All events |
|---|---|---|
| Suggests | 6 of 22 known | 35 of 76 known |
| Acts with approval | 15 of 22 known (6 each step, 9 at the outcome) | 30 of 76 known (19 each step, 11 at the outcome) |
| Acts alone | 1 of 22 known (CrossCut) | 11 of 76 known |
| Human approval or control shown as a feature | 15 of 21 known | 32 of 72 known |
| ... among agents that act (approval or alone) | 12 of 15 known | 22 of 37 known |
| Field baseline (Feb custom READMEs) | 17% mention human approval or review; 6% promise full autonomy | |

- **GitLab winners stopped at a human for anything that mattered.** "No winner merges or deploys without a yes" ([part 1](research/winners/gitlab-ai-hackathon-2026-part1.md)). Carver: "`main` is NEVER modified - everything waits for a human to review and merge." ([flow](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946/-/blob/main/flows/carver-handoff.flow.yml)). Marshal: "Each invocation handles exactly one phase, with a human approval gate between each" ([README](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992/-/blob/main/README.md)). DocSync: "No auto-merge - human approval is always required on the doc-fix MR." Gitdefender: "The maintainer just keeps saying 'yes' to move to the next step." LORE: "LORE doesn't block the merge. But it doesn't forget you saw the warning." ([README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311/-/blob/main/README.md)).
- **The one GitLab winner that acts alone shows an override.** CrossCut picks which tests run, and says: "Add the **`crosscut:full`** label or comment **`/crosscut full`** to run the entire suite." ([crosscut-comment.md](https://gitlab.com/rahulgunwanistudy-2005/Crosscut/-/blob/master/crosscut-comment.md)).
- **Other events put code gates under the model.** A `SafetyGuard` ([drone-copilot](https://github.com/BryenInsights/drone-copilot/blob/main/client/src/drone/safety_guard.py)), a policy gate with "Deterministic rules. No LLM." ([JohnKeats.AI](https://github.com/johnkeats-ai/johnkeats-ai/blob/main/backend/app/agents/policy_gate.py)), a risk-keyword gate ([VibeCat](https://github.com/Two-Weeks-Team/vibeCat/blob/master/backend/realtime-gateway/internal/ws/navigator.go)), a "Proceed" modal for risky plans ([Moonwalk](https://github.com/OactoDev/Moonwalk/blob/main/backend/agent/core_v2.py)), a safe-executor function ([GreenOps](https://github.com/niksm7/GreenOps/blob/master/greenops_agent/agent.py)), a row-count gate that "refused to open the PR" ([Culprit](https://github.com/JonathanSolvesProblems/culprit)).
- **Acting alone did win elsewhere.** SalesShortcut (ADK grand prize) phones and emails leads with no approval step; drone-copilot flies missions alone inside its safety guard; Agentic CICD (AI in Action GitLab track, level C) is described as making releases and rollbacks "without immediate human intervention". Vigil AI locks bank accounts with no human and got an honorable mention; its README lists "**Human-in-the-Loop**: Add approval workflow for high-stakes enforcement actions" as future work ([README](https://github.com/ayanliger/gke-turns10-hackathon-vigil/blob/master/README.md)).
- **Autonomy was made visible.** The videos could not be seen, but the repos show it: Marshal's issue #23 loop; Sim Francisco's session log with about six human messages in about 395,000 characters; Tekton's `npm run demo:corrupt`, "so the audience sees the verifier refuse it"; CrossBeam's "Run Live" button to "watch the agent work".
- **Losers promised the most autonomy.** The loudest "zero human" and "sentient" pitches in the Feb sample won nothing (section 4.2).
- **October's levels (inference).** By the coding above, most past GitLab winners sit in Supervised (9 stop at an outcome gate) or Assisted (6 ask at each step). October's theme pulls the other way: "Hands Off. How far can your agents go without you?" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)).

### 3.7 Human stories

| Measure | GitLab events | All events |
|---|---|---|
| Personal story (a specific real person) | 0 of 21 known | 13 of 69 known (Anthropic 11 of 17, Google 2 of 28) |
| Role scene (a group, a role or a "you" scene) | 10 of 21 known | 25 of 69 known |
| Neither (statistics, money or technical framing) | 11 of 21 known | 31 of 69 known |

- **GitLab winners used role scenes, not biographies:** "it's 11pm" (Time-Traveler), maintainers "drowning" (Gitdefender), "a senior engineer quietly repairing agent code days after the merge" (Stayed Shipped), "'80% done' for six months" (Marshal), "The people who understood the original decisions leave" (LORE), "a non-technical founder" (Universal Agent OS).
- **Anthropic winners told the builder's own story.** "I named this project after my daughter" (Elisa), "My father has 30 years of craft" (MaestrIA), a physician alone in an emergency department (Medkit), a microsoldering technician (Wrench Board). "And four out of five winners were not professional developers." ([4.6 post](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon), [4.7 post](https://claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon)).
- **Caveat (inference):** the Anthropic counts come from interview-style posts, while most GitLab and Google Devpost write-ups were not read. Part of the gap is the source, not the entries.
- **A story alone did not win.** NEXUS had "The best human story in this set" ("She opens an issue to refactor the payments client. She doesn't know nine other services call it."), and Backtrace had a 2 a.m. on-call story. Neither won ([June notes](research/winners/gitlab-transcend-june-2026-winners.md), [past editions](research/winners/gitlab-transcend-past-editions.md)).
- **GitLab asks for a story every time.** Feb: "The best submissions will tell a story: here's the pain, here's how the agent solves it, here's what changes for developers." June: "Your submission should tell a story" ([past editions](research/winners/gitlab-transcend-past-editions.md)). October's Presentation criterion asks whether the video communicates "what problem is solved, who it's for, and why it matters" ([rules](https://gitlab-transcend.devpost.com/rules)).

### 3.8 Polish and honesty about limits

| Measure | GitLab events | All events |
|---|---|---|
| At least one flaw flagged by the notes (overclaim, unsourced number, stale README, committed secret, missing file, a slip) | 20 of 21 known | 34 of 71 known |
| States its own limits | 8 of 21 known (June 5 of 8) | 22 of 38 known |
| Tests or evals | 14 of 14 known | 38 of 50 known |

- **Winners were not flawless.** Stayed Shipped's status table still said "Draft pending Duo platform access" after its flow ran. Unsourced numbers: Launch Control's "73%", DocSync's "50-70%". Committed demo secrets: GraphDev's API key, Time-Traveler's bearer token. Synthetic data not labelled: Aegis. Docs that disagree: Gitdefender (896 MRs against "50 recent MRs from the these 10 repos"), RedAgent (Gemini against Claude). Links to missing files: DocSync, Transcend. Claims beyond the code: DELTA's "650+ line system prompt" (66 lines now), CarbonLint's tool count, TFGuardian's 96% CO2 cut, which equals the example in its own prompt. Writing into other entrants' projects: Stayed Shipped, Marshal ([June notes](research/winners/gitlab-transcend-june-2026-winners.md), [part 1](research/winners/gitlab-ai-hackathon-2026-part1.md), [part 2](research/winners/gitlab-ai-hackathon-2026-part2.md)).
- **Honesty was a habit of strong entries.** "a one-sided alarm, by design" (Stayed Shipped); "Verified result: no." (Transcend); "Honest Status" and "Roadmap Honesty" (Universal Agent OS); "This boundary is stated openly" (Marshal); "Refuse to invent numbers" (Carver). All 4 known DataHub winners have an honesty section ("Honesty boundary", "Honest limits", "What is real", "What's real vs. synthetic").
- **Neither decided alone.** Dead Code Finder and ReachGate stated their limits and did not win. Kassandra reported "23 completed end-to-end runs out of 37 triggers" and was "The closest miss in this sample" ([part 2](research/winners/gitlab-ai-hackathon-2026-part2.md)).
- **Polish did not decide Google's top prizes.** ORION (Gemini grand prize) has no tests folder; cart-to-kitchen (GKE grand prize) has one commit and a plain README; the CO2-Aware assistant had the biggest claims and a judge-facing README and got an honorable mention ([Gemini and GKE notes](research/winners/google-gemini-live-and-gke.md)).
- **Tests were common but not enough.** Every June winner had tests (about 21 to 276), but so did non-winners: Downwind ("70-scenario eval, 207 tests") and Tremor ("119 passing tests").
- Inference: flaws did not stop wins in 2026, but October's judges can rely on the repo and video only, and the rules require the project to "function as depicted in the video and/or expressed in the text description" ([rules](https://gitlab-transcend.devpost.com/rules)). Each flaw above is an avoidable way to lose points.

### 3.9 README shape

| Measure | GitLab events | All events |
|---|---|---|
| Architecture diagram noted | 8 of 8 known (all Feb) | 42 of 48 known |
| Diagram or an Architecture heading | 16 of 16 known | 53 of 59 known |
| Video link in the README | 4 of 15 known | 16 of 55 known |
| Judge-facing section or doc mapping the build to criteria or prizes | at least 5 of 23 | at least 21 of 86 |
| Devpost text or video script kept in the repo | at least 8 of 23 | at least 14 of 86 |

- **Diagrams were near universal, and Google rubrics asked for them.** ADK's criterion asked "Have they included an architectural diagram?" and all 8 ADK winners had one; every Cloud Run repo read had "an architecture diagram or an ASCII flow" ([ADK notes](research/winners/google-adk-hackathon-2025.md), [Cloud Run notes](research/winners/google-cloud-run-hackathon.md)).
- **Judge-facing sections:** GraphDev "Prize Tracks", Time-Traveler "Prizes Targeted", DocSync "Hackathon Categories", CrossCut's "The Story" (the three parts of the Devpost story prompt), Transcend's "60-second proof (for judges)", PostVisit.ai "Hackathon Tracks", Sim Francisco's sections named after criteria, Culprit "For judges: where each criterion is answered", Project Blackbox's "For judges" map, Hindsight's SUBMISSION.md, ORION's "GCP Backend & Logs Demo (for Hackathon)", CO2-Aware "Key Demo Points for Judges", Particle Physics Agent's "Hackathon Submission", Rayan Memory's submission table, VibeCat's "Submission Assets", Agent Anansi's challenge checklist, plus the criteria maps in TARA's master plan, Medkit's "What wins prizes here", ARIA's PRD and win plan, Tekton's rubric file and GreenOps's Devpost headings.
- **Proof first.** Several put the proof above the explanation: Launch Control ("Live demo first", then "Real output from MR !3"), GraphDev ("Quick Links first"), TFGuardian (live dashboard and latest results), drone-copilot ("Try it without a drone" first), Tekton and Sim Francisco (live links at the top).
- **Length did not decide.** June winners' READMEs ran from 371 to 2,929 words (median about 1,920); the 8 compared non-winners ran from 845 to 2,782 (median about 1,160), but that sample was chosen for substantial READMEs. Sankofa won Technological Implementation 1st with 371 words.
- **Flow YAML lives in the repo.** All 5 June winners matched in the workspace scan "keep their flow or skill files in the repo even though flows are created in the UI" ([guide](research/gitlab_guide_and_reference.md)).
- **October requires** an MIT licence "detectable and visible at the top of the repository page", "all necessary source code, assets, and instructions", and, for the bonus, the Google Cloud deploy code in the repo ([rules](https://gitlab-transcend.devpost.com/rules)).

### 3.10 Team size and build time

| Measure | GitLab events | All events |
|---|---|---|
| Solo (one visible builder) | 17 of 21 known | 59 of 82 known |
| Two people | 4 of 21 known | 17 of 82 known |
| Three or more | 0 of 21 known | 6 of 82 known (all at Google or MCP events) |

- **Solo is the norm.** Caveat: team means visible committers or the post's credits, and several solo builders write "we".
- **AI coding help is normal.** At least 3 of 8 June winners show AI tools in commit metadata (Marshal's "Claude Code" author and Claude Sonnet 4.6 trailers; Claude Opus 4.8 trailers in Stayed Shipped and Universal Agent OS). CrossBeam's builder: "I didn't write a single line of code".
- **Short visible builds won in June.** 7 of 8 winners' GitLab history spans 5 days or less of a 2-week window: Sankofa one day, CrossCut's repo created 8 minutes before the deadline, OrbitWeaver one "Finalisation" commit. Some work happened elsewhere first: Stayed Shipped cites a "live run 2026-06-12"; Universal Agent OS's core dates from March.
- **Feb builds varied** across its 7-week window: BugFlow Feb 18 to Mar 25, GreenPipe Feb 24 to Mar 24, GraphDev about a week, TFGuardian Mar 19 to 25, CarbonLint mostly its last 2 days, DELTA's visible history about 12 hours.
- **Repeat entrants won.** Sankofa's and OrbitWeaver's authors had Feb workspaces. The same GitHub accounts won twice at Google events: giovannamoeller (Edu.AI, and the NeroFashion team) and M4RKUS28 (Nexora-AI and Piatto) (inference from account names). Two 4.6 winners later taught the 4.7 cohort, and ARIA studied CrossBeam.
- **Planning and the last day.** 8 of 11 Claude Code winners documented planning before the main build. "Next time, I'd reserve that entire last day just for producing the demo." (Virtual Puppet Theater, [4.7 post](https://claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon)).

### 3.11 Sustainability angle (GitLab events)

| Measure | Count |
|---|---|
| Feb winners with a sustainability angle | 9 of 13 known |
| Feb awards that went to sustainability | 5 of 13 named awards (Green Agent prize and 4 Sustainable Design bonuses) |
| Feb top-8 winners with a carbon note anyway | 4 of 8 (LORE, Aegis, Time-Traveler, Launch Control) |
| June winners | 0 of 8 (no green prize in June) |
| Feb field baseline | 40% of 496 custom READMEs; 73 of 506 catalog projects |

- **The bonus rewarded design, not slogans:** "Sustainable Design bonuses were awarded to the projects with exceptional sustainability practices in their design, from model optimization techniques to energy-efficient architecture choices." ([winners post](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/), search excerpt).
- **The green winners measured something.** An SCI score per ISO/IEC 21031:2024 with a benchmark of 200 real pipelines (GreenPipe candidate B, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34754046/-/blob/main/README.md)); 21 regions with Cloud Carbon Footprint and "Energy estimates are directional, not exact" (GreenPipe candidate A, [README](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35548558/-/blob/main/README.md)); a docs-only pipeline from "28 min" to "1 min" (BugFlow); "$556/mo → $21/mo" (TFGuardian); a diff-scoped model with a no-LLM fallback, because "Deterministic triage matters more than LLM triage." (DELTA, [PROJECT.md](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35701012/-/blob/main/PROJECT.md)); a 1 to 10 Green CI Score (CarbonLint). Which GreenPipe repo won is unverified; both measured.
- **Same theme, no measured run, no award:** Carbon Tracker (one global average, 475 gCO2/kWh), GreenPipeline AI ("60% lower carbon footprint" without a shown run), CarbonMerge (a "95%" claim without a shown run).
- **October has one green award.** Most Environmentally Impactful ($5,000) "should quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks"; entrants opt in on the submission form ([rules](https://gitlab-transcend.devpost.com/rules), [resources](https://gitlab-transcend.devpost.com/resources)).
- Inference: green helped where it was measured and tied to the main job. Feb paid 5 green awards; October pays 1.

## 4. What losers lacked

### 4.1 June 2026: 22 sampled non-winners

Sources: the 8 compared and the 6 "also scanned" in the [June notes](research/winners/gitlab-transcend-june-2026-winners.md), plus the 14 sampled in [past editions](research/winners/gitlab-transcend-past-editions.md); the union is 22 projects, none among the 8 winners. The 8 compared were chosen "to cover the busiest builders", so the sample leans toward active projects.

| What they lacked | Count | Projects |
|---|---|---|
| An uncrowded idea: in one of GitLab's two crowded clusters | 6 of 22 | [Contributor Compass](https://gitlab.com/gitlab-ai-hackathon/transcend/39109018), [Downwind](https://gitlab.com/gitlab-ai-hackathon/transcend/35554492), [Tremor](https://gitlab.com/gitlab-ai-hackathon/transcend/39301572), [Ripple](https://gitlab.com/gitlab-ai-hackathon/transcend/669256), [Impact Engine](https://gitlab.com/gitlab-ai-hackathon/transcend/34562572), [Aftershock](https://gitlab.com/gitlab-ai-hackathon/transcend/39516010) |
| ... or in a busy space (incident post-mortems, security reachability, MR review tools, about 10 entries each) | 5 of 22 | [AFTERMATH](https://gitlab.com/gitlab-ai-hackathon/transcend/35450945), [ReachGate](https://gitlab.com/gitlab-ai-hackathon/transcend/39037247), [Praetor](https://gitlab.com/gitlab-ai-hackathon/transcend/28344226), [Tether](https://gitlab.com/gitlab-ai-hackathon/transcend/34569267), [Backtrace](https://gitlab.com/gitlab-ai-hackathon/transcend/7963149) |
| Any visible flow run | 6 of 20 known | Tremor, ReachGate, Praetor, Tether, Impact Engine, [PatchCascade](https://gitlab.com/gitlab-ai-hackathon/transcend/38828481) |
| A product beyond a thin build | 5 of 22 | [Switchyard](https://gitlab.com/gitlab-ai-hackathon/transcend/19746610), [Evidence-First Reviewer](https://gitlab.com/gitlab-ai-hackathon/transcend/3757837), Backtrace, [Orbit AI Engineering Manager](https://gitlab.com/gitlab-ai-hackathon/transcend/26431636), [Transcend stub](https://gitlab.com/gitlab-ai-hackathon/transcend/26388507) |
| Sourced numbers | 2 of 22 | AFTERMATH ("8 to 40 hours"), Orbit AI Engineering Manager ("60% of their time") |
| One focused job | 2 of 22 | [NEXUS](https://gitlab.com/gitlab-ai-hackathon/transcend/39330880), Orbit AI Engineering Manager |
| Work done before the deadline | 2 of 22 | AFTERMATH (57 of 72 flow runs after it), [Slingshot](https://gitlab.com/gitlab-ai-hackathon/transcend/39207472) (8 commits after it) |
| Theme fit | 2 of 22 | Transcend stub (no Orbit use), [xeer](https://gitlab.com/gitlab-ai-hackathon/transcend/39125811) |
| Restraint | 1 of 22 | Contributor Compass (1,954 issues in a day) |

What they had: 14 of 20 known ran flows, a higher share than the winners (4 of 8). Downwind had "The most engineering in this set" (495 commits, "70-scenario eval, 207 tests"); NEXUS had the best story; [Dead Code Finder](https://gitlab.com/gitlab-ai-hackathon/transcend/39335192) stated its limits. Inference: activity, tests and honesty were common in June; the missing pieces were an uncrowded idea and one sharp axis.

The June field ([past editions](research/winners/gitlab-transcend-past-editions.md)): 132 of 312 workspaces never went past the initial commit; 66 of 312 ran a flow; 11 of 148 custom READMEs linked a YouTube video and 7 a hosted app; 76 of 148 said "blast radius". And 110 of 265 eligible entries had silent or missing demos ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)).

### 4.2 Feb to Mar 2026: 16 sampled non-winners and the field

Source: [part 2](research/winners/gitlab-ai-hackathon-2026-part2.md). Whether each was submitted on Devpost is unverified. Links use the group [2026-02-ai-hackathon](https://gitlab.com/groups/gitlab-community/community-projects/2026-02-ai-hackathon).

| What they lacked | Count | Projects |
|---|---|---|
| Agent-made artifacts, or any publish from the project | 12 of 14 known | [GreenPipeline AI](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/30158107), [EcoCI](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34560917), [VerdantFlow](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34577900), [Ifrit Omega](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/15122620), [Autonomous DevSecOps AI Platform](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/25830366), [EvoGuard](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35361944), [ShieldFlow AI](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/5255511), [GitLab AI Hackathon Planner](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/13603284), [MR Risk Sentinel](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34583627), [Carbon Tracker](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35602696), [CarbonMerge](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2699977), [Empty entry](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35553140) |
| Claims backed by a shown run (hype or unbacked numbers instead) | 5 of 16 | GreenPipeline AI, Ifrit Omega ("Sentient AGI-SecOps"), Autonomous DevSecOps AI Platform ("Zero Human Intervention"), EvoGuard ("The Invisible War in CI/CD"), CarbonMerge |
| A real build (thin README, few files or commits) | 5 of 16 | GreenPipeline AI, Ifrit Omega, MR Risk Sentinel, Carbon Tracker, Empty entry |
| Iteration (catalog items at v1.0.0 only) | 4 of 16 | GreenPipeline AI, [GuardianFlow](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/11482549), [Compliance Autopilot](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/27870198), CarbonMerge |
| A video or screenshots | 3 of 4 known | [Kassandra](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/3286613) (no video link), VerdantFlow, Compliance Autopilot |
| One focused problem | 2 of 16 | VerdantFlow ("Two unrelated problems in one pitch"), GuardianFlow ("four goals in one gate") |
| An explanation (template README) | 2 of 16 | [PerformanceSentinel](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34711761), Empty entry |
| Fit to the brief | 1 of 16 | GitLab AI Hackathon Planner (a tool for entrants, "Powered by GPT-4") |
| A sponsor or special-prize angle | 1 of 16 | Kassandra, "The closest miss in this sample" |

The Feb field (all 1,765 non-empty repos): 1,263 (72%) kept the one-line template README; only 506 of 1,788 projects published anything to the AI Catalog, and 425 a flow; 131 projects published a flow but never explained it. Of the 496 custom READMEs: 13% link a video, 6% a hosted app, 17% mention human approval or review, 6% promise full autonomy, 40% mention carbon, 26% Google Cloud, 51% Claude or Anthropic.

Winners against that field (Feb, 13 read): a hosted app 5 of 13 (38%, against 6%); human approval shown as a feature 9 of 13 (69%, against 17% that mention it); agent-made artifacts 12 of 13; a sustainability angle 9 of 13 (69%, against 40%). Two winners used "zero human" wording (BugFlow: "~20 minutes, zero human effort"; DELTA: "zero human intervention"), but both still stop at a human merge.

### 4.3 Not sampled

The notes hold no Google or Anthropic non-winners, so this section is GitLab only. The nearest signal elsewhere is the gap between honorable mentions and top prizes: the CO2-Aware assistant's unbacked claims, and VibeCat's demo tasks that were small "next to surgery or a flying drone" ([Gemini and GKE notes](research/winners/google-gemini-live-and-gke.md), inference).

## 5. Anti-patterns

1. **Building the idea everyone builds.** June: 69 pre-merge impact review and 36 onboarding entries of 265; 5 of 8 winners came from the rare tiers ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)). 11 of 22 sampled June non-winners sat in a crowded or busy space, including the entry with the most engineering (Downwind). October: the post-merge release gatekeeper is 4 of 7 known ideas ([FIELD.md](FIELD.md)).
2. **No visible run.** Impact Engine "Has every winner trait except visible flow runs"; ReachGate had 71 pipelines and no flow session; PatchCascade: "Nothing shows it running on GitLab." ([past editions](research/winners/gitlab-transcend-past-editions.md)). 12 of 14 known Feb non-winners showed no agent-made artifacts or published nothing. October requires CI history that shows "the automation running".
3. **Volume instead of value.** Contributor Compass's flow opened 1,954 issues on one day, 65 with the same title, "which reads as noise" ([June notes](research/winners/gitlab-transcend-june-2026-winners.md)). Staff asked entrants for "as little noise as possible" ([onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend/21418861/-/work_items/1)); the October epic wants "Gaming and AI-spam are kept out, so reviewer goodwill is protected" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)); a survey found "Incentives can favor quantity over quality" ([team-task#1329](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1329)).
4. **An agent that writes into other people's projects.** Stayed Shipped's service account "erroneously wrote to a **third-party** project" ([issue #1](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648/-/work_items/1)); Marshal opened a campaign issue in another entrant's project ([Downwind issue #5](https://gitlab.com/gitlab-ai-hackathon/transcend/35554492/-/work_items/5)); RedAgent was told "your flow has been posting comments on production issues ... please avoid commenting etc" ([issue #24](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156/-/work_items/24)). They still won (inference: tolerated once, not liked).
5. **A silent or missing demo.** 110 of 265 June entries; Design and Impact were then settled by hand. October scores the video as Presentation, one of five equal criteria, and judges may rely on the video and text alone.
6. **Promising "zero human" or "sentient" autonomy.** Ifrit Omega, Autonomous DevSecOps AI Platform and EvoGuard won nothing; 6% of Feb custom READMEs made such promises. GreenOps's README claims "Completely autonomous workflows" while its code asks the user first, a mismatch rather than a strength ([ADK notes](research/winners/google-adk-hackathon-2025.md)).
7. **Numbers without a source or a run.** "73%" (Launch Control), "50-70%" (DocSync), "8 to 40 hours" (AFTERMATH), "60% of their time" (Orbit AI Engineering Manager), "**25% reduction**" and "**99.9% uptime**" (CO2-Aware), "95% accuracy in priority assignment" (Agent Anansi), "60% lower carbon footprint" (GreenPipeline AI). October's Impact criterion asks whether the solution addresses the problem "based on what's demonstrated" ([rules](https://gitlab-transcend.devpost.com/rules)).
8. **Demo data dressed as real data.** Aegis's model reports "AUC 0.999 on 5,000 training samples" of generated data, and "The README does not say so"; BugFlow calls a planted scenario "A real bug report"; TFGuardian's "CO2 reduction 96%" equals the worked example in its own prompt ([agent](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/159555/-/blob/main/agents/tfguardian-greenops.yml)). Compare Paracelsus's "Honesty boundary" and Energy Agent AI's "Simulated Dataset with ClaudeAI". Our AGENTS.md rule 2 already forbids it.
9. **Secrets in a public repo.** GraphDev "publishes the demo API key in plain text"; Time-Traveler commits a bearer token in [.gitlab/duo-mcp.json](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572/-/blob/main/.gitlab/duo-mcp.json); Pipeline Doctor keeps a decoded service-account key as a job artifact ([.gitlab-ci.yml](https://gitlab.com/vanichitkara18/pipeline-doctor/-/blob/main/.gitlab-ci.yml)). October repos must be public.
10. **README and code that disagree, or a stale status.** Stayed Shipped's "Draft pending Duo platform access" after the flow ran; DELTA's "650+ line system prompt" (66 lines now); CarbonLint's "25 tools across 2 agents" (4 and 3 tools now, no `ci_linter`); DocSync and Transcend cite files that are not in the repo; Agent Anansi shows a "GitLab CI/CD Catalog" badge with no release. June's scoring packet read "the actual repo code".
11. **Flow files the platform cannot run, or never published.** CrossCut's and Universal Agent OS's flow files are not in the v1 flow shape; Autonomous DevSecOps kept its five flows in `.gitlab/workflows/`, "which the hackathon sync did not read"; GreenPipe candidate A's flow sat outside `flows/` and was not synced. Also: "Em dashes in flow YAML get silently corrupted in the editor (multiple teams)" ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)).
12. **Canned inputs presented as automation.** Agent Anansi's CI jobs post a hard-coded sample payload, so "the pipeline never reads the real MR or issues"; Pipeline Doctor's fix step never sees the real `.gitlab-ci.yml`, and one bot commit replaced a 61-line pipeline with 15 lines ([commit 594657a9](https://gitlab.com/vanichitkara18/pipeline-doctor/-/commit/594657a978d5a475b8dab6e603169c7b17c40336)). Both placed in 2025 (inference: riskier now that a repo evidence bundle is scored).
13. **Everything at once.** NEXUS ("a broad, many-agent scope instead of one job"), Orbit AI Engineering Manager ("Broad promise, little proof"), VerdantFlow, GuardianFlow. October: 3 of 7 known ideas pitch all-stage agent meshes ([FIELD.md](FIELD.md)).
14. **Built but never explained.** 131 Feb projects published a flow and kept the one-line template README (PerformanceSentinel: a flow at v1.6.0 and 63 commits); 72% of non-empty Feb repos kept the template.
15. **Work after the deadline.** AFTERMATH: "57 of its 72 flow runs and 18 of 58 commits came after the deadline"; Slingshot: 8 commits after it. October's FAQ: "Changes during judging put your eligibility at risk." ([resources](https://gitlab-transcend.devpost.com/resources)).
16. **Missing the required platform.** The June Transcend stub "Fails the theme check" (no Orbit); xeer was off-theme; the Feb Planner was off-brief. October: AfterMerge ("Nothing in the loop calls the network") and BABYDOV (no model at all) may fail the pass or fail check on "genuinely use GitLab AI features" (unverified) ([FIELD.md](FIELD.md)).

## 6. Mapping to Life After Code

### 6.1 The rules that shape the mapping

From [codex/RULES_CHECK.md](codex/RULES_CHECK.md), which quotes the [official rules](https://gitlab-transcend.devpost.com/rules):

- **Five equally weighted criteria (20% each by arithmetic):** Technological Implementation ("How thoroughly and skillfully does the project use GitLab to automate the post-code DevSecOps lifecycle? Does the code and pipeline config reflect genuine effort and a working, non-trivial implementation?"), Design ("a complete, coherent end-to-end workflow, not just a technical proof of concept"), Potential Impact ("a credible, specific case for solving a real problem for a real audience - and does the solution actually address that problem based on what's demonstrated?"), Innovation/Idea ("how inventively does it apply agentic automation compared to existing concepts?"), Presentation ("Does the video clearly demonstrate the automation running end-to-end? Does it communicate what problem is solved, who it's for, and why it matters?"). Google Cloud deployment adds up to 0.2, for a top score of 5.2.
- **Path A prizes by autonomy level:** Best Assisted Agent ($4,000, "you approve every step"), Best Supervised Agent ($4,000, "you approve the outcome, not the individual steps"), Best Hands-off Agent ($5,000, "you set the intent and walk away").
- **Special prizes:** Most Stages Covered ($5,000, one per path, "touch the most DevSecOps lifecycle steps ... in the most creative way"), Most Creative ($4,000, "The Project from either Path which scores highest in the Innovation/Idea judging criteria"), Most Environmentally Impactful ($5,000, must "quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks").
- **Prize limit:** "Each Project can win one (1) Prize from either Path A or Path B and one (1) Special Prize."
- **Judging may skip testing:** "Judges are not required to test the Project and may choose to judge based solely on the text description, images, and video provided in the Submission."
- **Required:** a public MIT-licensed GitLab repo, visible CI/CD history "show[ing] the automation running", a public YouTube video under three minutes, genuine GitLab Duo Agent Platform use (pass or fail), new work on or after October 5.

### 6.2 Each pattern against the criteria and prizes

"core" means the criterion or prize scores this directly; "helps" means indirectly; "low" means little effect.

| Pattern | Tech. impl. | Design | Impact | Innovation | Presentation | Assisted | Supervised | Hands-off | Most Stages | Most Creative | Most Env. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.1 One plain job outside the crowd, with a number | low | helps | core | core | helps | helps | helps | helps | tension: one job versus many stages | core | helps if the saving is measurable |
| 3.2 Pain and person in the first 20 s, spoken | low | low | helps | low | core | helps | helps | helps | helps | helps | helps |
| 3.3 Live URL and replays of real runs, no mockups | core (bonus needs a live URL) | core | helps | low | core | helps | helps | helps | helps | low | helps |
| 3.4 Proof the agent ran, left in GitLab | core | core | core | low | core | helps | core | core | core (each stage must be shown) | low | core |
| 3.5 Deep, named sponsor use | core | helps | low | helps | helps | helps | helps | helps | core | helps | helps |
| 3.6 Autonomy shown, human control as a feature | helps | core | helps | helps | core | core (approve each step) | core (approve the outcome) | inverse: show intent, code guardrails and a stop rule, no human in the middle | low | helps | low |
| 3.7 A real person in a real moment | low | low | core | low | core | helps | helps | helps | low | helps | helps |
| 3.8 Honest limits, clean repo, tests | core | helps | core | low | helps | helps | helps | helps | helps | low | core (credible numbers) |
| 3.9 README for a 60-second judge | helps | helps | helps | low | helps | helps | helps | helps | helps (map the stages) | low | helps (show the method) |
| 3.10 Solo, short, planned build | low | helps (finish one loop) | low | low | helps (a day for the video) | low | low | low | low | low | low |
| 3.11 Sustainability, measured with SCI | helps | low | helps | low | low | low | low | low | low | low | core |

### 6.3 What the mapping suggests for prize choice (inference)

- **One path prize plus one special prize.** The rules let an entrant choose the level: "build a project ... that fits within one of three levels of autonomy". So pick one level and make it unmistakable in the README and the video.
- **The evidence favours a Supervised or Assisted design; the theme favours Hands-off.** Past GitLab winners mostly approved the outcome (9 of 22 known) or each step (6 of 22); only 1 acted alone. October's theme is "Hands Off", and Hands-off pays $1,000 more. The October field so far has 3 of 7 known ideas claiming Path B Hands-off and 1 of 7 Path A with a human gate, so Path A Assisted and Supervised look thinly contested (small sample, [FIELD.md](FIELD.md)).
- **Special prize options differ in cost.** Most Creative needs no extra work beyond a high Innovation score, and June's Idea winners (Transcend, Universal Agent OS) won with no flow runs, on the concept and its proof. Most Stages Covered competes only within Path A and rewards breadth "in the most creative way"; the October field barely touches the configure and package stages ([FIELD.md](FIELD.md)). Most Environmentally Impactful needs an opt-in and SCI numbers; Feb gave 5 of 13 awards to measured green work, and October gives 1. Since only one special prize can be won, choose the one the core job earns without bending it.

## 7. Ten rules for our entry

1. **One job, outside the crowd, in one sentence with one number.** Not a release gatekeeper, not pre-merge impact review. (5 of 8 June winners came from rare tiers; 11 of 22 sampled June non-winners sat in crowded or busy spaces; 4 of 7 October ideas are release gatekeepers.)
2. **Real runs inside our own GitLab project, and leave the trail.** Flow runs, bot-made MRs, issues and comments, green CI history. (16 of 21 known GitLab winners; 4 of 4 June Technological Implementation and Design winners; the rules require visible CI history.)
3. **One human decision point, built in code and shown as a feature, and say which autonomy level we enter.** (15 of 22 known GitLab winners act only after a human yes; 12 of 15 known that act show it as a feature; only 1 acted alone.)
4. **A narrated video under 3:00 (aim for 2:40): person and pain in the first 20 seconds, then the loop running end to end on real GitLab objects.** (110 of 265 June demos were silent or missing; 4 of 5 known openings put the pain in the first 25 seconds; judges may judge on video and text only.)
5. **A real person in a real moment, plus a number we can prove.** (10 of 21 known GitLab winners framed a human scene; 11 of 17 known Anthropic winners told a personal story; NEXUS shows a story alone is not enough.)
6. **Code decides what is true, the model chooses where to look, and every loop is time-boxed. Ship tests and one eval with a number.** (Tests or evals in 38 of 50 known winners; 4 of the 5 Feb green winners set 120 to 600 s step timeouts; all 4 known DataHub winners let code, not the model, decide.)
7. **Deep, named sponsor use.** Duo flows on event triggers with narrow agents and scoped tools, flow YAML kept in the repo, Claude through GitLab, and a live Cloud Run URL for the 0.2 bonus. (11 of 21 known GitLab winners rated deep; at GitLab events light use won only in June Impact and Idea; Feb winners linked a hosted app 5 of 13 times against 6% of the field.)
8. **Honest and clean.** Label demo data in the UI, README and file names; state limits; cite every number; no secrets; README equal to the code. (20 of 21 known GitLab winners had a flaw the notes flag; June's scoring packet read the repo code; AGENTS.md rules 2, 6 and 7.)
9. **A README for a judge who reads for 60 seconds.** One-line job, demo link and demo MR first, an architecture diagram, a criteria and prize map, run steps, limits. Keep the Devpost text and video script in the repo. (Diagrams in 42 of 48 known winners; at least 21 winners had a judge-facing map.)
10. **Plan for one path prize plus one special prize, keep the agent inside our own project, and freeze everything at 13:00 UTC on October 27 until winners are announced.** (The prize limit is in the rules; Stayed Shipped and Marshal wrote into other projects; the FAQ says changes during judging put eligibility at risk.)

## Appendix A: every winner, coded

Codes are defined in section 1.4. "Personal story: no (role scene)" means a group, a role or a "you" scene; "heading only" means an Architecture heading with no diagram recorded. Links are the repo, or the post or Devpost page when no repo was found. Notes files: see section 1.1.

| # | Project | Event | Prize | Group | Ev. | Team | Live URL | Personal story | Autonomy | Approval as a feature | Proof it ran | Tests or evals | Arch. diagram | Video length | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Sankofa](https://gitlab.com/gitlab-ai-hackathon/transcend/34570711) | GitLab Transcend, Jun 2026 | Tech. Impl. 1st | GitLab | A | 1 | no | no | suggests | no | yes | yes | heading only | unknown | 35 of 38 flow runs; writes only comments and issues |
| 2 | [Stayed Shipped](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648) | GitLab Transcend, Jun 2026 | Tech. Impl. 2nd | GitLab | A | 1 | no | no (role scene) | suggests | yes | yes | yes | unknown | unknown | dry-run default; about 276 tests |
| 3 | [Carver](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946) | GitLab Transcend, Jun 2026 | Design 1st | GitLab | A | 1 | no | no | approval: outcome | yes | yes | yes | heading only | unknown | one branch and one MR; main never modified |
| 4 | [Marshal](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992) | GitLab Transcend, Jun 2026 | Design 2nd | GitLab | A | 1 | yes | no (role scene) | approval: each step | yes | yes | yes | unknown | 3-minute voiceover script; length unknown | /approve gate per phase; Pages dashboard |
| 5 | [CrossCut](https://gitlab.com/rahulgunwanistudy-2005/Crosscut) | GitLab Transcend, Jun 2026 | Impact 1st | GitLab | A | 2 (likely) | no | no (role scene) | acts alone | yes | no | yes | heading only | unknown | repo match probable; team likely 2; /crosscut full override |
| 6 | [OrbitWeaver](https://gitlab.com/gitlab-ai-hackathon/transcend/35222941) | GitLab Transcend, Jun 2026 | Impact 2nd | GitLab | A | 1 | no | no (role scene) | approval: outcome | yes | no | yes | heading only | unknown | demo links 404; timed human baseline |
| 7 | [Transcend](https://gitlab.com/gitlab-ai-hackathon/transcend/3537494) | GitLab Transcend, Jun 2026 | Idea 1st | GitLab | A | 1 | no | no | suggests | no | no | yes | unknown | link in README; length unknown | benchmark '6 for 6' instead of flow runs |
| 8 | [Universal Agent OS](https://gitlab.com/zyganali/universal-agent-os-gitlab-edition) | GitLab Transcend, Jun 2026 | Idea 2nd | GitLab | A | 1 | no | no (role scene) | approval: each step | yes | no | yes | unknown | link in README; length unknown | script planned silent text with music; one Duo Chat MR in a demo project |
| 9 | [LORE](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311) | GitLab AI Hackathon, Feb to Mar 2026 | Grand Prize | GitLab | B | 2 | no | no (role scene) | suggests | yes | yes | yes | heading only | unknown | 24 flow runs; 'doesn't block the merge' |
| 10 | [Gitdefender](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35458144) | GitLab AI Hackathon, Feb to Mar 2026 | Google Cloud Grand | GitLab | B | 1 | yes | no (role scene) | approval: each step | yes | yes | unknown | yes | script about 370 words; length unknown | 'Ready to proceed?' before each phase |
| 11 | [Aegis](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35550883) | GitLab AI Hackathon, Feb to Mar 2026 | Google Cloud Runner Up | GitLab | B | 1 | no | no | approval: outcome | no | no | yes | heading only | unknown | repo match likely; synthetic training data not labelled |
| 12 | [GraphDev](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35368827) | GitLab AI Hackathon, Feb to Mar 2026 | Anthropic Grand | GitLab | B | 1 | yes | no (role scene) | approval: each step | yes | yes | unknown | yes | 3-min story planned; length unknown | Claude Code as external agent via AI Gateway |
| 13 | [DocSync](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/2125704) | GitLab AI Hackathon, Feb to Mar 2026 | Anthropic Runner Up | GitLab | B | 2 | no | no | approval: outcome | yes | yes | unknown | yes | unknown | 'No auto-merge'; confidence rule |
| 14 | [Time-Traveler](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572) | GitLab AI Hackathon, Feb to Mar 2026 | Most Technically Impressive | GitLab | B | 1 | yes | no (role scene) | approval: each step | yes | yes | unknown | yes | shows MR !6 end to end; length unknown | deployer confirms first; bearer token committed |
| 15 | [RedAgent](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156) | GitLab AI Hackathon, Feb to Mar 2026 | Most Impactful | GitLab | B | 1 | no | no | suggests | no | yes | yes | yes | unknown | about 19 flow runs; staff warning about comments |
| 16 | [Launch Control](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258) | GitLab AI Hackathon, Feb to Mar 2026 | Easiest to Use | GitLab | B | 1 | yes | no (role scene) | suggests | yes | yes | unknown | yes | 179.8 s (coded in Remotion; submitted cut unverified) | GO / NEEDS_REVIEW / BLOCK; unsourced 73% |
| 17 | [GreenPipe](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34754046) | GitLab AI Hackathon, Feb to Mar 2026 | Green Agent | GitLab | B | 1 | no | no | approval: outcome | yes | yes | yes | heading only | no link | which of two GreenPipe repos won is unverified |
| 18 | [BugFlow](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34708497) | GitLab AI Hackathon, Feb to Mar 2026 | Sustainable Design bonus | GitLab | B | 1 | no | no | approval: outcome | no | yes | unknown | heading only | '3-minute' (README claim) | 53 bot issues; 'Walk away' pitch |
| 19 | [DELTA Cyber Reasoning](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35701012) | GitLab AI Hackathon, Feb to Mar 2026 | Sustainable Design bonus | GitLab | B | 2 | no | no | approval: outcome | no | yes | yes | yes | unknown | 6 CWE-fix bot commits; visible history about 12 h |
| 20 | [CarbonLint](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35504826) | GitLab AI Hackathon, Feb to Mar 2026 | Sustainable Design bonus | GitLab | B | 1 | no | no | approval: each step | yes | yes | unknown | unknown | no link | asks before opening the MR; late small build |
| 21 | [TFGuardian](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/159555) | GitLab AI Hackathon, Feb to Mar 2026 | Sustainable Design bonus | GitLab | B | 1 | yes | no | approval: outcome | yes | yes | yes | yes | no link | 64 bot commits; flow v1.26.0 |
| 22 | [SecurityMonkey](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35360576) | GitLab AI Hackathon, Feb to Mar 2026 | Honorable Mention (part 1 excerpt) | GitLab | C | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | repo match unverified; part 2 found no named mentions |
| 23 | [stregent](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35402517) | GitLab AI Hackathon, Feb to Mar 2026 | Honorable Mention (part 1 excerpt) | GitLab | C | unknown | unknown | unknown | approval: outcome | unknown | unknown | unknown | unknown | link in README; length unknown | merge fixes from WhatsApp (excerpt) |
| 24 | [Pipeline Doctor](https://gitlab.com/vanichitkara18/pipeline-doctor) | Google AI in Action 2025 (GitLab track) | GitLab track 1st or 2nd | Google (GitLab track) | B | 1 | no | no (role scene) | approval: outcome | no | yes | yes | no | unknown | 97 bot branches; one context-load test; CI/CD Catalog release |
| 25 | Agentic CICD | Google AI in Action 2025 (GitLab track) | GitLab track 1st or 2nd | Google (GitLab track) | C | unknown | unknown | unknown | acts alone | unknown | unknown | unknown | unknown | unknown | releases and rollbacks 'without immediate human intervention' (blog excerpt) |
| 26 | [Agent Anansi](https://gitlab.com/prehistoricpancake/agent-anansi) | Google AI in Action 2025 (GitLab track) | GitLab track 3rd | Google (GitLab track) | B | 1 | yes | no | suggests | no | no | no | yes | unknown | CI jobs post canned sample payloads |
| 27 | [CrossBeam](https://github.com/mikeOnBreeze/cc-crossbeam) | Built with Opus 4.6, Feb 2026 | 1st | Anthropic | A | 1 | yes | yes | suggests | no | unknown | yes | yes | not opened; length unknown | 'Run Live' and 'Showcase' buttons for judges |
| 28 | [Elisa](https://github.com/zoidbergclawd/elisa) | Built with Opus 4.6, Feb 2026 | 2nd | Anthropic | A | 1 | no | yes | acts alone | yes | unknown | yes | yes | not opened; length unknown | optional 'check with me' gates; 1,500+ tests |
| 29 | [PostVisit.ai](https://github.com/MedouneSGB/postvisit) | Built with Opus 4.6, Feb 2026 | 3rd | Anthropic | A | 1 | yes | yes | suggests | yes | unknown | yes | yes | link in README; length unknown | repo copy; 'Doctor-in-the-loop'; fictional patients disclosed |
| 30 | [TARA](https://github.com/Kye256/tara-transport-assessment) | Built with Opus 4.6, Feb 2026 | Keep Thinking | Anthropic | A | 1 | no | yes | suggests | no | yes | yes | no | link in README; length unknown | cached real-run results so judges need no key |
| 31 | [Conductr](https://github.com/nanassound/conductr) | Built with Opus 4.6, Feb 2026 | Creative Exploration | Anthropic | A | 1 | no | no | acts alone | no | unknown | yes | yes | not opened; length unknown | live bandmate; play, low stakes |
| 32 | [Medkit](https://github.com/bedriyan/medkit-app) | Built with Opus 4.7, Apr 2026 | 1st | Anthropic | A | 1 | yes | yes | approval: each step | yes | unknown | yes | no | none found | 'auto-allow reads, confirm writes'; licence line conflicts with rules |
| 33 | [Wrench Board](https://github.com/Junkz3/wrench-board) | Built with Opus 4.7, Apr 2026 | 2nd | Anthropic | A | 1 | yes | yes | suggests | yes | unknown | yes | no | '3-minute' (README link) | public history starts after the event |
| 34 | [Maieutic](https://github.com/srichandrak/maieutic) | Built with Opus 4.7, Apr 2026 | 3rd | Anthropic | A | 1 | yes | yes | suggests | yes | unknown | yes | no | none found | repo copy; teachers review AI drafts |
| 35 | [Virtual Puppet Theater](https://github.com/rhmoller/virtual-puppet-theater) | Built with Opus 4.7, Apr 2026 | Most Creative | Anthropic | A | 1 | no | yes | acts alone | no | unknown | yes | no | none found | play; one sanity test |
| 36 | [MaestrIA](https://claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon) | Built with Opus 4.7, Apr 2026 | Keep Thinking | Anthropic | C | 1 | yes | yes | suggests | yes | unknown | yes | unknown | link in post; length unknown | no public repo; eval 74% to 81% |
| 37 | [ARIA](https://github.com/zestones/Aria) | Built with Opus 4.7, Apr 2026 | Best use of Managed Agents | Anthropic | A | 2 | yes | no (role scene) | suggests | no | unknown | yes | yes | link in post; length unknown | starts investigations alone; writes work orders |
| 38 | [Tekton](https://github.com/tangxiya-star/Tekton) | Claude Opus 4.8 Build Day, Jun 2026 | 1st | Anthropic | A | 2 | yes | yes | suggests | no | yes | yes | yes | 1-minute required; actual unknown | verifier refuses a corrupted roof live; pre-event prototype |
| 39 | [Sim Francisco](https://github.com/tejasprabhune/simfrancisco) | Claude Opus 4.8 Build Day, Jun 2026 | 2nd | Anthropic | A | 2 | yes | no | suggests | no | yes | yes | unknown | 1-minute required; actual unknown | 81.3% forecast against 83.8% actual; adversarial critic |
| 40 | [Custom Universe](https://github.com/jss8649/image-edit-realtime-hackathon) | Claude Opus 4.8 Build Day, Jun 2026 | 3rd | Anthropic | A | 2 | yes | yes | suggests | no | no | no | unknown | 1-minute required; actual unknown | commit from Feb 2026, months before the event |
| 41 | [Cite-Before-Act MCP](https://github.com/bisonbet/Cite-Before-Act-MCP) | MCP's 1st Birthday, Nov 2025 | Track 1 Best Overall | Anthropic | A | unknown | unknown | no | approval: each step | yes | unknown | unknown | yes | YouTube link; length unknown | approval before any state change is the product |
| 42 | [MCEPTION](https://huggingface.co/spaces/MCP-1st-Birthday/MCEPTION) | MCP's 1st Birthday, Nov 2025 | Track 1 Best Enterprise | Anthropic | C | 1 | yes | unknown | unknown | unknown | unknown | unknown | unknown | unknown | creates and deploys other MCP servers |
| 43 | [Portfolio Intelligence Platform](https://huggingface.co/spaces/MCP-1st-Birthday/Finance-Portfolio-Intelligence-Platform) | MCP's 1st Birthday, Nov 2025 | Track 1 Best Consumer | Anthropic | C | 1 | yes | unknown | suggests | unknown | unknown | unknown | unknown | unknown | 'transparent multi-agent MCP orchestration' |
| 44 | [GCP Game Context Protocol](https://huggingface.co/spaces/MCP-1st-Birthday/GameContextProtocol) | MCP's 1st Birthday, Nov 2025 | Track 1 Best Creative | Anthropic | C | 1 | yes | unknown | unknown | unknown | unknown | unknown | unknown | unknown | 3D scenes from natural language |
| 45 | [Vehicle Diagnostic Assistant](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant) | MCP's 1st Birthday, Nov 2025 | Track 2 Enterprise 1st | Anthropic | A | 2 | yes | no | suggests | no | unknown | no | heading only | unknown | MCP server on a car's OBD-II dongle; simulator Space |
| 46 | [MCP Blockly](https://github.com/owenkaplinsky/MCP-Blockly) | MCP's 1st Birthday, Nov 2025 | Track 2 Consumer 1st | Anthropic | A | 1 | yes | no | acts alone | no | unknown | no | unknown | YouTube link; length unknown | assistant edits the workspace without a confirm step |
| 47 | [Vidzly](https://github.com/tihado/vidzly) | MCP's 1st Birthday, Nov 2025 | Track 2 Creative 1st | Anthropic | C | 4 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | repo found by search only, not opened |
| 48 | Legacy Code Modernizer | MCP's 1st Birthday, Nov 2025 | Modal Innovation Award | Anthropic | C | 1 | unknown | unknown | acts alone | unknown | unknown | unknown | unknown | unknown | 'An autonomous AI agent that modernizes legacy codebases' |
| 49 | [Project Blackbox](https://github.com/alejandro-publius/blackbox-datahub) | Build with DataHub, Jul to Aug 2026 | Grand Prize | Other (DataHub) | B | 1 | unknown | unknown | approval: each step | yes | yes | yes | unknown | unknown | Alex's own; operator presses 'Repair & Verify' |
| 50 | [Hindsight](https://github.com/gmassello/hindsight) | Build with DataHub, Jul to Aug 2026 | challenge winner (excerpt) | Other (DataHub) | B | 1 | yes | no (role scene) | approval: each step | yes | yes | yes | unknown | 2:33 (stated; not watched) | Approve / Reject on a dry-run diff |
| 51 | [Paracelsus](https://github.com/fiya-chris-and-AI/paracelsus) | Build with DataHub, Jul to Aug 2026 | challenge winner (excerpt) | Other (DataHub) | B | 2 | yes | no | suggests | no | unknown | no | unknown | no link | 'No number in the output comes from a language model' |
| 52 | [Culprit](https://github.com/JonathanSolvesProblems/culprit) | Build with DataHub, Jul to Aug 2026 | challenge winner (excerpt) | Other (DataHub) | B | 1 | no | no | approval: outcome | no | yes | no | unknown | YouTube link; length unknown | row-count gate rejected its own first fix |
| 53 | [ORION](https://github.com/40tify/orion) | Gemini Live Agent Challenge, 2026 | Grand Prize | Google | A | 1 | yes | no (role scene) | suggests | yes | unknown | no | yes | demo plus deployment-proof video; length unknown | display-only tools; 'The surgeon decides.' |
| 54 | [drone-copilot](https://github.com/BryenInsights/drone-copilot) | Gemini Live Agent Challenge, 2026 | The Live Agent | Google | A | 1 | no | no | acts alone | no | yes | yes | yes | two YouTube links; length unknown | code safety guard; replay mode for judges |
| 55 | [Sankofa (Gemini)](https://github.com/Jeremiah-Sakuda/Sankofa) | Gemini Live Agent Challenge, 2026 | Creative Storyteller | Google | A | 1 | no | no (role scene) | suggests | no | unknown | yes | yes | unknown | trust labels on every segment |
| 56 | [Moonwalk](https://github.com/OactoDev/Moonwalk) | Gemini Live Agent Challenge, 2026 | UI Navigator | Google | A | 2 | yes | no | approval: each step | yes | unknown | yes | yes | YouTube link; length unknown | risk-tiered 'Proceed' modal |
| 57 | [Wand](https://devpost.com/software/wand-a-live-agent-that-sees-browses-and-clicks-with-you) | Gemini Live Agent Challenge, 2026 | Best multimodal integration and UX | Google | C | 1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | no repo found |
| 58 | [JohnKeats.AI](https://github.com/johnkeats-ai/johnkeats-ai) | Gemini Live Agent Challenge, 2026 | Best technical execution and agent architecture | Google | A | 1 | yes | no (role scene) | suggests | yes | unknown | yes | heading only | YouTube link; length unknown | deterministic policy gate plus human approval |
| 59 | [Rayan Memory](https://github.com/yelnady/rayan) | Gemini Live Agent Challenge, 2026 | Best innovation and thought leadership | Google | A | 1 | yes | yes | suggests | yes | unknown | unknown | yes | unknown | STORY.md; screenshot placeholders unfilled |
| 60 | [NagarDrishti](https://devpost.com/software/nagardrishti) | Gemini Live Agent Challenge, 2026 | Honorable mention | Google | C | 2 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | no repo found |
| 61 | [Ekaette](https://geminiliveagentchallenge.devpost.com/submissions/970955-ekaette) | Gemini Live Agent Challenge, 2026 | Honorable mention | Google | C | 1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | no repo found |
| 62 | [VibeCat](https://github.com/Two-Weeks-Team/vibeCat) | Gemini Live Agent Challenge, 2026 | Honorable mention | Google | A | 2 | yes | no (role scene) | approval: each step | yes | unknown | yes | yes | YouTube link; length unknown | confirm-before-act plus code keyword gate |
| 63 | [Call My Parts](https://geminiliveagentchallenge.devpost.com/submissions/945801-call-my-parts) | Gemini Live Agent Challenge, 2026 | Honorable mention | Google | C | 4 | unknown | unknown | acts alone | unknown | unknown | unknown | unknown | unknown | calls suppliers on its own (post) |
| 64 | [Relay](https://geminiliveagentchallenge.devpost.com/submissions/967879-relay-real-time-voice-vision-lab-tutor-for-electronics) | Gemini Live Agent Challenge, 2026 | Honorable mention | Google | C | 1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | no repo found |
| 65 | [Cart-to-kitchen assistant](https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke) | GKE Turns 10, 2025 | Grand prize | Google | A | 1 | no | no (role scene) | approval: each step | yes | unknown | no | yes | unknown | cart write only after the user clicks; one commit |
| 66 | [CardOS](https://devpost.com/software/cardos) | GKE Turns 10, 2025 | North America | Google | C | 1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | no repo found |
| 67 | [NeroFashion](https://github.com/xValentim/nero-fashion) | GKE Turns 10, 2025 | Latin America | Google | A | 4 | yes | no (role scene) | suggests | no | unknown | no | yes | unknown | AI endpoints, no autonomous actions |
| 68 | [V-Commerce Studio](https://github.com/Siddharth-Khattar/gke-online-boutique) | GKE Turns 10, 2025 | Asia Pacific | Google | A | 4 | yes | no | approval: each step | yes | unknown | no | yes | unknown | admin approves or rejects ads; repo affiliation unverified |
| 69 | [Cartmate](https://github.com/victorbash400/Cartmate) | GKE Turns 10, 2025 | EMEA | Google | A | 1 | no | no | approval: each step | no | unknown | yes | yes | unknown | acts on user requests; README paths are placeholders |
| 70 | [Voice Teller](https://github.com/julian-hecker/gke-hackathon) | GKE Turns 10, 2025 | Honorable mention #1 | Google | A | 1 | yes | no (role scene) | approval: each step | no | unknown | no | yes | unknown | acts on the caller's request; prompt-only confirm |
| 71 | [CO2-Aware Shopping Assistant](https://github.com/prabhakaran-jm/co2-shopping-assistant) | GKE Turns 10, 2025 | Honorable mention #2 | Google | A | 1 | yes | no | approval: each step | no | unknown | yes | heading only | unknown | success metrics not backed by the repo |
| 72 | [Vigil AI](https://github.com/ayanliger/gke-turns10-hackathon-vigil) | GKE Turns 10, 2025 | Honorable mention #3 | Google | A | 1 | no | no | acts alone | no | unknown | no | yes | YouTube link; length unknown | locks accounts with no human; HITL listed as future work |
| 73 | [SalesShortcut](https://github.com/merdandt/SalesShortcut) | ADK Hackathon, 2025 | Grand prize | Google | A | 2 | no | yes | acts alone | no | unknown | unknown | yes | 'Full video' found by title; length unknown | phones and emails leads alone; story from a search excerpt |
| 74 | [Energy Agent AI](https://github.com/hazardscarn/energyagentai) | ADK Hackathon, 2025 | North America | Google | A | 1 | no | no | suggests | no | unknown | unknown | yes | unknown | dataset labelled as simulated |
| 75 | [Edu.AI](https://github.com/giovannamoeller/edu-ai-adk) | ADK Hackathon, 2025 | Latin America | Google | A | 1 | yes | no (role scene) | suggests | no | unknown | unknown | yes | unknown | essay photo in, rubric scores out |
| 76 | [GreenOps](https://github.com/niksm7/GreenOps) | ADK Hackathon, 2025 | Asia Pacific | Google | A | 2 | yes | no (role scene) | approval: each step | no | yes | unknown | yes | unknown | asks first, code checks safety; README says 'Completely autonomous' |
| 77 | [Nexora-AI](https://github.com/M4RKUS28/Nexora) | ADK Hackathon, 2025 | EMEA | Google | A | 4 | yes | no | suggests | no | unknown | unknown | yes | unknown | about 787 commits; product polish |
| 78 | [Particle Physics Agent](https://github.com/bee4come/Particle-Physics-Agent) | ADK Hackathon, 2025 | Honorable mention #1 | Google | A | 2 | yes | no | suggests | no | unknown | yes | yes | unknown | self-reported success rates (unverified) |
| 79 | [TradeSageAI](https://github.com/sudsk/tradesage-mvp) | ADK Hackathon, 2025 | Honorable mention #2 | Google | A | 1 | no | no | suggests | no | unknown | unknown | yes | unknown | contradiction agent argues against the idea |
| 80 | [Bleach](https://github.com/vivek100/bleachAgentBuilder) | ADK Hackathon, 2025 | Honorable mention #3 | Google | A | 1 | no | no | suggests | no | unknown | unknown | yes | unknown | generates ADK code for review |
| 81 | [Storytopia](https://github.com/Harpita-P/Storytopia) | Cloud Run Hackathon, 2025 | Grand Prize | Google | B | 2 | yes | no (role scene) | suggests | no | unknown | unknown | yes | linked from a later repo; length unknown | says its demo GIFs are sped up |
| 82 | [Rehearsal](https://github.com/konxu/Rehearsal-for-Cloud-Run-Hackathon) | Cloud Run Hackathon, 2025 | Best of AI Studio | Google | B | 1 | yes | no (role scene) | suggests | no | unknown | unknown | yes | unknown | repo match likely |
| 83 | [PermitScan AI](https://github.com/sagban/permitflowAI) | Cloud Run Hackathon, 2025 | Best of AI Agents | Google | B | 1 | yes | no (role scene) | approval: each step | yes | unknown | unknown | yes | unknown | person clicks 'Approve'; unsourced figures |
| 84 | [Commissure](https://github.com/hardrave/Commissure) | Cloud Run Hackathon, 2025 | Best of GPUs | Google | B | 1 | no | no | n/a (not an agent) | no | unknown | unknown | yes | unknown | infrastructure, not an agent |
| 85 | [Piatto](https://github.com/M4RKUS28/Piatto) | Cloud Run Hackathon, 2025 | Honorable Mention | Google | B | 4 | yes | unknown | suggests | no | unknown | unknown | yes | 21.4 s clip in repo; submitted video unknown | repo match likely |
| 86 | [SketchRun](https://github.com/amelia751/sketchrun-app) | Cloud Run Hackathon, 2025 | Honorable Mention | Google | B | 1 | no | unknown | suggests | no | unknown | unknown | yes | unknown | unbacked '3-5x faster' claim |
