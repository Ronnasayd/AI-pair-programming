#!/usr/bin/env python3
"""git commit-msg hook: reject messages that don't follow Conventional Commits.

Symlinked into each project's .git/hooks/commit-msg by scripts/claude.install.sh
(the install loop symlinks every git-hooks/* into .git/hooks/).

Requires: type(scope?)!?: subject, where type is one of feat, fix, docs, style,
refactor, perf, test, chore. A trailing `!` before the `:` marks a breaking
change; when used, a `BREAKING CHANGE: <description>` footer is also required.

Bypass for a deliberate exception: git commit --no-verify
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

from _commit_msg_shared import strip_comments

_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|chore)(\([^)]+\))?(?P<bang>!)?: .+"
)

_BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE: .+", re.MULTILINE)

_TYPES_HELP = """\
  feat: A new feature
  fix: A bug fix
  docs: Documentation only changes
  style: Changes that do not affect the meaning of the code (white-space,
    formatting, etc)
  refactor: A code change that neither fixes a bug nor adds a feature
  perf: A code change that improves performance
  test: Adding missing tests or correcting existing tests
  chore: Changes to the build process or auxiliary tools and libraries such as
    documentation generation
"""


def main() -> int:
    """Validate the commit message file passed as argv[1].

    Returns:
        0 if the message is valid Conventional Commits, 1 otherwise.
    """
    if len(sys.argv) < 2:
        return 0
    raw = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    msg = strip_comments(raw).strip()

    match = _PATTERN.match(msg)
    if not match:
        sys.stderr.write(
            "\n✖ commit rejected: message does not follow Conventional Commits"
            " format.\n"
            "  Please use one of the following formats:\n"
            f"{_TYPES_HELP}"
            "  Or use `git commit --no-verify` to bypass.\n\n"
        )
        return 1

    if match.group("bang") and not _BREAKING_FOOTER.search(msg):
        sys.stderr.write(
            "\n✖ commit rejected: breaking change marked with '!' but missing footer.\n"
            "  Add a footer: BREAKING CHANGE: <description>\n"
            "  Or use `git commit --no-verify` to bypass.\n\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:  # never wedge commits on a hook bug
        sys.stderr.write(f"[conventional-commits-commit-msg] error: {exc}\n")
        sys.exit(0)
