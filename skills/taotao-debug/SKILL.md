---
name: taotao-debug
description: Go 后端 Bug 与性能问题的系统化排查：以 superpowers 的 systematic-debugging 四阶段（根因调查 → 模式分析 → 假设验证 → 实施）为骨架，叠加 samber golang-troubleshooting 的 Go 手段（pprof、race、goroutine dump、dlv），用 5 Whys 收敛到带 file:line 证据的根因后才给最小修复。被 taotao-flow 的 tt:fix 调用；用户说"有个 bug""接口报错了""线上 panic""接口变慢了""内存涨了""goroutine 泄漏""帮我排查一下"时也应使用。
metadata:
  version: 2.0.0
  short-description: Go 系统化排查（debugging 适配层）
---

# taotao-debug — Go 排查（适配层）

`$VENDOR` = `${TAOTAO_VENDOR:-~/.taotao/vendor}`。

## 内核

1. Read `$VENDOR/superpowers/skills/systematic-debugging/SKILL.md`，遵守它的铁律：**没有根因调查就没有修复**；四个阶段按顺序走；连续 3 次修复失败就停下质疑架构假设。调用链深时读同目录 `root-cause-tracing.md`，需要多层防护时读 `defense-in-depth.md`。
2. Read `$VENDOR/cc-skills-golang/skills/golang-troubleshooting/SKILL.md`：Go 专项诊断手段。性能问题再读 `golang-performance`，并发问题读 `golang-concurrency`。

vendor 缺失时按下方兜底流程。

## Go 专项速查

| 现象 | 先做什么 |
|---|---|
| panic | 从堆栈第一帧业务代码看；常见 nil 指针、`concurrent map writes`、越界、类型断言失败、关闭已关闭的 channel |
| 错误结果 | 沿 handler → service → repo → 下游逐层核对数据；对比正常与异常请求的第一个分歧点；常见 JSON tag/omitempty、类型不一致、时区、错误被吞返回零值、缓存脏数据 |
| 慢 / 超时 | 先定位慢在哪段（日志耗时、trace span），再 `go tool pprof …/profile?seconds=30`；锁竞争看 `-mutex`/`-block`；查连接池、N+1、缺索引、下游无超时 |
| 内存/goroutine 上涨 | `…/goroutine?debug=2` 找数量大且堆栈相同的一组看阻塞点；`pprof -inuse_space` 两个时间点对比 |
| 偶现、和并发相关 | `go test -race` / `go run -race` 复现；查 check-then-act、懒加载单例、共享 map |
| 回归 | `git log -S`、`git bisect` 找引入提交 |

代码定位优先用 gopls MCP（`go_search`、`go_symbol_references`），其次知识索引，最后指定目录 grep。

## 兜底流程

1. **采集**（缺什么问什么，一次一个）：现象（错误/堆栈/日志/trace_id）、复现路径与频率、期望结果、影响范围与开始时间、最近变更。
2. **分类**：按上表归类。
3. **根因（5 Whys）**：一直问到落在具体代码或配置位置。
4. 🛑 输出根因与证据，等用户确认后再修。

## 报告

```
## 排查报告
**问题**：一句话 · **严重程度**：P0–P3 · **影响**：接口/用户/时间段
**复现**：步骤
### 根因
- 类型：数据 / 逻辑 / 并发 / 资源 / 配置环境 / 回归
- 位置：<file:line>
- 因果链：1. … 2. …
### 修复
- 推荐：<文件:行> + diff
- 备选：…
### 验证
- [ ] 复现测试 <TestXxx>：修复前失败、修复后通过
- [ ] 边界：空数据 / 并发 / 下游失败
- [ ] 回归：同模块其他接口
- [ ] 性能问题附修复前后数据
```

修复后提醒：用 taotao-review 过一遍；值得记录的坑走 tt:exp。
