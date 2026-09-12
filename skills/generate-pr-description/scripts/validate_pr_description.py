#!/usr/bin/env python3
"""
validate_pr_description.py - deterministic PR description structure check.

The skill promises the generated description follows the repo's own
.github/pull_request_template.md when present, else falls back to
Description/Impact/Task sections - and that every section is actually
filled in, not left as a template placeholder. This makes that checkable
instead of trusting the model to remember it. Pure standard library, zero
dependencies.

What it checks:
  ERROR - a required section heading (## ...) is missing
  ERROR - a section is empty (heading immediately followed by another
          heading or end of file)
  ERROR - a section still contains obvious placeholder text
          (TODO, TBD, <...>, [...] left unfilled)
  WARN  - description text is not in Markdown (no heading found at all)

Template source (priority order):
  1. .github/pull_request_template.md, if it exists - required headings are
     every top-level (##) heading found in it.
  2. Default fallback headings: Description, Impact, Task.

Usage:
  python3 <skill-dir>/scripts/validate_pr_description.py <pr_description.md>
  python3 <skill-dir>/scripts/validate_pr_description.py --message "## Description\\n..."
  cat pr.md | python3 <skill-dir>/scripts/validate_pr_description.py

Exit codes: 0 pass, 1 violation, 2 usage error.
"""

import argparse
import os
import re
import sys

DEFAULT_SECTIONS = ["Description", "Impact", "Task"]
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
TOP_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bTBD\b|<[^>\n]+>|\[[^\]\n]*\.\.\.[^\]\n]*\]")


def read_text(args):
    if args.message is not None:
        return args.message
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def required_sections(template_path):
    if template_path and os.path.exists(template_path):
        text = open(template_path, encoding="utf-8", errors="replace").read()
        headings = [m.group(1).strip() for m in TOP_HEADING_RE.finditer(text)]
        if headings:
            return headings
    return DEFAULT_SECTIONS


def section_bodies(text):
    """Map heading text -> body text between it and the next heading."""
    matches = list(HEADING_RE.finditer(text))
    bodies = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        bodies[m.group(1).strip()] = text[start:end].strip()
    return bodies


def check(text, sections):
    errors, warnings = [], []
    if not HEADING_RE.search(text):
        warnings.append("no Markdown heading found - description may not be structured")
        return errors, warnings

    bodies = section_bodies(text)
    for section in sections:
        matched = next((h for h in bodies if h.lower() == section.lower()), None)
        if matched is None:
            errors.append(f"missing required section: '{section}'")
            continue
        body = bodies[matched]
        if not body:
            errors.append(f"section '{section}' is empty")
            continue
        if PLACEHOLDER_RE.search(body):
            errors.append(
                f"section '{section}' still has placeholder text (TODO/TBD/<...>)"
            )
    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="validate_pr_description.py",
        description="Validate a generated PR description's structure.",
    )
    p.add_argument(
        "file", nargs="?", default=None, help="path to the PR description file"
    )
    p.add_argument("--message", default=None, help="the PR description as a string")
    p.add_argument(
        "--template",
        default=".github/pull_request_template.md",
        help="path to the repo's PR template (default: .github/pull_request_template.md)",
    )
    args = p.parse_args(argv)

    text = read_text(args)
    if not text.strip():
        print(
            "validate_pr_description: no content provided (pass a file, --message, or pipe via stdin).",
            file=sys.stderr,
        )
        return 2

    sections = required_sections(args.template)
    errors, warnings = check(text, sections)

    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if errors:
        print(
            f"\nvalidate_pr_description: FAIL ({len(errors)} error(s), required sections: {', '.join(sections)})"
        )
        return 1
    print(f"validate_pr_description: OK (sections: {', '.join(sections)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
