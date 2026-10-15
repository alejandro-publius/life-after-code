# Creating and enabling the flows in GitLab

Alex's laptop step, about 15 minutes, once the repository is pushed to the hackathon project. The four flow files are in [flows/](../flows/); every one of them passes GitLab's flow schema (`uv run python flows/validate.py`). The clicks below are from GitLab's own page on custom flows ([source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), read 11 Oct 2026). The page says creating and enabling a flow needs the Maintainer or Owner role; the hackathon gives Developer plus an AI member role, so the first attempt is also the test of that role. If GitLab refuses, say so in the hackathon Discord that day ([PLAN.md](PLAN.md), decision D1).

## 1. Create each flow (four times)

1. In the project's left sidebar select **AI**, then **Flows**, then **New flow**.
2. Under **Basic information**, enter the name and description from the table below.
3. Under **Visibility & access**, choose **Private**.
4. Under **Configuration**, select **Flow**, open the file named below in another tab (raw view), copy all of it and paste it into the editor. The files are ASCII only on purpose: the editor has corrupted long dashes for other entrants.
5. Select **Create flow**.

| Order | Name | Description | File |
|---|---|---|---|
| 1 | `night-orders-probe` | Day-one probe: reads an issue and posts one note | `flows/probe.yml` |
| 2 | `night-orders-watch` | Night watch: reads the incident and names a signed order or declines | `flows/watch.yml` |
| 3 | `night-orders-dusk` | Dusk: drafts tonight's orders from the day sheet and opens the orders merge request | `flows/dusk.yml` |
| 4 | `night-orders-dawn` | Dawn: proposes keep or restore for each overnight change and opens the countersign merge request | `flows/dawn.yml` |

## 2. Enable each flow in the project

1. **AI** > **Flows** > the **Managed** tab > the flow.
2. In the upper-right corner select **Enable**.
3. Under **Project**, choose this project.
4. Under **Add triggers**, choose the trigger in the table below. Leave the **Goal** field empty: the relay passes a goal when it starts a flow through the API, and the dusk flow reads the day sheet note on the issue it is assigned to. (Whether an assigned issue reaches the flow with an empty goal is checked on day one with the probe flow; if it does not, put "Draft tonight's orders from the day sheet on this issue" in the dusk trigger's Goal field.)
5. Select **Enable**.

| Flow | Trigger | Why |
|---|---|---|
| probe | **Assign** and **Mention** | the day-one test starts it through the Flows API, then by a mention, to learn which way works on this account |
| watch | **Mention** | the relay starts it through the Flows API; with `FLOW_START=mention` the relay starts it instead by a note on the incident that mentions the flow's service account ([GitLab: triggers](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)) |
| dusk | **Assign** | the on-call person assigns the "Tonight's watch" issue to it every evening |
| dawn | **Mention** | the relay starts it through the Flows API at 07:00, or by a mention on the watch issue with `FLOW_START=mention` |

GitLab's Mention trigger runs a flow "when the service account user is mentioned in a comment on an issue or merge request", and the flow receives that comment. So if the Flows API will not start a flow on this account, the relay can still keep the model's key: it posts the same goal as a note that begins with the flow's service account name (`FLOW_START=mention`). GitLab's triggers page says a bot or service account cannot set off a trigger, so with mention the relay's `GITLAB_TOKEN` must be a person's token, not a project or group access token (unverified on this account until the day-one `flow` step tries it). Standing Orders (no model at night) is the last fallback, not the first.

## 3. Record the IDs the relay needs

Run, with the token in the environment:

```sh
GITLAB_TOKEN=... python scripts/day_one.py --project <project id or path> --step catalog
```

It prints every enabled flow with its consumer ID and its service account. Put them in the public deploy config (`deploy/gcp.env`, see [deploy/README.md](../deploy/README.md)): `FLOW_CONSUMER_ID` for the watch flow, `DAWN_FLOW_CONSUMER_ID` for the dawn flow.

Each flow posts as **its own** service account: GitLab names it from the flow and the top-level group, `ai-<flow name>-<group>` (GitLab source: `ee/app/services/ai/catalog/item_consumers/create_service.rb`). `FLOW_SERVICE_ACCOUNT` must be the **watch** flow's account, for example `ai-night-orders-watch-<group>`, because the relay reads only that account's notes as answers. The probe's note comes from the probe's own account, so it only confirms the naming pattern; do not copy the probe's username into `FLOW_SERVICE_ACCOUNT`. `DAWN_FLOW_SERVICE_ACCOUNT` is the dawn flow's account, needed only with `FLOW_START=mention`. The `issue` step prints `WATCH_ISSUE_IID`.

## 4. If the API can do it instead

The script's `--create-probe` option tries the GraphQL mutations `aiCatalogFlowCreate` and `aiCatalogItemConsumerCreate` ([research](research/gitlab_day_one_api.md)). If they are allowed for our role, the same can be done for the other three flows and this page becomes a check rather than a chore.

## What can go wrong

| Symptom | Meaning |
|---|---|
| **New flow** is missing or greyed out | The role cannot create flows, or custom flows are off for the top-level group. Ask the organizers. |
| The editor rejects the YAML | Paste again from the raw file view; check nothing was changed by autocorrect. |
| **Enable** fails | The role cannot enable flows in the project. Ask the organizers; the day-one test records this. |
| The probe flow starts but never posts | Read its session under **AI** > **Sessions**. For catalog flows GitLab ignores the privilege fields in the Flows API request (`agent_privileges` and the others; GitLab source: `ee/lib/api/ai/duo_workflows/workflows.rb`), so what limits a flow is its toolset: the watch flow's writer has `create_issue_note` and nothing that changes flags, deployments or merge requests |
| Every night ask times out with "The agent did not answer" | `FLOW_SERVICE_ACCOUNT` is not the watch flow's own account (see step 3) |
| The Flows API answers 403 or 404 | Set `FLOW_START=mention` and check the watch flow's Mention trigger; if mentions do not start it either, `WATCH_MODE=standing` |
