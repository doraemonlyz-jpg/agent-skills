#!/usr/bin/env python3
"""Release agent skills and keep the local agents in step.

Everything is taken from the last commit (HEAD), never from uncommitted edits:
run the skills' tests, optionally tag a release, sync every skill to the local
agents, and build the Claude plugin package.

Usage:
  setup/release.py <skill>          tag <skill> at its SKILL.md version, then sync
  setup/release.py --sync           sync all skills and rebuild the plugin, no tag
  setup/release.py --install-hook   sync automatically after every commit or pull on main

Options:
  --push      also push the current branch and the new tag to origin
  --dry-run   show what would happen without changing anything
  --quiet     print a one-line summary (used by the git hook)

Environment (for tests or unusual setups):
  SKILL_TARGETS      label=path pairs separated by ':'. Default:
                     codex=$CODEX_HOME/skills (or ~/.codex/skills) and
                     smartwork=~/.SmartWork/skills; missing paths are skipped.
  AGENTS_SKILLS_DIR  shared skills directory Codex also reads
                     (default ~/.agents/skills). A skill found there is not
                     copied into the codex target, to avoid duplicates.

Standard library only; works with the macOS system python3.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
SKIP_NAMES = {"__pycache__", ".DS_Store"}
HOOK_BEGIN = "# >>> agent-skills sync >>>"
HOOK_END = "# <<< agent-skills sync <<<"
HOOK_BLOCK = f"""{HOOK_BEGIN}
# Sync skills to the local agents after each commit or pull on main.
# Installed by setup/release.py --install-hook; delete this block to stop.
if [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "main" ]; then
  python3 "$(git rev-parse --show-toplevel)/setup/release.py" --sync --quiet || true
fi
{HOOK_END}
"""


class ReleaseError(Exception):
    pass


def git(*args: str, check: bool = True) -> str:
    done = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if check and done.returncode != 0:
        raise ReleaseError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout.strip()


def export_head(tmp: Path) -> Path:
    """Extract skills/ as committed in HEAD, so uncommitted edits never ship."""
    archive = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", "HEAD", "skills"],
                             capture_output=True)
    if archive.returncode != 0:
        raise ReleaseError("git archive failed: " + archive.stderr.decode(errors="replace").strip())
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(tmp, filter="data")
        else:  # older Pythons, e.g. the macOS system python3
            tar.extractall(tmp)
    return tmp / "skills"


def frontmatter(skill_dir: Path) -> dict[str, str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ReleaseError(f"{skill_dir.name}: SKILL.md has no frontmatter")
    fields = {}
    for key, pattern in (("name", r"^name:\s*(.+)$"), ("description", r"^description:\s*(.+)$"),
                         ("version", r"^\s+version:\s*(.+)$")):
        found = re.search(pattern, match.group(1), re.M)
        if found:
            fields[key] = found.group(1).strip().strip("\"'")
    return fields


def skill_dirs(root: Path) -> list[Path]:
    skills = sorted(p for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    for path in skills:
        meta = frontmatter(path)
        if meta.get("name") != path.name:
            raise ReleaseError(f"{path.name}: frontmatter name {meta.get('name')!r} does not match the folder")
        if not meta.get("description"):
            raise ReleaseError(f"{path.name}: frontmatter has no description")
    return skills


def run_tests(skills: list[Path]) -> list[str]:
    results = []
    for test in sorted(t for path in skills for t in (path / "scripts").glob("test_*.py")):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        done = subprocess.run([sys.executable, "-B", str(test)], capture_output=True, text=True, env=env)
        rel = f"{test.parent.parent.name}/scripts/{test.name}"
        if done.returncode != 0:
            raise ReleaseError(f"tests failed: {rel}\n{(done.stdout + done.stderr)[-1500:]}")
        results.append(rel)
    return results


def changelog_title(path: Path, version: str) -> str:
    changelog = path / "CHANGELOG.md"
    if not changelog.is_file():
        raise ReleaseError(f"{path.name}: no CHANGELOG.md")
    for line in changelog.read_text(encoding="utf-8").splitlines():
        if re.match(rf"^##\s+{re.escape(version)}(\s|$)", line):
            parts = [p.strip() for p in line[2:].split("—")]
            return parts[-1] if len(parts) >= 3 else ""
    raise ReleaseError(f"{path.name}: CHANGELOG.md has no '## {version}' entry")


def plan_tag(path: Path) -> tuple[str, str | None]:
    """Return the tag name and its message, or None when the tag is already on HEAD."""
    version = frontmatter(path).get("version")
    if not version:
        raise ReleaseError(f"{path.name} has no metadata.version; add one, or run with --sync")
    title = changelog_title(path, version)
    tag = f"{path.name}/v{version}"
    existing = git("rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", check=False)
    if existing and existing != git("rev-parse", "HEAD"):
        raise ReleaseError(f"tag {tag} already exists on another commit; bump the version")
    if existing:
        return tag, None
    return tag, f"{path.name} {version}" + (f" — {title}" if title else "")


def targets() -> list[tuple[str, Path]]:
    raw = os.environ.get("SKILL_TARGETS")
    if raw:
        pairs = [item.split("=", 1) for item in raw.split(":") if item]
    else:
        codex = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"
        pairs = [("codex", str(codex)), ("smartwork", str(Path.home() / ".SmartWork" / "skills"))]
    return [(label, Path(path).expanduser()) for label, path in pairs if Path(path).expanduser().is_dir()]


def digest(root: Path) -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not SKIP_NAMES.intersection(path.parts) and path.suffix != ".pyc":
            files[str(path.relative_to(root))] = hashlib.sha1(path.read_bytes()).hexdigest()
    return files


def sync(skills: list[Path], dry_run: bool) -> list[tuple[str, str, str]]:
    shared = Path(os.environ.get("AGENTS_SKILLS_DIR", Path.home() / ".agents" / "skills")).expanduser()
    report = []
    for label, root in targets():
        for path in skills:
            dest = root / path.name
            link = shared / path.name
            if label == "codex" and (link.is_symlink() or link.exists()):
                duplicate = dest.exists() and not dest.is_symlink()
                report.append((label, path.name, "DUPLICATE: also in ~/.agents/skills, remove one"
                               if duplicate else "provided by ~/.agents/skills"))
                continue
            if dest.is_symlink():
                report.append((label, path.name, "linked, left alone"))
                continue
            if dest.exists():
                if not (dest / "SKILL.md").is_file() or frontmatter(dest).get("name") != path.name:
                    report.append((label, path.name, "SKIPPED: existing folder is a different skill"))
                    continue
                if digest(dest) == digest(path):
                    report.append((label, path.name, "up to date"))
                    continue
                action = "updated"
            else:
                action = "installed"
            if not dry_run:
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(path, dest, ignore=IGNORE)
            report.append((label, path.name, action + (" (dry run)" if dry_run else "")))
    return report


def build_plugin(skills: list[Path], dry_run: bool) -> str:
    version = f"0.{git('rev-list', '--count', 'HEAD')}.0"
    out = DIST / "agent-skills.plugin"
    if dry_run:
        return f"would build dist/agent-skills.plugin (version {version})"
    manifest = {
        "name": "agent-skills",
        "version": version,
        "description": "Engineering delivery workflow for coding agents: standards bootstrap, spec interview, "
                       "technical solution with approval gate, delivery planning, gated execution, coding "
                       "standards, and context handoff.",
        "author": {"name": "DL"},
        "keywords": ["engineering", "workflow", "delivery", "coding-standards"],
    }
    DIST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "agent-skills"
        (root / ".claude-plugin").mkdir(parents=True)
        (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        readme = subprocess.run(["git", "-C", str(REPO), "show", "HEAD:README.md"], capture_output=True)
        (root / "README.md").write_bytes(readme.stdout)
        for path in skills:
            shutil.copytree(path, root / "skills" / path.name, ignore=IGNORE)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(root.rglob("*")):
                if file.is_file():
                    archive.write(file, str(file.relative_to(root)))
    return f"built dist/agent-skills.plugin (version {version}, {len(skills)} skills)"


def untagged(skills: list[Path]) -> list[str]:
    tags = set(git("tag", "-l").splitlines())
    return [f"{p.name} {v}" for p in skills
            if (v := frontmatter(p).get("version")) and f"{p.name}/v{v}" not in tags]


def install_hook() -> list[str]:
    hooks = Path(git("rev-parse", "--git-path", "hooks"))
    hooks = hooks if hooks.is_absolute() else REPO / hooks
    hooks.mkdir(parents=True, exist_ok=True)
    report = []
    for name in ("post-commit", "post-merge"):
        hook = hooks / name
        text = hook.read_text(encoding="utf-8") if hook.exists() else "#!/bin/sh\n"
        if HOOK_BEGIN in text:
            report.append(f"{name}: already installed")
            continue
        # Insert right after the shebang: other hooks here may `source` scripts
        # that exit early, which would skip a block appended at the end.
        first, _, rest = text.partition("\n") if text.startswith("#!") else ("#!/bin/sh", "", text)
        hook.write_text(first + "\n" + HOOK_BLOCK + rest, encoding="utf-8")
        hook.chmod(hook.stat().st_mode | 0o755)
        report.append(f"{name}: installed")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Release agent skills.")
    parser.add_argument("skill", nargs="?", help="skill to tag, e.g. delivery-plan-bootstrap")
    parser.add_argument("--sync", action="store_true", help="sync and rebuild the plugin without tagging")
    parser.add_argument("--install-hook", action="store_true", help="sync automatically after commits and pulls on main")
    parser.add_argument("--push", action="store_true", help="push the branch and the new tag to origin")
    parser.add_argument("--dry-run", action="store_true", help="change nothing")
    parser.add_argument("--quiet", action="store_true", help="one-line summary")
    args = parser.parse_args()

    try:
        if args.install_hook:
            for line in install_hook():
                print(line)
            print("From now on, every commit or pull on main syncs the skills automatically.")
            return 0
        if bool(args.skill) == args.sync:
            parser.error("give a skill to release, --sync, or --install-hook")

        with tempfile.TemporaryDirectory() as tmp:
            skills = skill_dirs(export_head(Path(tmp)))
            notes = []
            if git("status", "--porcelain", "--untracked-files=all", "--", "skills"):
                notes.append("warning: skills/ has uncommitted changes; they are not included")
            branch = git("rev-parse", "--abbrev-ref", "HEAD")
            if branch != "main":
                notes.append(f"warning: on branch {branch}, not main")

            release = None
            if args.skill:
                path = next((p for p in skills if p.name == args.skill), None)
                if path is None:
                    raise ReleaseError(f"no skill named {args.skill!r} in the last commit")
                release = plan_tag(path)

            tests = run_tests(skills)

            tag_line = ""
            if release:
                tag, message = release
                if message is None:
                    tag_line = f"tag: {tag} already on HEAD"
                elif args.dry_run:
                    tag_line = f"tag: would create {tag}"
                else:
                    git("tag", "-a", tag, "-m", message)
                    tag_line = f"tag: created {tag}"

            report = sync(skills, args.dry_run)
            plugin = build_plugin(skills, args.dry_run)

            push_line = "push: not pushed; run with --push, or push from VS Code"
            if args.push:
                if args.dry_run:
                    push_line = "push: would push the branch" + (" and the tag" if release else "")
                else:
                    git("push", "origin", "HEAD")
                    if release:
                        git("push", "origin", release[0])
                    push_line = "push: done"

            changed = [r for r in report if r[2].startswith(("updated", "installed"))]
            problems = [r for r in report if r[2].startswith(("DUPLICATE", "SKIPPED"))]
            if args.quiet:
                labels = sorted({r[0] for r in report}) or ["no targets"]
                print(f"agent-skills: {len(skills)} skills synced to {', '.join(labels)}; "
                      f"{len(changed)} changed" + (f"; {tag_line}" if tag_line else ""))
                for note in notes:
                    print("agent-skills: " + note)
                for label, name, status in problems:
                    print(f"agent-skills: {label} {name}: {status}")
                return 0

            print(f"repo: {REPO}  branch: {branch}  HEAD: {git('rev-parse', '--short', 'HEAD')}")
            for note in notes:
                print(note)
            print("tests: " + (", ".join(tests) + " passed" if tests else "none found"))
            if tag_line:
                print(tag_line)
            print("sync:")
            for label, name, status in report or [("-", "-", "no targets found")]:
                print(f"  {label:10s} {name:42s} {status}")
            print("plugin: " + plugin)
            print(push_line)
            pending = untagged(skills)
            if pending:
                print("untagged current versions: " + ", ".join(pending))
            print("next: start a new agent session to load updated skills; "
                  "install dist/agent-skills.plugin in Claude when it changed.")
            return 0
    except ReleaseError as error:
        text = str(error)
        if args.quiet:  # keep the git hook output short
            lines = [line for line in text.splitlines() if line.strip()]
            text = lines[0] + (f" ({lines[-1].strip()})" if len(lines) > 1 else "")
        print(f"agent-skills release stopped: {text}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
