# Morning handoff

For Alex, updated **Thu 15 Oct 2026**.

**Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight. Everything else wakes them, and the orders end at 07:00.**

## Where we are

- The whole loop runs offline and is reviewed: decision code, dusk drafter, relay, demo shop, browser demo, three Duo flows, the pipeline. A five-lens review found more than thirty real defects; all are fixed, each with a test ([DECISIONS.md](DECISIONS.md)). The suite passes ([STATUS.md](STATUS.md) has the count).
- New since 11 Oct: the relay can start a flow by a mention if the Flows API is refused, approvals count only if they are newer than the commit they sign, Cloud Run changes are read back, and the night report links every step of the night in GitLab.
- On 14 Oct I read the other public entries in the hackathon's GitLab group. Three ideas are still ours alone: a permission signed each night, the morning countersign, and a kept change that ends when its fix ships. The pitch now leads with them.
- The strongest entries show live Duo runs, pipelines, a public URL and a video. All four start for us the day the token is in. Nothing has run on GitLab.com or Google Cloud yet.

## Your three steps (phone, about 15 minutes)

| # | What | Where | Why |
|---|---|---|---|
| 1 | Send me the link to your hackathon workspace from the approval email (it looks like `gitlab.com/gitlab-ai-hackathon/transcend-october-2026/<number>/showcase`), or just your GitLab username. | the approval email | I could not find it: 577 workspaces exist and none is under a name I know. |
| 2 | Create a personal access token: https://gitlab.com/-/user_settings/personal_access_tokens , **Add new token**, name `night-orders`, expiry `2026-11-20`, scopes `api` and `write_repository`. Copy it. In this Claude Code environment's settings (the cloud environment menu in the session title bar, then **Edit**), add it as an environment variable named `GITLAB_TOKEN`. Never paste it into the chat. Then start a new session and say "token is in". If GitLab asks for identity verification first, do that. | GitLab, then the environment settings | With the token I push the repo to GitLab, run the day-one test, create the flags and the watch issue, and later run the test nights. A personal token (not a project token) also lets the relay start a flow by a mention. |
| 3 | If not done: start the Google Cloud trial at https://cloud.google.com/free , then create a project named `night-orders` at https://console.cloud.google.com/projectcreate and keep its Project ID. | Google | Cloud Run hosts the shop and the relay. |

## What happens next, and when you are needed again

| When | Who | What |
|---|---|---|
| The day the token is in | Claude Code | Push to GitLab (the first pipeline, the Pages demo and a tagged release follow), then the live gate: [scripts/day_one.py](../scripts/day_one.py). It reports your role, whether you can merge, creates the two flags and the watch issue, and starts a probe flow. Its JSON feeds [scripts/live_gates.py](../scripts/live_gates.py), which rewrites [LIVE_GATES.md](LIVE_GATES.md). |
| Same day, 15 min on a laptop | Alex | Create the four flows in GitLab and enable them, following [FLOWS_SETUP.md](FLOWS_SETUP.md) (or the script does it through the API if our role allows). |
| Within two days, 30 min in Cloud Shell | Alex | Run `deploy/setup_gcp.sh` from [deploy/README.md](../deploy/README.md), paste the two hidden secrets when asked (the GitLab token and the Unleash instance ID), then press Play on the three deploy jobs. Install the ntfy app and subscribe to the topic the setup prints. |
| The first evening after deploy, and the morning after | Alex | First test night ([TEST_NIGHT.md](TEST_NIGHT.md)): merge the orders, sleep, one thumbs-up if paged, countersign over coffee. Aim for Mon 19 Oct, so a second night fits before filming. |
| By Wed 21 Oct | Both | Choose the video plan: the real night (Plan A) or the browser demo (Plan B) ([VIDEO.md](VIDEO.md)). |
| Sat 24 Oct | Alex | Film and upload. Submit by Mon 26 Oct, 9 PM Pacific ([SUBMIT.md](SUBMIT.md)). The deadline is Tue 27 Oct, 13:00 UTC. |

## Try it now without any account

```sh
uv sync --locked
cd relay
uv run --project .. uvicorn main:app --host 127.0.0.1 --port 8080
```

Open http://localhost:8080/demo and play one night: sign the demo orders, approve the fallback, read the morning brief. Then replay without signing. Everything in it is labelled demo data; the decisions come from the real code. The terminal version: `cd relay && uv run --project .. python -m nightorders.demo_night ../demo/night-2026-10-20`.

## One decision you should know about

A separate session on 6 Oct opened a review that suggested switching the concept to No Mouse (branch `claude/concept-review`). I kept Night Orders: the review's main worry (can a hackathon account create and enable a custom flow at all) applies to every concept equally, and the code gaps it found are fixed. The day-one test settles it. Details in [DECISIONS.md](DECISIONS.md).
