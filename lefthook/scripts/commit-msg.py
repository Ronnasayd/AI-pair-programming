#!/usr/bin/env python3
"""git commit-msg hook: reject messages that mention AI code assistants.

Symlinked into each project's .git/hooks/commit-msg by scripts/claude.install.sh
(the install loop symlinks every git-hooks/* into .git/hooks/).

Blocks the commit if the message body references Claude, Gemini, Codex, Copilot,
ChatGPT, Cursor, or a generic "AI assistant / AI-generated" phrasing. Keeps the
history free of tool attribution.

Bypass for a deliberate exception: git commit --no-verify
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

from _commit_msg_shared import strip_comments

# Word-boundary patterns. Case-insensitive. Keep this list tight to avoid
# false positives on unrelated prose.
# `(?![/.\w-])` guards against matching a path/filename segment
# (e.g. `claude/settings.json`, `codex.md`) rather than a tool reference.
_NAME_SUFFIX = r"(?![/.\w-])"
_PATTERNS = [
    r"\bclaude\b" + _NAME_SUFFIX,
    r"\banthropic\b" + _NAME_SUFFIX,
    r"\bgemini\b" + _NAME_SUFFIX,
    r"\bcodex\b" + _NAME_SUFFIX,
    r"\bcopilot\b" + _NAME_SUFFIX,
    r"\bchatgpt\b" + _NAME_SUFFIX,
    r"\bopenai\b" + _NAME_SUFFIX,
    r"\bcursor\s+(ai|ide|editor)\b",
    r"\bco-?authored-by:\s*claude",
    r"\bgenerated\s+(with|by)\s+.*\b(ai|claude|gemini|codex|copilot|chatgpt)\b",
    r"\bai[- ]generated\b",
    r"\bai\s+(assistant|agent|pair)\b",
    r"🤖",
]
_REGEX = re.compile("|".join(_PATTERNS), re.IGNORECASE)


def main() -> int:
    """Validate the commit message file passed as argv[1].

    Returns:
        0 if the message is clean, 1 if it references an AI assistant.
    """
    if len(sys.argv) < 2:
        return 0
    raw = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    msg = strip_comments(raw)

    hits = sorted({m.group(0) for m in _REGEX.finditer(msg)})
    if not hits:
        return 0

    sys.stderr.write(
        "\n✖ commit rejected: message references an AI code assistant.\n"
        f"  matched: {', '.join(hits)}\n"
        "  Remove the reference, or use `git commit --no-verify` to bypass.\n\n"
    )
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:  # never wedge commits on a hook bug
        sys.stderr.write(f"[commit-msg] error: {exc}\n")
        sys.exit(0)
