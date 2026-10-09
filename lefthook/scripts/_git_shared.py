"""Shared git helpers for lefthook scripts: full-path lookup, repo root, run."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

GIT = shutil.which("git") or "git"


def run_git(*args: str) -> str:
    """Run a git subcommand and return its stripped stdout.

    Args:
        *args: git subcommand and its arguments, e.g. "tag", "-l".

    Returns:
        The command's stdout, stripped of trailing whitespace.
    """
    return subprocess.run(  # noqa: S603 -- fixed lookup binary, trusted internal tool name
        [GIT, *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def repo_root() -> Path:
    """Return the current repository's top-level directory.

    Returns:
        Absolute path to the repo root.
    """
    return Path(run_git("rev-parse", "--show-toplevel"))
