# Statusline Setup

给 Claude Code 和 Codex 装上下文用量显示，用来判断「该开新会话了」。

## 一键装

```bash
~/Projects/agent-skills/setup/install.sh
```

会改 `~/.claude/settings.json` 和 `~/.codex/config.toml`，都先备份 `.bak`。
Codex 那边若已有 `[tui]` 段则不自动改，只打印待合并内容。

## Claude Code

`claude-code/statusline.sh`，两行输出：

```
Opus  myproject  ⎇ main
▓▓▓▓▓▓░░░░ 65% /200K  准备写 handoff · 5h 23%
```

阈值默认 60% 黄 / 80% 红，用环境变量改：

```bash
CC_WARN_PCT=50 CC_CRIT_PCT=75
```

字段取自官方 statusline JSON（`context_window.used_percentage` 等）。
注意两点，脚本已处理：

- `used_percentage` **只按输入 token 计算**（input + cache_creation + cache_read），不含 output
- 会话初期和 `/compact` 之后该字段为 `null`，此时显示 `context —`

自测：

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"context_window":{"used_percentage":88,"context_window_size":200000}}' \
  | ~/.claude/statusline.sh
```

零安装的替代：内置 `/context` 命令，能看各部分占比。

## Codex

`codex/config-tui.toml`，改配置即可，不用脚本。可选字段仅 6 个：

`model-with-reasoning` `current-dir` `context-usage` `used-tokens` `five-hour-limit` `weekly-limit`

### 两个限制

**不支持自定义命令** —— [openai/codex#17827](https://github.com/openai/codex/issues/17827) 还没合并，
所以 Codex 侧无法自定义阈值和配色，只能看数字自己判断。该 issue 的提案接口刻意对齐了
Claude Code 的 stdin JSON 格式，合并后上面那个脚本大概率能直接复用。

**计数偏低** —— [openai/codex#45074](https://github.com/openai/codex/issues/45074)：
显示 388K 时内部实际已 623K 并触发自动压缩。**显示值比真实占用低**，定阈值要留余量，
Claude Code 那边用 70%，Codex 这边建议按 50% 就准备交接。

## 下一步

statusline 只解决「发现」。发现之后要把状态交接出去，见
[REMvisual/claude-handoff](https://github.com/REMvisual/claude-handoff)（自带 PreCompact hook 兜底）。

先用一两周看看自己的长对话通常在什么百分比开始变笨，再定阈值 —— 别人的 70% 不一定适合你。
