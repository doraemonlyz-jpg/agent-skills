---
name: first-principles-analysis
description: Decompose a business or technical problem from first principles — outcome, constraints, objects, root problems — and derive the technical approach before choosing architecture or systems. Use when designing or re-architecting a system or platform, when asked to analyse requirements from first principles (第一性原理), or when existing systems or earlier proposals could anchor the answer.
metadata:
  version: 0.1.0
  short-description: Business essence → root problems → technical approach, evidence-graded
---

# First-Principles Analysis

## Purpose

Find the few problems whose solution makes the business work, and derive the
technical approach from them. Existing systems and earlier proposals are
evidence of constraints; the end state is derived from the business.

The output is an analysis to align on with the user. Stop after Step 6 and wait.

## Evidence grades

Tag every material claim with one grade and a short source name:

- **stated** — the user said it.
- **artefact** — a diagram, config sample or document; may mix current state and intent.
- **verified** — checked against code or records at a named version; proves the mechanism, not production traffic or business effect.
- **proposal** — an earlier design, plan or draft; a historical suggestion.
- **inference** — your reasoning; name what it rests on.
- **unknown** — missing. Missing material leaves the responsibility in scope; mark it unknown and keep it.

When sources conflict, name both, their dates and what the conflict changes, then ask.

## Step 1 — Read for facts, set proposals aside

Read the minimum material that reveals the outcome the business owes, whom it
protects or serves, the workflows, how the current implementation behaves, and
known pain. Read business facts first, current-state evidence second.

Read proposals, target designs, roadmaps and talk scripts only after Step 5,
and then as one candidate to compare against. If one is already in context,
name it and derive Steps 2–5 from facts alone.

Done when you can list every source read with its grade, and the proposal
material you set aside.

## Step 2 — State the business essence without system names

Answer each, with grade:

1. **Outcome** — what harm or cost do we reduce, what value do we create, and to whom are we accountable?
2. **Timing** — when must a judgement or action happen, and what does lateness cost at each moment?
3. **Information** — what is observable, when does it arrive, how reliable is it; what happens when it is missing, late or wrong?
4. **Levers** — which actions exist, and what does each cost (friction, false positives, money, people)?
5. **Scarcity** — which resource is always short (human review, latency budget, compute, user tolerance)?
6. **Roles** — who concludes, who acts, who confirms the result?
7. **Proof of value** — how would we know it worked, beyond "it ran" or "it hit"?

Then write the essence as one paragraph framed as a decision problem: who
decides what, about which unit, under which uncertainty and deadline,
constrained by which scarce resource, judged by which outcome.

Done when all seven are answered or marked unknown, and the paragraph names no
system or product.

## Step 3 — Map the work and its objects

Write the chain of transformations the business must perform, for example:
signal → fact → judgement → intent → action sent → acknowledged → completed →
outcome confirmed → learning.

For each object (a judgement, an ongoing case, a work item, an action, a policy
asset, a label) give what it is, its lifecycle states, and who owns each state
transition.

Done when every object has an owner for every state, and objects that current
systems conflate are named as conflated.

## Step 4 — Find the essential problems

Run every lens below against the evidence; record the lenses that find nothing.

For each finding write the symptoms with evidence, the structural cause
(marked inference), and the business consequence. Merge findings that share a
cause. Rank by consequence and keep three to six. Name the most essential one:
the structural defect most other symptoms descend from.

Done when each kept problem cites at least one non-proposal source and you can
say which symptoms it explains.

### Lenses

- **Unit mismatch** — is the unit the system judges (a request, an event) the unit the business is accountable for (a trip, a customer, an order over time)? Caches, counters and TTL'd keys standing in for a missing object are the tell.
- **Done vs returned** — where does a success code, an empty result or a consumed message stand in for "the required work finished in time"? Each such place reads "not checked" as "fine".
- **Time as a contract** — does each judgement and action carry a business deadline and a fallback the business chose (fail-open, fail-escalate, retry), or only a transport timeout?
- **Judgement vs side effects** — is computation mixed with writes, sends and calls? Then shadow runs, replay and rollback are unsafe and results cannot be reproduced.
- **Conclusion vs allocation** — is "how risky or important" decided together with "who handles it now"? Scarce capacity needs its own decision from severity, deadline and capacity.
- **Lifecycle gaps** — along signal → judgement → intent → completed action → outcome, which transitions are recorded and which are lost?
- **Reproducibility** — for one past result, can you name the code, config and model versions and the input values as of that moment?
- **Observable outcome** — where do labels come from, how late, from which biased subset (often only reviewed items get labels)? What measures the misses? Which samples are reserved for independent evaluation?
- **Change risk** — who can change behaviour, how is a change verified before it reaches users, and how is it withdrawn?
- **Unify vs isolate** — which differences between paths (sync, streaming, batch; product lines) are essential, and which are accidental duplication?

## Step 5 — Derive the technical approach

Express the approach as a small set of moves, each tracing to named problems:

- **separations** — what must be split apart;
- **records** — what must be durably recorded, and keyed by what;
- **loops** — what must feed back, and into which decision.

For each move give what it fixes, the realistic alternative, the benefit and
cost of each, and why you recommend yours. State what to unify (semantics,
versions, records) and what to isolate (resources, queues, failure handling).
Draw one small diagram only when the flow is hard to follow in prose.

Done when every Step 4 problem is addressed by some move and every move traces
to a Step 4 problem.

## Step 6 — Land it and stop

- **Assets**: map current systems onto the moves as keep, integrate, extend or new. Current implementation shapes the migration path; the end state comes from Step 5.
- **Verification**: the few metrics that show the essential problems shrinking, each with numerator, denominator, scope and time window. Set numeric targets only from a confirmed baseline.
- **Assumptions** the approach rests on, graded.
- **Questions**: at most three whose answers would change the design, each with your own judgement.

Then stop and wait. Comparison with earlier proposals, chapter drafting and
diagrams follow once the user aligns.

## Writing

Write for a senior reader with minutes to spare: conclusion first, reasoning
after. Prose by default, lists for parallel items, few tables. Collect short
source citations at the end of a section. Write in the user's language.
