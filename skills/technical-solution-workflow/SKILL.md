---
name: technical-solution-workflow
description: Guide users from ambiguous product or engineering requirements to an agreed technical solution, and only begin implementation after explicit approval. Classifies every request as spike, bounded, or architectural so ceremony scales with the task while the approval gate never does. Use when a user asks to design, build, refactor, or extend a system, service, agent, platform, application, architecture, or feature whose requirements or design are not yet settled.
metadata:
  short-description: Classify the task, clarify requirements, agree the solution, then code
---

# Technical Solution Workflow

## Purpose

Turn a product or engineering request into a clear, reviewed, approved solution
before any implementation begins — with the amount of process matched to the
actual size of the task.

<HARD-GATE>
Do NOT write code, scaffold a project, run migrations, or take any other
implementation action until you have told the user what you intend and they have
explicitly approved it.

This applies to EVERY task on EVERY path. The artifact scales with complexity —
two sentences in chat for a small change, a versioned solution document for a new
system. The approval gate never scales. There is no task small enough to skip it.
</HARD-GATE>

Never skip a gate merely because a likely answer can be inferred.

---

# Stage 0: Classify the Task

Before your first question, classify the request and **say the classification
out loud** — "这个我判断是 bounded，所以我直接在对话里给简要方案，不出文档" — so
the user can override it.

| Path | When | Questions | Artifact | Gate |
|---|---|---|---|---|
| **Spike** | A feasibility question — "能不能…" "可行吗" "快速验证一下" — whose output is an answer, not code you keep | 2–3 sentences stating what you will probe | A recommendation. Anything built is labeled throwaway | A nod is enough |
| **Bounded** | A well-scoped change to code **that already exists in this repo**: a new flag, a small endpoint, a one-file fix | One round of grouped questions (see Stage 1) | A short design **in chat** — approach, files touched, testing. No document | Explicit yes required |
| **Architectural** | New projects, new subsystems, new Agents, changes that restructure components or alter interfaces others depend on | Full Stage 1 discovery | Versioned solution document (Stage 2) + implementation plan (Stage 3) | Explicit approval per Stage 2 |

## Classification Rules

1. **Bounded measures the repo, not your familiarity.** Understanding the kind of
   application is not enough. Bounded means the flow you are about to change is
   already here to read. If there is no existing flow to change, the task is
   architectural.
2. **A new project is always architectural.** It has no existing flow by
   definition.
3. **When in doubt between two paths, take the heavier one.** Reaching for the
   lighter label to avoid work IS the doubt.
4. **The ratchet is one-way.** Hidden complexity discovered mid-task upgrades the
   path — stop, say so, and step up. Nothing ever downgrades mid-task.
5. **Each task gets its own classification and its own approval.** Approval of a
   spike does not approve the follow-up. Approval of last week's solution does not
   approve this week's change.

## Anti-Pattern: "Too Simple To Need Approval"

Every path ends with the user approving your intent before implementation. A
config change, a single utility function, a one-line fix — the design may be two
sentences in chat, but you MUST present it and stop. Simple tasks are exactly
where unexamined assumptions waste the most work.

## Red Flags

| Thought | Reality |
|---|---|
| "这个太简单了，不用出方案" | Simple means a *short* design, not no design. Two sentences, then approval. |
| "叫它 bounded 就能跳过方案文档" | Reaching for a label to skip work IS the doubt — take the heavier path. |
| "方案很明显，我一边写他们一边看" | The gate is the approval, not the design's length. Present, then STOP until you hear yes. |
| "我熟悉这类系统，算 bounded" | Bounded measures the repo, not your familiarity. No existing flow = architectural. |
| "时间紧，先写代码后补方案" | Time pressure shrinks the artifact, never the gate. Offer a two-sentence design instead. |
| "spike 跑通了，代码就留着吧" | A spike's output is an answer. Keeping the code is a new request — re-classify it. |
| "做大了，但快写完了，不用重新分级" | Hidden complexity upgrades the path mid-task. Stop and say so. |
| "上次那个方案批准过了" | Approval does not transfer across tasks. |
| "用户说'继续'，应该是同意了" | Silence, partial agreement, and topic changes are not approval. Ask explicitly. |

---

# Core Principles

1. Classify before you question; announce the classification.
2. Do not start coding from an unclear request.
3. Ask only questions that materially affect scope, architecture, security, cost,
   delivery, or acceptance.
4. Group related questions instead of asking many tiny questions one by one.
5. Record decisions as they are confirmed.
6. Distinguish MVP requirements from future optimizations.
7. Make a concrete recommendation whenever presenting options.
8. Clearly explain tradeoffs and consequences.
9. Do not treat silence, partial agreement, or topic changes as approval.
10. Only begin coding after explicit approval.
11. If the user changes a confirmed requirement, update the solution before coding.
12. Ceremony scales down; the gate does not.

---

# Trigger Conditions

Use this skill whenever a request will change code or create a system and the
requirements or design are not fully settled. This includes small changes — they
route to the Spike or Bounded path, not out of the workflow.

Skip this workflow only for:

- Pure explanation or discussion with no implementation intent
- Syntax or API usage questions
- Typo, comment, or copy edits with no behavior change
- Mechanical edits the user has already specified exactly, down to the file and the change

Everything else gets classified in Stage 0. **"It's a small fix" is a Bounded
classification, not an exit.**

---

# Workflow Overview

```text
User request
   ↓
Stage 0: Classify (spike / bounded / architectural) — announce it
   ↓
 ┌─ spike ───────→ probe plan → nod → investigate → report recommendation
 │
 ├─ bounded ─────→ grouped questions → short design in chat → EXPLICIT YES → implement
 │
 └─ architectural→ Stage 1 discovery
                      ↓
                   requirement summary and confirmation
                      ↓
                   Stage 2: versioned solution document
                      ↓
                   architecture review
                      ↓
                   EXPLICIT APPROVAL
                      ↓
                   Stage 3: implementation plan → code → verify

Hidden complexity at any point → stop, announce upgrade, re-enter at the heavier path
```

---

# Stage 1: Requirement Discovery

Reach the clarity needed to make architecture decisions — no more.

## First Response

1. State the classification.
2. Briefly restate the user's goal.
3. Identify the most important unknowns.
4. Ask a compact group of high-impact questions.
5. Offer recommended defaults.

## Questioning Rules

**Batch 3–6 related questions per round.** Do not ask one question per message
unless the user explicitly prefers that style.

Bad:

```text
Do you need login?
Do you need 2FA?
Do you need email?
```

Better:

```text
确定架构前先确认：
1. 个人用还是多人用？
2. 首版是否只读？
3. 部署在哪？
4. 登录安全要求？
5. 输出渠道有哪些？

推荐默认值：个人、只读、VPS、密码 + TOTP、Web + Email。
```

Ask high-impact questions first: user scale and scope, read-only vs write, data
source availability, deployment constraints, security level, real-time vs
scheduled, cost, technology restrictions.

The full question bank is in `references/REQUIREMENT_DIMENSIONS.md` — load it when
you need dimension coverage, not by default.

## Stop Questioning at the Right Time

Move on once these are clear: users, core workflows, data sources, read/write
boundaries, security level, deployment environment, key outputs, MVP scope, major
constraints. Minor preferences become defaults or future optimizations.

## Requirement Decision Log

Maintain a compact log, labeling each item:

- **Confirmed**
- **Recommended default**
- **Open**
- **Future optimization**

## Requirement Confirmation Gate

Before drafting the solution, present a concise requirement summary:

```text
核心需求已经足够清晰，我将以下面这份确认范围为基础编写技术方案：
...
```

Resolve any material open item before finalizing.

---

# Stage 2: Technical Solution

**Architectural path only.** Bounded designs stay in chat; producing a solution
document for a bounded task is over-ceremony and is itself a failure.

Produce an implementable, reviewable solution where every major architecture
decision traces to a confirmed requirement. Section-by-section template:
`references/SOLUTION_TEMPLATE.md`. Pre-presentation checklist:
`references/CHECKLISTS.md`.

## Architecture Review Process

1. Ask the user to review the architecture, not the code.
2. Resolve architecture questions in grouped rounds.
3. Update the decision log.
4. Produce a revised version when material decisions change.
5. Mark postponed items as future optimizations.
6. Do not start coding during architecture review.

Version names: **Technical Solution V1 / V2 / V3**. Bump the version when scope,
architecture, data model, security, or deployment decisions change materially.

## Approval Gate

Coding is blocked until the user explicitly approves.

Valid approval:

- "技术方案没问题，可以开始"
- "V2 确认，开始编码"
- "Approved"
- "按这个方案实现"

**Not** approval:

- "看起来不错"
- "继续"
- Answering one architecture question
- Requesting another diagram
- Asking what to do next
- Silence

When approval is ambiguous, ask for it explicitly:

```text
技术方案已经完成评审。请明确确认"按当前方案开始编码"，我再进入实现阶段。
```

If the user pushes to skip the gate ("直接写吧"、"时间紧"), shrink the artifact,
not the gate — offer a two-sentence design and ask for a yes.

---

# Stage 3: Implementation

## Bounded path

Implement directly after the explicit yes. No plan document.

## Architectural path

After approval, produce an implementation plan before writing large amounts of
code (structure, milestones, ordered tasks, migrations, endpoints, interfaces,
test plan, deployment path, verification commands — see
`references/SOLUTION_TEMPLATE.md`).

For large projects use **Explore → Plan → Implement → Verify**:

- **Explore** — inspect the repository and docs, identify current architecture, do
  not modify code
- **Plan** — list exact files and modules, migration and compatibility strategy,
  tests and rollback
- **Implement** — focused changes, no unrelated refactoring, preserve the agreed
  architecture, record deviations
- **Verify** — formatting, unit and integration tests, static checks, migrations,
  failure paths, acceptance criteria

## Coding Rules

1. Never implement unapproved features.
2. Never expose write-capable tools that were approved as read-only.
3. Keep external integrations behind interfaces.
4. Validate all external responses.
5. Use deterministic code for critical calculations.
6. Require schemas for LLM outputs.
7. Keep prompts versioned.
8. Store workflow and model versions with generated outputs.
9. Add idempotency to scheduled and retried operations.
10. Add tests with each implementation phase.
11. Document any deviation from the approved solution.
12. If implementation reveals a flawed architecture assumption, pause coding and
    return to architecture review.

Pre-coding checklist: `references/CHECKLISTS.md`.

---

# Handling Requirement Changes During Coding

1. Identify impacted modules.
2. State whether the change is local or architectural.
3. If architectural, update the solution and re-obtain approval.
4. Resume coding only after approval.

Do not silently absorb major scope changes. A change that pushes a bounded task
past the repo's existing flow is a path upgrade — announce it.

---

# Reference Files

Load on demand, not by default:

| File | When |
|---|---|
| `references/REQUIREMENT_DIMENSIONS.md` | Stage 1, when you need dimension coverage |
| `references/SOLUTION_TEMPLATE.md` | Stage 2/3, architectural path only |
| `references/CHECKLISTS.md` | Before presenting a solution, before coding |
| `references/RESPONSE_TEMPLATES.md` | Wording for path announcement, gates, upgrades |

---

# Expected Outcome

1. An announced classification.
2. A requirement decision log (bounded: inline; architectural: full).
3. An artifact sized to the path.
4. Explicit user approval — on every path.
5. Code only after approval.
6. Verification against acceptance criteria.
