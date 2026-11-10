#!/usr/bin/env python3
"""taotao-flow 测试证据：按任务记录 TDD 证据，并供 tt:cr 逐任务核验。

证据由本脚本**实际运行测试**后写入，不接受手填结果：
  docs/features/<active|completed>/.../<需求>/tdd-evidence.jsonl（追加写，每条带前一条的哈希，改动会被发现）

子命令
  red      --feature F --task N --cmd "go test ./pkg -run '^TestX$'" --expect "<预期失败原因正则>"
           改动前运行：必须失败，且失败原因与 --expect 吻合；环境故障、无关测试失败、没跑到测试都不算有效红灯
  green    --feature F --task N
           改动后重跑同一条命令：目标测试必须通过，且代码相对红灯时确有变化
  baseline --feature F --task N --cmd "go test ./pkg -run '^TestY'"
           纯重构改动前：同一组行为测试必须通过
  after    --feature F --task N
           纯重构改动后：重跑 baseline 命令，原来通过的测试仍全部通过，且代码确有变化
  verify   --feature F --task N --cmd "..." --label 入口|集成|并发|其他
           实现后补的测试：计入验证，标明「实现后执行」，不能当作红灯
  check    --feature F [--plan PATH] [--json]
           按 Plan 中每个任务的 **TDD:** 类型逐任务核验；有任务未验证时退出码为 1
  show     --feature F [--task N]

约定
  - red / green / baseline / after 必须是 `go test` 命令，红灯与绿灯还必须用 -run 限定目标测试，
    这样才能区分「目标测试按预期失败」和「别的测试碰巧失败」。
  - 代码状态用工作区树哈希判断（排除 docs/features 与 .taotao），不要求每步都提交。
  - Plan 任务类型：**TDD:** bugfix | behavior | refactor | none — <none 时写原因>
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime

ENV_PATTERNS = [
    r"dial tcp", r"connection refused", r"no such host", r"i/o timeout", r"TLS handshake timeout",
    r"cannot find module providing package", r"go: downloading .*(error|failed)", r"verifying module",
    r"go: errors parsing go\.mod", r"permission denied", r"Cannot connect to the Docker daemon",
    r"panic: test timed out", r"signal: killed", r"no Go files in", r"matched no packages",
    r"\[setup failed\]", r"directory not found", r"is not in std", r"go: command not found",
    r"command not found", r"no space left on device", r"too many open files",
]
EXCLUDE = [":(exclude)docs/features", ":(exclude).taotao", ":(exclude).superpowers"]
STEPS_RED_GREEN = ("red", "green")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def git(root, *a, env=None):
    p = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=env)
    return p.stdout.strip() if p.returncode == 0 else ""


def code_tree(root):
    """工作区代码状态的树哈希（含未提交与未跟踪文件，排除证据与流程目录）。"""
    gitdir = git(root, "rev-parse", "--absolute-git-dir")
    if not gitdir:
        return ""
    with tempfile.TemporaryDirectory() as td:
        idx = os.path.join(td, "index")
        src = os.path.join(gitdir, "index")
        if os.path.exists(src):
            with open(src, "rb") as a, open(idx, "wb") as b:
                b.write(a.read())
        env = {**os.environ, "GIT_INDEX_FILE": idx}
        subprocess.run(["git", "add", "-A", "--", ".", *EXCLUDE], cwd=root, capture_output=True, env=env)
        return git(root, "write-tree", env=env)


def feature_dir(root, feature):
    active = os.path.join(root, "docs", "features", "active", feature)
    if os.path.isdir(active):
        return active
    done = sorted(glob.glob(os.path.join(root, "docs", "features", "completed", "*", feature)))
    if done:
        return done[-1]
    os.makedirs(active, exist_ok=True)
    return active


def rec_hash(rec):
    body = {k: v for k, v in rec.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def append(path, rec, records):
    rec["seq"] = len(records) + 1
    rec["prev_hash"] = records[-1]["hash"] if records else ""
    rec["hash"] = rec_hash(rec)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def chain_ok(records):
    prev = ""
    for r in records:
        if r.get("prev_hash") != prev or rec_hash(r) != r.get("hash"):
            return False, r.get("seq")
        prev = r["hash"]
    return True, None


# ---------------------------------------------------------------- 运行 go test 并解析
def parse_cmd(cmd):
    try:
        argv = shlex.split(cmd)
    except ValueError as e:
        return None, None, f"命令无法解析：{e}"
    if len(argv) < 2 or os.path.basename(argv[0]) != "go" or argv[1] != "test":
        return None, None, "必须是 go test 命令"
    run = None
    for i, a in enumerate(argv):
        if a == "-run" and i + 1 < len(argv):
            run = argv[i + 1]
        elif a.startswith("-run="):
            run = a.split("=", 1)[1]
    return argv, run, None


def run_go_test(root, cmd):
    argv, run, err = parse_cmd(cmd)
    if err:
        return {"error": err}
    real = argv[:2] + ["-json"] + argv[2:] if "-json" not in argv else argv
    t0 = time.time()
    p = subprocess.run(real, cwd=root, capture_output=True, text=True)
    dur = round(time.time() - t0, 2)
    tests, outputs, build = {}, {}, []
    for line in (p.stdout + "\n" + p.stderr).splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            if line.strip():
                build.append(line)
            continue
        if not isinstance(ev, dict):
            continue
        act, name = ev.get("Action"), ev.get("Test")
        if act in ("build-output",) and ev.get("Output"):
            build.append(ev["Output"].rstrip("\n"))
            continue
        if name:
            if act in ("pass", "fail", "skip"):
                tests[name] = act
            if act == "output":
                outputs.setdefault(name, []).append(ev.get("Output", ""))
        elif act == "output" and ev.get("Output"):
            out = ev["Output"]
            if not re.match(r"^(ok|FAIL|PASS|\?)\s", out) and out.strip() not in ("PASS", "FAIL"):
                build.append(out.rstrip("\n"))
    text = "\n".join(build) + "\n" + "".join("".join(v) for v in outputs.values())
    return {"argv": real, "run": run, "exit_code": p.returncode, "duration_s": dur, "tests": tests,
            "outputs": {k: "".join(v) for k, v in outputs.items()}, "build": build, "text": text}


def top(name):
    return name.split("/", 1)[0]


def targeted(run, name):
    if not run:
        return False
    first = run.split("/", 1)[0]
    try:
        return re.search(first, top(name)) is not None
    except re.error:
        return False


def tail(text, n=40):
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines[-n:])


def env_failure(text):
    for pat in ENV_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def summarize(r):
    t = r["tests"]
    return {"passed": sorted(k for k, v in t.items() if v == "pass"),
            "failed": sorted(k for k, v in t.items() if v == "fail"),
            "skipped": sorted(k for k, v in t.items() if v == "skip")}


# ---------------------------------------------------------------- 判定
def judge_red(r, expect):
    reasons = []
    if r.get("error"):
        return False, [r["error"]], None
    if not r["run"]:
        return False, ["红灯命令必须用 -run 限定目标测试，否则无法排除无关测试失败"], None
    if r["exit_code"] == 0:
        return False, ["测试在改动前就通过了，不是红灯"], None
    env = env_failure(r["text"])
    if env:
        return False, [f"环境故障，不算红灯：{env}"], None
    s = summarize(r)
    failed_leaf = [n for n in s["failed"] if not any(o != n and o.startswith(n + "/") for o in s["failed"])]
    unrelated = sorted({top(n) for n in failed_leaf if not targeted(r["run"], n)})
    if unrelated:
        reasons.append("无关测试失败：" + ", ".join(unrelated))
    try:
        rx = re.compile(expect)
    except re.error as e:
        return False, [f"--expect 不是合法正则：{e}"], None
    target_failed = [n for n in failed_leaf if targeted(r["run"], n)]
    kind = None
    if target_failed:
        matched = [n for n in target_failed if rx.search(r["outputs"].get(n, ""))]
        others = [n for n in target_failed if n not in matched]
        if not matched:
            reasons.append("目标测试失败了，但失败输出与预期失败原因不符（可能是无关断言或 panic）")
        elif others:
            reasons.append("同一命令中还有测试因其他原因失败：" + ", ".join(others[:5]))
        else:
            kind = "assertion"
    elif r["build"] and not s["passed"] and not s["failed"]:
        if rx.search("\n".join(r["build"])):
            kind = "compile"
        else:
            reasons.append("编译失败，且编译错误与预期失败原因不符")
    else:
        reasons.append("目标测试没有失败（可能 -run 没匹配到任何测试）")
    return (not reasons and kind is not None), reasons, kind


def judge_green(r):
    if r.get("error"):
        return False, [r["error"]]
    s = summarize(r)
    reasons = []
    if r["exit_code"] != 0:
        reasons.append(f"测试仍然失败（exit {r['exit_code']}）" + (f"：{', '.join(s['failed'][:5])}" if s["failed"] else ""))
    if not [n for n in s["passed"] if targeted(r["run"], n)]:
        reasons.append("没有目标测试通过（被跳过或 -run 未匹配）")
    return not reasons, reasons


def judge_pass_set(r, need=None):
    if r.get("error"):
        return False, [r["error"]]
    s = summarize(r)
    reasons = []
    if r["exit_code"] != 0:
        reasons.append("测试未全部通过：" + ", ".join(s["failed"][:5]))
    if not s["passed"]:
        reasons.append("没有任何测试实际执行通过")
    if need:
        lost = sorted(set(need) - set(s["passed"]))
        if lost:
            reasons.append("改动前通过、改动后不再通过的测试：" + ", ".join(lost[:8]))
    return not reasons, reasons


# ---------------------------------------------------------------- 子命令
def base_record(args, step, cmd, r, root):
    return {"at": now(), "task": str(args.task), "step": step, "cmd": cmd,
            "head": git(root, "rev-parse", "--short", "HEAD"), "tree": code_tree(root),
            "exit_code": r.get("exit_code"), "duration_s": r.get("duration_s"),
            "tests": summarize(r) if "tests" in r else None,
            "output_tail": tail(r.get("text", r.get("error", ""))),
            "output_sha256": hashlib.sha256(r.get("text", "").encode()).hexdigest()}


def last(records, task, step, valid=None):
    for rec in reversed(records):
        if rec["task"] == str(task) and rec["step"] == step and (valid is None or rec.get("valid") == valid):
            return rec
    return None


def cmd_record(args, root, path, records):
    step = args.cmd_name
    if step in ("red", "baseline", "verify") and not args.cmd:
        sys.exit("--cmd 必填")
    if step == "red" and not args.expect:
        sys.exit("--expect 必填：写出预期的失败原因（正则），例如 'want ErrNotCancelable'")
    if step == "green":
        red = last(records, args.task, "red", valid=True)
        if not red:
            prev = last(records, args.task, "red")
            sys.exit("没有有效的红灯记录，不能记绿灯" + (f"（最近一次红灯无效：{'；'.join(prev['reasons'])}）" if prev else "") +
                     "。如果测试是实现之后才补的，用 verify 记录，tt:cr 会标记为 TDD 未验证。")
        cmd = red["cmd"]
    elif step == "after":
        base = last(records, args.task, "baseline", valid=True)
        if not base:
            sys.exit("没有有效的 baseline 记录（纯重构须在改动前先跑 baseline）")
        cmd = base["cmd"]
    else:
        cmd = args.cmd

    r = run_go_test(root, cmd)
    rec = base_record(args, step, cmd, r, root)
    if step == "red":
        ok, reasons, kind = judge_red(r, args.expect)
        rec.update(expect=args.expect, red_kind=kind)
    elif step == "green":
        ok, reasons = judge_green(r)
        if ok and rec["tree"] and rec["tree"] == red["tree"]:
            ok, reasons = False, ["代码与红灯时完全相同，没有看到实现改动"]
        rec.update(red_seq=red["seq"])
    elif step == "baseline":
        ok, reasons = judge_pass_set(r)
    elif step == "after":
        ok, reasons = judge_pass_set(r, need=base["tests"]["passed"])
        if ok and rec["tree"] and rec["tree"] == base["tree"]:
            ok, reasons = False, ["代码与 baseline 时完全相同，没有看到重构改动"]
        rec.update(baseline_seq=base["seq"])
    else:  # verify
        ok, reasons = judge_pass_set(r)
        rec.update(label=args.label or "其他", phase="post_impl")
    rec.update(valid=ok, reasons=reasons)
    rec = append(path, rec, records)
    mark = "✓" if ok else "✗"
    print(f"{mark} Task {rec['task']} {step} #{rec['seq']}  exit={rec['exit_code']}  {'；'.join(reasons) if reasons else '有效'}")
    if step == "red" and ok:
        print(f"  红灯类型：{rec['red_kind']}；预期原因已匹配：{args.expect}")
    print(f"  已写入 {os.path.relpath(path, root)}")
    sys.exit(0 if ok else 1)


def plan_tasks(plan_path):
    tasks = []
    if not plan_path or not os.path.exists(plan_path):
        return tasks
    text = open(plan_path, encoding="utf-8").read()
    text_nocode = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    heads = list(re.finditer(r"^#{2,4}\s+Task\s+([0-9A-Za-z.\-]+)\s*:?\s*(.*)$", text_nocode, re.M))
    for i, m in enumerate(heads):
        body = text_nocode[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text_nocode)]
        t = re.search(r"\*\*TDD[:：]\*\*\s*`?([A-Za-z]+)`?\s*(?:[—\-:：]\s*(.*))?", body)
        tasks.append({"task": m.group(1), "title": m.group(2).strip(),
                      "tdd": (t.group(1).lower() if t else None), "tdd_note": (t.group(2) or "").strip() if t else ""})
    return tasks


def check_task(t, recs, root):
    kind = t["tdd"] or "behavior"
    notes = [] if t["tdd"] else ["Plan 未声明 TDD 类型，按 behavior 检查"]
    mine = [r for r in recs if r["task"] == t["task"]]
    posts = [r for r in mine if r["step"] == "verify"]
    post_desc = [f"实现后补测（{r.get('label')}，执行于 {r['at']}，{'通过' if r['valid'] else '未通过'}）" for r in posts]
    stale = [r["seq"] for r in mine if r.get("head") and not ancestor(root, r["head"])]
    if stale:
        notes.append("以下证据来自当前分支历史之外的提交：#" + ", #".join(map(str, stale)))

    if kind == "none":
        ok = bool(t["tdd_note"])
        return {"status": "不适用" if ok else "TDD 未验证", "kind": kind,
                "missing": [] if ok else ["none 类型必须写明不需要测试的原因"], "notes": notes, "post_impl": post_desc}

    missing, evidence = [], {}
    if kind in ("bugfix", "behavior"):
        reds = [r for r in mine if r["step"] == "red"]
        good_red = next((r for r in reversed(reds) if r.get("valid")), None)
        if not reds:
            missing += ["测试命令", "预期失败原因", "改动前失败结果", "改动后通过结果"]
        elif not good_red:
            missing.append("改动前失败结果无效：" + "；".join(reds[-1].get("reasons") or []))
        if good_red:
            evidence["red"] = f"#{good_red['seq']} {good_red['at']} {good_red['red_kind']} 失败，预期原因 /{good_red['expect']}/ 已匹配"
            greens = [r for r in mine if r["step"] == "green" and r.get("red_seq") == good_red["seq"]]
            good_green = next((r for r in reversed(greens) if r.get("valid")), None)
            if good_green and good_green["seq"] > good_red["seq"] and good_green["cmd"] == good_red["cmd"]:
                evidence["green"] = f"#{good_green['seq']} {good_green['at']} 同一命令通过"
            elif greens:
                missing.append("改动后通过结果无效：" + "；".join(greens[-1].get("reasons") or []))
            else:
                missing.append("改动后通过结果")
            evidence["cmd"] = good_red["cmd"]
    elif kind == "refactor":
        bases = [r for r in mine if r["step"] == "baseline"]
        good_base = next((r for r in reversed(bases) if r.get("valid")), None)
        if not bases:
            missing += ["测试命令", "改动前通过结果（baseline）", "改动后通过结果"]
        elif not good_base:
            missing.append("改动前通过结果无效：" + "；".join(bases[-1].get("reasons") or []))
        if good_base:
            evidence["baseline"] = f"#{good_base['seq']} {good_base['at']} {len(good_base['tests']['passed'])} 个测试通过"
            afters = [r for r in mine if r["step"] == "after" and r.get("baseline_seq") == good_base["seq"]]
            good_after = next((r for r in reversed(afters) if r.get("valid")), None)
            if good_after:
                evidence["after"] = f"#{good_after['seq']} {good_after['at']} 同一组测试仍全部通过"
            elif afters:
                missing.append("改动后通过结果无效：" + "；".join(afters[-1].get("reasons") or []))
            else:
                missing.append("改动后通过结果")
            evidence["cmd"] = good_base["cmd"]
    else:
        missing.append(f"未知的 TDD 类型：{kind}")

    if missing and posts:
        notes.append("实现后补的测试只计入验证，不能代替改动前的记录")
    return {"status": "TDD 未验证" if missing or stale else "TDD 已验证", "kind": kind, "missing": missing,
            "evidence": evidence, "notes": notes, "post_impl": post_desc}


def ancestor(root, sha):
    return subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"], cwd=root, capture_output=True).returncode == 0


def cmd_check(args, root, path, records):
    ok_chain, bad = chain_ok(records)
    fdir = os.path.dirname(path)
    plan = args.plan or next(iter(sorted(glob.glob(os.path.join(fdir, "Plan-*.md")))), None)
    tasks = plan_tasks(plan)
    if not tasks:
        tasks = [{"task": t, "title": "", "tdd": None, "tdd_note": ""} for t in dict.fromkeys(r["task"] for r in records)]
    results = []
    for t in tasks:
        res = check_task(t, records, root)
        if not ok_chain:
            res["status"] = "TDD 未验证"
            res["missing"] = [f"证据文件在第 {bad} 条处被改动或顺序被破坏，全部证据作废"] + res["missing"]
        results.append({"task": t["task"], "title": t["title"], **res})
    unverified = [r for r in results if r["status"] == "TDD 未验证"]
    out = {"feature": args.feature, "plan": os.path.relpath(plan, root) if plan else None,
           "evidence_file": os.path.relpath(path, root), "chain_ok": ok_chain, "tasks": results,
           "summary": {"verified": sum(r["status"] == "TDD 已验证" for r in results),
                       "not_applicable": sum(r["status"] == "不适用" for r in results),
                       "unverified": len(unverified)},
           "note": "全仓测试通过不能替代逐任务证据"}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"## TDD 证据核验（{args.feature}）\n")
        print(f"Plan：{out['plan'] or '未找到，按证据文件中的任务核验'} · 证据：{out['evidence_file']} · 哈希链：{'完整' if ok_chain else '已损坏'}\n")
        print("| 任务 | 类型 | 结论 | 证据 / 缺项 |\n|---|---|---|---|")
        for r in results:
            detail = "；".join(r["missing"]) if r["missing"] else "；".join(f"{k}: {v}" for k, v in r.get("evidence", {}).items() if k != "cmd")
            extra = "；".join(r["notes"] + r["post_impl"])
            print(f"| Task {r['task']} {r['title'][:24]} | {r['kind']} | {r['status']} | {detail}{('；' + extra) if extra else ''} |")
        s = out["summary"]
        print(f"\n已验证 {s['verified']} · 不适用 {s['not_applicable']} · 未验证 {s['unverified']}。{out['note']}。")
    sys.exit(1 if unverified else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd_name", choices=["red", "green", "baseline", "after", "verify", "check", "show"])
    p.add_argument("--root")
    p.add_argument("--feature", required=True)
    p.add_argument("--task")
    p.add_argument("--cmd")
    p.add_argument("--expect")
    p.add_argument("--label")
    p.add_argument("--plan")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    root = a.root or git(os.getcwd(), "rev-parse", "--show-toplevel") or os.getcwd()
    path = os.path.join(feature_dir(root, a.feature), "tdd-evidence.jsonl")
    records = load(path)
    if a.cmd_name == "check":
        return cmd_check(a, root, path, records)
    if a.cmd_name == "show":
        rs = [r for r in records if not a.task or r["task"] == str(a.task)]
        print(json.dumps(rs, ensure_ascii=False, indent=2))
        return
    if not a.task:
        sys.exit("--task 必填")
    return cmd_record(a, root, path, records)


if __name__ == "__main__":
    main()
