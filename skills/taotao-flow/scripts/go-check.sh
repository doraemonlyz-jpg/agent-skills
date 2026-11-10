#!/usr/bin/env bash
# taotao-flow 本地扫描：对本次改动涉及的 Go 包跑 gofmt / build / vet / golangci-lint / gosec / govulncheck / test -race。
# 结果写入 <项目>/.taotao/last-check.json（提交门禁会读取：build/vet 失败、gosec 高危、govulncheck 命中 → 拦截推送）。
#
# 用法: go-check.sh [PROJECT_ROOT] [BASE_REF]
# 退出码: 0 全部通过；1 硬失败（build/vet 失败、gosec 高危、govulncheck 发现被调用的漏洞）；2 只有软问题或有工具被跳过
set -uo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)}"
cd "$ROOT" || exit 1
BASE="${2:-}"
if [ -z "$BASE" ]; then
  for b in master main origin/master origin/main; do
    if git rev-parse --verify -q "$b" >/dev/null; then BASE="$(git merge-base HEAD "$b")"; break; fi
  done
fi

files="$( { [ -n "$BASE" ] && git diff --name-only --diff-filter=ACMR "$BASE"...HEAD; git diff --name-only --diff-filter=ACMR HEAD; git ls-files --others --exclude-standard; } 2>/dev/null | grep '\.go$' | sort -u )"
pkgs=""
[ -n "$files" ] && pkgs="$(echo "$files" | xargs -n1 dirname | sort -u | sed 's#^#./#' | while read -r d; do [ -d "$d" ] && echo "$d"; done)"

R_FMT=skipped; R_BUILD=skipped; R_VET=skipped; R_LINT=skipped; R_GOSEC=skipped; R_VULN=skipped; R_TEST=skipped
hard=0; soft=0

if [ -z "$pkgs" ]; then
  echo "没有改动的 .go 包"
else
  echo "== 改动包 =="; echo "$pkgs"

  echo "== gofmt -l =="
  unformatted="$(echo "$files" | while read -r f; do [ -f "$f" ] && echo "$f"; done | xargs gofmt -l 2>/dev/null)"
  if [ -n "$unformatted" ]; then echo "$unformatted"; R_FMT=fail; soft=1; else echo "ok"; R_FMT=pass; fi

  echo "== go build =="
  if go build $pkgs; then echo "ok"; R_BUILD=pass; else R_BUILD=fail; hard=1; fi

  echo "== go vet =="
  if go vet $pkgs; then echo "ok"; R_VET=pass; else R_VET=fail; hard=1; fi

  echo "== golangci-lint =="
  if command -v golangci-lint >/dev/null 2>&1; then
    lintargs=""; [ -n "$BASE" ] && lintargs="--new-from-rev=$BASE"
    if golangci-lint run $lintargs $pkgs; then echo "ok"; R_LINT=pass; else R_LINT=fail; soft=1; fi
  else
    echo "跳过（未安装 golangci-lint）"; soft=1
  fi

  echo "== gosec =="
  if command -v gosec >/dev/null 2>&1; then
    # 高危单独判定（硬失败）；golangci 配置里已启用 gosec 时不再重复跑全量
    if ! gosec -quiet -severity high -confidence medium -fmt=text $pkgs; then
      R_GOSEC=fail_high; hard=1
    elif ls .golangci.* >/dev/null 2>&1 && grep -q gosec .golangci.* 2>/dev/null; then
      echo "ok（中低危由 golangci-lint 的 gosec linter 覆盖）"; R_GOSEC=pass
    elif gosec -quiet -fmt=text $pkgs; then
      echo "ok"; R_GOSEC=pass
    else
      R_GOSEC=fail; soft=1
    fi
  else
    echo "跳过（未安装 gosec：go install github.com/securego/gosec/v2/cmd/gosec@latest）"; soft=1
  fi

  echo "== govulncheck =="
  if command -v govulncheck >/dev/null 2>&1; then
    govulncheck $pkgs; rc=$?
    case $rc in
      0) echo "ok"; R_VULN=pass ;;
      3) R_VULN=fail_high; hard=1; echo "发现本次代码实际调用到的漏洞" ;;
      *) R_VULN=error; soft=1; echo "govulncheck 运行失败（rc=$rc，常见原因：无法访问漏洞库 vuln.go.dev，可设置 GOVULNDB 指向镜像）" ;;
    esac
  else
    echo "跳过（未安装 govulncheck：go install golang.org/x/vuln/cmd/govulncheck@latest）"; soft=1
  fi

  echo "== go test -race =="
  if go test -race -count=1 $pkgs; then echo "ok"; R_TEST=pass; else R_TEST=fail; soft=1; fi
fi

mkdir -p .taotao
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null)"
DIRTY=false; [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ] && DIRTY=true
python3 - "$HEAD_SHA" "$DIRTY" "$BASE" "$R_FMT" "$R_BUILD" "$R_VET" "$R_LINT" "$R_GOSEC" "$R_VULN" "$R_TEST" <<'PY'
import json, sys
from datetime import datetime
head, dirty, base, *r = sys.argv[1:]
keys = ["gofmt", "build", "vet", "golangci-lint", "gosec", "govulncheck", "test"]
json.dump({"head": head, "dirty": dirty == "true", "base": base, "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "results": dict(zip(keys, r))}, open(".taotao/last-check.json", "w"), ensure_ascii=False, indent=2)
PY
echo "== 汇总 =="
echo "gofmt=$R_FMT build=$R_BUILD vet=$R_VET golangci-lint=$R_LINT gosec=$R_GOSEC govulncheck=$R_VULN test=$R_TEST"
echo "已写入 .taotao/last-check.json（HEAD $HEAD_SHA$([ "$DIRTY" = true ] && echo '，工作区有未提交改动'))"

if [ $hard -ne 0 ]; then echo "结果: 硬失败"; exit 1; fi
if [ $soft -ne 0 ]; then echo "结果: 有软问题或工具被跳过"; exit 2; fi
echo "结果: 全部通过"
