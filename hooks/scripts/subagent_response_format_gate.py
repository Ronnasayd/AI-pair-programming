#!/usr/bin/python3
"""SubagentStop hook.

Blocks a subagent from stopping when its final message does not follow the
mandatory response format (hooks/markdown/SUBAGENT-RESPONSE-TEMPLATE.md):
a `status:` field is required, and `reason:` is required whenever status is
not `success`. Advisory-only fields (files_changed/evidence/gateways) are not
enforced here, only the two fields that make the report machine-checkable.
"""

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    bump_loop_count,
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    minify_json,
    project_dir,
    read_loop_count,
)

LOG = get_hooks_logger("SubagentResponseFormatGate")

LOOP_NAMESPACE = "subagent-format-loop-count"
MAX_LOOPS = 5
STATUS_RE = re.compile(
    r"^\s*status\s*:\s*(success|failure|partial)\s*$", re.IGNORECASE | re.MULTILINE
)
REASON_RE = re.compile(r"^\s*reason\s*:\s*\S", re.IGNORECASE | re.MULTILINE)


def missing_fields(message: str) -> list[str]:
    """Return which mandatory fields are absent from the subagent's final message.

    Args:
        message: the subagent's last assistant message (its final report).

    Returns:
        list[str]: names of missing mandatory fields, empty if the report is valid.
    """
    missing = []
    status_match = STATUS_RE.search(message)
    if not status_match:
        missing.append("status")
    elif status_match.group(1).lower() != "success" and not REASON_RE.search(message):
        missing.append("reason")
    return missing


def main() -> None:
    """Read the hook payload from stdin, block stop if response format is invalid."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    message = get_by_key(payload, "last_assistant_message") or ""
    if not message.strip():
        sys.exit(0)

    missing = missing_fields(message)
    if not missing:
        sys.exit(0)

    project_root = project_dir(payload)
    agent_id = get_by_key(payload, "agent_id") or get_session_id_short(
        get_by_key(payload, "session_id") or ""
    )

    loop_count = read_loop_count(project_root, LOOP_NAMESPACE, agent_id) + 1
    if loop_count > MAX_LOOPS:
        LOG.debug("Loop cap hit (%d/%d), letting subagent stop", loop_count, MAX_LOOPS)
        sys.exit(0)
    bump_loop_count(project_root, LOOP_NAMESPACE, agent_id, loop_count)

    reason = (
        "Your final report is missing required field(s): "
        f"{', '.join(missing)}. Re-send your report following the mandatory "
        "response format (status/summary/files_changed/reason/evidence/"
        "gateways/next_steps) from hooks/markdown/SUBAGENT-RESPONSE-TEMPLATE.md."
    )
    output = {"decision": "block", "reason": reason}
    LOG.debug("[block] (%d/%d): %s", loop_count, MAX_LOOPS, minify_json(output))
    print(minify_json(output))  # noqa: T201 - hook stdout protocol
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # why: hook must never crash the harness, degrade to no-op
        LOG.debug("Error: %s", exc)
        sys.exit(0)
