"""The shop page (GET /): a plain status page for the demo shop. Inline HTML and CSS, no external files."""

from __future__ import annotations

from datetime import datetime
from html import escape

from demo_catalog import CATALOG, REGIONS
from demo_traffic import LABEL as TRAFFIC_LABEL
from demo_traffic import PER_MINUTE, TrafficLoop
from faults import FAULTS, LABEL, Faults
from flags import FlagClient
from metrics import Minute

BANNER = "DEMO SHOP: simulated customers and planted faults"

STYLE = """
:root { color-scheme: light dark; --bg: #f7f6f1; --fg: #1d201c; --muted: #5c6159; --card: #ffffff;
  --line: #dcd9cf; --banner: #f2c230; --banner-fg: #1d201c; --on: #1f6f3a; --on-bg: #dcefe1;
  --off: #5c6159; --off-bg: #ebe9e2; --bad: #9f1d14; --bad-bg: #fbe1dd; }
@media (prefers-color-scheme: dark) { :root { --bg: #141713; --fg: #e9eae4; --muted: #a3a99f;
  --card: #1d211c; --line: #343a32; --banner: #f2c230; --banner-fg: #141713; --on: #8fd3a3;
  --on-bg: #1d3a26; --off: #a3a99f; --off-bg: #2a2f28; --bad: #ff9b8f; --bad-bg: #4a1f1a; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.banner { background: var(--banner); color: var(--banner-fg); font-weight: 800; text-align: center;
  font-size: clamp(1.05rem, 3.6vw, 1.6rem); padding: 14px 16px; letter-spacing: 0.02em; }
main { max-width: 980px; margin: 0 auto; padding: 8px 16px 32px; }
h1 { margin: 16px 0 4px; font-size: 1.8rem; }
h2 { margin: 0 0 8px; font-size: 1.1rem; }
p { margin: 4px 0 8px; }
.muted { color: var(--muted); }
section { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px;
  margin: 14px 0; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 6px 10px 6px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: 0.85rem; color: var(--muted); font-weight: 600; white-space: nowrap; }
td.num, th.num { text-align: right; }
.pill { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 0.85rem; font-weight: 600;
  white-space: nowrap; }
.on { color: var(--on); background: var(--on-bg); }
.off { color: var(--off); background: var(--off-bg); }
.bad { color: var(--bad); background: var(--bad-bg); }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.9em; }
footer { color: var(--muted); font-size: 0.9rem; margin-top: 18px; }
@media (max-width: 600px) { table { font-size: 0.85rem; } th, td { padding-right: 6px; } }
"""


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _ago(then: datetime | None, now: datetime) -> str:
    if then is None:
        return "never"
    seconds = max(0, int((now - then).total_seconds()))
    return f"{seconds} s ago" if seconds < 120 else f"{seconds // 60} min ago"


def _flags(flags: FlagClient, now: datetime) -> str:
    rows = []
    for name in flags.names():
        summary = flags.summary(name)
        css = "off" if summary.startswith("off") else "on"
        rows.append(f"<tr><td><code>{escape(name)}</code></td><td><span class='pill {css}'>{escape(summary)}</span>"
                    f"<br><span class='muted'>{escape(flags.source(name))}</span></td></tr>")
    if not flags.configured:
        note = ("No flag service is set (UNLEASH_URL and UNLEASH_INSTANCE_ID), so every flag is off unless "
                "FLAGS_OVERRIDE sets it.")
    elif flags.last_error:
        note = (f"GitLab did not answer the last time ({flags.last_error}). The shop keeps the last known values "
                f"(last good answer: {_ago(flags.fetched_at, now)}).")
    else:
        note = (f"Read from GitLab feature flags for the {flags.environment} environment every 15 seconds "
                f"(last good answer: {_ago(flags.fetched_at, now)}).")
    return ("<section><h2>Feature flags</h2><div class='scroll'><table><tr><th>Flag</th><th>State and source</th>"
            f"</tr>{''.join(rows)}</table></div><p class='muted'>{escape(note)}</p></section>")


def _faults(faults: Faults) -> str:
    rows = []
    for name, what in FAULTS.items():
        state = "<span class='pill bad'>on</span>" if faults.on(name) else "<span class='pill off'>off</span>"
        rows.append(f"<tr><td><code>{escape(name)}</code><br><span class='muted'>{LABEL}</span></td>"
                    f"<td>{state}</td><td>{escape(what)}</td></tr>")
    active = ", ".join(faults.active()) or "none"
    return (f"<section><h2>Planted demo faults (active: {escape(active)})</h2><div class='scroll'><table>"
            f"<tr><th>Fault</th><th>State</th><th>What it does</th></tr>{''.join(rows)}</table></div>"
            "<p class='muted'>Switched on purpose for the demo night with <code>POST /demo/faults</code> "
            "(needs DEMO_KEY) or the FAULTS env var.</p></section>")


def _traffic(traffic: TrafficLoop) -> str:
    if traffic.running and traffic.until is not None:
        text = (f"Running until {traffic.until:%H:%M} UTC: {traffic.checkouts} checkouts sent, "
                f"{traffic.failed} failed, {traffic.views} product views.")
    else:
        text = (f"Not running. <code>POST /demo/traffic?minutes=N</code> (needs DEMO_KEY, N up to 30) sends "
                f"about {PER_MINUTE} simulated checkouts a minute.")
    return f"<section><h2>Demo traffic</h2><p><span class='pill off'>{TRAFFIC_LABEL}</span> {text}</p></section>"


def _minutes(minutes: list[tuple[datetime, Minute]], started: datetime) -> str:
    if not minutes:
        return ("<section><h2>Last 10 minutes</h2><p class='muted'>No complete minute yet. The counters started at "
                f"{started:%H:%M} UTC.</p></section>")
    head = ("<tr><th>Minute (UTC)</th><th class='num'>Checkouts old / new</th><th class='num'>Errors old</th>"
            "<th class='num'>Errors new</th><th class='num'>Errors all</th><th class='num'>HTTP 5xx</th>"
            "<th class='num'>p95 ms</th><th class='num'>Payment errors</th></tr>")
    rows = []
    for at, bucket in reversed(minutes):
        s = bucket.signals()
        rows.append(
            f"<tr><td>{at:%H:%M}</td><td class='num'>{bucket.checkouts['old']} / {bucket.checkouts['new']}</td>"
            f"<td class='num'>{_pct(s['checkout_error_rate.old'])}</td>"
            f"<td class='num'>{_pct(s['checkout_error_rate.new'])}</td>"
            f"<td class='num'>{_pct(s['checkout_error_rate.all'])}</td>"
            f"<td class='num'>{_pct(s['http_5xx_ratio'])}</td>"
            f"<td class='num'>{s['p95_latency_ms']:,.0f}</td>"
            f"<td class='num'>{_pct(s['payment_error_rate'])}</td></tr>")
    return ("<section><h2>Last 10 minutes</h2><div class='scroll'><table>"
            f"{head}{''.join(rows)}</table></div><p class='muted'>Newest first. The relay reads the last 60 "
            "complete minutes from <code>/metrics.json</code>.</p></section>")


def _catalog() -> str:
    items = "".join(f"<tr><td>{escape(p.name)}</td><td><code>{escape(p.sku)}</code></td>"
                    f"<td class='num'>{p.price:.2f}</td></tr>" for p in CATALOG.values())
    regions = ", ".join(f"{name} ({r.currency} at {r.rate})" for name, r in REGIONS.items())
    return ("<section><h2>Catalog (demo products, USD list prices)</h2><div class='scroll'><table>"
            f"<tr><th>Product</th><th>SKU</th><th class='num'>USD</th></tr>{items}</table></div>"
            f"<p class='muted'>Regions: {escape(regions)}. Checkout is an API: <code>POST /checkout</code> with "
            "a user, a region and items with prices.</p></section>")


def render(*, environment: str, commit: str, flags: FlagClient, faults: Faults, traffic: TrafficLoop,
           minutes: list[tuple[datetime, Minute]], started: datetime, now: datetime) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="15">
<title>Juniper Market (demo shop)</title>
<style>{STYLE}</style>
</head>
<body>
<div class="banner" role="banner">{BANNER}</div>
<main>
<h1>Juniper Market</h1>
<p class="muted">The demo shop that Night Orders protects. Customers, orders, traffic and faults are simulated
(demo data). Nothing is charged or shipped.</p>
{_flags(flags, now)}
{_faults(faults)}
{_traffic(traffic)}
{_minutes(minutes, started)}
{_catalog()}
<footer>Environment <code>{escape(environment)}</code> (APP_ENV), commit <code>{escape(commit)}</code>.
Endpoints: <code>GET /products</code>, <code>POST /checkout</code>, <code>GET /metrics.json</code>,
<code>POST /demo/faults</code>, <code>POST /demo/traffic</code>, <code>GET /healthz</code>.
This page refreshes every 15 seconds.</footer>
</main>
</body>
</html>
"""
