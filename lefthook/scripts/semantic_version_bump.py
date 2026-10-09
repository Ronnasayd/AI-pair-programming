#!/usr/bin/env python3
"""git post-commit hook: tag the release based on Conventional Commits.

Symlinked/wired via lefthook.yml (post-commit) into any project that opts in
by having at least one `vX.Y.Z` tag already in its history. Language-agnostic:
no Node/npx dependency, works in any git repo (Node, Python, Go, ...).

The git tag itself is the single source of truth for the current version — no
separate version file to keep in sync. This mirrors what the companion CI
workflow (.github/workflows/semantic-version-bump.yml, using the
paulhatch/semantic-version action) does for PRs merged on GitHub, so a commit
tagged by one path is seen as already-tagged by the other (no duplicate tag
attempts for the same commit).

Behavior:
- No `vX.Y.Z` tag anywhere in history -> no-op (exit 0). This is the opt-in
  gate: projects that don't want versioning never pay for this hook, and
  never get a surprise v0.0.1 out of nowhere. Create the first tag manually
  (`git tag -a v0.1.0 -m "..."`) to opt in.
- Not on the main branch (main/master) -> no-op. Feature-branch commits don't
  represent a release.
- HEAD already has a `vX.Y.Z` tag -> no-op. Avoids re-tagging a commit the
  CI workflow (or a previous run of this hook) already tagged.
- Reads the just-made commit's subject, parses its Conventional Commits type
  (and `!`/BREAKING CHANGE marker) to decide the bump: major/minor/patch.
  Non-conforming subjects (e.g. plain merge commits) are skipped, not bumped.
- Merge commit (2+ parents, i.e. `git merge` without --ff-only): the subject
  itself ("Merge pull request #12 ...") never matches Conventional Commits,
  so instead every commit brought in by the second parent is scanned and the
  strongest bump found (major > minor > patch) is applied. This covers a
  feature branch with several feat/fix commits merged via a regular (non-
  squash) merge. Squash merges already work without this: GitHub rewrites
  them into a single Conventional Commits subject on the merge commit itself.
- Fast-forward merges (no merge commit created) are NOT covered — known
  limitation, since there is no post-commit event to hook into for them.
- Creates an annotated tag `vX.Y.Z` on HEAD. No extra commit is made.

Bypass for a deliberate exception: git commit --no-verify
"""

from __future__ import annotations

import re
import subprocess
import sys

from _git_shared import run_git

_MAIN_BRANCHES = {"main", "master"}

_TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")

_SUBJECT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)"
    r"(\([^)]+\))?(?P<bang>!)?: .+"
)
_BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE: .+", re.MULTILINE)

_BUMP_BY_TYPE = {"feat": "minor", "fix": "patch"}


def _current_branch() -> str:
    return run_git("rev-parse", "--abbrev-ref", "HEAD")


def _last_commit_message() -> str:
    return run_git("log", "-1", "--format=%B")


def _merge_parents() -> list[str]:
    """Return HEAD's parent commit hashes (1 for a normal commit, 2+ for a merge)."""
    return run_git("log", "-1", "--format=%P").split()


def _latest_version() -> tuple[int, int, int] | None:
    """Return the highest `vX.Y.Z` tag in the repo, or None if there is none."""
    best: tuple[int, int, int] | None = None
    for tag in run_git("tag", "-l", "v*").splitlines():
        match = _TAG_PATTERN.match(tag)
        if not match:
            continue
        version = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if best is None or version > best:
            best = version
    return best


def _head_already_tagged() -> bool:
    tags = run_git("tag", "--points-at", "HEAD").splitlines()
    return any(_TAG_PATTERN.match(tag) for tag in tags)


def _strongest_bump(kinds: list[str]) -> str | None:
    order = {"patch": 0, "minor": 1, "major": 2}
    present = [k for k in kinds if k in order]
    if not present:
        return None
    return max(present, key=lambda k: order[k])


def _merge_bump_kind(second_parent: str) -> str | None:
    """Decide the bump for a merge commit by scanning the commits it brought in.

    Args:
        second_parent: hash of the merge's second parent (the branch merged in).

    Returns:
        The strongest bump kind found among those commits, or None.
    """
    shas = run_git("log", f"HEAD^1..{second_parent}", "--format=%H").splitlines()
    kinds = [_bump_kind(run_git("log", "-1", "--format=%B", sha)) for sha in shas]
    return _strongest_bump([k for k in kinds if k])


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


def _apply_bump(version: tuple[int, int, int], kind: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if kind == "major":
        return (major + 1, 0, 0)
    if kind == "minor":
        return (major, minor + 1, 0)
    return (major, minor, patch + 1)


def main() -> int:
    """Tag HEAD with the next semantic version, if this commit warrants it.

    Returns:
        0 always (never blocks a commit that already happened).
    """
    try:
        if _current_branch() not in _MAIN_BRANCHES:
            return 0

        current = _latest_version()
        if current is None:
            return 0
        if _head_already_tagged():
            return 0

        parents = _merge_parents()
        if len(parents) >= 2:
            kind = _merge_bump_kind(parents[1])
        else:
            kind = _bump_kind(_last_commit_message())
        if kind is None:
            return 0

        new_version = _apply_bump(current, kind)
        new_tag = "v" + ".".join(str(part) for part in new_version)

        run_git("tag", "-a", new_tag, "-m", f"Release {new_tag}")
        sys.stderr.write(
            f"[semantic-version] bumped v{'.'.join(str(p) for p in current)} ->"
            f" {new_tag}, tagged\n"
        )
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"[semantic-version] error: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
