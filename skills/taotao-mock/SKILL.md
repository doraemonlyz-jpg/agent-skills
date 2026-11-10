---
name: taotao-mock
description: 为 Go 后端生成测试替身与 mock 服务：单测里的接口替身（手写 fake / mockery / gomock）、下游 HTTP 依赖的 httptest 假服务、按 OpenAPI 契约起的 Prism mock 服务、RPC 下游的接口级 fake，并覆盖正常/空/错误码/超时场景。被 taotao-flow 的 tt:mock 与 taotao-contract 调用；用户说"帮我 mock 一下这个接口""下游还没好怎么联调""生成 mock""给这个 interface 做个假实现"时也应使用。替代 soda 依赖的 mock-api。
metadata:
  version: 1.0.0
  short-description: Go mock 工具箱
---

# taotao-mock — Go mock 工具箱

## Step 1 — 判断场景

| 场景 | 推荐 | 原因 |
|---|---|---|
| 单测里替换自己定义的小接口（repo、client） | **手写 fake**（结构体 + 可配置返回值） | 可读、不依赖生成工具、重构时编译器帮你找出要改的地方 |
| 需要断言调用次数/参数顺序，或接口方法多 | **mockery**（项目已用）或 **go.uber.org/mock** 的 mockgen | 按 `docs/rules/tech-selection.md` 中登记的那个；都没登记就问用户选一个并登记 |
| 被测代码直接发 HTTP 请求给下游 | **httptest.NewServer** | 走真实 HTTP 栈，能测超时、状态码、畸形响应 |
| 下游/调用方需要一个可运行的假服务（联调、前端、压测前） | **Prism**：`prism mock api/openapi.yaml` | 从契约生成，字段与契约天然一致；`-d` 动态示例数据 |
| RPC（gRPC / Kitex）下游 | 对生成的 client 接口做 fake；gRPC 可用 `bufconn` 起进程内服务 | 不依赖网络，测试稳定 |
| SQL | 优先 testcontainers 起真库；纯逻辑分支用 sqlmock | mock SQL 字符串易与真实行为偏离 |
| Redis | miniredis | 进程内、行为接近真实 |

## Step 2 — 生成

**手写 fake**：

```go
type fakeNotifier struct {
	err   error
	calls []int64
}

func (f *fakeNotifier) NotifyCancelled(ctx context.Context, id int64) error {
	f.calls = append(f.calls, id)
	return f.err
}
```

**mockery**（`.mockery.yaml` 集中配置，生成到 `internal/mocks/` 或同包 `mock_*_test.go`）：

```bash
mockery --name=OrderStore --dir=internal/order/repo --output=internal/mocks --with-expecter
```

**gomock**：

```go
//go:generate mockgen -source=store.go -destination=mock_store_test.go -package=repo
```

**httptest**（覆盖四种场景）：

```go
srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	switch r.URL.Query().Get("id") {
	case "404": w.WriteHeader(http.StatusNotFound)
	case "slow": time.Sleep(2 * time.Second) // 配合客户端 1s 超时
	case "empty": w.Write([]byte(`{"data":[]}`))
	default: w.Write([]byte(`{"data":[{"id":1}]}`))
	}
}))
t.Cleanup(srv.Close)
```

**Prism**：

```bash
npx @stoplight/prism-cli mock api/openapi.yaml -p 4010          # 静态示例
npx @stoplight/prism-cli mock api/openapi.yaml -p 4010 -d       # 动态数据
# 强制某个响应码：curl -H 'Prefer: code=500' http://127.0.0.1:4010/api/v1/order/cancel
```

把启动命令写进 Makefile（如 `make mock-server`），不要只留在对话里。

## Step 3 — 约束

- 有契约文件就从契约生成，不手写字段；没有契约时字段以 Design 的接口定义为准；
- 至少覆盖：正常、空数据、业务错误码、超时/5xx；
- mock 代码与生产代码隔离：放 `_test.go`、`internal/mocks/`（只被测试 import），或用 build tag；mock 服务不进入生产构建与部署；
- 生成后跑一遍使用它的测试或 curl 一次 mock 服务，附结果。

## Step 4 — 输出

mock 文件位置、生成/启动命令、覆盖的场景清单、验证结果。
