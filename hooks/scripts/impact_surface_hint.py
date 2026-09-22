#!/usr/bin/python3
"""PostToolUse hook: after Edit/Write/MultiEdit, ask rag-rat's impact_surface.

Queries rag-rat's MCP `impact_surface` tool (via `utils.call_rag_rat_tool`) for
which symbols call into / are called by the top-level functions and classes
just touched, so the agent sees the blast radius without a separate tool
round-trip.
"""

# pylint: disable=missing-param-doc,missing-return-doc
# justified: private hook helpers, docstrings cover intent, not full param/return spec

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    call_rag_rat_tool,
    enclosing_def_name,
    extract_code_info,
    get_by_key,
    get_hooks_logger,
    is_rag_rat_available,
    minify_json,
    project_dir,
)

LOG = get_hooks_logger("ImpactSurfaceHint")

MAX_SYMBOLS = 5
MCP_TIMEOUT_SECONDS = 15
SOURCE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
}


def changed_symbols_from_payload(
    tool_name: str, tool_input: dict, file_path: str
) -> list[str]:
    """Symbol names touched by this edit, read straight from the hook payload.

    Prefers a def/class found inside new_string (covers renames/new
    functions); falls back to the nearest enclosing def in the current
    (post-edit) file content around new_string (covers comment-only / body-
    only edits). The hook runs after the edit lands, so file_text no longer
    contains old_string — only new_string is searchable.
    """
    edits = tool_input.get("edits") if tool_name == "MultiEdit" else [tool_input]
    if not edits:
        return []

    try:
        file_text = Path(file_path).read_text(encoding="utf-8")
    except OSError:
        file_text = ""

    names: list[str] = []

    def add(name: str | None) -> None:
        if name and name not in names and not name.startswith("_"):
            names.append(name)

    for edit in edits:
        new_string = edit.get("new_string") or ""
        for name in extract_code_info(new_string, file_path)["defs"]:
            add(name)
        if names:
            continue
        anchor = new_string or edit.get("old_string") or ""
        if file_text and anchor:
            offset = file_text.find(anchor)
            if offset != -1:
                add(enclosing_def_name(file_text, file_path, offset + len(anchor)))

    return names[:MAX_SYMBOLS]


def qualified_ref(file_path: str, symbol: str, cwd: str) -> str:
    """Build rag-rat's `path::symbol` ref, path relative to `cwd` when possible."""
    try:
        rel = str(Path(file_path).resolve().relative_to(Path(cwd).resolve()))
    except ValueError:
        rel = file_path
    return f"{rel}::{symbol}"


def call_impact_surface(symbol: str, cwd: str) -> str | None:
    """Call rag-rat's `impact_surface` MCP tool for one symbol."""
    return call_rag_rat_tool(
        "impact_surface", {"symbol": symbol}, cwd, LOG, timeout=MCP_TIMEOUT_SECONDS
    )


FROM_SYMBOL_RE = re.compile(r'from_symbol:\s*"([^"]+)"')
TO_SYMBOL_RE = re.compile(r'to_symbol:\s*"([^"]+)"')
PATH_RE = re.compile(r'^\s*(?:-\s*)?path:\s*"?([^"\n]+)"?', re.MULTILINE)
LINE_RE = re.compile(r"^\s*line:\s*(\d+)", re.MULTILINE)
SECTION_RE_CACHE: dict[str, re.Pattern] = {}


def _section(toon_text: str, header: str) -> str:
    pattern = SECTION_RE_CACHE.setdefault(
        header,
        re.compile(rf"^{re.escape(header)}\[\d+\]:\n((?:  .*\n?)*)", re.MULTILINE),
    )
    m = pattern.search(toon_text)
    return m.group(1) if m else ""


def _refs_from_edges(section_text: str, want_key: str) -> list[str]:
    """Compact 'edge_id: ...' blocks to 'symbol (path:line)' strings."""
    refs = []
    for block in re.split(r"^  - edge_id:", section_text, flags=re.MULTILINE)[1:]:
        m = (FROM_SYMBOL_RE if want_key == "from_symbol" else TO_SYMBOL_RE).search(
            block
        )
        path_m = PATH_RE.search(block)
        line_m = LINE_RE.search(block)
        if m:
            loc = f" ({path_m.group(1)}:{line_m.group(1)})" if path_m and line_m else ""
            refs.append(f"{m.group(1)}{loc}")
    return refs


def _refs_from_paths(section_text: str) -> list[str]:
    return [m.group(1) for m in PATH_RE.finditer(section_text)]


def summarize(symbol: str, toon_text: str) -> dict | None:
    """Extract callers/callees/dependents from rag-rat's toon impact_surface output."""
    callers = _refs_from_edges(
        _section(toon_text, "direct_semantic_callers"), "from_symbol"
    )
    callees = _refs_from_edges(
        _section(toon_text, "direct_semantic_callees"), "to_symbol"
    )
    dependents = _refs_from_paths(_section(toon_text, "import_export_dependents"))
    if not (callers or callees or dependents):
        return None
    return {
        "symbol": symbol,
        "called_by": callers or None,
        "calls": callees or None,
        "imported_by": dependents or None,
    }


def main() -> None:
    """Entry point: read the PostToolUse payload and emit impact_surface hints."""
    # why: spawns own rag-rat mcp subprocess per call — stdio JSON-RPC needs a fresh
    # handshake even if a server instance is already running elsewhere
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse stdin JSON: %s", e)
        sys.exit(0)

    try:
        cwd = project_dir(payload)
        if not is_rag_rat_available(cwd):
            LOG.debug("rag-rat not installed/configured in %s — skipping", cwd)
            sys.exit(0)

        tool_name = get_by_key(payload, "tool_name")
        if tool_name not in ("Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = get_by_key(payload, "tool_input") or {}
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        if not file_path or Path(file_path).suffix not in SOURCE_SUFFIXES:
            sys.exit(0)

        symbols = changed_symbols_from_payload(tool_name, tool_input, file_path)
        if not symbols:
            LOG.debug("No public top-level symbols found in %s", file_path)
            sys.exit(0)

        LOG.debug("Checking impact surface for %s in %s", symbols, file_path)

        results = []
        for symbol in symbols:
            ref = qualified_ref(file_path, symbol, cwd)
            text = call_impact_surface(ref, cwd)
            if not text:
                continue
            summary = summarize(symbol, text)
            if summary:
                results.append(summary)

        if not results:
            sys.exit(0)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": minify_json(
                    {
                        "instruction": (
                            "the file you just modified has these "
                            "dependents/dependencies per symbol (from rag-rat "
                            "impact_surface) — consider whether your change "
                            "breaks any callers listed"
                        ),
                        "file": file_path,
                        "results": results,
                    }
                ),
            }
        }
        LOG.debug(
            "[additionalContext]: %s", json.dumps(output, ensure_ascii=False)[:500]
        )
        print(json.dumps(output, ensure_ascii=False))  # noqa: T201 - hook stdout protocol

    except Exception as e:  # pylint: disable=broad-exception-caught
        LOG.warning("Unexpected error: %s: %s", type(e).__name__, e, exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
