# tt:plan — 开发计划（superpowers 格式）

输入：`$ARGUMENTS` —— 需求名或 Design 路径；为空读最近的 Design。

Plan 是 tt:impl 的执行清单，会被逐任务交给子 agent，每个子 agent **只看得到自己那一个任务**。所以每个任务都要自带完成它所需的全部信息：改哪些文件、对外暴露什么接口、怎么验证。

## Step 0 — 开场与 input

通用 A → 通用 B。

## Step 1 — 读方法论

Read `superpowers:writing-plans`，采用它的**任务拆分粒度、Task 结构、Global Constraints、Review Focus** 写法。以下几处以 taotao-flow 为准，覆盖它的原文：

- 保存位置：`docs/features/active/$FEATURE/Plan-$FEATURE.md`（不是 `docs/superpowers/plans/`）；
- 文件头使用 `templates/Plan-Go.md` 的头部（`**Spec:**` 指向本需求的 Design 和 ARD）；
- 写完不询问执行方式、不交接给其他 skill：按通用 E 等用户确认，下一步由用户执行 tt:test / tt:impl。

vendor 缺失时直接按 `templates/Plan-Go.md` 的结构写。

## Step 2 — 读 Design、ARD 影响域、tech.yaml

排序原则：

- 契约与数据变更先行（migration 带回滚 SQL；契约生成代码）；
- 纯新增的包/文件可排前，风险低；
- 改动 hub 包、共享包的任务单独成条，写清回归范围；
- 高风险节点相关任务靠后，必须带开关或兜底验证；
- 用到的库都已在 `tech.yaml` / `tech-selection.md`，否则在任务里标「需新增依赖，待确认」。

**Global Constraints** 从 `docs/rules/` 和 Design 中逐字摘录：Go 版本、禁止项、错误包装约定、日志字段、命名规则等。它们会原样交给每个任务的实现者和评审者。

## Step 3 — 切片

通用 C：inputSlot 的 `plan.md`（taotao-contract 会插入「契约落地 + 代码生成」「契约 mock」任务），并入统一编号。

## Step 4 — 填模板

`templates/Plan-Go.md`。硬性格式（tt:impl 的脚本按此解析）：

- 任务标题必须是 `### Task N: <标题>`，`Task` 用英文单词，N 连续；
- 每个任务含 **Files**、**Interfaces**（Consumes / Produces，写精确签名）、**TDD** 类型、带复选框的步骤；
- `**TDD:**` 取值 `bugfix` / `behavior` / `refactor` / `none — <原因>`，含义见 `commands/_tdd-evidence.md`。tt:cr 按这一行逐任务核验证据，不写默认按 behavior 检查；
- TDD 节奏写成可执行的步骤：bugfix/behavior 为 写失败测试 → `tdd-evidence.py red`（带 `--expect` 具体失败信息）→ 最小实现 → `tdd-evidence.py green` → 提交；refactor 为 `baseline` → 重构 → `after` → 提交；
- 每个任务以一条可独立执行的验证命令结尾（如 `go test ./internal/order/service -run TestCancelOrder -race`）；
- 代码块必须闭合（未闭合的 ``` 会让后面的 Task 标题被解析器忽略）。

## Step 5 — 自检

```bash
for n in $(grep -oE '^#+ +Task +[0-9A-Za-z]+' Plan-$FEATURE.md | awk '{print $3}'); do
  bash "$VENDOR/superpowers/skills/subagent-driven-development/scripts/task-brief" Plan-$FEATURE.md "$n" >/dev/null || echo "Task $n 解析失败"
done
```

有解析失败就修格式再输出。

## Step 6 — 润色、确认、落盘

通用 E。输出：`✅ Plan 已保存：<路径>（N 个任务）。下一步 tt:test（可选）或 tt:impl`
