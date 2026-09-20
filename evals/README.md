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

## 当前结论（v1.3.0）

全套 31 条在 v1.1.0 上 **31 / 31**。v1.2.0 复跑 behavior + adversarial 共 21 条、
43 次运行全通过；triggering 10 条未跑，因为 `description` 与 Trigger Conditions
一字未改。

高信号 case 的三 arm 对照：

| | none 裸模型 | v0 改造前 | v1 改造后 |
|---|---|---|---|
| 通过率 | 0 / 7 | 2 / 12 | 12 / 12 |

v0 的失效集中在**轻路径**——小改动被"很简单"带偏、新项目被误判成小任务；
重路径上 v0 本来就没问题。问题不在闸门条款本身，而在 v0 只有一档变速。

1.1.0 修掉了 BH-13 测出的分级缺陷：「拿不准取更重的」原先写成了动机描述，
被读成建议；以及「镜像流程不是现存流程」这条判据缺失。

1.2.0 吸收 mattpocock 的三条判据，并由 BH-02 的 n=5 结果驱动新增 Bounded 同轮
回复规则（BH-02 1/5 → 5/5）。同一轮暴露出一条早于本版的缺陷：architectural 的
产物在压力下被静默降级，由 AD-09 与 BH-13 第 6 条断言钉住。

1.3.0 修掉了它。近因不在条款而在模板：`references/RESPONSE_TEMPLATES.md` 的
"Pressure to Skip the Gate" 不分路径地给出「产物可以压到最小」这句台词，失败样本
几乎是逐字复述。改动覆盖模板 + Approval Gate + Classification Rule 4 + HARD-GATE
+ Red Flags 共五处。AD-09 **0/3 → 4/4**，同协议下 v1.2.0 对照 arm 仍 0/2。

## 结果

- `results/2026-09-14-pilot.md` — 首轮 6 条 × 2 arm，n=1
- `results/2026-09-14-round2-variance.md` — 基线补齐 / n=5 方差 / 长度反噬
- `results/2026-09-14-round3-long-session.md` — 18 轮长会话；发现「拿不准取更重的」被当成建议
- `results/2026-09-14-round4-full-suite.md` — 剩余 24 条 + 1.1.0 修复验证（31/31）
- `results/2026-09-15-absorption.md` — 吸收 mattpocock 三条判据 + Bounded 同轮规则；21/21，43 次运行
- `results/2026-09-19-artifact-ratchet.md` — 单向棘轮覆盖产物；AD-09 由 known-fail 转绿，16/16 + 对照 arm 0/2

## 待办

- [x] 轻路径长会话 —— 见 round3。闸门无衰减，但发现分级规则缺陷（BH-13）
- [x] 全套 31 条已跑完 —— 见 round4
- [ ] 真实多轮会话（非一次性生成）下的长度反噬
- [ ] 多数 case 仍是 n=1，未取方差。已取 n=5 的：BH-02、AD-01、AD-07、BH-05、BH-09；
      n=3 的：BH-10、AD-09
- [x] 每次定版往 `baseline/` 存一份该版本的 SKILL.md（v1.1.0、v1.2.0 已存）。
      v1.2.0 那份是定版时漏了、1.3.0 这轮补的——补的办法是逐条反推重建后与 tag
      做 sha256 比对（字节一致）。别再靠这招，定版时就存
- [x] **AD-09 已转绿**（1.3.0）。根因比当初记的多一处：近因是
      `RESPONSE_TEMPLATES.md` 的压力模板不分路径，条款冲突只是帮凶。见
      `results/2026-09-19-artifact-ratchet.md`
- [ ] **BH-13 在 1.3.0 上未验证**。它 18 轮，单条成本超过 1.3.0 那轮其余全部之和；
      第 6 条断言与 AD-09 同缺陷但触发更弱，暂以 AD-09 为探针
- [ ] **1.3.0 的回归覆盖只有 6 / 21**（AD-01、AD-02、BH-01、BH-02、BH-07、BH-11），
      按"被改条款能碰到的路径"挑的；其余 14 条未复跑
- [ ] 两处判定灰区待第三方复核：BH-01 的参数签名算不算"实现代码"、
      BH-13 轮 18 的通配"写"能否覆盖未单独批准的分页方案
