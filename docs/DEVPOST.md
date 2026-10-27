# Devpost submission draft

English draft, updated **27 Oct 2026**. The form fields and the story below are pasted into Devpost as they are; [SUBMIT.md](SUBMIT.md) says in what order. Keep the status statements until real execution evidence replaces them.

## Submission fields

| Field | Draft value |
|---|---|
| Project name | Night Orders |
| Tagline | Before bed, sign what the agent may do alone tonight. Everything else wakes you. |
| Entrant | Alex Velazquez, solo |
| Path | Path A: Start Fresh |
| Autonomy category | Supervised: the agents run the night, she approves the bounds before bed and the outcome over coffee |
| Public GitLab repository | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase |
| Working project URL | https://showcase-700ee4.gitlab.io (the browser demo on GitLab Pages, published by the project's pipeline) |
| Public YouTube video | Alex to upload before submission |
| Built with | python, fastapi, gitlab-duo-agent-platform, gitlab-ci, gitlab-pages, gitlab-feature-flags, playwright |
| Google Cloud bonus | Not claimed: the Cloud Run deployment code is in the repository, but no project was deployed |

The [official rules](https://gitlab-transcend.devpost.com/rules) define Supervised as "your agents run the workflow, you approve the outcome". That is this project: nobody approves the 03:13 action itself; she approved its bounds at 22:06, and she approves what stays at 07:42.

## Image gallery

Upload in this order. Each is 1500 x 1000 (3:2), made by [scripts/gallery.py](../scripts/gallery.py) from components the browser captured from the running demo, and each carries the demo label.

| File | Caption for Devpost |
|---|---|
| [01-dusk.png](images/gallery/01-dusk.png) | Before bed, she signs at most three orders, each checked before she signs. |
| [02-decline.png](images/gallery/02-decline.png) | 01:52: code would have allowed order 1. The model declined, and woke her with one fix to approve. |
| [03-handled.png](images/gallery/03-handled.png) | 03:13: the signed order ran, the whole shop was re-checked, and her phone stayed dark. |
| [04-morning.png](images/gallery/04-morning.png) | 07:00: one quiet push, a countersign over coffee, and a kept change that ends when its fix ships. |
| [05-refusals.png](images/gallery/05-refusals.png) | 23 attempts against the real decision code, 0 production changes, and a control that acts. |

## Inspiration

At 03:12 the new checkout starts failing. Priya is on call for a small online shop, alone, with nobody behind her on the pager. The fix is obvious and reversible: turn the new checkout off. It still costs her the night, because nothing is allowed to do it without her.

Blanket permission for an agent to change production is too broad. Approving every incident keeps her awake. Night Orders asks a smaller question before bed: which exact actions may the agent take tonight, and under which conditions? Everything outside that signed boundary still needs her.

## What it does

**Permission for one night, signed by the person who gets woken.**

Before bed, the **dusk flow**, a custom GitLab Duo Agent Platform flow, reads the day's merged merge requests, deployments and feature flags, and drafts at most three orders as a merge request. Each order is one measured condition and one reversible action from a fixed menu: set a GitLab feature flag in one environment, or move a Cloud Run service's traffic to a named earlier revision. A change that cannot be undone safely, such as a database migration, gets no order, so it will wake her. Before she signs, code tries each flag order on staging and puts it back, checks that each traffic order's revision exists, and posts the result on the merge request; GitLab Duo Code Review reads the orders with the project's own rules. She signs by merging or approving.

At night the relay reads the shop's numbers every minute. When an alert fires, it opens a GitLab incident with an evidence pack and asks the **watch flow**, a second Duo flow. Code and the watch flow must both say yes. Code checks the signature, the expiry, the numbers on enough traffic, and first use tonight. The watch flow must name the signed order and say why the evidence fits, or decline. The action always comes from the signed file, never from the model's text or a log line. If a code check fails or the watch flow declines, she gets a three-line page and at most one fix she can approve with a thumbs-up. Ten minutes after any action, code re-checks the whole shop, not just the path it switched off.

At 07:00 the grant ends. Code posts the watch log and one quiet push. The **dawn flow** proposes what to keep in a countersign merge request; she merges it over coffee, and code puts every change she did not keep back exactly as it was, from the snapshot it took before acting. A kept change can name the merge request that fixes its cause, and once that fix is deployed, code ends the keep by itself. Every grant ends.

## How it uses GitLab, stage by stage

| Stage | In Night Orders |
|---|---|
| Plan | The standing watch issue: the day sheet at 21:00, the watch log at 07:00, the kept changes; an incident with a timeline per alert |
| Create | Tonight's orders and the morning countersign are merge requests written by Duo flows, read by Duo Code Review, guarded by code owners |
| Verify | The pipeline checks the orders and the countersign against the allowed targets, validates the flows, runs the tests, lint and a browser walk; flag orders are rehearsed on staging |
| Package | The relay and shop images are pushed to the project's container registry |
| Secure | SAST, IaC, secret, dependency and container scanning; an audited, hashed dependency list with an SBOM; model and log text never become an action |
| Release | Feature flags are the night's actions; the demo is published on GitLab Pages; each default-branch pipeline cuts a tagged release |
| Configure | Keyless Cloud Run deploys and Cloud Scheduler; the night's limits live as code in `ops/` |
| Monitor | The relay watches the shop every minute, opens incidents, and re-checks the whole shop after any action |
| Govern | Only the on-call person's merge or approval signs; orders expire at 07:00; nothing changed overnight is forgotten |

## What is new here

Automatic remediation is not new: rules that roll back or run a runbook when an alert fires exist in many tools. They are standing permissions, written once and kept until someone removes them. Agent pipelines that grade autonomy per change decide it at deploy time, from risk scores or tests. Night Orders decides it per night and per person, for the faults that show up hours after the deploy, when the person who would approve is asleep. The permission is nightly: drafted from that day's merges, checked before she signs, void at 07:00, and narrowed, never widened, by the agent. Each morning she decides what stays, and a kept change ends when its fix is deployed.

The watch flow's job is narrow. It never chooses an action; it decides whether tonight's incident is the one she signed for, and a decline is not a dead end: it wakes her with the one fix that fits. In the demo night at 01:52 the numbers matched order 1, so code would have allowed it, but the watch flow saw the old checkout failing as well, declined, and woke her with the fix that did help. At 03:13 the same order fit, and her phone stayed dark.

## The working demonstration

The browser demo is one guided night, on a phone or a laptop, at `/demo` or on GitLab Pages. Priya is a demo persona on call for Juniper Market, a simulated shop. Both faults are planted; the agent replies, signatures, reaction and morning merge are recorded demo data. The decisions, the chart samples, the counts and the evidence come from the same Watch code the relay runs.

The viewer chooses whether to sign the orders and whether to approve the fallback. On the signed and approved path the ledger records one wake-up, one incident handled while she slept and one approved action. Unsigned, the same faults wake her twice and nothing changes on its own. The same night three ways, computed by the same code:

| The same demo night | Wake-ups | Wake-ups with a fix to approve | Faults handled while she slept | Changes that did not help |
|---|---|---|---|---|
| Signed, the watch flow checks the reason (as designed) | 1 | 1 | 1 | 0 |
| Signed, standing orders: no model at night | 1 | 0 | 0 | 1 |
| Nothing signed | 2 | 0 | 0 | 0 |

These counts are evidence about an invented night, not measured production impact or hours of sleep saved.

## How it is built

Python decision code keeps permission checks apart from side effects. The FastAPI relay is designed for Cloud Run, called once a minute by Cloud Scheduler; that deployment has not run yet. Its GitLab integration implements feature flags, incidents and timeline events, merge request merges and approvals as signatures, thumbs-up reactions as approvals, the deployments API that ends a kept change, and the Duo workflows API that starts the watch and dawn flows. If that API will not start a flow on an account, a relay setting runs Standing Orders instead: no model at night, code alone, and it says so on every incident.

Every refusal is run, not described: [23 attempts](https://github.com/alejandro-publius/life-after-code/blob/main/docs/REFUSALS.md) against the real decision code (model replies, a planted log line, a teammate's merge or thumbs-up, the clock, thin traffic, a switched-off path that reads 0%, files people write), 0 production changes, and a control row that does act. A test keeps that page equal to the code's output.

The browser also exposes these results in **Check the permission boundary**. A judge can inspect each attempted action and the code's exact verdict, including a valid control that does act. The 24 results are computed from simulated inputs during replay or the static build; selecting a case reads the result without changing a service.

**What ran live on GitLab (27 Oct 2026), and what is still offline.** The public project passed all 18 jobs in [pipeline 2994232284](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2994232284) for installer sync `e551271`: 639 application tests with 94% coverage, lint, security scans, a dependency audit with an SBOM, phone and laptop browser checks, registry images, [GitLab Pages](https://showcase-700ee4.gitlab.io) deployment and a tagged release. The [27 Oct handoff](HANDOFF.md#what-is-live-on-gitlab-today-real-verifiable) records a real [watch session](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10120703) on demo [incident #3](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/issues/3): no signed orders, a declined action and one suggested fix that the relay's parser accepted.

All three custom flows are now installed and checked against their released definitions by a [repeatable setup command](FLOWS_SETUP.md); running it again made zero changes. The real [dusk session](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/automate/agent-sessions/10124688) read the repository, reviewed its draft and created [orders MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/merge_requests/1). With no merged change or deployment to justify an action, it drafted zero orders. Code validated the generated file and checked the one-file diff, lack of approvals and unmerged state. The flow did not set the requested draft flag, so Codex marked the MR Draft afterward; [the evidence records that adjustment](codex/FLOW_SETUP.md#live-dusk-execution).

The browser still replays an invented night with recorded model replies. No deployed relay has changed a feature flag, and dawn has not run live. The Pages deployment passed, but direct public playback remains unverified from this network-restricted environment. No production impact or full live night is claimed.

Source code and instructions: [README](../README.md), [decision core](../relay/nightorders/), [flow definitions](../flows/), [pipeline](../.gitlab-ci.yml), [deployment setup](../deploy/README.md) and [how another team adopts it](ADOPT.md).

## Challenges

The hard part is making permission precise. A metric can cross a threshold while the order is still the wrong fix for the incident, so Night Orders needs both a numerical check and a reasoned match. A switched-off checkout path reads 0% errors, so the re-check reads the whole shop. One failed checkout out of two is "50%", so an order never acts on thin traffic. Log text is evidence, never authority, and the action always comes from the signed file. GitLab runs a note line that starts with "/" as a quick action with the poster's token, so every piece of text the relay did not write itself is put on one line before it is posted.

Expiry and morning cleanup are separate decisions. Ending the grant at seven does not mean undoing a recovery while the bug is still present. The countersign keeps that distinction and can only keep changes that actually happened.

## Accomplishments and what we learned

The demo makes the boundary visible to someone who has never read the code: one unsigned branch, one necessary wake-up, one eligible automatic action and one morning account, all computed rather than drawn.

Independent reviews of the code found real defects, and each fix comes with a test that failed before it. A few of them: a page that failed once was never sent again; a drafted order value like `1`, a blank line and `/approve` would have put a GitLab quick action into a note the relay posts, approving as the on-call person; an approval given before a later push still signed the new commit; the countersign would have put a change back over a fix a person made after the night; and a change that timed out after reaching production left the morning nothing to restore.

The design lesson is that useful autonomy can be narrow. The agent investigates and can decline an order; code verifies the facts; a person grants and renews permission for consequential actions, every night.

## Potential impact and what comes next

The audience is a small team without a follow-the-sun rotation, where one person holds the pager. The demonstrated benefit is a way to handle a known reversible fault within prior permission while escalating a fault that does not fit. No customer trial, sleep improvement or sustainability gain has been measured.

Before submission: verify public Pages playback, upload the required video and attach its link. Live watch and dusk records and a passing GitLab pipeline already exist. After the hackathon: deploy the relay, run a real test night and morning countersign, then expand the action menu only when each action has apply, snapshot, restore and refusal checks. A later rotation can hand the orders over at shift change.

## Before submitting

- Open the linked public GitLab project and Pages demo; add Alex's uploaded video URL.
- Preserve the linked Duo session and pipeline evidence, and verify the final submitted commit's pipeline result.
- Check that the MIT licence is detected in the GitLab About section.
- Keep the public English video below 3:00 and preserve readable demo labels.
- If requesting the cloud bonus, verify the public Google Cloud deployment and repository deployment code.
- Submit before **27 Oct 2026, 06:00 Pacific Time (13:00 UTC)**, then follow the organizer's freeze guidance.

Requirements and category definitions: [official rules](https://gitlab-transcend.devpost.com/rules), [resources](https://gitlab-transcend.devpost.com/resources), and [saved primary-source check](codex/RULES_CHECK.md).
