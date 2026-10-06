#!/usr/bin/python3
"""PreToolUse hook.

Denies writes of .md files into language-controlled docs directories when the
content is not in the configured language. Silent when content is fine.
"""

import fnmatch
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger

LOG = get_hooks_logger("MdLanguageCheck")

# Glob patterns (matched against the file path with fnmatch) whose targets
# require language-controlled markdown content.
ENGLISH_ONLY_DIRS = [
    "*/.spec/**",
    ".spec/**",
    "*/docs/**",
    "docs/**",
]

MD_LANGUAGE = os.environ.get("MD_LANGUAGE", "English")

PT_STOPWORDS = frozenset(
    {
        "de",
        "que",
        "não",
        "para",
        "com",
        "uma",
        "os",
        "as",
        "do",
        "da",
        "em",
        "um",
        "por",
        "mais",
        "como",
        "foi",
        "são",
        "está",
        "isso",
    }
)


def _looks_portuguese(text: str) -> bool:
    """Heuristic: Portuguese stopword density in prose, outside code fences.

    ponytail: only detects Portuguese when MD_LANGUAGE is English; use a
    langdetect lib if other language pairs matter.
    """
    if MD_LANGUAGE.lower() != "english":
        return False
    prose = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    words = re.findall(r"[^\W\d_]+", prose.lower())
    hits = sum(w in PT_STOPWORDS for w in words)
    return hits >= 4 and hits / len(words) > 0.04


def main() -> None:
    """Read the tool payload from stdin and emit a language reminder."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    tool_input = get_by_key(payload, "tool_input") or {}
    file_path = get_by_key(tool_input, "file_path") or ""

    if not file_path.endswith(".md"):
        sys.exit(0)

    if not any(fnmatch.fnmatch(file_path, pattern) for pattern in ENGLISH_ONLY_DIRS):
        sys.exit(0)

    content = (
        get_by_key(tool_input, "content") or get_by_key(tool_input, "new_string") or ""
    )
    if not _looks_portuguese(content):
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{Path(file_path).name} is in a language-controlled docs "
                f"directory: content must be in {MD_LANGUAGE}, but it looks "
                "Portuguese. Rewrite it and retry."
            ),
        }
    }
    LOG.debug("[blocked]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201
    sys.exit(0)


if __name__ == "__main__":
    main()
