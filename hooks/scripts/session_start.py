#!/usr/bin/python3
# log-tool-calls.py

import json
import os
import subprocess
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger, get_project_name  # noqa: E402

DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"

logger = get_hooks_logger("SessionStart")


def prewarmEmbeddingDaemon() -> None:
    sock_path = f"/tmp/embedding-daemon-{get_project_name()}.sock"
    if Path(sock_path).exists():
        return
    logger.debug("Pre-warming embedding daemon")
    subprocess.Popen(
        [sys.executable, str(DAEMON_SCRIPT)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    logger.debug("## Session Started ##")
    logger.debug(payload)
    prewarmEmbeddingDaemon()
    sys.exit(0)


if __name__ == "__main__":
    main()
