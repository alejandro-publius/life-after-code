# Morning handoff

For Alex, updated **5 Oct 2026 (Pacific Time)**.

**Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight. Everything else wakes them, and the orders end at 07:00.**

## What you can review now

One guided browser demo now shows the human workflow using the existing decision core. It has phone and laptop layouts, a chart of the actual simulated samples, and expandable decision evidence. The local suite has **256 passing tests**. No GitLab.com, Google Cloud or live model run has been demonstrated. The public demo URL is **pending**.

From the repository root:

```sh
uv sync --locked
cd relay
uv run --project .. uvicorn main:app --host 127.0.0.1 --port 8080
```

Open [http://localhost:8080/demo](http://localhost:8080/demo). Sign the demo orders, approve the demo fallback, review the checkout change, then read the morning brief. The default path reports 1 wake-up, 1 incident handled automatically and 1 approved action. Replay without signing to see the boundary hold. These counts describe the planted demo night.

The sign and approval buttons select recorded fixture inputs for an isolated replay. The morning countersign is recorded too. No button signs a real order, changes GitLab or pages a phone. At 07:00 permission ends; existing changes remain until a morning keep-or-undo decision.

## Public materials ready for review

- [README](../README.md): browser quickstart, local screenshots and plain limits.
- [Judge guide](GUIDE.md): five criteria, each 20%, with inspectable evidence.
- [Devpost draft](DEVPOST.md): English description with pending links and live proof identified.
- [Video script](VIDEO.md): a 2:40 browser recording plan that can be filmed now.
- [Status](STATUS.md): the verified state and integration gaps.

## The next account and integration steps

| Step | Where | Result needed |
|---|---|---|
| Join the event and request the hackathon workspace | [Devpost](https://gitlab-transcend.devpost.com/) and [GitLab contributor registration](https://contributors.gitlab.com/transcend-hackathon) | Access to the required GitLab Duo Agent Platform workspace. Official rules say approval takes about 24 business hours. |
| Make the project public in that workspace | [Official repository requirements](https://gitlab-transcend.devpost.com/rules) | Public GitLab repository URL, detected MIT licence and visible pipeline history showing automation running. |
| Configure credentials securely | [Relay setup](../relay/README.md) | Required tokens in protected environment or CI variables, never pasted into chat or committed. |
| Run the actual Duo night start | [Plan, decision D1](PLAN.md) and [three flows](../flows/) | A real flow session and relay-to-flow result. Schema validation alone does not meet the required live integration proof. |
| Set up Google Cloud if pursuing the bonus | [Deployment setup](../deploy/README.md) | A public working Google Cloud URL and a verified deployment. Deployment code alone earns no demonstrated bonus. |
| Film and submit | [Video](VIDEO.md), [Devpost draft](DEVPOST.md), [official rules](https://gitlab-transcend.devpost.com/rules) | Public YouTube video below 3:00 and completed submission before 27 Oct 2026, 06:00 Pacific Time (13:00 UTC). |

Path A is the plan. **Supervised is the current recommendation, still tentative.** Nightly approval and morning review should be reconciled with the [official autonomy definitions](codex/RULES_CHECK.md#required-duo-use-and-autonomy-level) before selecting the category. Hands-off is not yet a supported claim. There is no measured sleep gain, customer result or sustainability gain to report.
