# tt:ard — 需求分析文档（ARD）

输入：`$ARGUMENTS` —— Notion 链接 / 本地文件路径 / 网页 URL / 需求描述 / 为空。

ARD 回答"要做什么、边界在哪、会动到哪里"，不回答"怎么实现"。它是后面所有阶段的强约束输入，所以宁可多问一句，也不要带着猜测落盘。

## Step 0 — 开场

按 `_stage-common.md` 通用 A。需求名此时还没定，先记下开始时间。

## Step 1 — PRD 输入（taotao-prd）

Read `$SKILLS_DIR/taotao-prd/SKILL.md` 并按它识别来源、取回内容，得到 `$PRD`（规范化后的 Markdown + 来源链接）。

**输入为空或只有一句话** → 🚫 硬阻断，输出下面这段后停止：

```
🚫 tt:ard 需要以下之一才能继续：
A. Notion 页面链接
B. PRD 文件路径（md / pdf / docx）或网页 URL
C. 需求描述（≥ 3 行：背景 / 要做的功能 / 已知约束）
补充后重新执行 tt:ard。
```

不要执行后续任何步骤，也不要替用户脑补需求——基于想象写出的 ARD 会把错误一路传到代码里。可以补一句提示：如果仓库里已有相关代码，说明是新做还是改现有逻辑。

## Step 2 — 就绪清单（软约束）

```
📋 输入就绪检查（✅ 就绪 / ❌ 缺失 / 🚫 不涉及）
1. 需求载体          → 已提供（<来源>）
2. 接口协议（字段、IDL/proto/OpenAPI）
3. 技术硬约束（框架、存储、禁用项）
4. 代码模块上下文（涉及哪些服务/目录）
5. 数据变更（表 / 缓存 / MQ topic）
6. 依赖方与联调排期
7. 性能/容量（QPS、P99、数据量级）
8. 历史需求基线（同模块旧方案）
回复如「2 ❌ 5 ❌，其余 ✅」；直接回车视为全部就绪。
```

缺失项写入 ARD「输入就绪摘要」并标为风险；关键项（接口协议、数据变更）缺失时，在 Step 4 澄清环节追问。

## Step 3 — 影响域扫描

查询优先级（有结果就停，不跳级）：

1. **知识索引 + gopls**：`docs/knowledge/manifest.yml` 存在时先查新鲜度：`git diff <base_commit>..HEAD --name-only | wc -l` > 20 就提示"索引落后 N 个文件，建议 tt:map --update"，用户回复「继续」或「刷新」。然后 `index.md` 定位模块 → `packages.yaml` 看依赖/反向依赖 → `api.yaml` 看现有路由；需要精确到符号时用 gopls MCP 的 `go_search` / `go_symbol_references`。
2. **没有索引** → ⚠️ 建议先 tt:map；用户回复「跳过」就改用 gopls MCP（有的话）或指定目录 grep，报告中标注来源。禁止全仓库盲扫。

```
📊 影响域
- 改动入口: <包/文件:行>（说明）
- 传播链: <被谁调用>
- 高风险节点: <hub 包 / 共享状态 / 核心交易链路>（被 N 处引用）
- 来源: 知识索引 / gopls / grep 兜底
```

高风险：被 3 处以上引用、属于 hubs、涉及共享状态（全局变量、缓存 key、DB 表）、或在资金/订单等核心链路。

## Step 4 — input skill 与切片

1. 通用 B：默认 `[taotao-clarify]`，从就绪清单缺失项和 PRD 模糊点开始，一次一个问题，最后给方案对比。每轮实质问答按通用 D 记录。
2. `docs/knowledge/experiences/` 中与本需求关键词相关的经验文件读进来，在 ARD「历史经验」引用。
3. 通用 C：执行 inputSlot 的 `ard.md`（默认 taotao-contract：盘点要新增/变更的接口与契约归属）。

## Step 5 — 填模板

模板：`commands.ard.output` 非空用它，否则 `templates/ARD.md`。严格按章节填，不删章节；没内容写「待补充」或「不涉及」，不留空。切片产出作为独立章节并入。

## Step 6 — 润色、确认、落盘

按通用 E 执行，另外：

- 首次落盘前确认需求名（英文 kebab-case），然后补调 `eval-log.py start`（如 Step 0 未能调用）；
- `progress.md` 不存在就用 `templates/progress.md` 创建；
- 同目录写 `PRD-source.md`：来源链接/路径 + 规范化后的 PRD 正文（Notion/URL 的内容快照，便于日后追溯需求为何这样写）；
- 落盘后执行 `hooks/after_ard.md`（Claude Code 下 hook 会提醒）。

输出：`✅ ARD 已保存：<路径>。确认无误后执行 tt:design`
