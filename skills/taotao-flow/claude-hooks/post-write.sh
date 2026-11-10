#!/usr/bin/env bash
# Claude Code PostToolUse hook（Write|Edit|MultiEdit）。
# - 写入 docs/features/active/*/ARD-*.md / Design-*.md 后，提醒 Claude 执行对应门禁钩子；
# - 写入 .go 文件后自动 gofmt，并把格式化结果告知 Claude。
# 退出码 2 = 把 stderr 反馈给 Claude；0 = 静默。
FLOW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
input="$(cat)"
file="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print((d.get("tool_input") or {}).get("file_path",""))
except Exception: print("")')"
[ -n "$file" ] || exit 0

case "$file" in
  */docs/features/active/*/ARD-*.md)
    echo "taotao-flow: ARD 已写入 $file。现在 Read $FLOW_ROOT/hooks/after_ard.md 并执行需求覆盖检查，把结果告诉用户。" >&2
    exit 2 ;;
  */docs/features/active/*/Design-*.md)
    echo "taotao-flow: Design 已写入 $file。现在 Read $FLOW_ROOT/hooks/after_design.md 并执行架构完整性检查；硬阻断项未解决前不要进入 tt:plan。" >&2
    exit 2 ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 || exit 0
    if [ -n "$(gofmt -l "$file" 2>/dev/null)" ]; then
      gofmt -w "$file" && echo "taotao-flow: 已对 $file 执行 gofmt -w（格式已修正，后续编辑请基于最新内容）。" >&2 && exit 2
    fi
    exit 0 ;;
esac
exit 0
