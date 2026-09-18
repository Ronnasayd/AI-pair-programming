#!/usr/bin/python3
"""PostToolUse hook.

Track the active skill's CHECKLIST.md and re-surface it every time total
context usage crosses a new % bucket.
"""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    detect_skill,
    extract_query_text,
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    minify_json,
    minify_markdown,
    read_file,
    write_file,
)

PERCENTAGE_BUCKET_SIZE = 5

LOG = get_hooks_logger("ChecklistContextWatch")

STATUSLINE_PATH = Path.home() / ".claude" / "logs" / "claude_statusline.json"
_CLAUDE_PROJECT_DIR_RAW = os.environ.get("CLAUDE_PROJECT_DIR")
SKILLS_ROOT = (
    Path(_CLAUDE_PROJECT_DIR_RAW) / ".claude" / "skills"
    if _CLAUDE_PROJECT_DIR_RAW
    else Path(".claude") / "skills"
)


def state_path(session_id: str) -> Path:
    """Build the per-session state file path.

    Args:
        session_id: Full Claude Code session identifier.

    Returns:
        Path to this session's checklist-watch state file.
    """
    return Path(f"/tmp/checklist-watch-{get_session_id_short(session_id)}.json")  # noqa: S108


def load_state(path: Path) -> dict:
    """Load JSON state from a file.

    Args:
        path: State file to read.

    Returns:
        Parsed state dict, or {} if the file is missing or invalid.
    """
    content = read_file(path)
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def save_state(path: Path, state: dict) -> None:
    """Persist state as JSON to a file.

    Args:
        path: State file to write.
        state: State dict to serialize.
    """
    write_file(path, json.dumps(state))


def find_checklist(skill_name: str | None) -> str | None:
    """Locate the CHECKLIST.md for a skill.

    Args:
        skill_name: Name of the skill to look up, or None.

    Returns:
        String path to the skill's CHECKLIST.md, or None if not found.
    """
    LOG.debug(
        "find_checklist: skill_name=%r CLAUDE_PROJECT_DIR=%r SKILLS_ROOT=%s "
        "SKILLS_ROOT.exists()=%s cwd=%s",
        skill_name,
        _CLAUDE_PROJECT_DIR_RAW,
        SKILLS_ROOT,
        SKILLS_ROOT.exists(),
        Path.cwd(),
    )
    if not skill_name:
        LOG.debug("find_checklist: no skill_name given, returning None")
        return None
    candidate = SKILLS_ROOT / skill_name / "CHECKLIST.md"
    LOG.debug("find_checklist: candidate=%s exists=%s", candidate, candidate.exists())
    if candidate.exists():
        return str(candidate)
    return None


def read_context_pct() -> float | None:
    """Read the current context usage percentage from the statusline file.

    Returns:
        The used_percentage value, or None if unavailable.
    """
    content = read_file(STATUSLINE_PATH)
    if not content:
        return None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    pct = get_by_key(data, "context_window")
    if not isinstance(pct, dict):
        return None
    return pct.get("used_percentage")


def _track_checklist(path: Path, state: dict, skill_name: str | None) -> None:
    """Record skill_name's checklist in state, if one exists.

    Args:
        path: State file to persist to.
        state: Mutable state dict to update in place.
        skill_name: Name of the skill whose checklist should be tracked.
    """
    checklist = find_checklist(skill_name)
    LOG.debug("Tracking check: skill_name=%r checklist=%r", skill_name, checklist)
    if checklist:
        state["checklist_path"] = checklist
        state.setdefault("last_bucket", -1)
        save_state(path, state)
        LOG.debug("Tracking checklist for skill '%s': %s", skill_name, checklist)


def _emit_checklist(path: Path, state: dict, checklist_path: str, bucket: int) -> None:
    """Emit the checklist as additionalContext and persist the new bucket.

    Args:
        path: State file to persist to.
        state: Mutable state dict to update in place.
        checklist_path: Path to the CHECKLIST.md to re-surface.
        bucket: New context-usage bucket that triggered this emission.
    """
    checklist_content = read_file(Path(checklist_path))
    state["last_bucket"] = bucket
    save_state(path, state)
    if not checklist_content:
        LOG.debug("checklist_path=%s unreadable/empty", checklist_path)
        return

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": minify_json(
                {
                    "reason": (
                        f"context usage crossed {bucket * PERCENTAGE_BUCKET_SIZE}%"
                    ),
                    "checklist_path": checklist_path,
                    "checklist": minify_markdown(checklist_content),
                }
            ),
        }
    }
    LOG.debug("[additionalContext]: %s", output)
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201


def main() -> None:
    """Read the hook payload and re-surface the tracked checklist on context jumps."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    session_id = get_by_key(payload, "session_id") or ""
    tool_name = get_by_key(payload, "tool_name") or ""
    path = state_path(session_id)
    state = load_state(path)
    LOG.debug(
        "tool_name=%r session=%r state_path=%s state=%s",
        tool_name,
        session_id,
        path,
        state,
    )

    if tool_name == "Skill":
        tool_input = get_by_key(payload, "tool_input") or {}
        _track_checklist(path, state, get_by_key(tool_input, "skill"))
        sys.exit(0)

    if not tool_name:
        prompt = extract_query_text(payload) or ""
        _track_checklist(path, state, detect_skill(prompt))
        sys.exit(0)

    checklist_path = state.get("checklist_path")
    if not checklist_path:
        LOG.debug("No checklist tracked for this session, skipping.")
        sys.exit(0)

    pct = read_context_pct()
    LOG.debug("read_context_pct -> %r (statusline=%s)", pct, STATUSLINE_PATH)
    if pct is None:
        sys.exit(0)

    bucket = int(pct) // PERCENTAGE_BUCKET_SIZE
    last_bucket = state.get("last_bucket", -1)
    LOG.debug("bucket=%s last_bucket=%s", bucket, last_bucket)
    if bucket <= last_bucket:
        sys.exit(0)

    _emit_checklist(path, state, checklist_path, bucket)
    sys.exit(0)


if __name__ == "__main__":
    main()
