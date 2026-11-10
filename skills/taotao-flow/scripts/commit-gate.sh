#!/usr/bin/env bash
# taotao-flow 提交门禁的机械检查：CR 结论 + 本地扫描结果 + 范围一致性 + 敏感信息。
#
# 用法: commit-gate.sh [PROJECT_ROOT] [--range BASE..HEAD] [--feature NAME]
#   --range    待推送范围（git pre-push hook 传入）。不传时自动计算：
#              有 upstream → upstream..HEAD；没有 → merge-base(<主干>)..HEAD（首次推送也会扫已提交内容）
# 输出一段 JSON；verdict 取值见 hooks/before_commit.md。脚本自身出错时输出 verdict=block_gate_error（失败即拦截）。
set -uo pipefail

ROOT=""; RANGE=""; FEATURE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --range) RANGE="$2"; shift ;;
    --feature) FEATURE="$2"; shift ;;
    *) ROOT="$1" ;;
  esac
  shift
done
ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)}"
cd "$ROOT" || { echo '{"verdict":"block_gate_error","error":"无法进入项目目录"}'; exit 0; }

python3 - "$ROOT" "$RANGE" "$FEATURE" <<'PY' || echo '{"verdict":"block_gate_error","error":"门禁脚本异常退出"}'
import glob, json, os, re, subprocess, sys, traceback

root, rng, feature = sys.argv[1], sys.argv[2], sys.argv[3]
SEC_TOOLS = ("gosec", "govulncheck")
HARD_TOOLS = ("build", "vet")


def sh(*a):
    p = subprocess.run(a, cwd=root, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else ""


def ok(*a):
    return subprocess.run(a, cwd=root, capture_output=True).returncode == 0


def trunk():
    for b in ("origin/master", "origin/main", "master", "main"):
        if ok("git", "rev-parse", "--verify", "-q", b):
            return b
    return ""


def main():
    global rng
    branch = sh("git", "branch", "--show-current").strip()
    head = sh("git", "rev-parse", "--short", "HEAD").strip()
    res = {"branch": branch, "head": head, "range": None, "cr": None, "cr_path": None, "cr_problems": [],
           "checks": None, "scope": {}, "sensitive": [], "debug_leftovers": []}

    # ---------- 1. 找当前分支的 CR 结论（只认 branch 匹配、headCommit 可达的那份） ----------
    cands = []
    if feature:
        cands.append(os.path.join(root, "docs/features/active", feature, "cr-status.json"))
    cands += glob.glob(os.path.join(root, "docs/features/active/*/cr-status.json"))
    cands.append(os.path.join(root, ".taotao/cr-status.json"))
    chosen, invalid = None, []
    for c in dict.fromkeys(cands):
        if not os.path.exists(c):
            continue
        rel = os.path.relpath(c, root)
        try:
            cr = json.load(open(c, encoding="utf-8"))
            if not isinstance(cr, dict):
                raise ValueError("不是 JSON 对象")
        except Exception as e:                       # 损坏的结论文件：失败即拦截
            invalid.append(f"{rel}: 无法解析（{e.__class__.__name__}）")
            continue
        if cr.get("branch") and cr["branch"] != branch:
            continue                                 # 别的需求/分支的结论，不认
        if not cr.get("branch"):
            res["cr_problems"].append(f"{rel}: 缺少 branch 字段（旧格式），请重跑 tt:cr")
            continue
        hc = cr.get("headCommit") or ""
        if hc and not ok("git", "merge-base", "--is-ancestor", hc, "HEAD"):
            res["cr_problems"].append(f"{rel}: headCommit {hc} 不在当前分支历史中")
            continue
        if chosen is None or os.path.getmtime(c) > os.path.getmtime(chosen[0]):
            chosen = (c, cr)
    if chosen:
        c, cr = chosen
        res["cr_path"] = os.path.relpath(c, root)
        result = str(cr.get("result", "")).strip().lower()
        res["cr"] = {"result": result, "blockerCount": cr.get("blockerCount"), "warnCount": cr.get("warnCount"),
                     "score": cr.get("score"), "mode": cr.get("mode"), "headCommit": cr.get("headCommit"),
                     "commitReady": cr.get("commitReady"), "timestamp": cr.get("timestamp"), "tools": cr.get("tools")}
        if result not in ("pass", "conditional_pass", "fail"):
            res["cr_problems"].append(f"{res['cr_path']}: result 非法（{cr.get('result')!r}）")
        if cr.get("commitReady") is False and result != "fail":
            res["cr_problems"].append(f"{res['cr_path']}: commitReady=false")
        reviewed = cr.get("files") or []
        if isinstance(reviewed, dict):
            reviewed = sum(reviewed.values(), [])
        hc = cr.get("headCommit") or ""
        since = set(sh("git", "diff", "--name-only", f"{hc}..HEAD").split()) if hc and hc != head else set()
        since |= set(sh("git", "diff", "--name-only", "HEAD").split())          # 已暂存 + 未暂存
        res["scope"] = {"cr_head": hc, "changed_after_cr": sorted(f for f in since if f.endswith(".go"))}
    if invalid and not chosen:
        res["cr_problems"] += invalid

    # ---------- 2. 本地扫描结果（go-check.sh 写入 .taotao/last-check.json） ----------
    lc = os.path.join(root, ".taotao/last-check.json")
    if os.path.exists(lc):
        try:
            d = json.load(open(lc, encoding="utf-8"))
            r = d.get("results", {})
            res["checks"] = {"head": d.get("head"), "current": d.get("head") == head and not d.get("dirty"),
                             "hard_failed": [k for k in HARD_TOOLS if r.get(k) == "fail"] +
                                            [k for k in SEC_TOOLS if r.get(k) == "fail_high"],
                             "skipped": [k for k in SEC_TOOLS if r.get(k) in ("skipped", "error")], "results": r}
        except Exception as e:
            res["checks"] = {"invalid": f"无法解析（{e.__class__.__name__}）"}

    # ---------- 3. 敏感信息：暂存/未暂存改动 + 待推送范围内的提交 ----------
    if not rng:
        up = sh("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}").strip()
        if up:
            rng = f"{up}..HEAD"
        else:
            t = trunk()
            mb = sh("git", "merge-base", "HEAD", t).strip() if t else ""
            if mb and mb != sh("git", "rev-parse", "HEAD").strip():
                rng = f"{mb}..HEAD"
            elif not t:                              # 没有主干（新仓库）：扫全部提交
                rng = "HEAD"
    res["range"] = rng or None
    diff = sh("git", "diff", "HEAD", "-U0") or sh("git", "diff", "--cached", "-U0")
    if rng:
        diff += sh("git", "log", "-p", "-U0", "--no-merges", "--format=", rng)

    secret = re.compile(r'(?i)\b(\w*(?:token|secret|api[_-]?key|access[_-]?key|passw(?:or)?d|pwd)\w*|ak|sk)\b["\']?\s*(?::=|=|:)\s*["\'`]([^"\'`\s]{6,})["\'`]')
    placeholder = re.compile(r'(?i)^(x{3,}|your[-_].*|<.+>|\$\{.+\}|changeme|placeholder|example.*|dummy.*|test|mock|fake|redacted)$')
    bearer = re.compile(r'(?i)bearer\s+[A-Za-z0-9._\-]{16,}')
    privkey = re.compile(r'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY')
    innerip = re.compile(r'(?<![\d.])(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})(?![\d.])')
    debug = re.compile(r'\b(fmt\.Println|spew\.Dump|pp\.Println)\(')
    cur, seen = None, set()
    for line in diff.splitlines():
        if line.startswith("+++ "):
            cur = line[6:] if line.startswith("+++ b/") else None
            continue
        if not line.startswith("+") or line.startswith("+++") or cur is None:
            continue
        body = line[1:]
        hits = []
        m = secret.search(body)
        if m and not placeholder.match(m.group(2)):
            hits.append(("credential", m.group(1)))
        if bearer.search(body):
            hits.append(("bearer_token", ""))
        if privkey.search(body):
            hits.append(("private_key", ""))
        if innerip.search(body) and not cur.endswith("_test.go"):
            hits.append(("internal_ip", ""))
        for t, k in hits:
            if (cur, t, k) not in seen:
                seen.add((cur, t, k))
                res["sensitive"].append({"file": cur, "type": t, "key": k})
        if debug.search(body) and cur.endswith(".go") and not cur.endswith("_test.go") and "/cmd/" not in f"/{cur}":
            res["debug_leftovers"].append({"file": cur, "snippet": body.strip()[:80]})

    # ---------- 4. 判定（敏感信息 > 结论文件异常 > 无 CR > CR 失败 > 扫描失败 > CR 后改动 > 警告） ----------
    ch = res["checks"] or {}
    if res["sensitive"]:
        v = "block_sensitive"
    elif res["cr_problems"] and not res["cr"]:
        v = "block_invalid_cr" if invalid else ("soft_no_cr" if re.search(r"(^|/)(fix|hotfix)/", branch) else "block_no_cr")
    elif res["cr"] is None:
        v = "soft_no_cr" if re.search(r"(^|/)(fix|hotfix)/", branch) else "block_no_cr"
    elif res["cr_problems"]:
        v = "block_invalid_cr"
    elif res["cr"]["result"] == "fail":
        v = "block_cr_failed"
    elif ch.get("invalid") or (ch.get("current") and ch.get("hard_failed")):
        v = "block_checks_failed"
    elif res["scope"].get("changed_after_cr"):
        v = "block_changed_after_cr"
    elif res["debug_leftovers"] or not ch or not ch.get("current") or ch.get("skipped"):
        v = "warn"
    else:
        v = "pass"
    res["verdict"] = v
    warnings = []
    if res["debug_leftovers"]:
        warnings.append(f"调试残留 {len(res['debug_leftovers'])} 处")
    if not ch:
        warnings.append("当前 HEAD 没有本地扫描记录（go-check.sh 未运行）")
    elif not ch.get("invalid") and not ch.get("current"):
        warnings.append("本地扫描不是在当前 HEAD 上跑的，结果可能过期")
    if ch.get("skipped"):
        warnings.append("安全扫描被跳过: " + ", ".join(ch["skipped"]))
    res["warnings"] = warnings
    return res


try:
    print(json.dumps(main(), ensure_ascii=False, indent=2))
except Exception:
    print(json.dumps({"verdict": "block_gate_error", "error": traceback.format_exc()[-400:]}, ensure_ascii=False))
PY
