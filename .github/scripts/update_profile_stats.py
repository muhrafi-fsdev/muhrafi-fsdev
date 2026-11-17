#!/usr/bin/env python3
"""Refresh the profile README’s linked project cards and public activity details.

Uses only official GitHub API responses. It never invents numbers or overwrites
unrelated sections, and exits without writing if API data is incomplete.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape
from itertools import islice

README = pathlib.Path("README.md")
START = "<!-- LIVE_REPOS_START -->"
END = "<!-- LIVE_REPOS_END -->"
OWNER = "muhrafi-fsdev"
REPOS = [
    ("NusaMind Zenith", "NUSAMIND-ZENITH", "zenith"),
    ("NusaMind Swift", "NUSAMIND-SWIFT", "swift"),
    ("NusaMonitor", "NusaMonitor", "monitor"),
    ("RYKA Core", "RYKA-CORE", "ryka"),
    ("RayStore", "Raystore-topup", "raystore"),
    ("Academic Organizer", "AcademicOrganizer", "academic"),
]
CARD_DIR = "assets/nightshift/profile-cards"


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
    if "pushed_at" not in data or "stargazers_count" not in data:
        raise ValueError(f"Incomplete metadata for {repo}")
    return data


def render_activity(metadata: list[tuple[str, str, str, dict]]) -> str:
    """Keep image layouts and links stable while replacing only public metadata."""
    projects = []
    for title, repo, card, data in metadata:
        timestamp = data["pushed_at"]
        date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError(f"Timezone missing for {repo}")
        lang = data.get("language") or "Not specified"
        count = int(data["stargazers_count"])
        if count < 0:
            raise ValueError(f"Negative star count for {repo}")
        projects.append((title, repo, card, date.astimezone(timezone.utc), lang, count))

    lead_title, lead_repo, _, latest, _, _ = max(projects, key=lambda row: row[3])
    parts = []
    cards = iter(projects)
    while group := list(islice(cards, 2)):
        parts.append('<p align="center">')
        for title, repo, card, date, lang, count in group:
            url = f"https://github.com/{OWNER}/{repo}"
            day = date.strftime("%Y-%m-%d")
            details = f"{lang} · Last push {day} UTC · {count} {'star' if count == 1 else 'stars'}"
            name = escape(title, quote=True)
            tooltip = escape(details, quote=True)
            prefix = f"{CARD_DIR}/repo-{card}"
            parts.extend([
                f'  <a href="{url}" title="{tooltip}"><picture>',
                f'    <source media="(prefers-color-scheme: light)" srcset="{prefix}-light.webp">',
                f'    <source media="(prefers-color-scheme: dark)" srcset="{prefix}-dark.webp">',
                f'    <img src="{prefix}-dark.webp" width="400" alt="{name} — {tooltip}">',
                '  </picture></a>',
            ])
        parts.extend(['</p>', ''])

    lead_url = f"https://github.com/{OWNER}/{lead_repo}"
    parts.extend([
        f'<sub><strong>Latest public push</strong> · <a href="{lead_url}">{escape(lead_title)}</a>'
        f' · {latest:%d %b %Y} (UTC)</sub>',
        '',
        '<details>',
        '<summary>Languages, push dates, and stars</summary>',
        '',
        "| Repository | Primary language | Last push (UTC) | Stars |",
        "| :-- | :-- | :-- | --: |",
    ])
    for title, repo, _, date, language, count in projects:
        # Only metadata that belongs to this fixed public repository list is rendered.
        md_lang = escape(" ".join(language.split())).replace("|", "&#124;")
        parts.append(
            f"| [{title}](https://github.com/{OWNER}/{repo}) "
            f"| {md_lang} | {date:%Y-%m-%d} | {count} |"
        )
    parts.extend(['', '</details>'])
    return "\n".join(parts)


def main() -> int:
    original = README.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise RuntimeError("README live-stat markers are missing or duplicated")
    # Collect every API response before touching README.
    metadata = [(title, repo, card, fetch_repo(repo)) for title, repo, card in REPOS]
    activity = render_activity(metadata)
    updated = re.sub(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        lambda _: START + "\n" + activity + "\n" + END,
        original,
        count=1,
    )
    if updated != original:
        README.write_text(updated, encoding="utf-8")
        print("Updated six public repository entries from GitHub API")
    else:
        print("Profile stats already current")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"Profile update aborted safely: {err}", file=sys.stderr)
        sys.exit(1)
