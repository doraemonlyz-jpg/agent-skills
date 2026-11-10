#!/usr/bin/env python3
"""识别 Go 项目栈并按阶段给出 samber/cc-skills-golang 规范清单。只读 go.mod，不执行任何 go 命令。

用法: detect.py <project_root> [--stage design|impl|test|cr|fix]
"""
import json
import os
import re
import sys

# 依赖模块前缀 → (分类, 名称, 额外 samber skill)
DEP_RULES = [
    ("github.com/gin-gonic/gin", "http", "gin", []),
    ("github.com/labstack/echo", "http", "echo", []),
    ("github.com/cloudwego/hertz", "http", "hertz", []),
    ("github.com/go-chi/chi", "http", "chi", []),
    ("github.com/gofiber/fiber", "http", "fiber", []),
    ("google.golang.org/grpc", "rpc", "grpc", ["golang-grpc"]),
    ("connectrpc.com/connect", "rpc", "connect", ["golang-grpc"]),
    ("github.com/cloudwego/kitex", "rpc", "kitex", []),
    ("github.com/apache/thrift", "rpc", "thrift", []),
    ("github.com/99designs/gqlgen", "rpc", "gqlgen", ["golang-graphql"]),
    ("gorm.io/gorm", "orm", "gorm", ["golang-database"]),
    ("github.com/jmoiron/sqlx", "sql", "sqlx", ["golang-database"]),
    ("github.com/jackc/pgx", "sql", "pgx", ["golang-database"]),
    ("github.com/go-sql-driver/mysql", "sql", "mysql", ["golang-database"]),
    ("entgo.io/ent", "orm", "ent", ["golang-database"]),
    ("github.com/redis/go-redis", "cache", "go-redis", []),
    ("github.com/go-redis/redis", "cache", "go-redis", []),
    ("github.com/segmentio/kafka-go", "mq", "kafka-go", []),
    ("github.com/IBM/sarama", "mq", "sarama", []),
    ("github.com/Shopify/sarama", "mq", "sarama", []),
    ("github.com/stretchr/testify", "test", "testify", ["golang-stretchr-testify"]),
    ("go.uber.org/mock", "test", "gomock", []),
    ("github.com/golang/mock", "test", "gomock", []),
    ("github.com/vektra/mockery", "test", "mockery", []),
    ("github.com/testcontainers/testcontainers-go", "test", "testcontainers", []),
    ("go.uber.org/zap", "log", "zap", ["golang-observability"]),
    ("github.com/sirupsen/logrus", "log", "logrus", ["golang-observability"]),
    ("github.com/rs/zerolog", "log", "zerolog", ["golang-observability"]),
    ("go.opentelemetry.io/otel", "log", "otel", ["golang-observability"]),
    ("github.com/google/wire", "di", "wire", ["golang-google-wire"]),
    ("go.uber.org/fx", "di", "fx", ["golang-uber-fx"]),
    ("go.uber.org/dig", "di", "dig", ["golang-uber-dig"]),
    ("github.com/samber/do", "di", "samber/do", ["golang-samber-do"]),
    ("github.com/samber/lo", "lib", "samber/lo", ["golang-samber-lo"]),
    ("github.com/samber/oops", "lib", "samber/oops", ["golang-samber-oops"]),
    ("github.com/spf13/cobra", "cli", "cobra", ["golang-spf13-cobra"]),
    ("github.com/spf13/viper", "config", "viper", ["golang-spf13-viper"]),
    ("github.com/swaggo/swag", "doc", "swag", ["golang-swagger"]),
]

STAGE_BASE = {
    "design": ["golang-project-layout", "golang-error-handling", "golang-context", "golang-structs-interfaces"],
    "impl":   ["golang-code-style", "golang-naming", "golang-error-handling", "golang-context", "golang-concurrency", "golang-safety"],
    "test":   ["golang-testing"],
    "cr":     ["golang-code-style", "golang-error-handling", "golang-concurrency", "golang-safety", "golang-security", "golang-lint"],
    "fix":    ["golang-troubleshooting", "golang-concurrency", "golang-performance"],
}
# 各阶段只引入与该阶段相关的框架 skill
STAGE_FRAMEWORK = {
    "design": {"golang-grpc", "golang-graphql", "golang-database", "golang-observability", "golang-google-wire", "golang-uber-fx", "golang-uber-dig", "golang-samber-do"},
    "impl": None,   # 全部
    "test": {"golang-stretchr-testify", "golang-database", "golang-grpc"},
    "cr": {"golang-grpc", "golang-database", "golang-observability", "golang-samber-lo", "golang-samber-oops"},
    "fix": {"golang-database", "golang-grpc", "golang-observability"},
}


def parse_version(v):
    m = re.match(r"(\d+)\.(\d+)", v or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def version_notes(ver):
    notes = []
    if not ver:
        return ["go.mod 未声明 go 版本，按项目实际工具链判断"]
    if ver >= (1, 22):
        notes += ["循环变量每次迭代新建，闭包/goroutine 捕获无需手动拷贝", "可用 for i := range n；net/http ServeMux 支持方法与路径参数"]
    else:
        notes += ["Go < 1.22：闭包或 goroutine 捕获循环变量必须先拷贝（v := v）"]
    if ver >= (1, 21):
        notes += ["可用 slices / maps / cmp 标准库与内置 min/max/clear；日志优先 log/slog（项目已选型的除外）"]
    if ver >= (1, 23):
        notes += ["支持 range-over-func 迭代器（iter.Seq）；time.Timer/Ticker 不再需要手动 Stop 防泄漏"]
    if ver >= (1, 24):
        notes += ["可用 testing.B.Loop、泛型类型别名；go.mod 支持 tool 指令管理工具依赖"]
    if ver >= (1, 25):
        notes += ["可用 sync.WaitGroup.Go、testing/synctest 稳定版"]
    return notes


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = os.path.abspath(sys.argv[1])
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "impl"
    gomod = os.path.join(root, "go.mod")
    text = open(gomod, encoding="utf-8").read() if os.path.exists(gomod) else ""
    gov = (re.search(r"^go\s+(\S+)", text, re.M) or [None, None])[1]
    toolchain = (re.search(r"^toolchain\s+(\S+)", text, re.M) or [None, None])[1]
    module = (re.search(r"^module\s+(\S+)", text, re.M) or [None, None])[1]

    frameworks, extra = {}, []
    for prefix, cat, name, skills in DEP_RULES:
        if re.search(r"(^|\s)" + re.escape(prefix) + r"(/v\d+)?\s", text, re.M):
            frameworks.setdefault(cat, [])
            if name not in frameworks[cat]:
                frameworks[cat].append(name)
            extra += skills

    allow = STAGE_FRAMEWORK.get(stage)
    names = list(STAGE_BASE.get(stage, STAGE_BASE["impl"]))
    for s in extra:
        if (allow is None or s in allow) and s not in names:
            names.append(s)

    vendor = os.path.expanduser(os.environ.get("TAOTAO_VENDOR", "~/.taotao/vendor"))
    skills = []
    for n in names:
        p = os.path.join(vendor, "cc-skills-golang", "skills", n, "SKILL.md")
        skills.append({"name": n, "path": p, "exists": os.path.exists(p)})

    print(json.dumps({
        "module": module, "go_version": gov, "toolchain": toolchain, "stage": stage,
        "frameworks": frameworks, "version_notes": version_notes(parse_version(gov)),
        "skills": skills, "has_go_mod": bool(text),
        "has_golangci_config": any(os.path.exists(os.path.join(root, f)) for f in (".golangci.yml", ".golangci.yaml", ".golangci.toml")),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
