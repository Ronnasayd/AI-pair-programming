#!/usr/bin/python3
"""
Semantic-Similar-Refs Hook (POC)

PreToolUse hook for Edit|Write. Queries rag-rat's semantic_search with the
content about to be written and surfaces similar existing code, so the agent
doesn't duplicate what's already there. Requires a rag-rat index; the caller
(claude/settings.json) gates execution on `rag-rat` being installed, and this
script additionally requires a `rag-rat.toml` in cwd — no other fallback.
"""

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
    get_by_key,
    get_hooks_logger,
    is_rag_rat_available,
)

logger = get_hooks_logger("SemanticSimilarRefs")

MAX_STDIN = 1024 * 1024
MAX_EMBED_CHARS = 4000
MAX_RESULTS = 3
SEMANTIC_SEARCH_TIMEOUT = 10

SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go"}

# Each hit is a "  - chunk_id: ...\n    path: ...\n    ...\n    summary: \"...\"\n" block.
PATH_RE = re.compile(r'^\s*path:\s*"?([^"\n]+)"?', re.MULTILINE)
SUMMARY_RE = re.compile(r'^\s*summary:\s*"(.*?)"\s*$', re.MULTILINE)


def semantic_search_blocks(
    content: str, target_file: str, cwd: str
) -> list[str] | None:
    """Query rag-rat's semantic_search with the new code as the query text.
    Returns formatted blocks, or None if rag-rat errors."""
    query = content[:MAX_EMBED_CHARS]
    text = call_rag_rat_tool(
        "semantic_search",
        {"query": query, "limit": MAX_RESULTS},
        cwd,
        logger,
        timeout=SEMANTIC_SEARCH_TIMEOUT,
    )
    if not text:
        return None

    blocks = []
    for hit in re.split(r"^  - chunk_id:", text, flags=re.MULTILINE)[1:]:
        path_m = PATH_RE.search(hit)
        path = path_m.group(1) if path_m else None
        summary_m = SUMMARY_RE.search(hit)
        snippet = summary_m.group(1) if summary_m else ""
        if not path or not snippet:
            continue
        if Path(path).resolve() == Path(target_file).resolve():
            continue
        snippet = snippet.replace("\\n", "\n").replace('\\"', '"')
        blocks.append(f"=== semantically similar code in {path} ===\n{snippet}")
        if len(blocks) >= MAX_RESULTS:
            break

    return blocks


def build_context(content: str, target_file: str, cwd: str) -> str:
    if not is_rag_rat_available(cwd):
        logger.debug("rag-rat not available (binary or rag-rat.toml missing)")
        return ""

    blocks = semantic_search_blocks(content, target_file, cwd)
    if not blocks:
        logger.debug("no semantic_search blocks found or rag-rat call failed")
        return ""

    logger.debug("build_context: %d blocks from rag-rat semantic_search", len(blocks))
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

    logger.debug("tool_name=%s", tool_name)

    if tool_name not in ("Edit", "Write") or not tool_input:
        logger.debug("skipping: tool_name not in (Edit, Write) or no tool_input")
        sys.exit(0)

    file_path = get_by_key(tool_input, "file_path") or ""
    content = (
        get_by_key(tool_input, "content") or get_by_key(tool_input, "new_string") or ""
    )

    logger.debug("file_path=%s content_len=%d", file_path, len(content))

    if not file_path or not content:
        logger.debug("skipping: missing file_path or content")
        sys.exit(0)

    if Path(file_path).suffix.lower() not in SOURCE_EXTS:
        logger.debug("skipping: %s is not a source file", file_path)
        sys.exit(0)

    cwd = get_by_key(data, "cwd") or "."
    context = build_context(content, file_path, cwd)
    if context:
        output = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": context,
                }
            }
        )
        logger.debug(f"[additionalContext]: {output}")
        print(output)
    else:
        logger.debug("no context found, emitting nothing")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.debug("Error: %s", exc, exc_info=True)
        sys.exit(0)
