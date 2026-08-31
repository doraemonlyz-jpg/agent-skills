#!/usr/bin/env python3
"""Tests for deterministic delivery baseline fingerprinting."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).with_name("check_baseline.py")
SPEC = importlib.util.spec_from_file_location("check_baseline", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load check_baseline.py")
CHECK_BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_BASELINE)


class BaselineFingerprintTests(unittest.TestCase):
    def test_fingerprint_is_deterministic_and_content_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.md").write_bytes(b"alpha\n")
            (root / "two.md").write_bytes(b"beta\n")
            paths = ["one.md", "two.md"]

            first = CHECK_BASELINE.compute_files_sha256(root, paths)
            second = CHECK_BASELINE.compute_files_sha256(root, paths)
            self.assertEqual(first, second)
            self.assertRegex(first, r"^[0-9a-f]{64}$")

            (root / "two.md").write_bytes(b"changed\n")
            self.assertNotEqual(first, CHECK_BASELINE.compute_files_sha256(root, paths))

    def test_fingerprint_binds_paths_but_not_input_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.md").write_bytes(b"alpha")
            (root / "two.md").write_bytes(b"beta")

            forward = CHECK_BASELINE.compute_files_sha256(root, ["one.md", "two.md"])
            reverse = CHECK_BASELINE.compute_files_sha256(root, ["two.md", "one.md"])
            self.assertEqual(forward, reverse)

            (root / "one.md").write_bytes(b"beta")
            (root / "two.md").write_bytes(b"alpha")
            self.assertNotEqual(forward, CHECK_BASELINE.compute_files_sha256(root, ["one.md", "two.md"]))

    def test_fingerprint_rejects_duplicate_or_missing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.md").write_bytes(b"alpha")

            with self.assertRaises(ValueError):
                CHECK_BASELINE.compute_files_sha256(root, ["one.md", "one.md"])
            with self.assertRaises(FileNotFoundError):
                CHECK_BASELINE.compute_files_sha256(root, ["missing.md"])

    def test_repository_output_includes_baseline_fingerprint(self) -> None:
        repository = SCRIPT_PATH.parents[4]
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--repo", str(repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["status"], "PASS")
        self.assertRegex(result["baseline_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(result["baseline"], "MyStockAgent V3.2")
        self.assertEqual(result["baseline_manifest_version"], "mystockagent-baseline-context-v2")
        self.assertEqual(result["baseline_files"], 21)


if __name__ == "__main__":
    unittest.main()
