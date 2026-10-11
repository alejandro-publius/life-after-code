# Morning handoff

For Alex, updated **Sun 11 Oct 2026**.

**Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight. Everything else wakes them, and the orders end at 07:00.**

## Where we are

- The whole loop runs offline: decision code, dusk drafter, relay, demo shop, browser demo at `/demo`, three Duo flows, CI. The suite passes (see [STATUS.md](STATUS.md) for the count).
- Added on 11 Oct: the test-night runner, the day sheet the relay posts at dusk, and readiness and one-tick-at-a-time for the relay. Landing the same day, see [STATUS.md](STATUS.md): the day-one probe script, an exact restore at the morning countersign, and Codex's three-service deploy after review.
- Nothing has run on GitLab.com or Google Cloud yet. That is the only thing between us and a real night, and it needs three things from you.

## Your three steps (phone, about 15 minutes)

| # | What | Where | Why |
|---|---|---|---|
| 1 | Send me the link to your hackathon workspace from the approval email (it looks like `gitlab.com/gitlab-ai-hackathon/transcend-october-2026/<number>/showcase`), or just your GitLab username. | the approval email | I could not find it: 384 workspaces exist and none is under a name I know. |
| 2 | Create a personal access token: https://gitlab.com/-/user_settings/personal_access_tokens , **Add new token**, name `night-orders`, expiry `2026-11-20`, scopes `api` and `write_repository`. Copy it. In this Claude Code environment's settings (the cloud environment menu in the session title bar, then **Edit**), add it as an environment variable named `GITLAB_TOKEN`. Never paste it into the chat. Then start a new session and say "token is in". If GitLab asks for identity verification first, do that. | GitLab, then the environment settings | With the token I push the repo to GitLab, run the day-one test, create the flags and the watch issue, and later run the test nights. |
| 3 | If not done: start the Google Cloud trial at https://cloud.google.com/free , then create a project named `night-orders` at https://console.cloud.google.com/projectcreate and keep its Project ID. | Google | Cloud Run hosts the shop and the relay. |

## What happens next, and when you are needed again

| When | Who | What |
|---|---|---|
| Within 48 hours of the token | Claude Code | The live gate: [scripts/day_one.py](../scripts/day_one.py). It reports your role, whether you can merge, creates the two flags and the watch issue, and starts a probe flow through the Flows API. Results go in [STATUS.md](STATUS.md). |
| Same day, 15 min on a laptop | Alex | Create the flows in GitLab from `flows/*.yml` and enable them in the project (the script's `catalog` step prints the exact clicks, or does it through the API if that is allowed). |
| Tue 13 or Wed 14 Oct, 30 min in Cloud Shell | Alex | Run `deploy/setup_gcp.sh` from [deploy/README.md](../deploy/README.md), paste the two hidden secrets when asked (the GitLab token and the Unleash instance ID), then press Play on the three deploy jobs. Install the ntfy app and subscribe to the topic the setup prints. |
| Sat 17 or Sun 18 Oct, evening and morning | Alex | First test night ([TEST_NIGHT.md](TEST_NIGHT.md)): merge the orders, sleep, one thumbs-up if paged, countersign over coffee. |
| Sat 24 Oct | Alex | Film ([VIDEO.md](VIDEO.md)). Submit by Mon 26 Oct, 9 PM Pacific ([PLAN.md](PLAN.md)). |

## Try it now without any account

```sh
uv sync --locked
cd relay
uv run --project .. uvicorn main:app --host 127.0.0.1 --port 8080
```

Open http://localhost:8080/demo and play one night: sign the demo orders, approve the fallback, read the morning brief. Then replay without signing. Everything in it is labelled demo data; the decisions come from the real code. The terminal version: `cd relay && uv run --project .. python -m nightorders.demo_night ../demo/night-2026-10-20`.

## One decision you should know about

A separate session on 6 Oct opened a review that suggested switching the concept to No Mouse (branch `claude/concept-review`). I kept Night Orders: the review's main worry (can a hackathon account create and enable a custom flow at all) applies to every concept equally, and the code gaps it found are fixed. The day-one test settles it. Details in [DECISIONS.md](DECISIONS.md).
