# Agent Skills Collection

Reusable engineering skills and explicitly separated project-specific skills.

## Reusable Skills

- `project-engineering-standards-bootstrap`: generates project-specific `AGENTS.md`, architecture, coding, security, and testing standards.
- `technical-solution-workflow`: classifies each request as spike / bounded / architectural, clarifies requirements, reviews a versioned technical solution, and blocks coding until explicit approval. Ceremony scales with the task; the approval gate does not.
- `coding-standards`: enforces coding quality, security, testing, and verification during implementation.
- `gated-delivery-workflow`: executes repository-approved work packages through adapter-defined gates, verification, and handoff.

Reusable skills live under `skills/` and can be installed independently.

## Vendored Skills

Third-party skills copied in verbatim. Each carries a `.upstream` file recording
the source repo and commit it was taken from.

- `brainstorming`: turns an idea into a design through dialogue; classifies work as
  spike / bounded / architectural and gates implementation on approval.
  (obra/superpowers)
- `interview-me`: deep-dive spec interviewer — analyses a requirement against the
  codebase, interviews with active pushback, produces an opinionated spec.
  Supports `--verify` for spec/code drift detection. (Sorbh/interview-me)

Note: `brainstorming` overlaps with `technical-solution-workflow` by design — the
latter absorbed its classification and hard-gate model. Enabling both at once will
cause trigger contention; prefer one.

## Project-specific Skills

- `mystockagent-delivery-workflow`: applies the gated delivery workflow to the MyStockAgent V3.2 stages, evidence, security, and financial rules.

Project-specific skills live under `project-skills/`. They depend on files and
contracts owned by their named project and are not standalone generic skills.

## Recommended Usage

Use the skills in this order for a new project:

```text
project-engineering-standards-bootstrap
→ technical-solution-workflow
→ gated-delivery-workflow + coding-standards
```

For MyStockAgent, install
`project-skills/mystockagent-delivery-workflow` into the project's
`.agents/skills/` directory. It composes `gated-delivery-workflow` with the
project-owned adapter and V3.2 documents.

## Evals

`evals/` holds the behavioural test suite for `technical-solution-workflow`:
30 cases across triggering accuracy, gate compliance, and adversarial
gate-bypass attempts, plus the pre-refactor baseline for A/B comparison.
See `evals/README.md`.
