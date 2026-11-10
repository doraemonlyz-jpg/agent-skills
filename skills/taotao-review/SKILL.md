---
name: taotao-review
description: Go 代码六维审查（正确性、健壮性、并发安全、安全、性能、可维护性）：先跑 vet/golangci-lint/gosec/govulncheck，再按 samber Go 规范与内置检查表逐维审，full 模式另派一个不继承上下文的独立评审子 agent（superpowers code-reviewer 模板），合并去重后按 BLOCKER/WARN/NIT 分级并给可粘贴的修复与 1–10 评分。被 taotao-flow 的 tt:cr 与 tt:impl 评审环节调用；用户说"review 一下""CR 这个分支""看看这段 Go 代码有没有问题""提 PR 前帮我过一遍"时也应使用。
metadata:
  version: 2.2.0
  short-description: Go 六维 CR + 工具扫描 + 独立评审
---

# taotao-review — Go 六维代码审查

找出真正会出事的问题，分级处置，给能直接用的修复。风格问题交给 gofmt 和 golangci-lint。

`$VENDOR` = `${TAOTAO_VENDOR:-~/.taotao/vendor}`。

## Step 1 — 范围与模式

1. 调用方（tt:cr）注入了文件列表 / BASE / 模式 / Design 路径 → 直接用；
2. 用户指定文件或目录 → 审这些文件及其直接调用的项目内函数签名；
3. "审这个分支" → `git diff <merge-base>...HEAD` + 未提交改动；
4. 无 Git 或无改动 → 问用户要审什么，不盲扫。

对改动文件只审新增/修改行及必要上下文；新文件整文件审；跳过生成代码、vendor、`*.pb.go`。

| 模式 | 做法 | 上限 |
|---|---|---|
| fast | 工具扫描 + 六维基线，只报 BLOCKER | — |
| key | 🔴 文件全审，其余只看 BLOCKER | 每文件 WARN ≤ 5 |
| full | 全部文件全审 + 独立评审子 agent | 每文件 NIT ≤ 3 |

## Step 2 — 工具扫描

被 tt:cr 调用时，它已经跑过 `go-check.sh`，直接读 `.taotao/last-check.json` 和脚本输出，不重复执行。单独使用时自己跑：

```bash
bash <taotao-flow 目录>/scripts/go-check.sh "$PROJECT_ROOT" <BASE>
```

它会依次跑 gofmt / build / vet / golangci-lint / gosec（高危单独判定）/ govulncheck / `go test -race`，结果写入 `.taotao/last-check.json`。lint 告警解读见 `samber:golang-lint`，gosec 与 govulncheck 结果解读见 `samber:golang-security`。

工具结果作为输入，人工只看工具抓不到的问题。`skipped` / `error` 的工具在报告中写明「未执行」，不能算通过。

## Step 2.5 — TDD 证据

有需求目录时，读 `tdd-evidence.py check --json` 的结果（tt:cr 已运行则直接用）。R6 可维护性维度的「测试缺失」以它为准：逐任务列出「TDD 已验证 / 不适用 / TDD 未验证 + 缺项」。不要因为全仓测试通过就认定任务已按 TDD 完成。

## Step 3 — 加载规范

1. `python3 $SKILLS_DIR/taotao-go-standards/detect.py "$PROJECT_ROOT" --stage cr` → Read 返回的 samber skill（至少 error-handling、concurrency、security）；
2. Read `references/go-checklist.md`（本 skill 内置的逐维检查点与默认级别）；
3. 项目有 `docs/rules/forbidden.md` / `code.md` 时一并读：命中 forbidden 直接定 BLOCKER，并引用条目。

## Step 4 — 六维自审

每个维度都要有结论（无问题写"✅ 无"）：

| 维度 | 关注 |
|---|---|
| R1 正确性 | 逻辑与需求一致（对照 Design）、边界值、nil、错误分支、状态机越权转换 |
| R2 健壮性 | 错误包装与返回、context 超时、重试与降级、资源释放 |
| R3 并发安全 | data race、goroutine 泄漏、锁、map 并发写、循环变量捕获（看 Go 版本） |
| R4 安全 | SQL/命令注入、鉴权越权、凭证、敏感日志、路径穿越、SSRF |
| R5 性能 | N+1、循环内 I/O、无界内存、缺索引 |
| R6 可维护性 | 分层越界、职责混杂、重复代码、测试缺失 |

## Step 5 — 独立评审（full 模式）

自审难免受自己写代码时的思路影响。full 模式下派一个**不继承当前会话上下文**的评审子 agent：

1. 按 `$VENDOR/superpowers/skills/requesting-code-review/SKILL.md` 的做法：取 BASE/HEAD SHA，用同目录 `code-reviewer.md` 模板组装派发内容；
2. 模板中 `[DESCRIPTION]` 填本次改动摘要，`[PLAN_OR_REQUIREMENTS]` 填 Design / Plan 路径，`[BASE_SHA]`/`[HEAD_SHA]` 填范围（有未提交改动时先让用户提交到功能分支，或把 `git diff` 写入文件交给它）；额外附上 `references/go-checklist.md` 和 Step 3 加载的 samber skill 路径，要求它按 R1–R6 输出并标注级别；
3. 它的 Critical/Important/Minor 分别映射为 BLOCKER/WARN/NIT；
4. 与自审结果合并：同一位置同一问题去重，标注 `source: self / independent / tool`；两边定级不同时取较高的，并在描述里注明分歧。

没有子 agent 工具时跳过本步，报告注明"未做独立评审"。已有 GitHub PR 且装了官方 `code-review` 插件时，可以建议用户再跑一次 `/code-review` 做 PR 级多 agent 评审。

## Step 6 — 分级

| 级别 | 定义 | 例子 |
|---|---|---|
| **BLOCKER** | 上线大概率出故障、数据错误或安全事故 | SQL 拼接、data race、吞写库错误、无超时调下游、越权 |
| **WARN** | 特定条件下出问题，或明显降低可维护性 | 缺重试降级、错误丢上下文、N+1、缺关键单测 |
| **NIT** | 不影响正确性的改进 | 命名、注释、小重构 |

拿不准往低定一级并写清触发条件，别让 BLOCKER 失去分量。

## Step 7 — 输出

```
## CR 报告（<模式>）
范围：N 个文件（BASE <sha>）· 评分 X.X / 10 · 结论：通过 / 有条件通过 / 不通过
工具（.taotao/last-check.json）：build ✓ · vet ✓ · golangci-lint ✗ · gosec ✓ · govulncheck 未执行（漏洞库不可达）· test -race ✓
独立评审：已做（发现 k 条，其中 j 条自审未发现）/ 未做

| 维度 | 状态 | B / W / N |
|---|---|---|

### BLOCKER
[BLOCKER][R3][self+independent] internal/order/svc.go:88 — 并发写 map `cache`，并发取消会 panic
→ 修复：
​```go
s.mu.Lock(); s.cache[id] = st; s.mu.Unlock()
​```
### WARN …
### NIT …
```

- 评分 `max(1, 10 - BLOCKER×3 - WARN×1 - NIT×0.3)`；
- 每条 BLOCKER/WARN 带 `文件:行` 和可执行修复（代码片段优先）；
- 被 tt:cr 调用时，把问题以 `{level, file, line, dim, desc, source}` 列表和工具结果交回，用于写 cr-status.json。
