# taotao-contract · CR 切片

## 自门控

本次 diff 不含契约文件（`*.proto`、`*.thrift`、`openapi*.yaml`、swagger 产物）且不含生成目录 → 跳过。

## 检查

1. **破坏性变更**：`buf breaking --against '.git#branch=<主干>'` / `oasdiff breaking <主干版本> <当前版本>`。未在 Design 声明兼容方案的破坏性变更 → BLOCKER。
2. **生成物一致**：重新生成后 `git diff --exit-code <生成目录>`；不一致 → BLOCKER（手改了生成代码或忘了重新生成）。
3. **实现一致**：契约新增的错误响应在实现里是否都有对应返回路径；实现里返回了契约未声明的状态码 → WARN。

## 产出

问题以 `{level, file, line, dim: "契约", desc, source: "tool"}` 交回 taotao-review / tt:cr 合并进报告。
