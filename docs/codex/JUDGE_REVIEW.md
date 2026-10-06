# One judge review

Reviewed October 5, 2026, Pacific time, starting at 22:03 PDT. Source branch: main at `5fac2eb`. One review round, followed by implementation checks. No second product review was started.

## What could cost points

| Risk | Observed evidence | Judging criterion |
| --- | --- | --- |
| Missing live proof | No live URL in the current README or config; STATUS says GitLab and Google have not run. No configured cloud credentials in this session. | Technological Implementation and Presentation; Google deployment bonus remains unavailable |
| Confusing path | Shop and relay are separate status pages with no connected before-bed, night and morning journey. The root page in a browser ends at "No check has run yet." | Design |
| Thin human result | Wake-ups and changes live in terminal output and raw Markdown. The necessary wake and the incident handled during sleep are difficult to compare. | Potential Impact and Presentation |
| Missing recovery visual | The video describes a checkout chart, but the shop renders a wide metrics table. Empty local metrics show no recovery to inspect. | Presentation |
| Stale status risk | Relay HTML has no automatic refresh, although the shop refreshes. A page kept open across expiry can retain old wording. | Design and Technological Implementation |

These findings combine source inspection with a first-time browser check of the locally served current app at 390 by 844 and 1440 by 900. They are not a live-site audit: no live URL was available. The session requested one from Alex and continued local work. No live downtime, performance or integration failure is inferred from missing credentials.

Technical reviewers need inspectable code and actual integration runs. Product reviewers need one connected path. Impact reviewers need to see what happens to the on-call person. Innovation reviewers need to see that the permission is narrow, signed and temporary. Presentation reviewers need visible cause and effect. These are rubric lenses, not assertions about individual judges' private preferences.

## The single improvement

Build a guided browser replay through the existing Watch decision code. It makes the before-bed choice, necessary wake-up, allowed overnight fix and morning review usable without a terminal or account. It addresses the connected-path and buried-human-result gaps together, and supplies a recovery chart from actual replay samples.

The primary criterion is **Design**, with **Presentation** also served. The [official rules](https://gitlab-transcend.devpost.com/rules) equally weight five criteria, so each contributes 20%. This is arithmetic, not a separate percentage printed by the rules. The build is labelled demo data and does not substitute for the required GitLab Duo integration proof.

The sandbox never contacts GitLab, a model API, a real phone or production. Default choices yield one necessary wake, one automatic incident and one human-approved action. Unsigned orders yield two wakes and zero automatic actions. Counts, chart samples, evidence and morning changes come from the decision code, not manually painted success states.

## Remaining work

- Complete and record an actual GitLab Duo and Google Cloud run. Path A does not require deployment, but the optional Google bonus requires a public working Google URL and deployment code. [Rules](https://gitlab-transcend.devpost.com/rules).
- Check the live URL on phone and laptop once available, including signed actions, state persistence and email or phone delivery.
- Make the connected watch's status visibly current across expiry. This was deliberately left for the next improvement.

The README screenshots are local browser captures of the new replay. The video script and Devpost draft identify its recorded model replies and pending live integration. CI results are recorded in [STATUS.md](../STATUS.md).
