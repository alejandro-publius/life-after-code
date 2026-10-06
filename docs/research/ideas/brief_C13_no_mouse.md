# C13 No Mouse (merged with Spoken Diff): build brief and skeptical review

Written 2026-10-06 for Alex Velazquez's Path A entry in Life After Code. Read for this brief: [CANDIDATES.md](CANDIDATES.md); No Mouse (2.4) in [lens_oncall_inversion.md](lens_oncall_inversion.md) and Spoken Diff (1.1) in [lens_people_rituals.md](lens_people_rituals.md); the C13 entries in [scores_anthropic_judge.json](scores_anthropic_judge.json), [scores_gitlab_judge.json](scores_gitlab_judge.json), [scores_google_judge.json](scores_google_judge.json) and [scores_engineer.json](scores_engineer.json); [IDEATION_BRIEF.md](../IDEATION_BRIEF.md); [SPONSORS.md](../../SPONSORS.md) sections 1, 5 and 6; [RULES_CHECK.md](../../codex/RULES_CHECK.md); [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md) (the "guide"); [FIELD.md](../../FIELD.md); [deploy/README.md](../../../deploy/README.md); [AGENTS.md](../../../AGENTS.md). New today: five web searches, GitLab doc sources read from gitlab.com, and package registry lookups. Most vendor and research sites are blocked from this session, so those facts are search excerpts and are marked. Nothing below has run on GitLab or Google Cloud yet.

**Short version.** Keep No Mouse in the top three, at an adjusted 84.8 of 110 (was 85.6). Its honest autonomy level is Supervised, and its special prize is Most Creative, not Most Stages Covered. It touches all nine stages, five of them in a way specific to the idea. The load-bearing risk is that Claude must choose every key inside the GitLab loop. A one-component probe flow settles that on day one, and a CI fallback keeps Claude choosing the keys if no browser runs inside the flow.

## 1. Name and pitch

**No Mouse.** Keep the name. It says the agent's rule in two words, and it echoes the #NoMouse Challenge, a yearly awareness week in which people try the sites they use with the keyboard only (Wake Forest University ran one February 9 to 15, 2026: [accessibility.wfu.edu](https://accessibility.wfu.edu/?p=2475), search excerpt). No known entry uses the name. It is not among the 7 October ideas in [FIELD.md](../../FIELD.md), no gitlab.com project created since about Sep 27 matches "no mouse" or "nomouse" (projects API, checked today), and the October hackathon group still holds only the two staff workspaces (checked today). "By Ear" describes the method a little better, but it is not clearly better. Brand the agent "No Mouse, powered by Claude" ([SPONSORS.md](../../SPONSORS.md) 3.9).

**Pitch:** Before a release reaches production, an agent with no mouse and no screen must buy something on staging using only what a screen reader would announce. If a person who relies on a screen reader would get stuck, it holds the release, lets the developer hear what that person would hear, and opens the fix.

## 2. Who it is for, and their story

**For:** small product teams that ship every week with no accessibility specialist and nobody who uses a screen reader. The people it protects are their customers who do.

**Story.** Maria (a persona, not a real customer) is blind. For four years she has ordered coffee beans from the same small online shop every month with her screen reader, jumping by headings and typing ahead faster than most people click. On Friday the shop's developer merges a checkout redesign that turns the Pay, Edit cart and Coupon buttons into icons. Nobody notices, because nobody on the team uses a screen reader. Before the redesign reaches production, No Mouse makes Maria's purchase on staging by ear and hears "button, button, button" where it used to hear "Pay now, 18 dollars, button". It holds the release and hands the developer the recording and a one-line fix, so Maria's next order goes through as it always has.

Rules for the video and README: Maria is skilled, and the barrier is the shop's bug. Use no sad music, no "suffers" and no blindfold metaphors. Label her as a persona everywhere ([AGENTS.md](../../../AGENTS.md) rule 2), and say plainly that the tool does not speak for blind people.

## 3. The demo moment and a 2:40 video

**The moment.** The video opens on a black screen. A synthetic voice reads the checkout the way a screen reader would: "Checkout, heading level 1. Ethiopia Yirgacheffe, 12 ounces, 18 dollars. Button. Button. Button." Then a caption: "What Maria (persona) would hear after Friday's redesign." Later the same voice says "Pay now, 18 dollars, button. Order placed, heading level 1." The viewer feels the gap between the two clips without being told. A short calibration clip makes the scene honest: if Alex can, he records the same broken staging page once with a real screen reader (VoiceOver on his phone) saying "button".

| Time | Picture | Sound and words |
|---|---|---|
| 0:00 to 0:20 | Black screen. Small caption: "Simulated screen reader output, read aloud by Google Cloud Text-to-Speech." | The broken checkout, read aloud. Caption: "What Maria (persona) would hear after Friday's redesign." |
| 0:20 to 0:35 | The shop page, with the focus ring hopping across three icon buttons | "Maria has ordered here every month for four years with a screen reader. On Friday a redesign turned Pay into an icon. Nobody on the team uses a screen reader, so nobody heard it." |
| 0:35 to 0:50 | Title card: No Mouse | "Before every release, an agent with no mouse and no screen has to buy something on staging, using only what a screen reader would announce. The model chooses every key. Code decides what happened. A person decides what ships." |
| 0:50 to 1:25 | Real run, sped up: the merge click, the pipeline, the replay failing at Pay, the Duo session opening. Split screen: on the left, the agent's ears (what it heard, the key it chose, one line of why); on the right, the page with a focus ring, for the viewer only | The agent's own lines ("Three buttons with no names. I will try the first." "Coupon code, edit text." "Not it."). Then the code's verdict card: for example "GUESSED: two unnamed buttons pressed, one sent me back to the cart. WCAG 2.2 4.1.2. Release held." |
| 1:25 to 1:50 | The issue the flow opened (transcript, audio, the MR that caused it), then the fix MR with a one-line diff. The developer presses play and listens | "It holds the release, finds the line that caused it, and opens a one-line fix. On its own, its only power is to hold." |
| 1:50 to 2:10 | The fix MR: a tagged Cloud Run revision and a green replay. Before and after clips, back to back. A person merges | "Button." then "Pay now, 18 dollars, button. Order placed." |
| 2:10 to 2:28 | The manual production job and the Play click, the production replay going green, and the GitLab Release with "Maria's path: clear, 31 keys" and the audio | "A person ships it. Production is walked again after the deploy." |
| 2:28 to 2:40 | End card: three rules and the sponsors | "A Duo custom flow running Claude, served from Google Cloud. Cloud Run and Text-to-Speech. Simulated screen reader output: it does not replace testing with screen reader users." |

## 4. End-to-end flow (one loop)

A journey is a file a person writes, for example `journeys/maria-monthly-beans.yml`: start page, goal in plain words, success check (an order exists for this walker session), and a budget of 60 actions. The first time a journey runs, there is no recorded path yet. The listener walks it, and the flow opens an MR that records the path it found. After that, every release goes through this loop:

1. **A person merges** the redesign MR into `main` (merge request). This is the human action that lets the pipeline's events start a flow later. The guide quotes the rule: "All trigger event types require a human user to perform the triggering action."
2. **Build, scan, package** (CI/CD pipeline). The pipeline runs unit tests and GitLab's SAST and secret detection templates, then builds and pushes the shop image (container registry, or Artifact Registry through Cloud Build as in [deploy/](../../../deploy/README.md)).
3. **Deploy to staging** (environments and deployments). The pipeline deploys the Cloud Run service `shop-staging` keylessly, through Workload Identity Federation with `id_tokens`, and records the deployment on the `staging` environment.
4. **Replay by ear, code only** (CI job `replay-staging`, with a JUnit test report and job annotations). Playwright replays each recorded path, pressing keys and reading only the accessibility tree. Every announcement must match the recorded path, and the shop's test endpoint must show the order. GitLab's own Pa11y template (`Verify/Accessibility.gitlab-ci.yml`) checks the visited pages for rule violations and fills the accessibility report ([doc source](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/ci/testing/accessibility_testing.md)). A `speak` job turns each transcript into an MP3 with Google Cloud Text-to-Speech. If every journey is clear, skip to step 12. Otherwise the job fails, and so does the pipeline.
5. **The flow starts** (custom flow `no-mouse`, trigger **Pipeline events: Failed**). It receives the pipeline payload as its goal (guide, "Goal values by trigger type").
6. **Listen, model** (flow component `listener`). Claude walks the failing journey on staging through the walker, choosing every key from what it hears. Fallback: a CI job, `listen-staging`, runs the same walk with Claude on Google Cloud, and the flow reads its log with `get_job_logs` ([tools doc source](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/duo_agent_platform/agents/tools.md)).
7. **Verdict, code** (`nomouse verdict`). Code reads the walker's log and the shop's order record and returns one of four outcomes: clear, friction, guessed or blocked. It also returns the element, the WCAG 2.2 criterion and the spoken diff against the recorded path (the Spoken Diff part).
   - Clear: the page changed, but Maria can still pay. The flow opens an MR that updates the recorded path.
   - Friction: paying still works, but takes more than 25% more actions. The flow asks a person through a `HumanInputComponent` whether to accept the new path.
   - Guessed or blocked: the release stays held.
8. **Find the cause, model** (component `investigator`). It reads the MRs in this deployment (Deployments API, through `gitlab_api_get`), their diffs (`list_merge_request_diffs`) and the templates, and names the line that removed the name.
9. **Report and fix, model** (component `writer`; issues and merge requests). It opens an issue with the transcript (written by code), the audio, the WCAG criterion and the MR that caused the barrier. It also opens a fix MR (`create_commit`, `create_merge_request`) with the smallest change and "Closes #N".
10. **Re-walk the fix** (merge request pipeline, review app). The fix MR deploys a no-traffic Cloud Run revision under the fixed tag `fix` (dynamic environment `review/fix`). The pipeline replays the journey there and runs the Pa11y job, so the MR shows the result and the before and after clips before anyone merges. If the page structure changed and only the model can judge it, a person marks the MR ready (**Merge request: Marked ready** trigger), and the flow walks the `fix` URL. There are at most two rounds (section 6).
11. **A person merges the fix.** Steps 2 to 4 run again, and this time `replay-staging` is clear.
12. **A person approves production** (manual job). `deploy-production` is `when: manual` and `needs` the clear replay, and its annotations show the summary. A person presses Play. A hold can be lifted only by merging an override file that gives a reason (`holds/<short-sha>.yml`).
13. **Walk production, then release** (environment `production`, Releases). `replay-production` replays the journey on `shop-production` with a test-mode order. Then `glab release create` publishes a release that says "Maria's path: clear, 31 keys" and links the audio. A daily scheduled pipeline repeats the production replay (monitor). The production walk never closes or reopens issues; the issue already closed when the fix merged.

## 5. Lifecycle stages

| Stage | Covered | GitLab feature | Real or demo data |
|---|---|---|---|
| Plan | Yes | Issue opened by the flow (transcript, audio, WCAG criterion, the MR that caused it, labels); journeys are files a person merges; a production failure becomes an incident | Real issues. Maria, the shop and the planted regression are labelled demo data |
| Create | Yes | Fix MR, plus the recorded-path MR (the agent writes a regression test from its own walk), through `create_commit` and `create_merge_request` | Real code changes |
| Verify | Yes (the core) | Pipelines, `replay-staging`, the listener walk, the JUnit test report, the Pa11y accessibility report and MR widget, a review app on a tagged Cloud Run revision | Real |
| Package | Touched | Shop image and walker image in the container registry (Artifact Registry for Cloud Run) | Real, not agentic |
| Secure | Touched | SAST and secret detection templates; least privilege for the agent itself: the sandbox network allowlist, keyless Google auth, a listener that cannot write, page text treated as data, and one prompt-injection page in the eval set | Real; the injection page is demo data |
| Release | Yes | Environments `staging` and `production`, the hold through `needs`, the manual production job, the override file, and a GitLab Release with transcript and audio | Real |
| Configure | Touched | `.gitlab/duo/agent-config.yml` (image, network policy); journeys and budgets as files; the Cloud Run and WIF setup scripts in `deploy/` | Real, thin |
| Monitor | Yes | A production replay after each deploy, a daily scheduled replay, and an incident on failure | Real. Whether a scheduled pipeline can start the flow is unverified |
| Govern | Yes | Gates only a person can pass (merge, Play, an override with a reason); CODEOWNERS on `journeys/`, `holds/` and `.gitlab/duo/`; sessions and release evidence as the audit trail | Real. Code owner approval rules need Premium and setup rights (unverified) |

All nine stages are touched. Five are specific to the idea: plan, create, verify, release and monitor; govern is half and half. Package, secure and configure come with any sound pipeline, and the brief does not claim more for them. The two additions that cost little and are honest are the recorded-path MR (create) and the production replay (monitor). An optional extra for configure, about one day: ship the redesign behind a GitLab feature flag, so a hold can become "ship everything, but keep the new checkout off" (a person flips the flag).

## 6. The agent loop

There are three model roles and one walker, and code makes every decision. The components follow GitLab's reader and writer split ([SPONSORS.md](../../SPONSORS.md) 2.5, point 3).

| Role | May | May not |
|---|---|---|
| Listener (model) | Choose each action from a fixed menu: press Tab, Shift+Tab, Enter, Space, Escape, arrows, Home or End; type into the focused field; jump to the next heading, landmark, form field, button or link; list headings, landmarks, buttons, links or fields (like a screen reader's elements list); hear the current item again; say "stuck" with a reason | See screenshots, pixels, HTML, CSS or the DOM; use a mouse or coordinates; reach the shop except through the walker; write to GitLab; decide pass or fail |
| Investigator (model) | Choose which MRs, diffs and files to read, and name the cause | Write anything |
| Writer (model) | Word the issue, choose the smallest fix, write the MR description | Change the transcript (code quotes it); touch `journeys/`, `holds/` or the CI file; merge, approve, deploy or lift a hold; contact anyone outside the project |

**Code decides** what the listener hears: announcements rendered from the accessibility tree by one file of rules, tested on fixtures. Code also decides the verdict (an order exists for this walker session within budget; no unnamed control or unlabelled field was acted on; no focus trap, meaning the same focus for 3 presses of Tab). It maps barriers to WCAG 2.2 criteria (4.1.2 Name, Role, Value; 2.1.1 Keyboard; 2.1.2 No Keyboard Trap; 2.4.3 Focus Order; 1.1.1 Non-text Content; [WCAG 2.2](https://www.w3.org/TR/WCAG22/)), computes the spoken diff, enforces every budget, and decides whether production may deploy (the `needs` rule plus the override file). One wall holds in every design: nothing reaches production without a code replay in a normal CI job, whatever the model did in the flow.

**The person decides**, each time through a GitLab mechanism:

- which journeys exist, and their budgets (merging `journeys/`);
- whether a slower path is acceptable (approve or reject at the `HumanInputComponent` in AI > Sessions; this component is untested in trigger-started flows, so the fallback is a comment that mentions the flow);
- whether the fix merges (the merge request);
- whether the release ships (Play on the manual job);
- whether a known barrier ships anyway (merging `holds/<sha>.yml` with a reason);
- whether the agent tries again after round one (a mention, or marking the MR ready).

**Time boxes** (rule 5 in [AGENTS.md](../../../AGENTS.md)):

| Loop | Limit |
|---|---|
| Listener walk | The budget in the journey file (60 actions for checkout; the clean path is planned at about 31), 10 minutes, and a stop when the same announcement repeats 3 times with no change |
| Each model call in the flow | `params.timeout: 120` seconds. Custom flows reject `max_cycles` ([SPONSORS.md](../../SPONSORS.md) section 6, row 1), so shape and timeouts are the box |
| Investigator, writer | 15 tool calls and 5 minutes each (a prompt rule, checked in the session log) |
| Replay | 3 minutes per journey; CI `timeout: 10m` |
| CI fallback listener | 60 actions, 10 minutes, at most $1 of model spend per walk (code counts tokens) |
| Speech | 5,000 characters per clip |
| Whole flow session | 30 minutes (the workload job timeout is unverified) |

**Two-round limit** (AGENTS.md: "At most two review rounds on any change, then ship it or drop it"). Round 1 is the writer's fix MR and its replay. Round 2 happens only if a person asks, and it allows one revision. If round 2 still fails, the flow stops, labels the issue `needs-person` and posts what it heard; the person then fixes the barrier by hand or closes the agent's MR. The same cap applies to Duo Code Review rounds on the fix MR.

## 7. What it needs from Google Cloud

| Need | Use | Free tier and cost notes |
|---|---|---|
| Demo shop, staging | Cloud Run `shop-staging`: min 0 and max 1 instances, request billing | 2 million requests, 180,000 vCPU-seconds and 360,000 GiB-seconds free per month per billing account ([SPONSORS.md](../../SPONSORS.md) 4.1). One walk is a few hundred requests |
| Demo shop, production (the public link for the bonus) | Cloud Run `shop-production`. The deploy skeleton creates only one service ("Set up a separate service and trust configuration before treating another environment as separate production", [deploy/README.md](../../../deploy/README.md)), so Codex adds the second | Same free tier, shared |
| Fix previews | `gcloud run deploy --no-traffic --tag fix` on the staging service | No extra service; idle revisions cost nothing |
| Audio | Cloud Text-to-Speech, called keylessly from the `speak` job | Standard and WaveNet voices: first 4 million characters a month free, then $4 per million. Neural2 and Chirp 3 HD: first 1 million free. Gemini-TTS: no free tier. Billing must be on ([pricing](https://cloud.google.com/text-to-speech/pricing), read today). A transcript is 1,000 to 3,000 characters. The exact IAM role for the CI identity is unverified |
| Images | Cloud Build and Artifact Registry, as in `deploy/` | 2,500 build-minutes a month and 0.5 GiB of storage free, so add a cleanup policy ([SPONSORS.md](../../SPONSORS.md) 4.1) |
| Fallback listener, only if needed | Claude on Google Cloud's Agent Platform, called from CI with WIF | Billed per token. Whether the $300 Free Trial and its default quotas allow partner models is unverified |

Stay on the Free Trial: started Oct 6, its $300 lasts about 90 days, to about Jan 4, 2027, which is past judging. Budgets alert but do not cap spending, so keep `--max-instances` low ([SPONSORS.md](../../SPONSORS.md) section 1, fact 7). Nothing on the public shop calls a model, so visitors cannot run up a bill. Judges get a live shop they can test themselves: "Put your mouse away and buy a bag of coffee." An optional `/heard` page on the production service could list recent walks with audio, read from GitLab's public API (about 80 lines).

## 8. How Anthropic models show up

- **Inside GitLab.** The flow's three agents run on Duo's default model, Claude Sonnet 4.6, served from Google Cloud's Agent Platform. Custom flows reject a `model` field, and only the top-level group Owner (GitLab) can change the model ([SPONSORS.md](../../SPONSORS.md) section 1, fact 3). The README and video should say plainly that we did not pick it.
- **One skill format for both tools.** `skills/screen-reader-walk/SKILL.md` describes how experienced screen reader users move: headings first, then landmarks and form fields, then Tab. `skills/accessible-fix/SKILL.md` says to prefer visible text or a native button over `aria-label`, and never to put `role=button` on a div. Duo flows read these through `workspace_agent_skills`, and Claude Code reads the same files.
- **The fallback walker** is Claude on Agent Platform, called from CI. It uses the Anthropic SDK, or `claude -p` with the walker as its only MCP server and `--allowedTools` limited to it. It uses full model names (`claude-sonnet-5-5`, or `claude-haiku-4-5` for cheap steps) and structured output for each action, which code validates.
  - Cost per walk: about 60 calls of about 5,000 input tokens each, roughly $0.70 at Sonnet 5.5's $2 and $10 per million before caching.
  - The same walk in Duo is about 60 calls, about 30 GitLab Credits at Sonnet 4.6's listed rate of 2 calls per credit ([SPONSORS.md](../../SPONSORS.md) 2.1, Credits).
  - That is why the free code replay runs first.
- **No computer use, no screenshots,** on purpose. The constraint is the product.
- **Evals before the demo.** Build 12 fixture pages: 6 clean, and 6 with one barrier each (unnamed button, unlabelled field, focus trap in a dialog, a custom dropdown the keyboard cannot open, focus lost after "Add to cart", an image CAPTCHA). Add one page with injected instructions in a product review. Publish the listener's verdicts against the expected ones in the README. Past Anthropic winners wrote specs and evals early ([IDEATION_BRIEF.md](../IDEATION_BRIEF.md)).
- **The builders.** Claude Code (with Codex) writes the code, and the README says so.

## 9. Autonomy level and prize strategy

The official levels ([RULES_CHECK.md](../../codex/RULES_CHECK.md)):

- **Assisted:** "you approve every step".
- **Supervised:** "you approve the outcome, not the individual steps", with the example "You get a summary and approve the production deployment".
- **Hands-off:** "A full loop from code to production with no human in the middle".

**No Mouse is Supervised.** With nobody watching, the agents replay, listen, judge (in code), find the cause, write the issue and the fix, and re-walk it. A person approves the outcome twice: by merging the fix and by pressing Play on production. Two of the three scoring judges called it Hands-off, because its only independent power is to hold. By the official text, though, a person in the middle makes it Supervised. Making it Hands-off would mean auto-merging the agent's fixes and auto-promoting releases. That is the reference project's loop with one more check, and it breaks the project rule that a person decides what ships.

**Prizes.** Each project can win one path prize and one special prize.

- **Path prize: Path A, Best Supervised Agent ($4,000).** The likely rivals are release gatekeepers with a human gate, because the official Supervised example describes one almost word for word. On screen, No Mouse looks different from all of them. AfterMerge is the only known Path A entry with a gate, and it is a simulation with no Duo use found ([FIELD.md](../../FIELD.md)).
- **Special prize: Most Creative ($4,000),** which goes to the top Innovation score. No Mouse has the highest innovation score in our pool (9.0). It should not aim for Most Stages Covered: its count of stages covered in a creative way is about five, and rivals already claim all nine. It should not aim for Most Environmentally Impactful either.
- **Do not claim Hands-off.** A setting `auto_promote_when_clear` can exist for teams that want it, but it stays off in the demo.

## 10. The load-bearing risk, the fallback, and the day-one test

**The risk.** Claude has to choose every key, inside the GitLab loop, from announcements alone, and finish a checkout of 30 to 60 steps in minutes. If that fails, the concept shrinks to a scripted keyboard test with a voice-over. The Anthropic judge's file calls this a conditional trap: "the model becomes decoration and the concept collapses into a smoke test" ([scores_anthropic_judge.json](scores_anthropic_judge.json)). Two things can fail:

- **The platform:** a browser that the flow can drive and that can reach staging. That involves a custom image, the sandbox, a network allowlist on the default branch, and possibly strict mode, which ignores project allowlists ([sandbox doc source](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/duo_agent_platform/environment_sandbox.md)).
- **The model:** whether text alone is enough to finish the clean checkout every time, without false holds.

**Fallbacks, in order:**

1. **Same walker, browser outside the sandbox.** Start the browser from `setup_script`, which runs outside the sandbox, or use a custom image without the sandbox runtime. GitLab says that without SRT "your flow can access any domain reachable from the runner and the full file system" ([images doc source](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/duo_agent_platform/flows/execution/images.md)), so our code must then limit the browser to the staging host.
2. **Listener in a CI job, with Claude on Google Cloud.** Code owns the loop and the browser, and the model gets only the action menu. The flow keeps the investigator and writer roles and reads the listener's log. Claude still chooses every key; Duo does the finding and fixing.
3. **Last resort: no model in the walk.** A scripted replay produces the spoken transcript and audio (the Spoken Diff form), and the flow reports. This keeps the scene but costs about 6 points (section 13).

**Day-one test.** It needs the GitLab workspace with merge rights on `main` (the same day-one check every concept needs) and takes about 90 minutes:

1. Commit a probe `.gitlab/duo/agent-config.yml` to `main`:
   - `image:` Microsoft's Playwright Python image (`mcr.microsoft.com/playwright/python`, matching Playwright 1.63.0, today's PyPI release). Check that it has `git` and `curl`, which GitLab requires in custom images.
   - `allowed_domains:` the exact host of the placeholder Cloud Run service from `deploy/`.
2. Create a one-component custom flow, `nomouse-probe`, with toolset `[run_command]` and the prompt: "Run `python -m nomouse probe --url <staging URL> --tabs 5` and paste its output exactly."
3. Start it by mentioning the flow's service account in an issue comment (a human action).
4. It passes if, within 5 minutes, the session's final answer shows the browser version, the page title and five announcements from five presses of Tab, and the job log says whether the sandbox was active. Record the seconds per step.
5. If it fails inside the sandbox, rerun with the browser started from `setup_script` as a local service (fallback 1), then with an image that has no SRT. If all of these fail, run fallback 2's own check: one CI job with `id_tokens` gets a Google token through WIF and receives one valid action from Claude on Agent Platform.

Decide by Oct 8: the first passing variant decides where the listener lives.

**Test B, today, without Alex.** The builder runs the walker against the local shop and plays the listener by hand, reading only the text (no HTML, no screenshots). It passes if the clean checkout takes at most 40 actions and the planted checkout cannot be finished without pressing an unnamed button. This settles whether the screen reader view carries enough information, before any platform work.

## 11. Red team

**Prior art.** An AI agent that walks pages like a screen reader user is not new in industry or research in 2026.

- A U.S. patent application published Aug 20, 2026 describes an agent that mimics assistive technology flows to find accessibility issues, and Perforce released agentic accessibility testing in August ([aiagentstore, 2026-08-18](https://aiagentstore.ai/ai-agent-news/topic/accessibility-inclusion/2026-08-18), found by the coordinator).
- Evinced is described as "building actor agents that traverse websites and act exactly like a screen reader user would, called a 'screen reader agent'" ([aiagentstore, 2026-07-07](https://aiagentstore.ai/ai-agent-news/topic/accessibility-inclusion/2026-07-07/detailed); search excerpt, unverified).
- Agent skills for screen reader testing already exist ([vibeindex](https://www.vibeindex.ai/skills/wshobson/agents/screen-reader-testing)).
- Research: Apple's AXNav replays manual accessibility tests on iOS with an LLM and VoiceOver ([arXiv 2310.02424](https://arxiv.org/abs/2310.02424); cited from memory, not opened here). 2026 papers cover screen reader agents over the accessibility tree ([arXiv 2608.24898](https://arxiv.org/pdf/2608.24898)) and computer-use agents for blind users ([arXiv 2609.00524](https://arxiv.org/pdf/2609.00524)), and there is a review of LLMs for web accessibility ([arXiv 2605.13873](https://arxiv.org/pdf/2605.13873)). These titles come from search results; arxiv.org is blocked here.
- Tools: Guidepup drives real VoiceOver and NVDA ([GitHub](https://github.com/guidepup/guidepup), MIT) and ships a "screen reader simulator for testing" ([virtual-screen-reader](https://github.com/guidepup/virtual-screen-reader), MIT, 0.33.0 on npm today). GitLab itself ships Pa11y accessibility testing with an MR widget ([doc source](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/ci/testing/accessibility_testing.md)).
- In this contest's field it is rare. Accessibility after deploy appeared in 5 of 506 February catalog projects, 1 June catalog project, and none of the October ideas ([FIELD.md](../../FIELD.md)).

So never say "first". The new part is the place and the loop: a GitLab release that cannot reach production until an agent has bought something by ear, with spoken evidence, the MR that caused the barrier, and a fix MR, all built on Duo flows.

**Collisions:**

- **Release gatekeepers.** On a pipeline graph, No Mouse is "staging, a check, a manual production job". That is the shape of 4 of the 7 known October ideas, and of the judges' [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase), whose `validate-staging` job curls `/health`, creates a task, and then promotes (guide). Keep the graph on screen for three seconds, lead with the ear, never auto-rollback, and never score risk.
- **Smoke tests.** The replay is a synthetic journey test, and February had 5 smoke-test projects. The difference is the input (only what a screen reader would announce) and the question (can a person who cannot see the screen pay?).
- **Proof of Fix (excluded).** The production walk is close to "a synthetic user check" after a merge, which [FIELD.md](../../FIELD.md) section 3 puts in the same family. Keep it a release check that writes to the Release, and never close, reopen or comment on issues because of production results.

**What a skeptical judge would say, and the answer:**

| Objection | Answer |
|---|---|
| "GitLab already has accessibility testing. This is axe with an LLM on top." | Rule checkers (Pa11y in GitLab's template, axe) judge pages against rules. They cannot say whether a person can finish buying, and they weigh a missing name in the footer the same as a missing name on Pay. No Mouse runs GitLab's Pa11y job too, but it holds a release only when a journey fails. |
| "A model is not a blind person." | Agreed, and the README and video say so. The walk is a floor, not a certificate: if an agent with the same information cannot pay, a person very likely cannot either; passing proves little. Maria is a labelled persona. |
| "Why a model? A scripted keyboard test catches a missing label." | The script runs first, on every deploy, for free. The model runs only when the script breaks. It tells "the page changed but Maria can still pay" (update the path and ship) from "Maria cannot pay" (hold and fix), and it then finds and fixes the cause. Without it, every redesign is a red pipeline someone triages by hand. |
| "This is the reference project with one more job." | The two loops end in the same place, but the reference checks that a server answers. No Mouse checks that a person who cannot see the screen can pay, and it hands back a recording and a fix. The video shows the walk for about 35 seconds and the pipeline for 3. |
| "Model runs are flaky, so holds will be random." | Holds come from code: no order, a focus trap, or an unnamed control pressed on the way. A lucky path that needed guesses is still a hold, which is the point. Any path the model finds is replayed by code before it counts. |
| "The demo is planted." | Yes, and labelled, just as the reference project planted its injection bug in MR !1. The 12-page eval set and its published results show how it does on barriers not staged for the video. |
| "Is this a real problem for a real audience?" | Shops selling in the EU have had to meet the European Accessibility Act since 28 June 2025 ([Directive (EU) 2019/882](https://eur-lex.europa.eu/eli/dir/2019/882/oj); not opened here). A Pay button with no name stops a sale. |
| "It burns model calls on every deploy." | A clear replay makes zero model calls. When the replay fails, a walk costs about 30 GitLab Credits in Duo, or about $0.70 through the Google Cloud fallback. |

**Is "screen reader view" honest? Only if we say exactly what it is.**

- **What it is.** The listener does not run NVDA, JAWS or VoiceOver. It receives text that our code renders from Chromium's accessibility tree, which is the information browsers hand to screen readers through the platform accessibility APIs. Each element appears with its role, accessible name, states and position, in the order keyboard focus or a reading cursor reaches it. Playwright's own docs say "aria snapshots provide a YAML representation of the accessibility tree of a page" ([aria-snapshots.md](https://github.com/microsoft/playwright/blob/main/docs/src/aria-snapshots.md)).
- **What it misses.** Real screen readers add their own phrasing, verbosity settings, browse modes and bugs. Some barriers appear only with a real screen reader: the timing of live regions, focus jumps after dialogs, and problems specific to one browser and screen reader pair.
- **How to describe it truthfully:** "what a screen reader would announce, simulated from the browser's accessibility tree". The audio is "read aloud by Google Cloud Text-to-Speech", not a screen reader's voice.
- **What passing means:** a floor, not a certificate. Borrow Guidepup's own line: "there is no substitute for testing with real screen readers and with real users" ([virtual-screen-reader](https://github.com/guidepup/virtual-screen-reader)).
- **Words to avoid:** "WCAG compliant", "certified", "tested with a screen reader".
- **One calibration:** show a real screen reader saying "button" on the same broken page (VoiceOver on Alex's phone, or Guidepup driving VoiceOver or NVDA).

## 12. First build step and build size

**Today, in this repo, with no GitLab or Google account.** Claude Code owns the app and agent code under [AGENTS.md](../../../AGENTS.md).

1. **`shop/`:** a FastAPI app with server-rendered pages (home, product, cart, checkout, confirmation) and in-memory orders, running one worker. It has `/healthz` returning `CI_COMMIT_SHORT_SHA`, as the deploy contract requires, and a test endpoint that reports the orders for one walker session. A `PLANT=icon_buttons` switch renders the redesign with three unnamed icon buttons. Every page carries a "Demo shop" banner.
2. **`nomouse/`:** a Playwright session with the action menu from section 6, an announcement renderer that reads the accessibility tree, a JSONL log, and the commands `probe`, `walk --interactive`, `replay` and `verdict`.
3. **Run it here.** Playwright's browser download host is blocked in this session (cdn.playwright.dev answers 403). A Chrome for Testing zip from storage.googleapis.com downloaded with HTTP 200 today, so launch Chromium with `executable_path`.
4. **Produce the first results:** two transcripts (clean and planted) and a by-hand run of Test B.
5. **Write the test data:** `journeys/maria-monthly-beans.yml` and the first 6 eval fixture pages.

Report in the AGENTS.md format. Ask Codex, who owns `deploy/`, for the second Cloud Run service and the Text-to-Speech permission.

| Component | Rough lines | Builder days |
|---|---|---|
| Demo shop (5 pages, orders, test endpoint, plant switch) | 500 | 1 |
| Walker (actions, accessibility tree reader, renderer, log, CLI) | 700 | 1.5 |
| Verdict, replay, spoken diff, WCAG map, reports | 400 | 1 |
| Listener loop for the CI fallback (Anthropic SDK on Agent Platform) | 250 | 0.5 |
| Speech (Cloud Text-to-Speech, espeak-ng as offline fallback) | 100 | 0.25 |
| Duo flow YAML (3 agents, 1 human input, routers), prompts, `agent-config.yml`, 2 skills, AGENTS.md section | 450 | 1, plus the probe |
| `.gitlab-ci.yml` (build, scans, staging, replay, speak, fix revision, manual production, production replay, release, schedule) and the walker image | 350 | 1 |
| Google Cloud changes in `deploy/` (second service, TTS, revision tags; Codex) | 150 | 0.5 |
| Eval fixtures (13 pages) and unit tests | 450 | 1 |
| README, diagram, video script | | 1 |
| **Total** | **about 3,350** | **about 9 builder days** |

It fits the window if Alex spends about an hour before Oct 13 on the shared account steps: Devpost and the GitLab workspace, merge rights on `main`, and the Google project from [deploy/README.md](../../../deploy/README.md). The video and submission then take Oct 24 to 26.

## 13. Verdict

**Yes, keep it in the top three.** It has:

- the strongest first 30 seconds in the pool (wow 10 from all three judges);
- the highest innovation score;
- a clear human at the center;
- after this brief, a full loop with a code-first gate that keeps model cost low, and a fallback in which Claude still chooses every key.

**Suggested adjustment: 85.6 to 84.8.**

| Dimension | Was | Now | Why |
|---|---|---|---|
| Innovation | 9.0 | 8.3 | Prior art in industry and research (patent application, Perforce, Evinced, AXNav), plus GitLab's own Pa11y template. Still the most original in our pool |
| Design | 7.7 | 8.0 | Replay first, model on failure, a re-walk of the fix and a production walk make one coherent loop |
| Stages | 4.7 | 6.0 | All nine touched honestly, five specific to the idea (the write-up listed three) |
| Autonomy | 7.0 | 6.5 | The honest level is Supervised, not the Hands-off two judges assumed, and release gatekeepers will crowd that prize |
| Novelty | 7.0 | 6.5 | The pipeline shape sits near the gatekeepers and the reference project, and Proof of Fix sits next to the production walk |
| Feasibility | 7.0 | 6.5 | More moving parts (two Cloud Run services, speech, a walker image, a flow, evals); Claude on Agent Platform under the Free Trial is unverified; Alex's account steps |

Tech, impact, presentation, human, sponsors and wow stay the same. The new criteria mean is 8.48, so the total is 3 x 8.48 + 6.0 + 6.5 + 9.7 + 6.5 + 7.7 + 10 + 2 x 6.5 = 84.8. That keeps it second, about 4.8 above Forget Me (80.0).

**Conditions.**

- If the day-one tests leave only the scripted form (fallback 3), score it at about 79 and weigh it again against Forget Me.
- The order against Night Orders (88.6) should be settled by the two day-one tests (this browser probe, and Night Orders' non-human start), not by more scoring.
