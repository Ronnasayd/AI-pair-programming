"""
Concurrent lint auto-fix script using the Claude Agent SDK.

Runs ESLint with JSON output, groups errors per file, then spawns one
Claude Haiku subagent per file to fix them — capped at 5 concurrent agents.

Usage:
    python lint_fix_agent.py <directory> [--concurrency 5] [--eslint-args "--ext .ts,.tsx"]

Example:
    python lint_fix_agent.py ./src
    python lint_fix_agent.py ./src --concurrency 8 --eslint-args "--ext .js,.jsx"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

MODEL = "claude-haiku-4-5-20251001"
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


def run_eslint(directory: Path, eslint_args: str) -> list[dict]:
    """Run ESLint with JSON formatter and return the parsed report."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        report_path = Path(tmp.name)

    cmd = [
        "npx",
        "eslint",
        str(directory),
        "--format",
        "json",
        "--output-file",
        str(report_path),
    ] + eslint_args.split()
    print(f"Running: {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, capture_output=True, text=True)

    if not report_path.exists() or report_path.stat().st_size == 0:
        return []

    report = json.loads(report_path.read_text())
    report_path.unlink(missing_ok=True)
    return report


def files_with_errors(report: list[dict]) -> dict[str, str]:
    """Map file path -> formatted error text, skipping clean files."""
    result: dict[str, str] = {}
    for entry in report:
        messages = entry.get("messages", [])
        if not messages:
            continue
        lines = [
            f"line {m.get('line')}:{m.get('column')} [{m.get('ruleId')}] {m.get('message')}"
            for m in messages
        ]
        result[entry["filePath"]] = "\n".join(lines)
    return result


async def fix_file(
    semaphore: asyncio.Semaphore, project_root: Path, file_path: str, errors: str
) -> None:
    async with semaphore:
        print(f"[start] {file_path}")
        async for message in query(
            prompt=(
                f"Fix ONLY these ESLint errors in `{file_path}`:\n\n{errors}\n\n"
                "Do not touch unrelated code. Edit the file directly."
            ),
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit"],
                model=MODEL,
                cwd=str(project_root),
                settings=str(SETTINGS_PATH),
            ),
        ):
            if isinstance(message, ResultMessage):
                print(f"[done] {file_path}: {message.result}")


async def main(directory: str, concurrency: int, eslint_args: str) -> None:
    target = Path(directory).resolve()
    report = run_eslint(target, eslint_args)
    targets = files_with_errors(report)

    if not targets:
        print("No lint errors found.")
        return

    print(
        f"Found lint errors in {len(targets)} file(s). Fixing with concurrency={concurrency}.\n"
    )

    semaphore = asyncio.Semaphore(concurrency)
    await asyncio.gather(
        *(fix_file(semaphore, target, f, e) for f, e in targets.items())
    )

    print("\nDone.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ESLint, then fix reported errors concurrently with Claude Haiku subagents."
    )
    parser.add_argument("directory", help="Root directory to lint.")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Max concurrent fix agents (default: 5).",
    )
    parser.add_argument(
        "--eslint-args", default="", help='Extra ESLint args, e.g. "--ext .ts,.tsx".'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.directory, args.concurrency, args.eslint_args))
