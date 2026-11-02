import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USERNAME = os.environ.get("GITHUB_USERNAME", "pradeep23234545")
TOKEN = os.environ.get("GITHUB_TOKEN")
README_PATH = "README.md"
START = "<!-- AUTO-PROJECTS:START -->"
END = "<!-- AUTO-PROJECTS:END -->"

# Use Python's standard library so no pip dependencies are required.
query = urlencode({
    "per_page": 100,
    "sort": "updated",
    "direction": "desc",
    "type": "owner",
})
api_url = f"https://api.github.com/users/{USERNAME}/repos?{query}"

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "profile-readme-project-updater",
}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

request = Request(api_url, headers=headers)
try:
    with urlopen(request, timeout=30) as response:
        repos = json.loads(response.read().decode("utf-8"))
except (HTTPError, URLError, TimeoutError) as error:
    raise SystemExit(f"GitHub API request failed: {error}") from error

if not isinstance(repos, list):
    raise SystemExit("GitHub API returned an unexpected response.")

# Keep genuine public projects owned by this account.
repos = [
    repo for repo in repos
    if not repo.get("private")
    and not repo.get("fork")
    and not repo.get("archived")
    and repo.get("name", "").lower() != USERNAME.lower()
]

# Most recently updated repositories appear first.
repos.sort(
    key=lambda repo: repo.get("pushed_at") or repo.get("updated_at") or "",
    reverse=True,
)
repos = repos[:8]

lines = ["### ⭐ Recent public projects", ""]
if not repos:
    lines.append("_New public projects will appear here as they are published._")
else:
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        description = (
            repo.get("description")
            or "A public project from my GitHub portfolio."
        ).replace("\n", " ").strip()

        language = repo.get("language")
        topics = repo.get("topics") or []
        tech = [language] if language else []
        tech.extend(
            topic.replace("-", " ").title()
            for topic in topics[:4]
            if topic.lower() != (language or "").lower()
        )
        tech_text = (
            " · ".join(tech[:5])
            if tech
            else "Explore the repository for details"
        )

        lines.extend([
            f"- **[{name}]({url})** — {description}",
            f"  <sub>{tech_text}</sub>",
            "",
        ])

new_section = START + "\n" + "\n".join(lines).rstrip() + "\n" + END

with open(README_PATH, "r", encoding="utf-8") as file:
    readme = file.read()

pattern = re.compile(
    re.escape(START) + r".*?" + re.escape(END),
    re.DOTALL,
)
updated, count = pattern.subn(lambda _: new_section, readme, count=1)

if count != 1:
    raise SystemExit(
        "Could not find the AUTO-PROJECTS markers in README.md."
    )

with open(README_PATH, "w", encoding="utf-8") as file:
    file.write(updated)

print(
    f"Successfully refreshed the profile project list "
    f"with {len(repos)} public repositories."
)
