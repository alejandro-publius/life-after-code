# Status

Last updated: 2026-10-06, about 01:50 UTC (session 1).

## Progress

| Part | File | State |
|---|---|---|
| Rules | docs/RULES.md | done, with open questions (Devpost blocked) |
| 1. Past winners | docs/PAST_WINNERS.md | research notes in docs/research/winners/, write-up pending |
| 2. Patterns | docs/PATTERNS.md | pending |
| 3. Current field | docs/FIELD.md | notes in docs/research/field/, write-up pending |
| 4. Sponsors | docs/SPONSORS.md | notes in progress in docs/research/sponsors/ |
| 5. Ideas | docs/IDEAS.md | not started |
| 6. Build and plan | code, docs/PLAN.md | not started (Codex is building deploy/ on branch codex/deploy-skeleton) |
| Finish | docs/MORNING.md | not started |

## Blocked websites

The cloud session's network policy blocks these hosts. Each was tried and refused by the egress proxy (HTTP 403 on CONNECT, or "EGRESS_BLOCKED" from WebFetch):

| Host | What we lost | Workaround used |
|---|---|---|
| devpost.com and every *.devpost.com page (gitlab-transcend, gitlab, run, googlecloudmultiagents and others) | The live rules, updates, discussions, gallery, participants and every winner page | Search engine excerpts (tagged as such), GitLab's own guide source on gitlab.com, project repos |
| about.gitlab.com (blog, stages page, events) | GitLab's winner announcements and the DevSecOps stages page | Search excerpts; GitLab's www repo data files on gitlab.com |
| docs.gitlab.com | GitLab documentation site | The same docs read from source: gitlab.com/gitlab-org/gitlab/-/raw/master/doc/... |
| contributors.gitlab.com | GitLab's hackathon pages and registration API | The page source on gitlab.com (contributors-gitlab-com repo) |
| forum.gitlab.com | GitLab forum | none |
| web.archive.org | Archived copies of blocked pages | none |
| youtube.com | Demo videos of past winners (length, content) | Video titles and descriptions from search excerpts only |
| x.com, linkedin.com, medium.com, dev.to, discord | Social posts by entrants and winners | Search excerpts |
| developers.googleblog.com, discuss.google.dev | Some Google announcements | cloud.google.com blog where possible |
| html.duckduckgo.com, www.bing.com | Fallback search | none |
| github.com and api.github.com through curl | Raw API access | WebFetch on github.com pages works |

Also: the session's web search tool has a cap of 200 searches. It was used up by about 01:40 UTC, so later research relied on fetching known pages directly. Items that needed more searching are marked "(unverified)" in the docs.

Third-party mirrors of blocked pages appeared in search results. They were not used, because that would route around the block.

## Environment notes

- No `ANTHROPIC_API_KEY` in this cloud session, so the agent cannot make live Claude calls here. Code is tested with recorded, clearly labelled fixtures.
- No GitLab token in this session. Nothing is pushed to GitLab from here.
- This GitHub repo is public. Anyone can read the idea notes before the deadline (it is the top GitHub result for "Life After Code").
