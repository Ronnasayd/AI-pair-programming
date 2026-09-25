#!/usr/bin/python3
"""Pre-warm embedding daemon on hook startup."""

import os
from pathlib import Path
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger, get_project_name  # noqa: E402

DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"

logger = get_hooks_logger("StartEmbedding")


def prewarmEmbeddingDaemon() -> None:  # noqa: N802
    """Start embedding daemon if socket doesn't exist."""
    sock_path = f"/tmp/embedding-daemon-{get_project_name()}.sock"  # noqa: S108
    if Path(sock_path).exists():
        return
    logger.debug("Pre-warming embedding daemon")
    with subprocess.Popen(  # noqa: S603
        [sys.executable, str(DAEMON_SCRIPT)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ):
        pass


def main() -> None:
    """Invoke embedding daemon pre-warming."""
    prewarmEmbeddingDaemon()
    sys.exit(0)


if __name__ == "__main__":
    main()
