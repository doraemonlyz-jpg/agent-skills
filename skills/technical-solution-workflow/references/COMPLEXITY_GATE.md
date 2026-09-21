# Review Finding and Complexity Gate

Use this gate when a review finding, proof gap, or proposed correction may add a
subsystem, raise the proof standard, or move responsibility from an external
platform into the current project.

## Core rule

A finding proves that a risk or ambiguity exists. It does not prove that the
largest possible correction belongs in this project. Admit the finding before
revising the solution.

## Finding categories

| Category | Meaning | Default action |
|---|---|---|
| Core correction | A local correction required by a confirmed outcome or invariant | Revise the solution and retest the affected behavior |
| External prerequisite | Another platform or owner must supply a capability or fact | Record the evidence needed; do not build it implicitly |
| Operational mitigation | A release, rollback, monitoring, or manual control reduces the risk sufficiently | Record the residual risk and operating procedure |
| Accepted risk | The user accepts the stated residual risk | Record the decision; do not hide it as future work |
| Future optimization | Valuable but not required for the current outcome | Keep it outside the current implementation scope |
| Scope expansion | The correction adds a new subsystem or materially broader responsibility | Present a complexity delta and obtain explicit approval |

## Proof levels

Use the lightest level that satisfies the confirmed requirement.

- **Operational** is the recommended default: focused tests, existing telemetry,
  staged rollout, operator gates, and a rehearsed rollback.
- **Strong** covers named crash, restart, concurrency, or partial-failure cases
  deterministically, without building a general proof platform.
- **Audit-grade** proves completeness and provenance across instances, restarts,
  transport loss, and operator actions. It commonly requires durable state,
  membership, immutable messages, acknowledgements, and independent audit data.

Audit-grade proof must be explicit. Regulatory obligations, irreversible harm,
or a user-confirmed invariant can justify it. A reviewer asking for stronger
proof, by itself, cannot.

## Scope-expansion triggers

Stop before revising when a proposed fix introduces any of these:

- a new long-lived state store or recovery state machine;
- a new service, daemon, controller, or control plane;
- a new cross-instance membership or coordination mechanism;
- reliable delivery, replay, inbox/outbox, acknowledgement, or receipt protocols;
- a new platform capability because an existing platform lacks one;
- supporting machinery whose implementation or operational lifecycle approaches
  or exceeds the primary feature.

External capability gaps do not grant authority to build replacements. Keep the
system in its safe fallback, record a prerequisite, or propose a separately
approved project.

## Complexity delta

Present this before asking the user to expand scope:

| Item | Required content |
|---|---|
| Original failure | Exact trigger and observable impact |
| Confirmed requirement | The requirement or proof level this would violate |
| Minimal mitigation | Smallest correction or operational control |
| Comprehensive fix | New subsystem, protocol, or platform capability |
| Residual risk | What the minimal option still cannot guarantee |
| Cost and ownership | Code, deployment, operations, and responsible owner |
| Recommendation | Which option to choose and why |

If the comprehensive fix is recommended, ask for explicit scope approval. Do not
silently revise the architecture while waiting for an answer.

## Review iteration

- Run one full independent architecture review by default.
- Re-review accepted corrections narrowly. Do not restart an unrestricted review
  loop merely because the proposal changed.
- If a correction creates more machinery than the original feature, re-evaluate
  whether the correction, not the feature, is generating the new findings.
- A new blocker is still reported. The gate controls which fix enters scope; it
  never suppresses evidence about correctness, security, data loss, or rollback.

## Examples

- A lossy metrics path in an ordinary canary may justify holding rollout when
  telemetry is unhealthy and retaining manual approval. Exact per-instance
  checkpoint reconciliation is audit-grade and requires separate approval.
- A stale configuration cache that could reopen traffic may justify an
  authoritative current-head check. A durable cross-restart history protocol is
  stronger and must trace to a confirmed guarantee.
- Missing webhook signature verification or idempotency violates confirmed
  payment correctness and security. Those are core corrections, not optional
  complexity.
