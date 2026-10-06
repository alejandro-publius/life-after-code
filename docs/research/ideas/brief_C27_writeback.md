# C27 Writeback: build brief and skeptical review

Written 2026-10-06 for Alex Velazquez's solo Path A entry in Life After Code. Sources are linked where used. "(unverified)" marks anything no source here confirmed. Prior-art research used five web searches; most vendor pages were blocked by the session proxy, so those facts are marked as search excerpts.

## 1. Name and one-line pitch

**Writeback.** When someone fixes production by hand during an emergency, the next deploy stops instead of erasing the fix, and an agent writes the fix into code in that person's name, for them to keep or discard.

The name stays. Engineers already read "write back" as "copy a change back to where it should live", and the alternatives tried ("Tagout", "Keep", "Night Edit") say less.

## 2. Who it is for

Small teams that run services on Cloud Run and deploy from GitLab CI with `gcloud run deploy` flags, which is how the judges' reference project and our own deploy job work ([guide](../gitlab_guide_and_reference.md#every-stage-and-job-in-gitlab-ciyml), [ci_deploy.sh](../../../deploy/ci_deploy.sh)), and whose on-call person sometimes fixes production in the console at night.

**Clara (persona; Alex plays her in the demo), on call for a 12-person team.** At 02:10 a large customer export starts crashing the service, so she raises its memory from 256Mi to 512Mi in the Cloud Run console, watches the crashes stop and goes back to bed. At 10:00 a teammate deploys a one-line change, and our deploy job passes `--memory=256Mi` on every run ([ci_deploy.sh](../../../deploy/ci_deploy.sh)), so without Writeback the outage she fixed would come back on a routine deploy. With Writeback that deploy stops with her name on it, and a merge request that writes her fix into code under her name is waiting when she wakes; she merges it from her phone before standup.

## 3. The demo moment and a 2:40 video

**The moment.** The teammate presses Deploy. Within a minute the job is red and its log opens with:

```
STOPPED. Deploying now would undo a change Clara made by hand at 02:10:
  memory 256Mi -> 512Mi   (Cloud Run console, revision lac-123-00042)
In the hour before that change the service ran out of memory 37 times. Since then: 0.
Nothing in production was changed. Keep it or discard it first: see the Writeback MR.
```

Every fact in that message comes from code, not from the model (the 37 is whatever code counts on the day). The viewer has just seen, in the opening, what the same deploy does without Writeback: the crash comes back. The feeling is relief, then recognition when Clara's phone shows "Keep Clara's 02:10 fix" assigned to her.

| Time | Scene | Real or labelled |
|---|---|---|
| 0:00 to 0:12 | 02:10, dark room. Cloud Run console: memory 256Mi to 512Mi. The crash count stops. | Real edit and real out-of-memory crashes from a planted memory-hungry export path; caption "staged incident, persona" |
| 0:12 to 0:30 | "10:00. A teammate ships a one-line change." Filmed with the guard switched off: the deploy sets 256Mi back and the export crashes again. "This is how an outage comes back." Title: Writeback. | Real deploy, caption "guard off for this shot" |
| 0:30 to 0:55 | The same deploy with Writeback: `writeback_guard` turns red within a minute, with the message above. Cut to the 40 lines of code that decided it: "No model decided this." | Real |
| 0:55 to 1:30 | The failed pipeline starts the Writeback flow (AI > Sessions). It reads the guard report, finds incident INC-12 and its notes, reads the history of the service settings file, then opens MR "Keep Clara's 02:10 fix: memory 512Mi (INC-12)": one changed line, assigned to Clara, evidence with links, a note on the incident, one follow-up issue. | Real flow run; incident text is labelled demo data |
| 1:30 to 1:45 | MR pipeline green: guard tests, budget and file lint, Secret Detection, review-round counter. | Real |
| 1:45 to 2:05 | Clara's phone at 09:40: the MR in her name, two lines of explanation, Merge. Overlay: "Her fix, in code, under her name." | Real merge from Alex's account, persona labelled |
| 2:05 to 2:20 | Deploy again: guard green, Cloud Build, Cloud Run at 512Mi, health check, GitLab environment updated. The live page footer reads "512Mi: Clara's 02:10 fix, kept in !7". | Real |
| 2:20 to 2:32 | The other door: "@ai-writeback discard" brings up an approval in the session: "Discarding sets memory to 256Mi. At 256Mi the service ran out of memory 37 times in an hour." Two review rounds, then a person finishes. | Real HumanInputComponent run |
| 2:32 to 2:40 | One card: GitLab flow and CI, Cloud Run with keyless access, Claude inside the flow; nine stages; Supervised. "Fix it at 2am. Keep it at 10." | |

## 4. End-to-end flow (one loop)

1. **Monitor.** At 01:40 the export path starts running out of memory (planted, labelled demo). Clara opens incident INC-12 in **GitLab Incidents** and notes what she sees.
2. **Configure, by hand.** At 02:10 she raises memory in the Cloud Run console. Google stamps the service with her identity: the gcloud SDK reads it from the `serving.knative.dev/lastModifier` annotation, and the v2 API documents `last_modifier` as "Email address of the last authenticated modifier" ([service.proto](https://github.com/googleapis/googleapis/blob/master/google/cloud/run/v2/service.proto); Google Cloud SDK 530.0.0 `lib/googlecloudsdk/api_lib/run/service.py`, read locally). Cloud Audit Logs also record the change (unverified, Google's docs were blocked here).
3. **Create and verify.** At 10:00 a teammate merges a one-line **merge request**; the **main pipeline** runs tests and scans.
4. **Release, guarded.** The teammate plays the deploy, which now starts with the **manual job** `writeback_guard` (a normal **CI job** with `id_tokens` and the existing keyless Workload Identity Federation login); `deploy_cloud_run` runs only if it passes (`needs`). The guard reads the live service with `gcloud run services describe`, which `ci_deploy.sh` already runs before every deploy for its ownership check. Code compares a fixed list of fields with `deploy/service.env` in the commit being deployed, checks whether the service's last modifier is a person rather than the deploy service account, and looks for a merged keep or discard decision. It counts out-of-memory log lines before and after the change in Cloud Logging. Unresolved difference: the job fails with the plain sentence and a JSON report with emails and environment values removed, and the deploy never starts. Production is untouched.
5. **Trigger.** The failed pipeline, caused by the teammate's click, fires the **Pipeline events: Failed** trigger of the **custom flow** `writeback` on the **Duo Agent Platform**. The goal is the pipeline webhook payload, which lists each job's `name`, `stage` and `status` and the triggering `user` ([webhook_events.md, Pipeline events](https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/user/project/integrations/webhook_events.md)). A first component ends the session in seconds unless the failed job is `writeback_guard`.
6. **Investigate (the model chooses where to look).** A reader agent with read-only tools (`get_pipeline_failing_jobs`, `get_job_logs`, `gitlab_issue_search`, `get_work_item_notes`, `list_commits`, `get_commit_diff`, `get_repository_file`) reads the report, then looks for why: incidents and notes in the hour around 02:10, earlier changes to `deploy/service.env`, earlier Writeback decisions. It drafts, per field: owner (from code), reason with links, keep or discard, the exact line.
7. **Create.** A writer agent holding only write tools (`create_branch`, `create_commit`, `create_merge_request`, `create_issue_note`, `create_issue`) commits one line, `MEMORY=512Mi`, with a comment naming INC-12 and a `Co-authored-by` trailer for Clara; opens the **merge request** assigned to her; posts one note on INC-12; opens at most one follow-up **issue** ("make the export fit in 256Mi, or keep 512Mi on purpose").
8. **Verify and secure.** The **MR pipeline** runs the guard's unit tests, `writeback_lint` (only `deploy/service.env` and `ops/writeback/decisions.yml` changed, values inside budget limits, nothing secret-looking), **pipeline Secret Detection**, and `writeback_rounds`.
9. **Govern: a person decides.** Clara merges to keep it. She can instead mention the flow to change the MR (at most two rounds), or write "discard: reason": the flow shows what discarding will do and pauses at a **HumanInputComponent** (To-Do item and email, [SPONSORS.md section 1](../../SPONSORS.md#1-summary)); on approve it turns the MR into a discard record in `ops/writeback/decisions.yml`, and merging that is the discard.
10. **Release and close.** On main the deploy is played again; the guard passes because the code now says 512Mi; `deploy_cloud_run` builds with Cloud Build, deploys the image by digest to Cloud Run, checks health and updates the **GitLab environment**. A person closes INC-12, whose note links Google's record, the MR and the deployment.

## 5. Lifecycle stages

| Stage | Covered | GitLab feature | Real or demo data |
|---|---|---|---|
| Plan | Yes, light | Issues: one follow-up issue linked to the incident and the MR | Real objects; incident wording is labelled demo data |
| Create | Yes | Custom flow writes branch, commit and MR | Real |
| Verify | Yes | CI/CD pipelines: guard job on main; MR jobs for guard tests, `writeback_lint`, `writeback_rounds` | Real |
| Package | Touched, reused | The deploy it guards builds with Cloud Build and deploys by digest from Artifact Registry ([ci_deploy.sh](../../../deploy/ci_deploy.sh)); the guard also flags a running image that no pipeline built (blocked, never adopted) | Real, but mostly existing deploy code, not Writeback's own work |
| Secure | Yes, modest | Pipeline Secret Detection template on the MR; `id_tokens` with keyless WIF; a separate read-only Google identity; emails and environment values never reach the public job log or the model | Real |
| Release | Yes | Manual deploy job, `needs`, `resource_group`, environments and deployments | Real |
| Configure | Yes, the core | Cloud Run settings as code in `deploy/service.env`, drift found and written back | Real |
| Monitor | Yes | Incidents and notes; Cloud Logging out-of-memory counts and Google's modifier record read by the guard | Outage and incident are staged and labelled; crashes, console edit and Google's record are real |
| Govern | Yes | Merge as the keep decision; HumanInputComponent approval plus merge for discard; `ops/writeback/decisions.yml` with name and reason; flow sessions as the record | Real |

Nine touched, eight with Writeback's own work. Configure is the stage the October field touches least (one claim in seven ideas, [FIELD.md section 6](../../FIELD.md#6-open-spaces-nobody-seems-to-be-in-them-yet)).

## 6. The agent loop

**The model may:** choose where to look for the reason (incidents, notes, commits, earlier decisions); recommend keep or discard per field with links, or say it found no reason; choose the line and write the commit, MR text and one incident note; open one follow-up issue; revise its own MR when a person asks, at most twice.

**The model may not:** reach Google Cloud (the flow has no Google identity and no `allowed_domains`; a Feb 2026 winner wrote that flows "cannot make outbound HTTP requests", [past editions](../winners/gitlab-transcend-past-editions.md)); change production; merge, approve or close the MR (the flow's service account is a Developer and the stricter role wins in composite identity, [SPONSORS.md 2.1](../../SPONSORS.md#21-duo-agent-platform)); edit any file other than `deploy/service.env` and `ops/writeback/decisions.yml` (checked by `writeback_lint`); decide whether there is drift or who made it; see environment values or emails; discard a person's change without that person's approval.

**Code decides:** the difference between production and `deploy/service.env` over a fixed field list (memory, CPU, concurrency, timeout, minimum and maximum instances, ingress, runtime service account, traffic split, environment variable names and value hashes), with unit normalization and known noise ignored (operation ID, client name and version, revision name, the `lac-commit` label, the `CI_COMMIT_SHORT_SHA` value; the SDK's own export format drops the first three for the same reason, `command_lib/run/printers/export_printer.py`); whether a person made it (the last modifier is not the deploy service account; mapped to a GitLab user through `ops/writeback/people.yml`, which stores only hashes of Google principals); kept (the candidate already declares the live value), discarded (a merged record names the change's fingerprint) or unresolved (deploy blocked); the out-of-memory counts; budget limits (for example memory at most 1Gi, maximum instances at most 2); the review-round count.

**The human decides, in GitLab:** keep by merging; change by mentioning the flow on the MR; discard by asking, approving at the HumanInputComponent, then merging the discard record. Keeping changes nothing in production, so it takes one step; discarding moves production toward risk, so it takes two. Production changes only when a person plays the deploy job.

**Time boxes:** the guard job has `timeout: 5m` and fails closed (if it cannot read production, it does not deploy; the deploy would fail on the same credentials anyway). Flow prompts use `params.timeout` (60 s for the event sorter, 240 s reader, 120 s writer) and `max_correction_attempts: 2` where a one-shot writer is used. Custom flows reject `max_cycles` ([SPONSORS.md section 6, row 1](../../SPONSORS.md#6-contradictions-between-notes-and-how-they-were-resolved)), so the step limit is the flow's shape: one read pass, at most one human checkpoint, one write pass.

**Two review rounds:** at most two revisions after the first draft, per [AGENTS.md](../../../AGENTS.md) rule 5 ("ship it or drop it"). `writeback_rounds` in the MR pipeline fails once the flow's service account has pushed more than three commits to the branch, and the flow checks the count before revising and replies "two rounds used; a person finishes or closes this". While nobody decides, production keeps Clara's fix and only deploys wait.

## 7. What it needs from Google Cloud for the bonus

The bonus needs deploy code in the public repo and a public live URL ([RULES_CHECK.md](../../codex/RULES_CHECK.md#google-cloud-bonus-exact-faq-wording)). Most of it exists in [deploy/](../../../deploy/README.md).

| Need | Google Cloud piece | New or existing | Free tier note |
|---|---|---|---|
| Live demo service and URL | Cloud Run, request billing, min 0, max 1 | Existing; memory moves to 512Mi in the demo | 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests a month ([deploy README](../../../deploy/README.md#costs-and-free-allowances)); 512Mi stays far inside |
| Build | Cloud Build and Artifact Registry | Existing | 2,500 build-minutes a month; 0.5 GiB-month storage free; delete old images |
| Keyless access | WIF pool and provider, deploy service account | Existing ([setup_gcp.sh](../../../deploy/setup_gcp.sh)) | No charge |
| Read the live service and its modifier | `gcloud run services describe`; Run Developer on the service already allows it | New use, no new role | API reads free (unverified) |
| Evidence counts and audit history | Cloud Logging reads; Cloud Audit Logs Admin Activity | New: a read-only `lac-<id>-drift` service account with `roles/logging.viewer`, used only by the guard | Admin Activity logs always written at no charge (unverified, docs blocked); log ingestion 50 GiB a month free |
| Optional early warning | Cloud Scheduler and a Cloud Run job that checks every 15 minutes and starts the flow through the Flows API with a token in Secret Manager | Optional | Small free allowances for Scheduler and Secret Manager (unverified); skip it if a pipeline schedule's failure already fires the trigger |
| Spend guard | Existing USD 5 budget alert | Existing | Alerts only; budgets do not cap spending |

The live URL also shows why the service has its settings: a footer built from the baked-in `deploy/service.env` and decisions file ("512Mi: Clara's 02:10 fix, kept in !7").

## 8. How Anthropic models show up

- **Inside the flow.** The Writeback flow runs on GitLab's default model for agents and flows, Claude Sonnet 4.6 served from Google's Gemini Enterprise Agent Platform. Custom flows reject a `model` field and only GitLab, as top-level group Owner, can change it ([SPONSORS.md section 1, fact 3](../../SPONSORS.md#1-summary)). The README and video say so plainly. One run touches all three sponsors.
- **What the model is trusted with.** Reading untrusted text (incident notes, commit messages, log lines) as data, under the reader and writer split GitLab recommends against prompt injection ([SPONSORS.md 2.5, item 3](../../SPONSORS.md#25-what-gitlab-would-be-proud-to-see)); every claim it makes links to something code or a person wrote.
- **Optional eval job.** Claude Code headless in CI (`claude -p` with `--json-schema`, `--max-turns`, `--max-budget-usd`) on Claude via Google's Agent Platform through the same keyless pool, scoring the reader prompt on six labelled scenarios: memory raised during an incident, instances raised for a launch, a pasted secret, two people's changes, no incident at all, noise only. Partner-model access on a trial account is unverified; drop it if day one says no.
- **The build.** Claude Code writes the agent and app code under [AGENTS.md](../../../AGENTS.md). Branding: "Writeback, powered by Claude", never "Claude Code Agent".

## 9. Autonomy level and prize strategy

**Level: Supervised.** The official text: "you approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way. You review the end result" ([RULES_CHECK.md](../../codex/RULES_CHECK.md#required-duo-use-and-autonomy-level)). Detection, the hold, the investigation, the MR and its checks all run alone; the person approves one outcome, keep or discard. It is not Assisted (no step-by-step approvals) and should not be Hands-off: whether a person's production fix survives is the decision that must stay human.

**Prizes.** Each project can win one path prize and one special prize ([RULES_CHECK.md](../../codex/RULES_CHECK.md#multiple-prize-eligibility-and-tie-breaking)). Target **Path A Best Supervised Agent** ($4,000) and **Most Stages Covered, Path A** ($5,000): nine stages touched in one loop that starts from a person's console edit, with configure, the field's least touched stage, at the core. Not a Most Creative contender: the three judge personas scored its innovation 6 to 7, while Night Orders, No Mouse and Forget Me score 8 to 9 ([scores_combined.json](scores_combined.json)). No environmental angle.

**Competition.** The official Supervised example (agents review, fix the pipeline, remediate, deploy to staging, a person approves production) will be copied widely, and it is the crowded release-gate shape; Writeback is not that shape. Path A entries with a human gate are thin so far (1 of 7 known ideas, simulated) ([FIELD.md section 6](../../FIELD.md#6-open-spaces-nobody-seems-to-be-in-them-yet)). Most Stages Covered will draw "all nine stages" meshes (3 of 7 known ideas, [FIELD.md section 5](../../FIELD.md#5-crowded-idea-spaces-to-avoid-ranked)); Writeback's case is "in the most creative way": one person's fix carried through every stage. Theme fit: to "How far can your agents go without you?" it answers "all the way to a held deploy and a ready MR, and no further when a person's work is at stake".

## 10. Load-bearing risk, fallback, day-one test

**The risk: the hand-off from the CI guard to the flow.** The whole product is the moment the deploy stops and the MR is already being written. That needs (a) the guard's failure, in a pipeline a person caused, to start the custom flow through the Pipeline events: Failed trigger, created with our Developer plus AI member role, and (b) the sandboxed flow, which cannot see Google Cloud, to read the guard's report intact from the job log. Three of the four score notes tie C27's score to starting the flow ([scores_gitlab_judge.json](scores_gitlab_judge.json), [scores_google_judge.json](scores_google_judge.json), [scores_anthropic_judge.json](scores_anthropic_judge.json)). The Google side is lower risk: the modifier is on the service object the deploy account already reads, so audit logs are an extra, not a dependency. The flow itself talks only to GitLab, so it needs no network allowlist, and strict mode or the default-branch-only `agent-config.yml` cannot block it.

**Fallback.** If the trigger cannot be created or does not fire, the guard's message tells the deployer to comment "@ai-writeback" on the incident (Mention trigger, a person's action), and the flow finds the latest failed guard job itself through `gitlab_api_get` (unverified). The loop survives; "already waiting" becomes "one comment away". If the flow cannot read job logs, the guard also saves `writeback-report.json` as an artifact for `gitlab_api_get` (unverified), or passes data through `conversation_history` if `final_answer` references fail ([SPONSORS.md section 6, row 2](../../SPONSORS.md#6-contradictions-between-notes-and-how-they-were-resolved)). If merging to main is Maintainer-only (unverified), every concept needs the same organizer help or the dedicated-branch route in row 6 of that table.

**Day-one test (about 90 minutes; Alex does one merge, one paste and a few clicks):**

1. Merge a stub `writeback_guard` job (main only, manual, same keyless login as `ci_deploy.sh`) that compares `MEMORY` in `deploy/service.env` with the live service, prints a `WRITEBACK-REPORT` JSON block and exits 1 on a difference.
2. Create the custom flow `writeback-probe` from `flows/writeback-probe.yml` (one agent with `get_pipeline_failing_jobs`, `get_job_logs`, `create_issue_note`), enable it, add the trigger Pipeline events: Failed. This also tests whether our role can create flows and triggers.
3. In the Cloud Run console, change memory from 256Mi to 512Mi.
4. Play `writeback_guard` on the latest main pipeline.

Pass, within 10 minutes: the job fails and reports exactly one field, `memory 256Mi -> 512Mi`, with a modifier that maps to Alex and a client name other than `gcloud` (the SDK writes `gcloud` for its own changes, `command_lib/run/flags.py`); a `writeback-probe` session started by that pipeline appears under AI > Sessions; a fixed test issue gets a note whose JSON equals the log's block byte for byte. Then set memory back to 256Mi in the console, play the job again and confirm it passes with no noise fields. Extra check in the same hour: put the guard on a pipeline schedule and see whether a scheduled failure also fires the trigger; if it does, the early warning needs no Google piece.

## 11. Red team

**Prior art.** Every piece exists somewhere:

| Prior art | What it does | Source |
|---|---|---|
| driftctl (Snyk) | "Measures infrastructure as code coverage, and tracks infrastructure drift"; "This project is now in maintenance mode." Reports only. | [README](https://github.com/snyk/driftctl/blob/main/README.md) |
| env0 Drift Cause | Names who changed a resource, how and when, by correlating cloud audit logs with IaC state | [changelog](https://docs.envzero.com/changelogs/2024/12/introducing-drift-cause-adding-context-to-drift-management) (search excerpt) |
| Firefly | "Fix Drift > Create Pull Request" aligns the IaC code with the live asset, including ClickOps hotfixes | [docs](https://docs.firefly.ai/detailed-guides/cloud-asset-inventory/remediating-drifts) (search excerpt) |
| StackGuardian, "agentic IaC" (2026-08-06) | An agent opens a PR that keeps a change in Terraform, or one that reverts it | [post](https://www.stackguardian.io/post/agentic-iac) (search excerpt) |
| AWS CloudFormation drift-aware change sets | The next update shows drift instead of silently overwriting it; AWS's own example is Lambda memory raised in the console during an outage, which a later template update would cut, letting the outage recur | [AWS blog](https://aws.amazon.com/blogs/devops/safely-handle-configuration-drift-with-cloudformation-drift-aware-change-sets/) (search excerpt) |
| Argo CD self-heal | The opposite stance: a live difference triggers a sync back to Git | [auto_sync.md](https://github.com/argoproj/argo-cd/blob/master/docs/user-guide/auto_sync.md) |
| DocSync (Feb 2026, Anthropic runner-up) | Docs drift after a merge becomes a fix MR a human must approve | [winners note](../winners/gitlab-ai-hackathon-2026-part1.md) |

What is left: most of these serve teams with an IaC platform and work on a schedule; the closest, AWS's drift-aware change sets, acts at deploy time but only for CloudFormation and leaves the decision to whoever runs the update. Writeback acts inside the one deploy that would erase the fix, for teams whose "code" is a deploy script, and hands the decision to the person who made the change, with a ready MR in their name. The mechanism is not new; the moment and the person are. The README should name this prior art before a judge does.

**Collisions.** Release gatekeepers (crowded first, and the judges' reference): a red deploy job looks like a gate, but this one judges no code, tests or scans and passes every deploy where production matches code. Incident root cause (excluded): NEXUS's demo finds "Redis connection-pool config drift" as a cause ([FIELD.md](../../FIELD.md#notes-on-each-entry)); Writeback explains no incident. Evidence receipts (crowded): keep the incident note plain, no hashes or ledger. DocSync shares the drift-to-MR shape on a different object. Loose Ends and Scar Tissue ([lens_oncall_inversion.md](lens_oncall_inversion.md#14-loose-ends), [lens_biology_assumptions.md](lens_biology_assumptions.md#b6-scar-tissue)) go the other way (undo or remodel later); they are later add-ons, not this build.

**The judges' reference project.** Its staging and production jobs run `gcloud run deploy ... --set-env-vars APP_VERSION=$CI_COMMIT_SHORT_SHA`, and production deploys automatically after the staging check ([guide](../gitlab_guide_and_reference.md#every-stage-and-job-in-gitlab-ciyml)). gcloud's help for that flag: "All existing environment variables will be removed first." So in the reference loop, a variable set by hand at 02:10 disappears on the next merge, with no human in the middle. Writeback is the piece that loop lacks; say it in one respectful line.

**What a skeptical judge would say, and the answer.**

1. *"Drift detection is old; Firefly and env0 sell this."* For Terraform estates with a platform subscription, yes. Writeback is for small teams whose deploy script is the only code, and it acts at the deploy that would do the damage, in the fixer's name.
2. *"A diff and a template would do. Where is the agent?"* Code finds the diff on purpose. Without the model you get a red job and nobody knows why or whose. The model finds the reason in incident notes, separates the fix from incidental changes, decides where it belongs in code, explains it to the person and revises on request.
3. *"Blocking deploys until Clara wakes up is worse."* Production keeps running with her fix; only deploys wait; any teammate can keep it with one merge or discard it with an approval and a merge. With no drift the guard passes in seconds.
4. *"Real teams lock the console."* Many small teams do not, and teams with full IaC still hand-edit during incidents (AWS's own example). Writeback keeps the fastest fix at 02:10 from costing an outage at 10:00.
5. *"It is staged."* The incident and persona are labelled demo data. The console edit, Google's record of who made it, the crashes, the red job, the flow run, the MR and the deploy are real.

## 12. First build step and size

**First step, today, without Alex (Claude Code, about one day):**

1. `writeback/guard.py`: a pure function from (live service JSON, `deploy/service.env` text, decisions file, people file, deploy service account) to a verdict JSON plus the plain sentence, and a 30-line CLI that takes the same `gcloud run services describe` JSON that `ci_deploy.sh` already fetches.
2. `tests/test_writeback_guard.py` with six labelled fixtures, `tests/fixtures/demo_*.json`, shaped like `gcloud run services describe --format=json` output: pipeline deploy only; console memory edit; edit already kept; edit discarded by record; environment variable added by hand (value never printed); noise only.
3. `flows/writeback-probe.yml` and a first `flows/writeback.yml`, checked against GitLab's [flow_v2.json](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/validators/json_schemas/ai_catalog/flow_v2.json) with `jsonschema` as the Duo note did, ASCII only, under 40 KiB.
4. One request to Codex, who owns `deploy/`: move the six literal flags into `deploy/service.env`, run the guard on the existing `service.json` right before `gcloud run deploy`, make `writeback_guard` its own manual job that `deploy_cloud_run` needs, and add the optional read-only drift identity with `roles/logging.viewer`.

**Size:**

| Component | Rough lines | Owner |
|---|---|---|
| Guard: diff, attribution, fingerprint, redaction, sentence | 300 Python | Claude |
| Guard tests and labelled fixtures | 300 | Claude |
| CI jobs: guard, `writeback_lint`, `writeback_rounds`, Secret Detection include | 120 YAML, 100 Python | Claude |
| Flow: event sorter, reader, writer, reviser, discard checkpoint, prompts | 250 YAML | Claude |
| Demo app: memory-hungry export path, "why this config" footer | 80 Python | Claude |
| Deploy changes: settings file, guard call, read-only identity | 40 shell | Codex |

About 1,200 lines with tests. Five build days: two before Alex is free (guard, tests, flow YAML, CI) and three with his accounts (day-one test and wiring, end-to-end runs, discard path and rehearsal), plus one day for the video. That fits the Oct 24 build deadline.

## 13. Verdict

**Yes, put it in the top three, as the third pick and the dependable build, on the condition that the day-one hand-off test passes.** It has the cleanest split in the pool (code finds the change and holds the deploy, the model finds the reason and writes the code, the person keeps or discards), needs no non-human start, uses Google Cloud for real work, covers the most stages of the top five, and is a small build (about 1,200 lines). Its day-one test also proves the plumbing No Mouse's fallback needs (a CI job's output read by a flow started from the pipeline event, [scores_engineer.json](scores_engineer.json)). Its weakness is innovation: the mechanism is sold commercially today. Two cheap adjustments help: open the video with the outage coming back (the counterfactual), and borrow Lockout Tagout's language, a lock placed in Clara's name that only her decision removes ([lens_people_rituals.md](lens_people_rituals.md#24-lockout-tagout)); unlike Lockout Tagout, whose locks needed Maintainer settings ([score_table.md](score_table.md)), this lock binds only our own deploy job, the one that would erase the fix. If Night Orders is chosen instead, the guard is a one-day add-on: anything changed under a night order gets written back in the signer's name.

**Suggested score: about 80.1, up from 77.0.**

| Dimension | Now | Suggested | Why |
|---|---|---|---|
| Impact | 7.3 | 7.7 | AWS and two vendors built features for this exact failure, so the problem is credible |
| Innovation | 6.3 | 5.7 | Detection, attribution, keep-PRs and agentic keep-or-revert already exist (section 11) |
| Presentation | 7.3 | 7.7 | The counterfactual opening shows the stakes before the product |
| Stages | 7.7 | 8 | Nine touched, eight with its own work |
| Human | 6 | 6.5 | Her name on the lock and the MR; still milder than a dark phone or a screen reader |
| Novelty | 6.3 | 6 | Empty in the field, but DocSync used drift-to-MR and NEXUS uses config drift |
| Wow | 7 | 7.5 | The red job naming Clara lands inside 30 seconds after the counterfactual |
| Feasibility | 7 | 8 | No non-human start; the modifier is readable with roles the deploy account has; same hand-off shape as the validated triage skeleton |
| Tech, design, autonomy, sponsors | 8, 7.7, 6, 8 | unchanged | |

Criteria mean 7.36, so the total is 3 x 7.36 + 8 + 6 + 6.5 + 6 + 8 + 7.5 + 2 x 8 = 80.1, level with Forget Me (80.0) and within scoring noise of it; Writeback takes third on build risk. If the flow can only start from a comment, feasibility returns to 7 and wow to 7, giving about 77.6: then it is fourth and Forget Me should hold third.
