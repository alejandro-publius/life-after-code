# Devpost submission draft

English draft, updated **5 Oct 2026 (Pacific Time)**. Keep the status statements until real execution evidence replaces them.

## Submission fields

| Field | Draft value |
|---|---|
| Project name | Night Orders |
| Tagline | Sign what the agent may do while you sleep. Everything else wakes you. |
| Entrant | Alex Velazquez, solo |
| Path | Path A: Start Fresh |
| Autonomy category | Supervised, tentative recommendation. Confirm against the final demonstrated workflow and official definitions before submitting. |
| Public GitLab repository | Pending. A public GitHub repository does not replace the required GitLab URL. |
| Working project URL | Pending. The current browser app runs locally at `http://localhost:8080/demo`. |
| Public YouTube video | Pending. Target 2:40; must be below 3:00. |
| Built with | Python, FastAPI, GitLab Duo Agent Platform flow definitions, GitLab CI/CD configuration, Google Cloud Run deployment configuration |
| Google Cloud bonus | Not claimed. No deployment has run. |

The [official rules](https://gitlab-transcend.devpost.com/rules) define the categories. Supervised is the closest current recommendation because a person approves the nightly scope and reviews the morning outcome. The recorded night demonstrates bounded automatic action within that scope, but does not demonstrate a full Hands-off loop from code to production. This recommendation remains tentative.

## Inspiration

Being on call for a small team often means being the only person who can make a simple recovery decision. A reversible checkout failure at three in the morning can still break a night's sleep. Blanket permission for an agent to change production is too broad, but approving every incident leaves the person awake.

Night Orders asks a smaller question before bed: which exact actions may the agent take tonight, and under which conditions? Everything outside that signed boundary still needs the engineer.

## What it does

The dusk drafter reads the day's changes and proposes at most three orders. Each contains a measurable condition and one action from a fixed menu. Code validates the draft. A change that cannot be safely undone receives no order.

In the intended GitLab workflow, the on-call engineer reviews and merges the orders request. That merge is the signature. During the night, code checks the signature, expiry, measured threshold, exact action and first use. The watch flow must also name the order and explain why the evidence fits. The action comes from the signed file, never from the agent's free text. If either key fails, the engineer receives a short page and, when available, one suggestion requiring approval.

The grant ends at 07:00. Expiry stops new automatic actions; it does not automatically revert previous changes. The morning countersign says which changes to keep. Code undoes the others and records the result.

## The working demonstration

The current app is one guided browser replay at `/demo`, with a phone and laptop layout. Priya is a demo persona on call for Juniper Market, a simulated shop. Both faults are planted; the agent replies, signatures, reaction and morning merge are recorded demo data.

The viewer chooses whether to sign the demo orders and whether to approve an inventory fallback. Each combination is computed in isolated memory through the real Watch decision core, then cached for repeat choices. No button merges a real request, pushes code, contacts a model or pages a real phone.

First, both checkout paths fail. The recorded watch reply declines the new checkout order because disabling that path would not resolve the wider inventory fault. Priya gets one necessary wake-up and a suggested fallback. Later, only the new checkout fails above its signed 5% limit for five complete minutes. With a valid signature, code turns that path off and verifies recovery. The chart shows the actual simulated samples returned by this run.

On the signed and approved path, the ledger records one wake-up, one incident handled automatically and one approved action. The morning record keeps the new checkout off and undoes the fallback. Leaving the orders unsigned gives Watch no automatic authority and changes the outcome. The viewer can inspect the signature, checks, wake-up messages, ledger and morning result.

These counts are evidence about an invented night, not measured production impact or hours of sleep saved.

## How it is built and how GitLab fits

Python decision code separates permission checks from side effects. A FastAPI relay supplies the browser replay and implements the intended runtime interface to GitLab incidents, feature flags and flow starts. The same Watch class runs in the replay and the relay. The replay has hard limits on steps and time. Each choice combination uses isolated in-memory state when computed; repeated requests reuse its cached result.

Three custom Duo flow files define dusk drafting, watch investigation and dawn review. Narrow tools and structured answers keep the flow's authority limited. The flow files are validated against the checked-in GitLab schema and tool list. The repository also contains a GitLab pipeline for tests, replay artifacts, flow and order validation, security checks and manual deployment, plus keyless Google Cloud Run deployment configuration.

**Current integration status:** nothing has run on GitLab.com or Google Cloud yet. Live Duo execution, visible GitLab pipeline history and a public deployment URL are pending. Recorded model replies and schema validation demonstrate local behavior and configuration, not the required live GitLab Duo Agent Platform use. A standalone model API call would not replace that requirement.

Source code and instructions: [README](../README.md), [decision core](../relay/nightorders/), [flow definitions](../flows/), [pipeline](../.gitlab-ci.yml) and [deployment setup](../deploy/README.md).

## Challenges

The hard part is making permission precise. A metric can cross a threshold while the proposed action is still the wrong explanation for the incident. Night Orders therefore requires both a numerical check and a reasoned order match. It also treats log text as evidence, never as authority, and keeps action selection in the signed file.

Expiry and morning cleanup are separate decisions. Ending the grant at seven does not mean undoing a recovery while the bug is still present. The countersign preserves that distinction and validates that it can only keep changes that actually happened.

## Accomplishments and what we learned

The local demo now makes the boundary visible to someone who has never read the code: one unsigned branch, one necessary wake-up, one eligible automatic action and one morning account. Its charts and counters come from the backend replay rather than canned success states.

The design lesson is that useful autonomy can be narrow. The agent helps investigate and can decline an order; code verifies the facts; a person grants and renews permission for consequential actions.

## Potential impact and what comes next

The intended audience is a small team without a follow-the-sun on-call rotation. The demonstrated benefit is a way to handle a known reversible fault within prior permission while escalating a fault that does not fit. No customer trial, operational benefit, sleep improvement or sustainability gain has been measured.

The next milestone is an actual GitLab Duo run in the hackathon workspace, followed by visible pipeline execution and a public cloud deployment. Then we can test the same night end to end, show the real integrations in the video and evaluate usefulness with on-call engineers.

## Before submitting

- Replace pending repository, video and project links with verified public URLs.
- Capture genuine Duo Agent Platform execution and visible GitLab pipeline history.
- Confirm the selected autonomy category against the actual workflow.
- Check that the MIT licence is detected in the GitLab About section.
- Keep the public English video below 3:00 and preserve readable demo labels.
- If requesting the cloud bonus, verify the public Google Cloud deployment and repository deployment code.
- Submit before **27 Oct 2026, 06:00 Pacific Time (13:00 UTC)**, then follow the organizer's freeze guidance.

Requirements and category definitions: [official rules](https://gitlab-transcend.devpost.com/rules), [resources](https://gitlab-transcend.devpost.com/resources), and [saved primary-source check](codex/RULES_CHECK.md).
