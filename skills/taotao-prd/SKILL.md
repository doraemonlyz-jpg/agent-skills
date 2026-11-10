---
name: taotao-prd
description: 把需求原文从各种来源取回并规范化成一份可追溯的 PRD Markdown：Notion 页面（Notion MCP）、本地 md/txt/pdf/docx 文件、网页 URL、或直接粘贴的文字。被 taotao-flow 的 tt:ard 第一步调用；用户说"读一下这个 PRD""这个 Notion 需求文档帮我看看""把这份需求整理一下"时也应使用。替代 soda-ai-workflow 依赖的公司内部 cooper skill。
metadata:
  version: 1.0.0
  short-description: PRD 输入层：Notion / 文件 / URL / 粘贴
---

# taotao-prd — PRD 输入层

产出两样东西：`$PRD`（规范化 Markdown，交给 tt:ard 使用）和 `$PRD_SOURCE`（来源：链接 / 路径 / "粘贴"，tt:ard 落盘时写进 `PRD-source.md`）。

## Step 1 — 识别来源

| 信号 | 来源 | 取回方式 |
|---|---|---|
| `notion.so` / `notion.site` 链接，或"Notion 上的 XX 需求" | Notion | Notion MCP：有链接用 fetch 工具直接取页面；只有标题用 search 工具找，找到多个就列出来让用户选。页面里的子页面/数据库只在用户需要时再展开 |
| 本地路径，`.md` / `.txt` | 文件 | 直接 Read |
| `.pdf` | 文件 | 有 `pdftotext` 用 `pdftotext -layout <f> -`；否则 Read（宿主支持 PDF 时）；扫描件提示用户提供文字版 |
| `.docx` | 文件 | 有 `pandoc` 用 `pandoc -t gfm <f>`；否则用 python-docx 或 `unzip -p <f> word/document.xml` 粗提取，并提示格式可能丢失 |
| `http(s)://` 其他链接 | 网页 | WebFetch；需要登录的内网页面取不到时，请用户导出或粘贴 |
| 其他 ≥ 3 行文字 | 粘贴 | 原样使用 |

Notion MCP 不可用时：提示 Claude Code 用 `claude mcp add --transport http notion https://mcp.notion.com/mcp`（或 agent-skills 仓库的 `setup/install-taotao.sh --setup-mcp`）接入并完成授权；当下请用户把页面导出为 Markdown 或直接粘贴，不中断流程。

文件路径在用户电脑上而当前会话访问不到时，请用户把文件附进对话。

## Step 2 — 规范化

把原文整理成下面的结构，**只重排和标注，不改写需求含义，不补充原文没有的内容**：

```markdown
# <需求标题>
> 来源：<链接 / 路径 / 粘贴> · 获取时间：YYYY-MM-DD HH:mm

## 背景与目标
## 功能描述        （原文的功能点，保留原有编号）
## 业务规则        （状态、数值、校验、权限）
## 接口 / 数据     （原文出现的字段、接口、表）
## 非功能要求      （性能、安全、灰度）
## 原文未覆盖 / 存疑   （读的过程中发现的空白和矛盾，逐条列出）
```

原文中的图片、原型链接：保留链接并标注"[图：…]"，看不到内容的注明"未读取"。

## Step 3 — 交回

向 tt:ard 交回 `$PRD`、`$PRD_SOURCE`，以及「原文未覆盖 / 存疑」清单——它是 taotao-clarify 提问的起点。单独使用时，把规范化结果展示给用户即可，不写文件。
