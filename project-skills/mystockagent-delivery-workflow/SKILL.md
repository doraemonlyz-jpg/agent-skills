---
name: mystockagent-delivery-workflow
description: Apply the generic gated delivery workflow to MyStockAgent V3.2. Use whenever Codex selects, implements, resumes, verifies, reviews, or hands off a MyStockAgent Stage or Work Package, performs prototype or production validation, reports delivery status, or detects architecture drift. Loads the MyStockAgent adapter, inherited requirements, G0-G3 gates, read-only trading boundary, financial precision, security rules, Agent/Evidence constraints, and S0-S7 task files.
---

# MyStockAgent Delivery Adapter

## Compose the Generic Workflow

Use `$gated-delivery-workflow` as the execution engine. Stop and report an installation problem if that global Skill is unavailable.

Run the generic adapter check first:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/gated-delivery-workflow/scripts/inspect_delivery_config.py" --repo .
```

For a selected task:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/gated-delivery-workflow/scripts/inspect_delivery_config.py" --repo . --task <TASK-ID> --run-preflight
```

The adapter is `.agents/delivery-workflow.json`.

## Load MyStockAgent Context

On first entry into a Work Package, read the documents declared by the adapter in order. Then read only the selected Stage file from `docs/versions/v3.2/agent-coder/`.

For an exact same-Work-Package resume, apply the baseline-continuity rule in `AGENTS.md`. Never use `baseline_sha256` to bypass the first full read, a selected Skill read, preflight, approval, dependency, phase, security, architecture, or new-Work-Package gate.

Use `references/repository-map.md` for project paths. Use the generic Skill for task lifecycle, verification evidence, architecture drift, and handoff behavior.

## Keep Context Bounded

- Locate evidence through the target `STATUS.md` and `EVIDENCE_INDEX.md` rows, then read the canonical report and only its explicitly linked new delta.
- Do not load an entire Evidence tree, old samples, full Schema entries, or unrelated Work Packages unless an audit finding requires them.
- Treat referenced Evidence samples as append-only. For a repeated Schema Hash, store/read the compact count, digest reference, safe booleans, and new anomalies; load full entries only for the first observation, a new Hash, or an explicit audit.
- Prefer commands that return bounded PASS/FAIL summaries or selected JSON fields; do not echo full external responses or repeated Schema entries into model context.
- For independent subagents, provide bounded paths and the minimum required turns instead of full conversation history unless the subtask truly depends on it.

## Enforce Project Gates

- V3.2 is the approved development baseline; V3.1 remains historical Evidence and context.
- S0 baseline migration is complete; no product Stage is authorized until the user explicitly starts the prototype.
- S1 through S3 require the user to explicitly start the prototype.
- S4 requires G1 completion and an explicit user `CONTINUE`; S5 through S7 follow their documented dependencies.
- Select and execute one Work Package at a time.
- Stop after verification and handoff.

## Enforce MyStockAgent Hard Rules

1. Keep the MVP completely read-only; never register or expose a trading Tool.
2. Never use `float32` or `float64` for money, price, quantity, cost, cash flow, P&L, weight, or return.
3. Keep Robinhood, Providers, OpenAI, Resend, storage, and PDF behind internal interfaces.
4. Keep credentials, account identifiers, sessions, sensitive financial bodies, and prohibited identity data out of logs, errors, traces, fixtures, and LLM payloads.
5. Use deterministic code for finance, permissions, validation, state, scheduling, idempotency, risk, and writes.
6. Restrict LLMs to frozen Analysis Input Snapshots, structured output, field allowlists, and validated Evidence.
7. In the prototype, keep run data in memory and bind only to loopback; in the formal MVP, use PostgreSQL as source of truth and Redis only for rebuildable state.
8. Preserve immutable Raw, Normalized, Analysis Input, and Report versions once formal persistence begins.
9. Apply only the gate for the current risk: G0/G1 for prototype, G2 for formal MVP, and G3 for production release.
10. Do not weaken security, tests, backup, recovery, Evidence, or precision where the current gate requires them; do not pull production-only work ahead of product validation without a current requirement.

## Project Preflight

The adapter invokes:

```bash
python3 .agents/skills/mystockagent-delivery-workflow/scripts/check_baseline.py
```

On PASS, the script also returns a deterministic `baseline_sha256` over the
repository context files eligible for same-Work-Package reuse. Record that
value in the Work Package handoff; a missing value is not resumable evidence.

Stop if either the generic adapter check or project baseline check fails.
