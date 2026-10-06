# Claude Opus 4.8 Build Day, MCP's 1st Birthday Hackathon, Build with DataHub: winners and why they won

Researched 2026-10-06 for Alex Velazquez's Life After Code entry (GitLab Transcend Hackathon, judges from GitLab, Google and Anthropic). Goal: what recent agent hackathon judges rewarded, from the pages themselves.

Tags used below:

- "(unverified)": I could not confirm it from a page I opened.
- "(search excerpt, unverified)": taken from the earlier discovery notes in [_discovery_anthropic.md](_discovery_anthropic.md), which came from web search summaries, not from pages opened.
- "(team copy)": text from a copy of official rules that a team committed to its own repo. Close to the official text, but I could not check it against the official page (blocked).
- "(my reading)": my judgment, not a sourced fact.
- All pages were read on 2026-10-06 with WebFetch, which passes each page through a summarizer. Quotes from GitHub files came back through that tool, so small wording differences are possible. Repo counts (commits, stars) are approximate. Times are UTC unless marked.
- Where a quoted source used an em dash or en dash, it is replaced with " - ".

Read this first:

- Build Day: the official winners post on claude.com was read in full. All three winner repos were read. The event page (cerebralvalley.ai) is blocked, but the 1st place repo holds a copy of the participant guide with the judging rubric, prizes and rules.
- MCP's 1st Birthday: huggingface.co and gradio.app are blocked. I read the winners page through its source file in the Gradio GitHub repo (the same data the page renders). Three of the six winners I cover have GitHub repos and were read; the other three live only on Hugging Face Spaces and were not. No judging criteria or judge names found.
- DataHub: datahub.com and Devpost are blocked, so I could not read the winners post or what it says about why each project won. Alex's Blackbox repo holds his own copy of the Devpost rules (dates, prizes, tracks, criteria, judges). I read the repos of three other winners named in an earlier search excerpt (Hindsight, Paracelsus, Culprit). Seven projects were paid; the other three are unknown.

## Event facts

### 1. Claude Opus 4.8 Build Day (Anthropic with Cerebral Valley), June 13, 2026

| Item | Value | Source |
|---|---|---|
| Name | Official post: "Claude Opus 4.8 Build Day hackathon". The participant guide copy in the Tekton repo is titled "Claude Fable 5 Build Day" and says "Fable 5's safeguards route requests in those areas to Claude Opus 4.8 instead". The Tekton README calls it "Claude Build Day". I did not resolve the naming difference (unverified) | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon), [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md), [Tekton README](https://github.com/tangxiya-star/Tekton) |
| Event page | https://cerebralvalley.ai/e/claude-startups-build-day (blocked) | task brief |
| Date, place, length | "On June 13, we brought more than 300 founders and builders to San Francisco for a 12-hour hackathon with Claude Opus 4.8." | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon) |
| Venue, organizers | "Shack15, Ferry Building", organizers "Anthropic & Cerebral Valley" (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| Applicants, participants | "More than 1,500 people had applied; 310 took part, many traveling from around the world, each with $500 in credits and one day to turn an idea into a working demo." Submission count not stated | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon) |
| Winners post date | June 17, 2026 | [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon) |
| Schedule | Hacking from 10:30 AM, submissions due 5:00 PM, finalists announced 6:15 PM, winners 7:45 PM (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| The ask | "build something new, such as a complete, working app from a standing start". "What sets it apart most is long-horizon, difficult, autonomous work: planning, building, and validating its own work for a day or more at a time." (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| Prizes | 1st $100,000, 2nd $40,000, 3rd $10,000 in API credits (team copy). Tekton's README: "winning $100K in Claude credits". The official post does not state prizes | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md), [Tekton README](https://github.com/tangxiya-star/Tekton) |
| Rules | Teams of up to 4 (solo allowed); public repos; "Demo must only highlight...features...built during the hackathon"; banned project types include basic RAG, Streamlit apps, dashboards, image analyzers and educational chatbots (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| Submission | One-minute demo video, public repo, working demo link, and a "Brief, rubric, and session log" (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| Judging process | Round 1: "Submissions will be reviewed asynchronously by the Anthropic team". Round 2: "Top 6 teams will present on stage to a panel of judges & all attendees"; "Each team will have 3 minutes to live demo their project, followed by 1-2 minutes of Q&A" (team copy) | [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md) |
| Judges | Names not found. Round 1 by "the Anthropic team" (team copy) | same |

Judging criteria (team copy, [guide copy](https://github.com/tangxiya-star/Tekton/blob/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md)). The Tekton rubric file uses the same four names and weights, and the Sim Francisco brief has the same Autonomy (15%) and Orchestration (15%) lines, which supports the copy.

- Impact, 35%: "How useful is what they built? Who is it for, and how much does it matter to them?" "Is the output itself high quality (something someone would find useful)?"
- Demo, 35%: "Is it a working and impressive demo?" "Does it hold up live?" "Does the demo prove the impact?"
- Autonomy, 15%: "Judged from the session log. How many times did humans intervene mid-task?" "Were interventions course-corrections or new information?" "When something broke, did the model catch it itself (via a test, a check, a verifier)?" "Did it run long stretches without steering?"
- Orchestration, 15%: "Is this orchestration simple and repeatable?" "Is 'done' verifiable by the model without a human: a test suite, a responding URL, a rubric file it can grade against?" "Could another team rerun the setup tomorrow on a new problem?"

### 2. MCP's 1st Birthday Hackathon (Anthropic and Gradio), November 14 to 30, 2025

| Item | Value | Source |
|---|---|---|
| Name | Winners page title: "MCP's 1st Birthday Hackathon Winners" | [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte) (renders https://gradio.app/mcp-birthday-winners, blocked) |
| Hosts | Anthropic and Gradio. A winner's README: "This was created as part of our submission for the Anthropic Gradio MCP's 1st Birthday hackathon" | [Vehicle Diagnostic Assistant README](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant) |
| Dates | "MCP's 1st Birthday Hackathon: November 14-30, 2025" (a participant's README). Judging Dec 1 to 14 and winners Dec 15 (search excerpt, unverified) | [TraceMind-AI README](https://github.com/Mandark-droid/TraceMind-AI), [_discovery_anthropic.md](_discovery_anthropic.md) |
| Tracks and awards | Track 1 "Building MCP": Best Overall, Best Enterprise, Best Consumer, Best Creative. Track 2 "MCP in Action": Enterprise, Consumer and Creative categories, each with 1st, 2nd, 3rd and an Honorable Mention. Seven sponsor awards: Modal Innovation Award, LlamaIndex Category Award, OpenAI Best API Integration, OpenAI Best ChatGPT App, Blaxel Choice Award, ElevenLabs Category Award, Hugging Face Community Choice Award | [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte) |
| Space tags | Entries tag their Space with the track, for example "building-mcp-track-enterprise" and "building-mcp-track-customer" | [Cite-Before-Act SPACE_README.md](https://github.com/bisonbet/Cite-Before-Act-MCP/blob/main/SPACE_README.md) |
| Sponsors | "HuggingFace • Google Gemini • Modal • Anthropic • Gradio • OpenAI • Nebius • Hyperbolic • ElevenLabs • SambaNova • Blaxel" (a participant's README) | [TraceMind-AI README](https://github.com/Mandark-droid/TraceMind-AI) |
| Prizes | $21,000 cash (Hugging Face $15K, Modal $2.5K, Blaxel $2.5K, LlamaIndex $1K) plus $25K in Anthropic API credits (search excerpt, unverified; another excerpt said $20,000 cash). The winners page source has no amounts | [_discovery_anthropic.md](_discovery_anthropic.md) |
| Registrations | 7,100+ (search excerpt, unverified). Submission count not found | [_discovery_anthropic.md](_discovery_anthropic.md) |
| Judging criteria | Not found (the hackathon README Space on huggingface.co is blocked) | |
| Judges | Not found | |

### 3. Build with DataHub: The Agent Hackathon (Devpost), July 6 to August 10, 2026

Main source: [docs/HACKATHON_REQUIREMENTS.md](https://github.com/alejandro-publius/blackbox-datahub/blob/main/docs/HACKATHON_REQUIREMENTS.md) in Alex's Blackbox repo, a copy of the Devpost main, rules and resources pages that the file says was verified by "Live Fetch, 2026-08-09". All rows are (team copy) unless marked.

| Item | Value |
|---|---|
| Name and host | "Build with DataHub: The Agent Hackathon", run by DataHub on Devpost (datahub.devpost.com, blocked) |
| Dates | Registration opens "July 6, 2026, 9:00 AM ET"; deadline "August 10, 2026, 5:00 PM ET (EDT)"; judging "August 17, 2026, 10:00 AM ET" to "August 31, 2026, 5:00 PM ET"; winners "On or around September 8, 2026, 2:00 PM ET" |
| Prizes ($20,500) | Grand Prize "$6,000 cash" (1), plus "Presentation at DataHub Town Hall", social promotion and a LinkedIn badge; Challenge Winner "$3,000 cash" (4, one per category); Honourable Mention "$1,000 cash" (2); Most Valuable Feedback "$50 cash" (10). So seven paid project prizes |
| Participants, projects | About 2,969 participants when the copy was made. "600+ projects" ([Blackbox README](https://github.com/alejandro-publius/blackbox-datahub)); 3,000+ builders (search excerpt, unverified) |
| Categories | "Agents That Do Real Work" (agents that "read DataHub to understand what's connected to what, take action, and write results back"); "Metadata-Aware Code Generation & Development"; "Production ML Agents" (agents that "catch silent problems, like target leakage, upstream data changes that should have triggered a retrain, or schema drift"); "Open / Wildcard" |
| Hard requirement | "Projects must incorporate DataHub by using the open-source platform together with at least one of: the MCP Server, Agent Context Kit, DataHub Skills, or Analytics Agent." |
| Submission | Video "less than three (3) minutes"; public repo with an Apache 2.0 license file; working access for judges; "Projects must be newly created during the Submission Period", with pre-existing code disclosed; an `examples/` folder of generated artifacts recommended |
| Judging | Stage One pass/fail ("reasonably fits the theme and reasonably applies the required APIs/SDKs"). Stage Two: six criteria, equal weight (below) |
| Judges | Tim Bossenmaier (Cloudflight), Aman Gairola (Pinterest), Maggie Hays (DataHub), Alyssa Lee (DataHub), Nick Adams (DataHub), Wenjia You (OpenAI), Mike Burke ("Senior Developer") |
| Anthropic role | None found. Not an Anthropic event; included because Alex won it |
| Winners post | https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/ (blocked) |

Stage Two criteria (team copy). Two other winners list the same six names in their own repos ([Culprit README](https://github.com/JonathanSolvesProblems/culprit), and in paraphrase [Hindsight SUBMISSION.md](https://github.com/gmassello/hindsight/blob/main/SUBMISSION.md)), which supports the copy.

- Use of DataHub: "How meaningfully does the project use DataHub - its context graph (lineage, ownership, schemas, ML metadata, governance signals)", with a stated preference for writing back.
- Technical Execution: "Quality of implementation, robustness, and whether the project actually works end-to-end."
- Originality: "How creative and novel is the approach? Submissions should clearly go beyond features DataHub already provides."
- Real-World Usefulness: "Would a real data, ML, or AI platform team see clear value in this?"
- Submission Quality: "Quality of the demo video, written description, and README. A judge should be able to understand what the project does."
- Bonus: "meaningful open-source contributions to DataHub - new connectors, skills, fixes, RFCs, or documentation improvements".

## Winners table

### Build Day (all from the [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon))

| Place | Project | Team (size) | What it is | Repo | Live URL | Deep-dived |
|---|---|---|---|---|---|---|
| 1st | Tekton | Holly Tang, Austin Burgess (2) | 3D reconstruction of historic buildings where every component traces to a cited source; an independent verifier refuses unsourced geometry | [tangxiya-star/Tekton](https://github.com/tangxiya-star/Tekton) | https://tekton-build.vercel.app (listed; blocked here) | yes |
| 2nd | Sim Francisco | Tanmayi Priya Dasari, Tejas Prabhune, UC Berkeley EECS (2) | 10,000 synthetic San Francisco residents from Census data that can be polled; forecasts checked against real results | [tejasprabhune/simfrancisco](https://github.com/tejasprabhune/simfrancisco) | https://simfrancisco.org (listed; blocked here) | yes |
| 3rd | Custom Universe | Jake Stevens, Mauricio Pereira (2) | Phone photos to editable, photoreal 3D scenes in real time, for robotics synthetic training data | [jss8649/image-edit-realtime-hackathon](https://github.com/jss8649/image-edit-realtime-hackathon) | https://www.luminal.com/realtime-edit-demo (listed; not opened) | yes |

### MCP's 1st Birthday (main track winners, from the [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte))

| Award | Project | Handles | Winners page line | GitHub repo | Deep-dived |
|---|---|---|---|---|---|
| Track 1 Best Overall | Cite-Before-Act MCP | bisonnetworking | "Human-in-the-loop safety middleware for MCP servers. Require explicit approval before state-mutating operations." | [bisonbet/Cite-Before-Act-MCP](https://github.com/bisonbet/Cite-Before-Act-MCP) | yes |
| Track 1 Best Enterprise | MCEPTION | alihmaou | "This server allows you to create and deploy other MCP servers on Hugging Face Spaces." | none found | no |
| Track 1 Best Consumer | Portfolio Intelligence Platform | BrianIsaac | "AI-powered portfolio analysis with transparent multi-agent MCP orchestration" | none found | no |
| Track 1 Best Creative | GCP - Game Context Protocol | ArturoNereu | "Build 3D scenes and games with natural language." | none found | no |
| Track 2 Enterprise, 1st | Vehicle Diagnostic Assistant | castlebbs, stargarnet | "AI agent that connects to your car via an embedded MCP server to provide real-time diagnostics and insights." | [castlebbs/Vehicle-Diagnostic-Assistant](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant) | yes |
| Track 2 Consumer, 1st | MCP Blockly | owenkaplinsky | "AI that makes MCP servers with block-code." | [owenkaplinsky/MCP-Blockly](https://github.com/owenkaplinsky/MCP-Blockly) | yes |
| Track 2 Creative, 1st (not covered below) | Vidzly | tthhanh, tiena2cva, Nlag, Daphneee17 | "Transform raw footage into viral-ready content in seconds. No skills required. No expensive gear needed." | probably [tihado/vidzly](https://github.com/tihado/vidzly) (search result only, not opened) | no |

Other places on the same page: Track 2 Enterprise 2nd DevRel Campaign Generator (chenglu), 3rd DataPass (waroca), HM FleetMind AI Agent (mashrur950); Consumer 2nd Drone Control MCP Server (akirahrkw), 3rd Director's Cut (tyb343, sahiltanna7, nikunj30), HM Snowman AI (nextmarte); Creative 2nd The Emergent Show (inventwithdean), 3rd Reachy Mini Choreography Generator (TwinPeaksTownie), HM MYTHFORGE (hetanshwaghela). Sponsor awards include the Modal Innovation Award to Legacy Code Modernizer (naazimsnh02): "An autonomous AI agent that modernizes legacy codebases through intelligent planning, reasoning, and execution." That one is close to Alex's theme but was not researched further.

### Build with DataHub (winners post blocked)

| Prize | Project | Team (size) | What it is | Repo | Deep-dived |
|---|---|---|---|---|---|
| Grand Prize ($6,000) | Project Blackbox | Alex Velazquez (1) | Evidence-gated data incident response with human-approved repair, a real PR and DataHub write-back | [alejandro-publius/blackbox-datahub](https://github.com/alejandro-publius/blackbox-datahub) | no (Alex's own; summarised only) |
| Named as a challenge winner (search excerpt, unverified); entered "Agents That Do Real Work" | Hindsight | Germán Massello (search excerpt); GitHub gmassello (1) | On-call agent for data incidents that remembers past postmortems inside DataHub | [gmassello/hindsight](https://github.com/gmassello/hindsight) | no (repo only) |
| Named as a challenge winner (search excerpt, unverified); category unknown | Paracelsus | Lutfiya Miller, Chris Müller (search excerpt); commit authors Drfiya, Chriss54 (2) | Deterministic risk scoring for a data catalog, borrowed from drug safety | [fiya-chris-and-AI/paracelsus](https://github.com/fiya-chris-and-AI/paracelsus) | no (repo only) |
| Named as a challenge winner (search excerpt, unverified); entered "Production ML Agents" | Culprit | Jonathan SolvesProblems (search excerpt); GitHub JonathanSolvesProblems (1) | "A stack trace for model decay": walks ML lineage to the upstream column, prices the damage, opens a PR | [JonathanSolvesProblems/culprit](https://github.com/JonathanSolvesProblems/culprit) | no (repo only) |
| Three more paid prizes | unknown | | | | |

The prize level of Hindsight, Paracelsus and Culprit (challenge winner or honourable mention) and their categories are not verified. The tracks shown are the tracks each README says it entered.

## Build Day winners

### Tekton (1st place). Deep-dived: yes

Sources: [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon), [repo and README](https://github.com/tangxiya-star/Tekton), [done.rubric.json](https://github.com/tangxiya-star/Tekton/blob/main/done.rubric.json), [docs/KICKOFF_PROMPT.md](https://github.com/tangxiya-star/Tekton/blob/main/docs/KICKOFF_PROMPT.md), [commits](https://github.com/tangxiya-star/Tekton/commits/main), [GitHub API commit list](https://api.github.com/repos/tangxiya-star/Tekton/commits?per_page=100).

- What it does: "Give Tekton a historical building and Claude researches it, pulling together schematics, construction documents, photographs, and diagrams, then assembles a 3D model across 339 incremental construction states. When you click any component in the model, Tekton shows where the detail came from and why it was placed there." (post). The README's thesis: "nothing renders without a cited source." Four recreations: the Notre-Dame spire, the Notre-Dame towers and facade, whole-cathedral massing, and the Nanchan Temple Main Hall (782 CE).
- Verification, the core of the pitch: "The verification ran entirely on Opus 4.8. Independent verifier sub-agents graded each reconstruction in isolated context windows, and self-correction loops rechecked component placement until all 20 tests passed." (post). README: "An independent verifier recomputes the dimensions from the component coordinates (never trusting the engine's own claims)"; "the builder is not allowed to grade itself by reading its own answer key"; "Failed verifier reports are preserved in `artifacts/verifier-report.*.failed.json`. A visible failure loop is evidence of the system catching itself." For open-ended work: "parallel read-only diagnosers, sequential implementers so edits did not collide, and an adversarial verifier." The demo includes `npm run demo:corrupt`, which pushes the roof toward a textbook ideal so the audience sees the verifier refuse it.
- Sponsor tools and depth: Claude is the build engine ("I treated Claude as an autonomous build engine governed by a written brief and a machine-gradable rubric"). In the 25 newest commits from the GitHub API, 19 carry Claude co-author lines (Claude Opus 4.8, Claude Haiku 4.5 or Claude Opus) (approximate). The finished site "makes no LLM calls". Deep in the build, zero at runtime.
- Autonomy: the build acts alone inside a verifier gate. The kickoff prompt: "The verifier gates completion. You may NOT stop until npm run goal completes green end-to-end." and "Stop to ask the human ONLY for genuinely new information you cannot obtain (a deploy credential / API key)." The product itself is a read-only viewer.
- Human story: "I love watching documentaries, and it always upset me to see beautiful buildings lost to fire," Holly says (post). The post opens: "When a historic wooden building burns, centuries of craftsmanship can disappear with it." The rubric's Impact line: "a real heritage tool that makes fidelity affordable; the building the world watched burn (2019)". The pair "met a month earlier, in line for coffee at a Code with Claude event."
- Live URL: https://tekton-build.vercel.app (in the post and README; blocked here).
- Team size: 2.
- Repo facts: 74 commits. Oldest 2026-06-12T19:50:05Z ("Add Yingzao PRD"), and the Nanchan rule engine and first 3D viewer were committed on June 12 Pacific time, the day before the event; the post says "She had prototyped a single reconstruction on her own". Event-day work June 13; last commit June 23 (winner banner). Authors tangxiya-star and adxburgess plus Claude. 39 stars, 9 forks. No CLAUDE.md, AGENTS.md, tests/ or evals/ folder. Checks live in `scripts/verify.mjs` (README: 12 geometry assertions plus pixel checks) and `done.rubric.json` (31 criteria, 23 required, with a "hackathon_scoring" map using the 35/35/15/15 weights and lines such as Autonomy: "the verifier gate + vision sub-agent catch failures without a human; failed reports kept as proof"). Planning files: PRD.md, ANNOTATION_PLAN.md, the guide copy, docs/KICKOFF_PROMPT.md, three GOAL_*.md files, MERGE_PLAN.md, HANDOFF_HOLLY.md, and one build transcript in docs/session-logs/ (commit: "Add build-session transcript (autonomy log for the submission)").
- README structure: name and one-line thesis; winner banner; live demo link; building selector; "How the 3D is generated"; About; What It Does; Why This Matters; The Current Subject; How We Used Agents; Data And Citations; Build Pipeline (text diagram); Verifier (with the corrupt and restore demo); Run Locally; Tech Stack; Repository Map; Transfer Pattern.
- Why it most likely won (my reading): it answered each criterion on purpose. Impact: heritage lost to fire, with Notre-Dame as the hook. Demo: click any part and see its source, then watch the verifier refuse a corrupted roof live. Autonomy: kept failure reports as proof and limited human input to new information. Orchestration: a rubric file mapped to the judging weights and a "Transfer Pattern" for any building.

### Sim Francisco (2nd place). Deep-dived: yes

Sources: [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon), [repo and README](https://github.com/tejasprabhune/simfrancisco), [BRIEF.md](https://github.com/tejasprabhune/simfrancisco/blob/main/BRIEF.md), [NOTES.md](https://github.com/tejasprabhune/simfrancisco/blob/main/NOTES.md), [session-log.md](https://github.com/tejasprabhune/simfrancisco/blob/main/session-log.md), [commits](https://github.com/tejasprabhune/simfrancisco/commits/main).

- What it does: "Sim Francisco is a working model of San Francisco's population. It has 10,000 synthetic residents drawn from US Census data, each with their own demographics, personal history, and worldview, placed on a map of the city and reacting to the news in real time." It "forecast the 2024 presidential vote at 81.3% Democratic against an actual 83.8%, and San Francisco's March 2024 Prop A at 70% against an actual 70.38%." (post)
- Verification: "Opus 4.8 wrote the entire front and back end and verified the backend's behavior end to end. To verify the model's work, the team had Claude work alongside a verifier and an adversarial agent to build a backend that reproduced the city's real demographic distributions." (post). README: "before any milestone is 'done', an independent agent re-runs `validate` + contract tests, and a second adversarial agent tries to prove the gain is spurious (overfit / model-knowledge leakage / weight-gaming). Completion gates on both." In the session log the verifier returned "ALL-PASS" and the critic said "The ~0.84 is EARNED, not spurious", while also catching a prompt line that leaked the 2024 result; NOTES.md records "adversarial critic caught a leakage line; corrected. Final headline 0.8490". Score path in NOTES.md: 0.5336, 0.6703, 0.8171, about 0.84, 0.8490 (gate 0.70).
- Cost story: "Over time, Claude ran an evolutionary clustering algorithm it created itself," Tejas says, grouping residents into about 300 personas and "cutting inference cost by 10 to 100 times" (post).
- Sponsor tools and depth: the log shows Claude Code v2.1.177 with Opus 4.8 (1M context) doing the build. The README lists "four loops": a `/goal` self-correction loop, the verifier plus critic gate, saved workflows (`.claude/workflows/*.js` as `/sf:*` commands) and a pre-push hook. The `.claude/` folder is not in the public repo (404). At runtime, the leakage-free backtest used GPT-4o through Azure AI Foundry (README: "The older Claude models with a 2023 cutoff have since been retired"); a commit on June 14, the day after the event, ported the backend to Claude Sonnet 4.6. So Claude was the builder; the scored runtime model was not Claude.
- Autonomy: build acts alone from one goal prompt: "Build the SF digital-twin backend per BRIEF.md. The goal is met ONLY when all of these hold at once..." Across the roughly 395,000-character log I counted about six human messages, mostly questions ("how can we test it?") and UI requests, not corrections (my count, approximate). The product only informs (predictions, no actions).
- Human story: no emotional story. The pitch: "What if you could predict how your customers responded to releases before they went out into the real world? Or if you could get a signal on who will win an election?" The team: "electrical engineering and computer science majors at UC Berkeley who met through the Machine Learning club on campus." "For Tejas, Sim Francisco doubles as a test for the post-training company he's building" (post).
- Live URL: https://simfrancisco.org and API https://sf-digital-twin-tp.fly.dev (listed; simfrancisco.org blocked here).
- Team size: 2 (commit authors tejasprabhune and tanmayi2).
- Repo facts: 22 commits, June 13 to June 16, 2026 (a five-city expansion on June 16). 50 stars, 16 forks. Rust (axum, sqlite) backend and a static JS frontend. Files: BRIEF.md (written for Claude Code agents, with its own "Judging Criteria (Autonomy + Orchestration)" section), INTEGRATION.md, NOTES.md (failure to fix to rule log), session-log.md, rubric.yaml plus rubric files for four other cities, .githooks/. No CLAUDE.md or AGENTS.md. Tests: `cargo test` (README: 41) and `cargo run --bin validate`, which "exits 0 iff headline >= gate".
- README structure: tagline; live app and API links; "The brief" (pitch, historically predictive results, the future); What it is; Cost control; Reproduce it; "The four loops (autonomy + orchestration)"; "Repeatable on a new problem (Orchestration criterion)"; "Methodology integrity (no leakage / no gaming)".
- Why it most likely won (my reading): a number a judge can check against the real world, an adversarial agent pointed at its own score, and README sections named after the judging criteria. The live map of the city made the demo memorable.

### Custom Universe (3rd place). Deep-dived: yes

Sources: [claude.com post](https://claude.com/blog/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon), [repo and README](https://github.com/jss8649/image-edit-realtime-hackathon), [session-log.md](https://github.com/jss8649/image-edit-realtime-hackathon/blob/main/session-log.md), [commits](https://github.com/jss8649/image-edit-realtime-hackathon/commits/main).

- What it does: "Snap a phone photo of a chair, and Custom Universe turns it into a 3D object you can drop into a scene, restyle with a text prompt, and move around while the rendered image updates in real time." It is "aimed at robotics labs, which need large volumes of synthetic data to train robots for specific tasks and settings." (post)
- Sponsor tools and depth: "Opus 4.8 built the project end to end and operated the remote NVIDIA H100 that ran the model throughout the hackathon." Claude also picked models and wired in Apple RealityKit: "We asked Claude: add this to the pipeline." (post). Runtime models are not Claude: a self-hosted FLUX.2 Klein 9B image editor, a TRELLIS image-to-3D sidecar and Blender for USDZ files (README). 19 of 20 commits are co-authored by Claude.
- Autonomy: the product is a user-driven tool (it re-renders about 300 ms after each edit); no agent acts on its own. The session log is a written retrospective, not a transcript, and notes "An adversarial multi-agent review of the diff caught a camera-leak/abort-storm".
- Human story: Mauricio "brought the problem he knew firsthand: robotics still lacks training data, and building synthetic environments is hard." For Jake, "the scene builder started as a side project he had wanted to try." The two "met at the event." (post)
- Live URL: https://www.luminal.com/realtime-edit-demo (in the post; not opened). The README has no live URL; it needs a large GPU or a hosted provider.
- Team size: 2.
- Repo facts: 20 commits. The first, "initial", is dated Feb 26, 2026, months before the event; the other 19 run June 13 to June 15, 2026. 31 stars, 8 forks. Python FastAPI server, one index.html, Dockerfile. No tests, no CLAUDE.md or AGENTS.md.
- README structure: purely technical: what it is; requirements; run with Docker; manual quick start; how realtime works; model hosting (local, FAL, Fireworks, echo); environment variables; TRELLIS sidecar; API; next steps. No problem statement or story.
- Why it most likely won (my reading): the most visual live demo of the three and a clear user (robotics labs). Claude running the GPU box is an autonomy story. It shows the least written orchestration (no rubric file, no tests), which fits third place.

## MCP's 1st Birthday winners

### Cite-Before-Act MCP (Track 1 Best Overall). Deep-dived: yes (winners page via its source file, plus the repo)

Sources: [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte), [repo and README](https://github.com/bisonbet/Cite-Before-Act-MCP), [SPACE_README.md](https://github.com/bisonbet/Cite-Before-Act-MCP/blob/main/SPACE_README.md), [CLAUDE.md](https://github.com/bisonbet/Cite-Before-Act-MCP/blob/main/CLAUDE.md), [index.html landing page](https://github.com/bisonbet/Cite-Before-Act-MCP/blob/main/index.html), [commits](https://github.com/bisonbet/Cite-Before-Act-MCP/commits/main).

- What it does: an MCP proxy that sits in front of any MCP server. It "Intercepts all tool calls before execution", "Detects mutating operations using multiple strategies", "Generates human-readable previews of what would happen", "Requests approval via concurrent methods (native dialogs, Slack buttons, file-based) - first response wins", and "Executes only after explicit approval". "Read-only operations (like `read_file`, `list_directory`) execute immediately without approval." The repo description: "only on explicit approval by the human (or agent if configured) does it execute."
- Approval channels: native OS dialog, Slack buttons, Webex Teams cards, Microsoft Teams cards, and a file-based CLI fallback.
- Sponsor tools and depth: built on FastMCP; examples wrap the official Filesystem server and the GitHub MCP server, with Claude Desktop as the client. The repo was built with Claude (many commits co-authored by "claude", pull requests from `claude/...` branches). Per SPACE_README.md the Hugging Face Space is `sdk: "static"`, a landing page with a YouTube demo and a LinkedIn post, so I found no Gradio app (unverified for the live Space).
- Autonomy: acts with approval. Approval is the whole product.
- Human story: none found in the README, SPACE_README.md or the landing page.
- Live URL: https://huggingface.co/spaces/MCP-1st-Birthday/cite-before-act-mcp (blocked). Demo video https://www.youtube.com/watch?v=gZPYAwxf6Mo and a LinkedIn post (urn:li:share:7398425599721086976): could not be opened.
- Team size: commit authors bisonbet and Tim Champ; the Hugging Face author is bisonnetworking. One or two people (unverified).
- Repo facts: 105 commits. "Initial commit" on Nov 14, 2025 (the first hackathon day); most work Nov 15 to Nov 23; last commit Dec 2, 2025. 6 stars, 4 forks, AGPL-3.0, Python. CLAUDE.md present (11 sections, coding rules and test commands). I saw no tests/ folder in the listings, although CLAUDE.md lists `pytest tests/test_detection.py` (unverified whether tests exist).
- README structure: Overview; Features; Quick Start; Documentation; How It Works (text diagram and an 8-step example); Supported Approval Methods; Configuration; Examples; Development; License; Contributing; Acknowledgments.
- Why it most likely won (my reading): one small, general safety idea ("dry-run, approval, execute") that works with any MCP server, with approvals sent where people already work (Slack, Teams). It is exactly the human-control pattern Anthropic promotes.

### MCEPTION (Track 1 Best Enterprise). Deep-dived: no

- What it does: "This server allows you to create and deploy other MCP servers on Hugging Face Spaces." ([winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte)). Space: https://huggingface.co/spaces/MCP-1st-Birthday/MCEPTION (blocked).
- No GitHub repo found: the author's [GitHub profile](https://github.com/alihmaou?tab=repositories) (33 repos) has none by that name, and a GitHub search for "MCEPTION" returned only unrelated repos.
- Sponsor tools, autonomy, story, team, README: not known. Team size: 1 named author.
- Why it most likely won (my reading): an MCP server that ships MCP servers is a platform tool, which fits "Enterprise".

### Portfolio Intelligence Platform (Track 1 Best Consumer). Deep-dived: no

- What it does: "AI-powered portfolio analysis with transparent multi-agent MCP orchestration" ([winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte)). Space: https://huggingface.co/spaces/MCP-1st-Birthday/Finance-Portfolio-Intelligence-Platform (blocked).
- No GitHub repo found ([BrianIsaac's repos](https://github.com/BrianIsaac?tab=repositories) list none; a search for the name returned 0 results).
- Autonomy: suggests (analysis), per the one-line description (my reading). Team size: 1 named author.
- Why it most likely won (my reading): the word "transparent": the user can see which agent did what.

### GCP - Game Context Protocol (Track 1 Best Creative). Deep-dived: no

- What it does: "Build 3D scenes and games with natural language." ([winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte)). Space: https://huggingface.co/spaces/MCP-1st-Birthday/GameContextProtocol (blocked).
- No GitHub repo found ([ArturoNereu's repos](https://github.com/ArturoNereu?tab=repositories); a search for "GameContextProtocol" returned 0 results). Team size: 1 named author.

### Vehicle Diagnostic Assistant (Track 2 Enterprise, 1st). Deep-dived: yes (winners page via its source file, plus the repo)

Sources: [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte), [repo and README](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant), [hackathon_detail.md](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant/blob/main/hackathon_detail.md), [commits](https://github.com/castlebbs/Vehicle-Diagnostic-Assistant/commits/main).

- What it does: "For this second hackathon, we decided to have fun and created an AI agent that connects directly to your car and helps you diagnose issues." The MCP server runs on the car's diagnostic dongle: "Diagnostic MCP server, which we installed directly on an OBD-II device"; they "had to open it to replace the firmware with our special hackathon firmware". The agent calls the server over HTTP (JSON-RPC 2.0, `streamable_http`), and the firmware talks to the car through an ELM327 chip and the CAN bus. Tools: `get_system_status`, `send_elm327_command`, `get_history`.
- Sponsor tools and depth: Gradio 6 chat UI with streaming; a LangChain/LangGraph agent; models from the "Nebius Token Factory" (Qwen3-Coder-480B, Llama-3.3-70B, DeepSeek-R1). Claude is only an optional backend (`langchain[anthropic]`).
- Autonomy: suggests. It reads live data and explains it. The raw `send_elm327_command` tool could send any command, and the README describes no approval step (unverified whether write commands are blocked). The public demo uses a simulator Space because "we don't want everyone to mess with our car :-)".
- Human story: none beyond "have fun".
- Live URL: https://huggingface.co/spaces/MCP-1st-Birthday/Vehicle-Diagnostic-Assistant and a simulator Space (both blocked).
- Team size: 2: "@stargarnet: AI agent development" and "@castlebbs: MCP server and embedded firmware".
- Repo facts: 1 commit ("Inital commit", Dec 15, 2025), so the GitHub repo is a later copy of the Space code. 7 stars, MIT. Includes hackathon_detail.md, mcp_server_detail.md, demo_video.py, Dockerfile. No tests, no CLAUDE.md or AGENTS.md.
- README structure: hackathon context, team roles, how OBD-II works, architecture, LLM options, link to their previous hackathon entry.
- Why it most likely won (my reading): MCP running on real hardware in a real car, which is new, plus a safe simulator anyone can try.

### MCP Blockly (Track 2 Consumer, 1st). Deep-dived: yes (winners page via its source file, plus the repo)

Sources: [winners page source](https://github.com/gradio-app/gradio/blob/main/js/_website/src/routes/mcp-birthday-winners/+page.svelte), [repo and README](https://github.com/owenkaplinsky/MCP-Blockly), [commits](https://github.com/owenkaplinsky/MCP-Blockly/commits/main).

- What it does: "MCP Blockly is a visual programming environment for building real MCP servers without dealing with Python syntax or configuration." A "recursive Python code generator" turns blocks into Python on every change; one click deploys: "latest generated Python code is packaged with its dependencies and uploaded to Hugging Face Spaces".
- Sponsor tools and depth: Gradio 6 MCP format (commit "Change to Gradio 6 MCP format"), a generated Gradio test UI, Hugging Face Spaces for deployment, and the OpenAI API for the chat assistant ("OpenAI API Key: Enables the AI Assistant"). No Anthropic use found.
- Autonomy: the chat assistant edits the workspace directly (creates and deletes blocks, runs tests); the README describes no confirm step (my reading).
- Human story: none found.
- Live URL: https://huggingface.co/spaces/MCP-1st-Birthday/MCP-Blockly (blocked). Video https://www.youtube.com/watch?v=5oj-2uIZpb0 (could not be opened).
- Team size: 1.
- Repo facts: 79 commits; none on or before Nov 14, 2025 (GitHub's date filter shows no history up to that day), so it was built inside the hackathon window; latest on main Nov 26, 2025. 3 stars, MIT, JavaScript and Python. No tests, no CLAUDE.md or AGENTS.md.
- README structure: MCP Blockly; YouTube Video; What This Does; API Keys; Installation; Running Locally; How It Works; About.
- Why it most likely won (my reading): it lowers the bar for making MCP servers to "no Python needed" and closes the loop to a live deployed server.

## Build with DataHub winners

### Project Blackbox (Grand Prize). Alex's own project, summarised only

Blackbox ([repo](https://github.com/alejandro-publius/blackbox-datahub)) is an evidence-gated data incident agent: Claude investigates DataHub's context graph (official MCP server, Agent Context Kit, GraphQL), cannot confirm a root cause without lineage plus numeric evidence, and waits for an operator to press "Repair & Verify".
It then patches the SQL, passes 32 of 32 pipeline invariants, opens a real pull request and writes the incident resolution back to DataHub (51 commits, 58 unit tests, 11 machine-checked eval criteria, two upstream DataHub pull requests).

### Hindsight. Deep-dived: no (repo read; winners post blocked)

Sources: [repo and README](https://github.com/gmassello/hindsight), [SUBMISSION.md](https://github.com/gmassello/hindsight/blob/main/SUBMISSION.md), [AGENTS.md](https://github.com/gmassello/hindsight/blob/main/AGENTS.md), [commits](https://github.com/gmassello/hindsight/commits/main).

- What it does: "Your dashboard has been wrong since 03:00. Hindsight walks your DataHub lineage to find what broke it, ranks who it hits, and writes the answer back into the catalog - then re-reads every change through a different API to prove it landed." It saves each postmortem as a DataHub document and recalls it at the next incident. SUBMISSION.md reports a cold run versus a warm run in which memory cut tool calls (about 25%, approximate).
- Design: "Five decisions carry the design: Memory before investigation. Per-phase toolsets. All math and writes are code. Grounded hypotheses, and a verdict that can decline. Grounded mutations only." AGENTS.md: "a deterministic phase state machine with an LLM inside each phase, not a free ReAct loop".
- Sponsor tools and depth: "13 MCP tools (8 read, 5 mutation), multi-hop lineage, memory stored inside DataHub" (SUBMISSION.md); tags, ownership and documents are written back. Open source: a DataHub skill proposed upstream ([datahub-skills#110](https://github.com/datahub-project/datahub-skills/pull/110)). Model in the recorded runs: Gemini 3.1 Flash Lite (SUBMISSION.md); the README says Claude and Bedrock are also supported.
- Autonomy: acts with approval. The plan is shown "as a dry-run diff, with a rationale per mutation", and the web UI shows "the action plan as a diff with Approve / Reject".
- Human story: no named person. SUBMISSION.md maps real-world applicability to "Data on-call: concrete, expensive pain, backed by first-hand experience", and says the video "Opens with the real on-call pain (first 20 seconds → applicability criterion)".
- Live URL: https://gmassello.github.io/hindsight/ (a static replay of recorded runs; blocked here). Video https://youtu.be/y04gl1faens (2:33; could not be opened).
- Team size: 1.
- Repo facts: 34 commits, Aug 2 to Aug 23, 2026 (three after the Aug 10 deadline: badges and the video link). Apache 2.0. Python (FastAPI, SSE) backend, React frontend, docker-compose. AGENTS.md and CLAUDE.md, `.claude/`, `.agents/skills/datahub-incident-triage/`, CI workflows, 5 recorded example runs. Tests: `pytest` in backend; SUBMISSION.md reports 30 passing (approximate). SUBMISSION.md lists each of the six criteria with its evidence.
- README structure: "Data on-call, not ML drift"; "An agent that reports its own success proves nothing"; Start here; What it actually leaves behind; The 60-second run; How it works; "The memory lives in the catalog, not in a side database"; What gets written, and who inherits it; "Not what DataHub already gives you"; The workflow as a portable Skill; "Every claim, and where to check it"; Honest limits; Tests; Deeper; License.
- Why it most likely won (my reading): deep two-way use of DataHub with the memory stored inside the catalog (Originality and Use of DataHub), an approval gate on every write, and an upstream skill for the bonus. The README headings argue against self-reported success, in the same spirit as Blackbox.

### Paracelsus. Deep-dived: no (repo read; winners post blocked)

Sources: [repo and README](https://github.com/fiya-chris-and-AI/paracelsus), [explainer.html](https://github.com/fiya-chris-and-AI/paracelsus/blob/main/explainer.html), [engine/](https://github.com/fiya-chris-and-AI/paracelsus/tree/main/engine), [.env.example](https://github.com/fiya-chris-and-AI/paracelsus/blob/main/.env.example), [commits](https://github.com/fiya-chris-and-AI/paracelsus/commits/main).

- What it does: "Risk assessment for your data catalog. Ranks findings by how much harm can actually reach someone, not by how broken something looks." Formula: "Risk = Hazard x Exposure x Receptor-sensitivity x Uncertainty-factor". Exposure is "measured usage, not raw successor count"; receptor sensitivity "weights who's downstream (a finance dashboard is not a scratch table)"; and "missing evidence about a change raises the score instead of silently dropping it". The explainer: "Hazard is not risk. ... Toxicology has separated these two since the sixteenth century."
- Sponsor tools and depth: lineage traversal, imported usage statistics, an MCP server smoke test (`engine/mcp_smoke_test.py`), five structured properties written back per asset, risk-band tags, written assessments, and read-back checks of the writes.
- Role of the model: "The score is computed in plain Python, deterministically. No number in the output comes from a language model." The `.env.example` holds only DataHub settings, so the engine runs without a model key (my reading). The explainer says a model only turns results into sentences (approximate wording).
- Autonomy: writes metadata back on its own and recommends an action per asset (for example "Monitor" or "No Action"); it does not change pipelines. Mostly suggests.
- Human story: no named person; the framing is harm that reaches people downstream.
- Live URL: board at https://fiya-chris-and-ai.github.io/paracelsus/board/ (blocked). No video link in the README.
- Team size: 2 (commit authors Drfiya and Chriss54; several commits co-authored by Claude; some commit messages in German).
- Repo facts: 31 commits, Aug 8 to Aug 10, 2026 (as shown on GitHub). Apache 2.0, Python engine (risk_engine.py, exposure.py, write_back.py, recommended_action.py, weights.yaml and more), static board, Makefile, docker/, seed/ with seeded demo defects. No tests folder, no CLAUDE.md or AGENTS.md.
- README structure: Paracelsus; Prerequisites; Quickstart; How the demo numbers reproduce; "Honesty boundary: what's real, what's curated"; Troubleshooting; Known fragility; License. Honesty section: "Five specific assets carry deliberately seeded, disclosed defects...what's curated is the input (a plausible defect story), not the scoring logic."
- Why it most likely won (my reading): Originality. It replaces naive "blast radius" with a tested method from drug safety, keeps every number deterministic and reproducible, and is honest about what was seeded.

### Culprit. Deep-dived: no (repo read; winners post blocked)

Sources: [repo and README](https://github.com/JonathanSolvesProblems/culprit), [commits](https://github.com/JonathanSolvesProblems/culprit/commits/main), [culprit/ package](https://github.com/JonathanSolvesProblems/culprit/tree/main/culprit).

- What it does: "A stack trace for model decay. It names the column, prices the damage, and opens the PR." Built on a real incident: a new taxi vendor appeared in the NYC Taxi and Limousine Commission feed in December 2024, and the README reports "$90,322 of attributable model error in a single month, across 66,146 real NYC taxi trips, caused by one upstream column's maximum value changing from 6 to 7", or "$1.37 a trip, measured in SQL against 19.3M real records and net of a counterfactual control".
- Self-check shown in the README: "Its first attempt was this: + where vendor_id in (1, 2, 6). That does not encode the new vendor. It deletes all 87,693 of its rows. It compiles. dbt build passes." Then: "The row-count gate caught it and refused to open the PR".
- Sponsor tools and depth: "Reads through DataHub's own MCP server" (launched over stdio); lineage ingested by DataHub's own dbt connector; "Emits 13 mlFeatures, an mlFeatureTable, an mlModel and a dataProcessInstance training run through the DataHub Python SDK"; "raises a DataHub Incident (CUSTOM / Semantic drift / HIGH)" and annotates the source column. Open source: "One issue filed, two threads engaged, and one skill drafted". The agent is provider-agnostic; the recorded run used gpt-4o, and the Anthropic default is written as "claude-sonnet-5".
- Autonomy: acts alone up to a pull request: "It patches the transformation, runs `dbt build` against the real warehouse, and only opens a PR if the fix actually holds up." A human merges (my reading).
- Human story: no personal story; the hook is a real public incident priced in dollars.
- Live URL: none; there is a replay path ("See it without a key, without Docker, without a warehouse"). Video https://www.youtube.com/watch?v=KCjyNTgBp8k (could not be opened).
- Team size: 1.
- Repo facts: 46 commits, Aug 2 to Aug 10, 2026. Apache 2.0, Python, a dbt pipeline, contrib/ (upstream contributions), examples/ with the recorded run. No tests folder, no CLAUDE.md or AGENTS.md. Commit messages show a "mechanical claim check" and a "truth pass" that corrected six claims before submission.
- README structure: 24 sections, opening with "The number", then "Then it wrote the fix, and rejected its own first attempt", a no-setup path, "For judges: where each criterion is answered", the problem, the real incident, primary sources, "The obvious objection", what it does, the recorded run, how the run was chosen, the generated fix, the graph, how it uses DataHub, measuring the damage, quickstart, choosing a model, "What is real", "Limitations", layout, "Design note: the model is the engine", license.
- Why it most likely won (my reading): a dollar figure on real data, a fix that had to prove itself, a visible self-rejection, and a README that answers each judging criterion by name.

### The other three DataHub winners

Not found. Seven project prizes were paid (1 grand, 4 challenge, 2 honourable mentions), and only four names are known. What the winners post says about why each project won could not be read (datahub.com is blocked).

## What judges rewarded

### Build Day (Anthropic judges)

- The rubric weights the result most: Impact 35% and Demo 35%, against Autonomy 15% and Orchestration 15% (team copy). "Does the demo prove the impact?"
- Claude checking its own work, in a separate context. All three winners did it: Tekton's "Independent verifier sub-agents graded each reconstruction in isolated context windows"; Sim Francisco had "Claude work alongside a verifier and an adversarial agent"; Custom Universe's log notes "An adversarial multi-agent review of the diff". The rubric asks: "When something broke, did the model catch it itself (via a test, a check, a verifier)?"
- Proof of autonomy you can read: committed session logs and kept failure reports ("a logged fail→revise→pass cycle is the autonomy evidence; do not delete it", Tekton kickoff prompt).
- "Done" that a machine can check: rubric files (done.rubric.json, rubric.yaml), a green build, a responding URL. Both top teams wrote the judging criteria into their own build instructions.
- Numbers checked against the real world (Sim Francisco's 81.3% against an actual 83.8%) or against cited sources (Tekton).
- A plain human reason in the first lines (buildings lost to fire; robotics labs short of data).
- The runtime model did not have to be Claude: Sim Francisco's scored backtest ran on GPT-4o and Custom Universe runs FLUX.2 and TRELLIS. Judges scored how Claude built it.
- An earlier prototype did not block a win: Tekton's first commits are from the day before the event, and Custom Universe has a commit from February 2026. The post mentions Holly's earlier prototype; the guide says the demo "must only highlight" features built during the hackathon (my reading from commit dates).

### MCP's 1st Birthday (Anthropic and Gradio)

- No judge statement or criteria found. From the awards (my reading):
- Human control won the top prize: Track 1 Best Overall went to "Human-in-the-loop safety middleware for MCP servers. Require explicit approval before state-mutating operations."
- Tools that make more tools won twice: MCEPTION ("create and deploy other MCP servers") and MCP Blockly ("AI that makes MCP servers with block-code").
- MCP outside the laptop won Track 2 Enterprise: an MCP server on a car's diagnostic dongle.
- "Transparent" orchestration was named in the Best Consumer line.
- Winners did not need Claude at runtime (Nebius models, OpenAI), and the top winner's Space is a static page with a video, per its SPACE_README.md (the live Space is blocked).

### Build with DataHub

- Stated criteria (team copy): Use of DataHub (with writing back preferred), Technical Execution end to end, Originality "beyond features DataHub already provides", Real-World Usefulness, Submission Quality, and an open source Bonus. Equal weight.
- All four known winners write results back into DataHub (incidents, documents, tags, structured properties).
- All four make code, not the model, decide what is true: Blackbox's evidence gate and invariants, Hindsight's "All math and writes are code", Paracelsus's "No number in the output comes from a language model", Culprit's row-count gate and real `dbt build`.
- Human control before risky changes: Blackbox's "Repair & Verify" button, Hindsight's Approve / Reject on a dry-run diff, Culprit stopping at a pull request.
- Honesty sections ("What's real vs. synthetic", "Honesty boundary", "Honest limits", "What is real").
- A "For judges" map from each criterion to evidence (Blackbox, Culprit, Hindsight's SUBMISSION.md).
- Upstream contributions for the bonus (Blackbox, Hindsight, Culprit).
- Solo builders won three of the four known prizes.

### Across all three (my reading)

1. Verification is the story judges remember: separate verifier or critic agents, plus deterministic gates that refuse bad output, shown live.
2. A human approves the step that matters (merge, repair, state change), and everything up to that step is automated.
3. "Done" is machine-checkable and written down (rubric file, tests, invariants), and the README says which criterion each piece answers.
4. Real data and a number a judge can check, with an honest list of what is synthetic.
5. One plain human reason in the first lines.

## Blocked

- https://cerebralvalley.ai/e/claude-startups-build-day : WebFetch EGRESS_BLOCKED (1 attempt). Used the guide copy in the Tekton repo instead.
- https://huggingface.co/MCP-1st-Birthday : WebFetch EGRESS_BLOCKED (1 attempt). All Hugging Face Spaces of the MCP winners are therefore unread.
- https://gradio.app/mcp-birthday-winners : WebFetch EGRESS_BLOCKED (1 attempt). Read the page's source file in the Gradio GitHub repo instead.
- https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/ : WebFetch EGRESS_BLOCKED (1 attempt). What the post says about why each project won is unknown.
- Live demos, WebFetch EGRESS_BLOCKED: https://tekton-build.vercel.app/ , https://simfrancisco.org/ , https://gmassello.github.io/hindsight/ , https://fiya-chris-and-ai.github.io/paracelsus/board/ . Not tried: https://www.luminal.com/realtime-edit-demo .
- https://api.github.com/repos/bisonbet/Cite-Before-Act-MCP/git/trees/main?recursive=1 and https://api.github.com/repos/bisonbet/Cite-Before-Act-MCP/commits?per_page=100&page=2 : HTTP 403 (an earlier api.github.com call for Tekton worked). Used github.com commit pages with date filters instead.
- GitHub search, HTTP 429 once each: https://github.com/search?q=%22Build+with+DataHub%22&type=repositories and https://github.com/search?q=datahub+hackathon+winner&type=repositories . Later searches worked.
- https://github.com/tejasprabhune/simfrancisco/tree/main/.claude : HTTP 404 (the folder the README describes is not in the public repo).
- The summarizer refused a long verbatim copy of https://raw.githubusercontent.com/tangxiya-star/Tekton/main/CLAUDE_FABLE_5_BUILD_DAY_GUIDE.md on the second attempt; short quotes came from the github.com blob URL.
- Videos, not opened (youtube.com blocked): Cite-Before-Act https://www.youtube.com/watch?v=gZPYAwxf6Mo ; MCP Blockly https://www.youtube.com/watch?v=5oj-2uIZpb0 ; Hindsight https://youtu.be/y04gl1faens ; Culprit https://www.youtube.com/watch?v=KCjyNTgBp8k . Build Day demo videos were not linked in the post.
- Not tried (known blocked): devpost.com (rules, galleries and project pages, for example https://devpost.com/software/project-blackbox), x.com, linkedin.com (Cite-Before-Act's post), web.archive.org.
- Not found anywhere I could reach: MCP's 1st Birthday judging criteria, judges, prize amounts and submission count; the Build Day judges' names and finalists 4 to 6; the names of three DataHub winners and the prize level of Hindsight, Paracelsus and Culprit; repos for MCEPTION, Portfolio Intelligence Platform and GCP.
