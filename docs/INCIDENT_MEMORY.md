# Incident memory

An engineer taking the next shift should not have to rediscover why last night's fix failed, or mistake an approved action for a measured recovery. Night Orders now remembers the observed sequence, retains the source incident and carries it into the next dusk briefing.

## Use it

In the [browser demo](https://showcase-700ee4.gitlab.io), scroll to **The night leaves a memory**. Choose the checkout incident to follow a signed action through its recovery check. Choose the inventory incident to see the agent decline, the page and the human-approved alternative. Download the shift handoff, then replay without signing and compare the outcomes. These are computed records from the labelled simulated shop, not production history.

The running relay shows the same memory on its status page. `/status.json` includes `incident_memory`; `/handoff.md` downloads a Markdown handoff from the cached state snapshot. When the state cannot be read, the download returns HTTP 503 rather than inventing a healthy report.

## From one night to the next

1. The relay records the real Watch ledger in the existing leased state document after each tick.
2. Memory joins events by GitLab incident number, so an incident stays connected across the noon rollover. Repeated ticks do not duplicate its history.
3. Each outcome follows recorded events. An automatic action plus a passed re-check is **Recovery observed**. A thumbs-up and action is **A person chose the fix**, with recovery explicitly unverified. Failed calls remain uncertain; a failed call does not establish that nothing changed.
4. The next day's day sheet includes up to eight earlier incidents, with failed or incomplete actions first. The dusk flow already reads this sheet before drafting.
5. Every new night still requires fresh evidence and a new human signature. Memory cannot authorize an action, extend an expired order or widen a target.

Storage is bounded to the newest 60 incidents and 24 steps per incident. Compaction preserves the latest event of every kind, including the action and recovery evidence. State persists through the existing local file or Google Cloud Storage store; no new database or credential is required. The record is an observation history, not proof that an action caused recovery.

Implementation: [memory](../relay/nightorders/memory.py), [state persistence](../relay/nightorders/state.py), [day sheet](../relay/nightorders/daysheet.py), [live status](../relay/nightorders/status_page.py), [browser](../relay/demo_web/app.js).

## What the winner research contributed

The public repositories below were read on 27 Oct 2026. Award assignments come from the [saved primary-source winner announcement](codex/web/feb_winners.md); repository capabilities are those documented and implemented by their authors, not independent production benchmarks.

| Prior winner | Relevant work | How this informed Night Orders |
|---|---|---|
| [LORE, Grand Prize](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35153311) | Persistent team decisions, memory search, lifecycle agents and a visual dashboard | Keep operational knowledge across shifts. Night Orders derives its incident outcomes from the action ledger and distinguishes approvals from observed recovery. |
| [Time-Traveler, Most Technically Impressive](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/34562572) | Isolated migration rehearsal and a visible audit trail | Connect the proposed action to its measured result, and expose the intermediate decisions. Night Orders already rehearses supported orders and now retains what actually happened afterward. |
| [Launch Control, Easiest to Use](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/19053258) | Policy decisions with explicit blockers and required actions | Make each incident's disposition understandable and portable in the handoff. |
| [RedAgent, Most Impactful](https://gitlab.com/gitlab-community/community-projects/2026-02-ai-hackathon/35629156) | Adversarial tool-response testing and session evidence | Preserve the difference between a tool reporting success, a human approving and a recovery being measured. |

No winner code was copied. This addition extends Night Orders' existing overnight workflow; it does not claim superior benchmark results or a deployed production service.
