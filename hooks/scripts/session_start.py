#!/usr/bin/env python3
# log-tool-calls.py

import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger


logger = get_hooks_logger("session_start")
def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada
    logger.debug("## Session Started ##")
    logger.debug(payload)
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
