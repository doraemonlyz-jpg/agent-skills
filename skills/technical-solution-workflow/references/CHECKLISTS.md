# Checklists

## Before Presenting a Technical Solution (Architectural path)

- [ ] Core users and workflows are clear
- [ ] MVP and non-goals are explicit
- [ ] External integrations are validated or marked for feasibility testing
- [ ] Read/write boundaries are explicit
- [ ] Security is proportional to data sensitivity
- [ ] Agent and deterministic responsibilities are separated
- [ ] Tool whitelist and forbidden actions are explicit
- [ ] Data model supports ownership and history
- [ ] Retry and idempotency are defined
- [ ] Failure degradation is defined
- [ ] Deployment matches actual infrastructure
- [ ] Backup and recovery are covered
- [ ] Testing and acceptance criteria exist
- [ ] Future optimizations are separated from MVP
- [ ] Coding approval gate is stated

## Before Coding (all paths)

- [ ] The path was classified and announced
- [ ] The user explicitly approved — an approval matching Stage 2's valid list
- [ ] No material requirement remains open
- [ ] For Architectural: an implementation plan exists
- [ ] Required external interfaces have been validated or mocked
- [ ] Repository and deployment constraints are understood

## Before Presenting a Short Design (Bounded path)

- [ ] The flow being changed was actually read in this repo
- [ ] Approach, files touched, and testing are stated
- [ ] No solution document was produced (Bounded must not escalate ceremony)
- [ ] The message ends by asking for approval and nothing has been implemented

## Spike Completion

- [ ] The output is an answer or recommendation, not retained code
- [ ] Anything built is explicitly labeled throwaway
- [ ] If the user wants to keep it, it is re-classified as a new task
