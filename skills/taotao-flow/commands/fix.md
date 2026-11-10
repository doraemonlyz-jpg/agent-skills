# tt:fix — 系统化排查修复

输入：`$ARGUMENTS`（必填）—— 报错现象、复现路径、日志/trace、或性能劣化表现。为空就先问，不要猜。

## Step 0 — 开场

有对应需求目录时 `eval-log.py start --stage fix`。通用 B：默认 `[taotao-debug]`——它以 `superpowers:systematic-debugging` 的四个阶段为骨架（根因调查 → 模式分析 → 假设验证 → 实施），叠加 `samber:golang-troubleshooting` 的 Go 专项手段（pprof、race、goroutine dump、dlv）。

## Step 1 — 定位调用链

查询优先级（有结果就停）：

1. gopls MCP：`go_search` 找入口，`go_symbol_references` 反查调用方；或知识索引 `api.yaml` → `packages.yaml`；
2. 指定目录 grep（禁止全仓盲扫）；
3. 逐层读源码确认。

输出根因假设与 `file:line` 证据，🛑 等用户确认后才写修复代码。"先改一个试试"往往会掩盖真正的问题；systematic-debugging 的铁律也是：没有根因就没有修复。

## Step 2 — 修复（TDD）

1. 先写一个复现问题的失败测试（`taotao-tdd` 的 RED），确认失败原因就是报告的现象；实在无法自动化的写清手工复现步骤；
2. 最小改动修到 GREEN：只改根因涉及的代码，外部调用补齐超时与错误处理，清理本次产生的孤儿代码；
3. 连续 3 次修复失败 → 停下来，按 systematic-debugging 的要求质疑架构假设，和用户讨论，不要继续试。

## Step 3 — 验证

`gofmt -l`、`go vet ./<相关包>/...`、`go test ./<相关包>/... -race -count=1`；性能问题附修复前后对比（benchmark 或 pprof）。按 `superpowers:verification-before-completion`，结论必须附命令输出。

## Step 4 — 收尾

```
✅ 已修复：<根因一句话>
改动：<文件列表>
验证：<测试名 / 命令与结果>
```

修复改变了接口行为或需求理解的，提醒走 `tt:sync` 同步文档；值得记录的坑提醒 `tt:exp`。有需求目录时 `eval-log.py confirm --stage fix`。
