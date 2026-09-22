#!/usr/bin/env python3
"""Validate milestone files and the Work Package graph of a gated delivery plan.

Also runs gated-delivery-workflow's inspect_delivery_config.py when it is
installed next to this skill, so one command checks the whole plan.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

STATUSES = {"BLOCKED", "READY", "IN_PROGRESS", "VERIFYING", "DONE", "FAILED", "ARCH_REVIEW", "DROPPED"}
REQUIRED = ["Status", "Depends on", "Goal", "Why", "Acceptance criteria", "How to check", "Required tests",
            "Scope", "Solution refs", "Non-goals"]
NON_EMPTY = ["Goal", "Why", "How to check", "Required tests", "Scope", "Solution refs", "Non-goals"]
# A package blocked by an open decision may leave out what hinges on the answer.
BLOCKED_REQUIRED = ["Status", "Depends on", "Goal", "Why", "Scope", "Solution refs"]
DECISION_STATUSES = {"OPEN", "RESOLVED"}
HEADER_FIELDS = ["Milestone", "Phase", "Goal", "Exit criteria"]
HEADING = re.compile(r"^##\s+(\S+)\s+[—–-]+\s+(.+?)\s*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z -]*?):\s*(.*)$")
ITEM = re.compile(r"^\s{2,}-\s+(.+)$")
EMPTY = {"", "—", "-", "tbd", "todo"}
OPEN_DECISION = re.compile(r"\b(TBD|TODO|to be decided|decide during implementation|open question)\b|待定|待确认|未决|待讨论", re.I)
PLACEHOLDER = re.compile(r"<[a-z][^<>\n]*>")
PINNED = re.compile(r"\bV\d+(?:\.\d+)*\b|@[0-9a-f]{7,}|\bversion\b", re.I)
REQUIREMENT_ID = re.compile(r"\b[A-Z]{2,5}-\d+\b")
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
MAX_WORDS = 700
MAX_CRITERIA = 7


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--summary", action="store_true", help="include a per-package status table")
    parser.add_argument("--skip-adapter-check", action="store_true")
    parser.add_argument("--strict", action="store_true",
                        help="enforce the milestone format even if docs/tasks/README.md does not name delivery-plan-bootstrap")
    return parser.parse_args()


def parse_milestone(path: Path) -> tuple[dict[str, str], list[dict[str, Any]]]:
    header: dict[str, str] = {}
    packages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    last_key: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        heading = HEADING.match(line)
        if heading:
            current = {"id": heading.group(1), "title": heading.group(2), "line": number, "fields": {}, "items": {},
                       "text": [line]}
            packages.append(current)
            last_key = None
            continue
        if current is not None:
            current["text"].append(line)
        else:
            header.setdefault("__text__", "")
            header["__text__"] += line + "\n"
        field = FIELD.match(line)
        if field:
            key, value = field.group(1).strip(), field.group(2).strip()
            target = current["fields"] if current else header
            target[key] = value
            last_key = key
            continue
        item = ITEM.match(line)
        if item and current is not None and last_key:
            current["items"].setdefault(last_key, []).append(item.group(1).strip())
    return header, packages


def has_value(wp: dict[str, Any], key: str) -> bool:
    inline = wp["fields"].get(key, "").strip().lower() not in EMPTY
    return inline or bool(wp["items"].get(key))


def size_in_words(text: str) -> int:
    """Latin words plus CJK characters counted two per word."""
    cjk = len(CJK.findall(text))
    latin = len(CJK.sub(" ", text).split())
    return latin + cjk // 2


def split_deps(value: str) -> tuple[list[str], list[str], list[str]]:
    """Split a Depends on value into package IDs, EXT items, and decision IDs."""
    if value.strip().lower() in {"none", ""}:
        return [], [], []
    ids, external, decisions = [], [], []
    for part in (p.strip() for p in value.split(",")):
        if not part:
            continue
        upper = part.upper()
        if upper.startswith("EXT:"):
            external.append(part)
        elif upper.startswith("DECISION:"):
            decisions.append(part.split(":", 1)[1].strip())
        else:
            ids.append(part)
    return ids, external, decisions


def parse_decisions(index_text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Read the Blocking Decisions table from the plan index."""
    decisions: dict[str, dict[str, str]] = {}
    problems: list[str] = []
    lines = index_text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().lower().startswith("## blocking decisions"))
    except StopIteration:
        return decisions, problems
    header: list[str] | None = None
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        did = row.get("id", "").strip("`")
        if not did:
            continue
        status = (row.get("status", "").split() or [""])[0].upper()
        if status not in DECISION_STATUSES:
            problems.append(f"decision {did}: invalid Status {row.get('status', '')!r} (use OPEN or RESOLVED)")
        if did in decisions:
            problems.append(f"decision {did}: duplicate ID in Blocking Decisions")
        row["status"] = status
        decisions[did] = row
    return decisions, problems


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if nxt in graph and state.get(nxt) is None:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in graph:
        if state.get(node) is None:
            found = visit(node)
            if found:
                return found
    return None


def run_adapter_check(root: Path) -> dict[str, Any] | None:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent / "gated-delivery-workflow/scripts/inspect_delivery_config.py",
        Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills/gated-delivery-workflow/scripts/inspect_delivery_config.py",
    ]
    script = next((c for c in candidates if c.is_file()), None)
    if script is None:
        return None
    done = subprocess.run([sys.executable, str(script), "--repo", str(root)], text=True, capture_output=True)
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"status": "FAIL", "failures": [done.stderr.strip() or done.stdout.strip()]}


def main() -> int:
    args = arguments()
    root = args.repo.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    adapter_path = root / ".agents/delivery-workflow.json"
    if not adapter_path.is_file():
        print(json.dumps({"status": "FAIL", "failures": [f"missing {adapter_path}"]}, indent=2))
        return 1
    try:
        config = json.loads(adapter_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "failures": [str(exc)]}, indent=2))
        return 1

    delivery = config.get("delivery", {})
    milestone_files: dict[str, str] = delivery.get("milestone_files", {})
    authorized: list[str] = delivery.get("authorized_milestones", [])
    pattern = delivery.get("task_id_pattern") or r"^M[0-9]+-[0-9]+$"
    order = {m: i for i, m in enumerate(milestone_files)}

    index_path = root / "docs/tasks/README.md"
    owned = index_path.is_file() and "delivery-plan-bootstrap" in index_path.read_text(encoding="utf-8", errors="replace")
    checked_files = milestone_files if (owned or args.strict) else {}
    decisions: dict[str, dict[str, str]] = {}
    if checked_files and index_path.is_file():
        decisions, decision_problems = parse_decisions(index_path.read_text(encoding="utf-8", errors="replace"))
        failures.extend(decision_problems)
    if not checked_files and milestone_files:
        warnings.append("plan not created by delivery-plan-bootstrap (docs/tasks/README.md missing or does not name it); "
                        "milestone format checks skipped, adapter check only; use --strict to force")

    packages: dict[str, dict[str, Any]] = {}
    for milestone, relative in checked_files.items():
        where = relative
        if "-" in milestone:
            failures.append(f"{milestone}: milestone ID must not contain a hyphen")
        path = root / relative
        if not path.is_file():
            failures.append(f"{milestone}: missing milestone file {relative}")
            continue
        header, items = parse_milestone(path)
        header_text = header.pop("__text__", "")
        if PLACEHOLDER.search(header_text):
            failures.append(f"{where}: header has an unfilled template placeholder")
        for key in HEADER_FIELDS:
            if header.get(key, "").strip().lower() in EMPTY:
                failures.append(f"{where}: header missing {key}")
        if header.get("Milestone") and header["Milestone"] != milestone:
            failures.append(f"{where}: header Milestone {header['Milestone']!r} != adapter key {milestone!r}")
        if not items:
            failures.append(f"{where}: no Work Packages")
        elif len(items) == 1:
            warnings.append(f"{where}: only one Work Package; consider merging the milestone")
        elif len(items) > 10:
            warnings.append(f"{where}: {len(items)} Work Packages; may hide two milestones")
        for wp in items:
            wid, loc = wp["id"], f"{where}:{wp['line']} {wp['id']}"
            wp["milestone"], wp["file"] = milestone, relative
            if re.fullmatch(pattern, wid) is None:
                failures.append(f"{loc}: ID does not match task_id_pattern {pattern}")
            if wid.split("-", 1)[0] != milestone:
                failures.append(f"{loc}: ID prefix does not match milestone {milestone}")
            if wid in packages:
                failures.append(f"{loc}: duplicate ID (also in {packages[wid]['file']})")
                continue
            packages[wid] = wp
            fields = wp["fields"]
            status_word = fields.get("Status", "").split()[0] if fields.get("Status") else ""
            wp["status"] = status_word
            if not status_word:
                failures.append(f"{loc}: missing field Status")
            elif status_word not in STATUSES:
                failures.append(f"{loc}: invalid Status {status_word!r}")
            if status_word == "DROPPED":
                continue  # a dropped record keeps its history; only Status is required
            _, _, decision_deps = split_deps(fields.get("Depends on", ""))
            open_deps = [d for d in decision_deps if decisions.get(d, {}).get("status") == "OPEN"]
            wp["open_decisions"] = open_deps
            required = BLOCKED_REQUIRED if open_deps else REQUIRED
            for key in required:
                if key not in fields and key != "Status":
                    failures.append(f"{loc}: missing field {key}")
            for key in NON_EMPTY:
                if key in fields and not has_value(wp, key):
                    failures.append(f"{loc}: empty {key}")
            criteria = wp["items"].get("Acceptance criteria", [])
            if not criteria and not open_deps:
                failures.append(f"{loc}: Acceptance criteria needs at least one '  - ' item")
            elif len(criteria) > MAX_CRITERIA:
                warnings.append(f"{loc}: {len(criteria)} acceptance criteria; more than {MAX_CRITERIA} usually means two packages")
            for check in wp["items"].get("How to check", []):
                if "`" not in check and not check.lower().startswith("manual:"):
                    warnings.append(f"{loc}: How to check item is neither a `command` nor 'manual:': {check[:60]!r}")
            text = "\n".join(wp["text"])
            marker = OPEN_DECISION.search(text)
            if marker:
                failures.append(f"{loc}: open decision marker {marker.group(0)!r}; resolve it in "
                                "technical-solution-workflow or list it as a blocking decision")
            if PLACEHOLDER.search(text):
                failures.append(f"{loc}: unfilled template placeholder {PLACEHOLDER.search(text).group(0)!r}")
            refs = fields.get("Solution refs", "")
            if refs and not PINNED.search(refs):
                warnings.append(f"{loc}: Solution refs not pinned to a solution version (e.g. 'Technical Solution V2 §4.2')")
            for key in ("Goal", "Why"):
                found = REQUIREMENT_ID.search(fields.get(key, ""))
                if found:
                    warnings.append(f"{loc}: {key} contains requirement ID {found.group(0)}; move it to Acceptance criteria or Agent notes")
            words = size_in_words(text)
            wp["words"] = words
            if words > MAX_WORDS:
                warnings.append(f"{loc}: about {words} words; past {MAX_WORDS}, split the package or link the shared source")
            if status_word == "DONE":
                evidence = fields.get("Evidence", "").strip().strip("`")
                if evidence.lower() in EMPTY or not (root / evidence).is_file():
                    failures.append(f"{loc}: DONE without an existing Evidence file ({evidence or 'empty'})")
            if status_word in {"READY", "IN_PROGRESS", "VERIFYING", "DONE"} and milestone not in authorized:
                failures.append(f"{loc}: status {status_word} but milestone {milestone} is not authorized")

    graph: dict[str, list[str]] = {}
    for wid, wp in packages.items():
        if wp.get("status") == "DROPPED":
            continue
        ids, external, decision_deps = split_deps(wp["fields"].get("Depends on", ""))
        wp["external"] = external
        graph[wid] = ids
        for did in decision_deps:
            decision = decisions.get(did)
            if decision is None:
                failures.append(f"{wid}: depends on DECISION {did}, which is not in the Blocking Decisions table")
            elif decision["status"] == "RESOLVED":
                failures.append(f"{wid}: still depends on RESOLVED decision {did}; update the package in Replan")
            elif decision["status"] == "OPEN":
                if wp.get("status") != "BLOCKED":
                    failures.append(f"{wid}: status {wp.get('status')} while decision {did} is OPEN; it must stay BLOCKED")
                if wp["milestone"] in authorized:
                    failures.append(f"{wid}: milestone {wp['milestone']} is authorized while decision {did} is OPEN")
                listed = decision.get("affected packages", "")
                if wid not in listed:
                    warnings.append(f"decision {did}: affected packages does not list {wid}")
        for dep in ids:
            target = packages.get(dep)
            if target is None:
                failures.append(f"{wid}: depends on unknown {dep}")
                continue
            if target.get("status") == "DROPPED":
                failures.append(f"{wid}: depends on DROPPED {dep}")
            if order.get(target["milestone"], 0) > order.get(wp["milestone"], 0):
                failures.append(f"{wid}: depends on later milestone package {dep}")
            if wp.get("status") == "READY" and target.get("status") != "DONE":
                failures.append(f"{wid}: READY but dependency {dep} is {target.get('status') or 'unknown'}")
    cycle = find_cycle(graph)
    if cycle:
        failures.append("dependency cycle: " + " -> ".join(cycle))
    referenced = {d for wp in packages.values() for d in wp.get("open_decisions", [])}
    for did, decision in decisions.items():
        if decision["status"] == "OPEN" and did not in referenced:
            warnings.append(f"decision {did} is OPEN but no package depends on it")
    open_decisions = sorted(d for d, v in decisions.items() if v["status"] == "OPEN")
    blocked_milestones = sorted({wp["milestone"] for wp in packages.values() if wp.get("open_decisions")},
                                key=lambda m: order.get(m, 0))

    for index, milestone in enumerate(milestone_files):
        if milestone in authorized:
            earlier = [m for m in list(milestone_files)[:index] if m not in authorized]
            if earlier:
                warnings.append(f"{milestone} authorized while earlier {', '.join(earlier)} are not")
    for milestone in authorized:
        if milestone not in milestone_files:
            failures.append(f"authorized milestone has no file: {milestone}")

    if owned or args.strict:
        if not index_path.is_file():
            warnings.append("missing plan index docs/tasks/README.md")
        if not (root / "docs/tasks/handoffs").is_dir():
            warnings.append("missing docs/tasks/handoffs/ directory")
        for key in ("hard_rules", "architecture_change_triggers"):
            for rule in config.get(key, []):
                if "source:" not in rule.lower():
                    warnings.append(f"{key}: no '(source: …)' citation in {rule!r}")

    adapter = None if args.skip_adapter_check else run_adapter_check(root)
    if adapter is None and not args.skip_adapter_check:
        warnings.append("gated-delivery-workflow inspect_delivery_config.py not found; adapter not checked")
    elif adapter and adapter.get("status") != "PASS":
        failures.extend(f"adapter: {f}" for f in adapter.get("failures", []))

    counts: dict[str, int] = {}
    for wp in packages.values():
        counts[wp.get("status") or "?"] = counts.get(wp.get("status") or "?", 0) + 1
    result: dict[str, Any] = {
        "status": "PASS" if not failures else "FAIL",
        "project": config.get("project"),
        "baseline": config.get("baseline", {}).get("name"),
        "current_phase": delivery.get("current_phase"),
        "milestones": list(milestone_files),
        "authorized_milestones": authorized,
        "plan_owner": "delivery-plan-bootstrap" if owned else "repository",
        "work_packages": len(packages),
        "by_status": counts,
        "external_prerequisites": sorted({e for wp in packages.values() for e in wp.get("external", [])}),
        "open_decisions": open_decisions,
        "milestones_blocked_by_decisions": blocked_milestones,
        "adapter_check": None if adapter is None else adapter.get("status"),
        "failures": failures,
        "warnings": warnings,
    }
    if args.summary:
        result["packages"] = [
            {"id": w, "milestone": p["milestone"], "status": p.get("status"), "title": p["title"],
             "depends_on": graph.get(w, []), "words": p.get("words")}
            for w, p in packages.items()
        ]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
