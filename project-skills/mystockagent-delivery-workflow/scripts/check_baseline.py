#!/usr/bin/env python3
"""Validate and fingerprint the approved delivery baseline without modifying it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import sys


BASELINE_MANIFEST_VERSION = "mystockagent-baseline-context-v2"

BASELINE_CONTEXT_FILES = [
    "AGENTS.md",
    "docs/versions/v3.2/README.md",
    "docs/versions/v3.2/REQUIREMENTS.md",
    "docs/versions/v3.2/REQUIREMENT_INHERITANCE.md",
    "docs/versions/v3.2/TECHNICAL_SOLUTION.md",
    "docs/versions/v3.2/MIGRATION_STATUS.md",
    "docs/versions/v3.2/DELIVERY_GATES.md",
    "docs/versions/v3.2/ARCHITECTURE.md",
    "docs/versions/v3.2/SECURITY.md",
    "docs/versions/v3.2/TESTING.md",
    "docs/versions/v3.2/IMPLEMENTATION_PLAN.md",
    "docs/versions/v3.2/WORK_PACKAGES.md",
    "docs/versions/v3.2/agent-coder/README.md",
    ".agents/skills/mystockagent-delivery-workflow/SKILL.md",
    ".agents/delivery-workflow.json",
    "docs/ARCHITECTURE.md",
    "docs/CODING_STANDARDS.md",
    "docs/SECURITY.md",
    "docs/TESTING.md",
    ".agents/skills/technical-solution-workflow/SKILL.md",
    ".agents/skills/coding-standards/SKILL.md",
]

DELIVERY_SUPPORT_FILES = [
    *[f"docs/versions/v3.2/agent-coder/S{i}.md" for i in range(8)],
    ".agents/skills/mystockagent-delivery-workflow/agents/openai.yaml",
    ".agents/skills/mystockagent-delivery-workflow/references/repository-map.md",
    ".agents/skills/mystockagent-delivery-workflow/assets/work-package-handoff.md",
]

REQUIRED_FILES = list(dict.fromkeys([*BASELINE_CONTEXT_FILES, *DELIVERY_SUPPORT_FILES]))


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[4]
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=default_root)
    return parser.parse_args()


def require_text(path: Path, expected: str, failures: list[str]) -> None:
    if expected not in path.read_text(encoding="utf-8"):
        failures.append(f"{path}: missing expected text {expected!r}")


def compute_files_sha256(root: Path, relative_paths: list[str]) -> str:
    """Hash a canonical, path-bound manifest of repository file bytes."""
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError("baseline file list contains duplicates")

    entries: list[dict[str, str]] = []
    for relative in sorted(relative_paths):
        normalized = PurePosixPath(relative)
        if normalized.is_absolute() or ".." in normalized.parts or str(normalized) != relative:
            raise ValueError(f"invalid repository-relative path: {relative!r}")
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        entries.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )

    manifest = {
        "format": BASELINE_MANIFEST_VERSION,
        "files": entries,
    }
    canonical = json.dumps(
        manifest,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def main() -> int:
    root = parse_args().repo.resolve()
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            failures.append(f"missing required file: {relative}")

    if not failures:
        require_text(root / "AGENTS.md", "## Active Development Baseline", failures)
        require_text(root / "AGENTS.md", "## Same-Work-Package Resume", failures)
        require_text(
            root / ".agents/skills/mystockagent-delivery-workflow/SKILL.md",
            "baseline_sha256",
            failures,
        )
        require_text(
            root / "docs/versions/v3.2/TECHNICAL_SOLUTION.md",
            "状态：Approved Development Baseline",
            failures,
        )
        require_text(
            root / "docs/versions/v3.2/DELIVERY_GATES.md",
            "G1-E2E-001",
            failures,
        )
        require_text(
            root / "docs/versions/v3.2/REQUIREMENT_INHERITANCE.md",
            "没有删除 V3.1 的任何产品目标或安全底线",
            failures,
        )
        require_text(
            root / "docs/versions/v3.2/agent-coder/S1.md",
            "初始状态：`BLOCKED`",
            failures,
        )

    baseline_sha256: str | None = None
    if not failures:
        try:
            baseline_sha256 = compute_files_sha256(root, BASELINE_CONTEXT_FILES)
        except (OSError, ValueError) as error:
            failures.append(f"baseline fingerprint failed: {error}")

    result = {
        "repo": str(root),
        "baseline": "MyStockAgent V3.2",
        "required_files": len(REQUIRED_FILES),
        "baseline_manifest_version": BASELINE_MANIFEST_VERSION,
        "baseline_files": len(BASELINE_CONTEXT_FILES),
        "baseline_sha256": baseline_sha256,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
