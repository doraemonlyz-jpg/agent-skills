# tt:sync — 需求变更：代码 + 文档联动

输入：`$ARGUMENTS`（必填）—— 变了什么。

用在：产品改需求、接口契约变化、交互规则调整。不用在：改变量名、加注释、格式化；impl 开始前的方案迭代直接重跑 tt:design / tt:plan，不要走 sync（会污染返工记录）。

## Step 1 — 定位需求目录

`$ARGUMENTS` 中有需求名就用它，否则取 `docs/features/active/` 下最近修改的目录。`eval-log.py start --stage sync`。

## Step 2 — 先评估再动手

列出这次变更影响的：文档章节、Plan 任务、契约文件、已写代码（文件:行；gopls `go_symbol_references` 帮助找全调用方）。🛑 输出影响清单，等用户确认范围。

## Step 3 — 改契约与代码

有契约文件（inputSlot taotao-contract 启用）时先改契约并重新生成代码，再改实现。靶向修改，清理本次产生的孤儿代码。Plan 中被废弃的任务标 `- [~]`，新增任务追加为新的 `### Task N` 并接续编号。

## Step 4 — 改文档

逐份检查 ARD / Design / Plan / Test，只改相关段落，每处追加 `> 变更记录：YYYY-MM-DD <摘要>`。失效用例标注「已失效：原因」，不直接删。

## Step 5 — 刷新知识索引

`docs/knowledge/manifest.yml` 存在时按 `commands/map.md` 跑 `--update`。

## Step 6 — 记录

1. progress.md 变更记录追加 `| YYYY-MM-DD | <摘要> |`。
2. 如果 progress.md 中 Code 已 ✅（编码后返工），问一次返工原因（单选）：需求变更 prd_change / 接口变更 api_change / CR 发现 cr_finding / 测试发现 test_finding / 主动调整 user_pivot，然后：
   ```bash
   python3 "$FLOW_ROOT/scripts/eval-log.py" rework --feature "$FEATURE" --cause <cause> \
     --reason "<$ARGUMENTS 前 100 字>" --files <改动文件,逗号分隔> --docs <ARD,Design,Plan,Test 中实际改过的>
   ```
3. `eval-log.py confirm --stage sync`。

## Step 7 — 润色

更新过的文档按 `taotao-humanize` 处理。
