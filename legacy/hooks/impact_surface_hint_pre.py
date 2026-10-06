#!/usr/bin/python3
"""PreToolUse hook (draft): before Edit/MultiEdit, surface the impact surface.

Same data as `impact_surface_hint.py` (PostToolUse) but delivered BEFORE the
edit lands, when the agent can still decide what to change. Symbols come from
`old_string` against the current file, since `new_string` does not exist on
disk yet. `Write` is skipped: a new file has no callers and a full rewrite has
no anchor to locate the touched symbols.

Reuses the backend/summary helpers from `impact_surface_hint.py` so the two
do not drift; fold them together once the PostToolUse variant is retired.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from impact_surface_hint import (
    LOG,
    MAX_SYMBOLS,
    SOURCE_SUFFIXES,
    impact_summary_for_symbol,
)
from utils import (
    enclosing_def_name,
    extract_code_info,
    get_by_key,
    minify_json,
    pick_repo_intel_backend,
    project_dir,
)


def symbols_from_old_string(
    tool_name: str, tool_input: dict, file_path: str
) -> list[str]:
    """Public def/class names the edit is about to touch, read from the current file.

    Args:
        tool_name: "Edit" or "MultiEdit"; decides where the edits live in the input.
        tool_input: the hook payload's tool_input.
        file_path: file about to be edited; read to locate each old_string.

    Returns:
        Up to MAX_SYMBOLS public top-level names, in edit order.
    """
    edits = tool_input.get("edits") if tool_name == "MultiEdit" else [tool_input]
    try:
        file_text = Path(file_path).read_text(encoding="utf-8")
    except OSError:
        return []

    names: list[str] = []
    for edit in edits or []:
        old = edit.get("old_string") or ""
        if not old:
            continue
        found = extract_code_info(old, file_path)["defs"]
        if not found:
            offset = file_text.find(old)
            if offset == -1:
                continue
            # why: leading whitespace can belong to the parent node (class), skip it
            offset += len(old) - len(old.lstrip())
            name = enclosing_def_name(file_text, file_path, offset)
            found = [name] if name else []
        for name in found:
            if name not in names and not name.startswith("_"):
                names.append(name)
    return names[:MAX_SYMBOLS]


def main() -> None:
    """Entry point: read the PreToolUse payload and emit impact_surface hints."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse stdin JSON: %s", e)
        sys.exit(0)

    try:
        tool_name = get_by_key(payload, "tool_name")
        if tool_name not in ("Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = get_by_key(payload, "tool_input") or {}
        file_path = get_by_key(tool_input, "file_path")
        if not file_path or Path(file_path).suffix not in SOURCE_SUFFIXES:
            sys.exit(0)

        cwd = project_dir(payload)
        backend = pick_repo_intel_backend(file_path, cwd)
        if not backend:
            sys.exit(0)

        symbols = symbols_from_old_string(tool_name, tool_input, file_path)
        results = [
            s
            for symbol in symbols
            if (s := impact_summary_for_symbol(symbol, file_path, cwd, backend))
        ]
        if not results:
            sys.exit(0)

        print(  # noqa: T201 - hook stdout protocol
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "additionalContext": minify_json(
                            {
                                "instruction": (
                                    "you are about to modify these symbols; "
                                    "dependents/dependencies per symbol "
                                    f"(from {backend}) — check the change does "
                                    "not break the listed callers"
                                ),
                                "file": file_path,
                                "results": results,
                            }
                        ),
                    }
                },
                ensure_ascii=False,
            )
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        LOG.warning("Unexpected error: %s: %s", type(e).__name__, e, exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
