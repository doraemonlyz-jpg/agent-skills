# Changelog — taotao-flow

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

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
