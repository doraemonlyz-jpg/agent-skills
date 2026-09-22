# Changelog — coding-standards

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

## 1.1.0 — 2026-09-22 — 最小代码、外科手术式改动、项目风格、测试先行

借鉴来源（吸收原则，未复制原文）：
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)（MIT）的
Think Before Coding / Simplicity First / Surgical Changes；Anthropic
[code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier)
的“清晰优先于简短”；[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT）
的“写新代码前的决策阶梯”和“精简不能删掉校验、错误处理、安全”；blueprint `improve`
的“重构前先补行为测试”。

- **Simplicity First**：写新代码前先走一遍阶梯（真的需要吗 → 代码库里已有 → 标准库 →
  平台或框架自带 → 项目已有的依赖 → 最后才自己写最少的代码）；精简不能删掉校验、
  错误处理、安全检查、无障碍和测试先行要求的测试。ponytail 的“能一行就一行”没有采纳，
  与“清晰优先于简短”冲突。只写解决问题所需的最少代码；不加没人要的功能、选项和
  单次使用的抽象；不为不变量已排除的状态写处理。“最少”指范围最小，不是字符最少，
  清晰优先于简短。收尾自检：资深工程师会不会嫌它过度复杂。
- **Surgical Changes**：每一行改动都能追溯到任务；沿用周围代码的风格；不顺手重构、
  改名、重排无关代码；只清理自己这次改动造成的无用代码；需要的重构单独一步做。
- **Style and Formatting**：项目的格式化和 lint 配置是标准；没有配置时用语言的
  标准工具；只改格式的提交和行为改动分开。
- **Preconditions**：写明改动依赖的假设；需求有多种理解时停下来问。
- **Test-First Rule**：修 bug 和确定性逻辑先写失败的测试。
- 原来偏 Go / 金融项目的规则改成通用写法（超时与取消、精确小数、语言的竞态检查）。
- “处理每个错误”改为“处理每个可能发生的错误”，并在边界处校验，与“不写不可能状态的
  处理”一致。
- Review 清单新增“简洁与范围”；完成报告新增“所做假设”和“注意到但未改动的问题”。

## 1.0.0 — 2026-08-31 — 首个版本（当时未标版本号）
