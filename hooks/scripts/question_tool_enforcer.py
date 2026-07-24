#!/usr/bin/python3
"""Stop hook: if the last assistant message asked a plain-text question
(contains '?'), remind the agent to use an interactive question tool."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("QuestionToolEnforcer")

RULE = (
    "## Always Use Interactive Question Tools\n\n"
    "For every user question, use an interactive question tool. No exceptions "
    "for context, type, or intent.\n\n"
    "Use this for clarifications, options, confirmations, preference checks, "
    "all user interactions.\n\n"
    "- **Claude**: Use `AskUserQuestion`\n"
    "- **Other environments**: Use the equivalent interactive question tools "
    "available in your context\n"
    "- **Fallback**: if no interactive tools exist, use labeled options "
    "(A, B, C... Z)\n\n"
    "If an interactive tool exists, never ask a plain-text question."
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    last_message = get_by_key(payload, "last_assistant_message")
    if not last_message or "?" not in last_message:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": RULE,
        }
    }
    LOG.debug(f"Output: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
