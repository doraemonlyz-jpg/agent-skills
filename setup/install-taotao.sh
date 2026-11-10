#!/usr/bin/env bash
# 安装 taotao-flow 工具链（Claude Code + Codex 通用）：只处理 skills/taotao-*，不动仓库里的其他 skill。
# 与 setup/release.py 的关系：本脚本把 taotao-* 软链接进 ~/.agents/skills 与 ~/.claude/skills，release.py 同步时会跳过已在
# ~/.agents/skills 中的 skill，不会重复复制进 ~/.codex/skills。
#
# 用法:
#   setup/install-taotao.sh                 安装：taotao-* 软链接 + 按 skills/taotao-flow/deps.lock.json 拉取第三方 skill + 生成 /tt:* 命令
#   setup/install-taotao.sh --setup-mcp     额外为 Claude Code / Codex 注册 gopls 与 Notion MCP（需要对应 CLI）
#   setup/install-taotao.sh --codex-legacy  额外链接到 ~/.codex/skills（老版本 Codex 只读这个目录）
#   setup/install-taotao.sh --no-fetch      不拉取第三方（离线；之后可单独跑 scripts/fetch-deps.sh --from <dir>）
#   setup/install-taotao.sh --uninstall     卸载（只删除指向 skills/taotao-* 与 vendor 的链接和本脚本生成的命令文件，保留 vendor 目录）
set -eo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
SKILLS_SRC="$REPO/skills"
FLOW="$SKILLS_SRC/taotao-flow"
LOCK="$FLOW/deps.lock.json"
VENDOR="${TAOTAO_VENDOR:-$HOME/.taotao/vendor}"
CMDS="init map ard design plan test impl cr fix mock sync archive exp eval"
MARK="taotao-flow · tt:"

LEGACY=0; UNINSTALL=0; SETUP_MCP=0; FETCH=1
for a in "$@"; do
  case "$a" in
    --codex-legacy) LEGACY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --setup-mcp) SETUP_MCP=1 ;;
    --no-fetch) FETCH=0 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "未知参数: $a"; exit 1 ;;
  esac
done

TARGETS="$HOME/.agents/skills $HOME/.claude/skills"
[ $LEGACY -eq 1 ] && TARGETS="$TARGETS $HOME/.codex/skills"

link() { # src_dir target_dir
  local name dst; name="$(basename "$1")"; dst="$2/$name"
  mkdir -p "$2"
  if [ -L "$dst" ]; then ln -sfn "$1" "$dst"; echo "  ↻ $dst"
  elif [ -e "$dst" ]; then echo "  ⚠️ 跳过 $dst（已存在且不是软链接）"
  else ln -s "$1" "$dst"; echo "  + $dst"; fi
}

exposed_dirs() { # 需要全局暴露的第三方 skill 目录（deps.lock.json 中 expose=true 的 glob）
  python3 - "$LOCK" "$VENDOR" <<'PY'
import glob, json, os, sys
lock, vendor = sys.argv[1], sys.argv[2]
for d in json.load(open(lock))["deps"]:
    if d.get("expose"):
        for p in sorted(glob.glob(os.path.join(vendor, d["name"], d.get("expose_glob", "skills/*")))):
            if os.path.isfile(os.path.join(p, "SKILL.md")):
                print(p)
PY
}

cmd_file() { # kind name
  local dirs
  if [ "$1" = claude ]; then dirs='`~/.agents/skills/taotao-flow`、`~/.claude/skills/taotao-flow`'; else dirs='`~/.agents/skills/taotao-flow`、`~/.codex/skills/taotao-flow`'; fi
  cat <<EOF
---
description: taotao-flow · tt:$2
argument-hint: [参数]
---

执行 taotao-flow 流水线命令 \`tt:$2\`，参数：\$ARGUMENTS

1. 定位 taotao-flow skill 目录（\$FLOW_ROOT）：依次检查 $dirs，取第一个存在的。
2. Read \`\$FLOW_ROOT/SKILL.md\` 了解约定，然后 Read \`\$FLOW_ROOT/commands/$2.md\`，严格按其步骤执行。
EOF
}

if [ $UNINSTALL -eq 1 ]; then
  echo "卸载链接:"
  for t in $HOME/.agents/skills $HOME/.claude/skills $HOME/.codex/skills; do
    [ -d "$t" ] || continue
    for l in "$t"/*; do
      [ -L "$l" ] || continue
      case "$(readlink "$l")" in "$SKILLS_SRC"/taotao-*|"$VENDOR"/*) rm "$l"; echo "  - $l" ;; esac
    done
  done
  echo "删除命令文件:"
  for c in $CMDS; do
    for f in "$HOME/.claude/commands/tt/$c.md" "$HOME/.codex/prompts/tt-$c.md"; do
      if [ -f "$f" ] && grep -q "$MARK" "$f"; then rm "$f"; echo "  - $f"; fi
    done
  done
  rmdir "$HOME/.claude/commands/tt" 2>/dev/null || true
  echo "vendor 目录保留在 $VENDOR，不需要可手动删除。"
  exit 0
fi

echo "① taotao skill（软链接 → $SKILLS_SRC/taotao-*）:"
for t in $TARGETS; do for s in "$SKILLS_SRC"/taotao-*/; do link "${s%/}" "$t"; done; done

echo "② 第三方 skill（deps.lock.json → $VENDOR）:"
if [ $FETCH -eq 1 ]; then
  bash "$FLOW/scripts/fetch-deps.sh" || echo "  ⚠️ 部分依赖拉取失败；内网可设 TAOTAO_GIT_MIRROR，或下载后用 scripts/fetch-deps.sh --from <dir>"
else
  bash "$FLOW/scripts/fetch-deps.sh" --check || true
fi

echo "③ 全局暴露的第三方 skill（samber Go 规范，供日常写 Go 时自动触发）:"
n=0
for d in $(exposed_dirs); do for t in $TARGETS; do link "$d" "$t" >/dev/null; done; n=$((n+1)); done
echo "  已链接 $n 个"

echo "④ 命令:"
mkdir -p "$HOME/.claude/commands/tt" "$HOME/.codex/prompts"
for c in $CMDS; do
  cmd_file claude "$c" > "$HOME/.claude/commands/tt/$c.md"
  cmd_file codex "$c" > "$HOME/.codex/prompts/tt-$c.md"
done
echo "  Claude Code: /tt:{$(echo $CMDS | tr ' ' ',')}"
echo "  Codex:       /prompts:tt-<name>"

if [ $SETUP_MCP -eq 1 ]; then
  echo "⑤ MCP:"
  if command -v gopls >/dev/null 2>&1; then
    command -v claude >/dev/null 2>&1 && { claude mcp add --scope user gopls -- gopls mcp 2>&1 | sed 's/^/  claude: /' || true; }
    command -v codex >/dev/null 2>&1 && { codex mcp add gopls -- gopls mcp 2>&1 | sed 's/^/  codex: /' || true; }
  else
    echo "  ✗ 未找到 gopls：go install golang.org/x/tools/gopls@latest 后重跑 --setup-mcp"
  fi
  command -v claude >/dev/null 2>&1 && { claude mcp add --scope user --transport http notion https://mcp.notion.com/mcp 2>&1 | sed 's/^/  claude: /' || true; echo "  Notion 首次使用时在 Claude Code 里执行 /mcp 完成授权"; }
  command -v codex >/dev/null 2>&1 && echo "  codex: Notion 远程 MCP 请按 'codex mcp --help' 添加 https://mcp.notion.com/mcp"
fi

echo
echo "工具检查（✗ 必装 / · 可选）:"
python3 - "$LOCK" <<'PY'
import json, shutil, sys
miss = []
for t in json.load(open(sys.argv[1]))["tools"]:
    ok = shutil.which(t["name"])
    if not ok and t["required"]:
        miss.append(t["name"])
    print(f"  {'✓' if ok else ('✗' if t['required'] else '·')} {t['name']:<14} {'' if ok else t['install']}")
if miss:
    print(f"  ⚠️ 缺少必装工具：{', '.join(miss)}。缺 gosec / govulncheck 时安全扫描不会执行，提交门禁会对每次推送给出警告。")
    print("     go install 需要能访问 Go 模块代理；公司内网先设置：go env -w GOPROXY=<内部代理>,direct")
    print("     govulncheck 需要访问漏洞库 vuln.go.dev；不通时设置 GOVULNDB 指向镜像。")
PY
echo
echo "Claude Code 官方插件（在 Claude Code 里执行一次）:"
echo "  /plugin install gopls-lsp@claude-plugins-official"
echo "  /plugin install code-review@claude-plugins-official   # 可选：PR 级多 agent 评审"
echo
echo "完成。重启 Claude Code / Codex 后生效。在 Go 项目里执行 tt:init 开始。"
