#!/usr/bin/python3
"""
Session-end full Jest coverage hook.

When a session ends, if the project has jest installed, spawns a detached
background process that runs `jest --coverage` for the whole project so the
coverage dir reflects a full, non-incremental run.

Fire-and-forget: does not block the SessionEnd hook response.
"""

import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    acquire_lock,
    find_project_root,
    get_by_key,
    get_hooks_logger,
    jest_installed,
    lock_path_for,
    spawn_background,
    tmp_project_dir,
)

logger = get_hooks_logger("CoverageSessionEnd")


def maybe_run_full_coverage(project_root: str) -> None:
    if not jest_installed(project_root):
        logger.debug("Jest not installed in %s, skipping.", project_root)
        return

    tmp_dir = tmp_project_dir(project_root, "jest-coverage-session-end")

    lock_file = lock_path_for(tmp_dir, "full-coverage")
    if not acquire_lock(lock_file):
        logger.debug(
            "Full coverage run already in progress for %s, skipping.", project_root
        )
        return

    release_cmd = f"rm -f {json.dumps(str(lock_file))}"
    jest_cmd = "NODE_ENV=test node_modules/.bin/jest --coverage --passWithNoTests --runInBand"
    full_cmd = f"{jest_cmd}; {release_cmd}"
    logger.debug("Spawning background full coverage run: %s", jest_cmd)
    spawn_background(full_cmd, project_root, tmp_dir / "coverage-session-end.log")


def main() -> None:
    max_stdin = 1024 * 1024
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(max_stdin)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        cwd = get_by_key(data, "cwd") or os.getcwd()
        project_root = find_project_root(cwd)
        maybe_run_full_coverage(project_root)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("Error parsing stdin: %s", exc)

    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
