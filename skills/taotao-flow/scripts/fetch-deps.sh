#!/usr/bin/env bash
# 按 deps.lock.json 把第三方 skill 拉取到 vendor 目录，并检出锁定的 commit。
#
# 用法:
#   scripts/fetch-deps.sh                 拉取/校正到锁定版本
#   scripts/fetch-deps.sh --check         只检查，不改动（退出码 1 表示有缺失或版本不符）
#   scripts/fetch-deps.sh --from <dir>    离线：从已下载好的目录复制（<dir>/<name>/ 为各仓库）
#
# 环境变量:
#   TAOTAO_VENDOR       vendor 目录（默认 ~/.taotao/vendor）
#   TAOTAO_GIT_MIRROR   GitHub 镜像前缀，例如 https://mirror.example.com/github/ ，会替换 https://github.com/
set -eo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LOCK="$REPO/deps.lock.json"
VENDOR="${TAOTAO_VENDOR:-$HOME/.taotao/vendor}"
MODE=fetch; FROM=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check) MODE=check ;;
    --from) FROM="$2"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

mkdir -p "$VENDOR"
bad=0
while IFS=$'\t' read -r name url commit; do
  dst="$VENDOR/$name"
  [ -n "$TAOTAO_GIT_MIRROR" ] && url="${url/https:\/\/github.com\//$TAOTAO_GIT_MIRROR}"
  have=""
  [ -d "$dst/.git" ] && have="$(git -C "$dst" rev-parse HEAD 2>/dev/null || true)"

  if [ "$MODE" = check ]; then
    if [ "$have" = "$commit" ]; then echo "  ✓ $name ${commit:0:8}"; else echo "  ✗ $name 期望 ${commit:0:8}，实际 ${have:0:8}"; bad=1; fi
    continue
  fi

  if [ "$have" = "$commit" ]; then echo "  ✓ $name ${commit:0:8}（已是锁定版本）"; continue; fi

  if [ -n "$FROM" ]; then
    [ -d "$FROM/$name" ] || { echo "  ✗ $name：$FROM/$name 不存在"; bad=1; continue; }
    rm -rf "${dst:?}"; mkdir -p "$dst"; cp -R "$FROM/$name/." "$dst/"
  elif [ -d "$dst/.git" ]; then
    git -C "$dst" fetch -q origin "$commit" 2>/dev/null || git -C "$dst" fetch -q origin
  else
    git clone -q --filter=blob:none "$url" "$dst" || { echo "  ✗ $name：克隆失败（内网可设 TAOTAO_GIT_MIRROR 或用 --from）"; bad=1; continue; }
  fi
  if git -C "$dst" -c advice.detachedHead=false checkout -q "$commit" 2>/dev/null; then
    echo "  + $name ${commit:0:8}"
  else
    echo "  ✗ $name：检出 ${commit:0:8} 失败"; bad=1
  fi
done < <(python3 - "$LOCK" <<'PY'
import json, sys
for d in json.load(open(sys.argv[1]))["deps"]:
    print(f"{d['name']}\t{d['repo']}\t{d['commit']}")
PY
)

exit $bad
