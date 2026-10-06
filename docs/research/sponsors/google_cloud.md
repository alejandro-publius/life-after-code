# Google Cloud: deploying Life After Code from GitLab CI

Checked: 2026-10-06. Author: Claude Code research pass for Alex Velazquez.

How this was checked:

- Links go to the normal web page for each source. Unless a note says otherwise, the content was fetched and read today. GitHub files were read through raw.githubusercontent.com, GitLab files through the gitlab.com repository API, and package dates through the PyPI and npm registry APIs, because github.com pages and docs.gitlab.com are blocked here.
- `docs.cloud.google.com` (all Google Cloud product docs) and `docs.gitlab.com` are blocked here. GitLab docs were read from their source files in the `gitlab-org/gitlab` repository on gitlab.com. Google Cloud facts come from `cloud.google.com` pricing, product and blog pages, which are readable.
- "[gcloud help]" means the text came from the built-in `--help` of the gcloud CLI installed here (Google Cloud SDK 530.0.0, July 2025). The same text is published under `docs.cloud.google.com/sdk/gcloud/reference/...`.
- Release dates marked "[PyPI]" or "[npm]" come from the package registries' own metadata.
- "(search excerpt)" means only a search engine summary was seen, not the page.
- "(unverified)" means I could not confirm it from a readable primary source today.

## Short version

1. The $300 Free Trial lasts 90 days and cannot bill you unless you click "Upgrade" ([Free Trial FAQ](https://cloud.google.com/signup-faqs)). If Alex signs up on 2026-10-06 the trial ends on about 2027-01-04 (my date arithmetic), which should cover judging (October judging dates unverified).
2. Cloud Run's free tier (request-based billing) is 2 million requests, 180,000 vCPU-seconds and 360,000 GiB-seconds per month per billing account ([Cloud Run pricing](https://cloud.google.com/run/pricing)). A hackathon demo that scales to zero should cost nothing.
3. Budgets and alerts do not stop spending. Google announced Cloud Run "billing caps" as "coming soon" and project "Spend Caps" as a private preview on 2026-04-22 ([Cloud Run at Next '26](https://cloud.google.com/blog/products/serverless/whats-new-for-cloud-run-at-next26), [Next '26 recap item 139](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up)). Until those reach general availability, the safety nets are the trial, `--max-instances`, a budget with Pub/Sub alerts, and deleting the project after judging.
4. Keyless auth works on GitLab.com Free with plain `id_tokens` plus Workload Identity Federation (WIF). It needs no GitLab project settings and no CI/CD variables, which matters because the hackathon workspace gives Alex the Developer role. Exact commands and a `.gitlab-ci.yml` are in the "Keyless auth" section below.
5. GitLab's own hackathon reference project deploys to Cloud Run with a service account JSON key ([hello-world-showcase .gitlab-ci.yml](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml)). Doing the same thing keyless is an easy, visible improvement.
6. Google's GitLab CI/CD components (`gitlab.com/google-gitlab-components`, including the Cloud Run deploy component) were all archived on 2026-03-18. Do not build on them.
7. Vertex AI is now "Gemini Enterprise Agent Platform", and Agent Engine is now "Agent Runtime" (announced 2026-04-22). The newest Gemini models on its pricing page are Gemini 3.8 Flash and Gemini 3.1 Pro Preview.

## Launches 2025-2026

Dates are the publication date of the linked source. "SDK date" means the day the model was added to Google's Gen AI Python SDK, which is close to, but not proof of, the launch date.

| Date | What launched | Status at the time | Why it matters here | Source |
|---|---|---|---|---|
| 2025-04-09 | Agent Development Kit (ADK, open source), Agent Engine ("fully managed agent runtime in Vertex AI"), Agent2Agent (A2A) protocol, Agent Garden, announced at Google Cloud Next '25 | ADK open source; A2A new open protocol | The start of Google's current agent stack | [Vertex AI multi-agent post](https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai), [Next '25 recap items 14 to 17](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2025-wrap-up) |
| 2025-04 (Next '25) | Gemini 2.5 Pro in public preview; Cloud Run multi-region deploys (public preview) and worker pools (private preview) | Preview | Background only | [Next '25 recap items 1 and 230](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2025-wrap-up) |
| 2025-05-20 | ADK 1.0.0 (Python) | Stable | | [PyPI google-adk](https://pypi.org/project/google-adk/#history) |
| 2025-06-02 | Cloud Run GPUs (NVIDIA L4), pay per second, scale to zero | GA | Not needed for this project | [Cloud Run GPUs GA](https://cloud.google.com/blog/products/serverless/cloud-run-gpus-are-now-generally-available) |
| 2025-06-25 | Gemini CLI 0.1.0, open source (Apache-2.0) | First release | Terminal agent that can run headless in CI | [npm @google/gemini-cli](https://www.npmjs.com/package/@google/gemini-cli?activeTab=versions) [npm], [README](https://github.com/google-gemini/gemini-cli/blob/main/README.md) |
| 2025-07-30 | A2A spec v0.3.0 (gRPC support, signed security cards); Google Cloud A2A developer toolkit on 2025-07-31 | Released | | [A2A CHANGELOG](https://github.com/a2aproject/A2A/blob/main/CHANGELOG.md), [A2A toolkit post](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) |
| 2025-10-09 | Gemini Enterprise (workplace agent platform; Agentspace was folded into it) | Launched | Business product, not needed here | [Introducing Gemini Enterprise](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise) |
| 2025-11-19 | Gemini 3 (Gemini 3 Pro) in Vertex AI and Gemini Enterprise | Available | Start of the Gemini 3 family | [Bringing Gemini 3 to Enterprise](https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-is-available-for-enterprise) |
| 2025-12-10 | Google-managed remote MCP servers for Google and Google Cloud services | Announced | Agents can call Google Cloud through MCP without hosting a server | [MCP support for Google services](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services) |
| 2026-02-03 | NVIDIA RTX PRO 6000 GPUs on Cloud Run | Preview; GA announced 2026-04-22 | Not needed here | [RTX PRO 6000 post](https://cloud.google.com/blog/products/serverless/cloud-run-supports-nvidia-rtx-6000-pro-gpus-for-ai-workloads), [Cloud Run at Next '26](https://cloud.google.com/blog/products/serverless/whats-new-for-cloud-run-at-next26) |
| 2026-02-26 | `gemini-3.1-pro-preview` (SDK date) | Listed as "Gemini 3.1 Pro Preview" on the pricing page today | Strongest Gemini Pro model listed | [Gen AI SDK CHANGELOG](https://github.com/googleapis/python-genai/blob/main/CHANGELOG.md), [Agent Platform generative AI pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) |
| 2026-03-12 | A2A spec v1.0.0 (v1.0.1 on 2026-05-26); Python `a2a-sdk` 1.0.0 on 2026-04-20, latest 1.2.2 on 2026-10-05. A2A is "an open source project under the Linux Foundation, contributed by Google" | Stable 1.x | If our agents talk to other agents, A2A is the Google-backed standard | [A2A CHANGELOG](https://github.com/a2aproject/A2A/blob/main/CHANGELOG.md), [A2A README](https://github.com/a2aproject/A2A/blob/main/README.md), [PyPI a2a-sdk](https://pypi.org/project/a2a-sdk/#history) [PyPI] |
| 2026-03-13 | Identity-Aware Proxy (IAP) integration with Cloud Run | Post published (status not read) | One way to protect an admin page without writing auth code | [IAP with Cloud Run](https://cloud.google.com/blog/products/serverless/iap-integration-with-cloud-run) |
| 2026-03-18 | All 7 `google-gitlab-components` projects archived (Cloud Run, Artifact Registry, Cloud Deploy, Cloud SDK, GKE, App Engine, Cloud Storage) | Archived | Do not depend on them | [cloud-run component](https://gitlab.com/google-gitlab-components/cloud-run), see the GitLab section |
| 2026-04-09 | Cloud Run worker pools | GA | Pull-based workers, for example an agent consuming a queue | [Worker pools at Estee Lauder](https://cloud.google.com/blog/products/serverless/cloud-run-worker-pools-at-estee-lauder-companies) |
| 2026-04-22 | Gemini Enterprise Agent Platform, "the evolution of Vertex AI": Agent Studio, upgraded ADK (graph-based), re-engineered Agent Runtime (multi-day agents, Memory Bank, Sessions), Agent Identity, Agent Registry, Agent Gateway, Agent Simulation, Agent Evaluation, Agent Observability, Agent Optimizer, Agent Sandbox; 200+ models including Anthropic Claude Opus, Sonnet and Haiku | Announced at Next '26 | Use the new names. "Moving forward, all Vertex AI services and roadmap evolutions will be delivered exclusively through the Agent Platform" | [Agent Platform announcement](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform), [product page](https://cloud.google.com/products/gemini-enterprise-agent-platform) |
| 2026-04-22 | Cloud Run at Next '26: remote Cloud Run MCP server (GA), AI Studio full-stack deploys (GA), RTX PRO 6000 (GA); Cloud Run instances, SSH, ephemeral disk (preview); sandboxes, billing caps, service bindings ("coming soon") | Mixed | Billing caps would solve the "no surprise charges" problem once live | [Cloud Run at Next '26](https://cloud.google.com/blog/products/serverless/whats-new-for-cloud-run-at-next26) |
| 2026-04-22 | Gemini Cloud Assist, proactive operations: alert-triggered investigations, gcloud/kubectl/Terraform operations, a FinOps cost-anomaly agent, and Cloud Assist exposed as MCP servers usable from Gemini CLI | Announced | Direct tie-in to incident response, a post-code stage | [Gemini Cloud Assist at Next '26](https://cloud.google.com/blog/products/application-development/gemini-cloud-assist-at-next26) |
| 2026-04-22 | Spend Caps for AI Studio, Agent Platform, Cloud Run, Cloud Run functions and Maps: "These caps alert and ultimately pause API traffic once your set budget is reached." | Private preview (sign-up form) | Not available to us without approval | [Next '26 recap item 139](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up) |
| 2026-04-29 | Gen AI SDK adds `enterprise=True` / `GOOGLE_GENAI_USE_ENTERPRISE` for the Gemini API on Agent Platform (SDK 2.0.0 followed on 2026-05-07) | Released | Lets a Cloud Run service call Gemini with its service account, no API key | [Gen AI SDK CHANGELOG](https://github.com/googleapis/python-genai/blob/main/CHANGELOG.md), [Gen AI SDK README](https://github.com/googleapis/python-genai/blob/main/README.md), [PyPI google-genai](https://pypi.org/project/google-genai/#history) [PyPI] |
| 2026-05-19 | ADK 2.0.0: "Workflow Runtime" (graph-based execution with routing, loops, retry, human-in-the-loop), "Task API" for agent-to-agent delegation, "Tool Confirmation" (human approval before a tool runs); `adk deploy cloud_run`. Latest 2.11.0 on 2026-10-02. Also in Java, Kotlin, Go and TypeScript | Stable | Fits our "human decides" rule directly | [PyPI google-adk](https://pypi.org/project/google-adk/#history) [PyPI], [ADK README](https://github.com/google/adk-python/blob/main/README.md) |
| 2026-05-20 | Gemini 3.5 Flash (SDK date) | Listed on pricing page | | [Gen AI SDK CHANGELOG](https://github.com/googleapis/python-genai/blob/main/CHANGELOG.md) |
| 2026-05-21 | Google I/O 2026: AI Studio apps deploy to Cloud Run on the "Google Cloud Starter Tier", "no billing account required", up to two full-stack apps | Announced | Works from AI Studio, not from GitLab CI (unverified), so not our path | [AI Studio and Starter Tier post](https://cloud.google.com/blog/products/databases/vibe-coded-ai-studio-apps-with-firestore-firebase-cloud-sql) |
| 2026-05-28 | Google SRE publishes its principles for agentic operations ("SRE AI") | Guidance | A good lens for how Google people judge operations agents | [AI in SRE](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations) |
| 2026-07-20 | Cloud Run readiness probes and "service health" for automatic regional failover | Announced | Health signals an ops agent can read | [Multi-region Cloud Run](https://cloud.google.com/blog/products/serverless/cloud-run-multi-region-services-enhanced-for-high-availability) |
| 2026-08-13 | Gemini 3.7 Flash (SDK date) | Listed on pricing page | | [Gen AI SDK CHANGELOG](https://github.com/googleapis/python-genai/blob/main/CHANGELOG.md) |
| 2026-08-27 | Cloud Run instances: one long-lived instance, up to 7 days continuous runtime, a stable HTTPS URL, stop and resume; "$5.70" for 1 vCPU and 1 GiB running 30 days; `gcloud beta run instances create` | Preview | Possible home for an always-on watcher agent, but preview | [Cloud Run instances](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-instances) |
| 2026-09-02 | Gemini 3.8 Flash (SDK date). Introductory price $0.75 input / $3.75 output per 1M tokens through 2026-12-31, then $1.50 / $7.50 | Listed on pricing page | A sensible default Gemini model for agent steps (my view; Flash-Lite models are cheaper) | [Gen AI SDK CHANGELOG](https://github.com/googleapis/python-genai/blob/main/CHANGELOG.md), [Agent Platform generative AI pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) |
| 2026-09-29 | Gemini CLI 0.62.0 (stable releases weekly). Free tier "60 requests/min and 1,000 requests/day with personal Google account". Headless: `gemini -p "..." --output-format json`. README lists a GitHub Action; no GitLab CI integration is mentioned | Stable | Could run inside a GitLab CI job as a helper | [npm @google/gemini-cli](https://www.npmjs.com/package/@google/gemini-cli?activeTab=versions) [npm], [README](https://github.com/google-gemini/gemini-cli/blob/main/README.md) |
| 2026-09-30 | Google Cloud CLI remote MCP server: tools `run_gcloud_command` and `run_bq_command` at `cloudcli.googleapis.com/mcp`; needs role `roles/mcp.toolUser`; "There is no additional charge to use the MCP server itself"; calls run "with the permissions of the authenticated caller identity" and can be audit-logged | Public preview | An agent can run gcloud without gcloud in its container | [Cloud CLI remote MCP server](https://cloud.google.com/blog/products/ai-machine-learning/google-cloud-cli-remote-mcp-server-in-preview) |
| Date unverified | Google Antigravity "Now available through Agent Platform", with an "Antigravity CLI" | Unverified | Background only | [Agent Platform product page](https://cloud.google.com/products/gemini-enterprise-agent-platform) |

Other model facts from the [Agent Platform generative AI pricing page](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) (read 2026-10-06):

- Gemini models listed: 3.8 Flash, 3.8 Flash Cyber, 3.8 Live API, 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Pro Preview, 3.1 Flash-Lite, 3 Flash Preview, plus image models.
- Gemini 3.1 Pro Preview: $2.00 input / $12.00 output per 1M tokens (prompts up to 200K tokens).
- Anthropic Claude models are listed as "Partner models", including Claude Sonnet 5 at $2.00 input / $10.00 output per 1M tokens. Whether Free Trial credit covers partner models is unverified.
- "CodeMender" is listed as a token-priced service. What it does on Agent Platform could not be read here (unverified).

## Cloud Run and the free tier (exact numbers)

### The $300 Free Trial and billing

All from the [Google Cloud Free Trial FAQ](https://cloud.google.com/signup-faqs) unless noted:

- "The Google Cloud Free Trial is a 90-day program." Signing up "creates a Free Trial billing account that is preloaded with $300 in free Welcome credit which is valid for 90 days."
- "You will not be billed for any Google Cloud usage during your Free Trial."
- A payment method is still required: "we ask for your name, address, and payment method to verify your identity." You may see a pending authorization, which is "not a charge."
- "Your Free Trial billing account auto-closes if you spend the $300 credit or 90 days pass from signup, and you won't be charged unless you manually upgrade to a paid account."
- At the end: "When your trial ends, your workloads get shut down." You can restore them "within 30 days of your trial ending by upgrading to a paid account." After that grace period, "your workloads get deleted and you will not be charged."
- After a manual upgrade, the account is "pay-as-you-go"; you keep the remaining credit until it expires and pay only for usage beyond the credit and the free tier.
- Eligibility: the $300 is for people who have "never been a paying customer of Google Cloud, Google Maps Platform, or Firebase" and have not used the Free Trial before. Google accounts with only a phone number are not supported.
- Free tier products are separate from the credit: usage up to the monthly limits is "not charged against your $300 free credit" and the free usage limit "does not expire, but is subject to change" ([cloud.google.com/free](https://cloud.google.com/free)).

Is a billing account required? The Free Trial creates one, so in practice yes. Cloud Run, Artifact Registry, Cloud Build and Secret Manager need billing enabled on the project (unverified, the docs host is blocked; GitLab's own Google Cloud runner tutorial lists "Billing enabled" as a prerequisite, [source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/runners/provision_runners_google_cloud.md)). Exceptions seen today: the BigQuery sandbox works without a billing account ([FAQ](https://cloud.google.com/signup-faqs)); Firestore's free quota works until "you need more quota" ([Firestore pricing](https://cloud.google.com/firestore/pricing)); the AI Studio "Starter Tier" needs no billing account but is driven from AI Studio ([post](https://cloud.google.com/blog/products/databases/vibe-coded-ai-studio-apps-with-firestore-firebase-cloud-sql)).

Practical tips (my advice): sign up with a personal Google account, not a berkeley.edu account. A university Google Workspace account may place the project under the university's organization and its policies, for example blocking public access to Cloud Run (unverified). The Google Cloud student page offers "200 free Google Skills credits" for training labs, which are not billing credit ([Google Cloud for students](https://cloud.google.com/edu/students)).

### Always Free limits (per month unless noted)

| Product | Free amount | Counted per | Price after the free amount | Source |
|---|---|---|---|---|
| Cloud Run services, request-based billing (the default) | 2 million requests; first 180,000 vCPU-seconds; first 360,000 GiB-seconds | Billing account, all projects together | CPU $0.000024 per vCPU-second, memory $0.0000025 per GiB-second, $0.40 per million requests (Tier 1 regions) | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Cloud Run services, instance-based billing | First 240,000 vCPU-seconds; first 450,000 GiB-seconds | Billing account | CPU $0.000018, memory $0.000002 | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Cloud Run jobs | First 240,000 vCPU-seconds; first 450,000 GiB-seconds | Billing account | CPU $0.000018, memory $0.000002; minimum 1 minute per instance | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Cloud Run worker pools | First 384,204 vCPU-seconds; first 728,744 GiB-seconds | Billing account | CPU $0.000011244, memory $0.000001235 | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Cloud Run outbound data | 1 GiB within North America | Not stated | Google Cloud networking rates | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Artifact Registry | 0.5 GiB-month of storage | Billing account | $0.000136986 per GiB-hour (about $0.10 per GiB-month) | [Artifact Registry pricing](https://cloud.google.com/artifact-registry/pricing) |
| Cloud Build | 2,500 build-minutes per month ("promotional", e2-standard-2 in the default pool). Note: [cloud.google.com/free](https://cloud.google.com/free) still says "120 build-minutes per day". The pricing page is more specific | Billing account | $0.006 per minute (e2-standard-2) | [Cloud Build pricing](https://cloud.google.com/build/pricing) |
| Secret Manager | 6 active secret versions; 10,000 access operations; 3 rotation notifications | Billing account | $0.06 per active version per month (listed as $0.000082192 per hour), $0.03 per 10,000 accesses, $0.05 per rotation notification | [Secret Manager pricing](https://cloud.google.com/secret-manager/pricing) |
| Pub/Sub | First 10 GiB of throughput (Message Delivery Basic SKU) | Billing account | $40 per TiB | [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing) |
| Firestore | 1 GiB stored; 50,000 document reads, 20,000 writes and 20,000 deletes per day; 10 GiB outbound per month. "Firestore allows exactly one free database per project"; named databases get no free quota; quotas reset "around midnight Pacific time" | Project, per day | Reads $0.03 per 100,000 (us-central1 table) | [Firestore pricing](https://cloud.google.com/firestore/pricing) |
| Cloud Scheduler | 3 jobs | Billing account ("not the project level") | $0.10 per job per 31 days; a paused job still counts | [Cloud Scheduler pricing](https://cloud.google.com/scheduler/pricing) |
| Cloud Logging | First 50 GiB ingested; storage up to the default 30-day retention is included | Project | $0.50 per GiB; $0.01 per GiB-month for logs kept longer than 30 days | [Observability pricing](https://cloud.google.com/products/observability/pricing) |
| Agent Runtime (called "Agent Engine" on the free page) | 50 vCPU-hours (180,000 vCPU-seconds), 100 GiB-hours (360,000 GiB-seconds), 1 GiB-month of agent storage | Account | $0.085 per vCPU-hour, $0.009 per GiB-hour, $0.30 per GiB-month | [cloud.google.com/free](https://cloud.google.com/free), [Agent Platform pricing](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) |
| Gemini CLI (not a Cloud product) | 60 requests per minute and 1,000 per day with a personal Google account; a Gemini API key gives "1000 requests/day with Gemini 3 (mix of flash and pro)" | Google account | Paid tiers | [Gemini CLI README](https://github.com/google-gemini/gemini-cli/blob/main/README.md) |

Two Cloud Run rules that decide the bill ([Cloud Run pricing](https://cloud.google.com/run/pricing)):

- "The free tier usage is aggregated across projects by billing account and resets every month; you are billed only for usage past the free tier. The free tier is applied as a spending based discount using Tier 1 pricing." So the free tier stretches furthest in a Tier 1 region.
- Tier 1 includes us-central1 (Iowa), us-west1 (Oregon), us-east1, us-east4, us-east5, us-south1 and us-west8. us-west2 (Los Angeles), us-west3 and us-west4 are Tier 2. Recommendation: `us-west1` (closest Tier 1 region to Berkeley, marked "Low CO2") or `us-central1`.

### How Cloud Run bills (request-based is the default)

Quoted from [Cloud Run pricing](https://cloud.google.com/run/pricing):

- "By default, Cloud Run only charges for the CPU and memory allocated to an instance when" it is starting, shutting down, or "At least one request is being processed by the instance." Time is "rounded up to the nearest 100 milliseconds."
- Minimum instances: "Idle instances that are not minimum instances are not charged." Instances kept warm with minimum instances are billed at an idle rate (CPU $0.0000025 per vCPU-second).
- "Requests are only billed when they reach the container after successfully being authenticated, requests denied by IAM policy are not billed."
- Instance-based billing (opt-in) bills "the entire lifetime" of each instance, "with a minimum of 1 minute." Jobs always use the instance-based rate.

gcloud flags that control this ([gcloud help: run deploy](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy)): `--min-instances` (per revision) or `--min` (per service, changeable without a new revision), `--max-instances`, and `--[no-]cpu-throttling` ("Whether to throttle the CPU when the container is not actively serving requests"). The product page says Cloud Run "automatically scales your containers up and down from zero" ([Cloud Run](https://cloud.google.com/run)).

Cost bounds (my arithmetic from the Tier 1 prices above, 30-day month = 2,592,000 seconds):

| Setup | Cost per month before free tier |
|---|---|
| Scale to zero, a few hundred demo requests | about $0, inside the free tier |
| `--min-instances=1`, 1 vCPU, 512 MiB, idle all month | about $9.72 (6.48 CPU + 3.24 memory) |
| One instance busy 24 hours a day, 1 vCPU, 512 MiB | about $65.45 (62.21 + 3.24), minus about $5.22 of free tier |
| Cloud Run instance (preview), 1 vCPU, 1 GiB, always on | $5.70 per 30 days, per [Google](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-instances) |

With `--max-instances=2`, CPU and memory can never exceed about twice the "busy" line. Requests are not bounded by max instances: $0.40 per million after the first 2 million.

### Services, jobs and the other Cloud Run shapes

- Services answer HTTP requests and scale to zero. This is what the judges' public link should point to.
- Jobs "perform batch processing" and "run-to-completion"; "Let your jobs run for up to 24 hours" ([Cloud Run](https://cloud.google.com/run)). Flags: `--tasks`, `--max-retries`, `--task-timeout` ([gcloud help: run jobs deploy](https://docs.cloud.google.com/sdk/gcloud/reference/run/jobs/deploy)). Pricing example 5: a job run hourly for 1 minute costs "$0.00" with the free tier ([Cloud Run pricing](https://cloud.google.com/run/pricing)). Good fit for a scheduled agent run triggered by Cloud Scheduler (3 free jobs).
- Worker pools (GA 2026-04-09) are for pull-based, non-HTTP work ([post](https://cloud.google.com/blog/products/serverless/cloud-run-worker-pools-at-estee-lauder-companies)).
- Instances (preview) are single long-lived instances ([post](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-instances)).
- The pricing page also lists "Delayed Jobs" with lower, dynamic prices ("can change up to once every 30 days"). What they are could not be read (unverified).

### Deploying from source or from an image

- From an image: `gcloud run deploy SERVICE --image=REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG` ([gcloud help: run deploy](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy)). This is what GitLab's reference project does.
- From source: `gcloud run deploy SERVICE --source .`. "If a Dockerfile is present in the source code directory, it will be built using that Dockerfile, otherwise it will use Google Cloud buildpacks" ([gcloud help: run deploy](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy)). Source deploys use Cloud Build and store images in Artifact Registry, which are billed separately: "If you deploy your source code or function to Artifact Registry and exceed the Artifact Registry free tier usage, you will incur charges for deploying your functions, even when your use of Cloud Run falls within the free tier" ([Cloud Run pricing](https://cloud.google.com/run/pricing)).
- Images pile up either way. A few Python images can pass the 0.5 GiB Artifact Registry free tier, so add a cleanup policy (see next section).

## No surprise charges

1. Stay on the Free Trial and do not click "Upgrade". During the trial "You will not be billed for any Google Cloud usage" ([FAQ](https://cloud.google.com/signup-faqs)). If the $300 runs out, workloads stop instead of billing you. Plan for the 90-day end date.
2. Know that budgets do not cap spending. Two signs from Google itself: on 2026-04-22 Google said of Cloud Run billing caps, "Soon, you'll be able to define your maximum spend per month. If your bill reaches this amount, your Cloud Run resources will be de-activated" ([Cloud Run at Next '26](https://cloud.google.com/blog/products/serverless/whats-new-for-cloud-run-at-next26)), and project "Spend Caps" were "In private preview" ([Next '26 recap item 139](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up)). I found no general-availability announcement for either in the recent Cloud Run posts (unverified that they are still unlaunched). Google's "Disable billing usage with notifications" page warns that notifications arrive with a delay, so even an automatic shutoff does not guarantee you stay under budget (search excerpt; [page](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications) blocked).
3. Create a budget that sends alerts to email and to a Pub/Sub topic. Flags verified in [gcloud help: billing budgets create](https://docs.cloud.google.com/sdk/gcloud/reference/billing/budgets/create). `exclude-all-credits` makes the budget count usage before the trial credit, so you see how fast the $300 is going:

   ```bash
   PROJECT_ID="your-project-id"
   BILLING_ACCOUNT="$(gcloud billing projects describe "$PROJECT_ID" \
     --format='value(billingAccountName)' | sed 's#billingAccounts/##')"
   gcloud pubsub topics create budget-alerts --project="$PROJECT_ID"
   gcloud billing budgets create \
     --billing-account="$BILLING_ACCOUNT" \
     --display-name="life-after-code" \
     --budget-amount=10USD \
     --filter-projects="projects/$PROJECT_ID" \
     --credit-types-treatment=exclude-all-credits \
     --threshold-rule=percent=0.5 \
     --threshold-rule=percent=0.9 \
     --threshold-rule=percent=1.0 \
     --notifications-rule-pubsub-topic="projects/$PROJECT_ID/topics/budget-alerts"
   ```

   The Cloud Billing Budget API may need to be enabled first (unverified).
4. Optional kill switch. Google's documented pattern is a function triggered by the budget's Pub/Sub message that disables billing on the project (search excerpt; page blocked). The manual equivalent is `gcloud billing projects unlink PROJECT_ID`, which [gcloud help](https://docs.cloud.google.com/sdk/gcloud/reference/billing/projects/unlink) describes as: "This action disables billing on the project. Any billable resources and services in use in your project are stopped, and your application stops functioning." On a Free Trial this is not needed. On a paid account it is worth it.
5. Bound Cloud Run:
   - Keep `--min-instances=0` and the default request-based billing (do not pass `--no-cpu-throttling`).
   - Set `--max-instances=2` or lower.
   - Deploy internal endpoints (webhooks the agent calls) with `--no-allow-unauthenticated`. Requests "denied by IAM policy are not billed" ([Cloud Run pricing](https://cloud.google.com/run/pricing)). Only the public demo page needs `--allow-unauthenticated`.
   - The real risk is model spend, not Cloud Run. Do not let anonymous visitors trigger LLM calls without a per-day limit or a demo passcode (my advice).
6. Keep Artifact Registry under 0.5 GiB with a cleanup policy. Keys verified against the gcloud parser and the Artifact Registry API types in the installed SDK ([gcloud help: set-cleanup-policies](https://docs.cloud.google.com/sdk/gcloud/reference/artifacts/repositories/set-cleanup-policies)):

   ```json
   [
     {"name": "keep-last-3", "action": {"type": "KEEP"}, "mostRecentVersions": {"keepCount": 3}},
     {"name": "delete-older", "action": {"type": "DELETE"}, "condition": {"tagState": "ANY", "olderThan": "7d"}}
   ]
   ```

   ```bash
   gcloud artifacts repositories set-cleanup-policies app \
     --location=us-west1 --policy=cleanup.json --dry-run   # check first, then drop --dry-run
   ```

   The uppercase `KEEP`, `DELETE` and `ANY` match the enum names in the installed SDK's Artifact Registry API types. Google's own examples (on the blocked docs host) may use a different letter case (unverified).
7. Teardown after judging: unlink billing, or delete the project with `gcloud projects delete PROJECT_ID` ([gcloud help](https://docs.cloud.google.com/sdk/gcloud/reference/projects/delete)). A deleted project can be restored for about 30 days (unverified; [support page](https://support.google.com/cloud/answer/6251787) blocked). Keep the project alive until the winners are announced, because the rules require the live link to be "public and available to judges" ([docs/RULES.md](../../RULES.md)).

## Keyless auth from GitLab CI (exact steps)

How it works: a GitLab CI job asks GitLab for a short-lived OIDC ID token with `id_tokens`. Google's Security Token Service checks it against a workload identity pool provider and returns a federated token. That token impersonates a deployer service account. No JSON key exists anywhere. Sources: [GitLab: Configure OpenID Connect with GCP Workload Identity Federation](https://docs.gitlab.com/ci/cloud_services/google_cloud/) (read from [source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/google_cloud/_index.md); Tier: Free, Premium, Ultimate; GitLab.com, Self-Managed, Dedicated), [GitLab: ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/) ([source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md); Free tier included), and GitLab's working reference project [configure-openid-connect-in-gcp](https://gitlab.com/guided-explorations/gcp/configure-openid-connect-in-gcp).

Facts that shape the setup:

- gitlab.com's issuer is exactly `https://gitlab.com` ([gitlab.com/.well-known/openid-configuration](https://gitlab.com/.well-known/openid-configuration), read today). GitLab's tutorial says the issuer "must end in a trailing slash", but its own reference Terraform uses `https://gitlab.com` with no slash ([variables.tf](https://gitlab.com/guided-explorations/gcp/configure-openid-connect-in-gcp/-/blob/main/variables.tf)). Use no slash. If the token exchange fails with an issuer error, try `https://gitlab.com/` (unverified which one Google normalizes).
- "For projects hosted on GitLab.com, GCP requires you to limit access to only tokens issued by your GitLab group" ([GitLab tutorial](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/google_cloud/_index.md)). Use an attribute condition. GitLab: "Use the attribute `assertion.project_id` for a project and the attribute `assertion.namespace_id` for a group" ([GitLab IAM doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/integration/google_cloud_iam.md)). The hackathon workspaces all sit under the shared `gitlab-ai-hackathon` group, so a group-wide condition would accept every participant's tokens. Condition on our own `project_id`.
- All claim values are strings, for example `"ref_protected": "false"` ([ID token doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md)).
- `google.subject` "Cannot exceed 127 bytes" ([gcloud help: create-oidc](https://docs.cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/create-oidc)). GitLab's default `sub` is `project_path:{group}/{project}:ref_type:{type}:ref:{branch_name}`. For a project at `gitlab-ai-hackathon/transcend-october-2026/<id>/showcase` on `main` that is 97 bytes. A long branch name such as `claude/life-after-code-hackathon-5wm0gs` makes it 132 bytes, and the exchange would fail. So request Google tokens only in jobs on `main` (the snippet below does this).
- The ID token lives for the job's timeout, or 5 minutes if none is set ([ID token doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md)).
- Nothing in the setup is secret, so no GitLab CI/CD variables are needed. This matters: the workspace gives "the Developer role" ([hackathon guide source](https://gitlab.com/gitlab-org/developer-relations/contributor-success/contributors-gitlab-com/-/blob/main/contributors/app/javascript/pages/transcend-hackathon-page/ShowcaseDetails.md)). GitLab gives a project's creator their group-level role ([create_service.rb](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/services/projects/create_service.rb)). Project CI/CD variables need "the Maintainer role" ([CI/CD variables doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/variables/_index.md)) and so do integrations ([Artifact Management doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/integrations/google_artifact_management.md)). Whether the workspace's custom member role adds those permissions is unverified.

### Step 1. One-time setup in Google Cloud (run in Cloud Shell or a local gcloud)

All flags checked against gcloud help for [workload-identity-pools create](https://docs.cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/create), [providers create-oidc](https://docs.cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/providers/create-oidc), [service-accounts add-iam-policy-binding](https://docs.cloud.google.com/sdk/gcloud/reference/iam/service-accounts/add-iam-policy-binding), [artifacts repositories create](https://docs.cloud.google.com/sdk/gcloud/reference/artifacts/repositories/create) and [secrets create](https://docs.cloud.google.com/sdk/gcloud/reference/secrets/create). The pool, provider, mapping and `principalSet` binding follow GitLab's tutorial and reference project.

```bash
# 0. Values to change
PROJECT_ID="your-project-id"
REGION="us-west1"
GITLAB_PROJECT_ID="12345678"   # "Project ID" on the GitLab project page ($CI_PROJECT_ID in jobs)
POOL_ID="gitlab"
PROVIDER_ID="gitlab-com"
gcloud config set project "$PROJECT_ID"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
DEPLOYER_SA="gitlab-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA="app-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. APIs (the exact minimum list is unverified; these are the services the flow calls)
gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com \
  cloudresourcemanager.googleapis.com run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com

# 2. Workload identity pool
gcloud iam workload-identity-pools create "$POOL_ID" \
  --project="$PROJECT_ID" --location="global" --display-name="GitLab"

# 3. OIDC provider for gitlab.com, locked to our one GitLab project
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location="global" \
  --workload-identity-pool="$POOL_ID" \
  --display-name="gitlab.com" \
  --issuer-uri="https://gitlab.com" \
  --allowed-audiences="https://gitlab.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.project_id=assertion.project_id,attribute.namespace_id=assertion.namespace_id,attribute.ref=assertion.ref,attribute.ref_protected=assertion.ref_protected" \
  --attribute-condition="assertion.project_id=='${GITLAB_PROJECT_ID}'"
# Stricter, if main is a protected branch:
#   --attribute-condition="assertion.project_id=='${GITLAB_PROJECT_ID}' && assertion.ref_protected=='true'"

# 4. Two service accounts: one CI uses to deploy, one the app runs as
gcloud iam service-accounts create gitlab-deployer --display-name="GitLab CI deployer"
gcloud iam service-accounts create app-runtime --display-name="Cloud Run runtime"

# 5. Only pipelines of our GitLab project may act as the deployer
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_SA" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.project_id/${GITLAB_PROJECT_ID}"

# 6. What the deployer may do
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${DEPLOYER_SA}" --role="roles/run.admin"
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --member="serviceAccount:${DEPLOYER_SA}" --role="roles/iam.serviceAccountUser"
gcloud artifacts repositories create app --repository-format=docker --location="$REGION"
gcloud artifacts repositories add-iam-policy-binding app --location="$REGION" \
  --member="serviceAccount:${DEPLOYER_SA}" --role="roles/artifactregistry.writer"

# 7. Secrets live in Secret Manager, readable only by the runtime identity
printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:${RUNTIME_SA}" --role="roles/secretmanager.secretAccessor"
```

If a binding fails right after the service account or pool was created, wait a minute and run it again; IAM changes take a short time to propagate (general experience, unverified today).

Why these roles: Google's archived Cloud Run component granted `roles/run.admin` ("to get, create and update a service") and `roles/iam.serviceAccountUser` ("to run operations as the service account") ([component README](https://gitlab.com/google-gitlab-components/cloud-run/-/blob/main/README.md)). `run.admin` rather than a narrower role is needed because `--allow-unauthenticated` changes the service's IAM policy (my understanding, unverified). If the app calls Gemini through Agent Platform, also grant the runtime account the Vertex AI user role, `roles/aiplatform.user` (role name after the Agent Platform rename unverified).

### Step 2. `.gitlab-ci.yml`

The deploy job is GitLab's reference pattern ([reference .gitlab-ci.yml](https://gitlab.com/guided-explorations/gcp/configure-openid-connect-in-gcp/-/blob/main/.gitlab-ci.yml)) with a Cloud Run deploy added. The build job uses GitLab's documented token exchange with `curl` ([GitLab tutorial](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/google_cloud/_index.md)), because the `docker` image has no gcloud. Docker-in-Docker on GitLab.com runners is what the judges' reference project already uses ([hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml)).

```yaml
stages: [build, deploy]

# Identifiers only. Safe to commit. None of these grants access by itself.
variables:
  GCP_PROJECT_ID: "your-project-id"
  GCP_REGION: "us-west1"
  GCP_WIF_PROVIDER: "projects/123456789012/locations/global/workloadIdentityPools/gitlab/providers/gitlab-com"
  GCP_DEPLOYER_SA: "gitlab-deployer@your-project-id.iam.gserviceaccount.com"
  GCP_RUNTIME_SA: "app-runtime@your-project-id.iam.gserviceaccount.com"
  SERVICE: "life-after-code"
  IMAGE: "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/app/${SERVICE}:${CI_COMMIT_SHORT_SHA}"

# Every job that talks to Google Cloud extends this. Main branch only.
.gcp_oidc:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build-image:
  extends: .gcp_oidc
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - apk add --no-cache curl jq
    - |
      PAYLOAD="$(cat <<EOF
      {
        "audience": "//iam.googleapis.com/${GCP_WIF_PROVIDER}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
        "subjectToken": "${GITLAB_OIDC_TOKEN}"
      }
      EOF
      )"
      FEDERATED_TOKEN="$(curl --fail-with-body -sS "https://sts.googleapis.com/v1/token" \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        --data "${PAYLOAD}" | jq -r '.access_token')"
      ACCESS_TOKEN="$(curl --fail-with-body -sS \
        "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_DEPLOYER_SA}:generateAccessToken" \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        --header "Authorization: Bearer ${FEDERATED_TOKEN}" \
        --data '{"scope": ["https://www.googleapis.com/auth/cloud-platform"]}' | jq -r '.accessToken')"
      echo "${ACCESS_TOKEN}" | docker login -u oauth2accesstoken --password-stdin "https://${GCP_REGION}-docker.pkg.dev"
    - docker build -t "${IMAGE}" .
    - docker push "${IMAGE}"

deploy-cloud-run:
  extends: .gcp_oidc
  stage: deploy
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:stable
  needs: [build-image]
  environment:
    name: production
    url: $APP_URL
  script:
    - echo "${GITLAB_OIDC_TOKEN}" > .ci_job_jwt_file
    - gcloud iam workload-identity-pools create-cred-config "${GCP_WIF_PROVIDER}"
      --service-account="${GCP_DEPLOYER_SA}"
      --credential-source-file=.ci_job_jwt_file
      --output-file=.gcp_temp_cred.json
    - gcloud auth login --cred-file="$(pwd)/.gcp_temp_cred.json"
    - gcloud run deploy "${SERVICE}"
      --project="${GCP_PROJECT_ID}"
      --region="${GCP_REGION}"
      --image="${IMAGE}"
      --service-account="${GCP_RUNTIME_SA}"
      --allow-unauthenticated
      --min-instances=0
      --max-instances=2
      --cpu=1
      --memory=512Mi
      --set-env-vars="APP_VERSION=${CI_COMMIT_SHORT_SHA}"
      --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest"
      --quiet
    - echo "APP_URL=$(gcloud run services describe "${SERVICE}" --project="${GCP_PROJECT_ID}" --region="${GCP_REGION}" --format='value(status.url)')" >> deploy.env
  artifacts:
    reports:
      dotenv: deploy.env
```

Notes on the snippet:

- The credential file `create-cred-config` writes was generated here, offline, with gcloud 530.0.0. It contains no secret: `"type": "external_account"`, `"audience": "//iam.googleapis.com/projects/.../providers/gitlab-com"`, `"subject_token_type": "urn:ietf:params:oauth:token-type:jwt"`, `"token_url": "https://sts.googleapis.com/v1/token"`, `"credential_source": {"file": ".ci_job_jwt_file"}` and a `service_account_impersonation_url` ending in `:generateAccessToken`. The JWT file is the short-lived secret. Never list either file under `artifacts`.
- `--cred-file` accepts "the external account configuration file (workload identity pool, generated by the Cloud Console or gcloud iam workload-identity-pools create-cred-config)" ([gcloud help: auth login](https://docs.cloud.google.com/sdk/gcloud/reference/auth/login)). Instead of `gcloud auth login`, you can set `CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE` and `GOOGLE_APPLICATION_CREDENTIALS` to the file's path. GitLab's integration sets exactly these two variables for gcloud and client libraries ([Artifact Management doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/integrations/google_artifact_management.md)).
- `--set-secrets` values use the form `SECRET_NAME:SECRET_VERSION` ([gcloud help: run deploy](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy)).
- `docker login -u oauth2accesstoken` is Artifact Registry's access-token login. The Google page for it is on the blocked docs host (unverified today).
- `google-cloud-cli:stable` is the image Google recommends "for a minimal environment" ([cloud-sdk-docker README](https://github.com/GoogleCloudPlatform/cloud-sdk-docker/blob/master/README.md)). GitLab's reference projects use the older Docker Hub name `google/cloud-sdk:slim`, which also works for this job (unverified that it is still updated).
- `environment:url` read from a dotenv report is the pattern the judges' reference project uses.
- For a safer rollout (my suggestion), deploy with `--no-traffic --tag=candidate`, smoke-test the tagged URL, then move traffic with `gcloud run services update-traffic SERVICE --to-latest`. Roll back with `--to-revisions=OLD_REVISION=100` (flags from [gcloud help: update-traffic](https://docs.cloud.google.com/sdk/gcloud/reference/run/services/update-traffic)).

### Troubleshooting (from GitLab's docs)

- 401 errors: decode the token inside the job with `echo $OIDC_TOKEN | cut -d '.' -f2 | base64 -d | jq .` and check that `aud` matches ([ID token doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md)).
- Use `curl --fail-with-body` to see Google's error message ([GitLab tutorial](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/google_cloud/_index.md)).
- "ID token issuance is disabled" appears if the project path in `sub` was used before by a different project. Fix it with `ci_id_token_sub_claim_components` through the projects API, which needs Maintainer ([ID token doc](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md)).
- `CI_JOB_JWT` and `CI_JOB_JWT_V2` were removed in GitLab 17.0. Old blog posts that use them will not work ([cloud services doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/_index.md)).

### Alternative: deploy from source

`gcloud run deploy SERVICE --source .` in the deploy job removes the Docker job. Google's archived component did this, with the workload identity granted `roles/run.admin`, `roles/iam.serviceAccountUser` and `roles/cloudbuild.builds.editor` directly, and an Artifact Registry repository named `cloud-run-source-deploy` created first ([component README](https://gitlab.com/google-gitlab-components/cloud-run/-/blob/main/README.md), last updated 2024-09). Source uploads and Cloud Build log streaming may need more storage and logging permissions (unverified). The image path above has fewer unknowns.

## GitLab's Google Cloud integration and components

| Feature | Tier | Offering | Status | Needs | Source |
|---|---|---|---|---|---|
| `id_tokens` (OIDC ID tokens) plus your own WIF setup (recommended above) | Free, Premium, Ultimate | GitLab.com, Self-Managed, Dedicated | GA | Nothing in project settings | [ID token doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/secrets/id_token_authentication.md) |
| Google Cloud IAM integration ("Google Cloud Workload Identity Federation and IAM policies") | Free, Premium, Ultimate | GitLab.com only | Enabled on GitLab.com in 17.1 | Settings > Integrations > Google Cloud IAM, guided or manual setup | [IAM doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/integration/google_cloud_iam.md) |
| `identity: google_cloud` CI keyword | Free, Premium, Ultimate | GitLab.com | "Status: Beta" | The IAM integration above | [CI YAML reference source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/yaml/_index.md) |
| Google Artifact Management integration | Free, Premium, Ultimate | GitLab.com | Enabled on GitLab.com in 17.1 | "Maintainer or Owner role"; Docker-format, Standard-mode repository only | [Artifact Management doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/integrations/google_artifact_management.md) |
| Runner provisioning in Google Cloud | Free, Premium, Ultimate | GitLab.com | Enabled on GitLab.com in 17.1 | Maintainer (project runner), Owner on the Google Cloud project, billing enabled | [runner doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/runners/provision_runners_google_cloud.md) |
| CI/CD components `gitlab.com/google-gitlab-components/*` | n/a | GitLab.com catalog | Archived 2026-03-18 | n/a | [group projects via API](https://gitlab.com/api/v4/groups/google-gitlab-components/projects) |

Details:

- The IAM integration uses a different issuer from plain `id_tokens`: `https://auth.gcp.gitlab.com/oidc/<top-level-group>`, which "must include the path of the top-level group." Its manual setup is two gcloud commands (`workload-identity-pools create` and `providers create-oidc` with 14 mapped attributes such as `attribute.developer_access=assertion.developer_access`). Jobs then add `identity: google_cloud` and get `GOOGLE_APPLICATION_CREDENTIALS` and `CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE` set for them ([IAM doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/integration/google_cloud_iam.md), [Artifact Management doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/integrations/google_artifact_management.md)).
- For this hackathon the integration is a weaker choice. Setting it up needs project settings access, which the Developer role normally lacks. Its top-level group would be the shared `gitlab-ai-hackathon`. And `identity` is still Beta. Plain `id_tokens` does the same job on Free with no settings.
- The Artifact Management integration adds predefined variables `GOOGLE_ARTIFACT_REGISTRY_PROJECT_ID`, `GOOGLE_ARTIFACT_REGISTRY_REPOSITORY_NAME` and `GOOGLE_ARTIFACT_REGISTRY_REPOSITORY_LOCATION`, and a "Google Artifact Registry" page under Deploy. Its recommended copy method is the `upload-artifact-registry` component, which is now archived ([doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/user/project/integrations/google_artifact_management.md)).
- Components: the group lists 7 projects, all `archived: true`, last activity 2026-03-18. The Cloud Run project's last commit is "Archive project." (2026-03-18), and its README starts "Status: This project is archived and no longer developed or maintained." ([cloud-run component](https://gitlab.com/google-gitlab-components/cloud-run)). The CI/CD Catalog still lists them through GitLab's GraphQL API: Cloud Run 0.2.0 (released 2024-07-18) and Artifact Registry 0.1.1 (2024-05-22). The README still says the Beta feature flag "needs to be enabled", although GitLab removed that flag in 17.1. Archived projects stay readable, so an `include: component:` may still resolve (unverified). Copy the few gcloud lines instead of depending on them.
- What GitLab's judges built: the [hello-world-showcase](https://gitlab.com/gitlab-org/developer-relations/contributor-success/hello-world-showcase/-/blob/main/.gitlab-ci.yml) pipeline pushes to Artifact Registry with `docker login -u _json_key` and deploys with `gcloud auth activate-service-account --key-file="$GCP_SERVICE_KEY"`, to `us-central1`, with `--allow-unauthenticated`, a staging service, a `/health` smoke test, then production. Our pipeline can match that flow without the key.
- GitLab warns: "Configuring OIDC enables JWT token access to the target environments for all pipelines", so review who can run pipelines ([cloud services doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/ci/cloud_services/_index.md)). The attribute condition on `project_id`, plus running Google jobs only on `main`, covers this.

## What Google would be proud to see

This is my reading of what Google publishes as good practice, not a statement from the judges. The one named Google judge is Rajesh Agadi, Principal Architect ([docs/RULES.md](../../RULES.md)).

1. No keys anywhere. Keyless WIF, an attribute condition on our `project_id`, and separate deployer and runtime service accounts. GitLab's own docs say service account keys "are powerful credentials, and can present a security risk if they are not managed correctly" ([IAM doc source](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/integration/google_cloud_iam.md)). The judges' reference project still uses a key, so this difference is easy to show in the video.
2. Agents with their own identity and narrow permissions. From Google SRE's principles: "SRE AI agents must have a strong identity (agents have roles and permissions assigned)" ([AI in SRE](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations)). Give the agent's Cloud Run service its own runtime service account with only the roles it needs, and show that list.
3. Humans approve production changes, and the agent explains itself. The same post asks for "consistent controls to prevent unwanted mutations of production state" and says agents "must be able to explain and reason about why and how they performed an action, as well as what options were considered and rejected." ADK 2.0 has a built-in "Tool Confirmation" step for this ([ADK README](https://github.com/google/adk-python/blob/main/README.md)). Our AGENTS.md rule "A human decides when the agent acts on anything that matters" already matches.
4. Keep deterministic automation deterministic. "Processes and operations that are already successfully automated, or that can be easily automated with classic non-AI based systems, do not need to be replaced (as long as they meet business needs)" ([AI in SRE](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations)). Matches "The model chooses where to look. Code decides what is true."
5. Real post-code work, done the way Google SRE does it. Google lists agents that "Automatically create drafts of incident postmortems", generate playbooks from incidents, and group and enrich alerts ([AI in SRE](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations)). A GitLab agent that reads Cloud Logging and Cloud Run health signals, then opens a postmortem draft MR for a human to approve, speaks Google's language. Gemini Cloud Assist can investigate alerts and is reachable over MCP from Gemini CLI ([Cloud Assist post](https://cloud.google.com/blog/products/application-development/gemini-cloud-assist-at-next26)).
6. Cloud Run used well. Scale to zero, request-based billing, `--max-instances`, a dedicated runtime identity, secrets from Secret Manager via `--set-secrets`, revisions with tagged canaries and one-command rollback, and readiness probes ([multi-region post](https://cloud.google.com/blog/products/serverless/cloud-run-multi-region-services-enhanced-for-high-availability)). A scheduled Cloud Run job for periodic agent runs fits the free tier.
7. Current Google agent pieces, only where they earn their place. A current Gemini Flash model (3.8 Flash, or a Flash-Lite model for the cheapest steps), called through Agent Platform with the service account (`enterprise=True` in the Gen AI SDK, [README](https://github.com/googleapis/python-genai/blob/main/README.md)), so there is no Google API key. Optionally ADK 2.0 for the agent loop, an A2A 1.0 agent card if agents talk to each other, and Google's remote MCP servers (Cloud Run MCP server GA; Cloud CLI MCP server preview). Claude is also offered inside Agent Platform as a partner model ([pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)), one way to show GitLab, Google and Anthropic working together. Use the current names: Agent Platform, Agent Runtime.
8. Cost awareness. A budget with Pub/Sub alerts, `--max-instances`, and a teardown plan. Google is investing here: billing caps, Spend Caps and a FinOps cost-anomaly agent were all announced at Next '26 ([recap](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up)).
9. DORA thinking. Google's DORA research says "AI is an amplifier" and lists capabilities that make AI help, including "Strong version control practices", "Working in small batches" and "User-centric focus" ([DORA AI Capabilities Model post](https://cloud.google.com/blog/products/ai-machine-learning/from-adoption-to-impact-putting-the-dora-ai-capabilities-model-to-work)). Small MRs, easy rollback, and a stated user benefit fit our project rules.
10. Prompt-injection care. Our agents will read issue and MR text written by strangers. Google's Model Armor screens prompts and is now integrated with Agent Gateway and Agent Runtime in preview ([Next '26 recap item 210](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up)). Even a simple allow-list of agent actions shows awareness.

## Moved or broken links

| Link | What happens now | Notes |
|---|---|---|
| `https://cloud.google.com/run/docs` and every `cloud.google.com/<product>/docs/...` page | 301 to `https://docs.cloud.google.com/...` | Google moved product docs to a new host. Old links still redirect. That host is blocked here |
| `https://cloud.google.com/free/docs/gcp-free-tier` | 301 to `https://docs.cloud.google.com/free/docs/gcp-free-tier` | The `/free` page itself links to `docs.cloud.google.com/free/docs/free-cloud-features` |
| `https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines` | 301 to `docs.cloud.google.com` | The GitLab tutorial links here (`#gitlab-saas_2` anchor) |
| `https://cloud.google.com/billing/docs/how-to/budgets` and `.../disable-billing-with-notifications` | 301 to `docs.cloud.google.com` | |
| `https://cloud.google.com/docs/gitlab` | 301 to `https://cloud.google.com/solutions/gitlab`, then to `https://console.cloud.google.com/marketplace?q=gitlab` | GitLab's IAM doc links this as "Access control with IAM". It no longer leads to a docs page. Effectively broken |
| `https://cloud.google.com/stackdriver/pricing` | 301 to `https://cloud.google.com/products/observability/pricing` | |
| `https://cloud.google.com/products/gemini` | 301 to `https://cloud.google.com/ai/gemini` | |
| `https://cloud.google.com/vertex-ai/generative-ai/pricing` | 301 to `https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing` | Follows the Vertex AI rename |
| `https://cloud.google.com/feeds/run-release-notes.xml`, `https://cloud.google.com/release-notes` | 301 to `docs.cloud.google.com` | |
| `https://cloud.google.com/blog/rss/` | Returns the blog's HTML home page, not RSS | |
| Product names | Vertex AI is now Gemini Enterprise Agent Platform; Agent Engine is now Agent Runtime; Agentspace is now part of Gemini Enterprise; Cloud Functions is now Cloud Run functions; Firebase Data Connect is now Firebase SQL Connect | Sources: [Agent Platform post](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform), editor's notes on the [2025 A2A post](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade), [Cloud Run page](https://cloud.google.com/run), [Next '26 recap item 117](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up). The `/free` page and ADK README still say "Agent Engine" |
| `https://gitlab.com/google-gitlab-components/*` | All 7 projects archived 2026-03-18 | Still in the CI/CD Catalog. GitLab's Artifact Management doc still recommends `upload-artifact-registry@main` |
| `gcr.io/google.com/cloudsdktool/google-cloud-cli:466.0.0-alpine` (pinned in GitLab's Artifact Management examples) | Probably deleted | Google: "Package versions older than 1 year are automatically cleaned up" ([cloud-sdk-docker README](https://github.com/GoogleCloudPlatform/cloud-sdk-docker/blob/master/README.md)). 466.0.0 is from early 2024 (not pulled here, unverified). Use `:stable` |
| GitLab tutorial: issuer "must end in a trailing slash" | Conflicts with gitlab.com's discovery document (`"issuer": "https://gitlab.com"`) and GitLab's own reference Terraform | Use no slash |
| GitLab tutorial STS example | Header reads `Authorization: Bearer FEDERATED_TOKEN` (placeholder without `$`) | The reference script uses `${FEDERATED_TOKEN}` |
| Cloud Run component README | Says "Cloud Storage Admin (`roles/run.admin`)" | Label is wrong; the role is Cloud Run Admin. It also still says a feature flag must be enabled, but GitLab removed that flag in 17.1 |
| `cloud.google.com/free` vs Cloud Build pricing | "120 build-minutes per day" vs "2,500 free build-minutes per month" | Pricing page is more specific |
| `https://gitlab.com/gitlab-org/gitlab/-/raw/master/doc/...` | First request 200, then HTTP 429 (Cloudflare challenge) | The repository files API (`/api/v4/projects/gitlab-org%2Fgitlab/repository/files/<path>/raw?ref=master`) worked every time |

## Blocked

Two attempts at most per URL. I did not use archives or reader proxies to get around blocks.

| URL | Tried with | Error |
|---|---|---|
| https://docs.cloud.google.com/run/docs (the whole host; also reached by 301 redirects from the cloud.google.com free tier, WIF, budgets and release-notes URLs listed above) | curl, WebFetch | curl: `CONNECT tunnel failed, response 403`; WebFetch: `EGRESS_BLOCKED`. The `docs.cloud.google.com/sdk/gcloud/reference/...` links in this file were not fetched; their text was read from the local gcloud `--help` |
| https://docs.gitlab.com/ (for example /ci/cloud_services/google_cloud/) | curl, WebFetch | `403` on CONNECT; WebFetch `EGRESS_BLOCKED`. Read the doc sources on gitlab.com instead |
| https://google.github.io/adk-docs/ | curl, WebFetch | `403` on CONNECT; `EGRESS_BLOCKED`. Read the ADK README on raw.githubusercontent.com |
| https://ai.google.dev/gemini-api/docs/models | curl, WebFetch | `403` on CONNECT; `EGRESS_BLOCKED` |
| https://a2a-protocol.org/latest/ | curl, WebFetch | `403` on CONNECT; `EGRESS_BLOCKED`. Read the A2A README and CHANGELOG instead |
| https://blog.google/technology/ai/ | curl, WebFetch | `403` on CONNECT; `EGRESS_BLOCKED` |
| https://developers.googleblog.com/ | curl | `403` on CONNECT |
| https://geminicli.com/ | curl | `403` on CONNECT. Read the Gemini CLI README instead |
| https://github.com/google/adk-python | curl | HTTP `403`. raw.githubusercontent.com worked |
| https://deepmind.google/models/gemini/pro/ | curl | No connection (HTTP 000) |
| https://antigravity.google/docs/cli-overview | curl | No connection (HTTP 000) |
| https://codelabs.developers.google.com/ and https://developers.google.com/ | curl | No connection (HTTP 000) |
| https://support.google.com/cloud/answer/6251787 (deleting projects) | curl | `403` on CONNECT |
| https://cloudblog.withgoogle.com/rss/ | curl | `403` on CONNECT |
| https://console.cloud.google.com/marketplace?q=gitlab (redirect target of cloud.google.com/docs/gitlab) | curl | `403` on CONNECT |
| https://gitlab.com/api/v4/projects/gitlab-org%2Fdeveloper-relations%2Fcontributor-success%2Fcontributors-gitlab-com/search | curl | `401 Unauthorized` (could not look up the hackathon custom role's permissions) |
| WebSearch | tool | After four searches the tool refused: "this turn's web search budget is used up". Facts that would have needed a search are marked (unverified) |
