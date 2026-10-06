# Status

Last updated: 2026-10-06, about 04:30 UTC (session 1).

## Progress

| Part | File | State |
|---|---|---|
| Rules | docs/RULES.md | done; Codex checked the official pages directly ([RULES_CHECK.md](codex/RULES_CHECK.md)) |
| 1. Past winners | docs/PAST_WINNERS.md | done: 102 winners across 15 events |
| 2. Patterns | docs/PATTERNS.md | done: counts, anti-patterns, ten rules |
| 3. Current field | docs/FIELD.md | done |
| 4. Sponsors | docs/SPONSORS.md | done |
| 5. Ideas | docs/IDEAS.md | done: 74 concepts, 57 scored, five briefs, Night Orders chosen |
| 6. Build and plan | code, CI, docs/PLAN.md | first complete workflow done offline: decision code, dusk drafter, demo night, relay service, demo shop, morning countersign, three Duo flows, CI (218 tests). Codex's keyless deploy merged; the CLI audit passes in the pinned image. |
| Finish | docs/MORNING.md | done |

## What has not run yet

- Nothing has run on GitLab.com or Google Cloud. The GitLab workspace and the Google project need Alex (steps in [MORNING.md](MORNING.md)).
- The dusk drafter has only run on its recorded answer (no API key in this session).
- The day-one test of the night start ([PLAN.md](PLAN.md), decision D1) is the next real milestone.

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
