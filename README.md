# Agent Skills Collection

Reusable engineering skills and explicitly separated project-specific skills.

## Reusable Skills

- `project-engineering-standards-bootstrap`: generates project-specific `AGENTS.md`, architecture, coding, security, and testing standards.
- `technical-solution-workflow`: clarifies requirements, reviews a versioned technical solution, and blocks coding until explicit approval.
- `coding-standards`: enforces coding quality, security, testing, and verification during implementation.
- `gated-delivery-workflow`: executes repository-approved work packages through adapter-defined gates, verification, and handoff.

Reusable skills live under `skills/` and can be installed independently.

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
