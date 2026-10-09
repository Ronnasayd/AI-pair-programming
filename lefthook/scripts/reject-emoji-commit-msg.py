#!/usr/bin/env python3
"""git commit-msg hook: reject messages containing emoji.

Symlinked into each project's .git/hooks/commit-msg by scripts/claude.install.sh
(the install loop symlinks every git-hooks/* into .git/hooks/).

Bypass for a deliberate exception: git commit --no-verify
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

from _commit_msg_shared import strip_comments

_EMOJI_REGEX = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF"
    "\U0000FE0F"
    "]+"
)


def main() -> int:
    """Validate the commit message file passed as argv[1].

    Returns:
        0 if the message has no emoji, 1 otherwise.
    """
    if len(sys.argv) < 2:
        return 0
    raw = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    msg = strip_comments(raw)

    hits = sorted(set(_EMOJI_REGEX.findall(msg)))
    if not hits:
        return 0

    sys.stderr.write(
        "\n✖ commit rejected: message contains emoji.\n"
        f"  matched: {', '.join(hits)}\n"
        "  Remove emoji, or use `git commit --no-verify` to bypass.\n\n"
    )
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:  # never wedge commits on a hook bug
        sys.stderr.write(f"[reject-emoji-commit-msg] error: {exc}\n")
        sys.exit(0)
