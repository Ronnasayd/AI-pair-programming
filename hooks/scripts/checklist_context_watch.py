#!/usr/bin/python3
"""PostToolUse hook: track the active skill's CHECKLIST.md and re-surface it
every time total context usage crosses a new 10% bucket.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    read_file,
    write_file,
)

LOG = get_hooks_logger("ChecklistContextWatch")

STATUSLINE_PATH = Path.home() / ".claude" / "logs" / "claude_statusline.json"
SKILLS_ROOT = Path(os.environ.get("AI_PROJECT_DIR", ".")) / "skills"


def state_path(session_id: str) -> Path:
    return Path(f"/tmp/checklist-watch-{get_session_id_short(session_id)}.json")


def load_state(path: Path) -> dict:
    content = read_file(path)
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def save_state(path: Path, state: dict) -> None:
    write_file(path, json.dumps(state))


def find_checklist(skill_name: str | None) -> str | None:
    if not skill_name:
        return None
    candidate = SKILLS_ROOT / skill_name / "CHECKLIST.md"
    if candidate.exists():
        return str(candidate)
    return None


def read_context_pct() -> float | None:
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


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    session_id = get_by_key(payload, "session_id") or ""
    tool_name = get_by_key(payload, "tool_name") or ""
    path = state_path(session_id)
    state = load_state(path)

    if tool_name == "Skill":
        tool_input = get_by_key(payload, "tool_input") or {}
        skill_name = get_by_key(tool_input, "skill")
        checklist = find_checklist(skill_name)
        if checklist:
            state["checklist_path"] = checklist
            state.setdefault("last_bucket", -1)
            save_state(path, state)
            LOG.debug(f"Tracking checklist for skill '{skill_name}': {checklist}")
        sys.exit(0)

    checklist_path = state.get("checklist_path")
    if not checklist_path:
        sys.exit(0)

    pct = read_context_pct()
    if pct is None:
        sys.exit(0)

    bucket = int(pct) // 10
    last_bucket = state.get("last_bucket", -1)
    if bucket <= last_bucket:
        sys.exit(0)

    checklist_content = read_file(Path(checklist_path))
    if not checklist_content:
        state["last_bucket"] = bucket
        save_state(path, state)
        sys.exit(0)

    state["last_bucket"] = bucket
    save_state(path, state)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": json.dumps(
                {
                    "reason": f"context usage crossed {bucket * 10}%",
                    "checklist_path": checklist_path,
                    "checklist": checklist_content,
                },
                ensure_ascii=False,
            ),
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
