# Test night runbook

How one real night runs against the live services, and who does what. Two test nights are planned ([PLAN.md](PLAN.md): the weekend of 17 to 18 Oct and 20 to 21 Oct) and the filmed night on Sat 24 Oct. A night takes about 45 real minutes of faults, and the on-call person is asleep for all of it except one page.

Everything the shop serves is labelled demo data. The incidents, flag changes, flow sessions, pages and merge requests are real.

## Before the first test night (once)

| Who | What | Where |
|---|---|---|
| Alex | The services are deployed: `shop`, `shop-staging`, `relay` ([deploy/README.md](../deploy/README.md)) | Cloud Shell and the GitLab pipeline |
| Alex | Install the ntfy app on the phone and subscribe to the topic (the topic name is printed once by setup; in Cloud Shell: `gcloud secrets versions access latest --secret=ntfy-url`) | Phone |
| Alex | The watch flow and the dawn flow are enabled in the GitLab project; their consumer IDs and the flow account's username are in `deploy/gcp.env` (`FLOW_CONSUMER_ID`, `DAWN_FLOW_CONSUMER_ID`, `FLOW_SERVICE_ACCOUNT`, `WATCH_ISSUE_IID`), and the relay was redeployed after that | GitLab, Cloud Shell |
| Claude Code | The day-one test passed ([scripts/day_one.py](../scripts/day_one.py)): a flow started through the Flows API posted its note | with `GITLAB_TOKEN` in the environment |
| Alex | The Cloud Scheduler job `relay-tick` is resumed (setup leaves it paused) | Cloud Shell: `gcloud scheduler jobs resume relay-tick --location <region>` |

## The evening (Alex, phone, 5 minutes)

1. After 21:00 (`daysheet_at` in `ops/oncall.yml`), once the day sheet note is on the "Tonight's watch" issue (the relay's status page says "Day sheet posted" under Dusk), assign the issue to the dusk flow. Wait for the orders merge request (a few minutes).
2. Read the orders and the rehearsal note code posted on the merge request (each flag order was applied on staging, the staging shop checked, the flag restored). Delete any order you would not sign. Merge (or approve, if merging is not allowed). That is the signature.
3. Check the relay's status page: it should say "Active until 07:00" with the orders listed.
4. Go to bed with the phone's sound on for ntfy.

## The night (Claude Code or Alex from Cloud Shell, no attention needed)

Start the runner so the faults begin at 01:40 local time:

```sh
DEMO_KEY=$(gcloud secrets versions access latest --secret=demo-key) \
  nohup python3 scripts/test_night.py --shop https://SHOP_URL --at 01:40 > test-night.log 2>&1 &
```

What it does, in real minutes after 01:40 (`--dry-run` prints this):

| Minute | What the shop does | What the relay should do |
|---|---|---|
| 0 | demo traffic starts, about 60 checkouts a minute | nothing |
| 3 to 19 | `inventory_slow` on: both checkout paths fail | about minute 8: incident opened, watch flow asked; the flow declines order 1 (the old path fails too); one page with the `stock_from_cache` suggestion |
| when paged | | Alex taps thumbs-up on the page note: code turns `stock_from_cache` on, the shop recovers |
| 20 onward | `rounding_bug` on: the new checkout path fails | about minute 25: incident opened, watch flow asked, order 1 carried out (`new_checkout` off); minute 35: re-check passes, no page |
| 45 | faults off, traffic stops | nothing |
| 07:00 | | orders expire; the watch log is posted on the watch issue; the dawn flow opens the countersign merge request |

If the page does not arrive within 15 minutes of minute 3, the relay's own problem page (three failed ticks) or its status page says why. If the page is not answered, the incident closes on its own once the shop recovers (the suggestion is dropped with it), so the rounding bug at minute 20 still opens its own incident and reaches the signed order.

## The morning (Alex, phone, 3 minutes)

1. Read the watch log on the watch issue: woken once, one incident handled while asleep.
2. Open the countersign merge request. It proposes keeping `new_checkout` off until the fix ships and restoring `stock_from_cache`. Merge or approve.
3. The relay's note on the watch issue says what it restored.

## What to record on a test night

- Screenshots or a screen recording of: the orders merge request, the page on the phone, the thumbs-up, the incident notes (the agent's request and code's checks), the recovery on the shop page, the watch log, the countersign.
- Times: when the fault started, when the incident opened, when the flow answered, when the action ran. The watch log has them.
- Anything that needed a hand. Each becomes a fix or a line in the video's honest labels.

## If something fails

| Symptom | First thing to check |
|---|---|
| No incident opens | The Scheduler job is resumed; `GET /readyz` on the relay; the shop's `/metrics.json` shows the error rate |
| Incident opens but no flow note within 8 minutes | The flow session in GitLab (AI, Sessions); `FLOW_CONSUMER_ID` and `FLOW_SERVICE_ACCOUNT`; the Flows API answer in the relay's logs |
| The Flows API refuses to start the watch flow at all (decision D1 in [PLAN.md](PLAN.md)) | Redeploy the relay with `WATCH_MODE=standing` (Standing Orders): no model at night, code carries out the first signed order whose numbers hold and says so on the incident. The night's timeline changes: at about minute 8 code turns `new_checkout` off on the numbers alone, and at about minute 18 the re-check sees the old path still failing (the slowdown lasts until minute 19 for this reason) and pages, offering no suggestion. Say so in the video. |
| The page does not reach the phone | The ntfy topic subscription; the relay's logs ("push to the on-call phone") |
| The thumbs-up does nothing | It must be on the page note, from the on-call account, within 60 minutes of the page |
| Nothing at 07:00 | `WATCH_ISSUE_IID` and `DAWN_FLOW_CONSUMER_ID` set; the relay's tick summary has a `morning` list. Without a dawn flow, or with one that opens nothing within 20 minutes, code opens the countersign merge request itself ("written by code"); merging it as it is restores everything |
