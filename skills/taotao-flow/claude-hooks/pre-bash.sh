#!/usr/bin/env bash
# Claude Code PreToolUse hook（Bash）：提交门禁的提前拦截点（git 原生 pre-push hook 是最后一道）。
#
# 识别方式：对命令做词法切分，识别任意位置的 git 子命令（含 bash -c '…'、/usr/bin/git、git -C/-c/--no-pager 等全局参数）
# 以及 gh pr create / gh pr merge。
#   - push、gh pr create/merge、主干上的 commit、主干上的 merge  → 完整门禁
#   - 功能分支上的 commit（tt:impl 逐任务提交）                  → 只拦敏感信息
#   - 功能分支上 merge 主干（同步主干）                          → 放行
# 紧急通道：命令以 TAOTAO_GATE=off 开头（如 `TAOTAO_GATE=off git push`）→ 跳过 CR 与扫描检查，
#   敏感信息仍然拦截，并在 .taotao/gate-audit.log 留记录。
# 输出：拦截 = exit 2 + stderr（反馈给 Claude）；需要用户知情的警告 = JSON permissionDecision "ask"（弹给用户确认）；
#   门禁脚本本身出错 = 拦截（失败即拦截）。
FLOW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
input="$(cat)"

python3 - "$FLOW_ROOT" "$input" <<'PY'
import json, os, re, shlex, subprocess, sys
from datetime import datetime

flow_root, raw = sys.argv[1], sys.argv[2]
try:
    data = json.loads(raw)
except ValueError:
    sys.exit(0)
cmd = (data.get("tool_input") or {}).get("command") or ""
cwd = data.get("cwd") or os.getcwd()
if not re.search(r"\b(git|gh)\b", cmd):
    sys.exit(0)

GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
SHELLS = {"bash", "sh", "zsh", "dash"}
SEPS = {";", "&&", "||", "|", "&", "\n", "(", ")", "{", "}"}


def segments(text, depth=0):
    """切成简单命令（词列表），递归展开 bash -c / sh -c / eval。"""
    try:
        lex = shlex.shlex(text.replace("\n", " ; "), posix=True, punctuation_chars=";&|(){}")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        toks = text.split()
    seg = []
    for t in toks + [";"]:
        if t in SEPS or set(t) <= set(";&|(){}"):
            if seg:
                yield from expand(seg, depth)
            seg = []
        else:
            seg.append(t)


def expand(seg, depth):
    env = {}
    i = 0
    while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
        k, v = seg[i].split("=", 1)
        env[k] = v
        i += 1
    while i < len(seg) and seg[i] in ("env", "command", "exec", "sudo", "nohup", "time"):
        i += 1
        while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
            k, v = seg[i].split("=", 1)
            env[k] = v
            i += 1
    words = seg[i:]
    if not words:
        return
    prog = os.path.basename(words[0])
    if depth < 3 and prog in SHELLS and "-c" in words[1:]:
        j = words.index("-c")
        if j + 1 < len(words):
            for e, w in segments(words[j + 1], depth + 1):
                yield {**env, **e}, w
        return
    if depth < 3 and prog == "eval":
        for e, w in segments(" ".join(words[1:]), depth + 1):
            yield {**env, **e}, w
        return
    yield env, words


def classify(words):
    prog = os.path.basename(words[0])
    if prog == "gh" and len(words) >= 3 and words[1] == "pr" and words[2] in ("create", "merge"):
        return "push", None
    if prog != "git":
        return None, None
    i, gitdir = 1, None
    while i < len(words) and words[i].startswith("-"):
        w = words[i]
        if w in GIT_OPTS_WITH_ARG:
            if w == "-C":
                gitdir = words[i + 1] if i + 1 < len(words) else None
            i += 2
            continue
        i += 1
    sub = words[i] if i < len(words) else ""
    return (sub if sub in ("push", "commit", "merge") else None), gitdir


actions = []
for env, words in segments(cmd):
    kind, gitdir = classify(words)
    if kind:
        actions.append((kind, env, gitdir))
if not actions:
    sys.exit(0)


def git(*a, cwd=cwd):
    p = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": reason}}, ensure_ascii=False))
    sys.exit(0)


worst = None
for kind, env, gitdir in actions:
    wd = os.path.join(cwd, gitdir) if gitdir and not os.path.isabs(gitdir) else (gitdir or cwd)
    top = git("rev-parse", "--show-toplevel", cwd=wd)
    if not top:
        continue
    branch = git("branch", "--show-current", cwd=top)
    on_trunk = branch in ("master", "main")
    if kind == "merge" and not on_trunk:
        continue                                   # 功能分支同步主干，放行
    bypass = env.get("TAOTAO_GATE") == "off" or os.environ.get("TAOTAO_GATE") == "off"

    p = subprocess.run(["bash", os.path.join(flow_root, "scripts/commit-gate.sh"), top], capture_output=True, text=True)
    try:
        res = json.loads(p.stdout)
    except ValueError:
        block(f"taotao-flow 提交门禁：门禁脚本输出无法解析，已阻止 `{kind}`（失败即拦截）。\n{p.stderr[-300:]}")
    v = res.get("verdict", "block_gate_error")

    if v == "block_sensitive":
        lines = [f"  - {x.get('file')}: {x.get('type')}" for x in res.get("sensitive", [])]
        block("taotao-flow 提交门禁：检测到疑似敏感信息，已阻止 `" + kind + "`。\n" + "\n".join(lines) +
              "\n清除后重试（已提交的要改写历史后再推送）；不要回显完整敏感值。")
    if v == "block_gate_error":
        block(f"taotao-flow 提交门禁：门禁脚本出错，已阻止 `{kind}`（失败即拦截）：{res.get('error', '')[-300:]}")

    if bypass:
        os.makedirs(os.path.join(top, ".taotao"), exist_ok=True)
        with open(os.path.join(top, ".taotao/gate-audit.log"), "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}\t{branch}\t{res.get('head')}\t{kind}\tTAOTAO_GATE=off\tverdict={v}\n")
        worst = worst or f"已按 TAOTAO_GATE=off 跳过 CR/扫描检查（原判定 {v}，已记入 .taotao/gate-audit.log），上线后请补 tt:cr。"
        continue

    if kind == "commit" and not on_trunk:
        continue                                   # 功能分支逐任务提交：只拦敏感信息

    msgs = {
        "block_no_cr": "本次改动尚未 CR（或当前分支没有自己的 CR 结论）。先执行 tt:cr，通过后重试。",
        "block_cr_failed": "CR 结论为 fail（存在未修复 BLOCKER）。修复后 tt:cr --recheck。",
        "block_invalid_cr": "CR 结论文件异常：" + "；".join(res.get("cr_problems", [])) + "。重跑 tt:cr。",
        "block_checks_failed": "本地扫描存在硬失败：" + ", ".join((res.get("checks") or {}).get("hard_failed", []) or ["结果文件损坏"]) + "。修复后重跑 go-check.sh 与 tt:cr --recheck。",
        "block_changed_after_cr": "CR 之后又改了这些 .go 文件，未经审查：" + ", ".join(res.get("scope", {}).get("changed_after_cr", [])) + "。执行 tt:cr --recheck。",
    }
    if v in msgs:
        block(f"taotao-flow 提交门禁：已阻止 `{kind}`。{msgs[v]}\n紧急情况可在命令前加 TAOTAO_GATE=off（会留审计记录）。")
    if v in ("warn", "soft_no_cr"):
        w = res.get("warnings", []) + (["fix/hotfix 分支没有 CR 记录"] if v == "soft_no_cr" else [])
        worst = "taotao-flow 提交门禁（警告）：" + "；".join(w) + "。确认后继续。"

if worst:
    ask(worst)
sys.exit(0)
PY
