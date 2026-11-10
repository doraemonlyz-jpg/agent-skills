# tt:mock — 接口与下游 mock

输入：`$ARGUMENTS` —— 接口名 / 契约文件路径 / 下游服务名 / 为空则交互收集。

## Step 0 — 加载

通用 B：默认 `[taotao-mock]`，按它判断属于哪种场景并选工具。

## Step 1 — 收集信息

`$ARGUMENTS` 为空时逐个问（一次一个）：

1. 要 mock 什么：Go 接口（单测替身）/ 下游 HTTP 服务 / 下游 RPC 服务 / 给调用方用的本服务接口；
2. 契约来源：已有 OpenAPI / proto / thrift 文件，还是 Design 里的接口定义；
3. 需要覆盖的场景：正常、空数据、业务错误码、超时、5xx。

## Step 2 — 生成

按 taotao-mock 的选型生成，并确保：

- 响应结构与契约/真实接口一致（有契约就从契约生成，不手写字段）；
- 覆盖正常 / 空 / 错误 / 超时；
- mock 与业务代码隔离：单测替身放 `_test.go` 或 `internal/mocks/`，mock 服务的启动方式写进 Makefile 或 README，不进入生产构建。

## Step 3 — 验证与说明

生成后跑一遍使用它的测试或启动 mock 服务 curl 一次，附结果。输出 mock 文件位置、启动/使用方式、覆盖的场景清单。
