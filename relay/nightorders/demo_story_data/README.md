# Browser replay fixtures (DEMO DATA)

These files are bundled copies of the repository's `demo/night-2026-10-20`
fixtures and `ops/oncall.yml`, `ops/targets.yml`, and `ops/alerts.yml`.
They ship inside the relay package because the relay container copies `relay/`.

Juniper Market, Priya, the checkout metrics, the two faults, the changes, the
signature, the page reaction and the morning merge are invented demo data.
`night-2026-10-20/notes.json` and `dusk_recorded.json` contain recorded model
replies. They are inputs to the replay, not live model output.

`nightorders.browser_demo.replay` reads these fixed files and runs a fresh
in-memory shop through the existing `Watch` code. It makes no network calls,
uses no credentials, writes no files and changes no production state. The
browser's sign and approval choices select whether that run receives the
recorded signature and reaction. The real decision code determines what
happens, including the morning KEEP and UNDO operations.

The minute samples contain the last completed minute's error rates. Their
`at` field is the decision tick; `sampled_at` identifies the observed minute.
`flags_before` and `flags_after` show the actual flags around that tick. The
loop is bounded at 960 steps and 10 seconds.

An unsigned replay makes no changes. Its recorded morning keep proposal is
not applied: morning validation cannot keep a change that never occurred.
The replay reports that no countersign is needed.

The source scenario's planted log injection is inert demo evidence. It never
supplies an action to code. Allowed actions come from the signed orders or
the on-call person's approval of the one recorded suggestion.
