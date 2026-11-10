#!/usr/bin/env python3
"""taotao-flow 效率日志：维护 docs/features/<active|completed>/.../<需求>/eval-log.json。

替代 soda 的 eval-logger skill：阶段计时、人工介入、返工、归档自评全部落在需求目录，
不上传任何地方。token 由 eval-report.py 从本机 Claude Code / Codex 会话记录统计。

用法（在项目根目录执行，或用 --root 指定）：
  eval-log.py start    --feature F --stage ard
  eval-log.py confirm  --feature F --stage ard [--skills a,b] [--rounds 3] [--extra '{"k":1}']
  eval-log.py note     --feature F --stage ard --type clarify --q "问题" --a "回答摘要" [--action "AI 动作"]
  eval-log.py rework   --feature F --cause prd_change --reason "…" [--files a.go,b.go] [--docs ARD,Design]
  eval-log.py assess   --feature F [--manual-hours 16] [--ai-ratio 0.6] [--notes "…"]
  eval-log.py show     --feature F

stage 取值：ard design plan test impl cr fix sync archive
note 的 type：adjust（调整方向）supplement（补充信息）correct（纠错）clarify（澄清）
rework 的 cause：prd_change api_change cr_finding test_finding user_pivot
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from datetime import datetime

STAGES = ["ard", "design", "plan", "test", "impl", "cr", "fix", "sync", "archive"]
NOTE_TYPES = ["adjust", "supplement", "correct", "clarify"]
CAUSES = ["prd_change", "api_change", "cr_finding", "test_finding", "user_pivot"]


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_dir(root, feature):
    active = os.path.join(root, "docs", "features", "active", feature)
    if os.path.isdir(active):
        return active
    done = sorted(glob.glob(os.path.join(root, "docs", "features", "completed", "*", feature)))
    if done:
        return done[-1]
    os.makedirs(active, exist_ok=True)
    return active


def load(path, feature):
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
    return {"feature": feature, "branch": branch, "created_at": now(), "stages": {}, "rework_log": [], "archive_assessment": None}


def save(path, data):
    tmp = path + ".tmp"
    json.dump(data, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def stage(data, name):
    return data["stages"].setdefault(name, {"started_at": None, "confirmed_at": None, "skills_used": [],
                                            "total_rounds": None, "interventions": [], "extra": {}})


def hours(a, b):
    fmt = "%Y-%m-%d %H:%M:%S"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 3600


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["start", "confirm", "note", "rework", "assess", "show"])
    p.add_argument("--root", default=None)
    p.add_argument("--feature", required=True)
    p.add_argument("--stage", choices=STAGES)
    p.add_argument("--skills", default="")
    p.add_argument("--rounds", type=int)
    p.add_argument("--extra", default="")
    p.add_argument("--type", choices=NOTE_TYPES)
    p.add_argument("--q", default="")
    p.add_argument("--a", default="")
    p.add_argument("--action", default="")
    p.add_argument("--cause", choices=CAUSES)
    p.add_argument("--reason", default="")
    p.add_argument("--files", default="")
    p.add_argument("--docs", default="")
    p.add_argument("--manual-hours", type=float)
    p.add_argument("--ai-ratio", type=float)
    p.add_argument("--notes", default="")
    a = p.parse_args()

    root = a.root or subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
    path = os.path.join(find_dir(root, a.feature), "eval-log.json")
    data = load(path, a.feature)

    if a.cmd in ("start", "confirm", "note") and not a.stage:
        sys.exit("--stage 必填")

    if a.cmd == "start":
        s = stage(data, a.stage)
        if not s["started_at"]:          # 重复 start（断点续做）不覆盖首次开始时间
            s["started_at"] = now()
    elif a.cmd == "confirm":
        s = stage(data, a.stage)
        s["started_at"] = s["started_at"] or now()
        s["confirmed_at"] = now()
        if a.skills:
            s["skills_used"] = sorted(set(s["skills_used"]) | set(x.strip() for x in a.skills.split(",") if x.strip()))
        if a.rounds is not None:
            s["total_rounds"] = a.rounds
        if a.extra:
            s["extra"].update(json.loads(a.extra))
    elif a.cmd == "note":
        if not a.type:
            sys.exit("--type 必填")
        s = stage(data, a.stage)
        s["interventions"].append({"at": now(), "type": a.type, "question": a.q[:500], "input": a.a[:120], "ai_action": a.action[:120]})
    elif a.cmd == "rework":
        if not a.cause:
            sys.exit("--cause 必填")
        files = [x for x in a.files.split(",") if x]
        impact = "light" if len(files) <= 1 else "medium" if len(files) <= 3 else "heavy"
        data["rework_log"].append({"at": now(), "cause": a.cause, "reason": a.reason[:100], "files_changed": files,
                                   "impact": impact, "doc_synced": [x for x in a.docs.split(",") if x]})
    elif a.cmd == "assess":
        ai_hours = round(sum(hours(s["started_at"], s["confirmed_at"]) for s in data["stages"].values()
                             if s.get("started_at") and s.get("confirmed_at")), 1)
        data["archive_assessment"] = {"ai_dev_hours": ai_hours, "manual_dev_hours": a.manual_hours,
                                      "ai_code_ratio": a.ai_ratio, "notes": a.notes, "completed_at": now()[:10]}

    if a.cmd != "show":
        save(path, data)
    print(json.dumps(data if a.cmd == "show" else {"ok": True, "file": os.path.relpath(path, root)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
