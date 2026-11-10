# tt:exp — 沉淀一条经验

输入：`$ARGUMENTS` —— 需求名 / 话题关键词 / 为空。

经验库的价值在于"下次遇到同类情况能直接照做"。所以只收非显然的东西：隐性前提、使用陷阱、走过弯路后才知道的正确决策。平凡操作不写。

## Step 1 — 找素材

| 输入 | 素材 |
|---|---|
| 匹配到 `docs/features/active/` 或 `completed/` 下的需求 | 读它的 ARD + 相关 diff |
| 话题关键词 | 从当前对话里提炼这个话题的非显然知识点 |
| 为空 + 有新提交 | `git diff HEAD~1...HEAD` |
| 为空 + 无提交 | 扫描对话里的决策转折点；只有平凡问答就输出 `⏭ 无可沉淀内容` 并结束 |

## Step 2 — 查重

`ls docs/knowledge/experiences/`，有主题高度重叠的：读旧文件，在「验证记录」追加一行，`validated_count + 1`，≥ 2 时 `status` 改为 `confirmed`。输出 `🔄 已更新：<文件>` 并结束。

## Step 3 — 门槛（全过才写）

- [ ] 有具体来源（能说出是哪次任务/哪段对话）
- [ ] 可复用（同类场景会再遇到，不是偶发）
- [ ] 结论可操作（写"下次这样做"，不是"注意 xxx"）

任一不过：输出 `⏭ 门槛未过：<原因>` 并结束。

## Step 4 — 写入

路径 `docs/knowledge/experiences/YYYY-MM-DD-<主题>.md`，按 `templates/experience.md` 填。写完 Read 一遍「结论」段确认没截断。

## Step 5 — 自检 + 输出

按 `taotao-humanize` 处理，每条结论 ≤ 20 字。

```
✅ 经验已沉淀：<路径>
标签：[…]  结论：1. … 2. …  状态：candidate
```
