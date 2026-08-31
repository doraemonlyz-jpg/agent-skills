#!/usr/bin/env python3
"""Validate a repository gated-delivery adapter and optional task authorization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--task")
    parser.add_argument("--run-preflight", action="store_true")
    return parser.parse_args()


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def need(mapping: dict[str, Any], key: str, where: str, failures: list[str]) -> Any:
    if key not in mapping:
        fail(f"{where}: missing {key}", failures)
        return None
    return mapping[key]


def main() -> int:
    args = arguments()
    root = args.repo.resolve()
    adapter_path = root / ".agents/delivery-workflow.json"
    failures: list[str] = []

    if not adapter_path.is_file():
        print(json.dumps({"status": "FAIL", "failures": [f"missing {adapter_path}"]}, indent=2))
        return 1

    try:
        config = json.loads(adapter_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "failures": [str(exc)]}, indent=2))
        return 1

    if config.get("schema_version") != 1:
        fail("schema_version must be 1", failures)

    project = need(config, "project", "root", failures)
    baseline = need(config, "baseline", "root", failures) or {}
    delivery = need(config, "delivery", "root", failures) or {}
    preflight = need(config, "preflight", "root", failures) or {}
    verification = need(config, "verification", "root", failures) or {}
    hard_rules = need(config, "hard_rules", "root", failures)
    triggers = need(config, "architecture_change_triggers", "root", failures)

    if baseline.get("status") != "approved":
        fail("baseline.status must be approved", failures)

    documents = baseline.get("required_documents", [])
    if not documents:
        fail("baseline.required_documents must not be empty", failures)
    for relative in documents:
        if not (root / relative).is_file():
            fail(f"missing required document: {relative}", failures)

    for relative, markers in baseline.get("required_markers", {}).items():
        path = root / relative
        if not path.is_file():
            fail(f"marker file missing: {relative}", failures)
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                fail(f"{relative}: missing marker {marker!r}", failures)

    milestones = delivery.get("milestone_files", {})
    authorized = delivery.get("authorized_milestones", [])
    for milestone, relative in milestones.items():
        if not (root / relative).is_file():
            fail(f"{milestone}: missing milestone file {relative}", failures)

    for milestone in authorized:
        if milestone not in milestones:
            fail(f"authorized milestone has no file: {milestone}", failures)

    commands = preflight.get("commands", [])
    if not isinstance(commands, list):
        fail("preflight.commands must be a list", failures)
        commands = []

    if not verification.get("commands"):
        fail("verification.commands must not be empty", failures)
    handoff = verification.get("handoff_template")
    if handoff and not (root / handoff).is_file():
        fail(f"missing handoff template: {handoff}", failures)
    if not hard_rules:
        fail("hard_rules must not be empty", failures)
    if not triggers:
        fail("architecture_change_triggers must not be empty", failures)

    task_result: dict[str, Any] | None = None
    if args.task:
        pattern = delivery.get("task_id_pattern", "")
        if not pattern or re.fullmatch(pattern, args.task) is None:
            fail(f"task does not match task_id_pattern: {args.task}", failures)
        milestone = args.task.split("-", 1)[0]
        if milestone not in authorized:
            fail(f"task milestone is not authorized: {milestone}", failures)
        task_result = {
            "task": args.task,
            "milestone": milestone,
            "authorized": milestone in authorized,
            "milestone_file": milestones.get(milestone),
        }

    preflight_results: list[dict[str, Any]] = []
    if args.run_preflight and not failures:
        for command in commands:
            completed = subprocess.run(
                shlex.split(command),
                cwd=root,
                shell=False,
                text=True,
                capture_output=True,
            )
            preflight_results.append(
                {
                    "command": command,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout[-2000:],
                    "stderr": completed.stderr[-2000:],
                }
            )
            if completed.returncode != 0:
                fail(f"preflight command failed: {command}", failures)

    result = {
        "status": "PASS" if not failures else "FAIL",
        "project": project,
        "baseline": baseline.get("name"),
        "current_phase": delivery.get("current_phase"),
        "authorized_milestones": authorized,
        "task": task_result,
        "preflight": preflight_results,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
