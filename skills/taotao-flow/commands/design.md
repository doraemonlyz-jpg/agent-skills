# tt:design — 技术设计

输入：`$ARGUMENTS` —— 需求名或 ARD 路径；为空读最近修改的 ARD。

## Step 0 — 开场与 input

通用 A → 通用 B（`commands.design.input`；RPC 项目默认含 `samber:golang-grpc`）。

## Step 1 — 读 ARD，提取约束

- 「影响域 → 改动现有代码」：设计只能在清单内改，越界先回 ARD 补充；
- 「高风险节点」：每个都要给出隔离方案（开关 / 接口版本兼容 / 降级 / 灰度）；
- 「下游传播链」：不能破坏既有接口契约，破坏性变更写兼容期方案。

## Step 2 — 规约与现状

1. Read `docs/rules/tech-selection.md`、`forbidden.md`、`code.md`；不引入被禁止的依赖或模式，规约外的新依赖单独列出标"待确认"。
2. 查现有代码作为依据（有结果就停）：知识索引 → gopls MCP（`go_package_api` 看相邻包的公开接口，`go_symbol_references` 看现有调用方式）→ 指定目录 grep。让设计贴合现有写法，不另起炉灶。
3. 用到具体领域时按需读 samber 规范：错误处理 `samber:golang-error-handling`、context `samber:golang-context`、并发 `samber:golang-concurrency`、数据库 `samber:golang-database`、可观测 `samber:golang-observability`、项目结构 `samber:golang-project-layout`。只读相关的，不全读。

## Step 3 — 切片

通用 C：inputSlot 的 `design.md`（taotao-contract：产出/修改 OpenAPI 或 proto，作为接口设计的唯一事实来源）。

## Step 4 — 填模板

模板：`commands.design.output` 非空用它，否则 `templates/Design-Go.md`。不删章节。

Go 后端设计最容易漏的点（模板都有章节，逐个过）：错误码与错误包装、context 超时传递、幂等、事务边界、migration 与索引、缓存一致性、外部依赖超时+重试+降级、goroutine 生命周期、配置与开关、可观测性。

## Step 5 — 润色、确认、落盘

通用 E。落盘后执行 `hooks/after_design.md`；**硬阻断时**告诉用户缺什么，补完重新输出确认，不进入 Plan。

输出：`✅ Design 已保存：<路径>。确认后执行 tt:plan`
