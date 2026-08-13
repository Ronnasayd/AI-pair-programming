#!/usr/bin/python3
"""PostToolUse hook: track the active skill's CHECKLIST.md and re-surface it
every time total context usage crosses a new % bucket.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    detect_skill,
    extract_query_text,
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    read_file,
    write_file,
)

PERCENTAGE_BUCKET_SIZE = 5

LOG = get_hooks_logger("ChecklistContextWatch")

STATUSLINE_PATH = Path.home() / ".claude" / "logs" / "claude_statusline.json"
_AI_PROJECT_DIR_RAW = os.environ.get("AI_PROJECT_DIR")
SKILLS_ROOT = (
    Path(_AI_PROJECT_DIR_RAW) / ".claude" / "skills"
    if _AI_PROJECT_DIR_RAW
    else Path(".claude") / "skills"
)


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
    LOG.debug(
        f"find_checklist: skill_name={skill_name!r} "
        f"AI_PROJECT_DIR={_AI_PROJECT_DIR_RAW!r} SKILLS_ROOT={SKILLS_ROOT} "
        f"SKILLS_ROOT.exists()={SKILLS_ROOT.exists()} cwd={Path.cwd()}"
    )
    if not skill_name:
        LOG.debug("find_checklist: no skill_name given, returning None")
        return None
    candidate = SKILLS_ROOT / skill_name / "CHECKLIST.md"
    LOG.debug(f"find_checklist: candidate={candidate} exists={candidate.exists()}")
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
    LOG.debug(
        f"tool_name={tool_name!r} session={session_id!r} state_path={path} state={state}"
    )

    if tool_name == "Skill":
        tool_input = get_by_key(payload, "tool_input") or {}
        skill_name = get_by_key(tool_input, "skill")
        checklist = find_checklist(skill_name)
        LOG.debug(f"Skill invoked: skill_name={skill_name!r} checklist={checklist!r}")
        if checklist:
            state["checklist_path"] = checklist
            state.setdefault("last_bucket", -1)
            save_state(path, state)
            LOG.debug(f"Tracking checklist for skill '{skill_name}': {checklist}")
        sys.exit(0)

    if not tool_name:
        prompt = extract_query_text(payload) or ""
        skill_name = detect_skill(prompt)
        checklist = find_checklist(skill_name)
        LOG.debug(f"Prompt referenced skill: skill_name={skill_name!r} checklist={checklist!r}")
        if checklist:
            state["checklist_path"] = checklist
            state.setdefault("last_bucket", -1)
            save_state(path, state)
            LOG.debug(f"Tracking checklist for skill '{skill_name}': {checklist}")
        sys.exit(0)

    checklist_path = state.get("checklist_path")
    if not checklist_path:
        LOG.debug("No checklist tracked for this session, skipping.")
        sys.exit(0)

    pct = read_context_pct()
    LOG.debug(f"read_context_pct -> {pct!r} (statusline={STATUSLINE_PATH})")
    if pct is None:
        sys.exit(0)

    bucket = int(pct) // PERCENTAGE_BUCKET_SIZE
    last_bucket = state.get("last_bucket", -1)
    LOG.debug(f"bucket={bucket} last_bucket={last_bucket}")
    if bucket <= last_bucket:
        sys.exit(0)

    checklist_content = read_file(Path(checklist_path))
    if not checklist_content:
        LOG.debug(f"checklist_path={checklist_path} unreadable/empty")
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
                    "reason": f"context usage crossed {bucket * PERCENTAGE_BUCKET_SIZE}%",
                    "checklist_path": checklist_path,
                    "checklist": checklist_content,
                },
                ensure_ascii=False,
            ),
        }
    }
    LOG.debug(f"[additionalContext]: {output}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
