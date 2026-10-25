# No Mouse fix bench: pre-registration

Written 11 Oct 2026, before any barrier in the fix set exists. It is the gate named in [IDEAS.md, section 0.5](../IDEAS.md#05-feasibility-result-11-oct-2026) for option A, reframing No Mouse so that code decides whether a person can still pay and the GitLab Duo flow writes the fix.

## The question

When code has confirmed a barrier, does a model write a working repair more often than simple rules do? If not, No Mouse has no decision left that needs a model, and option A should not go ahead.

## Why this test

The [first bench](nomouse_bench.md#results-11-oct-2026) showed that deciding the route needs no model: with one more rule (the spoken name must contain the visible label), the no-model search chose the right route on all 15 held-out variants in a [post-hoc rerun](../../experiments/nomouse/posthoc-baselines-2026-10-11/README.md). The model's repairs worked on every barrier, but nothing compared them with a fixer that uses no model.

## What is frozen by the commit that adds this file

| Part | File | Role |
|---|---|---|
| Barrier gate | `nomouse/journey.py`, `nomouse/guards.py`, `nomouse/baselines.py` | A variant is a barrier only if the recorded walk breaks and B2, the bounded search that presses only named controls whose names match their visible labels, finds no way to place the order. |
| F0, the rule fixer | `nomouse/rulefix.py` | Rules with no model, tried first on the control the walk expected: click-only and fake-role elements become real buttons or links (keeping the expected role); unnamed buttons and links get the name the recorded journey expected; junk alt text becomes that name; spoken names that contradict or say nothing beyond the visible label are removed or replaced; mismatched or missing field labels are corrected; controls taken out of the tab order are put back; a hidden or fake expected heading is restored. It gives no fix for a focus trap with no closable control or for visible text that is itself meaningless. It sees the same evidence and template as the model. Its SHA-256 is recorded in every results file. |
| Model | `nomouse/prompts/judge.md`, `nomouse/model.py` | Unchanged from the first bench (SHA-256 `aa938b8b0fd972809796381968471683ec1e7c9ed195455442e101bd215c3771`). Three runs per barrier through the labelled stand-in (Claude Sonnet 4.6 via `claude -p`), not GitLab Duo. |
| Fix check and scoring | `nomouse/fix.py`, `nomouse/fixbench.py` | Applies each fix to a temporary copy, walks the fixed page, and scores the criteria below in code. |

Fairness note: F0 was written after the first held-out barriers were seen, so it is tuned to barrier types we already know. That favours the rules, which makes a model win harder to get, not easier.

## The blind fix set

- **Author:** a separate agent run that has not seen `nomouse/prompts/`, `nomouse/rulefix.py`, `nomouse/fixbench.py`, `nomouse/bench.py`, `nomouse/baselines.py`, `nomouse/guards.py`, `nomouse/heldout/` or `experiments/`. It sees the shop templates and `app.py`, the recorded journey and this section.
- **Where:** `nomouse/fixset/<id>/variant.yml` (`id`, `kind` of barrier or injection, `summary`, `wcag`, `author`) and `templates/<page>.html` overrides; ids numbered so they say nothing about the barrier.
- **Required set:** at least 10 barriers across the home, product, cart and checkout pages, using varied mechanisms. Some should need the fixer to work out what a control is for, from context on the page rather than from its old name; some may be mechanical. At most 2 may be injection pages. The author must not try to defeat or favour any particular fixer.
- **Validity:** a variant counts only if the recorded walk breaks and code finds no usable path; any other variant is reported as excluded.
- **No tuning:** nothing frozen changes after the set is written. A harness bug may be fixed and the bench rerun once; both results are reported.

## Green

A fix is green when all of these hold: code walks the fixed page and the shop records the order (by the recorded journey, or by the bounded search over named controls); that walk presses no unnamed, meaningless or mislabelled control; and the fix removes at most 2 words of visible text, so deleting a feature does not count as a repair.

## Pass criteria (all three must pass)

| | Criterion | Pass |
|---|---|---|
| F1 | Barriers where the model's fix is green in at least two of three runs and F0's is not | at least 2 |
| F2 | Barriers where the model's fix is green in at least two of three runs | at least two thirds of valid barriers |
| F3 | Green fixes whose walk pressed a meaningless control (any fixer) | 0 |

## Decision rule

- **PASS:** go ahead with option A. Build the vertical slice: the CI walk, the Duo flow that turns a confirmed barrier into an issue and a fix merge request, and code that replays the fix before anyone is asked to merge.
- **F1 fails:** the model does not repair barriers better than rules. No Mouse then has no decision that needs a model; recommend option B (Forget Me) or a new framing to Codex and Alex, and say so plainly.
- **F2 fails with F1 passing:** model fixes help sometimes but are unreliable; report and decide with Codex whether a person-in-the-loop fix flow is still worth building.

## What this cannot show

- That a GitLab Duo flow writes the same fixes; the live probe is a separate, required gate.
- That a green fix meets WCAG. Green means a person relying on a screen reader can now finish this one purchase, judged by our simulated walk; it is not an audit.
- That the content rule catches every harmful fix. It counts removed visible words only; Codex should read the fix diffs in the results.
