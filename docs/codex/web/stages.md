# GitLab lifecycle and capability names

Retrieved: 2026-10-06 02:13:45 UTC. Redirects checked again through raw HTTP at 02:14 UTC and supplemental documentation read at 02:15 UTC.
Source long dashes are normalized to ` - `. Functional stage, feature and product names retain source capitalization. Explanations are paraphrases.

## The requested URL has moved

Requested: https://about.gitlab.com/stages-devops-lifecycle/
Current destination: https://about.gitlab.com/platform/
Working HTTP variant: https://about.gitlab.com/platform/?amp=1

The current destination lists platform capabilities, rather than the older stage-by-stage product catalog. The exact heading names and feature names below come from its Key Platform Capabilities section. They are not a newly defined numbered lifecycle.

### DevOps

| Exact capability heading | Exact listed feature names |
| --- | --- |
| Planning | Agile planning framework; Epics, issues, and tasks; Service desk |
| Source Code Management | Code repositories; Code merge requests; Code review |
| Continuous Integration | Built-in CI/CD; Code testing; CI/CD catalog |
| Artifact Registry | Package registry; Container registry; Virtual registry |
| Continuous Delivery | Environment management; Release management; Feature flags |

### Security & Compliance

| Exact capability heading | Exact listed feature names |
| --- | --- |
| Application Security | Static App Security Testing (SAST); Dynamic App Security Testing (DAST); API security |
| Software Composition Analysis | Container scanning; Dependency scanning; Continuous vulnerability scanning |
| Vulnerability Management | Vulnerability report; Risk assessment data; False positive detection |
| Policy Enforcement | Merge request approvals; Pipeline execution policies; Vulnerability management policies |
| Compliance Management | Software Bill of Materials; Frameworks; Audit events |

### Agentic AI

Listed feature names: Agents for workflow automation; Flows for multi-stage tasks; Agentic chat; MCP client & server; Custom agents; Custom flows; Code and test generation; Model selection; External agents; AI Catalog for agents and flows; Explain, fix, and refactor code; Custom rules.

### Unified Context

Listed feature names: DevOps reports; Value stream analytics; Issue analytics; CI/CD analytics; Context Graph; DORA metrics; Product analytics; Merge request analytics; Security dashboard; AI and SDLC Trends; Contributor analytics; Code review analytics; Compliance dashboard.

### Flexible Deployment

Listed feature names: GitLab.com (Multi-tenant SaaS); GitLab Self-Managed; GitLab Flex; Compute minutes per month; Backup and restore; GitLab Dedicated (Single-tenant SaaS); Cloud-agnostic deployment; Storage units per month; Disaster recovery; GitLab Dedicated for Government; Air-gapped deployment; Runners to execute CI/CD jobs; Globally distributed cloning; GitLab-managed models; Self-hosted models.

## Explicit lifecycle stage names from another current official page

Source: https://about.gitlab.com/topics/devops/
Section: The DevOps lifecycle and how DevOps works.
Retrieved: 2026-10-06 02:15 UTC.

The nine exact names, in source order, are Plan, Create, Verify, Package, Secure, Release, Configure, Monitor and Govern.

Their meanings, paraphrased:

| Exact stage | Meaning |
| --- | --- |
| Plan | Prioritize and track the work. |
| Create | Develop code together. |
| Verify | Check behavior and quality, including automated tests. |
| Package | Produce and manage packages, containers and artifacts. |
| Secure | Find vulnerabilities through security testing and dependency checks. |
| Release | Deliver software to users. |
| Configure | Manage the application's infrastructure. |
| Monitor | Observe application behavior and incidents. |
| Govern | Control security, policy and compliance. |

The handbook uses a broader ten-stage table, also including Manage:
https://handbook.gitlab.com/handbook/solutions-architects/sa-practices/communities-of-practice/
Retrieved: 2026-10-06 02:15 UTC. Page last modified: March 19, 2026.

Exact table rows: Manage, Plan, Create, Verify, Package, Secure, Release, Configure, Monitor, Govern. The Topics entry is N/A for every one of those ten rows. A separate Integration Technologies row links Elasticsearch: Advanced Searching. Do not turn the handbook's N/A cells into claimed feature coverage.

## Current destinations of the old stage pages

All ten old stage subpages redirected in a direct HTTP check. These current destination pages list the following relevant product names. This is a factual reading of the current docs, not a reconstruction of the old catalog. A product's presence here does not establish Free-tier availability.

| Old exact stage name and URL | Current destination | Products discussed or linked there |
| --- | --- | --- |
| Manage: https://about.gitlab.com/stages-devops-lifecycle/manage/ | https://docs.gitlab.com/user/compliance/ | Compliance frameworks; Compliance pipelines; Audit events; Audit reports; Audit event streaming; Compliance center; Merge request approvals; Push rules; protected branches; Security policies; External status checks; License approval policies |
| Plan: https://about.gitlab.com/stages-devops-lifecycle/plan/ | https://docs.gitlab.com/user/get_started/get_started_planning_work/ | Milestones; Iterations; Epics; Issues; Tasks; OKRs; Issue boards; Labels; Comments and threads; Roadmaps; Time tracking; Requirements; Wikis |
| Create: https://about.gitlab.com/stages-devops-lifecycle/create/ | https://docs.gitlab.com/user/get_started/get_started_managing_code/ | Web Editor; Web IDE; workspaces; Code Suggestions; merge requests; Merge request approvals; Code Owners; Merge conflicts; Merge methods |
| Verify: https://about.gitlab.com/stages-devops-lifecycle/verify/ | https://docs.gitlab.com/ci/ | Pipelines; Runners; CI/CD variables; CI/CD expressions; CI/CD components |
| Package: https://about.gitlab.com/stages-devops-lifecycle/package/ | https://docs.gitlab.com/user/packages/package_registry/ | Package registry; GitLab CI/CD; package importer; Generic; Maven; npm; NuGet; PyPI; Terraform |
| Secure: https://about.gitlab.com/stages-devops-lifecycle/secure/ | https://docs.gitlab.com/user/application_security/get-started-security/ | Secret detection; Dependency scanning; vulnerability report; security dashboard; Scan execution policies; Merge request approval policy; Container scans; Operational container scanning; SAST; DAST; Fuzz testing; Web API fuzzing; Review apps |
| Release: https://about.gitlab.com/stages-devops-lifecycle/release/ | https://docs.gitlab.com/user/get_started/get_started_deploy_release/ | Packages and registries; Environments; Review apps; Protected environments; Deployment safety; Deployment approvals; Releases; Incremental rollouts; Feature flags; GitLab Pages; Auto Deploy |
| Configure: https://about.gitlab.com/stages-devops-lifecycle/configure/ | https://docs.gitlab.com/user/get_started/get_started_managing_infrastructure/ | Infrastructure as Code; Terraform; GitLab agent for Kubernetes; runbooks |
| Monitor: https://about.gitlab.com/stages-devops-lifecycle/monitor/ | https://docs.gitlab.com/user/get_started/get_started_monitoring/ | Error tracking; Sentry SDK; Incident Management; Insight dashboards; Executable runbooks |
| Govern: https://about.gitlab.com/stages-devops-lifecycle/govern/ | https://docs.gitlab.com/user/compliance/ | Same destination as Manage, with compliance automation, audit management and policy management. |

The compliance destination labels its overall page Ultimate. Check each actual feature's docs before claiming access in the hackathon project.

## Use in the submission

Use the nine-stage topic page as the clear published lifecycle definition, and mention Manage separately if the project uses that broader handbook taxonomy. Name test, release, deployment, monitoring and response actions in plain words, then link each actual GitLab object or feature. Response is work within Monitor and the next planning/testing cycle, rather than a separately listed stage on the cited nine-stage page.

Record the redirect and nine-versus-ten naming difference in the main decision log when Claude reconciles these notes. No stage count should depend on an obsolete catalog or an imagined feature.
