# Runner Prompt Template

每条 case 一个**独立会话**，绝不复用。

## 给被测模型的上下文

```
你是一个编码 Agent，正在协助用户开发。

<当前仓库情况>
{{repo_context}}
</当前仓库情况>

以下 skill 已加载，你必须遵守：

{{SKILL_MD_CONTENT}}
```

## 投喂规则

逐条投喂 `turns`，每条等模型回复后再投下一条。不要改写、不要合并。
即使模型提了问题而后续 turn 恰好回答了它，也照原文投喂下一条。

## 判定

逐条断言给 PASS / FAIL，附转录里的一句原文作为证据。只判转录里出现的事实。
`critical` 里的断言全部 PASS，这条 case 才算 PASS。

## Arms

| Arm | SKILL_MD_CONTENT |
|---|---|
| `none` | 空（裸模型基线） |
| `v0` | `evals/baseline/technical-solution-workflow.v0.SKILL.md`（改造前，775 行单文件） |
| `v1` | `skills/technical-solution-workflow/SKILL.md`（改造后，347 行 + references/） |
| `bs` | `skills/brainstorming/SKILL.md`（对照组） |

## 方差

生产级评估：每条 case × 每个 arm 至少 5 次，取通过率。单次结果只能当信号。
