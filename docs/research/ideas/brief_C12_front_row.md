# C12 Front Row: build brief and skeptical review

Written 2026-10-06 for Alex Velazquez's solo Path A entry. Merges Front Row ([lens_biology_assumptions.md](lens_biology_assumptions.md), A2), Promise Kept ([lens_oncall_inversion.md](lens_oncall_inversion.md), 2.3), Try First ([lens_people_rituals.md](lens_people_rituals.md), 1.2) and First Dibs ([lens_games_markets.md](lens_games_markets.md), M6), using the C12 notes in [scores_gitlab_judge.json](scores_gitlab_judge.json), [scores_google_judge.json](scores_google_judge.json), [scores_anthropic_judge.json](scores_anthropic_judge.json) and [scores_engineer.json](scores_engineer.json). Standing today: rank 5 of 57, 75.0 of 110 ([score_table.md](score_table.md)). GitLab docs were read from their source files on gitlab.com on 2026-10-06. All people, shops and tickets are demo personas.

## 1. Name and pitch

**Front Row.** When a bug is fixed, the people who reported it get the fix first if they agreed to, they hear about it in their own words, and their answers help a person decide when everyone else gets it.

Name kept. "Heard" is taken ([FIELD.md](../../FIELD.md), "Seen but not entries"), and a web search plus a GitLab project search on 2026-10-06 found nothing called Front Row in this space.

## 2. Who it is for

For small teams that run support and releases in GitLab, and the customers who take the time to write in.

Samir Haddad (persona) runs a two-person print shop and bills through Ledgerly, a small invoicing app (demo) whose team works in GitLab. On Sept 22 he wrote to support that every invoice he prints after 5 p.m. carries tomorrow's date and two clients asked whether he post-dates his bills; he got "we'll let you know" and expected nothing more. Sixteen days later the fix is switched on for his account before anyone else's, a note quotes his own words back to him, and his reply is one of three that a person reads before the fix goes to everyone.

## 3. Demo moment and video

**The moment (first 20 seconds).** Left: GitLab, Deploy > Feature flags, `fix-invoice-date`, "User list: front-row (3)" in production. Right: Samir's inbox (DEMO): "On Sept 22 you wrote: 'every invoice I print after 5 p.m. says tomorrow.' The fix is on for your account now, before anyone else, because you told us. Print one tonight and reply 'works', 'still wrong' or 'switch me back'." The feeling: remembered, and put first.

**The climax (about 1:30).** Grace Okafor (persona) replies: "The screen is right now, but the export for my accountant still says tomorrow." Code turns that into HOLD, so the release waits for the 2,000 other demo accounts; a second fix reaches her first and she answers "now it's right". The person who complained protected everyone else.

| Time | On screen | Says |
|---|---|---|
| 0:00-0:20 | The moment | "Samir reported a bug 16 days ago. Today he gets the fix before anyone else." |
| 0:20-0:35 | Four Service Desk tickets (DEMO), one never linked | "Fixes go to everyone at once, and the people who wrote in hear last." |
| 0:35-1:05 | Alex comments `@front-row` on bug #41; the Duo session finds unlinked #57; code: 4 reporters, 3 seated, Mei Lin left out (no early-fix consent), fix behind a flag, production serves it | "The model chooses where to look. Code decides who may be seated." |
| 1:05-1:25 | Approval To-Do; Alex adds three IDs to the user list and approves; code: "3 of 3 get it, control does not"; three inboxes | "A person seats them. Code checks before anyone is told." |
| 1:25-1:55 | Replies; `@front-row how is it going?`; HOLD with Grace's words; labelled time jump; round 2 to the same three | "One 'still wrong' holds the release for everyone else." |
| 1:55-2:15 | "Widen to 50%?"; Alex sets it and approves; code: 52% of 2,000 accounts plus the three; later all users; release job; GitLab release | "Every widening is a person's decision." |
| 2:15-2:35 | Diagram (Service Desk, Duo flow on Claude, code checks, person, flag, Cloud Run) and the nine stages | "Two human decisions per fix. The agent never emails anyone or touches production itself." |
| 2:35-2:40 | Title card | "Front Row: the people who tell you what is broken get the fix first." |

## 4. End-to-end flow

**Production feature flag user list, no review app.** The idea is the order of release, which only production has; a private preview asks the reporter to test demo data, turns them into an unpaid tester and drifts toward "confirm the fix", the Proof of Fix family ([FIELD.md](../../FIELD.md), section 3). In production the fix runs on the reporter's own account. The fix merges dark (deployed, off), so no extra environment is needed and taking it back is one click. The deploy skeleton trusts only the protected default branch ([deploy/README.md](../../../deploy/README.md)), so per-MR Cloud Run previews would need a second, wider trust path. And configure is the stage the October field touches least ([FIELD.md](../../FIELD.md), section 6). If a fix cannot sit behind a flag, the flow says so and steps aside.

**A person writes the flag.** Developers may manage flags and user lists ([feature flags](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/operations/feature_flags.md), [user lists API](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/api/feature_flag_user_lists.md)). Flows get no custom CI/CD variables and their token reaches only `ai_workflows` endpoints ([guide](../gitlab_guide_and_reference.md), "Where flows run"), and we will not keep an `api` token for a public project. The click is the decision we want a person to make.

**Honest starts.** Service Desk tickets are created by the Support Bot ([Service Desk](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/project/service_desk/configure.md)), and a bot "cannot activate a trigger" ([triggers](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/duo_agent_platform/triggers/_index.md)), so nothing starts when a customer writes. Every run starts with a person's mention; every decision is a `HumanInputComponent` approval. Not used: "Merge request: Approved", which fires "when a merge request has all required approvals" (unclear with no approval rule) and comes before the fix is live. `@front-row` stands for the flow's service account, probably `@ai-front-row-gitlab-ai-hackathon` (inference).

1. **Report (plan).** Samir emails the project's **Service Desk** address; it creates a ticket (always confidential in a public project) and sends a thank-you email. Support links it to bug **issue** #41. Three more reports arrive; #57 ("receipts dated the 9th on the 8th") is never linked.
2. **Fix, dark.** A developer, or the **Duo Developer flow** when a person assigns #41 to it, opens a **merge request** closing #41 with the change behind **feature flag** `fix-invoice-date`, off in production. The **MR pipeline** tests both flag states, runs SAST and secret detection, and checks the flow YAML against GitLab's schema. A person merges and plays the manual deploy job (Cloud Build, Artifact Registry by digest, **Cloud Run**, keyless Workload Identity Federation, **environment** `production`).
3. **Start run 1 (person).** The release manager comments `@front-row` on #41 (**Mention trigger**, **custom flow**).
4. **Find (model).** The agent reads #41, the MR and the diff, chooses which **Service Desk tickets** to open from the candidates code supplies (last 90 days, at most 50), and names those that describe the same failure, with one-line reasons.
5. **Check (code).** Scripts run with `run_command`: `seat.py` maps senders to demo user IDs by exact email in `demo/customers_DEMO.csv`, drops anyone without early-fix consent, dedupes, caps at 10, marks tickets nobody linked; `is_live.py` checks that the commit the app reports on `/healthz` contains the fix (git ancestry); `guard.py` checks the diff reads the flag. Any failure ends the run with a plain note.
6. **Draft (model).** One note per seated person, quoting their own report, saved as an **internal note** on their ticket. Customer words never enter the repo, an MR, a commit or a release.
7. **Decision 1 (person).** The `HumanInputComponent` raises a **To-Do**: "Seat these 3 in user list `front-row-fix-invoice-date`, then approve to send these 3 notes." Alex adds the IDs (**user list** strategy) and approves, edits or rejects in AI > Sessions.
8. **Tell (code).** `check.py` asks the live app: each seated ID gets the fix, control `cust_099` does not. Only then does `send.py` post each approved note as a public comment, which Service Desk emails ([external participants](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/project/service_desk/external_participants.md): "a notification for each public comment").
9. **Listen, run 2 (monitor).** Replies arrive as external participant comments (no trigger). Alex asks `@front-row how is it going?` (**Mention trigger**); the agent labels each reply works, still wrong, unclear or switch me back, with a verbatim quote. `tally.py`: unclear is never a yes, any "still wrong" is HOLD, fewer than two answers is "not enough to say", silence after 48 hours is not a yes.
10. **Decision 2 (person).** A second `HumanInputComponent` shows the tally (quotes only in an internal note on #41). Clear: "Widen to 50%? Set it, then approve." Hold: "Send Grace this reply and hand the export path to the developer?" Code then checks the effect: 45 to 55 percent of the 2,000 demo accounts, plus all three seated (**percent of users** strategy).
11. **Round 2, only if held.** The second fix ships dark under the same flag, so the three get it at deploy; run 1 tells only them, run 2 listens again. No third round.
12. **Release (release, govern).** Alex widens to all users and approves; code checks; Alex plays the release job, which creates the **GitLab release** with the CI job token ([SPONSORS.md](../../SPONSORS.md), section 2.2). The flow writes the record on #41 (who was seated, what they said, who approved what, when). Support closes the tickets.

## 5. Lifecycle stages

| Stage | Covered | GitLab feature (Google where used) | Real or demo |
|---|---|---|---|
| Plan | Yes | Service Desk tickets, issue links, mention triggers | Real emails and tickets; demo personas on a demo-only mailbox |
| Create | Yes | Fix MR behind a flag (person or Duo Developer flow); drafted notes | Real; bug planted in the demo app |
| Verify | Yes | Tests on both flag states, flow schema check; runtime checks of the served commit and who gets the fix | Real |
| Package | Thin | Image built once, deployed by digest (Cloud Build, Artifact Registry); optional copy to the GitLab container registry | Real |
| Secure | Thin | SAST, secret detection; confidential tickets, internal notes, no public note tool for the model, keyless auth, one-domain flow allowlist | Real |
| Release | Yes | Dark launch, `production` environment, staged widening, GitLab release | Real, live app |
| Configure | Yes | Flag with user list and percent strategies; the app's Unleash client; `.gitlab/duo/agent-config.yml` | Real flag, demo user IDs |
| Monitor | Yes | Service Desk replies after release ([SPONSORS.md](../../SPONSORS.md) 2.2 maps them to Monitor); optional error tracking (read path unverified) | Real feature; replies written by Alex as demo customers |
| Govern | Yes | `HumanInputComponent` approvals in AI > Sessions, consent rule in code, two-round limit, record on #41 | Real; consent values are demo |

Nine of nine touched; seven carry real work.

## 6. The agent loop

- **Model may:** choose which tickets to open and which match; write each note in the reporter's terms; label replies with quotes; look at error events for seated IDs; propose hold or widen.
- **Model may not:** email anyone or comment publicly (its only note tool is pinned `internal: true`, documented for MR notes, unverified for issue notes); change a flag, deploy, merge, close or reopen anything; seat anyone code did not map and find consent for; count an unclear reply as a yes; call a fix verified; put customer words anywhere public.
- **Code decides** (output the model must quote): identity, consent, the cap; whether production serves the fix; who really gets it; whether a widening took effect; the tally and HOLD; what is sent to whom. This folds in Straight Answer (C33): no claim reaches a customer before code checks it.
- **Human decides:** whether to start (a mention); who is seated and what they hear (a flag click plus an approval); widen, hold or stop (the same pair); the release (a manual job); closing tickets.
- **Time boxes:** `params.timeout` 300 seconds per agent component, since GitLab's validator rejects `max_cycles` ([SPONSORS.md](../../SPONSORS.md), section 6, row 1); straight-line runs with one human step and no cycles; 50 tickets, 90 days, 10 people; 48 hours of listening per round (a labelled time jump in the demo); an unanswered approval sends nothing.
- **Two rounds per bug** ([AGENTS.md](../../../AGENTS.md), rule 5). After a second "still wrong" the flow stops proposing and the person chooses: flag off, or everyone with the gap written down.

## 7. Google Cloud for the bonus

- **Needs:** the Ledgerly demo app on Cloud Run, public and live until about Nov 16 ([RULES_CHECK.md](../../codex/RULES_CHECK.md)); Cloud Build and Artifact Registry; keyless Workload Identity Federation from the protected default branch; Secret Manager for the app's Unleash instance ID (`--set-secrets`, runtime identity only). Deploy code stays in the public repo.
- **Free tier:** Cloud Run 2 million requests, 180,000 vCPU-seconds, 360,000 GiB-seconds a month; Cloud Build 2,500 build-minutes a month by the pricing page (120 a day by the Free Program page); Artifact Registry 0.5 GiB-month ([deploy/README.md](../../../deploy/README.md)); Secret Manager 6 active versions, 10,000 accesses, 3 rotation notifications a month ([google_cloud.md](../sponsors/google_cloud.md)). The USD 5 budget alert does not cap spending; stay on the unbilled Free Trial ([SPONSORS.md](../../SPONSORS.md), section 1, fact 7).
- **Design notes:** the app makes no model calls, so judges' traffic costs no tokens. Flags are read on the request path with a 10-second cache, because Cloud Run throttles CPU outside requests. The flow reaches the app through `*.run.app` in its allowlist (unverified under strict mode; fallback: a manual CI job runs the checks and the flow reads its log with `get_job_logs`).
- **Asks for Codex** (owns `deploy/`): label the live service's environment `production`, add `--set-secrets`, point `APP_DIR` at the app.

## 8. Anthropic models

- Every flow run uses Duo's default, Claude Sonnet 4.6 served from Google's Gemini Enterprise Agent Platform. Custom flows reject `model` and only GitLab, as top-level Owner, can change it, so the README and video say so ([SPONSORS.md](../../SPONSORS.md), section 1, fact 3).
- Claude does the three judgment jobs: matching reports written in other words, writing each note in the reporter's terms, and reading replies like "works, but the export is still wrong". Code checks every fact around them.
- Duo Code Review on the fix MR runs Claude Sonnet 5.5 (since 2026-10-05).
- Optional: a CI eval runs Claude Code headless (`claude -p --json-schema --max-turns --max-budget-usd`, keyless via `CLAUDE_CODE_USE_VERTEX=1`, model `claude-sonnet-5-5`) over 30 labelled demo replies, so a prompt change that misreads replies fails the pipeline ([SPONSORS.md](../../SPONSORS.md), section 5, point 6; quota on a new trial project unverified).

## 9. Autonomy level and prizes

**Supervised:** "you approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way" ([RULES_CHECK.md](../../codex/RULES_CHECK.md)). Per fix a person makes two outcome decisions (who is seated with what words; when everyone gets it); the agent finds, matches, checks, drafts, tells, listens and tallies between them. Not Hands-off on purpose: contacting customers and widening a release stay human. Not Assisted: nobody approves each step.

**Prizes** (one path prize plus one special): target **Path A Best Supervised** ($4,000). The rules' Supervised example ends in "approve the production deployment", so many entries will be release gatekeepers, the most crowded space ([FIELD.md](../../FIELD.md), section 5); here the gate is a person's words. Of 7 known October ideas only one is Path A with a human gate, a simulation with no Duo found (FIELD.md section 6; small sample). **Most Stages Covered** (Path A, $5,000) is a fair second target with nine stages in one story, but "all nine stages" is a crowded pitch (NEXUS and the reference README both claim it), so do not bend the build for it. **Most Creative** needs the event's top Innovation score; the prior art below makes that unlikely. Theme risk: "Hands Off. How far can your agents go without you?" ([IDEATION_BRIEF.md](../IDEATION_BRIEF.md)); our answer, "as far as finding, checking, telling and listening", is a stance some judges will not share.

## 10. Load-bearing risk, fallback, day-one test

**Risk: the reporter round trip through Service Desk, driven from a Duo flow.** An email must become a ticket the flow can read, a public comment posted by the flow's code must reach the inbox, and the reply must come back where the flow can read it. Without it nobody is told or answers, and Front Row is a flag click. The docs help ("By default, Service Desk is active in new projects", [configure](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/project/service_desk/configure.md); an email per public comment), but nothing has run in the hackathon workspace, Service Desk is "Not under active development" and moving into work items ([SPONSORS.md](../../SPONSORS.md), 2.2), and posting with `$GITLAB_TOKEN` from `run_command` is unverified.

**Fallback, in order:** (a) no incoming email: a person files each demo report as a confidential issue and adds the customer with `/add_email` (GA in GitLab 18.10, [quick actions](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/project/quick_actions.md)), keeping outgoing comments and email replies; (b) code cannot post: the final component gets `create_issue_note` with only the approved list as input; (c) no email at all: the person pastes each approved note, and the messaging step becomes Assisted. Flag, consent and listening stay the same. If `HumanInputComponent` does not pause a triggered flow (not yet run end to end, [SPONSORS.md](../../SPONSORS.md) section 6, row 3), each run ends with its proposal and the next mention ("@front-row go") is the approval.

**Day-one test** (40 minutes, Alex at a laptop in the provisioned project; log the result in `docs/STATUS.md`):

1. Send "DEMO: invoice dated tomorrow" from the demo mailbox to the Service Desk address. Pass: a confidential ticket and the thank-you email within 5 minutes.
2. Create flow `fr-probe` (agent with `get_issue`, `list_issue_notes`, `run_command`; a `HumanInputComponent`; a final agent) and a Mention trigger. Pass: AI > Flows and AI > Triggers work with the Developer plus AI role.
3. On a normal issue, comment `@<flow account> probe #<ticket>`. Pass: the agent quotes the confidential ticket and an approval To-Do appears.
4. Approve; the final agent `curl`s a public note "DEMO probe: reply YES" onto the ticket with `Authorization: Bearer $GITLAB_TOKEN`. Pass: it is on the ticket and in the inbox.
5. Reply YES by email and mention the flow again. Pass: the reply appears as an external participant comment and the agent quotes it.

Steps 1, 4 and 5 settle the risk; 2 and 3 settle Duo questions every concept shares, with merging to `main` ([guide](../gitlab_guide_and_reference.md), "Gotchas checklist"). Same sitting, 10 minutes: a user list holding `cust_014` on `probe-flag`, read from Cloud Shell through the Unleash endpoint; pass if `cust_014` is on and `cust_099` off.

## 11. Red team

**Prior art** (search excerpts; the pages are blocked here):

- Fix behind a flag for a few customers first: Optimizely, "test in production to a limited amount of customers" ([blog](https://optimizely.com/insights/blog/feature-flag-bug-fix)); DevCycle, a flag "for the user who reported a bug as well as users who reported similar issues", for debug logging ([blog](https://www.devcycle.com/blog/using-feature-flags-for-effective-debugging)); Flagsmith segments of affected users ([docs](https://docs.flagsmith.com/best-practices/mobile-app-versioning)).
- Telling the reporter: Linear's Intercom and Zendesk integrations reopen the conversation when the linked issue is completed ([Intercom](https://linear.app/integrations/intercom), [Zendesk](https://linear.app/docs/zendesk)).
- Early access for feedback: Google Play ([2016](https://android-developers.googleblog.com/2016/09/the-power-of-early-access.html)); Reflag's "early-access workflow" ([title only](https://reflag.com/betas)).
- Feedback-informed rollout: FeatBit widens while signals stay healthy ([guide](https://www.featbit.co/blogs/feature-flags-for-ai-agents)); PostHog links flags to tickets to roll back ([page](https://gurusup.com/integrations/posthog/feature-flag-support)).
- This event: no reporters-first entry seen; the judges' own reference project already comments "Deployed to production" on the issue ([guide](../gitlab_guide_and_reference.md), "The reference project end to end"), so telling someone is the floor.

Every part exists. Not found anywhere: the join, where reporters are the first ring, code enforces consent, their words can hold the release, and it all runs in the one product holding the tickets, code, flag and release. Novelty is moderate.

**Collisions.** *Proof of Fix* reads production logs after a merge for a promised line and reopens the issue. Front Row reads no logs to prove anything, never opens or closes an issue, and never says a fix works. The honest overlap: "works" is evidence, so the video leads with the seat, peaks on a "still wrong" that holds the release, and never says "verified" or "proof". *"Your bug is fixed" notifiers* (Promise Kept is one; banned in the people lens): our message goes before release, only to people who opted in, offers the fix and a way back, and asks a question that changes the rollout; nothing goes out en masse at release. *Release-note generators:* none; every message goes to one person.

**A skeptical judge:** "LaunchDarkly targeting plus an Intercom macro with an LLM in between, demoed by the builder playing three customers. Three happy replies prove nothing, and a person clicks every flag change, so where is the agent?"

**Answer:** (1) The parts exist, but tickets, flags and releases usually live in different tools owned by different people. In GitLab they are one project, and the agent is the join: it finds the people, including the one nobody linked, while code makes sure only matched, consenting, seated people are told. (2) The replies are not proof and are not used as proof: they are a first ring and a hold signal, and the next step is 50 percent of users, where normal signals take over (Canary Voices, C18, can later count complaints inside that cohort). (3) Demo customers are labelled, but the emails, tickets, flag, app and release are real and live; a judge can sign in as a demo customer and see the fix on or off. (4) A person acts twice per fix by design: emailing customers and widening a release stay human, and everything between is the agent. Also: most fixes are not behind flags (the flow checks and steps aside); "customers as testers" (only opted-in people, for their own problem, with a reviewed fix and a way back); privacy (customer words only in confidential tickets and internal notes, but flow job logs of a public project are probably public, inference, so the demo uses demo customers only and a real team would run it in a private project).

## 12. First build step and size

**Today, without Alex:** write `frontrow/seat.py` and `frontrow/tally.py` with pytest on labelled fixtures (`demo/fixtures/tickets_DEMO.json`: four reports, one never linked, one without consent; `demo/customers_DEMO.csv`), then the app's flag reader for GitLab's documented strategy shapes (`userWithId`, `gradualRolloutUserId`, user lists) against a fake Unleash payload, then draft `flows/front-row-seat.yml` and `flows/front-row-listen.yml` with a CI check against GitLab's flow schema. No account needed.

| Component | Rough lines | Days |
|---|---|---|
| Ledgerly app (FastAPI): demo sign-in, invoice view and export with the bug in two code paths, flag reader, `/healthz`, `/front-row/check` | 450 | 1.5 |
| Code layer: `seat`, `is_live`, `guard`, `check`, `send`, `tally` | 400 | 1.5 |
| Two flows, prompts, skill file, `agent-config.yml` | 300 | 2 (live debugging) |
| CI: tests, scans, schema check, deploy include, release job | 120 | 0.5 |
| Tests and labelled fixtures | 500 | in the above |
| Demo data, mailbox, rehearsal, video script | 150 | 1 |

About 1,900 lines and 6.5 build days for Claude Code and Codex. Alex: about 3 hours before Oct 23 (day-one test, two flows and triggers, the flag, the mailbox), best in one laptop session this week, plus filming.

## 13. Verdict

**Not top three on score; keep it as the first alternate.** Suggested total 76.7, up from 75.0:

- Stages 5.7 to 7.0 (+1.3): the loop touches all nine, seven with real work.
- Feasibility 6 to 6.5 (+1.0, double weight): Service Desk is active by default and Developers can manage flags and user lists, which removes two of the engineer's Maintainer worries; the flow-to-inbox path is untested.
- Human 8.3 to 8.7 (+0.4): the "still wrong" hold is a second, stronger beat.
- Novelty 5.7 to 5.0 (-0.7): fix-first flags and close-the-loop tools are commercial practice.
- Innovation 7.3 to 6.8 (-0.3 through the criteria mean, triple weight), same reason.

That puts it level with Writeback (77.0) and below Forget Me (80.0). The judges split: GitLab's ranked it second, Google's seventh, Anthropic's left it out and called it a framing trap. **Promote it** if Night Orders' night start or No Mouse's sandbox browser fails its day-one test, since every Front Row start is an ordinary human action and its load-bearing risk has a cheap, honest fallback. If Alex wants one of the three to be the "user who feels heard" story he asked for ([IDEATION_BRIEF.md](../IDEATION_BRIEF.md)), this is the only top-five candidate that is, and it should replace Forget Me, not either of the top two.
