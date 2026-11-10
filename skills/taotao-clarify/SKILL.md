---
name: taotao-clarify
description: 动手设计或编码前把需求问清楚：先看代码和已有材料，再一次只问一个问题、优先给选项，最后给 2–3 个方案对比并推荐。以 superpowers 的 brainstorming 方法为内核，结论交回 taotao-flow 写进 ARD。被 tt:ard 默认调用；用户说"帮我理一下这个需求""这个需求怎么做比较好""先别写代码想清楚再说"，或需求含糊、有多种理解时也应使用。需求已有验收标准和参照实现时不需要。
metadata:
  version: 2.0.0
  short-description: 需求澄清（brainstorming 适配层）
---

# taotao-clarify — 需求澄清（brainstorming 适配层）

回答"做什么、为什么"，不回答"怎么实现"。

## 内核：superpowers brainstorming

Read `${TAOTAO_VENDOR:-~/.taotao/vendor}/superpowers/skills/brainstorming/SKILL.md`，采用它的这些部分：

- 「What Do You Actually Know?」——先判断需求是否已经足够清楚，清楚就直说，不为走流程硬问；
- 「Look Before You Ask」——先读代码、PRD、已有文档，能自己查到的不问用户；
- 提问方法：一次一个问题、能给选项就给选项、先宽后窄、显式验证假设、早问成功标准；
- 「Lay out the approaches」——2–3 个方案，先给推荐和理由，诚实说明取舍，坚持 YAGNI。

**以下几处以 taotao-flow 为准，忽略 brainstorming 原文的对应要求**（它是为独立使用设计的，而这里只是 tt:ard 的一个环节）：

- 不写 `docs/superpowers/specs/` 设计文档，不提交 git；
- 不调用 writing-plans 或任何后续 skill，不进入实现；
- 不启动 visual companion / 浏览器；
- 结论按下方格式交回，由 tt:ard 写进 ARD 的「决策记录」。

vendor 缺失时，按上面列出的方法直接执行即可。

## Go 后端常需追问的点

挑相关的问，不要逐条念：

| 主题 | 例子 |
|---|---|
| 调用方 | 谁调？同步还是异步？QPS 多少？ |
| 一致性 | 失败回滚到什么程度？能接受最终一致吗？ |
| 并发 | 同一资源被并发操作时谁赢？ |
| 幂等 | 调用方会重试吗？用什么做幂等键？ |
| 数据 | 要新表/新字段吗？历史数据怎么处理？ |
| 依赖 | 下游挂了怎么办？ |
| 灰度 | 要开关或白名单吗？ |

被 tt:ard 调用时，从它给的「就绪清单缺失项」和 taotao-prd 的「原文未覆盖 / 存疑」清单开始问。

## 结论格式

```
✅ 澄清完成
- 要做：<1–2 句>
- 选定方案：<方案> —— <理由>
- 关键决策：<决策：原因>（逐条）
- 仍待定：<问题>（逐条，没有写"无"）
```

单独使用时，问用户是否进入 tt:ard。
