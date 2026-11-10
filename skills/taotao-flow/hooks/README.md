# 钩子：阶段门禁

钩子是阶段之间的检查点。它们由各命令在固定 Step **显式 Read** 后执行，不靠自动扫描目录——这样每个钩子什么时候跑是确定的，可以从命令文件里一眼看出来。

| 钩子 | 谁调用 | 时机 | 档位 |
|---|---|---|---|
| `after_ard.md` | tt:ard Step 6 | ARD 落盘后 | 全部软警告 |
| `after_design.md` | tt:design Step 5 | Design 落盘后 | 接口四要素缺失 = 硬阻断，其余软警告 |
| `before_code.md` | tt:impl Step 0 | 写代码前 | Design/Plan 缺失 = 硬阻断，其余软警告 |
| `after_code.md` | tt:impl Step 5 | 全部任务完成后 | 安全红线 = 硬阻断，清洁问题软警告 |
| `before_commit.md` | 用户说"推送/push/合代码"时 | git 操作前 | 无 CR / CR 失败 / 结论异常 / 扫描硬失败 / CR 后改动 / 敏感信息 = 硬阻断 |

```
after_ard  →  after_design  →  before_code  →  after_code  →  before_commit
 (软)          (硬/软)          (硬/软)         (硬/软)         (硬)
需求覆盖       架构完整          可以开工        代码质量         提交门禁
```

## 强制执行：脚本化的 hook

上面的钩子文件是给 AI 读的检查清单。为了让关键检查不依赖 AI 记不记得，`tt:init` 还会安装三个真正执行的 hook：

| hook | 脚本 | 作用 |
|---|---|---|
| Claude Code PostToolUse `Write\|Edit\|MultiEdit` | `claude-hooks/post-write.sh` | 写入 ARD/Design 后把"执行 after_ard / after_design"反馈给 Claude；写入 .go 后自动 gofmt |
| Claude Code PreToolUse `Bash` | `claude-hooks/pre-bash.sh` | 词法识别 git push / 主干 commit / 主干 merge / `gh pr create\|merge`（含 `bash -c`、绝对路径、`git -c` 等写法），跑 `commit-gate.sh`：硬阻断项退出码 2 拦下；警告以 `permissionDecision: ask` 弹给用户确认（exit 0 时 stderr 模型看不到，所以不用 stderr 传警告）；门禁脚本出错也拦（失败即拦截）；功能分支 commit 只拦敏感信息 |
| git 原生 pre-push | `git-hooks/pre-push` → `.git/hooks/pre-push` | 所有推送方式都生效（Codex、IDE、终端），按实际推送范围扫描；已有其他 pre-push 时不覆盖，只提示 |

紧急通道：命令写成 `TAOTAO_GATE=off git push`。两种 hook 都能识别，跳过 CR 与扫描检查，敏感信息仍然拦截，并写 `.taotao/gate-audit.log`。没安装 taotao-flow 的同事拉到这份配置时，hook 找不到脚本会静默放行。

## 两档的含义

- 🚫 **硬阻断**：停止当前流程，说明缺什么、怎么恢复；用户处理后重跑对应命令。不能因为用户说"先这样吧"就自行放行——需要用户明确改配置或修复问题。
- ⚠️ **软警告**：列出问题，用户回复「继续」即放行，并在 progress.md「当前卡点」记一笔，方便回头看。

## 项目级覆盖

在项目里放 `docs/hooks/<同名>.md`，命令会优先读项目版本，找不到再用本目录的内置版本。适合加团队专属检查，例如：

| 场景 | 覆盖哪个钩子 | 加什么 |
|---|---|---|
| 强制 DB Review | `after_design.md` | 检测到 migration 时提醒找 DBA 评审 |
| 公司级安全扫描 | `after_code.md` | 追加 semgrep 规则扫描（可参考 tob:static-analysis）或公司内部扫描服务 |
| 提交前跑全量单测 | `before_commit.md` | `go test ./... -race` 必须通过 |

自定义钩子按这个骨架写：

```markdown
# <钩子名>
**档位**：硬阻断 / 软警告
## 检查
1. …
## 输出
✅ <钩子名>：检查项 A 通过 / 失败（详情）
```
