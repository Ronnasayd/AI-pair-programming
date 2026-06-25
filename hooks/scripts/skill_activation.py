#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    read_file,
    write_file,
)

LOG = get_hooks_logger("SkillActivation")
RULES_PATH = Path(".claude/skill-rules.json")
DEDUP_HOURS = 24


def load_rules():
    try:
        content = read_file(RULES_PATH)
        if not content:
            LOG.debug("No rules file found, using empty ruleset")
            return {"rules": []}
        rules_data = json.loads(content)
        LOG.debug(f"Loaded {len(rules_data.get('rules', []))} rules from {RULES_PATH}")
        return rules_data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        LOG.debug(f"Failed to load rules: {e}")
        return {"rules": []}


def load_rec_log(rec_log_path: Path):
    try:
        if rec_log_path.exists():
            content = read_file(rec_log_path)
            if content:
                rec_log = json.loads(content)
                LOG.debug(
                    f"Loaded rec log with {len(rec_log)} entries from {rec_log_path}"
                )
                return rec_log
            LOG.debug(f"Rec log file exists but is empty: {rec_log_path}")
        else:
            LOG.debug(f"No rec log file found: {rec_log_path}")
    except (json.JSONDecodeError, Exception) as e:
        LOG.debug(f"Failed to load rec log: {e}")
    return {}


def save_rec_log(rec_log_path: Path, rec_log):
    try:
        write_file(rec_log_path, json.dumps(rec_log))
        LOG.debug(f"Saved rec log with {len(rec_log)} entries to {rec_log_path}")
    except Exception as e:
        LOG.debug(f"Failed to save rec log: {e}")


def should_suggest(skill_name, rec_log):
    if skill_name not in rec_log:
        return True
    last_iso = rec_log[skill_name]
    try:
        last_time = datetime.fromisoformat(last_iso)
        time_diff = datetime.now() - last_time
        if time_diff >= timedelta(hours=DEDUP_HOURS):
            LOG.debug(
                f"Skill '{skill_name}' last suggested {time_diff.total_seconds() / 3600:.1f}h ago, will suggest again"
            )
            return True
        LOG.debug(
            f"Skill '{skill_name}' recently suggested ({time_diff.total_seconds() / 3600:.1f}h ago), skipping"
        )
    except ValueError as e:
        LOG.debug(f"Invalid timestamp for '{skill_name}': {e}, will suggest")
        return True
    return False


MAX_SUGGESTIONS = 5
MIN_SCORE = 5

# Generic action/filler words - low value for skill relevance
GENERIC_WORDS = {
    "create",
    "generate",
    "write",
    "make",
    "build",
    "add",
    "get",
    "use",
    "whenever",
    "include",
    "about",
    "skill",
    "using",
    "based",
    "always",
}


def score_rule(prompt, rule):
    """Score match relevance. Higher = more specific/relevant."""
    prompt_lower = prompt.lower()
    prompt_words = set(re.findall(r"\b\w+\b", prompt_lower))
    skill_name = rule.get("skill", "")
    skill_parts = set(skill_name.lower().split("-"))

    score = 0

    # Skill name parts overlap with prompt words (most specific signal)
    name_overlap = prompt_words & skill_parts
    for word in name_overlap:
        score += 2 if word in GENERIC_WORDS else 5

    # Keyword matches: domain-specific score higher than generic action words
    for keyword in rule.get("keywords", []):
        kw_lower = keyword.lower()
        if kw_lower in prompt_lower:
            if kw_lower in GENERIC_WORDS:
                score += 1
            else:
                score += len(kw_lower.split()) * 3

    # Pattern matches: low score (catch-all patterns)
    for pattern in rule.get("intentPatterns", []):
        try:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 1
        except re.error:
            pass

    return score


def match_rule(prompt, rule):
    keywords = rule.get("keywords", [])
    intent_patterns = rule.get("intentPatterns", [])
    rule_name = rule.get("skill", "unknown")

    prompt_lower = prompt.lower()
    for keyword in keywords:
        if keyword.lower() in prompt_lower:
            LOG.debug(f"Rule '{rule_name}' matched keyword: '{keyword}'")
            return True

    for pattern in intent_patterns:
        try:
            if re.search(pattern, prompt, re.IGNORECASE):
                LOG.debug(f"Rule '{rule_name}' matched pattern: '{pattern}'")
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
        LOG.debug("Failed to parse stdin JSON payload")
        sys.exit(0)

    try:
        prompt = get_by_key(payload, "prompt")
        if not prompt:
            LOG.debug("No prompt found in payload")
            sys.exit(0)

        LOG.debug(f"Processing prompt ({len(prompt)} chars)")

        session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
        rec_log_path = Path(f"/tmp/skill-rec-log-{session_id}.json")
        LOG.debug(f"Session: {session_id}")

        rules_data = load_rules()
        rules = rules_data.get("rules", [])
        if not rules:
            LOG.debug("No rules available, skipping skill activation")
            sys.exit(0)

        rec_log = load_rec_log(rec_log_path)
        sorted_rules = sort_rules_by_priority(rules)
        LOG.debug(f"Processing {len(sorted_rules)} rules (prioritized)")

        scored_matches = []
        for rule in sorted_rules:
            skill_name = rule.get("skill")
            if not skill_name:
                continue

            if match_rule(prompt, rule) and should_suggest(skill_name, rec_log):
                score = score_rule(prompt, rule)
                LOG.debug(f"Skill '{skill_name}' score: {score}")
                if score >= MIN_SCORE:
                    hint = rule.get("hint", "")
                    scored_matches.append((score, skill_name, hint))

        scored_matches.sort(key=lambda x: x[0], reverse=True)
        matches = [(name, hint) for _, name, hint in scored_matches[:MAX_SUGGESTIONS]]

        for name, _ in matches:
            rec_log[name] = datetime.now().isoformat()

        if matches:
            LOG.debug(f"Found {len(matches)} skill matches: {[m[0] for m in matches]}")
            save_rec_log(rec_log_path, rec_log)
            suggestions = "; ".join(f"`/{m[0]}` — {m[1]}" for m in matches)
            context = f"**Skill suggestions:** {suggestions}"
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }
            LOG.debug(f"Output: {output}")
            print(json.dumps(output))
        else:
            LOG.debug("No skill matches found")

    except Exception as e:
        LOG.debug(f"Unexpected error: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
