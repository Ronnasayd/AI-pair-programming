#!/usr/bin/env python3
"""
Sync skill-rules.json from skills/index.yaml
Auto-generates activation rules for all skills.
Usage: sync-skill-rules.py [--check]
"""

import yaml
import json
import re
import sys
import argparse
from pathlib import Path


def extract_trigger_phrases(desc, name):
    """Extract specific trigger phrases from description"""
    desc_lower = desc.lower()
    phrases = []

    triggers = {
        "review": [r"(review|audit|check).*code", r"(review|audit).*PR"],
        "commit": [r"(commit|git commit).*message", r"(semantic|conventional).*commit"],
        "test": [r"(write|implement).*test", r"(test|verify|spec)"],
        "refactor": [r"(refactor|cleanup|rewrite).*code", r"(safe|improve).*refactor"],
        "design": [r"(design|diagram|visualiz).*", r"(architecture|ERD|flowchart)"],
        "generate": [
            r"(generate|create|write|produce).*",
            r"(generate|make|build).*PRD",
        ],
        "analyze": [r"(analyze|audit|check).*", r"(diagnose|debug|investigate)"],
        "migrate": [r"(migrate|upgrade|transition).*"],
        "research": [r"(research|search|lookup).*", r"(deep|thorough).*research"],
    }

    for trigger_type, patterns in triggers.items():
        if trigger_type in desc_lower:
            phrases.extend(patterns)

    return list(dict.fromkeys(phrases))[:4]


def generate_rules(yaml_path):
    """Generate skill-rules from index.yaml"""

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    skills = data.get("skills", [])
    rules = []

    priority_map = {
        "advisor": "high",
        "commit": "high",
        "review": "high",
        "test": "high",
        "testing": "high",
        "tdd": "high",
        "debug": "high",
        "diagnosing": "high",
        "refactor": "medium",
        "safe-refactor": "medium",
        "pattern": "medium",
        "best-practice": "medium",
        "style-guide": "medium",
    }

    for skill in skills:
        name = skill["name"][0] if isinstance(skill["name"], list) else skill["name"]
        desc = skill.get("description", "")

        # Priority
        priority = "medium"
        desc_name = (desc + " " + name).lower()
        for key, val in priority_map.items():
            if key in desc_name:
                priority = val
                break

        # Keywords
        keywords = []
        keywords.append(name)
        name_parts = name.split("-")
        keywords.extend(name_parts)

        first_sent = desc.split(".")[0] if "." in desc else desc[:120]
        words = re.findall(r"\b[a-z]+(?:-[a-z]+)?\b", first_sent.lower())
        keywords.extend([w for w in words if len(w) > 3])

        keywords = sorted(list(dict.fromkeys(keywords)))[:8]

        # Patterns
        patterns = []
        main_term = name.split("-")[0]
        patterns.append(f".*{main_term}.*")
        triggers = extract_trigger_phrases(desc, name)
        patterns.extend(triggers)
        patterns = list(dict.fromkeys(patterns))[:5]

        rule = {
            "skill": name,
            "priority": priority,
            "hint": (desc[:70] + "...") if len(desc) > 70 else desc,
            "keywords": keywords,
            "intentPatterns": patterns,
        }

        rules.append(rule)

    return {"rules": rules}


def main():
    parser = argparse.ArgumentParser(
        description="Sync skill-rules.json from skills/index.yaml"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check if update needed without writing"
    )
    parser.add_argument(
        "--yaml", default="skills/index.yaml", help="Path to index.yaml"
    )
    parser.add_argument(
        "--output", default="claude/skill-rules.json", help="Path to output JSON"
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    output_path = Path(args.output)

    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found", file=sys.stderr)
        sys.exit(1)

    # Generate new rules
    new_data = generate_rules(yaml_path)
    new_json = json.dumps(new_data, indent=2)

    # Check if file exists and compare
    if output_path.exists():
        with open(output_path, "r") as f:
            existing_json = f.read()

        if existing_json.strip() == new_json.strip():
            print(f"✓ {output_path} is up-to-date ({len(new_data['rules'])} rules)")
            return 0

    # Write or check mode
    if args.check:
        print(f"✗ {output_path} needs update ({len(new_data['rules'])} rules)")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(new_json)

    print(f"✓ Updated {output_path} ({len(new_data['rules'])} rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
