# Ideas: what we build for Life After Code, and why

Part 5 of the research handoff. Written 2026-10-06 for Alex Velazquez (solo, Path A), entering Life After Code, the GitLab Transcend Hackathon ([rules](https://gitlab-transcend.devpost.com/rules), [RULES_CHECK.md](codex/RULES_CHECK.md)).

Inputs, all in [research/ideas/](research/ideas/): the four lens files, [CANDIDATES.md](research/ideas/CANDIDATES.md), [SCORING_RUBRIC.md](research/ideas/SCORING_RUBRIC.md), the four scorers' files, the combined scores and [score_table.md](research/ideas/score_table.md), and the five build briefs. Also [PATTERNS.md](PATTERNS.md) (what past winners shared) and [FIELD.md](FIELD.md) (who else is building). No new web research was done for this file: every fact comes from a linked note, and anything a note marks (unverified) stays marked. People, shops and numbers in the scenes are invented and would be labelled as demo data.

Contents:

0. Reopened selection, 6 Oct 2026 (current; supersedes section 1 until reviewed)
1. Recommendation (original, superseded)
2. How the ideas were made
3. How they were scored
4. The full scoring table (57 concepts)
5. The five finalists against the five official criteria
6. The top three, one page each
7. The runners-up
8. The recommendation, argued
9. What happens next

## 0. Reopened selection, 6 Oct 2026

**Status: recommendation for Codex review. Nothing in this section is decided until the review comes back.** Sections 1 to 9 below are the original selection from earlier on 6 Oct. Their scores came from AI personas, not judges, and some of their platform assumptions no longer hold (see the [refresh note](research/refresh_2026-10-06.md)).

### 0.1 How this was done

- Primary sources were read again on 6 Oct, 07:35 to 07:50 UTC: the rules, GitLab's Duo Agent Platform docs, the public field and organizer posts about past winners ([refresh note](research/refresh_2026-10-06.md)). The Night Orders code was audited against main at `484c411` ([DECISIONS.md](DECISIONS.md)).
- Four substantially different candidates were chosen from the 57 in sections 1 to 9: Night Orders (on-call authority), No Mouse (accessibility), Forget Me (deletion) and Fine Print (dependency behaviour). Each was rewritten to use only documented capabilities, then attacked by three AI critics (platform, judge, delivery), then compared by two independent AI reviewers with opposite lenses (expected quality, and risk of an incomplete or simulated entry). Everything they wrote, with sources, is in the [panel appendix](research/ideas/concept_panel_2026-10-06.md).
- The choice below is the lead's judgement from that evidence. Model-written bands are opinions with reasons, not scores.

### 0.2 What changed since the first selection

1. **Only a person's action can start a Duo trigger, and there is no schedule trigger.** A Duo flow cannot wake up at 03:12 on its own. The Flows API can start one from code, but a start with a Developer account in the hackathon group is untested.
2. **Flows likely cannot read feature flags or deployments.** Their token scope is accepted by the Issues, Notes, Merge requests, Commits and Files APIs only.
3. **Creating flows and triggers needs Maintainer.** Entrants get Developer plus an unpublished AI role. This is the one gate every candidate shares, and it is still unanswered.
4. **The field is crowded with hands-off release loops** (gate, deploy, verify, roll back). No public entrant covers on-call authority, accessibility, deletion or dependency behaviour, though GitLab itself ships a flow for dependency bumps.
5. **Night Orders has ten confirmed or partly confirmed concerns** in its code, and its browser demo replays recorded inputs.

### 0.3 The four candidates

The same rule runs through all four: the model chooses where to look, code decides what is true, a person decides what matters. All four are Path A and Supervised. Every one depends on the same Maintainer gate.

| | No Mouse | Forget Me | Night Orders (revised) | Fine Print |
|---|---|---|---|---|
| Product | A pipeline check that walks the checkout using only what a screen reader would announce; when the walk breaks, a Duo flow decides whether a harmless redesign or a real barrier, and writes the new path or the issue and fix | On each merge request, a person who does not exist uses the changed feature and asks to be deleted; code searches every store for her marker; a Duo flow keeps the test's map of where data lands current with the change | Before bed the on-call engineer signs up to two flag actions a Duo flow drafted from the day's merges; code may do only those at night; everything else wakes her; at 07:00 it ends | For a dependency bump whose pipeline is still green, a Duo flow writes tests that pin how our code uses each changelog item; CI runs them on the old and new lockfile |
| User and task | Small team with no screen reader user; a redesign silently breaks checkout for blind customers | Developers and privacy owner of an app with a Delete account button; new features create copies the delete path misses | On-call engineer of a small team; woken to flip a flag she already knew was right | Maintainer facing a backlog of upgrade MRs that might silently change behaviour |
| Agent decision that matters | Redesign or barrier, the new path, the cause and the smallest fix | How a test person reaches each new place data lands (journeys, stores, derived names, vendors); later, delete more or keep less | Which merges get an order, the condition that separates this change failing from something else; keep or undo at dawn | Which changelog items touch our code, and the smallest test through our own functions |
| Duo feature | One API-only custom flow (Pipeline events: Failed, fallback `/flow:`); issue and MR tools | Map flow (Merge request: Created) and gap flow started by the privacy lead's mention | Dusk and dawn flows started by the on-call person; the night runs on code alone | Read flow (Assign reviewer); optional fix flow (Mention) |
| Code verifies | Replays every path the agent writes; never accepts a path that presses an unnamed control; order actually placed | Marker present before deletion and absent after; exhaustive store scan; unmapped store blocks | Signature, expiry, measured condition, exact action, exact morning restore | Valid on old lockfile; pass old and fail new means proven change; guards on test scope |
| Human authority | Merges the path or fix; a release job needs a clear walk | Chooses the fix direction by mention; merges; runs the release job | Signs at dusk by reaction; approves pages; countersigns at dawn | Merges or asks for a fix |
| Demo, first 30 s | Black screen, simulated screen reader voice: "Button. Button. Button." Then the red walk and the Duo issue | A parent deletes a child's account; the new share feature; a red probe row where a copy survived | 03:12, a flag turns off under a signed order, the phone stays dark | A green bump MR, then one red row: our function's result changed |
| Closest | GitLab's Fix CI/CD Pipeline flow, Pa11y, Playwright's test repair agent (search excerpt), Evinced | Compliance Sentinel (Feb 2026 honorable mention, static check), canary data subjects in commercial tools | AutoSRE-0 (2 a.m. rollbacks, no human), BABYDOV's autonomy budget, PagerDuty runbook automation | GitLab's Resolve Dependency Bump Breaking Changes flow, BreakGuard (arXiv, Aug 2026) |
| Distinction | Judges whether a person can pay, by ear; cannot turn a barrier green | Runs instead of reading; the test follows each change | A grant a person signs, that expires, and is restored by default | Works on a green pipeline and adds evidence, not repairs |
| Technological Implementation | Medium, higher with a live flow | Medium, higher with a live flow | Medium-low now: Duo is off the critical path | Medium |
| Design | Medium to medium-high | Medium | Medium to medium-high | Low-medium to medium |
| Potential Impact | Medium | Medium to medium-high | Medium-low to medium | Medium |
| Innovation/Idea | Medium-high against this field; never claim first | Medium; canary subjects are prior art | Medium | Low to low-medium |
| Presentation | High potential (audio) | Medium (risks reading as "a test failed") | Medium-high only if a real night is filmed | Medium |
| Local burden | About 2,600 lines; reuses the Playwright smoke test and flow validator | About 2,800 to 3,800 lines, all new | About 1,500 to 2,800 lines of rework on a tested core | About 1,500 to 2,500 lines |
| Integration burden | Medium: one flow; Playwright image in CI; Cloud Run optional | Medium: two flows; trigger rules mean the gap flow needs a mention | High: two flows, flags, incidents, reactions, a relay running for hours with a token | Low-medium: one flow; no cloud |
| Main failure risk | Duo looks like the Fix CI/CD Pipeline flow with an accessibility prompt; a 30-line rule catches the planted barrier | A fair crawler baseline catches most planted cases, so Duo writes YAML code could have produced | Judges see code acting at night and Duo writing paperwork; the night is staged | Prior art makes it mid-pack; the hero change is famous, so "the model remembered it" |
| Smallest fallback | Code walk plus one flow started by `/flow:` that opens an issue and a fix MR | Probe plus the map flow only; a person writes fixes | Code-only night plus whatever Duo run works (fails Stage One if none works) | One flow, one real bump, the fix by hand |
| Confidence | Medium that it is the best choice; 40 to 55% for a complete honest entry | Medium-low | Medium-low; 30 to 45% for the full product | Medium to finish; low to place |

Rejected as the main concept, and why:

- **Night Orders.** The useful part at 03:12 is deterministic code; the dossier itself keeps Duo out of the night, and code already handles the two dusk examples that were meant to show the model's value. It has the widest untested live surface and the most staged demo. It would move up only if a live probe showed a Flows API start working for this role, so that Duo acts at the paged moment under the signed grant.
- **Fine Print.** Most likely to finish and look honest, least likely to place: GitLab ships a neighbouring flow, a published method does the same thing, and the planned hero change is one the model may simply remember.

### 0.4 Recommendation

**Preferred: No Mouse, revised.** Code walks the checkout in CI using only accessible names and keys, Duo judges a broken walk, code replays whatever Duo writes, and a person merges. It is the only candidate both comparisons put in their top two. It has the clearest human consequence in a short video, a domain no visible entrant covers, an event-driven Duo start that fits the documented trigger rules, and an output (issues and MRs) judges can read without project access. Recommended category: **Path A, Best Supervised Agent**, with **Most Creative** as the special prize emphasis.

**Strongest argument against it.** The new part may be plain CI code. A short rule catches the planted unnamed-icon barrier, a bounded search over named controls may handle harmless redesigns without a model, and the flow resembles GitLab's Fix CI/CD Pipeline flow. The screen reader is simulated (Playwright's computed accessible names, read aloud by a speech engine), and a Developer cannot enforce "pipelines must succeed", so some control is convention plus a release job that needs a clear walk. If the model does not beat a strong baseline, Duo is decorative and the concept fails its own test.

**Closest alternative: Forget Me.** Prefer it if (a) No Mouse's experiment fails against the strong baseline while a pre-registered Forget Me bench shows the model catching cases a crawler misses, (b) a Playwright browser in GitLab shared runners proves impractical, or (c) Alex values Potential Impact and a real privacy decision over presentation and Most Creative.

**Prize emphasis.** Supervised path prize first. Most Creative second. Not Most Stages Covered (an honest count is Verify and Create, with thin Plan, Release and Monitor), and not the environmental prize. The Google Cloud bonus is optional and late: one scale-to-zero Cloud Run shop that the release job deploys and judges can try with their own screen reader, only after the live flow passes.

**Feasibility experiment, before any bulk build (about 1 to 1.5 days, local, decided by about 10 Oct).**

1. Build and commit, before writing any prompt: the labelled demo shop, the code walker and announcer, and two baselines. B1 is a short rule (an unnamed focusable control means barrier, otherwise match the old name). B2 is strong: a synonym list plus a bounded search over named controls, accepted only if an order is really placed and no unnamed or junk-named control is pressed.
2. Codex writes held-out variants without seeing the prompt: at least four harmless redesigns (including a reworded control no synonym covers), at least five barriers (including a named but meaningless control and a spoken name that does not match the visible label), and one prompt-injection page.
3. Run the exact flow prompt with mock tools that return only the log tail, three times per variant, using a clearly labelled stand-in model (not Duo).
4. Pass: the model beats B2 on at least two distinct cases; barriers are answered barrier or unsure in at least 14 of 15 runs; no accepted path presses an unnamed or junk-named control; the injection is ignored every time; drafted fixes replay green in at least two of three runs.
5. Fail: B2 ties the model. That is a concept decision for Codex and Alex (run the Forget Me bench or reframe), not a quiet fallback.

A separate live gate applies to every candidate, within 48 hours of workspace access: create and enable a one-component custom flow; start it by `/flow:` and by the Flows API; have it read a real job log tail, open an issue and commit a one-line change on a branch; record whether a failed pipeline after a person's push fires a Pipeline events trigger, whether Alex can merge, and the credits left. Escalate to the organizers the same day if anything is refused.

**Smallest complete product worth demonstrating.** One labelled demo shop and one checkout journey. A CI walk job that writes the verdict, a transcript, audio, one JUnit case per step and a short evidence block at the end of the log, and a release job that needs a clear walk. One API-only custom flow (a single agent first; split it only after routing is proven live) that reads the log tail and opens either a "record the new path" MR or an issue with a draft fix MR. Code guards on every agent path. Two real runs on GitLab.com: one harmless redesign and one barrier. One real VoiceOver clip for calibration. A README with the evaluation table against both baselines, failures included, and the prior art named.

**Deliberately out of scope.** An agent pressing keys inside the flow (only a stretch if the live probe shows a browser can run there); real screen readers in CI beyond the calibration clip; more than one journey; mobile; any WCAG compliance or "first" claim; auto-merge, auto-deploy and rollback; a human approval step on the critical path (unsure cases become an issue for a person); Cloud Run before about 22 Oct; Most Stages Covered and SCI claims; session links as the only proof; deleting the Night Orders code before the switch is reviewed.

**Confidence.** Medium that No Mouse is the best of the four; the margin over Forget Me is narrow. The shared gate (can the hackathon role enable a custom flow?) matters more than the choice between them: if it fails, no candidate qualifies.

### 0.5 Questions Codex should answer

1. Accept No Mouse as preferred, choose Forget Me, or keep Night Orders?
2. Are the experiment's baselines and pass bar fair, and will Codex write the held-out variants?
3. Should the submission repository contain only the new product, with Night Orders kept in the GitHub workbench?

## 1. Recommendation

Build **Night Orders** ([full brief](research/ideas/brief_C01_night_orders.md)). Before bed, the on-call engineer signs a short list of rehearsed, reversible actions the agent may take alone tonight; at night, code lets it do exactly those things and wakes her for anything else, and the orders expire at 07:00. It came first of 57 concepts on our total (88.6 of 110) and first on the five official criteria (mean 8.53, level with No Mouse but ahead on Technological Implementation, which the rules use first to break ties), and all three judge personas put it first in their top 10. It sits where nobody in the October field is (on-call at night), away from the crowded release gatekeepers, and it gives GitLab's own October theme, "Hands Off. How far can your agents go without you?", a plain answer: as far as she signed, for tonight only. The scene is easy to feel: at 03:12 the new checkout fails, the agent turns its flag off under an order she signed at 22:06, and her phone stays dark. The open risk is starting a flow at night with nobody awake; a one-hour test settles it this week, and if it fails, the code-only form (Standing Orders) still films the dark phone honestly. No Mouse is the backup.

## 2. How the ideas were made

The handoff asked for at least 40 distinct concepts under at least six lenses, generated before any judging, with the three most obvious answers under each lens banned. Four generation files used eight lenses and wrote 74 full concepts. Nothing in those files is scored or ranked. The last two lenses (the person on the other end, and rituals from other crafts) are the coordinator's own.

Every concept had to automate part of the post-code lifecycle on GitLab, be truly agentic with a person in control of anything that matters, and start from one person's moment. Each write-up gives the same parts: the person and their moment; the flow step by step, with the GitLab feature at each step; the lifecycle stages; the autonomy level; what the model may and may not do, and what code decides; the 30-second demo moment; the nearest crowded space and how the concept differs; and the biggest risk for one builder by Oct 24. All four files follow one house rule: the model chooses where to look, code decides what is true, and a person decides when the agent acts on anything that matters.

| # | Lens | Concepts | The question it asks | File |
|---|---|---|---|---|
| 1 | The 3am on-call engineer | 8 | What would let the person holding the pager sleep, trust, or stop dreading the night? | [lens_oncall_inversion.md](research/ideas/lens_oncall_inversion.md) |
| 2 | Inversion | 8 | How would we guarantee that a release fails? Each of 18 answers is turned around. | [lens_oncall_inversion.md](research/ideas/lens_oncall_inversion.md) |
| 3 | Game design | 8 | How do games structure decisions, risk, pacing and cooperation (not rewards)? | [lens_games_markets.md](research/ideas/lens_games_markets.md) |
| 4 | Markets | 8 | How do markets allocate scarce things, price risk and settle promises? | [lens_games_markets.md](research/ideas/lens_games_markets.md) |
| 5 | Biology | 11 | Which mechanism (what the body actually does, step by step) maps onto the post-code lifecycle? | [lens_biology_assumptions.md](research/ideas/lens_biology_assumptions.md) |
| 6 | Remove the load-bearing assumption | 9 | What does the lifecycle silently rely on (20 assumptions listed), and what follows when each is taken away? | [lens_biology_assumptions.md](research/ideas/lens_biology_assumptions.md) |
| 7 | The person on the other end (coordinator) | 10 | Who does the software affect who never sees GitLab, and what is their moment? | [lens_people_rituals.md](research/ideas/lens_people_rituals.md) |
| 8 | Rituals from other crafts (coordinator) | 12 | Which mechanism from a high-stakes craft (theatre, surgery, aviation, kitchens, hospitals) fits? | [lens_people_rituals.md](research/ideas/lens_people_rituals.md) |
| | **Total** | **74** | | |

### The banned obvious answers, copied from the lens files

1. **The 3am on-call engineer.** Banned: an incident summary chatbot (explains the alert, the logs and recent deploys); auto-rollback on alert; a root cause analyzer that walks from the alert to the deploy, the MR and its author and names the culprit. Close variants also out: postmortem draft writers, "similar past incidents" search, alert deduplication at page time, and a "self-healing" runbook executor that fixes production without a person.
2. **Inversion.** Banned: "nobody ran the tests or the scans" turned into a release gate that blocks on failed tests and scans (the most crowded October space and the judges' own reference project); "there was no rollback plan" turned into automatic rollback or a rollback rehearsal on every release; "nobody really reviewed the change" turned into an AI code reviewer on the MR. Close variants also out: "no deploys on Friday" calendars, release notes writers, pre-merge "what could this break" reports.
3. **Game design.** Banned: leaderboards that rank developers by merges, fixes, deploys or incidents closed; achievement badges, XP and streaks; a gamified dashboard (health bars for services, team levels, "boss HP" for an incident). Close variants also out: points races between teams, avatars, loot for fixing bugs, "quests" that are a checklist with points.
4. **Markets.** Banned: a prediction market where developers bet on whether a deploy will break, or a deploy risk score shown as odds; bug bounties or an internal token economy that pays for fixes, reviews or closed incidents; price tags on pipelines and MRs (CI or cloud cost per change, chargeback to teams). Close variants also out: auctions for runner time or queue priority, carbon credits for pipelines, a "stock price" for services or teams.
5. **Biology.** Banned: a self-healing pipeline that repairs or rolls itself back (including auto-rollback on a failed health check and CI failure fixers described as healing); an immune-system security scanner (agents as white blood cells, or "vaccinating" dependencies against CVEs); an organism health dashboard ("vital signs", a heartbeat, a health score).
6. **Remove the load-bearing assumption.** Banned: remove "a human approves the release", so agents ship to production alone after scans, tests and a health check (the hands-off release gatekeeper: 4 of 7 known October entries and the judges' reference project); remove "a human reviews code before merge", so an AI reviews every MR (95 code review projects in February); remove "the on-call person is awake", so an AI on-call bot diagnoses and auto-remediates incidents at night (root cause plus auto-rollback, as in ZeroTouch Monitor and Praetor).
7. **The person on the other end.** Banned: a support ticket summariser or triage bot; a "your bug is fixed" notifier that emails everyone who reported an issue when it closes or ships; a friendly nudge bot for people who wait (welcomes first-time contributors, pings reviewers on stale MRs). Close variants also out: customer-facing changelogs and "what's new" posts, status page updaters, feedback sentiment dashboards.
8. **Rituals from other crafts.** Banned: the surgical checklist as a release checklist bot; hospital shift handover as a handoff notes generator; the bomb squad's two-person rule as "two approvals before production". Close variants also out: go or no-go polls, pre-flight checklists, aviation-style blameless post-mortem writers, war-room chat summaries.

### From 74 concepts to 57 candidates

[CANDIDATES.md](research/ideas/CANDIDATES.md) merges near-duplicates into 57 distinct candidates. Seventeen concepts that two lenses reached from different directions were folded into one canonical write-up, for example Standing Orders into Night Orders, Spoken Diff into No Mouse, and Promise Kept, Try First and First Dibs into Front Row. A few close pairs were kept apart because they behave differently: Night Orders grants the agent actions while Night Nurse only decides whether to wake someone; Return Ticket proves a way back while Decision Height gates at the one-way step; Wince protects people from flaky tests while No Reloads treats a retry as a possible real bug; Lockout Tagout serves a person working by hand while Tactical Pause freezes change during an incident.

Night Orders was reached three times, independently: by the on-call lens, by the rituals lens as Standing Orders (hospital orders a nurse may carry out overnight), and by the game and market lenses as overwatch and a stop-loss order ([lens_games_markets.md](research/ideas/lens_games_markets.md), "Also produced by these lenses"). The rituals file notes that convergence cuts both ways: the fit is natural, and other entrants may reach the same idea.

## 3. How they were scored

**The rubric** ([SCORING_RUBRIC.md](research/ideas/SCORING_RUBRIC.md)). Every candidate was scored 1 to 10 on twelve dimensions, where 5 means average for this pool, as it would be if built well by Oct 24:

- The five official criteria, which the rules weight equally: Technological Implementation, Design, Potential Impact, Innovation/Idea, Presentation ([RULES_CHECK.md](codex/RULES_CHECK.md#judging-stages-criteria-and-weights)).
- Six from the handoff: lifecycle stages (of the nine: plan, create, verify, package, secure, release, configure, monitor, govern), autonomy (a credible story at the level it fits, with a chance at that level's prize), human moment, novelty (distance from past winners, the current field, the crowded spaces and the judges' reference project), sponsor depth, and the 30-second wow.
- Feasibility: can one builder (Claude Code and Codex writing, Alex only copying messages until Oct 23) build it, run it for real on GitLab, deploy it to Cloud Run and film it by Oct 24.

**The formula.** criteria = the mean of the five official criteria. total = 3 x criteria + stages + autonomy + human + novelty + sponsors + wow + 2 x feasibility, for a maximum of 110. The official criteria weigh most because they decide the real score; feasibility counts double because an idea that cannot be shown working scores nothing.

**The scorers.**

- **Three judge personas**, one for each sponsor on the panel: GitLab ([scores_gitlab_judge.json](research/ideas/scores_gitlab_judge.json)), Anthropic ([scores_anthropic_judge.json](research/ideas/scores_anthropic_judge.json)) and Google ([scores_google_judge.json](research/ideas/scores_google_judge.json)). Each scored all 57 candidates separately on the eleven judge dimensions, named the autonomy level the concept fits, wrote one line on what would move its score up or down, and listed a top 10 and its traps.
- **A feasibility engineer** ([scores_engineer.json](research/ideas/scores_engineer.json)) scored feasibility for all 57 and wrote, for each, the main blocker, a fallback, the minimum demo, and whether it is a trap: a concept that looks strong but will likely fail because it cannot be demoed honestly, depends on access we may not have, needs weeks of real history, or collides with an excluded or crowded idea. The engineer flagged 16 traps.
- **The combined file** ([scores_combined.json](research/ideas/scores_combined.json)) takes the mean of the three judges on each dimension, the engineer's feasibility and the engineer's trap flags. [score_table.md](research/ideas/score_table.md) ranks the result by total.
- **The top five by total then got a full build brief each**, with a skeptical review that could move the scores (section 5).

**Where the scorers agreed.** All three judges put Night Orders first in their top 10, and No Mouse in their top three. Forget Me and Writeback are in all three top-10 lists. Front Row is in two (GitLab's second, Google's seventh); the Anthropic persona left it out and called its framing a trap: a demo where the reporter confirms the fix works is Proof of Fix with a new audience, and its sibling Promise Kept is the banned "your bug is fixed" notifier. The engineer's top 10 for "feasible and human" includes Night Orders, No Mouse, Forget Me and Writeback.

**The honest limits of persona scoring.**

- These are AI personas we wrote, not the judges. They read the same research notes, so they share its blind spots, and their scores move together more than real judges' would.
- They scored written concepts, not running software. Nothing has run on GitLab or Google Cloud yet, and feasibility is one persona's estimate.
- The weights are ours. The rules weight only the five criteria, equally, so section 5 ranks the finalists on those alone.
- Small gaps are noise. A closer look in the briefs moved totals by between -0.8 and +3.1 points, and the Writeback brief calls a 0.1 gap "within scoring noise". Read the table in bands, not as exact ranks.
- A write-up with a vivid scene may score higher than a plainer one of equal merit (inference).
- The personas sometimes disagreed on facts, not only taste: two called No Mouse Hands-off and one Supervised; its brief settles on Supervised.
- In June, GitLab pre-scored entries with three models and then humans picked every winner ([PATTERNS.md, 3.4](PATTERNS.md#34-proof-that-the-agent-really-ran)). We did only the first half.

## 4. The full scoring table (57 concepts)

Copied from [score_table.md](research/ideas/score_table.md), ranked by total. "Criteria" is the mean of the three judges' five official criteria; feasibility and the trap flags are the engineer's. The "Brief-adjusted total" column is filled for the five finalists only: it is the total each build brief proposed after its skeptical review (section 5). A trap is a concept that looks strong but will likely fail; each one keeps its one-line reason. One-line descriptions of every concept are in [CANDIDATES.md](research/ideas/CANDIDATES.md).

| Rank | ID | Name | Criteria (mean of 5) | Stages | Autonomy | Human | Novelty | Sponsors | Wow | Feasibility | Total /110 | Brief-adjusted total | Trap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | C01 | Night Orders | 8.53 | 6 | 9 | 9 | 7 | 9 | 9 | 7 | 88.6 | 88.6 |  |
| 2 | C13 | No Mouse | 8.53 | 4.7 | 7 | 9.7 | 7 | 7.7 | 10 | 7 | 85.6 | 84.8 |  |
| 3 | C37 | Forget Me | 7.67 | 5.7 | 5.7 | 8 | 8.7 | 7.7 | 7.3 | 7 | 80.0 | 81.7 |  |
| 4 | C27 | Writeback | 7.33 | 7.7 | 6 | 6 | 6.3 | 8 | 7 | 7 | 77.0 | 80.1 |  |
| 5 | C12 | Front Row | 7.67 | 5.7 | 6.7 | 8.3 | 5.7 | 6.3 | 7.3 | 6 | 75.0 | 76.7 |  |
| 6 | C34 | Row Call | 6.87 | 4 | 5.3 | 7.3 | 6 | 5.3 | 8 | 9 | 74.6 |  |  |
| 7 | C57 | Make Whole | 7.27 | 7 | 5.7 | 6.3 | 8.3 | 6.3 | 6.3 | 6 | 73.8 |  |  |
| 8 | C44 | Site Mark | 6.87 | 5 | 6.7 | 6 | 8.3 | 5 | 7.3 | 7 | 72.9 |  |  |
| 9 | C02 | Night Nurse | 6.87 | 4.3 | 6.3 | 8 | 6.3 | 7 | 8 | 5 | 70.6 |  |  |
| 10 | C38 | Cue Light | 7.33 | 6 | 8.7 | 5 | 5.7 | 6.3 | 6.7 | 5 | 70.3 |  |  |
| 11 | C04 | Watermelon | 6.73 | 5 | 6 | 7.7 | 6.3 | 5.7 | 8 | 5 | 68.9 |  |  |
| 12 | C50 | Next Wave | 5.87 | 7.3 | 5 | 6 | 7.3 | 7.3 | 5 | 6 | 67.6 |  |  |
| 13 | C39 | Lockout Tagout | 6.8 | 6 | 7 | 5 | 9 | 5.3 | 6.7 | 4 | 67.4 |  | yes: Each lock is a Maintainer-level GitLab setting (deploy freeze, pausing schedules, turning triggers off); with our own marker it only binds jobs we wrote ourselves. |
| 14 | C03 | Dress Rehearsal | 6.87 | 5 | 7 | 6 | 5.3 | 8 | 6.7 | 4 | 66.6 |  | yes: The tested-fix menu needs several Cloud Run revisions and request replays within minutes of a page, which only works with a bug planted to replay cleanly, so it will likely look staged or run late. |
| 15 | C05 | Loose Ends | 6.07 | 7 | 5.3 | 5 | 7.3 | 6 | 5.7 | 6 | 66.5 |  |  |
| 16 | C29 | Learner Permit | 6.53 | 7 | 8.3 | 4.7 | 4.3 | 6.7 | 5.3 | 5 | 65.9 |  |  |
| 17 | C16 | Kill Switch | 6.13 | 6 | 5 | 6.7 | 4.3 | 6 | 7 | 6 | 65.4 |  |  |
| 18 | C54 | Alarm Level | 5.87 | 7.7 | 5 | 6.7 | 4 | 6.7 | 5.7 | 6 | 65.3 |  |  |
| 19 | C18 | Canary Voices | 5.8 | 4.7 | 5.3 | 5 | 6.7 | 5.7 | 6 | 7 | 64.7 |  |  |
| 20 | C32 | Last Caller | 5.73 | 6.7 | 5 | 7 | 6 | 6.3 | 4.7 | 5 | 62.9 |  |  |
| 21 | C48 | Respawn | 6.2 | 5 | 5.7 | 4.7 | 5.7 | 6 | 7 | 5 | 62.6 |  |  |
| 22 | C40 | Decision Height | 6.33 | 6 | 7.3 | 2.7 | 3.3 | 5.7 | 5.7 | 6 | 61.7 |  | yes: On screen it is a pipeline that deploys, holds at an approval and rolls back, which reads as the crowded release gatekeeper (4 of 7 known October entries and the judges' reference project). |
| 23 | C14 | Fine Print | 5.53 | 6 | 5 | 4.7 | 3.7 | 4.7 | 4.3 | 8 | 60.9 |  |  |
| 24 | C36 | Kind Revert | 5.07 | 4 | 4.3 | 8 | 8 | 3.3 | 5.7 | 6 | 60.5 |  |  |
| 25 | C49 | Telegraph | 4.93 | 5 | 4.7 | 3.7 | 6.7 | 5 | 4.3 | 8 | 60.1 |  |  |
| 26 | C07 | Fire Drill | 4.8 | 5.7 | 4.7 | 6.3 | 4.3 | 5 | 4.3 | 7 | 58.7 |  |  |
| 27 | C26 | Last Day | 5.67 | 6.7 | 5 | 6.3 | 8 | 4.7 | 5 | 3 | 58.7 |  | yes: The hand-over needs two real project members and Maintainer-level reads (protected environments, escalation policies, other people's triggers); with one builder every item belongs to Alex. |
| 28 | C45 | Med Rec | 5.2 | 6 | 5 | 3.7 | 5 | 7 | 4.3 | 6 | 58.6 |  |  |
| 29 | C28 | Teach Back | 4.67 | 3 | 6.3 | 4 | 6.7 | 3.7 | 4.7 | 8 | 58.3 |  |  |
| 30 | C33 | Straight Answer | 4.87 | 4.3 | 4.7 | 5.3 | 4.7 | 4.7 | 5 | 7 | 57.3 |  |  |
| 31 | C43 | Fight Call | 5.2 | 5 | 5.3 | 4.3 | 6 | 6.7 | 4 | 5 | 56.9 |  |  |
| 32 | C06 | Sleep Debt | 4.93 | 5 | 4.3 | 4.3 | 5.3 | 6.3 | 5.3 | 5 | 55.5 |  | yes: The proof is a replay over 30 days of alerts and metrics that cannot exist by Oct 24, so the headline number comes from history we generate ourselves. |
| 33 | C10 | Plane Mode | 5.0 | 4 | 5 | 8 | 4.3 | 3.3 | 5.7 | 5 | 55.3 |  |  |
| 34 | C11 | Return Ticket | 5.67 | 4.7 | 4.7 | 3.7 | 3.3 | 4.3 | 5 | 6 | 54.7 |  |  |
| 35 | C17 | Log Leak | 4.93 | 5.7 | 4.3 | 2.3 | 3 | 8 | 4.3 | 6 | 54.5 |  |  |
| 36 | C09 | Daylight Rollout | 4.93 | 5.7 | 5.7 | 3.3 | 5.7 | 4.3 | 4.7 | 5 | 54.1 |  |  |
| 37 | C41 | Heat Lamp | 4.27 | 5 | 4.3 | 4.7 | 4.7 | 3.7 | 4.3 | 7 | 53.5 |  |  |
| 38 | C35 | Dear Successor | 4.13 | 6.7 | 4 | 4.7 | 5 | 3.3 | 3 | 7 | 53.1 |  |  |
| 39 | C21 | Apoptosis | 4.87 | 5.7 | 4.3 | 3 | 5.3 | 4.7 | 5.3 | 5 | 52.9 |  |  |
| 40 | C20 | Scar Tissue | 4.47 | 5 | 4.3 | 5.7 | 4.7 | 4.3 | 4.7 | 5 | 52.1 |  |  |
| 41 | C23 | Mutualist | 4.47 | 6 | 4.3 | 4 | 7.3 | 3.7 | 3.3 | 5 | 52.1 |  |  |
| 42 | C52 | Tactical Pause | 4.8 | 4 | 5.3 | 3.3 | 5.3 | 4 | 6.7 | 4 | 51.1 |  | yes: The freeze levers (deploy freezes, pausing schedules, cancelling other people's auto-merge) need Maintainer; with a marker file it only pauses jobs we wrote. |
| 43 | C08 | Someone Awake | 4.47 | 1.7 | 4 | 6.7 | 7.7 | 4 | 7 | 3 | 50.4 |  | yes: It needs a second real teammate in the project, their time zone and busy status read from inside a flow, a night start and an outside timer, and adding members needs Maintainer. |
| 44 | C53 | No Reloads | 4.13 | 3 | 3.7 | 3.3 | 3.3 | 3.3 | 5.3 | 8 | 50.4 |  |  |
| 45 | C56 | Triple A | 4.8 | 6 | 5.7 | 2.3 | 3.3 | 4.3 | 4 | 5 | 50.1 |  |  |
| 46 | C51 | Speedrun | 4.53 | 4 | 5 | 4 | 3 | 4 | 5.7 | 5 | 49.3 |  |  |
| 47 | C42 | Readback | 4.33 | 5 | 4.7 | 4 | 4 | 3.7 | 4 | 5 | 48.3 |  | yes: It needs two real on-call members to hand over between, and on screen it sits next to the banned handoff-notes generator. |
| 48 | C55 | Limit Order | 4.0 | 3 | 5.3 | 5 | 3.7 | 4.3 | 4 | 5 | 47.3 |  |  |
| 49 | C47 | Shield Wall | 4.0 | 3 | 4.3 | 5 | 3 | 4 | 5.7 | 5 | 47.0 |  | yes: Its visible part is a bot answering 'ETA?' in the incident, which judges may file under the excluded generic incident chatbot, and the personal replies depend on Service Desk email. |
| 50 | C24 | Wince | 3.6 | 4 | 3.7 | 5.3 | 3 | 3.3 | 3.7 | 6 | 45.8 |  |  |
| 51 | C19 | Fever | 4.07 | 4.3 | 5.7 | 3.7 | 5 | 4.3 | 3.3 | 3 | 44.5 |  | yes: Its product is raising and lowering GitLab's own controls (deployment approvals, deploy freezes), which need Maintainer and Premium setup, and breaking the fever needs days of clean history. |
| 52 | C22 | Placebo | 4.27 | 4 | 3.3 | 3 | 9 | 3.3 | 4.7 | 2 | 44.1 |  | yes: It needs a year of incidents with metrics to build treated and untreated groups; generated history makes the statistics circular. |
| 53 | C15 | Lifeboat | 2.93 | 5.7 | 3.7 | 2.7 | 6 | 4 | 2 | 4 | 40.8 |  | yes: Cleanup policies and protected tags need Maintainer, our images live in Google Artifact Registry rather than the GitLab registry, and the human moment is a rollback that simply works. |
| 54 | C30 | Postcard | 3.0 | 4 | 2.7 | 5 | 2 | 4 | 3.3 | 4 | 38.0 |  | yes: 'A week after release' cannot happen by Oct 24, the usage numbers would come from generated traffic, and it reads close to the excluded Proof of Fix. |
| 55 | C46 | Understudy | 3.0 | 4.3 | 3.3 | 5.7 | 4.7 | 2.7 | 2.3 | 2 | 36.0 |  | yes: It counts who performed each task over six months; a new one-person project has days of history and one performer, so every finding is trivially true. |
| 56 | C25 | Night Replay | 2.73 | 1.7 | 3.3 | 3.3 | 1.7 | 4.3 | 3 | 4 | 33.5 |  | yes: It only works on top of another agent that people already corrected during a real day, so it doubles the build, and on its own it has no user value to show. |
| 57 | C31 | Auditor Hour | 3.2 | 4 | 3.3 | 2 | 2.7 | 3.3 | 2 | 3 | 32.9 |  | yes: It needs a quarter of approvals by several people and audit events that may need Owner access; on a new one-person project the honest answer is trivial, and evidence for auditors sits next to the crowded attestation space. |

Spread of autonomy levels (the most common of the three judges' calls per concept): 34 Supervised, 15 Assisted, 8 Hands-off. Seven concepts were called Hands-off by all three judges and one (No Mouse) by two. Night Orders has the highest total of them, 18 points above the next unanimous one, Night Nurse (70.6), which only decides whether to wake someone and changes nothing.

## 5. The five finalists against the five official criteria

The rules judge on five equally weighted criteria and nothing else (apart from the Google Cloud bonus of up to 0.2), so this ranking leaves out our extra dimensions. The numbers are the three judges' means from [scores_combined.json](research/ideas/scores_combined.json). Ties are broken the way the rules break them: "the tied Submission with the highest score in the first applicable criterion listed above will be considered the higher scoring Submission" ([RULES_CHECK.md](codex/RULES_CHECK.md#multiple-prize-eligibility-and-tie-breaking)), and Technological Implementation is listed first.

| Rank | Concept | Technological Implementation | Design | Potential Impact | Innovation/Idea | Presentation | Mean | Mean after the brief | Total, then brief-adjusted |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Night Orders (C01) | 8.7 | 9.0 | 8.0 | 8.3 | 8.7 | 8.53 | 8.53 | 88.6, then 88.6 |
| 2 | No Mouse (C13) | 7.7 | 7.7 | 8.7 | 9.0 | 9.7 | 8.53 | 8.48 | 85.6, then 84.8 |
| 3 | Forget Me (C37) | 7.7 | 7.3 | 8.0 | 8.3 | 7.0 | 7.67 | 7.80 | 80.0, then 81.7 |
| 4 | Front Row (C12) | 7.0 | 8.7 | 7.7 | 7.3 | 7.7 | 7.67 | 7.58 | 75.0, then 76.7 |
| 5 | Writeback (C27) | 8.0 | 7.7 | 7.3 | 6.3 | 7.3 | 7.33 | 7.36 | 77.0, then 80.1 |

**The ranking.**

1. **Night Orders**, mean 8.53. It is equal to No Mouse to the last digit and wins the tie-break on Technological Implementation (8.7 against 7.7).
2. **No Mouse**, mean 8.53. The best Presentation (9.7) and Innovation (9.0) in the pool.
3. **Forget Me**, mean 7.67. Equal to Front Row; it wins the same tie-break (7.7 against 7.0).
4. **Front Row**, mean 7.67. The second-best Design score of the five (8.7).
5. **Writeback**, mean 7.33. Strong on Technological Implementation (8.0), the weakest of the five on Innovation (6.3).

On the five criteria alone, Front Row moves above Writeback; on our total it is the other way round, because Writeback scores higher on stages and feasibility. After the briefs' reviews the order on the criteria stays the same, and the tie at the top opens: Night Orders 8.53, No Mouse 8.48.

**How each brief's review moved it.**

1. **Night Orders** ([brief, section 13](research/ideas/brief_C01_night_orders.md#13-verdict)). No change to the five criteria. Stages 6 to 7.5 (the rehearsal on staging, the image check, the refused prompt injection, and the agent-written orders and countersign MRs make verify, package, secure and create real); novelty 7 to 6.5 (PagerDuty's SRE agent and industry advice on "pre-approved, narrowly-scoped actions" sit close); feasibility 7 to 6.5 (three flows, a relay, a rehearsal job, and the signature needs merge or approval rights). Net zero: the total stays 88.6. The brief folds in Dress Rehearsal (the rehearsal moves to a calm dusk, away from that concept's trap) and Loose Ends (the morning ledger is the relay's own record, not one rebuilt from audit logs). If the night start fails and the code-only Standing Orders form is built: about 86.5.
2. **No Mouse** ([brief, section 13](research/ideas/brief_C13_no_mouse.md#13-verdict)). Innovation 9.0 to 8.3 (prior art: a 2026 U.S. patent application, Perforce, Evinced's "screen reader agent", Apple's AXNav research, GitLab's own Pa11y template, and Moonwalk among past winners) and design 7.7 to 8.0 (replay first, model only on failure, a re-walk of the fix and a production walk make one loop), so the criteria mean falls to 8.48. Stages 4.7 to 6.0; autonomy 7.0 to 6.5 (the honest level is Supervised); novelty 7.0 to 6.5; feasibility 7.0 to 6.5. Total 85.6 to 84.8. If only the scripted form survives its day-one test: about 79.
3. **Forget Me** ([brief, section 13](research/ideas/brief_C37_forget_me.md#13-verdict)). Technological Implementation 7.7 to 8.0, design 7.3 to 7.5, impact 8.0 to 8.5 (this exact bug class is documented: the FTC's 2023 case over children's Alexa recordings, and Meta's DELF), innovation 8.3 to 8.0 (canary deletion checks are patented and sold), so the criteria mean rises to 7.8. Stages 5.7 to 7.0, autonomy 5.7 to 6.0, novelty 8.7 to 8.0, sponsors 7.7 to 8.0. Total 80.0 to 81.7. The brief also replaced the persona (Laila, leaving an abusive partner) with a parent who deleted her son's homework-app account, because a 2:40 DevSecOps video cannot treat abuse with care. If only the local fallback works: 3 to 4 points less.
4. **Front Row** ([brief, section 18](research/ideas/brief_C12_front_row.md#18-verdict)). Innovation 7.3 to 6.8 (fix-first flags and close-the-loop tools are commercial practice, and the past winner BugFlow already owns "mention a customer's bug and the agents take it from there"), so the criteria mean falls to 7.58. Stages 5.7 to 7.0, human 8.3 to 8.7 (a "still wrong" reply that holds the release is a second, stronger beat), novelty 5.7 to 5.0, feasibility 6 to 6.5 (Service Desk is on by default and Developers can manage flags and user lists). Total 75.0 to 76.7.
5. **Writeback** ([brief, section 13](research/ideas/brief_C27_writeback.md#13-verdict)). Impact 7.3 to 7.7 and presentation 7.3 to 7.7 (open on the outage coming back), innovation 6.3 to 5.7 (driftctl, env0, Firefly, StackGuardian and AWS's drift-aware change sets already do parts of it), so the criteria mean is 7.36. Stages 7.7 to 8, human 6 to 6.5, novelty 6.3 to 6, wow 7 to 7.5, feasibility 7 to 8 (no flow has to start at night or without a person). Total 77.0 to 80.1. If the flow can only start from a comment: about 77.6.

**Where the briefs and the scores disagree.**

- **No Mouse's autonomy level.** Two judges called it Hands-off; its brief says the honest level is Supervised (a person merges the fix and presses Play on production) and moves its prize target to Best Supervised plus Most Creative.
- **Third place.** Each brief compared itself with the other concepts' first-pass totals. Writeback's brief claims third (80.1 against Forget Me's 80.0), but Forget Me's own brief raised it to 81.7, and Front Row's brief compares itself with 77.0 and 80.0. With every brief's own adjustment applied, the order is 88.6, 84.8, 81.7, 80.1, 76.7: the same as the table.
- **Night Orders' fallback.** Its brief says Standing Orders (about 86.5) would be "level with C13"; that uses No Mouse's first-pass 85.6. Against No Mouse's adjusted 84.8, the fallback still leads.
- **Stages.** Every brief found more stage coverage than the first scores credited. All five now touch all nine stages, at different depths.

## 6. The top three, one page each

Each page condenses its full brief, which has the sources, the flow YAML that was checked against GitLab's schema, the red team and the build plan. Everything here is a plan: nothing has run on GitLab or Google Cloud yet.

### 6.1 Night Orders (C01): Hands-off, 88.6

[Full brief](research/ideas/brief_C01_night_orders.md)

**Name and pitch.** Ship captains write night orders for the officer of the watch before they sleep, and the phrase already says "for tonight only". Pitch: before bed, the on-call engineer signs tonight's orders, a few rehearsed, reversible actions the agent may take alone; at night code lets it do exactly those things and wakes her for anything else.

**Who it is for, and the story.** Small teams with no follow-the-sun rotation. Priya Raman (persona), a backend engineer at a small online shop (the demo app "Juniper Market"), is on call this week for the first time since her daughter was born. Any alert might be the one that needs her, so every alert wakes her, and she has not slept through an on-call week this year. Night Orders lets her decide at 22:00 what the agent may handle alone tonight, rehearsed and signed, so the phone wakes her only for what it cannot handle.

**One person's specific problem.** At 16:20 a teammate's new checkout path went live behind the `new_checkout` flag. If it fails at 03:00, the right move is already obvious and safe (turn that one flag off), yet only Priya can do it, so she sleeps with the phone on the pillow and is woken for every alert. She has no way to hand that one decision to the agent for tonight only without handing over everything else.

**Closest past winner, and the difference in behavior.** StregEnt ("It never sleeps so you can."), an honorable mention in GitLab's February 2026 hackathon on the same Duo Agent Platform (prize known from search excerpts). When a CI pipeline fails, StregEnt always messages the developer, who then fixes things step by step in chat, and its README suggests letting Claude merge to main for "Zero human intervention", with no list and no end date. Night Orders watches production between the dusk signature and 07:00. A failure covered by a signed order sends no message at all: code runs the one signed action and re-checks. Anything else sends one page with one prepared decision. It may change only the actions in tonight's merged orders, each on its named target, once. At 03:12, with StregEnt the phone lights up; with Night Orders it stays dark. (Agentic CICD, from AI in Action 2025, lets the agent's own judgment start a rollback; here the agent alone can start nothing.)

**The demo moment.** Split screen at 03:12: the checkout error rate climbs to 7.9%, and a phone lies face down beside a baby monitor. A note appears on the incident: "Order 1 carried out: `new_checkout` off. Signed by Priya at 22:06." The line falls and the phone stays dark. A second beat earns trust: at 01:50 the agent declined an order whose numbers matched (payments were failing on both paths, so the flag would not help), the phone lit up with three lines, and she approved a fallback with one thumbs-up.

**What judges see in the first 30 seconds.**

- 0:00 to 0:04: a black card, "03:12. Priya is asleep.", and a small grey label kept all night: "Demo app, planted fault, time compressed."
- 0:04 to 0:09: the split screen, the error chart climbing past a dashed 5% line. Voice: "At 3:12 the new checkout starts failing."
- 0:09 to 0:14: incident #12. The agent asks to use order 1; the relay's note lists its checks (signed, not expired, 7.9% above 5% for 5 minutes, target matches, first use tonight) and turns the flag off.
- 0:14 to 0:19: the line falls to 0.3% and the phone stays dark. Caption: "Nobody approved this at 03:12. She already had, at 22:06."
- 0:19 to 0:30: the title card ("Before bed, you sign what the agent may do alone tonight. Everything else wakes you."), then 21:30 the evening before, as she assigns tonight's watch issue to the flow.

**The end-to-end flow, one night.**

1. Dusk: at 21:30 Priya assigns the "Tonight's watch" issue to the dusk flow. It reads the day's merged MRs, deployments, flags and open incidents, and drafts at most three orders: a condition, one action from a fixed menu (`flag_set` or `traffic_to_revision`), its target, and the change behind it. A change that cannot be undone safely gets no order, so it wakes her.
2. The flow opens an MR to `ops/night-orders.yml`. The MR pipeline checks the schema and rehearses each order on staging: apply, smoke test, undo.
3. Priya edits or deletes orders and merges. The merge is the signature, and code trusts only that merged file. No merge means no orders, so every alert wakes her.
4. Night: a Cloud Monitoring alert reaches the relay, a small FastAPI service on Cloud Run and the only part allowed to change production. It opens a GitLab incident with an evidence pack and starts the watch flow through the Flows API.
5. The watch flow reads the evidence and the diffs, decides whether an eligible order's reason fits, and posts one request, or none plus a three-line page.
6. The relay checks the request against the signed file (in the file, condition holds now, window open, not used tonight), runs the action taken from the file (never from the note), and re-checks ten minutes later. No match, no recovery, or no answer within eight minutes: it pages her. A thumbs-up from the on-call user on a suggested action runs it.
7. Dawn: at 07:00 the orders expire. The dawn flow writes the watch log and opens a countersign MR (keep or undo each night action); she merges and an `apply_state` job applies it. Once the fix is in production, the next dusk proposes turning the flag back on.

**Every stage, and the GitLab feature behind it** (all nine; seven strong, create and package thin):

| Stage | GitLab feature (and Google piece) |
|---|---|
| Plan | Watch issue from a template, Assign trigger, watch log on the issue |
| Create (thin) | Flow-written orders MR and countersign MR; stretch: a Duo Developer fix MR with Duo Code Review |
| Verify | MR pipeline: schema check, rehearsal of each order on staging, JUnit report |
| Package (thin) | Image built per merge; the rehearsal checks each rollback image still exists |
| Secure | SAST and secret detection; a read-only investigator; ID-token checks at the relay; the token in Secret Manager; a planted log line that tries to command the agent changes nothing |
| Release | Environments and deployments; Cloud Run traffic to a named previous revision |
| Configure | GitLab feature flags with per-environment scopes; orders and desired state kept as files |
| Monitor | Cloud Monitoring alert, GitLab incident with timeline events, the re-check, the page |
| Govern | Merge as the signature, the countersign MR, the 07:00 expiry, session and timeline records |

**The actual Duo Agent Platform workflow.** Three custom flows, kept as YAML in `flows/`:

| Flow | Started by | Components |
|---|---|---|
| Dusk | Assign trigger: Priya assigns the watch issue | `scout` (read-only agent), `ask_priya` (HumanInputComponent, one question), `critic_1`, `reviser`, `critic_2` (two review rounds at most), then one-shot writers that commit the orders file and open the MR |
| Watch | The relay, through the Flows API with Alex's token (no questions to the user; read and write GitLab only) | `investigator` (read-only agent), then `request_writer` (one-shot, only `create_issue_note`) |
| Dawn | The relay at 07:00 through the Flows API (fallback: a Mention trigger) | `reporter`, then one-shot writers for the watch log and the countersign MR |

Plain CI runs the schema check, the rehearsal, tests, SAST, secret detection, keyless deploys, `apply_state`, and a check of every flow file against GitLab's `flow_v2.json`. The watch and dusk flow files passed that schema with zero errors on Oct 6; none has run on GitLab.com yet.

**The agent loop.**

- **The model may:** choose which of today's changes could page tonight and draft up to three orders from the menu; ask one question; at night, choose what evidence to read, request one eligible order or none, decline any order, and write a three-line page with one suggested action; at dawn, write the log and propose keep or undo.
- **The model may not:** merge; use an action outside the menu; at night, act, add or edit an order, touch a target not in a signed order, use an order twice, deploy code, touch data, or lower the wake floor.
- **Code decides:** the schema and the rehearsal result; which conditions hold now; whether a request names an eligible, unused, signed order; the always-wake floor (payment errors, a second alert during a re-check, a malformed answer, a relay error, anything after expiry); the re-check; whether a thumbs-up came from the on-call user after the page.
- **A person decides:** the dusk answer, the edits and the merge (or closing the issue to grant nothing); one thumbs-up if woken; the countersign merge.
- **Two keys turn at night:** code checks the numbers, the model checks the reason. Either key alone can wake her; neither alone can act. Time boxes: prompt timeouts of 240 to 300 seconds, at most two review rounds at dusk, 3 minutes of rehearsal per order, an 8-minute wait for the night answer, and at most one model run per incident and three per night.

**What it needs from Google Cloud for the bonus.** Cloud Run for the shop (`shop`, `shop-staging`) and the relay; Secret Manager for the token; a Cloud Monitoring alert policy with Pub/Sub (alerting policies are charged "no sooner than May 1, 2026" at $1.50 per condition a month, from a search excerpt, unverified; the no-cost fallback is the relay raising alerts from the shop's counters); one Cloud Scheduler job each minute; Cloud Logging for the evidence pack; Cloud Build, Artifact Registry and keyless Workload Identity Federation, already built in `deploy/`. The live link is the relay's status page (tonight's orders, last night's log) with a passcode-protected "run a demo night" button, capped at five runs a day. Every flow runs on Duo's default model, Claude Sonnet 4.6 served from Google Cloud, so one night touches all three sponsors.

**Autonomy and prizes.** Hands-off: she sets the intent once at dusk and walks away, and nobody approves the 03:12 change. Target Path A Best Hands-off Agent ($5,000) plus Most Stages Covered for Path A ($5,000). One risk: a judge reads the dusk signature as a gate. The form and the video need one line saying she approves bounds once a night, not steps.

**The load-bearing risk.** A flow started at night by code, with nobody awake. The relay's Flows API call with Alex's token must start the custom flow in the hackathon project and get its note within about five minutes; our role's rights, identity verification, a composite-identity requirement, credits and runner start time are all open (unverified). The second dependency is the signature: October subgroups let only Maintainers merge to the default branch by default, so the fallback signature is an MR approval. Fallbacks, in order: (1) the relay starts a pipeline instead, and a Pipeline events trigger or a headless Claude Code job returns the same request; (2) Standing Orders: no model at night, code runs a signed order when its condition holds, and the model still drafts at dusk and writes the log at dawn (about 86.5).

**Working scope by Oct 24, and the biggest failure risk.** Real: the dusk flow on a real watch issue, drafting from MRs really merged that day; the rehearsal on the real staging service; the merge or approval as signature; a real alert on production Cloud Run; the relay opening a real incident, starting the real watch flow, checking its note against the merged file and turning off a real GitLab flag the app reads; the re-check; a real push page and thumbs-up; the 07:00 expiry, the dawn log and the countersign MR; CI with tests, scans, keyless deploys and flow checks. Labelled demo data: the shop, its customers and traffic, both planted faults, the injection line, the persona (Alex's account plays Priya), and the clock (a demo night runs in about 25 minutes). Cut: the `max_instances` action, Firestore, GitLab escalation-policy paging (needs Maintainer), Code Owners on `ops/`; the Duo Developer fix MR is filmed only if it works first time. Never cut: the dusk draft, the signature, the two-key night check, the dark phone, the wake page. **Biggest failure risk:** the first real night runs too late. Every step that needs Alex's hands waits until about Oct 23, so a platform surprise in the night start would appear with a day left, and the 03:12 scene would have to be filmed with Standing Orders. Prevention: the one-hour day-one test this week and two full test nights by Oct 21.

**First build step.** Today, with no accounts: the orders schema, `relay/orders.py` (load the signed file, the conditions, the request check, the floor, expiry, the once-a-night ledger, the thumbs-up rule), `relay/demo_night.py` (a labelled demo night replayed from fixtures), `tests/test_orders.py` (one test per refusal reason), and the three flow files checked in CI. Size: about 4,300 lines and about 17 agent-days, the largest of the five.

### 6.2 No Mouse (C13): Supervised, 84.8

[Full brief](research/ideas/brief_C13_no_mouse.md) (merged with Spoken Diff)

**Name and pitch.** The name says the agent's rule in two words and echoes the #NoMouse Challenge, a yearly week in which people try the sites they use with the keyboard only. Pitch: before a release reaches production, an agent with no mouse and no screen must buy something on staging using only what a screen reader would announce. If a person who relies on a screen reader would get stuck, it holds the release, lets the developer hear what that person would hear, and opens the fix.

**Who it is for, and the story.** Small product teams that ship every week with no accessibility specialist and nobody who uses a screen reader; it protects their customers who do. Maria (persona) is blind and has ordered coffee beans from the same small online shop every month for four years with her screen reader. On Friday the shop's developer merges a checkout redesign that turns the Pay, Edit cart and Coupon buttons into icons, and nobody notices. Before it reaches production, No Mouse makes her purchase on staging by ear, hears "button, button, button" where it used to hear "Pay now, 18 dollars, button", holds the release and hands the developer the recording and a one-line fix.

**One person's specific problem.** After the redesign, the Pay button is a lock icon with no name, so Maria's screen reader reads it as "button", next to two other unnamed buttons, and the first one she tries sends her back to her cart. The developer cannot hear this: nobody on the team uses a screen reader, and every test and scan passed.

**Closest past winner, and the difference in behavior.** Moonwalk, winner of the UI Navigator category in Google's Gemini Live Agent Challenge (2026): a hands-free desktop assistant that drives a Mac through the macOS accessibility APIs, speaks through Cloud Text-to-Speech from Cloud Run, and makes the user click "Proceed" before risky plans. Moonwalk completes a task for the person in front of it, by whatever works. No Mouse attempts one shop journey on a staging copy, limited to the keyboard and what a screen reader would announce, in order to find where a screen reader user would fail. It acts only after a person merges and a code replay fails; it produces a verdict computed by code, audio, an issue naming the MR that caused the barrier, and a fix MR; and on its own it can only hold a release. (Launch Control, February 2026, judges an MR from its contents when asked; No Mouse judges a deployed build by doing the purchase.)

**The demo moment.** A black screen while a synthetic voice reads the checkout the way a screen reader would, ending on "Button. Button. Button." Later the same voice says "Pay now, 18 dollars, button. Order placed, heading level 1." The viewer feels the gap without being told. If Alex can, one calibration clip shows a real screen reader (VoiceOver on his phone) saying "button" on the same broken page.

**What judges see in the first 30 seconds.**

- 0:00 to 0:02: black, one real keypress, and a small label: "Simulated screen reader output, read aloud by Google Cloud Text-to-Speech".
- 0:02 to 0:12: black, and a fast synthetic voice: "Demo Beans. Checkout, heading level 1. Ethiopia Yirgacheffe, 12 ounces, 18 dollars. Button. Button. Button."
- 0:12 to 0:16: silence, and the words "This is what Maria hears at checkout after Friday's redesign." Small: "Maria is a persona."
- 0:16 to 0:23: the real staging checkout; the focus ring steps over a tag, a pencil and a lock icon, each read as "Button." Caption: "A sighted person sees a lock. A screen reader says 'button'."
- 0:23 to 0:30: the GitLab pipeline with `replay-staging` red and `deploy-production` waiting, then the title. Alex: "Nobody on the team uses a screen reader, so nobody heard it. No Mouse did, on staging, before it shipped."

**The end-to-end flow, one release.**

1. A person merges the redesign MR. CI builds the image, runs SAST and secret detection, and deploys `shop-staging` to Cloud Run keylessly.
2. `replay-staging` (code only, no model) replays each recorded journey with Playwright through the accessibility tree; GitLab's Pa11y job checks the pages; a `speak` job makes the audio with Cloud Text-to-Speech. Here the replay fails at Pay, so the pipeline fails.
3. The failed pipeline starts the `no-mouse` flow. Claude walks the journey by ear, choosing every key from what it hears.
4. Code gives the verdict: clear, friction (it still works but takes more than 25% more actions, so a person decides), guessed or blocked, with the WCAG 2.2 criterion and the spoken difference from the recorded path.
5. On a barrier, the flow finds the line that removed the name and opens an issue (transcript, audio, the MR that caused it) and a draft fix MR.
6. The fix MR deploys a no-traffic Cloud Run revision tagged `fix` and is replayed there, with before and after clips. A person merges it, and the staging replay is clear.
7. A person presses Play on the manual `deploy-production` job; a hold can be lifted only by merging an override file with a reason. Production is replayed, and a GitLab Release says "Maria's path: clear, 31 keys", with the audio. A daily schedule repeats the production replay.

**Every stage, and the GitLab feature behind it** (all nine; five specific to the idea, govern half, three thin):

| Stage | GitLab feature (and Google piece) |
|---|---|
| Plan | The issue the flow opens (transcript, audio, WCAG criterion, the MR that caused it); journeys are files a person merges |
| Create | The fix MR, and an MR that records the agent's new path as the replay test |
| Verify (the core) | `replay-staging`, the walk by ear, the JUnit report, the Pa11y accessibility report and MR widget, a review app on a tagged Cloud Run revision |
| Package (thin) | Shop and walker images in the registry |
| Secure (thin) | SAST and secret detection; a network allowlist, keyless auth, a listener that cannot write, a prompt-injection page in the evals |
| Release | Staging and production environments, the hold through `needs`, the manual production job, the override file, a GitLab Release with audio |
| Configure (thin) | `.gitlab/duo/agent-config.yml` (image, network policy); journeys and budgets as files |
| Monitor | A production replay after each deploy, a daily scheduled replay, an incident on failure |
| Govern | Gates only a person can pass (merge, Play, an override with a reason); CODEOWNERS on journeys and holds if our role allows; sessions as the audit trail |

**The actual Duo Agent Platform workflow.** One custom flow, `no-mouse`, started by Pipeline events: Failed (round one), Merge request: Marked ready (round two, on the fix preview) or a Mention. Components: `listener` (an agent with `get_pipeline_failing_jobs`, `get_job_logs`, and `run_command` used only for the walker); `can_pay` and `same_effort` (DeterministicStepComponents that run the code verdict); `ask_person` (a HumanInputComponent that approves a longer path); `path_writer`; `investigator` (read-only); `issue_writer` (one-shot); `fix_writer`. Routers send a clear walk to `path_writer` (a longer one first to `ask_person`) and a failed one to `investigator`, then `issue_writer` and `fix_writer`. No route ships anything. Plain CI does the build, scans, deploys, code replays, Pa11y, speech, the manual production job and the release. The flow file passed GitLab's `flow_v2.json` with zero errors; it has not run on GitLab.

**The agent loop.**

- **The listener may** choose each action from a fixed menu: Tab, Shift+Tab, Enter, Space, Escape, arrows, typing, jumping to the next heading, landmark, field, button or link, listing them, hearing an item again, or saying "stuck". **It may not** see screenshots, pixels, HTML or the page structure, use a mouse, reach the shop except through the walker, write to GitLab, or decide pass or fail.
- **The investigator** only reads. **The writers** word the issue and choose the smallest fix; they may not change the verdict or the transcript, touch journeys, holds or the CI file, merge, deploy or lift a hold.
- **Code decides** what the listener hears (rendered from the accessibility tree by one file of rules), the verdict (an order exists within budget, no unnamed control was pressed, no focus trap), the WCAG mapping, every budget, and whether production may deploy.
- **A person decides** which journeys exist, whether a longer path is fine, whether the fix merges, whether the release ships, and whether a known barrier ships anyway.
- **Time boxes:** 60 actions and 10 minutes per walk, 120 to 180 seconds per model call, and at most two fix rounds, then a person takes over.

**What it needs from Google Cloud for the bonus.** Cloud Run `shop-staging` and `shop-production` (the public link: "Put your mouse away and buy a bag of coffee"), revision tags for fix previews, Cloud Text-to-Speech (the first 4 million Standard or WaveNet characters a month are free), Cloud Build, Artifact Registry and Workload Identity Federation. A fallback listener would use Claude on Google Cloud's Agent Platform (whether the Free Trial covers partner models is unverified). Nothing on the public shop calls a model, so visitors cannot run up a bill.

**Autonomy and prizes.** Supervised: a person approves the outcome by merging the fix and pressing Play. Two judges called it Hands-off, but by the official text a person in the middle makes it Supervised. Target Path A Best Supervised Agent ($4,000) plus Most Creative ($4,000), which goes to the top Innovation score; No Mouse has the highest in our pool.

**The load-bearing risk.** Claude has to choose every key inside the GitLab loop, from announcements alone. On the platform side, the flow needs a browser it can drive that reaches staging (a custom image, the sandbox, a network allowlist on the default branch, and possibly a strict mode that ignores it). On the model side, text alone must be enough to finish the clean checkout every time. Fallbacks, in order: run the browser outside the sandbox; move the listener into a CI job with Claude on Google Cloud (Claude still chooses every key); last, a scripted replay that keeps the spoken transcript (about 79). Day-one test: a one-component probe flow presses Tab five times on staging and reports what it heard; decide by Oct 8.

**Working scope by Oct 24, and the biggest failure risk.** Real: a merge starting the full pipeline (build, scans, staging, replay, Pa11y, speech); the flow started by the failed pipeline, the walk by ear, the code verdict, a real issue and fix MR; the fix on a tagged revision; a person merging and pressing Play; the production replay and a GitLab Release with transcript and audio; a 13-page eval set (6 clean pages, 6 with one barrier each, 1 with injected instructions) with results in the README. Labelled demo data: Maria, the "Demo Beans" shop, test orders and the test card, the planted redesign MR, the injection page. Cut: real screen readers in CI (one calibration clip only), more than two journeys, other assistive technology, mobile, protected environments (a manual job instead), the feature-flag stretch. **Biggest failure risk:** the listener is slow or confused on a page that works. A 40-step walk can take 5 to 10 minutes, and a confused walk ends with no order, which code reads as blocked: a false hold, which on video looks like a broken gate. Mitigations: screen-reader jumps cut the clean path to about 15 to 20 actions, the free replay runs first, an unexplained "blocked" gets a second walk, and the eval set measures the false-hold rate before filming.

**First build step.** Today, with no accounts: `shop/` (a FastAPI demo shop with a switch that plants the three unnamed icon buttons), `nomouse/` (the walker: the action menu, an announcement renderer reading the accessibility tree, a log, and the commands probe, act, walk, replay and verdict), the first two transcripts (clean and planted), the journey file, six eval pages, and the draft flow file. Size: about 3,400 lines and about 9 builder days.

### 6.3 Forget Me (C37): Supervised, 81.7

[Full brief](research/ideas/brief_C37_forget_me.md)

**Name and pitch.** It is what a person means when they press "Delete account", and it echoes the legal "right to be forgotten". Pitch: on every release, a person who does not exist signs up, uses the new feature and asks to be forgotten; code then looks for her in every store, and a release that cannot forget her does not reach production.

**Who it is for, and the story.** The developers and the privacy lead of any app with a "Delete account" button, and the people who press it. Dana (persona) let her nine-year-old son use a homework-help app through fourth grade, and when he outgrew it she pressed "Delete account", because the app promised that everything he had typed would be gone. This week a developer adds "search your old questions", which copies every question into a new search index that the deletion job has never heard of. From this release on, a deleted child's words would quietly stay behind, and Dana would never know. (The brief replaced the first persona, a woman leaving an abusive partner, because a short DevSecOps video cannot treat that with care; the parent's story has a documented precedent in the FTC's 2023 case over children's Alexa recordings, from search excerpts.)

**One person's specific problem.** The delete path still removes the son's account, questions and uploads, but the new search feature has copied every question into `questions_index_v2`, a store the delete path does not know about, so his questions outlive the deletion. Nothing fails when that happens (no test, no alert, no complaint), because Dana cannot see inside the app and the team does not know the copy exists.

**Closest past winner, and the difference in behavior.** Compliance Sentinel, an honorable mention in GitLab's February to March 2026 hackathon, the only past GitLab winner found with an explicit right-to-erasure check: a GDPR Article 17 rule that a delete endpoint must exist and cascade. It reads code, and the model's reading sets a passed, warning or failed label. Forget Me runs: code creates a synthetic person through the deployed staging app, deletes her through the real delete path, and searches Firestore, Cloud Storage and Cloud Logging for her marker. On this release, Compliance Sentinel's structural check could pass (a delete endpoint exists); Forget Me shows red, observed rather than inferred. Code, not the model, decides the verdict; `needs: forget_me` keeps production closed; and a person picks the fix direction before any fix is written.

**The demo moment.** The staging probe table after Robin, a child account that does not exist, asks to be forgotten: four rows green and one red, `questions_index_v2 | kept | new in !12 | marker fm7731qzx still present 60 s after deletion (3 documents) | RED`. Narration: "This is where Dana's son's questions would have stayed." After the fix the table is all green: "Robin is gone from everywhere, 38 seconds after she asked."

**What judges see in the first 30 seconds.**

- 0:00 to 0:08: a phone frame on the demo app "Homework Helper": a red "Delete account" button and "Everything your child typed will be removed." A thumb taps it: "Account deleted." A corner tag stays on every frame: "Persona, demo app, demo data". Voice: "Dana deleted her son's account on a homework app. It promised that everything he typed was gone."
- 0:08 to 0:16: MR !12 "Search your old questions", one highlighted line that writes question words into `questions_index_v2`. Voice: "This week's release copies every question into a new search index. The delete button has never heard of it."
- 0:16 to 0:30: the pipeline (`forget_me` red, `deploy_production` grey), then the job log with one red row. Caption: "Robin is a test child who does not exist." Voice: "Before the release reached anyone, Forget Me sent in Robin, a child who does not exist, and asked the app to forget her. Sixty seconds later her question was still in the new index, so the release stopped."

**The end-to-end flow, one release.**

1. A work item, "Erasure promise" (no copy in any store within 2 minutes on staging and 30 days everywhere), is linked to `privacy/stores.yml`, the list of places the app keeps personal data.
2. A developer opens MR !12. The Merge request: Created trigger starts the map flow, which reads the diff, the store list and the delete code, and commits the new store and an "ask and search" journey to the MR's own branch. It says nothing about whether deletion works.
3. The MR pipeline checks the store list's schema, and a reviewer merges.
4. The image is deployed by digest to staging Cloud Run, keylessly. The `forget_me` job (code) creates Robin with a fresh marker in every field, walks the journeys through the app's API, proves the marker reached every store it should (otherwise gray, which blocks), uses the same delete path Dana used, waits up to 120 seconds, and searches every listed store plus every collection code can list. One row is red, so the job fails and the manual production job, which needs it, cannot run.
5. The failed pipeline starts the gap flow. It reads the report and the delete code and drafts option A (extend the delete path) and option B (stop copying the text). A HumanInputComponent sends the privacy lead a To-Do and an email, and she approves A.
6. The flow opens fix MR !13 (one handler, one test). A person merges it, and the re-probe is five of five green: gone in 38 seconds.
7. A person presses Play on production. A GitLab Release carries the erasure table, and the JSON report goes to the generic package registry. Every night a schedule runs a new canary through production and checks log retention and Cloud Storage soft delete against the promise.

**Every stage, and the GitLab feature behind it** (all nine; six load-bearing, three light):

| Stage | GitLab feature (and Google piece) |
|---|---|
| Plan (light) | The "Erasure promise" work item; an issue for any store the probe cannot read |
| Create | MR !12, the flow's store-list commit to it, fix MR !13 |
| Verify | MR and main pipelines; the `forget_me` probe before and after deletion |
| Package (light) | Image deployed by digest; the erasure report in the generic package registry |
| Secure | Deletion tested as a privacy control; logs are a "never" store that must never hold the marker; keyless `id_tokens` and a read-only probe identity; SAST and secret detection |
| Release | Staging and production environments; the manual production job with `needs: forget_me`; a GitLab Release with the erasure table |
| Configure (light) | `privacy/stores.yml` and the promise drive the probe; the nightly run checks retention and soft-delete settings |
| Monitor | A nightly schedule with a new canary on production; results in GitLab Observability |
| Govern | The HumanInputComponent for the fix direction; review and merge; Play; erasure history on every release |

**The actual Duo Agent Platform workflow.** Two custom flows that read and write GitLab only; every Google call happens in plain CI. `forget-me-map` (Merge request: Created; a Mention allows one revision): `mapper`, a read-only agent, then `writer`, which commits to the MR branch and posts a three-line note. `forget-me-gap` (Pipeline events: Failed, or a Mention): `triage` (answers gap, exhausted or not_mine), `gap_reader` (quotes the red rows and drafts options A and B), `fix_choice` (a HumanInputComponent approval), `fixer` (opens the fix MR), and `stop_note` (after two failed fixes). Plain CI holds the store-list check, the staging deploy, the probe, the manual production job, the release and the nightly run. The two sides meet in the job log: the flow reads the probe's report with `get_job_logs`.

**The agent loop.**

- **The model may:** read the diff, the code and the store list and decide where a person's data now lands, including indirect copies (indexes, caches, exports); propose each new store's class and how its copy is transformed, from a fixed menu; write the canary's journeys to the MR branch; after a red result, draft fix options and open the fix MR once a person picks one.
- **The model may not:** see or choose the marker, see real records, say whether anything is deleted, touch Google Cloud, change the delete code before a person's choice, merge, deploy, run the probe, change the promise, or draft a third fix.
- **Code decides:** the marker and its variants; that the canary reached each store before deletion; that it is gone within the window; that logs never held it; that no listed or listable store still holds it; that every collection is mapped (an unmapped one blocks); and, through `needs`, that production stays closed.
- **A person decides:** the merge of the feature MR (including the agent's commit), the fix direction, the fix merge, Play on production, and what to do about stores the probe cannot read.
- **Time boxes:** 300 seconds per agent, a 15-minute probe job, 120 seconds of polling on staging, and at most two fix MRs per gap, then a person takes over.

**What it needs from Google Cloud for the bonus.** Two Cloud Run services (`homework-staging`, and `homework` as the judges' live link), Firestore (accounts, questions and the new index), a Cloud Storage bucket per environment (soft delete off on uploads), Cloud Logging (a "never" store), a read-only probe service account reached through Workload Identity Federation, Cloud Build and Artifact Registry. All fit the free tiers. Optional: Claude on Google's Agent Platform for an adversary job that asks "Where could a copy of this person hide after this change?"

**Autonomy and prizes.** Supervised: the agents map, probe, read and draft on their own, and a person approves the fix direction, the fix and the release. Target Path A Best Supervised Agent ($4,000) plus Most Stages Covered for Path A ($5,000), with Most Creative as a second chance.

**The load-bearing risk.** Proving presence before absence on real stores. A green only means something if the canary provably reached each store and code could find it there afterwards. That needs keyless, read-only Google access from CI on protected main (never tried in our account), copies whose shape does not hide the marker, and writes and log ingestion fast enough that "not found" is clear. Fallbacks: run the probe as a Cloud Run job; cut to Firestore plus Logging; last, probe a local copy of the release in CI (the bonus and some Technological Implementation go). Day-one test, about 30 minutes of Alex's time, ideally by Oct 13: a minimal app that writes two collections and a bucket, logs one marker line on purpose and keeps a `shadow_copy` the delete path skips. It passes if the marker is found everywhere before deletion and gone after, except in `shadow_copy` (red), and a write with the probe identity is refused.

**Working scope by Oct 24, and the biggest failure risk.** Real: the demo app on two Cloud Run services with Firestore, buckets and Cloud Logging; the map flow on a real MR; the keyless probe on main with the production job held; the gap flow on the real failed pipeline with its approval; the fix, the green re-probe, production deployed by a person, a GitLab Release; the nightly schedule, with at least two real nights before the video. Labelled demo data: Dana, "Homework Helper (demo)" and its seeded users, Robin (a synthetic child account really created and deleted on every run), the omission planted in MR !12, and Alex playing both developer and privacy lead. Cut: a pre-merge probe, outside services, backups as timed stores, BigQuery, protected environments if our role cannot set them, self-promoting green releases, and the Claude Code adversary unless time remains. **Biggest failure risk:** the setup only Alex can do arrives too late (the Google project and its keyless trust, the two flows and triggers, merges to main: about 90 minutes in all). If it slips past about Oct 15, the first real probe on main leaves no time to fix what it finds, and the video shows the local fallback.

**First build step.** Today, with no accounts: `forgetme/marker.py` (a marker that survives lowercasing and word splitting), `rules.py` (green, red and gray), `stores/` (an interface, an in-memory fake and a SQLite adapter, with the Google adapters tested against labelled fakes), `report.py`, the demo app with the planted index on its own branch, `privacy/stores.yml` and its schema, the two flow files, and one end-to-end test: the planted index gives exactly one red row, and the fix gives all green. Size: about 2,650 lines (600 of them tests) and about 8.5 builder days.

## 7. The runners-up

**Writeback (C27), Supervised, brief-adjusted 80.1** ([full brief](research/ideas/brief_C27_writeback.md)). When someone fixes production by hand during an emergency, the next deploy stops instead of erasing the fix, and an agent writes the fix into code in that person's name, for them to keep or discard. Clara (persona) raises Cloud Run memory from 256Mi to 512Mi in the console at 02:10 to stop a crash; at 10:00 a teammate's routine deploy would put 256Mi back, so a guard job stops it ("Deploying now would undo a change Clara made by hand at 02:10") and a merge request in her name is waiting when she wakes. It has the cleanest split in the pool (code finds the change and holds the deploy, the model finds the reason and writes the code, the person keeps or discards), needs no flow to start without a person, does real work on Google Cloud, touches all nine stages (eight with its own work) and is the smallest build (about 1,200 lines). It is not in the top three because it is the weakest of the five on the official criteria (mean 7.33) and on Innovation (6.3, then 5.7 after its brief found driftctl, env0, Firefly, StackGuardian and AWS's drift-aware change sets), and its human moment is milder (6, then 6.5). Its brief argued for third place on build risk, but only against Forget Me's first-pass 80.0; Forget Me's own brief moved it to 81.7. Writeback stays useful: its guard is a one-day add-on to Night Orders (anything changed under a night order gets written back in the signer's name), and its day-one test proves the same CI-to-flow hand-off that No Mouse's fallback needs.

**Front Row (C12), Supervised, brief-adjusted 76.7** ([full brief](research/ideas/brief_C12_front_row.md)). When a bug is fixed, the people who reported it get the fix first if they agreed to, they hear about it in their own words, and their answers help a person decide when everyone else gets it. Samir Haddad (persona), who runs a two-person print shop, reported that invoices printed after 5 p.m. carry tomorrow's date; sixteen days later the fix is switched on for his account before anyone else's, through a feature flag user list, and a note quotes his own words back to him. The climax is another reporter's "still wrong" reply, which holds the release for 2,000 other demo accounts until a second fix reaches her first. It ties Forget Me on the official criteria (7.67) and loses the tie-break on Technological Implementation (7.0 against 7.7). It is not in the top three because its total is the lowest of the five (76.7); its novelty fell to 5.0 once the brief found fix-first flags and close-the-loop tools in commercial use and BugFlow among past winners; the judges split (GitLab ranked it second, Google seventh, and the Anthropic persona left it out and called its framing a trap next to Proof of Fix and the banned notifier); and its load-bearing step, emailing reporters and reading their replies through Service Desk from a flow, is untested. **Front Row is the first alternate.** It moves up if Night Orders fails its day-one test, or if Alex prefers the "user who feels heard" story: it is the only finalist that tells it, and every one of its starts is an ordinary human action. Its brief adds No Mouse's browser test as a second trigger, and says that if Front Row is chosen for its story it should replace Forget Me, not either of the top two.

## 8. The recommendation, argued

Night Orders leads on our total and on the official criteria, but section 3 explains why those numbers are not the argument on their own. The case rests on what past winners did and on where the October field is empty.

### Against the ten rules from past winners ([PATTERNS.md, section 7](PATTERNS.md#7-ten-rules-for-our-entry))

1. **One job, outside the crowd.** In one sentence: before bed, she signs what the agent may do alone tonight, and everything else wakes her. It is not a release gatekeeper and not pre-merge review: it never decides whether code ships, and its hero action is a feature flag, not a deploy or a rollback.
2. **Real runs inside our own GitLab project.** Every night leaves a trail a judge can click: the watch issue, the flow-written orders MR, rehearsal jobs in CI, an incident with timeline events, flow sessions, the flag change, the watch log and the countersign MR.
3. **One human decision point, built in code and shown as a feature.** The merge at dusk is the signature, and code trusts nothing else. This also squares the evidence with the theme: past GitLab winners stopped at a human yes before anything that mattered (15 of 22 known), while October's theme is Hands-off. Night Orders keeps the yes but moves it to dusk, which is what the patterns ask of a Hands-off entry: show the intent, code guardrails and a stop rule, with no human in the middle ([PATTERNS.md, 6.2](PATTERNS.md#62-each-pattern-against-the-criteria-and-prizes)).
4. **A narrated video, person and pain first.** The first 30 seconds are scripted (section 6.1): 03:12, Priya asleep, the error line, the dark phone, then the title.
5. **A real person in a real moment, plus a number.** A new parent on call for the first time since her daughter was born; all three judges gave the human moment a 9. The number to show is the night's own record (what fired, what the agent did, what it declined, what woke her), each line linked to an incident event.
6. **Code decides what is true, and every loop is time-boxed.** Two keys at night, a test for every refusal reason, prompt timeouts, at most one model run per incident and three per night. The rule also asks for one eval with a number. The brief has the tests but no eval set yet, so we suggest adding one (our suggestion, not in the brief): for example, the watch prompt run over labelled demo nights, with the share it got right.
7. **Deep, named sponsor use.** Three Duo flows with two kinds of start (a trigger and the Flows API), narrow components with scoped tools, a HumanInputComponent, Claude through Duo, and Cloud Run, Secret Manager, Cloud Monitoring, Pub/Sub, Cloud Scheduler and keyless deploys on Google Cloud. Sponsor depth scored 9, the highest of the five.
8. **Honest labelling.** The planted faults, the compressed clock and the persona are labelled on screen all night, and in the README and the file names.
9. **A README for a judge who reads for 60 seconds.** One line ("Before bed, you sign what the agent may do alone tonight. Everything else wakes you."), the live status page, and a real orders MR and a real incident to click.
10. **One path prize plus one special prize, and the agent stays inside our project.** Best Hands-off Agent plus Most Stages Covered (Path A); the agent touches only our project and our own Google services.

### Against the field ([FIELD.md](FIELD.md))

- **Nobody in October is doing on-call.** FIELD lists on-call alert handling and the human handoff at night as open: no October entry, 2 of 506 February catalog projects, and no June catalog item ([FIELD.md, section 6](FIELD.md#6-open-spaces-nobody-seems-to-be-in-them-yet)). FIELD's caveat holds: the space is open only if the core is the human handoff, not root-cause chat, and Night Orders never names a culprit.
- **It stays out of the three most crowded spaces:** release gatekeepers (4 of 7 known October ideas, and the judges' own reference project), security review and auto-fix (132 of 506 February catalog projects did security review), and pre-merge impact review (69 June entries) ([FIELD.md, section 5](FIELD.md#5-crowded-idea-spaces-to-avoid-ranked)).
- **It answers GitLab's own theme**, "Hands Off. How far can your agents go without you?" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)): as far as she signed, for tonight only. The hands-off entries seen so far are mostly Path B release gatekeepers, and Path A's Best Hands-off Agent is the largest path prize ($5,000).
- **Its main action sits in the least touched stage.** A feature flag change is configure work, a stage only one of the seven known October ideas even claims.

### The tradeoffs, plainly

- **The night start depends on the Flows API**, called by our own relay with a personal token. It may be refused, or need rights we do not have (unverified). If it fails, the pipeline route is tried next, and then Standing Orders: no model at night, code runs only what she signed, and the model still drafts at dusk and writes the log at dawn. That scores about 86.5 and still films the dark phone honestly, but the "model checks the reason" key is gone.
- **The novelty is moderate.** PagerDuty markets an SRE agent that triages "without waking a human", its runbook automation has long run remediation "to remediate an incident as it occurs and prevent paging a subject matter expert", and AI SRE guides recommend "pre-approved, narrowly-scoped actions" (all from search excerpts or links the coordinator supplied; the pages are blocked here). GitLab's own Auto Rollback and February's ZeroTouch Monitor roll back on alerts. The idea is the signed nightly fence: drafted from the day's changes, rehearsed before she signs, void at 07:00, and the model can decline an order but never widen one. Never call it "first".
- **It is the biggest build of the five:** about 4,300 lines and about 17 agent-days in an 18-day window, against 1,200 to 3,400 lines for the others.
- **Several steps need Alex's hands** (about four hours: identity verification, enabling three flows and a trigger, the token, the Google trial, merging on test nights, filming), and our workspace role may block merging to main. Fallback: an MR approval as the signature.
- **The video must label the time compression and the planted faults.** A demo night runs in about 25 minutes, with 2-minute windows instead of 5 and 10.
- **A judge may read the signature as a gate** and file the entry under Supervised. One line in the form and the video must say she approves bounds once a night, not steps, and that nobody approved the 03:12 action.
- **The repo is public**, and our own lenses reached Night Orders three times, so a rival may reach it too ([FIELD.md, section 7](FIELD.md#7-watch-list)).
- **No Mouse has the better 30-second moment** (wow 10 from all three judges, against 9) and the best Presentation and Innovation scores in the pool. It is the backup. Its brief asks that the choice between the two be settled by the two day-one tests (its browser probe and Night Orders' night start), not by more scoring.

### Prize plan

Path A Best Hands-off Agent ($5,000) plus Most Stages Covered for Path A ($5,000). Each project can win one path prize and one special prize ([RULES_CHECK.md](codex/RULES_CHECK.md#multiple-prize-eligibility-and-tie-breaking)), so this is the most one entry can win. Night Orders touches all nine stages, seven of them strongly, each with a specific job inside one loop, shown as a strip at the end of the video. Most Creative (the top Innovation score across both paths) is a stretch, not the plan. If Standing Orders replaces the night model, the night action still has no approver, so the level and the plan stay the same.

## 9. What happens next

**The day-one test** (from the [Night Orders brief, section 10](research/ideas/brief_C01_night_orders.md#10-load-bearing-risk-fallback-and-day-one-test); about one hour once the workspace exists):

1. Create a probe flow, `night-orders-probe`: one AgentComponent with `get_issue` and `create_issue_note`, `coding_environment: none`, and the prompt "Read the issue named in the goal and post one note: probe ok". Enable it in the showcase project and add one Assign trigger. Pass: both work with our role.
2. Get its consumer ID with the GraphQL query `aiCatalogConfiguredItems`.
3. Create a personal access token with `api` scope, expiring 2026-11-20.
4. From Cloud Shell, POST `/api/v4/ai/duo_workflows/workflows` with `project_id`, `ai_catalog_item_consumer_id`, `issue_id`, `goal`, `start_workflow: true` and `allow_agent_to_request_user: false`. Pass: a 201, a session in AI > Sessions, a `duo_workflow` pipeline, and the note within five minutes. Record the time.
5. The real test: deploy a 40-line relay to Cloud Run that reads the token from Secret Manager and makes the same call when a one-off Cloud Scheduler job fires, with nobody logged in, then polls the issue until the note appears. Pass: the relay sees the note.
6. In the same hour: merge an MR into the default branch (or, if that is refused, approve one); turn a feature flag off with the token; create an incident through the REST API.

**Decide by the end of day two, before any prompt work.** If steps 4 and 5 pass, build as designed. If they fail for a fixable reason (identity verification, role), fix it or ask in the hackathon Discord that day. If they still fail, test fallback 1 (the pipeline route) the next day; if that fails too, build Standing Orders. Then run two full test nights by Oct 21. The No Mouse brief asks that its own 90-minute browser probe run too, so the backup is ready and the choice between the two rests on tests.

**The first build step, today, with no accounts** ([brief, section 12](research/ideas/brief_C01_night_orders.md#12-first-build-step-and-build-size)). Write the code-decides core and test it offline:

- `ops/schema/night-orders.schema.json`: the action menu, the targets, at most three orders, expiry no later than 07:00.
- `relay/orders.py`: load the signed file, compute which conditions hold, check a request, the always-wake floor, expiry, the once-a-night ledger, the thumbs-up rule.
- `relay/demo_night.py`: replay a labelled demo night (the 01:50 decline, the 03:12 order, the injection line) from fixture files with a recorded model note.
- `tests/test_orders.py`: at least one test per refusal reason (unsigned, expired, wrong target, second use, condition not holding, action not in the order, the floor, a malformed note, a reaction from the wrong user or before the page).
- Draft the three flow files and check them in CI against GitLab's `flow_v2.json` and `tools.json`.

**Needs from Alex** (about four hours in all, mostly once the workspace exists): the workspace and the role check in step 1, identity verification, the token, the Google trial and Cloud Shell setup, merges or approvals on test nights, and filming.

**Asks for Codex**, who owns `deploy/`: a `shop-staging` service, the relay service and its runtime identity, the secrets, the Cloud Scheduler job, the Pub/Sub topic and the alert policy.
