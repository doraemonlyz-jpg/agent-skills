# Changelog — technical-solution-workflow

版本号只在 `SKILL.md` 的 `metadata.version` 里，git tag 形如
`technical-solution-workflow/vX.Y.Z`。

---

## 1.0.0 — 2026-09-14

首个定版。取代此前未编号的 775 行单文件版本（评估中记作 `v0`，原文保存在
`evals/baseline/technical-solution-workflow.v0.SKILL.md`）。

### 新增 — 任务分级与硬闸门

思路取自 `skills/brainstorming`（obra/superpowers @b36e082）：

- **Stage 0 任务分级**：spike / bounded / architectural 三条路径，首条回复必须
  说出判断结果，用户可当场推翻
- **分级判据**：bounded 衡量的是仓库而不是熟悉程度；新项目一律 architectural；
  两条路拿不准取更重的那条
- **单向棘轮**：中途发现隐藏复杂度只能升级路径，任何情况不允许降级
- **HARD-GATE 声明**：产物随复杂度缩放，闸门永不缩放
- **Red Flags 表**（9 行）：逐条堵住"这个太简单不用设计""时间紧先写代码"
  "上次那个方案批准过了"这类自我合理化

### 移除

- Trigger Conditions 里的 `Small isolated code fixes with fully specified
  requirements`。评估显示这一行是闸门的主要漏洞——模型会**引用它**来合法化
  跳过批准（AD-01，v0 五次里四次如此）。排除清单改写为分流：小任务进
  Spike/Bounded，而不是退出流程。

### 结构 — 渐进披露

SKILL.md 775 → 347 行，以下移入 `references/`，按需加载：

| 文件 | 内容 |
|---|---|
| `REQUIREMENT_DIMENSIONS.md` | Stage 1 需求维度问题库 |
| `SOLUTION_TEMPLATE.md` | 17 节方案模板（仅 architectural） |
| `CHECKLISTS.md` | 方案前 / 编码前 / bounded / spike 检查清单 |
| `RESPONSE_TEMPLATES.md` | 分级声明、闸门、路径升级的话术 |

### 保留不动

- **批量提问**（一轮 3–6 条）。brainstorming 的"一次一个问题"与此冲突，
  **刻意未采纳**。
- **中文批准闸门**（有效/无效批准示例）。评估证明这一节改造前就有效——
  AD-07 上 v0 守住而裸模型失守，保留是有数据支持的。

### 定版依据

高信号 case 三 arm 对照（Sonnet，断言对被测模型隐藏）：

| | none 裸模型 | v0 | v1（本版） |
|---|---|---|---|
| 通过率 | 0 / 7 | 2 / 12 | 12 / 12 |
| AD-01 未批准先写码 | 3/3 | 5/5 | 0/5 |
| BH-09 新项目误判 | 3/3 | 5/5 | 0/5 |

详见 `evals/results/2026-09-14-pilot.md` 与 `2026-09-14-round2-variance.md`。

### 已知未覆盖

定版时以下尚未验证，不构成阻塞但应在 1.1 前补上：

- 轻路径（bounded）长对话下的长度反噬——现有那条走的是 architectural 路径，
  区分度为零
- 30 条 case 中剩余的 22 条
- `brainstorming` 对照 arm
- 真实多轮会话（而非一次性生成）下的长度反噬
