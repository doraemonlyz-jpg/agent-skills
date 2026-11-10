---
name: taotao-go-standards
description: 识别当前 Go 项目的 Go 版本、Web/RPC 框架、ORM、测试与日志库，按研发阶段挑出该加载的 samber/cc-skills-golang 规范（code-style、error-handling、context、concurrency、grpc、database、testing、security 等），让写代码和审代码时用对版本特性和项目惯例。被 taotao-flow 的 tt:impl、tt:cr、tt:test 调用；用户问"这个项目该遵循哪些 Go 规范""Go 1.22 有什么要注意的""按项目规范写"时也应使用。相当于 soda 里 vue-standards-detector 的 Go 版本。
metadata:
  version: 1.0.0
  short-description: Go 规范检测：go.mod → samber 规范
---

# taotao-go-standards — Go 规范检测器

## Step 1 — 检测

```bash
python3 "<本 skill 目录>/detect.py" "$PROJECT_ROOT" [--stage impl|cr|test|design]
```

输出 JSON：

- `go_version`：go.mod 的 `go` 指令（和 `toolchain`）；
- `frameworks`：命中的依赖分类（http / rpc / orm / sql / cache / mq / test / log / di / cli / config）；
- `version_notes`：与版本相关的硬规则，例如 Go ≥ 1.22 循环变量每次迭代新建、可用 `for i := range n`；Go ≥ 1.21 有 `slices`/`maps`/`min`/`max`/`log/slog`；Go < 1.22 时闭包捕获循环变量要手动拷贝；
- `skills`：本阶段应读的 samber skill 列表（已解析为 `$VENDOR/cc-skills-golang/skills/<name>/SKILL.md` 绝对路径，标注是否存在）。

## Step 2 — 加载

按 `skills` 顺序 Read。它们是彼此引用的原子规范（例如错误处理与日志的约定在 `golang-error-handling` 而不在 `golang-observability`），一起读才完整。

和项目自身规约的关系：`docs/rules/code.md` 与 `.golangci.yml` **优先于** samber 规范；两者冲突时按项目的写，并在输出里提一句差异。samber 规范只填补项目规约没写到的地方。

## Step 3 — 输出

```
🧭 Go 规范（<stage>）
- Go 版本：1.22（循环变量每迭代新建；可用 slices/maps/slog/for range int）
- 框架：http=gin · orm=gorm · test=testify · log=zap
- 已加载：golang-code-style, golang-error-handling, golang-context, golang-concurrency, golang-database, golang-stretchr-testify
- 与项目规约的差异：<无 / 列出>
```

被 tt:impl 调用时，把 `skills` 路径清单交回，供它按任务挑 2–4 个塞进实现子 agent 的派发内容。

## vendor 缺失时

detect.py 仍会输出版本与框架信息，`skills` 标注为 missing。此时按 `version_notes` 和 `taotao-review/references/go-checklist.md` 执行，并提示运行 taotao-flow 的 `scripts/fetch-deps.sh` 拉取 samber 规范。
