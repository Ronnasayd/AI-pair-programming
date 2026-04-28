"""
Linter auto-fix script using the GitHub Copilot Python SDK.

Usage:
    python linter.py <directory> <linter_command> [glob_pattern]

Examples:
    python linter.py ./src "ruff check" "**/*.py"
    python linter.py ./src "eslint" "**/*.{js,ts}"
"""

from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.generated.session_events import SessionEventType


DEFAULT_GLOB = "**/*"
MODEL = "claude-sonnet-4.6"


def _print_context_bar(used: int, total: int) -> None:
    """Print a context window usage progress bar to stderr."""
    if total <= 0:
        return
    pct = used / total
    filled = int(pct * 30)
    bar = "█" * filled + "░" * (30 - filled)
    label = f"Context: [{bar}] {pct:.1%}  ({used:,}/{total:,} tokens)"
    print(f"  {label}", file=sys.stderr)


def run_linter(linter_command: str, file_path: Path) -> tuple[int, str]:
    """Run linter on a single file and return (returncode, output)."""
    cmd = linter_command.split() + [str(file_path)]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=file_path.parent,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def collect_files(directory: Path, glob_pattern: str) -> list[Path]:
    """Return all files matching glob_pattern inside directory."""
    return [p for p in directory.glob(glob_pattern) if p.is_file()]


async def fix_linter_errors(
    session,
    file_path: Path,
    linter_output: str,
) -> None:
    """Ask Copilot to fix linter errors for a file and apply the fix."""
    source = file_path.read_text()

    prompt = (
        f"The following linter errors were found in `{file_path}`:\n\n"
        f"```\n{linter_output}\n```\n\n"
        f"Here is the current file content:\n\n"
        f"```\n{source}\n```\n\n"
        "Fix ALL linter errors"
    )

    response_parts: list[str] = []
    done = asyncio.Event()

    def on_event(event):
        if event.type == SessionEventType.ASSISTANT_REASONING_DELTA:
            chunk = event.data.delta_content or ""
            sys.stderr.write(chunk)
            sys.stderr.flush()
        elif event.type == SessionEventType.ASSISTANT_REASONING:
            # Reasoning complete — add a separator before the fix output
            sys.stderr.write("\n  [reasoning done]\n")
            sys.stderr.flush()
        elif event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            part = event.data.delta_content or ""
            response_parts.append(part)
            sys.stdout.write(part)
            sys.stdout.flush()
        elif event.type == SessionEventType.ASSISTANT_MESSAGE:
            # Fallback: non-streaming full message
            if not response_parts:
                response_parts.append(event.data.content or "")
        elif event.type == SessionEventType.SESSION_IDLE:
            done.set()

    unsubscribe = session.on(on_event)
    await session.send(prompt)
    await done.wait()
    unsubscribe()

    fixed_content = "".join(response_parts).strip()
    if fixed_content:
        print(f"\n  [fixed] {file_path}")
    else:
        print(f"\n  [skipped] No fix returned for {file_path}")


async def main(directory: str, linter_command: str, glob_pattern: str) -> None:
    target_dir = Path(directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: '{directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    files = collect_files(target_dir, glob_pattern)
    if not files:
        print(f"No files matched '{glob_pattern}' in '{target_dir}'.")
        return

    print(f"Found {len(files)} file(s) to lint with: {linter_command}\n")

    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=MODEL,
            streaming=True,
        ) as session:

            def on_compaction(event):
                event_type = (
                    event.type.value
                    if hasattr(event.type, "value")
                    else str(event.type)
                )
                data = event.data if hasattr(event, "data") else {}
                if event_type == "session.compaction_complete":
                    used = getattr(data, "tokens_used", None) or (
                        data.get("tokensUsed") if isinstance(data, dict) else None
                    )
                    total = getattr(data, "tokens_total", None) or (
                        data.get("tokensTotal") if isinstance(data, dict) else None
                    )
                    if used is not None and total is not None:
                        _print_context_bar(used, total)
                elif event_type == "session.compaction_start":
                    print("  [context] Compacting context window...", file=sys.stderr)

            session.on(on_compaction)

            for file_path in sorted(files):
                returncode, output = run_linter(linter_command, file_path)
                if returncode == 0:
                    print(f"[ok] {file_path}")
                    continue

                print(f"\n[errors] {file_path}")
                print(output)
                print(f"  -> Asking Copilot to fix...")

                await fix_linter_errors(session, file_path, output)

                # Verify fix
                returncode_after, output_after = run_linter(linter_command, file_path)
                if returncode_after == 0:
                    print(f"  [verified] Linter now passes for {file_path}")
                else:
                    print(
                        f"  [warning] Linter still reports issues for {file_path}:\n{output_after}"
                    )

    print("\nDone.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a linter on files in a directory and auto-fix errors with Copilot."
    )
    parser.add_argument("directory", help="Root directory to search files in.")
    parser.add_argument(
        "linter_command",
        help='Linter command to run (e.g. "ruff check" or "eslint").',
    )
    parser.add_argument(
        "--glob",
        default=DEFAULT_GLOB,
        help=f"Glob pattern to match files (default: '{DEFAULT_GLOB}').",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.directory, args.linter_command, args.glob))
