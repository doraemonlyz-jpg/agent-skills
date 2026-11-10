# Changelog — taotao-flow

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

## 2.2.0 — 2026-11-10 — 逐任务测试证据

- 新增 `scripts/tdd-evidence.py`：实际运行 `go test` 后按任务记录证据到 `tdd-evidence.jsonl`（追加写、哈希链）。
  - bugfix / behavior：`red`（改动前失败，失败原因须匹配 `--expect`；环境故障、改动前已通过、无关断言或 panic、未用 `-run` 限定一律判无效）→ `green`（重跑同一命令通过，且代码确有变化）。
  - refactor：`baseline` → `after`（改动前后同一组行为测试都通过）。
  - 实现后补的入口 / 集成 / 并发测试用 `verify` 记录，标明实现后执行与时间，不算红灯。
  - `check` 按 Plan 中每个任务的 `**TDD:**` 类型逐任务核验，输出「TDD 已验证 / 不适用 / TDD 未验证 + 缺项」。
- tt:plan：每个任务声明 `**TDD:**` 类型；Plan 模板的 TDD 步骤改为调用脚本。
- tt:impl：派发给实现子 agent 时要求记录证据，任务评审时先核对证据。
- tt:cr：新增 Step 3.5 逐任务核验，报告单列「TDD 证据」；全仓测试通过不能替代；默认作为 WARN，`cr.tdd_gate: block` 时作为 BLOCKER；cr-status.json 增加 `tdd` 字段。
- 协议文档 `commands/_tdd-evidence.md`；自测增加 24 项（三个验收任务、编译型红灯、各类无效红灯、证据被篡改）。

## 2.1.0 — 2026-11-10 — 提交门禁 6 个 P0 与本地扫描链路

依据独立评测报告修复：
- commit-gate：首次推送扫描已提交内容；扫描未暂存的已跟踪改动；只认当前分支（branch 字段）且 headCommit 可达的 CR 结论；结论文件损坏、result 非法、commitReady=false、脚本异常一律拦截（失败即拦截）；新增 Bearer token、DSN 内网 IP 识别。
- pre-bash hook：按 shell 词法识别 git push/commit/merge 与 gh pr create/merge（含 bash -c、绝对路径、git -c/-C）；命令前缀 TAOTAO_GATE=off 生效并写审计日志；警告改为 permissionDecision=ask；功能分支 merge 主干放行。
- 新增 git 原生 pre-push hook（tt:init 安装），Codex / IDE / 终端推送同样受门禁。
- go-check.sh：gosec 高危、govulncheck 命中判硬失败，结果写 .taotao/last-check.json 由门禁读取；tt:cr / tt:impl 中改为必须执行的脚本步骤。
- 重复 tt:init 不再追加 hook。

## 2.0.0 — 2026-11-09 — 开源工具链替换 soda 内部依赖

- 第三方 skill（superpowers、samber/cc-skills-golang、Humanizer-zh、Trail of Bits）按 deps.lock.json 锁定版本拉取到 ~/.taotao/vendor。
- tt:impl 改用 superpowers subagent-driven-development；Plan 模板改为 writing-plans 格式。
- 新增 tt:mock、tt:eval、Claude Code hooks、项目类型注册表、inputSlot 跨阶段切片。

## 1.0.0 — 2026-11-09 — 首版

借鉴来源（吸收设计，未复制原文）：SkillsHub soda-ai-workflow 的命令驱动、钩子门禁、配置化、分层上下文与产物契约。
