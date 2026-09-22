#!/usr/bin/env python3
"""Tests for check_delivery_plan.py. Standard library only.

Run: python3 -B scripts/test_check_delivery_plan.py
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("check_delivery_plan.py")
SKILL = SCRIPT.parent.parent

FULL = """## {id} — {title}

- Status: {status}
- Depends on: {deps}
- Goal: Something is missing today. After this package it works.
- Why: People can rely on it.
- Acceptance criteria:
  - The first observable result holds.
  - The second observable result holds.
  - The third observable result holds.
- How to check:
  - `make test`
  - manual: open the page and see the result.
- Required tests: unit
- Scope: one component.
- Solution refs: docs/solution.md — Technical Solution V2 §1
- Non-goals:
  - Related work (M9-1).
- Evidence: —
"""

PARTIAL = """## {id} — {title}

- Status: {status}
- Depends on: {deps}
- Goal: Something is missing today. After this package it works.
- Why: People can rely on it.
- Scope: one component.
- Solution refs: docs/solution.md — Technical Solution V2 §2
- Agent notes:
  - How the result is delivered is {decision}.
- Evidence: —
"""

HEADER = """# {m} — Milestone {m}

- Milestone: {m}
- Phase: phase1
- Goal: A demonstrable increment.
- Entry criteria: none
- Exit criteria: The increment can be shown.
- Checkpoint: none

"""


def decisions_table(rows: list[tuple[str, str, str]]) -> str:
    lines = ["| ID | Decision | Open question | Affected packages | Status | Resolved in |",
             "|---|---|---|---|---|---|"]
    for did, affected, status in rows:
        resolved = "V3 §4" if status == "RESOLVED" else "—"
        lines.append(f"| {did} | Decision {did} | What exactly? | {affected} | {status} | {resolved} |")
    return "\n".join(lines) + "\n"


class Plan:
    def __init__(self, root: Path):
        self.root = root
        (root / "docs/tasks/handoffs").mkdir(parents=True)
        (root / ".agents/templates").mkdir(parents=True)
        (root / ".agents/templates/handoff.md").write_text("# Handoff\n")
        (root / "AGENTS.md").write_text("# Agents\n")
        (root / "docs/solution.md").write_text("# Solution\nStatus: Approved — Technical Solution V2\n")
        self.authorized: list[str] = []
        self.milestones: dict[str, str] = {}
        self.decisions: list[tuple[str, str, str]] = []

    def milestone(self, m: str, *packages: str) -> None:
        self.milestones[m] = HEADER.format(m=m) + "\n".join(packages)

    def write(self) -> None:
        index = (SKILL / "assets/plan-index-template.md").read_text(encoding="utf-8")
        head, section, tail = index.partition("## Blocking Decisions")
        separator = "|---|---|---|---|---|---|\n"
        at = tail.index(separator) + len(separator)
        rows = "".join(line + "\n" for line in decisions_table(self.decisions).splitlines()[2:])
        (self.root / "docs/tasks/README.md").write_text(head + section + tail[:at] + rows + tail[at:], encoding="utf-8")
        for m, text in self.milestones.items():
            (self.root / f"docs/tasks/{m}.md").write_text(text, encoding="utf-8")
        adapter = json.loads((SKILL / "assets/delivery-workflow.template.json").read_text(encoding="utf-8"))
        adapter["delivery"]["milestone_files"] = {m: f"docs/tasks/{m}.md" for m in self.milestones}
        adapter["delivery"]["authorized_milestones"] = self.authorized
        adapter["hard_rules"] = ["Read only (source: docs/solution.md §5)"]
        adapter["architecture_change_triggers"] = ["Service boundaries (source: docs/solution.md §3)"]
        (self.root / ".agents/delivery-workflow.json").write_text(json.dumps(adapter), encoding="utf-8")

    def check(self, *extra: str) -> dict:
        self.write()
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo", str(self.root),
                               "--skip-adapter-check", *extra], capture_output=True, text=True)
        return json.loads(done.stdout)


def full(wid, status="BLOCKED", deps="none"):
    return FULL.format(id=wid, title=f"Package {wid}", status=status, deps=deps)


def partial(wid, decision, status="BLOCKED", deps=None):
    return PARTIAL.format(id=wid, title=f"Package {wid}", status=status,
                          deps=deps or f"DECISION: {decision}", decision=decision)


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plan = Plan(Path(self.tmp.name))
        self.plan.decisions = [("D1", "M1-2", "OPEN"), ("D2", "M2-1", "OPEN")]
        self.plan.milestone("M1", full("M1-1"), partial("M1-2", "D1", deps="M1-1, DECISION: D1"))
        self.plan.milestone("M2", partial("M2-1", "D2"), full("M2-2"))

    def tearDown(self):
        self.tmp.cleanup()

    def failures(self, result):
        return "\n".join(result["failures"])

    def test_plan_with_open_decisions_passes_and_reports_them(self):
        r = self.plan.check()
        self.assertEqual(r["status"], "PASS", r["failures"])
        self.assertEqual(r["open_decisions"], ["D1", "D2"])
        self.assertEqual(r["milestones_blocked_by_decisions"], ["M1", "M2"])

    def test_authorizing_a_milestone_with_an_open_decision_fails(self):
        self.plan.authorized = ["M1"]
        self.assertIn("authorized while decision D1 is OPEN", self.failures(self.plan.check()))

    def test_unknown_decision_fails(self):
        self.plan.milestone("M2", partial("M2-1", "D9"), full("M2-2"))
        self.assertIn("DECISION D9, which is not in the Blocking Decisions table", self.failures(self.plan.check()))

    def test_package_still_tied_to_resolved_decision_fails(self):
        self.plan.decisions[0] = ("D1", "M1-2", "RESOLVED")
        self.assertIn("still depends on RESOLVED decision D1", self.failures(self.plan.check()))

    def test_package_on_open_decision_must_stay_blocked(self):
        self.plan.milestone("M1", full("M1-1"), partial("M1-2", "D1", status="READY", deps="M1-1, DECISION: D1"))
        self.assertIn("while decision D1 is OPEN; it must stay BLOCKED", self.failures(self.plan.check()))

    def test_resolved_decision_requires_the_full_package(self):
        self.plan.decisions[0] = ("D1", "M1-2", "RESOLVED")
        self.plan.milestone("M1", full("M1-1"), partial("M1-2", "D1", deps="M1-1"))
        self.assertIn("M1-2: missing field Acceptance criteria", self.failures(self.plan.check()))

    def test_resolution_completed_passes(self):
        self.plan.decisions[0] = ("D1", "M1-2", "RESOLVED")
        self.plan.milestone("M1", full("M1-1"), full("M1-2", deps="M1-1"))
        r = self.plan.check()
        self.assertEqual(r["status"], "PASS", r["failures"])
        self.assertEqual(r["open_decisions"], ["D2"])
        self.assertEqual(r["milestones_blocked_by_decisions"], ["M2"])

    def test_unreferenced_open_decision_warns(self):
        self.plan.decisions.append(("D3", "M2-2", "OPEN"))
        self.assertIn("decision D3 is OPEN but no package depends on it", "\n".join(self.plan.check()["warnings"]))

    def test_index_must_list_every_dependent(self):
        self.plan.decisions[1] = ("D2", "—", "OPEN")
        self.assertIn("decision D2: affected packages does not list M2-1", "\n".join(self.plan.check()["warnings"]))

    def test_invalid_decision_status_fails(self):
        self.plan.decisions[1] = ("D2", "M2-1", "PENDING")
        self.assertIn("decision D2: invalid Status", self.failures(self.plan.check()))

    def test_partial_package_without_decision_fails(self):
        self.plan.milestone("M2", partial("M2-1", "D2", deps="none"), full("M2-2"))
        self.assertIn("M2-1: missing field Acceptance criteria", self.failures(self.plan.check()))

    def test_open_decision_words_still_fail(self):
        self.plan.milestone("M2", partial("M2-1", "D2").replace("is D2.", "is 待定."), full("M2-2"))
        self.assertIn("open decision marker '待定'", self.failures(self.plan.check()))


class OwnershipTests(unittest.TestCase):
    def test_foreign_plan_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = Plan(Path(tmp))
            plan.milestone("S0", "| WP | Status |\n|---|---|\n| S0-01 | DONE |\n")
            plan.write()
            (plan.root / "docs/tasks/README.md").write_text("# Project ledger\n")
            done = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo", tmp, "--skip-adapter-check"],
                                  capture_output=True, text=True)
            r = json.loads(done.stdout)
            self.assertEqual(r["status"], "PASS", r["failures"])
            self.assertEqual(r["plan_owner"], "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
