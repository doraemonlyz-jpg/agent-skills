---
name: taotao-impact
description: 基于 git diff 分析 Go 改动的影响面：提取被改的导出符号，用 gopls MCP（go_symbol_references）精确找出项目内调用方与反向依赖包，按高/中/低风险分级并给回归测试建议；改动涉及鉴权、资金、加解密、外部输入解析时，叠加 Trail of Bits differential-review 的爆炸半径与未覆盖测试分析。被 taotao-flow 的 tt:cr --full/--key 与 tt:ard 调用；用户问"这次改动会影响哪些地方""改这个函数要回归什么""这个包被谁用了"时也应使用。替代 soda 依赖的 code-impact-analysis。
metadata:
  version: 2.0.0
  short-description: Go 改动影响面（gopls + differential review）
---

# taotao-impact — Go 改动影响面（适配层）

回答三个问题：改了什么对外可见的东西、谁在用它、要回归测什么。

`$VENDOR` = `${TAOTAO_VENDOR:-~/.taotao/vendor}`。

## Step 1 — 收集改动

```bash
BASE=<调用方给的 BASE；否则 merge-base 主干>
git diff --name-status "$BASE"...HEAD
git diff -U0 "$BASE"...HEAD -- '*.go' '*.proto' '*.thrift' 'openapi*.yaml' '*.sql'
```

`_test.go` 单独列出；跳过生成代码与 vendor。

## Step 2 — 提取接口面

| 类别 | 判定 | 影响 |
|---|---|---|
| 导出函数/方法签名变化 | `func Xxx(` 行被改 | 调用方要跟着改，编译期能发现 |
| 导出函数行为变化 | 函数体改了，签名没变 | 调用方编译通过但行为可能变——最危险 |
| 导出类型/字段/tag 变化 | struct 字段增删、json/db tag 变 | 序列化、DB 映射、调用方 |
| 接口定义变化 | `type Xxx interface` | 所有实现者 |
| 常量/错误变量 | `const` / `var ErrXxx` | 依赖这些值判断的调用方 |
| 契约 | 路由、proto/thrift/OpenAPI、MQ topic | 外部调用方，跨服务 |
| DB / 配置 | migration、model、配置项 | 数据与运行时 |
| 未导出实现 | 小写符号 | 只影响本包 |

## Step 3 — 追踪调用方

按精确度从高到低：

1. **gopls MCP**（首选）：`go_search` 定位符号 → `go_symbol_references` 拿全部引用；接口变化用 implementation 查询找实现者；需要看相邻包接口时用 `go_package_api`。工具清单与用法见 `$VENDOR/cc-skills-golang/skills/golang-gopls/SKILL.md`（及其 `references/mcp.md`）。
2. **Claude Code LSP 工具**（装了官方 `gopls-lsp` 插件时）：按 `file:line:col` 查 references / call hierarchy。
3. **gopls CLI**：`gopls references <file>:<line>:<col>`、`gopls call_hierarchy …`。
4. **知识索引 / go list**：`docs/knowledge/packages.yaml` 的 `dependents` 或 `go list -f '{{.ImportPath}} {{join .Imports " "}}' ./...` 得到反向依赖包，再在这些包目录里 grep 符号名。

追 1–2 跳：直接调用方，以及调用方是否又是导出符号/接口入口。反射、依赖注入容器、跨服务调用无法静态追踪，列入"需人工确认"。

## Step 4 — 安全敏感改动加做 differential review

改动触及鉴权/权限、资金/计费、加解密/签名、外部输入解析（反序列化、文件路径、URL）、或删除了校验逻辑时：

Read `$VENDOR/trailofbits-skills/plugins/differential-review/skills/differential-review/SKILL.md`，按它的方法补做：git blame 看被改代码的历史（是否曾修过同类 bug）、按调用方数量算爆炸半径、标出没有任何测试覆盖的改动函数。它要求生成报告文件——被 tt:cr 调用时不单独落盘，把结论并入本 skill 的输出；单独使用且用户需要时再写文件。

## Step 5 — 风险分级

| 级别 | 条件（满足任一） |
|---|---|
| 🔴 高 | 导出函数行为变化且调用方 ≥ 3；hubs 包；接口定义变化；契约变化；DB 写/事务/资金订单核心链路；并发原语或共享状态；安全敏感且无测试覆盖 |
| 🟡 中 | 导出符号变化但调用方 < 3；只读查询逻辑变化；配置项变化 |
| 🟢 低 | 未导出实现、日志、注释、测试文件 |

## Step 6 — 输出

```
📊 影响面分析（BASE <sha>，N 个文件；查询方式：gopls MCP / LSP / grep）

🔴 高风险
- internal/order/service/cancel.go
  · CancelOrder 行为变化（新增状态校验）
  · 调用方：api/order/handler.go:45、internal/job/timeout.go:88、internal/refund/svc.go:120
  · 无测试覆盖的改动：CancelOrder 的已退款分支
  · 回归：超时自动取消、退款中的取消
🟡 中风险 …
🟢 低风险 …

建议回归
1. go test ./internal/order/... ./internal/refund/... ./internal/job/... -race
2. 手工：退款流程端到端
需人工确认：<反射调用 / DI 注入 / 跨服务调用方>
```

被 tt:cr 调用时只返回分级结果；被 tt:ard 调用时返回改动入口、传播链和高风险节点，填 ARD「影响域分析」。
