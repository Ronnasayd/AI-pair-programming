#!/usr/bin/python3
"""Stop / SubagentStop hook.

If the last assistant message asked a plain-text question (contains '?'),
remind the agent to use an interactive question tool.
"""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger, minify_markdown

LOG = get_hooks_logger("QuestionToolEnforcer")


def build_rule() -> str:
    """Build the interactive-question-tool reminder, honoring QUESTION_TOOL_LANG.

    Returns:
        str: the markdown rule text to inject as additional context.
    """
    lang = os.environ.get("QUESTION_TOOL_LANG", "").strip()
    lang_line = (
        f"MANDATORY: Ask questions in {lang}.\n"
        if lang
        else "Use the same language used by the user.\n"
    )
    return (
        "## Always Use Interactive Question Tools\n\n"
        "Use an interactive question tool for every user question — no exceptions.\n\n"
        "Covers clarifications, options, confirmations, preference checks, "
        "all user interactions.\n\n"
        "- **Claude**: `AskUserQuestion`\n"
        "- **Other environments**: equivalent interactive tool\n"
        "- **Fallback**: labeled options (A, B, C... Z)\n\n"
        "Never ask a plain-text question if an interactive tool exists.\n"
        "Multiple questions: use `grilling` skill.\n"
        "Ask in clear, technical language.\n"
        f"{lang_line}"
    )


RULE = build_rule()


def last_assistant_from_transcript(path: str | None) -> str | None:
    """Reconstruct the last assistant turn's text from the JSONL transcript.

    Used when the payload's ``last_assistant_message`` is missing or truncated
    (Claude Code drops/clips that field for very large messages).

    Args:
        path: path to the JSONL transcript file, or None.

    Returns:
        str | None: the joined assistant text, or None if unavailable.
    """
    if not path:
        return None
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        LOG.debug("Failed to read transcript %s: %s", path, e)
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
    """Read the hook payload from stdin and emit the reminder if warranted."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    if get_by_key(payload, "stop_hook_active"):
        sys.exit(0)

    event = get_by_key(payload, "hook_event_name") or "Stop"

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
            "hookEventName": event,
            "additionalContext": minify_markdown(RULE),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201 - hook stdout protocol
    sys.exit(0)


if __name__ == "__main__":
    main()
