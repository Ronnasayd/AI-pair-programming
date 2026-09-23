#!/usr/bin/python3
"""PostToolUse hook: scan tool output for secrets and redact them in place.

Runs after the tool executes (unlike protect_files.py's PreToolUse deny),
so it never blocks — it rewrites the output Claude sees via
hookSpecificOutput.updatedToolOutput, which for a built-in tool replaces
the whole tool_response object (not a bare string) — confirmed against
claude/claude-hooks-reference.md and by testing a bare top-level string
(harness-toolkit's own shape) against a live Read/Bash call, which the
installed Claude Code version silently ignored.
"""

from collections.abc import Mapping
import hashlib
import json
import os
import re
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from secret_scan import scan_content_for_secrets  # noqa: E402
from utils import get_by_key, get_hooks_logger  # noqa: E402

logger = get_hooks_logger("ScanSecretsOutput")


def scan_for_secrets(text: str) -> list[dict]:
    """Scan text for secrets via detect-secrets, or the regex fallback.

    Normalizes detect-secrets' `line_number` key to `line` (the fallback's
    own key) so redact() has one shape to handle.

    Args:
        text: Tool output to scan.

    Returns:
        Findings as {type, line} — redaction always replaces the whole line.
    """
    findings = scan_content_for_secrets(text, "tool_output.txt", logger)
    return [
        {"type": f.get("type", "Secret"), "line": f.get("line") or f.get("line_number")}
        for f in findings
        if f.get("line") or f.get("line_number")
    ]


def placeholder_for(matched_text: str, kind: str) -> str:
    """Stable placeholder for a matched secret, keyed by a hash — never the raw value.

    Args:
        matched_text: The exact text that matched (hashed, never stored raw).
        kind: The finding's type/kind label.

    Returns:
        A `[REDACTED:<kind>:<hash>]` placeholder string.
    """
    digest = hashlib.sha256(matched_text.encode("utf-8")).hexdigest()[:8]
    safe_kind = re.sub(r"[^A-Za-z0-9_-]", "_", kind)
    return f"[REDACTED:{safe_kind}:{digest}]"


def redact(text: str, findings: list[dict]) -> str:
    """Replace each finding's whole line with a placeholder.

    Args:
        text: Original tool output.
        findings: Findings from scan_for_secrets (type, line).

    Returns:
        text with every flagged line replaced by its placeholder.
    """
    lines = text.split("\n")
    by_line: dict[int, list[dict]] = {}
    for f in findings:
        by_line.setdefault(f["line"], []).append(f)

    for line_no, line_findings in by_line.items():
        idx = line_no - 1
        if 0 <= idx < len(lines):
            kinds = ",".join(sorted({f["type"] for f in line_findings}))
            lines[idx] = placeholder_for(lines[idx], kinds)

    return "\n".join(lines)


# why: order matters — Bash's tool_response has stdout at top level; Read's
# real text sits nested at tool_response.file.content (confirmed by logging
# a live Read payload), not tool_response.content.
_TEXT_PATHS: tuple[tuple[str, ...], ...] = (
    ("stdout",),
    ("file", "content"),
    ("output",),
    ("text",),
)


def extract_output_field(payload: Mapping) -> tuple[tuple[str, ...], str] | None:
    """Find the (key-path, text) pair carrying the tool's textual output.

    Args:
        payload: The hook's stdin JSON payload.

    Returns:
        (key_path, text) for the first matching field, or None if
        tool_response isn't a dict with any known text field.
    """
    tool_response = get_by_key(payload, "tool_response")
    if not isinstance(tool_response, Mapping):
        return None
    for path in _TEXT_PATHS:
        node: object = tool_response
        for segment in path:
            if not isinstance(node, Mapping):
                node = None
                break
            node = get_by_key(node, segment)
        if isinstance(node, str):
            return path, node
    return None


def apply_masked_field(
    tool_response: Mapping, path: tuple[str, ...], masked: str
) -> dict:
    """Rebuild tool_response with `masked` written at the given nested path.

    Args:
        tool_response: The original tool_response mapping.
        path: Key path where the matched text field was found.
        masked: The redacted replacement text.

    Returns:
        A new dict, deep-copied only along `path`, with the text swapped in.
    """
    if len(path) == 1:
        return {**tool_response, path[0]: masked}
    head, *rest = path
    nested = get_by_key(tool_response, head) or {}
    return {**tool_response, head: apply_masked_field(nested, tuple(rest), masked)}


def main() -> None:
    """Run the PostToolUse hook: scan tool output for secrets, redact, exit."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug("Invalid JSON: %s", e)
        sys.exit(0)

    found = extract_output_field(payload)
    if not found:
        sys.exit(0)
    path, output = found

    findings = scan_for_secrets(output)
    if not findings:
        sys.exit(0)

    masked = redact(output, findings)
    logger.debug("Redacted %d secret(s) from tool output", len(findings))

    tool_response = get_by_key(payload, "tool_response") or {}
    # why: updatedToolOutput replaces the whole tool_response object, not
    # just a string — Bash's shape is {stdout, stderr, ...}, Read's is
    # {type, file: {content, ...}}. Rebuilding only along the matched path
    # keeps every other field (and sibling nesting) intact.
    updated_response = apply_masked_field(tool_response, path, masked)
    output = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "updatedToolOutput": updated_response,
            }
        }
    )
    logger.debug("[additionalContext]: %s", output)
    sys.stdout.write(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
