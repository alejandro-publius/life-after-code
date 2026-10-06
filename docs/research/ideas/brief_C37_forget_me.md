# C37 Forget Me: build brief and skeptical review

Written 2026-10-06 for Alex Velazquez's solo Path A entry in Life After Code. Inputs: [CANDIDATES.md](CANDIDATES.md); the write-up in [lens_people_rituals.md](lens_people_rituals.md) (1.10) and its sibling Log Leak in [lens_oncall_inversion.md](lens_oncall_inversion.md) (2.8); the C37 notes in [scores_anthropic_judge.json](scores_anthropic_judge.json), [scores_gitlab_judge.json](scores_gitlab_judge.json), [scores_google_judge.json](scores_google_judge.json) and [scores_engineer.json](scores_engineer.json); [IDEATION_BRIEF.md](../IDEATION_BRIEF.md); [SPONSORS.md](../../SPONSORS.md) sections 1, 5 and 6; [RULES_CHECK.md](../../codex/RULES_CHECK.md); [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md); [FIELD.md](../../FIELD.md); [deploy/README.md](../../../deploy/README.md). Five web searches were used (section 11). The FTC, MediaPost, Willkie, USENIX, Meta, BigID, Justia and truto pages are blocked from this session, so facts from them come from search excerpts or from the coordinator, and say so.

## 1. Name and one-line pitch

**Forget Me.** Keep it. It is what a person means when they press "Delete account", it echoes the legal "right to be forgotten", and it fits a video title. ("Canary Person" names the mechanism, not the promise; "Ghost User" sounds like a bug.)

**Pitch:** On every release, a person who does not exist signs up, uses the new feature and asks to be forgotten; code then looks for her in every store, and a release that cannot forget her does not reach production.

## 2. Who it is for, and their story

For the developers and the privacy lead of any app with a "Delete account" button, and for the people who press it.

> Dana (a persona, not a real person) let her nine-year-old son use a homework-help app through fourth grade, and when he outgrew it she pressed "Delete account", because the app promised that everything he had typed would be gone. This week a developer adds "search your old questions", which copies every question into a new search index that the deletion job has never heard of. Children type things into homework apps that they would never say out loud, so from this release on a deleted child's words would quietly stay behind, and Dana would never know.

**Why this story replaces the original (Laila, leaving an abusive partner).** The original has the highest stakes, but a 2:40 DevSecOps video cannot treat abuse with care: it would use a survivor's danger as a hook, and survivors may be watching. It also invites a factual detour (would one leftover index entry really lead someone to her?) whose honest answer, "only if that copy leaks", weakens the scene. The parent's story is just as real and better documented: in 2023 the FTC said Amazon answered parents' requests to delete children's Alexa voice recordings by deleting the recordings but keeping the transcripts, and Amazon agreed to pay $25 million (search excerpts: [MediaPost](https://www.mediapost.com/publications/article/385888/ftc-fines-amazon-25m-over-childrens-voice-record.html), [AP via NY1](https://ny1.com/nyc/all-boroughs/ap-top-news/2023/06/01/ftc-charges-amazon-with-privacy-violations-over-alexa-and-ring-cameras), [Willkie](https://complianceconcourse.willkie.com/articles/amazon-settles-coppa-rule-and-ftc-act-violations/)). That is exactly the bug Forget Me catches: the main copy goes, a derived copy stays. If Alex prefers Laila: no abuse on screen, no partner character, one plain sentence ("she is starting over and deleting the accounts that could lead someone to her"), a support line on the closing card, and a name and setting that do not tie abuse to one culture.

## 3. The demo moment and the 2:40 video

**The moment (about 1:15).** The staging probe table after Robin, a child account that does not exist, asks to be forgotten. Four rows green, one red:

`questions_index_v2 | kept | new in !12 | marker fm7731qzx still present 60 s after deletion (3 documents) | RED`

Narration: "This is where Dana's son's questions would have stayed." Beside it, `deploy_production` is greyed out. Forty seconds later the same table is all green: "Robin is gone from everywhere, 38 seconds after she asked." The viewer feels the unease that "deleted" did not mean deleted, then relief that something checked before a real family had to rely on it.

| Time | Screen | Narration (short) |
|---|---|---|
| 0:00 to 0:12 | Phone: "Delete account. Everything your child typed will be removed." A thumb presses it. Corner label: "Persona and demo app." | "Dana deleted her son's homework account. The app promised everything he typed was gone." |
| 0:12 to 0:27 | MR !12 "Search your old questions": the one diff line that writes question words into `questions_index_v2`. | "This week, search copies every question into a new index. Nobody told the deletion job." |
| 0:27 to 0:50 | The MR: the Forget Me note and its commit to `privacy/stores.yml` (new store, journey "ask and search", transform "lowercase words"). Caption: GitLab Duo flow, Claude. | "Opening the MR starts Forget Me. Claude reads the change and decides where a person's data now lands, and what a test person must do to put it there." |
| 0:50 to 1:25 | Merge; staging deploy on Cloud Run; the `forget_me` job log: Robin signs up, asks, uploads, searches; "marker found in all 4 stores it should reach, never in the logs"; "Robin asks to be forgotten"; the table with one red row; the production job skipped. | "Code invents Robin, a child who does not exist, with a marker in every field. It proves Robin reached every store she should, presses the same delete button Dana pressed, and searches again." |
| 1:25 to 1:50 | The failed pipeline starts the gap flow. To-Do and email: approval required. In AI > Sessions: option A (delete the index entries) and B (index question IDs only). The privacy lead approves A. Fix MR !13: one handler, one test. | "The failure wakes the agent. It reads the report and the deletion code and drafts two fixes. What gets deleted is a person's call." |
| 1:50 to 2:12 | !13 merged; pipeline: 5 of 5 green, "gone in 38 s"; a person presses Play on production; Release v1.4 with the erasure table. | "A person merges the fix. Robin is gone from everywhere. Only then can a person ship it." |
| 2:12 to 2:28 | The nightly schedule on production, last runs green; one diagram: the model chooses where to look, code decides what is true, a person decides when to act; the nine-stage strip. | "Every night a new Robin signs up in production and asks to be forgotten." |
| 2:28 to 2:40 | Title card, repo and live link. | "Dana will never see any of this. She will just be right to trust the button." |

Narrated, no copyrighted music, demo data labelled on screen ([AGENTS.md](../../../AGENTS.md) rule 2). Do not open on the held pipeline: the GitLab judge marked a video that "leads with a release hold" down ([scores_gitlab_judge.json](scores_gitlab_judge.json)).

## 4. End-to-end flow (one complete loop)

1. **Plan: work item.** The promise is a work item, "Erasure promise" ("a deleted account leaves no copy in any store within 2 minutes on staging and 30 days everywhere"), linked to `privacy/stores.yml`, the list of places the app keeps personal data (four today: accounts, questions, uploads and app logs).
2. **Create: merge request and the "Merge request: Created" trigger.** A developer opens MR !12 "Search your old questions" (demo feature), which writes each question's words into a new Firestore collection, `questions_index_v2`. Opening the MR is a human action, so the trigger (added in 19.4, [guide](../gitlab_guide_and_reference.md)) starts the Forget Me map flow, a custom Duo flow.
3. **The model chooses where to look: flow tools.** A read-only mapper agent (`get_merge_request`, `list_merge_request_diffs`, `get_repository_file`) reads the diff, the store list and the deletion module, and decides: question text now also lands in `questions_index_v2`, stored as lowercase words, and only a person who asks and then searches puts data there. A writer component commits that store entry and an "ask and search" journey to the MR's own branch (`create_commit`) and posts a three-line MR note. It says nothing about whether deletion works.
4. **Verify: MR pipeline, then a person merges.** The MR pipeline runs unit tests and a schema check on the store list (only known kinds, classes and transforms). A reviewer reads the MR, including the agent's commit, and merges.
5. **Package and release to staging: main pipeline, environments.** The image is built once and deployed by digest to the `staging` Cloud Run service with keyless auth, as the deploy skeleton does ([deploy/README.md](../../../deploy/README.md)).
6. **Verify, code decides: the `forget_me` CI job.** With `id_tokens` and a read-only probe identity, code creates Robin with a fresh marker in every field, walks every journey through the app's public API, proves the marker reached every "kept" store (otherwise gray), calls the app's real delete path (`DELETE /me`, the button Dana used), polls for up to 120 s, and searches every listed store plus every collection code can list. Result: four green, one red (`questions_index_v2`, added in !12). The job fails, so the manual `deploy_production` job, which `needs: forget_me`, cannot run. The report is printed between markers in the job log and kept as an artifact.
7. **Secure and govern, a person picks the fix: "Pipeline events: Failed" trigger and `HumanInputComponent`.** The failed pipeline came from a person's merge, so it starts the gap flow. Its reader stops at once unless `forget_me` failed; otherwise it reads the report (`get_job_logs`) and the deletion module and drafts option A (delete the account's index entries) and option B (index question IDs, not text). A `HumanInputComponent` sends the privacy lead a To-Do and an email, and the privacy lead approves A in AI > Sessions ([SPONSORS.md](../../SPONSORS.md) section 1).
8. **Create: fix MR.** A fixer agent opens MR !13 (`create_branch`, `create_commit`, `create_merge_request`): one deletion handler and a unit test, noted on the promise work item.
9. **Govern and verify: merge, re-probe.** A person merges !13; the main pipeline redeploys staging and the probe runs with a new Robin: five of five green, gone in 38 s.
10. **Release: manual job, release, package.** A person presses Play on `deploy_production` (or approves a deployment, if protected environments are open to our role). A release job creates the GitLab Release with the erasure table in its notes and puts the JSON report in the generic package registry, both with `CI_JOB_TOKEN`, which may call the Releases and Packages APIs ([SPONSORS.md](../../SPONSORS.md) section 2.2).
11. **Monitor: pipeline schedule, GitLab Observability, back to plan.** Every night a schedule owned by the privacy lead runs the probe against production with a new canary and checks log retention and Cloud Storage soft delete against the promise; results go to GitLab Observability over OTLP. A red night fails the pipeline and notifies its owner, who mentions the flow on the promise work item (a human trigger), and the loop restarts at step 7.

What the model proposes and a person merges (demo app):

```yaml
# privacy/stores.yml  (demo data)
promise: {staging_window_seconds: 120, everywhere_window_days: 30}
stores:
  - {id: accounts, kind: firestore_collection, locator: "{env}_accounts", class: kept}
  - {id: app_logs, kind: cloud_logging, locator: "service={service}", class: never}
  # questions and uploads entries omitted here
  - id: questions_index_v2
    kind: firestore_collection
    locator: "{env}_questions_index_v2"
    class: kept                      # must hold the marker before deletion, and not after
    transforms: [lowercase_words]    # from a fixed menu that code implements
    reached_by: [ask_and_search]
    added_in: "!12"
journeys:
  - id: ask_and_search
    steps: ["POST /api/questions text='{marker} what is seven times eight'", "GET /api/search?q={marker}"]
```

## 5. Lifecycle stages

| Stage | Covered | GitLab feature: what happens | Real or demo |
|---|---|---|---|
| Plan | Yes, light | Work item "Erasure promise" holds the window and collects each finding and fix; a store the probe cannot read (an outside service) becomes an issue for a person to decide | Real GitLab objects; the promise text is ours |
| Create | Yes | Developer's MR !12; the flow's `create_commit` adds the store and journey to it; the flow opens fix MR !13 | Real MRs; the bug in !12 is planted on purpose and labelled |
| Verify | Yes | MR and main pipelines: unit tests, store-list schema check, the `forget_me` probe with a check before and after deletion | Real jobs on real stores; Robin is a synthetic person, labelled |
| Package | Yes, light | Image built once and deployed by digest; JSON erasure report published to the generic package registry per version | Real; mostly a standard step |
| Secure | Yes | Deletion tested as a privacy control; "never" stores catch personal data in logs; keyless `id_tokens` and a read-only probe identity; SAST and secret detection templates | Real; findings hold only the synthetic marker, so they can be public |
| Release | Yes | Environments `staging` and `production`; manual `deploy_production` with `needs: forget_me`; GitLab Release with the erasure table | Real |
| Configure | Yes, light | `privacy/stores.yml` and the promise drive the probe; the nightly run reads Cloud Logging retention and Cloud Storage soft delete and fails if a store can keep data longer than promised | Real Google settings, read by code |
| Monitor | Yes | Nightly pipeline schedule with a new canary on production; results in GitLab Observability (a Developer can enable it on our own subgroup) | Real runs; synthetic canary |
| Govern | Yes | `HumanInputComponent` for the fix direction; MR approval and merge; a person presses Play; erasure history on every release for an auditor | Real; Alex plays developer and privacy lead, labelled |

Count: **9 of 9 touched, 6 load-bearing** (create, verify, secure, release, monitor, govern) and 3 light (plan, package, configure). The lens write-up counted 5.

## 6. The agent loop

**The model may:**
- Read the MR diff, the code, the store list and the deletion module, and decide where a person's data now lands, including indirect copies (indexes, caches, exports, calls to outside services).
- Propose each new store's class (`kept`, `never`, `outside`) and its transforms, chosen from a fixed menu (lowercase words, sha256 of the normalized email, base64, URL encoding).
- Write the journeys the canary must walk so that its data reaches the new stores, and commit them to the MR's own branch, never to `main`.
- After a red probe, read the report and the deletion code, draft fix options in plain words, and open the fix MR once a person picks one.

**The model may not:**
- See or choose the marker (code makes a new one per run), or see any real person's records (the probe returns only marker hits).
- Say whether anything is deleted, or call a gap acceptable.
- Touch Google Cloud: flows reach only GitLab, and all Google access sits in CI jobs.
- Change the deletion code before a person's choice, merge, deploy, run the probe, change the promise, or reclassify a store as `outside` or `never` unless a person merges that change.
- Draft a third fix for the same gap.

**Code decides:** the marker and its variants; that the canary reached each `kept` store before deletion (else gray, which blocks); that it is gone within the window (else red, which blocks); that `never` stores never held it; that no listed or listable store still holds it (code scans every top-level Firestore collection and every object under the listed bucket prefixes, so even a copy nobody mapped turns red); that the store list fits its schema; that retention fits the promise; and, through `needs: forget_me`, that production stays closed.

**A person decides, and how:**
1. The developer and a reviewer merge the feature MR, including the agent's store-list commit (GitLab MR review).
2. The privacy lead picks the fix direction at the `HumanInputComponent` (To-Do and email; approve, reject or modify in AI > Sessions). Fallback, because the component is unverified in trigger-started flows ([SPONSORS.md](../../SPONSORS.md) section 6, row 3): the flow posts both options as an MR note and waits for a reply that mentions it (a human trigger).
3. A person merges the fix MR.
4. A person presses Play on `deploy_production`.
5. The privacy lead owns the nightly schedule and decides about stores the probe cannot read.

**Time boxes:**
- Each flow agent has `params.timeout: 300`. GitLab's validator rejects `max_cycles` ([SPONSORS.md](../../SPONSORS.md) section 6, row 1), so the flows have no loops: mapper then writer; reader then person then fixer.
- The probe job has `timeout: 15m`, at most 20 API calls per journey, and polls deletion every 10 s for up to 120 s on staging (the configured window in production).
- The optional Claude Code job runs with `--max-turns 8 --max-budget-usd 0.50`.
- **Two review rounds** ([AGENTS.md](../../../AGENTS.md) rule 5): a gap gets at most two fix MRs, each re-probed by the next pipeline. If the second is still red, the flow drafts nothing more, posts "two fixes did not close this gap" on the promise work item, the release stays held, and a person takes over. The same limit applies to journeys for a gray store and to revisions of the store-list commit.

## 7. What it needs from Google Cloud (bonus)

| Product | Used for | Free tier or cost note |
|---|---|---|
| Cloud Run | Two services: `homework-staging` and `homework` (production, the judges' link); min 0, max 1, request billing, as in [deploy/README.md](../../../deploy/README.md) | 2 million requests, 180,000 vCPU-seconds and 360,000 GiB-seconds a month per billing account ([SPONSORS.md](../../SPONSORS.md) 4.1) |
| Firestore (Native, default database) | `accounts`, `questions` and the new `questions_index_v2`, prefixed by environment, because only one database per project is free | 1 GiB; 50,000 reads, 20,000 writes and 20,000 deletes a day; a probe run scans a few hundred documents twice, so dozens of runs a day fit |
| Cloud Storage | Uploaded worksheet photos, one bucket per environment | 5 GB-months, 5,000 Class A and 50,000 Class B operations a month in US regions ([deploy/README.md](../../../deploy/README.md)); soft delete keeps deleted objects for a while (7 days by default, unverified), so disable it on the uploads bucket, as the skeleton does for its source bucket, or report it as a timed store |
| Cloud Logging | The app's structured logs, a `never` store | First 50 GiB ingested per project, 30-day default retention included; single entries cannot be deleted (unverified, per [lens_oncall_inversion.md](lens_oncall_inversion.md) 2.8), which is why logs must never hold the marker |
| IAM and Workload Identity Federation | Runtime service account (read and write on its own stores); a new probe service account, read-only (`roles/datastore.viewer`, `roles/storage.objectViewer`, `roles/logging.viewer`, plus bucket metadata read); only protected `main` pipelines of our project may impersonate it | No cost |
| Artifact Registry, Cloud Build | Image built once, deployed by digest (existing skeleton) | 0.5 GiB-month storage; 2,500 build-minutes a month |
| Optional: Cloud Scheduler and a Cloud Run job | Nightly fallback if a GitLab schedule on protected `main` is not allowed for our role | 3 scheduler jobs per billing account; Cloud Run jobs 240,000 vCPU-seconds a month |
| Optional: Claude on Google's Agent Platform | The Claude Code adversary job (section 8) | Billed per token; whether the $300 Free Trial credit covers partner models is unverified |

Needed from Codex in `deploy/`: a second Cloud Run service, a Firestore database, the buckets, the probe service account and its binding. The skeleton today "does not create a database" and is "one public service, not separate staging and production services" ([deploy/README.md](../../../deploy/README.md)). Put the non-secret Google IDs in `.gitlab-ci.yml`, since CI/CD variables need Maintainer ([DECISIONS.md](../../DECISIONS.md)). The USD 5 budget alert stays; budgets do not cap spending.

## 8. How Anthropic models show up

- **Inside GitLab.** Both flows run on Duo's default model, Claude Sonnet 4.6 served from Google's Agent Platform. Custom flows reject a `model` field and only the top-level group Owner (GitLab) can change it, so the README says so plainly instead of claiming a choice ([SPONSORS.md](../../SPONSORS.md) section 1, point 3). One flow run touches all three sponsors.
- **The model does what code cannot.** It reads a diff and sees that question text now flows into a new index, predicts how the copy will look (lowercase words), and picks the journey that puts the canary's data there. Without that, a hand-written erasure test goes stale with every feature. Code still decides every result.
- **Optional adversary (day 8 or later).** A CI job on `main` runs Claude Code headless (`claude -p`) on Google's Agent Platform with keyless WIF (`CLAUDE_CODE_USE_VERTEX=1`), the full model name `claude-sonnet-5-5` (the `sonnet` alias still means Sonnet 4.5 on Google Cloud), `--permission-mode dontAsk`, read-only tools, `--json-schema`, `--max-turns` and `--max-budget-usd` ([SPONSORS.md](../../SPONSORS.md) section 5, point 6). Its question: "Where could a copy of this person hide after this change?" It runs just before the probe; code adds any extra store it names to that run's search and prints where it disagrees with the mapper in the job log, which the gap flow quotes (a CI job token cannot post notes). That gives a second, independent reader.
- Fix MRs can also get Duo Code Review, which runs on Claude Sonnet 5.5 since 2026-10-05.
- Name it "Forget Me, powered by Claude", never "Claude Code Agent".

## 9. Autonomy level and prize strategy

**Level: Supervised.** The official text: "you approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way" ([RULES_CHECK.md](../../codex/RULES_CHECK.md)). Forget Me's agents map the stores, write the journeys, clear the store-list gate, read the red result and draft the fix without asking; a person approves outcomes: the fix direction, the fix, the production release. That mirrors the official example's "You get a summary and approve the production deployment." Not Hands-off: a red result must never be fixed and shipped with nobody in the middle, because a wrong deletion fix deletes the wrong data, a failure DELF names (section 11). Letting green releases promote alone could be a later setting; claim Supervised anyway. Not Assisted: nobody approves each step.

**Prizes** (each project can win one path prize and one special prize, [RULES_CHECK.md](../../codex/RULES_CHECK.md)):
- **Path prize: Path A Best Supervised Agent ($4,000).** Path A entries with a human gate are thin so far (1 of 7 known ideas, simulated, [FIELD.md](../../FIELD.md) section 6), but the official Supervised example (review, fix a pipeline, remediate a finding, deploy to staging, approve production) will pull many look-alikes later (inference). Forget Me's gate is a planted-person erasure test, not a scan, which stands apart only if the first 30 seconds show it.
- **Special prize: aim first at Most Stages Covered for Path A ($5,000; one award per path; "touching the stage counts").** The known entries built to cover many stages are Path B (BABYDOV says it is "also optimized for" the prize, and Receipted Pipeline), so they compete for the other award; the one known Path A entry touches four stages ([FIELD.md](../../FIELD.md) section 2). Forget Me touches all nine, six of them load-bearing, with touches a judge can call creative: a person who does not exist in verify, the retention promise in configure, the report as a package. Show the nine with evidence in the description, but do not pitch an "all nine stages" project, which is crowded framing ([FIELD.md](../../FIELD.md) section 5, rank 7).
- **Second chance: Most Creative ($4,000, the top Innovation score in either path).** No October entry, June category or February catalog cluster is about deletion ([FIELD.md](../../FIELD.md) sections 4 to 6), and the canary person is easy to remember, but the prior art in section 11 lowers its Innovation score, and it competes with both paths.

## 10. Load-bearing risk, fallback and day-one test

**The risk: proving presence before absence, on real stores.** A green only means something if the canary provably reached each store before deletion and code can find it there afterwards. Three things can break that: Google access from CI (keyless, read-only, `main` only, never tried in our account), a copy whose shape hides the marker (lowercased, split into words, hashed), and slow writes or log ingestion that make "not found" ambiguous. If these fail, the honest output is gray on every new store, and there is no demo moment.

**Fallback, in order:**
1. If the probe identity cannot be used from CI: run the same probe as a Cloud Run job under the probe service account, started by the deploy identity the skeleton already uses (`gcloud run jobs execute --wait`; Codex adds that one permission), and take the job's exit code and log as the result.
2. If several stores eat the build: cut to Firestore (accounts, questions, the new index) plus Cloud Logging. The red row survives.
3. If Google access fails entirely: run the probe in CI against a local instance of the release candidate (Firestore emulator, local files, a log file), as the engineer proposed ([scores_engineer.json](scores_engineer.json)). The loop and the flows stay; the bonus and some Tech score go.

**Day-one test** (needs Alex for about 30 minutes, the first day he can, ideally by Oct 13):
1. Codex adds the read-only probe service account, a Firestore database, one bucket and the WIF binding to `deploy/setup_gcp.sh`; Alex runs it in Cloud Shell.
2. Claude adds a minimal app (`POST /signup`, `POST /questions`, `POST /upload`, `DELETE /me`; writes to two collections and the bucket, logs one line with the marker on purpose so the log search is tested, and writes a `shadow_copy` collection that the delete path skips on purpose) and a `forget_me_smoke` job on `main` with `id_tokens` (audience `https://gitlab.com`).
3. Alex merges, or plays the manual job, on `main`.

Pass, in under 5 minutes: the marker is found in both collections, the bucket and Cloud Logging (the log line within 90 s); after `DELETE /me` it is gone from both collections and the bucket; `shadow_copy` is reported RED; and a write with the probe identity returns 403. Anything else: switch to the matching fallback that day. In the same sitting (15 minutes), open a test MR to confirm that the "Merge request: Created" trigger starts a flow whose `create_commit` lands on the MR branch, and that a `HumanInputComponent` raises the To-Do.

Shared risks that gate every concept, not this one in particular: merging to the protected `main` in October subgroups, creating flows and triggers with the Developer role plus the AI role, Maintainer-only CI/CD variables, protected environments, and pipeline schedules on protected `main` (all unverified, [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md) gotchas).

## 11. Red team

**Prior art.** Searches used: privacy code scanners in pull requests; erasure checks with a synthetic user; hackathon erasure agents; DELF; the FTC Alexa case.

| What | What it does | How close | How Forget Me differs |
|---|---|---|---|
| [BigID data deletion validation](https://home.bigid.com/data-deletion-validation-datasheet) (coordinator; blocked here) | Commercial check that deleted data is gone from the sources it scans | Same goal | Scans sources it was set up for, after requests; not tied to each release's code |
| [US patent 11354435](https://patents.justia.com/patent/11354435) (coordinator; blocked here) | Test data subjects used to confirm deletion | The canary person itself | The mechanism is not new; the release loop around it is |
| [Truto: automating DSAR verification](https://truto.one/blog/closing-the-loop-on-privacy-automating-dsar-verification-with-unified-apis/) (coordinator; blocked here) | Checks deletions across connected SaaS apps through unified APIs | Verification after deletion | Integration level, no reading of code changes |
| Meta's DELF, USENIX Security 2020 ([USENIX](https://www.usenix.org/conference/usenixsecurity20/presentation/cohn-gordon), [Meta](https://research.fb.com/publications/delf-safeguarding-deletion-correctness-in-online-social-networks/); search excerpts) | Developers annotate data types; checked statically and dynamically; "detected, surfaced, and helped developers correct thousands of omissions and dozens of mistakes" | Same bug class, at scale; also names "deleting the wrong data" | Needs a framework in every data type; Forget Me is black-box: any app, any store, no rewrite |
| HoundDog.ai ([devops.com](https://devops.com/hounddog-ai-code-scanner-shifts-data-privacy-responsibility-left/), [Carahsoft](https://www.carahsoft.com/hounddog); search excerpts) | Static scanner that follows personal data into logs, files and third parties and blocks unsafe pull requests | The diff-reading half | Scans code; Forget Me runs a person through the deployed app and searches real stores |
| [Ethyca erasure guide](https://www.ethyca.com/guides/right-to-be-forgotten-erasure-infrastructure) (search result) | Privacy as code and erasure orchestration | Store inventory and orchestration | Orchestration trusts the inventory; Forget Me tests whether it is still true after each release |
| [The Aegis Agent](https://lablab.ai/ai-hackathons/agentic-ai-hackathon-ibm-watsonx-orchestrate/aegis-agent/the-aegis-agent), lablab.ai IBM watsonx hackathon (search excerpt) | An agent that carries out deletion requests with anonymization | A hackathon erasure agent | Does the deleting; proves nothing after a release |

So the canary person and the marker search are known. What is new is the loop: each release's diff decides where the canary must walk and what its copies look like, code proves present-then-absent on the real stores, and a person decides the fix, inside GitLab's MR and release flow, re-run nightly.

**Collisions.**
- *Security scanning* (crowded, [FIELD.md](../../FIELD.md) section 5, rank 2): the diff reading looks like a privacy scanner. Lead with the runtime proof, never with "we scan your MR for personal data".
- *Evidence receipts and attestation* (rank 6): an erasure report per release looks like a receipt. Never say receipt, ledger, attestation or tamper-evident; the report is a five-row table for a person.
- *Release gatekeeper* (rank 1): the held production job is the gatekeeper shape. Show it for one second, after the red row.
- *Proof of Fix* (excluded): [FIELD.md](../../FIELD.md) section 3 lists "a synthetic user check" after a merge as the same idea. Stay clear: the probe tests a standing property of every release on staging, before release, not whether one fix worked; the nightly production run monitors that same property; no flow reopens or closes issues from production signals; the green re-run is "this release passes", never "the fix is proven in production".
- *Log Leak* (sibling C17): logs are one `never` store here, tested with the synthetic marker only, so Forget Me never reads real customers' log lines.

**What a skeptical judge would say, and the answer.**
1. *"It is an integration test with an LLM attached."* The test is easy for the stores you remember. The bug is the store nobody remembered: DELF found thousands of omissions at Meta, and the FTC case was a derived copy (transcripts) that outlived deletion. A hand-written test goes stale with every feature; the model keeps it current by reading each diff to choose the canary's journeys and the copy's shape, and code still decides every result.
2. *"Your bug is planted."* Yes, and labelled. The stores, the probe and the delete path are real, and the same probe runs nightly on production with nothing planted.
3. *"A marker search misses hashed or transformed copies, so green is not proof."* Code searches variants from a fixed menu, and a store that did not show the marker before deletion is gray and blocks. The report states its scope: the paths Robin walked, the listed stores and every store code can list.
4. *"Backups, soft deletes and logs cannot be deleted item by item."* They are checked against the promise window (for example "soft delete keeps objects 7 days; the promise allows 30"), and logs must never hold the marker at all.
5. *"Fake users pollute production."* One canary a night, a reserved `.invalid` email domain, an `is_canary` flag excluded from analytics, removed by the same delete path: ordinary synthetic monitoring.
6. *"The probe can read every store."* Read-only, keyless, limited to protected-branch pipelines of one project, and code prints only marker hits. Fallback 1 keeps even that identity inside Google.
7. *"One person plays every role."* Labelled in the video; each human decision is a separate GitLab action (approval, merge, Play) with its own audit trail.

## 12. First build step and build size

**Start today, no accounts needed** (Python 3.12, FastAPI, uv, pytest, per [AGENTS.md](../../../AGENTS.md)):
1. `forgetme/marker.py`: a marker (`fm` plus 7 random lowercase letters and digits, which survives lowercasing and word splitting), the canary profile and its variants.
2. `forgetme/rules.py`: the `kept`, `never`, `outside` and timed classes; the before and after checks; green, red and gray; polling inside the window.
3. `forgetme/stores/`: one interface, an in-memory fake and a SQLite adapter; Firestore, Cloud Storage and Cloud Logging adapters written against their client libraries and tested only with labelled fakes until Alex's project exists.
4. `forgetme/report.py`: a Markdown table and JSON, printed between markers so a flow can read them with `get_job_logs`.
5. `demo_app/` "Homework Helper (demo)": sign up, ask, upload, search, delete; the planted `questions_index_v2` on its own branch.
6. `privacy/stores.yml` and its JSON schema; `flows/forget-me-map.yml` and `flows/forget-me-gap.yml` drafted to the custom flow rules (ASCII only, no `model`, no `max_cycles`, [gitlab_guide_and_reference.md](../gitlab_guide_and_reference.md) gotchas).
7. One end-to-end pytest: the app with the planted index gives exactly one red row; with the fix, all green.

| Component | Lines (rough) | Builder days |
|---|---|---|
| Demo app with store layer and delete path | 500 | 1.5 |
| Probe core: marker, variants, rules, report, CLI | 450 | 1 |
| Store adapters and settings readers (retention, soft delete) | 350 | 1 |
| Tests and labelled fakes | 600 | 1 |
| `.gitlab-ci.yml`: tests, schema check, staging, probe, manual production, release, package, nightly | 200 | 0.5 |
| Google setup additions (Codex, `deploy/`) | 150 | 1 |
| Two Duo flows, prompts, `skills/forget-me/SKILL.md` | 300 | 1.5 |
| README, demo labels, video script | n/a | 1 |
| Optional Claude Code adversary job | 100 | 0.5 |
| **Total** | **about 2,650 (600 of them tests)** | **about 8.5** |

Alex's time: about 90 minutes in all (Google setup, creating the flows and triggers in the UI, merges), plus recording. It fits before Oct 24 if the day-one test passes by about Oct 13.

## 13. Verdict

**Yes, keep it in the top three, as third.** It trails C01 Night Orders (88.6) and C13 No Mouse (85.6) on the 30-second moment ([score_table.md](score_table.md)), but it depends least on unverified platform behavior: no flow start at night (C01's open question), no browser inside the flow sandbox (C13's), only human-started triggers, standard flow tools and the CI-to-Google path the deploy skeleton already uses. That makes it the safest third and a ready fallback if either leader fails its day-one test.

Suggested adjustment: **+1.4, from 80.0 to about 81.4**, if the design above is adopted (Robin's before-and-after check, the transform menu, the nine-stage loop, the gentler story).

| Dimension | Now | Suggested | Reason |
|---|---|---|---|
| Tech | 7.7 | 8.0 | Real Firestore, Cloud Storage and Logging; keyless read-only probe; two flows on human triggers |
| Design | 7.3 | 7.5 | One closed loop from MR to nightly production check, fix MR inside it |
| Impact | 8.0 | 8.5 | This exact bug class is documented (FTC v. Amazon; DELF's omissions) |
| Innovation | 8.3 | 8.0 | Canary deletion checks are patented and sold; only the release loop is new |
| Presentation | 7.0 | 7.0 | Strong red row, but it needs one sentence of setup |
| Stages | 5.7 | 7.0 | 9 of 9 touched, 6 load-bearing (the lens counted 5) |
| Autonomy | 5.7 | 6.0 | Fits the official Supervised text cleanly; thin Path A field so far |
| Human | 8.0 | 8.0 | Gentler story with a documented precedent; equal if told well |
| Novelty | 8.7 | 8.0 | Prior art found: BigID, the patent, DELF, HoundDog |
| Sponsors | 7.7 | 8.0 | Duo flows on Claude, five Google products, optional Claude Code |
| Wow | 7.3 | 7.0 | The moment lands near 1:15, not in the first 30 seconds |
| Feasibility | 7 | 7 | More Google setup than average, but three fallbacks |

Criteria mean 7.8, so 3 x 7.8 + 7.0 + 6.0 + 8.0 + 8.0 + 8.0 + 7.0 + 2 x 7 = 81.4. If the day-one test fails and only the local fallback works, take off about 3 to 4 points (Tech, Sponsors, Stages, the bonus), which puts it level with C27 Writeback (77.0).
