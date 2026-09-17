#!/usr/bin/python3
"""
Structural-Clone-Ref Hook (POC)

PostToolUse hook for Edit|Write. After a source file is written, extracts
its top-level def/class names and asks rag-rat's clones_for_symbol whether
each one belongs to a structural clone class elsewhere in the repo (token-
overlap duplication, not just semantic similarity). Surfaces the other
members so the agent can consider extracting a shared helper.

Runs per-symbol (not a full-repo find_clones scan) to stay cheap on every
edit. Requires a rag-rat index; the caller (claude/settings.json) gates
execution on `rag-rat` being installed and `rag-rat.toml` existing.
"""

import csv
import io
import json
import os
import re
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    call_rag_rat_tool,
    extract_code_info,
    get_by_key,
    get_hooks_logger,
    is_rag_rat_available,
)

logger = get_hooks_logger("StructuralCloneRef")

MAX_STDIN = 1024 * 1024
MAX_DEFS = 3
MAX_MEMBERS_PER_DEF = 3
CLONES_FOR_SYMBOL_TIMEOUT = 10

SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go"}

NO_CLONE_RE = re.compile(r"^class:\s*null\s*$", re.MULTILINE)
MEMBERS_BLOCK_RE = re.compile(
    r"members\[\d+\]\{ref,path,start_line,end_line,token_len,language\}:\s*\n"
    r"((?:.+\n)+?)"
    r"\s*member_count:",
)


def parse_members(text: str) -> list[tuple[str, str, str, str]]:
    """Parse the `members[N]{ref,path,start_line,end_line,...}:` CSV block
    from a clones_for_symbol response into (ref, path, start_line, end_line)
    tuples."""
    block_m = MEMBERS_BLOCK_RE.search(text)
    if not block_m:
        return []

    rows = []
    for line in block_m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            fields = next(csv.reader(io.StringIO(line)))
        except csv.Error:
            continue
        if len(fields) < 4:
            continue
        rows.append((fields[0], fields[1], fields[2], fields[3]))
    return rows


def clone_block_for_def(
    def_name: str, rel_path: str, target_file: str, cwd: str
) -> str | None:
    """Query clones_for_symbol for one def/class name; returns a formatted
    block listing the OTHER members of its clone class, or None if it's not
    part of one."""
    ref = f"{rel_path}::{def_name}"
    text = call_rag_rat_tool(
        "clones_for_symbol",
        {"ref": ref},
        cwd,
        logger,
        timeout=CLONES_FOR_SYMBOL_TIMEOUT,
    )
    if not text or NO_CLONE_RE.search(text):
        return None

    members = parse_members(text)
    others = [
        m for m in members if Path(m[1]).resolve() != Path(target_file).resolve()
    ][:MAX_MEMBERS_PER_DEF]
    if not others:
        return None

    lines = "\n".join(f"  - {path}:{start}-{end}" for _, path, start, end in others)
    return f"=== `{def_name}` is a structural clone of ===\n{lines}"


def build_context(content: str, target_file: str, rel_path: str, cwd: str) -> str:
    if not is_rag_rat_available(cwd):
        logger.debug("rag-rat not available (binary or rag-rat.toml missing)")
        return ""

    info = extract_code_info(content, target_file)
    defs: list[str] = []
    seen: set[str] = set()
    for name in info["defs"]:
        if name in seen:
            continue
        seen.add(name)
        defs.append(name)
        if len(defs) >= MAX_DEFS:
            break

    if not defs:
        logger.debug("no top-level defs/classes found, skipping")
        return ""

    blocks = []
    for name in defs:
        block = clone_block_for_def(name, rel_path, target_file, cwd)
        if block:
            blocks.append(block)

    logger.debug("build_context: %d clone blocks for defs=%s", len(blocks), defs)
    return "\n\n".join(blocks)


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_name = get_by_key(data, "tool_name")
        tool_input = get_by_key(data, "tool_input")
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("failed to parse stdin json: %s", exc)
        sys.exit(0)

    if tool_name not in ("Edit", "Write") or not tool_input:
        logger.debug("skipping: tool_name not in (Edit, Write) or no tool_input")
        sys.exit(0)

    file_path = get_by_key(tool_input, "file_path") or ""
    if not file_path:
        logger.debug("skipping: missing file_path")
        sys.exit(0)

    resolved = Path(file_path)
    if resolved.suffix.lower() not in SOURCE_EXTS:
        logger.debug("skipping: %s is not a source file", file_path)
        sys.exit(0)

    if not resolved.is_absolute():
        cwd_hint = get_by_key(data, "cwd") or "."
        resolved = Path(cwd_hint) / resolved
    resolved = resolved.resolve()

    if not resolved.exists():
        logger.debug("skipping: %s does not exist on disk", resolved)
        sys.exit(0)

    try:
        content = resolved.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        logger.debug("failed to read %s: %s", resolved, exc)
        sys.exit(0)

    cwd = get_by_key(data, "cwd") or "."
    cwd_resolved = Path(cwd).resolve()
    try:
        rel_path = resolved.relative_to(cwd_resolved).as_posix()
    except ValueError:
        rel_path = resolved.as_posix()

    logger.debug("file_path=%s rel_path=%s cwd=%s", resolved, rel_path, cwd_resolved)

    context = build_context(content, str(resolved), rel_path, str(cwd_resolved))
    if context:
        output = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
        logger.debug(f"[additionalContext]: {output}")
        print(output)
    else:
        logger.debug("no clone context found, emitting nothing")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.debug("Error: %s", exc, exc_info=True)
        sys.exit(0)
