# {需求名称} Implementation Plan

> **执行方式**：由 `tt:impl` 执行——默认按 superpowers:subagent-driven-development 逐任务派子 agent 实现并评审，无子 agent 能力时按 superpowers:executing-plans 内联执行。步骤用复选框（`- [ ]`）跟踪，完成勾 `- [x]`，废弃标 `- [~]` 不删除。
> 任务标题必须是 `### Task N: …`（英文单词 Task + 连续编号），代码块必须闭合，否则任务解析脚本会漏读。

**Goal:** {一句话：这个计划交付什么}

**Architecture:** {2–3 句：整体做法，引用 Design 的方案结论}

**Tech Stack:** Go {版本}，{框架}，{存储/中间件}

**Spec:** `docs/features/active/{需求名}/Design-{需求名}.md`（补充：`ARD-{需求名}.md`）

## Global Constraints

> 从 docs/rules/ 与 Design 逐字摘录，每条一行。每个任务的要求都隐含包括本节。

- Go 版本：{如 go 1.22，可用 for range int、循环变量每次迭代新建}
- 错误处理：`if err != nil` 全覆盖，向上返回用 `fmt.Errorf("动作: %w", err)`；错误码只在接口层转换
- 外部调用：一律带 context 超时；禁止 `http.DefaultClient`
- 日志：{日志库}，必带字段 trace_id、{业务主键}；同一错误只在处理层打一次
- 禁止项：{从 forbidden.md 摘录与本需求相关的条目}
- 新依赖：仅限 tech-selection.md 已登记的；其他须先确认

## Review Focus

> Design 隐含、但没有任何任务测试覆盖、最可能在线上出问题的输入或条件，每条一行（预期行为写清楚）。写完后把每一条对应的测试加到负责该代码的任务里。

- {如：同一订单被并发取消两次 → 只有一次成功，另一次返回 ErrOrderNotCancelable}
- {如：下游通知服务超时 3s → 取消仍成功，通知进入重试队列}

---

### Task 1: {契约 / 数据变更，如 migration：orders 表新增 cancel_reason}

**Files:**
- Create: `migrations/{时间戳}_add_cancel_reason.up.sql`、`….down.sql`
- Modify: `internal/order/repo/model.go:12-20`

**Interfaces:**
- Consumes: 无
- Produces: `repo.Order.CancelReason string`（列 `cancel_reason VARCHAR(255) NOT NULL DEFAULT ''`）

- [ ] **Step 1: 写 up/down migration**
- [ ] **Step 2: 本地库执行 up → down → up，确认可回滚**

Run: `{migrate 命令}`
Expected: 三次执行均成功

- [ ] **Step 3: 提交**

### Task 2: {repo 层方法}

**Files:**
- Modify: `internal/order/repo/order.go`
- Test: `internal/order/repo/order_test.go`

**Interfaces:**
- Consumes: Task 1 的 `CancelReason` 字段
- Produces: `func (s *Store) Cancel(ctx context.Context, id int64, from []Status, reason string) (bool, error)` —— 条件更新，返回是否命中

- [ ] **Step 1: 写失败测试**

```go
func TestStore_Cancel(t *testing.T) {
	tests := []struct {
		name   string
		status Status
		want   bool
	}{
		{name: "待支付可取消", status: StatusPending, want: true},
		{name: "已发货不命中", status: StatusShipped, want: false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// …
		})
	}
}
```

- [ ] **Step 2: 运行确认失败**

Run: `go test ./internal/order/repo -run TestStore_Cancel -v`
Expected: FAIL（Cancel 未定义）

- [ ] **Step 3: 最小实现（`UPDATE … WHERE id = ? AND status IN (?)`，占位符参数）**
- [ ] **Step 4: 运行确认通过**

Run: `go test ./internal/order/repo -run TestStore_Cancel -race -v`
Expected: PASS

- [ ] **Step 5: 提交**

### Task 3: {service 层：状态校验 + 幂等 + 事务}

…同上结构…

### Task 4: {接口层：handler / RPC 实现，参数校验与错误码映射}

…

### Task 5: {健壮性与可观测：下游超时/重试/降级、日志字段、metrics}

…

### Task 6: 收尾验证

**Files:** 无新增

- [ ] **Step 1: 全量检查**

Run: `gofmt -l . && go vet ./... && golangci-lint run --new-from-rev={base} && go test ./... -race -count=1`
Expected: 无输出 / 全部 PASS

- [ ] **Step 2: 清理调试输出与注释代码；必要时 tt:map --update**

---

## 高风险任务说明

| 任务 | 风险 | 兜底 / 开关 |
|---|---|---|

## 待确认

- [ ] …

## 执行留痕

> tt:impl 的裁决（Ruling）与偏差记录追加在这里：`YYYY-MM-DD Task N — Ruling: 决定 — 原因 — 若错的代价`
