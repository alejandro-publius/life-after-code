"""E8 and E12 from the review: the status page draws the night chart the way the browser demo does
(relay/demo_web/app.js, metricChart). Offline.

The badges are as large as the demo's (r=16, centre at top + 16 + lift * 32, the number 8 below the centre), and the
"5% limit" label is drawn after the lines, so a line near 7.9 percent cannot cover it. Every number is test data.
"""

from __future__ import annotations

import xml.etree.ElementTree as ElementTree
from datetime import timedelta, timezone

from nightorders import status_page
from test_relay_app import ONCALL, local

TOP = 18  # the chart's top margin, as in app.js


def svg_of(samples: list[dict], events: list[dict]) -> ElementTree.Element:
    html = status_page.chart(samples, events, ONCALL.timezone)
    start, end = html.index("<svg"), html.index("</svg>") + len("</svg>")
    return ElementTree.fromstring(html[start:end])


def an_hour(new_rate: float = 0.079) -> list[dict]:
    start = local("03:00")
    return [{"at": (start + timedelta(minutes=i)).astimezone(timezone.utc).isoformat(timespec="minutes"),
             "old": 0.003, "new": new_rate, "all": 0.04, "checkouts": 60} for i in range(60)]


def test_the_marker_badges_are_the_demos_size_and_place():
    events = [{"at": local("03:10").isoformat(), "kind": "woke"},
              {"at": local("03:13").isoformat(), "kind": "acted"},     # 3 minutes on: 26.5 px, closer than a badge
              {"at": local("03:40").isoformat(), "kind": "recovered"}]  # far away: back on the first row
    svg = svg_of(an_hour(), events)
    badges = svg.findall("circle")
    numbers = [t for t in svg.findall("text") if t.get("class") == "marker-number"]
    assert [b.get("r") for b in badges] == ["16", "16", "16"]
    assert [float(b.get("cy")) for b in badges] == [TOP + 16, TOP + 16 + 32, TOP + 16]
    assert [float(n.get("y")) for n in numbers] == [TOP + 16 + 8, TOP + 16 + 32 + 8, TOP + 16 + 8]
    assert [n.text for n in numbers] == ["1", "2", "3"]


def test_the_limit_label_is_drawn_after_the_lines_so_no_line_covers_it():
    svg = svg_of(an_hour(0.079), [{"at": local("03:13").isoformat(), "kind": "acted"}])
    drawn = list(svg)
    label = next(i for i, e in enumerate(drawn) if e.tag == "text" and e.text == "5% limit")
    line = next(i for i, e in enumerate(drawn) if e.get("class") == "chart-threshold")
    paths = [i for i, e in enumerate(drawn) if e.tag == "path"]
    badge = next(i for i, e in enumerate(drawn) if e.tag == "circle")
    assert line < min(paths) and max(paths) < label < badge  # the dashed line under the data, its words over it
    assert "limit-label" in drawn[label].get("class")  # the stylesheet gives this class its halo
