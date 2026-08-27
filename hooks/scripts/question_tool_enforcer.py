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
    "If an interactive tool exists, never ask a plain-text question.\n\n"
    "If there are multiple questions, use the `grilling` skill.\n"
    "Ask questions using clear, technical language.\n"
)


def last_assistant_from_transcript(path):
    """Reconstruct the last assistant turn's text from the JSONL transcript.

    Used when the payload's ``last_assistant_message`` is missing or truncated
    (Claude Code drops/clips that field for very large messages).
    """
    if not path:
        return None
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        LOG.debug(f"Failed to read transcript {path}: {e}")
        return None

    collected = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = entry.get("type")
        if etype == "assistant":
            content = entry.get("message", {}).get("content", [])
            texts = [b.get("text", "") for b in content if b.get("type") == "text"]
            joined = "\n".join(t for t in texts if t)
            if joined:
                collected.append(joined)
        elif etype in ("user", "system") and collected:
            break  # reached the start of the last assistant turn

    if not collected:
        return None
    return "\n".join(reversed(collected))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    if get_by_key(payload, "stop_hook_active"):
        sys.exit(0)

    last_message = get_by_key(payload, "last_assistant_message")
    if not last_message:
        # Field dropped/clipped for very large messages: reconstruct from transcript.
        last_message = last_assistant_from_transcript(
            get_by_key(payload, "transcript_path")
        )
    if not last_message or "?" not in last_message:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": RULE,
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
