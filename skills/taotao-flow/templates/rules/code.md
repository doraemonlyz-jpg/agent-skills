# 编码规范

> 项目团队维护。「（填写）」处请替换为实际约定；不适用的写「不适用」，保留标题。
> 冲突时以 golangci-lint 配置为准。

## 项目结构

- 目录布局：（填写，如 cmd/ internal/ pkg/ api/）
- 分层：handler → service → repo，禁止跨层调用（handler 不直接访问 repo）
- 包命名：小写单词，不用下划线，不用 util/common 这类无语义包名（已存在的除外）

## 命名

- 遵循 Effective Go；缩写全大写（`ID`、`URL`、`HTTP`）
- 接口按行为命名（`OrderStore`），实现放在使用方需要的地方
- 错误变量 `ErrXxx`，错误类型 `XxxError`

## 错误处理

- 统一错误包：（填写，如 internal/errs）
- 向上返回时 `fmt.Errorf("动作: %w", err)` 包装，不丢原始错误
- 错误码转换只在接口层做一次
- 日志只在最终处理错误的地方打一次，不要层层打

## context

- 所有对外 I/O 函数第一个参数是 `ctx context.Context`
- 不把 ctx 存进结构体；不传 nil ctx

## 日志与可观测

- 日志库：（填写，如 zap / 公司日志库）
- 必带字段：trace_id、（填写，业务主键）
- metrics / trace：（填写）

## 并发

- goroutine 必须有退出路径（ctx.Done / channel 关闭 / WaitGroup）
- 后台 goroutine 统一 recover 并上报

## 测试

- 表驱动测试；子测试名描述场景
- 单测不依赖外部网络；外部依赖用接口 + fake
- 覆盖率要求：（填写）

## 注释

- 导出符号写 godoc，说明用途、参数约束、错误语义
- 不写"这个函数做了什么"式的废话注释
