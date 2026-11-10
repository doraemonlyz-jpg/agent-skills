#!/usr/bin/env python3
"""taotao-flow 本地效率评测报告（替代 soda 的 /soda:eval + Gift 上传）。

汇总 docs/features/{active,completed}/**/eval-log.json 与 cr-status.json，
并按需求的时间窗统计本机 Claude Code（~/.claude/projects）与 Codex（~/.codex/sessions）会话的 token。
输出 docs/eval/<日期>-report.html，并在 stdout 打印 Markdown 摘要。不上传任何数据。

用法: eval-report.py [--root PROJECT_ROOT] [--feature NAME] [--no-tokens] [--out PATH]
"""
import argparse
import glob
import html
import json
import os
import re
import subprocess
from datetime import datetime, timezone

FMT = "%Y-%m-%d %H:%M:%S"
STAGE_ORDER = ["ard", "design", "plan", "test", "impl", "cr", "fix", "sync", "archive"]


def parse_local(s):
    return datetime.strptime(s, FMT).astimezone() if s else None


def parse_iso(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def claude_tokens(root, start, end):
    """Claude Code：~/.claude/projects/<编码后的项目路径>/*.jsonl，按 message.id 去重累计 usage。"""
    enc = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))
    tot = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "sessions": set()}
    seen = set()
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/{enc}*/*.jsonl")):
        for line in open(f, encoding="utf-8", errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message") or {}
            u = msg.get("usage") if isinstance(msg, dict) else None
            ts = parse_iso(d.get("timestamp", ""))
            if not u or not ts or not (start <= ts <= end):
                continue
            key = (msg.get("id"), d.get("requestId"))
            if key in seen:
                continue
            seen.add(key)
            tot["input"] += u.get("input_tokens", 0) or 0
            tot["output"] += u.get("output_tokens", 0) or 0
            tot["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
            tot["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
            tot["sessions"].add(d.get("sessionId") or f)
    tot["sessions"] = len(tot["sessions"])
    return tot


def codex_tokens(root, start, end):
    """Codex：~/.codex/sessions/**/rollout-*.jsonl，取 cwd 匹配的会话在时间窗内最后一次 total_token_usage。"""
    tot = {"input": 0, "output": 0, "cache_read": 0, "sessions": 0}
    root = os.path.abspath(root)
    for f in glob.glob(os.path.expanduser("~/.codex/sessions/**/*.jsonl"), recursive=True):
        cwd, last = None, None
        for line in open(f, encoding="utf-8", errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            pl = d.get("payload") or {}
            if isinstance(pl, dict) and pl.get("cwd"):
                cwd = pl["cwd"]
            ts = parse_iso(d.get("timestamp", ""))
            info = pl.get("info") if isinstance(pl, dict) and pl.get("type") == "token_count" else None
            if info and ts and start <= ts <= end:
                last = info.get("total_token_usage") or last
        if cwd and os.path.abspath(cwd).startswith(root) and last:
            tot["input"] += last.get("input_tokens", 0) or 0
            tot["output"] += last.get("output_tokens", 0) or 0
            tot["cache_read"] += last.get("cached_input_tokens", 0) or 0
            tot["sessions"] += 1
    return tot


def summarize(root, path, with_tokens):
    d = json.load(open(path, encoding="utf-8"))
    fdir = os.path.dirname(path)
    stages, first, last = [], None, None
    for name in sorted(d.get("stages", {}), key=lambda x: STAGE_ORDER.index(x) if x in STAGE_ORDER else 99):
        s = d["stages"][name]
        a, b = parse_local(s.get("started_at")), parse_local(s.get("confirmed_at"))
        dur = round((b - a).total_seconds() / 60, 1) if a and b else None
        first = min(filter(None, [first, a])) if a else first
        last = max(filter(None, [last, b])) if b else last
        stages.append({"stage": name, "minutes": dur, "rounds": s.get("total_rounds"),
                       "interventions": len(s.get("interventions", [])),
                       "types": sorted({i["type"] for i in s.get("interventions", [])}),
                       "skills": s.get("skills_used", [])})
    cr = None
    crp = os.path.join(fdir, "cr-status.json")
    if os.path.exists(crp):
        c = json.load(open(crp, encoding="utf-8"))
        cr = {k: c.get(k) for k in ("result", "score", "blockerCount", "warnCount", "mode", "timestamp")}
    tokens = None
    if with_tokens and first and last:
        tokens = {"claude": claude_tokens(root, first.astimezone(timezone.utc), last.astimezone(timezone.utc)),
                  "codex": codex_tokens(root, first.astimezone(timezone.utc), last.astimezone(timezone.utc))}
    plan = glob.glob(os.path.join(fdir, "Plan-*.md"))
    done = todo = 0
    if plan:
        t = open(plan[0], encoding="utf-8").read()
        done, todo = len(re.findall(r"^\s*- \[x\]", t, re.M)), len(re.findall(r"^\s*- \[ \]", t, re.M))
    return {"feature": d.get("feature"), "dir": os.path.relpath(fdir, root), "stages": stages,
            "total_minutes": round(sum(s["minutes"] or 0 for s in stages), 1),
            "interventions": sum(s["interventions"] for s in stages), "rework": d.get("rework_log", []),
            "assessment": d.get("archive_assessment"), "cr": cr, "tokens": tokens,
            "plan_progress": f"{done}/{done + todo}" if plan else "—"}


def fmt_tok(t):
    if not t:
        return "—"
    c, x = t["claude"], t["codex"]
    n = c["input"] + c["output"] + c["cache_read"] + c["cache_write"] + x["input"] + x["output"]
    return f"{n/1000:.0f}k（Claude {c['sessions']} 会话 / Codex {x['sessions']} 会话）"


def render_html(rows, out):
    e = html.escape
    cards = []
    for r in rows:
        srows = "".join(f"<tr><td>{e(s['stage'])}</td><td>{s['minutes'] if s['minutes'] is not None else '—'}</td>"
                        f"<td>{s['rounds'] if s['rounds'] is not None else '—'}</td><td>{s['interventions']}</td>"
                        f"<td>{e(', '.join(s['types']))}</td><td>{e(', '.join(s['skills']))}</td></tr>" for s in r["stages"])
        a = r["assessment"] or {}
        cr = r["cr"] or {}
        rw = "".join(f"<li>{e(x['at'][:10])} · {e(x['cause'])} · {e(x['impact'])} · {e(x['reason'])}</li>" for x in r["rework"]) or "<li>无</li>"
        cards.append(f"""
<section class="card"><h2>{e(r['feature'] or '')}</h2><p class="muted">{e(r['dir'])}</p>
<div class="kpis">
 <div><b>{r['total_minutes']}</b><span>阶段耗时（分钟）</span></div>
 <div><b>{r['interventions']}</b><span>人工介入</span></div>
 <div><b>{len(r['rework'])}</b><span>返工</span></div>
 <div><b>{e(str(cr.get('score', '—')))}</b><span>CR 评分（{e(str(cr.get('result', '—')))}）</span></div>
 <div><b>{e(r['plan_progress'])}</b><span>Plan 进度</span></div>
 <div><b>{e(str(a.get('ai_code_ratio', '—')))}</b><span>AI 代码占比（自评）</span></div>
</div>
<p>Token：{e(fmt_tok(r['tokens']))} · AI 用时 {e(str(a.get('ai_dev_hours', '—')))}h / 人工预估 {e(str(a.get('manual_dev_hours', '—')))}h</p>
<table><thead><tr><th>阶段</th><th>分钟</th><th>轮次</th><th>介入</th><th>介入类型</th><th>使用的 skill</th></tr></thead><tbody>{srows}</tbody></table>
<h3>返工</h3><ul>{rw}</ul></section>""")
    doc = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>研发效率报告</title><style>
:root{{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e4e4df;--accent:#2f6f5e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151614;--fg:#e9e9e4;--muted:#9a9a93;--card:#1e1f1c;--line:#33342f;--accent:#7cc4ad}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"PingFang SC",sans-serif}}
main{{max-width:980px;margin:auto}} .card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin:16px 0}}
.muted{{color:var(--muted);margin-top:-8px}} .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:12px 0}}
.kpis div{{border:1px solid var(--line);border-radius:8px;padding:8px 10px}} .kpis b{{display:block;font-size:22px;color:var(--accent)}}
.kpis span{{font-size:12px;color:var(--muted)}} table{{width:100%;border-collapse:collapse;font-size:13px;display:block;overflow-x:auto}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;white-space:nowrap}}
</style></head><body><main><h1>研发效率报告</h1><p class="muted">生成于 {datetime.now().strftime(FMT)} · 数据只来自本仓库与本机会话记录</p>
{''.join(cards) or '<p>没有找到 eval-log.json。</p>'}</main></body></html>"""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root")
    p.add_argument("--feature")
    p.add_argument("--no-tokens", action="store_true")
    p.add_argument("--out")
    a = p.parse_args()
    root = a.root or subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
    logs = sorted(glob.glob(os.path.join(root, "docs/features/active/*/eval-log.json")) +
                  glob.glob(os.path.join(root, "docs/features/completed/*/*/eval-log.json")))
    if a.feature:
        logs = [x for x in logs if os.path.basename(os.path.dirname(x)) == a.feature]
    rows = [summarize(root, x, not a.no_tokens) for x in logs]
    out = a.out or os.path.join(root, "docs", "eval", f"{datetime.now():%Y-%m-%d}-report.html")
    render_html(rows, out)
    print(f"| 需求 | 阶段耗时(min) | 介入 | 返工 | CR | Plan | Token |\n|---|---|---|---|---|---|---|")
    for r in rows:
        cr = r["cr"] or {}
        print(f"| {r['feature']} | {r['total_minutes']} | {r['interventions']} | {len(r['rework'])} | "
              f"{cr.get('result', '—')} {cr.get('score', '')} | {r['plan_progress']} | {fmt_tok(r['tokens'])} |")
    print(f"\n报告：{os.path.relpath(out, root)}")


if __name__ == "__main__":
    main()
