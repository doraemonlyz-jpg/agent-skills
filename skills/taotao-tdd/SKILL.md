---
name: taotao-tdd
description: Go 测试驱动开发：先写失败的表驱动测试（RED），再写最少代码让它通过（GREEN），最后重构（REFACTOR）。以 superpowers 的 test-driven-development 为方法内核、samber 的 golang-testing 为 Go 约定。被 taotao-flow 的 tt:test、tt:impl、tt:fix 调用；用户说"先写测试""TDD""给这个函数补单测""怎么测这段 Go 代码""帮我 mock 掉下游"时也应使用。
metadata:
  version: 2.1.0
  short-description: Go 测试驱动（TDD 适配层）
---

# taotao-tdd — Go 测试驱动（适配层）

`$VENDOR` = `${TAOTAO_VENDOR:-~/.taotao/vendor}`。

## 内核

1. Read `$VENDOR/superpowers/skills/test-driven-development/SKILL.md`：RED → GREEN → REFACTOR 循环、"测试必须先看到失败且失败原因正确"、不为通过测试而写测试、每轮只加一个行为。需要判断测试好坏时再读同目录 `writing-good-tests.md`。
2. Read `$VENDOR/cc-skills-golang/skills/golang-testing/SKILL.md`：表驱动、子测试、`t.Helper`/`t.Cleanup`/`t.Parallel`、httptest、benchmark、fuzz、`-race`。项目用 testify 时再读 `golang-stretchr-testify`。

vendor 缺失时按下方速查执行。

## 速查（兜底）

```go
func TestCancelOrder(t *testing.T) {
	tests := []struct {
		name    string
		status  Status
		wantErr error
	}{
		{name: "待支付可以取消", status: StatusPending},
		{name: "已发货不能取消", status: StatusShipped, wantErr: ErrInvalidState},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			svc := newTestService(t, withOrder(1, tt.status))
			err := svc.CancelOrder(context.Background(), 1)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("CancelOrder() err = %v, want %v", err, tt.wantErr)
			}
		})
	}
}
```

- 错误用 `errors.Is/As` 比较；失败信息格式 `Func(args) = got, want want`；
- 并发/幂等：`sync.WaitGroup` 起 N 个 goroutine 同时调用，断言最终状态；所有测试在 `-race` 下跑；
- 依赖替身怎么选见 `taotao-mock`（手写 fake 优先，需要校验调用时再用 mockery/gomock；SQL 优先 testcontainers，Redis 用 miniredis，HTTP 下游用 httptest）。

```bash
go test ./internal/order/... -run 'TestCancelOrder/已发货' -v
go test ./... -race -count=1
```

## 证据：每一步都要留下脚本记录

在 taotao-flow 里，"我跑过了、看到失败了"不算数，要用 `taotao-flow/scripts/tdd-evidence.py` 跑，让它把命令、输出摘要、代码状态写进 `tdd-evidence.jsonl`。完整规则见 `taotao-flow/commands/_tdd-evidence.md`，要点：

- 红灯命令必须用 `-run` 限定目标测试，`--expect` 写具体失败信息（`Discount\(10000\) = 10000, want 9000`、`undefined: Max`），不写 `FAIL`；
- 改动前就通过、环境故障（网络/模块/Docker/路径）、失败在别的断言上，都会被判为无效红灯——这时修测试或环境再跑，不要绕过；
- 纯重构用 `baseline` / `after`：改动前后同一组行为测试都通过；
- 实现后才写的入口、集成、并发测试用 `verify --label` 记录，会注明实现后执行；它们算验证，不算 TDD。

## 按调用方

- **tt:test**：为每条用例指定测试函数与子测试名，填进 Test Plan「对应测试」列；无法自动化的写手工步骤。
- **tt:impl**：Plan 每个任务本身就是 TDD 步骤（写失败测试 → `red` → 实现 → `green` → 提交；重构为 `baseline` → 重构 → `after`），子 agent 照做，不跳"确认失败"这一步。
- **tt:fix**：先写复现 Bug 的失败测试，用 `red --expect '<报告里的错误现象>'` 记录，确认失败原因就是报告的现象，再修复并 `green`；测试留作回归。没有需求目录时证据记到 `docs/features/active/fix-<简述>/`。
