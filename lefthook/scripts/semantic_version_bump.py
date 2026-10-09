#!/usr/bin/env python3
"""git post-commit hook: bump .semantic_version and tag the release.

Symlinked/wired via lefthook.yml (post-commit) into any project that opts in
by keeping a `.semantic_version` file at its repo root. Language-agnostic: no
Node/npx dependency, works in any git repo (Node, Python, Go, ...).

Behavior:
- No `.semantic_version` file at repo root -> no-op (exit 0). This is the
  opt-in gate: projects that don't want versioning never pay for this hook.
- Not on the main branch (main/master) -> no-op. Feature-branch commits don't
  represent a release.
- Reads the just-made commit's subject, parses its Conventional Commits type
  (and `!`/BREAKING CHANGE marker) to decide the bump: major/minor/patch.
  Non-conforming subjects (e.g. merge commits) are skipped, not bumped.
- Writes the new version (plain text, e.g. "1.2.3") back to
  `.semantic_version` and creates an annotated tag `vX.Y.Z` on HEAD.

The file is both the opt-in marker and the tracked version source, so the
current version is always visible by `cat .semantic_version`, independent of
any language's own manifest (package.json, pyproject.toml, go.mod, ...).

Bypass for a deliberate exception: git commit --no-verify
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys

_VERSION_FILE = ".semantic_version"
_MAIN_BRANCHES = {"main", "master"}

_SUBJECT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)"
    r"(\([^)]+\))?(?P<bang>!)?: .+"
)
_BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE: .+", re.MULTILINE)

_BUMP_BY_TYPE = {"feat": "minor", "fix": "patch"}

_GIT = shutil.which("git") or "git"


def _run_git(*args: str) -> str:
    return subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
        [_GIT, *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _current_branch() -> str:
    return _run_git("rev-parse", "--abbrev-ref", "HEAD")


def _repo_root() -> Path:
    return Path(_run_git("rev-parse", "--show-toplevel"))


def _last_commit_message() -> str:
    return _run_git("log", "-1", "--format=%B")


def _bump_kind(message: str) -> str | None:
    """Decide major/minor/patch/None from a commit message.

    Returns:
        "major", "minor", "patch", or None if the subject doesn't conform to
        Conventional Commits (nothing to bump, e.g. a merge commit).
    """
    subject = message.splitlines()[0] if message else ""
    match = _SUBJECT_PATTERN.match(subject)
    if not match:
        return None
    if match.group("bang") or _BREAKING_FOOTER.search(message):
        return "major"
    return _BUMP_BY_TYPE.get(match.group("type"))


def _apply_bump(version: str, kind: str) -> str:
    major, minor, patch = (int(part) for part in version.split("."))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    """Bump `.semantic_version` and tag HEAD, if this commit warrants it.

    Returns:
        0 always (never blocks a commit that already happened).
    """
    try:
        root = _repo_root()
        version_path = root / _VERSION_FILE
        if not version_path.is_file():
            return 0
        if _current_branch() not in _MAIN_BRANCHES:
            return 0

        kind = _bump_kind(_last_commit_message())
        if kind is None:
            return 0

        current = version_path.read_text(encoding="utf-8").strip()
        new_version = _apply_bump(current, kind)
        version_path.write_text(new_version + "\n", encoding="utf-8")

        subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
            [_GIT, "add", str(version_path)], cwd=root, check=True
        )
        commit_message = f"chore: bump version to {new_version}"
        subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
            [_GIT, "commit", "--no-verify", "-m", commit_message],
            cwd=root,
            check=True,
        )
        subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
            [_GIT, "tag", "-a", f"v{new_version}", "-m", f"Release v{new_version}"],
            cwd=root,
            check=True,
        )
        sys.stderr.write(
            f"[semantic-version] bumped {current} -> {new_version},"
            f" tagged v{new_version}\n"
        )
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"[semantic-version] error: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
