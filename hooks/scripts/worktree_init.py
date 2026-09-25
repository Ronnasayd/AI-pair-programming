#!/usr/bin/python3
"""Symlink node_modules from main repo into new worktree."""

import json
import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("WorktreeInit")

LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock")


def git_common_dir(cwd: str) -> str | None:
    """Get git common directory for the given working directory.

    Args:
        cwd: Working directory to query for git common directory.

    Returns:
        str | None: Absolute path to git common directory, or None on error.
    """
    try:
        result = subprocess.run(
            ["/usr/bin/git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        LOG.warning("git rev-parse failed: %s", exc)
        return None
    if result.returncode != 0:
        LOG.warning(
            "git rev-parse exited %s: %s", result.returncode, result.stderr.strip()
        )
        return None
    return result.stdout.strip()


def find_lockfile(root: str) -> str | None:
    """Find a Node.js lockfile in the given directory.

    Args:
        root: Directory to search for lockfiles.

    Returns:
        str | None: Path to the first matching lockfile, or None if not found.
    """
    for name in LOCKFILES:
        path = os.path.join(root, name)
        if os.path.isfile(path):
            return path
    return None


def main() -> None:
    """Initialize worktree by symlinking node_modules and checking lockfiles."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # erro no parse não bloqueia nada

    LOG.debug("Raw payload: %s", json.dumps(payload))

    tool_response = get_by_key(payload, "tool_response")
    worktree_path = (
        get_by_key(tool_response, "worktree_path") if tool_response else None
    )

    if not worktree_path:
        LOG.warning("No worktree_path in tool_response, skipping")
        sys.exit(0)

    common_dir = git_common_dir(worktree_path)
    if not common_dir:
        LOG.warning("Could not resolve git common dir, skipping symlink")
        sys.exit(0)

    main_repo_root = os.path.dirname(common_dir)
    main_node_modules = os.path.join(main_repo_root, "node_modules")
    worktree_node_modules = os.path.join(worktree_path, "node_modules")

    if not os.path.isdir(main_node_modules):
        LOG.warning(
            "Main repo node_modules not found at %s, skipping", main_node_modules
        )
        sys.exit(0)

    if os.path.exists(worktree_node_modules) or os.path.islink(worktree_node_modules):
        LOG.debug(
            "Worktree node_modules already exists at %s, skipping",
            worktree_node_modules,
        )
        sys.exit(0)

    try:
        os.symlink(main_node_modules, worktree_node_modules, target_is_directory=True)
        LOG.info("Symlinked %s -> %s", worktree_node_modules, main_node_modules)
    except OSError as exc:
        LOG.warning("Failed to create symlink: %s", exc)
        sys.exit(0)

    main_lock = find_lockfile(main_repo_root)
    worktree_lock = find_lockfile(worktree_path)
    if main_lock and worktree_lock:
        try:
            with open(main_lock, "rb") as f_main:
                main_content = f_main.read()
            with open(worktree_lock, "rb") as f_worktree:
                worktree_content = f_worktree.read()
            same = (
                os.path.basename(main_lock) == os.path.basename(worktree_lock)
                and main_content == worktree_content
            )
        except OSError:
            same = True  # não bloqueia em erro de leitura
        if not same:
            LOG.warning(
                "Lockfile differs between worktree (%s) and main repo — "
                "symlinked node_modules may be stale, consider running install",
                worktree_path,
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
