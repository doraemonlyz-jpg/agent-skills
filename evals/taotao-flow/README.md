# taotao-flow 行为评测

`cases/` 下每个目录是一个用例（`prompt.md` + `case.yaml` + `graders/`），格式与 `claude plugin eval` 兼容。

| 用例 | 测什么 |
|---|---|
| init-and-map-go-repo | tt:init + tt:map 产出骨架、配置、规则块、hooks、知识索引 |
| ard-blocks-on-thin-input | 输入只有一句话时 tt:ard 硬阻断、不臆造需求 |
| cr-full-finds-go-blockers | tt:cr --full 对预埋 Go 缺陷的检出与 cr-status.json |
| plan-superpowers-format | tt:plan 产出可被 superpowers task-brief 解析的计划 |

脚本级回归测试在 `skills/taotao-flow/tests/test_workflow.sh`。
