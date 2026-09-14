# Requirement Dimensions

Question bank for Stage 1. Cover only the dimensions relevant to the project.
Pull 3–6 high-impact questions per round from here — do not ask everything.

## Product Scope

- What problem does the product solve?
- Who will use it?
- Is it personal, internal, or public?
- What is required for MVP?
- What is explicitly out of scope?
- What should be reserved for future versions?

## Functional Requirements

- What are the primary user workflows?
- What data enters the system?
- What output is expected?
- Are there scheduled, manual, or event-driven workflows?
- What notifications or exports are needed?
- Are external integrations required?

## Non-Functional Requirements

- Expected users and traffic
- Latency and availability expectations
- Data volume and retention
- Security and privacy sensitivity
- Compliance or audit needs
- Cost constraints
- Deployment environment
- Maintainability expectations

## Data and Integration

- Source systems
- APIs, MCP servers, databases, files, or event streams
- Authentication method
- Rate limits and data freshness
- Whether interfaces are official, stable, or need validation
- Failure and fallback expectations

## AI and Agent Requirements

- Which decisions require LLM reasoning?
- Which calculations must be deterministic?
- Which tools may the Agent call?
- Which tools must never be exposed to the Agent?
- Is structured output required?
- Is human approval required?
- Are actions read-only or write-capable?
- How should hallucinations be detected?

## Security

- Login method
- Authorization model
- Credential storage
- Encryption requirements
- Audit logging
- Public network exposure
- Administrative access
- Two-factor authentication
- Sensitive data boundaries

## Delivery

- Programming language and framework constraints
- Existing infrastructure
- Local, VPS, cloud, or hybrid deployment
- Budget
- Development phases
- Testing and acceptance criteria

## High-Impact Ordering

Ask these first — they can materially change the design:

1. User scale and product scope
2. Read-only versus write or transaction capability
3. Data source availability
4. Deployment constraints
5. Security requirements
6. Real-time versus scheduled processing
7. Cost constraints
8. Technology restrictions
