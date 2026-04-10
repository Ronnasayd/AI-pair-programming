#!/usr/bin/env python3
"""
Strategic Compact Suggester

Cross-platform (Windows, macOS, Linux)

Runs on PreToolUse or periodically to suggest manual compaction at logical intervals

Why manual over auto-compact:
- Auto-compact happens at arbitrary points, often mid-task
- Strategic compacting preserves context through logical phases
- Compact after exploration, before execution
- Compact after completing a milestone, before starting next
"""

import json
import os
import sys
import tempfile

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("CompactSuggester")

def get_temp_dir():
    """Get the system temporary directory."""
    return tempfile.gettempdir()


def log(message):
    """Log a message to stdout."""
    logger.debug(message)
    print(json.dumps({"hookSpecificOutput": {"additionalContext": message}}))


def log_error(message):
    """Log an error message to stderr."""
    logger.debug(message)
    print(json.dumps({"hookSpecificOutput": {"error": message}}), file=sys.stderr, flush=True)


def main():
    """Main function to track tool calls and suggest compaction."""
    # Track tool call count (increment in a temp file)
    # Use a session-specific counter file based on session ID from environment
    # or process ID as fallback
    payload = json.load(sys.stdin)
    session_id = get_by_key(payload, "session_id") 

    counter_file =   f"/tmp/tool-count-{session_id[:8]}"
    logger.debug(f"Using counter file: {counter_file}")
    threshold = 2

    try:
        # Validate threshold is in reasonable range
        if threshold <= 0 or threshold > 10000:
            threshold = 50
    except ValueError:
        threshold = 50

    count = 1

    # Read existing count or start at 1
    try:
        if os.path.exists(counter_file):
            with open(counter_file, "r") as f:
                content = f.read().strip()
                if content:
                    try:
                        parsed = int(content)
                        # Clamp to reasonable range — corrupted files could contain huge values
                        if 0 < parsed <= 1000000:
                            count = parsed + 1
                        else:
                            count = 1
                    except ValueError:
                        count = 1

        # Write new count
        with open(counter_file, "w") as f:
            f.write(str(count))

    except Exception as e:
        # Fallback: just continue if file operations fail
        log_error(f"[StrategicCompact] Warning: Could not access counter file: {e}")

    # Suggest compact after threshold tool calls
    if count == threshold:
        logger.debug(f"Tool call count reached threshold: {threshold}")
        log(
            f"[StrategicCompact] {threshold} tool calls reached - consider /compact if transitioning phases"
        )

    # Suggest at regular intervals after threshold (every 25 calls from threshold)
    if count > threshold and (count - threshold) % 25 == 0:
        logger.debug(f"Tool call count reached interval: {count}")
        log(
            f"[StrategicCompact] {count} tool calls - good checkpoint for /compact if context is stale"
        )

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        log_error(f"[StrategicCompact] Error: {err}")
        sys.exit(2)
