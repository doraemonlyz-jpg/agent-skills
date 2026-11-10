#!/usr/bin/env bash
# 把 deps.lock.json 中的第三方依赖升级到上游默认分支最新 commit，并列出变更摘要供审阅。
# 用法: scripts/bump-deps.sh [name ...]   （不带参数则全部检查）
# 升级后请跑 skills/taotao-flow/tests/test_workflow.sh，并人工看一眼 superpowers 的 RELEASE-NOTES 是否改了 skill 结构。
set -eo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LOCK="$REPO/deps.lock.json"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

python3 - "$LOCK" "$TMP" "$@" <<'PY'
import json, subprocess, sys
lock, tmp, only = sys.argv[1], sys.argv[2], set(sys.argv[3:])
data = json.load(open(lock))
changed = False
for d in data["deps"]:
    if only and d["name"] not in only:
        continue
    out = subprocess.run(["git", "ls-remote", d["repo"], "HEAD"], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout:
        print(f"  ✗ {d['name']}: ls-remote 失败"); continue
    head = out.stdout.split()[0]
    if head == d["commit"]:
        print(f"  = {d['name']} 已是最新 {head[:8]}"); continue
    path = f"{tmp}/{d['name']}"
    subprocess.run(["git", "clone", "-q", "--filter=blob:none", d["repo"], path], check=True)
    log = subprocess.run(["git", "-C", path, "log", "--oneline", f"{d['commit']}..{head}"], capture_output=True, text=True).stdout
    stat = subprocess.run(["git", "-C", path, "diff", "--stat", d["commit"], head, "--", "skills"], capture_output=True, text=True).stdout
    print(f"  ↑ {d['name']} {d['commit'][:8]} → {head[:8]}\n{log}\n{stat}")
    d["commit"] = head
    changed = True
if changed:
    json.dump(data, open(lock, "w"), ensure_ascii=False, indent=2)
    open(lock, "a").write("\n")
    print("deps.lock.json 已更新；运行 scripts/fetch-deps.sh 与 tests/test_workflow.sh（均在 skills/taotao-flow 下）验证后再提交。")
PY
