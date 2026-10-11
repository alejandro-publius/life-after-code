# The case: who loses sleep, and what the field already says

Written 11 Oct 2026 for the README's "why it matters" lines. The pages below are blocked from the environment this was written in, so every fact was read through a web search summary and is marked (unverified) until someone opens the link and checks the wording. Do not quote a number in the video or on Devpost until it is checked.

## How much on-call load is too much

- Google's SRE book, chapter "Being On-Call": an incident takes about 6 hours to handle once root-cause analysis, remediation and the postmortem are counted, so the ceiling is 2 incidents per 12-hour shift; it also describes a typical median of zero pages per day. [sre.google/sre-book/being-on-call](https://sre.google/sre-book/being-on-call/) (unverified)
- The SRE workbook, chapter "On-Call", keeps the target of at most two incidents per on-call shift, to leave time for follow-up. [sre.google/workbook/on-call](https://sre.google/workbook/on-call/) (unverified)

What this means for Night Orders: a small team cannot hire its way under that ceiling at night. Every page that a signed, reversible action could have handled is a page that counts against it.

## What on-call does to sleep, even without a call

- An online survey of about 228 on-call workers in Australia (not software engineers): 80% slept under 7 hours a night while on call, and 56% said their sleep suffered on on-call nights even when no call came; worrying about missing a call was a main concern (69%). [PMC5876943](https://pmc.ncbi.nlm.nih.gov/articles/PMC5876943/) (unverified)

What this means for Night Orders: the cost is not only the pages. Knowing that anything might need you is itself the load. A signed boundary ("these exact things are handled; everything else wakes you") is meant to make the quiet nights actually quiet. We have not measured that; the demo counts are from an invented night.

## What we did not find

- No software-specific survey of on-call sleep (PagerDuty, incident.io, Catchpoint) came up in the search. If one exists, it would be a better source than the Australian study.

## What Alex can check in ten minutes

1. Open the two sre.google links and copy the exact sentences about the 6 hours and the two incidents.
2. Open the PMC article and copy the abstract's numbers and its title.
3. Replace "(unverified)" here and in the README with the quotes, or delete any line that does not hold.
