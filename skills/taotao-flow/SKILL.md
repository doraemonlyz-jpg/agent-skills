---
name: taotao-flow
description: 涛涛的 Go 后端 AI 研发流水线编排器：PRD → 需求分析(ARD) → 技术设计 → 开发计划 → 测试方案 → 子 agent 逐任务编码 → CR → 提交门禁 → 归档沉淀 → 效率评测，每个阶段落盘前停下等人确认，带硬阻断/软警告门禁，串起 superpowers、samber Go skills、gopls MCP、Humanizer-zh 等第三方工具链。凡是用户输入 tt:init / tt:map / tt:ard / tt:design / tt:plan / tt:test / tt:impl / tt:cr / tt:fix / tt:mock / tt:sync / tt:archive / tt:exp / tt:eval（含 /tt:xxx、/prompts:tt-xxx 形式），或说"按流程走这个需求""出个 ARD/技术方案/开发计划""按 Plan 开始写代码""提交前 CR 一下""归档这个需求""看看这个需求 AI 帮了多少"时，都应使用本 skill。普通问答、改个变量名这类小事不要触发。
metadata:
  version: 2.1.0
  short-description: Go 后端 AI 研发流水线编排（tt:* 命令）
---

# taotao-flow — Go 后端 AI 研发流水线

把研发流程编码成 AI 的行为规则：**文档不落盘不进下一阶段，文档没确认不写代码，推送前必须过 CR**。
目标不是让 AI 更聪明，而是给它一个工程师的工作环境：有轨道、有检查点、有记录、能复盘。

设计来自 soda-ai-workflow（命令驱动 + 钩子门禁 + 配置化 + 分层上下文 + 产物契约 + 效率评测）。soda 依赖的公司内部 skill 全部换成了开源工具链，见下方「工具链」。

## 路径约定

| 变量 | 含义 | 解析方式 |
|---|---|---|
| `$FLOW_ROOT` | 本 SKILL.md 所在目录 | 运行时取绝对路径 |
| `$SKILLS_DIR` | 兄弟 skill 目录（taotao-review 等） | `$FLOW_ROOT/..`；找不到再查 `~/.agents/skills`、`~/.claude/skills`、`~/.codex/skills` |
| `$VENDOR` | 第三方 skill 锁定版本 | `${TAOTAO_VENDOR:-~/.taotao/vendor}`，由 `setup/install-taotao.sh`（或 `$FLOW_ROOT/scripts/fetch-deps.sh`）按 `$FLOW_ROOT/deps.lock.json` 拉取 |
| `$PROJECT_ROOT` | 当前 Git 仓库根 | `git rev-parse --show-toplevel` |

**第三方 skill 的引用写法**：文中出现 `superpowers:<name>` 就 Read `$VENDOR/superpowers/skills/<name>/SKILL.md`；`samber:<name>` 对应 `$VENDOR/cc-skills-golang/skills/<name>/SKILL.md`；`tob:<plugin>/<skill>` 对应 `$VENDOR/trailofbits-skills/plugins/<plugin>/skills/<skill>/SKILL.md`。第三方 skill 内部再引用 `superpowers:xxx` 时用同样的规则解析。

vendor 缺失时：提示运行 `bash $FLOW_ROOT/scripts/fetch-deps.sh`，然后用 taotao 适配层里的内置兜底内容继续，不让整条流水线停摆。

## 触发规则：只认命令

只有显式命令才进入流水线；其他对话直接回答，不加载阶段文件。流程可预期，用户才知道 AI 此刻在哪个阶段、会不会改文件。

收到 `tt:<name>` 时，先 Read `$FLOW_ROOT/commands/<name>.md`，严格按该文件执行。

| 命令 | 做什么 |
|---|---|
| `tt:init` | 落地 docs/ 骨架、配置、规则块、Claude Code hooks，检测项目类型 |
| `tt:map [--update]` | `go list` 生成包依赖/hubs/路由候选，配合 gopls MCP 做语义查询 |
| `tt:ard` | 需求分析：PRD 输入（Notion/文件/URL/粘贴）→ 影响域 → 澄清 → 出稿确认 → 落盘 |
| `tt:design` | 技术设计，落盘后过接口四要素硬门禁 |
| `tt:plan` | superpowers 格式的开发计划（`### Task N`），可直接交给子 agent 执行 |
| `tt:test` | 测试方案，用例对应到具体 `go test` |
| `tt:impl [--from N] [--inline]` | 子 agent 逐任务实现 + 每任务评审（superpowers SDD），无子 agent 能力时内联执行 |
| `tt:cr [--full\|--key\|--recheck\|--pr]` | 六维 CR + 独立评审子 agent + 工具扫描，结论写 cr-status.json |
| `tt:fix` | 系统化排查：根因确认后才写代码，先写复现测试 |
| `tt:mock` | 接口/下游 mock：mockery·gomock / httptest / Prism |
| `tt:sync` | 需求变更：代码和四份文档联动，记录返工 |
| `tt:archive` | 归档、刷新知识索引、tech.yaml 对账、沉淀经验、归档自评 |
| `tt:exp` | 单独沉淀一条经验（过门槛才写） |
| `tt:eval` | 本地效率评测报告：各阶段耗时、人工介入、返工、token、CR 评分 |

典型顺序：`tt:ard → tt:design → tt:plan → tt:test → tt:impl → tt:cr → 推送 → tt:archive → tt:eval`。小需求可跳过 test；design/plan 不能跳，它们是 impl 的输入。

## 六条贯穿全程的纪律

1. **先出全文，确认后落盘。** 每份文档完整输出给用户，收到"确认/OK/可以"才写文件；有修改意见就改完再给一遍。静默落盘会让人失去对方向的控制，后面所有阶段都建立在没审过的内容上。
2. **确认隔离。** 一次"确认"只推进一步，不代表后续步骤可以合并或跳过。唯一例外是 tt:impl：任务清单确认后，子 agent 连续执行，只在规定的停止条件下停。
3. **门禁分两档。** 🚫 硬阻断：停下，说明缺什么、怎么恢复；⚠️ 软警告：列出问题，用户回复"继续"即放行。钩子定义见 `hooks/README.md`。
4. **项目规约最高优先级。** `docs/rules/` 高于 Design、Plan 和任何第三方 skill 的建议。命中 `forbidden.md` → 硬阻断；引入 `tech-selection.md` 未列出的依赖 → 先问。
5. **需求变更先改文档再改代码。** 听到"改一下""接口变了""产品要求变了"，或 ARD 比 Design 新，先走 `tt:sync`。
6. **证据先于断言。** 说"完成/通过/修好了"之前必须跑过验证命令并看到输出（`superpowers:verification-before-completion`）。

## 工具链（替代 soda 的内部依赖）

| 环节 | 用什么 | taotao 适配层 |
|---|---|---|
| PRD 输入 | Notion MCP / 本地文件(md/pdf/docx) / URL / 粘贴 | `taotao-prd` |
| 需求澄清 | `superpowers:brainstorming` 的提问与方案对比方法 | `taotao-clarify` |
| Go 规范检测 | 读 go.mod 判断版本与框架 → 按阶段加载 `samber:golang-*` | `taotao-go-standards` |
| 代码知识 | `go list`（tt:map）+ gopls MCP（`go_search`/`go_symbol_references`/`go_package_api`）+ 官方 `gopls-lsp` 插件 | `tt:map` / `taotao-impact` |
| 影响面 | gopls 引用 + `tob:differential-review/differential-review`（爆炸半径、未覆盖测试） | `taotao-impact` |
| 计划与执行 | `superpowers:writing-plans` 格式 → `superpowers:subagent-driven-development`（降级 `executing-plans`） | `tt:plan` / `tt:impl` |
| 测试 | `superpowers:test-driven-development` + `samber:golang-testing` | `taotao-tdd` |
| 排查 | `superpowers:systematic-debugging` + `samber:golang-troubleshooting` | `taotao-debug` |
| Mock | mockery·gomock、httptest、Prism | `taotao-mock` |
| CR | Go 六维检查表 + `superpowers:requesting-code-review` 独立评审 + `samber:golang-security` + golangci-lint/gosec/govulncheck；可选官方 `code-review` 插件 | `taotao-review` |
| 中文润色 | `op7418/Humanizer-zh` | `taotao-humanize` |
| 效率评测 | 阶段计时（eval-log.py）+ Claude Code / Codex 会话 token 统计 + 可选 ccusage | `tt:eval` |
| 分支收尾 | `superpowers:finishing-a-development-branch` | `before_commit` 钩子 |

## 项目配置：workflow.config.yaml

单文件、默认基线 + 增量覆盖：不存在或字段为空就用内置默认。完整样例 `templates/workflow.config.yaml`，项目类型默认值见 `project-types.yaml`。

```yaml
project: { name: my-service, type: backend-go }   # backend-go | backend-go-rpc
inputSlot: [taotao-contract]                       # 跨阶段切片
commands:
  ard:    { input: [taotao-clarify], output: [ARD.md] }
  design: { input: [],               output: [Design-Go.md] }
  plan:   { input: [],               output: [Plan-Go.md] }
  test:   { input: [taotao-tdd],     output: [Test-Go.md] }
  impl:   { input: [taotao-go-standards], mode: subagent }   # subagent | inline
  cr:     { input: [taotao-review] }
  fix:    { input: [taotao-debug] }
  mock:   { input: [taotao-mock] }
```

- `input`：阶段开始前按顺序 Read 并执行的 skill（在 `$SKILLS_DIR` 下按名找 `<name>/SKILL.md`；也可写 `samber:golang-grpc`、`superpowers:xxx` 这类第三方引用；你自己的 skill 也可以挂）。找不到时提示一次并跳过。
- `output`：模板文件名，相对 `$FLOW_ROOT/templates/`；以 `./` 开头表示项目内路径。
- `inputSlot`：**跨阶段切片**。对列表中每个 skill S，执行到阶段 X 时若存在 `$SKILLS_DIR/S/X.md` 就 Read 并作为子流程执行，不存在则该阶段不参与。切片先读上一阶段产物自检，上游没启用就自动跳过。切片产出由主流程在落盘时并入文档（作为独立章节或任务），切片自己不写顶层文档。内置切片 `taotao-contract`：契约优先（OpenAPI / proto / thrift 贯穿 ARD→Design→Plan→Impl→CR）。

## 上下文分层加载

| 层 | 内容 | 何时读 |
|---|---|---|
| Tier 1 规则层（常驻） | CLAUDE.md / AGENTS.md 中 init 注入的规则块 + `docs/knowledge/index.md` 薄路由 | 每次会话 |
| Tier 2 知识层（按意图） | `docs/knowledge/{packages,api,tech,terms}.yaml`、`experiences/`；gopls MCP 实时查询 | 命令需要时从 index.md 路由进去，不全量加载 |
| Tier 3 源码层（按需） | 具体 `.go` 文件 | 执行任务时读，用完即丢 |

各命令读什么：ard/design → index.md + packages.yaml + terms.yaml + 相关 experiences；plan → tech.yaml；fix → gopls 引用 / packages.yaml 定位调用链再读源码；cr → 不读知识层，只看 diff。

## 产物契约

```
docs/
├── rules/          code.md  forbidden.md  tech-selection.md         # 人工维护，init 只首次创建
├── knowledge/      index.md packages.yaml api.yaml tech.yaml terms.yaml manifest.yml experiences/
├── eval/           <日期>-report.html                                 # tt:eval 生成
└── features/
    ├── active/<需求名>/
    │   ├── PRD-source.md                                               # 输入快照与来源链接
    │   ├── ARD-<需求名>.md  Design-<需求名>.md  Plan-<需求名>.md  Test-<需求名>.md
    │   ├── progress.md        # 阶段状态，每个命令收尾时更新
    │   ├── eval-log.json      # 阶段计时、介入、返工（eval-log.py 维护）
    │   └── cr-status.json     # tt:cr 结论，提交门禁读取
    └── completed/YYYY-MM/<需求名>/
.superpowers/sdd/   # tt:impl 子 agent 执行的 ledger、任务简报、评审包（自动 gitignore）
```

- **阶段计时**：每个文档类命令开始时 `python3 $FLOW_ROOT/scripts/eval-log.py start --feature <需求名> --stage <阶段>`，用户确认落盘后 `... confirm ...`；实质性问答用 `... note ...` 记一条。不向用户展示这些命令的输出。
- Plan 任务勾选：`- [ ]` → `- [x]`；废弃 `- [~]`，不删除。
- 文档不大面积覆写：只改相关段落，改动处追加 `> 变更记录：YYYY-MM-DD 摘要`。
- 中文文档落盘前用 `taotao-humanize` 处理一遍。

## Claude Code 与 Codex 的差异

- **Claude Code**：`tt:init` 会在项目 `.claude/settings.json` 注册两个 hook：写入 ARD/Design 后自动提醒跑对应检查；执行 `git push`、`gh pr create`、主干上 `git commit`/`git merge` 前自动跑提交门禁，不通过直接拦下，警告弹给用户确认。另有 git 原生 pre-push hook 兜底。斜杠命令 `/tt:<name>`。
- **Codex**：没有 Claude Code 那样的工具调用 hook，但 `tt:init` 安装的 git 原生 pre-push hook 同样生效——推送时 git 会跑提交门禁。其余阶段门禁靠 AGENTS.md 规则块约束。提示词命令 `/prompts:tt-<name>`。子 agent 不可用时 tt:impl 自动降级为内联执行。
