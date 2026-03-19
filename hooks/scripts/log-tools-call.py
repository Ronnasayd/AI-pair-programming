#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("/tmp") / "tool-calls.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("tool-calls")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(file_handler)

def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": payload.get("tool_name", "unknown"),
        "input": payload.get("tool_input", {}),
    }

    logger.debug(json.dumps(entry))
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
