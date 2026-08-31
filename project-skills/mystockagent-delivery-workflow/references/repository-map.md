# Repository and Document Routing

## Required baseline

| Purpose | Path |
|---|---|
| Agent entry | `AGENTS.md` |
| Generic adapter | `.agents/delivery-workflow.json` |
| Project Skill | `.agents/skills/mystockagent-delivery-workflow/SKILL.md` |
| Version index | `docs/versions/v3.2/README.md` |
| Detailed requirements | `docs/versions/v3.2/REQUIREMENTS.md` |
| Inheritance matrix | `docs/versions/v3.2/REQUIREMENT_INHERITANCE.md` |
| Approved solution | `docs/versions/v3.2/TECHNICAL_SOLUTION.md` |
| Migration status | `docs/versions/v3.2/MIGRATION_STATUS.md` |
| Delivery gates | `docs/versions/v3.2/DELIVERY_GATES.md` |
| Architecture | `docs/versions/v3.2/ARCHITECTURE.md` |
| Security | `docs/versions/v3.2/SECURITY.md` |
| Testing | `docs/versions/v3.2/TESTING.md` |
| Human plan | `docs/versions/v3.2/IMPLEMENTATION_PLAN.md` |
| Task ledger | `docs/versions/v3.2/WORK_PACKAGES.md` |
| Agent protocol | `docs/versions/v3.2/agent-coder/README.md` |

## Milestone routing

| Task prefix | Read |
|---|---|
| `S0-*` | `docs/versions/v3.2/agent-coder/S0.md` |
| `S1-*` | `docs/versions/v3.2/agent-coder/S1.md` |
| `S2-*` | `docs/versions/v3.2/agent-coder/S2.md` |
| `S3-*` | `docs/versions/v3.2/agent-coder/S3.md` |
| `S4-*` | `docs/versions/v3.2/agent-coder/S4.md` |
| `S5-*` | `docs/versions/v3.2/agent-coder/S5.md` |
| `S6-*` | `docs/versions/v3.2/agent-coder/S6.md` |
| `S7-*` | `docs/versions/v3.2/agent-coder/S7.md` |

The unversioned `docs/ARCHITECTURE.md` and V3.1 are historical baselines. For new architecture and delivery decisions, V3.2 takes precedence. Unversioned coding, security, and testing standards remain mandatory unless V3.2 defines a stricter or explicitly stage-specific rule.

The project Skill delegates generic task lifecycle, gate enforcement, verification evidence, architecture-drift handling, and handoff to the personal `$gated-delivery-workflow` Skill. Keep MyStockAgent-only rules in this repository adapter.

For an exact same-Work-Package resume, `check_baseline.py` provides the
`baseline_sha256` used by the continuity rule in `AGENTS.md`. The matching
milestone file and current task/evidence delta are always read even when the
digest matches.
