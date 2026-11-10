## taotao-flow 研发规则

本项目使用 taotao-flow 流水线（`tt:*` 命令）。以下规则对每次对话生效。

### 触发方式

只有显式命令 `tt:<name>`（或 `/tt:<name>`）进入流水线：init / map / ard / design / plan / test / impl / cr / fix / mock / sync / archive / exp / eval。收到命令时读取 taotao-flow skill 下的 `commands/<name>.md` 并严格执行。其他对话正常回答，不加载流程文件。

### 上下文

- 常驻：本规则块 + `docs/knowledge/index.md`（路由器）+ `docs/rules/`。
- 按需：`docs/knowledge/` 下的 yaml 和 experiences，从 index.md 路由进去读，不全量加载。

### 编码铁律

1. **规约优先**：`docs/rules/` 高于设计文档和任何建议；命中 `forbidden.md` 立即停下报告。
2. **先想清楚再动笔**：有多种理解时列出来让我选；有更简单的方案主动说；不确定就问。
3. **最小改动**：只改本次需求涉及的代码，不顺手重构；本次产生的孤儿 import/变量/函数一并清理；已有死代码只报告不删。
4. **错误不吞**：`if err != nil` 全覆盖，用 `%w` 包装上下文向上返回；日志只在处理错误的那一层打一次。
5. **外部调用有边界**：HTTP/RPC/DB/Redis/MQ 必须带 context 超时，失败有降级。
6. **并发安全**：goroutine 有明确退出条件；共享数据有保护；提交前跑 `go test -race`。
7. **需求变更先同步文档**：听到"改一下""接口变了""需求变了"，先走 `tt:sync`，再改代码。
8. **多步任务目标驱动**：先列 `1. 步骤 → 验证：检查点`，每步做完立即验证。
9. **推送前过门禁**：说"推送/push/合代码"时先过 CR 结论检查和敏感信息扫描（Claude Code 下由 hook 强制执行）。
10. **证据先于断言**：说"完成/通过/修好了"之前先跑验证命令并给出输出。
