#!/usr/bin/env python3
"""git pre-push hook: push any local tags not yet on the remote.

Symlinked/wired via lefthook.yml (pre-push). Complements
semantic_version_bump.py: that script creates the local annotated tag on
commit, this one ships it to the remote on the next push. Kept separate so
"bump the version" and "sync tags to remote" stay distinct concerns.

Behavior:
- No tags at all -> no-op (exit 0). Same opt-in gate as the bump script:
  only projects that already have a `vX.Y.Z` tag in their history pay for
  tag pushes.
- All tags already on origin -> no-op.
- Otherwise: `git push origin --tags`. A failed push (no network, no
  `origin`) is reported but never blocks the push that triggered this hook.

Bypass for a deliberate exception: git push --no-verify
"""

from __future__ import annotations

import subprocess
import sys

from _git_shared import GIT, repo_root, run_git


def main() -> int:
    """Push local tags missing from origin, if this repo opts into versioning.

    Returns:
        0 always (never blocks the push that triggered this hook).
    """
    try:
        root = repo_root()
        local_tags = set(run_git("tag", "-l").splitlines())
        if not local_tags:
            return 0

        remote_tags = {
            line.split("refs/tags/", 1)[1].removesuffix("^{}")
            for line in run_git("ls-remote", "--tags", "origin").splitlines()
            if "refs/tags/" in line
        }
        if local_tags <= remote_tags:
            return 0

        result = subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
            [GIT, "push", "origin", "--tags"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            sys.stderr.write(
                f"[push-pending-tags] push failed: {result.stderr.strip()}\n"
            )
        else:
            sys.stderr.write("[push-pending-tags] pushed pending tags to origin\n")
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"[push-pending-tags] error: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
