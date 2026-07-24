#!/usr/bin/python3
"""Stop hook: if the last assistant message asked a plain-text question
(contains '?'), remind the agent to use an interactive question tool."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger, read_file  # noqa: E402

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


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join((c.get("text") or "") for c in content if isinstance(c, dict))
    return ""


def _last_assistant_message(transcript_path: str) -> str | None:
    content = read_file(Path(transcript_path))
    if not content:
        return None

    last_text = None
    for line in content.split("\n"):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if get_by_key(entry, "type") != "assistant":
            continue
        message = get_by_key(entry, "message") or {}
        text = _extract_text(message.get("content"))
        if text:
            last_text = text
    return last_text


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    transcript_path = get_by_key(payload, "transcript_path")
    if not transcript_path:
        sys.exit(0)

    last_message = _last_assistant_message(transcript_path)
    if not last_message or "?" not in last_message:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": RULE,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
