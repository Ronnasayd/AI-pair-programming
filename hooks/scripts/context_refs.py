#!/usr/bin/python3
"""
Context-Refs Hook

PreToolUse hook for Edit|Write. Points Claude to reference file locations that
apply to the file about to be edited, without injecting their full contents.
"""

import json
import os
import sys
from pathlib import Path, PurePosixPath

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger  # noqa: E402

logger = get_hooks_logger("ContextRefs")

MAX_STDIN = 1024 * 1024
CONFIG_FILE = ".claude/context-refs.json"


def _glob_match(file_path: str, glob: str) -> bool:
    """Match file_path against glob pattern using fnmatch."""
    import fnmatch

    p = PurePosixPath(file_path.replace("\\", "/"))
    for g in glob.split(","):
        g = g.strip().replace("\\", "/")
        if fnmatch.fnmatch(str(p), g):
            return True
    return False


def _extract_description(ref_path: Path) -> str:
    """Read the `description` field from a ref file's YAML frontmatter."""
    try:
        text = ref_path.read_text()
    except OSError:
        return ""

    if not text.startswith("---"):
        return ""

    end = text.find("\n---", 3)
    if end == -1:
        return ""

    frontmatter = text[3:end]
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    data: dict = {}
    try:
        data = json.loads(stdin_data)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
    except (json.JSONDecodeError, AttributeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        sys.exit(0)

    logger.debug("tool_name=%s", tool_name)

    if tool_name not in ("Edit", "Write"):
        logger.debug("Tool %s not in scope, skipping.", tool_name)
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        logger.debug("No file_path in tool_input, skipping.")
        sys.exit(0)

    logger.debug("file_path=%s", file_path)

    # Normalize to relative path for glob matching
    try:
        rel_path = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        rel_path = file_path
    rel_path = rel_path.replace("\\", "/")
    logger.debug("rel_path=%s", rel_path)

    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        logger.debug("Config %s not found, exiting silently.", CONFIG_FILE)
        sys.exit(0)

    try:
        config = json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        logger.debug("Failed to parse config %s, exiting.", CONFIG_FILE)
        sys.exit(0)

    rules = config.get("rules", [])
    logger.debug("rules_count=%d", len(rules))

    # Build ordered deduplicated union of matching refs
    seen: set[str] = set()
    matched_refs: list[str] = []
    for rule in rules:
        glob = rule.get("glob", "")
        if not glob:
            continue
        matched = _glob_match(rel_path, glob)
        logger.debug("glob=%s matched=%s", glob, matched)
        if not matched:
            continue
        for ref in rule.get("refs", []):
            if ref not in seen:
                seen.add(ref)
                matched_refs.append(ref)

    logger.debug("matched_refs=%s", matched_refs)

    if not matched_refs:
        logger.debug("No refs matched for %s, exiting.", rel_path)
        sys.exit(0)

    refs_list_path = Path("/tmp/context-instructions")
    lines = []
    for ref in matched_refs:
        description = _extract_description(Path(ref))
        lines.append(f"{ref}: {description}" if description else ref)
    try:
        refs_list_path.write_text("\n".join(lines) + "\n")
    except OSError:
        logger.debug("Could not write refs list to %s", refs_list_path)

    output = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    f"Reference instructions may apply to {rel_path}. "
                    f"Check {refs_list_path} for a list of candidate reference "
                    "files with their descriptions, then open only the ones "
                    "relevant to this edit before proceeding."
                ),
            }
        }
    )
    logger.debug("Output: %s", output)
    sys.stdout.write(output)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
