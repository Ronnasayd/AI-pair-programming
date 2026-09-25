#!/usr/bin/python3
"""Log hooks utility for capturing and formatting hook execution logs."""

import argparse
import json
import os
from pathlib import Path
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import colorize_json, get_hooks_logger  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-file", default=str(Path.home() / ".claude" / "logs" / "hooks-tools.log")
    )
    return parser.parse_args()


def main() -> None:
    """Process JSON log input from stdin and write to log file."""
    args = parse_args()
    logger = get_hooks_logger("Hooks", log_file=args.log_file)
    colorized_logger = get_hooks_logger(
        "HooksColorized", log_file=args.log_file.replace(".log", "-colorized.log")
    )
    try:
        payload = json.load(sys.stdin)

    except json.JSONDecodeError:
        sys.exit(0)  # erro no parse não bloqueia nada

    if os.environ.get("JSON_COLORIZE"):
        colorized_logger.debug(colorize_json(payload))
        logger.debug(json.dumps(payload))
    else:
        logger.debug(json.dumps(payload))
    sys.exit(0)  # nunca bloqueia


if __name__ == "__main__":
    main()
