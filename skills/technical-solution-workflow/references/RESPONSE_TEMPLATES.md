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

## Pressure to Skip the Gate

```markdown
我理解时间紧。闸门本身不会因为任务简单或时间紧而取消 —— 但产物可以压到最小：
我用两句话说清做法，你点头，我立刻开始。

<两句话的做法>

可以吗？
```
