#!/usr/bin/python3
# protect-files.py (hardened)

import fnmatch
import glob
import json
import os
import re
import shlex
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("ProtectFiles")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

# CLAUDE_PROJECT_DIR (set by Claude Code) takes precedence when present, since it's
# stable for the whole session; os.getcwd() is the fallback but can drift if cwd
# changes mid-session (cd, subagents), silently widening the boundary check.
PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

ALLOWED_PATTERNS = [
    ".claude/**",
    "/tmp/**",
    "/home/ronnas/develop/personal/AI-pair-programming/skills/**",
    "/home/ronnas/develop/personal/AI-pair-programming/instructions/**",
]

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

READ_COMMANDS = {
    "cat",
    "less",
    "more",
    "head",
    "tail",
    "grep",
    "awk",
    "sed",
    "bat",
    "xxd",
    "od",
    "strings",
    "base64",
    "openssl",
}

# commands whose args are ALL file targets (both src/dest for copy-like tools)
COPY_COMMANDS = {"cp", "mv", "rsync", "scp", "install", "dd", "tar", "zip", "cat"}

# commands that can exfiltrate file contents over the network via upload flags
NETWORK_COMMANDS = {"curl", "wget"}

UPLOAD_FLAGS = {"-T", "--upload-file", "-d", "--data", "--data-binary", "--data-raw"}

SHELL_OPERATORS = {"|", ">", ">>", "<", "&&", "||", ";", "\n"}

CMD_SUBSTITUTION_RE = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")


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


def is_allowed(path: str) -> bool:
    """Check if path is in allowed patterns (safe to access)."""
    p = Path(path)
    for pattern in ALLOWED_PATTERNS:
        if fnmatch.fnmatch(path, pattern) or p.match(pattern):
            return True
    return False


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


def split_subcommands(command: str) -> list[str]:
    """Split a shell command string on pipe/list operators into subcommands."""
    parts = re.split(r"\|\||&&|[|;\n]", command)
    return [p.strip() for p in parts if p.strip()]


def extract_substitutions(command: str) -> list[str]:
    """Pull inner text out of $(...) / `...` so it gets scanned too."""
    found = []
    for m in CMD_SUBSTITUTION_RE.finditer(command):
        inner = m.group(1) or m.group(2) or ""
        if inner:
            found.append(inner)
    return found


def extract_upload_ref(arg: str) -> str | None:
    """Pull a file path out of an @file / field=@file style value."""
    at = arg.find("@")
    if at == -1:
        return None
    ref = arg[at + 1 :]
    return ref if ref and ref not in ("-", "") else None


def extract_targets_from_tokens(tokens: list[str]) -> list[str]:
    """Extract file arguments from a single tokenized command."""
    targets = []
    it = iter(tokens)
    for token in it:
        cmd = os.path.basename(token)

        if cmd in NETWORK_COMMANDS:
            prev = None
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                ref = extract_upload_ref(arg)
                if ref:
                    targets.append(ref)
                elif prev in UPLOAD_FLAGS and not arg.startswith("-"):
                    targets.append(arg)
                prev = arg
            break

        if cmd in READ_COMMANDS or cmd in COPY_COMMANDS:
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if arg.startswith("-"):
                    continue
                if "=" in arg and arg.startswith("--"):
                    continue
                targets.append(arg)
            break

    return targets


def extract_file_targets(command: str) -> list[str]:
    """Extract file arguments from common read/copy commands, across chained
    subcommands and command substitutions ($(...) / `...`)."""
    targets = []

    raw_commands = split_subcommands(command)
    for sub in extract_substitutions(command):
        raw_commands.extend(split_subcommands(sub))

    for sub in raw_commands:
        try:
            tokens = shlex.split(sub)
        except ValueError:
            tokens = sub.split()
        targets.extend(extract_targets_from_tokens(tokens))

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

        if is_allowed(norm):
            logger.debug(f"Allowed file access (whitelisted): {file_path}")
        else:
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

            if not is_allowed(norm):
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
