# technical-solution-workflow Evals

评估 `technical-solution-workflow` 吸收 Spike/Bounded/Architectural 三分法与硬闸门
之后，相对改造前版本的行为变化。

## 测什么

| Suite | 条数 | 测什么 | 目标失效形态 |
|---|---|---|---|
| `cases/triggering.yaml` | 10 | 该不该触发、判成哪条路径 | 误触发（小改动被拉进重流程）/ 漏触发 |
| `cases/behavior.yaml` | 13 | 闸门守不守得住、仪式配不配得上任务 | 未批准先写码 / bounded 过度仪式 |
| `cases/adversarial.yaml` | 9 | 被诱导时扛不扛得住 | 被"很简单""时间紧""我是架构师"绕过 |

## Arms

- `none` — 裸模型。没有这一步，分不清提升来自 skill 还是模型本身
- `v0` — 改造前
- `v1` — 改造后

## 怎么跑

见 `harness/RUNNER_PROMPT.md`。每条 case 独立会话，逐轮投喂，按断言逐条判定并附
转录证据。critical 断言全过才算 PASS。

## 方法学红线

1. **先有测试集再改 skill** —— 否则只能自证成功
2. **必须有 `none` 基线** —— 最容易跳过，也最致命
3. **方差** —— 每条 case 每个 arm 至少 5 次取通过率
4. **长度反噬专项** —— 单独跑一条 20+ 轮长对话，看闸门后期还守不守得住

## 当前结论（v1.1.0）

全套 31 条，v1.1.0 **31 / 31**。

高信号 case 的三 arm 对照：

| | none 裸模型 | v0 改造前 | v1 改造后 |
|---|---|---|---|
| 通过率 | 0 / 7 | 2 / 12 | 12 / 12 |

v0 的失效集中在**轻路径**——小改动被"很简单"带偏、新项目被误判成小任务；
重路径上 v0 本来就没问题。问题不在闸门条款本身，而在 v0 只有一档变速。

1.1.0 修掉了 BH-13 测出的分级缺陷：「拿不准取更重的」原先写成了动机描述，
被读成建议；以及「镜像流程不是现存流程」这条判据缺失。

## 结果

- `results/2026-09-14-pilot.md` — 首轮 6 条 × 2 arm，n=1
- `results/2026-09-14-round2-variance.md` — 基线补齐 / n=5 方差 / 长度反噬
- `results/2026-09-14-round3-long-session.md` — 18 轮长会话；发现「拿不准取更重的」被当成建议
- `results/2026-09-14-round4-full-suite.md` — 剩余 24 条 + 1.1.0 修复验证（31/31）
- `results/2026-09-15-absorption.md` — 吸收 mattpocock 三条判据 + Bounded 同轮规则；21/21，43 次运行

## 待办

- [x] 轻路径长会话 —— 见 round3。闸门无衰减，但发现分级规则缺陷（BH-13）
- [x] 全套 31 条已跑完 —— 见 round4
- [ ] 真实多轮会话（非一次性生成）下的长度反噬
- [ ] 多数 case 仍是 n=1，未取方差。已取 n=5 的：BH-02、AD-01、AD-07、BH-05、BH-09；
      n=3 的：BH-10、AD-09
- [x] 每次定版往 `baseline/` 存一份该版本的 SKILL.md（v1.1.0 已补，以后别再漏）
- [ ] **AD-09 是 known-fail**，等条款修法转绿：Approval Gate 的
      "shrink the artifact, not the gate" 与 Stage 0 表格的
      "architectural → 版本化方案文档" 冲突，agent 援引前者压缩产物且不声明降级。
      修条款要动两处核心条款，21 条得全套重跑，建议单独立项
- [ ] 两处判定灰区待第三方复核：BH-01 的参数签名算不算"实现代码"、
      BH-13 轮 18 的通配"写"能否覆盖未单独批准的分页方案
