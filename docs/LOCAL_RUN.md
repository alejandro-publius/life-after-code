# Run a real local night

From the repository root, with Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv run --locked python scripts/run_local.py
```

Open the address printed by the command. The default port is 8082; use `--port 8083` if it is occupied.
The launcher starts its own disposable shop on a free loopback port. No GitLab, model, cloud or payment
credentials are needed. Both processes stay on this machine. Ctrl+C stops the launcher, attempts cleanup
and stops only its shop. The printed evidence directory is retained.

## One complete journey

1. Start the local run. Ten actual checkout requests establish the healthy starting state and save its flags.
2. Grant the exact permission shown, or continue unsigned. Local browser consent permits `new_checkout off`
   once, in this particular disposable shop, for ten real minutes. It is not a GitLab signature.
3. Plant the rounding fault and run the watch. Fifty actual checkout requests populate five accelerated
   minute buckets. The existing decision code checks the condition, traffic floor and permission. An unsigned
   run observes the same fault but makes no nightly flag change.
4. Verify the whole shop. Fresh checkout requests and independently read metrics establish recovery; an empty
   new path cannot establish it. The applied flag is also read back through a separate HTTP request.
5. Over coffee, keep the changed flag or restore its saved value. The injected fault is still present, so
   restoring the new path can make checkouts fail again. The interface reports that measured result.
6. Finish. The controller removes the planted fault, restores the original flags, reads them back and sends
   another set of checkouts. Download the receipt with the decisions, actual observations and cleanup result.

Refreshing the browser preserves the session. **Reload saved run** reconstructs its saved record. Mutation
intent and the original snapshot are flushed to disk before the HTTP write. A lost response leaves an
uncertain outcome; reloading does not repeat that write. Finish remains available for restoration and has
its own bounded request allowance even if the regular request budget is exhausted.

Each action has a 30-second limit; the normal session allows at most 200 shop requests and cleanup has a
separate allowance of 60. A fresh run uses a fresh evidence directory. `--state-dir PATH` chooses that new
directory; an existing session is preserved rather than overwritten.

## Know which layer you are seeing

| Layer | What actually executes |
| --- | --- |
| Local night | A real shop process, HTTP checkout requests, scoped flag mutations, independent readback, durable intent and measured recovery |
| Controlled infrastructure | Synthetic shopping requests, a deliberately planted fault and an accelerated minute clock; no customer purchase, charge or shipment |
| Decision mode | Existing deterministic Standing Orders checks; no fresh model decision or GitLab approval |
| Guided replay | The existing in-memory night, three-way comparison, chart inspection, incident memory and morning choices |
| Execution explorer | Previously captured real Dusk and Watch sessions, with their original artifact links; no live Dawn execution |

The receipt includes source revision and content digest, UTC request observations, logical sample times,
state snapshots and outcomes. Session control keys are omitted. Reconstruction checks cover a lost response
after a real local write; they do not establish production or cloud crash recovery. The archived GitLab
project remains outside this local execution path.

## Portable offline replay

To build a self-contained replay and execution explorer:

```sh
uv run --locked python scripts/build_offline.py --out /tmp/night-orders-offline.zip
```

Extract the ZIP and run `python3 serve.py` inside its folder. Python's standard library is enough; playback
needs no installed packages, credentials or network connection. The launcher verifies every bundled file
against `snapshot.json`, which also records source provenance. External artifact links still need a network.
This portable snapshot plays the simulated night and captured sessions; it does not run shop actions.

No video, narration, publishing or Devpost changes are part of this local workflow.
