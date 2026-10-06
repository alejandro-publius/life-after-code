# Ideas from two lenses: the 3am on-call engineer, and inversion

Generated on 2026-10-06 as input for Part 5 (docs/IDEAS.md). This is generation only: nothing here is scored or ranked.

Inputs: [IDEATION_BRIEF.md](../IDEATION_BRIEF.md), [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md), [field/code_hosts.md](../field/code_hosts.md), [field/social.md](../field/social.md). No web search was used. Names were checked only against the entries named in those field notes.

Every concept follows the house rule: the model chooses where to look, code decides what is true, a person decides when the agent acts on anything that matters. People, companies, versions and numbers in the scenes are invented for illustration and would be labelled as demo data.

## Shared mechanics (assumptions used below)

1. Demo target: a small app on Cloud Run with `staging` and `production` environments, like the judges' reference project ([guide](../gitlab_guide_and_reference.md), "The reference project end to end").
2. Starting a flow: "All trigger event types require a human user to perform the triggering action", and a flow cannot start another flow ([guide](../gitlab_guide_and_reference.md), "Triggers"). Concepts that start from a person's own action (assign, mention, approve, mark ready, set a status) are safe. Concepts that must start at night with nobody awake (Night Orders, Watermelon, Someone Awake, Daylight Rollout, Lifeboat) depend on the Flows API called from a small relay on Cloud Run, or on a pipeline from a person-owned schedule. Whether either counts as a human start is (unverified). Test on day one.
3. Acting outside GitLab: flows cannot read CI/CD variables, but can get OIDC tokens through `id_tokens` in `.gitlab/duo/agent-config.yml` and reach hosts listed under `network_policy.allowed_domains`, unless the group runs strict mode (unverified) ([guide](../gitlab_guide_and_reference.md), "Where flows run").
4. The "code decides" layer used throughout: production actions go through one small script or CI job that checks the request against a file a person merged, and the Google Cloud service account behind it can do only those actions. The model can ask; it cannot widen what is possible.
5. Human gates used: MR approval and merge, manual CI jobs, protected environments with deployment approvals (Premium; setup needs Maintainer, unverified in our role), and comments that mention the flow. `HumanInputComponent` inside a triggered flow is untested ([guide](../gitlab_guide_and_reference.md), "Flow components and syntax"), so no concept depends on it.
6. Not covered by our research, so (unverified) for our workspace: writing feature flags through the API, Service Desk setup, on-call schedules and escalation policies, container registry cleanup policies and protected tags, reading user status and time zone from inside a flow.

---

## Lens 1: the 3am on-call engineer

What would let the person holding the pager sleep, trust, or stop dreading the night?

### Banned: the three most obvious answers

1. **BANNED: Incident summary chatbot.** Explains the alert, the logs and the recent deploys in the incident issue or in chat.
2. **BANNED: Auto-rollback on alert.** An alert fires after a deploy and the agent rolls back on its own.
3. **BANNED: Root cause analyzer.** Walks from the alert to the deploy, the merge request and its author, and names the culprit.

Close variants also off the table: a postmortem draft writer, "similar past incidents" search, alert deduplication and grouping at page time, and a "self-healing" runbook executor that runs fixes in production without a person.

### 1.1 Night Orders

- **Pitch:** Before bed, the on-call engineer signs the agent's night orders: the few things it may fix alone tonight, and exactly when it must wake her. (Ship captains do this: they write night orders for the officer on watch before they sleep.)
- **Person and moment:** Priya is on call for the first time since her daughter was born, and she has not slept through a pager week in a year. At 22:00 she reads three orders the agent drafted from the day's changes, deletes one, approves the merge request, puts her phone face down and sleeps until six.
- **Flow:**
  1. Plan: Priya assigns the "Tonight's watch" issue to the flow's service account (Assign trigger, her action). The Duo flow reads the day's merged MRs, production deployments, feature flag changes and open incidents, decides which of them could page tonight, and opens an MR to `ops/night-orders.yml`. Each order has a condition (signal, threshold, duration), one action from a fixed menu (turn a named feature flag off, send Cloud Run traffic back to the previous revision, raise max instances) and the change that motivates it. Everything else is "wake Priya".
  2. Govern: Priya edits or deletes orders, approves and merges. The file on the default branch is the only thing code trusts.
  3. Monitor: at night an alert (Cloud Monitoring or GitLab Observability) reaches a small relay on Cloud Run, which opens a GitLab incident and starts the night-watch flow through the Flows API. The flow chooses which logs, traces and metrics to read (observability MCP server or Cloud Logging) and decides whether the situation matches an order.
  4. Configure or release: the flow asks `ops/act.py` to run the matched action. Code checks the request against the merged orders (same signal, named target, listed action, time window, once per night), runs it with a Google Cloud service account that can do nothing else, and re-checks the signal ten minutes later. No match, or no recovery, means a three-line page to Priya: what fired, what was checked, what the agent suggests.
  5. Morning: the flow writes the watch log on the issue (what happened, what it did, what it chose not to do and why). Each action taken under orders gets an undo or keep manual job. Orders expire at 09:00.
- **Stages:** plan, release, configure, monitor, govern.
- **Autonomy:** Hands-off, with a fence. Priya sets the intent at 22:00 and walks away; nobody approves the 03:00 step. The fence: tonight's powers were granted by a person, for tonight only.
- **Model may / may not; code decides:** The model may choose what to investigate, draft the orders, judge whether a live situation matches an order, and write the page and the log. It may not add an action at night, touch a target not named in an order, act twice, deploy code or touch data. Code decides whether a request matches a merged order, the cloud permissions cap what is possible at all, and the recovery check decides whether Priya is woken.
- **30-second demo moment:** Split screen at 03:12: the checkout error graph spikes, the flow matches order 2 ("if `new_checkout` errors stay above 5% for 5 minutes, turn the flag off"), the graph drops, and Priya's phone on the nightstand stays dark. A minute later a second alert matches no order and the phone lights up with a three-line page.
- **Nearest crowded space:** Auto-rollback on alert, and the release gatekeepers that roll back. Difference: the agent has no standing power. Each night a person grants a short list of named, reversible actions tied to that day's changes, the default is to wake her, and the product is the decision not to wake someone, not the rollback.
- **Biggest feasibility risk:** Starting a flow at night with nobody awake. The alert path depends on the Flows API (or a person-owned scheduled pipeline) being accepted as a human start (unverified). Also: Google Cloud access from inside a flow through `id_tokens` and the network allowlist (unverified in the hackathon group).
- **Variant, Watch It:** when she is paged, one tap hands only the watching to the agent. It picks the signals, code checks them every minute, and it wakes her again only if things get worse. Lower autonomy (Assisted), same bedroom scene.

### 1.2 Dress Rehearsal

- **Pitch:** When the page comes, the agent has already tried the likely fixes on staging, so the half-awake engineer picks a fix that was tested, not guessed.
- **Person and moment:** Tomás is woken at 03:40 with his heart pounding and has to choose between a rollback, a flag or more instances, knowing a wrong guess costs another hour of night. He opens the incident and finds three options, each with a small before-and-after chart from staging, and taps the one that brought errors to zero.
- **Flow:**
  1. Monitor: an alert opens an incident and pages Tomás (escalation policy email or push). He acknowledges by setting the incident status (Work item status changed trigger, his action), which starts the rehearsal flow.
  2. The flow samples failing production requests from logs and traces (code scrubs personal data first), forms two to four hypotheses, and picks which mitigations from the menu are worth testing: a feature flag off, the previous revision, a config value, more instances.
  3. Verify: for each candidate, a CI job applies it to a no-traffic staging revision on Cloud Run (tagged URL) and replays the sampled requests; code measures error rate and latency. At most four candidates and six minutes in total.
  4. The flow posts a ranked menu in the incident: "A: turn off `new_pricing` (staging errors 37% to 0%). B: previous revision (0%, but also undoes two other fixes). C: more instances (no change)." Each option is a manual job.
  5. Release or configure: Tomás runs option A (manual job on the protected `production` environment). CI applies it, and the flow re-checks the live signal and adds a timeline event to the incident.
- **Stages:** verify, release, configure, monitor.
- **Autonomy:** Assisted. A person approves every change to production; the agent experiments only where it is safe.
- **Model may / may not; code decides:** The model may choose which requests to sample, which hypotheses to form and which mitigations to try, and explain the results. It may not touch production, try more than four options, or invent an action outside the menu. Code computes the replay numbers, ranks the options by them, and only the manual job can change production.
- **30-second demo moment:** Four minutes after the page, three small before-and-after charts appear in the incident. Tomás's thumb taps "Run" on option A and the production error graph falls.
- **Nearest crowded space:** Root cause analyzers and auto-rollback. Difference: it never names a cause and never acts alone; it runs experiments on staging and hands a person a tested choice.
- **Biggest feasibility risk:** Reproducing a production failure on staging by replaying requests. It needs a planted bug that replays cleanly and requests without side effects, and the status trigger must work on incidents (unverified).

### 1.3 Watermelon

- **Pitch:** When the dashboards are green but customers are writing in, the agent notices, reproduces the problem, and wakes a person. (A "watermelon" metric is green outside and red inside.)
- **Person and moment:** At 02:10 Noor, a nurse finishing a night shift, writes "I can't log in, is it just me?", and two more customers write the same within twenty minutes, while every monitor stays green because the health check only calls /health. The on-call engineer is woken by a page that says "monitors are green, three people cannot sign in, I reproduced it", and Noor gets an answer before her next shift, and the feeling that someone believed her.
- **Flow:**
  1. Plan: customer emails arrive through Service Desk and become issues.
  2. A person-owned scheduled pipeline counts new Service Desk issues every ten minutes (code). When two or more arrive close together, it starts the flow (pipeline event or Flows API).
  3. Verify: the flow reads the tickets, decides whether they describe the same failure, picks a journey to reproduce (for example "sign in with Google on Android"), and writes or chooses a synthetic check that CI runs against production with a test account.
  4. Monitor: code decides. If the check fails, the flow opens an incident linked to the tickets and pages the on-call engineer (escalation policy). If it passes, nothing pages, and the tickets get a "could not reproduce" note for the morning support queue.
  5. Configure: after the fix, the flow opens an MR adding the missing synthetic check or alert rule, so a machine catches it next time; the on-call engineer approves. A support person approves one reply to all three reporters.
- **Stages:** plan, verify, configure, monitor.
- **Autonomy:** Supervised. The agent investigates, reproduces and pages on its own; people approve the new monitor and anything sent to customers.
- **Model may / may not; code decides:** The model may decide whether tickets are the same problem, choose what to reproduce and how, and draft the page, the check and the reply. It may not page on ticket count alone, send anything to customers, or change monitoring without a merged MR. Code decides the clustering threshold, whether the reproduction failed, and who is on call.
- **30-second demo moment:** The monitoring page is all green. Three emails land. A minute later a phone buzzes: "Monitors green. 3 customers cannot sign in. Reproduced: /auth/callback returns 500 for Google sign-in." Then the MR "Add synthetic sign-in check" appears.
- **Nearest crowded space:** Incident root cause and post-deploy verification. Difference: the alarm comes from people, not metrics; it catches what monitoring misses and then closes the gap with a new monitor.
- **Biggest feasibility risk:** Service Desk issues are created by a bot user, which cannot fire a trigger, so the start depends on a scheduled pipeline or the Flows API counting as human (unverified). Service Desk setup may also need Maintainer (unverified).

### 1.4 Loose Ends

- **Pitch:** After an incident, the agent remembers every temporary thing people did at 3am and makes sure each one is undone, or kept on purpose.
- **Person and moment:** Two weeks ago at 03:30, Sam turned off the `eu_tax` flag, silenced the disk alert "for an hour" and raised Cloud Run to ten instances; the fix shipped four days later and nobody remembered any of it. On Monday Sam gets one merge request, "During INC-12 you made three temporary changes, the fix is live, here is the undo for each", and feels that someone has his back.
- **Flow:**
  1. Monitor: when a person sets an incident to Resolved (Work item status changed trigger), the flow reads the incident timeline and comments, feature flag history, alert silences, Cloud Run revision and scaling history, and branches created in the incident window. It decides which changes were temporary mitigations (notes like "for now" or "until the fix ships").
  2. Code builds the ledger: for each candidate, the state before the incident and now (flags, silences and their expiry, instance counts, pinned versions, hotfix branches not merged back).
  3. Release: code checks whether the reason still holds. Is the fix MR's commit deployed to production (deployments API)? If yes, the flow proposes the undo. If not, it keeps the mitigation and links the blocker.
  4. Configure: the flow opens one MR "Loose ends from INC-12" that changes the ops config files (flags, silences, scaling), assigned to whoever made each change. Merging applies the undo through CI. Anything that is not config becomes a manual job.
  5. Govern: at each on-call handoff, the outgoing engineer assigns the handoff issue to the flow, which lists everything still temporary across all incidents, so the incoming engineer does not inherit hidden traps.
- **Stages:** plan, release, configure, monitor, govern.
- **Autonomy:** Supervised. The agent assembles the ledger and the undo plan; a person approves the result in one review.
- **Model may / may not; code decides:** The model may decide which changes were mitigations and propose undo or keep, with a reason. It may not undo anything itself. Code decides the before and now state, and whether the fix is deployed in production.
- **30-second demo moment:** The MR description lists: `eu_tax` still OFF (fix v1.8.2 live since Thursday, EU customers still on the old tax path), disk alert silenced 14 days (meant for 1 hour), 10 instances (about three times the usual cost). Sam approves and the flag comes back on.
- **Nearest crowded space:** Postmortem writers and incident root cause. Difference: it ignores why things broke and tracks the leftovers of the response, which nobody owns today.
- **Biggest feasibility risk:** A reliable history of manual changes (flag changes, silences, scaling) that the flow's token can read; audit events may need a higher tier or role (unverified). The demo mitigations will be staged by script, so they must look like real 3am work.

### 1.5 Sleep Debt

- **Pitch:** The agent counts how much sleep each alert rule cost the team, and pays it down with rule changes that are replayed against real history before anyone approves them.
- **Person and moment:** Jun was woken four times last week by `DiskUsageHigh`, and each time he looked, did nothing, and lay awake until five. On Friday he gets a merge request, "This rule woke Jun 4 times in 7 days and never needed action; with a 30-minute window it would have paged 0 times and still caught the real outage on 3 September", and approves it with a grin.
- **Flow:**
  1. Govern: once a week the team lead assigns the "Sleep debt" issue to the flow (Assign trigger). The flow pulls the last 30 days of alerts and incidents: when, who was paged, and what followed.
  2. Monitor: code computes the ledger: per rule, pages between 22:00 and 07:00 in the paged person's time zone, and whether an action followed within 30 minutes (a deployment, a flag change, a manual job).
  3. Configure: the flow picks the worst rules and proposes changes in the alerts-as-code file (`monitoring/alerts.yaml`): a longer window, a different threshold, a daytime queue instead of a page, or deletion.
  4. Verify: code replays each proposed rule against stored metric history and against the incidents marked real. Any proposal that would have missed a real incident is dropped.
  5. The flow opens one MR per rule with the replay table; the rotation approves; CI applies the rule to Cloud Monitoring (or GitLab Observability).
- **Stages:** verify, configure, monitor, govern.
- **Autonomy:** Supervised. The agent delivers finished, tested changes; people approve outcomes.
- **Model may / may not; code decides:** The model may choose which rules to work on and propose the change. It may not change a live rule without a merge, or keep a proposal that misses a real incident. Code decides the ledger counts, the replay, and the "still catches every real incident" check.
- **30-second demo moment:** The MR's replay chart: seven red night pages under the old rule, zero under the new one, and the 3 September outage still marked "caught".
- **Nearest crowded space:** Alert deduplication at page time (listed as an obvious answer above) and dashboards. Difference: it fixes the rule that makes the noise, as code, proven by replay; nothing changes at page time and nothing is a dashboard.
- **Biggest feasibility risk:** It needs weeks of realistic metric and paging history. Within the build window that has to be seeded demo data, clearly labelled, which can make the result feel staged.

### 1.6 Fire Drill

- **Pitch:** Before a new engineer's first on-call week, the agent designs a realistic outage from this month's real changes, stages it on staging, and coaches them through it.
- **Person and moment:** Kofi joined six weeks ago, his first on-call week starts Monday, and he has been lying awake imagining a page he cannot handle. On Thursday afternoon his phone buzzes with a drill page, he works the staging incident with hints from the agent and fixes it in 25 minutes, and he walks into Monday having done it once.
- **Flow:**
  1. Plan: the on-call lead assigns a "Drill for @kofi" issue to the flow (Assign trigger). The flow reads the last month's merged MRs, incidents and runbooks, and picks a failure that is realistic and worth learning (a bad flag combination, a slow dependency, a missing environment variable).
  2. It writes the drill plan as an MR to `drills/<date>.yml`: what breaks (staging only), how it will show up, how to undo it, and a time limit. The lead approves.
  3. Configure: on merge, CI injects the fault into the `staging` environment through a fault toggle built into the demo app, with an automatic undo after 45 minutes no matter what (code).
  4. Monitor: the drill page reaches Kofi. He works in the drill incident; when he mentions the flow (Mention trigger), it gives a hint, not the answer, and each hint is a little more specific.
  5. Create: afterwards the flow writes a short, kind debrief and opens MRs fixing the runbook gaps Kofi hit (for example a command that stopped working after the move to Cloud Run), assigned to the lead.
- **Stages:** plan, create, verify, configure, monitor.
- **Autonomy:** Supervised. The lead approves the plan; the agent runs the drill steps alone.
- **Model may / may not; code decides:** The model may choose the scenario, give graded hints, and write the debrief and the runbook fixes. It may not touch anything outside staging, extend the drill, or rate the person in public. Code limits injection to staging, runs the undo timer, and decides when the fault is cleared (signals back to normal).
- **30-second demo moment:** Kofi's phone buzzes "DRILL: checkout errors on staging"; a short time-lapse of him in the incident; then the debrief: "You found it in 23 minutes. Step 4 of the runbook was wrong, so I opened !57 to fix it."
- **Nearest crowded space:** Onboarding aids (36 in June). Difference: it is not questions and answers about the codebase; it breaks a real environment on purpose, exercises the response loop, and its output fixes runbooks.
- **Biggest feasibility risk:** The demo app needs built-in fault toggles and a drill that feels real rather than a toy, and the scope can creep into a training platform.

### 1.7 Someone Awake

- **Pitch:** Before it wakes the on-call engineer for a non-critical alert, the agent looks for a teammate who is awake, knows that part of the system, and agrees to take it.
- **Person and moment:** It is 03:05 in Berlin and Lena, who is on call, is asleep; in San Francisco it is 18:05 and Marcus, who reviewed the payment retry change last week, is wrapping up his day. Marcus gets a short ask ("Lena is asleep; this looks like the retry change you reviewed; can you take it before you log off?"), says yes, and Lena wakes at 07:00 to a resolved incident and a thank-you to Marcus.
- **Flow:**
  1. Monitor: an alert opens an incident and starts the flow (relay and Flows API, as in Night Orders). Code reads the severity: severity 1 pages the on-call engineer at once, with no detour.
  2. For lower severities, the flow decides who could handle it: CODEOWNERS, recent authors and reviewers of the affected code, past incidents in the same area.
  3. Code filters: only people inside their working hours (profile time zone) and not marked busy (GitLab user status), and at most two asks.
  4. Plan: the flow mentions the chosen person in the incident with a short ask and a 15-minute window. A reply "taking it" (Mention trigger, their action) makes the flow assign the incident to them and post a handoff summary. If nobody accepts in time, code pages the on-call engineer through the escalation policy.
  5. In the morning the flow posts the outcome, with a thank-you that credits the helper, on the incident and in the handoff issue.
- **Stages:** plan, monitor.
- **Autonomy:** Supervised. The agent routes on its own, but nothing moves without a person accepting, and severity 1 skips the agent.
- **Model may / may not; code decides:** The model may pick the best helper and write the ask. It may not assign without a yes, skip the on-call engineer for severity 1, or ask more than two people. Code decides working hours, busy status, the timeout and the severity rule.
- **30-second demo moment:** Two clocks on screen, Berlin 03:05 with a moon and San Francisco 18:05 with a sun. Marcus replies "on it". Lena's phone stays dark.
- **Nearest crowded space:** Root cause analyzers, which also read change history. Difference: it uses history to find a helper, not a culprit, and the output is a handoff the helper agreed to.
- **Biggest feasibility risk:** Reading teammates' time zones and status from inside a flow (unverified), plus the night start. The demo needs at least two real accounts, and the 15-minute timeout needs an outside timer (Cloud Tasks or a delayed job), because a flow cannot wait or restart itself.

### 1.8 Daylight Rollout

- **Pitch:** A feature flag rollout moves forward only while the people who own it are awake; at night the agent holds, so no robot pushes a feature to 50% at 2am.
- **Person and moment:** Dana, the product manager, wants the new search at 100% by Friday, and Ravi, on call all week, dreads rollouts that move overnight. Each evening Ravi gets one note ("holding at 25% overnight, errors flat, here is the off switch"), and on Thursday the rollout stops on its own when a signal turns and asks Dana and Ravi together what to do.
- **Flow:**
  1. Plan: Dana opens a rollout issue from a template and assigns it to the flow (Assign trigger). The flow proposes a plan as an MR to `rollouts/new_search.yml`: steps (5, 25, 50, 100%), the signals that reflect this feature (it picks metrics and log queries tied to the changed code), pass criteria, and the daylight hours of the owner and the on-call engineer. Dana and Ravi approve.
  2. Configure: a person-owned schedule runs a small pipeline every hour. Code checks the daylight window, the pass criteria on real metrics, and the plan. When all hold, a CI job raises the GitLab feature flag percentage for the `production` environment.
  3. Monitor: on each step the flow (pipeline event) writes a short note on the issue: what moved, what it watched, what it saw.
  4. Release: at the end of daylight, code freezes the rollout and the flow posts the overnight note to the on-call engineer, with the kill switch.
  5. If a criterion turns red, code holds (it never advances on red). The flow looks at what changed and asks the owners in the issue: hold, step back, or turn off (manual jobs).
- **Stages:** plan, release, configure, monitor.
- **Autonomy:** Hands-off. Dana and Ravi set the intent once and walk away; the flag climbs to 100% in production with no person in the middle, and a person is pulled in only on red.
- **Model may / may not; code decides:** The model may choose the signals and pass criteria to propose, and explain what it sees. It may not advance at night, advance on red, or change the approved plan. Code decides the window, the criteria and the flag percentage.
- **30-second demo moment:** A 48-hour timeline with sun and moon icons: the flag climbs in steps under the sun, stays flat under the moon, and the 18:00 "holding overnight" note arrives on Ravi's phone.
- **Nearest crowded space:** Canary analysis inside release gatekeepers. Difference: it manages feature flag exposure (the configure stage) around people's sleep, not a deploy gate; the rule that matters is who is awake.
- **Biggest feasibility risk:** Changing GitLab feature flags from CI needs a token with API rights (likely a personal or project token; unverified in our role). The model's share is small (signal choice and investigation), so the flow must visibly matter, and showing days of rollout in a 3-minute video needs honest time compression.

---

## Lens 2: inversion

How would we guarantee that a release fails? Each answer is turned around into a concept.

### Banned: the three most obvious negations

1. **BANNED:** "Nobody ran the tests or the scans" turned into a release gate that blocks on failed tests and scans. This is the most crowded October space and the judges' own reference project.
2. **BANNED:** "There was no rollback plan" turned into automatic rollback, or a rollback rehearsal on every release.
3. **BANNED:** "Nobody really reviewed the change" turned into an AI code reviewer on the merge request.

Close variants also off the table: "no deploys on Friday" calendars, release notes writers, and pre-merge "what could this break" reports.

### How to guarantee a release fails (18 ways), and the negation of each

| # | How to guarantee the release fails | Negation | Where it went |
|---|---|---|---|
| 1 | The only person who understands the migration is on a plane when it runs. | Get the knowledge out of her head while she is still on the ground. | 2.1 Plane Mode |
| 2 | The migration drops a column, so "roll back" puts back code that crashes on the new schema, and nobody knew the release was a one-way door. | Prove each release has a way back, or have a person sign for the one-way trip. | 2.2 Return Ticket |
| 3 | The customer who reported the bug is never told it is fixed, and cancels the day after the fix ships. | When the fix is live for them, tell them personally. | 2.3 Promise Kept |
| 4 | The redesign ships on Friday, nobody on the team uses a screen reader, and on Monday a blind customer cannot reach the Pay button. | Before promotion, an agent with no mouse and no screen must complete the purchase. | 2.4 No Mouse |
| 5 | A minor version of a transitive dependency changed a default timeout, and nobody read its changelog. | Read the fine print of every upgrade and prove with a test whether it touches us. | 2.5 Fine Print |
| 6 | Last night's registry cleanup deleted last week's image, so the 3am rollback has nothing to roll back to. | Never let cleanup delete a lifeboat. | 2.6 Lifeboat |
| 7 | The new feature has no off switch, so at 3am the only way to stop it is a full rollback that also undoes three unrelated fixes. | Every risky new path ships behind a switch tied to its alert and its runbook line. | 2.7 Kill Switch |
| 8 | A new debug line writes customers' email addresses into logs that forty contractors can read. | After each release, check the new log lines in production for personal data. | 2.8 Log Leak |
| 9 | During an incident the on-call engineer silenced an alert "for an hour"; three weeks later it is still silent when the same failure returns. | Track every temporary mitigation until someone undoes it on purpose. | 1.4 Loose Ends |
| 10 | The release goes out at 16:55 on a Friday and the person on call is a new hire who has never seen the service. | The obvious negation (no Friday deploys) is banned. Used instead: let the new hire live through a bad night in rehearsal first. | 1.6 Fire Drill |
| 11 | The feature goes to 100% in one step at 18:00, and the on-call engineer does not know it exists. | Rollouts move only while their owners are awake. | 1.8 Daylight Rollout |
| 12 | Someone set `PAYMENT_TIMEOUT` by hand in staging last Tuesday to make a test pass; production does not have it. | Catch settings that exist in one environment only, and ask their author before release. | Hand Edits (not developed) |
| 13 | The migration takes 2 seconds on staging's 1,000 rows and locks the orders table for 40 minutes on production's 90 million. | Rehearse migrations on a synthetic copy with production's size and shape, and propose a batched version. | Scale Model (not developed; pairs with Return Ticket) |
| 14 | The test everyone retries as "flaky" failed for a real race condition this time, and the retry turned it green. | Do not accept a pass on retry until the failure matches a known flake signature. | Not Flaky (not developed: sits next to the crowded CI failure tools) |
| 15 | Six months later an auditor asks who approved the v2.3 production deploy and why a critical finding was accepted, and an engineer loses a week digging. | Answer an auditor's questions from GitLab's own records, with links, when asked. | Audit Desk (not developed: next to the crowded evidence receipts space) |
| 16 | The data backfill after the migration starts at noon, at peak traffic, and slows the site for everyone. | Schedule heavy post-release jobs by observed traffic, with a person approving the window. | not developed |
| 17 | The announcement promises a feature that is still behind a flag at 0% for most customers. | Check what is announced against what is switched on before it goes out. | not developed (too close to release notes writers) |
| 18 | A certificate or API key the new feature depends on expires two days after launch. | Find what the release newly depends on, and when each of those expires. | not developed |

### 2.1 Plane Mode

- **Pitch:** Before a release, the agent finds the knowledge that lives in only one person's head, and interviews her while she is still on the ground.
- **Person and moment:** Ana wrote the billing migration, and two hours after the release window opens she boards a 14-hour flight to Manila for her sister's wedding. The day before, the agent asks her four pointed questions in the release issue; at 02:00, when the migration stalls, the on-call engineer follows her answers, and Ana lands to a note that says "You were not needed. Congratulations to your sister."
- **Flow:**
  1. Plan: the release manager assigns the release issue (a milestone with a date) to the flow (Assign trigger). The flow reads the MRs in the release and decides where knowledge is concentrated: who wrote and reviewed each risky piece, who else ever touched those files, who handled related incidents.
  2. Code checks availability: each expert's GitLab status (busy, out-of-office message, clear date) against the release window, and flags "only one expert, and she is away".
  3. The flow opens an interview thread mentioning the expert, with three to five questions written for a stranger at 3am: how will we know it is broken, what is safe to retry, what must never be done, how to undo, who else to ask. Each reply (Mention trigger, her action) wakes the flow, which checks the answer against the diff ("you wrote 'just roll back', but 0042 drops `invoice.legacy_id`; is rollback safe?") and asks at most one follow-up.
  4. Release: the answers become a "Plane Mode card" attached to the GitLab release and linked from the runbook of the affected components. If a flagged piece has no answered card, the deploy job waits until the release manager accepts the gap or moves the date (manual job).
  5. Monitor: if an alert fires on those components during the window, the flow posts the card at the top of the incident.
- **Stages:** plan, release, monitor, govern.
- **Autonomy:** Assisted. People act at every step that matters (the expert answers, the release manager decides); the agent's job is to ask the right person the right questions in time.
- **Model may / may not; code decides:** The model may decide which parts of the release depend on one person, write the questions, judge whether an answer covers the risk, and ask one follow-up. It may not move or block a release, contact anyone outside the project, or nag more than twice. Code decides availability from status and dates, and whether every flagged piece has an answered card.
- **30-second demo moment:** The interview thread: "If 0042 stalls halfway, is it safe to run it again?" and Ana's reply, "No. Run `fix_partial.sql` first." Cut to 02:00: the incident opens with her card on top and the on-call engineer follows it.
- **Nearest crowded space:** Onboarding aids and organizational memory (LORE, the February grand prize). Difference: it is set off by one release and one absence, asks a handful of targeted questions, and puts the answers into the incident path for that release window. It is not a knowledge base.
- **Biggest feasibility risk:** Reading user status from inside a flow (unverified), and a convincing interview needs a second real account to play Ana. Judging whether an answer is "good enough" is soft.

### 2.2 Return Ticket

- **Pitch:** Every release carries a proven way back; when it cannot, the agent shows exactly what is one-way, offers to split it, and a person signs for the one-way trip.
- **Person and moment:** Wei is the release manager, and his worst night was a rollback that crashed because the schema had already moved on. Now each release candidate shows either a green return ticket (rehearsed: old code runs on the new schema, and the down migration restores the data) or a red one-way door with the exact line, plus a merge request that splits the change so tonight's deploy stays reversible.
- **Flow:**
  1. Verify: when a release MR is marked ready (Merge request trigger, a person's action), the flow decides where irreversibility could hide: schema migrations, data backfills, message and cache formats, removed API fields, and side effects such as emails or payments sent on deploy.
  2. Code rehearses what can be rehearsed: in CI, a Postgres service with seeded demo data runs the new migrations, then the previous release's tests against the new schema, then the down migrations, and compares schema and row checksums.
  3. Govern: for one-way effects the model finds outside migrations (for example a deploy hook that emails every user), it records a finding with file and line. Code requires a named sign-off for each (MR approval rule or manual job).
  4. Create: where it can, the flow proposes an expand-and-contract split as a new MR (keep the column now, add a compatibility shim, drop it in a later release). A person reviews it.
  5. Release: the GitLab release records the ticket: "reversible", or "one-way, signed by Wei, with the reason".
- **Stages:** create, verify, release, govern.
- **Autonomy:** Supervised. The agent delivers the full verdict and the split MR; a person approves the outcome.
- **Model may / may not; code decides:** The model may search for one-way effects and write the split. It may not call a release reversible without the rehearsal, approve its own split, or stop a release (the person decides). Code decides the rehearsal results: old tests pass on the new schema, and down migrations restore the checksums.
- **30-second demo moment:** The release page shows a red ticket: "ONE-WAY: 0042_drop_legacy_email, line 12. v1.7 fails 14 of 40 tests on the new schema." Below it: "Split proposal !61: keep the column, drop it in v1.9." Wei merges the split, the pipeline reruns, and the ticket turns green.
- **Nearest crowded space:** Release gatekeepers and rollback rehearsal (BABYDOV Release Sentinel). Difference: it does not gate on tests or scans and does not roll back. It answers one question few tools automate, "can we come back?", by running old code against the new schema, and it rewrites the release so the answer becomes yes.
- **Biggest feasibility risk:** Building the rehearsal (old code on the new schema, down migrations, checksums) for even a small app, plus a believable schema history. ORM details can eat days.

### 2.3 Promise Kept

- **Pitch:** When a fix is live for the customer who reported the problem, the agent drafts a personal note to them, and a support person sends it.
- **Person and moment:** Mrs. Okafor runs a small bakery, and three weeks ago she wrote that the export button lost her orders; support replied "we'll let you know". On Tuesday she gets an email that quotes her own words, says the export is fixed for her account as of today, and thanks her for the clear report, and she forwards it to her sister: "they actually remembered."
- **Flow:**
  1. Plan: customer emails arrive through Service Desk and become issues. Most are never linked to the MR that fixes them.
  2. Release: when a deployment to `production` finishes (pipeline event on the deploy pipeline, started by a person's merge), the flow reads the shipped MRs and decides which Service Desk issues, open or closed, describe the same problem (symptoms, error text, dates, the feature), including ones nobody linked.
  3. Configure: code checks each match. Is the fix deployed in the environment that serves this customer (deployments API)? If the fix sits behind a feature flag, is the flag on for this customer (flag strategy or user list)? Only "live for this customer" goes on.
  4. The flow drafts a reply per customer, in their language and in their words, quoting their report and saying what changed for them, and posts it as an internal note on the Service Desk issue.
  5. A support person reads each draft and sends it as a public reply, which Service Desk emails to the customer. The flow then links the issue to the MR and closes it.
- **Stages:** plan, release, configure.
- **Autonomy:** Assisted. Every message is read and sent by a person; the agent does the finding, checking and drafting.
- **Model may / may not; code decides:** The model may decide which tickets match a fix and write the reply. It may not send anything, promise more than the shipped MR does, or reply when the fix is not live for that customer. Code decides deployment and flag state for that customer, and who has already been told.
- **30-second demo moment:** The support queue shows "4 customers can be told today", two of them never linked by anyone. She reads Mrs. Okafor's draft, presses send, and the email lands in an inbox.
- **Nearest crowded space:** Release notes writers, and Proof of Fix. Difference: it writes to one person about their own report, not to everyone about a release, and it checks only whether the fix is deployed and switched on for that customer, never whether production logs show the fix working.
- **Biggest feasibility risk:** Service Desk needs incoming email set up and GitLab's mailer to deliver replies (Maintainer setup, unverified). The demo needs realistic tickets, clearly labelled as demo data.

### 2.4 No Mouse

- **Pitch:** Before a release reaches production, an agent with no mouse and no screen must buy something on staging using only the keyboard and what a screen reader would announce.
- **Person and moment:** Maria is blind and has bought her coffee beans from this shop every month for four years with a screen reader. After Friday's redesign the agent tries her purchase on staging, hears "button, button, button" where Pay used to be, and holds the release; the developer listens to the recording of what Maria would have heard, winces, and fixes the label in ten minutes.
- **Flow:**
  1. Verify: when staging is deployed after a person's merge (pipeline event "passed"), the flow starts with a goal: complete the core journeys (find a product, add it to the cart, pay with the test card) by keyboard only.
  2. The model drives. After each key press (Tab, Enter, arrows, typing), a small Playwright helper it calls with `run_command` returns the focused element's role, name and state, and the announcement a screen reader would make. The model decides the next key, the way a screen reader user would.
  3. Code decides success: an order exists in staging (or the confirmation page is reached) within a step budget, and axe-core rules pass on each page visited.
  4. Release: on failure, the flow opens an issue with the transcript of what was announced (plus an optional text-to-speech audio file), the exact element and a suggested fix, and the production deploy job stays blocked until a fix lands or a person records an override with a reason (manual job).
  5. Plan: on success, the flow posts the transcript on the MR ("Maria's path: 38 key presses").
- **Stages:** plan, verify, release.
- **Autonomy:** Hands-off. It runs on every staging deploy with nobody watching, and its only power is to hold a release, which is the safe direction. A person decides any override.
- **Model may / may not; code decides:** The model may choose keys and paths, decide when it is stuck, and describe the barrier. It may not use the mouse or look at screenshots (the helper exposes only the keyboard and the accessibility tree), change code, or lift the hold. Code decides whether the order was placed, the step budget and the axe-core results.
- **30-second demo moment:** A black screen while text-to-speech plays "Link. Link. Button. Button. Button." Caption: "This is what Maria hears at checkout after Friday's redesign." The fix lands, and the audio says "Pay now, button."
- **Nearest crowded space:** Post-deploy smoke tests and verification. Difference: the check is a model walking a real disabled customer's journey with only assistive technology signals, not a health probe; a failure is a human barrier, not an error rate.
- **Biggest feasibility risk:** Running a browser inside a Duo flow session (an image with Playwright and browsers, the staging host on the network allowlist; unverified), and the time and cost of 40 or more tool calls per journey.

### 2.5 Fine Print

- **Pitch:** For every dependency upgrade, the agent reads the changelogs nobody reads, finds the lines that touch our code, and proves each one with a test before anyone merges.
- **Person and moment:** Elif maintains a small open-source booking service on weekends, and 23 dependency merge requests sit open because any one of them might be the one that breaks production. On Saturday morning she finds 21 of them marked "read 9 changelogs, nothing touches us, proven by 4 tests" and two with a failing test that shows exactly what would have broken, plus the fix, and she merges all 23 before her coffee is cold.
- **Flow:**
  1. Elif assigns the flow as reviewer on a dependency MR (Assign reviewer trigger). A bot (Renovate or dependency scanning) opened the MR, but a bot cannot start a flow, so her click does.
  2. Package: the flow reads the lockfile diff, fetches release notes and changelogs for every changed package including transitive ones (allowlisted hosts such as PyPI and GitHub releases), and decides which items could touch our use by searching our code for the APIs, defaults and behaviours each item mentions.
  3. Create: for each relevant item it writes a small pinning test (for example "outgoing requests time out after 30 seconds") and commits it to the MR branch.
  4. Verify: code decides. CI runs the new tests on the old lockfile (they must pass) and on the new lockfile. Pass on old and fail on new is proof of a real break; pass on both is proof we are safe on that point.
  5. Secure: the flow posts the verdict on the MR, with a fix commit when a break is proven. Elif approves and merges.
- **Stages:** create, verify, secure, package.
- **Autonomy:** Supervised. The agent delivers a finished verdict with proof; a person approves the merge.
- **Model may / may not; code decides:** The model may choose which changelog items matter, search our code, and write tests and a fix. It may not merge, delete or weaken existing tests, or call something safe without a test. Code decides the old versus new test results.
- **30-second demo moment:** The MR comment: a table of 14 packages with one red row, `paylib 2.4: default timeout is now 5 s (was 30 s)` (demo package), the failing test output beside it, then a green pipeline after the fix commit.
- **Nearest crowded space:** Security review and auto-fix of dependencies, and CI failure fixers. Difference: it is about behaviour changes, not vulnerabilities, and it proves impact with tests before anything turns red, instead of repairing a red pipeline.
- **Biggest feasibility risk:** Fetching changelogs from outside GitLab depends on the network allowlist (strict mode, unverified). Running tests on two lockfiles doubles CI time, and the demo needs a believable breaking change.

### 2.6 Lifeboat

- **Pitch:** Before the registry cleanup runs, the agent makes sure every image someone might need to roll back to at 3am is kept, and only then lets the cleanup delete the rest.
- **Person and moment:** Last spring Owen tried to roll back at 03:20 and found that last week's image had been deleted by the cleanup policy two hours earlier, and he still remembers the cold feeling in his stomach. Now each night the agent posts "kept 6 lifeboats, cleanup removed 214 images", and when Owen rolls back, the image is there.
- **Flow:**
  1. Package: a nightly pipeline from a person-owned schedule runs before the container registry cleanup and lists what the cleanup policy would delete (code).
  2. Monitor: the flow (pipeline event) decides what else might still be needed beyond the rules. It reads production and staging deployments, Cloud Run revisions that hold or recently held traffic, open incidents and MRs, and release pages and support issues that mention a version ("customer X is pinned to v1.6").
  3. Code decides the keep set: everything deployed now, or in the last N releases per environment, is kept by rule (protected tag, or a re-tag such as `lifeboat-v1.7.3`). The model's extra keeps are added with a reason. The model can add keeps, never remove one.
  4. Configure: cleanup runs on the rest and the flow posts a one-line report on the ops issue. Each week, if the same pattern keeps needing rescue, it opens an MR to change the cleanup policy (a person approves).
  5. Release: the rollback manual job in `production` uses the lifeboat tags.
- **Stages:** package, release, configure, monitor, govern.
- **Autonomy:** Hands-off. It runs every night with nobody watching, and its only power on its own is to keep things, which is the safe direction; policy changes go through an MR.
- **Model may / may not; code decides:** The model may find extra reasons to keep an image and propose policy changes. It may not delete anything or remove a keep made by rule. Code decides what is deployed, what the policy would delete, and the protection.
- **30-second demo moment:** Two columns on screen, "Cleanup wanted to delete 220" and "Lifeboat kept 6", with one row lit: `v1.7.3, running in production, Cloud Run revision 41`. Cut to 03:20: the rollback job finds the image and goes green.
- **Nearest crowded space:** Release gatekeepers that roll back. Difference: it guards the package stage (what exists to roll back to), not the decision to roll back.
- **Biggest feasibility risk:** Cleanup policies and protected tags may need Maintainer (unverified for our role). The model's share is thin unless the search for references a rule would miss visibly finds something, and the human moment is a non-event, so the video must show the counterfactual.

### 2.7 Kill Switch

- **Pitch:** Before a risky change reaches production, the agent wraps it in a feature flag, ties that flag to the alert that would catch it, and writes the one-line runbook entry, so at 3am the fix is one switch, not a rollback.
- **Person and moment:** Hana is on call when the new recommendations widget starts timing out at 03:00, and the last time this happened the only option was a full rollback that also undid a payments fix. This time the page itself says "Turn off `reco_widget` (kill switch added in !72, tested on staging)", she taps it, and she is back asleep in four minutes.
- **Flow:**
  1. Create: when the author marks an MR ready (Merge request trigger, a person's action), the flow decides whether the change adds a risky runtime path with no off switch: a new outside call, a new background job, a heavy query, a new widget on a busy page.
  2. Configure: if so, it commits to the MR a GitLab feature flag check around that path with a safe default, the flag definition for each environment, an alert rule in the alerts-as-code file on the signal that path would break, and a runbook line that links the alert to the flag.
  3. Verify: code proves the switch is safe. CI runs the test suite with the flag off and on, and on staging toggles the flag and checks that the path stops.
  4. Release: the author and the on-call reviewer approve the MR, and the release goes out as normal.
  5. Monitor: when that alert fires in production, the incident opens with the kill switch as its first line. Hana flips it (her action); the flow records a timeline event and opens a "turn it back on" follow-up issue for daytime.
- **Stages:** create, verify, release, configure, monitor.
- **Autonomy:** Supervised. The agent writes the switch, the alert and the runbook line; people approve the result in the MR.
- **Model may / may not; code decides:** The model may decide which paths need a switch and write the code, the alert and the runbook line. It may not merge, flip a production flag, or change behaviour when the flag is on. Code decides that the flag-off path passes the tests, that the flag exists in every environment, and that the alert links to it.
- **30-second demo moment:** The 03:00 page with its first line, "Kill switch: `reco_widget`. Tap to turn off." Hana's thumb, the latency graph dropping, and her hand turning off the lamp.
- **Nearest crowded space:** Pre-merge "what could this break" reports and code review agents. Difference: it does not comment or score; it builds the escape hatch (flag, alert, runbook line) and proves the off state is safe.
- **Biggest feasibility risk:** Editing application code reliably to add flag checks (a refactor that can itself break things), and wiring the demo app to GitLab feature flags (the Unleash client) from scratch.

### 2.8 Log Leak

- **Pitch:** After each release, the agent finds the log lines the release added, checks real production logs for personal data in them, and asks a person to approve the redaction and the cleanup.
- **Person and moment:** Jonas, the privacy lead, usually learns about personal data in logs months later, from an auditor. This time, an hour after v2.4 ships, he gets a confidential issue ("The new retry log line in checkout prints the customer's email: 1,214 entries since 14:02. Here is the redaction MR and the cleanup job"), and he approves both before lunch.
- **Flow:**
  1. Release: when a production deployment finishes (pipeline event, started by a person's merge), the flow reads the release diff and decides which new or changed log statements could carry personal data (fields like email, address, token, request bodies).
  2. Monitor: it queries production logs (Cloud Logging, or GitLab Observability logs through the MCP server) for entries from those statements since the deploy, choosing its own filters.
  3. Secure: code decides. A deterministic detector (patterns, or Google Sensitive Data Protection) runs on the samples, counts exposures, and masks everything before the flow sees or posts it.
  4. Create: the flow opens a confidential issue with counts and masked examples, an MR with the redaction and a test that the line no longer contains the pattern, and a manual cleanup job (an exclusion filter and shorter retention for the affected log bucket).
  5. Govern: the privacy lead approves the MR and runs the cleanup job. The flow records on the issue what was exposed, for how long, and to whom (the readers of that log bucket).
- **Stages:** create, release, secure, monitor, govern.
- **Autonomy:** Supervised. The agent finds, confirms and prepares; a person approves the redaction and the cleanup.
- **Model may / may not; code decides:** The model may choose which log lines to check and how to query, and write the redaction. It may not delete logs, see or post unmasked data (code masks first), or merge. Code decides whether personal data is present, the counts and the masking.
- **30-second demo moment:** The confidential issue: `checkout retry for j***@g***.com`, 1,214 entries since 14:02 (v2.4), then the merged redaction, and a fresh query showing zero new entries.
- **Nearest crowded space:** Security review on MRs (SAST), and Proof of Fix (which also reads production logs after a merge). Difference from Proof of Fix: same mechanism, a different question (personal data, not fix confirmation). Difference from SAST: it looks at what production actually logged after release, and its action is a privacy cleanup with a named approver.
- **Biggest feasibility risk:** Cloud Logging does not easily delete single entries, so the cleanup is probably an exclusion filter and retention change, not deletion (unverified). Flow access to Cloud Logging through `id_tokens` is also unverified, and the demo must plant a believable leak with fake data.

---

## Summary

| # | Lens | Name | Person | Stages | Autonomy |
|---|---|---|---|---|---|
| 1.1 | On-call | Night Orders | On-call engineer going to sleep | plan, release, configure, monitor, govern | Hands-off |
| 1.2 | On-call | Dress Rehearsal | On-call engineer just woken | verify, release, configure, monitor | Assisted |
| 1.3 | On-call | Watermelon | Customer writing in at night; on-call engineer | plan, verify, configure, monitor | Supervised |
| 1.4 | On-call | Loose Ends | Engineer who mitigated at 3am; next shift | plan, release, configure, monitor, govern | Supervised |
| 1.5 | On-call | Sleep Debt | Engineer woken by noise; team lead | verify, configure, monitor, govern | Supervised |
| 1.6 | On-call | Fire Drill | New hire before the first shift | plan, create, verify, configure, monitor | Supervised |
| 1.7 | On-call | Someone Awake | Teammate in another time zone | plan, monitor | Supervised |
| 1.8 | On-call | Daylight Rollout | Product manager; on-call engineer | plan, release, configure, monitor | Hands-off |
| 2.1 | Inversion | Plane Mode | Expert about to travel; release manager | plan, release, monitor, govern | Assisted |
| 2.2 | Inversion | Return Ticket | Release manager | create, verify, release, govern | Supervised |
| 2.3 | Inversion | Promise Kept | Customer who reported a bug; support person | plan, release, configure | Assisted |
| 2.4 | Inversion | No Mouse | Blind customer; developer | plan, verify, release | Hands-off |
| 2.5 | Inversion | Fine Print | Weekend open-source maintainer | create, verify, secure, package | Supervised |
| 2.6 | Inversion | Lifeboat | On-call engineer who needs to roll back | package, release, configure, monitor, govern | Hands-off |
| 2.7 | Inversion | Kill Switch | On-call engineer at 3am; change author | create, verify, release, configure, monitor | Supervised |
| 2.8 | Inversion | Log Leak | Privacy lead; customers in the logs | create, release, secure, monitor, govern | Supervised |

Range, without judging: 3 Assisted, 9 Supervised, 4 Hands-off. All nine stages appear at least once (package in Lifeboat and Fine Print, secure in Fine Print and Log Leak). Five concepts depend on starting a flow with nobody awake (see Shared mechanics, point 2), which is the main shared feasibility question to test first.
