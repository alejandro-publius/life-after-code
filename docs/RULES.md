# Life After Code: rules, requirements and prizes

GitLab Transcend Hackathon on Devpost, October 2026. Main page: [gitlab-transcend.devpost.com](https://gitlab-transcend.devpost.com/).
Compiled on 2026-10-06 (about 00:45 UTC) for Alex Velazquez (solo entrant, UC Berkeley CS).

> **Read this first.** Every Devpost page (`gitlab-transcend.devpost.com/*` and `devpost.com`) is blocked by this environment's network policy (the proxy answered `403` to CONNECT, and WebFetch returned `EGRESS_BLOCKED`). I could not open the Devpost site directly. All Devpost text below comes from the web search tool's excerpts of those pages, so its exact wording is **not confirmed**. GitLab's own copy of the hackathon guide (the source code of `contributors.gitlab.com/transcend-hackathon`, stored publicly on gitlab.com) was read directly and is quoted exactly. Before building too far, open the Devpost pages in a normal browser and check every item tagged **[S]** or **[J]**.

| Tag | Meaning |
|---|---|
| **[D]** | Read directly from the primary source file. Quoted word for word. |
| **[S]** | Text returned by the web search tool for the named Devpost page. Devpost was blocked, so the wording may differ from the live page (unverified wording). |
| **[J]** | From the **June 2026** edition of the Official Rules (the earlier "GitLab Orbit" Transcend hackathon, which used the same URL). The search index still holds that version of [/rules](https://gitlab-transcend.devpost.com/rules). Shown only as the likely template. Not confirmed for Life After Code (unverified). |

## What this means for us

1. **Sign up in two places today.** Join on [Devpost](https://gitlab-transcend.devpost.com/) (required for cash prizes), then register the Devpost username at `contributors.gitlab.com/transcend-hackathon` to get a GitLab workspace (public subgroup and project, Developer role) for building with Duo Agent Platform. Approval is manual, about 24 hours ([Devpost resources](https://gitlab-transcend.devpost.com/resources) [S]; [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). At 00:43 UTC on Oct 6 only 3 workspaces existed in the [October group](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026), all for GitLab staff accounts [D], so approvals had not visibly started.
2. **Deadline.** Devpost says "October 27th at 1:00 PM UTC" ([Devpost home](https://gitlab-transcend.devpost.com/) [S]), which is 6:00 AM Pacific on Tuesday Oct 27. GitLab's guide says 14:00 UTC ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Use the earlier time. Our own target: submitted by Monday Oct 26, 9:00 PM Pacific.
3. **Path A fits us.** A new project built from scratch after Oct 5, deployment optional. Path B needs an existing MIT-licensed project and requires deployment. Pick one path per project ([Devpost home](https://gitlab-transcend.devpost.com/) [S]).
4. **Prize map ($45,000, 9 categories).** Per path: Assisted $4,000, Supervised $4,000, Hands-off $5,000. Across paths: Most Stages Covered ($5,000, one winner per path), Most Creative ($4,000), Most Environmentally Impactful ($5,000, opt-in, needs SCI numbers) ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). A Path A hands-off build that covers many lifecycle stages lines up with three of these. No reachable source says whether one project can win more than one prize (unverified).
5. **Duo Agent Platform is mandatory.** "Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients" ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). A pass/fail check removes entries that do not "genuinely use GitLab AI features" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Using Claude Code or other tools to write the code is not addressed in anything I could read (unverified).
6. **Scoring.** Five equally weighted criteria: technological implementation, design, potential impact, innovation, presentation ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Deploying on Google Cloud adds up to 0.2 once after scoring (maximum final score 5.2), if the deployment code is in the public GitLab repo and the live link is public ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). Cloud Run deploy from GitLab CI is worth doing.
7. **Submission package.** Public GitLab project with an MIT License visible in the About section, a text description, visible CI/CD pipeline history, and a demo video under 3 minutes on YouTube (public, automation shown running, no third-party trademarks or copyrighted music) ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). The video is scored on its own ("Presentation").
8. **The judges' baseline for "hands-off".** GitLab's reference project [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase), built by listed judge Missy Davies, already runs: issue, Duo Developer flow, MR, Duo Code Review, auto-merge, security scans, Cloud Run staging, smoke test, production, release, summary on the issue [D]. Its README claims all nine lifecycle stages, but its monitoring is a post-deploy smoke test [D]. Matching it is the floor, not a differentiator. Real production monitoring and incident response (GitLab offers an optional per-workspace OpenTelemetry endpoint [D]) is a clear way to go further.
9. **Eligibility.** Age of majority in your country, US residents are fine; excluded places are listed in section 4 ([Devpost home](https://gitlab-transcend.devpost.com/) [S]). The June rules also barred judges, their employers and promotion entities [J]. If Alex has any current job or internship at GitLab, Google or Anthropic, check the live rules first.
10. **The Life After Code Official Rules text was not readable from here.** The indexed `/rules` page is still the June edition. Open [/rules](https://gitlab-transcend.devpost.com/rules) in a browser and re-check the open questions in section 16.

## Key dates

| Event | Stated time | Pacific time | Source |
|---|---|---|---|
| GitLab workspace registration opens | "September 29, 2026 (10:00 UTC)" | Sep 29, 3:00 AM PDT | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Submissions open | October 5, 2026; code value `2026-10-05T10:00:00Z` | Oct 5, 3:00 AM PDT | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D]; [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Paths, prizes and judges revealed | "Oct 6th, live from the Transcend Bangalore keynote" | Oct 6 | Devpost post title as shown in search results: [x.com/devpost](https://x.com/devpost/status/2104984062469308626) [S] (x.com blocked) |
| GitLab hackathon page start | "Join us from October 6, 2026"; code value `2026-10-06T10:00:00Z` | Oct 6, 3:00 AM PDT | [TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Build Session (Missy Davies, Dennis Meister) | "Oct 9, 10am ET" | Oct 9, 7:00 AM PDT | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| **Submission deadline (Devpost)** | "October 27th at 1:00 PM UTC" | **Oct 27, 6:00 AM PDT** | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Submission deadline (GitLab guide) | "October 27, 2026 (14:00 UTC)" | Oct 27, 7:00 AM PDT | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| GitLab workspace registration closes | code value `2026-10-27T14:00:00Z` | Oct 27, 7:00 AM PDT | [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Judging | "Judging runs until November 11, 2026."; code values `2026-10-28T10:00:00Z` to `2026-11-11T17:00:00Z` | ends Nov 11, 9:00 AM PST | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) [D] |
| Winners announced | "on or around November 16, 2026"; code value `2026-11-16T14:00:00Z` | Nov 16, 6:00 AM PST | same [D] |

US daylight saving time ends on Nov 1, 2026, so October times are PDT (UTC-7) and November times are PST (UTC-8). The Devpost Official Rules dates for this edition were not readable; the search tool only returned June 2026 dates for `/rules` [J].

Note: GitLab's registration card says to submit "before October 27, 2026" ([TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue) [D]), while its guide says "by October 27th" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D]). Another reason to finish on Oct 26.

## 1. The challenge

Devpost page title: "Life After Code: The path to production at the speed of imagination" ([Devpost home](https://gitlab-transcend.devpost.com/), title shown in search results [S]).

From the Devpost home page [S], as returned by search:

> "Code generation is solved. What happens next is the challenge."

> "Build agents and flows that take over the rest of the DevSecOps lifecycle: code review, security scanning, testing, compliance, deployment, monitoring, and more."

> "You pick how much control you hand over. Then you show us how far your automation goes."

> "The heart of the challenge is building automation that reaches across GitLab's DevSecOps lifecycle, not just one corner of it." Stages listed: "plan · create · verify · package · secure · release · configure · monitor · govern"

Other facts from the same page [S]: online and public event; "$45,000 in cash"; judges "from GitLab, Google, and Anthropic"; 621 participants at the time the search engine indexed it; theme tags DevOps, Machine Learning/AI, Productivity; registration is free and you may enter alone or as a team; sponsors listed as GitLab, Google Cloud and Anthropic. Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S].

GitLab's own description, word for word [D] ([TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue)):

> "Build agentic workflows on GitLab that automate any part of the software development lifecycle after the code is written, from review and testing through to deployment, monitoring, and incident response."

> "You must also register on Devpost to be eligible for cash prizes, and submit your final project there before October 27, 2026."

Do not confuse this with GitLab's separate **Community Hackathon** (swag credits, merge requests to GitLab, Oct 6 to 12, merge deadline Nov 12). GitLab's text [D]: "If you want to contribute to GitLab and earn swag credits, go to the Community Hackathon. If you want to showcase what comes after code and compete for cash prizes, go to the Transcend Hackathon." ([AboutSection.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/AboutSection.md); dates from [team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296) [D]).

## 2. The paths (word for word as far as search allowed)

Source for this whole section: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The page tells entrants to "Read the two Paths below and pick yours" [S]. Each quote below is assembled from several search excerpts that agreed with each other; the words match those excerpts, but sentence breaks on the live page may differ.

### Path A: Start Fresh [S]

> "Build a new AI-powered project on GitLab that shows agentic automation of the post-code lifecycle. You create the app, the CI/CD pipeline, and the automation from scratch. Your project must be new work, created for the hackathon. Deployment is optional, but deploying on Google Cloud makes you eligible for up to 0.2 bonus points."

### Path B: Bring Your Own [S]

> "Take an existing MIT-licensed open-source project. It can be yours or a fork. Import it to GitLab, build AI-powered post-code automation around it, and deploy it. The automation and deployment must be new work, done on or after October 5th."

Path B entrants must also explain "what you added or changed during the Submission Period" [S].

No other paths were found. Whether Path B deployment must be on Google Cloud is not stated in any excerpt (unverified).

## 3. Levels of autonomy (each is its own prize, per path)

Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S].

| Level | Definition [S] | Example given [S] |
|---|---|---|
| **Assisted** | "You approve every step. Your agents and flows propose actions and wait for your go-ahead before they proceed. You stay in the loop at every stage." | "An agent reviews your MR and flags a security vulnerability. It suggests a fix and waits for you to approve before committing. Then it runs the pipeline and waits for you to approve the deployment." |
| **Supervised** | "You approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way. You review the end result, not every individual action." | "You push code. Agents handle code review, fix a failing pipeline, remediate a security finding, and deploy to staging. You get a summary and approve the production deployment." |
| **Hands-off** | "You set the intent and walk away. A full loop from code to production with no human in the middle. You push code or create an issue, and the next time you check in, it's live." | "You create an issue. Agents review it, create 1+ MRs, run security scans, fix what they find, merge when everything passes, deploy to staging, validate, promote to production, and post a summary on the original issue. You touched nothing." |

## 4. Eligibility

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

## 5. What to submit

### Devpost "What to Submit" list [S]

Source for every row: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. The order and exact words are reconstructed from several search excerpts.

| # | Item | Text as returned by search [S] |
|---|---|---|
| 1 | The project | "Your project, built with the required technologies" (GitLab Duo Agent Platform features) |
| 2 | Text description | "what your project does, the problem it solves, and how you used GitLab to automate the post-code lifecycle" |
| 3 | Code repository | "A public GitLab Project with all source code, assets, and instructions needed to run the project", with an "MIT License file, visible at the top of the repository page in the About section" |
| 4 | Demo video | "under three minutes", "uploaded to YouTube", "publicly visible", shows "your automation running", must not include "third-party trademarks or copyrighted music" |
| 5 | Pipeline evidence | "visible CI/CD pipeline history showing your automation running" |
| 6 | Path B only | explain "what you added or changed during the Submission Period" |
| 7 | Optional, Google Cloud bonus | "include your Google Cloud deployment code in your public GitLab repository" and "provide a link to your live project on Google Cloud", which "must be public and available to judges" |
| 8 | Optional, environmental prize | opt in on the submission form; explain sustainability practices and quantify the gain with SCI (see section 7) |

### Video, in one place

| Rule | Value | Source |
|---|---|---|
| Required? | Yes. GitLab: "**Required:** Film an explanatory video of your project." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Maximum length | "under three minutes" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Hosting | YouTube, "publicly visible" (whether Vimeo or others are allowed is unverified) | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Content | show "your automation running"; no "third-party trademarks or copyrighted music" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| How it is scored | "Does the video clearly demonstrate the automation running end-to-end? Does it communicate what problem is solved, who it's for, and why it matters? Is the overall presentation easy to follow?" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |

Context only: the rules of GitLab's earlier Devpost hackathon said judges are not required to watch beyond 3 minutes ([gitlab.devpost.com/rules](https://gitlab.devpost.com/rules), search excerpt, different event, unverified for this one).

### GitLab's step list, word for word [D]

Source: [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), section "Get started".

> 1. Register for the hackathon on [Devpost](https://gitlab-transcend.devpost.com/).
> 1. Select **Get started** on the Transcend Hackathon card above and submit your Devpost username. Approvals start on October 5th when the hackathon opens.
> 1. Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it.
> 1. Build your project using Duo Agent Platform.
> 1. **Required:** Film an explanatory video of your project.
> 1. Submit your project on [Devpost](https://gitlab-transcend.devpost.com/) by October 27th, including both your repository and your video. See the "What to submit" section on Devpost for full details.
> 1. (Optional) Share your work through a blog post or on social media.

## 6. Judging: process, stages, criteria, weights

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

Source: [Devpost home](https://gitlab-transcend.devpost.com/) [S].

> "If you deploy on Google Cloud, your project is eligible for up to 0.2 bonus points, which are added once after judges score your project." "The highest possible final score is 5.2."
>
> To qualify: "include your Google Cloud deployment code in your public GitLab repository" and "provide a link to your live project on Google Cloud", which "must be public and available to judges."

A 5.2 maximum implies each criterion is scored on a 1 to 5 scale and averaged (my inference, unverified). GitLab's guide words the same idea differently: "Projects deployed on Google Cloud score higher on technological implementation" [D]. GitLab's guide also says the Devpost Official Rules are "the binding source" ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) [D]).

### Stages and ties in the June edition [J]

> "Stage One will determine via pass/fail whether the ideas meet a baseline level of viability, in that the Project reasonably fits the theme and reasonably uses GitLab Orbit."
>
> "All Submissions that pass Stage One will be evaluated in Stage Two based on the following equally weighted criteria."
>
> Tie-break: the tied Submission with the highest score in the first criterion listed wins; then the next criterion; if still tied on all criteria, "the panel of Judges will vote on the tied Submissions."

Source: [/rules](https://gitlab-transcend.devpost.com/rules) [J]. The October edition evidently swaps "GitLab Orbit" for GitLab AI features and adds a fifth criterion (Presentation); the tie-break order for October is unverified.

## 7. Prizes

Source for every row: [Devpost home](https://gitlab-transcend.devpost.com/) [S]. Total stated: "$45,000 in prizes" [S].

| Prize | Cash (each) | Winners | Total | Description [S] |
|---|---|---|---|---|
| Path A: Start Fresh, Best Assisted Agent | $4,000 | 1 | $4,000 | Best Path A entry at the Assisted level |
| Path A: Start Fresh, Best Supervised Agent | $4,000 | 1 | $4,000 | Best Path A entry at the Supervised level |
| Path A: Start Fresh, Best Hands-off Agent | $5,000 | 1 | $5,000 | Best Path A entry at the Hands-off level |
| Path B: Bring Your Own, Best Assisted Agent | $4,000 | 1 | $4,000 | Best Path B entry at the Assisted level |
| Path B: Bring Your Own, Best Supervised Agent | $4,000 | 1 | $4,000 | Best Path B entry at the Supervised level |
| Path B: Bring Your Own, Best Hands-off Agent | $5,000 | 1 | $5,000 | Best Path B entry at the Hands-off level |
| Most Stages Covered (one from each Path) | $5,000 | 2 | $10,000 | "The Projects from each Path which touch the most post-code DevSecOps lifecycle stages in the most creative way." |
| Most Creative (either Path) | $4,000 | 1 | $4,000 | Description not captured by search (unverified) |
| Most Environmentally Impactful (either Path) | $5,000 | 1 | $5,000 | "(Opt-in) To be considered, opt in on the submission form." Entrants explain "how your project demonstrates exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices," and "quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks." (SCI: Software Carbon Intensity) |
| **Sum** | | **10 winners** | **$45,000** | Matches the stated total, which supports the list being complete. |

The per-level descriptions in the table ("Best Path A entry at the ... level") are my plain summary of the prize names, not quoted text. Whether a single project can win more than one prize, and how a project is assigned to an autonomy level (self-declared or judged), are not in any reachable source (unverified).

## 8. New work and pre-existing work

| Case | Rule | Source |
|---|---|---|
| Path A | "Your project must be new work, created for the hackathon." | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path B | "The automation and deployment must be new work, done on or after October 5th." Also explain "what you added or changed during the Submission Period." The base project must be an existing MIT-licensed open-source project, "yours or a fork". | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition (for comparison) | "Projects may be new or existing and updated during the competition. If the Entrant's Project existed prior to the Hackathon Submission Period, it must have been significantly updated after the start of the Hackathon Submission Period." Entrants using existing content "should explain, to the satisfaction of the Judges, how their Project was significantly updated during the Submission Period." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition, funding | "A Project must not have been developed, or derived from a Project developed, with financial or preferential support from the Sponsor or Administrator", including projects that received funding, were developed under contract, or received a commercial license from them before the end of the Submission Period. | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |

For us: on Path A, keep every commit after Oct 5, 2026 10:00 UTC. The GitLab-provisioned project is created at approval time ([provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D]), which gives a clean, dated history. Disclose any reused open-source libraries in the README.

## 9. GitLab Duo and Duo Agent Platform

| Statement | Source |
|---|---|
| "Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients." | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| The page encourages using agents, flows, triggers, and MCP servers, as many Duo Agent Platform features as you can, to see how much of the lifecycle you can automate (search paraphrase). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Pass/fail gate: "does the project fit the theme and genuinely use GitLab AI features?" | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| "Build your project using Duo Agent Platform." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Rewarded through Technological Implementation: "how thoroughly and skilfully it uses GitLab to automate the post-code lifecycle." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |

GitLab's build notes, word for word [D] (same file, "Build your idea"):

> Add agents and flows through the UI of your provisioned project under **Automate → Agents**, or add skills directly to the repository.

> Your flow gets a user identity, and you choose what starts it with a [trigger](https://docs.gitlab.com/user/duo_agent_platform/triggers/). Flows can run when that user is mentioned in a comment, assigned to an issue or merge request, or added as a reviewer, and on pipeline, merge request, and work item events.

> [Project-level skills](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/#create-project-level-skills) live in `skills/<skill-name>/SKILL.md` at the project root. The `name` and `description` metadata fields at the top of the file are required. Start a **new** conversation or flow each time you change `SKILL.md` to avoid context confusion.

## 10. Licence and repository rules

| Rule | Source |
|---|---|
| "A public GitLab Project with all source code, assets, and instructions needed to run the project" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| An "MIT License file, visible at the top of the repository page in the About section" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path B base project must be "MIT-licensed open-source" | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition: "an MIT License notice file for any original work created by the Entrant, and applicable license notices for any third-party open source components. The primary license should be detectable and visible at the top of the repository page (in the About section)." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| GitLab-provisioned workspaces are created `visibility: 'public'` (group and project) with a README | [provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb) [D] |
| Workspace path pattern: `gitlab-ai-hackathon/transcend-october-2026/<GitLab user id>/showcase` | [transcend_hackathon_registration.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/models/transcend_hackathon_registration.rb) [D] |

Whether the submitted repository must be the provisioned workspace, or may be any public GitLab.com project, is not stated in any reachable source (unverified). Keep the MIT `LICENSE` file at the repository root so GitLab shows it in the About section.

## 11. What can disqualify an entry

| Risk | Source |
|---|---|
| Failing the pass/fail check: not fitting the theme or not genuinely using GitLab AI features | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Not using Duo Agent Platform features | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Not registering and submitting on Devpost (no cash prize eligibility) | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Missing items: public GitLab project, MIT License in About section, video, description | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Video over three minutes, not public, not on YouTube, or with third-party trademarks or copyrighted music | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Path A work that is not new; Path B automation or deployment done before Oct 5 | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| Living in an excluded country or region, or under the age of majority | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |
| June edition: conflict of interest ("The Sponsor may disqualify a Project if awarding a prize to the Project would create a real or apparent conflict of interest.") | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: "Failure to provide correct information on the Required Forms, or other correct information required for the delivery of a Prize, may result in delayed Prize delivery, disqualification of the Entrant, or forfeiture of a Prize." | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: tampering, acting "in violation of these Official Rules or in a manner that is inappropriate, unsportsmanlike, not in the best interests of this Hackathon, or a violation of any applicable law or regulation" | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| June edition: project developed with financial or preferential support from the Sponsor or Administrator | [/rules](https://gitlab-transcend.devpost.com/rules) [J] |
| GitLab can reject a workspace registration ("Your registration was not approved.") | [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue) [D] |

## 12. Judges

Devpost says judges come "from GitLab, Google, and Anthropic" [S]. Names found in search excerpts of the [Devpost home](https://gitlab-transcend.devpost.com/) page [S]:

| Name | Title and company as listed [S] |
|---|---|
| Missy Davies | Fullstack Software Engineer, GitLab |
| Mattias Michaux | Fullstack Engineer, GitLab |
| Dennis Meister | Full Stack Engineer, GitLab |
| Lee Tickett | Principal Fullstack Engineer, GitLab |
| Rajesh Agadi | Principal Architect, Google |
| Anthropic judge(s) | Not named in any source I could reach (unverified). |

Devpost announced that judges would be revealed on Oct 6 at the Transcend Bangalore keynote ([x.com/devpost](https://x.com/devpost/status/2104984062469308626), post text shown in search results [S]), so the live list may be longer than this one. At least two of the GitLab judges built this hackathon's own tooling: Dennis Meister wrote the October workspace code ([MR !2746](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2746), [MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747) [D]), and Missy Davies built the [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) reference project (commit history [D]).

## 13. Resources and access

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
| Reference project | "⚠️ This is a reference project, not a starter template." MIT licensed. Flask task API; hands-off loop from issue to Cloud Run production; "Deployment to Google Cloud is optional for the hackathon." | [hello-world-showcase README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md) [D] |
| GitLab's resource links | [Devpost](https://gitlab-transcend.devpost.com/), [Official rules](https://gitlab-transcend.devpost.com/rules), [GitLab Duo Agent Platform documentation](https://docs.gitlab.com/user/duo_agent_platform/), [Prompt library](https://about.gitlab.com/gitlab-duo/prompt-library/), [DevSecOps lifecycle stages](https://about.gitlab.com/stages-devops-lifecycle/), [GitLab Discord](https://discord.gg/gitlab) (all blocked from here except the list itself) | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) [D] |
| Google Cloud credits | No hackathon credit offer found in any reachable source (unverified). One search summary mentioned a Google Cloud partner credit request form but gave no link or amount. | search only |
| Anthropic resources | Anthropic is listed as a sponsor and judge source; no Anthropic resource page for this hackathon was found (unverified). | [Devpost home](https://gitlab-transcend.devpost.com/) [S] |

GitLab's onboarding issue, word for word [D] (template [description.md.erb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb); live example: [staff test workspace issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase/-/work_items/1)). The one em dash in the original is replaced with " - ", and the template variables (user name, workspace link) are shown as plain text:

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

Practical lesson from GitLab's review of the June edition ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245) [D]): "New GitLab accounts cannot run CI without a credit card on file"; "Custom flows require a group namespace, not personal"; "Em dashes in flow YAML get silently corrupted in the editor"; in June there was "still no "merge request opened" trigger" (check today's trigger list). Using the provisioned group workspace avoids the namespace problem.

## 14. Official Rules: what was and was not readable

- The Life After Code Official Rules at [gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules) could not be opened (proxy 403). The search index for that URL still returns the June 2026 edition, titled "GitLab Transcend Hackathon: Intelligent orchestration, now with context." [J]. Its content is about GitLab Orbit, a "Contribute Track" and a "Showcase Track", and June dates, so it is not this event's rules.
- June edition facts that may carry over (unverified for October) [J]: Sponsor and Administrator "GitLab Inc. 268 Bush Street #350, San Francisco, CA 94104-3503"; entry by "registering for the Hackathon on the Hackathon Website by clicking the "Join Hackathon" button"; June dates were "June 10, 2026 (10:00 am Eastern Time)" to "June 24, 2026 (2:00 pm Eastern Time)", judging "June 25, 2026 (10:00 am Eastern Time) - July 8, 2026 (5:00 pm Eastern Time)".
- GitLab's guide names the Devpost Official Rules as binding: "Amounts, judging criteria, and eligibility are set by the [official rules](https://gitlab-transcend.devpost.com/rules), which are the binding source." ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) [D])

## 15. What we were told, checked against sources

| Claim we were given | Finding | Source |
|---|---|---|
| Submission period Oct 5 to Oct 27, 2026 | Confirmed. Time: "October 27th at 1:00 PM UTC" on Devpost [S] versus "October 27, 2026 (14:00 UTC)" in GitLab's guide [D]. One hour apart; use 13:00 UTC. | [Devpost home](https://gitlab-transcend.devpost.com/), [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |
| $45,000 in prizes | Confirmed [S]; the nine listed prizes add up to exactly $45,000. | [Devpost home](https://gitlab-transcend.devpost.com/) |
| Judges from GitLab, Google and Anthropic | Devpost says so [S]. Named so far: four from GitLab, one from Google. No Anthropic judge is named in any reachable source (unverified). | [Devpost home](https://gitlab-transcend.devpost.com/) |
| Path A: start fresh, new AI-powered project on GitLab showing agentic automation of the post-code lifecycle | Confirmed [S]. Also: built from scratch, must be new work, deployment optional. There is also a Path B (bring your own MIT project, deployment required). | [Devpost home](https://gitlab-transcend.devpost.com/) |
| Prizes for every level of autonomy | Confirmed, and per path: six autonomy prizes (Assisted $4,000, Supervised $4,000, Hands-off $5,000, for each of Path A and Path B) [S]. | [Devpost home](https://gitlab-transcend.devpost.com/) |
| Prizes for the most post-code stages in the most creative way | Confirmed as "Most Stages Covered (one from each Path)", $5,000, 2 winners [S]. Not mentioned to us: "Most Creative (either Path)" $4,000 and "Most Environmentally Impactful (either Path)" $5,000 (opt-in). | [Devpost home](https://gitlab-transcend.devpost.com/) |
| Optional Google Cloud deployment adds up to 0.2 bonus once after judging; needs deploy code in the public GitLab repo and a link to the live project on Google Cloud | Confirmed [S], plus: the live link must be "public and available to judges"; maximum final score 5.2. GitLab's guide describes it as scoring "higher on technological implementation" [D]. Optional only on Path A; Path B must deploy (where, unverified). | [Devpost home](https://gitlab-transcend.devpost.com/), [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |

## 16. Open questions to check in a browser

1. Exact deadline wording and time zone in the Life After Code Official Rules (13:00 or 14:00 UTC).
2. Can one project win more than one prize (for example Hands-off plus Most Stages Covered)?
3. How is the autonomy level chosen: declared on the submission form, or decided by judges?
4. Video hosting: YouTube only, or also Vimeo and others? Any rule about judges stopping at 3 minutes?
5. Names of the Anthropic judges, and whether the judge list changed after the Oct 6 keynote.
6. Must the repository be the GitLab-provisioned workspace, or any public GitLab.com project?
7. Does Path B deployment have to be on Google Cloud?
8. Any rule on AI coding assistants, team size, or entering more than one project.
9. Office hours dates (Discord `#transcend-hackathon`).
10. Whether Google Cloud credits are offered, and how to request them.
11. Intellectual property, licence grant and publicity clauses in the October Official Rules.

## Sources that were blocked

| URL | Error |
|---|---|
| https://gitlab-transcend.devpost.com/ (and `/rules`, `/resources`, `/details/dates`, `/updates`, `/discussions`, `/project-gallery`) | Proxy `403` on CONNECT; WebFetch `EGRESS_BLOCKED` |
| https://devpost.com/ | Proxy `403` on CONNECT |
| https://contributors.gitlab.com/transcend-hackathon | curl could not connect through the proxy (no HTTP status, same pattern as the 403 policy denials); I read the page's source on gitlab.com instead |
| https://about.gitlab.com/ (blog, events, prompt library, stages page) | WebFetch `EGRESS_BLOCKED`; proxy `403` on CONNECT |
| https://docs.gitlab.com/ | Proxy `403` on CONNECT |
| https://forum.gitlab.com/ | curl could not connect through the proxy (no HTTP status) |
| https://discord.gg/gitlab and https://discord.com/ | curl could not connect; proxy `403` on CONNECT for discord.com |
| https://x.com/devpost/status/2104984062469308626 | Proxy `403` on CONNECT |
| https://www.youtube.com/ (Transcend Oct 6 keynote video `lw98rbIUdz0`) | curl could not connect through the proxy (no HTTP status); no transcript reachable |
| https://docs.cloud.google.com/free/docs/free-cloud-features | Proxy `403` on CONNECT |
| GitHub search API and github.com/search | "This GitHub API path is not available: sessions are bound to their configured repositories"; web search `403` |
| https://gitlab.com/api/v4/projects/55044057 (about.gitlab.com source repository) | `403 Forbidden` |
| Merge request comment threads on gitlab.com | `401 Unauthorized` without login |

I did not use web archives or reader proxies to get around the Devpost block, because the environment's policy says not to route around a denied host.

## Updates

See section below, filled by the discussions pass.

## Discussions

See section below, filled by the discussions pass.
