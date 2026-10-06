# Status

Last updated: **5 Oct 2026 (Pacific Time)**.

## Current result

One chosen improvement is ready locally: a guided Night Orders browser demo at `/demo`. It brings the existing decision core into a readable Before bed, During the night and Over coffee story, with two human choices, old and new checkout charts and inspectable evidence. It addresses **Design and Presentation, each 20%** under the [official judging criteria](https://gitlab-transcend.devpost.com/rules). See the [judge guide](GUIDE.md) and [review record](codex/JUDGE_REVIEW.md).

The demo uses a simulated shop, planted faults and recorded model replies. Signing and approval select isolated fixture inputs; they do not merge real orders, push code or send phone notifications. The default path reports 1 wake-up, 1 incident handled automatically and 1 approved action. These are actual counts from the invented night, not production impact measurements.

**Public live demo URL: pending.** No GitLab or Google Cloud integration is configured for this run. Nothing has run on GitLab.com or Google Cloud, and no live model execution has been demonstrated. The browser improvement is published to GitHub main at `a164dd4`. Remote CI is pending verification.

## Verified locally

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

## CI and integration proof still pending

- The [GitHub Actions checks workflow](../.github/workflows/checks.yml) is published on main but not yet verified green. Local passes do not establish a remote CI result.
- The [GitLab pipeline configuration](../.gitlab-ci.yml) is present. Visible GitLab pipeline history showing automation running is still pending.
- The three [Duo flow files](../flows/) are defined and validated against the checked-in schema and tool list. That is configuration validation, not proof of live Duo execution. The actual night start in [Plan, decision D1](PLAN.md) remains the next integration milestone.
- [Google Cloud deployment code](../deploy/README.md) is present and locally checked. A real deployment and public live URL are pending. No Google Cloud bonus is claimed.
- The [Devpost draft](DEVPOST.md) and [filmable browser video script](VIDEO.md) are ready. Public GitLab and YouTube links remain pending. Path A is planned; Supervised is the tentative autonomy recommendation.
- Account and configuration steps for Alex are in [Morning](MORNING.md). Required live GitLab Duo Agent Platform use remains an eligibility requirement under the [official rules](https://gitlab-transcend.devpost.com/rules).

## Progress

| Part | File | State |
|---|---|---|
| Rules | [RULES.md](RULES.md) | Research retained; later primary-source wording in [RULES_CHECK.md](codex/RULES_CHECK.md) controls where the early notes differ. |
| 1. Past winners | [PAST_WINNERS.md](PAST_WINNERS.md) | Research retained: 102 winners across 15 events. |
| 2. Patterns | [PATTERNS.md](PATTERNS.md) | Counts, anti-patterns and ten project rules retained. |
| 3. Current field | [FIELD.md](FIELD.md) | Dated field research retained; it is not a claim about every current competitor. |
| 4. Sponsors | [SPONSORS.md](SPONSORS.md) | Sponsor research retained. |
| 5. Ideas | [IDEAS.md](IDEAS.md) | 74 concepts, 57 scored and five briefs; Night Orders chosen. |
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
