#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
from datetime import datetime, timezone
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("ToolCalls")
def main():
    try:
        payload = json.load(sys.stdin)

    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": get_by_key(payload, "tool_name") or "unknown",
        "input": get_by_key(payload, "tool_input") or {},
        "session_id": get_by_key(payload, "session_id") or {},
        "transcript_path": get_by_key(payload, "transcript_path") or {},
    }

    logger.debug(json.dumps(entry))
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
