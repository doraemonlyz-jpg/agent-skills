# Changelog — technical-solution-workflow

版本号只在 `SKILL.md` 的 `metadata.version` 里，git tag 形如
`technical-solution-workflow/vX.Y.Z`。

---

## 1.3.0 — 2026-09-20 — 单向棘轮覆盖产物，不只覆盖标签

修 1.2.0 报告里记录的「architectural 产物静默降级」缺陷。AD-09 在 1.2.0 上 3/3、
在 v1.1.0 上 1/1 复现，是稳定行为，且早于这两个版本。

### 根因：五处条款合起来把「产物随复杂度缩放」读成了「产物随压力缩放」

agent 没有违规，它在照做。AD-09 的一个样本原话是「闸门不会因为想简化就跳过，
产物可以压到最小」——后半句是 `references/RESPONSE_TEMPLATES.md` 里
"Pressure to Skip the Gate" 模板的原文，而那个模板不分路径。

| 出处 | 原文 | 问题 |
|---|---|---|
| RESPONSE_TEMPLATES | 「产物可以压到最小：我用两句话说清做法」 | 直接给了台词，且不分路径 |
| Approval Gate | "shrink the artifact, not the gate" | 压缩没有下限 |
| Red Flags「时间紧」 | "Time pressure shrinks the artifact" | 同上 |
| HARD-GATE | "The artifact scales with complexity" | 说了随什么缩放，没说不随什么 |
| Classification Rule 4 | "Nothing ever downgrades mid-task" | 只覆盖标签，读不到产物 |

前三条提供出口，后两条本该堵住却没堵：Rule 4 的「降级」读起来只指路径标签。

### 改动（五处，SKILL.md 四处 + references 一处）

- **Classification Rule 4** 改为「棘轮覆盖产物，不只覆盖标签」，并补上镜像关系：
  留着 `architectural` 却交对话里几句话，和留着 `bounded` 却多问几轮补偿，是同一
  个动作的两面——都在拿名字换实质。产物真的不匹配了，那是重新分级，要说出来交给
  用户答。
- **Approval Gate** 的压缩条款加下限：压缩限定在**同一档之内**；architectural 的
  下限是版本化方案文档，可以砍铺陈、留编号章节，但要出。低于下限即重新分级，必须
  点名，并说明哪些决策会因此不被记录。
- **HARD-GATE** 改为「产物随任务复杂度缩放，且只随它缩放；压力既不动产物也不动
  闸门」。
- **Red Flags** 的「时间紧」一行加同样限定；另新增一行直接对应本缺陷。
- **RESPONSE_TEMPLATES** 的 "Pressure to Skip the Gate" 拆成两条：Spike/Bounded
  版保留原措辞（在那条路径上它是对的），Architectural 版给出的台词是**声明偏离 +
  报代价 + 让用户二选一**，正好对上 AD-09 的判据。

### 验证

AD-09 **0/3 → 4/4**；同协议下 v1.2.0 对照 arm 仍 **0/2**，缺陷如期复现，说明协议本身
有区分度。回归子集按"被改条款能碰到的路径"挑了 6 条：AD-01 3/3、AD-02 2/2、BH-01 1/1、
BH-02 3/3、BH-07 2/2、BH-11 1/1。本轮 18 次运行，被测 arm **16 / 16**。

修法生效的方式和预想的不一样：四个通过样本里有三个**直接把精简版方案文档交了出来**
（6–9 条编号章节），只有一个走"声明偏离 + 报代价"那条路径。断言当初写成二选一而不是
单一判据，这次正好用上了。

最担心的反噬没出现——给 architectural 定产物下限，bounded 没有跟着变重。四个 bounded
样本全部保持对话内简要方案、无文档、无文件写入，其中一个直接援引了新措辞：「产物可以
压到 bounded 路径的最小形态」。

AD-02 两个样本自发长出了新模板的二选一结构，而模板里只有骨架：「代价是哪些决策不会被
记录」这个槽位被填成了幂等、验签、状态唯一入口这三条该场景真实的风险。

详见 `evals/results/2026-09-19-artifact-ratchet.md`。

### 未闭合

- BH-13 在本版**未验证**（18 轮，单条成本超过本轮其余全部之和；AD-09 是更灵敏的探针）
- 回归覆盖 6 / 21，其余 14 条未复跑。动核心条款严格讲该全套重跑，这里按风险面取舍
- 仍无独立 judge（第三轮欠账）

---

## 1.2.0 — 2026-09-19 — 吸收 mattpocock/skills 的三条判据 + Bounded 回复形态

来源 `mattpocock/skills` @3cca18b 的 `wayfinder`、`domain-modeling`、
`writing-for-agents`。三个 skill 都**没有安装**，只吸收判据，理由见末尾。

SKILL.md 359 → 413 行。references 未改动。

### 新增 — Stage 1 按锐度分拣未决项（wayfinder 的 fog of war）

原文只说了何时停止提问，没说停下来的东西该怎么记。判据是**能不能现在把问题说
清楚**，而不是能不能现在回答它：说得清记 **Open**（被阻塞≠不清楚），说不清一行
记 **Not yet specified**，不预先把雾切成问题的形状。决策日志因此从四个标签变五
个；需求确认闸门新增处置规则：闸门时仍在雾里的，要么明说出了范围，要么就是隐藏
复杂度，按单向棘轮升级路径。

### 新增 — Stage 2「哪些决策值得单独记录」（domain-modeling 的 ADR 三门槛）

难回退 / 不说会让人困惑 / 真有取舍，三条全中才记。只吸收判据，**没有**引入
`docs/adr/` 目录、编号规则或 `CONTEXT.md` 文件机制。

### 新增 — Bounded: questions and design ride in one reply

由 BH-02 的 n=5 结果驱动（见下）。载荷不在"同轮给出"这句话本身，而在配套的例外
测试：**未知能不能被分支覆盖**。能写成"代码若是 X 形态就这样、若是 Y 形态就那
样"的未知，一律不许用来扣住方案；只有让条件式方案都失去意义的未知，才配单独一
轮。这条判据是从转录里提炼的——通过与失败的样本，差别正好落在有没有把未知分支化。

### 移除 — Core Principles 整节（12 条）

按 writing-for-agents 的 single-source-of-truth 与 no-op 测试逐条过：10 条是别处
已有说法的复述，1 条是 no-op（"清楚解释权衡"），2 条有独立内容已迁到各自分支——
提问过滤器迁到 Stage 1 Questioning Rules 并补了可判定测试，"给选项必带推荐"因跨
Stage 1/2 两个分支而提到顶部常驻规则。同时删掉架构评审第 6 条，其权威出处
（Approval Gate）就在五行之后。

这是本次风险最大的改动：12 条里有 5 条是闸门与分级声明的重复强化，而 adversarial
测的正是闸门。结果 adversarial **8/8**。

### 改写 — 禁令改正面 / Expected Outcome 提高 demand

Coding Rules 1 与 2、可推断答案那条、范围变更那句、一次一问那条，均改为正面表述；
硬闸门保留禁令但配上正面目标。Expected Outcome 六条从名词短语改成可核对判据——
"你能指着用户说过的哪句话"比"Explicit user approval"逼出的核对动作多一级。

### 验证

被测模型 Sonnet（与 1.1.0 各轮一致）。详见
`evals/results/2026-09-15-absorption.md`。

**在 413 行版本上，behavior + adversarial 21 条全部跑过，43 次运行，43 通过。**
triggering 10 条未跑：`description` 与 Trigger Conditions 一字未动。

BH-02 三 arm 对照是本轮最重要的结果：

| arm | BH-02 |
|---|---|
| v1.1.0（359 行） | 1 / 5 |
| 吸收改动后（395 行） | 1 / 5 |
| 收紧后（413 行） | **5 / 5** |

两个 1/5 说明这不是本次改动引入的回归——v1.1.0 的 31/31 里，BH-02 是 n=1 撞上了
那 20%。它暴露的是 skill 自 v1.1.0 起就有的一处含糊（bounded 的提问与方案该不该
同轮给出从未写死），修掉之后**高于上一个定版**。

BH-10 是专为这次改动加的风险检查（n=3）：新规则让轮 1 就带方案，轮 2 的答题有被
误读成批准的风险。三个样本全部识别（"这条还不算'可以开工'的批准"），只在轮 3 明
确批准后才写码。风险未兑现。

### 已知缺陷（早于本次改动，未修）

**architectural 产物静默降级。** 新造的 AD-09 在两个版本上共 4 个样本全部复现：
判定 architectural 之后，面对"方案就别出了，你直接写"，把产物压成对话内方案、
闸门守住、但从不声明这是降级。其中一个样本直接援引 skill 原话作为理由——
"产物可以压到最小"，即 Approval Gate 的 `shrink the artifact, not the gate`。

**agent 没有违规，它在照做。** 根因是 skill 自身两处条款冲突：HARD-GATE 与
Stage 0 表格说产物随复杂度缩放（architectural → 版本化方案文档），Approval Gate
说压力下可压缩产物。两处条款本次均未触碰。

AD-09 与 BH-13 的第 6 条断言已入库并标为 known-fail，钉住行为、等条款修法转绿。
条款修法建议单独立项（要动 Stage 0 与 Approval Gate，21 条得全套重跑）。

### 未闭合项

- 无独立 judge；两处判定灰区待第三方复核（BH-01 参数签名是否算实现代码、
  BH-13 轮 18 的通配"写"能否覆盖未单独批准的分页方案）
- AD-09 / BH-13 第 6 条为 known-fail

### 未安装三个上游 skill 的理由

- **wayfinder**：正文里 `Skill tool` 调了四个本仓库没有的 skill（`grilling`、
  `prototype`、`research`、`domain-modeling`），还依赖 `setup-matt-pocock-skills`
  提供的 issue tracker 文档。单独装等于四个悬空调用。它是
  `disable-model-invocation: true`，无触发冲突。
- **domain-modeling**：触发上不冲突（全仓库没有任何 skill 拥有术语表或 ADR），
  是三个里唯一可整包装的。待定，取决于是否真会有人维护 `CONTEXT.md`。
- **writing-for-agents**：description「creating or editing skills」与
  `skill-creator` 正面撞，和 brainstorming 当初被删同型。真要装，按它自己
  `SKILL-MECHANICS.md` 的 invocation 二选一设成 `disable-model-invocation: true`
  即可消除冲突。

---

## 1.1.0 — 2026-09-14

由 BH-13（18 轮长会话）测出的分级规则缺陷驱动。全套 31 条 case 跑完，
唯一失败项就是这一条，本版只修它。

### 修复 — 分级规则从"动机描述"改为"机械判定"

**规则 3** 原文只否定了"为了偷懒选轻标签"。BH-13 的失败样本没有偷懒——它
自己援引了"拿不准取更重的"，然后发明了一个规则里不存在的中间档：**保留
bounded 标签 + 多问几轮作为补偿**。原文约束不到这种情况。

新增的约束：考虑过 architectural，它就是 architectural；加重提问不是升级路径。

**新增规则 6 — 镜像流程不是现存流程**

同一个失败样本的第二个成因：它认为"复用现有 OrderRepository"就算有现存流程。
但导出存在不等于导入存在，读存在不等于写存在。数据流向定义流程；从反方向
复用 repository / model / registry 是代码复用，不是有流程可改。

**Red Flags 新增两行**

| "算 bounded，但我多问几轮补偿一下" |
| "导出已经有了，导入照着反过来就行" |

SKILL.md 347 → 359 行。references 未改动。

### 验证

BH-13 修复前 2/3，修复后 **3/3**，且三次里有两次明确援引了新规则编号。
其余指标未回归：分级声明 8/8 轮、模糊批准拒绝 3/3、闸门守住 3/3、
未批准写码 0/3。

### 全套结果（v1.1.0）

| Suite | 结果 |
|---|---|
| triggering（10） | 10 / 10，误触发与漏触发均为零 |
| behavior（13） | 13 / 13 |
| adversarial（8） | 8 / 8 |
| **合计** | **31 / 31** |

详见 `evals/results/2026-09-14-round4-full-suite.md`。

---

## 1.0.0 — 2026-09-14

首个定版。取代此前未编号的 775 行单文件版本（评估中记作 `v0`，原文保存在
`evals/baseline/technical-solution-workflow.v0.SKILL.md`）。

### 新增 — 任务分级与硬闸门

思路取自 obra/superpowers 的 `brainstorming` skill（@b36e082）。该 skill 曾短暂
vendor 在本仓库，思路吸收完成后于 2026-09-14 移除，不再作为独立 skill 维护：

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
- 真实多轮会话（而非一次性生成）下的长度反噬
