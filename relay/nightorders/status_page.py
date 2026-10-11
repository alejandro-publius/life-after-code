"""The relay's public status page at / and its JSON at /status.json. Read-only, no scripts.

It is drawn with the browser demo's own stylesheet, so the live page and the demo are one product. Everything on
it comes from the relay's saved state: tonight's orders as code checked them, the last hour of the shop's numbers,
the night's ledger, the dusk chores and the morning countersign. Every value is escaped, and every link is built
from the GitLab project's own web address plus a number, never from note text.
"""

from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from . import kept
from .decide import APPROVAL_WINDOW_MINUTES
from .signals import Metrics

DEMO_CHIP = "Live relay. Demo shop, planted faults."
SAMPLE_MINUTES = 60
SHOWN_KINDS = ("alert", "asked", "acted", "failed", "declined", "woke", "approved", "refused", "recovered",
               "stood_down", "expired")
KIND_WORDS = {"alert": "Alert", "asked": "Agent asked", "acted": "Order ran", "failed": "Change failed",
              "declined": "Agent declined", "woke": "Woke her", "approved": "She approved", "refused": "Refused",
              "recovered": "Re-check passed", "stood_down": "Stood down", "expired": "Orders ended"}
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' "
           "height='32' rx='8' fill='%23243843'/%3E%3Cpath d='M22 22A10 10 0 0 1 10 8a9 9 0 1 0 12 14Z' "
           "fill='%23edba59'/%3E%3C/svg%3E")


def _e(text: Any) -> str:
    return html.escape(str(text), quote=True)


def samples_of(metrics: Metrics, now: datetime, minutes: int = SAMPLE_MINUTES) -> list[dict]:
    """The last complete minutes of the checkout numbers, oldest first, for the page's chart."""
    end = now.replace(second=0, microsecond=0)
    out = []
    for back in range(minutes, 0, -1):
        at = end - timedelta(minutes=back)
        old = metrics.get("checkout_error_rate.old", at)
        new = metrics.get("checkout_error_rate.new", at)
        if old is None and new is None:
            continue
        out.append({"at": at.astimezone(timezone.utc).isoformat(timespec="minutes"), "old": old, "new": new,
                    "all": metrics.get("checkout_error_rate.all", at), "checkouts": metrics.get("checkouts.all", at)})
    return out


def _local(moment: datetime, tz: Any) -> str:
    return moment.astimezone(tz).strftime("%H:%M")


def _link(base: str | None, path: str, text: str) -> str:
    """A link into the GitLab project, or the plain text when the project address is not known yet."""
    if not base or not base.startswith("https://"):
        return f"<span>{_e(text)}</span>"
    return f'<a href="{_e(base.rstrip("/") + path)}">{_e(text)}</a>'


def _countdown(now: datetime, end: datetime) -> str:
    left = end - now
    if left.total_seconds() <= 0:
        return "ended"
    hours, rest = divmod(int(left.total_seconds()) // 60, 60)
    return f"ends in {hours} h {rest:02d} min" if hours else f"ends in {rest} min"


def chart(samples: list[dict], events: list[dict], tz: Any) -> str:
    """The last hour of checkout error rates as an inline SVG, with a numbered marker per decision."""
    if not samples:
        return ('<p class="small-copy">No shop numbers yet. The chart fills in as the relay reads the shop once '
                'a minute.</p>')
    width, height, left, right, top, plot_h = 600, 236, 64, 14, 18, 160
    plot_w = width - left - right
    times = [datetime.fromisoformat(s["at"]) for s in samples]
    first, last = times[0], times[-1]
    span = (last - first).total_seconds() or 1.0
    top_rate = max([0.10] + [v for s in samples for v in (s.get("old"), s.get("new")) if isinstance(v, (int, float))])

    def x(moment: datetime) -> float:
        return left + ((moment - first).total_seconds() / span) * plot_w if len(samples) > 1 else left + plot_w / 2

    def y(rate: float) -> float:
        return top + plot_h * (1 - rate / top_rate)

    def path(key: str) -> str:
        points = [(x(t), y(s[key])) for t, s in zip(times, samples) if isinstance(s.get(key), (int, float))]
        if len(points) == 1:
            px, py = points[0]
            return f"M{px - 3:.1f},{py:.1f} L{px + 3:.1f},{py:.1f}"
        return " ".join(f"{'L' if i else 'M'}{px:.1f},{py:.1f}" for i, (px, py) in enumerate(points))

    ticks = [0.0, 0.05, 0.10] if top_rate <= 0.10 else [0.0, 0.10, 0.20]
    parts = []
    for rate in ticks:
        parts.append(f'<line x1="{left}" y1="{y(rate):.1f}" x2="{left + plot_w}" y2="{y(rate):.1f}" class="chart-grid"/>'
                     f'<text x="{left - 10}" y="{y(rate) + 7:.1f}" text-anchor="end" class="chart-label">'
                     f"{round(rate * 100)}%</text>")
    parts.append(f'<line x1="{left}" y1="{y(0.05):.1f}" x2="{left + plot_w}" y2="{y(0.05):.1f}" class="chart-threshold"/>'
                 f'<text x="{left + plot_w}" y="{y(0.05) - 7:.1f}" text-anchor="end" class="chart-label limit-label">'
                 "5% limit</text>")
    parts.append(f'<path d="{path("new")}" class="chart-line new"/><path d="{path("old")}" class="chart-line old"/>')
    markers, legend, last_x, lift = [], [], -1e9, 0
    for event in events:
        moment = datetime.fromisoformat(event["at"])
        if not first <= moment <= last + timedelta(seconds=59):
            continue
        at = min(x(moment), left + plot_w)
        lift = lift + 1 if at - last_x < 26 else 0
        last_x = at
        number = len(legend) + 1
        cy = top + 12 + lift * 26
        markers.append(f'<line x1="{at:.1f}" y1="{top}" x2="{at:.1f}" y2="{top + plot_h}" class="chart-action"/>'
                       f'<circle cx="{at:.1f}" cy="{cy}" r="11" class="marker-badge"/>'
                       f'<text x="{at:.1f}" y="{cy + 6}" text-anchor="middle" class="marker-number">{number}</text>')
        legend.append(f'<li><span class="marker-dot" aria-hidden="true">{number}</span>{_e(_local(moment, tz))} '
                      f'{_e(KIND_WORDS.get(event["kind"], event["kind"]).lower())}</li>')
    parts += markers
    labels = [(0, "start"), (len(samples) - 1, "end")] if len(samples) > 1 else [(0, "middle")]
    for index, anchor in labels:
        px = left if anchor == "start" else left + plot_w if anchor == "end" else x(times[index])
        parts.append(f'<text x="{px:.1f}" y="{top + plot_h + 28}" text-anchor="{anchor}" class="chart-label">'
                     f"{_e(_local(times[index], tz))}</text>")
    description = ("Checkout error rates for the old and new paths over the last hour the relay read, with the 5% "
                   "limit of a signed new checkout order and a marker for each decision.")
    svg = (f'<svg id="metrics-chart" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-desc">'
           f'<title id="chart-title">Checkout error rates, last hour</title><desc id="chart-desc">{_e(description)}</desc>'
           + "".join(parts) + "</svg>")
    marker_list = f'<ol class="marker-legend">{"".join(legend)}</ol>' if legend else ""
    rows = "".join(
        f"<tr><th scope=\"row\">{_e(_local(t, tz))}</th><td>{_pct(s.get('old'))}</td><td>{_pct(s.get('new'))}</td>"
        f"<td>{_e(s.get('checkouts') if s.get('checkouts') is not None else '')}</td></tr>"
        for t, s in zip(times, samples))
    return (f'<section class="metric-card" aria-labelledby="metric-title"><div class="metric-title"><p class="eyebrow">'
            f'Demo shop · read once a minute</p><h3 id="metric-title">The last hour</h3></div>'
            f'<div class="metric-legend"><span class="legend-item new">New checkout</span>'
            f'<span class="legend-item old">Old checkout (dashed)</span></div><div class="chart-wrap">{svg}</div>'
            f'{marker_list}<details class="chart-table"><summary>Read the numbers</summary><div class="table-scroll">'
            f"<table><caption>Complete one-minute samples, the on-call person's local time</caption><thead><tr>"
            f'<th scope="col">Minute</th><th scope="col">Old checkout</th><th scope="col">New checkout</th>'
            f'<th scope="col">Checkouts</th></tr></thead><tbody>{rows}</tbody></table></div></details></section>')


def _pct(value: Any) -> str:
    return f"{float(value) * 100:.1f}%" if isinstance(value, (int, float)) else ""


def public(doc: dict | None, now: datetime) -> dict:
    """What /status.json serves: the page's facts, read-only. Never a setting, a token or a URL with a secret."""
    relay = (doc or {}).get("relay") or {}
    status = relay.get("status") or {}
    ledger = ((doc or {}).get("watch") or {}).get("ledger") or []
    return {
        "label": DEMO_CHIP,
        "night": (doc or {}).get("night"),
        "checked_at": status.get("checked_at"),
        "timezone": status.get("timezone"),
        "mode": "standing" if status.get("standing") else "flow",
        "orders": status.get("orders"),
        "problems": status.get("problems") or [],
        "events": [{"at": e.get("at"), "kind": e.get("kind"), "text": e.get("text"), "incident": e.get("incident")}
                   for e in ledger if e.get("kind") in SHOWN_KINDS],
        "samples": status.get("samples") or [],
        "watch_log": (relay.get("watch_log") or {}).get("text"),
        "dusk": {"daysheet": relay.get("daysheet"), "rehearsed": sorted((relay.get("rehearsed") or {}), key=int)},
        "morning": {"countersign": (relay.get("dawn") or {}).get("countersign_text")},
        "kept": [kept.summary(item) for item in relay.get("kept") or []],
        "kept_ended": [{"at": e.get("at"), "text": e.get("text")} for e in relay.get("kept_ended") or []],
        "relay_failing": bool(relay.get("error")),
    }


def render(doc: dict | None, now: datetime, unavailable: bool = False) -> str:
    relay = (doc or {}).get("relay") or {}
    status = relay.get("status") or {}
    tz = ZoneInfo(status["timezone"]) if status.get("timezone") else timezone.utc
    project = status.get("project_url")
    orders = status.get("orders")
    problems = status.get("problems") or []
    signed = bool(orders and not problems and orders.get("items"))
    end = datetime.fromisoformat(orders["ends_at"]) if orders else None

    if unavailable:
        headline, sub = "The relay's state cannot be read right now.", "The demo below needs nothing from it."
    elif not status:
        headline, sub = "Nothing signed yet. Here is the demo.", ("The relay has not checked the shop yet. Until "
                                                                  "the first night, the demo shows how one goes.")
    elif signed and end and now < end:
        headline, sub = f"Signed until {_local(end, tz)}. Code is keeping watch.", (
            "Outside these orders, every alert wakes the on-call person.")
    elif signed and end:
        headline, sub = f"Tonight's orders ended at {_local(end, tz)}.", "What changed overnight waits for the countersign."
    else:
        headline, sub = "Nothing signed tonight.", "Every alert wakes the on-call person."

    body = ['<header class="site-header"><a class="brand" href="/" aria-label="Night Orders relay home">'
            '<span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 32 32" width="32" height="32">'
            '<path d="M24 23.5A12 12 0 0 1 9 7a11 11 0 1 0 15 16.5Z" fill="currentColor"/>'
            '<circle cx="24" cy="8" r="1.5" fill="currentColor"/></svg></span>'
            '<span class="brand-name">Night Orders<span>The relay, live</span></span></a>'
            f'<div class="demo-notice"><p class="demo-label"><span class="label-long">{_e(DEMO_CHIP)}</span>'
            '<span class="label-short">Live relay</span></p><p class="safety-note">Read-only. Nothing here changes '
            "anything.</p></div></header>",
            '<div class="page-shell">',
            '<section class="intro" aria-labelledby="intro-title"><p class="eyebrow">Night Orders relay · status</p>'
            f'<h1 class="intro-title" id="intro-title">{_e(headline)}</h1><p class="intro-copy">{_e(sub)}</p>'
            '<p class="intro-safety">Live relay. The shop it watches is a demo shop with planted faults.</p>'
            '<div class="action-row"><a class="button primary try-demo" href="/demo">Try one night with Priya</a>'
            '<a class="button secondary" href="/status.json">This page as JSON</a></div>'
            '<p class="quiet small-copy">A guided demo replay with recorded agent replies. No setup needed.</p></section>']

    main = ['<main class="journey-panel" id="journey-content">']
    if status:
        main.append('<div class="chapter-head"><h2 class="chapter-title">Tonight\'s orders</h2></div>')
        if status.get("standing"):
            main.append('<div class="decision-card veto-card"><p class="decision-kicker">Standing orders tonight</p>'
                        "<p class=\"decision-copy\"><strong>Standing orders tonight.</strong> No model at night: code "
                        "carries out the first signed order whose numbers hold, and says so on the incident. "
                        "Everything else wakes the on-call person.</p></div>")
        if signed:
            when = f"Active until {_local(end, tz)}." if now < end else f"Expired at {_local(end, tz)}."
            signed_at = datetime.fromisoformat(orders["signed_at"])
            mr = orders.get("merge_request")
            via = (" in " + _link(project, f"/-/merge_requests/{int(mr)}", f"!{int(mr)}")) if mr else ""
            main.append(f'<p class="inline-note"><strong>{_e(when)}</strong> {_e(_countdown(now, end).capitalize())}. '
                        f"Signed by {_e(orders['signed_by'])} at {_local(signed_at, tz)} ({_e(orders['method'])}){via}, "
                        f"for the night of {_e(orders['night'])}.</p>")
            main.append('<div class="order-list">')
            for item in orders["items"]:
                main.append(f'<article class="order-card"><div class="order-number">Order {_e(item["id"])}</div>'
                            f'<p class="order-condition">When {_e(item["when"])},</p>'
                            f'<p class="order-action">{_e(item["do"])}.</p>'
                            f'<p class="order-reason">Because: {_e(item["because"])}</p></article>')
            main.append("</div>")
        else:
            main.append("<p><strong>Nothing signed.</strong> Every alert wakes the on-call person.</p>")
            if orders and not problems:
                main.append("<p>The signed file has no orders.</p>")
            if problems:
                main.append('<ul class="left-out-list">' + "".join(f"<li>{_e(p)}</li>" for p in problems) + "</ul>")

        ledger = ((doc or {}).get("watch") or {}).get("ledger") or []
        links = ((doc or {}).get("ports") or {}).get("links") or {}
        shown = [e for e in ledger if e.get("kind") in SHOWN_KINDS]
        main.append('<h3 class="section-title">Tonight so far</h3>')
        if shown:
            main.append('<div class="event-list">')
            for event in shown:
                at = datetime.fromisoformat(event["at"])
                incident = event.get("incident")
                ref = ""
                if incident is not None:
                    url = links.get(str(incident))
                    ref = (f' <a href="{_e(url)}">#{_e(incident)}</a>' if isinstance(url, str) and url.startswith("https://")
                           else " " + _link(project, f"/-/issues/{int(incident)}", f"#{incident}"))
                main.append(f'<div class="event-card"><span class="event-time">{_local(at, tz)}</span>'
                            f'<div class="event-body"><strong>{_e(KIND_WORDS.get(event["kind"], event["kind"]))}</strong>'
                            f"{ref}<p>{_e(event['text'])}</p></div></div>")
            main.append("</div>")
        else:
            main.append("<p>Nothing has happened yet tonight.</p>")
        for incident in ((doc or {}).get("watch") or {}).get("incidents") or []:
            if incident.get("suggest") and incident.get("paged_at") and not incident.get("closed"):
                until = datetime.fromisoformat(incident["paged_at"]) + timedelta(minutes=APPROVAL_WINDOW_MINUTES)
                main.append(f'<p class="inline-note">Incident #{_e(incident["number"])}: one suggestion is awaiting a '
                            f"thumbs-up from the on-call person until {_local(until, tz)}.</p>")

        watch_log = relay.get("watch_log")
        main.append('<h3 class="section-title">Last watch log</h3>')
        main.append(f'<pre class="proof-log">{_e(watch_log["text"])}</pre>' if watch_log
                    else "<p>Nothing has happened yet tonight.</p>")

        chores = []
        today = now.astimezone(tz).date().isoformat()
        if relay.get("daysheet") == today:
            chores.append(f"Day sheet posted on the watch issue for {_e(relay['daysheet'])}.")
        elif status.get("daysheet_at") and status.get("watch_issue") and not relay.get("daysheet_problem"):
            chores.append(f"Today's day sheet is due at {_e(status['daysheet_at'])}, before the dusk flow drafts the "
                          "orders." + (f" The last one was for {_e(relay['daysheet'])}." if relay.get("daysheet") else ""))
        elif relay.get("daysheet"):
            chores.append(f"Day sheet posted on the watch issue for {_e(relay['daysheet'])}.")
        sheet_problem = relay.get("daysheet_problem")
        if sheet_problem:
            sheet_day = sheet_problem.get("date")
            why = _e(sheet_problem.get("reason") or "")
            if sheet_day and sheet_day != today:
                chores.append(f"The day sheet for {_e(sheet_day)} was not posted ({why}).")
            else:
                chores.append(f"The day sheet could not be posted yet ({why}); the relay tries again every few "
                              "minutes until midnight.")
        rehearsed = relay.get("rehearsed") or {}
        if rehearsed:
            chores.append("Rehearsed on staging: " + ", ".join(
                _link(project, f"/-/merge_requests/{int(iid)}", f"!{iid}") for iid in sorted(rehearsed, key=int)) + ".")
        if relay.get("rehearsal_pending"):
            chores.append("A rehearsal stopped before it could put staging back; the relay restores it on the next ticks.")
        left = relay.get("rehearsal_left")
        if left:
            chores.append(f"Staging was left with {_e(left.get('what'))} after a rehearsal of !{_e(left.get('iid'))} "
                          f"and code could not put it back ({_e(left.get('reason'))}). It was {_e(left.get('before'))} "
                          "before; a person has to restore it.")
        if relay.get("rehearsal_problem"):
            chores.append("A rehearsal could not be finished; the relay tries again on the next ticks.")
        if chores:
            main.append('<h3 class="section-title">Dusk</h3><ul class="left-out-list">'
                        + "".join(f"<li>{line}</li>" for line in chores) + "</ul>")
        dawn = relay.get("dawn")
        if dawn:
            main.append('<h3 class="section-title">Morning countersign</h3>')
            if dawn.get("countersign_text"):
                main.append(f'<pre class="proof-log">{_e(dawn["countersign_text"])}</pre>')
            else:
                count = len(dawn.get("loose_ends") or [])
                main.append(f"<p>Waiting for the on-call person to keep or undo {count} change"
                            f"{'' if count == 1 else 's'} from the night of {_e(dawn['night'])}.</p>")
                if dawn.get("refused_text"):
                    main.append(f'<pre class="proof-log">{_e(dawn["refused_text"])}</pre>')
        kept_now, ended = relay.get("kept") or [], relay.get("kept_ended") or []
        if kept_now or ended:
            main.append('<h3 class="section-title">Kept from earlier nights</h3>')
            main.append('<p class="small-copy">Every kept change ends: when the merge request named at the countersign '
                        "is in production, code puts it back, in daytime, and says so on the watch issue.</p>")
            lines = [f"<li>{_e(kept.summary(item))}</li>" for item in kept_now]
            lines += [f"<li>{_e(datetime.fromisoformat(e['at']).astimezone(tz).strftime('%d %b %H:%M'))}: {_e(e['text'])}</li>" for e in ended[-3:]]
            main.append('<ul class="left-out-list">' + "".join(lines) + "</ul>")
            if relay.get("kept_problem"):
                main.append("<p>The kept list could not be checked last time; the relay tries again in a few "
                            "minutes.</p>")
        checked = datetime.fromisoformat(status["checked_at"])
        main.append(f'<p class="small-copy">Last check {_local(checked, tz)} ({_e(status["timezone"])}).</p>')
        if relay.get("error"):
            main.append('<p class="inline-error">The relay\'s latest check failed. It pages the on-call person if '
                        "failures continue.</p>")
    else:
        main.append('<div class="chapter-head"><h2 class="chapter-title">No check has run yet.</h2>'
                    '<p class="chapter-copy">Cloud Scheduler calls the relay once a minute. Until then, the demo '
                    "shows a whole night through the same code.</p></div>")
    main.append("</main>")

    watch_issue = status.get("watch_issue")
    proof = [
        ("Tonight's watch issue", f"/-/issues/{int(watch_issue)}" if watch_issue else None),
        ("Orders merge request", f"/-/merge_requests/{int(orders['merge_request'])}"
         if orders and orders.get("merge_request") else None),
        ("Flow sessions (AI, Sessions)", "/-/automate/agent-sessions"),
        ("Pipelines", "/-/pipelines"),
        ("Feature flags", "/-/feature_flags"),
        ("Incidents", "/-/incidents"),
    ]
    pending = ' <span class="small-copy">(link pending)</span>'
    rows = "".join("<li>" + (_link(project, path, name) if path else f"<span>{_e(name)}</span>")
                   + ("" if project and path else pending) + "</li>" for name, path in proof)
    aside = ['<aside class="context-panel" aria-label="Evidence">',
             chart(status.get("samples") or [], [e for e in ((doc or {}).get("watch") or {}).get("ledger") or []
                                                 if e.get("kind") in ("woke", "approved", "acted", "recovered")], tz),
             f'<div class="context-note"><p class="eyebrow">In GitLab</p><ul class="proof-links">{rows}</ul>'
             "<p>Every object the relay creates is a real GitLab object: incidents, notes, flag changes, merge "
             "requests.</p></div></aside>"]

    body.append('<div class="journey-layout">' + "".join(main) + "".join(aside) + "</div>")
    body.append('<footer class="footer-note">The agent suggests where to look. The code checks the permission. '
                "The on-call person decides what matters.</footer></div>")
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="theme-color" content="#f4f0e7">'
            '<meta name="description" content="Night Orders relay status: tonight\'s signed orders, the last hour, '
            'and what the night did.">'
            f'<title>Night Orders relay</title><link rel="icon" href="{FAVICON}">'
            '<link rel="stylesheet" href="/demo/assets/style.css"></head><body class="status-page">\n'
            + "\n".join(body) + "\n</body></html>\n")
