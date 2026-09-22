---
name: delivery-plan-bootstrap
description: Turn an approved technical solution or spec into the gated delivery plan that gated-delivery-workflow executes — phases, milestones, work packages in docs/tasks/, and the adapter at .agents/delivery-workflow.json. Prefer this over generic planning or task-breakdown skills whenever the repository has or should have .agents/delivery-workflow.json, AGENTS.md routes planning here, or the solution came from technical-solution-workflow. Use after approval and before implementation to break a solution into milestones or work packages, to authorize the next milestone, or to replan after ARCH_REVIEW or a new solution version. Not for tracker tickets or GitHub issues.
metadata:
  version: 1.2.1
  short-description: Approved solution → milestones, work packages, and delivery adapter
---

# Delivery Plan Bootstrap

## Purpose

Close the gap between "the solution is approved" and "execute the next Work
Package". This skill is the **planner**; `gated-delivery-workflow` is the
**executor**. The planner writes the plan and records authorization the user
gives. It never implements code and never authorizes on the user's behalf.

<HARD-GATE>
1. No plan without an approved baseline. If the solution or spec is not
   explicitly approved, stop and route to `technical-solution-workflow`.
2. No authorization without the user. Put a milestone into
   `authorized_milestones` only after the user explicitly authorizes that
   milestone by ID. Plan approval is not milestone authorization.
3. No scope beyond the baseline. Every Work Package traces to a section of the
   approved solution. Anything else is a new request.
4. No open decisions inside Work Packages. A choice that would change behavior,
   interfaces, data, security, scale, performance, compatibility, operations,
   cost, or proof is a blocking decision. Record it in the plan index, make
   every affected package depend on it (`DECISION: <id>`), and route it to
   `technical-solution-workflow`. Never leave it for the implementer, and never
   authorize a milestone that still depends on it.
</HARD-GATE>

## Where This Fits

```text
project-engineering-standards-bootstrap   AGENTS.md + docs/ standards
        ↓
interview-me (optional)                   spec-<name>.md
        ↓
technical-solution-workflow               approved Technical Solution Vn
        ↓
delivery-plan-bootstrap   ← this skill    docs/tasks/ + .agents/delivery-workflow.json
        ↓
gated-delivery-workflow (+ coding-standards)   one Work Package per turn
        ↓ ARCH_REVIEW
technical-solution-workflow → delivery-plan-bootstrap (Replan)

context-handoff: start a fresh session after planning, and whenever a
delivery session grows long. The plan files are the durable state.
```

## Modes

Pick one and say it out loud in the first reply.

| Mode | When | Output |
|---|---|---|
| **Bootstrap** | No adapter or no milestone files yet | Full plan + adapter + AGENTS.md link |
| **Authorize** | User wants to open the next milestone or phase | Updated `authorized_milestones`, `current_phase`, authorization log |
| **Replan** | New solution version (including one that resolves blocking decisions), `ARCH_REVIEW` outcome, approved scope change, or a plan written in an older format of this skill | Revised milestone files and adapter; completed work preserved |

## Existing Delivery Conventions

A repository may already run `gated-delivery-workflow` with its own plan layout,
for example a project-specific delivery skill with its own stage files, task
ledger, handoff template, and evidence index. A plan is this skill's own only
when `docs/tasks/README.md` says `Planned by: delivery-plan-bootstrap`. For any
other plan:

- Do not convert or rewrite its milestone files into this skill's format.
- Authorize: change only `authorized_milestones` and `current_phase`, and record
  the authorization where the repository documents it.
- Replan: follow the repository's own plan documents, or stop and ask.
- The checker skips milestone format checks and runs only the adapter check.

---

# Bootstrap

```text
Discover inputs → Gate A: baseline approved?
→ Draft breakdown → Two-pass review → Gate B: user confirms plan
→ Write files → Validate → Gate C: user authorizes milestones
→ Report + recommend fresh session
```

## Step 1: Discover Inputs

Read, in this order, whatever exists:

1. `AGENTS.md` and every document it lists.
2. The approved solution: usually `docs/solution.md` or the file the user names.
   Use its **Implementation Plan** section if present (produced in
   `technical-solution-workflow` Stage 3).
3. An `interview-me` spec (`spec-*.md`, `spec-overview.md`) if that is the
   baseline instead.
4. `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/TESTING.md`.
5. Existing `.agents/delivery-workflow.json` — if present, switch to Authorize
   or Replan; if the plan is not this skill's own, follow Existing Delivery
   Conventions.
6. Repository build, test, lint commands actually present.

If `AGENTS.md` or the standards documents are missing, say so and recommend
`project-engineering-standards-bootstrap` first. Proceed only if the user says
to; then `baseline.required_documents` lists only files that exist.

## Step 2: Gate A — Baseline Approved

Accept as evidence either:

- The document already contains a stable approval marker such as
  `Status: Approved` with a version; or
- The user explicitly approved this version in this session using the phrases
  `technical-solution-workflow` accepts ("V2 确认", "Approved", "按这个方案实现").

In the second case, tell the user you will add the marker, then add a single
line near the top: `Status: Approved — Technical Solution V<n> — <YYYY-MM-DD>`.
Do not edit anything else in the solution.

"看起来不错", "继续", or silence is not approval. A spec from `interview-me` is
not approved until the user says so — ask explicitly.

## Step 3: Draft the Breakdown

Read `references/decomposition-rules.md` and apply it. Produce:

- **Phases** — coarse gates such as `phase0` foundation, `phase1` core flow.
- **Milestones** — each a demonstrable increment with entry and exit criteria.
  ID has no hyphen (`M0`, `M1`) because work package IDs derive their
  milestone from the text before the first hyphen.
- **Work Packages** — `M<n>-<k>`, one working result per gated-delivery turn,
  written for two readers: a plain-language Goal and Why a person understands
  in under a minute, then acceptance criteria, how to check, required tests,
  scope boundary, pinned solution references, agent notes, and non-goals.
  Fields and writing rules: `references/milestone-file-format.md`.
- **Blocking decisions** — anything a package's implementer would have to
  decide (HARD-GATE 4). Give each an ID (`D1`, `D2`, …, never reused), the
  precise open question, and the affected packages. A package is affected when
  any plausible answer would change its Goal, acceptance criteria, contract, or
  scope, not only when it obviously mentions the topic. Affected packages are
  written with what is already decided and depend on `DECISION: <id>`. Open
  decisions do not stop the plan from being written; they stop the affected
  milestones from being authorized.
- **Hard rules** and **architecture change triggers** — each quoted or derived
  from a cited section of the solution, `AGENTS.md`, or `docs/SECURITY.md`.
  Never invent policy.
- **Verification commands** — only commands that exist, or that the approved
  solution proposes and an M0 Work Package creates.
- **Checkpoints** — milestones needing explicit approval before start.
- **Traceability** — every in-scope solution section maps to at least one
  Work Package; every Work Package maps back.

## Step 4: Two-Pass Review

Read every Work Package twice, as `references/decomposition-rules.md`
describes: a human pass on the title, Goal, and Why, and an agent pass asking
whether a fresh agent could implement and prove it without a product or
architecture question. Fix what fails, then delete repeated background.

## Step 5: Gate B — Plan Review

Present the breakdown compactly in chat before writing files:

```text
交付计划草案（基于 Technical Solution V<n>）：

Phase / 里程碑：
- phase0 — M0 基础骨架（4 个工作包）：退出条件 …
- phase1 — M1 核心流程（6 个工作包）：退出条件 …  ⚑ 开始前需确认

关键依赖：M1-2 依赖 M1-1 的数据库迁移；M2-3 依赖外部凭证（EXT）
硬性规则（来源）：只读访问券商 API（方案 §5.2）…
架构变更触发条件：服务边界、数据归属、信任边界 …
未覆盖的方案条目：无 / §9 未来优化（按方案排除）
阻塞决策：无 / D1 重试上限未定（影响 M2-1、M2-3）→ 交给 technical-solution-workflow
（计划照样写入；受影响的工作包保持阻塞，含待定决策的里程碑暂不能授权）

确认后我写入 docs/tasks/ 和 .agents/delivery-workflow.json。
```

Revise until the user confirms. Plan confirmation authorizes writing files, not
executing milestones.

## Step 6: Write Files

| File | Source template |
|---|---|
| `docs/tasks/README.md` | `assets/plan-index-template.md` |
| `docs/tasks/M<n>.md` (one per milestone) | `assets/milestone-template.md`, format in `references/milestone-file-format.md` |
| `docs/tasks/handoffs/.gitkeep` | empty; handoffs land here as `<TASK-ID>.md` |
| `.agents/templates/handoff.md` | copy `gated-delivery-workflow/assets/work-package-handoff.md` verbatim |
| `.agents/delivery-workflow.json` | `assets/delivery-workflow.template.json`, contract in `gated-delivery-workflow/references/adapter-contract.md` |
| `AGENTS.md` | add the section in `assets/agents-md-snippet.md`; targeted edit, never rewrite |

Adapter rules:

- `baseline.name` matches the approved version exactly.
- `baseline.status` is `approved` only because Gate A passed.
- `baseline.required_documents`: `AGENTS.md`, the solution, then
  `docs/tasks/README.md`, in reading order.
- `baseline.required_markers`: the Gate A marker text.
- `delivery.task_id_pattern`: `^M[0-9]+-[0-9]+$` unless the repo already uses
  another scheme.
- `delivery.milestone_files`: every milestone, in delivery order.
- `delivery.authorized_milestones`: **`[]`** until Gate C.
- `verification.handoff_template`: `.agents/templates/handoff.md`.
- Initial Work Package status: `BLOCKED` for all (milestone not yet authorized).

Existing files: read fully, propose a merge, and preserve project rules. Never
overwrite without approval.

## Step 7: Validate

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/delivery-plan-bootstrap/scripts/check_delivery_plan.py" --repo .
```

When installed elsewhere (for example as a Claude plugin), run it from this
skill's own `scripts/` directory.

The checker validates milestone files and dependency graph, and also runs
`gated-delivery-workflow`'s `inspect_delivery_config.py` when installed next to
this skill. Fix every failure and report every warning. An empty
`authorized_milestones` list is valid at this point.

## Step 8: Gate C — Milestone Authorization

Ask separately and explicitly:

```text
计划已写入并通过校验。要执行工作包，需要你明确授权里程碑。
建议先授权 M0（基础骨架，无外部依赖）。回复"授权 M0"即可；M1 起按检查点逐个授权。
```

Only an explicit reply naming milestone IDs counts. Then run **Authorize**.

A milestone with any package that depends on an open decision cannot be
authorized. Before suggesting an unaffected milestone, say whether it is truly
independent of every open decision (each plausible answer leaves its packages
unchanged). If that is uncertain, recommend waiting: code written before a
decision tends to decide it by default and invites rework.

## Step 9: Report

1. File tree created or changed.
2. Milestones, Work Package counts, authorized milestones.
3. Open blocking decisions and the milestones they block; assumptions and
   open items.
4. Validation output (literal PASS/FAIL).
5. Next step: start a fresh session. With open decisions, that is
   `technical-solution-workflow` for the decisions, then **Replan**; otherwise
   `gated-delivery-workflow` ("执行下一个工作包"). Planning context is not
   needed there; the files carry it.

---

# Authorize

For plans this skill did not create, follow Existing Delivery Conventions.

1. Read the adapter and `docs/tasks/README.md`.
2. Confirm the user named the milestone IDs explicitly.
3. Refuse any named milestone that still has a package depending on an open
   decision (HARD-GATE 4). Name the decisions and route them to
   `technical-solution-workflow`.
4. Check readiness and report, but do not block on it — authorization is the
   user's call:
   - earlier milestones DONE or explicitly left open;
   - milestone checkpoint rules satisfied;
   - external prerequisites (`EXT:`) available.
5. Append the IDs to `authorized_milestones`; update `current_phase` if the
   milestone opens a new phase.
6. In each newly authorized milestone file, set Work Packages whose
   dependencies are all DONE (or none) to `READY`. Leave others `BLOCKED`.
7. Append a row to the Authorization Log in `docs/tasks/README.md`: date,
   milestone, the user's literal words.
8. Run the checker. Report.

Dates, schedules, or "继续" never authorize a milestone. Never remove an
authorization unless the user asks.

---

# Replan

Triggered by a new solution version, an `ARCH_REVIEW` outcome resolved through
`technical-solution-workflow`, or approved scope change.

1. Gate A again for the new version.
2. Diff old vs new solution. List affected sections.
3. Classify every existing Work Package:
   - **Keep** — unaffected. DONE stays DONE with its evidence.
   - **Revise** — not started; edit in place, reset to `BLOCKED`.
   - **Rework** — DONE but invalidated: keep the original record, mark
     `Superseded by <new-id>`, add a new Work Package.
   - **Drop** — no longer in scope: mark `Status: DROPPED — <reason, version>`
     and remove from dependency lists. Never delete the record.
4. New Work Packages get new IDs. Never reuse an ID.
5. Update `baseline.name`, markers, triggers, and hard rules.
6. Authorization of milestones containing revised or new work is re-confirmed
   with the user.
7. Gate B on the delta, then write, validate, report.

## Decision resolution

When a new solution version resolves blocking decisions:

1. Gate A for the new version, as above.
2. In the plan index, mark each resolved decision `RESOLVED` with the version
   and section that answers it. Decisions the new version leaves open stay
   `OPEN` with their dependents.
3. For each package that depended on a resolved decision: remove the
   `DECISION:` dependency, write the fields that hinged on it, and run the
   two-pass review.
4. Check every DONE package against the answers, not only the listed ones:
   Keep or Rework as above.
5. Gate B on the delta, then write and validate. Milestones no longer tied to
   an open decision can now be authorized.

## Format upgrade

When the solution is unchanged but the plan was written in an older format of
this skill (the checker reports missing `Why` or `How to check`, for example):

1. Skip steps 1–2; the baseline and scope stay as they are.
2. Keep every ID, status, dependency, authorization, and evidence link.
3. Rewrite each package into the current format: plain Goal and Why, three to
   seven observable acceptance criteria, How to check, Scope as a boundary,
   pinned Solution refs, fixed decisions in Agent notes, concrete Non-goals.
4. A choice that surfaces as undecided is a blocking decision (HARD-GATE 4):
   list it instead of inventing an answer.
5. Run the two-pass review, then Gate B on the rewritten packages, then write
   and validate. Authorization stays unless the user changes scope.

---

# Red Flags

| Thought | Reality |
|---|---|
| "方案大致定了，先拆任务" | 未批准的方案没有计划。回到 technical-solution-workflow。 |
| "用户确认了计划，M0–M3 都授权上" | 计划确认只允许写文件。授权必须逐个点名里程碑。 |
| "顺便加一个监控工作包，反正以后要" | 方案里没有的就是新需求。 |
| "硬性规则写几条通用的" | 每条规则都要有出处。没有出处的是编造的政策。 |
| "验证命令先写 make test 占位" | 只写存在的，或方案提出且 M0 会创建的命令。 |
| "旧工作包没用了，删掉" | 标记 DROPPED 或 Superseded，保留记录和 ID。 |
| "计划写完顺手做 M0-1" | 本 skill 不写实现代码。新会话交给 gated-delivery-workflow。 |
| "这个细节让执行的 agent 到时候自己定" | 会改变行为、接口、数据或安全的选择就是阻塞决策，记进索引、交给方案，不写进工作包。 |
| "有阻塞决策，计划先不写，等定了再说" | 照样写入：决策进索引，受影响的工作包依赖它并保持阻塞。只存在对话里的计划，一压缩就没了。 |
| "M3 不受影响，先授权跑着" | 先把每条待定决策的几种答案过一遍，确认 M3 的工作包都不变；拿不准就等，先写的代码会替决策做主。 |
| "先建表，再写 service，最后接 API，拆三个包" | 按能工作的结果拆，不按层拆。共享契约只归一个工作包。 |
| "Scope 里先把要改的文件列全" | Scope 只写边界。具体文件由执行时的计划决定。 |
| "验收写：保证幂等、保证健壮" | 写可观察的行为：同一事件发两次只产生一条回复。 |

# Reference Files

| File | When |
|---|---|
| `references/decomposition-rules.md` | Steps 3–4: splitting, ordering, proof, two-pass review |
| `references/milestone-file-format.md` | Steps 3 and 6: Work Package fields and writing rules; the checker enforces them |
| `assets/*` | Step 6 templates |
| `scripts/test_check_delivery_plan.py` | After changing the checker: `python3 -B scripts/test_check_delivery_plan.py` |
| `gated-delivery-workflow/references/adapter-contract.md` | Adapter fields; the single source of truth |
| `gated-delivery-workflow/references/verification-evidence.md` | Choosing required test layers |

# Expected Outcome

1. The mode was stated.
2. Gate A evidence exists in the solution document.
3. The user confirmed the plan before files were written.
4. Every Work Package traces to the solution; every in-scope solution section is covered.
5. No Work Package hides an open decision: each one is in the index, its
   dependents are BLOCKED on it, and no milestone that depends on it is
   authorized. Each package passed the two-pass review.
6. The checker passes; warnings are reported.
7. `authorized_milestones` contains only milestones the user named.
8. No implementation code was written.
