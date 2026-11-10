# 测试证据协议（tt:impl 记录，tt:cr 核验）

目的：证明每个任务的测试**真的在实现之前失败过、失败原因正确，实现之后同一个测试通过**。全仓测试通过只说明现在没坏，说明不了测试有没有约束住这次改动，所以不能替代逐任务证据。

证据由 `scripts/tdd-evidence.py` 实际运行测试后写入 `docs/features/active/<需求名>/tdd-evidence.jsonl`。不手写、不改写这个文件——每条记录带前一条的哈希，改动会让 tt:cr 判定全部证据作废。

## 任务类型（写在 Plan 每个任务的 `**TDD:**` 行）

| 类型 | 适用 | 必需证据 |
|---|---|---|
| `bugfix` | 修缺陷 | 红灯（改动前复现缺陷）→ 绿灯（改动后同一测试通过） |
| `behavior` | 新增行为 | 红灯（改动前因功能不存在/不正确而失败）→ 绿灯 |
| `refactor` | 纯重构，不改变外部行为 | baseline（改动前一组行为测试通过）→ after（改动后同一组测试仍全部通过） |
| `none — <原因>` | 不涉及可测行为（文档、纯配置、migration 文件本身等） | 只需写明原因；能补验证的仍可用 verify 记录 |

## 记录命令

```bash
TE="python3 $FLOW_ROOT/scripts/tdd-evidence.py"

# bugfix / behavior：先写测试，不改实现，跑红灯
$TE red   --feature <需求名> --task <N> --cmd "go test ./internal/order/service -run '^TestCancelOrder$'" --expect '<预期失败原因正则>'
# 实现后跑绿灯（自动重跑红灯那条命令，不能换命令）
$TE green --feature <需求名> --task <N>

# refactor：改动前、改动后
$TE baseline --feature <需求名> --task <N> --cmd "go test ./internal/order/... -run '^TestCancel'"
$TE after    --feature <需求名> --task <N>

# 实现后补的入口 / 集成 / 并发测试：计入验证，自动标明「实现后执行」与时间
$TE verify --feature <需求名> --task <N> --cmd "go test ./api -run '^TestCancelHandler$' -race" --label 入口
```

## 什么算有效的红灯

脚本自动判定，以下情况一律**无效**：

- 测试在改动前就通过了（说明测试没约束住要改的行为，或实现已经先写了）；
- 环境故障：网络、模块下载、Docker、权限、超时、包路径不存在等；
- 命令没有用 `-run` 限定目标测试（无法排除无关失败）；
- 目标测试的失败输出和 `--expect` 不符（失败在别的断言、panic 或别的原因上）；
- 同一命令里还有别的测试因其他原因失败。

编译失败可以作为红灯（Go 里测试引用了尚不存在的函数，`undefined: CancelOrder`），前提是编译错误与 `--expect` 吻合。

`--expect` 要写**具体的失败信息**，例如 `CancelOrder\(.*\) err = <nil>, want ErrNotCancelable` 或 `undefined: CancelOrder`，不要写 `FAIL` 这类任何失败都能匹配的模式。

## 什么算有效的绿灯 / after

- 绿灯：重跑红灯同一条命令，退出码 0，目标测试实际执行并通过（不是被跳过），且代码相对红灯时确有变化；
- after：重跑 baseline 同一条命令，baseline 时通过的测试全部仍然通过，且代码确有变化。

## 核验

```bash
$TE check --feature <需求名>            # 人看的表格；--json 给 tt:cr 用；有未验证任务时退出码 1
```

每个任务的结论是「TDD 已验证」「不适用」或「TDD 未验证」。未验证时列出缺项：测试命令 / 预期失败原因 / 改动前失败结果 / 改动后通过结果，或具体的无效原因。实现后补的测试会列出来，并注明执行时间，但不能把任务变成「已验证」。
