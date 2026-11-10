#!/usr/bin/env python3
"""taotao-flow: 基于 `go list -json ./...` 生成轻量知识索引。

产物（写入 <project>/docs/knowledge/）：
  packages.yaml  包、内部依赖、反向依赖、导出符号数、hubs
  api.yaml       HTTP/RPC 路由注册候选（正则扫描，带 file:line，需读码确认）
  manifest.yml   base_commit、生成时间、统计

用法: go-map.py <project_root> [--update]
--update 只是在输出中标注变更的包；结果与全量一致（go list 本身就快）。
只依赖 Python 标准库，YAML 手写输出，不需要 PyYAML。
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

ROUTE_PATTERNS = [
    # gin / echo / hertz / chi / fiber: r.GET("/path", h) ; g.Handle("POST", "/path")
    (re.compile(r'\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|Any)\(\s*"([^"]+)"'), "http"),
    (re.compile(r'\.(Get|Post|Put|Delete|Patch)\(\s*"(/[^"]*)"'), "http"),
    (re.compile(r'\.Handle\(\s*"(GET|POST|PUT|DELETE|PATCH)"\s*,\s*"([^"]+)"'), "http"),
    # net/http
    (re.compile(r'(?:http\.)?HandleFunc\(\s*"([^"]+)"'), "http"),
    (re.compile(r'mux\.Handle\(\s*"([^"]+)"'), "http"),
    # grpc / kitex 注册
    (re.compile(r'\b(Register\w+Server)\('), "rpc"),
    (re.compile(r'\b(\w+service)\.NewServer\('), "rpc"),
]
EXPORTED_DECL = re.compile(r'^(?:func(?:\s+\([^)]*\))?\s+([A-Z]\w*)|type\s+([A-Z]\w*)|(?:var|const)\s+([A-Z]\w*))', re.M)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def q(s):
    """YAML 安全的双引号字符串。"""
    return json.dumps(s, ensure_ascii=False)


def go_list(root):
    p = run(["go", "list", "-e", "-json", "./..."], root)
    if p.returncode != 0 and not p.stdout:
        sys.exit("go list 失败:\n" + p.stderr)
    dec = json.JSONDecoder()
    s, i, pkgs = p.stdout, 0, []
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1
        if i >= len(s):
            break
        obj, i = dec.raw_decode(s, i)
        pkgs.append(obj)
    return pkgs


def git(root, *args):
    p = run(["git", *args], root)
    return p.stdout.strip() if p.returncode == 0 else ""


def read_manifest_commit(path):
    if not os.path.exists(path):
        return ""
    for line in open(path, encoding="utf-8"):
        if line.startswith("base_commit:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = os.path.abspath(sys.argv[1])
    update = "--update" in sys.argv[2:]
    out_dir = os.path.join(root, "docs", "knowledge")
    os.makedirs(out_dir, exist_ok=True)

    pkgs = go_list(root)
    module = next((p.get("Module", {}).get("Path") for p in pkgs if p.get("Module")), "")
    internal = {p["ImportPath"] for p in pkgs}

    rev = {ip: set() for ip in internal}
    info = {}
    routes = []
    for p in pkgs:
        ip = p["ImportPath"]
        deps = sorted(d for d in p.get("Imports", []) if d in internal)
        for d in deps:
            rev[d].add(ip)
        files = p.get("GoFiles", []) + p.get("CgoFiles", [])
        exported = 0
        pdir = p.get("Dir", "")
        for f in files:
            fp = os.path.join(pdir, f)
            try:
                src = open(fp, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "Code generated" in src[:400] and "DO NOT EDIT" in src[:400]:
                continue
            exported += sum(1 for _ in EXPORTED_DECL.finditer(src))
            rel = os.path.relpath(fp, root)
            for lineno, line in enumerate(src.splitlines(), 1):
                for pat, kind in ROUTE_PATTERNS:
                    m = pat.search(line)
                    if m:
                        g = m.groups()
                        method, path = (g[0], g[1]) if len(g) == 2 else ("", g[0])
                        routes.append((kind, method, path, f"{rel}:{lineno}"))
                        break
        info[ip] = {
            "dir": os.path.relpath(pdir, root) if pdir else "",
            "name": p.get("Name", ""),
            "files": len(files),
            "test_files": len(p.get("TestGoFiles", [])) + len(p.get("XTestGoFiles", [])),
            "deps": deps,
            "doc": (p.get("Doc") or "").strip(),
            "error": (p.get("Error") or {}).get("Err", ""),
        }

    changed = set()
    manifest_path = os.path.join(out_dir, "manifest.yml")
    prev = read_manifest_commit(manifest_path)
    if update and prev:
        files = git(root, "diff", "--name-only", f"{prev}..HEAD").splitlines()
        dirs = {os.path.dirname(f) for f in files if f.endswith(".go")}
        changed = {ip for ip, v in info.items() if v["dir"] in dirs}

    hubs = sorted(((len(rev[ip]), ip) for ip in internal if rev[ip]), reverse=True)[:10]
    edges = sum(len(v["deps"]) for v in info.values())

    with open(os.path.join(out_dir, "packages.yaml"), "w", encoding="utf-8") as fh:
        fh.write("# 由 tt:map 生成（go list），请勿手改；人工说明写到 index.md\n")
        fh.write(f"module: {q(module)}\n")
        fh.write("hubs:  # 被内部依赖最多的包，改动前先评估影响面\n")
        for n, ip in hubs:
            fh.write(f"  - {{ package: {q(ip)}, dependents: {n} }}\n")
        fh.write("packages:\n")
        for ip in sorted(info):
            v = info[ip]
            fh.write(f"  - path: {q(ip)}\n")
            fh.write(f"    dir: {q(v['dir'])}\n")
            fh.write(f"    files: {v['files']}\n    test_files: {v['test_files']}\n")
            if v["doc"]:
                fh.write(f"    doc: {q(v['doc'])}\n")
            fh.write(f"    deps: [{', '.join(q(d) for d in v['deps'])}]\n")
            fh.write(f"    dependents: [{', '.join(q(d) for d in sorted(rev[ip]))}]\n")
            if v["error"]:
                fh.write(f"    error: {q(v['error'])}\n")
            if ip in changed:
                fh.write("    changed_since_last_map: true\n")

    with open(os.path.join(out_dir, "api.yaml"), "w", encoding="utf-8") as fh:
        fh.write("# 由 tt:map 正则扫描生成：路由注册候选，需读码确认（可能有误报/漏报）\n")
        fh.write("routes:\n")
        for kind, method, path, loc in sorted(set(routes), key=lambda r: r[3]):
            fh.write(f"  - {{ kind: {kind}, method: {q(method)}, path: {q(path)}, at: {q(loc)} }}\n")

    head = git(root, "rev-parse", "HEAD")
    gov = run(["go", "env", "GOVERSION"], root).stdout.strip()
    with open(manifest_path, "w", encoding="utf-8") as fh:
        fh.write(f"base_commit: {q(head)}\n")
        fh.write(f"generated_at: {q(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n")
        fh.write(f"go_version: {q(gov)}\nmodule: {q(module)}\n")
        fh.write(f"stats: {{ packages: {len(info)}, internal_edges: {edges}, route_candidates: {len(routes)} }}\n")

    print(f"✅ packages={len(info)} edges={edges} routes={len(routes)} base_commit={head[:8] or '(no git)'}")
    if hubs:
        print("hubs top3: " + ", ".join(f"{ip}({n})" for n, ip in hubs[:3]))
    if update:
        print(f"changed packages since {prev[:8] or '(none)'}: {len(changed)}")
    errs = [ip for ip, v in info.items() if v["error"]]
    if errs:
        print(f"⚠️ {len(errs)} 个包加载出错（见 packages.yaml 的 error 字段）")


if __name__ == "__main__":
    main()
