# Verification Evidence

## Choose layers by risk

| Change | Typical minimum evidence |
|---|---|
| Pure logic | Unit and boundary tests |
| Persistence or migration | Database integration and constraints |
| External integration | Contract tests and approved real evidence |
| Retry, job, or state machine | Workflow, idempotency, recovery |
| Auth, ownership, or secrets | Security negative tests |
| User workflow | End-to-end tests |
| Generated artifact | Golden/snapshot plus visual review when applicable |
| Performance or concurrency | Benchmark/load evidence and race checks |
| Backup or disaster recovery | Real isolated restore drill |

## Report results accurately

For each command or check, report one of:

- `PASS`
- `FAIL`
- `NOT CONFIGURED`
- `NOT INSTALLED`
- `NOT APPLICABLE`
- `BLOCKED BY EXTERNAL DEPENDENCY`

Include the literal command, exit status, and meaningful output. Do not summarize unrun checks as verified.

## Test-first evidence

Bug fixes and deterministic logic are written test-first (see the Test-First
Rule in `coding-standards`). For each such test, record:

- The test name.
- The failing run before the implementation: the command and the one-line
  failure. For a bug fix, the failure must come from the bug, not from a
  compile error, a missing import, or setup.
- The passing run after.

If an in-scope change was not done test-first, say why. Never present a test
that was written after the implementation, or that never failed, as
test-first.

## Manual evidence

Record time, environment, version, sanitized evidence location, result, and reviewer. Never store secrets or personal data in evidence artifacts.
