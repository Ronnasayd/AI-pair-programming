#!/usr/bin/python3

import sys
import json
import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger

logger = get_hooks_logger("Hooks")

_KEY_COLOR = "\033[36m"  # cyan
_VALUE_COLOR = "\033[32m"  # green
_RESET = "\033[0m"


def colorize_json(payload) -> str:
    """Dump JSON with ANSI-colored keys and values."""
    text = json.dumps(payload, indent=2)
    text = re.sub(r'(".*?")(\s*:)', rf"{_KEY_COLOR}\1{_RESET}\2", text)
    text = re.sub(
        r'(:\s*)("(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?|true|false|null)',
        rf"\1{_VALUE_COLOR}\2{_RESET}",
        text,
    )
    return text


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
