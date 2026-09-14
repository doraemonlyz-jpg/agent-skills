#!/usr/bin/env bash
# Claude Code statusline — 模型 / 目录 / 分支 / 上下文条 / 换会话提示
#
# 阈值可用环境变量覆盖：
#   CC_WARN_PCT  黄色，准备写 handoff   默认 60
#   CC_CRIT_PCT  红色，该开新会话了     默认 80
#
# 字段依据官方文档 https://code.claude.com/docs/en/statusline
# 注意 used_percentage 只按输入 token 计算，且会话初期与 /compact 之后可能为 null。

set -uo pipefail

WARN_PCT=${CC_WARN_PCT:-60}
CRIT_PCT=${CC_CRIT_PCT:-80}

input=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  printf 'statusline: 需要 jq (brew install jq)\n'
  exit 0
fi

j() { jq -r "$1 // empty" <<<"$input" 2>/dev/null; }

model=$(j '.model.display_name'); model=${model:-?}
dir=$(j '.workspace.current_dir')
pct=$(j '.context_window.used_percentage' | cut -d. -f1)
size=$(j '.context_window.context_window_size')
five=$(j '.rate_limits.five_hour.used_percentage' | cut -d. -f1)

R=$'\033[31m'; Y=$'\033[33m'; G=$'\033[32m'; DIM=$'\033[2m'; BLD=$'\033[1m'; N=$'\033[0m'

branch=""
[ -n "$dir" ] && [ -d "$dir" ] && branch=$(git -C "$dir" branch --show-current 2>/dev/null)

base=$(basename "${dir:-?}")
line1="${BLD}${model}${N} ${DIM}${base}${N}"
[ -n "$branch" ] && line1="${line1} ${DIM}⎇ ${branch}${N}"

if [ -z "$pct" ]; then
  printf '%s\n%s\n' "$line1" "${DIM}context —${N}"
  exit 0
fi

filled=$(( pct / 10 )); [ "$filled" -gt 10 ] && filled=10
bar=""; i=0
while [ "$i" -lt 10 ]; do
  if [ "$i" -lt "$filled" ]; then bar="${bar}▓"; else bar="${bar}░"; fi
  i=$((i+1))
done

if   [ "$pct" -ge "$CRIT_PCT" ]; then c=$R; hint="  ${R}${BLD}← 该开新会话了${N}"
elif [ "$pct" -ge "$WARN_PCT" ]; then c=$Y; hint="  ${Y}准备写 handoff${N}"
else                                  c=$G; hint=""
fi

win=""
[ -n "$size" ] && win=" ${DIM}/$((size/1000))K${N}"

line2="${c}${bar}${N} ${c}${pct}%${N}${win}${hint}"
[ -n "$five" ] && line2="${line2} ${DIM}· 5h ${five}%${N}"

printf '%s\n%s\n' "$line1" "$line2"
