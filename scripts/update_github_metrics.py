import os
import requests
from datetime import datetime, timezone

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GH_TOKEN"]

now = datetime.now(timezone.utc)
year_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)

query = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
    }
  }
}
"""

variables = {
    "username": USERNAME,
    "from": year_start.isoformat(),
    "to": now.isoformat(),
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": variables},
    headers={"Authorization": f"Bearer {TOKEN}"},
    timeout=30,
)

response.raise_for_status()
data = response.json()

if "errors" in data:
    raise RuntimeError(data["errors"])

collection = data["data"]["user"]["contributionsCollection"]

total = collection["contributionCalendar"]["totalContributions"]
commits = collection["totalCommitContributions"]
issues = collection["totalIssueContributions"]
prs = collection["totalPullRequestContributions"]
reviews = collection["totalPullRequestReviewContributions"]
repos = collection["totalRepositoryContributions"]

generated = f"""<!-- GITHUB-METRICS:START -->
| Métrica | Valor |
|---|---:|
| Contribuciones en {now.year} | {total} |
| Commits | {commits} |
| Pull Requests | {prs} |
| Issues | {issues} |
| Reviews de código | {reviews} |
| Repositorios creados | {repos} |

<sub>Datos generados automáticamente desde la API oficial de GitHub.</sub>
<!-- GITHUB-METRICS:END -->"""

with open("README.md", "r", encoding="utf-8") as file:
    readme = file.read()

start = "<!-- GITHUB-METRICS:START -->"
end = "<!-- GITHUB-METRICS:END -->"

if start not in readme or end not in readme:
    raise RuntimeError("No se encontraron los marcadores GITHUB-METRICS en README.md")

before = readme.split(start)[0]
after = readme.split(end)[1]

new_readme = before + generated + after

with open("README.md", "w", encoding="utf-8") as file:
    file.write(new_readme)
