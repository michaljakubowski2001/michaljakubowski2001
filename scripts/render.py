"""Render the profile's SVG assets from profile.json and live GitHub data.

Uses only the standard library. Reads GITHUB_TOKEN (or GH_TOKEN) for the API;
without a token the live numbers fall back to the public REST API and the
contribution count is left out.

Output is deterministic for the same data, so the scheduled workflow only
commits when something on the profile actually changed.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROFILE = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))

WIDTH = 860
FONT = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"
CHAR = 0.6  # monospace advance width as a fraction of the font size

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#3fb950"
BLUE = "#58a6ff"
PURPLE = "#d2a8ff"
ORANGE = "#ffa657"

REDUCED_MOTION = (
    "@media (prefers-reduced-motion: reduce) {"
    " * { animation: none !important; } }"
)


# --------------------------------------------------------------------------- data


def _token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _request(url: str, body: dict | None = None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-render"}
    if token := _token():
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=30) as response:
        return json.load(response)


def fetch_live() -> dict:
    user = PROFILE["user"]
    repos = [
        repo
        for repo in _request(f"https://api.github.com/users/{user}/repos?type=owner&per_page=100")
        if not repo["fork"] and not repo["private"] and repo["name"] != user
    ]
    languages: dict[str, int] = {}
    workflows = 0
    details = {}
    for repo in repos:
        for name, size in _request(repo["languages_url"]).items():
            languages[name] = languages.get(name, 0) + size
        workflows += _request(f"{repo['url']}/actions/workflows")["total_count"]
        details[repo["name"]] = {"topics": repo.get("topics", [])}

    contributions = None
    if _token():
        query = "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions}}}}"
        result = _request("https://api.github.com/graphql", {"query": query, "variables": {"login": user}})
        contributions = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    top = sorted(languages, key=languages.get, reverse=True)[:4]
    return {
        "repos": len(repos),
        "workflows": workflows,
        "contributions": contributions,
        "languages": top,
        "details": details,
    }


# ------------------------------------------------------------------------ helpers


def text_width(text: str, size: float) -> float:
    return len(text) * size * CHAR


def svg(height: int, body: str, style: str, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{escape(label)}">\n'
        f"<title>{escape(label)}</title>\n"
        f"<style>\ntext {{ font-family: {FONT}; }}\n{style}\n{REDUCED_MOTION}\n</style>\n"
        f"{body}\n</svg>\n"
    )


def window(height: int, title: str) -> str:
    """Terminal window chrome shared by the header and the info card."""
    dots = "".join(
        f'<circle cx="{24 + i * 20}" cy="20" r="6" fill="{color}"/>'
        for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f"))
    )
    return (
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
        f'<path d="M0.5 40.5 H{WIDTH - 0.5}" stroke="{BORDER}"/>{dots}'
        f'<text x="{WIDTH / 2}" y="25" font-size="13" fill="{MUTED}" text-anchor="middle">{escape(title)}</text>'
    )


# ------------------------------------------------------------------------- assets


def render_header() -> str:
    """Typed terminal session: whoami, then the role, then a blinking prompt."""
    prompt = f"{PROFILE['shell_user']}@{PROFILE['host']}:~$"
    size, x = 18, 28
    steps = [
        ("cmd", "whoami", 0.4, 0.9),
        ("out", PROFILE["name"], 1.5, 0.0),
        ("cmd", "cat role.txt", 2.1, 1.0),
        ("out", PROFILE["role"], 3.3, 0.0),
    ]
    body, style, y = [window(250, f"{prompt} — zsh")], [], 82
    for index, (kind, value, start, duration) in enumerate(steps):
        if kind == "cmd":
            offset = x + text_width(prompt + " ", size)
            full = text_width(value, size) + 4
            body.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{GREEN}">{escape(prompt)}</text>')
            # The rect is full width by default and the animation starts at 0s, so a renderer
            # without SMIL shows the finished command instead of an empty prompt.
            total = start + duration
            body.append(
                f'<clipPath id="type{index}"><rect x="{offset}" y="{y - size}" width="{full:.0f}" height="{size + 8}">'
                f'<animate attributeName="width" values="0;0;{full:.0f}" keyTimes="0;{start / total:.3f};1" '
                f'dur="{total}s" fill="freeze"/></rect></clipPath>'
                f'<text x="{offset}" y="{y}" font-size="{size}" fill="{TEXT}" clip-path="url(#type{index})">{escape(value)}</text>'
            )
        else:
            weight, color, extra = ("700", "#ffffff", 28) if index == 1 else ("400", BLUE, 19)
            body.append(
                f'<text class="out" style="animation-delay:{start}s" x="{x}" y="{y}" '
                f'font-size="{extra}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'
            )
        y += 38 if kind == "out" and index == 1 else 34
    cursor_x = x + text_width(prompt + " ", size)
    body.append(f'<text class="out" style="animation-delay:3.9s" x="{x}" y="{y}" font-size="{size}" fill="{GREEN}">{escape(prompt)}</text>')
    body.append(f'<rect class="cursor" x="{cursor_x:.0f}" y="{y - size + 3}" width="10" height="{size}" fill="{TEXT}"/>')
    style.append(
        ".out { animation: fade .4s ease-out backwards; }\n"
        "@keyframes fade { from { opacity: 0; } }\n"
        ".cursor { animation: blink 1s step-end 3.9s infinite; }\n"
        "@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }"
    )
    return svg(250, "\n".join(body), "\n".join(style), f"{PROFILE['name']} — {PROFILE['role']}")


LOGO = [
    "   .-~~~-.      ",
    " .(       ).    ",
    "(  cloud   )~.  ",
    " `-._____.-'  ) ",
    "   |  |  |  .'  ",
    "  [#] [#] [#]   ",
    "  [#] [#] [#]   ",
    "  ===========   ",
]


def months_between(since: str, today: date) -> int:
    year, month = map(int, since.split("-"))
    return (today.year - year) * 12 + today.month - month


def render_info(live: dict) -> str:
    """neofetch-style card: ASCII logo on the left, facts and live numbers on the right."""
    size, line = 14, 23
    facts = list(PROFILE["facts"])
    months = months_between(PROFILE["it_since"], date.today())
    facts.append(["Uptime", f"{months // 12}y {months % 12}m in IT (since {PROFILE['it_since'].replace('-', '.')})"])
    stats = f"{live['repos']} public projects · {live['workflows']} CI workflows"
    if live["contributions"] is not None:
        stats += f" · {live['contributions']} contributions this year"
    facts.append(["GitHub", stats])
    facts.append(["Code", " · ".join(live["languages"])])

    header = f"{PROFILE['user']}@github"
    rows = [(header, None), ("-" * len(header), None)] + [(key, value) for key, value in facts]
    height = 60 + line * (len(rows) + 2) + 10
    body = [window(height, "neofetch")]
    for i, art in enumerate(LOGO):
        body.append(
            f'<text class="row" style="animation-delay:{i * 0.05:.2f}s" x="28" y="{78 + i * line}" '
            f'font-size="{size}" fill="{BLUE}" xml:space="preserve">{escape(art)}</text>'
        )
    x, label_width = 220, 9
    for i, (key, value) in enumerate(rows):
        y, delay = 78 + i * line, 0.3 + i * 0.07
        if value is None:
            color = GREEN if i == 0 else MUTED
            content = f'<tspan fill="{color}" font-weight="{700 if i == 0 else 400}">{escape(key)}</tspan>'
        else:
            content = (
                f'<tspan fill="{ORANGE}">{escape(key.ljust(label_width))}</tspan>'
                f'<tspan fill="{TEXT}">{escape(value)}</tspan>'
            )
        body.append(
            f'<text class="row" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" '
            f'font-size="{size}" xml:space="preserve">{content}</text>'
        )
    palette = ["#484f58", "#ff7b72", GREEN, "#d29922", BLUE, PURPLE, "#39c5cf", TEXT]
    y = 78 + len(rows) * line + 6
    for i, color in enumerate(palette):
        body.append(
            f'<rect class="row" style="animation-delay:{0.3 + len(rows) * 0.07:.2f}s" '
            f'x="{x + i * 26}" y="{y}" width="24" height="14" rx="2" fill="{color}"/>'
        )
    style = (
        ".row { animation: slide .45s ease-out backwards; }\n"
        "@keyframes slide { from { opacity: 0; transform: translateX(-6px); } }"
    )
    return svg(height, "\n".join(body), style, f"{PROFILE['name']}: {PROFILE['role']}")


def render_path() -> str:
    """The three projects as one pipeline: same services, three platforms."""
    height, box_w, box_h, top = 150, 230, 74, 38
    gap = (WIDTH - 40 - 3 * box_w) / 2
    nodes = [
        ("VPS", "Ansible + Docker", GREEN),
        ("AWS", "Terraform + SSM", ORANGE),
        ("Kubernetes", "Argo CD GitOps", BLUE),
    ]
    body = [
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="20" y="24" font-size="13" fill="{MUTED}"># same services, three platforms — each one tested in CI</text>',
    ]
    for i, (name, tool, color) in enumerate(nodes):
        x = 20 + i * (box_w + gap)
        body.append(
            f'<g class="node" style="animation-delay:{i * 0.35:.2f}s">'
            f'<rect x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="8" fill="{PANEL}" stroke="{color}"/>'
            f'<text x="{x + box_w / 2}" y="{top + 31}" font-size="17" font-weight="700" fill="{color}" text-anchor="middle">{escape(name)}</text>'
            f'<text x="{x + box_w / 2}" y="{top + 55}" font-size="13" fill="{TEXT}" text-anchor="middle">{escape(tool)}</text></g>'
        )
        if i < 2:
            x1, x2, y = x + box_w + 8, x + box_w + gap - 8, top + box_h / 2
            body.append(
                f'<path class="flow" d="M{x1} {y} H{x2}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 6"/>'
                f'<path d="M{x2 - 7} {y - 5} L{x2} {y} L{x2 - 7} {y + 5}" fill="none" stroke="{MUTED}" stroke-width="2"/>'
            )
    body.append(
        f'<text x="{WIDTH / 2}" y="{height - 16}" font-size="12" fill="{MUTED}" text-anchor="middle">'
        "Vaultwarden · Uptime Kuma · Prometheus · Grafana</text>"
    )
    style = (
        ".node { animation: fade .5s ease-out backwards; }\n"
        "@keyframes fade { from { opacity: 0; } }\n"
        ".flow { animation: flow 1.2s linear infinite; }\n"
        "@keyframes flow { to { stroke-dashoffset: -12; } }"
    )
    return svg(height, "\n".join(body), style, "Project path: VPS, then AWS, then Kubernetes")


def render_project(project: dict, live: dict) -> str:
    """Compact card: stage, title and repository topics. The summary lives in README text."""
    pad, height = 24, 104
    topics = live["details"].get(project["repo"], {}).get("topics", [])
    body = [
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="{pad}" y="40" font-size="15" fill="{GREEN}">{escape(project["stage"])}</text>',
        f'<text x="{pad + 105}" y="40" font-size="22" font-weight="700" fill="{BLUE}">{escape(project["title"])}</text>',
        f'<text x="{WIDTH - pad}" y="40" font-size="13" fill="{MUTED}" text-anchor="end">{escape(project["repo"])}</text>',
    ]
    x, y = pad, 62
    for topic in topics:
        w = text_width(topic, 13) + 20
        if x + w > WIDTH - pad:
            break
        body.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="#1f6feb26" stroke="#1f6feb66"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 16}" font-size="13" fill="{BLUE}" text-anchor="middle">{escape(topic)}</text>'
        )
        x += w + 8
    return svg(height, "\n".join(body), "", f"{project['stage']} {project['title']}: {', '.join(topics)}")


def render_stack() -> str:
    size, row, label_w, pad = 13, 34, 190, 24
    rows = PROFILE["stack"]
    height = 30 + row * len(rows) + 8
    body = [f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>']
    for i, (label, items) in enumerate(rows):
        y = 24 + i * row
        group = [f'<text x="{pad}" y="{y + 16}" font-size="{size}" fill="{ORANGE}">{escape(label)}</text>']
        x = pad + label_w
        for item in items:
            w = text_width(item, size) + 20
            group.append(
                f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="5" fill="{PANEL}" stroke="{BORDER}"/>'
                f'<text x="{x + w / 2:.0f}" y="{y + 16}" font-size="{size}" fill="{TEXT}" text-anchor="middle">{escape(item)}</text>'
            )
            x += w + 7
        if x > WIDTH:
            raise SystemExit(f"stack row '{label}' is {x:.0f}px wide, more than {WIDTH}px")
        body.append(f'<g class="row" style="animation-delay:{i * 0.08:.2f}s">{"".join(group)}</g>')
    style = (
        ".row { animation: fade .4s ease-out backwards; }\n"
        "@keyframes fade { from { opacity: 0; } }"
    )
    return svg(height, "\n".join(body), style, "Tech stack")


def main() -> None:
    live = fetch_live()
    ASSETS.mkdir(exist_ok=True)
    outputs = {
        "header.svg": render_header(),
        "neofetch.svg": render_info(live),
        "path.svg": render_path(),
        "stack.svg": render_stack(),
    }
    for project in PROFILE["projects"]:
        outputs[f"project-{project['repo']}.svg"] = render_project(project, live)
    for name, content in outputs.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"rendered {len(outputs)} files; live data: {json.dumps({k: v for k, v in live.items() if k != 'details'})}")


if __name__ == "__main__":
    main()
