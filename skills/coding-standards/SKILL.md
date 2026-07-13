---
name: coding-standards
description: Enforce shared coding quality, security, testing, and verification standards for implementation work. Use whenever writing, reviewing, refactoring, or debugging code.
metadata:
  short-description: Apply coding standards and verify changes
---

# Coding Standards Skill

## Purpose

Ensure all code is concise, readable, robust, secure, testable, and consistent with the approved architecture.

## Required Inputs

Before coding, read:

1. Repository `AGENTS.md`
2. Project architecture
3. Project coding standards
4. Security requirements
5. Testing requirements

## Preconditions

Do not begin implementation unless:

- Requirements are clear.
- The current technical solution is explicitly approved.
- No material architecture question remains open.
- The implementation scope is understood.

If any precondition fails, return to requirement or architecture review.

## Implementation Rules

- Keep code concise and readable.
- Avoid overengineering and premature abstraction.
- Use clear business-oriented names.
- Add comments only where they explain public contracts, complex logic, business rules, edge cases, security constraints, or non-obvious decisions.
- Do not add line-by-line comments for obvious code.
- Handle every error.
- Add contextual error wrapping.
- Use context and explicit timeouts for external operations.
- Keep concurrency bounded.
- Do not use floating-point types for financial values.
- Keep external systems behind interfaces.
- Validate external responses.
- Use structured schemas for LLM outputs.
- Never expose secrets or sensitive data.
- Preserve the approved architecture.

## Workflow

```text
Read project rules
→ Inspect existing code
→ Plan the change
→ Implement focused changes
→ Format
→ Run static checks
→ Run tests
→ Review security and logging
→ Report results
```

## Review Checklist

### Readability

- Is the code easy to understand?
- Are names precise?
- Is the control flow simple?
- Is abstraction justified?

### Comments

- Do comments explain why?
- Are public declarations documented?
- Are obvious comments removed?

### Robustness

- Are errors handled?
- Are timeouts defined?
- Are retries limited to recoverable failures?
- Are edge cases tested?

### Performance

- Is concurrency bounded?
- Are N+1 queries avoided?
- Are batch operations used where appropriate?
- Is optimization supported by evidence?

### Security

- Are secrets excluded from logs and prompts?
- Is ownership enforced?
- Are external inputs validated?
- Are forbidden tools excluded?

### Testing

- Are core paths tested?
- Are failure paths tested?
- Are financial calculations tested precisely?
- Does concurrent code pass the race detector?

## Architecture Drift

If implementation requires changing:

- Service boundaries
- Data model ownership
- Security boundaries
- External interfaces
- Read/write capability
- Agent permissions
- Deployment topology

stop implementation, update the technical solution, and request explicit approval before continuing.

## Completion Report

Always report:

- Files changed
- Important design choices
- Tests and checks run
- Results
- Known limitations
- Any deviation from the approved plan
