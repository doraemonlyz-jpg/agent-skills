# Milestone File Format

One file per milestone at the path mapped in `delivery.milestone_files`
(default `docs/tasks/M<n>.md`). Plain Markdown that people,
`gated-delivery-workflow`, and `scripts/check_delivery_plan.py` all read.
`gated-delivery-workflow` reads Status, Depends on, How to check, and Evidence.
Open blocking decisions live in the plan index (`docs/tasks/README.md`), never
inside a Work Package.

Each Work Package is written for two readers. The title, Goal, and Why tell a
person in under a minute what changes and why, in everyday words. The fields
after them give a fresh agent everything it needs without re-deciding
anything.

## Milestone header

```markdown
# M1 — Keep a reliable copy of broker positions

- Milestone: M1
- Phase: phase1
- Goal: Positions are fetched on schedule and stored once per snapshot.
- Entry criteria: M0 DONE; EXT: broker sandbox credentials
- Exit criteria: A scheduled run stores today's snapshot and the report reads it.
- Checkpoint: explicit approval before start — first external integration
```

`Milestone` must equal the key in `delivery.milestone_files` and must not
contain a hyphen.

## Work Package block

```markdown
## M1-2 — Store each broker snapshot once

- Status: BLOCKED
- Depends on: M1-1, EXT: broker sandbox credentials
- Goal: Fetched positions are lost when the process restarts. After this package they are saved, and fetching the same snapshot twice stores it once.
- Why: Reports can be rebuilt from saved data without calling the broker again.
- Acceptance criteria:
  - Fetching the same snapshot twice leaves one stored copy.
  - After a restart, the last saved positions are still available.
  - The storage change applies and rolls back cleanly on an empty database.
  - Amounts are stored as exact decimals, never floating point (INV-3).
- How to check:
  - `go test ./internal/store/...`
  - `make migrate-roundtrip`
  - manual: restart the service; the positions page still shows the last snapshot.
- Required tests: unit, integration (database)
- Scope: storage layer and its migration; no API change.
- Solution refs: docs/solution.md — Technical Solution V2 §4.2, §6.1
- Agent notes:
  - Owns the `positions` table contract; M1-3 and M2-1 depend on it.
  - A duplicate snapshot keeps the first copy and logs at info level.
  - Credentials and account numbers never reach logs or fixtures.
- Non-goals:
  - Historical backfill (M3-1).
  - Serving positions through the API (M1-3).
- Evidence: —
```

## Field rules

| Field | Rule |
|---|---|
| Heading | `## <ID> — <plain action and result>`; ID matches `delivery.task_id_pattern`; text before the first hyphen equals the milestone |
| Status | One of `BLOCKED`, `READY`, `IN_PROGRESS`, `VERIFYING`, `DONE`, `FAILED`, `ARCH_REVIEW`, `DROPPED`. Anything after the word is a free note, e.g. `DROPPED — out of scope in V3` |
| Depends on | `none`, or comma-separated items: package IDs, `EXT: <text>`, and `DECISION: <id>`. Package IDs must exist and be in the same or an earlier milestone; decision IDs must exist in the plan index's Blocking Decisions table |
| Goal | Required. One to three short sentences in everyday words: what is wrong or missing, and what works after. No requirement IDs, undefined terms, or implementation detail |
| Why | Required. One or two sentences: the practical value to a user, operator, or developer |
| Acceptance criteria | Required. Three to seven `  - ` items, each an observable result or checkable rule. Requirement IDs go here or in Agent notes |
| How to check | Required. `  - ` items: exact commands in backticks, or `manual: <what to do and see>` |
| Required tests | Required. Test layers from verification-evidence.md |
| Scope | Required. The boundary: components or areas this package may change. Not a file list; the executor picks files when it plans the package |
| Solution refs | Required. Path plus the pinned version and sections, e.g. `Technical Solution V2 §4.2` |
| Agent notes | Optional `  - ` items: fixed decisions, contracts this package owns, failure behavior, security constraints specific to this package. Link the source instead of copying it |
| Non-goals | Required. `  - ` items naming adjacent work this package is likely to absorb by mistake, with the package that owns it if planned. `none` is allowed but deliberate |
| Evidence | `—` until DONE; then the handoff path, e.g. `docs/tasks/handoffs/M1-2.md` |
| Superseded by | Optional; only on DROPPED packages replaced in a Replan |

Writing rules:

- No open decisions: TBD, TODO, 待定, or "decide during implementation" fail the
  checker. Unresolved choices go back to `technical-solution-workflow`.
- No unfilled `<placeholders>` from the template.
- Say each fact once. Aim for 250–500 words per package; the checker warns past
  700 (Chinese text counts two characters as one word).
- No slogans or vague claims such as "robust", "seamless", "comprehensive".

## Packages blocked by a decision

A package that depends on an open decision stays `BLOCKED` and may be partial.

```markdown
## M2-3 — Tell operators when a snapshot is rejected

- Status: BLOCKED
- Depends on: M2-1, DECISION: D4
- Goal: A snapshot that fails validation is dropped silently today. After this package operators learn about every rejection.
- Why: Operators can see why a report has no fresh data.
- Scope: snapshot validation and the rejection notice.
- Solution refs: docs/solution.md — Technical Solution V2 §5.3
- Agent notes:
  - The rejection reason codes are fixed by V2 §5.3; how the notice reaches operators is D4.
- Evidence: —
```

- Required while blocked: Status, Depends on, Goal, Why, Scope, Solution refs.
- Acceptance criteria, How to check, Required tests, and Non-goals may be left
  out until the decision is resolved; write only what is already decided.
- Refer to the decision by ID. TBD, 待定, and similar markers still fail.
- Only a Replan removes a `DECISION:` dependency, after the decision is marked
  `RESOLVED` in the index. The executor never treats it as satisfied.

## Status ownership

- The planner sets `BLOCKED`, `READY` (on authorization), and `DROPPED`.
- The executor may flip `BLOCKED` to `READY` once every package dependency is
  `DONE` and the milestone is authorized. `EXT:` and `DECISION:` dependencies
  are never satisfied by the executor.
- The executor (`gated-delivery-workflow`) moves packages through
  `IN_PROGRESS`, `VERIFYING`, `DONE`, `FAILED`, `ARCH_REVIEW`, writes the
  handoff, and fills `Evidence`.
- `DONE` without an existing Evidence file fails the checker.
