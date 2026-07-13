---
name: technical-solution-workflow
description: Guide users from ambiguous product or engineering requirements to an agreed technical solution, and only begin implementation after explicit approval. Use when a user asks to design a system, service, agent, platform, application, architecture, or technical implementation plan.
metadata:
  short-description: Clarify requirements, agree architecture, then code
---

# Technical Solution Workflow

## Purpose

Turn an initial product or engineering idea into a clear, reviewed, and approved technical solution before any implementation begins.

This skill enforces three sequential gates:

1. Requirements are sufficiently clear.
2. The technical solution is explicitly approved.
3. Coding begins only after approval.

Never skip a gate merely because a likely answer can be inferred.

---

# Core Principles

1. Do not start coding from an unclear request.
2. Ask only questions that materially affect scope, architecture, security, cost, delivery, or acceptance.
3. Group related questions instead of asking many tiny questions one by one.
4. Record decisions as they are confirmed.
5. Distinguish MVP requirements from future optimizations.
6. Make a concrete recommendation whenever presenting options.
7. Clearly explain tradeoffs and consequences.
8. Do not treat silence, partial agreement, or topic changes as approval.
9. Only begin coding after the user explicitly approves the technical solution.
10. If the user changes a confirmed requirement, update the solution before coding.

---

# Trigger Conditions

Use this skill when the user asks for any of the following:

- Design a system or service
- Build an application or platform
- Create an Agent, MCP service, backend, frontend, or data pipeline
- Produce a technical architecture
- Plan a refactor or migration
- Choose a technology stack
- Design authentication, authorization, data models, workflows, or deployment
- Implement a feature whose requirements or architecture are not yet settled

Do not use this workflow for:

- Small isolated code fixes with fully specified requirements
- Simple syntax questions
- Pure explanations with no implementation intent
- Minor text or configuration edits

---

# Workflow Overview

```text
User idea
   ↓
Stage 1: Requirement discovery
   ↓
Requirement summary and confirmation
   ↓
Stage 2: Technical solution draft
   ↓
Architecture review and decision confirmation
   ↓
Explicit solution approval
   ↓
Stage 3: Implementation plan
   ↓
Coding and verification
```

---

# Stage 1: Requirement Discovery

## Goal

Reach a level of clarity where scope, users, workflows, constraints, security, and acceptance criteria are sufficiently defined to make architecture decisions.

## First Response

Start by:

1. Briefly restating the user's goal.
2. Identifying the most important unknowns.
3. Asking a compact group of high-impact questions.
4. Offering recommended defaults when helpful.

Avoid asking one question per message unless the user explicitly prefers that style.

## Requirement Dimensions

Cover only the dimensions relevant to the project.

### Product Scope

- What problem does the product solve?
- Who will use it?
- Is it personal, internal, or public?
- What is required for MVP?
- What is explicitly out of scope?
- What should be reserved for future versions?

### Functional Requirements

- What are the primary user workflows?
- What data enters the system?
- What output is expected?
- Are there scheduled, manual, or event-driven workflows?
- What notifications or exports are needed?
- Are external integrations required?

### Non-Functional Requirements

- Expected users and traffic
- Latency and availability expectations
- Data volume and retention
- Security and privacy sensitivity
- Compliance or audit needs
- Cost constraints
- Deployment environment
- Maintainability expectations

### Data and Integration

- Source systems
- APIs, MCP servers, databases, files, or event streams
- Authentication method
- Rate limits and data freshness
- Whether interfaces are official, stable, or need validation
- Failure and fallback expectations

### AI and Agent Requirements

- Which decisions require LLM reasoning?
- Which calculations must be deterministic?
- Which tools may the Agent call?
- Which tools must never be exposed to the Agent?
- Is structured output required?
- Is human approval required?
- Are actions read-only or write-capable?
- How should hallucinations be detected?

### Security

- Login method
- Authorization model
- Credential storage
- Encryption requirements
- Audit logging
- Public network exposure
- Administrative access
- Two-factor authentication
- Sensitive data boundaries

### Delivery

- Programming language and framework constraints
- Existing infrastructure
- Local, VPS, cloud, or hybrid deployment
- Budget
- Development phases
- Testing and acceptance criteria

---

# Questioning Rules

## Ask High-Impact Questions First

Prioritize decisions that can materially change the design:

1. User scale and product scope
2. Read-only versus write or transaction capability
3. Data source availability
4. Deployment constraints
5. Security requirements
6. Real-time versus scheduled processing
7. Cost constraints
8. Technology restrictions

## Batch Questions

Prefer 3–6 related questions per round.

Bad pattern:

```text
Do you need login?
Do you need 2FA?
Do you need email?
Do you need PDF?
...
```

Better pattern:

```text
Before selecting the architecture, confirm:
1. Is this personal or multi-user?
2. Is the first version read-only?
3. Where will it run?
4. What login security is required?
5. Which output channels are needed?

Recommended defaults: personal, read-only, VPS, password + TOTP, Web + Email.
```

## Stop Questioning at the Right Time

Do not keep expanding the questionnaire after the architecture can be designed.

Move to the technical solution once these are clear:

- Users
- Core workflows
- Data sources
- Read/write boundaries
- Security level
- Deployment environment
- Key outputs
- MVP scope
- Major constraints

Minor preferences can be listed as defaults or follow-up optimizations.

---

# Requirement Decision Log

Maintain a compact decision log while discussing requirements.

Example:

```markdown
## Confirmed Requirements

- Usage: Personal, single user
- Assets: All account assets
- Reports: Premarket and postmarket
- Delivery: Web + Email
- Authentication: Email + password + TOTP
- Deployment: Local development, then one VPS
- Trading: Read-only MVP; human-approved trading reserved
- Data budget: Free sources first
```

Separate confirmed decisions from assumptions.

Use these labels:

- **Confirmed**
- **Recommended default**
- **Open**
- **Future optimization**

---

# Requirement Confirmation Gate

Before drafting the final technical solution, present a concise requirement summary.

Use language similar to:

```text
The core requirements are now sufficiently clear. I will use the following confirmed scope as the basis for the technical solution:
...
```

If a material requirement is still open, resolve it before finalizing the solution.

---

# Stage 2: Technical Solution

## Goal

Produce an implementable, reviewable technical solution that connects every major architecture decision to a confirmed requirement.

## Required Sections

Include the sections relevant to the project.

### 1. Project Goals and Scope

- Problem statement
- Target users
- MVP goals
- Non-goals
- Future extensions

### 2. Confirmed Requirements

Summarize product, functional, security, deployment, data, and operational decisions.

### 3. Architecture Overview

Include:

- System context
- Major components
- Main data flow
- External dependencies
- Trust boundaries

Use a text diagram when useful.

### 4. Technology Stack

For each major choice, provide:

- Selected technology
- Why it fits
- Rejected alternatives when relevant
- Constraints or risks

Do not select technologies only because they are popular.

### 5. Module Design

Define clear responsibilities and boundaries for:

- API
- Authentication
- Domain services
- Integration adapters
- Agent or workflow
- Analysis engine
- Reporting
- Storage
- Scheduling
- Notifications
- Observability

### 6. Agent Architecture

When AI is involved, explicitly separate:

#### Deterministic code

Use for:

- Financial or business calculations
- Permissions
- Validation
- State transitions
- Database writes
- Scheduling
- Idempotency
- Risk limits

#### Agent or LLM

Use for:

- Summarization
- Explanation
- Classification
- Evidence-based recommendations
- Natural-language report generation

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

### 7. Data Model

Specify:

- Core entities
- Important relationships
- Ownership and tenant keys
- Snapshots and history
- Audit records
- Job records
- Version fields
- Retention policy

### 8. API and Integration Design

Define:

- External connectors
- Internal interfaces
- Authentication
- Timeouts
- Rate limits
- Retry policy
- Idempotency
- Error normalization
- Schema validation

Use adapter or provider interfaces around unstable external systems.

### 9. Security Design

Include:

- Authentication
- Authorization
- Credential encryption
- Secret management
- Network exposure
- Audit logging
- Rate limiting
- Sensitive-data redaction
- LLM data boundaries
- Backup protection

### 10. Scheduling and Workflow

Define:

- Trigger types
- Workflow steps
- Job state machine
- Retry rules
- Timeouts
- Concurrency
- Idempotency key
- Recovery process

### 11. Failure and Degradation

For every critical dependency, specify:

- What happens if it fails
- Whether cached data may be used
- How stale data is labeled
- Whether the workflow continues
- Whether an alert is sent

Never allow stale data to appear current without labeling.

### 12. Deployment

Cover:

- Runtime topology
- Container layout
- Server requirements
- Ports
- TLS
- Database exposure
- Backup
- Logging
- Upgrade process

Choose the simplest architecture that meets current scale.

### 13. Observability

Define:

- Logs
- Metrics
- Traces where necessary
- Health checks
- Alerts
- Audit events
- Cost metrics for LLM systems

### 14. Testing Strategy

Include:

- Unit tests
- Integration tests
- Contract tests
- Mock external providers
- Workflow tests
- Security tests
- Structured-output validation
- Failure and retry tests
- Acceptance tests

### 15. Implementation Phases

Break delivery into reviewable phases:

```text
Phase 0: Technical feasibility
Phase 1: Core data and authentication
Phase 2: Deterministic domain logic
Phase 3: Agent and report generation
Phase 4: Deployment and reliability
Phase 5: Future enhancements
```

Each phase should have explicit acceptance criteria.

### 16. Risks and Open Questions

List:

- External API uncertainty
- Data quality limitations
- Security risks
- Operational single points of failure
- Cost risks
- Technical debt intentionally deferred

### 17. Architecture Decision Summary

End with a concise list of final decisions.

---

# Architecture Review Process

After presenting the technical solution:

1. Ask the user to review the architecture, not the code.
2. Resolve architecture questions in grouped rounds.
3. Update the decision log.
4. Produce a revised version when material decisions change.
5. Mark postponed items as future optimizations.
6. Do not start coding during architecture review.

Use version names:

- Technical Solution V1
- Technical Solution V2
- Technical Solution V3

A version should change when scope, architecture, data model, security, or deployment decisions materially change.

---

# Technical Solution Approval Gate

Coding is blocked until the user explicitly approves the solution.

Valid approval examples:

- “技术方案没问题，可以开始”
- “V2 确认，开始编码”
- “Approved”
- “按这个方案实现”

Not valid approval:

- “看起来不错”
- “继续”
- Answering one architecture question
- Requesting another diagram
- Asking what to do next

When approval is ambiguous, ask for explicit approval.

Use:

```text
技术方案已经完成评审。请明确确认“按当前方案开始编码”，我再进入实现阶段。
```

---

# Stage 3: Implementation Planning

After explicit approval, do not immediately write large amounts of code.

First produce an implementation plan containing:

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

For large projects, use:

```text
Explore → Plan → Implement → Verify
```

## Explore

- Inspect existing repository
- Read relevant documentation
- Identify current architecture
- Do not modify code

## Plan

- List exact files and modules to add or change
- Explain migration and compatibility strategy
- Define tests and rollback
- Obtain review when appropriate

## Implement

- Make focused changes
- Avoid unrelated refactoring
- Preserve agreed architecture
- Record deviations

## Verify

- Run formatting
- Run unit and integration tests
- Run static checks
- Validate migrations
- Test failure paths
- Confirm acceptance criteria

---

# Coding Rules

1. Never implement unapproved features.
2. Never expose write-capable tools that were approved as read-only.
3. Keep external integrations behind interfaces.
4. Validate all external responses.
5. Use deterministic code for critical calculations.
6. Require schemas for LLM outputs.
7. Keep prompts versioned.
8. Store workflow and model versions with generated outputs.
9. Add idempotency to scheduled and retried operations.
10. Add tests with each implementation phase.
11. Document any deviation from the approved solution.
12. If implementation reveals a flawed architecture assumption, pause coding and return to architecture review.

---

# Handling Requirement Changes During Coding

When the user changes a requirement after implementation starts:

1. Identify impacted modules.
2. Explain whether the change is local or architectural.
3. Update the technical solution if architecture is affected.
4. Obtain approval for the revised solution.
5. Resume coding only after approval.

Do not silently absorb major scope changes.

---

# Response Templates

## Initial Clarification

```markdown
我理解你的目标是：<goal>。

在确定技术架构前，需要先确认几项会直接影响方案的内容：

1. <question>
2. <question>
3. <question>

我的推荐默认值是：<defaults>。
```

## Requirement Summary

```markdown
## 已确认需求

- ...
- ...

## 后续优化

- ...

## 尚待确认

- ...
```

## Architecture Recommendation

```markdown
基于已确认需求，我建议采用：

> <architecture summary>

主要原因：
- ...
- ...
```

## Approval Request

```markdown
当前技术方案已经完成评审。

请明确回复：

> 按当前技术方案开始编码

收到明确确认后，我会先输出实施计划，再进入代码实现。
```

## Architecture Change During Coding

```markdown
这个新需求会影响已确认的 <module/architecture>。

需要先更新技术方案中的：
- ...
- ...

我会先生成修订版方案，确认后再继续编码。
```

---

# Quality Checklist

Before presenting a technical solution, verify:

- [ ] Core users and workflows are clear
- [ ] MVP and non-goals are explicit
- [ ] External integrations are validated or marked for feasibility testing
- [ ] Read/write boundaries are explicit
- [ ] Security is proportional to data sensitivity
- [ ] Agent and deterministic responsibilities are separated
- [ ] Tool whitelist and forbidden actions are explicit
- [ ] Data model supports ownership and history
- [ ] Retry and idempotency are defined
- [ ] Failure degradation is defined
- [ ] Deployment matches actual infrastructure
- [ ] Backup and recovery are covered
- [ ] Testing and acceptance criteria exist
- [ ] Future optimizations are separated from MVP
- [ ] Coding approval gate is stated

Before coding, verify:

- [ ] The user explicitly approved the current solution version
- [ ] No material requirement remains open
- [ ] Implementation plan exists
- [ ] Required external interfaces have been validated or mocked
- [ ] Repository and deployment constraints are understood

---

# Expected Outcome

A successful use of this skill produces:

1. A confirmed requirement decision log.
2. A versioned technical solution.
3. Explicit user approval.
4. A detailed implementation plan.
5. Code only after approval.
6. Verification results against acceptance criteria.
