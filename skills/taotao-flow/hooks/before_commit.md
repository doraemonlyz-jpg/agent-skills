# before_commit — 提交门禁与分支收尾

**时机**：用户说「推送 / push / 合代码 / 上线 / 提 PR」，或要在 master/main 上提交、把功能分支合入主干时，执行 git 操作之前。
功能分支上的逐任务提交（tt:impl 子 agent）只扫敏感信息；在功能分支上 `git merge master`（同步主干）不拦。

三道执行点共用同一个脚本 `scripts/commit-gate.sh`：

| 执行点 | 覆盖范围 | 说明 |
|---|---|---|
| 本文件（AI 主动执行） | 所有环境 | 推送前读结论、和用户确认整合方式 |
| Claude Code PreToolUse hook（`claude-hooks/pre-bash.sh`） | Claude Code 里的 Bash 调用 | 词法识别 git push/commit/merge 与 `gh pr create/merge`（含 `bash -c`、绝对路径、`git -c` 等写法），提前拦截；警告以「需要用户确认」的方式弹给用户 |
| git 原生 pre-push hook（`git-hooks/pre-push`，tt:init 安装） | 所有推送方式：Codex、IDE、终端 | 最后一道；按实际推送的提交范围扫描 |

先查项目覆盖版本 `docs/hooks/before_commit.md`。

## Step 0 — Hotfix 与紧急通道

信号：用户明确说 hotfix/紧急修复，或分支名含 `hotfix/`。命中时问一次：

```
🔧 紧急修复：是否跳过 CR？
「跳过」→ 命令写成 TAOTAO_GATE=off git push：跳过 CR 与扫描检查，敏感信息仍会拦截，记录写入 .taotao/gate-audit.log；上线后补 tt:cr
「不跳过」→ 完整门禁
```

`TAOTAO_GATE=off` 必须写在命令开头，Claude Code hook 和 git pre-push hook 都能识别。`git push --no-verify` 会跳过 git 原生 hook，但 Claude Code hook 仍会检查，不要建议用户用它。

## Step 1 — 机械检查

```bash
bash "$FLOW_ROOT/scripts/commit-gate.sh" "$PROJECT_ROOT" [--feature <需求名>]
```

扫描范围：已暂存与未暂存的改动 + 待推送的提交（有 upstream 用 `upstream..HEAD`；首次推送用 `merge-base(主干)..HEAD`，已提交的内容也会扫到）。
CR 结论：只认 `branch` 等于当前分支、且 `headCommit` 在当前分支历史中的那份 `cr-status.json`；别的需求的结论不算数。

| verdict | 含义 | 处理 |
|---|---|---|
| `block_sensitive` | 凭证 / Bearer token / 私钥 / 内网地址 | 🚫 清除后重试；已提交的要改写历史；只报位置和类型，不回显值 |
| `block_gate_error` | 门禁脚本自身出错 | 🚫 失败即拦截；排查脚本或用紧急通道 |
| `block_invalid_cr` | cr-status.json 损坏、result 非法、commitReady=false、缺 branch 字段 | 🚫 重跑 tt:cr |
| `block_no_cr` | 当前分支没有 CR 结论 | 🚫 先 tt:cr |
| `soft_no_cr` | `fix/`、`hotfix/` 分支没有 CR 结论 | ⚠️ 建议 tt:cr，用户确认可继续 |
| `block_cr_failed` | CR 有未修复 BLOCKER | 🚫 修复后 tt:cr --recheck |
| `block_checks_failed` | 当前 HEAD 的本地扫描有硬失败（build/vet、gosec 高危、govulncheck 命中） | 🚫 修复后重跑 go-check.sh 与 tt:cr --recheck |
| `block_changed_after_cr` | CR 之后又改了 .go 文件 | 🚫 tt:cr --recheck |
| `warn` | 调试残留 / 当前 HEAD 没跑过扫描 / 安全扫描被跳过 | ⚠️ 列出 `warnings`，用户确认后继续 |
| `pass` | — | 继续 |

## Step 2 — 分支收尾

门禁通过后，按 `superpowers:finishing-a-development-branch` 处理整合方式：先跑一遍测试确认全绿，再给用户选项——推送并提 PR / 本地合并到主干 / 保留分支稍后处理 / 放弃。taotao-flow 的覆盖规则：

- 提 PR 时，PR 描述包含需求名、ARD/Design 路径、CR 评分与结论（取自 cr-status.json）、本地扫描结果（取自 .taotao/last-check.json）；
- 使用了 worktree 的，按它的流程清理；
- 提交信息用 Conventional Commits（`feat(order): 支持取消订单`），需求名写进 scope 或正文。

```
✅ 提交门禁通过
- CR: 通过 / 有条件通过（评分 X）· BLOCKER 0 · WARN N（已知晓）
- 本地扫描: build ✓ vet ✓ lint ✓ gosec ✓ govulncheck ✓ test ✓
- 敏感扫描: 0
整合方式：<用户选择>
```
