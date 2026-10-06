# GitLab hackathon guide and reference

Research for Life After Code (GitLab Transcend Hackathon, Path A). Researched on 2026-10-06. Data was pulled from GitLab between 00:30 and 01:30 UTC that day, so counts are a snapshot.

How to read this file:

- Every fact has a link. "(unverified)" means I could not confirm it. "(inference)" means it is my conclusion from the evidence shown next to it.
- Quotes are word for word. The only change: any em dash or en dash in a source is replaced with " - ".
- GitLab docs were read from their source files in the `gitlab-org/gitlab` repository (`doc/` folder, `master` branch, 2026-10-06). The rendered page has the same path on docs.gitlab.com, for example `doc/user/duo_agent_platform/flows/custom.md` is https://docs.gitlab.com/user/duo_agent_platform/flows/custom/.
- Main sources:
  - Hackathon page source: [contributors/app/javascript/pages/transcend-hackathon-page/](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/tree/main/contributors/app/javascript/pages/transcend-hackathon-page) (renders at https://contributors.gitlab.com/transcend-hackathon).
  - Provisioning code: [provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb).
  - Reference project: [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase).
  - GitLab's review of the June 2026 edition: [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245), plus the June planning thread [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137).
  - Flow YAML spec: [flow registry v1](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md) (last changed 2026-10-05).

## Build setup inside GitLab's hackathon workspace

### Dates

From [transcendDates.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/transcendDates.ts) and [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md):

| Event | Time (UTC) |
|---|---|
| Registration opens | 2026-09-29 10:00 |
| Submissions open (approvals and provisioning start) | 2026-10-05 10:00 |
| Hackathons start (keynote) | 2026-10-06 10:00 |
| Submissions close (also registration close) | 2026-10-27 14:00 |
| Judging | 2026-10-28 10:00 to 2026-11-11 17:00 |
| Winners announced | on or around 2026-11-16 14:00 |

The deadline is 14:00 UTC on October 27, not midnight.

### How you get a workspace

1. Register on Devpost: https://gitlab-transcend.devpost.com/ . The page says: "**Required to be eligible for cash prizes:** you must both register for the hackathon and submit your work on [Devpost](https://gitlab-transcend.devpost.com/)." ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md))
2. Sign in at https://contributors.gitlab.com/transcend-hackathon , select **Get started** on the Transcend Hackathon card and submit your Devpost username ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)). The form posts to `/api/v1/transcend_hackathon` ([transcendHackathon.ts](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/api/transcendHackathon.ts)).
3. The username is checked by [devpost_validator.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/devpost_validator.rb): it must match `[a-zA-Z0-9_-]+` and `https://devpost.com/<username>` must answer HTTP 200, 301 or 302. Otherwise you see "DevPost username could not be verified." ([transcend_hackathon_controller.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/controllers/api/v1/transcend_hackathon_controller.rb)). One registration per GitLab user and per Devpost username; the Devpost name is stored lowercased ([transcend_hackathon_registration.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/models/transcend_hackathon_registration.rb)).
4. Your registration is "pending" until an admin approves it. The modal says: "Approvals and provisioning start on October 5, when submissions open." ([ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue))
5. On approval, the provisioning service does this, in order ([provisioning_service.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/services/transcend_hackathon/provisioning_service.rb), [its spec](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/spec/services/transcend_hackathon/provisioning_service_spec.rb)):
   - Creates a subgroup under group ID `142538134` (`gitlab-ai-hackathon/transcend-october-2026`). Name: your GitLab username. Path: your numeric GitLab user ID. Visibility: `public`. `project_creation_level: 'developer'`. Description: "Transcend Hackathon Showcase workspace for @<username> (DevPost: <devpost>)."
   - Adds you to that subgroup with access level 30 (Developer) and `member_role_id: 3007169`. The spec calls this "the AI member role".
   - Creates a project named `Showcase` with path `showcase`, `visibility: 'public'`, `initialize_with_readme: true`.
   - Posts the onboarding issue "Welcome to the Transcend Hackathon 🎉" as issue #1, unless the project already has open issues.
   - Marks the registration approved. A failed approval can be retried safely ([MR !2746](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2746)).
6. Your URLs ([transcend_hackathon_registration.rb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/models/transcend_hackathon_registration.rb)):
   - Group: `https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/<your-user-id>`
   - Project: `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/<your-user-id>/showcase`
   - Onboarding issue: `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/<your-user-id>/showcase/-/work_items/1`

What a fresh workspace contains: only GitLab's default README and the onboarding issue. No CI file, no flows, no agent config. Verified on the two staff test workspaces that exist today: [8659557/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase) and [1933526/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/1933526/showcase) (tree, issues, MRs and pipelines read through the public API; 1 commit "Initial commit", 0 MRs, 0 pipelines). The onboarding issue there was authored by a group bot (`group_142538134_bot_...`) and assigned to the participant ([issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/8659557/showcase/-/work_items/1)).

The provisioning token is `TRANSCEND_HACKATHON_GROUP_TOKEN`, and staff notes say the bot `CONTRIBUTOR_PLATFORM_HACKATHON` "must be **Owner** on `gitlab-ai-hackathon/transcend-october-2026` - Maintainer cannot add group members" ([MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747)).

### Your role, and what it probably allows

- Page text: "Once approved, we provision a dedicated GitLab subgroup and project for you. You have the Developer role in that space, so you can add more projects to it." ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md))
- You are a Developer plus custom role 3007169 on your subgroup. The project inherits it. You are not a member of the parent group ("parent: participant must NOT appear", [MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747)).
- What custom role 3007169 grants is not public. Anonymous GraphQL returns `memberRole: null` and `memberRoles: null` for the group, and member lists need sign-in (401). (unverified)
- GitLab offers custom permissions for exactly this: `admin_ai_catalog_item` ("Create, edit, and delete custom agents and flows in the AI catalog") and `admin_ai_catalog_item_consumer` ("Enable, disable, and configure custom agents and flows from the AI catalog for a project") ([abilities.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/custom_roles/abilities.md)). The "AI member role" is probably built on these (inference, unverified).
- Without those permissions a Developer could not build: the docs say creating an agent, creating a flow, enabling a flow and creating a trigger all need "the Maintainer or Owner role for the project" ([flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), [agents/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/custom.md), [triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)).
- Other actions that need Maintainer by default and may or may not be in the custom role (unverified): CI/CD variables (`admin_cicd_variables`), project access tokens (`manage_project_access_tokens`, and a token can only get "the same or fewer permissions as the default role used as the base", so at most Developer), protected branches (`admin_protected_branch`), webhooks (`admin_web_hook`) ([abilities.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/custom_roles/abilities.md)).

### Branch protection: the biggest setup risk

- In the staff test project, `main` is protected with push and merge allowed for Maintainers (access level 40) only, no force push ([public API: protected_branches of project 87183213](https://gitlab.com/api/v4/projects/87183213/protected_branches); branch list shows `developers_can_push: false`, `developers_can_merge: false`).
- The October participant subgroups have `default_branch_protection: 2` with defaults `allowed_to_push: 40`, `allowed_to_merge: 40` ([API: group 143820062](https://gitlab.com/api/v4/groups/143820062), same on the parent [142538134](https://gitlab.com/api/v4/groups/142538134)).
- The June group was different: defaults `allowed_to_push: 30`, `allowed_to_merge: 30`, force push allowed ([API: group 132494471](https://gitlab.com/api/v4/groups/132494471)). June winners pushed straight to `main` (for example [Carver commits](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946/-/commits/main)).
- GitLab docs: "**Fully protected** - Default value. Developers cannot push new commits, but maintainers can." ([branches/default.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/repository/branches/default.md)) and "Developers can push commits to the default branch of a new project only if the default branch protection is set to "Partially protected" or "Not protected"." ([permissions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/permissions.md))
- What this means (inference): unless custom role 3007169 covers it, you cannot push to `main` or merge into `main`, in `showcase` or in a new project you create in your subgroup. That blocks `.gitlab/duo/agent-config.yml` (read only from the default branch, see below) and any deploy job that runs on `main`. Test this on day one and ask the organizers if it fails.

### What the page says to build (word for word)

The full "Details" text of the October page, from [ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md) (last changed 2026-10-02):

````markdown
<!-- markdownlint-disable MD033 MD041 -->

### How it works

- **Registration** opens September 29, 2026 (10:00 UTC).
- **Submissions** run from October 5 until October 27, 2026 (14:00 UTC).
- **Judging** runs until November 11, 2026.
- **Winners** are announced on or around November 16, 2026.

Open to every experience level, from seasoned contributors to complete
beginners.
Some countries and regions are excluded.

> **Required to be eligible for cash prizes:** you must both register for
the hackathon and submit your work on
[Devpost](https://gitlab-transcend.devpost.com/).
See the full [official rules](https://gitlab-transcend.devpost.com/rules)
for details.

<details>
<summary><b>Get started</b></summary>

1. Register for the hackathon on
   [Devpost](https://gitlab-transcend.devpost.com/).
1. Select **Get started** on the Transcend Hackathon card above and submit
   your Devpost username.
   Approvals start on October 5th when the hackathon opens.
1. Once approved, we provision a dedicated GitLab subgroup and project for
   you.
   You have the Developer role in that space, so you can add more projects
   to it.
1. Build your project using Duo Agent Platform.
1. **Required:** Film an explanatory video of your project.
1. Submit your project on
   [Devpost](https://gitlab-transcend.devpost.com/) by October 27th,
   including both your repository and your video.
   See the "What to submit" section on Devpost for full details.
1. (Optional) Share your work through a blog post or on social media.

</details>
<br>

<details>
<summary><b>The challenge</b></summary>

Please see the official rules on
[Devpost](https://gitlab-transcend.devpost.com/rules) for the full
description.

</details>
<br>

<details>
<summary><b>How it is judged</b></summary>

First a pass or fail check: does the project fit the theme and genuinely use
GitLab AI features?

Everything that passes is then scored on five equally weighted criteria:

- **Technological implementation** - how thoroughly and skilfully it uses
  GitLab to automate the post-code lifecycle.
- **Design** - a complete, coherent workflow rather than a proof of concept.
- **Potential impact** - a credible, specific case for solving a real
  problem.
- **Innovation** - how novel the idea is, and how inventively it applies
  agentic automation.
- **Presentation** - how clearly the video demonstrates the automation
  running end to end.

Projects deployed on Google Cloud score higher on technological
implementation.
Full details are listed on the
[Devpost rules](https://gitlab-transcend.devpost.com/rules) page.

</details>
<br>

<details>
<summary><b>Build your idea</b></summary>

Add agents and flows through the UI of your provisioned project under
**Automate → Agents**, or add skills directly to the repository.

- Read the
  [agents](https://docs.gitlab.com/user/duo_agent_platform/agents/),
  [flows](https://docs.gitlab.com/user/duo_agent_platform/flows/), and
  [skills](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/#create-skills)
  documentation.
- The quickest way to author files is the
  [Web IDE](https://docs.gitlab.com/user/project/web_ide/).

#### Test your agent

Chat with your agent in the
[GitLab Duo sidebar](https://docs.gitlab.com/user/gitlab_duo_chat/agentic_chat/#use-gitlab-duo-chat-in-the-gitlab-ui)
by starting a new Duo Chat and selecting your agent, or use one of the
[available extensions](https://docs.gitlab.com/editor_extensions/#available-extensions).

#### Test your flow

Your flow gets a user identity, and you choose what starts it with a
[trigger](https://docs.gitlab.com/user/duo_agent_platform/triggers/).
Flows can run when that user is mentioned in a comment, assigned to an issue
or merge request, or added as a reviewer, and on pipeline, merge request, and
work item events.

#### Test your skill

[Project-level skills](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/#create-project-level-skills)
live in `skills/<skill-name>/SKILL.md` at the project root.
The `name` and `description` metadata fields at the top of the file are
required.
Start a **new** conversation or flow each time you change `SKILL.md` to
avoid context confusion.

#### Observability

Monitoring and incident response are part of life after code, so your
subgroup can have its own observability instance.
In your subgroup, go to
**Observe → Observability configuration → Enable Observability**.
Provisioning takes up to 10 minutes, and you get your own OpenTelemetry
endpoint to send traces, metrics, and logs to.
See the
[observability documentation](https://docs.gitlab.com/operations/observability/observability/)
for what you can do with it.

It is entirely optional and is not required to submit or to win.

</details>
<br>

### Resources

- [Devpost](https://gitlab-transcend.devpost.com/)
- [Official rules](https://gitlab-transcend.devpost.com/rules)
- [GitLab Duo Agent Platform documentation](https://docs.gitlab.com/user/duo_agent_platform/)
- [Prompt library](https://about.gitlab.com/gitlab-duo/prompt-library/)
- [DevSecOps lifecycle stages](https://about.gitlab.com/stages-devops-lifecycle/)
- [GitLab Discord](https://discord.gg/gitlab)
````

The "Rewards" tab only says: "Amounts, judging criteria, and eligibility are set by the [official rules](https://gitlab-transcend.devpost.com/rules), which are the binding source." ([ShowcaseRewards.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseRewards.md))

Summary of what is required and what is allowed, from that text:

- Required: register on Devpost, register on contributors.gitlab.com, build "using Duo Agent Platform", film an explanatory video, submit repo and video on Devpost by October 27.
- Pass or fail gate: "does the project fit the theme and genuinely use GitLab AI features?"
- Five equal criteria: technological implementation, design, potential impact, innovation, presentation. "Projects deployed on Google Cloud score higher on technological implementation."
- Allowed: you can add more projects to your subgroup. Observability "is entirely optional and is not required to submit or to win."
- Optional: blog post or social media.

### Observability

- Page steps: "In your subgroup, go to **Observe → Observability configuration → Enable Observability**. Provisioning takes up to 10 minutes, and you get your own OpenTelemetry endpoint to send traces, metrics, and logs to." ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)). Staff test URL pattern: `https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026/$UID/-/observability/setup` ([MR !2747](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2747)). The docs call the menu **Observe** > **Setup** and say a group Developer can enable it ([setup_gitlab_com.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/setup_gitlab_com.md)).
- Only on your own subgroup. The parent group description says: "Do NOT enable observability on this group, and do NOT add group-level secrets here." ([API: group 142538134](https://gitlab.com/api/v4/groups/142538134))
- Why each person got a subgroup: "GitLab observability is enabled per group and gives one shared instance per group, so a shared namespace would mean all participants see and can delete each other's observability." ([MR !2746](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2746))
- Facts from the docs:
  - Status is "Experiment", free on all tiers ([observability.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/observability.md)).
  - "By default, the GitLab Observability OpenTelemetry Protocol (OTLP) endpoint accepts telemetry without authentication." You can require a bearer ingest token; for CI pipeline telemetry the CI/CD variable is `GITLAB_OBSERVABILITY_TOKEN` ([ci_cd.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/ci_cd.md)).
  - Pipelines are traced with no code change by setting CI/CD variable `GITLAB_OBSERVABILITY_EXPORT` to `traces`, `metrics`, `logs` ([ci_cd.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/ci_cd.md)).
  - Recommended resource attributes: `gitlab.project.id` ("Required for GitLab Duo integration"), `gitlab.project.name`, `service.version`, `deployment.environment.name` ([send.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/send.md)).
  - Query API on GitLab.com: `https://<group_id>.gitlab-o11y.com` with header `SIGNOZ-API-KEY` ([api_access.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/api_access.md)).
  - MCP server for agents: `https://<namespace_id>.mcp.gitlab-o11y.com/mcp`, same API key header; tools for metrics, logs, traces, services, alerts, dashboards ([mcp_server.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/operations/observability/mcp_server.md)).

### Help and office hours

The onboarding issue text, from [description.md.erb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb):

````markdown
Hey @<%= username %>  -  you're in! 🎉

Your [workspace](<%= group_url %>) and project are set up and ready to go.

### Get started

1. Read the [Transcend Hackathon guide](https://contributors.gitlab.com/transcend-hackathon).
2. Join the [GitLab Community Discord](https://discord.gg/gitlab) and say hi in `#transcend-hackathon`.

### Optional: observability

Your workspace can have its own observability stack. In [your group](<%= group_url %>), go to **Observe → Observability configuration → Enable Observability**. It is not required to submit or to win.

### Need help?

- @-mention `gitlab-org/developer-relations/contributor-success` in any issue or MR and we jump in.
- Ask in `#transcend-hackathon` on [Discord](https://discord.gg/gitlab).
- Join the office hours for live troubleshooting + brainstorming.

Good luck, and have fun building! 🚀
````

- Office hours: the template mentions them but gives no link or time. I found no office hours link in the page source, the template, the reference project or the team-task issues. (unverified; the Discord channel is the likely place)
- Staff check-ins: the on-call plan for October 6 to 12 says: "two short check-ins a day instead of a full day watch, one in EU hours and one in US hours, around 30 min each. Between check-ins you just react to @mentions in Discord (#contribute and #transcend-hackathon) and in Slack #co-create-and-community-engineering when you can." Times: "EU check-in 10:00 CEST", "US check-in 16:00 ET"; weekend is one check-in ([team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296), comment by sabadi1, 2026-09-30). Coverage after October 12 is not stated (unverified).
- If a registration is rejected, the modal says to use the [contributors-gitlab-com issue tracker](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/issues/new?issuable_template=default) or [Discord](https://discord.gg/gitlab) ([ShowcaseTrackModal.vue](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseTrackModal.vue)).

### June setup compared with October setup

| | June 2026 (Orbit theme) | October 2026 (this event) |
|---|---|---|
| Namespace | `gitlab-ai-hackathon/transcend` (ID 132494471) | `gitlab-ai-hackathon/transcend-october-2026` (ID 142538134) |
| What you got | One project named by your user ID, directly in the shared group | Your own subgroup (path = user ID) with a project `showcase` |
| Role | Developer + role 3007169 on the project, later also Reporter on the parent group because "some Orbit APIs require the user to be a reporter of the project's parent group" ([MR !2333](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2333)) | Developer + role 3007169 on the subgroup |
| Default branch | Developers could push and merge | Maintainers only (see above) |
| Flow service account | "Your flow gets a user identity like `@ai-flow-name-gitlab-ai-hackathon`" ([June page text](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/16111da6005e8b8c392eb74054e4761e196fa98a/contributors/app/javascript/pages/transcend-hackathon-page/DetailsSection.md)) | Same naming rule in the docs: `ai-<flow>-<group>` |
| Must publish to AI Catalog | Yes: "Publish at least one agent or flow to the AI Catalog" (June page) | Not stated on the October page |

Sources: June and October [provisioning diff](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/commit/75cf9e61), [June page at the commit before removal](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/16111da6005e8b8c392eb74054e4761e196fa98a/contributors/app/javascript/pages/transcend-hackathon-page/DetailsSection.md).

### After the event

- A draft teardown MR already exists: [!2838 "Draft: Tidy up transcend hackathon"](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2838) (opened 2026-10-03) deletes the page, the registration table, the provisioning service and the onboarding template.
- After the February AI Hackathon, staff moved the whole participants group to `gitlab-community/community-projects` and "had to also run a script to change the branch protection so only maintainers can push/merge to them" ([team-task#1155](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1155)).
- So keep your own mirror of the repo and copies of every flow and agent YAML (inference).

## Duo Agent Platform: agents, flows, skills, triggers (exact syntax)

### Where things are in the UI

- The hackathon page says: "Add agents and flows through the UI of your provisioned project under **Automate → Agents**" ([ShowcaseDetails.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)).
- The current docs say **AI** > **Agents**, **AI** > **Flows**, **AI** > **Triggers**, **AI** > **Sessions** ([agents/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/custom.md), [flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md), [triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md), [troubleshooting.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/troubleshooting.md)). Look under both names.
- Session pages use the path `/-/automate/agent-sessions/<id>` ([example](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/automate/agent-sessions/8933788)).
- Latest GitLab release is 19.4 (tag `v19.4.0-ee` on 2026-09-16, [tags](https://gitlab.com/gitlab-org/gitlab/-/tags)). GitLab.com usually runs ahead of releases, so 19.4 features should be live (unverified).

### Custom agents (chat only)

- Create form: **Display name**, **Description**, **Visibility** (Private, Restricted, Public), **System prompt**, **Tools** ([agents/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/custom.md)).
- Use: open an issue, epic or MR, then in the GitLab Duo sidebar select **Add new chat** and pick the agent; also VS Code and JetBrains ([agents/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/custom.md)).
- "A trigger cannot be created for a custom agent or foundational agent." ([triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)) So only flows run on events.
- Max configuration size: 80 KiB ([ai_catalog.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/ai_catalog.md)).
- The YAML form used by the February AI Hackathon's repo template ([agents/agent.yml.template](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template/-/blob/main/agents/agent.yml.template)):

```yaml
name: "AI Hackathon Agent"
description: "An agent to..."
public: true
system_prompt: |
  Only reply with "I'm a placeholder agent, please change my prompt"
tools: # List of available tools https://gitlab.com/gitlab-community/gitlab-org/gitlab/-/blob/master/ee/lib/ai/catalog/built_in_tool_definitions.rb
  - read_file
  - read_files
```

Tool names (from [agents/tools.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/tools.md); the same names go in a flow `toolset`). Useful ones for post-code work:

- Issues and work items: `get_issue`, `list_issues`, `create_issue`, `update_issue`, `create_issue_note`, `list_issue_notes`, `get_work_item`, `create_work_item`, `update_work_item`, `create_work_item_note`, `get_work_item_notes`, `get_work_item_statuses`.
- Merge requests: `get_merge_request`, `create_merge_request`, `update_merge_request`, `create_merge_request_note`, `create_merge_request_diff_note`, `list_merge_request_diffs`, `list_mr_discussions`, `reply_to_discussion`, `set_discussion_resolved`, `submit_mr_review`, `add_merge_request_reviewers`, `build_review_merge_request_context`.
- Pipelines: `get_job_logs`, `get_pipeline_errors`, `get_pipeline_failing_jobs`, `get_downstream_pipelines`, `ci_linter`.
- Code and repo: `get_repository_file`, `get_repository_files`, `list_repository_tree`, `create_branch`, `create_commit`, `get_commit`, `get_commit_diff`, `list_commits`, `gitlab_blob_search`.
- Read-only API: `gitlab_api_get`, `gitlab_graphql`, `run_glql_query`, plus search tools (`gitlab_issue_search`, `gitlab_merge_request_search`, and others).
- Security: `list_vulnerabilities`, `get_vulnerability_details`, `create_vulnerability_issue`, `dismiss_vulnerability`, `confirm_vulnerability`, `link_vulnerability_to_issue`, `link_vulnerability_to_merge_request`.
- IDE only for custom agents, but usable in flows, because a flow gets a repository clone unless it sets `coding_environment: none` ([custom_flows_schema.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom_flows_schema.md)): `read_file`, `read_files`, `edit_file`, `create_file_with_contents`, `find_files`, `grep`, `list_dir`, `mkdir`, `run_command`, `notify_me_when`.
- Note on quick actions: notes and work items tools say "Quick actions are not supported."

### Custom flows: the facts

From [flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md) and [custom_flows_schema.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom_flows_schema.md) unless noted:

- Generally available in GitLab 19.2. The docs list the model as Anthropic Claude Sonnet 4.
- Create: **AI** > **Flows** > **New flow**, then name, description, visibility, then paste YAML in the editor under **Configuration** > **Flow**. Needs Maintainer or Owner (see role section).
- The YAML follows flow registry v1. Restricted in custom flows:
  - `environment`: only `ambient` (`chat` and `chat-partial` are not supported).
  - No `model` field inside `prompts` (the model comes from group or instance settings).
  - `AgentComponent` cannot use `response_schema_id` or `response_schema_version`.
  - `OneOffComponent` cannot use `ui_role_as`.
  - No `stop` inside `params`.
  - "The `name`, `description`, and `product_group` fields from the v1 specification are not supported. Custom flows reject these fields."
- Size limit: "Flow | 40 KiB | The YAML configuration you enter" ([ai_catalog.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/ai_catalog.md)).
- "You cannot define a custom flow to call a specific custom agent from a project or the AI Catalog. Custom flows create and use their own agents based on their YAML configuration."
- Enabling a flow creates a service account: "The name of the account follows this naming convention: `ai-<flow>-<group>`." For example "if you enable a flow called `Security scanner` in the `GitLab Duo` group, the service account user is `ai-security-scanner-gitlab-duo`." In our group that should be `ai-<flow-name>-gitlab-ai-hackathon`, matching the June page example `@ai-flow-name-gitlab-ai-hackathon` (inference).
- "The top-level group's service account is added to the project. This account is assigned the Developer role."
- Warning from the docs: "The service account can access all projects that both: You have access to. The flow has been added to."
- To run: "mention, assign, or request a review from the flow service account user", or use a GitLab Duo Agentic Chat slash command once the flow is on for the project.
- API token inside a flow: "Custom flows have a GitLab OAuth token available as `GITLAB_TOKEN` (also exposed as `GITLAB_OAUTH_TOKEN`)." It only reaches endpoints with the `ai_workflows` scope. "If you use the `PRIVATE-TOKEN` header to send the token, the API returns `401 Unauthorized`." Use `Authorization: Bearer $GITLAB_TOKEN`.
- Custom flows can be turned off per top-level group by an Owner under **Settings** > **GitLab Duo** > **Allow custom flows**. If flow creation silently fails, this or the June finding about `experiment_features_enabled` may be the cause (see lessons).

### Flow YAML skeleton (paste into the UI editor)

The skeleton below is built from the February hackathon template (shown after it), the schema doc and the v1 spec. It keeps to the documented fields and ASCII only. I have not run it (unverified).

```yaml
version: "v1"
environment: ambient            # the only value custom flows accept
# coding_environment: none      # optional: "full" (default, repo clone) or "none" (API-only flow)

components:
  - name: "triage_agent"        # unique; no ":" or "." in names
    type: AgentComponent
    prompt_id: "triage_prompt"  # must match a prompts[].prompt_id below
    inputs:
      - "context:goal"          # what the trigger passed (see "Goal values" below)
      - from: "context:project_id"
        as: "project_id"
      - from: "context:inputs.workspace_agent_skills"
        as: "workspace_agent_skills"
        optional: true          # lets skills/<name>/SKILL.md load; harmless if none
    toolset:
      - "get_issue"
      - "list_issue_notes"
      - "create_issue_note"
    max_cycles: 20              # soft cap on the agent loop (default 280)
    ui_log_events:
      - "on_agent_final_answer"
      - "on_tool_execution_success"
      - "on_tool_execution_failed"

prompts:
  - prompt_id: "triage_prompt"
    name: "Triage prompt"
    unit_primitives: []
    prompt_template:
      system: |
        You are a careful on-call assistant. Use only the tools you have.
      user: |
        Project ID: {{project_id}}
        Task: {{goal}}
      placeholder: history      # optional now; the spec says history is added automatically
    params:
      timeout: 180              # seconds

routers:
  - from: "triage_agent"
    to: "end"                   # built-in; "abort" ends with an error status

flow:
  entry_point: "triage_agent"
```

The original February 2026 template ([flows/flow.yml.template](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template/-/blob/main/flows/flow.yml.template)). Its outer `name`, `description`, `public` and `definition` keys are the wrapper used by the repo sync job in the next section; in the UI editor you paste only what is under `definition:`, because the schema rejects top-level `name` and `description` (inference):

```yaml
name: "AI Hackathon Flow"
description: "A flow to..."
public: true
definition:
  version: v1
  environment: ambient
  
  # Components define the steps in your flow
  # Each component can be an Agent, DeterministicStep, or other component types
  components:
    - name: "my_agent"
      type: AgentComponent  # Options: AgentComponent, DeterministicStepComponent
      prompt_id: "my_prompt"  # References a prompt defined below
      inputs:
        - "context:goal"  # Input from user or previous component
      toolset: []  # Add tool names here: ["get_issue", "create_issue_note"], see https://gitlab.com/components/ai-catalog/-/blob/main/tool_mapping.json?ref_type=heads

      # Optional: UI logging
      ui_log_events:
        - on_agent_final_answer
        - on_tool_execution_success
  
  # Define your prompts here
  # Each prompt configures an AI agent's behavior
  prompts:
    - prompt_id: "my_prompt"  # Must match the prompt_id referenced above
      name: "My Agent Prompt"

      # System and user prompts define the agent's behavior
      prompt_template:
        system: |
          Only reply with "I'm a placeholder agent, please change my prompt"

        # Available variables depend on your inputs:
        # {{goal}} - The user's request
        # {{context}} - Additional context from previous steps
        user: |
          {{goal}}
        placeholder: history  # Maintains conversation context
      unit_primitives: []
      params:
        timeout: 180  # Seconds before timeout

  # Routers define the flow between components
  # Use "end" as the final destination
  routers:
    - from: "my_agent"
      to: "end"

    # Example: Multi-step flow
    # - from: "fetch_data"
    #   to: "process_data"
    # - from: "process_data"
    #   to: "my_agent"
    # - from: "my_agent"
    #   to: "end"

  # Define the entry point for your flow
  flow:
    entry_point: "my_agent"
```

A real flow that ran in June: the first-place "Design and Usability" winner Carver kept its flow in the repo as [flows/carver-handoff.flow.yml](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946/-/blob/main/flows/carver-handoff.flow.yml). It uses one `AgentComponent` with `inputs: ["context:goal", "context:project_id"]`, a local prompt with `unit_primitives: []` and `params: timeout: 300`, `routers: [{from: "carver_handoff_agent", to: "end"}]` and `flow: entry_point: "carver_handoff_agent"`. Its prompt says "`main` is NEVER modified - everything waits for a human to review and merge." The project ran 2 successful `duo_workflow` pipelines ([pipelines](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946/-/pipelines)).

### Flow components and syntax (from the v1 spec)

All from [flow_registry/v1.md](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md):

| Component | Required keys | What it does | Outputs you can read |
|---|---|---|---|
| `AgentComponent` | `name`, `type`, `prompt_id` | LLM loop with tools until done | `context:<name>.final_answer`, `conversation_history:<name>` |
| `DeterministicStepComponent` | `name`, `type`, `tool_name` | Runs exactly one tool, no LLM | `context:<name>.tool_responses`, `context:<name>.error`, `context:<name>.execution_result` ("success" or "failed") |
| `OneOffComponent` | `name`, `type`, `prompt_id`, `toolset` | One round of tool calls with retries (`max_correction_attempts`, default 3) | `context:<name>.tool_calls`, `.tool_responses`, `.execution_result` |
| `HumanInputComponent` | `name`, `type`, `sends_response_to`, `message_template` | Pauses for a person; `interaction_type: "approval"` (default) or `"input"` | `context:<name>.approval` ("approve" or "reject") |
| `end` / `abort` | none (built in) | Finish as COMPLETED or ERROR | |

Useful optional `AgentComponent` keys: `prompt_version` (omit to use a local prompt), `toolset`, `inputs` (default `["context:goal"]`), `max_cycles` (default 280, soft limit), `max_wrap_up_retries` (default 3), `identical_tool_call_limit`, `model_tags`, `compaction`, `ui_log_events`, `require_tool_approval` and `pre_approved_tools`, `subagents` with `max_delegations` (supervisor mode; each sub-agent needs a `description`).

Inputs. A plain string like `"context:goal"`, or an object:

```yaml
inputs:
  - from: "context:analyzer.final_answer"   # another component's output
    as: "analysis_results"                  # becomes {{analysis_results}} in the prompt
  - from: "config_backup.txt"
    as: "file_path"
    literal: true                           # pass a fixed value
```

Routers. Straight or by condition (the agent must answer with the exact route key):

```yaml
routers:
  - from: "validator"
    condition:
      input: "context:validator.final_answer"
      routes:
        "valid": "processor"
        "invalid": "abort"
  - from: "user_approval"
    condition:
      input: "context:user_approval.approval"
      routes:
        "approve": "execute_changes"
        "reject": "revise_proposal"
        "default_route": "manual_review"
  - from: "processor"
    to: "end"
```

Tool options (force a value the model cannot change):

```yaml
toolset:
  - "get_merge_request"
  - "create_merge_request_note":
      "internal": true
```

Human approval step (spec example):

```yaml
components:
  - name: "user_approval"
    type: HumanInputComponent
    sends_response_to: "code_assistant"
    interaction_type: "approval"
    message_template: "The code assistant has proposed the following changes: {{ proposed_changes }}. Do you approve?"
    inputs:
      - from: "context:code_assistant.final_answer"
        as: "proposed_changes"
```

Whether `HumanInputComponent` and `require_tool_approval` work in a custom `ambient` flow started by a trigger is not stated in the custom flow docs (unverified). The VS Code flow builder lists "**Human Input**: pauses the flow and waits for user input or approval before continuing" ([flows/custom.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom.md)). Test early.

Passing data between agents: the spec says outputs such as `context:<name>.final_answer` "can be used as inputs by other components". June participants reported the opposite: "Inter-agent data must flow through `conversation_history`; direct output references are not valid." ([team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)). Test both early.

### Goal values by trigger type

From [custom_flows_schema.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/custom_flows_schema.md):

- Mention: the goal is `Input: <comment_text>` and `Context: {<resource_type> IID: <iid>}`. Example: "Input: @ai-my-flow Can you work on this?" and "Context: {Issue IID: 2}".
- Assign and Assign reviewer: "the IID of the resource is passed as the goal". Example: "assigned as a reviewer on merge request `!10`, the value of `context:goal` is `10`." Read it together with `context:project_id`.
- Pipeline events: "the full pipeline event webhook payload is passed as the goal."
- "A flow can have multiple trigger types configured, and each trigger type passes a different value as `context:goal`. Your flow must handle the goal format for each trigger type you configure."

### Where flows run (execution environment)

- "Flows executed from the GitLab UI use CI/CD." The runner downloads the GitLab Duo CLI binary and connects to the GitLab Duo Workflow Service ([flows/execution/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/execution/_index.md)).
- In the reference project each session shows up as a pipeline with source `duo_workflow`, ref `refs/workloads/<id>`, one job `workload` in stage `build`, on a GitLab-hosted runner with tag `gitlab--duo`. The Developer flow job took about 97 seconds; the next workload, which by its timing was the code review session (inference), took about 201 seconds ([pipeline 2905826919](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2905826919), [pipeline 2905830631](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2905830631)).
- Config file: `.gitlab/duo/agent-config.yml`. "The configuration file is read-only from the project's default branch. Files committed to other branches are ignored, even when a flow runs from those branches." Keys ([agent-config-yaml.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/execution/agent-config-yaml.md)): `image`, `setup_script`, `cache` (`paths`, `key`, `key.files` max 2, `key.prefix`), `network_policy` (`allowed_domains`, `denied_domains`, `include_recommended_allowed`, `allow_all_unix_sockets`), and `id_tokens` (added in 19.2, [execution/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/execution/_index.md)).
- `setup_script` runs outside the sandbox: "These commands have access to all environment variables in the flow, including the triggering user's OAuth token, service token, and identity details."
- Variables ([execution-variables.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/execution/execution-variables.md)):
  - Available: `CI_PROJECT_ID`, `CI_PROJECT_PATH`, `CI_DEFAULT_BRANCH`, `CI_JOB_TOKEN`, `CI_PIPELINE_URL`, `CI_WORKLOAD_REF` and others; `GITLAB_BASE_URL`, `GITLAB_PROJECT_PATH`, `GITLAB_TOKEN`, `DUO_WORKFLOW_GOAL` ("URL of the issue that triggered the flow"), `DUO_WORKFLOW_GIT_USER_NAME` and `_EMAIL` (triggering human), `DUO_WORKFLOW_GIT_AUTHOR_USER_NAME` and `_EMAIL` (service account).
  - Not available: `CI_SERVER_URL`, `CI_API_V4_URL`, `CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_COMMIT_SHA`, `CI_COMMIT_BRANCH`, `GITLAB_USER_LOGIN`, `CI_PIPELINE_SOURCE`.
  - "Custom CI/CD variables defined in **Settings** > **CI/CD** > **Variables** for projects, groups, or the instance are not available." So a flow cannot read a secret you put in CI/CD variables. For outside services use `id_tokens` (OIDC) in `agent-config.yml`.
- Network ([environment_sandbox.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/environment_sandbox.md)): with the default image (it includes the Anthropic Sandbox Runtime), flows reach only `localhost`, `host.docker.internal`, your GitLab domain and the Duo Workflow Service, plus what you add under `network_policy.allowed_domains` (no `"*"`, but `"*.domain.com"` works). "If you use a custom image without SRT, no network restrictions are applied". A group Owner can run "Strict mode", where `allowed_domains` from `agent-config.yml` "are ignored". Whether our hackathon group uses strict mode is unknown (unverified).
- Flows need at least one commit in the repo; flows need a runner with tag `gitlab--duo` (hosted runners qualify); if the namespace runs out of compute minutes, flows do not start ([troubleshooting.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/troubleshooting.md)).

### Skills

From [agent_skills.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/customize/agent_skills.md) and the page:

- Location: `skills/<skill-name>/SKILL.md` at the project root. "The `name` and `description` YAML front matter fields are required."

```markdown
---
name: <skill_name>
description: <skill_description>
---

<your_instructions_and_context_for_the_skill>
```

- Where skills work in the GitLab UI: "only foundational and custom flows, excluding Code Review, support project-level skills. GitLab Duo Chat in the GitLab UI does not support skills."
- Custom flows must read them through an input. The docs snippet (its indentation is broken in the docs; this is the same content with the indentation fixed):

```yaml
components:
  - name: "my_agent"
    type: AgentComponent
    prompt_id: "my_prompt"
    inputs:
      - from: "context:inputs.workspace_agent_skills"
        as: "workspace_agent_skills"
        optional: true
```

- Optional slash command: add `metadata:` with `slash-command: enabled` to the front matter, then use `/<skill_name>`.
- "Existing conversations and flows do not have access to new or updated skills automatically." The page: "Start a **new** conversation or flow each time you change `SKILL.md` to avoid context confusion."
- From the June thread: a skill can be a directory with `SKILL.md` plus `references/`; "If we copy a single file, it won't work properly." ([team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137), comment by dgruzd, 2026-05-06)

### Triggers

From [triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md) (Tier: Premium, Ultimate; needs Maintainer or Owner):

- Create: **AI** > **Triggers** > **New flow trigger**, add conditions one at a time (**Add condition** > **On an event**), pick the **Service account**, then **Configuration source**: **AI Catalog** (a flow configured for the project) or **Configuration path** (a YAML file such as `.gitlab/duo/flows/claude.yaml`, only with feature flag `ai_catalog_create_third_party_flows`). You can also enable a flow with triggers in one step from the flow page.

| Event | When | Options |
|---|---|---|
| Mention | "When the service account user is mentioned in a comment on an issue or merge request." | none |
| Assign | "When the service account user is assigned to an issue or merge request." | none |
| Assign reviewer | "When the service account user is assigned as a reviewer to a merge request." | none |
| Pipeline events | "When a pipeline changes state." | Running, Passed, Failed, Canceled |
| Merge request | "When a selected merge request action occurs." | Approved, Created (19.4), Marked ready, Merge conflict |
| Work item | "When a selected work item action occurs." | Created, Status changed (can filter by status) |

- The human rule, word for word: "All trigger event types require a human user to perform the triggering action. A non-human user such as a bot user, service account user, or another flow, cannot activate a trigger. This restriction applies to all trigger event types. For example, a flow cannot trigger another flow by mentioning the service account in a comment."
- Cost: "A flow started by a trigger runs as the trigger's service account, which makes the service account the billing subject for the flow's GitLab Credits consumption."
- Triggers can be turned off and on without deleting them (19.4).

### Starting a flow from outside GitLab (Flows API)

From [api/duo_agent_platform_flows.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md) (Tier: Premium, Ultimate):

- `POST /api/v4/ai/duo_workflows/workflows` with `project_id`, `goal`, `start_workflow: true` and either `workflow_definition` (built-in, for example `developer/v1`) or `ai_catalog_item_consumer_id` (your custom flow, must already be enabled in the project).
- Find the consumer ID with GraphQL `aiCatalogConfiguredItems(projectId: "gid://gitlab/Project/<id>")`; use the number at the end of `gid://gitlab/AiCatalogItemConsumer/<n>`.
- Other attributes: `issue_id`, `merge_request_id`, `source_branch`, `image`, `allow_agent_to_request_user`, `agent_privileges`.
- Errors: "403 Forbidden - Identity verification is required to use GitLab Duo Agent Platform" if your account needs identity verification.
- Flow lifecycle callbacks to a webhook (`callback_hook_id`) are an experiment behind flag `duo_flow_callback_hooks`, "Disabled by default" ([webhook_callbacks.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/webhook_callbacks.md)).
- This is the documented way for a non-GitLab event (for example a production alert) to start a flow. Whether a call made with a bot or service token counts as "human" for flows is not documented (unverified).

### Built-in (foundational) flows used by the reference project

- Developer flow: "mention `@duo-developer-<namespace>` in a comment", or assign the Duo Developer service account to an issue ([developer.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/merge_requests/developer.md)). The account pattern is "`duo-[flow-name]-[top-level-group-name]`" ([troubleshooting.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/troubleshooting.md)). In `gitlab-org` it is `duo-developer-gitlab-org`; in our group it should be `duo-developer-gitlab-ai-hackathon` (inference). It opens a draft MR on a `duo/feature/<iid>-...` branch (seen in the reference run).
- Code Review flow: assign `@GitLabDuo` as reviewer, or `/assign_reviewer @GitLabDuo`, or turn on automatic reviews; automatic reviews skip draft MRs ("For GitLab Duo to review the merge request, mark it ready.") ([code_review/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/foundational_flows/code_review/_index.md)). Custom review rules live in `.gitlab/duo/mr-review-instructions.yaml` ([review_instructions.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/customize/review_instructions.md)). Skills do not apply to Code Review.
- Others listed in [foundational_flows/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/flows/foundational_flows/_index.md): Fix CI/CD Pipeline, SAST Vulnerability Resolution, SAST False Positive Detection, Secret False Positive Detection, Security Review, Recommend Reviewers, Software Development, Convert to GitLab CI/CD, Agentic Breaking Change Resolution.
- `AGENTS.md` at the repo root is read by agentic flows (since GitLab 18.8) ([agents_md.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/customize/agents_md.md)). Our repo's AGENTS.md will be read by Duo flows too.

### External agents (bring Claude Code or Codex)

- GitLab-managed external agents: "The [Claude Code Agent by GitLab](https://gitlab.com/explore/ai-catalog/agents/2337/) uses GitLab-managed credentials and does not require additional configuration." Same for the Codex Agent ([agents/external.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/external.md)).
- Tier Premium, Ultimate, and: "The availability of this feature is controlled by a feature flag and enabled for verified customers." Whether it works in the hackathon group is unknown (unverified). External agents can be triggered like flows.

## The reference project end to end

### What it is

- Name: "Hello World Showcase - reference only". Description and first line of the README: "⚠️ This is a reference project, not a starter template." ([project](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase), [README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md))
- Built by Missy Davies, the Transcend III DRI. Created 2026-09-02. Her 2026-09-10 status: "started building `Hello World Showcase` sample project and scripting demo video" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)).
- The app is deliberately tiny: a Flask task API (`/`, `/health`, `/status`, `/api/tasks` CRUD, `/api/tasks/count`, `/api/tasks/stats`) with an in-memory store and 11 pytest tests ([app/main.py](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/app/main.py), [tests/test_api.py](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/tests/test_api.py)). AGENTS.md: "Keep the app deliberately simple. Complexity belongs in the pipeline and agent automation, not the application." ([AGENTS.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/AGENTS.md))
- README on cloud: "Deployment to Google Cloud is optional for the hackathon. Swap the `deploy-*` jobs for your own target if you prefer."
- There is no custom flow, custom agent or skill in this repo. It uses built-in flows only (Developer, Code Review, SAST Vulnerability Resolution) plus CI glue.

### Files

| File | Purpose |
|---|---|
| [.gitlab-ci.yml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml) | Pipeline: tests, scans, build, staging, smoke test, production, release, issue comment, agent MR glue |
| [.gitlab/duo/agent-config.yml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab/duo/agent-config.yml) | Flow execution image, setup script, cache, network policy |
| [.gitlab/duo/mr-review-instructions.yaml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab/duo/mr-review-instructions.yaml) | Custom rules for GitLab Duo Code Review |
| [AGENTS.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/AGENTS.md) | Context and rules for Duo flows ("When implementing issues" list) |
| [.gitlab/issue_templates/feature.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab/issue_templates/feature.md) | Issue template with acceptance criteria, adds label `type::feature` |
| [.gitlab/merge_request_templates/default.md](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab/merge_request_templates/default.md) | MR template with "Closes #" and a checklist |
| [Dockerfile](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/Dockerfile) | `python:3.12-slim`, gunicorn with 1 worker on port 8080 |
| `app/`, `tests/`, `requirements.txt` | Flask app, tests, `flask==3.1.1`, `gunicorn==23.0.0`, `pytest==8.3.5` |

### Every stage and job in .gitlab-ci.yml

Stages, in order: `test`, `build`, `deploy`, `validate`, `release`. Global variables: `CONTAINER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA`, `GCP_REGION: us-central1`, `GCP_SERVICE_NAME: hello-world-showcase`, `GCP_AR_IMAGE: us-central1-docker.pkg.dev/$GCP_PROJECT_ID/hello-world-showcase/app:$CI_COMMIT_SHORT_SHA`. Included templates: `Security/SAST.gitlab-ci.yml`, `Security/Dependency-Scanning.gitlab-ci.yml`, `Security/Secret-Detection.gitlab-ci.yml`, `Security/Container-Scanning.gitlab-ci.yml`, `Jobs/Code-Quality.gitlab-ci.yml` ([.gitlab-ci.yml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml)).

| Job | Stage | Runs when | What it does |
|---|---|---|---|
| `unit-tests` | test | every pipeline | `pytest tests/ --junitxml=report.xml -v` on `python:3.12-slim`, JUnit report |
| `lint` | test | every pipeline | `flake8 app/ tests/ --max-line-length=120` |
| SAST, dependency scanning, secret detection, code quality | test | from templates | Seen as `semgrep-sast`, `gemnasium-python-dependency_scanning`, `secret_detection`, `code_quality` (allowed to fail) in [pipeline 2905838409](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2905838409) |
| `ready-for-review` | test | MR pipelines on `duo/*` branches | Strips "Draft:" from the MR title with the API, then arms auto-merge (`merge_when_pipeline_succeeds=true&squash=true&should_remove_source_branch=true`), using `$AUTO_MERGE_TOKEN` |
| `build-image` | build | default branch | Docker in Docker; pushes `$CI_REGISTRY_IMAGE:<sha>` and `:latest`; logs in to Artifact Registry with `_json_key` from `$GCP_SERVICE_KEY`; pushes `$GCP_AR_IMAGE` |
| `container_scanning` | build | default branch | Scans `$CONTAINER_IMAGE`, `allow_failure: true` |
| `deploy-staging` | deploy | default branch | `gcloud run deploy hello-world-showcase-staging --image $GCP_AR_IMAGE --region us-central1 --platform managed --allow-unauthenticated --set-env-vars APP_VERSION=$CI_COMMIT_SHORT_SHA`; writes `STAGING_URL` to a dotenv report; environment `staging` |
| `validate-staging` | validate | default branch, `needs: deploy-staging` | `curl $STAGING_URL/health` must be 200, reads `/status`, creates and deletes a task |
| `wait-for-duo-review` | validate | MR pipelines on `duo/*`, `needs: ready-for-review`, `timeout: 20m` | Polls MR notes 60 times every 15 s for a non-system note by `GitLabDuo`; fails if it matches `critical|security vulnerability|command injection`; fails on timeout |
| `deploy-production` | release | default branch, `needs: validate-staging` | Same `gcloud run deploy` for service `hello-world-showcase`; writes `PRODUCTION_URL` dotenv; environment `production` |
| `create-release` | release | default branch, `needs: deploy-production` | `release-cli create` with tag `v1.0.${CI_PIPELINE_IID}`, description from the commit message and the `Closes #N` reference, asset links to the production URL and the container registry |
| `notify-issue` | release | default branch, `needs: deploy-production, create-release` | Finds `Closes|Resolves|Fixes #N` in the commit message, posts "Deployed to production" with the live URL, release link, pipeline link and `/status` JSON on issue N |

### Cloud Run deploy and the auth method

- Auth is a long-lived service account key: `GCP_SERVICE_KEY` is a File-type CI/CD variable holding "Service account JSON with Cloud Run and Artifact Registry permissions"; jobs run `gcloud auth activate-service-account --key-file="$GCP_SERVICE_KEY"` and `docker login -u _json_key` ([README](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/README.md), [.gitlab-ci.yml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml)).
- Required CI/CD variables (README): `AUTO_MERGE_TOKEN` ("Project access token (Maintainer, `api` scope) used to mark MRs ready, arm auto-merge, and comment on issues"), `GCP_PROJECT_ID`, `GCP_SERVICE_KEY`.
- Environments (read through GraphQL): `production` at https://hello-world-showcase-tmepbnfv7q-uc.a.run.app and `staging` at https://hello-world-showcase-staging-tmepbnfv7q-uc.a.run.app; last production deploy 2026-10-05 21:29 to 21:30 UTC by job `deploy-production` ([environments](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/environments)).
- Our project rule is keyless auth (Workload Identity Federation). GitLab documents it two ways: `id_tokens` in the CI job plus a token exchange with Google STS ([ci/cloud_services/google_cloud/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/google_cloud/_index.md)), or the **Settings** > **Integrations** > **Google Cloud IAM** guided setup with the `identity: google_cloud` keyword ([google_cloud_iam.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/integration/google_cloud_iam.md)). The pool ID, provider ID, project number and service account email are not secrets, so they can sit in `.gitlab-ci.yml` and no CI/CD variable is needed (inference). Flows can also get OIDC tokens through `id_tokens` in `agent-config.yml`.

### The loop from issue to production, and what triggers each step

The README, word for word:

> **The hands-off loop**
>
> 1. Create an issue describing a small change and assign it to `duo-developer-gitlab-org`.
> 2. The Duo Developer flow implements it and opens a merge request on a `duo/*` branch.
> 3. The MR pipeline marks the MR ready, arms auto-merge, and waits for GitLab Duo Code Review to finish without critical findings.
> 4. On merge, the main pipeline runs tests, builds the image, runs SAST, dependency, secret and container scans, deploys to staging, smoke-tests it, promotes to production, cuts a tagged GitLab Release, and posts a summary with the live URL and release link back on the issue.
>
> Nothing in steps 2 to 4 requires a human.
>
> **Replicating this**
>
> Set these CI/CD variables on your project:
>
> | Variable | Type | Purpose |
> |---|---|---|
> | `AUTO_MERGE_TOKEN` | masked | Project access token (Maintainer, `api` scope) used to mark MRs ready, arm auto-merge, and comment on issues |
> | `GCP_PROJECT_ID` | variable | Google Cloud project for Cloud Run |
> | `GCP_SERVICE_KEY` | file | Service account JSON with Cloud Run and Artifact Registry permissions |
>
> Deployment to Google Cloud is optional for the hackathon. Swap the `deploy-*` jobs for your own target if you prefer.

| Step | Triggered by | Who acts |
|---|---|---|
| 1. Issue assigned to `duo-developer-gitlab-org` (or mention) | A person | Human |
| 2. Developer flow session (workload pipeline, `duo_workflow`) writes code, runs tests, pushes `duo/feature/<iid>-...`, opens a draft MR with "Closes #<iid>" | Assign or Mention trigger of the Developer flow | Service account `duo-developer-gitlab-org` |
| 3. MR pipeline: `ready-for-review` strips "Draft:", arms auto-merge | Push to a `duo/*` branch with an open MR (rule `$CI_MERGE_REQUEST_IID && $CI_COMMIT_REF_NAME =~ /^duo\//`) | CI with `AUTO_MERGE_TOKEN` (project bot) |
| 4. GitLab Duo Code Review session posts a review | The MR became ready while automatic reviews are on (the system note shows the bot "requested review from @GitLabDuo") | `GitLabDuo` |
| 5. `wait-for-duo-review` passes, pipeline succeeds, auto-merge merges | Review note without the blocking words | CI, then the project bot merges |
| 6. Main pipeline: tests, scans, build, staging, smoke test, production, release | Merge commit on `main` | CI |
| 7. `notify-issue` comments on the issue | `Closes #N` in the commit message | Project bot |

Note: step 4 started even though a bot marked the MR ready. Automatic code review is a project setting, not a flow trigger, so the human-only trigger rule did not block it (observed in [MR !5](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/merge_requests/5); inference about the reason).

### A real run, minute by minute (issue #4, 2026-10-02, UTC)

From the notes of [issue #4](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/work_items/4) and [MR !5](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/merge_requests/5) (read through GraphQL), and the [pipelines list](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines):

| Time | Event |
|---|---|
| 08:03:15 | missy-gitlab assigns the issue to `@duo-developer-gitlab-org` |
| 08:03:16 | Developer posts "✅ Duo Developer has started." with a link to [session 8933788](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/automate/agent-sessions/8933788); workload pipeline 2905826919 starts |
| 08:04:39 | MR !5 opened from `duo/feature/4-add-task-stats-endpoint`, assigned to the human |
| 08:04:44 | Developer comments: "@missy-gitlab I opened !5, which adds `GET /api/tasks/stats` (`TaskStore.stats()` helper, route and test). `pytest tests/ -v` (11 passed) and flake8 both pass locally." |
| 08:04:52 | Project bot marks the MR ready; review requested from `@GitLabDuo`; 08:04:54 auto-merge armed |
| 08:08:13 | GitLabDuo: "I finished my review and found nothing to comment on. Nice work! :tada:" |
| 08:08:19 | Merged by `project_86033682_bot_...` as commit `7e0b4222`; issue set to Complete |
| 08:08 to 08:18 | Main [pipeline 2905838409](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2905838409): unit-tests 17 s, lint 10 s, semgrep-sast 33 s, dependency scanning 40 s, secret detection 11 s, code quality 231 s, build-image 43 s, container scanning 40 s, deploy-staging 75 s, validate-staging 11 s, deploy-production 47 s, create-release 9 s, notify-issue 8 s |
| 08:18:31 | Bot comments "## Deployed to production :rocket:" with the live URL and [release v1.0.56](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/releases/v1.0.56) |

About 15 minutes from assignment to the production comment, with one human action.

### Other runs worth knowing

- Issue #3 / MR !4 (2026-10-01): the first MR pipeline failed in `ready-for-review` ([pipeline 2904344237](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2904344237)). The fix commit [b01050dc](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/b01050dc) "Mark agent MRs ready by stripping the Draft prefix from the title" replaced `--data '{"draft": false}'` with a title edit. The job log needs sign-in, so the exact error is unknown (unverified).
- The Developer flow noticed the hands-off rule and said so: "Heads-up: AGENTS.md says `duo/*` MRs are marked ready and auto-merged straight through to production with no manual gates." ([issue #3](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/work_items/3))
- MR !1 (planted bug): GitLab Duo Code Review flagged "a critical shell command injection vulnerability in the new `search_tasks` endpoint" and suggested a fix. Earlier attempts on that MR failed with ":warning: Something went wrong and the review request was stopped. Please request a new review." ([MR !1](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/merge_requests/1))
- MR !2: the SAST Vulnerability Resolution flow (service account `duo-resolve-sast-vulnerability-gitlab-org`) opened a fix MR. Code Review then failed with "Something went wrong while starting Code Review Flow" and "Error code: DCR5000". The MR's first pipeline failed `unit-tests`; a human pushed a test fix and merged ([MR !2](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/merge_requests/2), [pipeline 2834677284](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines/2834677284)).
- Totals on 2026-10-06: 59 pipelines (push: 31 success, 8 failed; `duo_workflow`: 10 success, 2 failed; MR: 3 success, 1 failed; `security_orchestration_policy`: 4 success), 5 issues, 5 MRs, 4 releases (`v1.0.0`, `v1.0.50`, `v1.0.56`, `v1.0.58`) ([pipelines](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/pipelines), [releases](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/releases)). The two failed `duo_workflow` runs were on 2026-09-08, before the image fix below.
- Issue #5 is a test copy of the October onboarding issue with the template variable unrendered ("`<%= group_url %>`") ([issue #5](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/work_items/5)).

### Fixes found in the commit history

| Commit | Lesson (commit message, word for word) |
|---|---|
| [da3e3929](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/da3e3929) | "python:3.12-slim lacks git, which Duo flows need to clone the repo during code review sessions." |
| [c6c861ea](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/c6c861ea) | "GCP_SERVICE_KEY is a file-type variable, so use --key-file directly instead of piping through echo." |
| [6b855f3c](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/6b855f3c) | "TaskStore is in-memory (per-process). With 2 workers, each had its own copy of the task list, causing requests load-balanced between workers to return inconsistent state. Use 1 worker since there is no shared backend database." |
| [68436ab9](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/68436ab9) | "Environment URLs now use actual Cloud Run URLs from gcloud instead of templated URLs with missing variables." |
| [809ffd70](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/809ffd70) | "Merge requests on duo/* branches are now marked ready and armed for auto-merge by CI, then gated on GitLab Duo Code Review finishing with no critical findings. After production deploys, CI posts a summary with the live URL back on the originating issue." Same commit made container scanning non-blocking and changed the review rule from "Production deploys must require manual approval." to "Production deploys must depend on the staging validation job." |
| [182a6c1e](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/182a6c1e) | "Configure Python 3.12 image, pip caching, and network policy for Duo foundational flows (code review, security review, SAST resolution, pipeline fix)." |

### What we can copy, and what we cannot

- Copy: the stage layout, staging then smoke test then production, the dotenv hand-off of URLs, the release job, the issue comment, the `AGENTS.md` "When implementing issues" rules, `mr-review-instructions.yaml`, and the `agent-config.yml` with a full image that has git.
- Cannot copy as is in our workspace (inference from the role section): `AUTO_MERGE_TOKEN` is a Maintainer project token, and our base role is Developer; CI/CD variables may be Maintainer-only; `main` merges may be Maintainer-only.
- Should not copy: the JSON key (our rule is keyless WIF), and "There are no manual gates anywhere in the loop" (our rule: a human decides when the agent acts on anything that matters). Note the theme pulls the other way, see the epic quote in the lessons section.

### Full config files (word for word)

`.gitlab/duo/agent-config.yml`:

```yaml
image: python:3.12
setup_script:
  - pip install -r requirements.txt
cache:
  key:
    files:
      - requirements.txt
    prefix: python-deps
  paths:
    - .cache/pip
network_policy:
  include_recommended_allowed: true
```

`.gitlab/duo/mr-review-instructions.yaml`:

```yaml
instructions:
  - name: security
    fileFilters:
      - "app/**/*.py"
    instructions: |
      Check for hardcoded secrets, credentials, or API keys.
      Verify that user input is validated before use.
      Flag any use of string formatting for SQL or shell commands, and any subprocess call with shell=True.
  - name: testing
    fileFilters:
      - "app/**/*.py"
      - "tests/**/*.py"
    instructions: |
      Every new endpoint or behavior change must have a corresponding test in tests/test_api.py.
      Tests must use the Flask test client fixture.
  - name: api_consistency
    fileFilters:
      - "app/**/*.py"
    instructions: |
      All API endpoints must return JSON via jsonify.
      Error responses must include an "error" key with a human-readable message.
      Use standard HTTP status codes: 200, 201, 400, 404.
  - name: dockerfile
    fileFilters:
      - "Dockerfile"
    instructions: |
      The Dockerfile must use a slim base image.
      Dependencies must be installed before copying application code (layer caching).
      No secrets or credentials in the Dockerfile.
  - name: pipeline
    fileFilters:
      - ".gitlab-ci.yml"
    instructions: |
      Changes to .gitlab-ci.yml must not remove security scanning templates.
      Deploy jobs must only run on the default branch.
      Production deploys must depend on the staging validation job.
```

`.gitlab-ci.yml`:

````yaml
stages:
  - test
  - build
  - deploy
  - validate
  - release

variables:
  DOCKER_TLS_CERTDIR: "/certs"
  CONTAINER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  GCP_REGION: us-central1
  GCP_SERVICE_NAME: hello-world-showcase
  GCP_AR_IMAGE: us-central1-docker.pkg.dev/$GCP_PROJECT_ID/hello-world-showcase/app:$CI_COMMIT_SHORT_SHA

include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Jobs/Code-Quality.gitlab-ci.yml

# ---------------------------------------------------------------------------
# TEST
# ---------------------------------------------------------------------------
unit-tests:
  stage: test
  image: python:3.12-slim
  before_script:
    - pip install --quiet -r requirements.txt
  script:
    - pytest tests/ --junitxml=report.xml -v
  artifacts:
    reports:
      junit: report.xml

lint:
  stage: test
  image: python:3.12-slim
  before_script:
    - pip install --quiet flake8
  script:
    - flake8 app/ tests/ --max-line-length=120

# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
build-image:
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CONTAINER_IMAGE .
    - docker tag $CONTAINER_IMAGE $CI_REGISTRY_IMAGE:latest
    - docker push $CONTAINER_IMAGE
    - docker push $CI_REGISTRY_IMAGE:latest
    - cat "$GCP_SERVICE_KEY" | docker login -u _json_key --password-stdin https://us-central1-docker.pkg.dev
    - docker tag $CONTAINER_IMAGE $GCP_AR_IMAGE
    - docker push $GCP_AR_IMAGE
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

container_scanning:
  stage: build
  allow_failure: true
  variables:
    CS_IMAGE: $CONTAINER_IMAGE
  needs:
    - job: build-image
      artifacts: true
      optional: true
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ---------------------------------------------------------------------------
# DEPLOY - Staging (automatic on main)
# ---------------------------------------------------------------------------
deploy-staging:
  stage: deploy
  image: google/cloud-sdk:slim
  environment:
    name: staging
    url: $STAGING_URL
  before_script:
    - gcloud auth activate-service-account --key-file="$GCP_SERVICE_KEY"
    - gcloud config set project $GCP_PROJECT_ID
  script:
    - |
      gcloud run deploy $GCP_SERVICE_NAME-staging \
        --image $GCP_AR_IMAGE \
        --region $GCP_REGION \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars APP_VERSION=$CI_COMMIT_SHORT_SHA \
        --quiet
    - STAGING_URL=$(gcloud run services describe $GCP_SERVICE_NAME-staging --region $GCP_REGION --format 'value(status.url)')
    - echo "STAGING_URL=$STAGING_URL" >> deploy.env
  artifacts:
    reports:
      dotenv: deploy.env
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ---------------------------------------------------------------------------
# DEPLOY - Production (auto after staging validation)
# ---------------------------------------------------------------------------
deploy-production:
  stage: release
  image: google/cloud-sdk:slim
  environment:
    name: production
    url: $PRODUCTION_URL
  before_script:
    - gcloud auth activate-service-account --key-file="$GCP_SERVICE_KEY"
    - gcloud config set project $GCP_PROJECT_ID
  script:
    - |
      gcloud run deploy $GCP_SERVICE_NAME \
        --image $GCP_AR_IMAGE \
        --region $GCP_REGION \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars APP_VERSION=$CI_COMMIT_SHORT_SHA \
        --quiet
    - PRODUCTION_URL=$(gcloud run services describe $GCP_SERVICE_NAME --region $GCP_REGION --format 'value(status.url)')
    - echo "PRODUCTION_URL=$PRODUCTION_URL" >> prod.env
  artifacts:
    reports:
      dotenv: prod.env
  needs:
    - validate-staging
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ---------------------------------------------------------------------------
# VALIDATE - Post-deploy smoke test
# ---------------------------------------------------------------------------
validate-staging:
  stage: validate
  image: curlimages/curl:latest
  needs:
    - deploy-staging
  script:
    - echo "Validating staging deployment at $STAGING_URL"
    - |
      HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$STAGING_URL/health")
      if [ "$HTTP_STATUS" != "200" ]; then
        echo "Health check failed with status $HTTP_STATUS"
        exit 1
      fi
      echo "Health check passed"
    - |
      STATUS=$(curl -s "$STAGING_URL/status")
      echo "Service status: $STATUS"
    - |
      TASK=$(curl -s -X POST "$STAGING_URL/api/tasks" \
        -H "Content-Type: application/json" \
        -d '{"title": "Smoke test task"}')
      echo "Created task: $TASK"
      TASK_ID=$(echo $TASK | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
      curl -s -X DELETE "$STAGING_URL/api/tasks/$TASK_ID"
      echo "Smoke test passed"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ---------------------------------------------------------------------------
# AGENT MR LIFECYCLE - runs on merge requests from duo/* branches
# ---------------------------------------------------------------------------
.duo-mr:
  image: alpine:latest
  before_script:
    - apk add --no-cache curl jq
  variables:
    MR_API: "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}"
  rules:
    - if: $CI_MERGE_REQUEST_IID && $CI_COMMIT_REF_NAME =~ /^duo\//

ready-for-review:
  extends: .duo-mr
  stage: test
  script:
    - |
      TITLE=$(curl --silent --fail --header "PRIVATE-TOKEN: $AUTO_MERGE_TOKEN" "$MR_API" | jq -r '.title')
      READY_TITLE=$(echo "$TITLE" | sed -E 's/^((\[?Draft\]?|\(Draft\)|WIP):?[[:space:]]*)+//I')
      echo "Marking MR !$CI_MERGE_REQUEST_IID ready for review: \"$READY_TITLE\""
      curl --silent --show-error --fail-with-body --request PUT \
        --header "PRIVATE-TOKEN: $AUTO_MERGE_TOKEN" \
        --header "Content-Type: application/json" \
        --data "$(jq -n --arg t "$READY_TITLE" '{title: $t}')" \
        "$MR_API" > /dev/null
      echo "Arming auto-merge"
      curl --silent --show-error --fail-with-body --request PUT \
        --header "PRIVATE-TOKEN: $AUTO_MERGE_TOKEN" \
        "$MR_API/merge" \
        --data "merge_when_pipeline_succeeds=true&squash=true&should_remove_source_branch=true" > /dev/null
      echo "Done. Merge will happen once this pipeline passes."

wait-for-duo-review:
  extends: .duo-mr
  stage: validate
  needs:
    - ready-for-review
  timeout: 20m
  script:
    - |
      echo "Waiting for GitLab Duo Code Review on !$CI_MERGE_REQUEST_IID"
      for i in $(seq 1 60); do
        NOTES=$(curl --silent --header "PRIVATE-TOKEN: $AUTO_MERGE_TOKEN" \
          "$MR_API/notes?per_page=100&order_by=created_at&sort=desc")
        REVIEW=$(echo "$NOTES" | jq -r '
          [.[] | select(.system == false and .author.username == "GitLabDuo"
                        and (.body | test("Processing|started|review session"; "i") | not))]
          | first // empty | .body')
        if [ -n "$REVIEW" ]; then
          echo "Review received:"
          echo "$REVIEW" | head -c 1500; echo
          if echo "$REVIEW" | grep -qiE "critical|security vulnerability|command injection"; then
            echo "Duo flagged a critical finding. Blocking merge."
            exit 1
          fi
          echo "No blocking findings. Clearing the gate."
          exit 0
        fi
        echo "[$i/60] no review yet, waiting 15s"
        sleep 15
      done
      echo "Timed out waiting for Duo Code Review. Blocking merge."
      exit 1

# ---------------------------------------------------------------------------
# NOTIFY - report the production deployment back on the originating issue
# ---------------------------------------------------------------------------
create-release:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  needs:
    - deploy-production
  variables:
    GIT_STRATEGY: none
  script:
    - |
      RELEASE_TAG="v1.0.${CI_PIPELINE_IID}"
      MR_TITLE=$(echo "$CI_COMMIT_MESSAGE" | sed -n '3p')
      [ -z "$MR_TITLE" ] && MR_TITLE="$CI_COMMIT_TITLE"
      ISSUE_REF=$(echo "$CI_COMMIT_MESSAGE" | grep -oiE '(Closes|Resolves|Fixes) #[0-9]+' | head -1 || true)
      echo "RELEASE_TAG=$RELEASE_TAG" >> release.env
      DESCRIPTION=$(printf '## %s\n\n%s\n\nBuilt from `%s` by pipeline %s.\n\nReviewed by GitLab Duo, scanned, deployed to staging, smoke-tested and promoted to production automatically.' \
        "$MR_TITLE" "$ISSUE_REF" "$CI_COMMIT_SHORT_SHA" "$CI_PIPELINE_URL")
      release-cli create \
        --name "$RELEASE_TAG" \
        --tag-name "$RELEASE_TAG" \
        --ref "$CI_COMMIT_SHA" \
        --description "$DESCRIPTION" \
        --assets-link "{\"name\":\"Production\",\"url\":\"${PRODUCTION_URL}\",\"link_type\":\"other\"}" \
        --assets-link "{\"name\":\"Container image ${CI_COMMIT_SHORT_SHA}\",\"url\":\"${CI_PROJECT_URL}/container_registry\",\"link_type\":\"image\"}"
  artifacts:
    reports:
      dotenv: release.env
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

notify-issue:
  stage: release
  image: alpine:latest
  needs:
    - deploy-production
    - create-release
  before_script:
    - apk add --no-cache curl jq
  script:
    - |
      ISSUE_IID=$(echo "$CI_COMMIT_MESSAGE" | grep -oiE '(Closes|Resolves|Fixes) #[0-9]+' | grep -oE '[0-9]+' | head -1 || true)
      if [ -z "$ISSUE_IID" ]; then
        echo "No issue reference in commit message, nothing to notify"
        exit 0
      fi
      STATUS=$(curl --silent "$PRODUCTION_URL/status")
      RELEASE_URL="${CI_PROJECT_URL}/-/releases/${RELEASE_TAG}"
      BODY=$(jq -n --arg sha "$CI_COMMIT_SHORT_SHA" --arg url "$PRODUCTION_URL" \
        --arg pipeline "$CI_PIPELINE_URL" --arg status "$STATUS" \
        --arg tag "$RELEASE_TAG" --arg release "$RELEASE_URL" '{
        body: ("## Deployed to production :rocket:\n\n" +
               "Commit `" + $sha + "` is live at " + $url + "\n\n" +
               "Release: [" + $tag + "](" + $release + ")\n\n" +
               "Pipeline: " + $pipeline + "\n\n" +
               "Tests, security scans, staging deploy and smoke test all passed before promotion.\n\n" +
               "```json\n" + $status + "\n```")}')
      curl --silent --fail --request POST \
        --header "PRIVATE-TOKEN: $AUTO_MERGE_TOKEN" \
        --header "Content-Type: application/json" \
        --data "$BODY" \
        "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/issues/${ISSUE_IID}/notes" > /dev/null
      echo "Posted deployment summary on issue #$ISSUE_IID"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
````

## Lessons from the June 2026 edition

### Numbers

From the 2026-07-13 update in [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137) and [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245):

- 1,576 developers registered, 318 submissions, 265 eligible for judging in the Showcase track, 219 with substantive "Challenges" text.
- Contribute track: 26 contributors merged 61 MRs.
- 8 winners: first and second in four categories.
- October so far: "667 folks registered so far" on 2026-10-05; target "5,000 registrations and 500 submissions" ([epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40)).

### How June was judged and what won (word for word)

The 2026-07-13 update by mmichaux-ext in [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137):

> **2026-07-13 update**
>
> **90%, on track.** The GitLab Transcend Hackathon (theme: build with GitLab Orbit) is judged and the winners are [announced publicly on Devpost](https://gitlab-transcend.devpost.com/updates/44639-winners-announcement-gitlab-transcend-hackathon-how-the-community-built-on-orbit). We are moving to the write-up phase. Nothing blocked.
>
> **The funnel**
>
> * **1,576 developers registered.**
> * **318 submissions received.**
> * **265 eligible for judging** (Showcase Track: agents, flows, and skills built on Orbit).
> * Most submissions clustered into a few crowded problem spaces (69 built pre-merge impact review, 36 built onboarding aids), but the field still produced genuinely novel work: 17 one-of-a-kind concepts and 20 two-of-a-kind. Five of the eight winners came from those rare tiers.
> * **Contribute Track: 26 unique contributors merged 61 MRs** directly into the Orbit codebase (new language support, bug fixes, the first query tutorial, docs cleanup). 19 earn a cash prize, all 26 earn swag credits.
>
> **How we judged it: a hybrid pipeline**
>
> * **Bulk scoring by AI, final selection by humans.** Each eligible submission was packaged into a self-contained packet (write-up plus an evidence bundle pulled from the actual repo code) and scored by three models in independent sessions: **Opus 4.8, GPT 5.5, and Gemini 3.1**. Around 800 scoring runs, tracked to a completion gate so nothing was skipped.
> * **The AI was decision support, not the decision.** Consensus gave clear shortlists for Technological Implementation and Quality of the Idea. It could not settle Potential Impact (models cap it differently) or Design (110 of 265 had silent or missing demos), so the panel resolved both by hand. Humans picked every winner.
>
> **The winners**
>
> | Category | First | Second |
> |----------|-------|--------|
> | Technological Implementation | [Sankofa](https://gitlab-transcend.devpost.com/submissions/1054521-sankofa) | [Stayed Shipped](https://gitlab-transcend.devpost.com/submissions/1054106-stayed-shipped) |
> | Design and Usability | [Carver](https://gitlab-transcend.devpost.com/submissions/1062163-carver-the-migration-quoting-agent) | [Marshal](https://gitlab-transcend.devpost.com/submissions/1062651-marshal-autonomous-migration-assistant) |
> | Potential Impact | [CrossCut](https://gitlab-transcend.devpost.com/submissions/1061837-crosscut) | [OrbitWeaver](https://gitlab-transcend.devpost.com/submissions/1061548-orbitweaver) |
> | Quality of the Idea | [Transcend](https://gitlab-transcend.devpost.com/submissions/1056751-transcend) | [Universal Agent OS](https://gitlab-transcend.devpost.com/submissions/1053916-universal-agent-os) |
>
> Full write-up with the reasoning behind each pick: [winners announcement on Devpost](https://gitlab-transcend.devpost.com/updates/44639-winners-announcement-gitlab-transcend-hackathon-how-the-community-built-on-orbit).
>
> **What we learned**
>
> * We scanned the "challenges we ran into" text across all 318 submissions (219 had substantive text). The friction is overwhelmingly on our side, and it is documentation and platform maturity, not participant skill: the Orbit query DSL is hard and under-documented, schema docs drift from the live schema, and silent failures return confident wrong answers. Captured in [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)
> * These are the same three themes we saw in our two earlier events, the [AI Hackathon](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1133) and the [Odisee Co-Create week](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1157). Now three times running. Captured in [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245), which proposes no new issues: every theme maps to work the Orbit and Duo Agent Platform teams already track, so it adds evidence weight to raise priority.
>
> **What's next**
>
> * Decide whether to run a GitLab company blog post off the winners write-up. The Devpost announcement is live; the open question is whether a GitLab.com blog version adds reach beyond it. Draft is ready if we go.
> * Hand the recurring-friction evidence to the Orbit and Duo Agent Platform teams via [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245).

Takeaways (inference): show a working demo with sound; avoid the crowded ideas (pre-merge impact review, onboarding aids); the scoring packet used "the actual repo code", so the repo must hold the real flows and code; humans decide Design and Impact.

### GitLab's review of June, word for word (team-task#1245)

Source: [team-task#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245), "GitLab Transcend Hackathon - participant observations", opened 2026-07-06 by mmichaux-ext. It has no comments (only 3 system notes, checked through GraphQL). The sections that carry lessons:

> The [GitLab Transcend Hackathon](https://gitlab-transcend.devpost.com/) gave us another large-scale view of developers building on the Duo Agent Platform and GitLab Orbit under real conditions: **318 submissions** across the Showcase and Contribute tracks. We extracted signal from the submissions themselves, specifically the "Challenges we ran into" and "What we learned" sections, which 219 submissions filled in with substantive detail. Where the same issue appears across many independent teams, the confidence is high.
>
> This is the third event in a row where we have captured this signal, after the [GitLab AI Hackathon](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1133) and the [Odisee Co-Create Hackathon](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1157). The headline is not new friction, it is the **same three themes recurring**: developers cannot self-diagnose failures, time to first success is too long because behavior is undocumented, and silent failures erode trust. Several specific bugs from the AI hackathon have since been fixed, but the underlying classes of friction showed up again with new specifics, this time concentrated on the Orbit query surface.
>
> **Three signals that came through clearly**
>
> **1. The Orbit query DSL and its documentation are the single biggest friction point**
>
> More teams cited this than anything else. The query language is strict, its error messages are unhelpful, and the public documentation does not match the shipped schema. Teams routinely spent iterations on 400 errors and reverse-engineered the correct query shapes from validation errors. The most common specific traps:
> - Single-node (`node`) vs multi-node (`nodes[]` + `relationships[]`) shapes are easy to confuse; a one-entry `nodes` array silently violates a `oneOf` constraint.
> - `query_type` values ("traversal", "aggregation", "neighbors") were described as undocumented.
> - `columns` must be `"*"`, not an array.
>
> **Actionables:** publish a correct, example-rich DSL reference with copy-paste query templates; make validation error messages name the actual problem; keep the schema docs in sync with the shipped version.
>
> **Already tracked (all open):** [gitlab-org/orbit/knowledge-graph#933](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/933) (unify `node`/`nodes` DSL shapes), [#970](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/970) (DSL schema too verbose for models), [#913](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/913) (evaluate Cypher front-end), [#917](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/917) (error pipeline for validator rejections), [#732](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/732) (schema-discovery workflow guide), [#902](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/902) (docs out of sync with product), [#832](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/832) (MCP quickstart has incorrect CLI commands).
>
> <details>
> <summary>Detail</summary>
>
> * Multiple teams baked "READ TWICE" warnings and known-good JSON templates into their own agent/flow prompts after burning iterations on 400s.
> * The public schema docs describe a `content` column on Definition nodes and per-relation edge tables. The real DuckDB schema (v0.78) has neither: all edges live in one `gl_edge` table keyed by `relationship_kind`, and source content is not on the row (teams re-read it from disk by line range).
> * Teams ran `orbit schema` against a live index on day one and rebuilt around what they found rather than the docs.
>
> </details>
>
> **2. Silent failures produce confident wrong answers, not errors**
>
> The most dangerous class, and a direct echo of the "cannot self-diagnose failures" theme from both prior events. Several Orbit behaviors fail silently by returning empty or wrong results instead of an error:
> - Querying the wrong relationship direction returns zero results silently; many teams lost time debugging empty responses.
> - `project_id` filtering is inconsistent: it works for MergeRequest but silently returns 0 rows for File/Definition.
> - The graph is shared across all projects, so an unscoped query silently blends results from other repos.
>
> **Actionables:** return explicit errors or warnings for wrong-direction and unscoped queries rather than empty results; document project scoping as a required step, not an option.
>
> **Already tracked:** [gitlab-org/orbit/knowledge-graph#916](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/916) (low/empty result indistinguishable from "nothing matched", open), [#915](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/915) (traversal limit silently starves fan-out queries, open), [#801](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/801) (aggregation count inflation, filed from our own earlier testing, now closed).
>
> <details>
> <summary>Detail</summary>
>
> * "Relationship direction is enforced, using the wrong direction returns zero results silently. No error, no warning. We spent significant time debugging empty responses." (Orbit Memory)
> * "An unscoped query for validateToken returned nine results from other repos, so everything had to be project-scoped." (Switchyard)
> * "project_id filtering is inconsistent across entity types. Works for MergeRequest, silently returns 0 rows for File/Definition. Discovered by trial and error." (Downwind)
>
> </details>
>
> **3. The Duo Agent Platform flow/skill contract is undocumented and discovered by trial and error**
>
> The same "time to first success is too long" and "undocumented behavior" theme from the two prior events, now on the flow/skill mechanics. Teams reverse-engineered the platform contract from UI templates and API errors:
> - Custom agents cannot access `query_graph` directly; Orbit is reachable only via the MCP endpoint + `invoke_command` wrapper (undocumented).
> - Flow YAML requires exact field names (`prompt_id` not `id`, `entry_point` not `entry`, `unit_primitives`) not found in docs.
> - Inter-agent data must flow through `conversation_history`; direct output references are not valid.
> - Custom flows require a group namespace, not personal; a group-level `experiment_features_enabled` flag silently blocks all flow creation.
> - The per-account "Orbit in GitLab Duo" toggles (Agentic Chat, Custom Agents, etc.) default OFF, one team spent significant time debugging tool-access failures caused by this.
>
> **Actionables:** document the flow/skill contract fully (required YAML fields, triggers, tool access, namespace requirements); improve flow YAML validation feedback; surface the "Orbit in Duo" access requirement in onboarding or default it on for participants.
>
> **Already tracked (Duo Agent Platform):** [gitlab-org/gitlab#592792](https://gitlab.com/gitlab-org/gitlab/-/work_items/592792) (orphaned custom agents, open, also flagged in the AI hackathon), [#595181](https://gitlab.com/gitlab-org/gitlab/-/work_items/595181) (DAP activation UX, excessive config steps, open), [#591428](https://gitlab.com/gitlab-org/gitlab/-/work_items/591428) (expand DAP troubleshooting/setup docs, open). The AI-hackathon session-debugging issues [#593150](https://gitlab.com/gitlab-org/gitlab/-/work_items/593150) and [#592972](https://gitlab.com/gitlab-org/gitlab/-/work_items/592972) have since been **closed**.
>
> <details>
> <summary>Detail</summary>
>
> * "Custom agents can't access query_graph. Discovered Orbit MCP endpoint + invoke_command wrapper." (NEXUS)
> * "Flow YAML requires specific field names that aren't clearly documented. Discovered through trial and error by reading the UI template." (Orbit AI Engineering Manager)
> * "All four Orbit-in-Duo toggles were off by default. Enabling Custom Agents gave the flow real tool access immediately." (Dead Code Finder)
> * Em dashes in flow YAML get silently corrupted in the editor (multiple teams).
>
> </details>
>
> **What developers expected but does not exist yet**
>
> Recurring capability gaps, several of which were already surfaced in the AI hackathon ([team-task#1133](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1133)) and appeared again here.
>
> | What the hackathon confirmed | Feature request |
> |---|---|
> | Multiple teams noted there is still no "merge request opened" trigger; they assumed one existed and had to rebuild around it. | Native MR-opened trigger for flows |
> | Flows can read the API and create issues but have no native MR-note tool; teams split their architecture to work around it. | Native MR-comment capability for flows |
> | Flows cannot make outbound HTTP calls; teams routed scanning through CI and passed results back via an issue. | Documented pattern (or capability) for external calls from flows |
> | Orbit provides no native pathfinding; teams reimplemented bounded BFS themselves. | Native bounded pathfinding in Orbit |
> | Missing parsers (HCL, Dockerfile) and unreliable cross-file resolution outside TS/JS forced manual workarounds. | Broader, documented language/file-type coverage |
>
> **Access and account gates that blocked hackathon work**
>
> A smaller but sharp set of issues where participants lost time to access rather than to the platform itself:
> - The `/api/v4/orbit/query` remote endpoint requires a paid tier; teams pivoted to the REST API.
> - New GitLab accounts cannot run CI without a credit card on file; several teams dropped CI or moved it to GitHub Actions.
> - `CI_JOB_TOKEN` cannot post MR notes (scoped to package registry only).
>
> **Actionable:** provision hackathon participants with the tier, CI access, and token scopes they need up front.
>
> **Where this fits with the prior two events**
>
> | Theme | AI Hackathon ([#1133](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1133)) | Odisee ([#1157](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1157)) | Transcend (this) |
> |---|---|---|---|
> | Cannot self-diagnose / silent failures | Yes | Yes | Yes (wrong-direction / unscoped queries return empty) |
> | Time to first success too long / docs gaps | Yes | Yes | Yes (Orbit DSL and schema docs) |
> | Undocumented platform behavior found by trial and error | Yes | Yes | Yes (flow/skill contract, Orbit-in-Duo toggles) |
>
> Some specific bugs from the AI hackathon have since been fixed (session-failed-with-no-details, the token 403, the misleading catalog validation error, and the two session-debugging MVCs [gitlab-org/gitlab#593150](https://gitlab.com/gitlab-org/gitlab/-/work_items/593150) and [#592972](https://gitlab.com/gitlab-org/gitlab/-/work_items/592972)). That progress is real. But the same *classes* of friction recurred, which suggests the fixes have been point fixes rather than a systemic investment in error visibility and documentation.
>
> **This report proposes no new issues.** Everything participants hit is already tracked: the links are inline under each signal above, in the Orbit queue and the Duo Agent Platform. The value here is real multi-team evidence to raise the priority of issues that are already open, the same play as [team-task#1133](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1133). The recurrence across three events is itself the argument for prioritizing the underlying gaps.
>
> **Notes on method**
>
> - Source: the self-reported "Challenges" and "What we learned" sections of 318 submissions (219 substantive). This is participant-reported friction, not staff-observed as in the prior two events, so it skews toward what teams found notable enough to write down. It under-counts issues teams solved silently.
> - Several teams filed Contribute-track fixes for the Orbit issues they hit, so some of this is already in the upstream queue.

### More lessons from the June planning thread (team-task#1137)

Word for word, from [team-task#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137):

- leetickett-gitlab, 2026-05-01, on roles: "I'm also considering whether we can/should make them maintainers so participants:"
  - "can create agents and flows the documented way through the UI"
  - "will be credited/attributed in the catalog"
  - "can create other CI (including secrets/variables)"
- leetickett-gitlab, 2026-05-05: "Note: project maintainers can now enable agents and flows in a project (previously they needed to be top level group maintainers, which was in large the reason for our clever setup)."
- mmichaux-ext, 2026-05-05: "Looking at the issues that the GitLab AI hackathon participants surfaced on proving what works (secrets, CI, ...), it would be really useful if they can be owner or maintainer of their own project."
- leetickett-gitlab, 2026-05-05: "You need to be a maintainer to manage agents/flows... if we created a token and didn't have a secure policy in place it would be trivial to extract the token. We also lose the attribution if we use a token."
- leetickett-gitlab, 2026-05-12, quoting an internal search: "Agentic Chat only gets Orbit tools when that flag is on for the user". 2026-06-08: "Looks like all except `mcp_catalog_agent_tools` have now been globally enabled".
- mmichaux-ext, 2026-07-16: "We experienced some hurdles in Devpost platform and internally due to the not defined process."

From the February AI Hackathon cleanup ([team-task#1155](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1155)): "Can the authors get some attribution (at the moment the service account gets the credit)?" and, a month after the event, "only a dozen or so of the agents/flows have been used in the last 30 days".

### Organizer retrospective and survey

- [team-task#1260](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1260) "Transcend Hackathon: learnings & how we do better next time" is an organizer checklist. Items that touch us: "Participant provisioning/access + security policy tested", "**Explainer video** produced: how to participate + how to do the work", "Do a full sign-up + onboarding run yourself with ≥2 people". No comments.
- [team-task#1329](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1329) survey (20 responses): "the Transcend/Devpost hackathon **4.15/5**"; "The Transcend/Devpost format was particularly appreciated for its multiple tracks, freedom to choose projects, cash prizes, and opportunities to build in public." Pain points include "Beginners need more support" with "help presenting unfinished projects or demos", and "AI-assisted contribution creates fairness concerns."

### The October theme and goals (epic #40)

From [epic #40](https://gitlab.com/groups/gitlab-org/developer-relations/contributor-success/-/work_items/40), DRI missy-gitlab:

- "Challenge theme from the meeting: "Hands Off. How far can your agents go without you?""
- Deliverable still open: "Gaming and AI-spam are kept out, so reviewer goodwill is protected".
- 2026-09-04: "Prize structure decided. DevPost intake form submitted, social media intake completed, external judge recruitment started."
- 2026-10-05: "Soft launch is today (Oct 5), hard launch is during keynote tomorrow Oct 6." and "Details, rules, prizes, challenge, judges are all sorted".

### What the June workspace data shows (my analysis)

Counts from the public API on 2026-10-06 (root tree of each of the 312 projects in [gitlab-ai-hackathon/transcend](https://gitlab.com/gitlab-ai-hackathon/transcend); pipeline lists limited to the latest 100 per project):

- 139 of 312 projects hold only a README. 116 have `skills/`, 81 have `.gitlab-ci.yml`, 52 have `.gitlab/`, 33 have `AGENTS.md`, 18 have `flows/`, 16 have `agents/`, 117 have a `LICENSE`, 7 have a `Dockerfile`.
- CI worked inside the provisioned group: of the 81 projects with `.gitlab-ci.yml`, 69 have at least one successful pipeline, 8 never passed, 4 never ran. So the "credit card" problem in the review most likely hit people working outside the provisioned group (inference).
- 66 of 312 projects ran flows (`duo_workflow` pipelines): 770 succeeded, 13 failed, 43 canceled.
- Winners I could match by README title: [Sankofa](https://gitlab.com/gitlab-ai-hackathon/transcend/34570711) (4 flow YAML files in `flows/`, a `cloud-run/` folder, 35 successful flow runs), [Marshal](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992) (`.gitlab/duo/agent-config.yml`, two flows in `.gitlab/duo/flows/`), [Carver](https://gitlab.com/gitlab-ai-hackathon/transcend/13178946) (one flow, five skills), [Stayed Shipped](https://gitlab.com/gitlab-ai-hackathon/transcend/2902648) (one flow, one skill), [OrbitWeaver](https://gitlab.com/gitlab-ai-hackathon/transcend/35222941) (`SKILL.md`, `Dockerfile`, `deploy/`). All five have a `LICENSE` and a `.gitlab-ci.yml`, and all five keep their flow or skill files in the repo even though flows are created in the UI.
- Marshal's [agent-config.yml](https://gitlab.com/gitlab-ai-hackathon/transcend/10572992/-/blob/main/.gitlab/duo/agent-config.yml) notes that custom CI/CD variables are not available in flows and derives settings from `GITLAB_BASE_URL`, `CI_PROJECT_ID` and the `DUO_WORKFLOW_*` variables instead.

### Which June gaps the docs now say are closed

Per the current docs (test each one; none of this is verified in our workspace):

- "no "merge request opened" trigger": the Merge request event now has a **Created** action, added in GitLab 19.4 ([triggers/_index.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/triggers/_index.md)).
- "no native MR-note tool": `create_merge_request_note`, `create_merge_request_diff_note`, `reply_to_discussion` and `submit_mr_review` are listed ([agents/tools.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/agents/tools.md)).
- "Flows cannot make outbound HTTP calls": `network_policy.allowed_domains` exists since 18.10 ([environment_sandbox.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/environment_sandbox.md)), unless the group uses strict mode.
- "Flow YAML requires exact field names": still true; the schema page now lists the restricted fields, and the v1 spec is public.

## Hackathon group structure and counts

### Subgroups and project counts

Counted on 2026-10-06 at 01:25 UTC with `groups/:id/subgroups`, `groups/:id/descendant_groups` and `groups/:id/projects?include_subgroups=true` (all pages). Top group: [gitlab-ai-hackathon](https://gitlab.com/groups/gitlab-ai-hackathon) (ID 121124982, created 2025-12-18, public): 7 direct subgroups, 10 groups in total, 345 projects, 0 archived.

| Subgroup | ID | Created | Subgroups | Projects | What it is |
|---|---|---|---|---|---|
| [transcend-october-2026](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) | 142538134 | 2026-09-17 | 3 | 2 | This event. Description: "GitLab Transcend III hackathon (October 2026) - showcase track. One subgroup per participant is provisioned under here by contributors.gitlab.com. Do NOT enable observability on this group, and do NOT add group-level secrets here." |
| [transcend](https://gitlab.com/groups/gitlab-ai-hackathon/transcend) | 132494471 | 2026-05-18 | 0 | 312 | June 2026 edition, one project per participant, named by user ID |
| [participants-test-mattias](https://gitlab.com/groups/gitlab-ai-hackathon/participants-test-mattias) | 123068969 | 2026-01-28 | 0 | 24 | Staff test group (February setup) |
| [participants-test-lee](https://gitlab.com/groups/gitlab-ai-hackathon/participants-test-lee) | 123069139 | 2026-01-28 | 0 | 2 | Staff test group (February setup) |
| [test](https://gitlab.com/groups/gitlab-ai-hackathon/test) | 122493198 | 2026-01-17 | 0 | 1 | `ci-component-test` |
| [project-templates](https://gitlab.com/groups/gitlab-ai-hackathon/project-templates) | 121634200 | 2026-01-01 | 0 | 1 | `participant-template` (February agent and flow YAML templates) |
| [gitlab-devsecops-flow-hackathon](https://gitlab.com/groups/gitlab-ai-hackathon/gitlab-devsecops-flow-hackathon) | 126794830 | 2026-03-16 | 0 | 0 | Empty |
| (projects directly in the top group) | | | | 3 | `ci`, `security-policies`, `gitlab-profile` |

Moved out: the February 2026 AI Hackathon participants group (`gitlab-ai-hackathon/participants`, ID 121614317) now lives at [gitlab-community/community-projects/2026-02-ai-hackathon](https://gitlab.com/groups/gitlab-community/community-projects/2026-02-ai-hackathon) with 1,788 projects ([team-task#1155](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1155) for the move).

### October 2026 group today

All three participant subgroups are staff tests created 2026-10-02: `1933526` (leetickett, project `showcase`), `12687636` (leetickett-gitlab, no public project), `8659557` (missy-davies, project `showcase`) ([API: subgroups of 142538134](https://gitlab.com/api/v4/groups/142538134/subgroups)). No real participant workspace was visible at 01:25 UTC on October 6.

### Shared projects in the top group

- [gitlab-ai-hackathon/ci](https://gitlab.com/gitlab-ai-hackathon/ci): "CI configuration for all participant projects, enforced by pipeline security policy". Its `.gitlab-ci.yml` includes `component: $CI_SERVER_HOST/components/ai-catalog/catalog-sync@0.0.10` with `group_id: "121124982"` and `gitlab_token: $CATALOG_SYNC_TOKEN`, and a `placeholder-test` job that fails if `agents/*.yml` or `flows/*.yml` still contain the template name, description or prompt ([file](https://gitlab.com/gitlab-ai-hackathon/ci/-/blob/main/.gitlab-ci.yml)). This was the February "repo backed" model: YAML files in the repo were synced to the AI Catalog by CI.
- [gitlab-ai-hackathon/security-policies](https://gitlab.com/gitlab-ai-hackathon/security-policies): a `pipeline_execution_policy` named "Enforce CI" with `pipeline_config_strategy: override_project_ci`, `skip_ci: allowed: false`, scoped to groups 123069139, 123068969 and 121614317 ([policy.yml](https://gitlab.com/gitlab-ai-hackathon/security-policies/-/blob/main/.gitlab/security-policies/policy.yml)). Neither the June group nor the October group is in that scope, so your own `.gitlab-ci.yml` should run (inference; another policy could exist that I cannot see, unverified).
- [gitlab-ai-hackathon/gitlab-profile](https://gitlab.com/gitlab-ai-hackathon/gitlab-profile): README points to the February event page `https://gitlab.devpost.com/`.

### Onboarding templates and office hours

- The only onboarding template is the issue template quoted in the setup section ([description.md.erb](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/templates/transcend_hackathon_issue/description.md.erb)). The group has no issue templates of its own that I could find.
- No office hours link found (see Blocked). A Discord event link exists only for the Community Hackathon: https://discord.gg/gitlab?event=1549080709073997925 ([team-task#1296](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1296)).

## Gotchas checklist for our build

Day one, workspace:

- [ ] Register on Devpost and on contributors.gitlab.com with the same Devpost username. Find your numeric GitLab user ID; your project will be `gitlab-ai-hackathon/transcend-october-2026/<id>/showcase` ([model](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/models/transcend_hackathon_registration.rb)).
- [ ] Complete GitLab identity verification early. June: "New GitLab accounts cannot run CI without a credit card on file" ([#1245](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1245)); the Flows API can return "Identity verification is required to use GitLab Duo Agent Platform" ([API doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/api/duo_agent_platform_flows.md)).
- [ ] Test push to `main` and merge of an MR into `main`. The staff test project allows only Maintainers ([API](https://gitlab.com/api/v4/projects/87183213/protected_branches)). If blocked, ask in Discord `#transcend-hackathon` or @-mention `gitlab-org/developer-relations/contributor-success` before building anything that depends on `main`.
- [ ] Check that **AI** (or **Automate**) > **Flows** > **New flow**, **AI** > **Agents** > **New agent** and **AI** > **Triggers** > **New flow trigger** are available to you. The docs require Maintainer; you have Developer plus a custom role.
- [ ] Check whether you can add CI/CD variables and project access tokens. Plan so you do not need them: keyless WIF with IDs in `.gitlab-ci.yml`, and a human merge instead of a bot token (this also matches our "human decides" rule).
- [ ] Never enable observability or add variables on the parent group. Enable observability only on your own subgroup; allow up to 10 minutes.

Flow YAML:

- [ ] Paste only `version`, `environment`, `components`, `prompts`, `routers`, `flow` (plus optional `coding_environment`). No top-level `name`, `description`, `product_group`; no `model`; `environment: ambient` only; at most 40 KiB.
- [ ] Use exact field names: `prompt_id` (not `id`), `entry_point` (not `entry`), `unit_primitives`, `prompt_template` with `system` and `user`, `params.timeout`.
- [ ] Component names: letters, digits, underscore; no `:` or `.`.
- [ ] ASCII only. "Em dashes in flow YAML get silently corrupted in the editor (multiple teams)." Our no-dash rule already covers this.
- [ ] Keep a copy of every flow and agent YAML in the repo (for example `flows/<name>.yml`), as the June winners did, so judges see it in the code.
- [ ] Handle every goal format you enable: mention text, a bare IID for assign, or a full pipeline JSON payload. Always pass `context:project_id`.
- [ ] Add the `workspace_agent_skills` input if the flow should use `skills/`.
- [ ] Time-box agents with `max_cycles` and `params.timeout` (our rule 5).
- [ ] Test data passing between two agents (`context:<name>.final_answer`) and `HumanInputComponent` in a triggered ambient flow early; both have open questions.

Triggers and running:

- [ ] A human must perform the triggering action. Bots, service accounts and other flows cannot. Script the demo so a person assigns, mentions, or changes status, or start flows through the Flows API.
- [ ] Our flow's service account will be `ai-<flow-name>-gitlab-ai-hackathon` (inference). It acts with the triggering user's access (composite identity) and is billed for credits.
- [ ] In flow scripts call the API with `Authorization: Bearer $GITLAB_TOKEN` (not `PRIVATE-TOKEN`); only `ai_workflows` scope endpoints work. June: "`CI_JOB_TOKEN` cannot post MR notes".
- [ ] Flows cannot read CI/CD variables. Put non-secret config in `agent-config.yml`; use `id_tokens` for cloud access; add outside hosts to `network_policy.allowed_domains`.
- [ ] `agent-config.yml` is read from the default branch only. Use an image with git (for example `python:3.12`, not `python:3.12-slim`).
- [ ] Each flow run is a CI pipeline on hosted runners (tag `gitlab--duo`). If a session fails to start, the docs point to runner availability and used-up compute minutes; a session stuck in "created" can also be push rules ([troubleshooting.md](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/duo_agent_platform/troubleshooting.md)).
- [ ] Custom flows need a group namespace (we have one). If flow creation fails silently, the group-level `experiment_features_enabled` flag was the June cause; ask the organizers.

Google Cloud and observability:

- [ ] Deploy on Google Cloud ("Projects deployed on Google Cloud score higher on technological implementation"). The reference uses a JSON key; we use WIF with `id_tokens`.
- [ ] Use one gunicorn worker if state is in memory (reference commit [6b855f3c](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/6b855f3c)).
- [ ] Use real Cloud Run URLs from `gcloud run services describe` for environment URLs, passed by dotenv artifacts (commit [68436ab9](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/commit/68436ab9)).
- [ ] Send OpenTelemetry with `gitlab.project.id` set; the OTLP endpoint accepts data without auth unless you add an ingest token. The observability MCP server lets an agent query the data.

Submission:

- [ ] Video is required. In June "110 of 265 had silent or missing demos". Narrate it and show the loop end to end.
- [ ] Avoid crowded ideas: in June "69 built pre-merge impact review, 36 built onboarding aids"; "Five of the eight winners came from those rare tiers."
- [ ] Theme: "Hands Off. How far can your agents go without you?" Show how far the agents go alone, and where a person decides. The Design and Usability winner kept a human merge gate.
- [ ] Add a `LICENSE` (the June planning issue said "Projects must have an MIT license", [#1137](https://gitlab.com/gitlab-org/developer-relations/contributor-success/team-task/-/work_items/1137); October rule unverified, see docs/RULES.md).
- [ ] Submit before 2026-10-27 14:00 UTC. Keep a mirror of the repo; teardown MR [!2838](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/merge_requests/2838) is ready.
- [ ] The project and subgroup are public. Never commit secrets; flow final answers are visible "on the session detail page in the UI and in the CI job log" ([v1 spec](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md)).

## Blocked

| What | URL | Error |
|---|---|---|
| Devpost (all pages, including June winners write-up and the rules) | https://gitlab-transcend.devpost.com/ , https://gitlab-transcend.devpost.com/rules , https://gitlab-transcend.devpost.com/updates/44639-winners-announcement-gitlab-transcend-hackathon-how-the-community-built-on-orbit | 403, tested by the lead before this task; not retried |
| Internet Archive | https://web.archive.org/ | Blocked, tested by the lead; not retried |
| GitLab forum post for the October hackathon | https://forum.gitlab.com/t/our-next-gitlab-hackathon-starts-october-6th/135317.json | `curl: (56) CONNECT tunnel failed, response 403` (proxy: connect_rejected) |
| GitLab hackathon page | https://about.gitlab.com/community/hackathon/ | `curl: (56) CONNECT tunnel failed, response 403` (proxy: connect_rejected) |
| Live reference app | https://hello-world-showcase-tmepbnfv7q-uc.a.run.app/health | `curl: (56) CONNECT tunnel failed, response 403` |
| Web search for office hours | query "GitLab Transcend Hackathon October 2026 office hours" | Search budget for this session was used up; not retried |
| GitLab REST endpoints that need sign-in | `/projects/:id/issues/:iid/notes`, `/discussions`, `/merge_requests/:iid/notes`, `/environments`, `/deployments`, `/jobs/:id/trace`, `/search?scope=blobs`, `/version`, `/groups/:id/members`, `/projects/:id/members/all` | `401 Unauthorized`. Notes and environments were read through GraphQL instead; job logs and members could not be read |
| team-task#1133 (AI Hackathon observations) and #1157 (Odisee) | https://gitlab.com/api/v4/projects/gitlab-org%2Fdeveloper-relations%2Fcontributor-success%2Fteam-task/issues/1133 and .../1157 | `404 Not found`; absent from anonymous GraphQL (probably confidential) |
| Custom member role 3007169 | GraphQL `memberRole(id: "gid://gitlab/MemberRole/3007169")` | Returns `null` without sign-in |
| Discord, Google Docs and Sheets linked from issues | discord.gg/gitlab, docs.google.com links | Not attempted (need sign-in or internal) |
