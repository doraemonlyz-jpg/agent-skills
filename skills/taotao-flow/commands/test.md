# tt:test — 测试方案

输入：`$ARGUMENTS` —— 需求名；为空读最近的 ARD + Plan。

## Step 0 — 开场与 input

通用 A → 通用 B（默认 `[taotao-tdd]`，它会带上 `superpowers:test-driven-development` 与 `samber:golang-testing` 的约定）。

## Step 1 — 读 ARD + Design + Plan

用例来源：ARD 功能清单与业务规则（正向）、边界与异常（反向）、Design 的接口与错误码（契约）、Plan 的 Review Focus 与每个任务的验证命令。

## Step 2 — 填模板

`commands.test.output` 非空用它，否则 `templates/Test-Go.md`。

- 用例 ID 连续（TC-01…），`[ ]` 表示未验证；
- 每条写清前置数据、输入、期望输出/错误码，以及**对应的测试函数与子测试名**（`TestCancelOrder/已发货不能取消`），无法自动化的写手工步骤；
- Go 后端侧重：接口契约、业务分支、幂等与并发（`-race`）、事务回滚、超时与降级、P99 基线、权限与越权；
- 测试名与 Plan 中 TDD 步骤的测试名保持一致，tt:impl 的子 agent 会照着写。

## Step 3 — 润色、确认、落盘

通用 E。输出：`✅ Test Plan 已保存：<路径>。确认后执行 tt:impl`
