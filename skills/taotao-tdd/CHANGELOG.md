# Changelog — taotao-tdd

版本号只在 `SKILL.md` 的 `metadata.version` 里。

---

## 2.1.0 — 2026-11-10 — 测试证据

TDD 每一步改为用 taotao-flow 的 `tdd-evidence.py` 记录（red / green / baseline / after / verify），说明有效红灯的判定规则。

## 2.0.0 — 2026-11-09 — 第三方适配层

改为调用锁定版本的第三方 skill（见 skills/taotao-flow/THIRD_PARTY.md），保留 Go 专属规则与 vendor 缺失时的兜底内容。
