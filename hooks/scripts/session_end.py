#!/usr/bin/env python3
"""
Stop Hook (Session End) - Persist learnings during active sessions

Cross-platform (Windows, macOS, Linux)

Runs on Stop events (after each response). Extracts a meaningful summary
from the session transcript (via stdin JSON transcript_path) and updates a
session file for cross-session continuity.
"""

import json
import os
import re
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
    
from utils import  log, strip_ansi, get_sessions_dir, get_date_string, get_time_string, get_session_id_short, get_project_name, ensure_dir, read_file, write_file, run_command
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUMMARY_START_MARKER = "<!-- ECC:SUMMARY:START -->"
SUMMARY_END_MARKER = "<!-- ECC:SUMMARY:END -->"
SESSION_SEPARATOR = "\n---\n"
MAX_STDIN = 1024 * 1024  # 1 MB

# Tools that indicate a file write/edit in Copilot
_WRITE_TOOLS_COPILOT = {"write_file", "edit_file", "create_file", "apply_edit"}



# ---------------------------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------------------------

def extract_session_summary_claude(transcript_path: Path) -> dict | None:
    """
    Extract a meaningful summary from the session transcript.
    Reads the JSONL transcript and pulls out key information:
    - User messages (tasks requested)
    - Tools used
    - Files modified
    """
    content = read_file(transcript_path)
    if not content:
        return None

    lines = [l for l in content.split("\n") if l.strip()]
    user_messages: list[str] = []
    tools_used: set[str] = set()
    files_modified: set[str] = set()
    parse_errors = 0

    for line in lines:
        try:
            entry = json.loads(line)

            # Collect user messages (first 200 chars each)
            role = entry.get("type") or entry.get("role") or (entry.get("message") or {}).get("role")
            if role == "user":
                raw_content = (
                    (entry.get("message") or {}).get("content")
                    or entry.get("content")
                    or ""
                )
                if isinstance(raw_content, str):
                    text = raw_content
                elif isinstance(raw_content, list):
                    text = " ".join(
                        (c.get("text") or "") for c in raw_content if isinstance(c, dict)
                    )
                else:
                    text = ""
                cleaned = strip_ansi(text).strip()
                if cleaned:
                    user_messages.append(cleaned[:200])

            # Collect tool names and modified files (direct tool_use entries)
            if entry.get("type") == "tool_use" or entry.get("tool_name"):
                tool_name = entry.get("tool_name") or entry.get("name") or ""
                if tool_name:
                    tools_used.add(tool_name)
                tool_input = entry.get("tool_input") or entry.get("input") or {}
                file_path = tool_input.get("file_path", "")
                if file_path and tool_name in ("Edit", "Write"):
                    files_modified.add(file_path)

            # Extract tool uses from assistant message content blocks
            if entry.get("type") == "assistant":
                message = entry.get("message") or {}
                content_blocks = message.get("content") or []
                if isinstance(content_blocks, list):
                    for block in content_blocks:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use":
                            tool_name = block.get("name") or ""
                            if tool_name:
                                tools_used.add(tool_name)
                            file_path = (block.get("input") or {}).get("file_path", "")
                            if file_path and tool_name in ("Edit", "Write"):
                                files_modified.add(file_path)

        except (json.JSONDecodeError, AttributeError):
            parse_errors += 1

    if parse_errors > 0:
        log(f"[SessionEnd] Skipped {parse_errors}/{len(lines)} unparseable transcript lines")

    if not user_messages:
        return None

    return {
        "user_messages": user_messages[-10:],   # Last 10 user messages
        "tools_used": list(tools_used)[:20],
        "files_modified": list(files_modified)[:30],
        "total_messages": len(user_messages),
    }



def extract_session_summary_copilot(transcript_path: Path) -> dict | None:
    """
    Extract a meaningful summary from the session transcript.
    Reads the JSONL transcript and pulls out key information:
    - User messages (tasks requested)
    - Tools used
    - Files modified
    """
    content = read_file(transcript_path)
    if not content:
        return None

    lines = [l for l in content.split("\n") if l.strip()]
    user_messages: list[str] = []
    tools_used: set[str] = set()
    files_modified: set[str] = set()
    parse_errors = 0

    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue
        entry_type = entry.get("type", "")
        data = entry.get("data") or {}

            # ── User messages ────────────────────────────────────────────────
        if entry_type == "user.message":
            raw = data.get("content", "")
            if isinstance(raw, str):
                text = raw
            elif isinstance(raw, list):
                text = " ".join(
                    (c.get("text") or "") for c in raw if isinstance(c, dict)
                )
            else:
                text = ""
            cleaned = strip_ansi(text).strip()
            if cleaned:
                user_messages.append(cleaned[:200])

        # ── Tool executions ──────────────────────────────────────────────
        elif entry_type == "tool.execution_start":
            tool_name = data.get("toolName", "")
            if tool_name:
                tools_used.add(tool_name)

            arguments = data.get("arguments") or {}
            # Copilot uses "filePath" for read_file / write_file
            file_path = (
                arguments.get("filePath")
                or arguments.get("file_path")
                or arguments.get("path")
                or ""
            )
            if file_path and tool_name in _WRITE_TOOLS_COPILOT:
                files_modified.add(file_path)

        # ── Tool requests embedded in assistant.message ──────────────────
        elif entry_type == "assistant.message":
            for req in data.get("toolRequests") or []:
                tool_name = req.get("name", "")
                if tool_name:
                    tools_used.add(tool_name)
                # arguments may be a JSON string here
                raw_args = req.get("arguments", {})
                if isinstance(raw_args, str):
                    try:
                        raw_args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        raw_args = {}
                file_path = (
                    raw_args.get("filePath")
                    or raw_args.get("file_path")
                    or raw_args.get("path")
                    or ""
                )
                if file_path and tool_name in _WRITE_TOOLS_COPILOT:
                    files_modified.add(file_path)

    if not user_messages:
        return None

    return {
        "user_messages": user_messages[-10:],
        "tools_used": list(tools_used)[:20],
        "files_modified": list(files_modified)[:30],
        "total_messages": len(user_messages),
    }


# ---------------------------------------------------------------------------
# Session file building
# ---------------------------------------------------------------------------

def get_session_metadata() -> dict:
    branch_result = run_command("git rev-parse --abbrev-ref HEAD")
    return {
        "project": get_project_name() or "unknown",
        "branch": branch_result["output"] if branch_result["success"] else "unknown",
        "worktree": str(Path.cwd()),
    }


def extract_header_field(header: str, label: str) -> str | None:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+)$"
    match = re.search(pattern, header, re.MULTILINE)
    return match.group(1).strip() if match else None


def build_session_header(
    today: str,
    current_time: str,
    metadata: dict,
    existing_content: str = "",
) -> str:
    heading_match = re.search(r"^#\s+.+$", existing_content, re.MULTILINE)
    heading = heading_match.group(0) if heading_match else f"# Session: {today}"
    date = extract_header_field(existing_content, "Date") or today
    started = extract_header_field(existing_content, "Started") or current_time

    lines = [
        heading,
        f"**Date:** {date}",
        f"**Started:** {started}",
        f"**Last Updated:** {current_time}",
        f"**Project:** {metadata['project']}",
        f"**Branch:** {metadata['branch']}",
        f"**Worktree:** {metadata['worktree']}",
        "",
    ]
    return "\n".join(lines)


def merge_session_header(
    content: str,
    today: str,
    current_time: str,
    metadata: dict,
) -> str | None:
    separator_index = content.find(SESSION_SEPARATOR)
    if separator_index == -1:
        return None

    existing_header = content[:separator_index]
    body = content[separator_index + len(SESSION_SEPARATOR):]
    next_header = build_session_header(today, current_time, metadata, existing_header)
    return f"{next_header}{SESSION_SEPARATOR}{body}"


def build_summary_section(summary: dict) -> str:
    section = "## Session Summary\n\n"

    # Tasks
    section += "### Tasks\n"
    for msg in summary["user_messages"]:
        safe_msg = msg.replace("\n", " ").replace("`", "\\`")
        section += f"- {safe_msg}\n"
    section += "\n"

    # Files modified
    if summary["files_modified"]:
        section += "### Files Modified\n"
        for f in summary["files_modified"]:
            section += f"- {f}\n"
        section += "\n"

    # Tools used
    if summary["tools_used"]:
        section += f"### Tools Used\n{', '.join(summary['tools_used'])}\n\n"

    section += f"### Stats\n- Total user messages: {summary['total_messages']}\n"
    return section


def build_summary_block(summary: dict) -> str:
    return f"{SUMMARY_START_MARKER}\n{build_summary_section(summary).strip()}\n{SUMMARY_END_MARKER}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Read stdin (limited to MAX_STDIN)
    stdin_data = ""
    try:
        raw = sys.stdin.read(MAX_STDIN)
        stdin_data = raw
    except Exception:
        pass

    # Parse stdin JSON to get transcript_path
    transcript_path: Path | None = None
    try:
        data = json.loads(stdin_data)
        if data.get("transcript_path"):
            transcript_path = Path(data["transcript_path"])
    except (json.JSONDecodeError, ValueError):
        # Fallback: env var for backwards compatibility
        env_path = os.environ.get("CLAUDE_TRANSCRIPT_PATH")
        if env_path:
            transcript_path = Path(env_path)

    sessions_dir = get_sessions_dir()
    today = get_date_string()
    short_id = get_session_id_short()
    session_file = sessions_dir / f"{today}-{short_id}-session.tmp"
    session_metadata = get_session_metadata()

    ensure_dir(sessions_dir)
    current_time = get_time_string()

    # Try to extract summary from transcript
    summary: dict | None = None
    if transcript_path:
        if transcript_path.exists():
            summary = extract_session_summary_copilot(transcript_path)
        else:
            log(f"[SessionEnd] Transcript not found: {transcript_path}")

    if session_file.exists():
        existing = read_file(session_file)
        updated_content = existing or ""

        if existing:
            merged = merge_session_header(existing, today, current_time, session_metadata)
            if merged:
                updated_content = merged
            else:
                log(f"[SessionEnd] Failed to normalize header in {session_file}")

        # Update only the generated summary block (idempotent)
        if summary and updated_content:
            summary_block = build_summary_block(summary)

            if SUMMARY_START_MARKER in updated_content and SUMMARY_END_MARKER in updated_content:
                pattern = (
                    re.escape(SUMMARY_START_MARKER)
                    + r"[\s\S]*?"
                    + re.escape(SUMMARY_END_MARKER)
                )
                updated_content = re.sub(pattern, summary_block, updated_content)

        if updated_content:
            write_file(session_file, updated_content)

        log(f"[SessionEnd] Updated session file: {session_file}")

    else:
        # Create new session file
        if summary:
            summary_section = (
                f"{build_summary_block(summary)}\n\n"
            )
        else:
            summary_section = (
                "## Current State\n\n"
                "[Session context goes here]\n\n"
                "### Completed\n- [ ]\n\n"
                "### In Progress\n- [ ]\n\n"
            )

        header = build_session_header(today, current_time, session_metadata)
        template = f"{header}{SESSION_SEPARATOR}{summary_section}\n"
        write_file(session_file, template)
        log(f"[SessionEnd] Created session file: {session_file}")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SessionEnd] Error: {exc}", file=sys.stderr)
        sys.exit(0)
