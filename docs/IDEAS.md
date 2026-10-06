# Ideas: what we build for Life After Code, and why

Part 5 of the research handoff. Written 2026-10-06 for Alex Velazquez (solo, Path A), entering Life After Code, the GitLab Transcend Hackathon ([rules](https://gitlab-transcend.devpost.com/rules), [RULES_CHECK.md](codex/RULES_CHECK.md)).

Inputs, all in [research/ideas/](research/ideas/): the four lens files, [CANDIDATES.md](research/ideas/CANDIDATES.md), [SCORING_RUBRIC.md](research/ideas/SCORING_RUBRIC.md), the four score files and [score_table.md](research/ideas/score_table.md), and the five build briefs. Also [PATTERNS.md](PATTERNS.md) (what past winners shared) and [FIELD.md](FIELD.md) (who else is building). No new web research was done for this file: every fact comes from a linked note, and anything a note marks (unverified) stays marked. People, shops and numbers in the scenes are invented and would be labelled as demo data.

Contents:

1. Recommendation
2. How the ideas were made
3. How they were scored
4. The full scoring table (57 concepts)
5. The five finalists against the five official criteria
6. The top three, one page each
7. The runners-up
8. The recommendation, argued
9. What happens next

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

Night Orders was reached three times on its own: by the on-call lens, by the rituals lens as Standing Orders (hospital orders a nurse may carry out overnight), and by the game and market lenses as overwatch and a stop-loss order ([lens_games_markets.md](research/ideas/lens_games_markets.md), "Also produced by these lenses"). The rituals file notes that convergence cuts both ways: the fit is natural, and other entrants may reach the same idea.

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

