# 阶段通用步骤

文档类命令（ard / design / plan / test）和 impl 都按下面的骨架执行。命令文件里写「通用 A」「通用 B」等时，回到这里照做。

## 通用 A — 开场

1. 读 `workflow.config.yaml`（不存在就用 `$FLOW_ROOT/project-types.yaml` 的默认值），得到 `$PROJECT_TYPE` 和本阶段的 `input`、`output`、`inputSlot`。
2. 确定需求名 `$FEATURE`（`$ARGUMENTS` 中指定的，或 `docs/features/active/` 下最近修改的目录；tt:ard 首次落盘前和用户确认）。
3. 记录开始时间（输出不展示给用户）：
   ```bash
   python3 "$FLOW_ROOT/scripts/eval-log.py" start --feature "$FEATURE" --stage <阶段>
   ```
   tt:ard 在需求名确定之前先记下当前时间，确定后再补调 start。

## 通用 B — 执行 input skill

对 `commands.<阶段>.input` 中的每一项按顺序：

- 名字是 `taotao-*` 或其他本地 skill → Read `$SKILLS_DIR/<name>/SKILL.md`；
- 形如 `samber:x` / `superpowers:x` / `tob:p/s` → 按 SKILL.md「路径约定」解析到 `$VENDOR` 下；
- 找不到 → 提示一次「未找到 <name>，跳过」，不阻断。

需要和用户交互的 skill（如 taotao-clarify）：执行完输出产物摘要，🛑 等确认后再执行下一个。只提供知识的 skill（如 samber 规范）：读完即可，不需要确认。

## 通用 C — 跨阶段切片 inputSlot

对 `inputSlot` 中每个 skill S：若 `$SKILLS_DIR/S/<阶段>.md` 存在 → Read 并按它执行（它会先读上一阶段产物判断自己要不要参与，并可能有自己的确认点）；不存在 → 本阶段跳过 S。

切片的产出暂存在上下文，由主流程落盘时并入文档：ARD/Design 作为独立章节（标题注明来源，如 `## 接口契约（taotao-contract）`），Plan 作为任务并入统一编号。切片自己不写顶层文档。

## 通用 D — 记录人工介入

本阶段中，AI 提问且用户给出实质回答（不是"确认/OK/继续"）时，记一条：

```bash
python3 "$FLOW_ROOT/scripts/eval-log.py" note --feature "$FEATURE" --stage <阶段> \
  --type <adjust|supplement|correct|clarify> --q "<问题>" --a "<用户回答摘要>" --action "<AI 随后做了什么>"
```

## 通用 E — 润色、确认、落盘

1. 按 `taotao-humanize` 处理全文。
2. 🛑 输出完整文档，等用户确认；有修改意见就改完再输出一遍。确认前不写任何文件。
3. 写入 `docs/features/active/$FEATURE/<文档名>`，输出「已落盘 → <路径>」。
4. Claude Code 下，写入 ARD/Design 会由 hook 自动提醒执行对应门禁钩子；其他环境由命令文件显式 Read 钩子。
5. 更新 `progress.md`：本阶段 ✅（填今天），下一阶段 🔄。
6. 记录确认：
   ```bash
   python3 "$FLOW_ROOT/scripts/eval-log.py" confirm --feature "$FEATURE" --stage <阶段> \
     --skills <本阶段实际使用的 skill，逗号分隔> --rounds <对话轮次-1>
   ```
