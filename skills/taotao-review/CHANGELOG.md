# Changelog — taotao-review

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

## 2.1.0 — 2026-11-10 — 复用 go-check.sh 结果

工具扫描改为读取 .taotao/last-check.json（tt:cr 已运行 go-check.sh），被跳过的工具必须在报告中写明「未执行」。

## 2.0.0 — 2026-11-09 — 第三方适配层

内核改为 samber Go 规范 + superpowers requesting-code-review 独立评审子 agent；保留 Go 六维检查表作为兜底。
