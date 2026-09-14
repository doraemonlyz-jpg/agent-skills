# technical-solution-workflow Evals

评估 `technical-solution-workflow` 吸收 Spike/Bounded/Architectural 三分法与硬闸门
之后，相对改造前版本的行为变化。

## 测什么

| Suite | 条数 | 测什么 | 目标失效形态 |
|---|---|---|---|
| `cases/triggering.yaml` | 10 | 该不该触发、判成哪条路径 | 误触发（小改动被拉进重流程）/ 漏触发 |
| `cases/behavior.yaml` | 12 | 闸门守不守得住、仪式配不配得上任务 | 未批准先写码 / bounded 过度仪式 |
| `cases/adversarial.yaml` | 8 | 被诱导时扛不扛得住 | 被"很简单""时间紧""我是架构师"绕过 |

## Arms

- `none` — 裸模型。没有这一步，分不清提升来自 skill 还是模型本身
- `v0` — 改造前
- `v1` — 改造后
- `bs` — `brainstorming` 对照

## 怎么跑

见 `harness/RUNNER_PROMPT.md`。每条 case 独立会话，逐轮投喂，按断言逐条判定并附
转录证据。critical 断言全过才算 PASS。

## 方法学红线

1. **先有测试集再改 skill** —— 否则只能自证成功
2. **必须有 `none` 基线** —— 最容易跳过，也最致命
3. **方差** —— 每条 case 每个 arm 至少 5 次取通过率
4. **长度反噬专项** —— 单独跑一条 20+ 轮长对话，看闸门后期还守不守得住

## 结果

见 `results/`。
