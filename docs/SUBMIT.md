# Submit

The runbook from today to a submitted entry, for Alex. Written Sun 11 Oct 2026. Deadline: **Tue 27 Oct, 13:00 UTC (6:00 AM Pacific)**. Our target: **Mon 26 Oct, 9:00 PM Pacific** ([PLAN.md](PLAN.md)).

Only Alex can do four things: create the GitLab token, create the Google Cloud project, film the video, and press Submit on Devpost (it needs his login, and Devpost cannot be reached from the build environment). Everything else is ready or runs from code once the token exists.

## What the rules require, and where each stands

| Required ([rules](https://gitlab-transcend.devpost.com/rules), quoted in [RULES_CHECK.md](codex/RULES_CHECK.md)) | State today | What makes it true |
|---|---|---|
| Public GitLab repository with the MIT licence visible in About | The code is on GitHub only | The token; then Claude Code pushes and checks the licence (day-one `publish` step) |
| CI/CD pipeline history visible and showing the automation running | `.gitlab-ci.yml` ready and pinned; the same checks pass on GitHub | The first push to GitLab runs it |
| The project uses the GitLab Duo Agent Platform (pass or fail) | Three flows (dusk, watch, dawn) and a probe flow written and validated against GitLab's schema; Duo Code Review rules in `.gitlab/duo/`; none has run | Flows enabled in the project, then the day-one `flow` step and one test night |
| An English text description | Final draft in [DEVPOST.md](DEVPOST.md) | Replace the pending links |
| A public YouTube video under 3:00 | Two scripts in [VIDEO.md](VIDEO.md), paced and checked | Filming, after a test night (Plan A) or from the browser demo (Plan B) |
| Explain what was added during the submission period | Everything here was made on or after 5 Oct; the git history shows it | One paragraph, below |
| Optional: Google Cloud bonus, up to 0.2 | Deploy code ready in `deploy/` | The Google Cloud project, then the deploy jobs |

Live progress is tracked gate by gate in [LIVE_GATES.md](LIVE_GATES.md).

## The order of things

| When | Who | Step | Done when |
|---|---|---|---|
| As soon as possible, 15 min on a phone | Alex | Create the GitLab token and add it to the Claude Code environment as `GITLAB_TOKEN` ([MORNING.md](MORNING.md), step 2). Send the workspace link or the GitLab username. | A new session can read the project |
| Same day | Claude Code | Push to GitLab, run `scripts/day_one.py`, create the flags and the watch issue, start the probe flow, rewrite [LIVE_GATES.md](LIVE_GATES.md) | The first pipeline is green on GitLab |
| Same day, 15 min on a laptop | Alex | Create and enable the four flows ([FLOWS_SETUP.md](FLOWS_SETUP.md)) if the API cannot | The `flow` gate passes |
| Within two days, 30 min in Cloud Shell | Alex | Google Cloud project, then `deploy/setup_gcp.sh` and the three deploy jobs ([deploy/README.md](../deploy/README.md)) | `/healthz` answers on Cloud Run |
| The first evening after deploy | Alex | Test night ([TEST_NIGHT.md](TEST_NIGHT.md)): merge the orders, sleep, countersign over coffee | The `night` and `morning` gates pass |
| By Wed 21 Oct | Both | Decision D3: film the real night (Plan A), or the browser demo with Standing Orders said plainly (Plan B) | A plan is chosen |
| By Sat 24 Oct, 1 hour | Alex | Film and upload to YouTube, Public. `python scripts/video_pace.py --plan A --srt captions.srt` writes captions to upload with it | The `video` gate passes |
| By Mon 26 Oct, 9 PM | Alex | Fill the Devpost form from the table below and press Submit | Devpost shows "Submitted" |
| Until about Mon 16 Nov | Both | Change nothing: not the repository, the video, the form or the live services. Keep building only on a fork ([rules FAQ](codex/RULES_CHECK.md#submission-changes-after-deadline)) | |

If the token never arrives, there is no valid entry: the rules require a public GitLab repository with visible pipeline history. The browser demo, the docs and the GitHub checks do not replace it.

## The Devpost form

| Field | Paste |
|---|---|
| Project name | Night Orders |
| Tagline | Before bed, sign what the agent may do alone tonight. Everything else wakes you. |
| About the project | The sections of [DEVPOST.md](DEVPOST.md) from "Inspiration" to "Potential impact and what comes next", with the pending links replaced |
| Built with | python, fastapi, gitlab-duo-agent-platform, gitlab-ci, gitlab-feature-flags, gitlab-pages, google-cloud-run, cloud-scheduler, ntfy, playwright |
| Try it out | The browser demo on GitLab Pages (the pipeline publishes it); the public GitLab repository; the relay's public URL (its `/demo` and `/`) once deployed |
| Video | The YouTube link |
| Image gallery | [docs/images/gallery/](images/gallery/), files 01 to 05, with the captions in [DEVPOST.md](DEVPOST.md#image-gallery) |
| Path | Path A: Start Fresh |
| Autonomy category | Supervised: "your agents run the workflow, you approve the outcome" ([DEVPOST.md](DEVPOST.md)) |
| Google Cloud bonus | Claim only with a public Cloud Run URL that answers, and the deploy pipeline visible |
| Environmentally Impactful prize | Do not opt in: nothing was measured with the SCI framework |

**What was added during the submission period** (paste where the form asks): Everything in this repository was created on or after 5 Oct 2026: the decision code and its tests, the relay, the demo shop, the three Duo Agent Platform flows (dusk, watch, dawn), a probe flow for the day-one test, the skill they follow, the Duo Code Review rules, the GitLab pipeline, the browser demo, the Cloud Run deployment code, and the documentation. The git history shows each change with its date.

## Before pressing Submit

- [ ] The GitLab repository is public, and its About section shows the MIT licence.
- [ ] The latest pipeline on the default branch is green and visible without logging in.
- [ ] Every "pending" in README.md and DEVPOST.md is replaced by a link, or still says pending honestly.
- [ ] The video is Public on YouTube, under 3:00 by the player's count, and plays from a logged-out browser.
- [ ] The demo labels are readable in the video: demo shop, planted faults, Priya is a demo persona.
- [ ] No token, ntfy topic or relay key appears in the video, the screenshots or the repository.
- [ ] [LIVE_GATES.md](LIVE_GATES.md) is regenerated and committed, and its links open.
- [ ] Submitted before Tue 27 Oct, 13:00 UTC.
