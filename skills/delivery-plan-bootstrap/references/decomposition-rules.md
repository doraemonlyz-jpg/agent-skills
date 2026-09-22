# Decomposition Rules

How to cut an approved solution into phases, milestones, and Work Packages that
`gated-delivery-workflow` can execute one per turn. A good Work Package lets a
fresh agent finish it without making a product or technical decision.

## Decisions stay out of Work Packages

Before writing a package, check whether its implementer would have to choose
anything that changes behavior, interfaces, data, security, scale,
performance, compatibility, operations, cost, or proof.

- If yes, it is a **blocking decision**. List it in the Gate B draft and return
  to `technical-solution-workflow`. Never hide it inside a package as "decide
  during implementation", TBD, or 待定.
- Decisions the approved solution already fixed go into the package's Agent
  notes, with the pinned source.
- Interchangeable local mechanics (helper names, file layout inside the agreed
  boundary) are left to the implementer.

## Split by working result

A Work Package delivers one working result: behavior a person can observe or a
check can prove.

- Do not split one working behavior into file or technical-layer packages
  ("create table", then "write service", then "wire API").
- Size: one agent run and one focused review — roughly ≤ 1 working day, a
  reviewable diff, and 250–500 words of package text. Past 700 words, split the
  package or link the shared source instead of copying it.
- Leaves the system building and existing tests passing.
- Has acceptance criteria that can be checked without later packages.
- Can be described in one sentence without "and also".

Split when any rule fails. Merge when a package has no acceptance criterion of
its own.

## Shared contracts and refactoring

- **One owner per shared contract.** A schema, API, event format, or file format
  used by several packages is defined by exactly one package; the others depend
  on it. Two packages never answer the same question independently.
- A migration gets its own package only when several packages depend on it or
  it runs on real data. Otherwise it belongs to the package whose behavior
  needs it.
- **Separate refactoring** into its own package when mixing it in would hide a
  behavior change from review.
- No scaffolding or cleanup package without a checked outcome. "Set up the
  project" is not done until a command proves it.

## Ordering

1. **M0 foundation first.** Repository skeleton, build, lint, test commands, CI,
   baseline checks — each with a command that proves it. After M0 every
   `verification.commands` entry must run.
2. **Contract owners before consumers.**
3. **Vertical slices over layers.** After the foundation, prefer a thin
   end-to-end flow over completing one layer at a time.
4. **Risk early.** Put the riskiest integration or unproven assumption in the
   earliest milestone that can hold it.
5. **Read before write.** When the solution has read and write capabilities,
   deliver and verify read first; write-capable packages get a checkpoint.

## Dependencies

- List only real prerequisites: a contract, schema, state, or order another
  package owns.
- A package never depends on a later milestone.
- The graph is acyclic.
- External prerequisites (credentials, accounts, vendor approval, hardware) use
  `EXT: <description>` and are listed in the plan index. They are never mocked
  away to make a package look READY.

## Milestones and phases

- A milestone boundary is where the user would want to stop, look at the
  result, and decide whether to authorize the next step. Do not add a milestone
  only to group packages.
- A milestone is a demonstrable increment with entry and exit criteria a user
  can check. 3–8 packages is typical; one package is a smell; more than ten
  usually hides two milestones.
- A phase groups milestones behind one gate: foundation, core flow, hardening,
  release. `current_phase` in the adapter names the phase in progress.

## Checkpoints

Mark a milestone `Checkpoint: explicit approval before start` when it:

- Introduces write capability, money movement, or destructive operations.
- Runs a data migration on real data.
- Opens a new trust boundary or external integration.
- Deploys to a shared or production environment.
- Follows a milestone whose outcome may change the plan (spike results, load tests).

Copy each checkpoint into `delivery.checkpoint_rules`.

## Proof

- **Acceptance criteria**: three to seven observable results. Write the
  behavior, not the property: "sending the same event twice creates one reply",
  not "ensure idempotency". An internal rule that must hold is stated as a
  checkable rule.
- **How to check**: exact commands, plus `manual:` steps when automation
  cannot cover the behavior. External systems need real evidence, never a mock
  in place of it.
- **Required tests**: layers from
  `gated-delivery-workflow/references/verification-evidence.md`.

## Hard rules and architecture change triggers

Hard rules are the constraints a single package must never break. Derive them
from, and cite:

- Solution non-goals and read/write boundaries.
- `docs/SECURITY.md` allowlists and data boundaries.
- `AGENTS.md` repository hard rules.

Architecture change triggers are boundaries whose change forces `ARCH_REVIEW`.
Typical sources in the solution: service boundaries, data ownership, core data
model, trust boundaries, external dependencies, deployment topology,
deterministic vs Agent responsibilities, and read/write capability.

## Traceability

Maintain a matrix in the plan index:

| Solution section | Requirement IDs | Work Packages | Notes |
|---|---|---|---|

- Every in-scope section has at least one package.
- Keep each requirement ID (`AC-n`, `INV-n`, …) attached to the same rule. Do
  not renumber or reuse IDs. IDs go in Acceptance criteria or Agent notes, not
  in Goal or Why.
- Sections labeled Future optimization, Non-goal, or Open are listed as
  excluded with the label; they get no package.
- A package whose only justification is "good practice" is scope expansion.

## Two-pass review

Before Gate B, read every package twice:

1. **Human pass** — from the title, Goal, and Why alone, can someone explain
   what will change and why?
2. **Agent pass** — can a fresh agent find the pinned source, see its
   dependencies and fixed decisions, implement the package, and prove it
   without asking a product or architecture question?

Fix what fails. Then delete background that repeats the linked source or
another section.
