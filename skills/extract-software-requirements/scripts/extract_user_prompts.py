#!/usr/bin/env python3
"""Extract only genuine human-typed prompts from Claude Code session transcripts (.jsonl).

Usage:
    python extract_user_prompts.py <glob-pattern> [<glob-pattern> ...] \\
        --out <output-file> [--last-n-sessions N]

Example:
    python extract_user_prompts.py \\
        "$CLAUDE_CONFIG_DIR/projects/-path-to-project/*.jsonl" \\
        --out user_prompts_only.txt
    python extract_user_prompts.py \\
        "$CLAUDE_CONFIG_DIR/projects/-path-to-project/*.jsonl" \\
        --out out.txt --last-n-sessions 5

--last-n-sessions N: after matching all patterns, keep only the N most
recently modified session files (by mtime) instead of every match.

Filters strictly on type == "user" AND promptSource == "typed" to exclude
tool results, system-reminders, and injected skill content that also carry
role "user" in the raw transcript. Verify this schema still holds by reading
one raw line before trusting the filter (see SKILL.md Step 1).
"""

import argparse
import glob
import os
import sys
from pathlib import Path

_SIBLING_SCRIPT_DIR = (
    Path(__file__).resolve().parents[2] / "extract-automation-candidates" / "scripts"
)
if str(_SIBLING_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SIBLING_SCRIPT_DIR))

from extract_user_prompts import process_file  # noqa: E402


def main() -> None:
    """Parse arguments, extract prompts from matched session files, and report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "patterns", nargs="+", help="Glob pattern(s) for session .jsonl files"
    )
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument(
        "--last-n-sessions",
        type=int,
        default=None,
        help="Keep only the N most recently modified matched session files",
    )
    args = parser.parse_args()

    paths = sorted({path for pattern in args.patterns for path in glob.glob(pattern)})
    if args.last_n_sessions is not None:
        paths = sorted(paths, key=os.path.getmtime)[-args.last_n_sessions :]
    paths.sort()

    total = 0
    with open(args.out, "w", encoding="utf-8") as out:
        for path in paths:
            total += process_file(path, out)

    print(f"Wrote {total} human prompts from {len(paths)} session(s) to {args.out}")


if __name__ == "__main__":
    main()
