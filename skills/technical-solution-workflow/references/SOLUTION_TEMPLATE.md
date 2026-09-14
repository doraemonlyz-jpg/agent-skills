# Technical Solution Document Template

Used by the **Architectural** path only. Bounded designs live in chat and must
not produce this document.

Include the sections relevant to the project; scale each section to its actual
complexity. Every major architecture decision must trace back to a confirmed
requirement.

## 1. Project Goals and Scope

- Problem statement
- Target users
- MVP goals
- Non-goals
- Future extensions

## 2. Confirmed Requirements

Summarize product, functional, security, deployment, data, and operational
decisions. Carry over the labels from the requirement decision log:
**Confirmed / Recommended default / Open / Future optimization**.

## 3. Architecture Overview

- System context
- Major components
- Main data flow
- External dependencies
- Trust boundaries

Use a text diagram when useful.

## 4. Technology Stack

For each major choice:

- Selected technology
- Why it fits
- Rejected alternatives when relevant
- Constraints or risks

Do not select technologies only because they are popular.

## 5. Module Design

Define clear responsibilities and boundaries for: API, authentication, domain
services, integration adapters, agent or workflow, analysis engine, reporting,
storage, scheduling, notifications, observability.

## 6. Agent Architecture

When AI is involved, explicitly separate:

### Deterministic code

Financial or business calculations, permissions, validation, state transitions,
database writes, scheduling, idempotency, risk limits.

### Agent or LLM

Summarization, explanation, classification, evidence-based recommendations,
natural-language report generation.

Define:

- Agent count
- Agent inputs and outputs
- Tool whitelist
- Forbidden tools
- Structured output schemas
- Human approval points
- Retry and fallback behavior
- Hallucination controls

Default principle:

> Workflow controls the Agent; the Agent does not control the workflow.

## 7. Data Model

Core entities, important relationships, ownership and tenant keys, snapshots and
history, audit records, job records, version fields, retention policy.

## 8. API and Integration Design

External connectors, internal interfaces, authentication, timeouts, rate limits,
retry policy, idempotency, error normalization, schema validation.

Use adapter or provider interfaces around unstable external systems.

## 9. Security Design

Authentication, authorization, credential encryption, secret management, network
exposure, audit logging, rate limiting, sensitive-data redaction, LLM data
boundaries, backup protection.

## 10. Scheduling and Workflow

Trigger types, workflow steps, job state machine, retry rules, timeouts,
concurrency, idempotency key, recovery process.

## 11. Failure and Degradation

For every critical dependency, specify:

- What happens if it fails
- Whether cached data may be used
- How stale data is labeled
- Whether the workflow continues
- Whether an alert is sent

Never allow stale data to appear current without labeling.

## 12. Deployment

Runtime topology, container layout, server requirements, ports, TLS, database
exposure, backup, logging, upgrade process.

Choose the simplest architecture that meets current scale.

## 13. Observability

Logs, metrics, traces where necessary, health checks, alerts, audit events, cost
metrics for LLM systems.

## 14. Testing Strategy

Unit tests, integration tests, contract tests, mocked external providers,
workflow tests, security tests, structured-output validation, failure and retry
tests, acceptance tests.

## 15. Implementation Phases

```text
Phase 0: Technical feasibility
Phase 1: Core data and authentication
Phase 2: Deterministic domain logic
Phase 3: Agent and report generation
Phase 4: Deployment and reliability
Phase 5: Future enhancements
```

Each phase should have explicit acceptance criteria.

## 16. Risks and Open Questions

External API uncertainty, data quality limitations, security risks, operational
single points of failure, cost risks, technical debt intentionally deferred.

## 17. Architecture Decision Summary

A concise list of final decisions.

---

## Implementation Plan (produced after approval)

- Repository structure
- Milestones
- Ordered tasks
- Database migrations
- API endpoints
- Interfaces
- Test plan
- Local environment
- Deployment path
- Verification commands
