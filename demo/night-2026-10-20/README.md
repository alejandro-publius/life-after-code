# Demo night: Tuesday 20 October 2026 (DEMO DATA)

Everything in this folder is invented demo data, labelled as such:

- The shop ("Juniper Market"), its traffic and its numbers are simulated.
- Both faults are planted: an inventory slowdown at 01:45 and a price-rounding bug in the new checkout at 03:07.
- "Priya" is a persona; Alex's GitLab account plays her.
- `notes.json` holds recorded answers in the format the watch flow writes. They are not live model output.
- One log line in `scenario.yml` is a planted prompt injection, to show that log text never drives an action.

What is real: the code that decides. `python -m nightorders.demo_night` runs the same Watch class the relay
runs in production, against these files, and prints the night and the morning watch log.
