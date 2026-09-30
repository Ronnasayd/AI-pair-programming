#!/usr/bin/python3
"""Semantic-Similar-Refs Hook (POC).

PreToolUse hook for Edit|Write. Queries the content about to be written
against a repo-intelligence backend and surfaces similar existing code, so
the agent doesn't duplicate what's already there. Uses rag-rat for languages
it indexes here (see rag-rat.toml target_bindings), falling back to
codebase-memory-mcp otherwise (see utils.pick_repo_intel_backend). The
caller (claude/settings.json) gates execution on either binary being
installed.
"""

import contextlib
import json
import os
from pathlib import Path
import re
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    call_cbm_tool,
    call_rag_rat_tool,
    get_by_key,
    get_hooks_logger,
    pick_repo_intel_backend,
    project_dir,
    resolve_cbm_project,
)

logger = get_hooks_logger("SemanticSimilarRefs")

MAX_STDIN = 1024 * 1024
MAX_EMBED_CHARS = 4000
MAX_RESULTS = 3
SEMANTIC_SEARCH_TIMEOUT = 10

# why: rag-rat target_bindings languages + JS family, plus cbm hybrid-LSP
# languages that fall back to codebase-memory-mcp (pick_repo_intel_backend)
SOURCE_EXTS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".kt",
    ".java",
    ".php",
    ".cs",
    ".c",
    ".cpp",
    ".rs",
    ".pl",
}

# Each hit is a "  - chunk_id: ...\n    path: ...\n" block (with summary).
PATH_RE = re.compile(r'^\s*path:\s*"?([^"\n]+)"?', re.MULTILINE)
SUMMARY_RE = re.compile(r'^\s*summary:\s*"(.*?)"\s*$', re.MULTILINE)


def _rag_rat_search_blocks(query: str, target_file: str, cwd: str) -> list[str]:
    """Parse rag-rat's TOON `semantic_search` output into display blocks."""
    text = call_rag_rat_tool(
        "semantic_search",
        {"query": query, "limit": MAX_RESULTS},
        cwd,
        logger,
        timeout=SEMANTIC_SEARCH_TIMEOUT,
    )
    if not text:
        return []

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


def _cbm_search_blocks(query: str, target_file: str, cwd: str) -> list[str]:
    """Query codebase-memory-mcp's `search_graph` and parse structuredContent."""
    project = resolve_cbm_project(cwd, logger)
    if not project:
        logger.debug("no codebase-memory-mcp project indexed for %s", cwd)
        return []

    text = call_cbm_tool(
        "search_graph",
        {
            "project": project,
            "query": query,
            "limit": MAX_RESULTS,
            "format": "json",
        },
        cwd,
        logger,
        timeout=SEMANTIC_SEARCH_TIMEOUT,
    )
    if not text:
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    cols = data.get("cols") or []
    try:
        file_idx = cols.index("file")
        qn_idx = cols.index("qn")
    except ValueError:
        return []

    blocks = []
    for row in data.get("rows") or []:
        path = row[file_idx]
        qn = row[qn_idx]
        if Path(path).resolve() == Path(target_file).resolve():
            continue
        blocks.append(f"=== semantically similar code in {path} ===\n{qn}")
        if len(blocks) >= MAX_RESULTS:
            break
    return blocks


def semantic_search_blocks(
    content: str, target_file: str, cwd: str, backend: str
) -> list[str] | None:
    """Query the chosen repo-intel backend with the new code as the query text.

    Args:
        content: The source code to query.
        target_file: The file being edited (excluded from results).
        cwd: Current working directory for the MCP subprocess.
        backend: "rag-rat" or "cbm", from pick_repo_intel_backend.

    Returns:
        Formatted blocks of similar code, or None if the backend errors.
    """
    query = content[:MAX_EMBED_CHARS]
    if backend == "rag-rat":
        return _rag_rat_search_blocks(query, target_file, cwd)
    return _cbm_search_blocks(query, target_file, cwd)


def build_context(content: str, target_file: str, cwd: str) -> str:
    """Build semantic context from similar code in the repository.

    Args:
        content: The source code to find similar code for.
        target_file: The file being edited (excluded from results).
        cwd: Current working directory for the MCP subprocess.

    Returns:
        Formatted string of similar code blocks, or empty string if none found.
    """
    backend = pick_repo_intel_backend(target_file, cwd)
    if not backend:
        logger.debug("no repo-intel backend available (rag-rat or cbm)")
        return ""

    blocks = semantic_search_blocks(content, target_file, cwd, backend)
    if not blocks:
        logger.debug("no semantic search blocks found via %s", backend)
        return ""

    logger.debug("build_context: %d blocks from %s", len(blocks), backend)
    return "\n\n".join(blocks)


def main() -> None:
    """Main entry point for PreToolUse hook."""
    stdin_data = ""
    with contextlib.suppress(OSError):
        stdin_data = sys.stdin.read(MAX_STDIN)

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

    cwd = project_dir(data)
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
        logger.debug("[additionalContext]: %s", output)
        print(output)  # noqa: T201
    else:
        logger.debug("no context found, emitting nothing")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as exc:
        logger.debug("Error: %s", exc, exc_info=True)
        sys.exit(0)
