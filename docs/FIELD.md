# Field: who else is building for Life After Code

Compiled 2026-10-06 at about 01:50 UTC for Alex Velazquez (solo entrant, Path A). This is day 2 of Life After Code, the GitLab Transcend Hackathon on Devpost: submissions opened 2026-10-05 at 10:00 UTC and close on 2026-10-27 ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)). The Bangalore keynote, where Devpost said the "full reveal (paths, prizes, judges)" would happen, had not started yet ([x.com/devpost](https://x.com/devpost/status/2104984062469308626), search-result title, unverified).

This file condenses four research notes from this session, plus one fresh count of the October group:

- [research/field/code_hosts.md](research/field/code_hosts.md): GitLab and GitHub.
- [research/field/social.md](research/field/social.md): social media, web search, the AI Catalog, earlier editions.
- [research/rules_discussions.md](research/rules_discussions.md): Devpost updates, discussions, gallery, participants and ideas entrants posted.
- [research/gitlab_guide_and_reference.md](research/gitlab_guide_and_reference.md), part "Lessons from the June 2026 edition".

"(unverified)" means no primary source confirmed the fact. "(inference)" marks my own conclusion from the evidence next to it.

## Read this first

1. **The visible field is small and early.** 7 agent ideas are known: 4 projects with code, 2 planning issues on GitHub and 1 onboarding request that names an idea. Add 1 class DevOps project (not an agent) and 5 onboarding requests that mention entering but give no idea. GitLab's October group still held only 2 staff projects when I re-counted at 01:48 UTC.
2. **The crowded space right now is the post-merge release gatekeeper:** review, scan, test, deploy, health check, then ship, hold or roll back. 4 of the 7 known ideas do this, and the judges' own reference project runs the same loop.
3. **Crowded ideas won less often in June.** GitLab's own update: "69 built pre-merge impact review, 36 built onboarding aids" and "Five of the eight winners came from those rare tiers." In Feb to Mar, on the same Duo Agent Platform as October, 132 of 506 catalog projects did security review on merge requests.
4. **Excluded for us:** post-merge release gatekeepers, release-notes generators, CI failure fixers, generic incident chatbots, dashboards as the main idea, and anything near Proof of Fix (an agent that checks production after a merge to prove a fix worked).
5. **Open so far (hints from a small sample):** the on-call handoff with a human gate, user feedback after release, feature flags and progressive rollout (the configure stage), database migration safety, package and registry hygiene, compliance evidence for auditors, accessibility after deploy. Also thin: Path A entries with a human gate (1 of 7).
6. **Only 1 of the 4 built entries shows Duo Agent Platform files, and that flow was not registered yet.** The judges' first check is pass or fail on genuine use of GitLab AI features, so several rivals may not pass as they stand (unverified).
7. **Our repo is public** and is the first GitHub result for "Life After Code" ([search](https://github.com/search?q=%22Life+After+Code%22&type=repositories&s=updated&o=desc)), so rivals can read this file. See the Watch list.

## 1. Method

### 1.1 Passes and times

All times are UTC on 2026-10-06.

| Pass | Note | Time | What it covered |
|---|---|---|---|
| Devpost tabs and GitLab's guide | [rules_discussions.md](research/rules_discussions.md) | about 00:20 to 00:45 | Devpost updates, discussions, gallery and participants (all blocked), GitLab's guide page source, the October group, entrant notes found by search |
| GitLab guide and June lessons | [gitlab_guide_and_reference.md](research/gitlab_guide_and_reference.md) | about 00:30 to 01:30 | GitLab's June judging update and review, hackathon group counts |
| Code hosts | [code_hosts.md](research/field/code_hosts.md) | about 01:05 to 01:35 | GitLab API, GitHub pages, 5 web searches |
| Social and web | [social.md](research/field/social.md) | about 01:05 to 01:30 | 18 web searches, social sites (all blocked), GitLab project search, AI Catalog, June and Feb groups |
| Re-count for this file | this file | 01:48:39 to 01:48:40 | One call to the October group projects API |

No new web search was run for this file, because the session's search budget was used up (see 1.10).

### 1.2 The October group (GitLab REST API, no token)

| Query or URL | When | Result |
|---|---|---|
| [group](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026) ([web page](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026)) | code-host pass | Public, created 2026-09-17. Description: "GitLab Transcend III hackathon (October 2026) - showcase track. One subgroup per participant is provisioned under here by contributors.gitlab.com." |
| [subgroups](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/subgroups) ([per_page=100](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/subgroups?per_page=100), [by ID](https://gitlab.com/api/v4/groups/142538134/subgroups)) | about 00:30, 00:41, 01:08, 01:10, 01:17, 01:25 | 3 subgroups, all GitLab staff, all created Oct 2: [1933526 leetickett](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/1933526), [12687636 leetickett-gitlab](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/12687636), [8659557 missy-davies](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/8659557) |
| [projects](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true) | 01:17 | 2 projects (leetickett-gitlab has none visible) |
| [descendant_groups](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/descendant_groups) | code-host pass | 3 |
| [missy-davies/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase) and [leetickett/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase): tree, commits, issues, MRs, pipelines | code-host pass | Each: 1 file (default README), 1 commit, 1 onboarding issue, 0 MRs, 0 pipelines. No flow or agent files. |
| [Onboarding issue #1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1) | rules pass | Template welcome text. Mentions optional per-workspace observability and Discord `#transcend-hackathon`. The notes API needs a token (401). |
| **Re-count for this file:** [projects, include_subgroups, per_page=100](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true&per_page=100) | **01:48:40** (the response's HTTP Date header) | `x-total: 2`, 1 page. Still only the two staff showcases: project 87183213 (missy-davies, last activity 2026-10-05 21:24 UTC) and project 87181550 (leetickett, last activity 2026-10-02 21:26 UTC). No entrant workspace yet. Subgroups were not re-counted (one call allowed). |

### 1.3 Earlier hackathon groups on GitLab (counts)

| Group | Projects | Note |
|---|---|---|
| [gitlab-ai-hackathon](https://gitlab.com/gitlab-ai-hackathon) (root) | 345 in all, 7 direct subgroups, 10 descendant groups | [projects API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon/projects?include_subgroups=true&per_page=1) |
| [transcend](https://gitlab.com/groups/gitlab-ai-hackathon/transcend) (June 2026, Orbit edition) | 312 | One project per entrant. Every README downloaded: 308 READMEs, 159 still the blank template, 149 describe a project. |
| [gitlab-devsecops-flow-hackathon](https://gitlab.com/groups/gitlab-ai-hackathon/gitlab-devsecops-flow-hackathon) (created 2026-03-16) | 0 | Empty or private |
| participants-test-lee / participants-test-mattias / project-templates / test | 2 / 24 / 1 / 1 | Staff test groups |
| [gitlab-community/community-projects/2026-02-ai-hackathon](https://gitlab.com/groups/gitlab-community/community-projects/2026-02-ai-hackathon) (Feb to Mar 2026 AI Hackathon) | 1,788 | Moved out of `gitlab-ai-hackathon/participants`; found through the redirect of [participants/621485](https://gitlab.com/api/v4/projects/gitlab-ai-hackathon%2Fparticipants%2F621485). 506 of these projects published 1,807 AI Catalog items. READMEs not downloaded. |

### 1.4 GitLab public project search (API equivalent of Explore)

All through `https://gitlab.com/api/v4/projects?search=<term>`. Totals are the API's `x-total`.

| Search | Total | Relevant hits |
|---|---|---|
| [transcend](https://gitlab.com/api/v4/projects?search=transcend&order_by=created_at&sort=desc) | 438 | receipted-pipeline, receipted-pipeline-demo, the 2 staff showcases |
| [life after code](https://gitlab.com/api/v4/projects?search=life%20after%20code&order_by=created_at&sort=desc) | 15 | sam1054/aftermerge, babydov-release-sentinel |
| [life-after-code](https://gitlab.com/api/v4/projects?search=life-after-code) | 0 | none |
| [transcend hackathon](https://gitlab.com/api/v4/projects?search=transcend%20hackathon&order_by=created_at&sort=desc) | 342 | same as "transcend" |
| [gitlab-transcend](https://gitlab.com/api/v4/projects?search=gitlab-transcend) | 3 | none (all June 2026) |
| Topic [gitlab-transcend](https://gitlab.com/api/v4/projects?topic=gitlab-transcend) | 1 | receipted-pipeline |
| Topics transcend / transcend-hackathon / duo-agent-platform / GitLab-Duo-Agent-Platform / GitLab AI Hackathon / lifecycle | 2 / 4 / 8 / 3 / 1 / 16 | none from October |
| 31 keywords on projects created since about Sep 27 (`id_after=86950000`): hackathon 26, devsecops 68, post-code 1, post-merge 1, "post code" 8, "duo agent" 2, duo 15, agentic 21, lifecycle 46, hands-off 3, autonomous 18, self-healing 2, sentinel 3, incident 19, on-call 6, rollback 16, canary 6, release 180, triage 21, compliance 14, SBOM 1, changelog 11, postmortem 1, runbook 8, SRE 16, pipeline 221, deploy 204, "cloud run" 8, mcp 87, flow 165, agent 281 | see left | Only the 3 GitLab entries plus the receipted demo |
| 19 more keywords since about Sep 28 (`id_after=86990000`): "path a" 92, "path b" 92, devpost 2, showcase 17, post-deploy 0, "after merge" 1, "after code" 3, "duo flow" 1, "custom flow" 2, ambient 1, orbit 9, "release notes" 1, flaky 1, vulnerability 5, remediation 4, observability 18, postmortem 0, "change risk" 2, "blast radius" 3 | see left | No new entries |
| Name checks since about Sep 25: nexus 13, "proof of fix" 0, proof-of-fix 0, a2a 5, aftermerge 1, receipted 2, "release sentinel" 1, hvfr 0, omega 1 | see left | No GitLab copy of NEXUS, Proof of Fix or A2A Omega |
| [explore/projects?search=transcend](https://gitlab.com/explore/projects?search=transcend), [explore/projects?search=life+after+code](https://gitlab.com/explore/projects?search=life+after+code) | HTTP 200, 0 visible | The list is drawn by JavaScript, so the API was used instead |

A second pass (social note) ran 41 terms, kept the newest 100 matches of each and kept projects created since Sep 29 (when registration opened): it found the same 3 GitLab entries and opened 9 other candidates, all excluded (listed in section 2). Terms: transcend, life after code, life-after-code, lifeaftercode, hackathon, devpost, post-code, post-merge, after code, hands-off, duo agent, agentic, devsecops agent, incident, on-call, release agent, deploy agent, sdlc, path a, path b, showcase, gitlab duo, autonomous, lifecycle, agent, rollback, canary, postmortem, self-healing, remediation, release, observability, sentinel, guardian, merge request, pipeline, flow, devsecops, sre, triage, review ([example call](https://gitlab.com/api/v4/projects?search=transcend&order_by=created_at&sort=desc)).

Limits: project search matches only names and descriptions, returns at most 100 newest matches per term (for broad terms like "agent" that reaches back only a few days), and cannot see private projects. Entries on GitHub or with plain names can be missed.

### 1.5 GitLab issues

| Query or URL | Result |
|---|---|
| [issues?scope=all&search=Life After Code&created_after=2026-09-01](https://gitlab.com/api/v4/issues?scope=all&search=Life%20After%20Code&created_after=2026-09-01T00:00:00Z) | Word match, not phrase: 100+ results, mostly noise. Led to the onboarding project below. |
| [gitlab-community/community-members/onboarding](https://gitlab.com/gitlab-community/community-members/onboarding) issues since 2026-09-25 ([API](https://gitlab.com/api/v4/projects/60607268/issues?created_after=2026-09-25T00:00:00Z&per_page=100)) | 70 onboarding requests, each with a "Reason:" line. 6 name Transcend or Life After Code, 1 more says "AI agent project for the hackathon", 4 more name a hackathon without saying which (likely the separate October Community Hackathon, Oct 6 to 12, which rewards merged contributions to GitLab itself, [team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296)). |
| User project lists for those 7 people ([example](https://gitlab.com/api/v4/users/williamleewilliam1-star/projects)) | 0 public projects each, except iykyk-vedant (1 unrelated). @rambozambodotdev, who filed #5529, owns Receipted Pipeline. |

### 1.6 GitLab AI Catalog (public GraphQL API)

Every public item pulled at about 01:15 UTC from the [AI Catalog](https://gitlab.com/explore/ai-catalog/agents/): 3,498 items. Created in Feb 2026: 344; Mar 2026: 1,892; Jun 2026: 519; Oct 1 to 6: 7. Of those 7, six look like tests or small utilities ("probe-agent", "Flow1", "Repo Issue Helper") and one is a GitLab internal flow (see section 2). None is clearly from an entrant.

### 1.7 GitHub (WebFetch of github.com pages)

| Query or URL | Count | Relevant |
|---|---|---|
| [topics/gitlab-transcend](https://github.com/topics/gitlab-transcend) | 0 repos | none |
| [repos: "Life After Code" gitlab](https://github.com/search?q=%22Life+After+Code%22+gitlab&type=repositories) | 1 | jamesparser/a2a-omega-hvfr |
| [repos: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=repositories&s=updated&o=desc) | 7 | [alejandro-publius/life-after-code](https://github.com/alejandro-publius/life-after-code) (ours), Cubiczan/aftermerge, icohangar-ops/aftermerge, jamesparser/a2a-omega-hvfr |
| [repos: "GitLab Transcend"](https://github.com/search?q=%22GitLab+Transcend%22&type=repositories) | 8 | a2a-omega-hvfr (the other 7 are June) |
| [repos: transcend hackathon gitlab](https://github.com/search?q=transcend+hackathon+gitlab&type=repositories&s=updated&o=desc) | 4 | none (all June) |
| [repos: "Life After Code" OR "gitlab-transcend" OR "GitLab Transcend"](https://github.com/search?q=%22Life+After+Code%22+OR+%22gitlab-transcend%22+OR+%22GitLab+Transcend%22&type=repositories&s=updated&o=desc) | 14 | same 4 as above |
| [repos: "Duo Agent Platform"](https://github.com/search?q=%22Duo+Agent+Platform%22&type=repositories&s=updated&o=desc) | 12 | none (newest Aug 14) |
| [repos: gitlab duo created after Sep 28](https://github.com/search?q=gitlab+duo+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 0 | none |
| [repos: gitlab hackathon created after Sep 28](https://github.com/search?q=gitlab+hackathon+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 0 | none |
| [repos: gitlab devsecops agent created after Sep 28](https://github.com/search?q=gitlab+devsecops+agent+created%3A%3E2026-09-28&type=repositories&s=updated&o=desc) | 3 | a2a-omega-hvfr; Akhyame/ai-telegram-devsecops-agent (no hackathon mention) |
| [issues: "gitlab-transcend.devpost.com"](https://github.com/search?q=%22gitlab-transcend.devpost.com%22&type=issues&s=created&o=desc) | 1 | JannetEkka/DSProjects#18 |
| [issues: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=issues&s=created&o=desc) | 225 | DSProjects#18, TSAMBALI/Ariadne_Tsambali#218 (the rest unrelated) |
| [issues: "GitLab Transcend"](https://github.com/search?q=%22GitLab+Transcend%22&type=issues&s=created&o=desc) | 38 | same 2 (the rest are bot article digests) |
| [issues: "Transcend Hackathon"](https://github.com/search?q=%22Transcend+Hackathon%22&type=issues&s=created&o=desc) | 37 | Ariadne_Tsambali#218 |
| [issues: "Duo Agent Platform" hackathon](https://github.com/search?q=%22Duo+Agent+Platform%22+hackathon&type=issues&s=created&o=desc) | 33 | Ariadne_Tsambali#218 |
| Owner pages: [JannetEkka repos](https://github.com/JannetEkka?tab=repositories), [DSProjects hackathon issues](https://github.com/JannetEkka/DSProjects/issues?q=is%3Aissue+label%3Ahackathon), [TSAMBALI repos](https://github.com/TSAMBALI?tab=repositories), [Ariadne_Tsambali](https://github.com/TSAMBALI/Ariadne_Tsambali) | 16 / 14 / 11 / about 218 issues | No Proof of Fix repo, no NEXUS repo; Ariadne_Tsambali has no code |

The social pass also opened the 3 entrant pages its web searches found (Proof of Fix, NEXUS, the DevOps class project). GitHub repository search through `gh` was refused (see 1.10).

### 1.8 Web search (search-engine excerpts)

Code-host pass, 5 queries, 10 results each, 0 relevant:

| Query | Results | Relevant |
|---|---|---|
| `site:github.com "gitlab-transcend"` | 10 | 0 (June gitlab.com workspaces) |
| `site:github.com "Life After Code" GitLab hackathon` | 10 | 0 |
| `site:github.com "GitLab Transcend" hackathon` | 10 | 0 (June blog and June workspaces) |
| `"Duo Agent Platform" hackathon 2026 "Life After Code"` | 10 | 0 (Feb 2026 winners blog) |
| `"gitlab-transcend.devpost.com"` | 10 | 0 (June items) |

Social pass, 18 queries ("Results" is the number of links returned):

| # | Query | Mode | Results | What came back |
|---|---|---|---|---|
| 1 | "GitLab Transcend" hackathon | standard | 10 | GitLab's June recap, 7 June welcome issues, 2 listing-site pages. No October entrant. |
| 2 | "Life After Code" GitLab | standard | 9 | Nothing relevant |
| 3 | "#GitLabTranscend" | standard | 9 | Press releases for GitLab's Feb and June 2026 events |
| 4 | "gitlab-transcend.devpost.com" | standard | 10 | June recap (French), a daily.dev copy, 4 June welcome issues |
| 5 | "Duo Agent Platform" hackathon project | standard | 9 | GitLab's 2025 "AI in Action" post, a Feb 2026 welcome issue, a demo project, launch news |
| 6 | site:linkedin.com "GitLab Transcend" | standard | 9 | 2 LinkedIn profiles linked to the June event. No entrant posts. |
| 7 | site:linkedin.com "Life After Code" hackathon | standard | 9 | 0 LinkedIn results |
| 8 | site:reddit.com GitLab hackathon 2026 | standard | 9 | 0 Reddit results |
| 9 | site:dev.to gitlab hackathon 2026 | standard | 9 | 0 dev.to results |
| 10 | site:medium.com GitLab Duo Agent Platform hackathon | standard | 10 | 0 Medium results; GitLab's Feb winners post and forum thread |
| 11 | site:x.com "GitLab Transcend" | standard | 9 | 0 X results |
| 12 | site:youtube.com GitLab Transcend hackathon | standard | 10 | 0 YouTube results; 8 June welcome issues |
| 13 | "GitLab Orbit" hackathon project | standard | 9 | June recap in three languages, a forum thread, a workshop page |
| 14 | "Transcend Bangalore" GitLab | standard | 10 | GitLab's Bangalore event page ([page](https://about.gitlab.com/events/transcend/india/)) |
| 15 | "devpost.com/software" "GitLab Duo" | standard | 9 | 0 Devpost project pages |
| 16 | "GitLab Transcend" hackathon | extended | 9 | Devpost's X post announcing October; June forum posts; the June /rules page |
| 17 | "gitlab-transcend.devpost.com" | extended | 9 | 2 October entrant notes on GitHub (Proof of Fix, NEXUS) |
| 18 | "Life After Code" GitLab | extended | 9 | Proof of Fix again; GitLab blog posts "[When code is abundant](https://about.gitlab.com/blog/when-code-is-abundant/)" and "[Claude Code and GitLab: Three workflows that ship](https://about.gitlab.com/blog/claude-code-and-gitlab/)" (titles only) |

The `site:` filter was mostly ignored by the search tool. Caveat: the June edition used the same Devpost address (in June, GitLab's [contributors-gitlab-com!2293](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2293) pointed "Official Rules" to its /rules page), so any search excerpt about that address may describe June (unverified). Not run because the budget ran out (8 planned, 7 distinct). Code-host pass: `"Life After Code" GitLab hackathon agent project October 2026`, `site:gitlab.com "Life After Code"`, `"GitLab Transcend" "Path A" OR "Path B" agent "hands-off" 2026`. Social pass: `site:github.com "Life After Code" GitLab hackathon`, `site:github.com "gitlab-transcend.devpost.com"`, `"Life After Code" hackathon Duo agent October 2026`, `"Transcend III" GitLab hackathon`, `site:gitlab.com "Life After Code"` (also planned by the code-host pass).

### 1.9 GitLab's own sources on the event and on June

- June judging update, 2026-07-13: [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137). GitLab's review of June participant feedback: [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245). October theme and goals: [epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40).
- GitLab's guide page source: [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue), [AboutSection.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/AboutSection.md), [ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue), added in [MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747).
- The judges' reference project: [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase).
- Our rules write-up, which holds the Devpost text seen through search excerpts: [RULES.md](RULES.md).
- Devpost tabs read: updates 0, discussion topics 0, gallery projects 0, team-formation posts 0. All were blocked ([rules_discussions.md](research/rules_discussions.md)).
- The platform-friction parts of GitLab's June review (the Orbit query language, flow YAML, access gates) are not about the field and are not repeated here; their links are in [gitlab_guide_and_reference.md](research/gitlab_guide_and_reference.md).

### 1.10 Blocked, and the search cap

**Search cap.** The web search tool allows 200 calls per turn, shared by every agent in the session. It ran out during this research: the code-host pass got 5 searches and the social pass 18 before the tool refused ("this turn's web search budget is used up"). The 8 queries above were never run. This file used no web search, and only one GitLab API call.

**Blocked hosts.** Each URL was tried once with the tool shown and not retried.

| Host or URL | Tool | Error |
|---|---|---|
| Devpost: [gitlab-transcend.devpost.com](https://gitlab-transcend.devpost.com/), [/updates](https://gitlab-transcend.devpost.com/updates), [/forum_topics](https://gitlab-transcend.devpost.com/forum_topics), [/project-gallery](https://gitlab-transcend.devpost.com/project-gallery), [/participants](https://gitlab-transcend.devpost.com/participants), [/rules](https://gitlab-transcend.devpost.com/rules), [devpost.com search](https://devpost.com/hackathons?search=gitlab%20transcend) | curl, WebFetch | 403 to CONNECT ("policy denial"); WebFetch `EGRESS_BLOCKED` |
| about.gitlab.com: [June recap](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/), [Bangalore event](https://about.gitlab.com/events/transcend/india/) | WebFetch | `EGRESS_BLOCKED` ("Access to about.gitlab.com is blocked by the network egress proxy.") |
| contributors.gitlab.com: [guide page](https://contributors.gitlab.com/transcend-hackathon), [registration API](https://contributors.gitlab.com/api/v1/transcend_hackathon) (route exists in the [site source](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/config/routes/api_routes.rb)) | WebFetch, curl | `EGRESS_BLOCKED`; "CONNECT tunnel failed, response 403" |
| GitLab forum: [June recap thread](https://forum.gitlab.com/t/gitlab-transcend-hackathon-what-developers-built-on-gitlab-orbit/134593), [June start post](https://forum.gitlab.com/t/the-transcend-hackathon-starts-now/134144), [forum.gitlab.com](https://forum.gitlab.com/) | curl, WebFetch | 403 to CONNECT; `EGRESS_BLOCKED` |
| Social: [LinkedIn](https://www.linkedin.com/in/helenadixon), [Reddit](https://www.reddit.com/r/gitlab/), [dev.to](https://dev.to/t/gitlab), [Medium](https://medium.com/tag/gitlab), [YouTube search](https://www.youtube.com/results?search_query=gitlab+transcend+hackathon), [keynote video](https://www.youtube.com/watch?v=lw98rbIUdz0), [x.com/gitlab](https://x.com/gitlab), [Devpost on X](https://x.com/devpost/status/2104984062469308626), [Hacker News](https://hn.algolia.com/api/v1/search?query=gitlab%20transcend), [Bluesky](https://bsky.app/search?q=gitlab%20transcend), [Bluesky API](https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=gitlab%20transcend), [Mastodon](https://mastodon.social/api/v2/search?q=gitlab%20transcend), [Threads](https://www.threads.net/search?q=gitlab), [Hashnode](https://hashnode.com/search?q=gitlab%20transcend), [lobste.rs](https://lobste.rs/search?q=gitlab) | curl, WebFetch | 403 to CONNECT (curl exit 56); `EGRESS_BLOCKED` |
| Discord: [discord.gg/gitlab](https://discord.gg/gitlab), [invite API](https://discord.com/api/v10/invites/gitlab?with_counts=true) | WebFetch, curl | `EGRESS_BLOCKED`; 403 to CONNECT |
| Copies of the June recap: [daily.dev](https://daily.dev/posts/gitlab-transcend-hackathon-what-developers-built-on-gitlab-orbit-lhajgd46q), [startupgrantsindia.com](https://www.startupgrantsindia.com/gitlab-transcend-hackathon), [aiweekly.co](https://aiweekly.co/node/2806); short link [go.gitlab.com/pLDY3G](https://go.gitlab.com/pLDY3G) | WebFetch | `EGRESS_BLOCKED` |
| GitHub API: [github.com search](https://github.com/search?q=gitlab-transcend&type=repositories) and [topics](https://github.com/topics/gitlab-transcend) through curl, [api.github.com search](https://api.github.com/search/repositories?q=gitlab-transcend), `gh search repos` ([api.github.com/search/repositories](https://api.github.com/search/repositories)) | curl, gh | 403: "This GitHub API path is not available: sessions are bound to their configured repositories." WebFetch of github.com pages worked. |
| GitLab endpoints that need sign-in: [issue notes](https://gitlab.com/api/v4/projects/87183213/issues/1/notes), [global search](https://gitlab.com/api/v4/search?scope=issues&search=Life%20After%20Code), [about-gitlab-com project search](https://gitlab.com/api/v4/projects/gitlab-com%2Fmarketing%2Fdigital-experience%2Fabout-gitlab-com/search) | curl | 401 Unauthorized. The `/issues?scope=all` endpoint worked instead. |
| [gitlab-ai-hackathon/participants](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Fparticipants) | curl | `404 Group Not Found` (moved, see 1.3) |
| GitLab Explore pages | curl, WebFetch | HTTP 200 but the list is drawn by JavaScript |
| web.archive.org | not tried | Known to be blocked |

Not opened on purpose: entrant demo videos ([AfterMerge](https://youtu.be/jl3muP7JNEE), [BABYDOV](https://youtu.be/6d7QBKYO29I); YouTube is blocked), live demo sites ([aftermerge.vercel.app](https://aftermerge.vercel.app), [BABYDOV Pages dashboard](https://babydov-release-sentinel-e52f53.gitlab.io); the READMEs were read), and sites that copy blocked pages (awskws.duckdns.org, backiee.wasmer.app, thenote.app), because using them would route around the block.

## 2. October entrants and planned entries

Stages use the nine names on the Devpost page: plan, create, verify, package, secure, release, configure, monitor, govern ([RULES.md](RULES.md), unverified). "Uses Duo" means GitLab Duo Agent Platform features (flows, agents, MCP) visible in the repo or stated by the author. Every entry must use them ([RULES.md](RULES.md)).

| # | Name | Link | Author | What it does | Stages | Idea space | Built or planning | Uses Duo |
|---|---|---|---|---|---|---|---|---|
| 1 | Receipted Pipeline | [GitLab](https://gitlab.com/rambozambodotdev/receipted-pipeline), [demo target](https://gitlab.com/rambozambodotdev/receipted-pipeline-demo) | @rambozambodotdev (profile name "Rambo (AI, director of ops for Zambo)") | An agent opens an MR, gates review, security and tests, merges, checks the GitLab Pages deploy and a health probe, and mints one "verifiable receipt" per stage | create (review), secure, verify, release, monitor | Whole post-merge pipeline with evidence receipts. Path B, hands-off. | Partly built: MR !1 merged and green pipelines on Oct 5, driven by an outside script (see notes) | Yes on paper: custom flow YAML, AGENTS.md, MCP config. The flow is "inert until it is registered." |
| 2 | AfterMerge | [GitLab](https://gitlab.com/sam1054/aftermerge), [GitHub](https://github.com/Cubiczan/aftermerge), [GitHub copy](https://github.com/icohangar-ops/aftermerge) | @sam1054 (GitLab), Cubiczan (GitHub), Sam Desigan | Browser-only simulated console: after a merge, an agent runs SAST, dependency reachability, staging deploy, smoke tests, release notes, risk-based human approval, promote | secure, verify, release, govern | Post-merge release gatekeeper with a human gate at medium or high risk. Path A. | Built as a simulation: demo UI and video. GitLab project: 1 commit, 0 pipelines. | None found: "Nothing in the loop calls the network" |
| 3 | BABYDOV Release Sentinel | [GitLab](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel) | Ivan Babydov (group babydov-life-after-code) | Deterministic "release authority": evidence ledger, risk and "autonomy budget" scores, canary, rollback rehearsal, then GO, HOLD or ROLLBACK, attestation, Pages dashboard | verify, secure, package (SBOM), release, monitor, govern | Release gatekeeper with canary, rollback and tamper-evident evidence. Path B, hands-off. | Built: 5 pipeline runs (first failed, 4 green), Pages dashboard, 58-second video | None found: no model at all |
| 4 | A2A Omega HVFR | [GitHub](https://github.com/jamesparser/a2a-omega-hvfr) | @jamesparser | Hunter agent scans MRs and commits, Verifier confirms and fixes or blocks, Triage closes false positives, hourly poller | secure, verify, govern | Security triage and auto-fix. Path B, hands-off. | Early code: 11 commits, last updated about Oct 2. No GitLab copy. | None found: no CI file, no `.gitlab/duo`, model not named |
| 5 | NEXUS DevSecOps AI | [GitHub issue #218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218) | @TSAMBALI | Plan for a governed "10-agent mesh" with a falsification agent, a Gemini model router and SANS SIFT forensics. Demo: finds the real cause of a staging HTTP 503. | claims all 9; focus on incident root cause, security, compliance | Multi-agent "everything" mesh with incident root cause. Claims all 3 autonomy levels and Cloud Run. | Planning only: repo empty, the GitLab repo it names returns 404 | Claimed (unverified: no code public) |
| 6 | Proof of Fix | [GitHub issue #18](https://github.com/JannetEkka/DSProjects/issues/18) | @JannetEkka | "an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears" | release (after merge), monitor, plan (reopens the issue) | Post-deploy proof that a fix worked. Path not stated. | Planning only: no repo yet | Not stated |
| 7 | (unnamed) post-code release agent | [onboarding #5528](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5528) | @williamleewilliam1-star | "build and validate an autonomous post-code release agent with GitLab Duo Agent Platform" | release | Release agent | Intent only: no public project | Stated in the request |
| 8 | DevOps class project | [GitHub](https://github.com/Reeti05Agarwal/DevOps-) | @Reeti05Agarwal | Flask notes API with GitHub Actions CI, Ansible, Docker, Kubernetes, Prometheus and Grafana. The README lists the hackathon as an optional bonus step: "Event: Life After Code, the GitLab Transcend Hackathon on Devpost (deadline Oct 27, 2026)". | verify (CI), configure (Ansible), release (deploy), monitor | Plain DevOps pipeline, not an agent | Built (class project) | No |
| 9 | (no idea stated) | [onboarding #5524](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5524) | @1Hilal7 | "Participating in the Life After Code: Transcend Hackathon and learning to build agentic DevSecOps workflows with GitLab Duo Agent Platform." | n/a | n/a | No public project | Named in the request |
| 10 | (no idea stated) | [onboarding #5523](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5523) | @mhamzanadeem2000003 | "...build an AI-powered DevSecOps project using GitLab Duo Agent Platform." | n/a | n/a | No public project | Named in the request |
| 11 | (no idea stated) | [onboarding #5525](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5525) | @matthewjameswatkins1978 | "...an open-source project that uses GitLab Duo Agent Platform and CI/CD" | n/a | n/a | No public project | Named in the request |
| 12 | (no idea stated) | [onboarding #5488](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5488) | @tusharaggarwal274 | "...build an agentic solution that automates meaningful parts of the software delivery lifecycle." | n/a | n/a | No public project | Not stated |
| 13 | (no idea stated) | [onboarding #5520](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5520) | @hawk-2221 | "build an AI agent project for the hackathon" (hackathon not named) | n/a | n/a | No public project | Not stated |

Counts: 7 agent ideas (rows 1 to 7). Paths: 3 say Path B hands-off (Receipted Pipeline, BABYDOV, A2A Omega), 1 says Path A (AfterMerge), 3 do not say. Duo: 1 of the 4 built agent entries has Duo files (Receipted Pipeline), and its flow was not live on Oct 6.

### Notes on each entry

**1. Receipted Pipeline.** Description: "Receipted Pipeline: an AI agent runs the full post-code DevSecOps lifecycle (review, security, test, deploy, monitor) hands-off on GitLab, and every stage leaves a verifiable execution receipt (AER-1). GitLab Transcend hackathon Path B entry." Topics include `gitlab-transcend`, `mcp`, `verifiable-receipts`. MIT. Created 2026-10-05 ([project API](https://gitlab.com/api/v4/projects/87252421)).
- Two layers. An outside Python orchestrator with a personal access token makes a real change, opens an MR, posts a review note, triages SAST and secret-detection findings, parses JUnit, merges only if gates pass, then checks the Pages deploy and a monitor probe ([orchestrator/README.md](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/orchestrator/README.md), [config.yaml](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/orchestrator/config.yaml)). A Duo custom flow has five `AgentComponent` stages chained by routers that stop at the first failing gate, triggered by pipeline events ([flow YAML](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/.gitlab/duo/flows/receipted-pipeline.yaml), [AGENTS.md](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/AGENTS.md)). Receipts come from the author's own "Zambo" MCP server ([mcp.json](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/.gitlab/duo/mcp.json)).
- The two notes disagree on what runs. The code-host pass saw [MR !1](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/merge_requests/1) merged on Oct 5 with 5 notes and the latest 10 [pipelines](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/pipelines) green, and the [README](https://gitlab.com/rambozambodotdev/receipted-pipeline/-/blob/main/README.md) saying "The flow YAML above is inert until it is registered." The social pass quotes the README saying the orchestrator "is under construction for the hackathon entry and is not implemented yet". Either way, no Duo flow had run by Oct 6 (unverified which part is unfinished).
- AGENTS.md: "Hands-off: the flow runs ambient on pipeline events. No human in the loop and no interactive prompts." Also: "a receipt proves the saved result was not changed. It does NOT prove the agent was right."
- The account looks AI-run and enters many contests at once: 20 projects, including six `hackathon-blitz-*` entries for other contests created Oct 4, all built on the same "AER-1 receipts" idea ([user projects API](https://gitlab.com/api/v4/users/rambozambodotdev/projects), [projects](https://gitlab.com/users/rambozambodotdev/projects)). Its onboarding request [#5529](https://gitlab.com/gitlab-community/community-members/onboarding/-/work_items/5529): "Participating in the GitLab Transcend hackathon (October 2026) with the receipted-pipeline project". Deploys to GitLab Pages, not Google Cloud.

**2. AfterMerge.** Description: "AfterMerge - post-merge DevSecOps agent for Life After Code" (GitLab); "Post-merge agent console demo (FieldClear / Life After Code Path A)" (GitHub).
- [README](https://gitlab.com/sam1054/aftermerge/-/blob/main/README.md): "When a merge request lands, an agent owns the life after the code: security scan, dependency audit, staging deploy, smoke tests, release notes, a human approval gate, and production promote. The demo is fully simulated. No GitLab token and no paid API." Policy: "Medium risk stops at a person. A critical, reachable advisory on an older run never leaves the dependency stage." Path A: "This is a **new repo and a new demo**."
- Fictional field-service company ("Northline Mechanical", product "FieldClear"). Next.js, state in the browser, hosted at [aftermerge.vercel.app](https://aftermerge.vercel.app), video at [youtu.be/jl3muP7JNEE](https://youtu.be/jl3muP7JNEE) (both unverified, not opened).
- [architecture.md](https://gitlab.com/sam1054/aftermerge/-/blob/main/docs/architecture.md): "The hackathon build runs entirely in the browser. A later plug-in replaces the player with GitLab webhooks and CI job APIs." As it stands it would likely fail the "genuinely use GitLab AI features" check (unverified; they may add it).

**3. BABYDOV Release Sentinel.** Description: "Evidence-first autonomous release authority for GitLab Life After Code 2026 · Path B Hands-off Agent." Group created Oct 3, commits Oct 5 and 6.
- [README](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/README.md): it "will only promote a build when it can prove three things": evidence intact, canary correct, previous release restorable. "If any of those proofs are missing, the agent does not improvise. It **HOLDs**. If production verification fails, it **ROLLBACKs**."
- Self-reported (unverified): a "2,000,000-agent adversarial fleet" with "0 unsafe GO decisions" ([SUBMISSION_DRAFT.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/SUBMISSION_DRAFT.md)). Targets Path B Best Hands-off and is "also optimized for" Most Stages Covered, Most Impactful and Most Creative ([JUDGING_MATRIX.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/JUDGING_MATRIX.md)).
- No model: the agent returns `"llm_can_override": False`, and [ARCHITECTURE.md](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/blob/main/docs/ARCHITECTURE.md) says "Any future model or heuristic advisor may summarize a diff or propose risk signals, but it cannot change the deterministic safety kernel." Same pass or fail risk as AfterMerge (unverified).
- Links (not opened): [Pages dashboard](https://babydov-release-sentinel-e52f53.gitlab.io), [video](https://youtu.be/6d7QBKYO29I), [pipelines](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel/-/pipelines) ([pipelines API](https://gitlab.com/api/v4/projects/87191977/pipelines)).

**4. A2A Omega HVFR.** About text: "A2A Omega HVFR - Hunt · Verify · Fix/Block · Report. Hands-off multi-agent DevSecOps lifecycle automation for GitLab Transcend (Life After Code)." It reuses the author's "A2A Omega" routing hub, "redirect[ing] agent-to-agent orchestration from external bounty hunting toward GitLab's post-code lifecycle", and is labelled "Path B: Bring Your Own · Hands-off Agent" ([raw README](https://raw.githubusercontent.com/jamesparser/a2a-omega-hvfr/main/README.md)). Files: `a2a_hub.py`, `a2a_agentverse.py`, `a2a_e2a.py`, `a2a_client.py`, `poller.py`, `mesh_test.py`, `config/`.

**5. NEXUS DevSecOps AI.** [Issue #218](https://github.com/TSAMBALI/Ariadne_Tsambali/issues/218), "GitLab Transcend Hackathon", opened Oct 5, no comments. "A governed 10-agent software lifecycle and SIFT forensic intelligence suite built on the GitLab Duo Agent Platform and Model Context Protocol."
- Agents: Lifecycle Orchestrator, Code Intelligence, Security, Verification, Compliance, Deployment, Monitoring, Risk and Scenario, a "Challenge/Falsification Agent (Popperian Disproof Gate)", Executive Decision. A "Green SCI Model Router" picks Gemini models for cost and carbon. Demo: the falsification agent rejects "code regression" for a staging 503 and finds Redis connection-pool config drift.
- Key line: "Trust in autonomous DevSecOps does not come from an LLM claiming '99% confidence.' Trust comes from falsifiability and architectural containment."
- All accuracy numbers are self-reported (unverified), for example 99.4% recall and "cutting carbon intensity by 64.2%". It seems aimed at a SANS SIFT contest too ("GitLab Transcend 3:00 limit and SIFT 5:00 limit"). The GitLab repo it names, `gitlab.com/gitlab-transcend/nexus-devsecops-ai`, returns 404 ([API](https://gitlab.com/api/v4/projects/gitlab-transcend%2Fnexus-devsecops-ai)).
- The repo is a notebook of about 218 issues, many of them other "NEXUS" hackathon plans (#217 "Case Closed & Atlantic Nexus AI Platform", #216 "Dublin Nexus AI", #209 "Protocol SIFT", per the [issue list](https://github.com/TSAMBALI/Ariadne_Tsambali/issues?q=is%3Aissue+sort%3Acreated-desc)). A June team called NEXUS is quoted in GitLab's June review ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)); whether it is the same author is not known (unverified).

**6. Proof of Fix.** See section 3.

**7. Onboarding requests.** From the 70 requests since Sep 25 ([API](https://gitlab.com/api/v4/projects/60607268/issues?created_after=2026-09-25T00:00:00Z&per_page=100)). None of these people had a public GitLab project on Oct 6.

### Who is entering (inference)

Three of the seven ideas come from accounts that enter many contests at once: @rambozambodotdev (its profile says it is an AI; six other contest entries made Oct 4), @JannetEkka (14 hackathon tracking issues, one per contest from Oct 8 to Dec 2, ticked by agent "sessions") and @TSAMBALI (a notebook of about 218 issues, many of them other contest plans). GitLab's October epic lists an open goal: "Gaming and AI-spam are kept out, so reviewer goodwill is protected" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)), and a GitLab participant survey that covers the June hackathon lists "AI-assisted contribution creates fairness concerns" among the pain points ([team-task#1329](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1329)). Mass-produced entries tend to follow the official examples, which sit in the crowded spaces (inference, see section 4).

Field size: "621 participants" on the Devpost page when a search engine indexed it ([Devpost](https://gitlab-transcend.devpost.com/), unverified, crawl date unknown). GitLab's own count: "667 folks registered so far" on 2026-10-05, with a target of "5,000 registrations and 500 submissions" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)). At June's rate (265 eligible of 1,576 registered, about 17%), 667 registrations would give about 110 judged projects (inference).

### Seen but not entries

- GitLab staff workspaces: [leetickett](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase), [missy-davies](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase), [leetickett-gitlab](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/12687636). Default template, nothing built. Missy Davies is a listed judge ([RULES.md](RULES.md), from search excerpts of Devpost, unverified).
- The judges' reference, [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase) (GitLab staff): a Duo Developer flow opens an MR, Duo Code Review, auto-merge, tests, image build, SAST, dependency, secret and container scans, staging deploy, smoke test, promote to production, tagged release, summary on the issue. "Nothing in steps 2 to 4 requires a human."
- GitLab internal AI Catalog flow "Review instructions learner": "After merge, find human review feedback Duo missed and propose review-instruction updates." ([catalog](https://gitlab.com/explore/ai-catalog/flows/1016015/)). From a gitlab-org project.
- GitLab demo account [custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo) (Oct 5): sample flows for release notes, coding-standards review and issue triage. These are what GitLab's field teams demo, so these ideas look stock.
- New projects on gitlab.com or GitHub with no hackathon mention: [rodripn91/pipeline-doctor](https://gitlab.com/rodripn91/pipeline-doctor) (CI file analysis, no AI agent), [Akhyame/ai-telegram-devsecops-agent](https://github.com/Akhyame/ai-telegram-devsecops-agent) (Telegram control of a CI security gate: "The deterministic Security Gate makes security decisions, not the AI model"), [Qivoxe/Codegenome](https://gitlab.com/Qivoxe/Codegenome) (change blast-radius graph, "hackathon MVP" badge, no contest named), [jyoshise1/ai-security-deepscan-orbit](https://gitlab.com/jyoshise1/ai-security-deepscan-orbit) (Japanese test write-up of Duo custom agents for security review), [DiogoRibeiro7/gitlab-pipeline-profiler](https://gitlab.com/DiogoRibeiro7/gitlab-pipeline-profiler) (pipeline history analysis), [StateOfFlowHunter/votely](https://gitlab.com/StateOfFlowHunter/votely) (DevOps showcase app with canary releases), [peerivo/reviewer](https://gitlab.com/peerivo/reviewer) (commercial fail-closed MR security reviewer), [ipylypenko/Heard-Product-Feedback-App](https://gitlab.com/ipylypenko/Heard-Product-Feedback-App) (agent that turns public customer feedback into a ranked roadmap), [nishankbagde/devops-incident-platform](https://gitlab.com/nishankbagde/devops-incident-platform) (blank template), and two GitLab staff or demo projects, [jira-swag-shop](https://gitlab.com/gl-demo-ultimate-jhooper/ai-agents/jira-swag-shop) and [duo-design-review](https://gitlab.com/gitlab-org/upstream-studios/design-strategy/duo-design-review).

## 3. Proof of Fix (the idea we must avoid)

**Source:** [JannetEkka/DSProjects#18](https://github.com/JannetEkka/DSProjects/issues/18), found by web search (social pass, queries 17 and 18) and by GitHub issue search ([search](https://github.com/search?q=%22gitlab-transcend.devpost.com%22&type=issues&s=created&o=desc)), read with WebFetch on 2026-10-06.

**The issue:** title "Oct 27 · GitLab: Life After Code - "Proof of Fix"", label `hackathon`, opened 2026-10-05, open, 0 comments, no linked PRs or repos.

**The idea, word for word:**

> **Plan:** "Proof of Fix", an agent that checks production after a merge for the log line the fix promised, and reopens the issue if that line never appears.

The rest of the issue is an unticked checklist (Registered, Rules read, Devpost page, Repo, Working build, Demo video, Submission text, Submitted, Result), the line "Waiting on Jannet: Start session S4." and the footer "Every session ticks this checklist and comments at each milestone. This issue is the single place for status."

**Context:** the same repo has 14 `hackathon` tracking issues opened Oct 5, one per contest from Oct 8 to Dec 2 ([list](https://github.com/JannetEkka/DSProjects/issues?q=is%3Aissue+label%3Ahackathon)). It looks like agent sessions run a hackathon pipeline for the owner (inference). No Proof of Fix repo among the owner's 16 repos ([repos](https://github.com/JannetEkka?tab=repositories)), and no GitLab project named "proof of fix" or "proof-of-fix" since about Sep 25. State: planning only. Path and Duo use not stated.

**How the idea works, in parts:**

1. A fix is merged.
2. The fix "promised" a log line: a specific signal that should show up in production once the fix works.
3. An agent reads production logs after the merge.
4. If the line never appears, the agent reopens the issue.

Stages: release (after merge), monitor (logs), plan (issue state). Its emotional hook, in my words: a closed issue is not the same as a fixed problem.

**Nearby ideas that would collide with it:**

- **Any "did the fix work in production" check, whatever the signal.** Swapping the log line for metrics, error rates, traces, OpenTelemetry data from GitLab's observability instance, a health probe or a synthetic user check is still the same idea.
- **Fix promises or expected-signal contracts.** An issue or MR states what production should show after the fix, and an agent checks it later.
- **Changing issue state from production evidence.** Reopening, relabelling or commenting on a closed issue because the fix did not show up or the error came back (a regression watch on closed issues), or closing issues only when production proves the fix.
- **"Your bug is really fixed" messages to the reporter.** If the core is still confirming the fix in production, this is Proof of Fix with a different audience. The social note listed "proving the fix worked for the person who reported the problem" as a thin space; it sits right next to Proof of Fix.
- **"Did the change hold in production" scoring.** June's [Stayed Shipped](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648) ("Merged is not done. Shipped and stayed shipped is done.") measured whether changes merged by AI agents survive in production, and won second place in Technological Implementation ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137)). Judges have seen this family before.
- **Partial overlaps already in the October field:** BABYDOV's production verification, Receipted Pipeline's monitor probe, AfterMerge's smoke tests, and the judges' reference, which smoke-tests production and posts a summary back on the issue.

To stay clear (inference): do not make post-merge verification of a promised fix the core, and do not have the agent reopen or close issues based on production signals.

## 4. History of crowding

### June 2026 (Transcend II, built on GitLab Orbit; same Devpost address and organizers)

GitLab's own judging update, 2026-07-13, by mmichaux-ext in [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137), word for word:

> * **1,576 developers registered.**
> * **318 submissions received.**
> * **265 eligible for judging** (Showcase Track: agents, flows, and skills built on Orbit).
> * Most submissions clustered into a few crowded problem spaces (69 built pre-merge impact review, 36 built onboarding aids), but the field still produced genuinely novel work: 17 one-of-a-kind concepts and 20 two-of-a-kind. Five of the eight winners came from those rare tiers.

The same update says the AI pre-scoring (three models, about 800 runs) "could not settle Potential Impact (models cap it differently) or Design (110 of 265 had silent or missing demos), so the panel resolved both by hand. Humans picked every winner."

What the numbers mean:

- 69 of 265 (26%) built pre-merge impact review and 36 (14%) built onboarding aids: together 105 of 265 (40%) sat in two ideas.
- The rare tiers held at most 57 projects (if "20 two-of-a-kind" means 20 pairs) or 37 (if it means 20 projects): 14% to 22% of the field. That share produced 5 of the 8 winners (more than 60%).
- The other 3 winners came from more common ideas. [Sankofa](https://gitlab.com/gitlab-ai-hackathon/transcend/34570711) won first in Technological Implementation with blast radius plus CVE tracing, inside the most crowded space, so strong execution can still win there (inference from a search-excerpt description; GitLab did not say which 3).

June winners ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137), full write-up in the [winners announcement](https://gitlab-transcend.devpost.com/updates/44639-winners-announcement-gitlab-transcend-hackathon-how-the-community-built-on-orbit)):

| Category | First | Second |
|---|---|---|
| Technological Implementation | [Sankofa](https://gitlab-transcend.devpost.com/submissions/1054521-sankofa) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/34570711)): "blast-radius analysis, issue briefing, and CVE tracing via three agents" (search excerpt, unverified) | [Stayed Shipped](https://gitlab-transcend.devpost.com/submissions/1054106-stayed-shipped) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648)): whether AI-merged changes survive in production |
| Design and Usability | [Carver](https://gitlab-transcend.devpost.com/submissions/1062163-carver-the-migration-quoting-agent) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946)): "estimates what a legacy migration will cost before you commit to one" | [Marshal](https://gitlab-transcend.devpost.com/submissions/1062651-marshal-autonomous-migration-assistant) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992)): an autonomous migration assistant (from its Devpost link name) |
| Potential Impact | [CrossCut](https://gitlab-transcend.devpost.com/submissions/1061837-crosscut): "CI test selection based on call-graph traversal, cutting CI payload by 90%+" (search excerpt, unverified) | [OrbitWeaver](https://gitlab-transcend.devpost.com/submissions/1061548-orbitweaver) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/35222941)): not described in our notes |
| Quality of the Idea | [Transcend](https://gitlab-transcend.devpost.com/submissions/1056751-transcend) ([repo](https://gitlab.com/gitlab-ai-hackathon/transcend/3537494)): semantic web reasoning on top of Orbit with OWL, SPARQL and RDF (search excerpt, unverified) | [Universal Agent OS](https://gitlab-transcend.devpost.com/submissions/1053916-universal-agent-os): not described in our notes |

Our own sorts of the public [June group](https://gitlab.com/gitlab-ai-hackathon/transcend) (312 projects, 149 READMEs that describe a project, 146 sorted by title and first paragraph; keyword sort, rough):

| June idea | READMEs | Examples |
|---|---|---|
| Pre-merge blast radius and change impact | about 45 | [Ripple](https://gitlab.com/gitlab-ai-hackathon/transcend/669256), [Tremor](https://gitlab.com/gitlab-ai-hackathon/transcend/39301572) |
| Other merge request review tools | about 10 | [Switchyard](https://gitlab.com/gitlab-ai-hackathon/transcend/19746610) (safe merge order), [Tether](https://gitlab.com/gitlab-ai-hackathon/transcend/34569267) (production-aware review), [DeployGuard](https://gitlab.com/gitlab-ai-hackathon/transcend/31901382) (deploy confidence score) |
| Onboarding and codebase questions | 17 | |
| Incident root cause and post-mortems | about 10 | [Praetor](https://gitlab.com/gitlab-ai-hackathon/transcend/28344226), [Backtrace](https://gitlab.com/gitlab-ai-hackathon/transcend/7963149), [AFTERMATH](https://gitlab.com/gitlab-ai-hackathon/transcend/35450945) |
| Security reachability and CVE triage | 10 | [ReachGate](https://gitlab.com/gitlab-ai-hackathon/transcend/39037247) |
| Architecture rules and drift | 9 | |
| Dead code and code health | 5 | |
| Compliance and access | 4 | |
| CI failure and test tools | 4 | [Pipeline Pathologist](https://gitlab.com/gitlab-ai-hackathon/transcend/39033288) |
| Deploy confidence or post-merge outcomes | 3 | [Stayed Shipped](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648) |
| Cost | (not counted) | [COGS Sentinel](https://gitlab.com/gitlab-ai-hackathon/transcend/39430932) (pre-merge infrastructure cost) |

A separate scan of the same READMEs found the phrase "blast radius" in 76 of 148 ([gitlab-transcend-past-editions.md](research/winners/gitlab-transcend-past-editions.md)). GitLab's blog recap, seen only as a search excerpt, said: "Seventy teams built a version of the same tool: Tell me what this change could break before I merge it." ([GitLab blog](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/), unverified wording). GitLab's count, both README sorts and the blog excerpt agree: pre-merge impact review held a quarter or more of June.

### Feb to Mar 2026 (GitLab AI Hackathon, the same Duo Agent Platform as October)

Size: "nearly 7,000 developers" and "600+" agents and flows ([GitLab blog](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/), search excerpts, unverified). On gitlab.com: 1,788 public projects in the [Feb to Mar group](https://gitlab.com/groups/gitlab-community/community-projects/2026-02-ai-hackathon); 506 of them published 1,807 [AI Catalog](https://gitlab.com/explore/ai-catalog/agents/) items.

Keyword counts: projects (of the 506 that published to the catalog) whose agent or flow names or descriptions match the idea. One project can count in several rows. Rough.

| Idea | Projects | Share of 506 | Example |
|---|---|---|---|
| Security review on merge requests | 132 | 26% | |
| Code review | 95 | 19% | |
| Remediation fix MRs (auto-fix) | 82 | 16% | |
| Issue triage and planning | 81 | 16% | |
| Carbon or energy footprint | 73 | 14% | [GreenOps](https://gitlab.com/explore/ai-catalog/agents/1003840/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/29841609)), [Carbon-Aware Deployment Agent](https://gitlab.com/explore/ai-catalog/agents/1006976/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35652005)) |
| CI pipeline failure diagnosis and fix MRs | 56 | 11% | [Nobi Pipeline Fixer](https://gitlab.com/explore/ai-catalog/flows/1007275/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34668653)) |
| Incident root cause and post-mortems | 56 | 11% | [Autopsy MR Analyst](https://gitlab.com/explore/ai-catalog/agents/1006916/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/28872610)), [Incident Replay](https://gitlab.com/explore/ai-catalog/flows/1004957/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/832180)) |
| Secrets detection | 48 | 9% | |
| Docs, changelogs and release notes | 48 | 9% | |
| Merge request risk scores | 28 | 6% | [MR Risk Triage](https://gitlab.com/explore/ai-catalog/agents/1003272/) (11 catalog items share this name) |
| Release readiness gates and deploy confidence | 24 | 5% | [Release Gate Assessor](https://gitlab.com/explore/ai-catalog/agents/1004637/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35161620)) |
| Blast radius | 22 | 4% | |
| Rollback, canary and feature flags | 14 | 3% | [ZeroTouch Monitor](https://gitlab.com/explore/ai-catalog/agents/1006475/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35460382)): "Production monitoring + auto-rollback protection" |
| Onboarding and codebase questions | 14 | 3% | |
| Smoke tests, health checks, post-deploy checks | 5 | 1% | [Smoke Tester](https://gitlab.com/explore/ai-catalog/agents/1005966/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572)) |
| Database migration safety | 5 | 1% | [DB Migration Safety Checker](https://gitlab.com/explore/ai-catalog/agents/1005786/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35297484)) |
| Accessibility after deploy | 5 | 1% | |
| User feedback into issues | 4 | 1% | |
| Release tagging and semantic versioning | a handful | about 1% | [Release Tagger](https://gitlab.com/explore/ai-catalog/agents/1004428/) ([project](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34573566)) |
| On-call alerts and paging | 2 | 0.4% | |

Feb to Mar winners, for context: LORE (Grand Prize, team memory from merge requests), Gitdefender (Google Cloud prize) and GraphDev (Anthropic prize, code graph plus merge request ripple analysis) ([gitlab-ai-hackathon-2026-part1.md](research/winners/gitlab-ai-hackathon-2026-part1.md)). Correction to the code-host note: it cited a search summary calling Gitdefender a security fixer ([Feb winners post](https://about.gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners/), unverified). The winners note read the repo: Gitdefender scores merge requests for AI-generated "slop" and a human approves each step. "This does not match the repo." So there is no evidence that security auto-fix won in February.

### 2025 ("AI in Action" with Google Cloud)

Only the title of [GitLab's Aug 5, 2025 post](https://about.gitlab.com/blog/ai-in-action-hackathon-celebrating-the-gitlab-innovations/) was seen. No crowding data.

### What pushes October entrants into the same spaces

- The official autonomy examples describe the crowded ideas almost word for word (Devpost, search excerpts, unverified, see [RULES.md](RULES.md)). Supervised: "You push code. Agents handle code review, fix a failing pipeline, remediate a security finding, and deploy to staging. You get a summary and approve the production deployment." Hands-off: "You create an issue. Agents review it, create 1+ MRs, run security scans, fix what they find, merge when everything passes, deploy to staging, validate, promote to production, and post a summary on the original issue. You touched nothing."
- GitLab's internal theme: "Hands Off. How far can your agents go without you?" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)).
- The Most Stages Covered prize, one per path ("touching the stage counts") ([RULES.md](RULES.md), unverified).
- The judges' reference project already runs the full loop ([hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase)).
- GitLab offers each entrant an observability instance: "Monitoring and incident response are part of life after code, so your subgroup can have its own observability instance." ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md), [observability docs](https://docs.gitlab.com/operations/observability/observability/)). Expect many monitoring and incident entries (inference).
- The hackathon card: "Build agentic workflows on GitLab that automate any part of the software development lifecycle after the code is written, from review and testing through to deployment, monitoring, and incident response." ([TranscendHackathonPage.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/TranscendHackathonPage.vue)).
- GitLab on X: "Your coding agents just got faster. Did your reviews, security, and release cycles keep up?" ([x.com/gitlab](https://x.com/gitlab/status/2098488335140372729), search-result title, unverified). Devpost on X lists "review, security, testing, deployment, monitoring" ([x.com/devpost](https://x.com/devpost/status/2104984062469308626), unverified).
- Not all of GitLab's framing points to hands-off. The June event line was "speed with control across the entire software lifecycle" ([press release](https://about.gitlab.com/press/releases/2026-06-04-gitlab-to-host-gitlab-transcend-global-virtual-event-on-agentic-engineering/), search excerpt, unverified), and the Bangalore event asks "which workflows change, which controls hold, and how to measure success with agentic engineering" ([event page](https://about.gitlab.com/events/transcend/india/), search excerpt, unverified). Entries about human control are rarer in the field so far (section 6).

## 5. Crowded idea spaces to avoid (ranked)

Ranked by risk for October. The October field counts most (same theme), then Feb to Mar (same platform), then June (same Devpost page and organizers). "Excluded" means we will not build it.

| Rank | Idea space | Evidence count | Examples | Verdict |
|---|---|---|---|---|
| 1 | **Post-merge release gatekeeper:** an agent walks a merged change through scans, tests, deploy and a health check, then ships, holds or rolls back | October: 4 of 7 known ideas (5 of 7 counting NEXUS). The judges' reference runs this loop. Devpost's Hands-off example describes it (unverified). Feb to Mar: 24 release-readiness projects. June: DeployGuard. | Receipted Pipeline, AfterMerge, BABYDOV Release Sentinel, @williamleewilliam1-star's release agent; [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase); [Release Gate Assessor](https://gitlab.com/explore/ai-catalog/agents/1004637/); [ZeroTouch Monitor](https://gitlab.com/explore/ai-catalog/agents/1006475/) | **Excluded** |
| 2 | Security review and auto-fix on merge requests (SAST triage, fix MRs, secrets, CVE reachability) | Feb to Mar: 132 security review, 82 remediation fixes, 48 secrets (of 506). June: 10 READMEs. October: 1 main idea, and a stage in 4 more. Devpost examples: "remediate a security finding", "run security scans, fix what they find" (unverified). | A2A Omega HVFR, [ReachGate](https://gitlab.com/gitlab-ai-hackathon/transcend/39037247), [peerivo/reviewer](https://gitlab.com/peerivo/reviewer) (commercial) | Avoid |
| 3 | Pre-merge impact review and code review (blast radius, "what could this break", merge request risk scores) | June: 69 by GitLab's count; about 55 of 146 READMEs by our sort; "blast radius" in 76 of 148. Feb to Mar: 95 code review, 28 merge request risk, 22 blast radius. October: 0 entries, but "blast radius" matched 3 new GitLab projects and "change risk" 2 (not entries). | [Ripple](https://gitlab.com/gitlab-ai-hackathon/transcend/669256), [Tremor](https://gitlab.com/gitlab-ai-hackathon/transcend/39301572), [MR Risk Triage](https://gitlab.com/explore/ai-catalog/agents/1003272/), [Codegenome](https://gitlab.com/Qivoxe/Codegenome) (not an entry) | Avoid |
| 4 | **CI failure fixers** (diagnose a failed pipeline, open a fix MR) | Feb to Mar: 56. June: 4 READMEs on CI failure and tests. Devpost Supervised example: "fix a failing pipeline" (unverified). October: 0 entries; 2 new CI analysis tools on gitlab.com without a hackathon link. | [Nobi Pipeline Fixer](https://gitlab.com/explore/ai-catalog/flows/1007275/), [Pipeline Pathologist](https://gitlab.com/gitlab-ai-hackathon/transcend/39033288), [pipeline-doctor](https://gitlab.com/rodripn91/pipeline-doctor), [gitlab-pipeline-profiler](https://gitlab.com/DiogoRibeiro7/gitlab-pipeline-profiler) | **Excluded** |
| 5 | **Generic incident chatbots**, incident root cause and post-mortems | Feb to Mar: 56. June: about 10 READMEs. October: NEXUS's demo is a staging 503 root cause; "incident" matched 19 new GitLab projects (not entries). GitLab offers every entrant an observability instance. | [Praetor](https://gitlab.com/gitlab-ai-hackathon/transcend/28344226), [Backtrace](https://gitlab.com/gitlab-ai-hackathon/transcend/7963149), [AFTERMATH](https://gitlab.com/gitlab-ai-hackathon/transcend/35450945), [Autopsy MR Analyst](https://gitlab.com/explore/ai-catalog/agents/1006916/), [Incident Replay](https://gitlab.com/explore/ai-catalog/flows/1004957/) | **Excluded** |
| 6 | Evidence receipts, tamper-evident ledgers and attestation of agent actions | October: 3 of 7 (Receipted Pipeline, BABYDOV, NEXUS). Not measured in earlier editions. | AER-1 receipts, SHA-256 ledgers | Avoid as the lead |
| 7 | "All nine stages" multi-agent meshes | October: 3 of 7 (NEXUS 10 agents, Receipted Pipeline 5 stage agents, A2A Omega 3 agents). The reference README already claims all nine stages ([RULES.md](RULES.md)). | | Avoid as the pitch |
| 8 | Carbon or energy footprint as the main product | Feb to Mar: 73. October: NEXUS's "Green SCI Model Router" as one part. October has an opt-in Most Environmentally Impactful prize (unverified), which will pull more in. | [GreenOps](https://gitlab.com/explore/ai-catalog/agents/1003840/), [Carbon-Aware Deployment Agent](https://gitlab.com/explore/ai-catalog/agents/1006976/) | Avoid as the main idea |
| 9 | **Release-notes generators**, changelogs and docs | Feb to Mar: 48. GitLab's demo account ships a release-notes sample flow. AfterMerge has a release-notes step. "changelog" matched 11 new GitLab projects, "release notes" 1 (not entries). | [custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo) | **Excluded** |
| 10 | Issue triage and planning | Feb to Mar: 81. GitLab's demo account ships an issue-triage sample flow. It happens before code, so it is off theme. | [custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo) | Avoid |
| 11 | Onboarding aids and codebase questions | June: 36 by GitLab's count, 17 READMEs by our sort. Feb to Mar: 14. Off theme for October. | | Avoid |
| 12 | **Dashboards as the main idea** | Not measured in earlier editions. October: 2 of the 4 built entries lead with a screen (AfterMerge's simulated console, BABYDOV's Pages dashboard), and neither shows Duo use. Judging asks for "a complete, coherent workflow rather than a proof of concept" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)). | | **Excluded** |
| 13 | **Post-merge proof in production that a fix worked** | October: Proof of Fix (plan), plus checks inside BABYDOV, Receipted Pipeline and AfterMerge. June: Stayed Shipped won second in Technological Implementation. Feb to Mar: 5 post-deploy check projects. | Section 3 | **Excluded** (named rival) |
| 14 | GitLab's own stock flows: coding-standards review, learning from human review feedback | GitLab's demo account sample flows; GitLab's internal "Review instructions learner" flow | [custom-agent-demo](https://gitlab.com/gl-demo-premium-mushijima/custom-agent-demo), [Review instructions learner](https://gitlab.com/explore/ai-catalog/flows/1016015/) | Avoid |

## 6. Open spaces (nobody seems to be in them yet)

The October sample is small (7 ideas on day 2). Few matches can also mean an idea is hard to demo, so treat each row as a lead, not a finding. October counts are the 7 known ideas plus new GitLab projects matched by keyword (none of which were entries).

| Space | October | Feb to Mar (of 506) | June | Caveat |
|---|---|---|---|---|
| On-call alert handling and the human handoff at night (paging, runbook steps, what the agent may do alone at 3 a.m., the morning handoff) | none seen; "on-call" matched 6 and "runbook" 8 new GitLab projects since about Sep 27, none entries | 2 | 0 catalog items | Incident root cause next door is crowded (Feb to Mar 56, June about 10, NEXUS). Open only if the core is the human handoff, not root-cause chat. |
| User feedback and support tickets flowing back into issues after release | none seen ([Heard](https://gitlab.com/ipylypenko/Heard-Product-Feedback-App), a customer-feedback agent on gitlab.com, is not an entry) | 4 | 2 catalog items (loose keyword matches) | Issue triage is crowded (81) and sits before code; the after-release loop is the open part. |
| Feature flags and progressive rollout (the configure stage) | no one leads with it; BABYDOV does canary and rollback rehearsal; of the agent ideas, only NEXUS claims the configure stage | 14 (rollback, canary and feature flags together) | 3 catalog projects | Rollback and canary overlap the excluded gatekeeper space. |
| Database migration safety | none seen | 5 | 0 catalog items | Two June winners (Carver, Marshal) were about code migrations, so "migration" may feel familiar to judges (inference). |
| Package and registry hygiene (the package stage) | only BABYDOV's SBOM step; "SBOM" matched 1 new GitLab project | not measured | not measured | Thin evidence either way. |
| Compliance evidence for auditors | NEXUS lists a compliance agent; "compliance" matched 14 new GitLab projects, none entries | not measured | 4 READMEs (compliance and access) | Overlaps evidence receipts (3 of 7 October ideas). |
| Accessibility checks after deploy | none seen | 5 | 1 catalog project | |
| Flaky-test handling | none seen; "flaky" matched 1 new GitLab project, not an entry | inside CI failure (56) | inside CI failure and test tools (4); CrossCut won with test selection | Close to CI fixers (excluded). |
| Dependency upgrade flows | none seen as a main idea | overlaps the 82 remediation-fix projects (inference) | not measured | Close to security auto-fix (crowded). |
| Release tagging and semantic versioning | none seen | a handful (Release Tagger) | 0 | Small, and close to release notes (excluded). |
| Path A with a human gate | 1 of 7 (AfterMerge, simulated, no Duo found); 3 of 7 say Path B hands-off | n/a | The June Design and Usability winner kept a human merge gate ([gitlab_guide_and_reference.md](research/gitlab_guide_and_reference.md)) | Autonomy levels are separate prizes per path (unverified), so the Path A Assisted and Supervised prizes look thinly contested so far (inference). |

Not open, despite looking thin in October: proof in production that a fix worked (Proof of Fix and Stayed Shipped, section 3), and carbon or cost as the main product (73 carbon projects in Feb to Mar; [COGS Sentinel](https://gitlab.com/gitlab-ai-hackathon/transcend/39430932) did pre-merge cost in June).

**Stages the October field barely touches.** My mapping of the 7 ideas to the nine Devpost stages (rough, from the table in section 2):

| Stage | Ideas that touch it (of 7) |
|---|---|
| release | 6: Receipted Pipeline, AfterMerge, BABYDOV, NEXUS, Proof of Fix, @williamleewilliam1-star |
| verify | 5: Receipted Pipeline, AfterMerge, BABYDOV, A2A Omega, NEXUS |
| secure | 5: Receipted Pipeline, AfterMerge, BABYDOV, A2A Omega, NEXUS |
| monitor | 4: Receipted Pipeline, BABYDOV, NEXUS, Proof of Fix |
| govern | 4: AfterMerge, BABYDOV, A2A Omega, NEXUS |
| plan | 2: Proof of Fix (reopens the issue), NEXUS (claim) |
| create | 2: Receipted Pipeline (review), NEXUS (claim) |
| package | 2: BABYDOV (SBOM), NEXUS (claim) |
| configure | 1: NEXUS (claim only) |

Configure and package are the least touched stages, and plan and create are touched mostly by claims.

## 7. Watch list

What to re-check before submission. Any Claude Code session can run the GitLab and GitHub checks (no token needed). Devpost and Discord are blocked in the cloud session, so Alex checks those in a normal browser. Update sections 2, 5 and 6 of this file after each check.

| What | Why | How | When |
|---|---|---|---|
| October group projects | GitLab provisions one public `showcase` project per approved entrant here. It is the most direct view of the field. | Count with the command below, then open each new project: a fresh workspace has only the default README, so any other file means work has started. Look for `.gitlab/duo/`, `flows/`, `agents/`, `skills/`, `AGENTS.md` and the README's first paragraph. | Daily while building; last look Oct 26 |
| October subgroups | Each subgroup description names the entrant and their Devpost username | [subgroups API](https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/subgroups?per_page=100), read `x-total` and the descriptions | With the above |
| Devpost project gallery | Where submissions show | Alex opens [the gallery](https://gitlab-transcend.devpost.com/project-gallery) logged in, reads every title and tagline, and adds new ones to section 2. Whether it shows entries before the deadline is not known (unverified). | Every few days once it shows entries, and Oct 26 |
| Devpost updates, discussions, participants | Team-formation posts and official changes | [updates](https://gitlab-transcend.devpost.com/updates), [discussions](https://gitlab-transcend.devpost.com/forum_topics), [participants](https://gitlab-transcend.devpost.com/participants), in a browser; updates also arrive by email once registered | Weekly |
| Keynote and Build Session | Ideas shown on stage become crowded ideas (inference) | Keynote video [GitLab Transcend, October 6, 2026](https://www.youtube.com/watch?v=lw98rbIUdz0) (title from search results, unverified); Build Session with Missy Davies and Dennis Meister, Oct 9, 10am ET (unverified) | Oct 6 and Oct 9 |
| Proof of Fix | The named idea we must avoid | Comments and ticks on [issue #18](https://github.com/JannetEkka/DSProjects/issues/18); a new repo on [JannetEkka's repos](https://github.com/JannetEkka?tab=repositories) | Weekly |
| The four built rivals | Whether they add Duo flows or change direction | [Receipted Pipeline](https://gitlab.com/rambozambodotdev/receipted-pipeline) (is the flow registered?), [AfterMerge](https://gitlab.com/sam1054/aftermerge) (Duo added?), [BABYDOV](https://gitlab.com/babydov-life-after-code/babydov-release-sentinel) (model added?), [A2A Omega](https://github.com/jamesparser/a2a-omega-hvfr) (GitLab copy?) | Weekly |
| GitHub | Entrants who build or plan on GitHub | WebFetch of [repos: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=repositories&s=updated&o=desc), [issues: "gitlab-transcend.devpost.com"](https://github.com/search?q=%22gitlab-transcend.devpost.com%22&type=issues&s=created&o=desc), [issues: "Life After Code"](https://github.com/search?q=%22Life+After+Code%22&type=issues&s=created&o=desc) | Weekly |
| GitLab project search | Entrants who build outside the group | The searches in 1.4, for example [transcend](https://gitlab.com/api/v4/projects?search=transcend&order_by=created_at&sort=desc), adding `&id_after=86990000` to keep only new projects | Weekly |
| Onboarding requests | People write what they plan to build in the "Reason:" line | [onboarding issues API](https://gitlab.com/api/v4/projects/60607268/issues?created_after=2026-09-25T00:00:00Z&per_page=100) | Weekly |
| AI Catalog | Flows and agents that entrants publish | [agents](https://gitlab.com/explore/ai-catalog/agents/) in a browser, or the public GraphQL API as in the social pass | Weekly |
| Discord `#transcend-hackathon` | Questions and ideas in the open | [discord.gg/gitlab](https://discord.gg/gitlab), in a browser | Weekly |
| Our own repo | Rivals can read our ideas | [alejandro-publius/life-after-code](https://github.com/alejandro-publius/life-after-code) is public and the first GitHub result for "Life After Code". Consider making it private until submission, or keep idea docs out of it. | Now |

Commands for the October group (public API, no token):

```sh
# Count projects (read the x-total line)
curl -sS -D - -o /dev/null "https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true&per_page=100" | grep -i '^x-total'

# List them, newest first (add &page=2 and so on when x-total-pages is above 1)
curl -sS "https://gitlab.com/api/v4/groups/gitlab-ai-hackathon%2Ftranscend-october-2026/projects?include_subgroups=true&per_page=100&order_by=created_at&sort=desc" | python3 -I -c 'import json,sys; [print(p["id"], p["path_with_namespace"], p["last_activity_at"]) for p in json.load(sys.stdin)]'

# Files in one project (replace ID)
curl -sS "https://gitlab.com/api/v4/projects/ID/repository/tree?recursive=true&per_page=100"
```

Plan the last field check before recording the video (Oct 24 to 26), so the video and write-up can name how our entry differs. The deadline is 2026-10-27 at 13:00 UTC per a Devpost excerpt (unverified) or 14:00 UTC per GitLab's source ([transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts)). GitLab calls the Devpost rules "the binding source" ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md)), so plan on the earlier time.
