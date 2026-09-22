---
name: gated-delivery-workflow
description: Execute, review, resume, verify, or hand off approved engineering work through repository-defined phases, milestones, and work packages. Use when Codex is asked to implement a planned task, choose the next task, continue milestone delivery, enforce an architecture approval gate, validate completion, report project progress, or stop on architecture drift. Works across languages and frameworks through a repository adapter at .agents/delivery-workflow.json.
---

# Gated Delivery Workflow

## Objective

Execute one repository-approved Work Package at a time. Discover project rules from the repository adapter, respect approval and phase gates, verify with evidence, and stop on architecture drift.

## Discover the Adapter

1. Locate the repository root.
2. Read every applicable `AGENTS.md` before editing.
3. Require `.agents/delivery-workflow.json`.
4. Run:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/gated-delivery-workflow/scripts/inspect_delivery_config.py" --repo .
   ```

   When this skill is installed elsewhere (for example as a Claude plugin), run the same script from this skill's own `scripts/` directory.

5. Stop if the adapter is missing, invalid, unapproved, or references missing files.
6. Read the adapter's `baseline.required_documents` in order.
7. Run every command in `preflight.commands`.

Read `references/adapter-contract.md` when creating or repairing an adapter. Do not invent project policy when the adapter is incomplete.

If the adapter or milestone files are missing, stop and route to `delivery-plan-bootstrap`. For plans it created (`docs/tasks/README.md` names it), milestone files follow its `references/milestone-file-format.md`, and milestone authorization and replanning go through it instead of hand edits to `authorized_milestones`. Repositories with their own delivery conventions, such as a project-specific delivery skill, keep them.

## Select One Work Package

Use a stable task ID supplied by the user or documented by the repository.

If a task ID is provided, run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/gated-delivery-workflow/scripts/inspect_delivery_config.py" --repo . --task <TASK-ID>
```

If the user asks for the next task:

1. Inspect documented status and completion evidence.
2. Select the earliest task whose dependencies and phase gate are satisfied.
3. Do not infer authorization from dates, partial progress, or words such as “continue.”
4. Ask for approval only when the adapter requires a user checkpoint and no evidence exists.

Execute one Work Package per turn unless the user explicitly requests parallel work and the tasks have no shared files, migrations, state, external limits, or ordering dependencies.

Read `references/task-lifecycle.md` for selection, resume, state, and blocking rules.

## Plan Before Editing

Publish a focused plan containing:

- Task ID and goal.
- Gate and dependency evidence.
- Exact files or modules expected to change.
- Interface, schema, migration, compatibility, rollout, and rollback effects.
- Required test layers.
- Explicit non-goals.

Inspect the working tree, relevant implementation, tests, and user changes before editing. At most one plan step may be in progress.

## Implement Within the Adapter

1. Apply all `hard_rules` from the adapter.
2. Keep changes limited to the selected Work Package.
3. Preserve existing user changes and avoid unrelated refactoring.
4. Follow repository coding, security, testing, and architecture standards.
5. Keep external systems behind approved boundaries.
6. Add or update tests with the implementation.
7. Document intentional compatibility or migration behavior.
8. Do not weaken gates to preserve a target date.

Project adapter rules override generic preferences but cannot override system safety or repository governance.

## Verify With Evidence

Use the task's required tests, its `How to check` commands and manual checks when the plan lists them, and adapter `verification.commands`. Run only commands configured or justified for the repository.

Classify evidence as appropriate:

- Unit.
- Integration.
- Contract.
- Workflow or end-to-end.
- Security.
- Golden or snapshot.
- Performance or reliability.
- Manual external evidence.

Read `references/verification-evidence.md` for selection and reporting rules.

Never replace real authorization, licensing, external-service, production, or restore evidence with a mock. Never report a check as passed unless it actually ran.

## Stop on Architecture Drift

Stop and set status to `ARCH_REVIEW` when implementation requires changing any adapter-defined `architecture_change_triggers` or an equivalent material boundary.

Report:

- The discovered assumption.
- The affected requirements and components.
- Why the current solution cannot safely absorb it.
- The decision or new approval required.

Do not silently modify an approved technical solution or expand capability.

## Complete and Handoff

Mark a Work Package DONE only when:

- Task-specific acceptance criteria pass.
- Adapter and repository checks pass.
- Required evidence is recorded.
- Security and architecture reviews find no unreported drift.
- Known limitations and skipped checks are explicit.

Use `assets/work-package-handoff.md`, or the adapter's `verification.handoff_template` when set. For plans created by `delivery-plan-bootstrap`, save it as `docs/tasks/handoffs/<TASK-ID>.md` and set the Work Package's `Status` and `Evidence` fields in its milestone file; otherwise record it where the repository documents evidence. Stop after handoff; do not automatically start the next Work Package.

## Status Semantics

- `BLOCKED`: a documented dependency, permission, or gate is missing.
- `READY`: dependencies and authorization are satisfied.
- `IN_PROGRESS`: the single selected task is being implemented.
- `VERIFYING`: implementation is complete and checks are running.
- `DONE`: all completion evidence exists.
- `FAILED`: required verification ran and failed.
- `ARCH_REVIEW`: a material approved assumption must change.
