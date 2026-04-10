#!/usr/bin/env python3
# protect-files.py (hardened)

import sys
import json
import shlex
import fnmatch
import os
import glob
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("ProtectFiles")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

PROJECT_ROOT = os.getcwd()

PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    "**/*.env",
    "**/*.secret",
    "**/*.secrets",
    "**/secrets/**",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
    "**/.ssh/**",
    "**/id_*",
    "**/*.pub",  # opcional (menos crítico, mas útil)
    "**/.gnupg/**",
    "**/*.gpg",
    "**/*.asc",
    "**/.aws/**",
    "**/.azure/**",
    "**/.gcloud/**",
    "**/credentials",
    "**/.git-credentials",
    "**/.gitconfig",
    "**/.netrc",
    "**/.npmrc",
    "**/.yarnrc",
    "**/.pypirc",
    "**/.docker/config.json",
    "**/.kube/config",
    "**/kubeconfig",
    "**/.bash_history",
    "**/.zsh_history",
    "**/.python_history",
    "**/.sqlite_history",
    "**/.psql_history",
    "**/.mysql_history",
    "**/.config/BraveSoftware/**",
    "**/.config/google-chrome/**",
    "**/.config/chromium/**",
    "**/.mozilla/**",
    "**/.cache/mozilla/**",
    "**/*.crt",
    "**/*.csr",
    "**/*.p12",
    "**/*.pfx",
    "**/*.der",
]

READ_COMMANDS = {"cat", "less", "more", "head", "tail", "grep", "awk", "sed", "bat"}

SHELL_OPERATORS = {"|", ">", ">>", "<", "&&", "||", ";"}


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────


def normalize(path: str) -> str:
    """Normalize + resolve symlinks."""
    try:
        return os.path.realpath(os.path.abspath(path))
    except Exception:
        return path


def is_within_project(path: str) -> bool:
    return normalize(path).startswith(PROJECT_ROOT)


def matches_pattern(path: str) -> tuple[bool, str]:
    """Match against protected patterns using pathlib semantics."""
    p = Path(path)

    for pattern in PROTECTED_PATTERNS:
        # direct fnmatch (string-based)
        if fnmatch.fnmatch(path, pattern):
            return True, pattern

        # pathlib match (more robust for **)
        if p.match(pattern):
            return True, pattern

    return False, ""


def expand_targets(targets: list[str]) -> list[str]:
    """Expand globs like *.env → actual files."""
    expanded = []
    for t in targets:
        matches = glob.glob(t, recursive=True)
        if matches:
            expanded.extend(matches)
        else:
            expanded.append(t)
    return expanded


def extract_file_targets(command: str) -> list[str]:
    """Extract file arguments from common read commands."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    targets = []

    it = iter(tokens)
    for token in it:
        cmd = os.path.basename(token)

        if cmd in READ_COMMANDS:
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if not arg.startswith("-"):
                    targets.append(arg)
            break

    return targets


def deny(file_path: str, pattern: str, source: str) -> None:
    print(
        json.dumps(
            {
                "decision": "deny",
                "file": file_path,
                "source": source,
                "reason": f"matches protected pattern '{pattern}'",
            }
        ),
        file=sys.stderr,
    )
    logger.debug(f"Denied '{file_path}' ({source}) due to pattern '{pattern}'")
    sys.exit(2)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON: {e}")
        sys.exit(1)

    tool_input = get_by_key(payload, "tool_input")

    # ── 1. Direct file access (Read/Write/Edit tools)
    file_path = get_by_key(tool_input, "file_path")

    if file_path:
        norm = normalize(file_path)

        # optional: enforce project boundary
        if not is_within_project(norm):
            deny(file_path, "outside_project", "path_escape")

        blocked, pattern = matches_pattern(norm)
        if blocked:
            deny(file_path, pattern, "file_path")

        logger.debug(f"Allowed file access: {file_path}")

    # ── 2. Shell command inspection
    command = get_by_key(tool_input, "command")

    if command:
        targets = extract_file_targets(command)
        targets = expand_targets(targets)

        for target in targets:
            norm = normalize(target)

            # block traversal outside project
            if not is_within_project(norm):
                deny(target, "outside_project", "command_path_escape")

            blocked, pattern = matches_pattern(norm)
            if blocked:
                deny(target, pattern, "command_read")

            logger.debug(f"Allowed command: {command} access: {target}")
            
    sys.exit(0)


if __name__ == "__main__":
    main()
