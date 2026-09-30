# Agent Skills Collection

Reusable engineering skills and explicitly separated project-specific skills.

## Reusable Skills

- `project-engineering-standards-bootstrap`: generates project-specific `AGENTS.md`, architecture, coding, security, and testing standards.
- `technical-solution-workflow`: classifies each request as spike / bounded / architectural, clarifies requirements, reviews a versioned technical solution, and blocks coding until explicit approval. Ceremony scales with the task; the approval gate does not.
- `coding-standards`: enforces coding quality, security, testing, and verification during implementation.
- `delivery-plan-bootstrap`: turns an approved solution into phases, milestones, work packages, and the `.agents/delivery-workflow.json` adapter; records milestone authorization and replans after `ARCH_REVIEW`. Leaves repositories with their own delivery conventions in their format.
- `gated-delivery-workflow`: executes repository-approved work packages through adapter-defined gates, verification, and handoff.
- `context-handoff`: decides when a session must end and writes the handoff that auto-compaction destroys — grounded in 22 measured compaction events.

Reusable skills live under `skills/` and can be installed independently.

## Vendored Skills

Third-party skills copied in verbatim. Each carries a `.upstream` file recording
the source repo and commit it was taken from.

- `interview-me`: deep-dive spec interviewer — analyses a requirement against the
  codebase, interviews with active pushback, produces an opinionated spec.
  Supports `--verify` for spec/code drift detection. (Sorbh/interview-me)

## Project-specific Skills

- `mystockagent-delivery-workflow`: applies the gated delivery workflow to the MyStockAgent V3.2 stages, evidence, security, and financial rules.

Project-specific skills live under `project-skills/`. They depend on files and
contracts owned by their named project and are not standalone generic skills.

## Recommended Usage

Use the skills in this order for a new project:

```text
project-engineering-standards-bootstrap
→ (interview-me) → technical-solution-workflow
→ delivery-plan-bootstrap
→ gated-delivery-workflow + coding-standards
```

After each milestone, authorize the next one with `delivery-plan-bootstrap`.
On `ARCH_REVIEW`, revise the solution with `technical-solution-workflow`, then
replan with `delivery-plan-bootstrap`. Use `context-handoff` when a session runs
long.

For MyStockAgent, install
`project-skills/mystockagent-delivery-workflow` into the project's
`.agents/skills/` directory. It composes `gated-delivery-workflow` with the
project-owned adapter and V3.2 documents.

## Evals

`evals/` holds the behavioural test suite for `technical-solution-workflow`:
30 cases across triggering accuracy, gate compliance, and adversarial
gate-bypass attempts, plus the pre-refactor baseline for A/B comparison.
See `evals/README.md`.

## Setup

`setup/` 里是两个 Agent 的 statusline 配置，用来显示上下文用量、判断何时该开新会话。
`setup/install.sh` 一键装 Claude Code 与 Codex 两侧，详见 `setup/README.md`。

## Release

同步和发布都只使用最后一次提交里的内容，未提交的改动不会被同步出去。

**自动同步（推荐）：** 执行一次 `setup/release.py --install-hook`。之后在 main 上每次提交或拉取，
都会自动跑测试，并把所有 skill 同步到 Codex（`~/.codex/skills`）和 SmartWork（`~/.SmartWork/skills`），
同时重新生成 `dist/agent-skills.plugin`。测试不通过就不同步。

**手动：**

```bash
setup/release.py <skill>            # 按 SKILL.md 里的 metadata.version 打标签，再同步
setup/release.py --sync             # 只同步和打包，不打标签
setup/release.py <skill> --push     # 同时推送当前分支和新标签
setup/release.py --sync --dry-run   # 只看会做什么，不改任何东西
```

- 打标签前，SKILL.md 的 `metadata.version` 要在 CHANGELOG 里有对应的 `## <version>` 条目。
- 已经通过 `~/.agents/skills` 链接提供的 skill，不会再复制进 `~/.codex/skills`。
- 钩子插在 `.git/hooks/post-commit` 和 `post-merge` 的开头，原有内容（比如 Moss 的钩子）照常执行；
  如果被其他工具覆盖，重新执行一次 `--install-hook` 即可。
