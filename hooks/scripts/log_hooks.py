#!/usr/bin/python3

import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import colorize_json, get_hooks_logger

logger = get_hooks_logger("Hooks")


def main():
    try:
        payload = json.load(sys.stdin)

    except json.JSONDecodeError:
        sys.exit(0)  # erro no parse não bloqueia nada

    if os.environ.get("JSON_COLORIZE"):
        logger.debug(colorize_json(payload))
    else:
        logger.debug(json.dumps(payload))
    sys.exit(0)  # nunca bloqueia


if __name__ == "__main__":
    main()
