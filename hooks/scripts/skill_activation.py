#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_by_key,
    get_hooks_logger,
    read_file,
    write_file,
    get_session_id_short,
)

LOG = get_hooks_logger("SkillActivation")
RULES_PATH = Path(".claude/skill-rules.json")
DEDUP_HOURS = 24


def load_rules():
    try:
        content = read_file(RULES_PATH)
        if not content:
            return {"rules": []}
        return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        LOG.debug(f"Failed to load rules: {e}")
        return {"rules": []}


def load_rec_log(rec_log_path: Path):
    try:
        if rec_log_path.exists():
            content = read_file(rec_log_path)
            if content:
                return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        LOG.debug(f"Failed to load rec log: {e}")
    return {}


def save_rec_log(rec_log_path: Path, rec_log):
    try:
        write_file(rec_log_path, json.dumps(rec_log))
    except Exception as e:
        LOG.debug(f"Failed to save rec log: {e}")


def should_suggest(skill_name, rec_log):
    if skill_name not in rec_log:
        return True
    last_iso = rec_log[skill_name]
    try:
        last_time = datetime.fromisoformat(last_iso)
        if datetime.now() - last_time >= timedelta(hours=DEDUP_HOURS):
            return True
    except ValueError:
        return True
    return False


def match_rule(prompt, rule):
    keywords = rule.get("keywords", [])
    intent_patterns = rule.get("intentPatterns", [])

    prompt_lower = prompt.lower()
    for keyword in keywords:
        if keyword.lower() in prompt_lower:
            return True

    for pattern in intent_patterns:
        try:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        except re.error as e:
            LOG.debug(f"Invalid regex pattern '{pattern}': {e}")

    return False


def sort_rules_by_priority(rules):
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(
        rules, key=lambda r: priority_order.get(r.get("priority", "low"), 999)
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    try:
        prompt = get_by_key(payload, "prompt")
        if not prompt:
            sys.exit(0)

        session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
        rec_log_path = Path(f"/tmp/skill-rec-log-{session_id}.json")

        rules_data = load_rules()
        rules = rules_data.get("rules", [])
        if not rules:
            sys.exit(0)

        rec_log = load_rec_log(rec_log_path)
        sorted_rules = sort_rules_by_priority(rules)

        matches = []
        for rule in sorted_rules:
            skill_name = rule.get("skill")
            if not skill_name:
                continue

            if match_rule(prompt, rule) and should_suggest(skill_name, rec_log):
                hint = rule.get("hint", "")
                matches.append((skill_name, hint))
                rec_log[skill_name] = datetime.now().isoformat()

        if matches:
            save_rec_log(rec_log_path, rec_log)
            suggestions = "; ".join(f"`/{m[0]}` — {m[1]}" for m in matches)
            context = f"**Skill suggestions:** {suggestions}"
            output = {"hookSpecificOutput": {"additionalContext": context}}
            print(json.dumps(output))

    except Exception as e:
        LOG.debug(f"Unexpected error: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
