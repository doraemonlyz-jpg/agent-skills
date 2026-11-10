# tt:cr — Code Review

| 触发 | 模式 | 行为 |
|---|---|---|
| `tt:cr` | `fast`（默认） | 工具扫描 + 六维基线，只报 BLOCKER |
| `tt:cr --full` | `full` | 影响面 + 工具扫描 + 六维全审 + 独立评审子 agent，报 BLOCKER/WARN/NIT |
| `tt:cr --key` | `key` | 影响面分级后只全审 🔴 高风险文件，其余列为「已跳过」 |
| `tt:cr --recheck` | `recheck` | 复用上次范围，只复审上次有 BLOCKER 的文件 |
| `tt:cr --pr` | `pr` | 已有 GitHub PR 时，额外提示可用官方 `code-review` 插件做 PR 级多 agent 评审 |

## Step 0 — 开场

`eval-log.py start --stage cr`（有需求目录时）；通用 B：默认 `[taotao-review]`。找不到就按 `taotao-review/references/go-checklist.md` 降级自检，报告标注「降级模式」。

## Step 1 — 范围

```bash
# 优先本地主干（tt:impl 可能先把文档提交到本地主干再开分支），其次远端
BASE=$(git merge-base HEAD master 2>/dev/null || git merge-base HEAD main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || git merge-base HEAD origin/main)
git diff --name-status "$BASE"...HEAD; git diff --name-status   # 未提交改动一并纳入
```

- 保留 `.go`、`go.mod/go.sum`、`*.sql`、契约文件（`*.proto` / `*.thrift` / `openapi*.yaml`）、配置；`_test.go` 单独分组；生成代码（`Code generated … DO NOT EDIT.`）跳过。
- 范围为空 → 「当前分支无改动，CR 结束」。
- `recheck` → 用上次 `cr-status.json` 中 BLOCKER 的文件。
- 🛑 输出文件清单和 BASE 等确认；用户已说"范围已确认/直接审"可跳过。

## Step 2 — 影响面（full / key）

`taotao-impact`：gopls 引用计数 + 风险分级 🔴/🟡/🟢；涉及鉴权、资金、加解密、外部输入解析时，它会叠加 `tob:differential-review` 的爆炸半径与未覆盖测试分析。不可用时用 `packages.yaml` 反向依赖人工判断；再不行 key 降级为 full。

## Step 3 — 本地扫描（所有模式必做）

```bash
bash "$FLOW_ROOT/scripts/go-check.sh" "$PROJECT_ROOT" "$BASE"
```

把输出原样贴给用户，并读取 `.taotao/last-check.json`。判定：

- `build` / `vet` 为 `fail`、`gosec` 为 `fail_high`、`govulncheck` 为 `fail_high` → 记为 BLOCKER（`source: tool`）；
- `golangci-lint` / `gosec` 为 `fail`、`test` 为 `fail` → 按问题是否由本次改动引入定级（通常 WARN）；
- 工具 `skipped` / `error` → 报告里写明「未执行：<工具>，原因」，不能当作通过。提交门禁会对此给出警告。

这一步的结果由脚本写盘，提交门禁直接读取，不依赖报告里的文字。

## Step 4 — 审查

交给 taotao-review，注入：模式、文件列表、BASE、影响面分级、需求目录下的 Design/Plan 路径（作为"需求是否实现"的依据）。taotao-review 负责工具扫描、按 samber 规范逐维审查，full 模式再派一个**不继承当前会话上下文**的独立评审子 agent（`superpowers:requesting-code-review` 模板），合并去重。

inputSlot 的 `cr.md` 存在时一并执行（taotao-contract：契约破坏性变更检测）。

**可选：公司远端扫描（dlinter）**。full 模式下，如果本机装了 `dlinter` skill（`~/.agents/skills/dlinter` 或 `~/.claude/skills/dlinter`），问用户一次是否同时跑一次增量扫描。遵守 dlinter 自己的规则：创建扫描任务前必须获得确认、只支持增量、失败就如实报告、不伪造结果。结果并入报告（`source: dlinter`）。tt:impl 的连续执行中不调用它，因为它每次都要人工确认。

## Step 5 — BLOCKER 处理

- **有 BLOCKER** → 🚫 列出每条及修复建议，写 cr-status.json（`result: fail`），提示修复后 `tt:cr --recheck`，不进入后续步骤。
- **无 BLOCKER 有 WARN**（非 fast）→ ⚠️ 列出，用户回复「确认」后继续。用户对评审意见的实质反馈（"忽略 X""Y 不是问题，因为…"）按通用 D 记录；评审意见不对时可以有理有据地反驳（`superpowers:receiving-code-review` 的态度：技术上核实，不盲从）。
- **都没有** → 继续。

## Step 6 — 落盘 cr-status.json

写入 `docs/features/active/<需求名>/cr-status.json`；没有需求目录时写 `.taotao/cr-status.json`；`.gitignore` 里还没有 `.taotao/`（项目未 tt:init）就顺手追加一行，避免结论文件被误提交。

```json
{
  "timestamp": "YYYY-MM-DD HH:mm",
  "branch": "<git branch --show-current>",
  "mode": "full",
  "base": "<sha>",
  "headCommit": "<git rev-parse --short HEAD>",
  "dirty": false,
  "files": ["internal/order/service/cancel.go"],
  "blockerCount": 0, "warnCount": 2, "nitCount": 1,
  "score": 7.7,
  "result": "conditional_pass",
  "commitReady": true,
  "tools": { "build": "pass", "vet": "pass", "golangci-lint": "fail", "gosec": "pass", "govulncheck": "skipped", "test": "pass" },
  "issues": [ { "level": "WARN", "file": "…", "line": 42, "dim": "R2 健壮性", "desc": "…", "source": "self|independent|tool" } ]
}
```

- `score = max(1, 10 - BLOCKER×3 - WARN×1 - NIT×0.3)`；fast 模式 `warnCount = -1`。
- `result`：`pass` / `conditional_pass`（有 WARN 且用户已确认）/ `fail`，**一律小写**。
- `branch` 必填：提交门禁只认当前分支的结论，缺少 branch 的旧文件会被当作无效。
- `tools` 原样复制 `.taotao/last-check.json` 的 `results`。
- 有 BLOCKER 时 `commitReady: false`；门禁同时校验 `result` 和 `commitReady`，任一不满足即拦截。

## Step 7 — 结论与记录

```
✅ 通过 [模式] — 评分 X
⚠️ 有条件通过 — N 个 WARN 已知晓
```

key 模式追加：「N 个非高风险文件已跳过，需要完整审查执行 tt:cr --full」。
`eval-log.py confirm --stage cr --extra '{"bugs_found": B+W, "score": X}'`；progress.md：CR ✅。

## 提交门禁与分支收尾

用户说「提交 / push / 合代码 / 上线 / 提 PR」时，Read `$FLOW_ROOT/hooks/before_commit.md` 并执行，通过后再做 git 操作。Claude Code 下 PreToolUse hook 会在 `git push` 前强制跑同一套检查。
