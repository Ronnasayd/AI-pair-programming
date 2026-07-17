#!/usr/bin/python3

import argparse
import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import colorize_json, get_hooks_logger  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", default="/tmp/hooks.log")
    return parser.parse_args()


def main():
    args = parse_args()
    logger = get_hooks_logger("Hooks", log_file=args.log_file)
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
