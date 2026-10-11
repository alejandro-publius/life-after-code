## Tonight's watch

This issue stays open. Each evening the on-call person assigns it to the dusk flow.

1. **Dusk.** At 21:00 code posts the day sheet here. Assign this issue to the dusk flow. It reads the day
   sheet, drafts at most three orders and opens a merge request that changes `ops/night-orders.yml`. It never
   waits on you: a question goes in the merge request under "One question". Code rehearses the orders on
   staging and notes the result on that merge request.
2. **Sign.** Read the orders, edit or delete any of them, and merge or approve. That is the signature.
   Close the merge request instead to sign nothing: then every alert wakes you.
3. **Night.** The relay watches production. It acts only on a signed order, and only when code and the
   watch flow agree. Anything else pages you.
4. **Dawn.** At 07:00 the orders end. Code posts the watch log here and sends one quiet push, and the dawn
   flow opens the countersign merge request: keep or undo each change made overnight. Merge or approve it to
   decide. If no flow opens one, code does, keeping nothing until you say what to keep.
5. **Kept.** A kept change can name the merge request that ends it (`until_deployed`). When that merge
   request is in production, code puts the change back in daytime and notes it here.

Rules: `skills/night-orders/SKILL.md` in this repository.

/label ~"night-watch"
