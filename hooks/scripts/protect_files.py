#!/usr/bin/env python3
# protect-files.py

import sys
import json
import shlex
import fnmatch
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    "secrets/*",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
]


def is_protected(file_path: str) -> tuple[bool, str]:
    for pattern in PROTECTED_PATTERNS:
        if fnmatch.fnmatch(file_path, pattern):
            return True, pattern
        # checa também se o padrão aparece como substring
        if pattern.strip("*./") in file_path:
            return True, pattern
    return False, ""


def extract_cat_targets(command: str) -> list[str]:
    """Extract file path arguments from a shell command that invokes cat.

    Handles:
      - Simple:       cat .env
      - Multi-file:   cat secrets/db.key secrets/api.key
      - Flags:        cat -n .env
      - Pipe prefix:  cat .env | grep SECRET
      - Redirect:     cat .env > /tmp/out
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        # shlex fails on unmatched quotes; fall back to naive split
        tokens = command.split()

    targets: list[str] = []
    SHELL_OPERATORS = {"|", ">", ">>", "<", "&&", "||", ";"}

    it = iter(tokens)
    for token in it:
        if token in ("cat", "\\cat"):          # bare or escaped cat
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break                       # stop at shell control chars
                if not arg.startswith("-"):     # skip flags (-n, -A, -e …)
                    targets.append(arg)
            break                               # only inspect the first cat call
    return targets


def deny(file_path: str, pattern: str, source: str) -> None:
    """Write a structured denial to stderr and exit with code 2."""
    print(
        json.dumps({
            "decision": "deny",
            "file": file_path,
            "source": source,          # "file_path" | "cat_command"
            "reason": f"matches protected pattern '{pattern}'",
        }),
        file=sys.stderr,
    )
    sys.exit(2)


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logging.error(f"JSON inválido: {e}")
        sys.exit(1)

    tool_input = payload.get("tool_input", {})
    tool_name  = payload.get("tool_name", "")

    # ── 1. Direct file-path tools (Write, Read, Edit …) ──────────────────────
    file_path = (
        tool_input.get("filePath")
        or tool_input.get("file_path")
        or ""
    )

    if file_path:
        blocked, pattern = is_protected(file_path)
        if blocked:
            deny(file_path, pattern, "file_path")

    # ── 2. Bash tool — intercept `cat <file>` ────────────────────────────────
    command = tool_input.get("command", "")

    if command:
        targets = extract_cat_targets(command)
        for target in targets:
            blocked, pattern = is_protected(target)
            if blocked:
                deny(target, pattern, "cat_command")

    sys.exit(0)


if __name__ == "__main__":
    main()
