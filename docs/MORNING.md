# Morning

For Alex, Wed 7 Oct 2026. One page.

## The concept in one sentence

**Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight; everything else wakes them, and the orders end at 07:00.**

## Why it beats past winners and the field

- **It does what past GitLab winners did, in a new place.** One job, real runs inside our own GitLab project, and one human decision built in code: the merge at dusk is the signature ([PATTERNS.md](PATTERNS.md#7-ten-rules-for-our-entry)). It meets all ten of our rules from 102 past winners.
- **Nobody in October is doing on-call at night** ([FIELD.md](FIELD.md#6-open-spaces-nobody-seems-to-be-in-them-yet)). It stays out of the crowded spaces: release gatekeepers, security review, pre-merge review.
- **It answers GitLab's October theme**, "Hands Off. How far can your agents go without you?": as far as you signed, for tonight only.
- **The closest past winner behaves differently.** StregEnt (Feb 2026 honorable mention) messages the developer on every failure. Night Orders sends nothing when a signed order covers the failure, and one three-line page when it does not.
- Prize plan: Path A Best Hands-off Agent plus Most Stages Covered (one path prize and one special prize is the most one entry can win).

## The top three

| Rank | Concept | One line | Criteria mean | Total (of 110) |
|---|---|---|---|---|
| 1 | **Night Orders** | Sign tonight's few reversible actions; everything else wakes you | 8.53 | 88.6 |
| 2 | No Mouse (backup) | An agent with no mouse and no screen must buy something on staging by ear, or the release is held | 8.48 | 84.8 |
| 3 | Forget Me | A made-up user signs up, uses the new feature and asks to be forgotten; a release that cannot forget that user is held | 7.80 | 81.7 |

Full reasoning: [IDEAS.md](IDEAS.md).

## What was built, and how to see it

All of it runs offline and in CI. **Nothing has run on GitLab.com or Google Cloud yet.**

- The decision code, with one test per reason it refuses to act: [relay/nightorders/](../relay/nightorders/), [tests/](../tests/).
- The agent's first job, the dusk drafter (today's changes in, tonight's orders out): [agent/dusk.py](../agent/dusk.py).
- A labelled demo night replayed through the real code: run `cd relay && uv run --project .. python -m nightorders.demo_night ../demo/night-2026-10-20`, or open the `demo_night` job's artifact in CI.
- Three Duo flows, checked against GitLab's own flow schema: [flows/](../flows/).
- In progress: the relay service (`relay/main.py`) and the demo shop (`shop/`).
- The pipeline (tests, demo night, flow and orders checks, SAST, secret detection, the gcloud audit in the pinned image, manual keyless deploy): [.gitlab-ci.yml](../.gitlab-ci.yml).
- What a judge reads first: [README.md](../README.md). The dated plan: [PLAN.md](PLAN.md).

## Your steps, with exact links

| # | When | Link | What to do | Time |
|---|---|---|---|---|
| 1 | Today | https://gitlab-transcend.devpost.com/ | Click **Join Hackathon**. | 2 min |
| 2 | Today | https://contributors.gitlab.com/transcend-hackathon | Sign in with GitLab, click **Get started**, enter your Devpost username, submit. Approval is manual, about one business day. | 3 min |
| 3 | Today | https://cloud.google.com/free | Click **Get started for free** and finish the card check (a trial is not billed unless you upgrade). Then at https://console.cloud.google.com/projectcreate create a project named `night-orders` and keep its Project ID. | 10 min |
| 4 | Today | (Codex) | Paste the Codex message from my last chat reply. | 1 min |
| 5 | When GitLab approves you | https://gitlab.com/-/user_settings/personal_access_tokens | Click **Add new token**. Name `night-orders`, expiry `2026-11-20`, scopes `api` and `write_repository`. Create, copy. In this Claude Code environment's settings (the environment menu in the session title bar, then **Edit**), add it as an environment variable named `GITLAB_TOKEN`. Never paste it into a chat. Then start a new Claude Code session and say "workspace ready". If GitLab says "Identity verification is required", follow its prompt first. | 5 min |
| 6 | After Codex's deploy branch is merged | https://shell.cloud.google.com/ | Paste the setup block from [deploy/README.md](../deploy/README.md), step 6. It prints a block of public IDs; paste that back to me. | 30 min |
| 7 | Test nights, Sat 17 or Sun 18 Oct and Tue 20 or Wed 21 Oct | the orders merge request link I send | Merge (or approve) the orders, then give one thumbs-up when paged. | 20 min each |
| 8 | Fri 23 to Mon 26 Oct | [PLAN.md](PLAN.md) | Walk-through, filming, Devpost form. | about 3 hours |

## The first five things to do tomorrow

1. Join on Devpost (step 1).
2. Register for the GitLab workspace (step 2).
3. Start the Google Cloud trial and create the project (step 3).
4. Paste the Codex message (step 4).
5. When the approval email comes, add the token and say "workspace ready" (step 5).
