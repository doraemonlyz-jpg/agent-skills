# Changelog — first-principles-analysis

版本号只在 `SKILL.md` 的 `metadata.version` 里，git tag 形如
`first-principles-analysis/vX.Y.Z`。

---

## 0.1.0 — 2026-10-12 — 初版

来源：2026-10-12 安全策略顶层设计对话中的分析方法（剥离系统名称看业务本质 →
找最本质的结构问题 → 推导技术思路），整理为通用流程。领域内容未写入 Skill。

- 六步：只读事实、搁置方案稿 → 不带系统名的业务本质（七问 + 决策问题一段话）→
  业务工作链与对象生命周期 → 用透镜找本质问题 → 以“分离 / 记录 / 闭环”推导技术
  思路 → 落到现有资产、验证指标、假设与至多三个问题，然后停下等待对齐。
- 证据分级：stated / artefact / verified / proposal / inference / unknown。
- 十个透镜：判断单位错位、完成≠返回、时间即契约、判断与副作用、结论与资源分配、
  生命周期断点、可复现、结果可观测、变更风险、统一与隔离。

待优化：触发描述的准确率；透镜是否需要拆到 references；与
`technical-solution-workflow` 的衔接；是否需要评测用例。
