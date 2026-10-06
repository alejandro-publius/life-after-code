# Ideas: the person on the other end, and rituals from other crafts

Concept generation for Part 5 (docs/IDEAS.md), written 2026-10-06. Two lenses from the coordinator. No scoring or ranking here.

Inputs: [IDEATION_BRIEF.md](../IDEATION_BRIEF.md) (read in full), [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md) (Duo flows, triggers, tools, limits), [field/code_hosts.md](../field/code_hosts.md) and [field/social.md](../field/social.md) (crowded spaces and names already in use). No web search. GitLab facts come from the guide; anything the guide marks unverified, or that I could not check, says (unverified).

Each concept gives: pitch; the person and their moment; the flow, with the GitLab features at each step; stages; autonomy; what the model may and may not do and what code decides; the 30-second demo moment; the nearest crowded space; the biggest risk for one builder by Oct 24. Lens 2 concepts also name the craft and the mechanism borrowed.

**About the sibling file.** I generated 1.1 to 1.9 and 2.1 to 2.9 before I read [lens_oncall_inversion.md](lens_oncall_inversion.md), which appeared in this folder while I worked. Several of mine landed on the same ideas independently. I kept them as written and added a "Sibling overlap" line wherever a concept there is close. Then I added 1.10, 2.10, 2.11 and 2.12 for range. Independent convergence cuts both ways: the fit is natural, and other entrants may reach the same idea.

Platform facts these concepts lean on (all from the guide):

- Only a human action can fire a flow trigger (mention, assign, assign reviewer, pipeline events, merge request created, marked ready, approved or merge conflict, work item created or status changed). Other events can start a flow through the Flows API; whether a call made with a token counts as a human start is unverified.
- A flow's token reaches only `ai_workflows` endpoints, and flows cannot read CI/CD variables. So changes to flags, freezes, schedules and environments go through a CI job that a person starts, or an MR that a person merges.
- Tool options in the flow YAML can force a value the model cannot change (the guide's example pins `create_merge_request_note` to `internal: true`). Several concepts use this so the model cannot email a customer.
- Our role is Developer plus an "AI member role". Protected environments, deployment approvals, freeze periods, Service Desk setup, alert integrations and CI/CD variables may need Maintainer (unverified).

## Lens 1: The person on the other end

People that software affects who never see GitLab, or see only one corner of it. Each concept starts from one of them and their moment, then works back to what the agent does in GitLab.

### Banned: the three most obvious answers

1. **BANNED:** a support ticket summariser or triage bot (Service Desk emails grouped into issues, duplicates merged, sentiment scored).
2. **BANNED:** a "your bug is fixed" notifier (when the issue closes or the release ships, email everyone who reported it).
3. **BANNED:** a friendly nudge bot for people who wait (welcomes first-time contributors, pings reviewers on stale merge requests).

Close variants also left out: customer-facing changelogs and "what's new" posts, status page updaters, feedback sentiment dashboards.

### 1.1 Spoken Diff

- **Pitch:** Before a release reaches production, hear what a screen reader user will hear on the pages the change touched, before and after.
- **Person and moment:** Grace is blind and pays her rent in the app every month with a screen reader. This month a refactor dropped a label, the button she needs is read out as just "button", and she has to phone the office and ask a stranger to pay for her.
- **Flow:**
  1. A person merges an MR and the main pipeline deploys to the staging environment on Cloud Run (CI/CD, environments, deployments). The staging pipeline's "passed" event starts the Duo custom flow (pipeline event trigger). Production promotion is a separate pipeline.
  2. The flow's agent reads the merged diff and the app's routes (`get_commit_diff`, `read_file`) and decides which user journeys the change could affect, for example "pay rent" and "change address".
  3. For each journey it drives a headless browser in its sandbox (`run_command`, Playwright) through staging and through production, adapts its steps when a page changed, and saves the ARIA snapshot at every step.
  4. Code turns each snapshot into the text a screen reader would speak (role, name, state, focus order), diffs before and after, and runs axe-core. The model never writes the spoken text.
  5. The flow posts the before and after transcript on the MR and the release issue, with an audio clip rendered in CI. If code found a regression, the production deploy job waits on a deployment approval for the protected environment, and the flow opens a small fix MR (for example the missing `aria-label`) for a person to merge.
- **Stages:** create, verify, release, govern.
- **Autonomy:** Supervised: a person approves the outcome (release, hold, or merge the fix). A Hands-off variant fits too: promote on its own when nothing a screen reader user hears got worse, and stop only on a regression.
- **Model and code:** The model may choose journeys, find its way through changed pages, explain the change in plain words and draft a fix. It may not call a regression acceptable, approve the deploy or merge. Code computes the spoken text from the accessibility tree, the diff and the axe counts, and decides whether the deploy is held.
- **Demo moment:** Two clips back to back: "Pay rent, button" and then just "Button". The production job shows "Waiting for approval", and the one-line fix MR sits beside it.
- **Nearest crowded:** Release gatekeepers (it can hold a deploy) and code review. It judges neither code nor tests: it plays back one person's experience of the live staging build, computed from the real accessibility tree. Accessibility after deploy had about 5 projects in February and 1 catalog project in June.
- **Sibling overlap:** Nearly the same as No Mouse (2.4 in lens_oncall_inversion.md). The difference is small: here the journeys come from the diff, and code, not the model, produces the spoken text.
- **Biggest risk:** A headless browser inside the flow sandbox (custom image in `agent-config.yml`, `*.run.app` in the network allowlist, time limits). Fallback: a CI job captures the snapshots and the flow reads them, which leaves the agent less room to explore.

### 1.2 Try First

- **Pitch:** The person who reported a bug gets a private preview of the fix before it ships, and their answer goes on the merge request.
- **Person and moment:** Beatriz runs a small bike repair shop and wrote to support three weeks ago that the booking form drops her Saturday slots. She has heard nothing and assumes nobody read it.
- **Flow:**
  1. Her email became a Service Desk issue. A developer opens a fix MR that says "Closes #N" (Service Desk, issues, merge requests).
  2. The MR pipeline deploys a review app as a tagged Cloud Run revision that takes no traffic and holds demo data only (CI/CD, dynamic environments). When the developer marks the MR ready, the "marked ready" trigger starts the flow.
  3. The flow reads Beatriz's own words and the diff, decides what she should try (which page, which steps, which data matches her case), then tries it itself in the review app with a browser script. If the preview does not behave differently, it stops and tells the developer instead of bothering her.
  4. It drafts a short note with the private link and two steps, posted as an internal note (the note tool pinned to internal in the flow YAML; documented for MR notes, unverified for issue notes), so the model cannot email her. The support agent edits it and posts it as a normal reply, which Service Desk emails to Beatriz.
  5. Her answer lands on the issue. The support agent mentions the flow, which reads it and posts "Confirmed by the reporter in preview" or "Not fixed: she says X" on the MR, and opens a follow-up issue if she found something new. A maintainer merges.
- **Stages:** plan, verify, release.
- **Autonomy:** Assisted: a person approves every message to the customer, and the merge.
- **Model and code:** The model may choose the steps and test data, check the preview itself, write the note and read the reply. It may not send anything to a customer, merge, or close the issue. Code decides whether the agent's own preview check passed (browser assertions), that the link expires, and that the preview holds only demo data.
- **Demo moment:** Beatriz's email appears under the MR: "Yes, Saturday shows now. Thanks for asking me." The MR gets one line: "Confirmed by the person who reported it."
- **Nearest crowded:** The banned "your bug is fixed" notifier, and Proof of Fix. This happens before release; the reporter checks the fix in a private preview and her answer becomes review evidence. Nothing watches production logs.
- **Sibling overlap:** Promise Kept (2.3 there) is the after-release "it's fixed" note, which is my banned answer 2. Try First is the before-release preview.
- **Biggest risk:** Service Desk and review apps in the provisioned project (enabling Service Desk may need Maintainer, unverified), and the "marked ready" trigger and the internal-note pin behaving as documented.

### 1.3 Canary Voices

- **Pitch:** During a staged feature flag rollout, complaints from users inside the rollout count as a signal and can hold the next step.
- **Person and moment:** Yuki writes to support at 9 a.m.: "Since this morning I can't log in." She is one of the 5% who got the new login rule, and on a normal day her ticket would wait two days while the rollout went on to 100%.
- **Flow:**
  1. A GitLab feature flag with a percent or user list strategy per environment controls the new login rule; the rollout plan (5%, 25%, 100%) lives in an issue (feature flags, issues).
  2. Before each step the release owner comments "@canary-voices ready for 25%?" on the rollout issue (mention trigger).
  3. The flow reads Service Desk issues since the last step and decides which could be about this change (it reads the flag description, the MR diff and the ticket text, and follows linked tickets). For each candidate, code checks whether that customer is inside the flag's cohort (user list membership, or the rollout hash).
  4. Code compares the complaint rate inside the cohort with the rate outside and applies the threshold the team set. The flow posts "Hold recommended" with the matching tickets quoted, or "Clear to advance".
  5. The release owner decides: a manual CI job advances or rolls back the flag through the Feature Flags API, or nothing moves (hold). The flow drafts replies for support to send to the affected users.
- **Stages:** plan, release, configure, monitor.
- **Autonomy:** Supervised: the agent never moves the flag, and a person approves each step. If the flow fails or the signal is unclear, the default is no advance.
- **Model and code:** The model may decide which tickets relate to the change, summarise them and draft replies. It may not change the flag, close tickets or contact users. Code decides cohort membership, the rate comparison, the threshold and the recommendation.
- **Demo moment:** On the rollout issue: "Ready for 25%?" Then: "2 of the 3 login complaints today come from the 5% cohort (expected about 0.15). Hold." Yuki's ticket is quoted, and the owner holds.
- **Nearest crowded:** Post-deploy verification and rollback in release gatekeepers. The signal here is people's own words matched to a flag cohort, not error rates, and it gates a flag step, not a deploy. User feedback and feature flags are both open spaces.
- **Sibling overlap:** Watermelon (1.3 there) also treats customer words as a signal, to wake a person when the monitors look green. Canary Voices uses cohort membership to gate a rollout step.
- **Biggest risk:** Enough believable demo tickets (seeded, labelled as demo), and flag write access from CI (a token with api scope; CI/CD variables may need Maintainer, unverified).

### 1.4 Straight Answer

- **Pitch:** A support agent asks "what can I honestly tell this customer?" and gets a status traced through GitLab with every claim checked, plus a way to get her the fix today.
- **Person and moment:** Ruth in support is answering the same customer for the third time about a broken invoice export. She is about to send "the team is aware and working on it" again, and she knows it reads like a brush-off.
- **Flow:**
  1. Ruth mentions the flow on the Service Desk issue: "@straight-answer what can I tell her?" (mention trigger).
  2. The flow decides what to follow from the ticket: linked issues, "Closes" references, MRs, cherry-picks to release branches, which commit each environment runs (deployments), the release that contains the fix, and the flag strategy that covers this customer (`gitlab_api_get`, `gitlab_graphql`).
  3. It drafts a list of claims, each with its source ("Fix merged in !241", "Live in production for 25% of accounts through flag invoice_v2"), and a reply in plain words.
  4. Code checks each claim against live API state and drops any it cannot confirm before Ruth sees the draft. No date appears unless a scheduled step exists in the rollout issue.
  5. Ruth edits and sends the reply herself. If the fix is live but not for this customer, she can ask for early access: the release owner approves, and a manual CI job adds the customer to the flag's user list (Feature Flags API). The flow drafts the "it's on for you now" note for Ruth to send.
- **Stages:** plan, release, configure, monitor.
- **Autonomy:** Assisted: read-only until a person acts; every message and the early-access change are approved by a person.
- **Model and code:** The model may choose what to trace and write the answer. It may not promise a date nobody set, send anything or change the flag. Code decides whether each claim is true (states, membership) and makes the early-access change only after approval.
- **Demo moment:** Ruth's draft changes from "The team is aware" to "The fix is live for 25% of accounts. Yours isn't one of them yet; the next step is planned for Thursday", with three checked links. She asks for early access, the owner approves, and the customer has the fix that afternoon.
- **Nearest crowded:** The banned notifier, and issue triage. This is pulled by the support agent at any moment, answers "is it live for this one customer" from deployments and flag strategies, has every claim checked by code, and can move the customer into the rollout.
- **Biggest risk:** The demo needs a real linked history (ticket, issue, MR, deployments, flag) across two environments; reading flag strategies through the flow's read-only API is assumed (unverified).

### 1.5 Row Call

- **Pitch:** Before a data migration runs in production, see the actual (demo) customers whose records it would change, and exactly how.
- **Person and moment:** Siobhan O'Brien-Nakamura has used the app for six years. A migration that "cleans up names" would print "Siobhan Obrien-nakamura" on every invoice from tomorrow, and she would only find out when her accountant asks.
- **Flow:**
  1. An MR adds a data migration. After a person merges it, the pipeline loads a masked or synthetic snapshot into a throwaway database (a CI service container, or a SQLite file) in a "rehearsal" environment (CI/CD, environments). The pipeline's "passed" event starts the flow.
  2. The flow reads the migration and decides which data shapes could go wrong (apostrophes, accents, long names, nulls, time zones, duplicates). It writes SQL probes to find such rows in the snapshot, and adds probes when one finds something.
  3. Code runs the migration on a fresh copy and computes the exact before and after for every probed row, plus totals: rows changed, rows changed in columns the migration does not name, constraint failures.
  4. The flow posts the row call on the MR and the release issue: three named demo customers with before and after, and the counts ("312 names with an apostrophe lose it").
  5. The production migration job, in the promotion pipeline, is a protected deployment that waits for approval (deployments and approvals). A person approves, or the flow drafts a fix to the migration as an MR for review.
- **Stages:** create, verify, release, govern.
- **Autonomy:** Supervised: the agent rehearses and reports; a person approves the production run.
- **Model and code:** The model may choose what to probe, write the probes, explain the effect and draft a fix. It may not touch production data or approve the migration. Code runs the migration on a copy, computes the diffs and counts, and holds the production job.
- **Demo moment:** One table row: "Siobhan O'Brien-Nakamura" becomes "Siobhan Obrien-nakamura", with "and 311 more like this" under it. The production migrate job: "Waiting for approval".
- **Nearest crowded:** Pre-merge blast radius, and the February "DB Migration Safety Checker" (risk class and rollback scripts). This runs the migration on a copy after merge and shows person-level before and after for the rows the model suspected, at the deploy gate.
- **Biggest risk:** A realistic, clearly labelled synthetic dataset with the right edge cases, and running a database inside the flow sandbox (or passing results between a CI job and the flow).

### 1.6 Wake Budget

- **Pitch:** An on-call agent that has to earn the right to wake you: it checks first, prepares one decision, and lets the house sleep when the morning can wait.
- **Person and moment:** Ilse is on call; her partner Tom starts work at six and their toddler has just gone down. At 2:14 a.m. an alert fires, and the phone on the nightstand stays dark because the agent checked and found nothing a person needs to decide before eight.
- **Flow:**
  1. A production alert reaches a small Cloud Run receiver, which opens a GitLab incident without paging anyone and starts the flow through the Flows API (alerts, incidents, Flows API).
  2. The flow decides where to look: recent deployments to that environment, flags changed today, error tracking or the subgroup's observability data, past incidents with the same alert, how many users are affected.
  3. Code applies the floor: a short list of conditions that always wake a person (payments failing, signs of data loss, error budget burning faster than a set rate). The model can add reasons to wake, never remove one.
  4. If nobody is needed now, the flow writes the morning note on the incident (what it saw, what it ruled out, what it suggests) and sends no page. If someone is needed, it prepares one decision with a ready manual job (for example "turn off flag new_checkout?") and code pages the on-call person (escalation policy set on the incident, or a push service; unverified which), so the wake-up is one tap.
  5. In the morning Ilse marks the night "right call" or "should have woken me". Code keeps that record, and the team uses it to tune the floor.
- **Stages:** release, configure, monitor, govern.
- **Autonomy:** Hands-off for the night itself: letting someone sleep changes nothing in production. Every production change still needs a person's tap.
- **Model and code:** The model may investigate, decide to wake earlier than the floor requires, and prepare the decision and the message. It may not change production, lower the floor or close the incident. Code holds the floor, sends the page and keeps the wake record.
- **Demo moment:** 2:14 a.m., the alert fires and the phone stays dark. The morning note: "I let you sleep. One crawler hit an old endpoint 4,000 times; no customer was affected. Blocking it is one click." Then a real fault at 3:40, and the phone buzzes once with one yes or no question.
- **Nearest crowded:** Incident root cause and generic incident chatbots. The goal is not the cause but whether a person must be awake, with a floor the model cannot lower and a wake-up shrunk to one prepared decision. On-call handling had 0 catalog items in June.
- **Sibling overlap:** Same scene as Night Orders (1.1 there) and close to Someone Awake (1.7 there); the morning record is close to Sleep Debt (1.5 there). Night Orders grants the agent actions for the night; Wake Budget grants it only silence, above a code floor.
- **Biggest risk:** Starting a flow at night with no human action: the Flows API call from Cloud Run must be accepted (unverified). On-call schedules, escalation policies and the alert integration may need Maintainer (unverified).

### 1.7 Last Caller

- **Pitch:** Before you delete an old API endpoint, the agent finds who still calls it and helps you tell each of them, person to person.
- **Person and moment:** Mr. Haddad, a school librarian, runs a script a parent wrote in 2019 that renews books through your old v1 API. The day v1 is deleted, 400 children's renewals fail and nobody tells him why.
- **Flow:**
  1. A developer opens the MR that removes `/v1/renewals` (merge request "created" trigger, or assigning the flow as reviewer).
  2. The flow decides where callers might show up: request logs or traces for that route in the subgroup's observability instance or Cloud Logging (network allowlist and `id_tokens`), API keys mapped to accounts, old support tickets that mention v1.
  3. Code counts calls per consumer over 30 days. For each remaining consumer, the model works out what they call and what the v2 equivalent is, by reading both implementations.
  4. The flow opens a sunset issue with one task per consumer and a drafted personal notice for each, and opens an MR that first adds Deprecation and Sunset response headers to v1 (`create_branch`, `create_commit`, `create_merge_request`).
  5. People send the notices. The removal MR stays blocked by an open thread until code shows zero calls for N days, or until a person accepts the remaining breakage in writing.
- **Stages:** plan, create, release, monitor, govern.
- **Autonomy:** Assisted: every notice and the removal itself are a person's call.
- **Model and code:** The model may search for callers, map v1 to v2, and write the notices and the header MR. It may not send notices, merge the removal, or decide the breakage is fine. Code decides the call counts and the zero-calls condition.
- **Demo moment:** The sunset issue lists three callers, one of them "Riverside Primary School library, last call 07:58 today". The removal MR shows "Blocked: 1 consumer still active".
- **Nearest crowded:** Pre-merge blast radius ("what could this break"). This uses real traffic, not the code graph, and runs the deprecation over weeks until people have been told.
- **Biggest risk:** Request logs with consumer identity that the flow can reach, and believable seeded traffic (labelled demo); a story that takes weeks must be compressed for a 3-minute video.

### 1.8 Dear Successor

- **Pitch:** When someone pins a dependency, skips a test or adds a flag, the agent asks them one question while they still remember why, and comes back when the reason is gone.
- **Person and moment:** Next October, Pablo inherits the billing service after Farah has left, and finds `requests==2.28.1  # do not upgrade`. He is afraid to touch it; with this, the line links to Farah's own words and to a ready MR saying her reason was fixed upstream last month.
- **Flow:**
  1. When a person approves an MR (merge request "approved" trigger), the flow reads the diff and decides which lines are promises to the future: pins, skipped or quarantined tests, new feature flags, retries with magic numbers, TODOs with a condition.
  2. It asks the author one question on the MR thread: "What would have to be true to remove this?"
  3. The author answers in plain words. The flow turns the answer into a checkable condition ("upstream issue X closed", "flag at 100% for 30 days", "test passed 20 runs in a row") and commits it to a `WHY.yml` registry on the MR branch; a person merges it with the MR.
  4. A weekly pipeline schedule owned by a person (unverified as a human trigger), or the team lead's monthly mention, starts the check run. Code checks each condition (upstream issue state through the network allowlist, flag history, test history); the model handles the conditions code cannot read directly.
  5. For each condition that has come true, the flow opens a removal MR that quotes the author's original words and assigns it to the current owner (CODEOWNERS). A person merges.
- **Stages:** plan, create, verify, package, configure, govern.
- **Autonomy:** Supervised: the agent finds, asks, checks and prepares; people merge.
- **Model and code:** The model may spot the promises, phrase the question, turn answers into conditions and open removal MRs. It may not merge, delete flags or unpin on its own. Code decides whether each condition is met.
- **Demo moment:** The MR thread: "Farah, Oct 2026: 2.29 breaks our proxy login; safe once the upstream issue is fixed." Cut to a staged "one year later": "Farah's condition is met. Unpin requests?" with a green pipeline.
- **Nearest crowded:** Onboarding aids and organisational memory (LORE, the February grand prize). This does not mine history to answer questions: it asks one question at the moment of change, stores a condition that code can check, and acts when it comes true (flag and dependency hygiene).
- **Sibling overlap:** Plane Mode (2.1 there) also asks the one person while she remembers, before a release. Dear Successor asks at the pin, skip or flag, and closes the loop later with a removal MR.
- **Biggest risk:** The "a year later" half must be staged for the demo; turning free-text answers into reliable checks.

### 1.9 Kind Revert

- **Pitch:** When a newcomer's merged change is reverted after a bad deploy, they get the reason, a failing test that shows it, and an invitation back, instead of silence.
- **Person and moment:** Kwame's first contribution was merged on Monday and reverted on Tuesday with only "Revert 'Fix date parsing'" as the message. Nobody explains, and he decides open source is not for people like him.
- **Flow:**
  1. After errors in production, a maintainer uses GitLab's Revert button and opens a revert MR (merge requests, deployments). The merge request "created" trigger (GitLab 19.4) starts the flow.
  2. The flow decides where the reason lives: the incident, error tracking events after the deploy, failed post-deploy checks, the maintainer's notes. It finds the stack trace and the input that broke (for example two-digit years).
  3. It writes the smallest test that reproduces the failure and pushes it to a branch; code runs it and requires that it fails with Kwame's change and passes without it.
  4. It drafts a note for Kwame: what happened, the input, the test, how to run it, and "your next MR can start from this branch". The maintainer edits and approves it (a human input step, or a reply), and it is posted on Kwame's original MR.
  5. When Kwame opens a new MR from that branch, the test is already there, so a reviewer can see at once that the case is covered.
- **Stages:** plan, create, verify, monitor.
- **Autonomy:** Assisted: nothing reaches the newcomer without the maintainer.
- **Model and code:** The model may investigate, write the test and write the note. It may not post without the maintainer, re-merge anything, or judge the contributor. Code checks that the test fails on the reverted change and passes on main.
- **Demo moment:** Kwame's notification: "Your change was reverted. That happens to everyone here. Dates like 03/04/25 broke it; this test shows it; this branch is ready for you." Then a new MR from Kwame, green.
- **Nearest crowded:** Incident root cause (walking from a deploy back to the MR). The culprit is already known from the revert; the product is a reproduction test and a message that brings the newcomer back.
- **Biggest risk:** Staging a believable revert story with one builder (a second account plays Kwame); whether the "created" trigger fires on a revert MR is unverified.

### 1.10 Forget Me (added after reading the sibling file)

- **Pitch:** After each release, the agent proves that a deletion request still deletes everything, including the new places this release keeps personal data.
- **Person and moment:** Laila will ask the app to delete her account next month, after leaving an abusive partner. This week's release adds a search index that copies every address, and the deletion job has never heard of it.
- **Flow:**
  1. A person merges the release MR and the pipeline deploys to staging (CI/CD, environments). The staging pipeline's "passed" event starts the flow.
  2. The flow reads the release diff and decides where personal data could now live: new tables or columns, new log lines with user fields, new analytics events, exports, caches, search indexes, calls to outside services.
  3. Code creates a canary person in staging, a synthetic user with a unique marker string in every field. The flow chooses the journeys that reach the new stores and drives them as that user; then code runs the real deletion job, the same path support uses.
  4. Code searches every known store, plus every new store the flow found (database tables, logs, the search index, bucket exports), for the marker. Any hit is a gap, with its exact location.
  5. The flow posts the result on the release: "Erasure complete: 0 traces in 9 stores", or "Gap: marker found in search index addresses_v2 after deletion". For a gap it drafts an MR that adds the store to the deletion job; the production deploy waits on a deployment approval and the privacy lead decides.
- **Stages:** verify, secure, release, monitor, govern.
- **Autonomy:** Supervised: the privacy lead approves the outcome. A Hands-off variant fits: a clean result lets the release go on by itself.
- **Model and code:** The model may decide where personal data could now be stored and which journeys reach it, and draft the deletion-job MR. It may not approve the release, change the deletion job without review, or touch production data. Code plants the canary person, searches for the marker and decides whether there is a gap.
- **Demo moment:** A list of stores, eight green ticks and one red: "addresses_v2 (search index, added in !318): marker LAILA-CANARY-7731 still present after deletion." The deploy waits; the fix MR adds one line to the deletion job.
- **Nearest crowded:** Security scanning (secret and pattern detection). This is not a pattern scan: it proves end to end, with a planted person, that the deletion promise still holds after each release. Compliance evidence for auditors is an open space.
- **Sibling overlap:** Log Leak (2.8 there) finds personal data in new log lines after a release. Forget Me tests erasure across every store.
- **Biggest risk:** The demo app needs several real stores on Google Cloud (database, logs, a small index or bucket), and searching them from a CI job or the flow needs access through Workload Identity Federation and the network allowlist (unverified).

## Lens 2: Rituals from other crafts

High-stakes crafts have spent decades on how to hand over work and when to act. Each concept borrows one mechanism, names it, and maps it onto the post-code lifecycle.

### Banned: the three most obvious answers

1. **BANNED:** the surgical checklist as a release checklist bot (an agent ticks a pre-deploy checklist).
2. **BANNED:** hospital shift handover as a handoff notes generator (an agent writes the on-call summary).
3. **BANNED:** the bomb squad's two-person rule as "two approvals before production".

Close variants also left out: go or no-go polls (mission control), pre-flight checklists, aviation-style blameless post-mortem writers, war-room chat summaries.

### 2.1 Cue Light

- **Craft and mechanism:** Theatre stage management. Cues are numbered in the prompt book. The stage manager warns "standby cue 12" (a cue light comes on at the operator's post), the operator answers "standing by", and only the stage manager says "go" (the light goes out). Anyone can call "hold". Before opening night, a cue-to-cue rehearsal runs only the cues and skips the scenes between them.
- **Pitch:** A risky rollout becomes a numbered list of cues. The agent prepares each cue and calls "standby"; only a person says "go".
- **Person and moment:** Ines, a junior engineer, runs her first production rollout of the new checkout. Instead of a wiki page and a nervous chat thread she has a cue sheet: each cue is ready, she says go, and the agent reports "complete" before it calls the next standby.
- **Flow:**
  1. When the release MR is approved (merge request "approved" trigger), the flow writes the cue sheet from the change: numbered cues (run the migration, deploy region 1, flag to 5%, warm the cache, flag to 50%, flag to 100%, remove the old path), each with a "you'll see" line and a "hold if" line, committed as `cues.yml` and mirrored to a rollout issue.
  2. Cue-to-cue: the commit starts a pipeline whose generated child pipeline runs every cue against staging without the waits (CI/CD, child pipelines, environments). Code checks each "you'll see" condition, and the result goes on the issue.
  3. Show time: the flow posts "Standby cue 3: new_checkout to 5% in production. You'll see 5% of sessions on v2. Hold if checkout errors pass 1%." The people the cue names (support lead, on-call) answer "standing by", and the cue's job checks that every needed answer is in before it does anything.
  4. Ines says go by playing cue 3's manual job; production cues also sit behind a deployment approval (protected environments, Feature Flags API inside the job). GitLab already requires a person to fire a trigger; here that rule is the craft.
  5. The cue job itself watches the cue's signals for its dwell time (code). When it passes or fails, the pipeline event wakes the flow, which reports "Cue 3 complete", or calls "Hold" and readies the reverse cue (3R), then calls the next standby. At the end it writes the show report on the release.
- **Stages:** plan, verify, release, configure, monitor.
- **Autonomy:** Assisted: a person says go at every cue.
- **Model and code:** The model may write the cue list from the change, choose what to watch for each cue, explain the signals, and call standby. It may call hold early if it sees something the thresholds miss, because a hold only stops the show. It may not fire a cue, skip one or reorder the list during the show. Code holds the cue state (no go before standby is acknowledged, one cue at a time), the hold thresholds and the acknowledgements.
- **Demo moment:** The issue reads like a show: "Standby cue 4" / "Standing by" / "Go" / "Cue 4 complete: 50% on v2, errors 0.2%" / "Standby cue 5". At cue 5 a planted fault: "HOLD. Errors 3.1%. Reverse cue 5R ready."
- **Nearest crowded:** Release gatekeepers (deploy, check, ship or roll back), and the banned checklist bot. The agent never decides to ship and ticks no list: it paces a person through a rehearsed cue sequence with standby, go and hold, which suits feature flag rollouts (configure, an open space).
- **Sibling overlap:** Daylight Rollout (1.8 there) also paces a flag rollout around people (it holds at night). Cue Light is the standby, go and hold protocol plus the cue-to-cue rehearsal.
- **Biggest risk:** Many moving parts (two environments, flag writes from CI, one manual job per cue) and keeping the show state right across separate flow runs, each started by a different human action.

### 2.2 Sponge Count

- **Craft and mechanism:** Surgery. The scrub nurse and the circulating nurse count every sponge, needle and instrument at the start, before closing, and at skin closure. If the count does not match, closing stops until the item is found. (The count is one line of the WHO checklist's sign-out; the mechanism borrowed here is reconciling items that were found, not ticking fixed boxes.)
- **Pitch:** Before an incident is closed, the agent counts everything people opened during it (flags, alert silences, scale-ups, debug logging, temporary access) and confirms each one was put back.
- **Person and moment:** Marco led a three-hour incident and wants to go to bed at 5 a.m. He goes to close it and the count reads 9 opened, 8 closed: `debug_payments_logging` is still on and writing card fragments to the logs (demo), which nobody would have noticed for weeks.
- **Flow:**
  1. The incident commander assigns the incident to the count flow (assign trigger).
  2. The flow decides where temporary changes hide: the incident timeline and comments ("I bumped replicas to 10"), audit events, feature flag changes, CI/CD variable changes, deployments and manual jobs since the incident started, membership changes that granted access, job logs of ad-hoc commands. It builds the count sheet: what was opened, by whom, when.
  3. Code checks the current state of each item through the API ("flag debug_payments_logging: on, 100%"; "temporary Maintainer for marco: still active").
  4. The flow posts the count on the incident: opened 9, closed 8, missing 1, each missing item with a prepared restore (a manual CI job, or an MR back to the original value).
  5. A person runs each restore or marks the item "kept on purpose" with a reason. When the count balances, the flow adds the timeline event "Count correct"; if the incident is closed early, the flow reopens it and posts the count.
- **Stages:** secure, release, configure, monitor, govern.
- **Autonomy:** Supervised: the agent finds and checks; people restore and close.
- **Model and code:** The model may decide where to look, read free text for changes nobody logged, pair "opened" with "closed" events and prepare restores. It may not restore anything itself or close the incident. Code checks each item's live state and decides whether the count balances.
- **Demo moment:** "Opened 9. Closed 8. Missing: debug_payments_logging, on since 02:41, set by marco." Marco clicks the prepared job. "Count correct." He closes the incident.
- **Nearest crowded:** Incident root cause and post-mortem writers. This ignores the cause entirely; it reconciles temporary changes against live state before close.
- **Sibling overlap:** Close to Loose Ends (1.4 there), which tracks leftovers until the fix ships. Sponge Count reconciles at close, like a count, and includes temporary access.
- **Biggest risk:** Reading audit events and variable history may need a higher role or tier (unverified); the demo needs a staged incident with realistic temporary changes (labelled demo).

### 2.3 Standing Orders

- **Craft and mechanism:** Hospital standing orders. A doctor writes an order in advance ("if potassium falls below 3.5, give X and recheck in 4 hours"); a nurse may carry it out without calling, exactly as written and only under its conditions. Orders carried out overnight must be countersigned by the doctor within a set time.
- **Pitch:** Before going off shift, the on-call engineer signs a few narrow "if this, then that" orders the agent drafted from today's changes; overnight, plain code carries them out exactly; in the morning she countersigns.
- **Person and moment:** At 6 p.m. Esther signs three orders, including "if checkout errors pass 5% for 5 minutes while flag new_pricing is on, turn the flag off". At 3:12 a.m. it happens, the flag goes off, nobody's phone rings, and at eight she reads one paragraph and countersigns.
- **Flow:**
  1. At the end of the day Esther assigns the "Tonight" issue to the flow (assign trigger). The flow reads today's deployments, flag changes, migrations and open incidents, and decides what could go wrong tonight and which narrow, reversible action would contain each risk.
  2. It drafts the orders as an MR to `standing-orders.yml`: condition (metric, threshold, duration), one action from an allowlist (flag off, scale to N, roll back service X to its previous deployment), expiry (8 a.m.), and who to page if an order fires twice.
  3. Esther edits and merges the MR; the merge is the signature (approval rules, CODEOWNERS on the file).
  4. Overnight, plain code (a Cloud Run job or a scheduled pipeline) checks the signed conditions against monitoring and, when one is met, runs exactly the signed action (Feature Flags API, rollback job) and records it as an incident timeline event. No model runs at night.
  5. In the morning Esther mentions the flow on the countersign issue; it investigates what happened around each fired order and writes a short account. She countersigns or flags it for review. Unused orders expire.
- **Stages:** plan, release, configure, monitor, govern.
- **Autonomy:** Hands-off overnight, inside bounds a person signed; a signature at dusk and a countersignature at dawn bracket every night.
- **Model and code:** The model may propose orders and thresholds, explain each, and investigate in the morning. It may not act at night, put an order live without the merge, or pick an action outside the allowlist. Code evaluates conditions, runs the actions, and enforces expiry and the allowlist.
- **Demo moment:** A clock at 03:12; the flag turns off by itself and the incident gets one line: "Standing order 2 carried out (signed by Esther at 18:04)." The phone stays dark. 08:00: "Countersign?" Esther approves.
- **Nearest crowded:** Auto-rollback in release gatekeepers (ZeroTouch Monitor, BABYDOV). No agent decides to roll back: a person pre-authorises one narrow action in writing, code carries it out, and the person countersigns. The model drafts by day and explains by morning.
- **Sibling overlap:** Nearly the same as Night Orders (1.1 there). Differences: no model runs at night here (code only), and the morning countersignature is a formal step.
- **Biggest risk:** Writing flags and running rollbacks from an unattended job needs a token with api scope (CI/CD variables may need Maintainer, unverified); a believable night fault for the demo (simulated, labelled demo).

### 2.4 Lockout Tagout

- **Craft and mechanism:** Industrial lockout and tagout. Before maintenance, each worker isolates every energy source and puts their own padlock and tag (name, reason) on each isolation point. With several workers there are several locks on one hasp, and the machine cannot restart until the last person removes their own lock. A "try-out" attempts to start the machine to prove it is isolated.
- **Pitch:** When a person has to work on production by hand, the agent finds every automation that could touch it (deploy jobs, schedules, auto-merge, other agents' flows) and puts that person's lock on each one.
- **Person and moment:** Aiko is repairing corrupted rows in the orders table at 11 p.m. Halfway through, an auto-deploy runs a migration on that table and another team's agent opens a "fix" MR; with her lock on, nothing moves until she removes it herself.
- **Flow:**
  1. Aiko opens a lockout issue naming the target (production, the orders service, the orders table) and assigns it to the flow (assign trigger).
  2. The flow decides where "energy" can come from: CI jobs that deploy to that environment (it reads `.gitlab-ci.yml` and its includes), pipeline schedules, MRs with auto-merge set, Duo flow triggers on the project, cron jobs in the code, outside schedulers it can see. It lists the isolation points with reasons.
  3. Aiko confirms the list and clicks the "apply lock" manual job, and code applies her lock: a deploy freeze on the environment, schedules paused, auto-merge cancelled, Duo triggers switched off (GitLab 19.4 can turn triggers off without deleting them; doing it from a job is unverified), each tagged "Locked by Aiko: orders repair".
  4. Try-out: code starts a harmless deploy-shaped job and checks that it is blocked (the job sees `CI_DEPLOY_FREEZE`). The result is posted on the lockout issue: "isolated".
  5. When Aiko removes her lock (her own "remove lock" job), code restores exactly what it changed. If Raj also locked, the freeze stays until Raj removes his.
- **Stages:** verify, release, configure, monitor, govern.
- **Autonomy:** Supervised: a person confirms the isolation list; code applies and removes the locks.
- **Model and code:** The model may discover isolation points and explain them. It may not remove anyone's lock, drop a point the person chose, or run deploys. Code keeps the lock registry (who holds what), applies and restores each change, and runs the try-out.
- **Demo moment:** Aiko's issue shows six padlocks with her name. A scheduled deploy tries to run and stops: "Locked by Aiko (orders repair)". She removes her lock and everything comes back, one item at a time.
- **Nearest crowded:** None directly; deploy freezes are a manual GitLab feature today. It sits next to release gatekeepers but judges no release: it holds every automation still while a person works. It is the theme question turned around: not how far agents go without you, but how you stop all of them when you need the floor.
- **Biggest risk:** Freeze periods, schedule changes and trigger toggles may need Maintainer in the provisioned project (unverified); restoring state exactly needs careful code.

### 2.5 Decision Height

- **Craft and mechanism:** Aviation, the instrument approach. Before the approach the crew briefs a decision height. Above it, any doubt means "go around", a normal, practised, blameless manoeuvre. At decision height the pilot must see the runway or go around. Below it, the aircraft is committed to land.
- **Pitch:** The agent flies the release on its own while every step can still be undone, and hands the decision to a person at the first step that cannot be undone.
- **Person and moment:** Oskar's team ships a release that ends by dropping an old database column. Everything before the drop runs and reverses on its own; at the drop, Oskar gets one question with the evidence, and he is the one who says "land".
- **Flow:**
  1. When the release MR is approved (merge request "approved" trigger), the flow reads the release's steps (deploy jobs, migrations, flag changes, outbound calls) and classifies each as reversible or not, with a reason: "flag to 50%: reversible", "DROP COLUMN: irreversible", "email to all users: irreversible", "package publish: irreversible".
  2. Code applies hard rules on top (any DROP, any DELETE without WHERE, any package publish or bulk email is irreversible, whatever the model said) and writes the release as dynamic child pipelines: the steps above decision height run automatically, and the landing step is a deploy job behind a protected-environment approval (CI/CD, child pipelines, deployments and approvals).
  3. Above decision height the pipeline runs alone (staging, canary, backfill). If code sees a set signal (error rate, failed check), it runs the go-around: automatic reversal of the steps so far, reported as routine, not as a failure.
  4. When the steps above decision height pass, the pipeline event wakes the flow, which posts the brief beside the waiting approval: what happened above, what the step does, what cannot be undone, the backup taken a minute ago.
  5. Oskar approves ("land") or declines ("go around", with the reversal ready). The flow records the flight on the release (releases).
- **Stages:** verify, release, configure, monitor, govern.
- **Autonomy:** Hands-off above decision height and a person exactly at the irreversible step, so Supervised for the release as a whole. It answers "how far can your agents go without you?" with "as far as everything can be undone".
- **Model and code:** The model may classify steps, explain what cannot be undone and prepare reversals. It may not mark a step reversible against a code rule, or pass decision height without a person. Code holds the rule floor, the go-around signals, the generated pipeline and the gate.
- **Demo moment:** A strip of steps turns green by itself; a planted canary error triggers "Go-around: steps 3 to 1 reversed, nothing lost." Second try: "Decision height: DROP COLUMN legacy_email. Cannot be undone. Backup taken 14:02. Land?" Oskar approves.
- **Nearest crowded:** Release gatekeepers (BABYDOV's GO, HOLD, ROLLBACK). The gate is not a risk score or a test result; it sits exactly at the first irreversible step, found by the model and floored by code, and everything above it runs and reverses alone.
- **Sibling overlap:** Return Ticket (2.2 there) also puts the person at the one-way step; it proves the way back and splits one-way changes. Decision Height lets the agent run alone and go around by itself above that step.
- **Biggest risk:** A demo release with both kinds of steps and believable reversals; in a 3-minute video it can look like another gatekeeper unless the reversible-or-not view is the hero.

### 2.6 Heat Lamp

- **Craft and mechanism:** The kitchen expediter at the pass. Finished plates wait under the heat lamp and die there. The expo knows how long each plate has waited, checks it, and calls "Hands!" so one server carries it out now.
- **Pitch:** Finished work dies while it waits. The agent finds fixes that are merged but not delivered and calls the one person who can carry each one out, with everything ready.
- **Person and moment:** Rosa reported that her receipts show the wrong VAT; the fix was merged 16 days ago, but production still runs last month's release because promotion is a manual job nobody owns. She has written to support twice, and the support agent has run out of ways to say sorry.
- **Flow:**
  1. Each morning the release owner assigns the day's "Pass" issue to the flow, the way an expo opens the pass (assign trigger; a pipeline schedule is the alternative, unverified as a human trigger).
  2. The flow decides what is sitting at the pass after merge: commits on main that production does not run yet (main compared with the production environment's last deployment), staging deployments never promoted, flags left at a partial rollout for weeks, fixes linked to open Service Desk tickets. For each, it finds why it is stuck (a failed manual job, a missing approval, no owner).
  3. Code computes each plate's age, who may carry it (protected environments, approval rules) and which customers are waiting (linked tickets), and limits calls to one person per plate per day.
  4. The flow makes each plate as ready as it can without acting on it (checks the last pipeline is green and recent, drafts the promotion summary), then calls "Hands": one mention to one person, with the age, who is waiting, and the single action.
  5. The person carries it (plays the deploy job, approves the deployment). The Pass issue shows each plate's time under the lamp, and the flow drafts the "it's live" note for support to send to Rosa.
- **Stages:** plan, verify, release, configure, govern.
- **Autonomy:** Supervised: it prepares and calls; people carry.
- **Model and code:** The model may work out why each plate is stuck and which one action frees it, and write the call. It may not deploy, approve, or call more than one person per plate per day. Code computes ages, permissions and call limits.
- **Demo moment:** "Hands, @owner: the VAT fix has waited 16 days under the lamp. Two customers are waiting. Pipeline green 3 minutes ago. One click: deploy." The click, the deployment, and Rosa's ticket gets its answer.
- **Nearest crowded:** Stale-MR nudge bots (a close variant of banned answer 3 in lens 1) and issue triage. This starts after merge (undelivered merges, stuck promotions, stale partial rollouts), prepares the plate so the call is one click, and calls one person per plate.
- **Biggest risk:** The demo needs believable history (merged but undeployed commits, a stuck flag) across environments; finding who may carry a plate may need read access to protected environment settings (unverified).

### 2.7 Readback

- **Craft and mechanism:** Air traffic control. A flight moves to the next sector only when the receiving controller accepts it. Pilots read back every clearance, and the controller listens to the readback for errors ("hearback"). Responsibility moves only on an explicit accept.
- **Pitch:** When on-call passes to the next time zone, the incoming engineer reads back what she is taking over, and the agent checks that readback against everything actually in flight.
- **Person and moment:** Mei in Singapore takes over from Carlos in Berlin. She reads back "two incidents, both quiet", and the agent hears back: "You missed one: a migration paused at 40% on eu-west, and an alert silence that runs out at 11:00."
- **Flow:**
  1. Carlos assigns the handover issue to Mei. Mei writes her readback in her own words and mentions the flow (mention trigger).
  2. The flow decides what counts as in flight now: open incidents and their status, environments mid-deployment, flags mid-rollout, running or paused migration jobs, pending deployment approvals, deploy freezes, alert silences or schedule overrides with an expiry, MRs set to auto-merge toward production.
  3. Code builds the true list from the API (the strip board). The model compares Mei's readback with it item by item and finds what she missed or misread ("quiet" when it is "paused, needs a decision by 14:00").
  4. The flow replies with the hearback: confirmed, corrected, missing, each linked. Mei corrects her readback.
  5. When she says "accept" and code confirms her readback now covers every item, the flow moves the in-flight items' assignee from Carlos to Mei (a step that runs only if that check passed) and records the time. Until then, Carlos stays the owner.
- **Stages:** release, configure, monitor, govern.
- **Autonomy:** Assisted: each step starts from a person and ends with a person's accept.
- **Model and code:** The model may compare the readback with the live list and explain misunderstandings. It may not write the handover for Carlos or move ownership before Mei accepts. Code builds the live list, checks coverage and gates the transfer.
- **Demo moment:** Mei's readback with a red line under it: "Missed: orders_backfill paused at 40% (eu-west) since 06:10." She adds it. "Readback correct. 4 items now assigned to Mei."
- **Nearest crowded:** The banned handoff notes generator. The agent writes no notes: the receiver speaks first, the agent checks her understanding against live GitLab state, and ownership moves only on a correct readback. This is the concept here closest to a banned answer.
- **Biggest risk:** A complete in-flight list (silences and paused jobs may not be readable by the flow); playing two people in the demo with one builder.

### 2.8 Fight Call

- **Craft and mechanism:** The theatre's fight call: before every performance, the actors walk through each stage fight at half speed with the fight captain, so nobody gets hurt that night. (Ships do the same with fire and abandon-ship drills on a fixed schedule.) Practise the dangerous moves when nothing is at stake, slowly, and fix what you find.
- **Pitch:** The agent walks your emergency runbooks step by step in staging during the day, so nobody finds a broken step at 3 a.m.
- **Person and moment:** At 3 a.m. Tariq opens the "Restore from backup" runbook, and step 4 points to a storage bucket that was renamed in March. He spends 40 minutes searching while the site is down; with fight calls, that step was caught and fixed on a Tuesday afternoon.
- **Flow:**
  1. Once a week the on-call lead assigns the fight call issue to the flow (assign trigger), or a pipeline schedule starts it (unverified as a human trigger).
  2. The flow picks which runbook to walk (the one walked longest ago, or one whose commands touch code that changed since), reads its prose steps from the repo or wiki, and turns each into a command or API call to try in staging.
  3. It runs the walk-through in staging step by step (`run_command` in its sandbox with staging-only credentials through `id_tokens`, or manual CI jobs in a "drill" environment). When a step fails, it looks for the working form (the tool's help output, the current config, recent MRs that renamed things). Code checks each step's expected result (exit code, health check, restored row count) and times it.
  4. For each broken or stale step it opens an MR that fixes the runbook text, with the old command, the error and the working command as evidence (`create_branch`, `create_commit`, `create_merge_request`), and records the time against the target recovery time.
  5. A person reviews and merges. The log goes on the runbook's issue: "last walked Tuesday, 14 minutes, step 4 fixed".
- **Stages:** verify, release, configure, monitor, govern.
- **Autonomy:** Hands-off in staging (walking runbooks there is safe); a person merges runbook changes, so Supervised overall.
- **Model and code:** The model may choose the runbook, turn prose into commands, try alternatives when a step fails, and write the fix. It may not touch production, merge, or skip a step without saying so. Code checks results and timings and enforces the staging-only boundary (staging credentials only, network allowlist).
- **Demo moment:** The log: "Step 4 failed: bucket backups-prod not found (renamed to prod-backups in !211). Working command found. Runbook MR !88 opened. Restore took 14 minutes (target 30)." A person merges.
- **Nearest crowded:** Rollback rehearsal (BABYDOV) and incident tooling. This walks the human runbooks themselves, finds rot in the prose and fixes the document; it gates no release.
- **Sibling overlap:** Fire Drill (1.6 there) trains a new engineer on a staged outage, and its debrief also fixes runbooks. Fight Call has the agent walk the runbooks itself, on a schedule, with no person on stage.
- **Biggest risk:** An agent running commands needs a tightly limited staging (credentials, network); a restore drill needs a real backup to restore, which costs money or needs a small database in CI; turning prose into commands can wander.

### 2.9 Small Pour

- **Craft and mechanism:** The sommelier's tasting. The sommelier presents the label (right wine, right vintage), opens the bottle and pours a small taste for the host, who checks for faults such as cork taint, not for preference. Only a sound bottle is served to the table.
- **Pitch:** Before a dependency upgrade reaches production, the agent pours a small taste: it runs the exact calls your code makes against the old and the new version and reports "sound" or "corked".
- **Person and moment:** Nadia maintains a small open-source tool alone and has a pile of dependency MRs open. She merges none, because one bad upgrade last year broke her users' builds for a weekend; with a taste note on each, she merges most of them in ten minutes and keeps three for a closer look.
- **Flow:**
  1. A dependency bot opens upgrade MRs; Nadia assigns the flow as reviewer on them (assign reviewer trigger; bot actions cannot fire triggers, so her assignment is the start).
  2. Present the label: code checks the version, lockfile hashes, publish date, and whether the package's maintainers changed recently.
  3. The flow finds every call site of the package (`grep`, `read_file`), decides which matter (parsing, dates, encoding, public API), and writes small probe scripts that call those functions with inputs taken from the project's own tests and fixtures.
  4. Code runs each probe against the old and the new version in two virtual environments in the sandbox (`run_command`, package index in the network allowlist) and compares outputs, exceptions and timings. Any difference is a fault candidate, with the exact input.
  5. The flow posts the taste note on the MR: "Sound: 14 call sites, identical results", or "Corked: parse_date('03/04/25') now returns 3 April, was 4 March". Nadia merges or closes.
- **Stages:** verify, package, secure, release.
- **Autonomy:** Supervised. A Hands-off variant fits too: auto-merge patch upgrades that taste sound, if the maintainer sets that policy.
- **Model and code:** The model may pick call sites and inputs, write probes and explain differences. It may not merge, change the code to fit, or call a bottle sound when code found a difference. Code runs the comparison and the label checks.
- **Demo moment:** Two taste notes side by side: one "Sound" merged in one click, one "Corked" with the input and both outputs.
- **Nearest crowded:** Security fixers and dependency scanning, and CI fixers. It looks for no CVEs and fixes no builds: it compares the behaviour of the calls you actually make, old against new, in the open "dependency upgrades" space.
- **Sibling overlap:** Nearly the same scene as Fine Print (2.5 there), which reads changelogs and proves the lines that touch our code with tests. Small Pour skips the changelog and compares the two versions directly on your own call sites.
- **Biggest risk:** Choosing probe inputs that show real differences; package installs and run time inside the flow sandbox.

### 2.10 Site Mark (added after reading the sibling file)

- **Craft and mechanism:** Surgery's site marking. Before anaesthesia, while the patient is awake, the surgeon marks the operation site with a pen and the patient confirms it; at the time-out the team checks the mark. The person who knows the body takes part in marking it. (Not the checklist: the mechanism is the awake patient confirming the exact site.)
- **Pitch:** For one-off production data fixes, the agent finds the exact records, the customer who asked confirms them, and code refuses to touch any record that was not marked.
- **Person and moment:** Mr. Brennan asked support to remove one duplicate invoice from March. Last year a hand-written fix with a loose WHERE clause deleted all eleven of his March invoices, and his accountant spent a week rebuilding them.
- **Flow:**
  1. The request arrives through Service Desk, and the support agent assigns it to the flow (assign trigger).
  2. The flow investigates a staging copy or a read replica: it decides which tables and queries identify what the customer means ("the duplicate from March" is invoice 4472: same amount and date as 4471, created 3 seconds later) and writes the fix as a script in an MR (`create_branch`, `create_commit`, `create_merge_request`).
  3. Code dry-runs the script in a transaction that is rolled back (a CI job) and records the exact set of affected row IDs.
  4. Marking the site: the flow drafts a plain confirmation for the customer ("We will remove invoice 4472, 12 March, 89.00 EUR. Invoice 4471 stays.") as an internal note; the support agent sends it; the customer replies "yes, that one". The confirmed IDs are written to the MR as the mark.
  5. Time-out: the production job (protected environment with a deployment approval) runs the script only if code finds the dry-run set equals the marked set exactly, inside a transaction that aborts if any other row would change. An engineer approves the deployment.
- **Stages:** plan, create, verify, release, govern.
- **Autonomy:** Assisted: people confirm the site and approve the run.
- **Model and code:** The model may find the records, write the script and phrase the confirmation. It may not run anything on production, widen the set after marking, or send the confirmation. Code decides the dry-run set, its equality with the mark, and the transaction guard.
- **Demo moment:** The MR shows "Marked by the customer: invoice 4472" beside "Dry run affects: 4472". In a second take, a planted bug makes the dry run hit 11 rows and the job refuses: "Site mismatch: 11 rows, 1 marked."
- **Nearest crowded:** None of the crowded spaces; production data fixes are everyday operations work. Closest are database migration tools (the February DB Migration Safety Checker, and Row Call above). This is a one-off fix a customer asked for, and the person who asked confirms the exact records.
- **Biggest risk:** A realistic demo database and a safe read path for the flow (a staging copy); a believable support story with one builder.

### 2.11 Med Rec (added after reading the sibling file)

- **Craft and mechanism:** Hospital medication reconciliation. At every transition of care (admission, transfer, discharge), a nurse or pharmacist compares the medication lists before and after, line by line, to catch omissions, duplicates and doses changed by mistake. Each difference is either intended, with a reason, or fixed.
- **Pitch:** Before a change moves from staging to production, the agent reconciles what each environment "takes" (variables, secret names, flags, limits, service settings) and asks a person to settle every difference.
- **Person and moment:** Kenji deploys on a Thursday afternoon and production crashes, because the release reads `TAX_API_URL`, which exists only in staging. He spends the evening apologising in the incident channel for a line of config nobody compared.
- **Flow:**
  1. When the release MR is approved (merge request "approved" trigger), the flow starts.
  2. The flow reads the release diff and decides what configuration the new code needs: new environment variable reads, new flag checks, new secret names, new service settings (memory, timeouts, concurrency), new outbound hosts.
  3. Code in a CI job builds both "medication lists": CI/CD variable names scoped to each environment, Cloud Run settings per service and environment (read through Workload Identity Federation), flags per environment scope, secret names in Secret Manager. It compares names and hashes only, so the model never sees a secret value.
  4. The flow posts the reconciliation on the release MR: each difference marked "needed by this release and missing in production", "different on purpose (reason from last time)", or "unexplained", with a link to the code that reads it.
  5. A person settles each line: adds the missing setting through a reviewed change, or marks it intended with a reason that is remembered next time. The production deployment approval waits until no line is unexplained (deployments and approvals).
- **Stages:** verify, secure, release, configure, govern.
- **Autonomy:** Supervised: the agent reconciles; a person settles the differences and approves the deploy.
- **Model and code:** The model may decide what configuration the change needs, explain differences and propose the missing settings. It may not see secret values, change production configuration, or approve the deploy. Code builds the lists, compares names and hashes, and decides whether any line is unexplained.
- **Demo moment:** A reconciliation table with one red line: "TAX_API_URL: read in billing/tax.py line 14 (added in !402), set in staging, missing in production." Kenji adds it, the line turns green, and he approves the deploy.
- **Nearest crowded:** Release gatekeepers. It judges no code or tests; it reconciles configuration between two environments at the moment of transition, driven by what the new code reads.
- **Biggest risk:** Reading CI/CD variables and Cloud Run settings needs permissions (variables may need Maintainer, unverified); the "model never sees a secret" boundary must be built in from the start.

### 2.12 Understudy (added after reading the sibling file)

- **Craft and mechanism:** Theatre understudies. Every lead role has an understudy who learns the part, rehearses it separately, and must be ready to go on tonight if the lead is ill. The show never depends on one body.
- **Pitch:** The agent finds post-code tasks that only one person has ever done (cutting a release, rotating keys, restoring a backup, renewing a certificate) and arranges for an understudy to do the next one, with a script built from the lead's last run.
- **Person and moment:** Gloria is the only person who has ever cut a release or rotated the payment keys, and she has not had a phone-free holiday in three years. This year her understudy has done both twice, and she leaves her phone at home.
- **Flow:**
  1. Once a month the team lead assigns the "Understudies" issue to the flow (assign trigger).
  2. The flow decides which tasks count: manual jobs played, deployments to production, releases created, protected-branch merges, runbook-driven jobs. Code counts distinct performers for each over the last six months from GitLab history (jobs, deployments, releases, audit events where readable).
  3. For each task with one performer, the flow builds the understudy script from the lead's last run: the job logs, the commands and their order, the checks the lead did by eye (from comments), the places the lead paused (long gaps). It proposes an understudy from who has touched the related code; the lead approves.
  4. The next time the task is due, the flow opens it as an issue assigned to the understudy, with the lead as reviewer. The understudy performs every step (plays the manual jobs, approves the deployment); the lead watches.
  5. Afterwards the flow updates the script with what differed and marks the task "two performers". The issue keeps the cast list: each critical task and who can go on tonight.
- **Stages:** plan, secure, release, configure, govern.
- **Autonomy:** Assisted: people perform every step; the agent finds the gaps, writes scripts and schedules.
- **Model and code:** The model may decide which tasks are critical, build scripts from logs and propose understudies. It may not perform the task or assign anyone without the lead's approval. Code counts performers from history.
- **Demo moment:** The cast list: "Cut a release: Gloria only. Rotate payment keys: Gloria only." One month later: "Cut a release: Gloria, Felix (understudy, 18 Oct)", and Felix's run with the script open beside the pipeline.
- **Nearest crowded:** Onboarding aids (36 in June). It is not codebase questions and answers: it uses GitLab history to find single-performer operations tasks and schedules real performances with a script from the lead's own last run.
- **Sibling overlap:** Plane Mode (2.1 there) interviews the one person who knows before a release. Understudy moves the doing to a second person.
- **Biggest risk:** Enough history to count performers (seeded for the demo, labelled); reading audit events may need a higher role (unverified).

## Parked (generated, not developed)

One line each, so the coordinator can see what else came out of the lenses.

- **Due Credit** (lens 1, the security researcher who reported a vulnerability): keep them informed as the fix moves through backports and the advisory, and ask them to review the advisory text and their credit. Parked: next to the crowded security space, and a real CVE request cannot be filed for a demo.
- **Harbour Pilot** (lens 2, the ship's pilot and notices to mariners): each production environment gets a pilot that knows its local hazards from past deployments, boards each release with a passage plan, and posts a notice after each deploy. Parked: weaker human moment, close to release gating.
- **Wake Turbulence** (lens 2, air traffic separation): deploys to one environment are spaced by the "weight" of each change, so effects can be told apart. Parked: weak human moment.
- **Turnaround Time** (lens 2, mountaineering): before a long incident, the team sets the time it stops fixing forward and rolls back; the agent holds them to it with the rollback ready. Parked: overlaps Decision Height and the sibling's Return Ticket.
- **Sterile Cockpit** (lens 2, aviation): during a critical phase the agent holds non-essential merges and deploys, and answers status questions for the people working. Parked: drifts toward an incident chatbot.
- **Eighty-six** (lens 2, the kitchen's "86"): when a base image or package version goes bad, every in-flight MR, pipeline and environment that uses it is marked at once. Parked: close to security scanning.
- **Watch Alarm** (lens 2, the ship's bridge watch alarm, which calls the captain if the officer on watch stops pressing it): a long supervised operation continues only while its person keeps answering check-ins; if they go quiet, the agent holds at the next safe point and calls the backup. Parked: niche, but a different answer to what "Supervised" should mean.

## Notes across both lenses (not a ranking)

- **The night cluster.** Wake Budget, Standing Orders, Sponge Count and Readback, with the sibling's Night Orders, Loose Ends and Someone Awake, describe one night: sign at dusk, act inside signed bounds or stay silent at night, count before closing, read back at handover, countersign at dawn. They could be one product or one demo.
- **The human-trigger rule as design.** Concepts that must start on their own (Wake Budget at night; the weekly or monthly runs in Dear Successor, Heat Lamp, Fight Call and Understudy) depend on the Flows API or a person-owned pipeline schedule being accepted as a human start (unverified). Most ritual concepts make the rule the design instead: a person's go, signature, assignment, lock or accept is the trigger.
- **Write access.** Changes to flags, freezes, schedules and environments go through a CI job a person starts or an MR a person merges, and messages to customers are posted by a person, because the flow's token reaches only `ai_workflows` endpoints and our base role is Developer. Several concepts need a token with api scope in CI/CD variables, which may need Maintainer (unverified). This decides which concepts are buildable, so it is worth testing first.
- **Guards that keep a person in control.** Pin note tools to internal in the flow YAML so the model cannot email a customer (Try First, Straight Answer, Canary Voices, Site Mark). Keep secret values out of the model's reach (Med Rec). Let code produce the facts the model talks about: spoken text (Spoken Diff), cohorts (Canary Voices), claim checks (Straight Answer), diffs (Row Call, Small Pour), counts (Sponge Count, Understudy), set equality (Site Mark), the marker search (Forget Me).
- **Shared building blocks.** A small demo app on Cloud Run with GitLab feature flags serves Canary Voices, Straight Answer, Cue Light, Standing Orders, Decision Height and Heat Lamp. Service Desk serves Try First, Canary Voices, Straight Answer, Heat Lamp and Site Mark. A browser in the flow sandbox serves Spoken Diff, Try First and Forget Me. Cloud Run revision tags give cheap per-MR previews (Try First).
- **Demo data.** Every concept with customers in it needs seeded people and tickets. Per [AGENTS.md](../../../AGENTS.md) rule 2, label them as demo data in the UI, the README and the file names.
