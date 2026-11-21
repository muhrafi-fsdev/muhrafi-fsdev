#!/usr/bin/env python3
"""Refresh the profile README’s public repository activity table.

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

README = pathlib.Path("README.md")
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


def _clean_cell(text: str) -> str:
    return escape(" ".join(text.split())).replace("|", "&#124;")


def render_activity(metadata: list[tuple[str, str, str, dict]]) -> str:
    """Render scannable Markdown rows sorted by most recent public push."""
    projects = []
    for title, repo, fallback_desc, data in metadata:
        timestamp = data["pushed_at"]
        date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError(f"Timezone missing for {repo}")
        lang = data.get("language") or "Not specified"
        desc = PROFILE_SUMMARIES.get(repo) or (data.get("description") or "").strip() or fallback_desc
        projects.append((title, repo, desc, date.astimezone(timezone.utc), lang))

    projects.sort(key=lambda row: row[3], reverse=True)
    lead_title, lead_repo, _, latest, _ = projects[0]
    lead_url = f"https://github.com/{OWNER}/{lead_repo}"

    parts = [
        f'**Latest push** · [{lead_title}]({lead_url}) · {latest:%d %b %Y} (UTC)',
        "",
        "| Repository | Last push (UTC) |",
        "| :-- | --: |",
    ]
    for title, repo, desc, date, language in projects:
        display_date = date.strftime("%d %b %Y").replace(" ", "&nbsp;")
        parts.append(
            f"| **[{title}](https://github.com/{OWNER}/{repo})**"
            f"<br><sub>{_clean_cell(desc)} · {_clean_cell(language)}</sub> | {display_date} |"
        )
    return "\n".join(parts)


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

    activity = render_activity(metadata)
    if args.dry_run:
        print(activity)
        return 0

    updated = re.sub(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        lambda _: START + "\n" + activity + "\n" + END,
        original,
        count=1,
    )
    if updated != original:
        README.write_text(updated, encoding="utf-8")
        print("Updated public repository activity table")
    else:
        print("Profile stats already current")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, urllib.error.URLError, json.JSONDecodeError, KeyError) as err:
        print(f"Profile update aborted safely: {err}", file=sys.stderr)
        sys.exit(1)

