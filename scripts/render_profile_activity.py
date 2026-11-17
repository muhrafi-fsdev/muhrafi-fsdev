#!/usr/bin/env python3
"""Render a dated 12-week snapshot from GitHub's public contribution calendar.

Run from anywhere with Python 3.10+:
    python3 scripts/render_profile_activity.py
An optional first argument is a copy of the public GitHub calendar HTML.
"""
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

SOURCE = "https://github.com/users/muhrafi-fsdev/contributions"
OUT = Path(__file__).resolve().parents[1] / "assets" / "nightshift"
THEMES = {
    "dark": ("#101827", "#1f2b3e", "#8c9db7", "#e6eefb", "#75caff", "#17283d"),
    "light": ("#f2f6fc", "#d9e4f1", "#4d6585", "#14233c", "#136592", "#e3eff9"),
}
COUNT = re.compile(r"(No|[0-9,]+) contributions? on ", re.ASCII)


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.labels = {}
        self.tip = None

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "td" and {"data-date", "id"} <= fields.keys():
            self.days[fields["id"]] = date.fromisoformat(fields["data-date"])
        if tag == "tool-tip":
            self.tip = fields.get("for")

    def handle_data(self, data):
        if self.tip and (match := COUNT.match(data.strip())):
            raw = match[1]
            self.labels[self.tip] = 0 if raw == "No" else int(raw.replace(",", ""))

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tip = None

    def last_twelve_weeks(self):
        by_date = {day: self.labels[key] for key, day in self.days.items() if key in self.labels}
        if not by_date:
            raise ValueError("Could not read exact counts from GitHub's public calendar")
        end = max(by_date)
        span = [end - timedelta(days=83 - i) for i in range(84)]
        if not all(day in by_date for day in span):
            raise ValueError("Public calendar response is missing dates in the last 12 weeks")
        return span[0], end, [by_date[day] for day in span]


def render(start: date, end: date, days: list[int], theme: str) -> str:
    bg, grid, dim, ink, accent, area = THEMES[theme]
    weekly = [sum(days[i:i + 7]) for i in range(0, 84, 7)]
    scale = max(4, ((max(weekly) + 3) // 4) * 4)
    top, bottom, x0, x1 = 162, 254, 68, 844
    points = [(round(x0 + (x1 - x0) * i / 11, 2), round(bottom - value / scale * (bottom - top), 2))
              for i, value in enumerate(weekly)]
    path = " ".join(f"{x},{y}" for x, y in points)
    marks = " / ".join(map(str, weekly))
    date_range = f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}"
    chunks = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="880" height="292" viewBox="0 0 880 292" role="img" aria-labelledby="title desc">
<title id="title">Public contribution activity</title>
<desc id="desc">GitHub public calendar snapshot from {escape(date_range)}. Contributions by week, oldest first: {marks}.</desc>
<rect x=".5" y=".5" width="879" height="291" rx="13" fill="{bg}" stroke="{grid}"/>
<g font-family="system-ui,Segoe UI,Arial,sans-serif">
<text x="30" y="38" fill="{ink}" font-size="22" font-weight="700">Public contribution activity</text>
<text x="850" y="38" text-anchor="end" fill="{dim}" font-size="15">{escape(date_range)}</text>
<path d="M30 55H850 M30 128H850 M303 69V114 M576 69V114" stroke="{grid}"/>
''']
    for x, label, val in ((30, "CONTRIBUTIONS", sum(days)), (331, "ACTIVE DAYS", sum(n > 0 for n in days)),
                          (605, "BEST DAY", max(days))):
        chunks.append(f'<text x="{x}" y="79" fill="{dim}" font-size="13" letter-spacing="1.2">{label}</text>'
                      f'<text x="{x}" y="111" fill="{ink}" font-size="26" font-weight="700">{val:,}</text>')
    chunks.append(f'<polygon points="{x0},{bottom} {path} {x1},{bottom}" fill="{area}"/>')
    for n in range(5):
        y = bottom - n * (bottom - top) / 4
        chunks.append(f'<path d="M{x0} {y}H{x1}" stroke="{grid}"/>'
                      f'<text x="55" y="{y+4}" text-anchor="end" fill="{dim}" font-size="12">{n * scale // 4}</text>')
    chunks.append(f'<polyline points="{path}" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
    for x, y in points:
        chunks.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{bg}" stroke="{accent}" stroke-width="1.7"/>')
    chunks.append(f'<text x="{x0}" y="278" fill="{dim}" font-size="12">Week of {start.strftime("%d %b")}</text>'
                  f'<text x="{x1}" y="278" text-anchor="end" fill="{dim}" font-size="12">Week ending {end.strftime("%d %b")}</text>'
                  '</g>\n</svg>\n')
    return "\n".join(chunks)


def main():
    source_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if source_file:
        body = source_file.read_text(encoding="utf-8")
    else:
        request = Request(SOURCE, headers={"User-Agent": "muhrafi-fsdev profile calendar"})
        with urlopen(request, timeout=15) as response:
            body = response.read(4_000_000).decode("utf-8")
    calendar = Calendar()
    calendar.feed(body)
    start, end, counts = calendar.last_twelve_weeks()
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        dest = OUT / f"activity-{theme}.svg"
        dest.write_text(render(start, end, counts, theme), encoding="utf-8")
    print(f"{start}–{end}: {sum(counts)} contributions across {sum(n > 0 for n in counts)} active days")


if __name__ == "__main__":
    main()
