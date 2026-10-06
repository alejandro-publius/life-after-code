## Tonight's watch

This issue stays open. Each evening the on-call person assigns it to the dusk flow.

1. **Dusk.** Assign this issue to the dusk flow. It reads today's merged merge requests, deployments and
   flags, may ask one question here, and opens a merge request that changes `ops/night-orders.yml`.
2. **Sign.** Read the orders, edit or delete any of them, and merge. The merge is the signature.
   Close the merge request instead to sign nothing: then every alert wakes you.
3. **Night.** The relay watches production. It acts only on a signed order, and only when code and the
   watch flow agree. Anything else pages you.
4. **Dawn.** At 07:00 the orders end. Code posts the watch log here, and the dawn flow opens the
   countersign merge request: keep or undo each change made overnight. Merge it to decide.

Rules: `skills/night-orders/SKILL.md` in this repository.

/label ~"night-watch"
