#!/usr/bin/env python3
"""Refresh the profile README’s public repository activity and linked cards.

Uses only official GitHub API responses (or a local fixture file when
`--fixture` is passed for testing). Never invents numbers or overwrites
unrelated sections, and exits without writing if API data is incomplete.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape
from textwrap import shorten

README = pathlib.Path("README.md")
CARD_DIR = pathlib.Path("assets/city-window/activity")
START = "<!-- LIVE_REPOS_START -->"
END = "<!-- LIVE_REPOS_END -->"
OWNER = "muhrafi-fsdev"
REPOS = [
    ("YouTube Ambient Glass", "YouTube-Ambient", "Video-powered ambience for YouTube"),
    ("KillerTab", "KillerTab", "Tab sleep, ad blocking, and suspicious link checks"),
    ("NusaMind Zenith", "NUSAMIND-ZENITH", "Local-first AI workspace for multi-file projects"),
    ("NusaMind Swift", "NUSAMIND-SWIFT", "Local AI assistant with retrieval and memory"),
    ("NusaMonitor", "NusaMonitor", "Live public data mapping dashboard for Indonesia"),
    ("RYKA Core", "RYKA-CORE", "Accessible gesture control and desktop interaction platform"),
    ("RayStore", "Raystore-topup", "Game top-up storefront prototype"),
    ("Academic Organizer", "AcademicOrganizer", "Student tasks, schedules, and academic planning"),
]
PROFILE_SUMMARIES = {
    "NUSAMIND-SWIFT": "Local AI assistant with retrieval and memory",
    "Raystore-topup": "Game top-up storefront prototype",
    "RYKA-CORE": "Gesture controls for accessible desktop interaction",
}
LANGUAGE_COLORS = {
    "CSS": "#b59aee",
    "HTML": "#ff9e82",
    "JavaScript": "#f3d584",
    "TypeScript": "#90c8fa",
}


def fetch_repo(repo: str) -> dict:
    url = f"https://api.github.com/repos/{OWNER}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "muhrafi-fsdev-profile-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)
    if data.get("full_name", "").lower() != f"{OWNER}/{repo}".lower():
        raise ValueError(f"Unexpected repository metadata for {repo}")
    if data.get("private"):
        raise ValueError(f"Refusing private repository data: {repo}")
    if "pushed_at" not in data:
        raise ValueError(f"Incomplete metadata for {repo}")
    return data


def render_card(title: str, desc: str, language: str, date: str, *, latest: bool, compact: bool) -> str:
    """Lay out the same repository metadata for wide and narrow displays."""
    width, height = (440, 85) if compact else (820, 66)
    inset = 20 if compact else 25
    title_y, desc_y, meta_y = (26, 49, 72) if compact else (26, 48, 40)
    language_x = inset + 12 if compact else width - 287
    color = LANGUAGE_COLORS.get(language, "#a7becf")
    fill = "#14273b" if latest else "#111d2d"
    border = "#5986ac" if latest else "#405773"
    max_desc = 50 if compact else 58
    short_desc = shorten(desc, width=max_desc, placeholder="…")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="10" fill="{fill}" stroke="{border}"/>
  <path d="M8 {title_y-13}v14" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  <g font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">
    <text x="{inset}" y="{title_y}" font-size="20" font-weight="650" fill="#edf5ff">{escape(title)}</text>
    <text x="{inset}" y="{desc_y}" font-size="15" fill="#c1d2e6">{escape(short_desc)}</text>
    <circle cx="{language_x-10}" cy="{meta_y-4.5}" r="3.5" fill="{color}"/>
    <text x="{language_x}" y="{meta_y}" font-size="14" fill="#c6d5e8">{escape(language)}</text>
    <text x="{width-34}" y="{meta_y}" text-anchor="end" font-size="14" font-family="ui-monospace,Consolas,monospace" fill="#d5e4f4">{date}</text>
    <path d="M{width-23} {meta_y-9}h9m-4-4 4 4-4 4" fill="none" stroke="#8dc5e9" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
"""


def render_activity(metadata: list[tuple[str, str, str, dict]]) -> tuple[str, dict[pathlib.Path, str]]:
    """Render linked cards sorted by most recent public push."""
    projects = []
    for title, repo, fallback_desc, data in metadata:
        timestamp = data["pushed_at"]
        date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError(f"Timezone missing for {repo}")
        lang = data.get("language") or "Not specified"
        desc = PROFILE_SUMMARIES.get(repo) or data.get("description") or fallback_desc
        desc = " ".join(desc.split()) or fallback_desc
        projects.append((title, repo, desc, date.astimezone(timezone.utc), lang))

    projects.sort(key=lambda row: row[3], reverse=True)
    lead_title, lead_repo, _, latest, _ = projects[0]
    lead_url = f"https://github.com/{OWNER}/{lead_repo}"

    lead = f"**Latest push** · [{lead_title}]({lead_url}) · {latest:%d %b %Y} (UTC)"
    parts = []
    cards = {}
    for index, (title, repo, desc, date, language) in enumerate(projects):
        name = repo.lower()
        wide = CARD_DIR / f"{name}.svg"
        narrow = CARD_DIR / f"{name}-compact.svg"
        formatted = f"{date:%d %b %Y}"
        alt = escape(f"{title} — {desc}. {language}. Last push {formatted} (UTC).")
        cards[wide] = render_card(title, desc, language, formatted, latest=index == 0, compact=False)
        cards[narrow] = render_card(title, desc, language, formatted, latest=index == 0, compact=True)
        parts.append(
            f'  <a href="https://github.com/{OWNER}/{repo}"><picture>\n'
            f'    <source media="(max-width: 600px)" srcset="{narrow.as_posix()}">\n'
            f'    <img width="820" src="{wide.as_posix()}" alt="{alt}">\n'
            f'  </picture></a>'
        )
    card_links = "<br>\n".join(parts)
    return f"{lead}\n\n<p>\n{card_links}\n</p>", cards


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=pathlib.Path, help="Read repo metadata map from JSON fixture instead of GitHub API")
    parser.add_argument("--dry-run", action="store_true", help="Print rendered output without modifying README.md")
    args = parser.parse_args(argv)

    original = README.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise RuntimeError("README live-stat markers are missing or duplicated")

    if args.fixture:
        fixture_data = json.loads(args.fixture.read_text(encoding="utf-8"))
        metadata = [(title, repo, fallback, fixture_data[repo]) for title, repo, fallback in REPOS]
    else:
        metadata = [(title, repo, fallback, fetch_repo(repo)) for title, repo, fallback in REPOS]

    activity, cards = render_activity(metadata)
    if args.dry_run:
        print(activity)
        return 0

    updated = re.sub(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        lambda _: START + "\n" + activity + "\n" + END,
        original,
        count=1,
    )
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    changed = updated != original
    for path, card in cards.items():
        if not path.exists() or path.read_text(encoding="utf-8") != card:
            path.write_text(card, encoding="utf-8")
            changed = True
    if updated != original:
        README.write_text(updated, encoding="utf-8")
    print("Updated public repository cards" if changed else "Profile stats already current")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, urllib.error.URLError, json.JSONDecodeError, KeyError) as err:
        print(f"Profile update aborted safely: {err}", file=sys.stderr)
        sys.exit(1)
