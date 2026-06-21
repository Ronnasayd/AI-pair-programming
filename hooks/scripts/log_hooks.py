#!/usr/bin/env python3

import sys
import json
from datetime import datetime, timezone
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("Hooks")
def main():
    try:
        payload = json.load(sys.stdin)

    except json.JSONDecodeError as e:
        sys.exit(0)  # erro no parse não bloqueia nada

    logger.debug(json.dumps(payload))
    sys.exit(0)  # nunca bloqueia

if __name__ == "__main__":
    main()
