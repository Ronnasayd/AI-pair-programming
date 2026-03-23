#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from os import makedirs

def get_session_log_file(session_id):
    """Find the existing session log file for the given session_id, or create new one"""
    sessions_dir = Path("/tmp/sessions")
    makedirs(sessions_dir, exist_ok=True)
    
    # Look for files matching pattern with this session_id
    pattern = f"*-{session_id}.log"
    matching_files = list(sessions_dir.glob(pattern))
    
    if matching_files:
        # Return the most recently modified file (created by session_start)
        return max(matching_files, key=lambda p: p.stat().st_mtime)
    
    # Fallback: create new file if none exists
    return sessions_dir / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{session_id}.log"

def main():
    try:
        payload = json.load(sys.stdin)
        session_id = payload.get("session_id", {})
        LOG_FILE = get_session_log_file(session_id)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("tool-calls")
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)
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
