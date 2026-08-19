#!/usr/bin/python3
"""protect_branches.py

Deny git operations that would mutate a protected branch (main, master,
develop, homolog, ...) without the user going through a normal PR flow.
Runs as a PreToolUse hook on the Bash tool, alongside protect_files.py.
"""

import json
import os
import shlex
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger  # noqa: E402

logger = get_hooks_logger("ProtectBranches")

PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

DEFAULT_PROTECTED_BRANCHES = {"main", "master", "develop", "homolog"}


def get_protected_branches() -> set[str]:
    """PROTECTED_BRANCHES env var overrides the default list (comma-separated)."""
    override = os.environ.get("PROTECTED_BRANCHES", "").strip()
    if not override:
        return DEFAULT_PROTECTED_BRANCHES
    return {b.strip() for b in override.split(",") if b.strip()}


PROTECTED_BRANCHES = get_protected_branches()

# git subcommands that mutate branch history/refs and take the operation's
# risk from "which branch is this?" rather than the subcommand alone.
DESTRUCTIVE_PUSH_FLAGS = {"-f", "--force", "--force-with-lease", "--force-if-includes"}

SHELL_OPERATORS = {"|", ">", ">>", "<", "&&", "||", ";", "\n"}


def split_on_operators(command: str) -> list[str]:
    """Split a shell command string on &&, ||, ;, |, and newlines (quote-aware)."""
    segments = []
    current = []
    i = 0
    in_single = False
    in_double = False

    while i < len(command):
        ch = command[i]
        if ch == "\\" and not in_single and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            i += 1
            continue
        if in_single or in_double:
            current.append(ch)
            i += 1
            continue
        if ch == "&" and i + 1 < len(command) and command[i + 1] == "&":
            segments.append("".join(current))
            current = []
            i += 2
            continue
        if ch == "|" and i + 1 < len(command) and command[i + 1] == "|":
            segments.append("".join(current))
            current = []
            i += 2
            continue
        if ch in (";", "|", "\n"):
            segments.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1

    segments.append("".join(current))
    return [s.strip() for s in segments if s.strip()]


def current_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", PROJECT_ROOT, "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        branch = result.stdout.strip()
        return branch or None
    except Exception:
        return None


def deny(command: str, reason: str, branch: str) -> None:
    print(
        json.dumps(
            {
                "decision": "deny",
                "command": command,
                "source": "protect_branches",
                "reason": f"{reason} (protected branch: '{branch}')",
            }
        ),
        file=sys.stderr,
    )
    logger.debug(f"Denied '{command}' — {reason} on branch '{branch}'")
    sys.exit(2)


def strip_flags(tokens: list[str]) -> list[str]:
    return [t for t in tokens if not t.startswith("-")]


def check_git_segment(tokens: list[str]) -> None:
    """Inspect one tokenized `git ...` command for protected-branch operations."""
    if not tokens or os.path.basename(tokens[0]) != "git":
        return

    subcmd = tokens[1] if len(tokens) > 1 else None
    args = tokens[2:]
    branch = current_branch()

    # push --force* / delete of a protected branch (remote or local ref)
    if subcmd == "push":
        has_force = any(a in DESTRUCTIVE_PUSH_FLAGS for a in args)
        has_delete = "--delete" in args or "-d" in args
        refs = strip_flags(args)

        for ref in refs:
            ref_branch = ref.split(":")[-1] if ":" in ref else ref
            ref_branch = ref_branch.lstrip("+")
            if ref_branch in PROTECTED_BRANCHES:
                if has_force:
                    deny(" ".join(tokens), "force-push to protected branch", ref_branch)
                if has_delete:
                    deny(" ".join(tokens), "delete of protected branch (remote)", ref_branch)

        # `git push` / `git push origin` with no explicit ref, force-pushing
        # while HEAD is on a protected branch
        if has_force and branch in PROTECTED_BRANCHES and not any(
            r in PROTECTED_BRANCHES for r in refs
        ):
            deny(" ".join(tokens), "force-push while on protected branch", branch)

        if has_delete:
            return

        # plain `git push` (no force) while sitting on a protected branch
        if branch in PROTECTED_BRANCHES and not has_force:
            deny(" ".join(tokens), "direct push to protected branch", branch)
        return

    # branch deletion: git branch -D/-d <name>
    if subcmd == "branch":
        has_delete = any(a in ("-D", "-d", "--delete") for a in args)
        if has_delete:
            targets = strip_flags(args) or ([branch] if branch else [])
            for t in targets:
                if t in PROTECTED_BRANCHES:
                    deny(" ".join(tokens), "delete of protected branch", t)
        return

    # git reset --hard while sitting on a protected branch
    if subcmd == "reset":
        if "--hard" in args and branch in PROTECTED_BRANCHES:
            deny(" ".join(tokens), "hard reset on protected branch", branch)
        return

    # checkout -B <protected> / branch -f <protected> (force-overwrite ref)
    if subcmd == "checkout":
        if "-B" in args:
            idx = args.index("-B")
            if idx + 1 < len(args) and args[idx + 1] in PROTECTED_BRANCHES:
                deny(" ".join(tokens), "force-recreate protected branch (checkout -B)", args[idx + 1])
        return

    if subcmd == "commit":
        if branch in PROTECTED_BRANCHES:
            deny(" ".join(tokens), "direct commit on protected branch", branch)
        return

    if subcmd == "merge":
        if branch in PROTECTED_BRANCHES:
            deny(" ".join(tokens), "direct merge into protected branch", branch)
        return

    if subcmd == "rebase":
        if branch in PROTECTED_BRANCHES:
            deny(" ".join(tokens), "rebase on protected branch", branch)
        return

    if subcmd == "cherry-pick":
        if branch in PROTECTED_BRANCHES:
            deny(" ".join(tokens), "cherry-pick onto protected branch", branch)
        return


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON: {e}")
        sys.exit(1)

    tool_input = get_by_key(payload, "tool_input")
    command = get_by_key(tool_input, "command") if tool_input else None

    if not command or "git" not in command:
        sys.exit(0)

    for segment in split_on_operators(command):
        if "git" not in segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        check_git_segment(tokens)

    sys.exit(0)


if __name__ == "__main__":
    main()
