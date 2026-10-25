# Status

Last updated: **11 Oct 2026, about 20:30 UTC** (No Mouse fix bench in preparation).

## Current state

| Item | State |
|---|---|
| Concept | **Undecided.** The concept review (PR #1) recommended No Mouse and has no Codex verdict yet. The pre-registered No Mouse bench (PR #2) **failed its first criterion**: deciding the route needs no model. Since then code refuses controls whose spoken name contradicts their visible label, and in a labelled post-hoc rerun the no-model search chose the right route on all 15 held-out variants. The open question for option A in [IDEAS.md, section 0.5](IDEAS.md#05-feasibility-result-11-oct-2026) is whether the model repairs barriers better than rules: the fix bench and F0, a rule fixer, are built; the [pre-registration](research/nomouse_fix_bench.md) is under a bias review before it is frozen and a blind barrier set is written. |
| Prize emphasis | Path A, Best Supervised Agent; Most Creative as the special prize, if the concept holds. Not Most Stages Covered or the environmental prize. |
| Latest reviewed source | GitHub main at `484c41154a2742666483a53c715121685eb7dac0`. Unreviewed: `claude/concept-review` (PR #1) and `claude/nomouse-feasibility` (PR #2, stacked on it). |
| Works locally | No Mouse: the labelled demo shop, the keyboard walker reading Chromium's accessibility tree (now also the visible label of each control), journey replay with guards, B1 and B2, the stand-in model adapter, F0, fixes on temporary copies, and both benches ([nomouse/README.md](../nomouse/README.md)). Night Orders: unchanged from 5 Oct (see below). Tests on 11 Oct: 546 passed with the walker extra; 509 passed and 37 browser tests skipped without it. |
| Simulated | The shop, persona and every variant are demo data. The screen reader is simulated from Chromium's accessibility tree. Bench model answers come from a stand-in (Claude Sonnet 4.6 via `claude -p`), not from GitLab Duo. The Night Orders replay's inputs are recorded fixtures. |
| Live integrations verified | **None.** Nothing has run on GitLab.com or Google Cloud, and no Duo flow has run. |
| CI evidence | [GitHub Checks run 38162722824](https://github.com/alejandro-publius/life-after-code/actions/runs/38162722824) passed all three jobs on `835389158fa6e5d0ed752eb8a4fac9ed2d21ddd4` (the frozen harness), including the 13 No Mouse browser tests in Chromium on Linux. This is GitHub CI, not GitLab pipeline history. |
| Current blocker | The concept decision after the bench, and whether the hackathon role can create and enable a custom Duo flow (still untested; every concept depends on it). |
| Next highest-value task | Codex and Alex choose an option in [IDEAS.md, section 0.5](IDEAS.md#05-feasibility-result-11-oct-2026). Alex requests the hackathon workspace if not done; the one-flow live probe runs within 48 hours of access. |

The sections below describe the Night Orders work on main as of 5 Oct.

## Night Orders result on main (5 Oct)

One chosen improvement is published on main: a guided Night Orders browser demo at `/demo`. It brings the existing decision core into a readable Before bed, During the night and Over coffee story, with two human choices, old and new checkout charts and inspectable evidence. See the [judge guide](GUIDE.md) and [review record](codex/JUDGE_REVIEW.md).

The demo uses a simulated shop, planted faults and recorded model replies. Signing and approval select isolated fixture inputs; they do not merge real orders, push code or send phone notifications. The default path reports 1 wake-up, 1 incident handled automatically and 1 approved action. These are actual counts from the invented night, not production impact measurements. A code audit on 6 Oct confirmed ten known concerns in this implementation ([DECISIONS.md](DECISIONS.md)).

## Verified locally (5 Oct)

| Check | Result |
|---|---|
| Application and decision suite, `uv run --locked pytest -q` | 256 passed. One upstream Starlette deprecation warning. |
| Deployment unittest suite | 16 discovered: 15 passed, 1 skipped because local gcloud is absent. |
| Separate pinned Google Cloud SDK Docker audit | 2 passed, including the gcloud help check skipped locally. This validates command flags, not a cloud deployment. |
| Browser through actual local HTTP | Signed and approved, signed and declined, and unsigned paths passed at phone width 390 and laptop width 1440. Keyboard and focus behavior, no horizontal overflow, 44px tap targets, retry and no-JavaScript fallback passed. |
| Relay Docker demo | The non-root container served the demo offline. No credentials or production integration were needed. |
| Screenshots | Six screenshots captured from the local application, covering before bed, checkout and morning at both widths. |

| Local demo screenshots | Phone | Laptop |
|---|---|---|
| Before bed | [Phone](images/demo-phone-dusk.png) | [Laptop](images/demo-laptop-dusk.png) |
| Checkout decision | [Phone](images/demo-phone.png) | [Laptop](images/demo-laptop.png) |
| Morning brief | [Phone](images/demo-phone-morning.png) | [Laptop](images/demo-laptop-morning.png) |

## CI and pending integration proof

- The [GitHub Actions checks workflow](../.github/workflows/checks.yml) passed all three hosted jobs on `0812bc938fb06835a12f166a26e2ddb48da9e640` at 22:31 PDT on October 5. [Verified run](https://github.com/alejandro-publius/life-after-code/actions/runs/37418744092). It runs checks only and does not deploy. The hosted deployment suite also ran all 16 tests without the local SDK skip.
- The [GitLab pipeline configuration](../.gitlab-ci.yml) is present. Visible GitLab pipeline history showing automation running is still pending.
- The three [Duo flow files](../flows/) are defined and validated against the checked-in schema and tool list. That is configuration validation, not proof of live Duo execution. The actual night start in [Plan, decision D1](PLAN.md) remains the next integration milestone.
- [Google Cloud deployment code](../deploy/README.md) is present and locally checked. A real deployment and public live URL are pending. No Google Cloud bonus is claimed.
- The [Devpost draft](DEVPOST.md) and [filmable browser video script](VIDEO.md) are ready. Public GitLab and YouTube links remain pending. Path A is planned; Supervised is the tentative autonomy recommendation.
- Account and configuration steps for Alex are in [Morning](MORNING.md). Required live GitLab Duo Agent Platform use remains an eligibility requirement under the [official rules](https://gitlab-transcend.devpost.com/rules).

## Progress

| Part | File | State |
|---|---|---|
| Rules | [RULES.md](RULES.md) | Research retained. Primary sources were read again on 6 Oct ([refresh note](research/refresh_2026-10-06.md)); that note and [RULES_CHECK.md](codex/RULES_CHECK.md) control where the early notes differ. |
| 1. Past winners | [PAST_WINNERS.md](PAST_WINNERS.md) | Research retained: 102 winners across 15 events. |
| 2. Patterns | [PATTERNS.md](PATTERNS.md) | Counts, anti-patterns and ten project rules retained. |
| 3. Current field | [FIELD.md](FIELD.md) | Dated field research retained; it is not a claim about every current competitor. |
| 4. Sponsors | [SPONSORS.md](SPONSORS.md) | Sponsor research retained. |
| 5. Ideas | [IDEAS.md](IDEAS.md) | 74 concepts, 57 scored and five briefs. Selection reopened on 6 Oct: section 0 holds the four-candidate review and the current recommendation. |
| 6. Build and plan | [PLAN.md](PLAN.md), code and pipeline files | Decision core, dusk drafter, replay, relay, demo shop, countersign and three Duo definitions available offline. Current verification is listed above. |
| Public materials | [README](../README.md), [GUIDE](GUIDE.md), [DEVPOST](DEVPOST.md), [VIDEO](VIDEO.md), [MORNING](MORNING.md) | Updated around the guided local demo and its limits. |

## Historical research access limits

The initial research session reported these network refusals (HTTP 403 on CONNECT or "EGRESS_BLOCKED" from WebFetch). This table records the limits of that earlier research, not the current environment's access policy. The official October Devpost pages were read successfully later, as documented in [RULES_CHECK.md](codex/RULES_CHECK.md) and [source-status.json](codex/source-status.json).

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

The initial session exhausted its reported 200-search budget by about 01:40 UTC on 6 Oct, which was still 5 Oct Pacific Time. Later research in that session relied on fetching known pages directly. Items that needed more searching remain marked "(unverified)" in the research docs.

Third-party mirrors of blocked pages appeared in search results. They were not used, because that would route around the block.

## Environment notes

- The browser demo runs with recorded, clearly labelled fixtures and requires no model key or external token.
- GitLab and Google Cloud configuration has not been supplied for the live integration. No GitLab push or cloud deployment is reported here.
- The GitHub repository is public. Its source and research are readable before the deadline; it does not replace the required public GitLab submission repository.
