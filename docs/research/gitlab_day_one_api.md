# GitLab API notes for the Night Orders day-one test

What a script needs to run the day-one test ([brief_C01_night_orders.md, section 10](ideas/brief_C01_night_orders.md)) against a GitLab.com project where our user has the Developer role plus the hackathon's AI member role. Everything below is read from the GitLab docs source on gitlab.com (master, read 2026-10-11) or from the GitLab source code where the docs are silent. Nothing was called live: there is no token on this machine. Anything not found in the docs is marked (unverified).

Conventions: `PRIVATE-TOKEN: <token>` header for REST, `POST /api/v4/graphql` with `{"query": "..."}` for GraphQL. The token is a personal access token with the `api` scope ([access_token_scopes.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/security/tokens/access_token_scopes.md)): `api` "Grants complete read and write access to the API", `read_api` is read only, `read_user` covers only `/user` and `/users`.

## 1. Flows API

Source: [doc/api/duo_agent_platform_flows.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md). Tier: Premium, Ultimate. Generally available in GitLab 19.5.

### Start a flow

`POST /ai/duo_workflows/workflows`. Returns `201 Created`. Request fields we use (all optional in the schema, but `project_id` is required with `ai_catalog_item_consumer_id` and with `issue_id`):

| Field | Type | Doc text |
|---|---|---|
| `project_id` | string | "ID or path of the project to associate the flow with." |
| `ai_catalog_item_consumer_id` | integer | "ID of the AI Catalog item consumer that configures which catalog item to execute. Requires `project_id`. Cannot be used with `workflow_definition`; if both are provided, `ai_catalog_item_consumer_id` takes precedence." |
| `goal` | string | "Description of the task for the agent to complete." |
| `issue_id` | integer | "IID of the issue to associate the flow with. Requires `project_id`." |
| `merge_request_id` | integer | "IID of the merge request to associate the flow with. Requires `project_id`." |
| `start_workflow` | boolean | "When `true`, starts the flow immediately after creation." |
| `allow_agent_to_request_user` | boolean | "When `true` (default), the agent may pause to ask the user questions before proceeding. When `false`, the agent runs to completion without user input." |
| `agent_privileges` | integer array | "Privilege IDs the agent is allowed to use. Defaults to all privileges." IDs: 1 `read_write_files`, 2 `read_only_gitlab`, 3 `read_write_gitlab`, 4 `run_commands`, 5 `use_git`, 6 `run_mcp_tools` (`GET /ai/duo_workflows/workflows/agent_privileges`). |
| `pre_approved_agent_privileges` | integer array | "Privilege IDs the agent can use without asking for user approval. Must be a subset of `agent_privileges`." |
| `environment` | string | "One of: `ide`, `web`, `chat_partial`, `chat`, `ambient`." |
| `workflow_definition` | string | Built-in flow type, for example `developer/v1`. Not used with a catalog consumer. |
| `source_branch`, `image` | string | Only when the flow runs in a CI pipeline. |
| `callback_hook_id`, `client_reference` | integer, string | Webhook callbacks instead of polling. Experiment behind the flag `duo_flow_callback_hooks` (disabled by default), so not for us. |

Example body for the probe: `{"project_id": "<id>", "ai_catalog_item_consumer_id": 12, "issue_id": 7, "goal": "Read issue 7 and post one note: probe ok", "start_workflow": true, "allow_agent_to_request_user": false}`.

Response fields: `id` (integer, "ID of the flow"), `status` (string, "One of `created`, `running`, `paused`, `finished`, `failed`, `stopped`, `input_required`, `plan_approval_required`, or `tool_call_approval_required`"), `web_url` ("URL of the session in the GitLab UI", `.../-/automate/agent-sessions/<id>`), `project_id`, `workflow_definition`, `agent_privileges`, `agent_privileges_names`, `pre_approved_agent_privileges`, `allow_agent_to_request_user`, `workload.id`, `workload.message` ("`null` if no workload was created, for example when `start_workflow` is not `true`"), `mcp_enabled`, `gitlab_url`, `title`, `summary`.

Errors named in the doc: `403 Forbidden` with `"message": "403 Forbidden - Identity verification is required to use GitLab Duo Agent Platform"`. The source adds `403` "Access to the container is not allowed" and `400` "AI Catalog flows can only be executed in project context" ([ee/lib/api/ai/duo_workflows/workflows.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/ee/lib/api/ai/duo_workflows/workflows.rb)). The flag `enforce_composite_identity_for_api_started_workflows` (disabled by default) would demand a composite identity service account when `start_workflow` is true.

Role needed to call it: not stated in the API doc (unverified). The nearest doc text: "Use a flow. Prerequisites: You must have the Developer, Maintainer, or Owner role for the project. The flow must be enabled in the project." ([flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md)). Token scope: the source accepts the `ai_workflows` scope only for the WebSocket, `trace.jsonl` and `execute` routes, so the create call needs a token with `api`.

### Read the status afterwards

There is no `GET /ai/duo_workflows/workflows/:id` in the doc, and the source defines no such route (the routes are the create `POST`, `GET .../agent_privileges`, `GET .../:workflow_id/trace.jsonl`, and `POST .../:workflow_id/execute`, `resume`, `restart`). Two ways to read status:

1. GraphQL `duoWorkflowWorkflows` ("List the workflows owned by the current user"), argument `workflowId: AiDuoWorkflowsWorkflowID` (`"gid://gitlab/Ai::DuoWorkflows::Workflow/<id>"`), or `projectPath` plus `statuses: [DuoWorkflowStatus!]`. Fields on `DuoWorkflow`: `id`, `status` (enum `CREATED`, `RUNNING`, `PAUSED`, `FINISHED`, `FAILED`, `STOPPED`, `INPUT_REQUIRED`, `PLAN_APPROVAL_REQUIRED`, `TOOL_CALL_APPROVAL_REQUIRED`), `humanStatus`, `statusName`, `goal`, `resourceIid`, `lastExecutorLogsUrl`, `stalled` ("Workflow got created but has no checkpoints") ([GraphQL reference](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/graphql/reference/_index.md)).
2. `GET /ai/duo_workflows/workflows/:workflow_id/trace.jsonl` (experiment): one JSON object per line with `status`, `content`, `message_type` (`human`, `ai`). Optional `thread=latest`.

`POST /ai/duo_workflows/workflows/:workflow_id/restart` (experiment) restarts a `failed` or `stopped` project flow and returns a new `id`.

### Look up the consumer ID

Doc section "Look up the consumer ID": "The item must already be enabled for the project."

```graphql
query { aiCatalogConfiguredItems(projectId: "gid://gitlab/Project/<project_id>") { nodes { id item { name } } } }
```

"The `id` field is a Global ID in the format `gid://gitlab/AiCatalogItemConsumer/<numeric_id>`. Use the numeric suffix as the `ai_catalog_item_consumer_id` value." (The GraphQL reference shows the type's example as `gid://gitlab/Ai::Catalog::ItemConsumer/1`; take the number after the last slash either way.)

`Query.aiCatalogConfiguredItems` (experiment, 18.2) returns `AiCatalogItemConsumerConnection!`. Arguments: `projectId: ProjectID`, `groupId: GroupID`, `configurableForProjectId: ProjectID`, `itemId: AiCatalogItemID`, `itemType: AiCatalogItemType`, `itemTypes: [AiCatalogItemType!]`, `includeInherited: Boolean` ("Can only be used with `projectId`"), `includeFoundationalConsumers: Boolean`, `foundationalFlowReference: String`, `sort: AiCatalogConfiguredItemsSort`, plus `first`, `after`, `last`, `before`. Fields of `AiCatalogItemConsumer`: `id: ID!`, `item: AiCatalogItem`, `enabled: Boolean`, `consumerKind: AiCatalogItemConsumerKind!`, `project`, `group`, `serviceAccount: UserCore`, `flowTriggers: [AiFlowTriggerType!]`, `pinnedVersionPrefix`, `webPath`, `userPermissions`.

## 2. GraphQL for the AI Catalog

All from the [GraphQL reference](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/graphql/reference/_index.md). Every mutation here is marked "Status: Experiment". Roles per the user docs: creating a flow, enabling a flow and creating a trigger each say "You must have the Maintainer or Owner role for the project" ([flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), [triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)). Whether the hackathon's AI member role grants these as a Developer is the day-one question (unverified); the custom role abilities are `admin_ai_catalog_item` and `admin_ai_catalog_item_consumer` ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md)).

### Create a flow item from YAML: `aiCatalogFlowCreate`

Exists (introduced 18.3). Input `AiCatalogFlowCreateInput`:

| Argument | Type | Doc text |
|---|---|---|
| `projectId` | `ProjectID!` | "Project for the flow." (the managing project) |
| `name` | `String!` | "Name for the flow." |
| `description` | `String!` | "Description for the flow." |
| `definition` | `String` | "YAML definition for the flow." |
| `release` | `Boolean` | "Whether to release the latest version of the flow." |
| `visibility` | `AiCatalogItemVisibility` | `PRIVATE`, `PUBLIC`, `RESTRICTED` (19.2). `public: Boolean` is deprecated. |

Returns `item: AiCatalogFlow` (`id`, `name`, `versions`, `configurationForProject(projectId:)`, `acceptsTriggerGoal`) and `errors: [String!]!`. Item IDs look like `gid://gitlab/Ai::Catalog::Item/1`. Siblings: `aiCatalogFlowUpdate`, `aiCatalogFlowDelete`, `aiCatalogThirdPartyFlowCreate`.

`aiCatalogAgentCreate` also exists (18.2): `projectId: ProjectID!`, `name: String!`, `description: String!`, `systemPrompt: String!`, `userPrompt: String`, `tools: [AiCatalogBuiltInToolID!]`, `mcpServers`, `mcpTools`, `release`, `visibility`. There is no `aiCatalogItemCreate` mutation.

Note from the docs: "Item definitions are stored in the AI Catalog instead of the repository" ([ai_catalog.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/ai_catalog.md)), so a flow YAML committed to `flows/` must still be pushed into the catalog with this mutation or the UI.

### Enable the item in a project: `aiCatalogItemConsumerCreate`

Exists (18.3). Input `AiCatalogItemConsumerCreateInput`:

| Argument | Type | Doc text |
|---|---|---|
| `itemId` | `AiCatalogItemID!` | "Item to configure." |
| `target` | `ItemConsumerTargetInput!` | `{ projectId: ProjectID }` or `{ groupId: GroupID }`: "Target project or top-level group in which the catalog item is configured." |
| `consumerKind` | `AiCatalogItemConsumerKind` | `DIRECT` or `INHERITANCE` ("`INHERITANCE` is only valid for a top-level group target"). |
| `triggerTypes` | `[String!]` | "List of event types to create AI Catalog triggers for (values can be mention, assign or assign_reviewer)." |
| `triggerGoals` | `JSON` | "Goals for the auto-created AI Catalog triggers, keyed by event type." (19.5) |
| `triggerConditions` | `AiCatalogTriggerConditionsInput` | Per event (`mention`, `assign`, `assignReviewer`, `pipelineHooks`, `mergeRequest`, `workItem`, `scheduled`, ...) a group `{ match, rules: [{ field, operator, value }] }`. |
| `pinnedVersion` | `AiCatalogPinnedVersion` | "Version to pin the item to, in the format `n.n.n`. Must be a released version." |
| `parentItemConsumerId`, `replaceExistingDirectConfigurations` | | Group inheritance cases. |

Returns `itemConsumer: AiCatalogItemConsumer` (its `id` is the consumer ID the Flows API wants), `errors`, `warnings`. `aiCatalogItemConsumerBulkCreate` takes `projectIds: [ProjectID!]!` (up to 100). `aiCatalogItemConsumerUpdate` sets `serviceAccountId: UserID` and `triggerTypes`; `aiCatalogItemConsumerDelete` takes `id`. The UI doc adds: enabling in a project also enables in the top-level group and "A service account is created in the group" named `ai-<flow>-<group>`, which gets the Developer role in the project.

### Create a trigger: `aiFlowTriggerCreate`

Exists (18.3). Input `AiFlowTriggerCreateInput`: `projectPath: ID!` ("Full path of the project"), `description: String!`, `eventTypes: [Int!]`, `aiCatalogItemConsumerId: AiCatalogItemConsumerID` ("AI catalog item consumer to use instead of config_path"), `configPath: String` (for example `.gitlab/duo/flows/claude.yaml`), `userId: UserID` ("Service account for the AI flow trigger"), `filter: JSON`, `goals: JSON` ("keyed by event type"), `active: Boolean`. Returns `aiFlowTrigger: AiFlowTriggerType` (`id`, `eventTypes: [Int!]!`, `active`, `user`, `aiCatalogItemConsumer`) and `errors`. Also `aiFlowTriggerUpdate(id!)` and `aiFlowTriggerDelete(id!)`.

The integer codes for `eventTypes` are not in the docs. From the model [ee/app/models/ai/flow_trigger.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/ee/app/models/ai/flow_trigger.rb): `mention: 0, assign: 1, assign_reviewer: 2, pipeline_hooks: 3, merge_request_ready: 4, merge_request_code_conflict: 5, merge_request: 6, work_item: 7, commit_to_default_branch: 8, scheduled: 9`. The GraphQL enum `AiFlowTriggerEventType` lists the same names in upper case. The triggers doc: "A non-human user such as a bot user, service account user, or another flow, cannot activate a trigger."

Simplest path for the script: pass `triggerTypes: ["assign"]` to `aiCatalogItemConsumerCreate` and skip `aiFlowTriggerCreate`.

### Queries

- `Query.aiCatalogItems` returns `AiCatalogItemConnection!`. Arguments: `itemType: AiCatalogItemType` (`AGENT`, `FLOW`, `FOUNDATIONAL_AGENT`, `SKILL`, `THIRD_PARTY_FLOW`), `itemTypes`, `search: String` ("Search items by name and description"), `sort: AiCatalogItemsSort`, pagination. Use it to find our flow's `id` by name after creation.
- `Query.aiCatalogItem(id: AiCatalogItemID!)`, `Query.aiCatalogItemConsumer(id: AiCatalogItemConsumerID!)`, `Query.aiCatalogConfiguredItems` (section 1).

## 3. Feature flags

Source: [doc/api/feature_flags.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/feature_flags.md) (tier: Free). "Prerequisites: You must have the Developer, Maintainer, or Owner role." The permissions table agrees: "Manage Feature flags" is checked for Developer, Maintainer and Owner ([permissions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/permissions.md)). A project can raise this with `feature_flags_minimum_role` (`PUT /projects/:id/feature_flags_settings?minimum_role=maintainer`, 19.4, behind the flag `feature_flag_management_permissions`); default `developer`.

### Create a flag with a userWithId strategy scoped to production

`POST /projects/:id/feature_flags`. Fields: `name` (required), `version` (required, must be `new_version_flag`), `description`, `active` (default true), `strategies` (array), `strategies:name` ("Can be `default`, `gradualRolloutUserId`, `userWithId`, `gitlabUserList`, or `flexibleRollout`"), `strategies:parameters`, `strategies:scopes`, `strategies:scopes:environment_scope`. The `userWithId` parameter key is `userIds`, a comma-separated string (the doc's example is `"parameters": {"userIds": "user1"}`; the user doc says "Enter user IDs as a comma-separated list of values").

```json
{"name": "new_checkout", "version": "new_version_flag", "description": "demo data: Night Orders pilot", "active": true,
 "strategies": [{"name": "userWithId", "parameters": {"userIds": "pilot-01,pilot-02,pilot-03"},
                 "scopes": [{"environment_scope": "production"}]}]}
```

Response echoes `name`, `active`, `version`, `strategies[].id`, `strategies[].scopes[].id`. To turn a flag off: `PUT /projects/:id/feature_flags/:feature_flag_name` with `active: false` (also `strategies:id`, `strategies:_destroy`). `DELETE /projects/:id/feature_flags/:feature_flag_name` removes it. `GET /projects/:id/feature_flags` lists.

### Unleash client API

User doc [doc/operations/feature_flags.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/feature_flags.md), "Get access credentials": in the project go to Deploy > Feature flags > Configure to see "API URL: URL where the client (application) connects to get a list of feature flags", "Instance ID: Unique token that authorizes the retrieval of the feature flags", "Application name: The name of the environment the application runs in". The examples use `url: 'https://gitlab.com/api/v4/feature_flags/unleash/42'` (42 is the project ID) and `instance_id: '29QmjsW6KngPR5JNPMWx'`.

The client endpoints are no longer in the REST API docs; from the source [lib/api/unleash.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/unleash.rb): `GET /api/v4/feature_flags/unleash/:project_id/client/features` (also `GET .../features`, `POST .../client/register`, `POST .../client/metrics`). Authentication is `authorize_by_unleash_instance_id!`: the instance ID is read from the header `UNLEASH-INSTANCEID` or the query parameter `instance_id`; the environment from the header `UNLEASH-APPNAME` or `app_name`. A wrong instance ID gives `401 Unauthorized`. No `PRIVATE-TOKEN` is involved.

Is the instance ID readable through the REST API? No. [lib/api/feature_flags.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/feature_flags.rb) has no token endpoint, the GraphQL reference has no Unleash or client token field, and the only route that touches it is the UI's `POST /<project>/-/feature_flags_client/reset_token` ([config/routes/project.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/config/routes/project.rb)). Alex copies it once from the Configure dialog into Secret Manager. Whether a Developer can open that dialog on GitLab.com: the API doc's Developer prerequisite suggests yes (unverified).

## 4. Issues, notes, reactions

- Create an issue: `POST /projects/:id/issues` with `title` (required), `description` ("Limited to 1,048,576 characters"), `issue_type` ("One of `issue`, `incident`, `test_case` or `task`. Default is `issue`"), `labels` (comma-separated, creates missing labels), `confidential` ([issues.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/issues.md)). Permissions: "Create issues" from Guest up; "Create incident" from Reporter up ([permissions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/permissions.md)).
- Templates: the issues API has no template parameter. Templates live in `.gitlab/issue_templates/*.md` ([description_templates.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/description_templates.md)). The script either reads the file from the repo or calls `GET /projects/:id/templates/issues/:name`, which returns `name` and `content` and includes "project-specific templates" ([project_templates.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/project_templates.md)), then posts `content` as `description`.
- Create a note: `POST /projects/:id/issues/:issue_iid/notes` with `body` (required, "Limited to 1,000,000 characters"), `internal` (boolean). List notes: `GET /projects/:id/issues/:issue_iid/notes` with `sort` (`asc`, `desc`), `order_by` (`created_at`, `updated_at`), `activity_filter` (`all_notes`, `only_comments`, `only_activity`) ([notes.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/notes.md)). Same shape under `/merge_requests/:merge_request_iid/notes`.
- Emoji reaction on a note: `POST /projects/:id/issues/:issue_iid/notes/:note_id/award_emoji` with `name` ("Name of the emoji without colons", for example `thumbsup`); returns `id`, `name`, `user.username`, `awardable_type: "Note"`. List them with `GET` on the same path; this is how the relay sees Alex's thumbs-up ([emoji_reactions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/emoji_reactions.md)).

## 5. Branches, commits, merge requests

- Branch: `POST /projects/:id/repository/branches` with `branch` and `ref`; `201 Created`, response has `can_push` ([branches.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/branches.md)).
- Commit: `POST /projects/:id/repository/commits` with `branch`, `commit_message`, `actions[]` (each: `action` one of `create`, `update`, `delete`, `move`, `chmod`; `file_path`; `content`; `encoding` `text` or `base64`), and `start_branch` to create the branch in the same call ("To create a new branch, also provide either `start_branch` or `start_sha`") ([commits.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/commits.md)).
- Open an MR: `POST /projects/:id/merge_requests` with `source_branch`, `target_branch`, `title` (all required), `description`, `labels`, `remove_source_branch`, `squash`, `reviewer_ids`, `assignee_id` ([merge_requests.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_requests.md)). "Create merge request" needs Developer or above.
- Merge: `PUT /projects/:id/merge_requests/:merge_request_iid/merge` with optional `sha`, `squash`, `should_remove_source_branch`, `merge_commit_message`, `auto_merge`. Failure codes from the doc: `400` "SHA must be provided when merging", `401` "401 Unauthorized" ("This user does not have permission to accept this merge request"), `405` "405 Method Not Allowed" ("The merge request cannot merge"), `409` "SHA does not match HEAD of source branch", `422` "Branch cannot be merged".
- Approve: `POST /projects/:id/merge_requests/:merge_request_iid/approve` (Free tier) with optional `sha` (mismatch gives `409 Conflict`); returns `201 Created` and the approval state (`approved`, `approved_by`) ([merge_request_approvals.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/merge_request_approvals.md)). "By default, the creator of a merge request (author) cannot approve it" ([approvals/settings.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/merge_requests/approvals/settings.md)), so the flow's MR must be approved by Alex, not by the account that opened it. `POST .../unapprove` undoes it.

### What a Developer gets when merging into a protected default branch is refused

The merge route checks `unauthorized! unless merge_request.can_be_merged_by?(current_user)` with the comment "Merge request can not be merged because the user doesn't have permissions to push into target branch" ([lib/api/merge_requests.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/merge_requests.rb)). So the script sees HTTP `401` with body `{"message": "401 Unauthorized"}`. (`405` means the MR itself is not mergeable, for example a conflict or a failed pipeline.)

Why it happens: "The default branch for your repository is protected by default" and the default level is "Fully protected - Default value. Developers cannot push new commits, but maintainers can." ([branches/default.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/repository/branches/default.md)). The table "Permission combinations for Developer role" in [branches/protected.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/repository/branches/protected.md) says a Developer can "Merge through MR" only when Allowed to merge is "Developers + Maintainers"; with "Maintainers" it is no for both direct push and merge. The hackathon subgroups default to `allowed_to_merge: 40` ([gitlab_guide_and_reference.md](gitlab_guide_and_reference.md)). To check before trying: `GET /projects/:id/protected_branches/:name` returns `merge_access_levels[].access_level` and `push_access_levels[].access_level` (`30` Developer, `40` Maintainer) ([protected_branches.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/protected_branches.md)). Changing it needs Maintainer.

## 6. Who am I, what can I do

- `GET /user`: `id`, `username`, `name`, `email`, `state` ([users.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/users.md)).
- `GET /projects/:id`: `permissions.project_access.access_level` and `permissions.group_access.access_level` (each `null` when there is no direct membership of that kind), `visibility`, `default_branch`, `duo_remote_flows_enabled`, `duo_foundational_flows_enabled` ([projects.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/projects.md)). Access levels: 10 Guest, 20 Reporter, 30 Developer, 40 Maintainer, 50 Owner.
- `GET /projects/:id/members/all` lists direct and inherited members with `username`, `access_level`, `expires_at` ([project_members.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/project_members.md)). Custom roles: the member entry may carry a `member_role` object on Ultimate (unverified, not in the section read). The flow's service account `ai-<flow>-<group>` should appear here with `access_level: 30` once a flow is enabled.
- `PUT /projects/:id`: "The Maintainer or Owner role on a project to edit the project's properties." Attributes include `visibility` (`private`, `internal`, `public`), `duo_remote_flows_enabled` ("Determine whether or not flows can run in your project"), `feature_flags_minimum_role`, `default_branch`. The permissions table has "Change project visibility level" checked for Owner only, so making the project public is an Owner action; a Developer gets `403` (the code is inferred, unverified).
- `duo_features_enabled` is not a project attribute. It is a group attribute: `PUT /groups/:id` with `duo_features_enabled` and `lock_duo_features_enabled` ("GitLab Self-Managed, Premium and Ultimate only"), and that call requires "an administrator or have the Owner role for the group" ([groups.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/groups.md)). A Developer cannot set it; the organizers must have.
- Agent Platform prerequisites: GitLab Duo turned on (or Duo Core on for the top-level group), the Agent Platform turned on (18.8 and later), a project in a group namespace, and "the Developer, Maintainer, or Owner role" ([duo_agent_platform/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/_index.md)).

## 7. Pipelines

- Start one: `POST /projects/:id/pipeline` with `ref` (required, "The branch or tag to run the pipeline on"), `variables` (array of `{"key": ..., "value": ..., "variable_type": "env_var" | "file"}`), `inputs` (hash). Response: `id`, `iid`, `status`, `ref`, `sha`, `web_url`, `yaml_errors` ([pipelines.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/pipelines.md)). Developers may "run CI/CD pipelines"; on a protected branch "Only if the user is allowed to merge or push to the protected branch" ([permissions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/permissions.md)), so test on a feature branch.
- Read it: `GET /projects/:id/pipelines/:pipeline_id` for `status`; `GET /projects/:id/pipelines/:pipeline_id/jobs` with `scope` (one or more status values) and `include_retried`; each job has `id`, `name`, `stage`, `status`, `web_url`. Status values: `created`, `pending`, `preparing`, `waiting_for_resource`, `waiting_for_callback`, `running`, `success`, `failed`, `canceling`, `canceled`, `skipped`, `manual`, `scheduled`. Log: `GET /projects/:id/jobs/:job_id/trace` ([jobs.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/jobs.md)).

## Order for the script (day one)

1. `GET /user`, `GET /projects/:id` (role), `GET /projects/:id/protected_branches/<default>`, `GET /projects/:id/members/all`. Record the role and the merge access level.
2. `aiCatalogFlowCreate` with the probe YAML (expect a permission error if the AI member role does not include `admin_ai_catalog_item`; then Alex creates it in the UI).
3. `aiCatalogItemConsumerCreate` with `target: {projectId}` and `triggerTypes: ["assign"]`; read `itemConsumer.id`. Confirm with `aiCatalogConfiguredItems`.
4. Create an incident issue; `POST /ai/duo_workflows/workflows` with the consumer ID, `issue_id`, `start_workflow: true`, `allow_agent_to_request_user: false`. Poll `duoWorkflowWorkflows(workflowId:)` and the issue notes for five minutes.
5. Feature flag create, toggle off, delete. Branch, commit, MR, approve attempt, merge attempt: record the `401` or the merge.
6. Pipeline on the branch, read jobs. Write the results to [STATUS.md](../STATUS.md).
