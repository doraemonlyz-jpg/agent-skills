# 第三方组件与许可证

taotao 工具链**不包含**以下第三方 skill 的源码，`setup/install-taotao.sh`（或 `skills/taotao-flow/scripts/fetch-deps.sh`）会按 `skills/taotao-flow/deps.lock.json` 中锁定的 commit 从上游拉取到 `~/.taotao/vendor/`。taotao-* 适配层只按路径读取它们，并在各自 SKILL.md 中写明哪些部分被 taotao-flow 覆盖。

| 组件 | 上游 | 许可证 | 用途 |
|---|---|---|---|
| superpowers | https://github.com/obra/superpowers | MIT © Jesse Vincent | brainstorming、writing-plans、subagent-driven-development、executing-plans、test-driven-development、systematic-debugging、requesting-code-review、verification-before-completion、using-git-worktrees、finishing-a-development-branch |
| cc-skills-golang | https://github.com/samber/cc-skills-golang | MIT © Samuel Berthe | Go 规范（code-style、error-handling、concurrency、testing、security、gopls 等 46 个） |
| Humanizer-zh | https://github.com/op7418/Humanizer-zh | MIT © 歸藏 | 中文去模板化表达 |
| Trail of Bits skills | https://github.com/trailofbits/skills | CC BY-SA 4.0 © Trail of Bits | differential-review（改动爆炸半径、未覆盖测试） |

外部工具（按需安装，不随本仓库分发）：gopls（BSD-3）、golangci-lint（GPL-3.0，独立二进制）、gosec（Apache-2.0）、govulncheck（BSD-3）、mockery（BSD-3）、go.uber.org/mock（Apache-2.0）、Prism（Apache-2.0）、ccusage（MIT）、Notion MCP（Notion 官方托管）。

Claude Code 官方插件 gopls-lsp、code-review 来自 https://github.com/anthropics/claude-plugins-official（Apache-2.0），在 Claude Code 内通过 `/plugin install` 安装。

设计思路参考：SkillsHub 上的 soda-ai-workflow（滴滴内部），未复制其代码。
