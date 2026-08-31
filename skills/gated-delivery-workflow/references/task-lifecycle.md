# Task Lifecycle

## Select

1. Prefer an explicit task ID.
2. Confirm its milestone is authorized.
3. Read the mapped milestone file.
4. Confirm listed dependencies have completion evidence.
5. Select one task and declare adjacent tasks out of scope.

## Resume

Inspect working-tree changes, prior test output, completion evidence, and external state. Continue verified progress; do not restart or overwrite completed work.

## Parallel work

Parallelize only when explicitly requested and tasks do not share files, migrations, APIs, state machines, external rate limits, or prerequisite order. Each task still needs its own verification and handoff.

## Gate outcomes

- Missing dependency: `BLOCKED`.
- Failed required test: `FAILED`.
- Material solution change: `ARCH_REVIEW`.
- Successful implementation without all evidence: `VERIFYING`, not DONE.

Dates and schedule pressure never authorize a task.
