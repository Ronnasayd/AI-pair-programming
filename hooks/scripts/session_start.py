#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
import logging
from pathlib import Path
from os import makedirs
from datetime import datetime


def main():
    try:
        payload = json.load(sys.stdin)
        makedirs("/tmp/sessions/", exist_ok=True)
        session_id = payload.get("session_id", {})
        cwd = payload.get('cwd', {})
        project_name = cwd.split("/")[-1].lower() if cwd else "unknown"
        LOG_FILE = Path("/tmp/sessions") / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{project_name}.log"
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("session_start")
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)
    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada

   

    logger.debug("## Session Started ##")
    logger.debug(payload)
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
