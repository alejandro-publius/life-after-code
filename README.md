# Night Orders

**Before bed, you sign what the agent may do alone tonight. Everything else wakes you. The orders end at 07:00.**

An entry for [Life After Code, the GitLab Transcend Hackathon](https://gitlab-transcend.devpost.com/), Path A. Built by Alex Velazquez. MIT licence.

Status on 6 Oct 2026: the decision code, the dusk drafter, a replayed demo night, the relay service, the demo shop, the morning countersign and the three Duo flow files are in this repo, with 218 offline tests that run in CI. Nothing has run on GitLab.com or Google Cloud yet. The dated plan is in [docs/PLAN.md](docs/PLAN.md).

## The problem

Priya (a demo persona, played by Alex) is on call for a small online shop. At 16:20 a teammate shipped a new checkout path behind the `new_checkout` feature flag. If it fails at 3am, the right move is obvious and safe: turn that one flag off. Only she can do it, so every alert wakes her. She has no way to hand that one decision to an agent for tonight only, without handing over everything else.

## How it works

1. **Dusk.** She assigns tonight's watch issue to the dusk flow. The agent reads the day's merged merge requests, deployments and flags, and drafts at most three orders. Each order is a condition plus one action from a fixed menu: set a feature flag on or off, or send a Cloud Run service's traffic to a named earlier revision. Code checks the draft. A change that cannot be undone safely gets no order, so it will wake her.
2. **Signature.** She edits the orders merge request and merges it. The merge is the signature. No merge means no orders, and every alert wakes her.
3. **Night.** An alert reaches the relay, a small FastAPI service on Cloud Run. Two keys must turn before anything changes:
   - code checks the numbers: the orders are signed by the on-call person, not expired, the order's condition holds right now, and the order has not been used tonight;
   - the watch flow checks the reason, and names the order in a short machine-readable note.

   The action is always read from the signed file, never from the agent's note. If either key fails, she gets a three-line page with one suggested action, which she can approve with a thumbs-up.
4. **Dawn.** The orders expire at 07:00. Code writes the watch log on the watch issue. The dawn flow proposes keep or undo for each change made overnight, as a countersign merge request. When she signs it, code undoes every night change she did not keep, once.

Some things always wake her and no order can cover them: payment errors, a second alert during a re-check, anything after 07:00, a malformed agent answer, no answer within 8 minutes, and a fourth model run in one night.

## See it in one minute

```
uv sync
cd relay && uv run --project .. python -m nightorders.demo_night ../demo/night-2026-10-20
```

This replays one labelled demo night through the real decision code. An excerpt of its output:

```
01:52  PAGE (phone lights up) for #1: Checkout failing on both paths since 01:45 (about 20%). | Not the new checkout, so I did not use order 1. | ...
01:53  APPLY stock_from_cache on in production
03:13  APPLY new_checkout off in production
03:13  note on #2: Order 1 carried out 03:13: new_checkout off in production. Checks: signed by Priya at 22:06 (merge);
       not expired (ends 07:00); checkout error rate (new path) 7.9%, above 5.0% for 5 min; action and target taken
       from the signed file; first use tonight.
03:23  note on #2: Re-check 03:23: checkout error rate (new path) back to 0.0% (limit 5.0%). No page.

Woken: 1 time (01:52).
Handled while you slept: incident #2 (order 1).
```

**Demo data.** Everything in [demo/](demo/) is demo data: the shop ("Juniper Market"), its traffic, both planted faults, the persona and the agent's notes, which are recorded, not live. One planted log line tries to order the agent to roll back every service; it changes nothing. The code that decides is the real code. The same labels appear in the video and on the live status page.

## How the pieces fit

```
  GitLab project                                   Google Cloud
  ------------------------------------------       ------------------------------------
  watch issue  --assign-->  dusk flow (Duo)
                              |  drafts orders
                              v
  orders MR  --merge = signature-->  ops/night-orders.yml
                                                    Cloud Scheduler, every minute
                                                       |
                                                       v
  incident  <--------- opens, posts notes ---------  relay (FastAPI, Cloud Run)
     |                                                 ^  reads shop metrics
     | Flows API starts                                |  checks the numbers
     v                                                 |  applies the signed action
  watch flow (Duo): reads evidence, names an order --->+
                                                       |
  feature flags  <------- flag on or off --------------+---> shop (Cloud Run): traffic
                                                              to a named revision
  dawn flow (Duo): keep-or-undo MR    relay: watch log, then applies the signed countersign
```

## What to look at, by judging criterion

| Criterion | Where |
|---|---|
| Technological implementation | The two keys in code: [decide.py](relay/nightorders/decide.py), [orders.py](relay/nightorders/orders.py). One test per reason code refuses to act: [tests/](tests/). Three Duo flows checked in CI against GitLab's own flow schema and tool list: [flows/](flows/). Keyless deploys to Cloud Run: [deploy/](deploy/). |
| Design | One decision at dusk, at most one tap at night, one merge at dawn. The page is three lines with the answer ready. |
| Potential impact | Small teams with no follow-the-sun rotation. The on-call person sleeps through what she already decided. |
| Innovation | The grant is a document a person signs each night, drafted from that day's changes, void at 07:00. The model can decline an order but never widen one. |
| Presentation | The demo night above, the live status page, and the video (link added when filmed). |

GitLab Duo Agent Platform use: three custom flows ([dusk](flows/dusk.yml), [watch](flows/watch.yml), [dawn](flows/dawn.yml)) with narrow components and scoped tools, a human input step at dusk, and the Flows API start at night. The rules the agents follow are in [skills/night-orders/SKILL.md](skills/night-orders/SKILL.md).

## Limits, plainly

- Not yet run on GitLab.com or Google Cloud. Until it is, this README says so.
- The night start depends on calling GitLab's Flows API from the relay with a personal token. If that does not work, the fallback is Standing Orders: code alone acts on signed orders at night, and the model still drafts at dusk and writes the log at dawn.
- Two actions on the menu. Anything else wakes the on-call person.
- The demo clock is compressed: a demo night runs in about 25 minutes.
- Similar products exist (for example PagerDuty's SRE agent and runbook automation). What is different here is the nightly signed fence, not the ability to act.

## Run the checks

```
uv sync
uv run pytest -q                    # decision code, relay, shop, dusk drafter, flows
uv run python flows/validate.py     # Duo flow files against GitLab's flow schema and tool list
cd relay && uv run --project .. python -m nightorders.cli validate ../ops/night-orders.yml --ops ../ops
```

The gcloud flag audit (`deploy/tests/test_cli_flags.py`) runs in CI inside the pinned Google Cloud SDK image, which has the alpha and beta components it checks.

## Repository

| Path | What |
|---|---|
| [agent/](agent/) | The dusk drafter: today's changes in, tonight's orders out (Claude through the Anthropic API, or a recorded answer labelled as demo data) |
| [flows/](flows/) | The three Duo flows, the validator, and GitLab's schema files |
| [ops/](ops/) | Who is on call, the targets, the alert rules, tonight's orders, and the desired state |
| [relay/](relay/) | The decision code (`nightorders`) and the relay web service |
| [shop/](shop/) | The demo shop (demo data) that reads GitLab feature flags |
| [demo/](demo/) | Demo nights (demo data) |
| [skills/](skills/) | The rules every agent follows |
| [deploy/](deploy/) | Keyless Cloud Run deploys from GitLab CI (owned by Codex) |
| [docs/](docs/) | Rules, research, ideas, decisions, the plan |

How the AI agents that build this repo work together: [AGENTS.md](AGENTS.md).
