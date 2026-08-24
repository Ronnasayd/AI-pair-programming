#!/usr/bin/python3
"""
Similar-Code-Ref Hook (POC)

PreToolUse hook for Edit|Write. Extracts imports/symbols from the content
being written and looks for similar existing code: rag-rat's semantic_search
when the project has a rag-rat index, falling back to plain ripgrep term
search otherwise.
"""

import json
import os
import re
import subprocess
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

logger = get_hooks_logger("SimilarCodeRef")

MAX_STDIN = 1024 * 1024
MAX_TERMS = 3
MAX_FILES_PER_TERM = 5
CONTEXT_LINES = 2
MAX_SNIPPET_CHARS = 800
MAX_EMBED_CHARS = 4000
MAX_RESULTS = 3
SEMANTIC_SEARCH_TIMEOUT = 10

# Trivial terms that would create noise (too common to be a useful signal)
DENYLIST = {
    "os",
    "sys",
    "json",
    "re",
    "path",
    "fs",
    "io",
    "time",
    "typing",
    "react",
    "utils",
    "types",
    "index",
    "config",
    "logging",
    "subprocess",
}

EXT_TO_RG_TYPE = {
    ".py": "py",
    ".ts": "ts",
    ".tsx": "ts",
    ".js": "js",
    ".jsx": "js",
    ".go": "go",
}


def extract_terms(content: str, file_path: str) -> list[str]:
    """Pull candidate library/symbol names out of new code, filtering noise."""
    info = extract_code_info(content, file_path)
    raw_terms = info["imports"] + info["defs"]

    terms: list[str] = []
    seen: set[str] = set()
    for raw in raw_terms:
        term = raw.split(".")[-1].split("/")[-1]
        term_norm = term.lower()
        if not term or term_norm in DENYLIST or len(term) < 3:
            continue
        if term_norm in seen:
            continue
        seen.add(term_norm)
        terms.append(term)
        if len(terms) >= MAX_TERMS:
            break

    return terms


def rg_search(term: str, rg_type: str | None, exclude_file: str) -> list[str]:
    """Return up to MAX_FILES_PER_TERM file paths containing `term`."""
    # NOTE: "." must be passed explicitly. Without a path arg, ripgrep falls
    # back to reading stdin when stdin isn't a tty (always true in a hook,
    # since Claude Code feeds the event JSON via stdin) and blocks forever
    # waiting for EOF. stdin=DEVNULL is a second layer of defense.
    cmd = ["rg", "-l", "--fixed-strings", term]
    if rg_type:
        cmd += ["--type", rg_type]
    cmd += ["--glob", f"!{exclude_file}", "."]

    logger.debug("rg_search cmd=%s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.debug("rg -l failed for term=%s: %s", term, exc)
        return []

    if result.returncode not in (0, 1):
        logger.debug("rg -l nonzero for term=%s: %s", term, result.stderr)
        return []

    files = [f for f in result.stdout.splitlines() if f][:MAX_FILES_PER_TERM]
    logger.debug("rg_search term=%s found=%d files=%s", term, len(files), files)
    return files


def rg_snippet(term: str, file_path: str) -> str:
    """Return a truncated -C context snippet for `term` in `file_path`."""
    cmd = ["rg", "-n", "--fixed-strings", "-C", str(CONTEXT_LINES), term, file_path]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.debug("rg -C failed for %s in %s: %s", term, file_path, exc)
        return ""

    out = result.stdout.strip()
    truncated = len(out) > MAX_SNIPPET_CHARS
    if truncated:
        out = out[:MAX_SNIPPET_CHARS] + "\n... (truncated)"
    logger.debug(
        "rg_snippet term=%s file=%s len=%d truncated=%s",
        term,
        file_path,
        len(out),
        truncated,
    )
    return out


# Each hit is a "  - chunk_id: ...\n    path: ...\n    ...\n    summary: \"...\"\n" block.
PATH_RE = re.compile(r'^\s*path:\s*"?([^"\n]+)"?', re.MULTILINE)
SUMMARY_RE = re.compile(r'^\s*summary:\s*"(.*?)"\s*$', re.MULTILINE)


def semantic_search_blocks(
    content: str, target_file: str, cwd: str
) -> list[str] | None:
    """Query rag-rat's semantic_search with the new code as the query text.
    Returns formatted blocks, or None if rag-rat is unavailable/errors (caller
    should fall back to plain rg)."""
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
    if is_rag_rat_available(cwd):
        blocks = semantic_search_blocks(content, target_file, cwd)
        if blocks:
            logger.debug(
                "build_context: %d blocks from rag-rat semantic_search", len(blocks)
            )
            return "\n\n".join(blocks)
        if blocks is not None:
            # rag-rat answered but found nothing relevant — no need for rg fallback
            return ""
        logger.debug("rag-rat semantic_search failed, falling back to rg")

    ext = Path(target_file).suffix.lower()
    rg_type = EXT_TO_RG_TYPE.get(ext)

    terms = extract_terms(content, target_file)
    logger.debug("target=%s ext=%s terms=%s", target_file, ext, terms)
    if not terms:
        logger.debug("no terms extracted, skipping build_context")
        return ""

    blocks = []
    for term in terms:
        files = rg_search(term, rg_type, target_file)
        for f in files:
            snippet = rg_snippet(term, f)
            if not snippet:
                logger.debug("empty snippet for term=%s file=%s, skipping", term, f)
                continue
            blocks.append(f"=== existing usage of '{term}' in {f} ===\n{snippet}")
            if len(blocks) >= MAX_RESULTS:
                break

    logger.debug("build_context (rg fallback) returning %d blocks", len(blocks))
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

    if Path(file_path).suffix.lower() not in EXT_TO_RG_TYPE:
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
