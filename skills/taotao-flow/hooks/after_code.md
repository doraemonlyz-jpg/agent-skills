# after_code — 代码后置扫描（Go）

**档位**：安全红线 = 硬阻断；清洁问题 = 软警告。只做快速拦截，完整审查走 `tt:cr`。先查项目覆盖版本 `docs/hooks/after_code.md`。

## Step 1 — 工具扫描（必须实际运行）

```bash
bash "$FLOW_ROOT/scripts/go-check.sh" "$PROJECT_ROOT"
```

脚本对本次改动的 Go 包依次跑 gofmt、build、vet、golangci-lint（`--new-from-rev`）、gosec、govulncheck、`go test -race`，退出码 0 / 1 / 2 分别表示通过 / 硬失败 / 软问题或有工具被跳过，结果写入 `.taotao/last-check.json`（提交门禁读取）。把输出原样贴给用户。

| 结果 | 处理 |
|---|---|
| `build` / `vet` = fail | 硬阻断，修复后重跑 |
| `gosec` = fail_high（`-severity high -confidence medium` 有命中） | 硬阻断 |
| `govulncheck` = fail_high（退出码 3：本次代码实际调用到的漏洞） | 硬阻断：升级依赖或说明不可达的理由 |
| `gofmt` = fail | 直接 `gofmt -w` 修掉并告知 |
| `golangci-lint` / `gosec` / `test` = fail | 判断是否本次引入：是 → 修；不是 → 软警告说明 |
| 任一安全工具 = skipped / error | 软警告：在报告中写明「未执行」及原因（未安装、漏洞库不可达），不能当作通过 |

lint 配置与告警解读参考 `samber:golang-lint`，gosec / govulncheck 结果解读参考 `samber:golang-security`。golangci 配置里已启用 gosec linter 时，脚本只单独跑一遍高危判定，避免重复。

## Step 2 — 安全红线 [硬阻断]

在本次新增/修改的代码中检查：

| 红线 | 特征 |
|---|---|
| 硬编码凭证 | 变量名含 token/secret/password/ak/sk/key，值是非占位字符串 |
| SQL 拼接 | `fmt.Sprintf` / `+` 拼接后传给 `Query`/`Exec`/`Raw`，没用占位符 |
| 命令注入 | `exec.Command("sh","-c", <含用户输入>)` |
| 吞错误 | `_ = xxx()` 返回 error 却丢弃，或 `if err != nil {}` 空处理，且无注释说明 |
| 无超时的外部调用 | `http.Get`/`http.DefaultClient`、`context.Background()` 直接打下游 |
| goroutine 泄漏风险 | `go func()` 无退出条件 / 无 ctx.Done() / 无 WaitGroup |
| 越过鉴权 | 注释掉的鉴权中间件、`// TODO auth` |

命中 → 输出位置和修复建议，修复后重新扫描。

## Step 3 — 清洁快扫 [软警告]

只看能客观判定的：本次新增但未使用的函数/变量（go vet 和编译器之外的，如未导出且无引用的函数）、调试残留（`fmt.Println`、`log.Printf("debug`、`spew.Dump`）、注释掉的大段代码、遗留 `TODO` 没写负责人。

一句话带过：`⚠️ 2 处清洁问题：order.go:88 fmt.Println；svc.go:120 注释代码块`

## 输出

```
✅ 代码后置扫描（backend-go）
- 工具: gofmt ✓ vet ✓ build ✓ lint ✓/跳过 test ✓（-race）
- 安全红线: 0
- 清洁问题: 0 / N（软警告）
完整审查：tt:cr --full
```
