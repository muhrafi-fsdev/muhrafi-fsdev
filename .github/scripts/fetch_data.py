#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request

token = os.getenv("GITHUB_TOKEN", "")
headers = {"Accept": "application/vnd.github+json", "User-Agent": "muhrafi-profile-generator"}
if token:
    headers["Authorization"] = f"Bearer {token}"

def get_json(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

with open("projects.json", encoding="utf-8") as handle:
    projects = json.load(handle)

merged = []
for project in projects:
    item = dict(project)
    try:
        metadata = get_json(f"https://api.github.com/repos/{project['repo']}")
        languages = get_json(f"https://api.github.com/repos/{project['repo']}/languages")
        item.update({
            "stars": metadata.get("stargazers_count", 0),
            "forks": metadata.get("forks_count", 0),
            "pushed_at": metadata.get("pushed_at"),
            "languages": languages,
        })
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
        print(f"warning: {project['repo']}: {error}")
    merged.append(item)

with open("merged.json", "w", encoding="utf-8") as handle:
    json.dump(merged, handle, indent=2)
