# tt:impl — 子 agent 逐任务实现

输入：`$ARGUMENTS` —— 需求名或 Plan 路径（为空读最近的 Plan）；`--from <N>` 从 Task N 起；`--inline` 强制内联执行。

执行引擎是 `superpowers:subagent-driven-development`（SDD）：每个任务派一个全新上下文的实现子 agent，做完由评审子 agent 检查「是否符合规格 + 代码质量」，全部完成后做一次整分支终审。taotao-flow 负责它的输入（Plan、规格、Go 规范）、停止条件和收尾。

> **优先级**：`docs/rules/` > Design > Plan > 任何 skill 的建议。冲突以 rules 为准并记录。

## Step 0 — 开工前门禁

1. Read `$FLOW_ROOT/hooks/before_code.md` 并执行，硬阻断就停。
2. 通用 A（stage = impl）。

## Step 1 — 组装输入

1. **项目规约**：Read `docs/rules/code.md`、`tech-selection.md`、`forbidden.md`。缺失 → 软警告并在报告里标注；任一文件「（填写）」占位 ≥ 3 处 → ⚠️ 提示规约未生效，用户回复「继续」才往下走。
2. **Go 规范**：通用 B，默认 `[taotao-go-standards]`——它运行 `detect.py` 得到本项目 impl 阶段该读的 samber skill 路径清单 `$GO_SKILLS`（如 code-style、error-handling、context、concurrency，再加 grpc/database/testify 等按依赖命中的）。
3. **切片**：通用 C，inputSlot 的 `impl.md`（taotao-contract：先跑代码生成并校验契约与实现一致）。
4. **规格与计划**：Plan = `Plan-$FEATURE.md`；Spec = 同目录 `Design-$FEATURE.md`（ARD 作为补充规格）。

## Step 2 — 🛑 任务清单确认（唯一一次）

```
即将执行 N 个任务（模式：subagent / inline）：
Task 1: …   Task 2: …（依赖 Task 1）
已完成跳过 M 个（Plan 中已全部勾选 / --from）
工作区：<分支 / worktree>
确认后连续执行，只在停止条件出现时暂停。
```

工作区：在 master/main 上不开工。没有功能分支时按 `superpowers:using-git-worktrees` 新建 worktree 或分支（问用户选哪种）。

## Step 3 — 选择执行方式

- `commands.impl.mode` 为 `subagent`（默认）且当前环境有派发子 agent 的工具 → Read `superpowers:subagent-driven-development` 并执行；
- 用户传 `--inline`、配置为 `inline`、或没有子 agent 工具（部分 Codex 环境）→ Read `superpowers:executing-plans` 并执行；
- vendor 缺失 → 按下方「内置兜底」逐任务执行。

## Step 4 — 执行时 taotao-flow 的覆盖规则

照 SDD / executing-plans 原文执行（包括它的脚本 `sdd-workspace`、`task-brief`、`review-package`，用 `$VENDOR/superpowers/skills/subagent-driven-development/scripts/` 下的绝对路径调用），以下几点以本文件为准：

**停止条件**：SDD 原有的四种（不可逆操作、安全敏感操作、需要先问的外部副作用、计划坏到无路可走），再加两种：
- 任务方案命中 `forbidden.md` → 🚫 停下，输出「禁止条目 / 当前方案 / 建议」，等指示；
- 需要 `tech-selection.md` 之外的新依赖 → 停下问，确认后才 `go get`。

其余歧义按 SDD 的「Rulings, not stalls」自行裁决，写入 ledger，同时追加到 Plan 末尾「执行留痕」。

**给实现子 agent 的派发内容**额外加入（文件路径交付，不粘贴全文）：
- `docs/rules/code.md`、`forbidden.md` 的路径——"写代码前先读，冲突以它们为准"；
- `$GO_SKILLS` 中与本任务相关的 2–4 个 samber skill 路径（并发任务给 concurrency，DB 任务给 database……）；
- Go 红线：`if err != nil` 全覆盖并 `%w` 包装；外部调用带 context 超时；goroutine 有退出条件；不顺手重构无关代码；本次产生的孤儿代码清掉；
- 验证要求：任务的验证命令 + `gofmt -l` 无输出 + `go vet <包>` 通过 + `go test <包> -race`。

**给评审子 agent 的 Global Constraints**：从 Plan 的 Global Constraints 原样复制，并附上 `$SKILLS_DIR/taotao-review/references/go-checklist.md` 路径作为 Go 质量检查依据。

**提交**：子 agent 在功能分支/worktree 上逐任务提交是允许的（Claude Code 的提交门禁 hook 对功能分支 commit 只检查敏感信息）。推送和合并要等 tt:cr。

**进度**：每个任务评审通过后，把 Plan 中该任务的步骤复选框全部勾为 `- [x]`，并更新 progress.md 的「当前卡点」。

**收尾**：SDD 终审通过后，**不要**执行它最后的 `finishing-a-development-branch`——分支收尾放在 tt:cr 通过之后（见 `hooks/before_commit.md`）。

## Step 5 — 代码后置扫描与验证

1. **必须运行**扫描脚本（不能只读文档代替）：`bash "$FLOW_ROOT/scripts/go-check.sh" "$PROJECT_ROOT"`，结果自动写入 `.taotao/last-check.json`，提交门禁会读取。然后按 `$FLOW_ROOT/hooks/after_code.md` 处理结果：硬失败（build/vet、gosec 高危、govulncheck 命中）修复后重跑，直到通过；工具被跳过的，在收尾报告里写明。
   在 progress.md「当前卡点」下记一行：`- [x] go-check.sh <日期> <结果摘要>`，便于事后核对这一步确实执行过。
2. 按 `superpowers:verification-before-completion`：报告里每一个"通过"都要附上刚刚跑过的命令和输出摘要。

## Step 6 — 收尾

1. progress.md：Code ✅。
2. `eval-log.py confirm --stage impl --skills <…> --extra '{"tasks": N, "rulings": R, "fix_rounds": F}'`。
3. 输出：

```
✅ 实施完成「<需求名>」（subagent / inline）
任务：N 个完成 · 评审修复 F 轮 · 裁决 R 条（见 Plan 执行留痕）
改动：新增 a 个文件 / 修改 b 个文件 · 提交 c 个
规约：加载状态 … / forbidden 0 触发 / 新依赖 … / code.md 偏离 …
验证：gofmt ✓ vet ✓ build ✓ lint ✓ test -race ✓（附命令）
下一步：tt:cr
```

## 内置兜底（vendor 缺失时）

逐任务：Plan 中标记进行中 → 合规预检（FORBIDDEN / 新依赖）→ 改文件前先 Read → 按 TDD 步骤实现 → 跑任务验证命令 → 勾选完成 → 输出 `✓ Task N → 改动: …`。同一时刻只做一个任务；有前置未完成不跳；阻塞就停下说明。
