#!/usr/bin/env bash
# taotao-skills 自测：在临时目录里生成一个小 Go 仓库，逐项验证脚本行为。
# 用法: skills/taotao-flow/tests/test_workflow.sh   （需要 go、git、python3）
# 覆盖：init 幂等与类型检测、settings.json hooks 合并、go-map、detect.py、eval-log/eval-report、
#       commit-gate 各 verdict、pre-bash/post-write hook、Plan 模板可被 superpowers task-brief 解析。
set -o pipefail
FLOW="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
SKILLS="$(dirname "$FLOW")"
VENDOR="${TAOTAO_VENDOR:-$HOME/.taotao/vendor}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0
ok()  { echo "  ✓ $1"; pass=$((pass+1)); }
bad() { echo "  ✗ $1"; fail=$((fail+1)); }
check() { if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi; }
G="git -c user.email=t@t -c user.name=t"

mkrepo() { # dir [rpc]
  mkdir -p "$1"/{cmd/server,internal/order/{repo,service},api} && cd "$1" || exit 1
  printf 'module example.com/ordersvc\n\ngo 1.22\n' > go.mod
  [ "$2" = rpc ] && printf '\nrequire google.golang.org/grpc v1.65.0\n' >> go.mod
  cat > internal/order/repo/repo.go <<'EOF'
// Package repo 订单数据访问。
package repo

type Store struct{}

func (s *Store) Get(id int64) int64 { return id }
EOF
  cat > internal/order/service/service.go <<'EOF'
package service

import "example.com/ordersvc/internal/order/repo"

type Service struct{ Store *repo.Store }

func (s *Service) Get(id int64) int64 { return s.Store.Get(id) }
EOF
  cat > api/handler.go <<'EOF'
package api

import (
	"net/http"

	"example.com/ordersvc/internal/order/service"
)

func Register(mux *http.ServeMux, svc *service.Service) {
	mux.HandleFunc("/api/v1/order/get", func(w http.ResponseWriter, r *http.Request) { _ = svc })
}
EOF
  printf 'package main\n\nfunc main() {}\n' > cmd/server/main.go
  git init -q -b master && git add -A && $G commit -qm init
}

echo "== S1 init"
mkrepo "$T/p1"
bash "$FLOW/scripts/init-project.sh" . >/dev/null
check "docs 骨架" "[ -f docs/rules/forbidden.md ] && [ -f docs/knowledge/index.md ] && [ -d docs/features/active ] && [ -d docs/eval ]"
check "类型 backend-go" "grep -q 'type: backend-go$' workflow.config.yaml || grep -q 'type: backend-go ' workflow.config.yaml"
check "规则块" "grep -q 'taotao-flow:start' CLAUDE.md && grep -q 'taotao-flow:start' AGENTS.md"
check "CLAUDE.md 用 @ 引用、AGENTS.md 用文字" "grep -q '^@docs/knowledge/index.md' CLAUDE.md && ! grep -q '^@docs' AGENTS.md"
check "hooks 注册" "python3 -c \"import json;h=json.load(open('.claude/settings.json'))['hooks'];assert 'post-write.sh' in json.dumps(h['PostToolUse']) and 'pre-bash.sh' in json.dumps(h['PreToolUse'])\""
echo '{"permissions":{"allow":["Bash(ls)"]},"hooks":{"PreToolUse":[{"matcher":"Edit","hooks":[{"type":"command","command":"echo mine"}]}]}}' > .claude/settings.json
echo "custom" >> docs/rules/forbidden.md
bash "$FLOW/scripts/init-project.sh" . >/dev/null
check "二次 init 不覆盖 rules" "tail -1 docs/rules/forbidden.md | grep -q custom"
check "hooks 合并保留用户配置" "python3 -c \"import json;d=json.load(open('.claude/settings.json'));s=json.dumps(d);assert 'echo mine' in s and 'Bash(ls)' in s and s.count('pre-bash.sh')==1\""
check "规则块只有一份" "[ \$(grep -c 'taotao-flow:start' CLAUDE.md) -eq 1 ]"
check ".gitignore 含 .taotao/" "grep -qx '.taotao/' .gitignore"
mkrepo "$T/p2" rpc; bash "$FLOW/scripts/init-project.sh" . >/dev/null
check "grpc 依赖 → backend-go-rpc" "grep -q 'type: backend-go-rpc' workflow.config.yaml && grep -q 'samber:golang-grpc' workflow.config.yaml"

echo "== S2 go-map / detect"
cd "$T/p1"
python3 "$FLOW/scripts/go-map.py" . >/dev/null
check "packages.yaml + hubs" "grep -q 'hubs:' docs/knowledge/packages.yaml && grep -q 'internal/order/repo' docs/knowledge/packages.yaml"
check "api.yaml 路由" "grep -q '/api/v1/order/get' docs/knowledge/api.yaml"
check "manifest base_commit" "grep -q \"base_commit: \\\"\$(git rev-parse HEAD)\\\"\" docs/knowledge/manifest.yml"
D="$(python3 "$SKILLS/taotao-go-standards/detect.py" "$T/p2" --stage design)"
check "detect: grpc → golang-grpc（design）" "echo '$D' | python3 -c \"import json,sys;d=json.load(sys.stdin);assert d['frameworks']['rpc']==['grpc'] and any(s['name']=='golang-grpc' for s in d['skills'])\""
check "detect: 1.22 版本提示" "echo '$D' | grep -q '循环变量每次迭代新建'"

echo "== S3 eval-log / eval-report"
EL="python3 $FLOW/scripts/eval-log.py"
$EL start --feature cancel-order --stage ard >/dev/null && $EL note --feature cancel-order --stage ard --type clarify --q 状态 --a 待支付 >/dev/null \
  && $EL confirm --feature cancel-order --stage ard --skills taotao-clarify --rounds 2 >/dev/null \
  && $EL rework --feature cancel-order --cause prd_change --reason x --files a.go,b.go >/dev/null \
  && $EL assess --feature cancel-order --manual-hours 8 --ai-ratio 0.5 >/dev/null
F=docs/features/active/cancel-order/eval-log.json
check "eval-log 结构" "python3 -c \"import json;d=json.load(open('$F'));s=d['stages']['ard'];assert s['started_at'] and s['confirmed_at'] and len(s['interventions'])==1 and d['rework_log'][0]['impact']=='medium' and d['archive_assessment']['manual_dev_hours']==8\""
python3 "$FLOW/scripts/eval-report.py" --no-tokens >/dev/null
check "eval-report 生成 HTML" "ls docs/eval/*-report.html && grep -q cancel-order docs/eval/*-report.html"

echo "== S4 commit-gate / Claude Code hook / git pre-push"
git add -A && $G commit -qm docs
# 本地 bare 远端，用来测首次推送与 git pre-push hook
git init -q --bare "$T/remote.git" && git remote add origin "$T/remote.git" && git push -q origin master 2>/dev/null
git checkout -qb feature/x
V() { bash "$FLOW/scripts/commit-gate.sh" . | python3 -c 'import json,sys;print(json.load(sys.stdin)["verdict"])'; }
hook() { printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.stdin.read()},"cwd":sys.argv[1]}))' "$PWD" | bash "$FLOW/claude-hooks/pre-bash.sh" >/tmp/tt_hook_out 2>/dev/null; echo $?; }
crs() { # result [branch] [extra-json]
  mkdir -p .taotao; echo "{\"result\":\"$1\",\"branch\":\"${2:-$(git branch --show-current)}\",\"headCommit\":\"$(git rev-parse --short HEAD)\",\"commitReady\":${4:-true},\"files\":[]${3:-}}" > .taotao/cr-status.json; }
okcheck() { bash "$FLOW/scripts/go-check.sh" . >/dev/null 2>&1; true; }

printf 'package service\n\nconst apiToken = "sk_live_9f8a7b6c5d4e"\n' > internal/order/service/s.go && git add -A
check "暂存区敏感信息 → block_sensitive（优先于无 CR）" "[ \"\$(V)\" = block_sensitive ]"
check "hook：功能分支 commit 含敏感信息被拦" "[ \"\$(hook 'git commit -m x')\" = 2 ]"
$G commit -qm leak
crs pass
check "P0-1 首次推送（无 upstream）扫已提交内容 → 拦" "[ \"\$(V)\" = block_sensitive ] && [ \"\$(hook 'git push -u origin feature/x')\" = 2 ]"
git reset -q --hard HEAD~1
printf 'package service\n\nconst apiToken = "your-token-here"\nvar dsn = "user:pw@tcp(10.1.2.3:3306)/db"\n' > internal/order/service/s.go && git add -A
check "DSN 中的内网 IP 被识别" "[ \"\$(V)\" = block_sensitive ]"
printf 'package service\n\nconst apiToken = "your-token-here"\n' > internal/order/service/s.go && git add -A
check "占位符不误报；功能分支普通 commit 放行" "[ \"\$(hook 'git commit -m x')\" = 0 ]"
$G commit -qm s
rm -f .taotao/cr-status.json
check "无 CR → block_no_cr" "[ \"\$(V)\" = block_no_cr ]"
for c in 'git push origin feature/x' "bash -c 'git push'" '/usr/bin/git push' 'git -c core.quotepath=off push' 'git --no-pager push' 'git -C . push' 'cd . && git push' 'gh pr create --fill' 'env FOO=1 git push'; do
  check "P0-5 绕过写法被识别：$c" "[ \"\$(hook \"$c\")\" = 2 ]"
done
check "无关命令放行" "[ \"\$(hook 'go test ./... && git status')\" = 0 ]"
check "P1-11 功能分支 merge 主干放行" "[ \"\$(hook 'git merge master')\" = 0 ]"
crs pass feature/other
check "P0-2 别的分支的 CR 结论不算数" "[ \"\$(V)\" = block_no_cr ]"
echo '{broken' > .taotao/cr-status.json
check "P0-6 cr-status 损坏 → 拦" "[ \"\$(V)\" = block_invalid_cr ] && [ \"\$(hook 'git push')\" = 2 ]"
crs FAIL
check "P0-6 result 大写 FAIL 也按失败处理" "[ \"\$(V)\" = block_cr_failed ]"
crs pass '' '' false
check "P0-6 commitReady=false → 拦" "[ \"\$(V)\" = block_invalid_cr ]"
echo "{\"result\":\"pass\",\"headCommit\":\"$(git rev-parse --short HEAD)\",\"files\":[]}" > .taotao/cr-status.json
check "旧格式（缺 branch）不被采信" "[ \"\$(V)\" = block_no_cr ]"
crs pass
check "CR pass 但当前 HEAD 没跑扫描 → warn" "[ \"\$(V)\" = warn ]"
check "P0-3 警告以 ask 弹给用户（不是 stderr）" "[ \"\$(hook 'git push')\" = 0 ] && grep -q '\"permissionDecision\": \"ask\"' /tmp/tt_hook_out"
okcheck
check "go-check 写入 last-check.json" "python3 -c \"import json;d=json.load(open('.taotao/last-check.json'));assert d['results']['build']=='pass' and d['results']['vet']=='pass'\""
python3 -c "import json;p='.taotao/last-check.json';d=json.load(open(p));d['results'].update(gosec='pass',govulncheck='pass');json.dump(d,open(p,'w'))"
check "CR pass + 扫描通过 → pass，hook 放行" "[ \"\$(V)\" = pass ] && [ \"\$(hook 'git push')\" = 0 ]"
python3 -c "import json;p='.taotao/last-check.json';d=json.load(open(p));d['results']['gosec']='fail_high';json.dump(d,open(p,'w'))"
check "gosec 高危 → block_checks_failed" "[ \"\$(V)\" = block_checks_failed ] && [ \"\$(hook 'git push')\" = 2 ]"
okcheck; python3 -c "import json;p='.taotao/last-check.json';d=json.load(open(p));d['results'].update(gosec='pass',govulncheck='pass');json.dump(d,open(p,'w'))"
printf '\nfunc Extra() int { return 1 }\n' >> internal/order/service/service.go
check "P0-3 CR 后又改 .go → block_changed_after_cr" "[ \"\$(V)\" = block_changed_after_cr ] && [ \"\$(hook 'git push')\" = 2 ]"
git checkout -q -- internal/order/service/service.go
rm -f .taotao/cr-status.json
check "P0-4 命令前缀 TAOTAO_GATE=off 生效并留审计" "[ \"\$(hook 'TAOTAO_GATE=off git push')\" = 0 ] && grep -q 'TAOTAO_GATE=off' .taotao/gate-audit.log"
printf 'package service\n\nconst apiToken = "sk_live_9f8a7b6c5d4e"\n' > internal/order/service/s.go
check "TAOTAO_GATE=off 仍拦敏感信息；commit -am 时未暂存的已跟踪改动也被扫描" "[ \"\$(hook 'TAOTAO_GATE=off git commit -am x')\" = 2 ]"
git checkout -q -- internal/order/service/s.go
SETCMD="$(python3 -c "import json;print(json.load(open('.claude/settings.json'))['hooks']['PreToolUse'][-1]['hooks'][0]['command'])")"
runset() { printf '{"tool_input":{"command":"git push"},"cwd":"%s"}' "$PWD" | TAOTAO_FLOW_ROOT="$1" HOME="$T/nohome" bash -c "$SETCMD" >/dev/null 2>&1; echo $?; }
check "settings.json 命令：退出码 2 透传" "[ \"\$(runset '$FLOW')\" = 2 ]"
check "settings.json 命令：找不到脚本时静默放行" "[ \"\$(runset '')\" = 0 ]"
# git 原生 pre-push hook（init 已安装）
check "init 安装了 git pre-push hook" "grep -q taotao-flow-git-hook .git/hooks/pre-push"
check "git pre-push：无 CR 时真实 push 被拒" "! TAOTAO_FLOW_ROOT='$FLOW' git push -q origin feature/x 2>/dev/null"
crs pass; okcheck; python3 -c "import json;p='.taotao/last-check.json';d=json.load(open(p));d['results'].update(gosec='pass',govulncheck='pass');json.dump(d,open(p,'w'))"
check "git pre-push：CR 通过后真实 push 成功" "TAOTAO_FLOW_ROOT='$FLOW' git push -q origin feature/x 2>/dev/null"
mkdir -p docs/features/active/x
pw() { printf '{"tool_input":{"file_path":"%s"}}' "$1" | bash "$FLOW/claude-hooks/post-write.sh" 2>/dev/null; echo $?; }
check "post-write：ARD 触发提醒" "[ \"\$(pw \"$PWD/docs/features/active/x/ARD-x.md\")\" = 2 ]"
check "post-write：普通 md 静默" "[ \"\$(pw \"$PWD/README.md\")\" = 0 ]"
printf 'package service\nfunc  Bad( ) {}\n' > internal/order/service/fmt.go
check "post-write：.go 自动 gofmt" "[ \"\$(pw \"$PWD/internal/order/service/fmt.go\")\" = 2 ] && [ -z \"\$(gofmt -l internal/order/service/fmt.go)\" ]"
rm -f internal/order/service/fmt.go

echo "== S4b init 幂等（P1-1）"
cd "$T/p2"
bash "$FLOW/scripts/init-project.sh" . >/dev/null; bash "$FLOW/scripts/init-project.sh" . >/dev/null
check "连续 init：每类 hook 只有一份" "python3 -c \"import json;h=json.load(open('.claude/settings.json'))['hooks'];assert len(h['PreToolUse'])==1 and len(h['PostToolUse'])==1\""
printf '#!/bin/sh\necho other\n' > .git/hooks/pre-push
bash "$FLOW/scripts/init-project.sh" . >/dev/null
check "已有别人的 pre-push 不覆盖" "grep -q 'echo other' .git/hooks/pre-push"
cd "$T/p1"

echo "== S5 Plan 模板与 superpowers 兼容"
TB="$VENDOR/superpowers/skills/subagent-driven-development/scripts/task-brief"
if [ -f "$TB" ]; then
  cp "$FLOW/templates/Plan-Go.md" Plan-t.md
  check "task-brief 能解析 Task 1/2/6" "bash $TB Plan-t.md 1 && bash $TB Plan-t.md 2 && bash $TB Plan-t.md 6"
else
  echo "  · 跳过（未拉取 superpowers：scripts/fetch-deps.sh）"
fi

echo "== S7 TDD 证据：三个验收任务 + 负例"
mkdir -p "$T/tdd/calc" && cd "$T/tdd" || exit 1
printf 'module example.com/demo\n\ngo 1.22\n' > go.mod
cat > calc/calc.go <<'EOF'
package calc

// Discount 满 100 元减 10 元。Bug：边界写成了 >。
func Discount(cents int) int {
	if cents > 10000 {
		return cents - 1000
	}
	return cents
}

// Sum 求和（待重构）。
func Sum(xs []int) int {
	total := 0
	for i := 0; i < len(xs); i++ {
		total = total + xs[i]
	}
	return total
}
EOF
cat > calc/sum_test.go <<'EOF'
package calc

import "testing"

func TestSum(t *testing.T) {
	cases := []struct {
		in   []int
		want int
	}{{nil, 0}, {[]int{1, 2, 3}, 6}, {[]int{-1, 1}, 0}}
	for _, c := range cases {
		if got := Sum(c.in); got != c.want {
			t.Fatalf("Sum(%v) = %d, want %d", c.in, got, c.want)
		}
	}
}

func TestSumUnrelated(t *testing.T) {
	if Sum([]int{2}) != 3 {
		t.Fatal("unrelated assertion broke")
	}
}
EOF
git init -q -b main && git add -A && $G commit -qm init
mkdir -p docs/features/active/demo
cat > docs/features/active/demo/Plan-demo.md <<'EOF'
# demo Implementation Plan

### Task 1: 修复满 100 元不减
**TDD:** bugfix

### Task 2: Sum 改为 range 写法
**TDD:** refactor

### Task 3: 新增 Max
**TDD:** behavior

### Task 4: 补充 README
**TDD:** none — 纯文档
EOF
TE="python3 $FLOW/scripts/tdd-evidence.py"
CK() { { $TE check --feature demo --json 2>/dev/null || true; } | python3 -c "import json,sys;d=json.load(sys.stdin);t={x['task']:x for x in d['tasks']};print(t['$1']['status'] + '|' + ';'.join(t['$1']['missing']))"; }

# 负例：环境故障 / 改动前已通过 / 失败原因不符 / 无关测试失败 / 没用 -run
check "负例：包路径不存在 → 环境故障，红灯无效" "! $TE red --feature demo --task 9 --cmd \"go test ./nope -run '^TestX$'\" --expect 'want 9000' && $TE show --feature demo --task 9 | grep -q '环境故障'"
check "负例：改动前就通过 → 不是红灯" "! $TE red --feature demo --task 9 --cmd \"go test ./calc -run '^TestSum$'\" --expect 'want'"
check "负例：同一命令里有测试因其他原因失败 → 无效" "! $TE red --feature demo --task 9 --cmd \"go test ./calc -run '^TestSum'\" --expect 'want [0-9]' && $TE show --feature demo --task 9 | grep -q -E '其他原因失败|不符'"
check "负例：失败原因与 --expect 不符 → 无效" "! $TE red --feature demo --task 9 --cmd \"go test ./calc -run '^TestSumUnrelated$'\" --expect 'want 9000'"
check "负例：未用 -run 限定 → 无效" "! $TE red --feature demo --task 9 --cmd 'go test ./calc' --expect 'unrelated'"
printf 'package calc\n\nimport "testing"\n\nfunc TestPairA(t *testing.T) { t.Fatal("want 1, got 0") }\n\nfunc TestPairB(t *testing.T) { panic("boom") }\n' > calc/pair_test.go
check "负例：目标测试之一按预期失败、另一个因 panic 失败 → 无效" "! $TE red --feature demo --task 9 --cmd \"go test ./calc -run '^TestPair'\" --expect 'want 1' && $TE show --feature demo --task 9 | grep -q '其他原因失败'"
rm calc/pair_test.go
sed -i 's/Sum(\[\]int{2}) != 3/Sum([]int{2}) != 2/' calc/sum_test.go   # 修好无关测试，后续用例干净

# Task 1：Bug 修复，先红后绿
cat > calc/discount_test.go <<'EOF'
package calc

import "testing"

func TestDiscountAtThreshold(t *testing.T) {
	if got := Discount(10000); got != 9000 {
		t.Fatalf("Discount(10000) = %d, want 9000", got)
	}
}
EOF
check "Task 1 红灯有效（断言按预期失败）" "$TE red --feature demo --task 1 --cmd \"go test ./calc -run '^TestDiscountAtThreshold$'\" --expect 'Discount\\(10000\\) = 10000, want 9000'"
check "Task 1 未改代码就记绿灯 → 拒绝" "! $TE green --feature demo --task 1"
sed -i 's/cents > 10000/cents >= 10000/' calc/calc.go
check "Task 1 绿灯有效（同一命令通过）" "$TE green --feature demo --task 1"
check "Task 1 → TDD 已验证" "[ \"\$(CK 1)\" = 'TDD 已验证|' ]"

# Task 2：纯重构，前后都绿
check "Task 2 baseline 有效" "$TE baseline --feature demo --task 2 --cmd \"go test ./calc -run '^TestSum$'\""
python3 - <<'PY2'
p="calc/calc.go"; s=open(p).read()
s=s.replace("for i := 0; i < len(xs); i++ {\n\t\ttotal = total + xs[i]\n\t}","for _, x := range xs {\n\t\ttotal += x\n\t}")
open(p,"w").write(s)
PY2
check "Task 2 after 有效（同一组测试仍通过）" "$TE after --feature demo --task 2"
check "Task 2 → TDD 已验证" "[ \"\$(CK 2)\" = 'TDD 已验证|' ]"

# Task 3：先实现、后补测试
printf '\n// Max 返回较大值。\nfunc Max(a, b int) int {\n\tif a > b {\n\t\treturn a\n\t}\n\treturn b\n}\n' >> calc/calc.go
printf 'package calc\n\nimport "testing"\n\nfunc TestMax(t *testing.T) {\n\tif Max(1, 2) != 2 || Max(3, 1) != 3 {\n\t\tt.Fatal("Max wrong")\n\t}\n}\n' > calc/max_test.go
check "Task 3 事后补红灯 → 无效（改动前就通过）" "! $TE red --feature demo --task 3 --cmd \"go test ./calc -run '^TestMax$'\" --expect 'Max wrong'"
check "Task 3 没有有效红灯 → 拒绝记绿灯" "! $TE green --feature demo --task 3"
check "Task 3 verify 记录（实现后执行）" "$TE verify --feature demo --task 3 --cmd \"go test ./calc -run '^TestMax$' -race\" --label 并发 && $TE show --feature demo --task 3 | grep -q post_impl"
check "Task 3 → TDD 未验证，列出缺项" "CK 3 | grep -q '^TDD 未验证|改动前失败结果无效'"
check "Task 4 none + 原因 → 不适用" "[ \"\$(CK 4)\" = '不适用|' ]"
check "check 表格显示「TDD 未验证」与实现后补测时间" "{ $TE check --feature demo || true; } | grep -q 'Task 3.*TDD 未验证.*实现后补测（并发，执行于'"
check "check 在有未验证任务时退出码为 1" "! $TE check --feature demo >/dev/null"

# 编译型红灯（引用尚不存在的函数）
cat >> docs/features/active/demo/Plan-demo.md <<'EOF'

### Task 5: 新增 Min
**TDD:** behavior
EOF
printf 'package calc\n\nimport "testing"\n\nfunc TestMin(t *testing.T) {\n\tif Min(1, 2) != 1 {\n\t\tt.Fatal("Min wrong")\n\t}\n}\n' > calc/min_test.go
check "Task 5 编译型红灯有效（undefined: Min）" "$TE red --feature demo --task 5 --cmd \"go test ./calc -run '^TestMin$'\" --expect 'undefined: Min' && $TE show --feature demo --task 5 | grep -q '\"red_kind\": \"compile\"'"
printf '\nfunc Min(a, b int) int {\n\tif a < b {\n\t\treturn a\n\t}\n\treturn b\n}\n' >> calc/calc.go
check "Task 5 绿灯有效 → 已验证" "$TE green --feature demo --task 5 && [ \"\$(CK 5)\" = 'TDD 已验证|' ]"

# 证据文件被手改 → 全部作废
cp docs/features/active/demo/tdd-evidence.jsonl "$T/ev.bak"
sed -i '1s/"exit_code": 1/"exit_code": 0/' docs/features/active/demo/tdd-evidence.jsonl
check "证据被改动 → 哈希链损坏，全部未验证" "CK 1 | grep -q '被改动'"
cp "$T/ev.bak" docs/features/active/demo/tdd-evidence.jsonl
cd "$T/p1"

echo "== S6 skill 文件"
for s in "$SKILLS"/taotao-*/SKILL.md; do
  check "frontmatter $(basename "$(dirname "$s")")" "head -1 '$s' | grep -q '^---$' && sed -n '2,5p' '$s' | grep -q '^name: ' && sed -n '2,6p' '$s' | grep -q '^description: '"
done
for c in init map ard design plan test impl cr fix mock sync archive exp eval; do
  check "命令文件 $c.md" "[ -f '$FLOW/commands/$c.md' ]"
done

echo
echo "结果: $pass 通过, $fail 失败"
[ $fail -eq 0 ]
