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

## Test-First Rule

Write the test before the code where it pays most. Elsewhere, tests come with
the implementation.

**Test first (required):**

- **Bug fix.** First write a test that reproduces the reported bug and fails
  because of it. Then fix.
- **Deterministic logic.** Calculations (money, quantities, precision),
  parsing and validation, state transitions, permission and ownership checks,
  idempotency and retry rules, scheduling rules. Turn the acceptance criterion
  into a failing test, then implement.

**Tests with or after the implementation:**

- UI and visual layout: automated checks where practical, plus visual or
  browser verification.
- Throwaway spikes: no tests; a spike's code is not kept.
- External integrations whose behavior is learned by calling them: contract
  tests after the first real call; real evidence is still required.
- Configuration, glue, and scaffolding without logic: the command that proves
  it works.
- Pure refactoring: run the existing tests green before changing code, and
  keep them green without editing them.

**Rules:**

1. Run the new test and see it fail for the expected reason before writing
   the implementation. A test that already passes, or fails for another reason
   such as a compile error or a missing import, is not a failing test.
2. Make the smallest change that passes it, then refactor with tests green.
3. Never weaken, skip, or delete a failing test to get green. If the test is
   wrong, say so and change it in the open.
4. Record the evidence: test name, the one-line failure before, and the pass
   after. If an in-scope change was not done test-first, say why.

## Workflow

```text
Read project rules
→ Inspect existing code
→ Plan the change
→ Write the failing test (bug fix or deterministic logic) and see it fail
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

- Did each bug fix start with a test that reproduced the bug?
- Was deterministic logic written test-first, with the failing run recorded?
- Were any failing tests weakened, skipped, or deleted?
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
- Test-first evidence (failing before, passing after), or why it did not apply
- Results
- Known limitations
- Any deviation from the approved plan
