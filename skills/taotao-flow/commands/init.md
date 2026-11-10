# tt:init — 在当前 Go 项目落地流水线

可重复运行：项目层文件只在不存在时创建，永不覆盖；规则块和 hooks 按标记幂等更新。

## Step 1 — 确认位置

1. `git rev-parse --show-toplevel` 得到 `$PROJECT_ROOT`；不是 Git 仓库就问用户是否仍在当前目录初始化。
2. 检查 `go.mod`。不存在时提示"未检测到 go.mod，当前只内置 Go 后端模板"，问用户是否继续。

## Step 2 — 运行初始化脚本

```bash
bash "$FLOW_ROOT/scripts/init-project.sh" "$PROJECT_ROOT"      # Codex 或不想要 hooks 时加 --no-hooks
```

| 动作 | 已存在时 |
|---|---|
| 创建 `docs/{features/{active,completed},knowledge/experiences,rules,eval}` | 跳过 |
| 复制 rules 与 knowledge 模板 | 不覆盖 |
| 按 `project-types.yaml` 检测类型（含 grpc/kitex/thrift → `backend-go-rpc`），生成 `workflow.config.yaml` | 不覆盖 |
| `CLAUDE.md`、`AGENTS.md` 写入规则块 | 只替换标记之间 |
| `.claude/settings.json` 注册 PostToolUse（写 ARD/Design 提醒门禁、.go 自动 gofmt）与 PreToolUse（git push/主干 commit 跑提交门禁）hook | 合并，不动其他配置 |
| 安装 git 原生 pre-push hook（`.git/hooks/pre-push`，复用提交门禁；Codex/IDE/终端推送都生效） | 已有我们的 → 更新；已有别人的 → 不覆盖，提示手动接入 |
| `.gitignore` 加 `.taotao/` | 已有则跳过 |

把脚本输出原样展示给用户。

## Step 3 — 工具链检查（只提示，不自动安装）

1. 第三方 skill：`bash $FLOW_ROOT/scripts/fetch-deps.sh --check`。缺失时直接运行 `bash $FLOW_ROOT/scripts/fetch-deps.sh` 拉取（先告诉用户会从 GitHub 拉 4 个仓库到 `~/.taotao/vendor`）。
2. 兄弟 skill：`$SKILLS_DIR` 下 taotao-prd / clarify / go-standards / review / tdd / debug / impact / mock / humanize / contract 是否齐全。
3. 本机工具：`go`、`gopls`（必需，gopls MCP 与 LSP 都靠它）、`golangci-lint`、`gosec`、`govulncheck`、`mockery`、`prism`（可选）。缺什么给出 `$FLOW_ROOT/deps.lock.json` 里的安装命令，并说明缺了会降级成什么。
4. MCP：当前会话能否看到 gopls MCP 工具（`go_workspace` / `go_search` 等）和 Notion MCP。没有就提示 agent-skills 仓库的 `setup/install-taotao.sh --setup-mcp`。
5. 运行 `python3 $SKILLS_DIR/taotao-go-standards/detect.py "$PROJECT_ROOT"`，告诉用户识别到的 Go 版本、框架和各阶段会加载的 samber skill。

## Step 4 — 收尾

```
✅ taotao-flow 已初始化：<PROJECT_ROOT>（<type>）
下一步：
1. 补全 docs/rules/ 中的「（填写）」占位（tech-selection.md、forbidden.md 是编码阶段的硬约束）
2. tt:map 生成知识索引
3. 有需求时从 tt:ard 开始；Claude Code 下重启会话让 hooks 生效
```

`docs/rules/` 占位仍 ≥ 3 处时提醒：不补全的话 tt:impl 开工前会再提醒一次。
