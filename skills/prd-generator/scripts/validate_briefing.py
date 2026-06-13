#!/usr/bin/env python3
"""
Validate if a project briefing is sufficient for PRD generation.

Checks for minimum information needed before running 5-battery Q&A.
Used by prd-generator to confirm briefing completeness.

Exit codes:
  0 = Briefing sufficient, proceed to batteries
  1 = Briefing incomplete, ask for more info
"""

import sys
from typing import Tuple


def validate_briefing(briefing_text: str) -> Tuple[bool, list]:
    """
    Check if briefing contains minimum required elements.

    Returns:
        (is_valid: bool, missing_elements: list[str])
    """

    briefing_lower = briefing_text.lower()
    missing = []

    # Check 1: Problem statement
    problem_keywords = [
        "problem",
        "solve",
        "issue",
        "pain",
        "challenge",
        "build",
        "create",
        "make",
    ]
    has_problem = any(kw in briefing_lower for kw in problem_keywords)
    if not has_problem:
        missing.append("Problem statement (what's the challenge?)")

    # Check 2: Target users
    user_keywords = [
        "user",
        "customer",
        "team",
        "company",
        "business",
        "consumer",
        "developer",
        "admin",
        "people",
        "who",
    ]
    has_users = any(kw in briefing_lower for kw in user_keywords)
    if not has_users:
        missing.append("Target users (who will use this?)")

    # Check 3: Solution direction
    solution_keywords = [
        "app",
        "tool",
        "platform",
        "service",
        "system",
        "software",
        "build",
        "create",
        "web",
        "mobile",
        "api",
    ]
    has_solution = any(kw in briefing_lower for kw in solution_keywords)
    if not has_solution:
        missing.append("Solution direction (what are you building?)")

    # Check 4: Minimum length (50 words)
    word_count = len(briefing_text.split())
    if word_count < 15:
        missing.append(f"Briefing too short ({word_count} words, need ~15+)")

    is_valid = len(missing) == 0
    return is_valid, missing


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_briefing.py '<briefing text>'")
        print(
            "Example: python validate_briefing.py 'Building an IPTV player for Android. Uses xtream servers.'"
        )
        sys.exit(1)

    briefing = sys.argv[1]
    is_valid, missing = validate_briefing(briefing)

    if is_valid:
        print("✓ Briefing sufficient. Ready for 5-battery Q&A.")
        sys.exit(0)
    else:
        print("✗ Briefing incomplete. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("\nTips:")
        print("  - Describe the problem you're solving")
        print("  - Name the target users")
        print("  - Say what you're building (app, platform, API, etc.)")
        print("  - Aim for 2-5 sentences")
        sys.exit(1)


if __name__ == "__main__":
    main()
