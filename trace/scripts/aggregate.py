#!/usr/bin/env python3
"""拾迹 Trace 聚合器：读 notes/*.md 的 frontmatter，重算 notes/README.md（成长轨迹）；
并扫 reports/*.md 在 README 末尾列出最近周报。

独立运行，只依赖标准库（不依赖 shiji 包，保证 skill 可移植）。
用法：python aggregate.py <NOTES_REPO>
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

GRACE = 3          # 连续天数断档宽限
BAR_CAP = 8        # 技能进度条总格
WEEKS = 8          # 热力图显示周数
WEEKDAYS = "一二三四五六日"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")


def parse_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm: dict = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            fm[k] = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        elif v.startswith('"') and v.endswith('"'):
            fm[k] = v[1:-1]
        else:
            try:
                fm[k] = int(v)
            except ValueError:
                fm[k] = v
    return fm


def load_notes(notes_dir: Path) -> list[tuple[str, dict]]:
    """返回 [(date_str, frontmatter), ...]，按文件名升序。"""
    recs = []
    for p in sorted(notes_dir.glob("*.md")):
        if p.name == "README.md" or p.name.startswith("."):
            continue
        if not DATE_RE.match(p.stem):
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        if fm:
            recs.append((p.stem, fm))
    return recs


def load_reports(reports_dir: Path) -> list[dict]:
    """返回 [{week, period, ...}, ...]，按 week 升序。"""
    out = []
    if not reports_dir.exists():
        return out
    for p in sorted(reports_dir.glob("*.md")):
        if p.name == "README.md" or p.name.startswith("."):
            continue
        if not WEEK_RE.match(p.stem):
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        if fm:
            out.append({"week": p.stem, **fm})
    return out


def streak(dates_set: set[str], cutoff: str, grace: int) -> tuple[int, int]:
    """从 cutoff 往回数连续天数。返回 (streak, 用掉的宽限)。"""
    c = date.fromisoformat(cutoff)
    s = g = 0
    for i in range(366):
        d = (c - timedelta(days=i)).isoformat()
        if d in dates_set:
            s += 1
        else:
            if s == 0 and i == 0:
                continue  # 今天还没笔记：免费跳过，不耗宽限
            if g < grace:
                g += 1
            else:
                break
    return s, g


def bar(days: int) -> str:
    f = min(BAR_CAP, days)
    return "█" * f + "░" * (BAR_CAP - f)


def badges(s: int, n_tech: int, tech_days: dict[str, set], solved: int) -> list[str]:
    b: list[str] = []
    if s >= 30:
        b.append("🔥🔥 30 天连击")
    elif s >= 7:
        b.append("🔥 7 天连击")
    if n_tech >= 15:
        b.append("🧭🧭 老练探索者（15+ 技术）")
    elif n_tech >= 5:
        b.append("🧭 探索者（5+ 技术）")
    for lvl, th in ((3, 20), (2, 10), (1, 5)):
        if solved >= th:
            b.append(f"🐛 Debug 侦探 Lv.{lvl}（攻克 {th}+）")
            break
    deep = sorted(n for n, days in tech_days.items() if len(days) >= 3)
    if deep:
        b.append(f"📖 深挖者（{deep[0]} 跨 3+ 天）")
    return b


def heatmap(dates_set: set[str], cutoff: str, weeks: int) -> str:
    end = date.fromisoformat(cutoff)
    monday = end - timedelta(days=end.weekday())
    start = monday - timedelta(weeks=weeks - 1)
    rows = []
    for w in range(weeks):
        cells = [
            "🟩" if (start + timedelta(weeks=w, days=d)).isoformat() in dates_set else "⬜"
            for d in range(7)
        ]
        rows.append("".join(cells))
    return f"近 {weeks} 周（🟩=有学习 ⬜=无）：\n\n```\n{WEEKDAYS}\n" + "\n".join(rows) + "\n```"


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python aggregate.py <NOTES_REPO>", file=sys.stderr)
        return 1
    repo = Path(sys.argv[1])
    notes_dir = repo / "notes"
    reports_dir = repo / "reports"
    notes_dir.mkdir(parents=True, exist_ok=True)

    recs = load_notes(notes_dir)
    dates_set = {d for d, _ in recs}
    dates_sorted = sorted(dates_set)

    tech_counter: Counter[str] = Counter()
    tech_days: dict[str, set[str]] = defaultdict(set)
    solved = 0
    for d, fm in recs:
        for t in fm.get("technologies", []):
            if isinstance(t, str) and t.strip():
                name = t.strip()
                tech_counter[name] += 1
                tech_days[name].add(d)
        solved += int(fm.get("mistakes_resolved", 0) or 0)

    cutoff = date.today().isoformat()
    s, _g = streak(dates_set, cutoff, GRACE)
    bdg = badges(s, len(tech_counter), tech_days, solved)

    parts = [
        "# 🚀 我的实习成长轨迹",
        "",
        "> 多对话 · 多犯错 · 多学习 — 由 **/trace** 自动记录",
        "",
        f"🔥 连续 **{s}** 天 · 累计学习 **{len(dates_set)}** 天 · 🐛 已攻克问题 **{solved}** · 🧭 已点亮技术 **{len(tech_counter)}**",
        "",
        heatmap(dates_set, cutoff, WEEKS),
        "",
        "## 🌳 技能进度",
        "",
    ]
    if tech_counter:
        for name, cnt in tech_counter.most_common():
            days = len(tech_days[name])
            parts.append(f"- `{bar(days)}` {min(BAR_CAP, days)}/{BAR_CAP}  **{name}** · {cnt} 次")
    else:
        parts.append("_（还没有技术被记录，去和 AI 多聊聊吧）_")
    parts += ["", "## 🏅 徽章墙", ""]
    parts.append("\n".join(f"- {b}" for b in bdg) if bdg else "_（继续学习，解锁第一个徽章）_")
    parts += ["", "## 📝 最近笔记", ""]
    recent = list(reversed(dates_sorted))[:7]
    parts.append("\n".join(f"- [{d}]({d}.md)" for d in recent) if recent else "_（还没有笔记）_")

    # 周报链接（README 在 notes/ 下，周报在 ../reports/，故相对路径 ../reports/）
    reports = load_reports(reports_dir)
    parts += ["", "## 📋 最近周报", ""]
    recent_reports = sorted(reports, key=lambda r: r["week"], reverse=True)[:4]
    if recent_reports:
        for r in recent_reports:
            label = r.get("period") or r["week"]
            parts.append(f"- [{r['week']} 周报](../reports/{r['week']}.md)（{label}）")
    else:
        parts.append("_（还没有周报，用 `/trace weekly` 生成）_")
    parts.append("")

    out = notes_dir / "README.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(
        f"✓ 已更新 {out}：连续 {s} 天 · 累计 {len(dates_set)} 天 · 攻克 {solved} · 技术 {len(tech_counter)} · 周报 {len(reports)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
