# Creating and enabling the flows in GitLab

The repeatable setup command below installs the three Night Orders workflows from [flows/](../flows/). It was run successfully against the hackathon project on 27 Oct 2026: dusk, watch and dawn are enabled with verified released definitions and actual service accounts. A second apply made zero changes. [Verification record](codex/FLOW_SETUP.md).

## Automated setup

Set `GITLAB_TOKEN` in the process environment, with API access to the target project. From the repository root:

```sh
# Read-only check. A missing or mismatched flow returns exit code 1.
uv run --locked python scripts/setup_flows.py --project <project-id-or-path>

# Create and enable only missing flows, then verify GitLab's saved configuration.
uv run --locked python scripts/setup_flows.py --project <project-id-or-path> --apply --out /tmp/night-orders-flows.json
```

The command validates all selected YAML files before making any network request. It searches every catalog page within a bounded limit, uses only items owned by this project, checks the released definition against the local file, and reads each service account from GitLab, including accounts stored on flow triggers. It leaves disabled, mismatched or ambiguous existing flows unchanged and reports the problem. `--flow dusk`, `--flow watch` and `--flow dawn` select individual flows and can be repeated.

The JSON contains consumer IDs, service-account names, definition hashes, verification results and the changes made. It contains no token. Copy its `values` into the relay's configuration; the watch and dawn values match the relay's existing setting names. The dusk account is the user to assign the watch issue to. Setup does not start a flow, sign orders, send issue notes or change a feature flag. An enabled flow is configuration evidence; its execution must be checked separately.

The optional probe remains available through `scripts/day_one.py --project <id> --step catalog --create-probe --yes`. It is a diagnostic flow, separate from the three application workflows.

## Manual fallback

The clicks below are from GitLab's own page on custom flows ([source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), read 11 Oct 2026). That page describes Maintainer or Owner access; the hackathon project's Developer+ role successfully used the setup API. Check the actual response for another project rather than assuming the same permissions. Validate files with `uv run python flows/validate.py` before pasting them.

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

Run the verifier, with the token in the environment:

```sh
uv run --locked python scripts/setup_flows.py --project <project-id-or-path> --out /tmp/night-orders-flows.json
```

It prints verified consumer IDs and actual service accounts. Put them in the public deploy config (`deploy/gcp.env`, see [deploy/README.md](../deploy/README.md)): `FLOW_CONSUMER_ID` for the watch flow, `DAWN_FLOW_CONSUMER_ID` for the dawn flow.

Each flow posts as **its own** service account: GitLab names it from the flow and the top-level group, `ai-<flow name>-<group>` (GitLab source: `ee/app/services/ai/catalog/item_consumers/create_service.rb`). `FLOW_SERVICE_ACCOUNT` must be the **watch** flow's account, for example `ai-night-orders-watch-<group>`, because the relay reads only that account's notes as answers. The probe's note comes from the probe's own account, so it only confirms the naming pattern; do not copy the probe's username into `FLOW_SERVICE_ACCOUNT`. `DAWN_FLOW_SERVICE_ACCOUNT` is the dawn flow's account, needed only with `FLOW_START=mention`. The `issue` step prints `WATCH_ISSUE_IID`.

## 4. If the API can do it instead

Both setup commands use the GraphQL mutations `aiCatalogFlowCreate` and `aiCatalogItemConsumerCreate` ([research](research/gitlab_day_one_api.md)). The automated setup above now handles all three application flows, including post-write verification and repeat runs.

## What can go wrong

| Symptom | Meaning |
|---|---|
| **New flow** is missing or greyed out | The role cannot create flows, or custom flows are off for the top-level group. Ask the organizers. |
| The editor rejects the YAML | Paste again from the raw file view; check nothing was changed by autocorrect. |
| **Enable** fails | The role cannot enable flows in the project. Ask the organizers; the day-one test records this. |
| The probe flow starts but never posts | Read its session under **AI** > **Sessions**. For catalog flows GitLab ignores the privilege fields in the Flows API request (`agent_privileges` and the others; GitLab source: `ee/lib/api/ai/duo_workflows/workflows.rb`), so what limits a flow is its toolset: the watch flow's writer has `create_issue_note` and nothing that changes flags, deployments or merge requests |
| Every night ask times out with "The agent did not answer" | `FLOW_SERVICE_ACCOUNT` is not the watch flow's own account (see step 3) |
| The Flows API answers 403 or 404 | Set `FLOW_START=mention` and check the watch flow's Mention trigger; if mentions do not start it either, `WATCH_MODE=standing` |
