# taotao-flow

涛涛的 Go 后端 AI 研发工具链，Claude Code 和 Codex 通用。本目录是编排 skill，配套的 10 个 `taotao-*` 子 skill 在同级目录。

**taotao-flow**：把一次需求从 PRD 推到上线的流水线。设计吸收自 SkillsHub 的 `soda-ai-workflow`，它依赖的 11 个公司内部 skill 全部换成了开源方案（superpowers、samber/cc-skills-golang、gopls MCP、Humanizer-zh、Trail of Bits 等），按锁定版本拉取。

```
PRD ─▶ tt:ard ─▶ tt:design ─▶ tt:plan ─▶ tt:test ─▶ tt:impl ─▶ tt:cr ─▶ 推送 ─▶ tt:archive ─▶ tt:eval
(Notion/   澄清+影响域  契约+设计    superpowers   TDD 用例   子agent逐任务  六维+独立   提交门禁   知识刷新    效率报告
 文件/URL)  after_ard   after_design  格式计划               +每任务评审    评审+工具   (hook强制)  经验沉淀
```

## 安装

```bash
git clone https://github.com/doraemonlyz-jpg/agent-skills.git ~/Projects/agent-skills && cd ~/Projects/agent-skills
setup/install-taotao.sh              # taotao-* 软链接 + 拉取第三方到 ~/.taotao/vendor + 生成 /tt:* 命令
setup/install-taotao.sh --setup-mcp  # 可选：注册 gopls MCP 与 Notion MCP
```

然后在 Claude Code 里执行一次：

```
/plugin install gopls-lsp@claude-plugins-official
/plugin install code-review@claude-plugins-official     # 可选
```

| 参数 | 作用 |
|---|---|
| `--setup-mcp` | 为 Claude Code / Codex 注册 `gopls mcp` 与 Notion MCP |
| `--codex-legacy` | 额外链接到 `~/.codex/skills`（老版本 Codex） |
| `--no-fetch` | 不联网拉第三方；内网可 `TAOTAO_GIT_MIRROR=<镜像前缀>` 或 `skills/taotao-flow/scripts/fetch-deps.sh --from <已下载目录>` |
| `--uninstall` | 卸载链接和命令文件 |

本机工具：`gopls`（必需）、`golangci-lint`、`gosec`、`govulncheck`、`mockery`、`prism`、`ccusage`（可选，缺了会降级）。`setup/install-taotao.sh` 最后会列出缺哪些和安装命令。

## 用法

```
tt:init                      # 每个项目一次：docs/ 骨架、workflow.config.yaml、规则块、Claude Code hooks
tt:map                       # 知识索引
tt:ard <Notion 链接 | 文件路径 | URL | 需求描述>
tt:design → tt:plan → tt:test → tt:impl → tt:cr
（说"推送/提 PR"时过提交门禁；Claude Code 下 git push 会被 hook 强制检查）
tt:archive <需求名> → tt:eval
```

Claude Code：`/tt:ard`；Codex：`/prompts:tt-ard`；两边也都可以直接打 `tt:ard`。

| 命令 | 说明 |
|---|---|
| `tt:init` | 落地骨架、检测项目类型（HTTP / RPC）、注册 Claude Code hooks 与 git pre-push hook；可重复执行，不覆盖已有文件 |
| `tt:map [--update]` | `go list` 生成包依赖、hubs、路由候选；gopls MCP 校正 |
| `tt:ard` | PRD 输入 → 就绪清单 → 影响域 → 澄清（brainstorming）→ 出稿确认 → 落盘 |
| `tt:design` | 技术设计；契约切片产出 OpenAPI/proto diff；接口四要素硬门禁 |
| `tt:plan` | superpowers writing-plans 格式（`### Task N`、Interfaces、Global Constraints、Review Focus） |
| `tt:test` | 测试方案，用例对应到测试函数名 |
| `tt:impl [--from N] [--inline]` | superpowers SDD：每任务一个新子 agent 实现 + 评审 + 终审；无子 agent 时内联 |
| `tt:cr [--full\|--key\|--recheck\|--pr]` | vet/lint/gosec/govulncheck + samber 规范六维审 + 独立评审子 agent |
| `tt:fix` | systematic-debugging：根因确认后才修，先写复现测试 |
| `tt:mock` | 手写 fake / mockery / gomock / httptest / Prism |
| `tt:sync` | 需求变更：契约→代码→文档联动，记录返工原因 |
| `tt:archive` | 归档、知识增量刷新、tech.yaml 对账、经验沉淀、归档自评 |
| `tt:exp` | 单独沉淀一条经验（有来源、可复用、可操作三条全过才写） |
| `tt:eval` | 本地 HTML 效率报告：阶段耗时、介入、返工、CR、token（Claude Code + Codex 会话） |

## soda 依赖 → 开源替代

| soda 依赖 | 替代 | taotao 适配层 |
|---|---|---|
| code-map | `go list` 索引 + gopls MCP + 官方 gopls-lsp 插件 | tt:map / taotao-impact |
| brainstorming | superpowers `brainstorming` | taotao-clarify |
| code-reviewer | Go 检查表 + superpowers `requesting-code-review` 独立评审 + samber 规范 + 工具扫描（+ 官方 `code-review` 插件） | taotao-review |
| test-driven-development | superpowers `test-driven-development` + samber `golang-testing` | taotao-tdd |
| Humanizer-zh | op7418/Humanizer-zh | taotao-humanize |
| vue-standards-detector | Go 版检测器：go.mod → samber 规范按阶段加载 | taotao-go-standards |
| cooper | Notion MCP / 本地文件 / URL / 粘贴 | taotao-prd |
| bug-analyse | superpowers `systematic-debugging` + samber `golang-troubleshooting` | taotao-debug |
| mock-api | mockery / gomock / httptest / Prism | taotao-mock |
| eval-logger | `eval-log.py` + 会话 token 统计（+ ccusage） | tt:eval |
| code-impact-analysis | gopls `go_symbol_references` + Trail of Bits `differential-review` | taotao-impact |
| dlinter | 本地：golangci-lint + gosec（高危硬失败）+ govulncheck（命中硬失败），结果写 `.taotao/last-check.json` 由门禁读取；公司规则仍可在 `tt:cr --full` 里可选调用 dlinter | go-check.sh / taotao-review |
| great-ui-plus（跨阶段切片） | 后端版：契约优先 | taotao-contract |

superpowers **不全局暴露**：它的 `using-superpowers` / `brainstorming` 会自动接管所有开发任务，和 tt 流程抢主导权，所以只由适配层按路径读取，并在各适配层中写明覆盖了它的哪些步骤（保存位置、交接、分支收尾时机）。samber 的 Go 规范则全局暴露，日常写 Go 时也会自动触发。

## 目录结构

```
skills/taotao-flow/        编排：SKILL.md · commands/ · hooks/ · claude-hooks/ · git-hooks/ · templates/ · scripts/
  deps.lock.json           第三方 skill 锁定清单（仓库 + commit）、插件、MCP、工具
  scripts/fetch-deps.sh    按锁定版本拉取（支持镜像与离线目录）；bump-deps.sh 升级锁定版本
  tests/test_workflow.sh   自测（83 项，覆盖门禁各绕过/漏判场景）
skills/taotao-prd/  taotao-clarify/  taotao-go-standards/  taotao-review/  taotao-tdd/
skills/taotao-debug/  taotao-impact/  taotao-mock/  taotao-humanize/  taotao-contract/
setup/install-taotao.sh    安装 / 卸载（只处理 taotao-*）
evals/taotao-flow/cases/   行为评测用例
```

## 配置与扩展

项目根的 `workflow.config.yaml`：每个阶段的 `input`（挂 skill，可写 `samber:golang-grpc` 这类第三方引用或你自己的 skill）、`output`（换模板）、`impl.mode`（subagent / inline）、`inputSlot`（跨阶段切片）。新增项目类型改 `project-types.yaml`，团队专属检查放项目 `docs/hooks/<同名>.md` 覆盖内置钩子。

## 维护

```bash
skills/taotao-flow/scripts/bump-deps.sh     # 看上游有什么变化，更新锁定版本
skills/taotao-flow/scripts/fetch-deps.sh    # 拉到新版本
skills/taotao-flow/tests/test_workflow.sh   # 自测（需要 go、git、python3）
```

第三方许可证见 [THIRD_PARTY.md](THIRD_PARTY.md)。

## 与本仓库其他 skill 的关系

`technical-solution-workflow → delivery-plan-bootstrap → gated-delivery-workflow` 是另一条通用流水线；taotao-flow 是面向 Go 后端、命令驱动的版本。同一个需求只走其中一条。`coding-standards` 可以挂到 tt:impl / tt:cr 的 `input` 里叠加使用，配置示例见 `templates/workflow.config.yaml`。
