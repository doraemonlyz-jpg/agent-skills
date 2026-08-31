# Work Package Handoff

## Result

- Work Package: `<Mx-yy>`
- Status: `DONE | FAILED | BLOCKED | ARCH_REVIEW`
- Summary: `<one paragraph>`

## Baseline continuity

- Context load: `FULL | SAME-WP-RESUME`
- Initial full read completed for this Work Package: `YES | NO`
- Baseline SHA-256: `<64 lowercase hex or N/A>`
- Resume source: `<handoff path or none>`

The digest records covered repository bytes only. It does not replace
approval, preflight, content review, or a full read for a different Work
Package.

## Changed files

- `<absolute or repository-relative path>` — `<purpose>`

## Acceptance evidence

- `<requirement or acceptance ID>` — `<evidence>`

## Verification

| Command/check | Result | Notes |
|---|---|---|
| `<literal command>` | `PASS/FAIL/NOT RUN` | `<detail>` |

## Security and architecture

- Read-only/trading boundary: `<result>`
- Financial precision: `<result>`
- Ownership and secrets: `<result>`
- Architecture drift: `<none or explanation>`

## Limitations and follow-up

- `<known limitation>`
- Next dependency: `<task ID and readiness>`
