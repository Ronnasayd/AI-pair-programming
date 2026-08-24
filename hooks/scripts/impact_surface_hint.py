#!/usr/bin/python3
"""PostToolUse hook: after Edit/Write/MultiEdit, ask rag-rat's impact_surface
(via raw MCP JSON-RPC over stdio) which symbols call into / are called by the
top-level functions and classes just touched, so the agent sees the blast
radius without a separate tool round-trip.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("ImpactSurfaceHint")

MAX_SYMBOLS = 5
MCP_TIMEOUT_SECONDS = 15
SOURCE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".rs",
    ".go",
    ".kt",
    ".swift",
    ".c",
    ".cpp",
    ".h",
}

DEF_RE = re.compile(
    r"^\s*(?:pub\s+|export\s+)?(?:async\s+)?(?:def|class|fn|func)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)


def is_rag_rat_available(cwd: str) -> bool:
    return shutil.which("rag-rat") is not None and (Path(cwd) / "rag-rat.toml").exists()


def _enclosing_symbol(file_text: str, old_string: str) -> str | None:
    """Nearest DEF_RE match at or before old_string's position in file_text."""
    offset = file_text.find(old_string)
    if offset == -1:
        return None
    last = None
    for m in DEF_RE.finditer(file_text, 0, offset + len(old_string)):
        if m.start() <= offset + len(old_string):
            last = m
    return last.group(1) if last else None


def changed_symbols_from_payload(tool_name: str, tool_input: dict, file_path: str) -> list[str]:
    """Symbol names touched by this edit, read straight from the hook payload.

    Prefers a def line inside new_string (covers renames/new functions); falls
    back to the nearest enclosing def found in the current file content around
    old_string (covers comment-only / body-only edits).
    """
    edits = tool_input.get("edits") if tool_name == "MultiEdit" else [tool_input]
    if not edits:
        return []

    try:
        file_text = Path(file_path).read_text()
    except OSError:
        file_text = ""

    names: list[str] = []

    def add(name: str | None) -> None:
        if name and name not in names and not name.startswith("_"):
            names.append(name)

    for edit in edits:
        new_string = edit.get("new_string") or ""
        m = DEF_RE.search(new_string)
        if m:
            add(m.group(1))
            continue
        old_string = edit.get("old_string") or ""
        if file_text and old_string:
            add(_enclosing_symbol(file_text, old_string))

    return names[:MAX_SYMBOLS]


def qualified_ref(file_path: str, symbol: str, cwd: str) -> str:
    try:
        rel = str(Path(file_path).resolve().relative_to(Path(cwd).resolve()))
    except ValueError:
        rel = file_path
    return f"{rel}::{symbol}"


def call_impact_surface(symbol: str, cwd: str) -> str | None:
    try:
        proc = subprocess.Popen(
            ["rag-rat", "mcp"],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except OSError as e:
        LOG.warning(f"Failed to spawn rag-rat mcp: {e}")
        return None

    try:
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "impact-surface-hook", "version": "0.0.1"},
                },
            },
        )
        _recv(proc, MCP_TIMEOUT_SECONDS)

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "impact_surface", "arguments": {"symbol": symbol}},
            },
        )
        resp = _recv(proc, MCP_TIMEOUT_SECONDS)
    except (TimeoutError, EOFError, json.JSONDecodeError) as e:
        LOG.warning(f"impact_surface MCP call failed for {symbol!r}: {e}")
        return None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    if "error" in resp:
        LOG.debug(f"impact_surface error for {symbol!r}: {resp['error']}")
        return None
    content = resp.get("result", {}).get("content", [])
    return content[0]["text"] if content else None


def _send(proc: subprocess.Popen, msg: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()


def _recv(proc: subprocess.Popen, timeout: int) -> dict:
    import select

    assert proc.stdout is not None
    ready, _, _ = select.select([proc.stdout], [], [], timeout)
    if not ready:
        raise TimeoutError("no response from rag-rat mcp")
    line = proc.stdout.readline()
    if not line:
        stderr = proc.stderr.read()[:500] if proc.stderr else ""
        raise EOFError("rag-rat mcp closed: " + stderr)
    return json.loads(line)


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
    """Compact 'edge_id: ... from_symbol: ... callsite: path/line' blocks to 'symbol (path:line)'."""
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


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse stdin JSON: {e}")
        sys.exit(0)

    try:
        cwd = get_by_key(payload, "cwd") or "."
        if not is_rag_rat_available(cwd):
            LOG.debug(f"rag-rat not installed/configured in {cwd} — skipping")
            sys.exit(0)

        tool_name = get_by_key(payload, "tool_name")
        if tool_name not in ("Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = get_by_key(payload, "tool_input")
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        if not file_path or Path(file_path).suffix not in SOURCE_SUFFIXES:
            sys.exit(0)

        symbols = changed_symbols_from_payload(tool_name, tool_input, file_path)
        if not symbols:
            LOG.debug(f"No public top-level symbols found in {file_path}")
            sys.exit(0)

        LOG.debug(f"Checking impact surface for {symbols} in {file_path}")

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
                "additionalContext": json.dumps(
                    {
                        "instruction": (
                            "the file you just modified has these dependents/dependencies "
                            "per symbol (from rag-rat impact_surface) — consider whether "
                            "your change breaks any callers listed"
                        ),
                        "file": file_path,
                        "results": results,
                    },
                    ensure_ascii=False,
                ),
            }
        }
        LOG.debug(
            f"[additionalContext]: {json.dumps(output, ensure_ascii=False)[:500]}"
        )
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        LOG.warning(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
