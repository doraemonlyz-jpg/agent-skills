# before_code — 开工前检查

**档位**：Design/Plan 缺失 = 硬阻断；其余软警告。先查项目覆盖版本 `docs/hooks/before_code.md`。

## Step 0 — 判断来源

- 由 `tt:impl` 触发 → 新需求编码，执行全部检查；
- 由 `tt:fix` / `tt:sync` 触发 → 修复/补丁模式，输出「🔧 修复/补丁模式，跳过文档检查」，直接到 Step 3。

## Step 1 — 文档就绪 [硬阻断]

需求目录下：

- `Design-*.md`、`Plan-*.md` 缺失 → 🚫 硬阻断（impl 的输入不存在，没法按计划写）；
- `ARD-*.md`、`Test-*.md` 缺失 → ⚠️ 软警告。

## Step 2 — 文档时序 [软警告]

比较 ARD 和 Design 的最后修改时间（优先 `git log -1 --format=%ci -- <file>`，未提交时用 `stat`；macOS 用 `stat -f %m`，Linux 用 `stat -c %Y`）。ARD 比 Design 新 → 提示"需求可能已变、设计未同步，建议先 tt:sync"。

## Step 3 — Git 状态 [软警告]

- `git status --porcelain` 有无关的未提交改动 → 列出，确认后继续；
- `git branch --show-current` 是 master/main → 建议先切功能分支。

## Step 4 — Go 环境 [软警告]

- `go build ./...` 当前能否通过（开工前就编不过的，先告诉用户，别把旧问题算到新代码上）；
- Design 里提到的新依赖是否已在 go.mod；
- 有 DB 变更时，migration 目录是否存在；
- 新增配置项对应的配置文件/环境变量是否就位。

## 输出

```
✅ 开工前检查通过（backend-go）
- 文档: Design ✓ Plan ✓ ARD ✓ Test ✓/—
- 时序: 一致 ✓ / ARD 更新（已确认）
- Git: 干净 ✓ / 分支 feature/xxx ✓
- 环境: go build ✓ / 依赖 ✓ / migration —
可以开始写代码。
```
