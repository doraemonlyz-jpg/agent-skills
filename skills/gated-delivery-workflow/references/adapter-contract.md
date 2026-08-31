# Repository Adapter Contract

Create `.agents/delivery-workflow.json` at the repository root.

## Required fields

```json
{
  "schema_version": 1,
  "project": "Example",
  "baseline": {
    "name": "Technical Solution V1",
    "status": "approved",
    "required_documents": ["AGENTS.md", "docs/solution.md"],
    "required_markers": {
      "docs/solution.md": ["Status: Approved"]
    }
  },
  "delivery": {
    "current_phase": "phase0",
    "authorized_milestones": ["M0", "M1"],
    "task_id_pattern": "^M[0-9]+-[0-9]+$",
    "milestone_files": {
      "M0": "docs/tasks/M0.md",
      "M1": "docs/tasks/M1.md"
    },
    "checkpoint_rules": ["M2 requires explicit approval"]
  },
  "preflight": {
    "commands": ["python3 scripts/check_baseline.py"]
  },
  "verification": {
    "commands": ["go test ./..."],
    "handoff_template": ".agents/templates/handoff.md"
  },
  "hard_rules": ["Do not add write capability"],
  "architecture_change_triggers": ["Service boundaries", "Data ownership"]
}
```

## Rules

- Use JSON so the bundled standard-library validator can parse it without extra dependencies.
- Keep project-specific requirements in repository documents, not in the generic Skill.
- List required documents in reading order.
- Use `required_markers` only for stable approval or gate text.
- Map every authorized milestone to a real file.
- Keep commands literal and repository-owned.
- Do not place secrets, tokens, account identifiers, or credentials in the adapter.
