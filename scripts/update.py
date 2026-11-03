#!/usr/bin/env python3
"""Refresh benchmark metadata from the GitHub API and regenerate README + chart.

Source of truth : data/benchmarks.csv  (name, group, repo, level_L, level_M, what)
Metrics output  : data/metrics.csv
Generated docs  : README.md tables between markers, docs/positioning.svg

No third-party dependencies. Requires GITHUB_TOKEN for higher rate limits.
"""

import csv
import json
import math
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "benchmarks.csv")
MET = os.path.join(ROOT, "data", "metrics.csv")
README = os.path.join(ROOT, "README.md")
SVG = os.path.join(ROOT, "docs", "positioning.svg")

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

GROUP_LABEL = {
    "video": "视频世界模型 / 生成真实度",
    "policy": "具身策略评测",
    "sim": "仿真基准平台",
}
GROUP_COLOR = {"video": "#3b82f6", "policy": "#10b981", "sim": "#8b5cf6"}


def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "world-model-evals-monitor",
            **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(repo):
    """Return metrics dict, or None when the repo is not resolvable."""
    if repo == "PENDING":
        return None
    try:
        d = api("/repos/" + repo)
    except Exception:
        return None
    lic = (d.get("license") or {}).get("spdx_id") or "none"
    if lic in ("NOASSERTION", "none"):
        lic = "无 LICENSE" if lic == "none" else "NOASSERTION"
    rel = ""
    try:
        rel = api(f"/repos/{repo}/releases/latest").get("tag_name", "")
    except Exception:
        pass
    return {
        "stars": d.get("stargazers_count", 0),
        "forks": d.get("forks_count", 0),
        "open_issues": d.get("open_issues_count", 0),
        "pushed": (d.get("pushed_at") or "")[:10],
        "license": lic,
        "release": rel,
        "archived": bool(d.get("archived")),
    }


def mpos(level):
    """Map an M-level string to a numeric x position on the ladder."""
    if level.strip() in ("平台", "", "—"):
        return 0.55
    nums = [float(x) for x in re.findall(r"[1-5](?:\.\d)?", level)]
    return sum(nums) / len(nums) if nums else 0.55


def nstars(r):
    try:
        return int(r.get("stars") or 0)
    except (TypeError, ValueError):
        return 0


def radius(stars):
    return 7 + 2.4 * math.sqrt(max(stars, 0))


COLS = ["M1", "M1–M2", "M2", "M2–M3", "M3", "M3–M4", "M4", "平台"]


def norm_level(lv):
    lv = (lv or "").strip()
    if lv in COLS:
        return lv
    if lv in ("L0–L3", "L1–L3", "L2–L3"):
        return "M2"
    return "M1–M2"


def build_svg(rows):
    CW, gutter = 132, 12
    left = 40
    W = left + CW * len(COLS) + 40
    top = 150
    pad = 10

    cols = {c: [] for c in COLS}
    for r in rows:
        cols[norm_level(r["level_M"])].append(r)

    heights = {}
    for c in COLS:
        h = 0
        for r in cols[c]:
            h += 2 * min(radius(nstars(r)), 22) + 26
        heights[c] = h
    maxh = max(heights.values()) if heights else 200
    H = top + maxh + 90

    def colx(i):
        return left + CW * i + CW / 2

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Noto Sans SC, Helvetica, Arial, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        '<text x="40" y="46" font-size="23" font-weight="700" fill="#0f172a">'
        "世界模型 / 具身测评：在证据阶梯上的位置</text>",
        '<text x="40" y="72" font-size="12.5" fill="#64748b">'
        "气泡大小 ∝ GitHub stars · 纵轴按列堆叠 · 颜色 = 评测类型 · 数据 "
        + datetime.now(timezone.utc).strftime("%Y-%m-%d") + "</text>",
    ]

    # legend
    lx = W - 300
    for i, g in enumerate(["video", "policy", "sim"]):
        x = lx + i * 100
        out.append(f'<circle cx="{x}" cy="62" r="6" fill="{GROUP_COLOR[g]}" fill-opacity="0.75"/>')
        out.append(f'<text x="{x + 11}" y="66" font-size="11.5" fill="#475569">{GROUP_LABEL[g][:6]}</text>')

    # decision boundary between M2 and M2–M3
    bx = colx(3) - CW / 2 - gutter / 2
    out.append(f'<rect x="{left}" y="{top - 34}" width="{bx - left}" height="{H - top + 10}" fill="#f8fafc" opacity="0.55"/>')
    out.append(f'<line x1="{bx}" y1="{top - 40}" x2="{bx}" y2="{H - 60}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="7 5"/>')
    out.append(f'<text x="{bx + 6}" y="{top - 46}" font-size="11.5" font-weight="700" fill="#b45309">← 产物诊断 ｜ 决策证据 →</text>')

    for i, c in enumerate(COLS):
        x = colx(i)
        out.append(f'<text x="{x}" y="{top - 16}" font-size="12.5" font-weight="700" fill="#334155" text-anchor="middle">{c}</text>')
        y = top
        for r in cols[c]:
            rad = min(radius(nstars(r)), 22)
            y += rad
            out.append(
                f'<circle cx="{x}" cy="{y:.1f}" r="{rad:.1f}" '
                f'fill="{GROUP_COLOR[r["group"]]}" fill-opacity="0.22" '
                f'stroke="{GROUP_COLOR[r["group"]]}" stroke-width="1.5"/>'
            )
            name = r["name"] if len(r["name"]) <= 17 else r["name"][:16] + "…"
            out.append(
                f'<text x="{x}" y="{y + rad + 13:.1f}" font-size="10.5" fill="#334155" '
                f'text-anchor="middle">{name}</text>'
            )
            out.append(
                f'<text x="{x}" y="{y + rad + 24:.1f}" font-size="9.5" fill="#94a3b8" '
                f'text-anchor="middle">{r.get("stars") or "?"}</text>'
            )
            y += rad + 26

    out.append(
        f'<text x="40" y="{H - 20}" font-size="10.5" fill="#94a3b8">'
        "层级判定为分析结论；M1–M5 为该清单采用的压缩框架，非行业标准。"
        "「平台」列不产出证据层级。</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


def table(rows, group, with_push):
    sel = [r for r in rows if r["group"] == group]
    sel.sort(key=lambda z: -nstars(z))
    if with_push:
        head = "| 项目 | Stars | 许可证 | 最近推送 |\n|---|---:|---|---|\n"
        body = "\n".join(
            f'| {r["name"]} | {fmt(r.get("stars"))} | {r["license"]} | {r["pushed"]} |'
            for r in sel
        )
    else:
        head = "| 项目 | Stars | 许可证 | L | M |\n|---|---:|---|---|---|\n"
        body = "\n".join(
            f'| {r["name"]} | {fmt(r.get("stars"))} | {r["license"]} | '
            f'{r["level_L"]} | {r["level_M"]} |'
            for r in sel
        )
    return head + body


def fmt(v):
    return f"**{v:,}**" if v else "未核实"


def main():
    with open(SRC, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        m = fetch(r["repo"])
        if m is None:
            r["stars"] = ""
            r["license"] = "未知"
            r["pushed"] = "—"
            r["forks"] = ""
            r["open_issues"] = ""
            r["release"] = ""
            r["archived"] = ""
        else:
            r.update({k: v for k, v in m.items()})

    fields = [
        "name", "group", "repo", "level_L", "level_M", "what",
        "stars", "forks", "open_issues", "pushed", "license", "release", "archived",
    ]
    os.makedirs(os.path.dirname(MET), exist_ok=True)
    with open(MET, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    nolic = [r["name"] for r in rows if r["license"] in ("无 LICENSE", "未知")]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(rows)

    blocks = {
        "VIDEO_TABLE": table(rows, "video", False),
        "POLICY_TABLE": table(rows, "policy", False),
        "SIM_TABLE": table(rows, "sim", True),
        "STAMP": stamp,
        "TOTAL": str(total),
        "NO_LICENSE": "、".join(f"`{n}`" for n in nolic) or "无",
        "NO_LICENSE_N": str(len(nolic)),
        "VIDEO_N": str(sum(1 for r in rows if r["group"] == "video")),
        "POLICY_N": str(sum(1 for r in rows if r["group"] == "policy")),
        "SIM_N": str(sum(1 for r in rows if r["group"] == "sim")),
    }

    text = open(README, encoding="utf-8").read()
    for key, val in blocks.items():
        text = re.sub(
            rf"(<!-- BEGIN:{key} -->)(.*?)(<!-- END:{key} -->)",
            lambda m, v=val: m.group(1) + "\n" + v + "\n" + m.group(3),
            text,
            flags=re.S,
        )
    open(README, "w", encoding="utf-8").write(text)

    os.makedirs(os.path.dirname(SVG), exist_ok=True)
    open(SVG, "w", encoding="utf-8").write(build_svg(rows))
    print(f"updated {total} benchmarks, {len(nolic)} without license, {stamp}")


if __name__ == "__main__":
    sys.exit(main())
