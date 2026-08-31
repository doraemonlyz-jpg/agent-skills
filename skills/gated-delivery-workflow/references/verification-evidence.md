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

## Manual evidence

Record time, environment, version, sanitized evidence location, result, and reviewer. Never store secrets or personal data in evidence artifacts.
