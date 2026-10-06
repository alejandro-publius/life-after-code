# Life After Code: updates, discussions, gallery and participants

Research for Alex Velazquez (solo entrant). Checked on 2026-10-06, between about 00:20 and 00:45 UTC. That is day 2 of the event: GitLab's own source says submissions opened on 2026-10-05 at 10:00 UTC ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)).

## Read this first: the Devpost pages could not be opened

The network egress proxy for this research environment refused every request to the hackathon's Devpost site. None of the four pages in scope (Updates, Discussions, Project gallery, Participants) could be read, and nothing below is copied from them. This file uses two other kinds of source instead:

1. **GitLab's own public sources on gitlab.com, which were reachable (primary sources):** the October 2026 participant group, the onboarding issue that each approved participant gets, the source code of GitLab's "Showcase Track guide" page (the live page at contributors.gitlab.com is blocked, but its text is public in the repository), and GitLab's reference project for this hackathon.
2. **Search-engine summaries of the blocked Devpost pages.** These are marked (unverified) because I could not compare them with the live page. The same Devpost address also hosted the June 2026 edition (see the next section), so some search results may describe the older event.

Blocked addresses (each tried once per tool listed; not retried, as the proxy instructions require):

| URL | Tool | Error |
|---|---|---|
| https://gitlab-transcend.devpost.com/ | curl | Proxy answered 403 to CONNECT ("policy denial"), curl exit 56 |
| https://gitlab-transcend.devpost.com/updates | WebFetch and curl | WebFetch: `EGRESS_BLOCKED`, "Access to gitlab-transcend.devpost.com is blocked by the network egress proxy." curl: 403 to CONNECT |
| https://gitlab-transcend.devpost.com/forum_topics | curl | 403 to CONNECT |
| https://gitlab-transcend.devpost.com/project-gallery | curl | 403 to CONNECT |
| https://gitlab-transcend.devpost.com/participants | curl | 403 to CONNECT |
| https://devpost.com/hackathons?search=gitlab%20transcend | WebFetch | `EGRESS_BLOCKED` (devpost.com) |
| https://contributors.gitlab.com/transcend-hackathon | WebFetch | `EGRESS_BLOCKED` |
| https://discord.gg/gitlab | WebFetch | `EGRESS_BLOCKED` |
| https://discord.com/api/v10/invites/gitlab?with_counts=true | curl | 403 to CONNECT |
| https://forum.gitlab.com/t/the-transcend-hackathon-starts-now/134144 | WebFetch | `EGRESS_BLOCKED` |
| https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/ | WebFetch | `EGRESS_BLOCKED` |
| https://go.gitlab.com/pLDY3G | WebFetch | `EGRESS_BLOCKED` |
| https://www.youtube.com/watch?v=lw98rbIUdz0 | WebFetch | `EGRESS_BLOCKED`, so no title, length or transcript |
| https://x.com/devpost/status/2104984062469308626 | WebFetch | `EGRESS_BLOCKED` |

How to fill the gap: open the four Devpost pages in a normal browser while logged in. Devpost also emails each update to registered participants, so if Alex has registered, his inbox should hold the full text of every update.

## Which hackathon this is (two editions share one address)

- GitLab's participant group [gitlab-ai-hackathon/transcend-october-2026](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) (created 2026-09-17) has this description: "GitLab Transcend III hackathon (October 2026) - showcase track. One subgroup per participant is provisioned under here by contributors.gitlab.com." Search results give the Devpost home page title as "Life After Code: The path to production at the speed of imagination - Devpost" ([Devpost](https://gitlab-transcend.devpost.com/), title from search results).
- The June 2026 edition, "GitLab Transcend Hackathon: Intelligent orchestration, now with context." (built on GitLab Orbit), used the same Devpost address. In June, GitLab's change [contributors-gitlab-com!2293](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2293) pointed "Official Rules" to https://gitlab-transcend.devpost.com/rules, and search engines still show the June title for that /rules address. Any search result about this subdomain may therefore describe the June event. The June dates (June 10 to 24), GitLab Orbit and the "two tracks" do not apply to this edition.
- **Disagreement:** one search-engine summary called the June event "Transcend III". GitLab's group description, the primary source, says Transcend III is the October 2026 event. The primary source wins.
- **A different event:** GitLab's "October 2026 Community Hackathon" runs from 2026-10-06 to 2026-10-12, with a merge date of 2026-11-12 ([team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296)). It rewards merged contributions to GitLab itself. GitLab's guide puts it this way: "If you want to contribute to GitLab and earn swag credits, go to the Community Hackathon. If you want to showcase what comes after code and compete for cash prizes, go to the Transcend Hackathon." ([AboutSection.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/AboutSection.md))

## Updates

**Devpost updates read: 0.** The updates page was blocked. No individual update URL (`gitlab-transcend.devpost.com/updates/...`) turned up in search results, and no search snippet quoted the text of an update.

Official announcements found on other channels:

| Date | Channel and title | Text | Link | Status |
|---|---|---|---|---|
| Before 2026-10-06 (exact date unknown) | Devpost's account on X | "GitLab Transcend Hackathon is back! This time it's about everything that happens after the commit to your agents: review, security, testing, deployment, monitoring. Full reveal (paths, prizes, judges) drops Oct 6th, live from the Transcend Bangalore keynote (eyes emoji) Register today: https:/..." (the search result cuts it off there) | [x.com/devpost/status/2104984062469308626](https://x.com/devpost/status/2104984062469308626) | (unverified): text from the search-result title, because x.com is blocked |
| Before 2026-10-06 (exact date unknown) | GitLab's account on X | "Your coding agents just got faster. Did your reviews, security, and release cycles keep up? Join GitLab Transcend on October 6 for live demos on scaling agentic AI across the full software lifecycle, from commit to production." | [x.com/gitlab/status/2098488335140372729](https://x.com/gitlab/status/2098488335140372729) | (unverified): text from the search-result title, because x.com is blocked |
| 2026-10-06 | Keynote video, "GitLab Transcend - October 6, 2026" | Not read. The Devpost post says the full reveal comes in the Bangalore keynote. | [YouTube](https://www.youtube.com/watch?v=lw98rbIUdz0) | (unverified): title from search results. YouTube is blocked, and no transcript was reachable. |
| 2026-10-09, 10am ET (14:00 UTC, 7:00 am in Berkeley) | Build Session listed on the Devpost page | "Build Session with Missy Davies and Dennis Meister": a "live walkthrough of GitLab Duo Agent Platform automating what happens after the code is written." | [Devpost](https://gitlab-transcend.devpost.com/) | (unverified): search-engine summary of the Devpost page, so the wording may be paraphrased |
| 2026-10-02 | GitLab onboarding issue "Welcome to the Transcend Hackathon", posted in each approved participant's project | Full text below | [work item #1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) | Verified (primary). This copy is in a GitLab staff member's test workspace. Every approved participant gets the same text in their own project. |

Full text of the onboarding issue, word for word except two changes: the em dash is replaced with " - ", and emoji are written as words in brackets ([source](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1), created 2026-10-02 by the provisioning bot):

> **Welcome to the Transcend Hackathon (party emoji)**
>
> Hey @missy-davies - you're in! (party emoji)
>
> Your [workspace](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/8659557) and project are set up and ready to go.
>
> ### Get started
>
> 1. Read the [Showcase Track guide](https://contributors.gitlab.com/transcend-hackathon).
> 2. Join the [GitLab Community Discord](https://discord.gg/gitlab) and say hi in `#transcend-hackathon`.
>
> ### Optional: observability
>
> Your workspace can have its own observability stack. In [your group](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/8659557), go to **Observe → Observability configuration → Enable Observability**. It is not required to submit or to win.
>
> ### Need help?
>
> - @-mention `gitlab-org/developer-relations/contributor-success` in any issue or MR and we jump in.
> - Ask in `#transcend-hackathon` on [Discord](https://discord.gg/gitlab).
> - Join the office hours for live troubleshooting + brainstorming.
>
> Good luck, and have fun building! (rocket emoji)

## Discussions

**Discussion topics read: 0.** The forum_topics page was blocked. Searches for `gitlab-transcend.devpost.com/forum_topics` found no topic from this edition, only GitLab forum posts about the June edition. I could not record any question, or any answer from organisers, GitLab staff or Devpost staff.

**Official answers to likely questions (from GitLab sources, not from the Devpost discussions).** All of these come from GitLab, the organiser. The guide texts are in GitLab's contributor platform repository and were added in [merge request !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747) by Dennis Meister (GitLab), merged on 2026-10-02.

| Likely question | Official text, word for word | Source |
|---|---|---|
| Which document is binding? | "Amounts, judging criteria, and eligibility are set by the [official rules](https://gitlab-transcend.devpost.com/rules), which are the binding source." | [ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md) |
| Do I need to register in two places? | "**Required to be eligible for cash prizes:** you must both register for the hackathon and submit your work on [Devpost](https://gitlab-transcend.devpost.com/)." Also: "Select **Get started** on the Transcend Hackathon card above and submit your Devpost username. Approvals start on October 5th when the hackathon opens." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |
| What do I get after approval? | "Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |
| Is a video required? | "**Required:** Film an explanatory video of your project." and "Submit your project on [Devpost](https://gitlab-transcend.devpost.com/) by October 27th, including both your repository and your video." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |
| Must I deploy on Google Cloud? | "Projects deployed on Google Cloud score higher on technological implementation." From GitLab's reference project: "Deployment to Google Cloud is optional for the hackathon. Swap the `deploy-*` jobs for your own target if you prefer." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [hello-world-showcase README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) |
| Is observability required? | "It is entirely optional and is not required to submit or to win." | [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) |
| What if my registration is rejected? | "Your registration was not approved. Please contact us via the contributors-gitlab-com issue tracker or find us on our Discord." | [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue) |
| What is the scope? | "Build agentic workflows on GitLab that automate any part of the software development lifecycle after the code is written, from review and testing through to deployment, monitoring, and incident response." | [TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue) |

## Project gallery

**Projects read: 0.** The gallery page was blocked, so I do not know whether any project is visible yet. Submissions opened on 2026-10-05 at 10:00 UTC ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)). Because the June edition used the same address, any gallery entries found later through search may be June projects (unverified).

Related things visible on gitlab.com (none of these are gallery entries):

| Item | Link | One-line summary |
|---|---|---|
| October participant group | [transcend-october-2026](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) | At 2026-10-06 00:41 UTC (checked twice, first at about 00:30), the API listed 3 public workspaces, all for GitLab team members' accounts (two for Lee Tickett, one for Missy Davies). No entrant workspace was public yet. GitLab says approvals and provisioning "start on October 5, when submissions open" ([ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue)). |
| GitLab's reference project, "Hello World Showcase - reference only" | [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) | Its README says "(warning emoji) This is a reference project, not a starter template." and "Built for the Transcend III Hackathon". It is a small Flask task API whose "hands-off loop" works like this: an issue is assigned to the Duo Developer flow, which opens an MR; Duo Code Review gates auto-merge; then the pipeline runs tests, SAST, dependency, secret and container scans, deploys to staging, smoke-tests, promotes to production (Google Cloud Run in this reference setup), cuts a release, and posts the live URL back on the issue. "Nothing in steps 2 to 4 requires a human." It contains `.gitlab/duo/agent-config.yml`, `.gitlab/duo/mr-review-instructions.yaml` and `AGENTS.md`. |

## Participants

| Item | Value | Source and status |
|---|---|---|
| Participant count | **621** | (unverified): search-engine summaries of the [Devpost home page](https://gitlab-transcend.devpost.com/) report "$45,000 in cash" and "621 participants". The crawl date is unknown, and some summaries still show the pre-launch text, so the live number is likely higher now. |
| Skills and interests | Not available | The participants page was blocked. |
| Public entrant workspaces on gitlab.com | 0 entrant workspaces (3 staff workspaces) | [GitLab API, subgroups of the group](https://gitlab.com/api/v4/groups/142538134/subgroups), checked 2026-10-06 00:41 UTC |

Field size in earlier GitLab hackathons, for context only. Both figures are (unverified): they come from search-engine summaries of GitLab blog posts that were blocked here.

- June 2026 Transcend (GitLab Orbit) edition: "1,576 registered developers" and "265 eligible Showcase Track projects" ([GitLab blog](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/)).
- GitLab AI Hackathon (February 9 to March 25, 2026): "nearly 7,000 developers" and "600+" agents and flows ([GitLab blog](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/)).

## Ideas mentioned by entrants

**Devpost team-formation posts read: 0** (blocked). Search did turn up public notes from people planning entries, all on GitHub rather than Devpost:

| Idea | What it does, word for word from the source | Link | Date |
|---|---|---|---|
| Proof of Fix | "an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears." | [JannetEkka/DSProjects#18](https://github.com/JannetEkka/DSProjects/issues/18) | Opened 2026-10-05 |
| NEXUS DevSecOps AI | "A governed 10-agent software lifecycle and SIFT forensic intelligence suite built on the GitLab Duo Agent Platform and Model Context Protocol." A fetch summary adds that the issue claims automation of all nine DevSecOps stages, with three autonomy levels (Assisted, Supervised, Hands-Off), and an MIT license. | [TSAMBALI/Ariadne_Tsambali#218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218) | Opened 2026-10-05 |
| Class DevOps project entered as a bonus | "A tiny Flask REST service taken through a full DevOps lifecycle: CI/CD, configuration management, containers and Kubernetes, and monitoring." Its README adds: "Event: Life After Code, the GitLab Transcend Hackathon on Devpost (deadline Oct 27, 2026)". | [Reeti05Agarwal/DevOps-](https://github.com/Reeti05Agarwal/DevOps-) | Unknown |

## Community channels and office hours

| Channel | What GitLab says | Link | Status |
|---|---|---|---|
| GitLab Community Discord, channel `#transcend-hackathon` | "Join the [GitLab Community Discord](https://discord.gg/gitlab) and say hi in `#transcend-hackathon`." | [discord.gg/gitlab](https://discord.gg/gitlab) | Blocked, not opened |
| Office hours | "Join the office hours for live troubleshooting + brainstorming." The issue gives no time or link. | [onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) | Schedule not found (unverified) |
| Build Session | Oct 9, 10am ET, with Missy Davies and Dennis Meister of GitLab (Dennis Meister wrote GitLab's guide page; their job titles come from search summaries) | [Devpost](https://gitlab-transcend.devpost.com/) | (unverified), from a search summary |
| Help in GitLab issues | "@-mention `gitlab-org/developer-relations/contributor-success` in any issue or MR and we jump in." | [onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) | Verified |
| GitLab forum | No thread for this edition found. The forum is blocked. | [forum.gitlab.com](https://forum.gitlab.com/) | Blocked |
| Slack | No reachable source mentions a Slack workspace for entrants | n/a | n/a |

## Official GitLab guide text (Showcase Track guide)

This is the text of [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) on the main branch (commit fd53410d, 2026-10-02), which feeds https://contributors.gitlab.com/transcend-hackathon. I did not check the live page, because it is blocked. HTML wrapper tags are removed, headings are shown in bold, line breaks inside paragraphs are joined, and passages I left out are marked [...]. All other words are verbatim, and the source contains no em or en dashes.

> **How it works**
>
> - **Registration** opens September 29, 2026 (10:00 UTC).
> - **Submissions** run from October 5 until October 27, 2026 (14:00 UTC).
> - **Judging** runs until November 11, 2026.
> - **Winners** are announced on or around November 16, 2026.
>
> Open to every experience level, from seasoned contributors to complete beginners. Some countries and regions are excluded.
>
> **Get started**
>
> 1. Register for the hackathon on [Devpost](https://gitlab-transcend.devpost.com/).
> 1. Select **Get started** on the Transcend Hackathon card above and submit your Devpost username. Approvals start on October 5th when the hackathon opens.
> 1. Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it.
> 1. Build your project using Duo Agent Platform.
> 1. **Required:** Film an explanatory video of your project.
> 1. Submit your project on [Devpost](https://gitlab-transcend.devpost.com/) by October 27th, including both your repository and your video. See the "What to submit" section on Devpost for full details.
> 1. (Optional) Share your work through a blog post or on social media.
>
> **The challenge**
>
> Please see the official rules on [Devpost](https://gitlab-transcend.devpost.com/rules) for the full description.
>
> **How it is judged**
>
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
>
> **Build your idea**
>
> Add agents and flows through the UI of your provisioned project under **Automate → Agents**, or add skills directly to the repository.
>
> [...] (links to the agents, flows and skills documentation, the Web IDE, and a "Test your agent" section about chatting with the agent in the GitLab Duo sidebar)
>
> **Test your flow:** Your flow gets a user identity, and you choose what starts it with a [trigger](https://docs.gitlab.com/user/duo_agent_platform/triggers/). Flows can run when that user is mentioned in a comment, assigned to an issue or merge request, or added as a reviewer, and on pipeline, merge request, and work item events.
>
> **Test your skill:** [Project-level skills](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/#create-project-level-skills) live in `skills/<skill-name>/SKILL.md` at the project root. The `name` and `description` metadata fields at the top of the file are required. Start a **new** conversation or flow each time you change `SKILL.md` to avoid context confusion.
>
> **Observability:** Monitoring and incident response are part of life after code, so your subgroup can have its own observability instance. In your subgroup, go to **Observe → Observability configuration → Enable Observability**. Provisioning takes up to 10 minutes, and you get your own OpenTelemetry endpoint to send traces, metrics, and logs to. See the [observability documentation](https://docs.gitlab.com/operations/observability/observability/) for what you can do with it.
>
> It is entirely optional and is not required to submit or to win.

Key dates in the same repository ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)): submissions open 2026-10-05 10:00 UTC; submissions close and GitLab-side registration closes 2026-10-27 14:00 UTC; judging 2026-10-28 10:00 UTC to 2026-11-11 17:00 UTC; winners 2026-11-16 14:00 UTC.

## Facts that change how to build or submit

1. **The deadline sources disagree.** GitLab's source says submissions close **2026-10-27 at 14:00 UTC** ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)). Several search-engine summaries of the Devpost page say "October 27th at 1:00 PM UTC" (unverified). GitLab itself calls the Devpost rules "the binding source" ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md)). Plan on the earlier time: 13:00 UTC is 6:00 am PDT in Berkeley on Tuesday, October 27 (US daylight time ends on November 1). Check the time on the Devpost page.
2. **Register in two places:** on Devpost (needed for cash prizes) and on GitLab's contributor platform with your Devpost username (needed to get the provisioned subgroup and project, where you have the Developer role) ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)).
3. **Judging has a gate.** A pass or fail check comes first ("fit the theme and genuinely use GitLab AI features"). Projects that pass are scored on five equal criteria: technological implementation, design, potential impact, innovation and presentation. "Design" rewards "a complete, coherent workflow rather than a proof of concept", and "Presentation" rewards a video that shows the automation "running end to end" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)).
4. **Google Cloud deployment is optional but scores higher** on technological implementation ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase)). A search summary of the Devpost page says Google Cloud deployment makes a project "eligible for up to 0.2 bonus points" (unverified).
5. **Paths (unverified, from search summaries of the Devpost page).** "Path A: Start Fresh" means building a new project on GitLab: the app, the CI/CD pipeline and the automation, all new work. "Path B: Bring Your Own" means taking "an existing MIT-licensed open-source project (yours or a fork)", importing it to GitLab and building the automation around it. The Path B requirements reported are: a public GitLab project with an MIT License file visible in the About section; an explanation of what was added during the Submission Period, where "the agentic automation and the deployment must be new work, done on or after October 5th"; and a deployed project URL that stays live until winners are announced on or around November 16 ([Devpost](https://gitlab-transcend.devpost.com/)).
6. **Prizes and judges (unverified, from search summaries).** The summaries report "$45,000 in cash", a "Most Creative (either Path)" prize of $4,000, and prize categories for covering the most DevSecOps stages. The judges reported are Missy Davies, Mattias Michaux, Dennis Meister and Lee Tickett (GitLab) and Rajesh Agadi (Google), with an Anthropic judge not named. These names may come from the June page, which used the same address ([Devpost](https://gitlab-transcend.devpost.com/)). Devpost's own post said "paths, prizes, judges" would be revealed on Oct 6 ([x.com](https://x.com/devpost/status/2104984062469308626), unverified).
