# tt:eval — 本地效率评测报告

输入：`$ARGUMENTS` —— 需求名（只看一个）/ 为空（全部需求）/ `--no-tokens`。

回答"AI 在这个需求上到底帮了多少、卡在哪"：各阶段耗时、人工介入次数和类型、返工原因、CR 评分、Plan 完成度、token 消耗、归档自评。所有数据来自本仓库的 `eval-log.json` / `cr-status.json` 和本机会话记录，不上传。

## Step 1 — 生成

```bash
python3 "$FLOW_ROOT/scripts/eval-report.py" --root "$PROJECT_ROOT" [--feature <需求名>] [--no-tokens]
```

- token 统计：Claude Code 读 `~/.claude/projects/<项目>/*.jsonl`，Codex 读 `~/.codex/sessions/**/*.jsonl`，按需求的阶段时间窗累计。
- 装了 ccusage 时可补一份更细的费用视图：`ccusage session --since <需求开始日期>`（Claude Code）/ `ccusage codex session`，把结果附在报告后面。

## Step 2 — 解读

把脚本打印的 Markdown 表展示给用户，然后用 3–5 句话指出最值得关注的点，例如：

- 哪个阶段耗时最长、介入最多（通常说明模板或输入不够好）；
- 返工原因的分布（prd_change 多 → 需求输入阶段要加强；cr_finding 多 → impl 阶段规范没生效）；
- CR 评分和 BLOCKER 来源（自审 / 独立评审 / 工具）；
- 自评的人工预估 vs AI 用时。

报告文件路径：`docs/eval/<日期>-report.html`。
