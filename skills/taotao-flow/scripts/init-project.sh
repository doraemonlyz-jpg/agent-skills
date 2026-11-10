#!/usr/bin/env bash
# taotao-flow: 在 Go 项目中落地 docs 骨架、配置、规则块与 Claude Code hooks。
# 可重复运行：项目层文件只在不存在时创建，永不覆盖；规则块与 hooks 按标记幂等更新。
# 用法: init-project.sh [PROJECT_ROOT] [--no-hooks]
set -eo pipefail  # 不用 -u：macOS 自带 bash 3.2 对空数组展开会误报

FLOW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
NO_HOOKS=0; ARG_ROOT=""
for a in "$@"; do case "$a" in --no-hooks) NO_HOOKS=1 ;; *) ARG_ROOT="$a" ;; esac; done
PROJECT_ROOT="${ARG_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -P)"
TPL="$FLOW_ROOT/templates"

created=(); skipped=()
copy_if_absent() { # src dst
  if [ -e "$2" ]; then skipped+=("${2#$PROJECT_ROOT/}"); else cp "$1" "$2"; created+=("${2#$PROJECT_ROOT/}"); fi
}

mkdir -p "$PROJECT_ROOT/docs/features/active" "$PROJECT_ROOT/docs/features/completed" \
         "$PROJECT_ROOT/docs/knowledge/experiences" "$PROJECT_ROOT/docs/rules" "$PROJECT_ROOT/docs/eval"
for d in docs/features/active docs/features/completed docs/knowledge/experiences docs/eval; do
  [ -e "$PROJECT_ROOT/$d/.gitkeep" ] || touch "$PROJECT_ROOT/$d/.gitkeep"
done
for f in code.md forbidden.md tech-selection.md; do copy_if_absent "$TPL/rules/$f" "$PROJECT_ROOT/docs/rules/$f"; done
for f in index.md tech.yaml terms.yaml; do copy_if_absent "$TPL/knowledge/$f" "$PROJECT_ROOT/docs/knowledge/$f"; done

# 项目类型检测 + workflow.config.yaml
TYPE_INFO="$(python3 - "$FLOW_ROOT/project-types.yaml" "$PROJECT_ROOT/go.mod" <<'PY'
import os, re, sys
reg, gomod = sys.argv[1], sys.argv[2]
text = open(reg, encoding="utf-8").read()
mod = open(gomod, encoding="utf-8").read() if os.path.exists(gomod) else ""
blocks = re.split(r"\n  - id: ", text.split("defaults:")[0])[1:]
for b in blocks:
    tid = b.split("\n", 1)[0].strip()
    m = re.search(r"go_mod_any:\s*\[([^\]]*)\]", b)
    mods = [x.strip().strip("'\"") for x in (m.group(1).split(",") if m else []) if x.strip()]
    d = re.search(r"design:\s*\{\s*input:\s*(\[[^\]]*\])", b)
    if not mods or any(re.search(r"(^|\s)" + re.escape(x) + r"(\s|/|$)", mod, re.M) for x in mods):
        print(tid + "\t" + (d.group(1) if d else "[]"))
        break
PY
)"
PTYPE="${TYPE_INFO%%$'\t'*}"; DESIGN_INPUT="${TYPE_INFO#*$'\t'}"
[ -n "$PTYPE" ] || { PTYPE=backend-go; DESIGN_INPUT="[]"; }

cfg="$PROJECT_ROOT/workflow.config.yaml"
if [ -e "$cfg" ]; then
  skipped+=("workflow.config.yaml")
else
  name="$(basename "$PROJECT_ROOT")"
  if [ -f "$PROJECT_ROOT/go.mod" ]; then
    mod="$(awk '/^module /{print $2; exit}' "$PROJECT_ROOT/go.mod")"
    [ -n "$mod" ] && name="${mod##*/}"
  fi
  python3 - "$TPL/workflow.config.yaml" "$cfg" "$name" "$PTYPE" "$DESIGN_INPUT" <<'PY'
import sys
src, dst, name, ptype, din = sys.argv[1:6]
t = open(src, encoding="utf-8").read()
t = t.replace("__PROJECT_NAME__", name).replace("__PROJECT_TYPE__", ptype).replace("__DESIGN_INPUT__", din)
open(dst, "w", encoding="utf-8").write(t)
PY
  created+=("workflow.config.yaml（type: $PTYPE）")
fi

# 规则块：CLAUDE.md 与 AGENTS.md（只替换标记之间的内容）
inject_block() { # file
  python3 - "$1" "$TPL/rules-block.md" <<'PY'
import os, re, sys
path, block_src = sys.argv[1:3]
start, end = "<!-- taotao-flow:start -->", "<!-- taotao-flow:end -->"
# Claude Code 支持 @ 引用文件；Codex 不支持，改为文字指引
ref = ("@docs/knowledge/index.md" if os.path.basename(path) == "CLAUDE.md"
       else "知识路由：需要了解项目结构时先读 `docs/knowledge/index.md`。Codex 没有 hook，说「提交/push」时必须先执行 taotao-flow 的 hooks/before_commit.md。")
block = f"{start}\n{open(block_src, encoding='utf-8').read().rstrip()}\n\n{ref}\n{end}"
text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
if start in text and end in text:
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S); action = "updated"
else:
    action = "appended" if text.strip() else "created"
    text = (text.rstrip() + "\n\n" if text.strip() else "") + block + "\n"
open(path, "w", encoding="utf-8").write(text)
print(action)
PY
}
for f in CLAUDE.md AGENTS.md; do created+=("$f（规则块 $(inject_block "$PROJECT_ROOT/$f")）"); done

# Claude Code hooks：合并进 .claude/settings.json（带 taotao-flow 标记，幂等）
if [ $NO_HOOKS -eq 0 ]; then
  mkdir -p "$PROJECT_ROOT/.claude"
  act="$(python3 - "$PROJECT_ROOT/.claude/settings.json" <<'PY'
import json, os, sys
path = sys.argv[1]
existed = os.path.exists(path)
data = json.load(open(path)) if existed else {}
def hook(script):
    # 依次在 TAOTAO_FLOW_ROOT 与三个常见安装位置找脚本；用 exec 保留脚本退出码（2 = 阻止/反馈给 Claude）。
    # 都找不到（没装 taotao-flow 的同事）时静默放行。标记放在命令字符串里（taotao-flow/claude-hooks），不加自定义字段。
    cands = '"${TAOTAO_FLOW_ROOT:-}" "$HOME/.agents/skills/taotao-flow" "$HOME/.claude/skills/taotao-flow" "$HOME/.codex/skills/taotao-flow"'
    cmd = (f'for d in {cands}; do f="$d/claude-hooks/{script}"; '
           f'if [ -n "$d" ] && [ -f "$f" ]; then exec bash "$f"; fi; done; exit 0')
    return {"type": "command", "command": cmd}
want = {
    "PostToolUse": {"matcher": "Write|Edit|MultiEdit", "hooks": [hook("post-write.sh")]},
    "PreToolUse": {"matcher": "Bash", "hooks": [hook("pre-bash.sh")]},
}
hooks = data.setdefault("hooks", {})
for event, entry in want.items():
    # 按脚本名去重（兼容旧版本写入的命令格式），重复 init 只保留一份
    mine = lambda c: "claude-hooks/post-write.sh" in c or "claude-hooks/pre-bash.sh" in c
    lst = [e for e in hooks.get(event, []) if not any(mine(h.get("command", "")) for h in e.get("hooks", []))]
    lst.append(entry)
    hooks[event] = lst
json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
print("merged" if existed else "created")
PY
)"
  created+=(".claude/settings.json（hooks $act）")
fi

# git 原生 pre-push hook：对所有推送方式生效（Codex、IDE、终端），复用 commit-gate.sh
if [ $NO_HOOKS -eq 0 ] && git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  hooks_dir="$(git -C "$PROJECT_ROOT" rev-parse --git-path hooks)"
  case "$hooks_dir" in /*) ;; *) hooks_dir="$PROJECT_ROOT/$hooks_dir" ;; esac
  mkdir -p "$hooks_dir"
  pp="$hooks_dir/pre-push"
  if [ -f "$pp" ] && ! grep -q 'taotao-flow-git-hook' "$pp"; then
    skipped+=("git pre-push hook（已有其他 pre-push：$pp，未覆盖；可在其中追加调用 $FLOW_ROOT/git-hooks/pre-push）")
  else
    cp "$FLOW_ROOT/git-hooks/pre-push" "$pp" && chmod +x "$pp"
    created+=("git pre-push hook（${pp#$PROJECT_ROOT/}）")
  fi
fi

# .gitignore：CR 兜底结论目录
gi="$PROJECT_ROOT/.gitignore"
if ! grep -qx '.taotao/' "$gi" 2>/dev/null; then printf '\n# taotao-flow\n.taotao/\n' >> "$gi"; created+=(".gitignore（.taotao/）"); fi

echo "taotao-flow init → $PROJECT_ROOT"
echo "项目类型: $PTYPE"
echo "新建/更新:"; for x in "${created[@]}"; do echo "  + $x"; done
if [ "${#skipped[@]}" -gt 0 ]; then echo "已存在，未覆盖:"; for x in "${skipped[@]}"; do echo "  = $x"; done; fi
placeholders="$(grep -o '（填写' "$PROJECT_ROOT"/docs/rules/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "docs/rules 中「（填写）」占位: $placeholders 处"
[ -f "$PROJECT_ROOT/go.mod" ] || echo "⚠️ 未检测到 go.mod：当前只内置 Go 后端模板"
