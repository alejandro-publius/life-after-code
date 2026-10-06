# Scoring rubric for Part 5

Every candidate in [CANDIDATES.md](CANDIDATES.md) is scored 1 to 10 on each dimension below. 5 means average for this pool, not average for all software. Use the whole range. Score the concept as it would be if built well by Oct 24, but judge honestly what one builder can show.

## Dimensions scored by the three judges

The first five are the official judging criteria, which the rules weight equally ([RULES.md](../../RULES.md), [codex/RULES_CHECK.md](../../codex/RULES_CHECK.md)):

| Key | Dimension | What 10 means |
|---|---|---|
| tech | Technological Implementation | "How thoroughly and skillfully does the project use GitLab to automate the post-code DevSecOps lifecycle? Does the code and pipeline config reflect genuine effort and a working, non-trivial implementation?" |
| design | Design | "a complete, coherent end-to-end workflow, not just a technical proof of concept" |
| impact | Potential Impact | "a credible, specific case for solving a real problem for a real audience", and the solution visibly addresses it |
| innovation | Innovation/Idea | "How creative and novel is the concept and how inventively does it apply agentic automation compared to existing concepts?" (The top Innovation score also wins Most Creative.) |
| presentation | Presentation | A video under 3 minutes can show the automation running end to end and make the problem, the person and the reason clear |

The rest come from the handoff brief:

| Key | Dimension | What 10 means |
|---|---|---|
| stages | Lifecycle stages | Touches many of the nine stages (plan, create, verify, package, secure, release, configure, monitor, govern) for real, in a creative way (Most Stages Covered prize) |
| autonomy | Autonomy | A compelling, credible autonomy story at the level it fits (Assisted, Supervised or Hands-off), with a good chance at that level's prize given likely competition |
| human | Human moment | One person, one feeling, one scene a viewer remembers |
| novelty | Novelty | Far from the 2025 and 2026 winners, the current field, the crowded spaces and the judges' reference project ([FIELD.md](../../FIELD.md), [IDEATION_BRIEF.md](../IDEATION_BRIEF.md)) |
| sponsors | Sponsor depth | Duo Agent Platform at the core plus GitLab features, Google Cloud and Anthropic used naturally and deeply |
| wow | 30-second wow | The demo moment lands in the first 30 seconds of a video |

## Dimension scored by the engineer

| Key | Dimension | What 10 means |
|---|---|---|
| feasibility | Feasibility | One builder (Claude Code and Codex writing the code, Alex only copying messages until Oct 23) can build it, run it for real on GitLab, deploy it to Cloud Run, and film it by Oct 24, given the verified platform limits |

The engineer also flags traps: a trap looks strong but will likely fail (it cannot be demoed honestly, depends on access we may not have, needs weeks of real history, or collides with an excluded or crowded idea).

## Total

criteria = mean(tech, design, impact, innovation, presentation)

total = 3 x criteria + stages + autonomy + human + novelty + sponsors + wow + 2 x feasibility

Maximum 110. The official criteria carry the most weight because they decide the score. Feasibility counts double because an idea that cannot be shown working scores nothing.
