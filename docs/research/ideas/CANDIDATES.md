# Candidate list for scoring

The four lens files hold 74 raw concepts. Near-duplicates are merged here into 57 distinct candidates. Each candidate names the concept whose write-up is the canonical one; "Merged" lists siblings from other lenses whose best parts count toward it. Full write-ups (person, flow, stages, autonomy, what the model may and may not do, demo moment, nearest crowded space, risk) are in the lens files:

- O: [lens_oncall_inversion.md](lens_oncall_inversion.md) (3am on-call engineer; inversion)
- G: [lens_games_markets.md](lens_games_markets.md) (game design; markets)
- B: [lens_biology_assumptions.md](lens_biology_assumptions.md) (biology; remove the load-bearing assumption)
- P: [lens_people_rituals.md](lens_people_rituals.md) (the person on the other end; rituals from other crafts; the coordinator's own lenses)

| ID | Name | Lens (file) | Merged | One line |
|---|---|---|---|---|
| C01 | Night Orders | on-call (O) | Standing Orders (P) | Before bed the on-call engineer signs a few reversible actions the agent may take alone tonight and exactly when it must wake her. |
| C02 | Night Nurse | biology (B) | Wake Budget (P), Reserve Price (G) | At night the agent gathers evidence and code decides whether an alert is worth waking a person; the rest waits for morning, ready. |
| C03 | Dress Rehearsal | on-call (O) | | When the page comes, likely fixes have already been tried on staging, so the engineer picks a tested option. |
| C04 | Watermelon | on-call (O) | | Monitors are green but customers write in; the agent reproduces it, pages a person, and proposes the missing monitor. |
| C05 | Loose Ends | on-call (O) | Sponge Count (P) | After an incident, every temporary change people made at 3am is found and undone or kept on purpose. |
| C06 | Sleep Debt | on-call (O) | Thymus (B) | Alert rules are replayed against history; the agent proposes rules that would have paged less and still caught real incidents. |
| C07 | Fire Drill | on-call (O) | Booster (B) | Before a first on-call week, a realistic outage from this month's changes is staged on staging and coached. |
| C08 | Someone Awake | on-call (O) | | Before waking the on-call person for a non-critical alert, the agent finds an awake teammate who knows the code and agrees to take it. |
| C09 | Daylight Rollout | on-call (O) | Landing Window (B) | Flag rollouts and risky landings move only while their owners are awake; at night the agent holds. |
| C10 | Plane Mode | inversion (O) | | Before a release, the agent finds knowledge only one person holds and interviews them while they are still reachable. |
| C11 | Return Ticket | inversion (O) | | Every release carries a proven way back; one-way changes are shown and split, and a person signs for the one-way trip. |
| C12 | Front Row | assumption (B) | Promise Kept (O), Try First (P), First Dibs (G) | The person who reported a bug gets the fix first (flag user list or private preview), is told in plain words, and their answer helps a person decide when everyone gets it. |
| C13 | No Mouse | inversion (O) | Spoken Diff (P) | Before production, an agent with only a screen reader's view and a keyboard must complete a real journey on staging; it holds the release if a person relying on it would fail. |
| C14 | Fine Print | inversion (O) | Small Pour (P) | For each dependency upgrade, the agent finds the changelog lines that touch our code and proves each with a test before merge. |
| C15 | Lifeboat | inversion (O) | | Before registry cleanup, the agent keeps every image someone may need to roll back to. |
| C16 | Kill Switch | inversion (O) | | Before a risky change ships, the agent wraps it in a flag tied to the alert that would catch it, so 3am is one switch. |
| C17 | Log Leak | inversion (O) | | After a release, new log lines are checked in production for personal data, and a person approves redaction. |
| C18 | Canary Voices | people (P) | Quorum (B) | During a staged rollout, complaints from users inside the rollout cohort are a signal that can hold the next step. |
| C19 | Fever | biology (B) | | When production is sick the project raises its own guard (approvals, smaller steps, freezes) and lowers it again by itself. |
| C20 | Scar Tissue | biology (B) | | Every emergency patch is remembered; once quiet, the agent returns with the proper fix for the patch author to approve. |
| C21 | Apoptosis | biology (B) | | Feature flags must keep earning their life; unused ones ask once, then remove themselves in an MR a person approves. |
| C22 | Placebo | biology (B) | | The agent checks whether incident rituals actually work by comparing with times nobody did them. |
| C23 | Mutualist | biology (B) | | When we work around a library bug, the agent reports it upstream with a minimal reproduction, watches for the fix, then removes our workaround. |
| C24 | Wince | biology (B) | | Retry clicks count as pain; flaky tests that hurt people without protecting anything are quarantined with an end date, and people hear it was not them. |
| C25 | Night Replay | biology (B) | | Each night agents replay the day's human corrections and propose edits to their own skill files for people to approve. |
| C26 | Last Day | assumption (B) | | When someone leaves, everything in the post-code lifecycle that depends on them is found and handed over before they go. |
| C27 | Writeback | assumption (B) | | A manual emergency fix in production is noticed, written back into code in the person's name, and protected from the next deploy. |
| C28 | Teach Back | assumption (B) | | Before a production approval, the approver is asked one cited question about the change most likely to surprise someone. |
| C29 | Learner Permit | assumption (B) | Credit Line (G) | Each production action starts as "ask me"; after a good record the agent asks for a permit to do that one action alone, and loses it on the first mistake. |
| C30 | Postcard | assumption (B) | | A week after a change ships, its author gets a postcard: who used it, what failed, what users said, one decision. |
| C31 | Auditor Hour | assumption (B) | | An auditor's plain question is answered from GitLab records by code, and a compliance lead approves the reply. |
| C32 | Last Caller | people (P) | Sunset (B), Last Caller (G) | Before removing an old API, the agent finds who still calls it, tells each person, and holds removal until traffic shows nobody is left. |
| C33 | Straight Answer | people (P) | | Support asks what it can honestly tell one customer; the agent traces the fix's true status for that customer and offers early access. |
| C34 | Row Call | people (P) | | Before a data migration, see the actual (demo) customers whose records it would change, and exactly how. |
| C35 | Dear Successor | people (P) | | When someone pins, skips or flags something, the agent asks why while they remember, and comes back when the reason is gone. |
| C36 | Kind Revert | people (P) | | When a newcomer's change is reverted, they get the reason, a failing test, and an invitation back. |
| C37 | Forget Me | people (P) | | After each release, the agent proves a deletion request still deletes everything, including new stores the release added. |
| C38 | Cue Light | rituals (P) | | A risky rollout becomes numbered cues; the agent calls standby, only a person says go. |
| C39 | Lockout Tagout | rituals (P) | | When a person works on production by hand, every automation that could touch it is locked in their name until they release it. |
| C40 | Decision Height | rituals (P) | | The agent runs the release alone while every step is reversible and hands the decision to a person at the first irreversible step. |
| C41 | Heat Lamp | rituals (P) | | Fixes that are merged but not delivered are found, and the one person who can deliver each is called with everything ready. |
| C42 | Readback | rituals (P) | Clearing House (G) | At on-call handover the incoming engineer reads back what they are taking over, and the agent checks it against everything in flight. |
| C43 | Fight Call | rituals (P) | | The agent walks emergency runbooks step by step on staging during the day, and fixes the steps that broke. |
| C44 | Site Mark | rituals (P) | | One-off production data fixes touch only records the requesting customer confirmed; code refuses anything unmarked. |
| C45 | Med Rec | rituals (P) | | Before promotion, what each environment needs (variables, flags, limits) is reconciled, and a person settles every difference. |
| C46 | Understudy | rituals (P) | | Post-code tasks only one person has ever done get an understudy who performs the next one with a script. |
| C47 | Shield Wall | game design (G) | | During an incident the agent fields every outside question and later replies personally to each person who wrote in. |
| C48 | Respawn | game design (G) | | After a rollback, innocent changes are re-landed one at a time, so good work returns and the bad change is found by elimination. |
| C49 | Telegraph | game design (G) | | After merge, the agent finds the first scheduled or date-driven moment the new code will meet and offers a dry run of it now. |
| C50 | Next Wave | game design (G) | | Before a planned traffic wave, the paths it will hit are load-tested on staging and defenses are proposed. |
| C51 | Speedrun | game design (G) | | During an outage, the fastest safe pipeline route for a small fix is planned and approved; the full pipeline runs right after. |
| C52 | Tactical Pause | game design (G) | | One command freezes every change in motion during an incident, and on resume the agent proposes the order. |
| C53 | No Reloads | game design (G) | | A pipeline that went green only after a retry is investigated; real intermittent bugs get a reproduction. |
| C54 | Alarm Level | game design (G) | | When a secret leaks, the response runs in phases with a person's go, and the person who leaked it is guided without blame. |
| C55 | Limit Order | markets (G) | | A developer leaves a deploy order with conditions and an expiry; the agent ships only when every condition holds. |
| C56 | Triple A | markets (G) | | Each dependency release and its publisher are rated; top-rated patches merge after a cooldown, low-rated ones wait for a person. |
| C57 | Make Whole | markets (G) | | After an incident, the agent works out which customers were hurt and prepares repairs and credits for a person to approve. |

Notes on merges: Night Orders and Night Nurse stay separate (one grants actions, the other only decides whether to wake). Return Ticket and Decision Height stay separate (one proves a way back exists, the other gates at the one-way step). Wince and No Reloads stay separate (one protects people from flaky tests, the other treats a retry as a possible real bug). Lockout Tagout and Tactical Pause stay separate (a person working by hand versus an incident freeze).
