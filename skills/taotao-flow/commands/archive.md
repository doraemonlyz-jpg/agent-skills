# tt:archive — 需求归档

输入：`$ARGUMENTS`（必填）—— 需求名。只归档这一个。前提：代码已合入主干。

## Step 1 — 前置检查

`docs/features/active/<需求名>/` 下至少有 ARD 和 Plan；缺失就停下。Plan 中还有 `- [ ]` 时 ⚠️ 列出，用户确认后继续。`eval-log.py start --stage archive`。

## Step 2 — 分析本次改动

```bash
git diff <主干>...<需求分支或合并 commit> --name-only    # 已合入时向用户确认比较范围
```

标记 `api_changed`（handler/router/契约文件）、`db_changed`（migration/*.sql/model）、`dep_changed`（go.mod 新 require）。

## Step 3 — 移动目录

progress.md：变更记录追加 `| 今天 | 归档至 completed/YYYY-MM/ |`；`git mv docs/features/active/<需求名> docs/features/completed/YYYY-MM/<需求名>`。

## Step 4 — 刷新知识（必做）

1. 按 `commands/map.md` 跑 `--update`；
2. tech.yaml 对账（无条件）：go.mod 有、tech.yaml 无 → 补登；版本不一致 → 以 go.mod 为准；tech.yaml 有、go.mod 无 → 列为「疑似已移除」，等人确认，不擅自删；
3. `api_changed` 时更新 index.md 服务概览中的接口说明。

## Step 5 — 经验沉淀

按 `commands/exp.md` 的门槛判断；有就写，没有输出 `⏭ 本次无新经验`。

## Step 6 — 归档自评（可跳过）

```
📊 归档自评（直接回车跳过）
- 如果不用 AI，自己做大概要几小时？
- AI 生成代码占比（0~1，主观估计）？
- 备注？
```

```bash
python3 "$FLOW_ROOT/scripts/eval-log.py" assess --feature <需求名> [--manual-hours H] [--ai-ratio R] [--notes "…"]
python3 "$FLOW_ROOT/scripts/eval-log.py" confirm --feature <需求名> --stage archive
```

AI 用时由各阶段 started_at/confirmed_at 自动计算，不用问。数据只留在本仓库。

## Step 7 — 报告

```
✅ 已归档「<需求名>」→ docs/features/completed/YYYY-MM/<需求名>/
- 接口变更 … / 数据变更 … / 新依赖 …
- 知识索引已增量刷新（base_commit <sha>）
- tech.yaml 对账：补登 N / 纠正 M / 疑似移除 K（待确认）
- 经验：<路径> / 无
建议：tt:eval 看本需求的效率报告
```
