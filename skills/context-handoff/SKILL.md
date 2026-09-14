---
name: context-handoff
description: Decide when the current session must end and write the handoff that compaction cannot preserve. Use when context usage is high, when a session has run across multiple days or many tasks, when the agent starts repeating questions or forgetting settled decisions, or when the user asks about context limits, compaction, /new, starting fresh, or handing off to a new session.
metadata:
  version: 1.0.0
  short-description: End the session before compaction does, and carry over what it destroys
---

# Context Handoff

Auto-compaction is not a way of working. It is a survival mechanism that
**deletes every assistant turn**. Anything that exists only in what the assistant
said — "X is fixed", "Y is done", "don't touch Z" — is gone the moment it fires.

This skill decides when to stop, and writes the handoff that covers that loss.

<HARD-RULE>
Never let auto-compaction be the thing that ends a session. Either the work
finishes first, or you hand off first. If compaction has already fired in this
session, treat everything the assistant claimed before it as unverified.
</HARD-RULE>

---

## Stage 0: Must this session end?

Check the context meter (`/status` in Codex, `/context` in Claude Code).
Any ONE of these means **end it now** — they are tests, not judgment calls:

| Condition | Why |
|---|---|
| **Context ≥ 70% used** | Compaction fires around 93% of the session budget. Below 70% there is room to hand off cleanly; above it there may not be. Use the percentage, never a token count — the budget is configurable and varies by model and client version. |
| **Session started on an earlier calendar day** | User messages are never dropped by compaction, so a multi-day session carries a floor that only grows. |
| **Compaction already fired once** | The next one comes sooner than the last. Interval shrinks roughly 40% across a long session. |
| **Third distinct task in one session** | Tasks do not need each other's history. Each one inherited is pure cost. |

Softer signals — any two together mean end it:

- Asks a question the user already answered
- Forgets a convention or boundary settled earlier in the session
- Reintroduces a bug that was already fixed
- Re-reads a file it already read
- Answers get vaguer, more generic, less specific to this repo

**Do not negotiate with the threshold.** "Almost done" is the most common reason
a session blows past it and loses the record of what was almost done.

---

## Stage 1: Write the handoff

Write `HANDOFF.md` in the repo root. Structure it around **what compaction
deletes**, not around what happened.

### Must include

1. **Done list.** Every completed item, one line each, with the file touched.
   This is the single most important section: completion status exists only in
   assistant turns, which compaction removes entirely. If it is not written
   down here, the next session will redo it.
2. **Do-not-touch list.** Files and modules that are finished, approved, or
   deliberately left alone. Without this the next session edits settled work.
3. **Settled decisions, with the reason.** The reason matters more than the
   decision — without it the next session relitigates or silently reverses it.
4. **Open next steps**, in order, with the first one concrete enough to start.
5. **Blockers**, including anything waiting on the user.

### Must NOT include

- Code the next session can read for itself
- File contents or directory listings
- Narrative of how the work went
- Anything you did not verify — mark uncertain items as uncertain

Keep it under 150 lines. A handoff long enough to bloat the next session
defeats its own purpose.

### Verify before ending

Re-read the Done list and ask: if I only had this file, would I know not to
redo any of it? If any item is ambiguous about whether it is finished, fix it.

---

## Stage 2: Start the new session

1. Start fresh — `/new` in Codex, a new session in Claude Code.
2. First instruction: read `HANDOFF.md`, then state the plan before acting.
3. Do not paste the old conversation. That rebuilds the problem.

---

## Prevention — worth more than any handoff

**Isolate heavy work in subagents.** Anything that reads many files, runs a
broad search, or explores an unfamiliar area belongs in a subagent whose context
is discarded. The main thread receives only the conclusion. A main context that
does not grow never reaches the threshold.

**One task, one session.** The floor rises with every user message and never
falls. Ending at a task boundary is the only thing that resets it.

**Write decisions to files as they are made**, not at handoff time. A decision
recorded in a file survives compaction; the same decision in an assistant turn
does not.

---

## Basis

Measured on 22 real compaction events in a single 8-day Codex session
(see `codex-compaction-verification.md` next to this file):

- All 22 compactions kept `compaction×1 + developer×N + user×N` and
  **zero assistant entries**
- User messages accumulated 7 → 140 and were never dropped
- Compaction interval shrank ~40% from the first five to the last five
- Triggered at 219K–250K input tokens (median 239K) against a 258K window
- The replacement summary is `encrypted_content` — **not auditable locally**,
  so never assume it preserved anything specific

**The window is not fixed.** Codex allocates a session working budget that is far
smaller than the model's real context — Astra measured 258K against a ~1M model.
Two top-level `config.toml` keys raise it, verified working on a Pro Lite
subscription 2026-09-14:

```toml
model_context_window = 1000000
model_auto_compact_token_limit = 900000
```

Check the actual number with `/status` before trusting it; the keys are
undocumented for some models. Everything above is stated in **percentages** for
exactly this reason — the thresholds hold whether the budget is 258K or 1M.

The last point is why the Done list is written by hand rather than trusted to
the summary.

---

## Status

**Not yet validated by evals.** Thresholds here are derived from one user's
measured sessions, not from a benchmark. Treat 70% as a starting point and
adjust once you have observed where your own sessions start degrading.
