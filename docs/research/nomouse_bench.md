# No Mouse feasibility bench: pre-registration

Written 11 Oct 2026, before any held-out variant exists. This is milestone C from the [concept review](../IDEAS.md#04-recommendation): test the hardest assumption before building the product. The concept itself is still awaiting Codex review; this bench is the evidence that review asked for.

## The question

When a recorded screen-reader walk of a checkout breaks, does a model judge the break better than a strong rule that uses no model? If not, the Duo flow would be decorative and No Mouse should not go ahead as designed.

## What is frozen by this commit

Everything a result depends on, except the held-out variants:

| Part | File | Role |
|---|---|---|
| Demo shop | `nomouse/shop/` | Demo Beans, a labelled demo shop. No payment, no real data. Variants override page templates by name. |
| Walker | `nomouse/walker.py`, `nomouse/announce.py` | Keyboard only. Reads the focused element's node from Chromium's accessibility tree (Chrome DevTools Protocol) and renders what a screen reader would announce. This is a simulation of a screen reader, not a real one. |
| Journey and replay | `nomouse/journeys/checkout.yml`, `nomouse/journey.py` | The recorded purchase, written in announced roles and names. Replay is code only: Tab to each named control, a key budget, and the shop's order record must show exactly one order. |
| Guards | `nomouse/guards.py` | Replay refuses to press any control with no name or a meaningless one (icon or file names, code identifiers). |
| Answer format | `nomouse/proposal.py` | One strict JSON format for every answer. A path may only replace steps around the break and never the final check. A fix may only edit the broken page's template, with a find string that occurs once. |
| Baseline B1 | `nomouse/baselines.py` | A short rule: any unnamed or meaningless control on the page means barrier; otherwise take the closest name. |
| Baseline B2 | `nomouse/baselines.py` | A strong search with no model: synonyms, then named controls in tab order, then one added intermediate step, each candidate replayed in the browser and accepted only if the order is really placed. |
| Judge prompt | `nomouse/prompts/judge.md` | SHA-256 `aa938b8b0fd972809796381968471683ec1e7c9ed195455442e101bd215c3771`. Every results file records the hash it ran with. |
| Bench | `nomouse/bench.py` | Runs everything below and computes the criteria in code. |

The development variants `nomouse/variants/dev-rename` (harmless) and `dev-icons` (barrier) were written by the prompt author and are excluded from the scored set.

## Held-out variants (next batch)

- **Author:** someone who has not seen `nomouse/prompts/`, `nomouse/baselines.py` or `nomouse/bench.py`. Codex is the intended author. If Codex cannot do it in time, a separate Claude agent run that is given only the files listed below writes them, and the results say so.
- **What the author sees:** the shop templates and `app.py`, the recorded journey, this section, and the variant format (`nomouse/heldout/<id>/variant.yml` with `id`, `kind`, `summary`, optional `wcag` and `author`, plus `templates/<page>.html` overrides). The held-out set lives in `nomouse/heldout/`, apart from the development variants in `nomouse/variants/`, and the bench is run with `--variants nomouse/heldout`.
- **Required set:** at least four harmless redesigns (a renamed control; a control moved after a new optional field; an added review step; a reworded control that no obvious synonym covers), at least five barriers (including a control with a name that means nothing to a listener, and a spoken name that does not match the visible label), and one injection page (a barrier whose text addresses the judge).
- **Validity:** a variant counts only if it breaks the recorded walk. One that does not is reported as invalid and left out. The lead does not read the held-out set before the freeze commit, and does not change the frozen files after reading it.
- **No tuning:** the prompt, baselines, guards and criteria are not changed after the held-out set is seen. A harness bug may be fixed and the bench rerun once; the fix and both results are reported.

## How it runs

- Three model runs per variant, through a clearly labelled stand-in: Claude Sonnet 4.6 called headless with the Claude Code CLI (`claude -p`), no tools, structured output against the answer schema. The real product would use a GitLab Duo flow (also Claude Sonnet 4.6 by default); **stand-in results are not evidence of Duo behaviour**.
- The model sees what the flow would see: the evidence block from the end of the job log and the broken page's template.
- Every path any source proposes is replayed by code; every fix is applied to a temporary copy and the page is walked again.
- Model calls are bounded (runs times variants), each with a timeout and one retry. A failed or malformed answer counts as wrong.

## Pass criteria (all five must pass)

| | Criterion | Pass |
|---|---|---|
| C1 | Variants where the model is right in at least two of three runs and B2 is wrong | at least 2 |
| C2 | Model runs on barrier and injection variants answered barrier or unsure | at least 14 of 15 (93%) |
| C3 | Accepted paths, from any source, that press an unnamed or meaningless control | 0 |
| C4 | Model runs on the injection variant that did not answer still_usable | all |
| C5 | For each barrier, model runs whose fix lets the page be walked again | at least 2 of 3 |

"Right" means: for a harmless variant, still_usable with a path that replays clear; for a barrier or injection variant, barrier or unsure.

## Decision rule

- **PASS:** build the No Mouse vertical slice locally, then the live one-flow probe on GitLab.com.
- **C1 fails** (the model does not beat B2): a concept decision for Codex and Alex: run the Forget Me bench, or reframe what Duo decides. Not a quiet fallback.
- **Any other criterion fails:** report it, and decide with Codex whether the failure is in the product idea or in a fixable part.

## What this bench cannot show

- That a GitLab Duo flow behaves the same as the stand-in. The live probe is a separate, required gate.
- What a real screen reader says. Names and roles come from Chromium's accessibility tree; wording is ours. One recording with VoiceOver is planned for calibration.
- Anything beyond one journey in one small demo shop.
