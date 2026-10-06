# Ideas from two lenses: biology, and removing the load-bearing assumption

Generated 2026-10-06 as input for Part 5 (docs/IDEAS.md). This file only generates ideas: nothing here is scored or ranked. Inputs: [IDEATION_BRIEF.md](../IDEATION_BRIEF.md), [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md), [field/code_hosts.md](../field/code_hosts.md), [field/social.md](../field/social.md). No web search was used. Every concept name was checked against the entries named in the research files and against the parallel lens file [lens_oncall_inversion.md](lens_oncall_inversion.md).

Two lenses:

1. **Biology.** Map a mechanism (what the body actually does, step by step) onto the post-code lifecycle, not just a name.
2. **Remove the load-bearing assumption.** List what the lifecycle silently relies on, take each one away, and design what follows.

20 full concepts (11 biology, 9 assumption), plus short sketches, an overlap table with the parallel lens file, and natural combinations at the end.

## Index

| # | Name | Lens | Person | Stages | Autonomy |
|---|---|---|---|---|---|
| B1 | Quorum | biology (quorum sensing) | support agent, and the customers who wrote in | monitor, plan, configure, release | Supervised |
| B2 | Night Nurse | biology (emergency triage) | on-call engineer, asleep | monitor, plan, govern | Hands-off |
| B3 | Thymus | biology (immune selection) | SRE writing an alert rule | monitor, verify, configure, govern | Supervised |
| B4 | Booster | biology (vaccines) | junior engineer before first on-call week | plan, configure, release, monitor | Assisted |
| B5 | Fever | biology (homeostasis) | senior developer after a bad week | govern, release, configure, monitor | Supervised, then Hands-off |
| B6 | Scar Tissue | biology (wound healing) | engineer who pushed a 3 a.m. hotfix | monitor, plan, create, verify, release | Supervised |
| B7 | Apoptosis | biology (programmed cell death) | developer who created a flag and forgot it | configure, create, verify, release, govern | Supervised |
| B8 | Placebo | biology (placebo effect) | runbook owner, and everyone woken by a ritual | monitor, plan, configure, govern | Assisted |
| B9 | Mutualist | biology (symbiosis) | open source maintainer, and the app developer | plan, create, verify, package, release | Supervised |
| B10 | Wince | biology (pain as a signal) | developer who keeps clicking Retry | verify, create, plan, govern | Supervised |
| B11 | Night Replay | biology (sleep and memory) | engineer who corrected the agent | govern, plan | Assisted |
| A1 | Last Day | assumption: the person who set it up is still here | engineer leaving, and her successor | govern, configure, release, monitor, secure, plan | Assisted |
| A2 | Front Row | assumption: the release goes to everyone at once | small business owner who reported a bug | plan, release, configure, monitor | Supervised |
| A3 | Landing Window | assumption: the developer decides when to ship | developer at 17:40 Friday, on-call engineer abroad | release, govern, configure, monitor | Supervised |
| A4 | Writeback | assumption: production only changes through the pipeline | on-call engineer who fixed prod by hand | monitor, create, verify, release, configure, govern | Supervised |
| A5 | Teach Back | assumption: the approver understands what they approve | release approver at 18:00 | release, govern, verify | Assisted |
| A6 | Learner Permit | assumption: agent autonomy is set once in config | SRE deciding what the agent may do alone | monitor, release, configure, govern | Hands-off, earned per action |
| A7 | Postcard | assumption: deploy is the end of the story | developer who never hears how her feature did | monitor, release, configure, plan | Hands-off report, Assisted follow-up |
| A8 | Auditor Hour | assumption: evidence is gathered when the auditor asks | engineering lead facing a SOC 2 audit | govern, release, verify, secure | Supervised |
| A9 | Sunset | assumption: deprecation notices work | external integrator, and the API owner | monitor, plan, create, package, release, govern | Supervised |

## Ground rules every concept follows

- The model chooses where to look and what to try. Code decides what is true (counts, thresholds, diffs, test results, who owns what). A human decides when anything that matters happens.
- A rule that came out of both lenses: **an agent may act alone only toward safety** (pause, hold, wake someone, raise the guard, demote itself, return to a baseline a person wrote). Anything toward risk (ship, widen a rollout, delete, lower the guard, promote itself) needs a human yes.
- "Code decides" means small scripts in the repo. A flow runs them with `run_command` in its repo clone, or a CI job runs them, and the model must quote their output. Where possible the script runs as a `DeterministicStepComponent` so the model cannot skip it (unverified that `run_command` works there).
- Starting flows: only a human action fires a Duo trigger. Each concept either rides on a human action that already happens (a support agent triaging, a manager assigning, a developer merging, a reply that mentions the flow) or starts from a non-human event through a small Cloud Run relay that calls the Flows API (`POST /api/v4/ai/duo_workflows/workflows`) with a personal token kept in Google Secret Manager. The relay path is unverified.
- Human approval in GitLab terms: a reply that mentions the flow's service account ("go"), a work item status change, a merge, a manual CI job, or a protected environment deployment approval. `HumanInputComponent` in a triggered ambient flow is unverified, so no concept depends on it.
- Writes outside issues, MRs and commits (feature flags, deployments, Google Cloud) run as CI jobs that a human action starts, because the flow token's `ai_workflows` scope may not reach those APIs, and CI write tokens may need Maintainer to store (both unverified).

## Lens 1: Biology

### Banned: the three most obvious answers

1. **Self-healing pipeline.** A pipeline or deployment that notices its own failure and repairs or rolls itself back ("wound healing" for CI, "regeneration"). Close variants also banned: auto-rollback on a failed health check, CI failure fixers described as healing.
2. **Immune-system security scanner.** Agents as white blood cells or antibodies that find and neutralize vulnerabilities, or that "vaccinate" dependencies against CVEs.
3. **Organism health dashboard.** A "vital signs" or yearly check-up view of the repo or service, with a heartbeat and a health score.

### B1. Quorum

- **Pitch:** When several users describe the same problem in different words, the agent sees that it is one problem, ties it to the change that caused it, and asks a human to pause that change for the people it reached.
- **Mechanism mapped:** In quorum sensing, each bacterium releases a small signal molecule. One cell's signal does nothing; when the concentration from many independent cells passes a threshold, the whole colony switches behavior at once. The threshold stops the colony from acting before there are enough cells for the action to work. Here each support ticket, error event or failed check is a signal; the model decides which signals carry the same "molecule" (one underlying problem); code counts independent reporters in a time window; crossing the threshold switches the project's state together: an incident opens, a pause is proposed for the affected cohort, and every reporter gets an answer. One angry email cannot pause anything.
- **Person and moment:** Maya works support, and on Tuesday afternoon three customers write "the pay button does nothing", "stuck on checkout in Safari" and "was I charged twice?", each looking like a one-off. A note on the third ticket says all three, plus 41 error events, come from the 20% of users who got the new checkout that morning and asks whether to pause it for them; she says yes, and each customer gets an email that afternoon saying they were heard and what was done.
- **Flow:**
  1. Customer emails become confidential issues through **Service Desk**. Maya's normal triage step (setting the work item status to "Triaged") starts the Quorum **Duo custom flow** through a **work item status-changed trigger**.
  2. The flow reads the ticket, then searches recent Service Desk issues, **error tracking** events, **feature flags** and recent **production deployments** to decide which problem the ticket belongs to (the model chooses where to look). It writes the signature as a note.
  3. A script counts independent reporters per signature in a sliding window and checks, from the flag's strategy, whether the affected user IDs fall in the new cohort (code decides).
  4. At the threshold, the flow opens an **incident** linking every signal and proposes one action: set the flag to 0% for that cohort. It mentions the on-call person.
  5. The on-call person replies "pause", mentioning the flow (**mention trigger**); a **manual CI job** changes the flag through the Feature Flags API and reads it back.
  6. The flow replies on each Service Desk issue, which GitLab emails to the customer: "You were one of three people who told us. We switched you back to the old checkout at 14:32. We will write again when the fix is out."
- **Stages:** monitor, plan, configure, release.
- **Autonomy:** Supervised. The agent builds the case and proposes; a human approves the outcome. Because a pause moves toward safety and is reversible, a team could pre-approve it and run that one step Hands-off.
- **Model may / may not / code decides:** May read tickets, errors, flags and deploys, group tickets by meaning, write the proposal and the replies. May not change a flag, close a ticket, or tell a customer something was done before code has confirmed it. Code decides the reporter count, the threshold, cohort membership, and whether the flag change took effect.
- **30-second demo:** Three emails in three different wordings arrive. On screen they link one by one to a single incident while a counter goes 1, 2, 3 and crosses the line. Maya types "pause". Cut to three inboxes, each with a reply.
- **Nearest crowded space:** issue triage (81 projects in Feb) and post-deploy rollback gatekeepers. Difference: it does not sort a backlog or judge a deploy by health checks; it waits for independent people to agree, acts only on the cohort that got the change, and answers each person by email.
- **Biggest risk:** Writing to the Feature Flags API and the Service Desk email round trip in the hackathon project are both unverified; the fallback is a manual CI job for the flag and test mailboxes for the customers.

### B2. Night Nurse

- **Pitch:** At night, an agent sorts every alert the way a triage nurse sorts patients, and wakes the on-call engineer only when the team's own rules say so; everything else waits for morning with the evidence already gathered.
- **Mechanism mapped:** In START triage, an officer who treats nobody sorts each patient in under a minute by a few hard vital signs (breathing, pulse, can they walk), ties on a colored tag that travels with the patient, and re-triages on a schedule because patients get worse. The walking wounded sort themselves ("if you can walk, go over there"). Here the vital signs are deterministic checks the team writes (share of requests failing, error budget burn, failed writes, users affected) and code sets the tag: red (wake now), yellow (wake if it worsens), green (morning), black (known noise already tracked in an issue). An alert that clears by itself within 5 minutes sorts itself green. The model takes the history, like the nurse: recent deploys, flag changes, similar past incidents. It may raise a tag with a written reason; it may never lower a tag below what the vital signs say. Re-triage runs every 10 minutes, and the tag (a scoped label) goes with the alert into the morning hand-off.
- **Person and moment:** At 03:12 a latency alert fires and Bilal, on call, sleeps on because the vital signs say green (0.3% of requests, no errors, the nightly batch running), while at 04:40 a different alert crosses red and his phone wakes him with a page that already holds the last deploy, the flag that changed and a similar incident from June. At 07:30 he reads a five-line hand-off for the alert he slept through: what fired, what was checked, why he was not woken, and what would have changed that.
- **Flow:**
  1. **Cloud Monitoring** (watching the app on **Cloud Run**) calls a small Cloud Run relay, which creates a GitLab **alert** through the **HTTP endpoint integration** (and an **incident** for anything above green) and starts the **Duo custom flow** through the **Flows API**, since a non-human event cannot fire a trigger.
  2. A script computes the vital signs from metrics and sets the starting tag as a scoped label (code).
  3. The flow takes the history from **deployments**, **feature flags**, past **incidents** and open issues, writes a short summary on the alert or incident, and may propose an upgrade with evidence.
  4. Red pages the on-call person through the **on-call schedule and escalation policy**; the relay re-runs triage every 10 minutes.
  5. In the morning the flow posts a hand-off note on each overnight item and assigns it to the day shift.
- **Stages:** monitor, plan, govern (the vital-sign rules live in the repo and change only by **merge request**).
- **Autonomy:** Hands-off. It runs the whole night alone because it never touches production and can only add urgency. People own the vital-sign rules through MRs, and every action on production belongs to the person it wakes.
- **Model may / may not / code decides:** May gather context, write the history, raise a tag with a reason. May not lower a tag, hold back a page the vital signs require, or act on production. Code decides the vital signs, the starting tag, the floor, and whether a page went out.
- **30-second demo:** Split screen: a dark phone on a bedside table, and the alert stream. Three alerts arrive; two get green and yellow labels and the phone stays dark; the third crosses red and the phone lights up with a page that already has the deploy, the flag and June's incident. The clock jumps to 07:30 and the hand-off appears.
- **Nearest crowded space:** incident root cause and post-mortems (56 in Feb; Praetor, Backtrace, AFTERMATH in June) and auto-remediation bots. Difference: it finds no causes and fixes nothing; it decides who is woken and when, under a rule that the model can only add urgency, and it hands the night to the morning.
- **Biggest risk:** The whole night depends on starting flows from non-human alerts through the Flows API (unverified), and each session takes 1 to 3 minutes to start; GitLab paging needs Premium on-call schedules set up by a Maintainer, so a fallback pager may be needed.

### B3. Thymus

- **Pitch:** Before a new alert rule may page anyone, it is tested against the team's own history: it must have caught the real incidents and stayed quiet on normal days. The agent proposes better variants and a human picks one.
- **Mechanism mapped:** Young T cells are tested in the thymus. Cells that react to the body's own proteins are deleted (negative selection), cells that recognize nothing useful die too (positive selection), and only cells that ignore "self" but can bind foreign targets are released. B cells add affinity maturation: their receptors mutate, and the strongest binders are kept. Here an alert rule is the receptor. "Self" is labelled normal history (deploy days, the nightly batch, Monday peaks); "foreign" is past real incidents. Code replays each rule against both: rules that fire on self are rejected, rules that miss real incidents are rejected. The model mutates: it proposes variants (threshold, window, burn-rate form, excluding the batch window) and explains each; code scores them; a human chooses.
- **Person and moment:** Hiro was paged 14 times last week, 11 of them for the nightly batch job, so when he opens an MR for a new checkout latency alert he half expects more of the same. Minutes later a comment shows his rule would have paged him 9 times last month on normal nights and caught 2 of 3 real incidents, next to a variant that would have paged 0 times and caught all 3; he picks it, merges, and his phone stays dark that weekend.
- **Flow:**
  1. Alert rules live as code in the repo (for example `alerts/*.yaml` for Cloud Monitoring policies). A human opens a **merge request** that adds or changes a rule; the **MR created trigger** starts the **Duo custom flow**.
  2. The flow decides what counts as self and foreign: it reads closed **incidents** (real ones and ones labelled false alarm), **deployment** history and **pipeline schedule** times, picks the replay windows, and commits them to the MR branch with reasons (the model chooses where to look).
  3. A **CI job** replays the rule and each variant against stored metric history and outputs pages-on-self and catches-of-foreign for each (code decides).
  4. The flow posts the table on the MR with a plain explanation and offers the variants as **suggestions**.
  5. The human applies one and merges; the main pipeline applies the alert config to the monitoring backend.
- **Stages:** monitor, verify, configure, govern.
- **Autonomy:** Supervised. The agent runs the whole selection loop; the human approves the rule that goes live.
- **Model may / may not / code decides:** May pick history windows, label them self or foreign with reasons, propose variants. May not change the scoring, relabel a real incident as noise without a visible reason, or merge. Code decides the backtest numbers.
- **30-second demo:** The MR comment: the original rule, "would have paged you 9 times on normal nights, caught 2 of 3", and variant B below it, "0 pages, caught 3 of 3". Hiro clicks Apply suggestion and merges.
- **Nearest crowded space:** none directly; it sits next to incident analysis and CI checks. Difference: it tests the alert rules themselves, at review time, before they can reach a person.
- **Biggest risk:** A believable backtest needs weeks of metrics and labelled incidents; for the demo that history must be recorded from a load generator over several days or generated and labelled as such, and applying alert policies from CI needs Google Cloud credentials (keyless WIF).

### B4. Booster

- **Pitch:** Before someone's on-call week, they get a safe practice page: a weakened replay, in staging, of a real past incident, so the first time they meet it is not at 3 a.m.
- **Mechanism mapped:** A vaccine shows the immune system a weakened or inactivated pathogen, so memory cells form without the disease. Memory fades, so boosters re-expose; vaccine makers pick the strains that are circulating. Here the pathogen is a real incident from the archive; weakening means replaying its failure mode only in staging, at low strength, with a time limit and a kill switch; memory forms in the person, not the code; a booster is due when someone has not met that kind of incident for some months; strain choice is the model picking the past incident most likely to come back, given what was merged since and what this person has already seen.
- **Person and moment:** Zoe starts on-call for the first time next Monday and is quietly afraid of it. On Thursday at 14:00 she accepts a practice page in which staging times out on the payment provider exactly as production did in March, and at 3 a.m. on Saturday, when the real thing starts, she recognizes it.
- **Flow:**
  1. A weekly **pipeline schedule** owned by the team lead (or the lead assigning the "drills" issue to the flow, **assign trigger**) starts the **Duo custom flow**.
  2. The flow reads the **on-call schedule** (who is next), closed **incidents** with their timelines and runbooks, and **merge requests** merged since the last drill, then chooses which incident to replay and why. It writes a drill plan as an issue: "weakened replay of incident #42 in staging: payment provider latency 3 s for 20 minutes".
  3. Zoe and the lead accept by setting the drill issue to "Scheduled" (**work item status-changed trigger**).
  4. At the agreed time, a **CI job** turns on a fault-injection **feature flag** scoped to the **staging environment** only (code checks the scope; production is impossible by construction) and opens a practice **incident** labelled drill that pages Zoe.
  5. The flow follows the practice incident and answers only when Zoe mentions it; a CI job turns the fault off at the time limit or when she resolves it.
  6. The flow writes a short "what you met" note, records person, incident type and date, and plans a booster in four months.
- **Stages:** plan, configure, release (staging), monitor.
- **Autonomy:** Assisted. The person who takes the drill accepts every drill, and anyone can stop it.
- **Model may / may not / code decides:** May choose the incident, write the plan and give hints. May not inject anything outside staging, start a drill without acceptance, or score the person in public. Code decides the environment scope, the duration and the kill switch.
- **30-second demo:** Zoe's phone: "PRACTICE PAGE: replay of incident #42". Staging graphs spike, she follows the runbook. Cut to "Saturday 03:04, production": the same graph shape, and her first note in the real incident: "Seen this. Runbook step 3."
- **Nearest crowded space:** incident post-mortem tools (crowded); chaos engineering (not crowded here). Difference: it does not analyze incidents; it uses them to prepare the next person, picks the drill for that person, keeps a memory record with boosters, and keeps every fault in staging behind consent.
- **Biggest risk:** Fault injection needs app code wired to flags plus a believable incident archive to draw from; paging through GitLab on-call schedules needs Premium setup, so the practice page may need a simpler channel.

### B5. Fever

- **Pitch:** When production is sick, the project raises its own guard for a while (more approvals, smaller rollout steps, a freeze on the risky area) and lowers it again by itself once the vital signs have been normal long enough.
- **Mechanism mapped:** Homeostasis holds the body at a set point by negative feedback. Fever is a controlled exception: during infection the hypothalamus raises the set point on purpose, the body works to reach it, and when the threat passes the set point returns and the body sheds the heat. Here the set point is the project's level of change control: deployment approvals required, rollout step size, freeze windows. A sensor in code (error budget burn, open high-severity incidents, failed deploys in a row) detects infection. The model proposes a specific fever: which controls, on which paths, for how long, and why. After the threat, code counts clean days and returns everything to the baseline the humans wrote, never lower.
- **Person and moment:** After a week with three incidents, Mateo, a senior developer, finds that his routine deploys need two approvals and roll out in 5% steps, and the note on each one tells him why. Eight days later he reads "Fever broke: 40 clean deploys, error budget recovered, your approvals are back to one", and he feels trusted again without anyone having to remember to undo the rules.
- **Flow:**
  1. A human declares an **incident** (**work item created trigger**), or a daily **pipeline schedule** finds the error budget burning too fast and opens one.
  2. The **Duo custom flow** reads recent incidents, **deployments** and the areas of code they touched, and proposes a fever as a **merge request** to `controls.yml` (governance as code): "production needs 2 approvals; flag rollouts in steps of at most 5%; freeze `payments/` for 7 days".
  3. A human merges. A **CI job** applies it: **protected environment** approval rules, a **deploy freeze**, the flag rollout policy.
  4. While the fever lasts, every held deploy carries a note with the reason.
  5. The daily schedule checks the vital signs (code). After N clean days the fever breaks: CI restores the human-written baseline and the flow posts the note.
- **Stages:** govern, release, configure, monitor.
- **Autonomy:** Supervised for the first fevers (a human merges each one). It can become Hands-off once the team trusts the policy, because both automatic moves (raise to a human-written fever level, return to the human-written baseline) go toward settings people chose.
- **Model may / may not / code decides:** May choose which controls to raise, on which paths, and explain why. May not go below the baseline, change who may approve, or extend a fever without a human. Code decides the vital signs, the clean-day count, the apply and the restore.
- **30-second demo:** The production deploy panel shows "2 approvals required (fever: incident #51)" next to an error-rate line that falls and then flattens. Fast-forward eight days: the panel flips back to "1 approval", and Mateo gets "Fever broke."
- **Nearest crowded space:** release gatekeepers that ship, hold or roll back each release (BABYDOV's "autonomy budget"). Difference: it never judges a release; it moves the team's own rules up and down with production's health and always brings them back.
- **Biggest risk:** Changing protected environment approvals and deploy freezes needs Maintainer rights and Premium features we may not have; the fallback is a gate job in our own CI that reads `controls.yml`, which shows less of GitLab.

### B6. Scar Tissue

- **Pitch:** Every emergency patch made during an incident is remembered, and once the wound is quiet the agent comes back with the proper fix for the person who made the patch to approve.
- **Mechanism mapped:** Wound healing runs in phases with gates between them: a fast, crude clot stops the bleeding; inflammation cleans up; new tissue grows; then, over weeks, remodeling replaces the provisional tissue with stronger, aligned tissue. Remodeling starts only once inflammation is over. Scars that are never remodeled stay stiff and weak, and many of them stiffen the whole organ (fibrosis). Here people make clots during incidents: a hotfix commit, a disabled check, `allow_failure: true`, a raised timeout, a pinned version, a flag forced off. The agent catalogues each clot as it happens. Code decides when inflammation is over (incident closed, metrics at baseline for 7 days). Then the agent remodels: an MR that replaces the clot with the proper fix, not just a revert. The count of clots never remodeled is the project's fibrosis.
- **Person and moment:** At 02:50 Ines pushed "temporary: raise DB timeout to 30s, will revisit" and went back to bed. Nine days later an MR arrives in her name with the timeout back to 5 s, an index on the slow query, proof that the wound has been quiet for a week and one line, "You said you'd revisit; here it is", and she approves it feeling the project kept her promise for her.
- **Flow:**
  1. During or right after an **incident**, a responder sets its status to "Mitigated" (**work item status-changed trigger**). The **Duo custom flow** reads the incident timeline and the commits, **merge requests**, CI config changes and **feature flag** changes made in the incident window, and decides which were clots (the model chooses where to look).
  2. It records each clot as a child task with its location, its author and its remodel condition.
  3. A daily **pipeline schedule** checks the condition (code: incident closed, metrics at baseline for N days, no related new incident).
  4. When it holds, the flow opens a draft MR that remodels the clot, runs the **pipeline**, and assigns it to the clot's author.
  5. The author approves and merges; the normal deploy runs; the task closes and the incident gets a "healed" note.
- **Stages:** monitor, plan, create, verify, release.
- **Autonomy:** Supervised. The agent does the remodeling; the human approves the result.
- **Model may / may not / code decides:** May decide what was a clot, write the remodel MR and explain it. May not touch anything during the inflammation phase, remodel a clot whose condition is not met, or merge. Code decides incident state, the baseline check and test results.
- **30-second demo:** A timeline: the 02:50 commit "temporary". Fast-forward to day nine: a draft MR appears with the timeout restored and the index added, the pipeline turns green, and the comment says "You said you'd revisit." Ines clicks Merge.
- **Nearest crowded space:** CI failure fixers and post-mortem follow-up (Feb's Incident Replay "creates tracked prevention work"). Difference: it does not analyze causes or repair pipelines; it tracks the shortcuts people took under pressure and returns, at a time code says is safe, to replace them properly.
- **Biggest risk:** Telling a clot from an ordinary change is fuzzy in real history, and writing the proper fix is hard in general; the demo needs a staged incident with clear temporary commits and a fix the agent can get right.

### B7. Apoptosis

- **Pitch:** Every feature flag must keep earning its life; when nothing gives it a reason to live, it asks once, and then removes itself in a clean MR that a human approves.
- **Mechanism mapped:** Many cells survive only while they keep receiving survival signals. When the signals stop, the default is apoptosis: an orderly self-dismantling that shows an "eat me" signal so cleaner cells remove it without inflammation, unlike necrosis, a messy death that inflames the tissue around it. Here a flag's survival signals are: it is partly rolled out, someone changed it recently, an open issue references it, or a person gave a written reason ("keep until the ACME migration in November"). Code measures the signals. With none for N days, the flag starts dying: it shows its "eat me" signal, a removal MR that deletes the flag checks and the dead code path. Clean death means tests pass and no reference is left (code checks). Necrosis is what happens today: someone deletes a flag in the UI and a forgotten code path breaks.
- **Person and moment:** Diego created the `new_export` flag in June and forgot it, the way everyone forgets flags. In October he gets "new_export has been on for everyone for 92 days and nobody has touched it; give me one reason to live by Friday or approve my removal", laughs, approves, and 140 lines of dead branches disappear.
- **Flow:**
  1. A weekly **pipeline schedule** starts the **Duo custom flow**. A script first collects survival signals from the **Feature Flags** API (strategies, environment scopes, last change), linked issues and code references.
  2. For flags with no signal, the flow posts a last call on the flag's issue and mentions the owner, with a deadline.
  3. The model reads replies; a written reason counts only if the flow can quote it, and any "keep" from a person wins.
  4. With no reason by the deadline, the flow writes the removal **merge request**: it decides from the flag's state which branch is dead, deletes the checks and the dead path, updates tests, and runs the **pipeline**.
  5. A human merges; after the **deployment**, a CI job deletes the flag and code confirms no references remain.
- **Stages:** configure, create, verify, release, govern.
- **Autonomy:** Supervised. Up to the MR the program runs alone; every removal needs a human merge. The last-call notices can run Hands-off.
- **Model may / may not / code decides:** May decide which path is dead, judge whether a reply is a real reason (quoting it), write the MR. May not delete a flag, merge, or overrule a person's "keep". Code decides the signals, references and tests.
- **30-second demo:** Nine flags, each with a survival meter. Four drain to zero, their owners get "give me one reason to live", one replies "keep, ACME in November", and three green MRs appear, each deleting 40 to 140 lines. One merge.
- **Nearest crowded space:** none in this hackathon (the configure stage is open); outside it, flag clean-up tools exist. Difference: the default is death unless something keeps the flag alive, and a person's written reason is a survival signal. The same program can retire idle preview environments, which could feed the environmental prize with measured savings.
- **Biggest risk:** Removing a dead code path is a real code edit that can go wrong; the demo app needs flags used in a clean, testable way, and flag writes from the flow token are unverified.

### B8. Placebo

- **Pitch:** The agent checks whether what the on-call team does during incidents actually works, by comparing with the times nobody did it, and retires the rituals that only seemed to help.
- **Mechanism mapped:** People seek treatment when symptoms are at their worst, and symptoms often ease on their own afterwards (regression to the mean), so whatever was done last gets the credit. Medicine answers with control groups and by looking at the trend before treatment. Here an alert fires at its peak, someone restarts the worker, the graph recovers, and "restart the worker" enters the runbook. The agent builds the control group from history: incidents of the same kind where nobody acted, or acted late. Code compares the trend before and after each action and the time to recover with and without it. The model decides which past incidents are the same kind and what the action really was, from timeline notes and job logs.
- **Person and moment:** For a year, every queue-lag alert has woken someone to restart the worker, and Marco wrote that step into the runbook himself. The agent shows that in 9 of 11 cases the lag was already falling when the restart happened and the 3 untreated cases cleared in 12 minutes on their own; Marco approves "wait 15 minutes, restart only if still rising", and nobody is woken for queue lag again.
- **Flow:**
  1. When a human sets an **incident** to Resolved (**work item status-changed trigger**), the **Duo custom flow** pulls out the actions taken, from **incident timeline events**, comments and linked **pipelines** and jobs (rollbacks, restarts, flag changes).
  2. It finds similar past incidents and builds treated and untreated groups, writing why each one belongs.
  3. A **CI job** pulls the metric series around each action and computes the slope before the action and the time to recovery, treated against untreated (code decides).
  4. When an action shows no effect over enough cases (a threshold in code), the flow opens a **merge request** to the runbook and to the alert's routing (page after 15 minutes for this alert), with the evidence table.
  5. The runbook owner approves and merges.
- **Stages:** monitor, plan, configure, govern.
- **Autonomy:** Assisted. Each runbook change is a person's call; the evidence is offered, not imposed.
- **Model may / may not / code decides:** May pick comparable incidents and name the actions, write the MR. May not call an action useless with fewer cases than the code threshold, or change routing itself. Code decides the statistics.
- **30-second demo:** Eleven incident curves aligned at the moment of the restart: in nine, the line is already bending down before it. A gray band shows untreated cases recovering in 12 minutes. The MR "Runbook: wait 15 minutes before restarting" is approved.
- **Nearest crowded space:** incident root cause and post-mortems. Difference: it does not ask why incidents happen; it asks whether the team's remedies work.
- **Biggest risk:** It needs many past incidents with timestamps and metrics; the demo history must be generated and labelled as such, and the statistics must stay simple enough to be honest with small numbers.

### B9. Mutualist

- **Pitch:** When your app has to work around a bug in a library, the agent gives the library's maintainers a clean report with a minimal reproduction, watches for their fix, and when it ships, opens the MR that upgrades and deletes your workaround.
- **Mechanism mapped:** In mutualism each partner supplies what the other cannot make: nitrogen-fixing bacteria give the plant nitrogen, the plant gives them sugar. Plants also sanction partners that stop giving: legumes cut the oxygen to root nodules that fix no nitrogen. Here a workaround in your code is a debt to an upstream project. The agent pays it with what maintainers lack (a minimal reproduction and a failing test), and you get what you lack (their fix). Sanctions: the agent keeps a ledger per dependency (reports sent, time to fix, releases), and when a partner stops giving it proposes alternatives to the humans.
- **Person and moment:** Rui maintains a small date-parsing library in his spare time and receives an issue with a 12-line reproduction and a failing test, approved by a human, which he fixes in a day. Three weeks later Kai, the app developer, finds an MR that bumps the version and deletes the ugly workaround he wrote in August.
- **Flow:**
  1. A developer labels an issue `upstream-bug` and mentions the flow (**mention trigger**), pointing at the workaround.
  2. The **Duo custom flow** reads the workaround and the library's source in its repo clone, builds a minimal reproduction, and a **CI job** proves it fails on the pinned version (code).
  3. It drafts the upstream report in the issue; a human approves ("send") before anything is posted to another project.
  4. A **pipeline schedule** checks new upstream releases (registry metadata through the flow's allowed domains, or the upstream project's **releases** API) and runs the reproduction against each one (code decides when it is fixed).
  5. When fixed, the flow opens a **merge request** that bumps the dependency and deletes the workaround; the pipeline runs; a human merges; the normal **release** follows.
- **Stages:** plan, create, verify, package, release.
- **Autonomy:** Supervised. Posting to someone else's project and changing a dependency both need a human yes.
- **Model may / may not / code decides:** May build the reproduction, write the report and the MR. May not post outside the project without approval, or claim a fix the reproduction has not confirmed. Code decides fail or pass.
- **30-second demo:** The upstream issue appears with the minimal test. Cut to "21 days later": CI shows the reproduction passing on the new version, and the MR diff shows 30 lines of workaround in red.
- **Nearest crowded space:** dependency update bots (not crowded in this hackathon) and security auto-fix (crowded). Difference: it starts from your own workaround, gives back upstream first, and upgrades only when that specific bug is proven fixed.
- **Biggest risk:** The demo needs an upstream that fixes the bug on cue; an honest stand-in is our own small library project in the subgroup, labelled as such, plus registry access through the network allowlist.

### B10. Wince

- **Pitch:** Every time someone clicks Retry on a failed job, the agent counts a wince; tests that keep hurting people while protecting nothing are quarantined with an end date, and the person who kept retrying hears that it was not their fault.
- **Mechanism mapped:** Pain is a signal from nerve endings that detect possible damage. It is located and graded, and the body treats pain with damage differently from pain without damage. Guarding protects a hurt area for a while, and pain that outlasts healing has to be retrained rather than obeyed. Here a person's Retry click is the wince. Code separates pain with damage (the job fails again, or fails on main every time) from pain without damage (same commit, failed, then passed). The model locates it: which test, and what kind of failure (timeout, network, test order), from logs and test reports. Guarding is a quarantine with an end date, not a deletion; if the test still fails after the end date, it comes back loudly.
- **Person and moment:** Yusuf has clicked Retry on the same integration test 11 times this month and has started to wonder whether his changes are the problem. On Monday he reads: "test_checkout_timeout failed and then passed on the same commit 23 times this month, for 6 people, 11 of them yours: it is flaky, it is not you."
- **Flow:**
  1. A weekly **pipeline schedule** (or a **pipeline event trigger** when a person's retry restarts a pipeline) starts the **Duo custom flow**; a script lists retried jobs and their **unit test reports** (code).
  2. The flow reads the failed attempts' **job logs** to locate the test and the kind of failure.
  3. Code decides pain without damage: same commit failed then passed at least N times for M people.
  4. The flow drafts a quarantine **merge request** (a skip marker with an end date) and an issue for the test's owner (from **CODEOWNERS**), and tells the people who kept retrying.
  5. The owner or a maintainer merges; after the end date a CI check fails if the test is still quarantined without a fix.
- **Stages:** verify, create, plan, govern.
- **Autonomy:** Supervised. The agent finds and drafts; a human approves each quarantine.
- **Model may / may not / code decides:** May locate the failure, write the MR and the messages. May not delete tests, quarantine a test that fails every time, or extend an end date. Code decides the retry statistics and enforces the end date.
- **30-second demo:** A tally of Retry clicks per test, Yusuf's name beside 11 of them, the message "it is flaky, it is not you", and the quarantine MR with its end date.
- **Nearest crowded space:** CI failure fixers (56 in Feb). Difference: it never repairs a red pipeline; it reads weeks of human retries to find the tests that hurt without protecting, and it quarantines them for a fixed time.
- **Biggest risk:** It needs a genuinely flaky test and weeks of retries by several people; one builder can stage this with a second account and a test that fails at random, labelled as staged.

### B11. Night Replay

- **Pitch:** Each night the agents replay the day's human corrections (every "no", every edit to one of their proposals) and propose a small change to their own skill files, so a person only has to teach them once; people approve what the agents remember and what they forget.
- **Mechanism mapped:** During deep sleep the hippocampus replays the day's experiences in fast bursts, and the cortex stores the ones that matter in long-term memory. At the same time connections are scaled down overall, so weak, unused ones fade and the important ones stand out. Memory is consolidated offline, in a quiet period, not during the experience. Here, during the day people correct the agents' post-code proposals: they reject them, edit them, or answer "not during the batch window". At night, a flow replays the day's corrections, finds the rule behind each one (the model), checks each rule against past decisions people approved (code: the rule must not contradict any of them), and proposes an edit to `skills/<agent>/SKILL.md`. The downscaling half: rules that have not been used for 60 days are proposed for removal, so the skills stay short.
- **Person and moment:** Chen corrected the agent three times yesterday, each time some version of "never restart workers during the nightly batch". The next morning he finds an MR titled "What I learned from you yesterday" that adds one line to the agent's skill file with links to his three comments; he approves it, and the agent never asks him again.
- **Flow:**
  1. A nightly **pipeline schedule** owned by a person starts the **Duo custom flow** in the team's quiet window.
  2. The flow collects the day's corrections: replies to agent proposals, rejected proposals, and human edits to agent **merge requests** (the agent's first commit compared with what was merged). The model decides which notes are corrections and which are ordinary talk.
  3. It writes candidate rules, each with the quotes it came from.
  4. A script checks each rule against the log of past proposals and human decisions (code: no contradiction with an approved decision; at least two corrections, or one explicit "always" or "never").
  5. It opens one MR to the agents' **skills** files (and `AGENTS.md`), including removals for rules unused in 60 days; a human approves; new flow sessions load the updated skills.
- **Stages:** govern, plan (and whichever stages the corrected agents work in).
- **Autonomy:** Assisted. Every change to what the agents remember is approved by a person.
- **Model may / may not / code decides:** May find corrections and phrase rules. May not edit skill files directly, add a rule without quotes, or keep a rule that contradicts an approved decision. Code decides the contradiction check and the usage counts.
- **30-second demo:** A time-lapse of Chen's three comments during the day; night falls; the MR "What I learned from you yesterday" appears with three quotes and one new line; merge. The next day the agent's proposal reads "Waiting until 06:00: nightly batch window (rule learned from Chen, Oct 14)."
- **Nearest crowded space:** organizational memory (LORE, the Feb grand prize) and GitLab's own "Review instructions learner" flow (code review rules). Difference: it learns how the agents should behave after code from people's corrections, only through skill files people approve, and it forgets on purpose.
- **Biggest risk:** It needs a day of real corrections to replay, so other agents must already be running and being corrected; the contradiction check has to stay simple (plain rules against a decision log) to be honest.

### Also considered (biology, not written up)

- **Antigen** (antigen presentation): the agent turns one user's report into a reproduction and shows it back to the reporter to recognize ("is this what happened?") before it becomes a permanent regression test.
- **Chrysalis** (metamorphosis): a risky schema change is split into expand, migrate and contract steps across several releases, with a parity check between old and new structures and a human yes before each step.
- **Moonlight** (circadian rhythm): each region gets a release at its users' quietest hour, but only while someone who can fix it is awake.

## Lens 2: Remove the load-bearing assumption

### Banned: the three most obvious answers

1. **Remove "a human approves the release": agents ship to production alone** after scans, tests and a health check. This is the hands-off release gatekeeper: 4 of 7 known October entries and the judges' reference project.
2. **Remove "a human reviews code before merge": an AI reviews every MR**, before or after merge. 95 code review projects in Feb.
3. **Remove "the on-call person is awake": an AI on-call bot that diagnoses and auto-remediates incidents at night** (root cause plus auto-rollback, as in ZeroTouch Monitor and Praetor).

### The assumptions, and what follows when each is removed

| # | Assumption the lifecycle rests on | Remove it: what follows | Where it goes |
|---|---|---|---|
| 1 | The developer decides when to ship. | Merging and landing become two decisions by two people: the on-call person whose night it is says when a risky change lands (in B2B, also the customer whose change window it is). | A3 Landing Window |
| 2 | Deploy is the end of the story. | The change keeps a line back to its author: a week later she hears how it is doing and makes one decision. | A7 Postcard |
| 3 | Users report bugs to someone who reads them. | If nobody reads them, the system must: join independent reports into one signal, act at a threshold, and answer every reporter. If users never report at all, the system has to notice silent failure itself. | B1 Quorum; sketch Silent Report |
| 4 | The on-call person is awake. | Night is the normal case: nothing risky lands in someone's night without consent, alerts are sorted so only the critical wake anyone, and a hand-off carries the night into the morning. | A3 Landing Window; B2 Night Nurse |
| 5 | Code review happens before merge. | Banned answer: AI review after merge. Other answer: the review that matters happens when the change meets real users, by its author, a week later. | A7 Postcard |
| 6 | The release goes to everyone at once. | Order becomes a choice made for people: those who reported the bug get the fix first, with consent, and their replies inform when the rest get it. | A2 Front Row |
| 7 | The person who set it up is still here. | Schedules, approvals, alert routing, tokens and know-how that hang on one person must be found and handed over before they leave, each one checked by API. | A1 Last Day |
| 8 | Production only changes through the pipeline. | Hand-made emergency changes exist, so drift must be caught, written back into code in the fixer's name, and the next deploy must refuse to erase it silently. | A4 Writeback |
| 9 | The approver understands what they approve. | Approval has to carry understanding: one cited question about the most surprising change, answered before consent. | A5 Teach Back |
| 10 | What the agent may do alone is fixed in config. | Autonomy becomes per action and earned: granted by a person from the agent's record, revoked automatically on a miss. | A6 Learner Permit |
| 11 | Evidence for auditors is gathered when the auditor asks. | Any audit question can be answered from existing records on any day; people approve answers instead of collecting screenshots. | A8 Auditor Hour |
| 12 | Announcing a deprecation makes people stop using the old thing. | They do not read the notice; the publisher must find who still uses it, help each one move, and remove it only when real use reaches zero. | A9 Sunset |
| 13 | Rollback is always possible. | Some steps are one-way doors (dropping a column, sending emails, publishing a package); gate only those with a named person and let reversible steps flow. | sketch One-way Door |
| 14 | An alert means something is wrong. | Most pages are noise, so alert rules must be tested against normal history before they may page a person. | B3 Thymus |
| 15 | Temporary means temporary. | Emergency patches stay forever unless something brings them back at a safe moment and replaces them properly. | B6 Scar Tissue |
| 16 | A failing test means broken code. | Many failures are pain without damage; human retries are the signal that finds them. | B10 Wince |
| 17 | The runbook is right because it worked last time. | Remedies need a control group: compare treated and untreated incidents before keeping a step. | B8 Placebo |
| 18 | Someone notices when a scheduled job stops. | A missing run must itself be a signal; often the cause is that the schedule's owner left. | folded into A1 Last Day |
| 19 | The approver is around. | Approvals route to someone available with the same authority, or the deploy waits for a stated return date, never silently. | sketch Stand-in |
| 20 | A fix is what users need first. | Users often need relief before a fix: support switches the new feature off for one customer, safely, in minutes. | sketch Relief Valve |

### A1. Last Day

- **Pitch:** When someone leaves the team, the agent finds every part of the post-code lifecycle that quietly depends on them (schedules that run as them, approvals only they can give, alerts that page only them, know-how only they have) and walks the hand-over with them before they go.
- **Assumption removed:** "The person who set it up is still here." In GitLab, a pipeline schedule runs as its owner; a protected environment or a CODEOWNERS rule can name one person; an escalation policy pages named people; tokens and runners belong to users; and runbooks say "ask Grace". When her account is blocked, some of this fails at once and some fails silently weeks later.
- **Person and moment:** Grace's last day is Friday, and on Monday her manager assigns the hand-over issue to the flow; by lunch she has a checklist built from what is actually true, 9 things only she holds, including the nightly backup schedule that would have stopped with her account. On Friday she watches the last item turn green and leaves knowing nothing will break because she is gone.
- **Flow:**
  1. The manager creates a hand-over issue from a template, names the person, and assigns it to the **Duo custom flow** (**assign trigger**).
  2. The flow searches everywhere a person can carry weight (the model chooses where to look): **pipeline schedules** and their owners, **protected environments** and **approval rules**, **CODEOWNERS**, **escalation policies** and **on-call schedules**, **feature flags** tied to their issues, assigned issues and MRs, **Duo triggers** they set up, and the informal ones: runbooks and comments that say "ask Grace".
  3. Code checks each finding through the API (is she really the only approver? does the schedule really run as her?) and drops anything it cannot confirm.
  4. The flow proposes a successor per item, from who touched it most recently, and creates one child task per item for Grace and the successor. For know-how items it asks Grace three short questions and drafts the runbook MR from her answers.
  5. Each item is closed by a human: the successor clicks **Take ownership** on the schedule (GitLab requires the new owner to do it), a maintainer merges the CODEOWNERS and approval-rule MRs the flow drafted, Grace approves the runbook MR.
  6. On the last day a **CI job** re-checks every item and posts the result on the issue.
- **Stages:** govern, configure, release, monitor, secure, plan.
- **Autonomy:** Assisted. Every hand-over is approved by the person giving and the person receiving.
- **Model may / may not / code decides:** May search, propose successors, draft MRs and questions. May not reassign anything, revoke tokens, or change approvals. Code decides who owns what.
- **30-second demo:** The checklist fills in, nine items, one highlighted in red: "Nightly backup pipeline runs as @grace and will stop when her account is blocked." Arjun clicks Take ownership; the item turns green; the last-day check says 9 of 9.
- **Nearest crowded space:** onboarding aids (36 in June), the opposite end of a person's time on a team. Nothing in the known field handles leaving. Difference: it is about the post-code responsibilities a person carries, each one checked against the API.
- **Biggest risk:** Reading other people's schedules, protected environments and escalation policies may need Maintainer rights or Premium features; the demo needs a second account to play Grace, and the informal "ask Grace" knowledge must be seeded.

### A2. Front Row

- **Pitch:** The fix for a bug reaches the people who reported it first, with their consent; they hear about it in plain words, and their replies help a human decide when everyone else gets it.
- **Assumption removed:** "A release goes to everyone at once." Once it does not, the order can be chosen for people instead of by a random percentage: the people who took the time to report the problem, who care most and will notice whether it works, go first.
- **Person and moment:** Mr. Haddad runs a print shop and wrote to support two weeks ago that his invoices print with the wrong date. On Thursday he gets an email saying the fix is live for him before anyone else and asking him to print one invoice and check, he writes back "Yes! Thank you", and that reply is what the release manager reads before widening the fix to everyone.
- **Flow:**
  1. Customer emails arrive through **Service Desk** and are linked to a bug issue by support (human triage). The fix **merge request** closes the bug; a human merges it.
  2. A **pipeline event trigger** starts the **Duo custom flow**: it finds everyone who reported the bug (linked **Service Desk** issues, duplicates, and similar unlinked tickets it recognizes, which a human must confirm), and code maps them to user IDs in the app.
  3. The flow proposes the first audience: the fix behind a **feature flag** with a **user list** strategy containing the reporters, in the **production environment**, plus the plain-language email. A human approves by replying "go" (**mention trigger**).
  4. A **CI job** applies the flag; the flow replies on each Service Desk issue, which GitLab emails to the reporter.
  5. Replies come back as notes; the model reads each one (works, does not, unclear) and code adds **error tracking** counts for those user IDs. The flow posts a summary and proposes the next step (50%, then everyone), each approved by a human.
  6. At 100%, everyone who reported gets a closing note and a **release** is created.
- **Stages:** plan, release, configure, monitor.
- **Autonomy:** Supervised. The agent runs the loop; a human approves the first audience and each widening.
- **Model may / may not / code decides:** May find reporters (unlinked ones only for a human to confirm), read replies, draft messages and propose the next step. May not email anyone outside the human-approved list, widen the rollout, or count an unclear reply as a yes. Code decides the user list, the flag state and error counts per group.
- **30-second demo:** Three reporters' inboxes receive "the fix is live for you first". One replies "works!". The release manager reads the summary and clicks; the flag panel goes from "user list: 3" to "50%".
- **Nearest crowded space:** post-deploy verification, and Proof of Fix (excluded). Difference: it does not hunt logs to prove a fix; it chooses who receives the fix first and listens to them, and every widening is a human decision.
- **Biggest risk:** The Service Desk email round trip in the hackathon project and mapping email senders to app user IDs need a demo convention; flag writes may have to run as CI jobs because the flow token may not reach the Feature Flags API.

### A3. Landing Window

- **Pitch:** A risky change does not land in someone else's night: the agent finds when the people who would have to fix it are awake, and asks the on-call person before anything risky ships into their sleep.
- **Assumption removed:** "The developer decides when to ship." The person who pays for a bad deploy is the one on call, often in another time zone. Merging and landing become two decisions by two people.
- **Person and moment:** Friday 17:40 in Berlin, Felix merges a database change and is about to stay late to watch it, but the agent replies that Ama in Accra is on call tonight and proposes Monday 09:30 unless she accepts now. Ama taps "hold", Felix goes home, and on Monday the change lands with both of them watching.
- **Flow:**
  1. A human merges to main; the **pipeline** builds and deploys to **staging** as usual; the production deploy job waits (manual or delayed job).
  2. A **pipeline event trigger** starts the **Duo custom flow**. It reads the diff and decides what kind of change it is (migration, config, user-facing, harmless) and which signals would show trouble (the model chooses where to look).
  3. Code computes the window from the **on-call schedule**, people's time zones, **deploy freeze** periods and the team's quiet hours; harmless changes get "now".
  4. For risky changes outside a waking window, the flow asks the on-call person on the MR: "accept now" or "hold until Monday 09:30". The reply (**mention trigger**) decides; no reply means hold.
  5. At the window, a **pipeline schedule** or delayed job runs the production **deployment** to Cloud Run; the flow tells the author and the on-call person.
- **Stages:** release, govern, configure, monitor.
- **Autonomy:** Supervised. Holding and scheduling happen alone because they move toward safety; shipping into someone's night needs that person's yes.
- **Model may / may not / code decides:** May classify the change and explain the risk. May not ship into a night without consent or move a deploy earlier than the window code computed. Code decides the schedule, time zones, freezes and the deploy itself.
- **30-second demo:** The MR shows a strip of three time zones with a green band, "everyone awake: Mon 09:30". Ama's reply: "hold". Time jumps to Monday 09:30, the deploy runs, and both get a note.
- **Nearest crowded space:** release gatekeepers. Difference: it never judges whether a change is good enough to ship; it only decides when, by people's clocks and with the on-call person's consent.
- **Biggest risk:** On-call schedules are a Premium feature read through GraphQL, and deploy freezes and delayed production jobs on a protected main may need Maintainer; the fallback is a team clock file in the repo.

### A4. Writeback

- **Pitch:** When someone fixes production by hand during an emergency, the agent notices, writes the change back into code in their name, and stops the next deploy from quietly undoing it.
- **Assumption removed:** "Production only changes through the pipeline." In real incidents people change memory limits, environment variables or traffic splits in the cloud console; the next routine deploy from main erases the fix and the outage comes back.
- **Person and moment:** At 02:10 Clara raised the Cloud Run memory limit by hand to stop the crashes and went back to sleep, and at 10:00 a teammate's routine deploy would have reset it. Instead the deploy stops with a plain message, and Clara finds a draft MR in her name that writes the new limit into the service config with a link to the incident; she approves it, and the deploy goes on with her fix inside.
- **Flow:**
  1. A scheduled check (a **pipeline schedule**, or a Cloud Run job every 15 minutes) compares the live **Cloud Run** service config, read with keyless WIF, against the config in the repo at the last **deployment** (code decides drift).
  2. On drift it starts the **Duo custom flow** (Flows API, or an issue a human assigns). The flow finds who and why: the **Cloud Audit Logs** entry, the **incident** open at that time, its timeline notes (the model chooses where to look).
  3. The flow drafts a **merge request** that adopts the change into code (service config or deploy job flags), assigned to the person who made it and linked to the incident.
  4. Code guard: the deploy job checks for unadopted drift and fails with a plain message: "Deploying now would undo a manual change Clara made at 02:10. Adopt it or discard it first."
  5. A human chooses: merge the adopting MR, or close it and confirm the discard; the deploy then proceeds.
- **Stages:** monitor, create, verify, release, configure, govern.
- **Autonomy:** Supervised. Detecting and drafting happen alone; keeping or discarding a manual change is always a person's choice.
- **Model may / may not / code decides:** May work out the change's purpose and owner and write the MR. May not change production, merge, or discard anything. Code decides the drift diff and the deploy block.
- **30-second demo:** The console at "02:10": memory 512Mi to 1Gi. Cut to 10:00: the deploy pipeline stopped with the message. The MR in Clara's name. Merge; the deploy runs; the service shows 1Gi.
- **Nearest crowded space:** config drift as one cause in incident root cause (the NEXUS plan). Difference: drift is not reported as a cause; the person's fix is protected and turned into code.
- **Biggest risk:** It needs Google Cloud read access and audit log access from the checker, a token to start the flow from a non-human event, and edits to the deploy job on a protected main (Maintainer).

### A5. Teach Back

- **Pitch:** Before a person approves a production deployment, the agent finds the one change most likely to surprise someone and asks the approver one plain question about it, so the approval means something.
- **Assumption removed:** "The approver understands what they approve." At 18:00, with 14 changes in a release, approvers click Approve. Teach-back is a hospital practice: the nurse asks the patient to say the plan back in their own words to check it was understood.
- **Person and moment:** Nadia approves production releases every evening, usually 10 to 15 changes at a time. Tonight the request asks her one question, "One change will log users out after 5 minutes instead of 30 (config/session.py line 12, from MR !88): is that intended?", and she checks with the author, finds a debug value left in, and rejects the deploy instead of hearing about it from angry users tomorrow.
- **Flow:**
  1. The production deploy job targets a **protected environment** with **deployment approvals** (or a manual job). When the main **pipeline** starts, a **pipeline event trigger** starts the **Duo custom flow**, so the question is ready by the time the deploy waits.
  2. The flow reads every change since the last production **deployment** (compare API), the **merge requests** and config diffs, and picks the most consequential change in behavior that a user would notice (the model chooses where to look and what matters).
  3. Code checks the citation: the quoted line exists in the diff at that path. No claim without a real line.
  4. The flow posts a three-line summary and one yes-or-no question with the evidence link, mentioning the approver.
  5. The approver answers; the question and answer are kept with the deployment; then the human approves or rejects in GitLab as usual. A small gate job can require an answer before the deploy job runs.
- **Stages:** release, govern, verify.
- **Autonomy:** Assisted. A person approves every production step; the agent only makes that approval informed.
- **Model may / may not / code decides:** May choose the question and write the summary. May not approve, block a human decision, or ask about anything it cannot cite. Code decides the citation check and the gate.
- **30-second demo:** The approval screen with the question highlighted. Nadia types "No, that's wrong" and rejects. Ten minutes later the author's fix MR changes 5 back to 30.
- **Nearest crowded space:** release notes generators (excluded) and MR summaries or code review. Difference: no notes for users and no review of code; one cited question for one person at the moment of consent.
- **Biggest risk:** Deployment approvals need protected environments (Premium, set up by a Maintainer), and there is no trigger for "a deployment is waiting", so timing rides on the pipeline start; question quality depends on a demo diff with one clear surprise.

### A6. Learner Permit

- **Pitch:** Each action the agent can take in production starts as "ask me every time"; after enough approved, unedited proposals with good outcomes, the agent asks for a permit to do that one action alone, and loses the permit by itself the first time it gets one wrong.
- **Assumption removed:** "What the agent may do alone is set once, in config." People do not extend trust that way; a new colleague earns permissions one task at a time. The contest's own three levels (Assisted, Supervised, Hands-off) become a path that an agent walks, one action at a time, while a person watches.
- **Person and moment:** Femi has approved the agent's proposal "roll back to the previous Cloud Run revision" six times, unchanged, each time at 3 a.m. On the seventh morning she finds an MR from the agent asking "May I do this one alone at night and tell you at 08:00?", merges it, and the next Tuesday she sleeps through the rollback and reads about it over coffee.
- **Flow:**
  1. `permits.yml` in the repo lists action types (roll back a revision, raise min instances, turn a flag off, restart) with a level: ask, notify after, or alone at night. It changes only by **merge request** with **CODEOWNERS** approval.
  2. During an **incident** (an **alert** through the relay and the Flows API, or a person mentioning the flow), the **Duo custom flow** investigates (deployments, flags, metrics; the model chooses where to look) and proposes one action from the list, with evidence.
  3. Code checks the permit. At "ask", the flow waits for a person's "go" (**mention trigger**); at "alone", a **CI job** carries it out on **Cloud Run** and records a **deployment**.
  4. After each action, code measures the outcome (did the error rate recover within 10 minutes?) and the flow adds a row to the ledger issue for that action type.
  5. After N clean, unedited approvals, the flow opens the promotion MR; a person merges or not. On any rejection or bad outcome, CI demotes that action type at once (toward safety) and the flow explains why.
- **Stages:** monitor, release, configure, govern.
- **Autonomy:** All three as a path, per action. Best fit Hands-off: the person sets the intent and walks away for exactly the actions that have earned it.
- **Model may / may not / code decides:** May investigate, propose, and ask for promotion. May not edit `permits.yml` without a human merge, pick an action outside the list, or skip the ledger. Code decides the permit check, the outcome and the demotion.
- **30-second demo:** The ledger with six green rows; the MR "Permit request: rollback, alone at night"; merge. A staged fault at "03:00", the rollback runs, the 08:00 note arrives. Then a staged bad case: the outcome check fails and the permit drops back to "ask" on its own.
- **Nearest crowded space:** auto-rollback bots and release gatekeepers with autonomy levels (AfterMerge acts alone at low risk; BABYDOV's autonomy budget). Difference: autonomy is not computed from a risk score; a person grants it per action, from the agent's own record, through an MR, and it is taken back automatically. The rollback is ordinary; the permission system is the product.
- **Biggest risk:** Carrying out production actions needs Google Cloud credentials from CI or from the flow (`id_tokens` in agent-config is unverified); showing six approvals means staging several incidents; night alerts again depend on the Flows API.

### A7. Postcard

- **Pitch:** A week after your change reaches production, you get a short postcard from it: how many people used it, what went wrong, what users said, and one decision to make.
- **Assumption removed:** "Deploy is the end of the story." The author moves on and never learns whether the work mattered, and flags and half-done rollouts stay behind because nobody comes back.
- **Person and moment:** Kemi spent two weeks on CSV export and never heard about it again. Seven days after release a comment lands on her MR, "214 exports by 61 customers; 2 failed on files over 10 MB; one customer wrote 'finally!'; the flag has been at 100% with no errors for 5 days, shall I remove it?", and she smiles, replies "yes", and opens an issue for the 10 MB case.
- **Flow:**
  1. When an MR reaches the **production environment**, a **CI job** records a postcard date seven days out; a daily **pipeline schedule** picks up the postcards that are due.
  2. On the day, the **Duo custom flow** reads the MR diff to decide what to measure (endpoint, event names, flag key) and where: app telemetry (**GitLab Observability** or Cloud Logging through allowed domains), **error tracking**, **Service Desk** issues that mention the feature, and the **feature flag** (the model chooses where to look).
  3. A script runs the queries and computes every number; the flow writes the postcard using only those numbers and quoted user words.
  4. It posts on the MR; GitLab notifies the author.
  5. The author replies (**mention trigger**), and the flow does what she chose: a flag-removal MR or a follow-up issue.
- **Stages:** monitor, release, configure, plan.
- **Autonomy:** Hands-off for the postcard (read-only, nothing in production changes); Assisted for any follow-up, which waits for the author's reply.
- **Model may / may not / code decides:** May decide what to measure and how to tell it, and quote users. May not invent or round numbers, reopen anything, or act without the author's reply. Code decides every number.
- **30-second demo:** Day 7: Kemi's notification. The postcard with three numbers and a customer quote. She replies "yes", and a flag-removal MR appears.
- **Nearest crowded space:** Proof of Fix (excluded) and June's Stayed Shipped (whether merged changes survive). Difference: postcards are for features, not fixes; nothing is verified or reopened; the output is a story for the author and her next decision.
- **Biggest risk:** It needs real usage telemetry for a demo app (generated traffic, labelled), a reliable seven-day schedule, and a clear line in the video so judges do not file it under Proof of Fix.

### A8. Auditor Hour

- **Pitch:** An auditor asks a question in plain words as an issue; the agent works out which GitLab records answer it, code computes the answer, and a compliance lead approves the reply before it goes out.
- **Assumption removed:** "Evidence is gathered when the auditor asks." Today that means weeks of screenshots every quarter, collected by engineers.
- **Person and moment:** Every quarter Olu loses two weeks to screenshots for the SOC 2 auditor. This time the auditor writes "Show that every production change in Q3 was approved by someone other than its author", and an hour later Olu reads a draft with the count (212 of 212), two edge cases explained and a link to every record, approves it and goes back to his real work.
- **Flow:**
  1. The auditor's question arrives through **Service Desk** (or Olu files it), and Olu assigns it to the **Duo custom flow** (**assign trigger**).
  2. The flow maps the question to records (the model chooses where to look): production **deployments**, the **merge requests** in each, **MR approvals**, **protected environment** approvals, **pipelines**, **audit events**.
  3. A **CI job** computes the answer deterministically and attaches a CSV with a link per record (code decides what is true).
  4. The flow drafts the reply: the plain answer, exceptions explained, links. Olu approves ("send", **mention trigger**), and the reply goes to the auditor through Service Desk.
- **Stages:** govern, release, verify, secure.
- **Autonomy:** Supervised. Drafting happens alone; anything that reaches an auditor is approved by a person.
- **Model may / may not / code decides:** May interpret the question, choose the records and explain exceptions. May not compute the numbers itself or send anything without approval. Code decides the queries and counts.
- **30-second demo:** The auditor's question as an issue; a minute later a draft reply with "212 of 212", two explained exceptions and a CSV; Olu types "send".
- **Nearest crowded space:** evidence receipts and tamper-evident attestation (crowded). Difference: it mints no new evidence and signs nothing; it answers questions from records GitLab already keeps, with a person approving every answer.
- **Biggest risk:** Audit events and approval data may need Maintainer or Owner access, and a quarter of believable history must be generated for the demo; the human moment is quieter than the others.

### A9. Sunset

- **Pitch:** When you retire an API endpoint or an old package version, the agent finds who still uses it, helps each of them move with a ready change or a plain email, and proposes the removal only when code shows nobody is left.
- **Assumption removed:** "Announcing a deprecation makes people stop using the old thing." They do not read the notice, so the old thing lives for years, or it is removed and someone's integration breaks on a Monday.
- **Person and moment:** Sofia keeps a small integration running for a warehouse and never saw the deprecation banner; three weeks before the old endpoint goes away she gets an email with the two lines she has to change and a test request she can run. Meanwhile Amir, who owns the API, watches the remaining callers drop from 14 to 0 and deletes the old endpoint without a single angry ticket.
- **Flow:**
  1. The owner opens a deprecation issue naming the endpoint or package version and assigns it to the **Duo custom flow** (**assign trigger**).
  2. A script finds the users: request logs for the endpoint by API key (Cloud Logging), and, for a package, which projects in the group still pin the old version in the **package registry** or their lockfiles. The model decides where else to look (SDKs, docs and examples that still use it) and matches keys to owners.
  3. For internal projects, the flow opens **merge requests** in each consumer project with the migration; for external users it drafts plain emails through **Service Desk**, which the owner approves before sending.
  4. A weekly **pipeline schedule** recounts usage (code), and the flow updates the issue with who is left.
  5. At zero use for N days (code), the flow opens the removal MR; the owner merges; the **release** goes out.
- **Stages:** monitor, plan, create, package, release, govern.
- **Autonomy:** Supervised. The agent does the finding and drafting; each email, each MR in another team's project, and the removal need a human yes.
- **Model may / may not / code decides:** May identify consumers from logs and code, write migration MRs and emails. May not contact anyone or open MRs in other projects without approval, or propose removal before code shows zero use. Code decides the usage counts.
- **30-second demo:** A burndown of callers from 14 to 0 over "three weeks", one external email with two changed lines, and the final removal MR going green.
- **Nearest crowded space:** dependency update bots (not crowded in this hackathon) and Apoptosis in this file. Difference: it works from the publisher's side and for the consumers, and removal waits for zero real use.
- **Biggest risk:** It needs request logs with client identifiers and several consumer projects to migrate; one builder must stage a few clearly labelled fake consumers, and opening MRs in other projects needs access to them.

### Also considered (sketches from the table)

- **One-way Door** (rollback is always possible): tag only the irreversible steps in a release and require a named person for those; everything reversible flows without approval. Largely covered by Return Ticket in the parallel file.
- **Stand-in** (the approver is around): when the required approver's GitLab status says busy or away, propose another approver with the same authority, or schedule the deploy for their return, instead of letting it sit.
- **Relief Valve** (a fix is what users need first): support switches a new feature off for one customer within minutes, with the agent checking that the complaint matches that feature and an engineer told.
- **Silent Report** (users report bugs): the agent notices failures nobody reports (repeated clicks on a button that does nothing after a release) and writes the bug report on the user's behalf.

## Overlap with the parallel lens file

The on-call and inversion lenses ([lens_oncall_inversion.md](lens_oncall_inversion.md)) were generated at the same time and reached some of the same places. Ideas found from two directions may be the sturdier ones; these pairs should be merged or chosen between at scoring time.

| This file | Parallel file | Shared core | What this version adds |
|---|---|---|---|
| B3 Thymus | 1.5 Sleep Debt | replay alert rules against history before a person approves them | Gates new and changed rules at MR time with both tests (must catch real incidents, must stay quiet on normal days) and proposes mutated variants. Same replay engine. |
| B4 Booster | 1.6 Fire Drill | a staged practice incident before an on-call week | Replays real past incidents chosen per person, keeps a memory record, and schedules boosters when memory fades. |
| B6 Scar Tissue | 1.4 Loose Ends | undo the temporary changes made at 3 a.m. | Waits for a quiet period that code checks, and replaces a crude patch with the proper fix rather than only undoing it; counts unremodeled patches. |
| A3 Landing Window | 1.8 Daylight Rollout | nothing risky moves while its people sleep | Applies to deploys, and asks the on-call person's consent before landing in their night. |
| A6 Learner Permit | 1.1 Night Orders | what the agent may do alone at night | Permits are earned per action from the agent's record, granted by MR, revoked automatically; Night Orders is a list signed each evening. |
| A2 Front Row | 2.3 Promise Kept | the reporter hears when the fix reaches them | Changes the rollout order (reporters first, by user list) and uses their replies to inform widening. |
| B1 Quorum | 1.3 Watermelon | customer reports as a production signal | Counts independent reports to a threshold, ties them to a flag cohort, and pauses only that cohort. |
| A1 Last Day | 2.1 Plane Mode | knowledge held by one person | Covers everything a leaving person owns (schedules, approvals, routing, tokens), each checked by API, not only what is in their head. |
| B9 Mutualist | 2.5 Fine Print | dependency upgrades with proof | Starts from your own workaround and reports upstream before upgrading. |

## Natural combinations

Listed for the scoring step, not ranked:

- **A user loop:** Quorum (many reports become one signal and pause the cohort), then Antigen (the reporter recognizes the reproduction), then Front Row (the fix reaches those reporters first).
- **An on-call loop:** Thymus (which alerts may page), Night Nurse (who is woken), Learner Permit (what the agent may do alone), Placebo (which remedies work), Booster (who is ready), Night Replay (what the agents remember).
- **A "temporary becomes permanent" loop:** Scar Tissue (emergency patches), Writeback (hand-made production changes), Apoptosis (flags), Sunset (old endpoints and package versions).
