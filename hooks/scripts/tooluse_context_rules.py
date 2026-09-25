#!/usr/bin/python3
"""Generic hook: inject additionalContext when a rule's `match(payload)` returns True.

Each rule gets the full raw hook payload, so matching logic isn't limited to
a fixed set of fields (event/tool_name/tool_input/...) — add whatever check
you need directly in the rule's `match` lambda/function.
"""

from collections.abc import Generator
import json
from os import path
import re
import sys

script_dir = path.dirname(path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
from utils import get_by_key, get_hooks_logger, minify_markdown  # noqa: E402

LOG = get_hooks_logger("ToolUseContextRules")


def read_file(filepath: str) -> str:
    """Read file contents.

    Args:
        filepath: Path to file to read.

    Returns:
        str: File contents.
    """
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def iter_string_values(value: str | dict | list) -> Generator[str, None, None]:
    """Recursively yield string values from nested structures.

    Args:
        value: Value to extract strings from (str, dict, or list).

    Yields:
        str: String values found in value or nested dicts/lists.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from iter_string_values(v)
    elif isinstance(value, list):
        for v in value:
            yield from iter_string_values(v)


def tool_input_matches(payload: dict, pattern: re.Pattern) -> bool:
    """Check if pattern matches any string in tool_input.

    Args:
        payload: Hook payload dict.
        pattern: Compiled regex pattern to search for.

    Returns:
        bool: True if pattern matches any string value in tool_input.
    """
    tool_input = get_by_key(payload, "tool_input") or {}
    return any(pattern.search(v) for v in iter_string_values(tool_input))


# Add new rules here. Each rule: a name, and a `match(payload)` predicate that
# decides whether `additionalContext` gets injected for this hook call.
RULES = [
    {
        "name": "plan-mode-ask-user-question-grilling",
        "match": lambda payload: (
            get_by_key(payload, "hook_event_name") == "PreToolUse"
            and (
                get_by_key(payload, "tool_name") == "AskUserQuestion"
                or get_by_key(payload, "tool_name") == "UserPromptSubmit"
            )
            and get_by_key(payload, "permission_mode") == "plan"
        ),
        "additionalContext": (
            "use the skill `grilling` for Grill the user relentlessly about "
            "a plan or design. Use when the user wants to stress-test a plan "
            "before building, or uses any 'grill' trigger phrases."
        ),
    },
]


def main() -> None:
    """Entry point: inject additionalContext based on matching rules."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    hook_event_name = get_by_key(payload, "hook_event_name")
    tool_name = get_by_key(payload, "tool_name")
    if not tool_name or not hook_event_name:
        sys.exit(0)

    matched = [rule for rule in RULES if rule["match"](payload)]
    if not matched:
        sys.exit(0)

    contexts = [rule["additionalContext"] for rule in matched]
    LOG.debug("Matched rules: %s", [r["name"] for r in matched])

    output = {
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": minify_markdown("\n\n".join(contexts)),
        }
    }
    output_json = json.dumps(output, ensure_ascii=False)
    LOG.debug("[additionalContext]: %s", output_json)
    sys.stdout.write(output_json + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
