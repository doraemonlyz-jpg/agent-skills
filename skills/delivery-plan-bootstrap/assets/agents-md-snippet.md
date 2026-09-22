## Delivery

Implementation follows an approved delivery plan.

- Plan map: `docs/tasks/README.md`; milestone files: `docs/tasks/M*.md`.
- Adapter: `.agents/delivery-workflow.json`. Execute with `gated-delivery-workflow`,
  one Work Package per turn, only in authorized milestones.
- Handoffs: `docs/tasks/handoffs/<TASK-ID>.md`, from `.agents/templates/handoff.md`.
- Planning, milestone authorization, and replanning go through
  `delivery-plan-bootstrap`, not generic planning or task-breakdown skills. Do
  not edit `authorized_milestones` by hand from a delivery session.
- Architecture drift stops work with `ARCH_REVIEW`; resolve it through
  `technical-solution-workflow`, then replan.
