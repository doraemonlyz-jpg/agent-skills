#!/usr/bin/env bash
# 安装 statusline：Claude Code 自动装，Codex 视情况追加或提示手动合并
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Claude Code =="
command -v jq >/dev/null 2>&1 || echo "  ⚠ 未装 jq，statusline 会提示你装：brew install jq"
mkdir -p "$HOME/.claude"
cp "$HERE/claude-code/statusline.sh" "$HOME/.claude/statusline.sh"
chmod +x "$HOME/.claude/statusline.sh"
echo "  已写入 ~/.claude/statusline.sh"

python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".claude/settings.json"
d = {}
if p.exists() and p.read_text().strip():
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        raise SystemExit("  ✗ ~/.claude/settings.json 不是合法 JSON，未改动，请手动加 statusLine")
    p.with_suffix(".json.bak").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("  已备份到 ~/.claude/settings.json.bak")
d["statusLine"] = {"type": "command", "command": "$HOME/.claude/statusline.sh"}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("  已更新 ~/.claude/settings.json")
PY

echo
echo "== Codex =="
CFG="$HOME/.codex/config.toml"
mkdir -p "$HOME/.codex"
if [ -f "$CFG" ] && grep -q '^\[tui\]' "$CFG"; then
  echo "  ~/.codex/config.toml 里已经有 [tui] 段，没有自动改。"
  echo "  请手动合并下面这段（TOML 不能有两个同名表）："
  echo
  sed 's/^/    /' "$HERE/codex/config-tui.toml"
else
  [ -f "$CFG" ] && cp "$CFG" "$CFG.bak" && echo "  已备份到 ~/.codex/config.toml.bak"
  printf '\n' >> "$CFG"
  cat "$HERE/codex/config-tui.toml" >> "$CFG"
  echo "  已追加 [tui] 段到 ~/.codex/config.toml"
fi

echo
echo "完成。Claude Code 重开一个会话生效；Codex 重启 TUI 生效。"
