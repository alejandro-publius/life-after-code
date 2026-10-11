# No Mouse (feasibility stage)

No Mouse checks whether a person who is blind could still buy something after a change to a shop. Code walks the checkout with the keyboard only and hears each control the way a screen reader would. When the recorded walk breaks, something has to decide whether the change is a harmless redesign or a barrier. In the product, that is a GitLab Duo flow; here, a local bench tests whether a model is better at it than a strong rule with no model.

**Status:** feasibility stage, local only. The concept is under review ([docs/IDEAS.md, section 0](../docs/IDEAS.md#0-reopened-selection-6-oct-2026)) and the bench is pre-registered in [docs/research/nomouse_bench.md](../docs/research/nomouse_bench.md). Nothing here has run on GitLab.com or in a Duo flow.

**What is demo data:** Demo Beans is an invented shop. It takes no payment and keeps orders only in memory. The persona, products and planted changes are invented.

**What is simulated:** names and roles come from Chromium's accessibility tree, which is what screen readers on Chromium receive, but the spoken wording is ours. It is not a recording of a real screen reader.

## Run it locally

From the repository root, with Python 3.11 or newer and [uv](https://docs.astral.sh/uv/):

```sh
uv sync --locked --extra walker
uv run --locked --extra walker python -m playwright install chromium
uv run --locked uvicorn nomouse.shop.app:app --host 127.0.0.1 --port 8090
```

Open [http://127.0.0.1:8090](http://127.0.0.1:8090) to see the shop. To serve a variant, start the shop with `NOMOUSE_VARIANTS_DIR=nomouse/variants` and set the `nm_variant` cookie to the variant id. No environment variables are needed otherwise, and nothing is sent anywhere.

Tests (the browser tests need the Chromium step above):

```sh
uv run --locked pytest -q tests/nomouse
NOMOUSE_REQUIRE_BROWSER=1 uv run --locked --extra walker pytest -q -m browser tests/nomouse
```

The bench, with the baselines only:

```sh
uv run --locked --extra walker python -m nomouse.bench --variants nomouse/variants --runs 1 --model none --out /tmp/nomouse-bench
```

With `--model standin`, the bench also asks a stand-in model through the Claude Code CLI (`claude -p`, signed in on this machine). That is a local stand-in for the Duo flow's model, labelled as such in every result; its answers are not Duo results.

To reset: stop the shop. Orders, carts and bench copies of the variants live only in memory or in temporary directories.

## How it fits together

| File | What it does |
|---|---|
| `shop/` | The demo shop; variants override page templates by name |
| `walker.py`, `announce.py` | Keyboard-only browser session; what has focus and how it is announced |
| `journeys/checkout.yml` | The recorded purchase, in announced roles and names |
| `journey.py` | Replays a journey; code decides clear, broken, refused, over budget or no order; prints the evidence block |
| `guards.py` | Never press a control with no name or a meaningless one |
| `proposal.py` | The one answer format for baselines and models, checked strictly |
| `baselines.py` | B1 (a short rule) and B2 (a bounded search in the browser) |
| `model.py` | Prompt rendering, the labelled stand-in model, and recorded answers for tests |
| `fix.py` | Applies a proposed template fix to a temporary copy |
| `bench.py` | Runs the pre-registered bench and writes results |
| `prompts/judge.md` | The judge prompt, frozen before the held-out variants |
