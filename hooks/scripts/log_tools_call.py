#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
from datetime import datetime, timezone
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger

logger = get_hooks_logger("tool-calls")
def main():
    try:
        payload = json.load(sys.stdin)

    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": payload.get("tool_name", "unknown"),
        "input": payload.get("tool_input", {}),
        "session_id": payload.get("session_id", {}),
        "transcript_path":payload.get("transcript_path", {}),
    }

    logger.debug(json.dumps(entry))
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
