---
name: project-engineering-standards-bootstrap
description: Generate and maintain a reusable engineering-governance document set for a software project. Use when starting a new repository, standardizing an existing project, or preparing a repository for coding Agents.
metadata:
  short-description: Bootstrap project engineering standards
---

# Project Engineering Standards Bootstrap

## Purpose

Create a complete, project-specific engineering governance package that coding Agents and human engineers can follow consistently.

The standard output is:

```text
<project-root>/
├── AGENTS.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CODING_STANDARDS.md
│   ├── SECURITY.md
│   └── TESTING.md
└── skills/
    ├── technical-solution-workflow/
    │   └── SKILL.md
    └── coding-standards/
        └── SKILL.md
```

Generate only files appropriate to the project. Add extra documents only when justified, such as `OPERATIONS.md`, `DATA_GOVERNANCE.md`, or `API_STANDARDS.md`.

## Trigger Conditions

Use this skill when the user asks to:

- Create engineering standards for a new project
- Prepare a repository for coding Agents
- Add `AGENTS.md`
- Standardize coding, testing, security, or architecture documents
- Reuse common engineering practices across projects
- Audit or refresh an existing repository's engineering rules

## Core Principles

1. Inspect the repository before generating files.
2. Reuse existing project conventions when sound.
3. Do not overwrite existing governance documents without reviewing them.
4. Separate global practices from project-specific constraints.
5. Keep rules concrete, testable, and enforceable.
6. Avoid generic boilerplate that does not match the project.
7. Link every rule to the actual stack and risk profile.
8. Prefer the smallest complete document set.
9. Record unresolved assumptions explicitly.
10. Treat architecture and security documents as versioned specifications.

## Workflow

```text
Inspect repository
→ Identify project context
→ Check existing standards
→ Confirm material unknowns
→ Generate document set
→ Cross-check consistency
→ Present file tree and summary
→ Obtain approval before committing
```

## Stage 1: Inspect the Repository

Inspect:

- Language and framework
- Package manager and build system
- Repository structure
- Existing README and contributor guides
- Existing `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, or similar files
- CI workflows
- Linters and formatters
- Test commands
- Deployment files
- Database and migration tools
- External integrations
- Security-sensitive areas
- Existing architecture documents

Do not infer a tool or command merely because it is common for the language.

## Stage 2: Confirm Material Unknowns

Ask only questions that materially affect the generated standards:

- Is the architecture already approved?
- Is the system single-user, multi-user, internal, or public?
- Which files are authoritative?
- What deployment environment is used?
- What data is sensitive?
- Are write-capable Agent tools allowed?
- What checks are mandatory before merge?
- Are there language-specific constraints?

Group questions. Do not turn the process into a long questionnaire.

## Stage 3: Generate `AGENTS.md`

`AGENTS.md` is the repository entry point for all coding Agents.

It must include:

- Required reading order
- Pre-coding approval gate
- Repository-specific hard rules
- Explore → Plan → Implement → Verify workflow
- Commands for formatting, linting, testing, and building
- Architecture-drift handling
- Security boundaries
- Completion-report requirements

Keep it concise. Detailed rules belong in linked documents.

## Stage 4: Generate `docs/ARCHITECTURE.md`

Include:

- Document status and version
- System purpose
- Architecture summary
- Major components
- Data flow
- Trust boundaries
- External dependencies
- Deployment topology
- Deterministic versus Agent responsibilities
- Explicit non-goals
- Architecture decision summary

Do not invent architecture. Base it on approved decisions or mark the document as draft.

## Stage 5: Generate `docs/CODING_STANDARDS.md`

Include relevant rules for:

- Readability and simplicity
- Naming
- Functions, packages, and modules
- Comments
- Error handling
- Context and timeouts
- Concurrency
- Performance
- Data precision
- Database access
- Time handling
- External integrations
- Agent and LLM boundaries
- Logging
- Configuration
- Dependencies
- Git practices

Comment rule:

> Comments should be sufficient but not excessive. Add comments for public contracts, complex logic, business rules, edge cases, security-sensitive behavior, and non-obvious decisions. Do not add line-by-line comments for obvious code.

Tailor examples and commands to the project's language.

## Stage 6: Generate `docs/SECURITY.md`

Include:

- Authentication and authorization
- Secret handling
- Credential encryption
- Network boundaries
- Input validation
- Logging redaction
- LLM data boundary
- Agent tool allowlist and denylist
- Audit events
- Backup protection
- Incident or revocation procedures

Do not include real secrets, account numbers, or production identifiers.

## Stage 7: Generate `docs/TESTING.md`

Include:

- Test layers
- Required tests for critical logic
- Integration and contract testing
- Security and negative testing
- Race or concurrency testing where relevant
- Required commands
- Acceptance criteria
- Handling of missing tools
- CI expectations

Only list commands that exist or are explicitly proposed.

## Stage 8: Install Shared Skills

Add or reference:

- `technical-solution-workflow`
- `coding-standards`
- `delivery-plan-bootstrap` and `gated-delivery-workflow` when the project
  will be delivered milestone by milestone through coding Agents

Avoid duplicating full project specs inside Skill files. Skills enforce behavior; project documents define detailed rules.

## Stage 9: Consistency Check

Before completion, verify:

- `AGENTS.md` references existing files.
- Commands match the repository.
- Architecture and security rules do not conflict.
- Coding standards match the chosen language.
- Agent permissions match the approved product boundary.
- Testing covers critical deterministic logic.
- No secrets or user-specific private data are included.
- Draft and approved documents are clearly labeled.

## Existing Files

When a target file already exists:

1. Read it fully.
2. Identify useful existing rules.
3. Propose a merge or targeted update.
4. Preserve project-specific constraints.
5. Do not replace the file wholesale without approval.

## Output

Present:

1. Generated directory tree
2. Short purpose of each file
3. Assumptions and unresolved items
4. Files created or changed
5. Validation performed
6. A downloadable archive when useful

## Approval Gate

Do not commit or publish generated standards unless the user explicitly asks to save or upload them.

When publishing to GitHub:

- Create a focused branch.
- Commit only the governance files.
- Open a Draft PR by default.
- Do not mix unrelated repository changes.
