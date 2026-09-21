# Response Templates

## Path Announcement (every path, first response)

```markdown
这个任务我判断是 **<Spike / Bounded / Architectural>**：<一句话理由>。
所以我会 <该路径的动作>，你可以直接推翻这个判断。
```

## Spike: Probe Proposal

```markdown
要验证的问题：<question>

我打算这样验证：<2-3 句探针方案>

产出是结论不是代码，写出来的东西都算一次性。确认我就开始。
```

## Bounded: Clarify then Short Design

```markdown
我读了 <file/flow>。开工前确认几点：

1. <question>
2. <question>
3. <question>

推荐默认值：<defaults>。
```

```markdown
## 简要方案

- 做法：<approach>
- 改动文件：<files>
- 测试：<testing>

确认后我开始实现。在你明确说可以之前我不动代码。
```

## Architectural: Initial Clarification

```markdown
我理解你的目标是：<goal>。

在确定技术架构前，需要先确认几项会直接影响方案的内容：

1. <question>
2. <question>
3. <question>

我的推荐默认值是：<defaults>。
```

## Requirement Summary

```markdown
## 已确认需求

- ...

## 后续优化

- ...

## 尚待确认

- ...
```

## Architecture Recommendation

```markdown
基于已确认需求，我建议采用：

> <architecture summary>

主要原因：
- ...
```

## Approval Request

```markdown
当前技术方案已经完成评审。

请明确回复：

> 按当前技术方案开始编码

收到明确确认后，我会先输出实施计划，再进入代码实现。
```

## Ambiguous Approval — Ask Again

```markdown
我还不能把这个当作批准。请明确回复"按当前方案开始编码"，我再进入实现阶段。
```

## Path Upgrade Mid-Task

```markdown
这个任务比一开始判断的重：<发现的隐藏复杂度>。

我把它从 <old path> 升级到 <new path>，先回到 <对应阶段>，不继续往下写。
```

## Architecture Change During Coding

```markdown
这个新需求会影响已确认的 <module/architecture>。

需要先更新技术方案中的：
- ...

我会先生成修订版方案，确认后再继续编码。
```

## Review Finding That Expands Scope

```markdown
这个finding是真实风险，但它的完整修法会把当前项目扩展为
<new subsystem / protocol / platform capability>，它还不是已确认范围。

- 最小缓解：<approach and residual risk>
- 完整修法：<approach and delivery/operating cost>
- 需要的证明等级：<operational / strong / audit-grade>
- 我的推荐：<choice and why>

请确认是接受最小缓解的残余风险，还是明确扩大范围实现完整修法。
在你选择前，我不会把完整修法默默写进方案。
```

## Pressure to Skip the Gate — Spike / Bounded

```markdown
我理解时间紧。闸门本身不会因为任务简单或时间紧而取消 —— 但产物可以压到这条路径
的最小形态：我用两句话说清做法，你点头，我立刻开始。

<两句话的做法>

可以吗？
```

## Pressure to Skip the Gate — Architectural

架构任务的产物下限是版本化方案文档。可以砍掉铺陈、只留编号章节，但换成对话里的
几句话就不是压缩而是降级——那要当着用户的面说出来，并把代价一起报出来。

```markdown
我理解时间紧。这件事我判成 architectural，它该出的是版本化方案文档；压成对话里
的几句话等于降一级，不是压缩，所以我先把这件事摆出来。

两个选择：

1. 我出一份精简版方案文档，只留结论、接口和风险，<N> 分钟，你确认后开工；
2. 你现在拍板降成 bounded —— 代价是 <哪些架构决策不会被记录>，
   返工的账记在这里。

你选哪个？
```
