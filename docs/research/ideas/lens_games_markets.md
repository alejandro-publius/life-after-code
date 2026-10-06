# Concepts from two lenses: game design and markets

Generated on 2026-10-06 as input for Part 5 (docs/IDEAS.md, not written yet). This is generation only: nothing here is scored, ranked or recommended.

Inputs: [IDEATION_BRIEF.md](../IDEATION_BRIEF.md), [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md), [field/code_hosts.md](../field/code_hosts.md), [field/social.md](../field/social.md). No web search was used. People, companies and numbers in the scenes are invented for illustration and would be labelled as demo data.

What is here: the banned obvious answers and 8 concepts for each lens (G1 to G8, M1 to M8), then six concepts these lenses also produced that the parallel file [lens_oncall_inversion.md](lens_oncall_inversion.md) already holds (kept short, with only what these lenses add), then notes for the scoring step.

## Rules every concept follows

- **The model chooses where to look and what to try. Code decides what is true** (numbers, dates, thresholds, what is allowed). **A person decides when the agent acts on anything that matters.**
- **Human gates are ordinary GitLab actions:** merging an MR, approving a deployment to a protected environment, assigning or mentioning the flow. This avoids `HumanInputComponent`, whose behavior in a triggered ambient flow is unverified ([guide](../gitlab_guide_and_reference.md#flow-components-and-syntax-from-the-v1-spec)). It also fits the rule that only a human action can start a flow and a flow cannot start another flow ([guide](../gitlab_guide_and_reference.md#triggers)): each human step starts the next flow run.
- **Actions a flow cannot take with its own tools** (flip a feature flag, run a deploy, rotate a key, run a load test) are done by CI jobs whose rules are code. Flows cannot read CI/CD variables ([guide](../gitlab_guide_and_reference.md#where-flows-run-execution-environment)).
- **Timed and night-time starts:** a pipeline started by a pipeline schedule or a trigger token runs as the person who owns the schedule or token (GitLab behavior as I understand it, not re-checked in this session), so a job in it acts on that person's earlier approval. Whether such a pipeline counts as a human action for a flow's Pipeline events trigger is unverified. Every concept that runs on a timer or at night depends on it.
- **Pipeline events fire for every pipeline** in the project, so each flow that uses them must stop at once when the pipeline is not its kind (each start still costs a CI job and credits).
- **Tier and role unknowns:** protected environments with deployment approvals, Code Owner approval, and on-call schedules with escalation policies need Premium or Ultimate; the workspace tier is unverified. Enabling Service Desk, deploy freezes, CI/CD variables and merging to `main` may need Maintainer ([guide](../gitlab_guide_and_reference.md#branch-protection-the-biggest-setup-risk)).
- **Names** were checked against the known October entries, the June and February projects in the field files, the past winners in the brief, and the parallel lens file.

## At a glance

| ID | Name | Borrowed from | Who feels it | Fits best |
|---|---|---|---|---|
| G1 | Shield Wall | the raid tank who holds aggro | the engineer fixing an incident; users who wrote in | Supervised |
| G2 | Respawn | save points and the corpse run | a developer whose good change was rolled back | Supervised (Hands-off possible) |
| G3 | Telegraph | enemy intents in Into the Breach | the weekend on-call engineer | Supervised |
| G4 | Next Wave | tower defense | a marketer about to send a big campaign | Supervised |
| G5 | Speedrun | speedrun routes with rules | the engineer shipping a fix at 2am | Assisted |
| G6 | Tactical Pause | real-time with pause | the incident commander | Assisted |
| G7 | No Reloads | save scumming and ironman mode | a developer retrying a "flaky" test | Supervised |
| G8 | Alarm Level | stealth game alert phases | a new developer who leaked a key | Supervised |
| M1 | Reserve Price | an auction's reserve price | the on-call engineer, asleep | Hands-off (wake or wait only) |
| M2 | Limit Order | a limit order with expiry | a developer who wants to go home | Hands-off |
| M3 | Credit Line | a line of credit | a team lead deciding agent autonomy | Assisted, earns Hands-off |
| M4 | Triple A | credit ratings | a developer facing 30 update MRs | Hands-off for top-rated |
| M5 | Make Whole | service credits and recalls | customer success, and the customers | Supervised |
| M6 | First Dibs | a matching market (waitlist) | a user who asked for a feature | Supervised |
| M7 | Clearing House | end-of-day settlement | the outgoing and incoming on-call engineers | Assisted |
| M8 | Last Caller | escrow | an API owner stuck with an old endpoint | Supervised |

## Lens 1: Game design

### Banned: the three most obvious answers

1. **BANNED:** Leaderboards that rank developers by merges, fixes, deploys or incidents closed.
2. **BANNED:** Achievement badges, XP and streaks for merges, green pipelines or reviews.
3. **BANNED:** A gamified dashboard: health bars for services, team levels, "boss HP" for an incident.

Close variants are out too: points races between teams, avatars, loot for fixing bugs, "quests" that are a checklist with points. The concepts below borrow how games structure decisions, risk, pacing and cooperation, not how they hand out rewards.

### G1. Shield Wall

- **Mechanic:** the tank in a raid holds the boss's attention (aggro) so everyone else can work.
- **Pitch:** During an incident the agent fields every question from users, support and managers with facts and approved wording, so the people fixing it are left alone, then replies personally to everyone who wrote in.
- **Person and moment:** Diego is fixing a broken login at 2am while support tickets pile up and his manager wants an ETA every ten minutes. Nobody interrupts him for 40 minutes, and the next morning he sees that each of the 31 users who wrote in got a reply naming when they reported it and when it was fixed.
- **Flow:**
  1. An incident is open, from an alert or declared by a person. The incident commander assigns the flow to it. *(alerts and incidents, Duo flow with Assign trigger)*
  2. The agent searches Service Desk issues opened since the incident began, decides by meaning which ones describe this problem ("can't log in", "2FA code never arrives"), links them to the incident and posts a count. It does not reply yet. *(Service Desk, issues, linked items)*
  3. Stakeholders ask on the incident by mentioning the flow ("@shield ETA?"). Each mention is a human action that starts a run; the agent answers only from the incident timeline, the latest deployment and the pipeline status, never by asking the responders. *(incidents, environments and deployments, CI/CD, Mention trigger)*
  4. The agent drafts a status update and a reply template. The commander approves with a mention, and code checks that the approver is the commander; only then does the agent post on the linked Service Desk issues, which emails the users. *(Service Desk, Mention trigger)*
  5. When the fix is deployed and the incident is closed, the commander assigns the flow again. It drafts closing replies per user with their report time and the fix time, a person approves the batch, and the agent sends them and closes the linked tickets. *(environments and deployments, incidents, Service Desk)*
- **Stages:** plan, release, monitor.
- **Autonomy:** Supervised: the commander approves the wording of each update once, and the agent handles the 31 individual replies.
- **Model, code, person:** The model may decide which tickets belong to the incident, answer factual questions from GitLab data, and draft wording. It may not send anything to users without approved wording, promise a time, diagnose, touch production, or post in the responders' thread. Code decides incident start and end times, deployment status, who has been answered, that the approver is the commander, and a rate limit on outgoing replies.
- **Demo moment (30 seconds):** Left, the incident page stays quiet. Right, Service Desk tickets ("can't log in", "login broken???", "2FA not working") snap into the incident as linked items, and a manager's "@shield ETA?" gets "The fix passed staging at 02:44 and is waiting for the production deploy." The fix deploys, and an email arrives: "You told us about this at 02:14. It was fixed at 02:51. Thank you for writing."
- **Nearest crowded space:** generic incident chatbots (excluded) and incident root cause from deploy to MR. **Difference:** it never diagnoses or talks to the responders. It faces outward to users, support and stakeholders, keeps interruptions away from the people fixing the problem, and closes the loop with each person who wrote in.
- **Biggest feasibility risk:** Service Desk in the workspace (enabling it may need Maintainer) and a believable, labelled set of demo user emails; matching tickets to the incident reliably with few examples.

### G2. Respawn

- **Mechanic:** the save point and the corpse run (Dark Souls): when you die you go back to the last bonfire, then run back to pick up what you dropped.
- **Pitch:** After a bad release is rolled back, the agent re-lands the innocent changes one at a time, each tested and deployed on its own, so good work comes back and the bad change is found by elimination.
- **Person and moment:** Mira's small accessibility fix shipped in the same release as someone else's broken cache change, and the whole release was rolled back at 11am. By 3pm her fix is back in production on its own, and she never had to ask, rebase or chase anyone.
- **Flow:**
  1. A person rolls production back by re-deploying the previous deployment or merging a revert. The incident commander assigns the flow to the incident. *(environments and deployments, incidents, Duo flow with Assign trigger)*
  2. The agent reads which MRs were in the rolled-back range, the incident, and error tracking around the bad deploy, and decides an order: clearly unrelated changes first, suspects last. *(deployments, merge requests, error tracking)*
  3. For each change in order, it opens an MR that re-lands only that change, with a note on why it is believed innocent. *(merge requests)*
  4. Each MR runs the normal pipeline and reaches staging, then production (with a person's approval in Supervised mode). After each deploy, a CI job watches the same error signals for a fixed window. *(CI/CD, protected environments, deployment approvals, error tracking)*
  5. If a re-landed change brings the errors back, the agent stops, marks it as the suspect on the incident, leaves it out and continues with the rest. It ends with "4 of 5 changes are back; !52 is held, with evidence" and tells each author. *(incidents, merge requests)*
- **Stages:** plan, create, verify, release, monitor.
- **Autonomy:** Supervised by default: the agent prepares every re-landing, and a person approves each production deployment or the batch. Hands-off is a credible setting, because the agent only re-lands code that people already reviewed and merged once, one change at a time, and code stops it at the first sign of the errors returning; the suspect never goes back without a person.
- **Model, code, person:** The model may order the changes, write the re-land MRs, and read errors to decide what is suspect. It may not re-land the suspect, change code beyond the original diff, or skip the watch window. Code decides what was in each deployment, the watch window, and the error threshold that marks a re-land as bad.
- **Demo moment (30 seconds):** Five MRs in a row, all grey after the rollback. One by one they turn green as they are re-landed. The fourth brings the error spike back; the agent pulls it and labels it "suspect". The fifth goes back cleanly, and Mira gets: "Your change !49 is back in production."
- **Nearest crowded space:** rollback inside post-merge release gatekeepers, and incident root cause from deploy to MR. **Difference:** it starts after a person has already rolled back. Its goal is getting innocent work back safely; finding the bad change is a by-product of re-landing, not a guess from logs.
- **Biggest feasibility risk:** staging a believable multi-MR release with one truly bad change, and fitting several deploy cycles into a short demo (each pipeline must take about 2 to 3 minutes).

### G3. Telegraph

- **Mechanic:** in Into the Breach every enemy shows exactly what it will do next turn, so play is about answering threats before they land.
- **Pitch:** After a merge, the agent finds the first future moment the new code will meet something scheduled or date-driven, and offers a dry run of that moment now, before it happens in production.
- **Person and moment:** Ines is on call this weekend, and the monthly invoice job runs Sunday at 00:00 for the first time since Tuesday's tax change. On Friday at 2pm she approves the dry run the agent proposed, it fails on a rounding error, and the fix ships before the weekend instead of during it.
- **Flow:**
  1. When an MR is merged, the merge pipeline's event starts the flow. The agent reads the diff and decides where scheduled or date-driven behavior could meet it: pipeline schedules, cron entries in code and Cloud Scheduler config, date logic (month end, time zones, daylight saving), certificate and token expiry dates, flags with scheduled changes. *(merge requests, pipeline schedules, feature flags, Duo flow with Pipeline events trigger)*
  2. It lists the "intents" for the next 7 days: what will run, when, and whether it runs the changed code for the first time. Code checks what it can: schedule times from the API, and whether the job's files changed since its last successful run. *(CI/CD, repository)*
  3. It posts each intent on a "next turn" issue with a proposed answer: dry run now on staging, add a guard, or move the schedule. *(issues)*
  4. A person picks answers with a mention. A dry run is a manual CI job against staging, and its result goes back on the item. *(Mention trigger, manual CI/CD jobs, environments)*
  5. Before each intent's time, the agent reminds the on-call engineer, with the dry-run result attached. *(issues, mentions, pipeline schedules)*
- **Stages:** plan, verify, release, configure, monitor.
- **Autonomy:** Supervised: the agent finds and prepares, and a person chooses which answers to run.
- **Model, code, person:** The model may decide where to look for scheduled and date-driven behavior, connect it to the change, and propose answers. It may not change schedules or code without an MR a person merges, or run anything outside staging. Code decides schedule times, the "first run since the change" fact, and the dry run's pass or fail.
- **Demo moment (30 seconds):** A merged MR, "change tax rounding". The agent posts "Next turn: Sunday 00:00, monthly invoices will run the new rounding code for the first time." One mention runs the dry run on staging; 3 invoices fail; the fix MR merges on Friday afternoon.
- **Nearest crowded space:** pre-merge blast radius ("what could this break", 69 teams in June). **Difference:** it works after merge and along time instead of code structure: the question is "when will production first run this, and can we try that moment now?"
- **Biggest feasibility risk:** making the discovery of scheduled and date-driven code general enough to convince; the demo app needs real scheduled jobs and date logic.

### G4. Next Wave

- **Mechanic:** tower defense: you know the next wave is coming and the path it will take, so you place defenses before it arrives.
- **Pitch:** When someone plans a traffic wave (a campaign email, a launch, a sale), the agent works out which paths it will hit, load-tests them on staging, and proposes defenses for a person to approve before the wave arrives.
- **Person and moment:** Lucia in marketing is about to email 200,000 customers on Tuesday at 10:00, and the last time she did that the site fell over and she felt it was her fault. This time the weak promo page is found and fixed on Monday, and on Tuesday she watches the traffic climb and the site stay up.
- **Flow:**
  1. The campaign owner opens a "wave" issue from a template (what, when, how many people, the links in the email) and assigns the flow. *(issues, issue templates, Duo flow with Assign trigger)*
  2. The agent follows the links to routes and code, decides which paths the wave will hit (the promo page, the product API, checkout, the image service), and estimates the peak from the audience size and past campaigns, with its assumptions written down. *(repository, issues, deployments and error tracking from past waves)*
  3. A CI job load-tests those paths on staging at the estimated peak; code sets the numbers and decides pass or fail. The agent reads the results and finds where it breaks and why. *(CI/CD, environments)*
  4. It proposes defenses as MRs: a cache on the slow query, minimum instances raised for Tuesday 09:30 to 12:00 only, a rate limit on the costly endpoint. A person merges each one, and the load test runs again to prove it. *(merge requests, CI/CD, environments)*
  5. On the day, a schedule applies the temporary capacity and removes it afterwards, and the agent writes how the wave went on the issue for the next campaign. *(pipeline schedules, deployments, monitoring)*
- **Stages:** plan, create, verify, configure, release, monitor.
- **Autonomy:** Supervised: the agent finds the weak points and prepares the defenses; a person approves each defense, and the temporary capacity runs on a schedule that was approved with it.
- **Model, code, person:** The model may map the campaign to paths, estimate the load with stated assumptions, choose what to test, and propose defenses. It may not change production capacity or code without an approved MR, or load-test anything but staging. Code decides the load numbers, pass or fail, and the time window for temporary capacity.
- **Demo moment (30 seconds):** The wave issue: "200,000 emails, Tuesday 10:00, 3 links". The agent maps the links, the staging load test shows the promo page failing at 120 requests per second against a peak estimate of 350, the cache MR is merged, the rerun passes at 400, and on "Tuesday" (a labelled, scaled-down simulation) the traffic graph climbs and stays green.
- **Nearest crowded space:** none in the field; nearest are pre-merge "what could this break" tools and post-deploy smoke tests. **Difference:** it starts from a business event, not a code change, and its job is to defend known paths before a known wave, with load tests as the ground truth.
- **Biggest feasibility risk:** load-testing Cloud Run staging honestly (cost, quotas, cold starts), and making the demo wave real but small and clearly labelled as a simulation.

### G5. Speedrun

- **Mechanic:** speedrun routing: runners plan the fastest route through a game, but a category such as "glitchless" still forbids breaking the rules. Fast, and by the rules.
- **Pitch:** When production is broken and a small fix is ready, the agent plans the fastest safe route through the pipeline for that exact change, a person approves it, and the full pipeline runs right after the fix is live.
- **Person and moment:** Kenji has a one-line fix for a checkout outage at 2am, and the full pipeline takes 48 minutes while customers cannot pay. The agent proposes an 11-minute route that keeps the checks that matter for this change, he approves it, checkout is back at 02:19, and the full run that follows is green by 03:05.
- **Flow:**
  1. During an open incident, the engineer opens the fix MR and mentions the flow ("@speedrun route this"). *(incidents, merge requests, Duo flow with Mention trigger)*
  2. The agent reads the diff, the pipeline definition, which tests cover the touched code, and past job durations, and decides which jobs matter for this change. It writes a route: jobs to run now, jobs deferred until after the fix, the time saved, and a reason for each deferral. *(CI/CD, repository, security scans)*
  3. Code checks the route against `never-skip.yml` (for example secret detection, the touched module's unit tests, the staging smoke test, the production approval). A route that drops any of these is rejected before a person sees it. *(CI/CD rules)*
  4. The engineer approves the route with a mention, and code confirms an incident is open. The pipeline runs with the route as variables that skip the deferred jobs, then deploys to production through the usual approval. *(CI/CD, environments, deployment approvals)*
  5. As soon as the fix is live, the full pipeline runs on the same commit. If anything deferred fails, the agent reopens the incident and pages the engineer with the failure. *(CI/CD, incidents)*
- **Stages:** verify, secure, release, govern.
- **Autonomy:** Assisted: the engineer approves the route and the production deploy; the agent plans the route and runs the follow-up.
- **Model, code, person:** The model may decide which jobs are relevant to this change and explain each deferral. It may not drop a never-skip job, offer a route outside an open incident, or skip the full run afterwards. Code decides the never-skip list, the incident check, the job rules and the follow-up run.
- **Demo moment (30 seconds):** A pipeline graph with 14 jobs and "48 min". The agent's route lights up 5 of them: "11 min. Deferred: end-to-end suite (does not reach the checkout code changed here), container scan (image base unchanged)." The engineer approves, the route runs, checkout recovers, and the deferred jobs then run and turn green.
- **Nearest crowded space:** CI test selection (CrossCut, a June winner) and post-merge release gatekeepers. **Difference:** it exists only for an open incident, the route is checked by code against a never-skip list and approved by a person, and everything skipped runs right after; it is an emergency lane, not everyday test selection.
- **Biggest feasibility risk:** a demo pipeline slow enough for the route to matter (a real slow stage, or a labelled stand-in), and expressing routes as job rules (`rules:` with variables) without breaking the normal pipeline.

### G6. Tactical Pause

- **Mechanic:** real-time with pause (Baldur's Gate, FTL): when the fight gets chaotic you freeze time, look at everything, give orders, then unpause.
- **Pitch:** During an incident one command freezes every change in motion (deploys, armed auto-merges, scheduled jobs, flag rollouts) so the team can think, and on resume the agent proposes what to let back first.
- **Person and moment:** Grace is running an incident when another team's deploy lands in the middle of it and doubles the error rate. Next time she types "@pause", sees the seven changes due in the next hour frozen, and lets them back one at a time after the fix, in the order the agent proposed.
- **Flow:**
  1. The incident commander mentions the flow in the incident ("@pause"). *(incidents, Duo flow with Mention trigger)*
  2. The agent decides where to look for change in motion: running and pending pipelines with deploy jobs, MRs with auto-merge set, pipeline schedules due in the next hours, flags with gradual rollouts in progress, running agent sessions. It lists them on the incident. *(CI/CD, merge requests, pipeline schedules, feature flags, Duo sessions)*
  3. Code applies the freeze: a deploy freeze for the project, so deploy jobs stop on `CI_DEPLOY_FREEZE`, plus a pause marker that rollout and scheduled jobs check before they act. The agent posts a short note on each frozen MR telling its author why. *(deploy freezes, CI/CD rules, merge requests)*
  4. When the commander says "@pause resume", the agent proposes an order to let changes back (smallest and least related first, anything touching the incident's area last). The commander approves it, and code lifts the freeze for one item at a time. *(Mention trigger, deploy freezes, environments and deployments)*
- **Stages:** release, configure, monitor, govern.
- **Autonomy:** Assisted: a person pauses, resumes and approves the order; the agent does the inventory, the notes to authors and the sequencing.
- **Model, code, person:** The model may decide where to look for change in motion, explain each item, and propose the resume order. It may not pause or resume on its own, cancel anyone's work, or change the freeze rules. Code decides the freeze window, which jobs honor it, and the one-at-a-time release.
- **Demo moment (30 seconds):** The incident page. "@pause". Seven items appear (two pipelines about to deploy, an auto-merge, a 30% flag step, a nightly data job, two agent sessions) and each turns grey: frozen. After the fix, "@pause resume" brings them back one by one in the proposed order.
- **Nearest crowded space:** post-merge release gatekeepers, which hold single changes. **Difference:** it holds all change at once on a person's command during an incident, including other teams' and other agents' changes, and the agent's work is the inventory and the resume order, not a ship-or-hold judgment.
- **Biggest feasibility risk:** deploy freezes and pausing schedules through the API likely need Maintainer and may be outside the flow token's scope (unverified); the freeze may have to be a file in the repo that pipelines read.

### G7. No Reloads

- **Mechanic:** save scumming: reloading a save until the dice roll your way. Ironman mode forbids it, because a reload hides what really happened.
- **Pitch:** A pipeline that only went green after a retry is a reload; the agent tries to make the failure happen again on purpose, and when it is a real intermittent bug rather than a flaky runner, it opens an issue with a reproduction for a person to act on.
- **Person and moment:** Bea has retried the same "flaky" checkout test for weeks because it fails about one run in twenty. The agent reproduces it under parallel load and shows a real race that would charge about 1 in 500 customers twice, and Bea fixes it instead of retrying it away.
- **Flow:**
  1. When a pipeline passes after one or more retried jobs, its event starts the flow (the flow stops at once for pipelines with no retries). *(CI/CD, Duo flow with Pipeline events trigger)*
  2. The agent reads the failed attempt's log next to the passed attempt's log, and decides what kind of failure it was (runner or network trouble, test order, timing, shared state) and what to try. *(CI/CD job logs)*
  3. It sets up experiments as a CI job a person starts (run the test alone 200 times, with a fixed seed, in random order, under parallel load), and code counts the outcomes. *(manual CI/CD jobs)*
  4. If code finds the failure reproducible (for example at least 3 failures in 200 runs), the agent opens an issue with the reproduction command, the rate and its reading of the cause, and assigns the test's code owner. If not, it records the environment cause and proposes an infrastructure fix or a quarantine as an MR. *(issues, CODEOWNERS, merge requests)*
  5. The test owner decides: fix, quarantine, or close. A quarantined test gets a due date and a weekly re-run. *(merge requests, issues with due dates, pipeline schedules)*
- **Stages:** plan, create, verify.
- **Autonomy:** Supervised: the agent investigates and proves; the test's owner decides what happens to the test.
- **Model, code, person:** The model may classify the failure, choose experiments, and write the reproduction and its reading of the cause. It may not quarantine, skip or change tests, or change the pipeline, without a person's merge. Code decides the counts, whether the failure counts as reproducible, and the weekly re-check.
- **Demo moment (30 seconds):** A green pipeline with a small retry icon. The experiments run: 200 isolated runs pass, 200 parallel runs fail 7 times. The issue reads: "Not flaky: a race in `reserve_stock`, reproducible under parallel load; about 1 in 500 orders would be charged twice." The owner merges the fix.
- **Nearest crowded space:** CI failure fixers (excluded). **Difference:** it never touches a red pipeline; it questions green pipelines that needed a retry, and its output is evidence (a reproduction and a rate), not a fix. It sits in the open flaky-test space.
- **Biggest feasibility risk:** a demo app with an honest intermittent bug that reproduces reliably under load in CI, and enough CI minutes for hundreds of repetitions.

### G8. Alarm Level

- **Mechanic:** alert phases in stealth games (Metal Gear Solid): Alert, then Evasion, then Caution, then back to normal; the world stays watchful for a while after you are spotted.
- **Pitch:** When a secret leaks, the agent runs the response in phases (contain with a person's go, check for misuse, stay watchful, stand down) and guides the person who leaked it without blame.
- **Person and moment:** Felix, two weeks into the job, pushes a live API key at 6pm and his stomach drops when the secret detection finding appears. By 8pm the key is replaced, the logs show it was never used, and the agent's last note to him is about what to change, not whose fault it was.
- **Flow:**
  1. Secret detection in the pipeline finds a secret. The pipeline's event (a person pushed) starts the flow, and it opens an incident. *(security scans: secret detection, CI/CD, incidents, Duo flow with Pipeline events trigger)*
  2. Alert: the agent works out the key's type and where it is used (code, CI config, environments, the cloud project) and proposes containment. The lead approves with a mention; a CI job rotates the key for a supported provider, and the agent opens an MR updating references. *(Mention trigger, CI/CD, merge requests)*
  3. Evasion: the agent decides where to look for misuse (the provider's access log if that host is on the allowlist, the app's logs, unusual deploys or pipeline runs since the leak) and reports with links. *(deployments, CI/CD, allowlisted network access)*
  4. Caution: for a set time, for example 48 hours, code turns on extra checks, such as secret detection on every branch and an approval on production deploys. *(security scans, protected environments)*
  5. Stand down: the agent closes the incident with a plain summary, a no-blame note to the person, and one prevention proposed as an MR. *(incidents, merge requests)*
- **Stages:** create, secure, release, configure, monitor, govern.
- **Autonomy:** Supervised: a person approves containment, and the rest is prepared and reported.
- **Model, code, person:** The model may work out the key's scope, decide where to look for misuse, and write the guidance and the summary. It may not rotate without approval, rewrite git history, or name or blame anyone in notes. Code decides the phase timers, the rotation call and the caution-phase checks.
- **Demo moment (30 seconds):** A red secret detection finding. The incident shows "ALERT" and one approval request to the lead; approved; the key is rotated (a demo key for a demo service, labelled). "EVASION: 3 log sources checked, no use." "CAUTION until Thursday 18:00." Then the agent's note to Felix.
- **Nearest crowded space:** security review and auto-fix on MRs, which includes secret detection (48 projects in February). **Difference:** detection is left to GitLab. The concept is the response over the next hours (contain, check for misuse, watch, stand down) and the person who made the mistake.
- **Biggest feasibility risk:** rotating a real key needs provider credentials a flow cannot read from CI/CD variables; the demo needs a small demo service whose keys we control.

## Lens 2: Markets

### Banned: the three most obvious answers

1. **BANNED:** A prediction market where developers bet on whether a deploy will break, or a deploy risk score shown as odds.
2. **BANNED:** Bug bounties or an internal token economy that pays developers for fixes, reviews or closed incidents.
3. **BANNED:** Price tags on pipelines and merge requests: CI or cloud cost per change, chargeback to teams.

Close variants are out too: auctions for runner time or CI queue priority, carbon credits for pipelines, a "stock price" for services or teams. The concepts below borrow how markets allocate scarce things, price risk and settle promises. No money changes hands, except in M5, where customers may receive credits they are owed.

### M1. Reserve Price

- **Mechanism:** the reserve price in an auction: nothing sells unless a bid clears it. What is for sale here is a person's sleep.
- **Pitch:** At night an alert has to clear a price to wake a person: the agent gathers the evidence, code prices it, and alerts below the reserve wait for morning with the evidence ready.
- **Person and moment:** Theo's phone used to ring for every disk warning and crawler spike. At 03:40 a crawler burst prices at 12 against a night reserve of 60 and Theo sleeps, and at 05:10 real checkout errors price at 88 and his page opens with the evidence already gathered.
- **Flow:**
  1. The team sets reserves in `reserve.yml` (for example day 20, night 60, weekend 50) and a list of alerts that always page, through an MR a person merges. *(merge requests)*
  2. An alert arrives: the monitoring webhook records a GitLab alert and starts a pipeline through a trigger token the on-call engineer owns, and the pipeline's event starts the flow. *(alerts with the HTTP endpoint integration, webhooks, CI/CD, Duo flow with Pipeline events trigger)*
  3. The agent decides where to look: error tracking (users affected, new or known error), recent deployments and flag changes, Service Desk tickets in the last hour, and the alert's own history (how often it fired, how often a person acted on it). It fills a fixed evidence form with links. *(error tracking, environments and deployments, feature flags, Service Desk)*
  4. Code computes the price from the form and compares it with the reserve. Above it: open an incident and page the on-call engineer with the evidence on top. Below it: note it on the alert and add it to the morning queue. Open alerts are priced again every 15 minutes, so a growing problem crosses the reserve on its own. *(incidents, on-call paging or a mention, pipeline schedules)*
  5. In the morning the agent posts the queue of alerts that waited, each with its price and evidence. The on-call engineer can mark any price as wrong; code records it next to the form's inputs so the team can tune the formula by MR. *(issues, merge requests)*
- **Stages:** configure, monitor, govern.
- **Autonomy:** Hands-off for one decision only, letting someone sleep, inside rules the team wrote; it never acts on production. Changes to the formula or the reserves are Assisted (a person's MR).
- **Model, code, person:** The model may choose where to look, fill the evidence form with cited links, and write the morning queue. It may not set or change a price, change reserves, silence or delete alerts, or act on production. Code decides the price formula, the reserves, the always-page list, the re-pricing schedule and the page itself.
- **Demo moment (30 seconds):** Two night alerts side by side. Left: "404 burst", price 12 (no users affected, a known crawler), not paged. Right: "checkout 5xx", price 88 (41 users, a new error since the 04:55 deploy, two support emails), paged, and the page opens on that evidence. Morning: the queue, with one price marked wrong.
- **Nearest crowded space:** generic incident chatbots (excluded) and alert triage in paging tools. **Difference:** it never talks with responders and never touches production. It decides one thing, whether waking a person is worth it, and the price is set by code from evidence the agent collected.
- **Biggest feasibility risk:** the night start (a trigger-token pipeline counting as a human action is unverified), and paging a real phone (GitLab on-call schedules need Premium; email or a mention may have to stand in).

### M2. Limit Order

- **Mechanism:** a limit order: you give the broker your conditions and an expiry and walk away; it fills only when the conditions hold, or it is cancelled at expiry.
- **Pitch:** A developer leaves a deploy order with conditions and an expiry, goes home, and the agent ships it only when every condition holds, or cancels and tells her.
- **Person and moment:** Clara's change is ready at 5pm, but production is mid-incident and she has to pick up her kids. She leaves a limit order and goes, and at 19:40 her phone says the order filled because every condition was met at 19:31.
- **Flow:**
  1. Her MR is merged with the production job held. She writes the order as a comment ("@limit ship when the incident is closed and errors are under 1%, before 22:00, never Friday after 15:00"); the agent turns it into a structured order and posts it back, and she confirms with a mention. *(merge requests, manual CI/CD jobs, Duo flow with Mention trigger)*
  2. Code stores the order with its hard limits (expiry, time windows, target environment), and a pipeline schedule she owns runs every 15 minutes until expiry. *(issues or repository, pipeline schedules)*
  3. Each scheduled run checks the numbers in code, and its event starts the flow. The agent judges the conditions that need judgment (is the incident really resolved, did the database team finish their migration, has something happened that the order did not foresee) and writes a verdict. *(incidents, error tracking, Pipeline events trigger)*
  4. The next scheduled run, which runs with Clara's own rights because she owns the schedule, deploys if code finds a fresh "all conditions met" verdict and the hard limits still hold. *(environments and deployments, protected environments)*
  5. If something unforeseen happens, the agent does not ship and asks her. At expiry the schedule stops, and the agent cancels the order and tells her. *(mentions, issues)*
- **Stages:** release, monitor, govern.
- **Autonomy:** Hands-off: she sets the intent and walks away, the agent completes the loop to production on her terms, and anything the order did not cover goes back to her.
- **Model, code, person:** The model may turn her words into conditions, judge soft conditions, notice what the order did not foresee, and explain. It may not ship after expiry, change the conditions, or ship when a condition is unclear (unclear means wait and ask). Code decides expiry, windows, numeric thresholds and the deploy itself.
- **Demo moment (30 seconds):** 17:02, Clara types the order and leaves. The timeline shows checks every 15 minutes ("incident still open", "error rate 2.1%, above 1%"). At 19:31 every condition turns green, the deploy runs, and her phone lights up.
- **Nearest crowded space:** post-merge release gatekeepers, and GitLab's own auto-merge. **Difference:** a gatekeeper decides whether a change may ship; here a person writes her own conditions and expiry, and the agent is her broker, carrying out her decision later with production state and judgment calls as conditions.
- **Biggest feasibility risk:** a schedule-started pipeline counting as a human action for the flow trigger (unverified), and a scheduled job deploying to a protected environment in a workspace where roles are unclear.

### M3. Credit Line

- **Mechanism:** a line of credit: the lender sets a limit from your record, raises it as you repay, and cuts it when you default. The lender is the team, and the credit is autonomy.
- **Pitch:** A chore agent starts with zero autonomy and earns it per action type from its record in production; every increase is an MR a person merges, and a revert cuts it back to zero.
- **Person and moment:** Ruth, a team lead, does not trust agents to merge anything. Two weeks in, the agent sends her a credit application ("my last 14 patch upgrades were merged unchanged and none was reverted"), she approves one small step, and she feels that she, not the agent, decides how far it goes.
- **Flow:**
  1. `credit.yml` lists action types (patch upgrades of dev-only packages, quarantining a flaky test, removing a dead flag) and the limit for each, where 0 means ask every time. Code Owner rules make any change to it need Ruth's approval. *(repository, CODEOWNERS, MR approval rules)*
  2. The agent does chores in flows started by a person's schedule or by assigning a chore issue. It opens MRs, the pipeline runs, and a person merges or not. *(Duo flow with Pipeline events or Assign trigger, merge requests, CI/CD, security scans)*
  3. Code keeps the ledger from GitLab facts: for each agent MR, whether it was merged unchanged, changed, closed or later reverted, and whether an incident linked to it within 7 days. *(merge requests, incidents)*
  4. When the record supports it, the agent opens a "credit application" MR raising one limit by one step, with the record as the description. Ruth approves or closes it. *(merge requests, approvals)*
  5. Within its limit, the agent's MRs are set to auto-merge when the pipeline passes, and deploy as usual. A revert or a linked incident cuts that limit to zero (code), and the agent posts the default on the MR. *(auto-merge, environments and deployments)*
- **Stages:** create, verify, package, secure, release, govern.
- **Autonomy:** starts Assisted and earns Hands-off one action type at a time; every step up is a person's merge.
- **Model, code, person:** The model may do the chores, judge when to apply, and write the application. It may not change `credit.yml` except through an MR a person merges, act above a limit, or argue with a cut. Code decides the ledger, the default rule, and the limit check before any merge without a person.
- **Demo moment (30 seconds):** The credit application MR with its ledger (14 merged unchanged, 0 reverted). Ruth approves. The next patch upgrade merges and deploys by itself. Then a staged bad upgrade (labelled) is reverted, the limit drops to zero, and the agent's note says so.
- **Nearest crowded space:** evidence receipts and attestation, and the "autonomy budget" in BABYDOV Release Sentinel. **Difference:** the record is not proof for an auditor; it is a credit history that decides how much the agent may do next, and every increase is a human merge.
- **Biggest feasibility risk:** a believable track record by demo day (two weeks of real chore MRs, or seeded history clearly labelled), and auto-merge into a protected `main` that only Maintainers may merge into.

### M4. Triple A

- **Mechanism:** credit rating agencies rate each issuer and each bond, and investors set rules by rating (buy AAA without review, never buy junk).
- **Pitch:** The agent rates each new dependency version and its publisher, and code applies the team's rules: top-rated patches merge after a cooldown, low-rated ones wait for a person with a short report.
- **Person and moment:** Jules spends every Monday morning on 30 dependency update MRs and approves most of them unread. Now she reads two, each with a short report ("new publisher account, released 3 hours ago, adds an install script that calls the network"), and the other 28 are already in production.
- **Flow:**
  1. A schedule a person owns runs an updater (for example Renovate) that opens MRs for new versions; the pipeline's event starts the flow, which rates every MR that run opened. (MRs opened by a bot would not start a flow by themselves.) *(pipeline schedules, merge requests, Duo flow with Pipeline events trigger)*
  2. The agent reads the version diff, changelog, release age, publisher history, issues reported since release, and how the project uses the package, and decides how deep to go: a tiny patch from a long-time maintainer gets a light look, a new publisher gets a deep one. *(package registry or upstream source over allowlisted network access, repository)*
  3. It fills a fixed rating form with links. Code turns the form into a rating and applies `ratings-policy.yml`: AAA patch, wait 72 hours then merge if green; A, one approval; junk, blocked with the report. *(merge requests, approvals, auto-merge)*
  4. The pipeline runs tests, dependency scanning and license checks as usual. *(CI/CD, security scans)*
  5. Merged updates deploy normally. If one is later reverted or linked to an incident, code lowers that publisher's rating for next time. *(environments and deployments, incidents)*
- **Stages:** verify, package, secure, release, govern.
- **Autonomy:** Hands-off for top-rated patch updates within the policy; Supervised or Assisted for the rest.
- **Model, code, person:** The model may decide what to read and how deep, fill the form with evidence, and write the report. It may not set the formula or the policy, merge outside the policy, or shorten a cooldown. Code decides the rating from the form, cooldowns, merge rules and downgrades.
- **Demo moment (30 seconds):** Monday's list: 28 AAA updates with cooldown timers, 1 BB, 1 junk. The junk one is a staged, labelled case of a package version that adds a postinstall script calling an unknown host. Jules blocks it. The AAA updates merge themselves when their timers end.
- **Nearest crowded space:** security review and auto-fix on MRs, and Dependabot-style updaters. **Difference:** it does not scan your code for flaws. It rates the release and its publisher, applies cooldowns by rating, and lets most updates flow without a person.
- **Biggest feasibility risk:** reading package diffs and publisher history needs outside network access from the flow (an allowlist, which a group in strict mode would ignore); the supply-chain case must be staged and labelled.

### M5. Make Whole

- **Mechanism:** service credits and recalls: when a provider breaks a promise it compensates the affected customers, and when a product is faulty the maker finds every buyer. "Make whole" is the finance term for paying someone back for what they lost.
- **Pitch:** After an incident, the agent works out exactly which customers were hurt and how, prepares repairs and plan-based credits, and a person approves before anyone is contacted, repaired or credited.
- **Person and moment:** Mei runs customer success and usually spends two days in spreadsheets after an outage working out who to apologize to. An hour after this one closes she has 63 affected accounts with what happened to each, credits from their plans and a draft email each, and customers hear from her before they complain.
- **Flow:**
  1. The incident commander closes the incident and assigns the flow to it. *(incidents, Duo flow with Assign trigger)*
  2. The agent decides where to look (error tracking events in the incident window, app logs, failed jobs, the deployment involved, Service Desk tickets) and lists affected accounts with evidence for each. *(error tracking, environments and deployments, CI/CD, Service Desk)*
  3. Code computes the impact per account (minutes, failed requests) and the credit from the plan rules in `sla.yml`. No model touches the numbers. *(repository, CI/CD)*
  4. If data was damaged, the agent opens an MR with a repair script (for example, re-queue failed orders), and a CI job dry-runs it on a copy; a person approves the production run. *(merge requests, CI/CD, protected environments, deployment approvals)*
  5. The agent drafts one message per account, and a person approves the batch. Replies go out through Service Desk or the app's email, and credits are recorded on the incident. *(Service Desk, incidents)*
- **Stages:** plan, create, verify, release, monitor, govern.
- **Autonomy:** Supervised: a person approves the list, the repair and the messages as outcomes.
- **Model, code, person:** The model may find affected accounts and explain each, and write the repair script and the messages. It may not decide amounts, send messages or credits without approval, or run the repair on production. Code decides the incident window, impact numbers, credits and the dry-run result.
- **Demo moment (30 seconds):** The incident closes. A table fills with 63 accounts, each with "what happened" and evidence links, and credits appear from plan rules. Mei approves. One customer's email: "Between 14:02 and 14:41 your 3 orders failed. We have sent them again and added a $12 credit."
- **Nearest crowded space:** incident root cause and post-mortems. **Difference:** it never asks why it broke. It asks who was hurt and makes it right, which no known entry does.
- **Biggest feasibility risk:** a demo app with accounts, plans and believable incident data (all labelled), and keeping the repair step safe without the scope growing.

### M6. First Dibs

- **Mechanism:** a matching market, like a waitlist done well: scarce early access goes to the people who showed the most demand, not to a random slice of users.
- **Pitch:** When a requested feature ships behind a flag, the people who asked for it through support get it first, after a person approves, and their feedback flows back before the wide rollout.
- **Person and moment:** Ibrahim asked support for bulk editing twice and was told it was on the roadmap. A month later he reads "You asked for this, so you get it first, starting today; tell us what's wrong with it", feels like a partner, and sends the first bug report before the wide rollout.
- **Flow:**
  1. A developer merges the feature behind a flag that is off for everyone, and the deploy pipeline's event starts the flow. *(feature flags, merge requests, CI/CD, Duo flow with Pipeline events trigger)*
  2. The agent searches Service Desk issues for people who asked (by meaning), ranks demand (how often, how recently, how blocked they were) and drafts the first group with their quotes. Code removes anyone who has not agreed to be contacted and caps the group size. *(Service Desk, issues)*
  3. The product owner approves the group and the message with a mention. *(Mention trigger)*
  4. A CI job adds those users to the flag's user list, and the agent replies on each Service Desk issue. *(feature flags with user lists, CI/CD, Service Desk)*
  5. Replies land on the Service Desk issues. When the owner assigns the flow, it groups them on the feature issue (bugs, confusion, thanks) and proposes the next step, fix first or widen, and a person decides. *(Service Desk, issues, Assign trigger)*
- **Stages:** plan, configure, release, monitor.
- **Autonomy:** Supervised: the product owner approves the group and the message, and the agent does the matching, setup and grouping.
- **Model, code, person:** The model may find and rank the people who asked, write the messages, and group feedback. It may not add anyone who has not opted in, widen the rollout, or promise dates. Code decides opt-in, group size and the flag change.
- **Demo moment (30 seconds):** A flag at 0%. The agent shows "12 people asked for this", in their own words. The owner approves. The flag's user list fills with 12 IDs, Ibrahim's email arrives, and his reply with a bug lands on the issue.
- **Nearest crowded space:** none in the field; closest is progressive rollout inside release gatekeepers. **Difference:** the rollout order comes from who asked, not a random percentage, and those people hear back directly.
- **Biggest feasibility risk:** Service Desk setup, and linking a support email address to an app user ID for the flag's user list (a small identity table in the demo app).

### M7. Clearing House

- **Mechanism:** a clearing house settles every open position at the end of the day, so nothing between two parties is left without an owner.
- **Pitch:** At on-call shift change, the agent lists every open position (incidents, silenced alerts, half-done rollouts, armed auto-merges) and the two engineers settle each one by name before the handoff.
- **Person and moment:** Arjun ends a rough night shift at 9am, half asleep and worried he will forget the alert he silenced at 4am. He settles five open positions in two minutes, Julia accepts them, and he goes to bed knowing nothing is left hanging.
- **Flow:**
  1. At shift end the outgoing engineer assigns the flow to the handoff issue. *(issues, Duo flow with Assign trigger)*
  2. The agent decides where to look: incidents and their status, alerts acknowledged or ignored during the shift, flags changed during the shift, environments with failed or stopped deployments, MRs with auto-merge set, paused schedules, issues labelled `on-call`. Code confirms that each one really is open. *(alerts and incidents, feature flags, environments, merge requests, pipeline schedules)*
  3. It writes a settlement sheet on the issue: each position with links and a proposed settlement (close, transfer, or extend with an owner and an expiry). *(issues)*
  4. The outgoing engineer marks each line. The incoming engineer accepts with a mention, which runs the flow again to apply what was agreed (re-open the ignored alert, set owners and expiries, close what both agreed to close). *(Mention trigger, alerts, issues)*
- **Stages:** plan, release, configure, monitor, govern.
- **Autonomy:** Assisted: both people approve every settlement, and the agent finds, proposes and applies.
- **Model, code, person:** The model may decide where to look, describe each position, and propose settlements. It may not close or change anything both people did not agree to. Code decides whether a position is really open, and records who owns what after the handoff.
- **Demo moment (30 seconds):** The sheet with five positions. Arjun marks three "transfer", one "close", and the silenced alert "extend to 18:00". Julia accepts. The alert gets its expiry, owners appear on each item, and Arjun's status shows off duty.
- **Nearest crowded space:** summary bots and dashboards (excluded as a main idea). **Difference:** it is not a digest. Every open item has to be settled by name between two people, and the agent carries out the result.
- **Biggest feasibility risk:** many object types to read (alerts, flags, environments, schedules) through APIs the flow token may not reach, and staging a realistic night's worth of open items.

### M8. Last Caller

- **Mechanism:** escrow: a neutral party holds something until the conditions both sides agreed on are met, then releases it.
- **Pitch:** Removing an old API endpoint is held in escrow until production traffic shows nobody calls it; the agent finds the last callers and warns each by name, and when usage has been zero long enough it releases the removal MR for a person to merge.
- **Person and moment:** Bruno has kept the old `/v1/orders` endpoint alive for two years because nobody knows who still calls it, and every change to orders has to be made twice. The agent finds the last two callers, both move after a direct note, and fourteen quiet days later Bruno merges the removal without fear.
- **Flow:**
  1. The API owner opens a "sunset" issue (what goes, the replacement, the earliest removal date) and assigns the flow. The flow opens the removal MR as a draft. *(issues, merge requests, Duo flow with Assign trigger)*
  2. Each week a schedule the owner owns runs a CI job that counts production calls to the old endpoint or field from logs, grouped by caller (API key, user agent, source service). *(pipeline schedules, CI/CD, logs in Cloud Logging or GitLab Observability)*
  3. The pipeline's event starts the flow. The agent decides who each caller is and how to reach them: an internal service (it searches the group's code for the URL and opens an issue in that project) or a partner (a Service Desk note, sent after the owner approves the wording). Each note says what they call, how often, what to use instead, and by when. *(Pipeline events trigger, code search, issues in other projects, Service Desk)*
  4. Code holds the escrow conditions: zero calls for 14 days in a row, and the removal date reached. Until both hold, the removal MR stays a draft with a live count in its description. *(merge requests, CI/CD)*
  5. When both hold, the agent marks the MR ready and asks the owner to merge. After release, a CI job watches for calls to the old path for a week and alerts the owner if anyone shows up. *(merge requests, environments and deployments, alerts)*
- **Stages:** plan, create, release, monitor, govern.
- **Autonomy:** Supervised: the agent tracks, warns and prepares; the owner approves outside messages and merges the removal.
- **Model, code, person:** The model may identify callers from the evidence, choose how to reach each one, and write the notes. It may not remove anything, contact outside parties without approved wording, or shorten the escrow period. Code decides the counts, the 14-day rule, the date and the post-release watch.
- **Demo moment (30 seconds):** The sunset issue's live count: "3 callers, 1,240 calls last week". The notes go out; the count drops to 2, then 1, then 0; a labelled, compressed clock runs fourteen days; the draft removal MR flips to ready; Bruno merges it.
- **Nearest crowded space:** pre-merge blast radius. **Difference:** it does not guess consumers from code before a merge; it reads real production traffic over weeks, reaches the actual callers, and holds the removal until the traffic proves nobody is left.
- **Biggest feasibility risk:** believable traffic from several labelled demo callers over time, log queries from CI, and access to other projects to open issues there.

## Also produced by these lenses, already held in lens_oncall_inversion.md

These six came out of the game and market lenses too, before I saw the parallel file. They match concepts written there, so they are not repeated in full. Each line says only what these lenses add, for the merge step.

1. **Night Orders** (overwatch in XCOM, gambits in Final Fantasy XII; as a market order, a stop-loss). Same concept as "1.1 Night Orders", down to the captain's night order book. Adds: orders behave like a turn, so each fires at most once and all expire at 09:00; the night pipeline can be started by a trigger token the on-call engineer owns, so the action job runs on her own earlier approval rather than through a separate service account; and it pairs with Limit Order (M2) as the stop-loss to Limit Order's entry.
2. **Sparring** (a tutorial that teaches by doing; a sparring partner). Same as "1.6 Fire Drill". Adds: the drill is also a test of the runbook (a step that no longer works is a finding, fixed by an MR in the trainee's name); hints are sized like a game's hint system; a fault catalog in code limits what the agent can break.
3. **No Undo** (permadeath and ironman mode). Close to "2.2 Return Ticket". Adds: irreversible effects beyond the schema (emails or payments sent by jobs, cache and file format changes, backfills that overwrite data), and a freshness rule: the irreversible job refuses to start if its rehearsal on a fresh copy is more than an hour old.
4. **Quest Giver** (the quest turn-in). Same as "2.3 Promise Kept". Adds: the turn-in asks "does it work for you?", and the answer flows back (a "still broken" reply reopens the linked issue in the user's words); it pairs with First Dibs (M6), which reaches the same people earlier in the rollout.
5. **Breather** (the AI Director in Left 4 Dead). Close to "1.8 Daylight Rollout". Adds: the pace also follows team fatigue (pages and incidents in the last 24 hours, not only who is awake), and the agent may step back as well as hold.
6. **IOU** (deposits and IOUs). Close to "1.4 Loose Ends". Adds: the IOU is recorded at the moment of the hurried change, with a return date the person picks ("@iou until 10:00"), not only reconstructed after the incident; skipped tests and forgotten flags count too (a flag fully on for 60 days becomes an IOU). The cautionary story: Knight Capital lost about $440 million in 45 minutes in 2012 when a reused flag woke up old code on a server that missed a deploy ([SEC order 34-70694](https://www.sec.gov/litigation/admin/2013/34-70694.pdf), not opened in this session, unverified).

## Notes for the scoring step (no scores here)

- **Pairs inside this file:** Shield Wall (users during an incident) and Make Whole (customers after it); Tactical Pause (freeze all change) and Limit Order (a pending deploy can wait for "pause lifted" as a condition); Telegraph (scheduled jobs meet new code) and Next Wave (a traffic wave meets the system), both about a known future moment.
- **Neighbors in lens_oncall_inversion.md:** Reserve Price and "1.5 Sleep Debt" (night pricing of one alert, against weekly rule cleanup) and "1.7 Someone Awake"; Shield Wall and "1.3 Watermelon" (customer reports used to shield responders, against reports used to detect an outage); Triple A and "2.5 Fine Print" (supply-chain trust in a release, against behavior changes proven by tests); First Dibs and "2.3 Promise Kept"; Clearing House and "1.4 Loose Ends".
- **Shared weak point:** Reserve Price, Limit Order, Credit Line, Triple A, Last Caller and Telegraph's reminders start flows from a pipeline that a schedule or trigger token started. If that does not count as a human action for a flow trigger, they need another start (for example the Flows API, also unverified). Test this first if any of them is chosen.
- **Considered and dropped while generating:** Cairn (a note from the last person who handled an alert, shown when it fires again; close to LORE's organizational memory); Skill Tree (earned agent autonomy, kept as Credit Line); Wards (fog of war: add monitoring where new code has none; close to "Kill Switch" and "Watermelon"); Ready Check (wait for the right people to be online before a deploy; close to "Someone Awake" and "Daylight Rollout"); Limit Down (an automatic circuit breaker on change speed; too close to gatekeepers, kept as the person-triggered Tactical Pause); Exit Quotes (a tested revert kept ready for every change; close to "Kill Switch", "Return Ticket" and "Dress Rehearsal"); Sleep Budget (what alerts cost in sleep; same as "Sleep Debt"); a reputation score for flaky tests (replaced by No Reloads); Customs (declare new outbound data flows at release; weak market fit, close to "Log Leak"); Margin Call (cap the number of open risks at once; close to gatekeepers).
