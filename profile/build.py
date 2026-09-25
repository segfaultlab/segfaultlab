"""生成主页顶部的终端风 SVG（深色、浅色各一张）。

在 GitHub Actions 里每天跑一次：设置了 GITHUB_TOKEN 时从 GraphQL 拉统计数字并写进
stats.json；拉取失败或本地没有 token 时沿用 stats.json 里的旧值。
"""

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("USER_LOGIN", "segfaultlab")
CAREER_START = dt.date(2022, 6, 1)
HERE = Path(__file__).resolve().parent
STATS_FILE = HERE / "stats.json"

CHAR_W = 8.4
LINE_H = 20
FONT_SIZE = 14
PAD_X = 24
TITLE_H = 36
LEFT_COLS = 40
RIGHT_COLS = 58

THEMES = {
    "dark": {
        "window": "#161b22", "border": "#30363d", "bar": "#21262d", "title": "#8b949e",
        "text": "#c9d1d9", "muted": "#8b949e", "key": "#ffa657", "value": "#a5d6ff",
        "prompt": "#3fb950", "path": "#79c0ff", "error": "#ff7b72", "art": "#ff7b72", "shadow": "#5c2320",
    },
    "light": {
        "window": "#ffffff", "border": "#d0d7de", "bar": "#f6f8fa", "title": "#57606a",
        "text": "#24292f", "muted": "#6e7781", "key": "#953800", "value": "#0a3069",
        "prompt": "#1a7f37", "path": "#0550ae", "error": "#cf222e", "art": "#cf222e", "shadow": "#ffc1ba",
    },
}

ART = [
    "███████╗███████╗ ██████╗ ██╗   ██╗",
    "██╔════╝██╔════╝██╔════╝ ██║   ██║",
    "███████╗█████╗  ██║  ███╗██║   ██║",
    "╚════██║██╔══╝  ██║   ██║╚██╗ ██╔╝",
    "███████║███████╗╚██████╔╝ ╚████╔╝",
    "╚══════╝╚══════╝ ╚═════╝   ╚═══╝",
]

GDB = [
    ("", "muted"),
    ("Program received signal SIGSEGV,", "error"),
    ("Segmentation fault.", "error"),
    ("0x0000000000000000 in ?? ()", "muted"),
    ("(gdb) bt", "text"),
    ("#0  0x0000000000000000 in ?? ()", "muted"),
    ("#1  build (target=aarch64)", "muted"),
    ("      at crossbuild.cpp:404", "muted"),
    ("#2  main () at life.cpp:42", "muted"),
]


def fetch_stats(token):
    def gql(query, variables):
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": variables}).encode(),
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
        if body.get("errors"):
            raise RuntimeError(body["errors"])
        return body["data"]["user"]

    user = gql(
        """query($login: String!) {
          user(login: $login) {
            followers { totalCount }
            repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
              totalCount
              nodes { stargazerCount }
            }
            contributionsCollection { contributionYears }
          }
        }""",
        {"login": LOGIN},
    )
    contributions = 0
    for year in user["contributionsCollection"]["contributionYears"]:
        start = f"{year}-01-01T00:00:00Z"
        end = f"{year}-12-31T23:59:59Z"
        data = gql(
            """query($login: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                  contributionCalendar { totalContributions }
                }
              }
            }""",
            {"login": LOGIN, "from": start, "to": end},
        )
        contributions += data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    repos = user["repositories"]
    return {
        "repos": repos["totalCount"],
        "stars": sum(node["stargazerCount"] for node in repos["nodes"]),
        "followers": user["followers"]["totalCount"],
        "contributions": contributions,
    }


def load_stats():
    cached = json.loads(STATS_FILE.read_text()) if STATS_FILE.exists() else {}
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return cached
    try:
        stats = fetch_stats(token)
    except Exception as exc:  # 网络或权限问题时保留旧数字，不让整张图挂掉
        print(f"fetch stats failed, keep cached values: {exc}")
        return cached
    STATS_FILE.write_text(json.dumps(stats, indent=2) + "\n")
    return stats


def uptime(today):
    months = (today.year - CAREER_START.year) * 12 + today.month - CAREER_START.month
    if today.day < CAREER_START.day:
        months -= 1
    anchor_month = CAREER_START.month - 1 + months
    anchor = CAREER_START.replace(year=CAREER_START.year + anchor_month // 12, month=anchor_month % 12 + 1)
    days = (today - anchor).days
    years, months = divmod(months, 12)

    def plural(n, word):
        return f"{n} {word}" + ("" if n == 1 else "s")

    return f"{plural(years, 'year')}, {plural(months, 'month')}, {plural(days, 'day')}"


def fmt(value):
    return f"{value:,}" if isinstance(value, int) else "-"


def right_column(stats, today):
    def row(key, value):
        dots = max(RIGHT_COLS - len(key) - len(value) - 4, 2)
        return [(key + ": ", "key"), ("." * dots + " ", "muted"), (value, "value")]

    def section(name):
        return [(f"- {name} " + "-" * (RIGHT_COLS - len(name) - 3), "muted")]

    return [
        [("koko", "prompt"), ("@", "text"), ("segfaultlab", "prompt")],
        [("-" * RIGHT_COLS, "muted")],
        row("OS", "Linux, macOS, OpenHarmony"),
        row("Uptime", uptime(today)),
        row("Host", "Wuhan, China"),
        row("Kernel", "Embedded Linux, OTA, Toolchains"),
        row("Focus", "Cross-compilation, Agent Runtime"),
        row("Languages.Programming", "C++, C, Rust, Python"),
        row("Languages.Real", "Chinese, English"),
        row("Toolchain", "CMake, Clang/LLVM, musl, Ninja"),
        row("Debug", "GDB, Valgrind, perf"),
        [("", "text")],
        section("Contact"),
        row("GitHub", "github.com/segfaultlab"),
        [("", "text")],
        section("GitHub Stats"),
        row("Public Repos", fmt(stats.get("repos"))),
        row("Stars", fmt(stats.get("stars"))),
        row("Followers", fmt(stats.get("followers"))),
        row("Contributions (all time)", fmt(stats.get("contributions"))),
    ]


def left_column():
    # 字符画那几行留空，由 render 用方块画出来，不依赖浏览器里的等宽字体
    return [[] for _ in ART] + [[(text, color)] for text, color in GDB]


def art_blocks(theme, top, delay_of):
    cell_h = LINE_H * len(ART) / (len(ART) - 1)
    out = []
    for layer, dx, color in (("shadow", 3, theme["shadow"]), ("art", 0, theme["art"])):
        for r, line in enumerate(ART):
            rects = "".join(
                f'<rect x="{PAD_X + c * CHAR_W + dx:.1f}" y="{top + r * cell_h + dx:.1f}" '
                f'width="{CHAR_W + 0.3:.1f}" height="{cell_h + 0.3:.1f}"/>'
                for c, ch in enumerate(line) if ch == "█"
            )
            if rects:
                out.append(f'<g class="r" shape-rendering="crispEdges" fill="{color}" style="animation-delay:{delay_of(r):.2f}s">{rects}</g>')
    return out


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_line(x, y, spans, theme, delay):
    parts = "".join(f'<tspan fill="{theme[color]}">{esc(text)}</tspan>' for text, color in spans if text)
    if not parts:
        return ""
    return f'<text x="{x}" y="{y}" class="r" style="animation-delay:{delay:.2f}s">{parts}</text>'


def render(theme, stats, today):
    left, right = left_column(), right_column(stats, today)
    body_rows = max(len(left), len(right))
    rows = body_rows + 4  # 命令行、空行、输出、空行、结尾提示符
    width = round(PAD_X * 2 + (LEFT_COLS + RIGHT_COLS) * CHAR_W)
    height = TITLE_H + 20 + rows * LINE_H
    base_y = TITLE_H + 28
    right_x = PAD_X + LEFT_COLS * CHAR_W

    command = "neofetch"
    cmd_x = PAD_X + len("koko@segfaultlab:~$ ") * CHAR_W
    cmd_w = len(command) * CHAR_W
    type_start, type_dur = 0.4, 0.8
    output_start = type_start + type_dur + 0.3
    step = 0.05

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;"
        f"font-size:{FONT_SIZE}px;white-space:pre}}",
        ".r{opacity:0;animation:show .01s linear forwards}",
        "@keyframes show{to{opacity:1}}",
        f".cover{{animation:type {type_dur}s steps({len(command)}) {type_start}s forwards}}",
        f"@keyframes type{{to{{transform:translateX({cmd_w:.1f}px)}}}}",
        f".tcur{{animation:type {type_dur}s steps({len(command)}) {type_start}s forwards,"
        f"hide .01s linear {output_start - 0.1:.2f}s forwards}}",
        "@keyframes hide{to{opacity:0}}",
        ".blink{animation:blink 1s step-end infinite}",
        "@keyframes blink{50%{opacity:0}}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{theme["window"]}" stroke="{theme["border"]}"/>',
        f'<path d="M0.5 {TITLE_H} V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V{TITLE_H} Z" fill="{theme["bar"]}"/>',
        f'<line x1="0.5" y1="{TITLE_H}" x2="{width - 0.5}" y2="{TITLE_H}" stroke="{theme["border"]}"/>',
        '<circle cx="22" cy="18" r="6" fill="#ff5f57"/>',
        '<circle cx="42" cy="18" r="6" fill="#febc2e"/>',
        '<circle cx="62" cy="18" r="6" fill="#28c840"/>',
        f'<text x="{width / 2}" y="23" text-anchor="middle" fill="{theme["title"]}" style="font-size:13px">koko@segfaultlab: ~ (zsh)</text>',
    ]

    prompt = [("koko@segfaultlab", "prompt"), (":", "text"), ("~", "path"), ("$ ", "text")]
    parts = "".join(f'<tspan fill="{theme[c]}">{esc(t)}</tspan>' for t, c in prompt)
    out.append(f'<text x="{PAD_X}" y="{base_y}">{parts}<tspan fill="{theme["text"]}">{command}</tspan></text>')
    out.append(f'<rect class="cover" x="{cmd_x:.1f}" y="{base_y - 15}" width="{cmd_w:.1f}" height="20" fill="{theme["window"]}"/>')
    out.append(f'<rect class="tcur" x="{cmd_x:.1f}" y="{base_y - 14}" width="{CHAR_W:.1f}" height="18" fill="{theme["text"]}"/>')

    out.extend(art_blocks(theme, base_y + 2 * LINE_H - 15, lambda r: output_start + r * step))

    for i in range(body_rows):
        y = base_y + (i + 2) * LINE_H
        delay = output_start + i * step
        if i < len(left):
            out.append(text_line(PAD_X, y, left[i], theme, delay))
        if i < len(right):
            out.append(text_line(round(right_x, 1), y, right[i], theme, delay))

    end_y = base_y + (body_rows + 3) * LINE_H
    end_delay = output_start + body_rows * step + 0.2
    out.append(f'<g class="r" style="animation-delay:{end_delay:.2f}s">')
    out.append(f'<text x="{PAD_X}" y="{end_y}">{parts}</text>')
    out.append(f'<rect class="blink" x="{cmd_x:.1f}" y="{end_y - 14}" width="{CHAR_W:.1f}" height="18" fill="{theme["text"]}"/>')
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(line for line in out if line) + "\n"


def main():
    stats = load_stats()
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    for name, theme in THEMES.items():
        (HERE / f"{name}.svg").write_text(render(theme, stats, today), encoding="utf-8")


if __name__ == "__main__":
    main()
