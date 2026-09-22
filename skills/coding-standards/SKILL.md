---
name: coding-standards
description: Enforce shared coding standards for implementation work — minimum code that solves the task, surgical changes, the project's own style, sound error handling and security, test-first for bug fixes and deterministic logic, and verified results. Use whenever writing, reviewing, refactoring, or debugging code.
metadata:
  version: 1.1.0
  short-description: Minimal, surgical, project-style code, verified
---

# Coding Standards Skill

## Purpose

Write the least code that correctly does what was asked, in the project's own
style, change nothing the task does not need, and prove it works.

## Required Inputs

Before coding, read:

1. Repository `AGENTS.md`
2. Project architecture
3. Project coding standards, formatter, and linter configuration
4. Security requirements
5. Testing requirements

Project rules override this skill where they are more specific.

## Preconditions

Do not begin implementation unless:

- Requirements are clear.
- The current technical solution is explicitly approved.
- No material architecture question remains open.
- The implementation scope is understood.

State the assumptions the change relies on. If a request has more than one
reasonable reading, or something does not make sense, stop and ask. Do not
pick an interpretation silently.

If any precondition fails, return to requirement or architecture review.

## Simplicity First

Before writing new code, go down this ladder and stop at the first rung that
works:

1. Does it need to exist at all? If nobody asked for it, do not build it.
2. Does the codebase already do it? Reuse it.
3. Does the standard library do it?
4. Does the platform or framework already provide it?
5. Does a dependency the project already has do it? A new dependency needs a
   reason in the report.
6. Only then, write the minimum code that does it.

Minimalism never removes validation, error handling, security checks,
accessibility, or the tests the Test-First Rule requires.

Write the minimum code that solves the stated problem. Nothing speculative:

- No features, options, parameters, flags, or configuration nobody asked for.
- No abstraction with a single use — an interface with one implementation, a
  factory for one type, a wrapper that only forwards — unless the approved
  architecture or a rule below requires it (external systems stay behind
  interfaces).
- No handling for states the code's own invariants rule out. Validate at
  boundaries instead.

Minimal means the least scope, not the fewest characters. Choose clarity over
brevity: no clever one-liners, nested ternaries, or dense expressions; an
explicit `if`/`else` or `switch` beats a compact trick.

Self-check before finishing: would a senior engineer reviewing the diff call it
overcomplicated? Could it be much smaller with the same behavior? If so, cut.

## Surgical Changes

- Every changed line traces to the task.
- Match the surrounding code's style and patterns, even where you would write
  it differently.
- Do not refactor, rename, or reformat working code outside the task. Mention
  it in the report instead.
- Clean up only your own mess: remove imports, variables, functions, and files
  that your change made unused. Report pre-existing dead code; do not delete it.
- Preserve public interfaces, data shapes, error types, and user-visible
  behavior unless the task changes them.
- When the task needs a refactor, do it as a separate step before the behavior
  change, with tests green before and after. If the behavior it touches has no
  tests, first add tests against the unchanged code.

## Style and Formatting

- The project's formatter and linter configuration is the source of truth. Run
  them on changed files. Do not hand-format against them, and do not disable a
  lint rule to pass unless the project allows it — then say why at that line.
- Without project configuration, use the language's standard tooling and
  conventions (for example gofmt/goimports, ruff, prettier) and follow the
  surrounding file.
- Formatting-only changes to code the task does not touch go in their own
  commit, never mixed into a behavior change.
- Names follow the language's conventions and the project's domain vocabulary.
  One concept, one name.
- Add comments only where they explain public contracts, complex logic,
  business rules, edge cases, security constraints, or non-obvious decisions.
  No line-by-line comments for obvious code.

## Engineering Rules

- Handle every error that can occur: return it or wrap it with context. Never
  swallow it.
- Set explicit timeouts and cancellation for external operations (in Go, a
  `context`).
- Keep concurrency bounded.
- Use exact decimal types for money and any value that needs exact
  arithmetic, never binary floating point.
- Keep external systems behind interfaces.
- Validate external input and external responses.
- Use structured schemas for LLM output the code consumes.
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
→ State assumptions and the checks that prove success
→ Write the failing test (bug fix or deterministic logic) and see it fail
→ Implement the minimum change
→ Format and lint changed files
→ Run static checks
→ Run tests
→ Review the diff: every line traces to the task; nothing speculative
→ Review security and logging
→ Report results
```

## Review Checklist

### Simplicity and Scope

- Does every changed line trace to the task?
- Is anything speculative: unrequested options, single-use abstractions,
  handling for impossible states?
- Could the change be much smaller with the same behavior?
- Was existing code, the standard library, or an installed dependency used
  before writing new code? Is every new dependency justified?
- Is anything compact at the cost of clarity?
- Were unrelated code, names, and formatting left alone?
- Was only code orphaned by this change removed?

### Readability

- Is the code easy to understand?
- Are names precise and consistent with the project's vocabulary?
- Is the control flow simple?
- Does the code match the surrounding style and the project formatter?

### Comments

- Do comments explain why?
- Are public declarations documented?
- Are obvious comments removed?

### Robustness

- Are errors handled and wrapped with context?
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
- Are agent tools limited to the project's allowlist, where it has one?

### Testing

- Did each bug fix start with a test that reproduced the bug?
- Was deterministic logic written test-first, with the failing run recorded?
- Were any failing tests weakened, skipped, or deleted?
- Are core paths tested?
- Are failure paths tested?
- Are exact-arithmetic values (money, quantities) tested precisely?
- Does concurrent code pass the language's race checks (for example `go test -race`)?

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
- Assumptions made
- Important design choices, and any new dependency with its reason
- Tests and checks run
- Test-first evidence (failing before, passing after), or why it did not apply
- Results
- Issues noticed outside the task and left unchanged
- Known limitations
- Any deviation from the approved plan
