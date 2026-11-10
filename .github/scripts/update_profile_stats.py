#!/usr/bin/env python3
"""Update the native Markdown repository-activity table in the profile README.

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

README = pathlib.Path("README.md")
START = "<!-- LIVE_REPOS_START -->"
END = "<!-- LIVE_REPOS_END -->"
OWNER = "muhrafi-fsdev"
REPOS = [
    ("NusaMind Swift", "NUSAMIND-SWIFT"),
    ("NusaMind Zenith", "NUSAMIND-ZENITH"),
    ("NusaMonitor", "NusaMonitor"),
    ("RYKA Core", "RYKA-CORE"),
    ("RayStore", "Raystore-topup"),
    ("Academic Organizer", "AcademicOrganizer"),
]


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


def render_table(metadata: list[tuple[str, str, dict]]) -> str:
    rows = [
        "| Repository | Primary language | Last push (UTC) | Stars |",
        "| :-- | :-- | :-- | --: |",
    ]
    for title, repo, data in metadata:
        timestamp = data["pushed_at"]
        date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError(f"Timezone missing for {repo}")
        day = date.astimezone(timezone.utc).strftime("%Y-%m-%d")
        lang = (data.get("language") or "Not specified").replace("|", "\\|")
        count = int(data["stargazers_count"])
        if count < 0:
            raise ValueError(f"Negative star count: {repo}")
        rows.append(
            f"| [{title}](https://github.com/{OWNER}/{repo}) "
            f"| {lang} | {day} | {count} |"
        )
    return "\n".join(rows)


def main() -> int:
    original = README.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise RuntimeError("README live-stat markers are missing or duplicated")
    # Collect every API response before touching README.
    metadata = [(title, repo, fetch_repo(repo)) for title, repo in REPOS]
    table = render_table(metadata)
    updated = re.sub(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        lambda _: START + "\n" + table + "\n" + END,
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
