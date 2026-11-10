# tt:map — Go 项目知识索引

两层：`go list` 生成的静态索引落盘（零 token、可审阅、给新会话做路由）；gopls MCP 负责实时语义查询（定义、引用、调用层级），不落盘。替代 soda 依赖的 code-map AST 管道。

```
tt:map            # 全量：首次，或大重构后
tt:map --update   # 增量：base_commit 以来有变更时（tt:sync / tt:archive 自动调用）
```

## Step 1 — 预检

- `go version` 可用；`go list ./...` 能跑通。失败时展示错误、建议 `go mod download`，不要擅自改 go.mod。
- 检查 gopls MCP 是否可用（会话里有 `go_workspace` 等工具）。可用就先调一次 `go_workspace` 确认模块布局；不可用就提示 `setup/install-taotao.sh --setup-mcp`，本命令照常继续。

## Step 2 — 提取结构

```bash
python3 "$FLOW_ROOT/scripts/go-map.py" "$PROJECT_ROOT" [--update]
```

| 文件 | 内容 |
|---|---|
| `packages.yaml` | 每个包：路径、目录、文件数、内部依赖、反向依赖、doc；`hubs` 段为被依赖最多的前 10 个包 |
| `api.yaml` | HTTP/RPC 路由注册候选（gin/echo/hertz/chi/net/http/grpc/kitex 常见写法），带 `file:line`，需读码确认 |
| `manifest.yml` | `base_commit`、生成时间、Go 版本、统计 |

## Step 3 — 校正路由候选

对 `api.yaml` 中的候选：gopls MCP 可用时，用 `go_search` 找到 handler 定义、`go_symbol_references` 确认注册点，把误报标 `# 误报` 注释、漏掉的补上（例如通过变量间接注册的路由）。没有 gopls 就保持"候选"标注。

## Step 4 — 刷新路由器 index.md

更新 `docs/knowledge/index.md`：

- **模块 ↔ 包**：按目录前缀归模块，每个一句话职责。职责来自包注释或入口文件；读不出来写"待补充"，不要编。
- **核心枢纽**：hubs 前 10 及被依赖次数。
- **服务概览**：只写代码里能确认的；上下游、数据归属不确定写"待补充"。

index.md 保持薄：只放路由和概览。

## Step 5 — 全局资产

- `tech.yaml`：首次或 go.mod 有新 require 时刷新直接依赖（`dependencies.core`，标注用途），间接依赖不登记。
- `terms.yaml`：**已有任何术语就不动**。仍是空模板（`terms: []`）时，从包名/路由/核心结构体生成初稿，每条标 `draft: true`，提醒用户审。

## Step 6 — 摘要

```
✅ 知识索引已更新
- 包 N / 内部依赖边 M / 枢纽 <top3>
- 路由 K 条（已用 gopls 校正 / 未校正）
- base_commit <sha> · tech.yaml 刷新/未动 · terms.yaml 保留/初稿
- gopls MCP：可用 / 未配置（setup/install-taotao.sh --setup-mcp）
```
