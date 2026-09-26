#!/usr/bin/python3
"""protect_branches.py.

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

from utils import get_by_key, get_hooks_logger, split_on_operators  # noqa: E402

logger = get_hooks_logger("ProtectBranches")

PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

DEFAULT_PROTECTED_BRANCHES = {"main", "master", "develop", "homolog"}


def get_protected_branches() -> set[str]:
    """PROTECTED_BRANCHES env var overrides the default list (comma-separated).

    Returns:
        Set of protected branch names
    """
    override = os.environ.get("PROTECTED_BRANCHES", "").strip()
    if not override:
        return DEFAULT_PROTECTED_BRANCHES
    return {b.strip() for b in override.split(",") if b.strip()}


PROTECTED_BRANCHES = get_protected_branches()

# git subcommands that mutate branch history/refs and take the operation's
# risk from "which branch is this?" rather than the subcommand alone.
DESTRUCTIVE_PUSH_FLAGS = {"-f", "--force", "--force-with-lease", "--force-if-includes"}


def current_branch() -> str | None:
    """Get the current git branch name.

    Returns:
        Current branch name or None if not in a git repo or on error.
    """
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "-C", PROJECT_ROOT, "branch", "--show-current"],  # noqa: S607 -- fixed lookup binary, trusted internal tool name
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        branch = result.stdout.strip()
        return branch or None
    except Exception:  # pylint: disable=broad-except
        return None


def deny(command: str, reason: str, branch: str) -> None:
    """Write deny decision to stderr and exit with code 2.

    Args:
        command: Git command that was denied.
        reason: Reason for the denial.
        branch: Protected branch name involved in the operation.
    """
    print(  # noqa: T201
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
    logger.debug("Denied '%s' — %s on branch '%s'", command, reason, branch)
    sys.exit(2)


def strip_flags(tokens: list[str]) -> list[str]:
    """Remove command-line flags from token list.

    Args:
        tokens: List of command tokens.

    Returns:
        Tokens with flags (starting with -) removed.
    """
    return [t for t in tokens if not t.startswith("-")]


def _check_push(tokens: list[str], args: list[str], branch: str | None) -> None:
    """Check `git push` for force-push/delete of a protected branch."""
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
                deny(
                    " ".join(tokens),
                    "delete of protected branch (remote)",
                    ref_branch,
                )

    # `git push` / `git push origin` with no explicit ref, force-pushing
    # while HEAD is on a protected branch
    if (
        has_force
        and branch in PROTECTED_BRANCHES
        and not any(r in PROTECTED_BRANCHES for r in refs)
    ):
        deny(" ".join(tokens), "force-push while on protected branch", branch)

    if has_delete:
        return

    # plain `git push` (no force) while sitting on a protected branch
    if branch in PROTECTED_BRANCHES and not has_force:
        deny(" ".join(tokens), "direct push to protected branch", branch)


def _check_branch_delete(
    tokens: list[str], args: list[str], branch: str | None
) -> None:
    """Check `git branch -D/-d <name>` for deletion of a protected branch."""
    has_delete = any(a in ("-D", "-d", "--delete") for a in args)
    if has_delete:
        targets = strip_flags(args) or ([branch] if branch else [])
        for t in targets:
            if t in PROTECTED_BRANCHES:
                deny(" ".join(tokens), "delete of protected branch", t)


def _check_reset(tokens: list[str], args: list[str], branch: str | None) -> None:
    """Check `git reset --hard` while sitting on a protected branch."""
    if "--hard" in args and branch in PROTECTED_BRANCHES:
        deny(" ".join(tokens), "hard reset on protected branch", branch)


def _check_checkout(tokens: list[str], args: list[str], _branch: str | None) -> None:
    """Check `git checkout -B <protected>` (force-overwrite ref)."""
    if "-B" in args:
        idx = args.index("-B")
        if idx + 1 < len(args) and args[idx + 1] in PROTECTED_BRANCHES:
            deny(
                " ".join(tokens),
                "force-recreate protected branch (checkout -B)",
                args[idx + 1],
            )


def _check_commit_like_ops(tokens: list[str], subcmd: str, branch: str | None) -> None:
    """Check commit/merge/rebase/cherry-pick performed on a protected branch."""
    reasons = {
        "commit": "direct commit on protected branch",
        "merge": "direct merge into protected branch",
        "rebase": "rebase on protected branch",
        "cherry-pick": "cherry-pick onto protected branch",
    }
    if branch in PROTECTED_BRANCHES:
        deny(" ".join(tokens), reasons[subcmd], branch)


def check_git_segment(tokens: list[str]) -> None:
    """Inspect one tokenized `git ...` command for protected-branch operations.

    Args:
        tokens: Tokenized command.
    """
    if not tokens or os.path.basename(tokens[0]) != "git":
        return

    subcmd = tokens[1] if len(tokens) > 1 else None
    args = tokens[2:]
    branch = current_branch()

    if subcmd == "push":
        _check_push(tokens, args, branch)
    elif subcmd == "branch":
        _check_branch_delete(tokens, args, branch)
    elif subcmd == "reset":
        _check_reset(tokens, args, branch)
    elif subcmd == "checkout":
        _check_checkout(tokens, args, branch)
    elif subcmd in ("commit", "merge", "rebase", "cherry-pick"):
        _check_commit_like_ops(tokens, subcmd, branch)


def main() -> None:
    """Parse hook payload and check git commands for protected-branch violations."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug("Invalid JSON: %s", e)
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
