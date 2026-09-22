# Changelog — delivery-plan-bootstrap

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

## 1.1.1 — 2026-09-22 — 旧格式计划的升级路径

- Replan 新增「Format upgrade」：方案没变、只是计划用旧格式写的（比如缺 `Why`、
  `How to check`），保留全部 ID、状态、依赖、授权和证据，只把工作包改写成当前格式；
  改写中冒出来的未定选择按阻塞决策处理，不自行补答案。

## 1.1.0 — 2026-09-22 — 吸收 blueprint `plan` 的任务写法

- HARD-GATE 4：工作包里不留待定决策。会改变行为、接口、数据、安全等的选择列为
  阻塞决策，退回 `technical-solution-workflow`。
- 拆分改为按“能工作的结果”，不按文件或技术层；共享契约只归一个工作包；会掩盖
  行为变化的重构单独拆；脚手架、清理类工作包必须有可检查的结果。
- 工作包写给两类读者：先是大白话的 Goal、新增的 Why，再是 Acceptance criteria
  （3–7 条可观察结果）、新增的 How to check（确切命令或 manual 检查）、Scope（只写
  边界）、带版本的 Solution refs、Agent notes（替代 Interface effects）、Non-goals
  （最容易被顺手做掉的相邻工作）。
- 新增 Step 4 两遍自检（人读一遍、新 agent 读一遍）；Gate B 草案列出阻塞决策。
- 追溯矩阵新增 Requirement IDs 列，需求编号原样保留。
- 里程碑边界放在用户想停下来看结果、决定是否继续的地方。
- `check_delivery_plan.py`：新字段必填；待定标记（TBD、TODO、待定…）和未填的模板
  占位符判失败；验收超过 7 条、篇幅超过 700 词、Solution refs 未注明版本、Goal/Why
  里出现需求编号、How to check 不是命令也不是 manual 时给出警告。

## 1.0.2 — 2026-09-22 — 兼容已有交付约定的仓库

- 新增「Existing Delivery Conventions」：只有 `docs/tasks/README.md` 写明
  `Planned by: delivery-plan-bootstrap` 的计划才按本 skill 的格式处理；其他仓库
  （例如用项目专属交付 skill 的 MyStockAgent）不改写里程碑文件，授权只改
  `authorized_milestones`/`current_phase`，并按仓库自己的方式记录。
- `check_delivery_plan.py`：非本 skill 创建的计划跳过里程碑格式检查，只做适配器
  检查；`--strict` 可强制检查。输出新增 `plan_owner`。
- 配套：`gated-delivery-workflow` 里交接路径和授权路由改为只对本 skill 创建的计划生效。

## 1.0.1 — 2026-09-22 — 与通用拆任务 skill 区分触发

- description 写明：仓库有或应有 `.agents/delivery-workflow.json`、AGENTS.md 把规划
  交给本 skill、或方案来自 `technical-solution-workflow` 时，优先于通用的规划/拆任务
  skill（例如 blueprint 的 `plan`）；不用于拆分工单或 GitHub issue。
- `assets/agents-md-snippet.md`：规划、授权、重规划明确不走通用规划 skill。

## 1.0.0 — 2026-09-22 — 首个版本

- Bootstrap / Authorize / Replan 三种模式；方案批准、计划确认、里程碑授权三道门。
- 定义里程碑文件格式，`scripts/check_delivery_plan.py` 校验计划并调用
  `gated-delivery-workflow` 的适配器检查。
