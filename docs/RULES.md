# Life After Code: rules, requirements and prizes

> **Refreshed 6 Oct 2026, 07:35 to 07:50 UTC.** Primary sources were read again for the rules. Where [the refresh note](research/refresh_2026-10-06.md#1-official-rules) differs from this file, the refresh note controls.

GitLab Transcend Hackathon on Devpost, October 2026. Main page: [gitlab-transcend.devpost.com](https://gitlab-transcend.devpost.com/).
Compiled on 2026-10-06 (about 00:45 UTC) for Alex Velazquez (solo entrant, UC Berkeley CS). Checked again and extended in a second pass between about 01:00 and 01:30 UTC the same day.

> **Read this first.**
>
> - Update, later on Oct 6: the official October pages were read directly by Codex and are quoted in [docs/codex/RULES_CHECK.md](codex/RULES_CHECK.md). See "Confirmed from the official pages" below. The notes in this box describe the first two passes.
> - Every Devpost page (`gitlab-transcend.devpost.com/*` and `devpost.com`) is blocked by this environment's network policy (the proxy answered `403` to CONNECT, and WebFetch returned `EGRESS_BLOCKED`). All Devpost text below comes from the web search tool's excerpts of those pages, so its exact wording is **not confirmed**.
> - GitLab's own copy of the hackathon guide (the source code of `contributors.gitlab.com/transcend-hackathon`, public on gitlab.com) was read directly on both passes and is quoted exactly. Nothing in it changed between the passes; the latest change, on Oct 5, renamed one link in the onboarding issue template (see Updates).
> - **The "full reveal" had not happened yet when this was checked.** Devpost said paths, prizes and judges would be revealed "live from the Transcend Bangalore keynote" on Oct 6 [S]. The Bangalore keynotes run 6:45 PM to 9:30 PM IST, which is 13:15 to 16:00 UTC, or 6:15 AM to 9:00 AM Pacific on Oct 6 [S]. Search excerpts show the Devpost page already listing paths, prizes and judges, but the keynote may add or change details (for example, name the Anthropic judges).
> - The shared web search budget ran out near the end of the second pass, so a few exact-phrase checks were not run (listed under Sources that were blocked).
> - Before building too far, open the Devpost pages in a normal browser and check every item tagged **[S]** or **[J]**.

| Tag | Meaning |
|---|---|
| **[D]** | Read directly from the primary source file (on gitlab.com). Quoted word for word. |
| **[S]** | Search excerpt, unverified wording: text the web search tool returned for the named page, which could not be opened from here (usually Devpost). The live wording may differ. |
| **[J]** | From the **June 2026** edition of the Official Rules (the earlier "GitLab Orbit" Transcend hackathon, which used the same URL), as returned by search. The search index still holds that version of [/rules](https://gitlab-transcend.devpost.com/rules). Shown only as the likely template. Not confirmed for Life After Code (unverified). |

## Confirmed from the official pages (Oct 6, 2026)

Later on Oct 6, Codex (working from a different network) read the October Official Rules, home, resources, dates and updates pages directly, and saved the exact text in [docs/codex/RULES_CHECK.md](codex/RULES_CHECK.md) with content hashes in [docs/codex/source-status.json](codex/source-status.json). That file is now the primary record for Devpost wording. Where it differs from the [S] and [J] text further down, it wins. The points that change or settle things:

| Topic | Official wording (quoted in RULES_CHECK.md) | Effect on this file |
|---|---|---|
| Deadline | "Submission Period: October 5, 2026 (10:00 am UTC) - October 27, 2026 (1:00 pm UTC)" | Confirms 13:00 UTC. GitLab's 14:00 UTC is wrong for Devpost. |
| Judging | "Judging Period: October 28, 2026 (10:00 am UTC) - November 14, 2026 (5:00 pm UTC)" | GitLab's guide says Nov 11; the rules say Nov 14. Rules win. |
| Duo | "build a project using GitLab Duo Agent Platform that fits within one of three levels of autonomy"; Stage One checks that it "reasonably uses GitLab Duo Agent Platform" | Duo Agent Platform use is a pass/fail gate. |
| Path A | "The focus is on how many post-code steps your agents handle in the DevSecOps lifecycle including but not limited to: code review, security scanning, testing, compliance, deployment, monitoring, etc." | Breadth of post-code steps is the stated focus of Path A. |
| Criteria | Five "equally-weighted" criteria: Technological Implementation, Design, Potential Impact, Innovation/Idea, Presentation | 20% each. Tie-breaks go criterion by criterion in that order. |
| Google Cloud | "A maximum of 0.2 points will be added." Final score 1 to 5.2. The deployment code must be in the public repo and the live project public | Confirms the bonus. |
| Video | "should be less than three (3) minutes. Judges are not required to watch beyond three minutes"; "made publicly visible on YouTube" | Aim for about 2:40, set to Public. |
| Repo | Public GitLab repo, MIT licence file visible in About; "The project's CI/CD pipeline history must be visible and show the automation running." | Confirms. |
| Judging without testing | "Judges are not required to test the Project and may choose to judge based solely on the text description, images, and video" | The video and write-up carry the score. |
| Prize limit | "Each Project can win one (1) Prize from either Path A or Path B and one (1) Special Prize." | Answers the open question: at most one autonomy prize plus one special prize. |
| Most Creative | "The Project from either Path which scores highest in the Innovation/Idea judging criteria" | Most Creative is simply the top Innovation score. |
| Most Stages Covered | "The Projects from each Path which touch the most DevSecOps lifecycle steps ... in the most creative way." | One per path. |
| After the deadline | FAQ: "leave everything alone until winners are announced. That includes your submission form, your code repository, your video" | Freeze the repo from Oct 27 to about Nov 16; keep building only in a fork. |
| Staying live | FAQ: if the project goes down "you are not disqualified. But you may score lower" | Keep Cloud Run up until Nov 16. |

## What this means for us

1. **Sign up in two places today.** Join on [Devpost](https://gitlab-transcend.devpost.com/) (required for cash prizes), then register the Devpost username at `contributors.gitlab.com/transcend-hackathon` to get a GitLab workspace (public subgroup and project, Developer role) for building with Duo Agent Platform. Approval is manual, about 24 hours ([Devpost resources](https://gitlab-transcend.devpost.com/resources) [S]; [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). At 01:10 UTC on Oct 6 the [October group](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) still held only 3 workspaces, all for GitLab staff accounts [D], so approvals had not visibly started.
2. **Deadline: Tuesday Oct 27, 13:00 UTC (6:00 AM Pacific).** Devpost says "October 27th at 1:00 PM UTC", and search metadata for the page gives 9:00 AM EDT, the same moment ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). GitLab's guide and code say 14:00 UTC ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D]). Use the earlier time. Our own target: submitted by Monday Oct 26, 9:00 PM Pacific.
3. **Re-check everything after the keynote.** The reveal is at the Bangalore keynote, 6:15 AM to 9:00 AM Pacific on Oct 6 ([x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S]; [Transcend India page](https://about.gitlab.com/events/transcend/india/) [S]). After that, re-open Devpost's home, rules and updates pages and compare them with this file.
4. **Path A fits us.** A new project built from scratch after Oct 5, deployment optional. Path B needs an existing MIT-licensed project and a deployed URL that stays live until about Nov 16. Pick one path per project ([Devpost home](https://gitlab-transcend.devpost.com/) [S]).
5. **Prize map ($45,000, 9 categories, 10 winners).** Per path: Assisted $4,000, Supervised $4,000, Hands-off $5,000. Across paths: Most Stages Covered ($5,000, one winner per path; "touching the stage counts"), Most Creative ($4,000), Most Environmentally Impactful ($5,000, opt-in, needs SCI numbers) ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). A Path A hands-off build that covers many stages lines up with three of these. No reachable source says whether one project can win more than one prize (unverified).
6. **Choose the autonomy level on purpose.** Entrants "pick one Path and then build a project that fits one of three levels of autonomy" ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). Hands-off means "no human in the middle" from issue or push to production [S]. How a project's level is recorded (a form field or the judges' call) is unverified; see How autonomy levels are defined.
7. **Duo Agent Platform is mandatory.** "Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients" ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). A pass/fail check removes entries that do not "genuinely use GitLab AI features" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Using Claude Code or other tools to write the code is not addressed in anything reachable (unverified).
8. **Scoring.** Five equally weighted criteria: technological implementation, design, potential impact, innovation, presentation ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Deploying on Google Cloud adds up to 0.2 once after scoring (maximum final score 5.2), if the deployment code is in the public GitLab repo and the live link is public ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). A Cloud Run deploy from GitLab CI is worth doing.
9. **Submission package.** Public GitLab project with an MIT License visible in the About section, a text description, visible CI/CD pipeline history, and a demo video under 3 minutes on YouTube (public, automation shown running, no third-party trademarks or copyrighted music) ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). The video is scored on its own ("Presentation"), and the June rules let judges stop watching at 3 minutes [J].
10. **The judges' baseline for "hands-off".** GitLab's reference project [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase), built by listed judge Missy Davies, already runs: issue, Duo Developer flow, MR, Duo Code Review, auto-merge, security scans, Cloud Run staging, smoke test, production, release, summary on the issue [D]. Its README claims all nine lifecycle stages, but its monitoring is a post-deploy smoke test [D]. Matching it is the floor, not a differentiator. Real production monitoring and incident response (GitLab offers an optional per-workspace OpenTelemetry endpoint [D]) is a clear way to go further.
11. **Eligibility.** Age of majority in your country; US residents are fine; excluded places are listed under Eligibility below ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). The June rules also barred judges, their employers and promotion entities [J]. If Alex has any current job or internship at GitLab, Google or Anthropic, check the live rules first.
12. **The Life After Code Official Rules text was not readable from here.** The indexed `/rules` page is still the June edition. Open [/rules](https://gitlab-transcend.devpost.com/rules) in a browser and work through the Open questions section below.

## Key dates

| Event | Stated time | Pacific time | Source |
|---|---|---|---|
| GitLab posts about the Oct 6 Transcend event on X | post created 2026-09-11, 19:06 UTC (decoded from the post ID) | Sep 11, 12:06 PM PDT | [x.com/gitlab](https://x.com/gitlab/status/2098488335140372729) [S] (x.com blocked; the time is computed from the ID in the URL) |
| Devpost announces the hackathon on X | post created 2026-09-29, 17:18 UTC (decoded from the post ID) | Sep 29, 10:18 AM PDT | [x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S] (same method) |
| GitLab workspace registration opens | "September 29, 2026 (10:00 UTC)" | Sep 29, 3:00 AM PDT | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Submissions open | October 5, 2026; code value `2026-10-05T10:00:00Z` | Mon Oct 5, 3:00 AM PDT | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D]; [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| GitLab hackathon page start | "Join us from October 6, 2026"; code value `2026-10-06T10:00:00Z` | Oct 6, 3:00 AM PDT | [TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Full reveal of paths, prizes and judges | "Oct 6th, live from the Transcend Bangalore keynote" | Oct 6 | [x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S] |
| Transcend Bangalore (JW Marriott, doors open 5:30 PM IST) | "Keynote: Open" 6:45 PM to 7:45 PM IST; "Keynote: Innovations" 7:45 PM to 8:00 PM IST; "Keynote: Close" 8:00 PM to 9:30 PM IST | Tue Oct 6, 6:15 AM to 9:00 AM PDT | [about.gitlab.com/events/transcend/india](https://about.gitlab.com/events/transcend/india/) [S] (blocked) |
| Build Session (Missy Davies, Dennis Meister) | "Oct 9, 10am ET" | Fri Oct 9, 7:00 AM PDT | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| **Submission deadline (Devpost)** | "October 27th at 1:00 PM UTC"; page metadata via search: Oct 27, 2026, 9:00 AM EDT (same moment) | **Tue Oct 27, 6:00 AM PDT** | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Submission deadline (GitLab guide) | "October 27, 2026 (14:00 UTC)" | Tue Oct 27, 7:00 AM PDT | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| GitLab workspace registration closes | code value `2026-10-27T14:00:00Z` | Oct 27, 7:00 AM PDT | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Judging | "Judging runs until November 11, 2026."; code values `2026-10-28T10:00:00Z` to `2026-11-11T17:00:00Z` | ends Wed Nov 11, 9:00 AM PST | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Path B deployments must stay live until | "winners are announced on or around November 16th" | | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Winners announced | "on or around November 16, 2026"; code value `2026-11-16T14:00:00Z` | Mon Nov 16, 6:00 AM PST | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |

Notes:

- US daylight saving time ends on Nov 1, 2026, so October times are PDT (UTC-7) and November times are PST (UTC-8). The Devpost Official Rules dates for this edition were not readable; search only returned June 2026 dates for `/rules` [J].
- GitLab's registration card says to submit "before October 27, 2026" ([TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue) [D]), while its guide says "by October 27th" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Another reason to finish on Oct 26.
- One search summary gave the start as "October 5 at 1:00pm EDT" (17:00 UTC). No other source supports it, and GitLab's code says 10:00 UTC [D]. It does not affect us.
- The post times above are decoded from X post IDs (an X post ID stores its creation time in milliseconds). The method was checked against a GitLab post from June 9 that said "Happening tomorrow" about the June 10 event.

## The challenge

Devpost page title: "Life After Code: The path to production at the speed of imagination" ([Devpost home](https://gitlab-transcend.devpost.com/), title shown in search results [S]).

From the Devpost home page [S], as returned by search:

> "Code generation is solved. What happens next is the challenge."

> "Build agents and flows that take over the rest of the DevSecOps lifecycle: code review, security scanning, testing, compliance, deployment, monitoring, and more."

> "You pick how much control you hand over. Then you show us how far your automation goes."

> "The heart of the challenge is building automation that reaches across GitLab's DevSecOps lifecycle, not just one corner of it." Stages listed: "plan · create · verify · package · secure · release · configure · monitor · govern"

Pre-launch text from the same page, as summarised by search [S]: "Life After Code is a global hackathon for developers and builders who are ready to hand the rest of the DevSecOps lifecycle to their agents." and "Writing the code is the easy part now. What happens next is the challenge." The page also carries the phrase "Prizes for every level of autonomy" [S].

Other facts from the same page [S]: online and public event; "$45,000 in cash"; judges "from GitLab, Google, and Anthropic"; 621 participants at the time the search engine indexed it; theme tags DevOps, Machine Learning/AI, Productivity; registration is free and you may enter alone or as a team; sponsors listed as GitLab, Google Cloud and Anthropic. Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S].

GitLab's own description, word for word [D] ([TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue)):

> "Build agentic workflows on GitLab that automate any part of the software development lifecycle after the code is written, from review and testing through to deployment, monitoring, and incident response."

> "You must also register on Devpost to be eligible for cash prizes, and submit your final project there before October 27, 2026."

Do not confuse this with GitLab's separate **Community Hackathon** (swag credits, merge requests to GitLab, Oct 6 to 12, merge deadline Nov 12). GitLab's text [D]: "If you want to contribute to GitLab and earn swag credits, go to the Community Hackathon. If you want to showcase what comes after code and compete for cash prizes, go to the Transcend Hackathon." ([AboutSection.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/AboutSection.md); dates from [team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296) [D]).

## The paths (word for word as far as search allowed)

Source for this whole section: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The page tells entrants to "Read the two Paths below and pick yours" [S]. Each quote below is assembled from several search excerpts that agreed with each other; the words match those excerpts, but sentence breaks on the live page may differ.

### Path A: Start Fresh [S]

> "Build a new AI-powered project on GitLab that shows agentic automation of the post-code lifecycle. You create the app, the CI/CD pipeline, and the automation from scratch. Your project must be new work, created for the hackathon. Deployment is optional, but deploying on Google Cloud makes you eligible for up to 0.2 bonus points."

### Path B: Bring Your Own [S]

> "Take an existing MIT-licensed open-source project. It can be yours or a fork. Import it to GitLab, build AI-powered post-code automation around it, and deploy it. The automation and deployment must be new work, done on or after October 5th."

Another excerpt words the last sentence as "The agentic automation and the deployment must be new work, done on or after October 5th." [S]. Path B entrants must also explain "what you added or changed during the Submission Period", "provide a URL to your deployed project", and keep it live: "Your deployed project should stay live until winners are announced on or around November 16th" [S].

No other paths were found. Whether Path B deployment must be on Google Cloud is not stated in any excerpt (unverified).

## How autonomy levels are defined

Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The definitions were returned by search on both passes with the same words, except the last sentence of Supervised, which only the first pass returned. An exact-phrase search for the first Supervised sentence found no page, which shows the search tool may be summarising, so treat the wording as unverified.

> **Assisted:** "You approve every step. Your agents and flows propose actions and wait for your go-ahead before they proceed. You stay in the loop at every stage."
>
> **Supervised:** "You approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way. You review the end result, not every individual action."
>
> **Hands-off:** "You set the intent and walk away. A full loop from code to production with no human in the middle. You push code or create an issue, and the next time you check in, it's live."

| Level | Example given on the page [S] |
|---|---|
| Assisted | "An agent reviews your MR and flags a security vulnerability. It suggests a fix and waits for you to approve before committing. Then it runs the pipeline and waits for you to approve the deployment." |
| Supervised | "You push code. Agents handle code review, fix a failing pipeline, remediate a security finding, and deploy to staging. You get a summary and approve the production deployment." |
| Hands-off | "You create an issue. Agents review it, create 1+ MRs, run security scans, fix what they find, merge when everything passes, deploy to staging, validate, promote to production, and post a summary on the original issue. You touched nothing." (Full sentence from the first pass only; the second pass returned only its start, and the exact-phrase check could not run.) |

**How a project is placed in a level:**

- Entrants "pick one Path and then build a project that fits one of three levels of autonomy" ([Devpost home](https://gitlab-transcend.devpost.com/) [S], search summary wording). So the entrant chooses the target level and builds to it.
- Each level is a separate prize inside each path, named like "Path A: Start Fresh, Best Hands-off Agent" [S].
- No reachable source says how the level is recorded: a field on the submission form, a statement in the description, or the judges' own call (unverified). The submission form does have prize-specific fields: the environmental prize says "opt in on the submission form" [S].
- No source gives a test beyond the definitions and examples. Read literally: Assisted has a human approval at each step (commit, pipeline, deployment); Supervised has one approval of the outcome (the production deployment); Hands-off has none after the issue or push.
- GitLab's reference project names its loop "The hands-off loop" and says "Nothing in steps 2 to 4 requires a human." Step 1 is a person creating an issue and assigning it to the Duo Developer flow ([hello-world-showcase README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md) [D]). That matches the Devpost Hands-off example, so creating the issue does not count as a human "in the middle".

For us: say the level in the first line of the Devpost description and in the video, and show that no human step happens between the issue and production. Ask in the Devpost discussions how the level is chosen.

## Eligibility

From the Devpost home page sidebar [S] ([Devpost home](https://gitlab-transcend.devpost.com/)):

> "Above legal age of majority in country of residence"
>
> "Specific countries/territories excluded": Brazil, China, Crimea, Cuba, Donetsk People's Republic, Iran Islamic Republic of, Korea Democratic People's Republic of, Luhansk People's Republic, Quebec, Russia, Syrian Arab Republic.

From GitLab's guide, word for word [D] ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)):

> "Open to every experience level, from seasoned contributors to complete beginners. Some countries and regions are excluded."
>
> "**Required to be eligible for cash prizes:** you must both register for the hackathon and submit your work on [Devpost](https://gitlab-transcend.devpost.com/). See the full [official rules](https://gitlab-transcend.devpost.com/rules) for details."

From the **June 2026** rules at the same URL [J] ([/rules](https://gitlab-transcend.devpost.com/rules), as returned by search):

> "The Hackathon is open to individuals who are at least the age of majority where they reside as of the time of entry ("Eligible Individuals"), Teams of Eligible Individuals, and Organizations" that exist and were organized or incorporated at the time of entry.

Not eligible under the June rules [J]: residents of the excluded places "and any other country or region where participation is prohibited by law"; organizations involved with the design, production, paid promotion, execution, or distribution of the Hackathon ("Promotion Entities"); "any Judge or company/individual that employs a Judge"; any parent, subsidiary or affiliate of those; and anyone whose participation "would create a real or apparent conflict of interest". The June rules also said "An Eligible Individual may join more than one Team or Organization and may also enter the Hackathon on an individual basis", and a team must appoint one Representative to submit [J].

For us: Alex (US, California) is eligible if 18 or older and not employed by GitLab, Google, Anthropic or Devpost (the judge-employer rule is from the June edition, unverified for this one).

## What to submit

### Devpost "What to Submit" list [S]

Source for every row: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The order and exact words are reconstructed from several search excerpts; the second pass returned the same items.

| # | Item | Text as returned by search [S] |
|---|---|---|
| 1 | The project | "Your project, built with the required technologies" (GitLab Duo Agent Platform features) |
| 2 | Text description | "what your project does, the problem it solves, and how you used GitLab to automate the post-code lifecycle" |
| 3 | Code repository | "A public GitLab Project with all source code, assets, and instructions needed to run the project", with an "MIT License file, visible at the top of the repository page in the About section" |
| 4 | Demo video | "under three minutes", "uploaded to YouTube", "publicly visible", shows "your automation running", must not include "third-party trademarks or copyrighted music" |
| 5 | Pipeline evidence | "visible CI/CD pipeline history showing your automation running" |
| 6 | Path B only | explain "what you added or changed during the Submission Period"; "provide a URL to your deployed project", which "should stay live until winners are announced on or around November 16th" |
| 7 | Optional, Google Cloud bonus | "include your Google Cloud deployment code in your public GitLab repository" and "provide a link to your live project on Google Cloud", which "must be public and available to judges" |
| 8 | Optional, environmental prize | opt in on the submission form; explain sustainability practices and quantify the gain with SCI (see Prizes) |

### Video, in one place

| Rule | Value | Source |
|---|---|---|
| Required? | Yes. GitLab: "**Required:** Film an explanatory video of your project." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Maximum length | "under three minutes" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Hosting | YouTube, "publicly visible". The June rules allowed "YouTube or Vimeo" [J]; whether Vimeo is allowed in October is unverified. | [Devpost home](https://gitlab-transcend.devpost.com/) [S]; [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| Content | show "your automation running"; no "third-party trademarks or copyrighted music" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| What judges watch | June rules: the video "should be less than three (3) minutes", and judges are not required to watch beyond three minutes | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| How it is scored | "Does the video clearly demonstrate the automation running end-to-end? Does it communicate what problem is solved, who it's for, and why it matters? Is the overall presentation easy to follow?" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |

### GitLab's step list, word for word [D]

Source: [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), section "Get started" (unchanged since commit fd53410d of 2026-10-02, checked 01:05 UTC Oct 6).

> 1. Register for the hackathon on [Devpost](https://gitlab-transcend.devpost.com/).
> 1. Select **Get started** on the Transcend Hackathon card above and submit your Devpost username. Approvals start on October 5th when the hackathon opens.
> 1. Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it.
> 1. Build your project using Duo Agent Platform.
> 1. **Required:** Film an explanatory video of your project.
> 1. Submit your project on [Devpost](https://gitlab-transcend.devpost.com/) by October 27th, including both your repository and your video. See the "What to submit" section on Devpost for full details.
> 1. (Optional) Share your work through a blog post or on social media.

## Judging: process, stages, criteria, weights

### GitLab's summary, word for word [D]

Source: [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), section "How it is judged".

> First a pass or fail check: does the project fit the theme and genuinely use GitLab AI features?
>
> Everything that passes is then scored on five equally weighted criteria:
>
> - **Technological implementation** - how thoroughly and skilfully it uses GitLab to automate the post-code lifecycle.
> - **Design** - a complete, coherent workflow rather than a proof of concept.
> - **Potential impact** - a credible, specific case for solving a real problem.
> - **Innovation** - how novel the idea is, and how inventively it applies agentic automation.
> - **Presentation** - how clearly the video demonstrates the automation running end to end.
>
> Projects deployed on Google Cloud score higher on technological implementation. Full details are listed on the [Devpost rules](https://gitlab-transcend.devpost.com/rules) page.

### Devpost criteria text [S]

Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. Weights: equal, so 20% each, per GitLab's "five equally weighted criteria" [D].

| Criterion | Weight | Text as returned by search [S] |
|---|---|---|
| Technological Implementation | 1/5 | "How thoroughly and skillfully does the project use GitLab to automate the post-code DevSecOps lifecycle? Does the code and pipeline config reflect genuine effort and a working, non-trivial implementation?" |
| Design | 1/5 | "Does the project deliver a complete, coherent end-to-end workflow, not just a technical proof of concept?" |
| Potential Impact | 1/5 | "Does the project make a credible, specific case for solving a real problem for a real audience - and does the solution actually address that problem based on what's demonstrated?" |
| Innovation / Idea | 1/5 | "How creative and novel is the concept and how inventively does it apply agentic automation compared to existing concepts?" |
| Presentation | 1/5 | "Does the video clearly demonstrate the automation running end-to-end? Does it communicate what problem is solved, who it's for, and why it matters? Is the overall presentation easy to follow?" |

### Google Cloud bonus [S]

Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The second pass returned the same wording.

> "If you deploy on Google Cloud, your project is eligible for up to 0.2 bonus points, which are added once after judges score your project." "The highest possible final score is 5.2."
>
> To qualify: "include your Google Cloud deployment code in your public GitLab repository" and "provide a link to your live project on Google Cloud", which "must be public and available to judges."

A 5.2 maximum implies each criterion is scored on a 1 to 5 scale and averaged (my inference, unverified). GitLab's guide words the same idea differently: "Projects deployed on Google Cloud score higher on technological implementation" [D]. GitLab's guide also says the Devpost Official Rules are "the binding source" ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) [D]).

### Stages, testing and ties in the June edition [J]

> "Stage One will determine via pass/fail whether the ideas meet a baseline level of viability, in that the Project reasonably fits the theme and reasonably uses GitLab Orbit."
>
> "All Submissions that pass Stage One will be evaluated in Stage Two based on the following equally weighted criteria."
>
> Tie-break: the tied Submission with the highest score in the first criterion listed wins; then the next criterion; if still tied on all criteria, "the panel of Judges will vote on the tied Submissions."
>
> Judges "are not required to test the Project and may choose to judge based solely on the text description, images, and video provided in the Submission" (search summary wording).

Source: [/rules](https://gitlab-transcend.devpost.com/rules) [J]. The October edition evidently swaps "GitLab Orbit" for GitLab AI features and adds a fifth criterion (Presentation); the tie-break order for October is unverified. If the "not required to test" rule carries over, the description and video must prove the automation works on their own.

## Prizes

Source for every row: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. Total stated: "$45,000 in prizes" [S]. The second pass returned the same amounts.

| Prize | Cash (each) | Winners | Total | Description [S] |
|---|---|---|---|---|
| Path A: Start Fresh, Best Assisted Agent | $4,000 | 1 | $4,000 | Best Path A entry at the Assisted level |
| Path A: Start Fresh, Best Supervised Agent | $4,000 | 1 | $4,000 | Best Path A entry at the Supervised level |
| Path A: Start Fresh, Best Hands-off Agent | $5,000 | 1 | $5,000 | Best Path A entry at the Hands-off level |
| Path B: Bring Your Own, Best Assisted Agent | $4,000 | 1 | $4,000 | Best Path B entry at the Assisted level |
| Path B: Bring Your Own, Best Supervised Agent | $4,000 | 1 | $4,000 | Best Path B entry at the Supervised level |
| Path B: Bring Your Own, Best Hands-off Agent | $5,000 | 1 | $5,000 | Best Path B entry at the Hands-off level |
| Most Stages Covered (one from each Path) | $5,000 | 2 | $10,000 | "The Projects from each Path which touch the most post-code DevSecOps lifecycle stages in the most creative way." The page lists nine stages and says you do not have to use every feature inside a stage: "touching the stage counts" (search summary wording). |
| Most Creative (either Path) | $4,000 | 1 | $4,000 | Description not captured by search (unverified) |
| Most Environmentally Impactful (either Path) | $5,000 | 1 | $5,000 | "(Opt-in) To be considered, opt in on the submission form." Entrants explain "how your project demonstrates exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices," and "quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks." (SCI: Software Carbon Intensity) |
| **Sum** | | **10 winners** | **$45,000** | Matches the stated total, which supports the list being complete. |

The per-level descriptions in the table ("Best Path A entry at the ... level") are my plain summary of the prize names, not quoted text. Whether a single project can win more than one prize, and how a project is assigned to an autonomy level (self-declared or judged), are not in any reachable source (unverified).

## New work and pre-existing work

| Case | Rule | Source |
|---|---|---|
| Path A | "Your project must be new work, created for the hackathon." | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path B | "The automation and deployment must be new work, done on or after October 5th." Also explain "what you added or changed during the Submission Period." The base project must be an existing MIT-licensed open-source project, "yours or a fork". | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition (for comparison) | "Projects may be new or existing and updated during the competition. If the Entrant's Project existed prior to the Hackathon Submission Period, it must have been significantly updated after the start of the Hackathon Submission Period." Entrants using existing content "should explain, to the satisfaction of the Judges, how their Project was significantly updated during the Submission Period." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition, funding | "A Project must not have been developed, or derived from a Project developed, with financial or preferential support from the Sponsor or Administrator", including projects that received funding, were developed under contract, or received a commercial license from them before the end of the Submission Period. | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |

For us: on Path A, keep every commit after Oct 5, 2026 10:00 UTC. The GitLab-provisioned project is created at approval time ([provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D]), which gives a clean, dated history. Disclose any reused open-source libraries in the README.

## GitLab Duo and Duo Agent Platform

| Statement | Source |
|---|---|
| "Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients." (returned again on the second pass; an exact-phrase search did not surface the page, so wording unverified) | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| The page encourages using agents, flows, triggers, and MCP servers, as many Duo Agent Platform features as you can, to see how much of the lifecycle you can automate (search paraphrase). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Pass/fail gate: "does the project fit the theme and genuinely use GitLab AI features?" | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| "Build your project using Duo Agent Platform." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Rewarded through Technological Implementation: "how thoroughly and skilfully it uses GitLab to automate the post-code lifecycle." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |

GitLab's build notes, word for word [D] (same file, "Build your idea"):

> Add agents and flows through the UI of your provisioned project under **Automate → Agents**, or add skills directly to the repository.

> Your flow gets a user identity, and you choose what starts it with a [trigger](https://docs.gitlab.com/user/duo_agent_platform/triggers/). Flows can run when that user is mentioned in a comment, assigned to an issue or merge request, or added as a reviewer, and on pipeline, merge request, and work item events.

> [Project-level skills](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/#create-project-level-skills) live in `skills/<skill-name>/SKILL.md` at the project root. The `name` and `description` metadata fields at the top of the file are required. Start a **new** conversation or flow each time you change `SKILL.md` to avoid context confusion.

## Licence and repository rules

| Rule | Source |
|---|---|
| "A public GitLab Project with all source code, assets, and instructions needed to run the project" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| An "MIT License file, visible at the top of the repository page in the About section" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path B base project must be "MIT-licensed open-source" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition: "an MIT License notice file for any original work created by the Entrant, and applicable license notices for any third-party open source components. The primary license should be detectable and visible at the top of the repository page (in the About section)." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| GitLab-provisioned workspaces are created `visibility: 'public'` (group and project) with a README | [provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D] |
| Workspace path pattern: `gitlab-ai-hackathon/transcend-october-2026/<GitLab user id>/showcase` | [transcend_hackathon_registration.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/models/transcend_hackathon_registration.rb) [D] |

Whether the submitted repository must be the provisioned workspace, or may be any public GitLab.com project, is not stated in any reachable source (unverified). Keep the MIT `LICENSE` file at the repository root so GitLab shows it in the About section.

## What can disqualify an entry

| Risk | Source |
|---|---|
| Failing the pass/fail check: not fitting the theme or not genuinely using GitLab AI features | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Not using Duo Agent Platform features | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Not registering and submitting on Devpost (no cash prize eligibility) | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Missing items: public GitLab project, MIT License in About section, video, description | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Video over three minutes, not public, not on YouTube, or with third-party trademarks or copyrighted music | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path A work that is not new; Path B automation or deployment done before Oct 5; a Path B deployment that goes offline before about Nov 16 | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Living in an excluded country or region, or under the age of majority | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition: conflict of interest ("The Sponsor may disqualify a Project if awarding a prize to the Project would create a real or apparent conflict of interest.") | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: "Failure to provide correct information on the Required Forms, or other correct information required for the delivery of a Prize, may result in delayed Prize delivery, disqualification of the Entrant, or forfeiture of a Prize." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: tampering, acting "in violation of these Official Rules or in a manner that is inappropriate, unsportsmanlike, not in the best interests of this Hackathon, or a violation of any applicable law or regulation" | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: project developed with financial or preferential support from the Sponsor or Administrator | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: several entries that are not "unique and substantially different" from each other | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| GitLab can reject a workspace registration ("Your registration was not approved.") | [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue) [D] |

## Judges

Devpost says judges come "from GitLab, Google, and Anthropic" [S]. Names found in search excerpts of the [Devpost home](https://gitlab-transcend.devpost.com/) page [S]:

| Name | Title and company as listed [S] |
|---|---|
| Missy Davies | Fullstack Software Engineer, GitLab |
| Mattias Michaux | Fullstack Engineer, GitLab |
| Dennis Meister | Full Stack Engineer, GitLab |
| Lee Tickett | Principal Fullstack Engineer, GitLab |
| Rajesh Agadi | Principal Architect, Google |
| Anthropic judge(s) | Not named in any source I could reach (unverified). |

Cautions:

- Devpost announced that judges would be revealed on Oct 6 at the Transcend Bangalore keynote ([x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S]), which had not happened when this was checked. The live list may be longer.
- The same Devpost address hosted the June edition, and Rajesh Agadi also judged GitLab's earlier Devpost hackathons: one search summary tied his name to the February to March 2026 GitLab AI Hackathon, while others list him for Life After Code [S]. Part of this list could be carried over from older pages (unverified).
- At least two of the GitLab judges built this hackathon's own tooling: Dennis Meister wrote the October workspace code ([MR !2746](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2746), [MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747) [D]), and Missy Davies built the [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) reference project (commit history [D]).

## Resources and access

| Resource | Details and dates | Source |
|---|---|---|
| GitLab workspace (this is how Duo access is provided) | Register at `contributors.gitlab.com/transcend-hackathon` with your Devpost username; an admin approves; GitLab creates a public subgroup and a project named "Showcase" with the Developer role (custom member role) and an onboarding issue. "Approvals start on October 5th when the hackathon opens." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D] |
| Onboarding time | "Start GitLab Transcend Hackathon contributor onboarding (5 minutes, plus about 24 hours for approval)" | [Devpost resources](https://gitlab-transcend.devpost.com/resources) [S] |
| Quickstart | "Build your first agent with the Duo Agent Platform quickstart (45 minutes)" | [Devpost resources](https://gitlab-transcend.devpost.com/resources) [S] |
| Planning guide | Browse the DevSecOps lifecycle stages and plan agent and flow implementation (30 minutes) | [Devpost resources](https://gitlab-transcend.devpost.com/resources) [S] |
| Build Session | "Attend the Build Session with Missy Davies and Dennis Meister on Oct 9, 10am ET." A live walkthrough of Duo Agent Platform automating what happens after the code is written. (7:00 AM Pacific.) | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Office hours | GitLab: "Join the office hours for live troubleshooting + brainstorming." Devpost: schedules are posted on Discord. No dates found (unverified). | [onboarding template](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb) [D]; [Devpost resources](https://gitlab-transcend.devpost.com/resources) [S] |
| Discord | `#transcend-hackathon` on [discord.gg/gitlab](https://discord.gg/gitlab); the Devpost Participants tab for finding teammates | [onboarding template](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb) [D]; [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Staff help | "@-mention `gitlab-org/developer-relations/contributor-success` in any issue or MR and we jump in." | [onboarding template](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb) [D] |
| Observability (optional) | "In your subgroup, go to **Observe → Observability configuration → Enable Observability**. Provisioning takes up to 10 minutes, and you get your own OpenTelemetry endpoint to send traces, metrics, and logs to." "It is entirely optional and is not required to submit or to win." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Reference project | "⚠️ This is a reference project, not a starter template." (line added 2026-10-05, [commit 9303b3e1](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/9303b3e1)). MIT licensed. Flask task API; hands-off loop from issue to Cloud Run production; "Deployment to Google Cloud is optional for the hackathon." | [hello-world-showcase README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md) [D] |
| GitLab's resource links | [Devpost](https://gitlab-transcend.devpost.com/), [Official rules](https://gitlab-transcend.devpost.com/rules), [GitLab Duo Agent Platform documentation](https://docs.gitlab.com/user/duo_agent_platform/), [Prompt library](https://about.gitlab.com/gitlab-duo/prompt-library/), [DevSecOps lifecycle stages](https://about.gitlab.com/stages-devops-lifecycle/), [GitLab Discord](https://discord.gg/gitlab) (all blocked from here except the list itself) | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Google Cloud credits | No hackathon credit offer found in any reachable source (unverified). One search summary mentioned a Google Cloud partner credit request form but gave no link or amount. | search only |
| Anthropic resources | Anthropic is listed as a sponsor and judge source; no Anthropic resource page for this hackathon was found (unverified). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |

GitLab's onboarding issue, word for word [D] (current template [description.md.erb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb); live examples in staff test workspaces: [1933526](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase/-/work_items/1), [8659557](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1)). The issue title is "Welcome to the Transcend Hackathon 🎉" ([provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D]). The one em dash in the original is replaced with " - ", and the template variables (user name, workspace link) are shown as plain text. The two live examples were created on Oct 2 and still say "Showcase Track guide"; the template was changed to "Transcend Hackathon guide" on Oct 5 ([MR !2836](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2836) [D]).

> Hey @username - you're in! 🎉
>
> Your workspace and project are set up and ready to go.
>
> ### Get started
>
> 1. Read the [Transcend Hackathon guide](https://contributors.gitlab.com/transcend-hackathon).
> 2. Join the [GitLab Community Discord](https://discord.gg/gitlab) and say hi in `#transcend-hackathon`.
>
> ### Optional: observability
>
> Your workspace can have its own observability stack. In your group, go to **Observe → Observability configuration → Enable Observability**. It is not required to submit or to win.
>
> ### Need help?
>
> - @-mention `gitlab-org/developer-relations/contributor-success` in any issue or MR and we jump in.
> - Ask in `#transcend-hackathon` on [Discord](https://discord.gg/gitlab).
> - Join the office hours for live troubleshooting + brainstorming.
>
> Good luck, and have fun building! 🚀

Practical lesson from GitLab's review of the June edition ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D]): "New GitLab accounts cannot run CI without a credit card on file"; "Custom flows require a group namespace, not personal"; "Em dashes in flow YAML get silently corrupted in the editor"; in June there was "still no "merge request opened" trigger". GitLab's October guide now lists "merge request" events among flow triggers [D], so check today's trigger list. Using the provisioned group workspace avoids the namespace problem.

## Official Rules: what was and was not readable

- The Life After Code Official Rules at [gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules) could not be opened (proxy 403). The search index for that URL still returns the June 2026 edition, titled "GitLab Transcend Hackathon: Intelligent orchestration, now with context." [J]. Its content is about GitLab Orbit, a "Contribute Track" and a "Showcase Track", and June dates, so it is not this event's rules. A second-pass excerpt from it still described merge request prizes ("A maximum of five (5) MRs per person are eligible for prizes, awarded to the first forty (40) eligible merged MRs."), which only fits the June Contribute Track [J].
- June edition facts that may carry over (unverified for October) [J]: Sponsor and Administrator "GitLab Inc. 268 Bush Street #350, San Francisco, CA 94104-3503"; entry by "registering for the Hackathon on the Hackathon Website by clicking the "Join Hackathon" button"; "An Entrant may submit more than one Submission, however, each Submission must be unique and substantially different from each of the Entrant's other Submissions, as determined by the Sponsor and Devpost in their sole discretion."; June dates were "June 10, 2026 (10:00 am Eastern Time)" to "June 24, 2026 (2:00 pm Eastern Time)", judging "June 25, 2026 (10:00 am Eastern Time) - July 8, 2026 (5:00 pm Eastern Time)".
- GitLab's guide names the Devpost Official Rules as binding: "Amounts, judging criteria, and eligibility are set by the [official rules](https://gitlab-transcend.devpost.com/rules), which are the binding source." ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) [D])
- GitLab's planning checklist for this hackathon series lists "Rules defined on the site" and "Rules/FAQ page published + linked from every announcement" as tasks, so a rules or FAQ page should exist on Devpost ([team-task#1260](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1260) [D]). No such page for October was found in the GitLab repositories that are public.

## Open questions to check in a browser

1. Exact deadline wording and time zone in the Life After Code Official Rules (13:00 or 14:00 UTC).
2. Anything added or changed at the Bangalore keynote (Oct 6, 13:15 to 16:00 UTC): judges (especially Anthropic), prizes, paths.
3. Can one project win more than one prize (for example Hands-off plus Most Stages Covered)?
4. How is the autonomy level chosen: declared on the submission form, or decided by judges?
5. Video hosting: YouTube only, or also Vimeo? Do judges stop at 3 minutes?
6. The "Most Creative" prize description.
7. Must the repository be the GitLab-provisioned workspace, or any public GitLab.com project?
8. Does Path B deployment have to be on Google Cloud?
9. Any rule on AI coding assistants, team size, or entering more than one project.
10. Office hours dates (Discord `#transcend-hackathon`).
11. Whether Google Cloud credits are offered, and how to request them.
12. Intellectual property, licence grant and publicity clauses in the October Official Rules.

## Sources that were blocked

| URL | Error |
|---|---|
| https://gitlab-transcend.devpost.com/ (and `/rules`, `/resources`, `/details/dates`, `/updates`, `/forum_topics`, `/discussions`, `/project-gallery`, `/participants`) | Proxy `403` on CONNECT; WebFetch `EGRESS_BLOCKED` |
| https://devpost.com/ | Proxy `403` on CONNECT; WebFetch `EGRESS_BLOCKED` |
| https://contributors.gitlab.com/transcend-hackathon | curl could not connect through the proxy (no HTTP status); WebFetch `EGRESS_BLOCKED`. I read the page's source on gitlab.com instead |
| https://about.gitlab.com/ (blog, events including /events/transcend/india/, prompt library, stages page) | WebFetch `EGRESS_BLOCKED`; proxy `403` on CONNECT |
| https://docs.gitlab.com/ | Proxy `403` on CONNECT |
| https://forum.gitlab.com/ | curl could not connect through the proxy (no HTTP status); WebFetch `EGRESS_BLOCKED` |
| https://discord.gg/gitlab and https://discord.com/ | curl could not connect; proxy `403` on CONNECT for discord.com |
| https://x.com/devpost/status/2104984062469308626 and https://x.com/gitlab/status/2098488335140372729 | Proxy `403` on CONNECT; WebFetch `EGRESS_BLOCKED` |
| https://www.youtube.com/watch?v=lw98rbIUdz0 (Transcend Oct 6 keynote video) | curl could not connect; WebFetch `EGRESS_BLOCKED`; no transcript reachable |
| https://www.competehub.dev/en/competitions/devpost30053 (third-party copy of Devpost listings) | WebFetch `EGRESS_BLOCKED` |
| https://www.startupgrantsindia.com/gitlab-transcend-hackathon (third-party listing; search shows it covers the June edition) | WebFetch `EGRESS_BLOCKED` |
| https://docs.cloud.google.com/free/docs/free-cloud-features | Proxy `403` on CONNECT |
| GitHub search API and github.com/search | "This GitHub API path is not available: sessions are bound to their configured repositories"; web search `403` |
| https://gitlab.com/api/v4/projects/55044057 (about.gitlab.com source repository) | Project metadata readable (`200`), but `/merge_requests` and `/repository/tree` return `403 Forbidden` |
| Merge request and issue comment threads on gitlab.com (for example the notes of MR !2747 and team-task#1260) | `401 Unauthorized` without login |
| WebSearch | The shared budget of 200 searches ran out during the second pass, so exact-phrase checks of the Hands-off and Supervised examples were not run |

I did not use web archives or reader proxies to get around the Devpost block, because the environment's policy says not to route around a denied host. The GitHub issues and repositories that mention this hackathon (for example [JannetEkka/DSProjects#18](https://github.com/JannetEkka/DSProjects/issues/18), [TSAMBALI/Ariadne_Tsambali#218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218), [Cubiczan/aftermerge](https://github.com/Cubiczan/aftermerge)) were read and contain no copied rules text.

## Updates

**Devpost updates read: 0.** The Updates tab ([gitlab-transcend.devpost.com/updates](https://gitlab-transcend.devpost.com/updates)) is blocked from here (proxy `403`, WebFetch `EGRESS_BLOCKED`). Search found no individual update URL for this subdomain, and no search excerpt quotes the text of an update. Devpost also emails each update to registered participants, so Alex's inbox is the easiest place to read them once he has joined.

Official announcements and changes found on other channels, oldest first:

| When (UTC) | Channel | What it says or changes | Source and status |
|---|---|---|---|
| 2026-09-11 19:06 (decoded from post ID) | GitLab on X | "Your coding agents just got faster. Did your reviews, security, and release cycles keep up? Join GitLab Transcend on October 6 for live demos on scaling agentic AI across the full software lifecycle, from commit to production." | [x.com/gitlab](https://x.com/gitlab/status/2098488335140372729) [S] (post text from the search result title; x.com blocked) |
| 2026-09-29 10:00 | GitLab contributor platform | Workspace registration opens; "Approvals and provisioning start on October 5, when submissions open." | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts), [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue) [D] |
| 2026-09-29 17:18 (decoded from post ID) | Devpost on X | "GitLab Transcend Hackathon is back! This time it's about everything that happens after the commit to your agents: review, security, testing, deployment, monitoring. Full reveal (paths, prizes, judges) drops Oct 6th, live from the Transcend Bangalore keynote 👀 Register today: https:/..." (cut off in the search result) | [x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S] |
| Before Oct 5 (date unknown) | Devpost home page, pre-launch text | When "submissions open on October 5th", the full challenge details, "including paths, prizes, judges, and resources", will be shared (search summary wording) | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| 2026-10-02 21:26 and 22:58 | GitLab onboarding issue "Welcome to the Transcend Hackathon 🎉" | First issues created in staff test workspaces. Full current text under Resources and access. | [1933526](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase/-/work_items/1), [8659557](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) [D] |
| 2026-10-05 10:00 | GitLab contributor platform | Submissions open; GitLab's page switches to the submissions phase | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| 2026-10-05 (exact time unknown) | Devpost home page | Search excerpts show paths, prizes, autonomy levels, criteria and judges on the page | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| 2026-10-05 17:49 | GitLab MR !2836 "Change "showcase" to "transcend" in naming" (Missy Davies) | The onboarding issue now links "Transcend Hackathon guide" instead of "Showcase Track guide". No rule change. | [MR !2836](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2836) [D] |
| 2026-10-05 21:22 | GitLab reference project README (Missy Davies) | Added the first line "⚠️ This is a reference project, not a starter template." | [commit 9303b3e1](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/9303b3e1) [D] |
| 2026-10-06 13:15 to 16:00 (6:45 PM to 9:30 PM IST) | Transcend Bangalore keynotes ("Keynote: Open", "Keynote: Innovations", "Keynote: Close") | The promised full reveal. Not yet happened at the time of this check. | [about.gitlab.com/events/transcend/india](https://about.gitlab.com/events/transcend/india/) [S] |
| 2026-10-06 | YouTube, "GitLab Transcend - October 6, 2026" | Keynote video; not read | [YouTube](https://www.youtube.com/watch?v=lw98rbIUdz0) [S] (title from search results) |
| 2026-10-09 14:00 (10am ET) | Devpost home page | "Build Session with Missy Davies and Dennis Meister": a "live walkthrough of GitLab Duo Agent Platform automating what happens after the code is written." | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |

No other changes to GitLab's hackathon files were found: the folder `transcend-hackathon-page` has had no commit since fd53410d on 2026-10-02, checked through the public API at 01:05 UTC on Oct 6 ([commits for that path](https://gitlab.com/api/v4/projects/gitlab-org%2Fdeveloper-relations%2Fcontributor-success%2Fcontributors-gitlab-com/repository/commits?path=contributors/app/javascript/pages/transcend-hackathon-page) [D]). An open draft, [MR !2838](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2838) "Tidy up transcend hackathon", prepares the removal of GitLab's hackathon page after the event; it changes no rules [D].

**Check in a browser:** the Devpost Updates tab and your email for every update posted since Oct 5, especially any posted during or after the Oct 6 keynote; the keynote recording for prize, judge or rule changes.

## Discussions

**Devpost discussion topics read: 0.** The Discussions tab ([gitlab-transcend.devpost.com/forum_topics](https://gitlab-transcend.devpost.com/forum_topics)) is blocked from here (proxy `403` on CONNECT). Searches for this subdomain's forum topics found no topic from this edition, only GitLab forum posts about the June edition and a topic from the earlier GitLab AI Hackathon. No question, and no answer from organisers, GitLab staff or Devpost staff, could be recorded.

**Official answers to likely questions, from GitLab's own pages [D].** These are not from the Devpost discussions. The guide texts were added in [MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747) by Dennis Meister (GitLab), merged on 2026-10-02, and were unchanged at 01:05 UTC on Oct 6.

| Likely question | Official text, word for word | Source |
|---|---|---|
| Which document is binding? | "Amounts, judging criteria, and eligibility are set by the [official rules](https://gitlab-transcend.devpost.com/rules), which are the binding source." | [ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) [D] |
| Do I need to register in two places? | "**Required to be eligible for cash prizes:** you must both register for the hackathon and submit your work on [Devpost](https://gitlab-transcend.devpost.com/)." Also: "Select **Get started** on the Transcend Hackathon card above and submit your Devpost username. Approvals start on October 5th when the hackathon opens." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| What do I get after approval? | "Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Is a video required? | "**Required:** Film an explanatory video of your project." and "Submit your project on [Devpost](https://gitlab-transcend.devpost.com/) by October 27th, including both your repository and your video." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Must I deploy on Google Cloud? | "Projects deployed on Google Cloud score higher on technological implementation." From GitLab's reference project: "Deployment to Google Cloud is optional for the hackathon. Swap the `deploy-*` jobs for your own target if you prefer." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [hello-world-showcase README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md) [D] |
| Is observability required? | "It is entirely optional and is not required to submit or to win." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| What if my registration is rejected? | "Your registration was not approved. Please contact us via the contributors-gitlab-com issue tracker or find us on our Discord." | [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue) [D] |
| What is the scope? | "Build agentic workflows on GitLab that automate any part of the software development lifecycle after the code is written, from review and testing through to deployment, monitoring, and incident response." | [TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue) [D] |

**Other likely questions, answered from search excerpts and the June rules (unverified):**

| Question | Best available answer | Source |
|---|---|---|
| Do I have to use every feature in a stage for it to count? | No: you do not have to use every feature inside a stage; "touching the stage counts" (search summary wording). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Is deployment required? | Path A: "Deployment is optional". Path B: deploy, "provide a URL to your deployed project", keep it live until about Nov 16. | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Can I enter alone? | Yes: you can enter on your own or with a team, and registration is free (search summary wording). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Can I enter more than one project? | June rules: "An Entrant may submit more than one Submission, however, each Submission must be unique and substantially different from each of the Entrant's other Submissions". October rules unread. | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| Which video sites are allowed? | October page: YouTube, "publicly visible". June rules: YouTube or Vimeo. | [Devpost home](https://gitlab-transcend.devpost.com/) [S]; [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| Will judges run my project? | June rules: judges "are not required to test the Project and may choose to judge based solely on the text description, images, and video provided in the Submission". | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |

**Ask or look for in the Devpost Discussions tab (logged in):** how the autonomy level is declared; whether one project can win several prizes; whether Vimeo is allowed; whether the repository must be the provisioned workspace; whether Path B must deploy on Google Cloud; whether Google Cloud credits exist; office hours times.

## Discrepancies with the handoff brief

| Handoff claim | Verdict | Details | Source |
|---|---|---|---|
| Submissions Oct 5 to Oct 27, 2026 | **Matches** | Opens Oct 5, 10:00 UTC (GitLab code). Closes Oct 27 at "1:00 PM UTC" on Devpost, but 14:00 UTC in GitLab's guide and code: one hour apart, so use 13:00 UTC (6:00 AM Pacific). The October Official Rules, which are binding, were not readable. | [Devpost home](https://gitlab-transcend.devpost.com/) [S]; [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts), [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| $45,000 in prizes | **Matches** | "$45,000 in cash"; the nine prize categories add up to exactly $45,000 (10 winners). Not checked against the Official Rules (unverified). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Judges from GitLab, Google and Anthropic | **Matches the Devpost statement; partly unverified** | Devpost says judges come "from GitLab, Google, and Anthropic". Named so far: four from GitLab, one from Google. No Anthropic judge is named in any reachable source, and the full judge reveal was due at the Oct 6 keynote, after this check. | [Devpost home](https://gitlab-transcend.devpost.com/), [x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S] |
| Path A: a new AI project on GitLab that automates the post-code lifecycle with agents | **Matches in meaning; wording differs** | Devpost: "Build a new AI-powered project on GitLab that shows agentic automation of the post-code lifecycle." Conditions the brief leaves out: you create "the app, the CI/CD pipeline, and the automation from scratch"; it "must be new work, created for the hackathon"; deployment is optional. There is also a Path B (bring your own MIT project, deployment required). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Prizes for every level of autonomy | **Matches, with more detail** | The page uses the phrase "Prizes for every level of autonomy". There are six autonomy prizes, one per level per path: Assisted $4,000, Supervised $4,000, Hands-off $5,000, for each of Path A and Path B. | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Prizes for most post-code lifecycle stages in the most creative way | **Matches; differs in detail** | "Most Stages Covered (one from each Path)": "The Projects from each Path which touch the most post-code DevSecOps lifecycle stages in the most creative way." $5,000 each, 2 winners, so a Path A entry competes only with Path A. "Touching the stage counts". The brief does not mention two other prizes: "Most Creative (either Path)" $4,000, and "Most Environmentally Impactful (either Path)" $5,000 (opt-in). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Google Cloud deployment optional; up to 0.2 bonus points, added once after judging; needs deployment code in the public GitLab repository and a link to the live project on Google Cloud | **Matches the Devpost text; differs in GitLab's wording** | Devpost: "eligible for up to 0.2 bonus points, which are added once after judges score your project"; "include your Google Cloud deployment code in your public GitLab repository"; "provide a link to your live project on Google Cloud". Extra conditions: the link "must be public and available to judges"; "The highest possible final score is 5.2." GitLab's guide instead says "Projects deployed on Google Cloud score higher on technological implementation", which reads as part of one criterion rather than a bonus added after scoring. Deployment is optional only on Path A; Path B must deploy (where is unverified). | [Devpost home](https://gitlab-transcend.devpost.com/) [S]; [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
