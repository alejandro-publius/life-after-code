# Post-hoc baseline rerun (not a pre-registered test)

After the held-out bench failed C1, code gained one rule: never press a control whose spoken name leaves out its visible label (WCAG 2.5.3), in commit `376679ce7895b704202cc85bfb77f2f026c4b1a8`. This rerun uses the same 15 held-out variants with no model, at `de3da238825210fe59f9a624834a0f84f754cf6a`.

Result: B2, which uses no model, now chooses the right route on all 15 variants; on heldout-06 it no longer accepts the button announced "Save for later". B1 is right on 13.

Read this as a check that the new rule works, not as evidence of generality: the rule was added after the held-out set was seen, so this set cannot test it fairly. The overall FAIL in `results.md` is only because no model ran.
