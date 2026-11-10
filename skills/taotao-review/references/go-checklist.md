# Go 审查检查表

按维度逐项过。每项后面括号是默认级别，实际按触发条件调整。

## R1 正确性

- 错误分支返回后，后续代码是否仍使用了无效值（BLOCKER）
- `if err != nil` 写成了 `if err == nil`，或判断后忘记 `return`（BLOCKER）
- 指针/接口/map/slice 的 nil 访问；类型断言没有用 `v, ok :=`（BLOCKER）
- 时间：时区、`time.Now()` 在测试中不可控、Duration 单位（秒 vs 毫秒）（WARN）
- 整数溢出、除零、金额用 float（BLOCKER）
- 状态机：转换前是否校验当前状态；更新语句是否带状态条件（`WHERE status = ?`）防并发越权（BLOCKER）
- `defer` 在循环里累积；`defer` 捕获的变量在执行时已变化（WARN）
- 切片 append 别名问题：多个切片共享底层数组被意外修改（WARN）

## R2 健壮性

- 错误被吞：`_ = f()`、空 `if err != nil {}`、只打日志不返回（BLOCKER，写操作）/（WARN，只读）
- 错误未用 `%w` 包装，上层无法 `errors.Is/As`（WARN）
- 同一错误层层打日志（NIT）
- 外部调用无超时：`http.DefaultClient`、`context.Background()`/`TODO()` 打下游（BLOCKER）
- ctx 没有从入口传到下游；在 goroutine 里使用已取消的请求 ctx 做后台任务（WARN）
- 重试非幂等操作（BLOCKER）；重试无退避无上限（WARN）
- `resp.Body`、`rows`、文件、`Tx` 未关闭或未回滚（BLOCKER）
- 依赖失败没有降级，导致整个接口失败（WARN）
- panic 风险：库代码中 `panic`、后台 goroutine 无 recover（WARN）

## R3 并发安全

- map 并发读写（BLOCKER）
- 共享变量无锁读写，`go test -race` 可复现（BLOCKER）
- goroutine 无退出条件：无 `ctx.Done()`、channel 永不关闭、无缓冲 channel 发送无人接收（BLOCKER）
- `sync.WaitGroup.Add` 在 goroutine 内调用（BLOCKER）
- 持锁调用外部 I/O / 持锁期间回调（WARN）；锁顺序不一致可能死锁（BLOCKER）
- Go < 1.22 时循环变量被 goroutine/闭包捕获（BLOCKER）
- `sync.Mutex` 被值拷贝（结构体按值传递）（BLOCKER）
- 无界并发：循环里直接 `go`，没有限流/worker pool（WARN）

## R4 安全

- SQL 用 `fmt.Sprintf` / `+` 拼接后执行；gorm `Where(fmt.Sprintf(...))`、`Raw` 拼接（BLOCKER）
- `exec.Command("sh","-c", 用户输入)`（BLOCKER）
- 硬编码 token/密码/AK/SK/私钥（BLOCKER）
- 接口缺鉴权，或只校验登录不校验资源归属（越权）（BLOCKER）
- 日志打印密码、token、身份证、手机号全量（WARN）
- 把内部错误/堆栈/SQL 返回给调用方（WARN）
- 文件路径由外部输入拼接，未做 `filepath.Clean` 与前缀校验（BLOCKER）
- 反序列化不可信输入到 `interface{}` 后不校验直接使用（WARN）

## R5 性能

- 循环里查 DB / 调 RPC（N+1）（WARN，热路径 BLOCKER）
- 新查询条件无索引、`SELECT *` 大表（WARN）
- 一次性加载无上限数据到内存（WARN）
- 热路径上的反射、正则重复编译、`fmt.Sprintf` 拼接大量字符串（NIT/WARN）
- 大结构体按值传递 / 频繁小对象分配可用 `sync.Pool`（NIT）
- 缓存无 TTL、key 无限增长（WARN）

## R6 可维护性

- 分层越界：handler 直接操作 DB；repo 里写业务规则（WARN）
- 函数过长（> 80 行）、参数过多（> 5 个）（NIT）
- 导出了不需要导出的符号；接口定义在实现方而非使用方（NIT）
- 复制粘贴的重复逻辑（WARN，≥ 3 处）
- 新增逻辑无单测，尤其是分支多的业务函数（WARN）
- 测试只测 happy path；表驱动用例名不描述场景（NIT）
- 魔法数字、误导性命名（NIT）
