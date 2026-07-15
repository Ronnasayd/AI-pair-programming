#!/usr/bin/env python3
"""Extract only genuine human-typed prompts from Claude Code session transcripts (.jsonl).

Usage:
    python extract_user_prompts.py <glob-pattern> [<glob-pattern> ...] --out <output-file>

Example:
    python extract_user_prompts.py "$HOME/.claude/projects/-path-to-project/*.jsonl" --out user_prompts_only.txt

Filters strictly on type == "user" AND promptSource == "typed" to exclude
tool results, system-reminders, and injected skill content that also carry
role "user" in the raw transcript. Verify this schema still holds by reading
one raw line before trusting the filter (see SKILL.md Step 1).
"""

import argparse
import glob
import json


def extract_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "\n".join(p for p in parts if p)
    return ""


def process_file(path: str, out) -> int:
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "user":
                continue
            if obj.get("promptSource") != "typed":
                continue
            text = extract_text(obj.get("message", {}).get("content")).strip()
            if not text:
                continue
            ts = obj.get("timestamp", "")
            out.write(f"[{ts}] {text}\n\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "patterns", nargs="+", help="Glob pattern(s) for session .jsonl files"
    )
    parser.add_argument("--out", required=True, help="Output file path")
    args = parser.parse_args()

    total = 0
    with open(args.out, "w", encoding="utf-8") as out:
        for pattern in args.patterns:
            for path in sorted(glob.glob(pattern)):
                total += process_file(path, out)

    print(f"Wrote {total} human prompts from matched sessions to {args.out}")


if __name__ == "__main__":
    main()
