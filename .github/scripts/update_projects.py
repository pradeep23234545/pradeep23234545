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

# Hand-written summaries and stacks. Repositories not listed here fall back to
# their GitHub description, language and topics, so new projects still appear.
PROJECT_DETAILS = {
    "Emergency-Response-System": {
        "description": "AI-powered predictive emergency corridor for SIH 2026: predictive routing, green-wave traffic signals, multi-vehicle priority and live hospital ETA alerts.",
        "tech": ["TypeScript", "React", "Node.js", "Express", "SQLite"],
    },
    "Smart-Inbox-to-Calendar-Assistant": {
        "description": "Autonomous Gmail agent that finds time-bound commitments in email (meetings, exams, due dates) and adds them to Google Calendar with smart reminders.",
        "tech": ["Python", "Machine Learning", "Gmail API", "Google Calendar API"],
    },
    "Steam-Game-Discovery-System": {
        "tech": ["Python", "Streamlit", "Recommendation System", "Data Analytics"],
    },
    "portfolio-from-resume": {
        "tech": ["TypeScript", "AI", "Web App"],
    },
    "retail-demand-forecasting": {
        "tech": ["Python", "Machine Learning", "Streamlit", "Jupyter"],
    },
    "tern-search": {
        "tech": ["JavaScript", "SearXNG", "Docker", "Valkey"],
    },
    "AI-Research-Agent": {
        "description": "Autonomous deep-research agent that searches the live web, reasons with the ReAct pattern and writes source-cited Markdown reports.",
        "tech": ["Python", "Groq LLM", "DuckDuckGo Search", "ReAct Agent"],
    },
    "pradeep23234545.github.io": {
        "tech": ["JavaScript", "HTML", "CSS", "GitHub Pages"],
    },
    "restaurant-ecommerce-platform": {
        "description": "The Zaika Loft: responsive restaurant website with a categorised menu, shopping cart, order total and Cash on Delivery / UPI checkout options.",
        "tech": ["HTML", "CSS", "JavaScript"],
    },
}

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

lines = [
    f"### ⭐ All public projects ({len(repos)})",
    "",
    "_Newest first. This list updates itself when I publish a new repository._",
    "",
]
if not repos:
    lines.append("_New public projects will appear here as they are published._")
else:
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        extra = PROJECT_DETAILS.get(name, {})
        description = (
            extra.get("description")
            or repo.get("description")
            or "A public project from my GitHub portfolio."
        ).replace("\n", " ").strip()

        tech = extra.get("tech")
        if not tech:
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

        homepage = (repo.get("homepage") or "").strip()
        if not homepage and repo.get("has_pages"):
            homepage = f"https://{USERNAME}.github.io/{name}/"
        if name.lower() == f"{USERNAME}.github.io".lower():
            homepage = f"https://{USERNAME}.github.io/"
        demo = f" · [Live demo]({homepage})" if homepage else ""

        lines.extend([
            f"- **[{name}]({url})**{demo} — {description}",
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
