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


def extract_trigger_phrases(desc, name, skill_name):
    """Extract specific trigger phrases, prioritize by skill type"""
    desc_lower = desc.lower()
    name_lower = skill_name.lower()
    phrases = []

    # Primary triggers match skill name first (most specific)
    skill_triggers = {
        "test": [r"(write|implement).*test", r"(test|verify|spec)"],
        "testing": [r"(write|implement).*test", r"(test|verify|spec)"],
        "tdd": [r"(write|implement).*test", r"(test|verify|spec)"],
        "review": [r"(review|audit|check).*code", r"(review|audit).*PR"],
        "commit": [r"(commit|git commit).*message", r"(semantic|conventional).*commit"],
        "refactor": [r"(refactor|cleanup|rewrite).*code", r"(safe|improve).*refactor"],
        "design": [r"(design|diagram|visualiz).*", r"(architecture|ERD|flowchart)"],
    }

    # Check skill name for exact match first
    for key, pats in skill_triggers.items():
        if key in name_lower:
            phrases.extend(pats)
            return list(dict.fromkeys(phrases))[:3]

    # Secondary: extract from description
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

    return list(dict.fromkeys(phrases))[:3]


def extract_keywords_smart(desc, name):
    """Extract keywords prioritized by relevance and specificity"""
    keywords = []

    # Tier 1: skill name parts (highest priority)
    keywords.append(name)
    keywords.extend(name.split("-"))

    # Tier 2: first sentence/phrase (most important)
    first_sent = desc.split(".")[0] if "." in desc else desc[:100]
    words = re.findall(r"\b[a-z]+(?:-[a-z]+)?\b", first_sent.lower())
    # Filter: 4+ chars, exclude common words
    common = {"this", "that", "when", "with", "from", "into", "using"}
    tier2 = [w for w in words if len(w) > 3 and w not in common]
    keywords.extend(tier2)

    # Tier 3: secondary sentences (lower priority)
    sentences = desc.split(".")
    if len(sentences) > 1:
        for sent in sentences[1:2]:
            words = re.findall(r"\b[a-z]{5,}\b", sent.lower())
            keywords.extend(words[:2])

    # Deduplicate while preserving order, prioritize specificity (longer = more specific)
    seen = set()
    dedup = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            dedup.append(kw)

    # Sort: name/parts first, then by length (specific), then alphabetical
    def sort_key(kw):
        if kw == name:
            return (0, 0, kw)
        if kw in name.split("-"):
            return (1, -len(kw), kw)
        return (2, -len(kw), kw)

    sorted_kw = sorted(dedup, key=sort_key)
    return sorted_kw[:10]


def format_hint(desc):
    """Format hint: complete first sentence or smart truncation"""
    if not desc:
        return ""

    # Try to get complete first sentence
    sentences = desc.split(". ")
    first = sentences[0] + ("." if not sentences[0].endswith(".") else "")

    if len(first) <= 80:
        return first

    # Smart truncation: break at word boundary
    truncated = desc[:75]
    last_space = truncated.rfind(" ")
    if last_space > 50:
        return desc[:last_space] + "..."

    return truncated + "..."


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
        "create": "high",
        "generate": "high",
    }

    for skill in skills:
        name = skill["name"][0] if isinstance(skill["name"], list) else skill["name"]
        desc = skill.get("description", "")

        # Priority: smart detection
        priority = "medium"
        desc_name = (desc + " " + name).lower()
        for key, val in priority_map.items():
            if key in desc_name:
                priority = val
                break

        # Keywords: use smart extraction (prioritized, relevant)
        keywords = extract_keywords_smart(desc, name)

        # Patterns: skill-specific triggers, less generic duplicates
        main_term = name.split("-")[0]
        patterns = [f".*{main_term}.*"]
        triggers = extract_trigger_phrases(desc, name, name)
        patterns.extend(triggers)
        patterns = list(dict.fromkeys(patterns))[:4]

        # Hint: smart formatting (complete sentences)
        hint = format_hint(desc)

        rule = {
            "skill": name,
            "priority": priority,
            "hint": hint,
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
