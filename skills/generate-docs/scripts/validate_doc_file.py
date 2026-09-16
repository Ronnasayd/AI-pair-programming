#!/usr/bin/env python3
"""
validate_doc_file.py - deterministic checks for one generate-docs output file.

Turns generate-docs' references/shared.md Writing Standards / Quality
Checklist / Anti-patterns, plus the module-file structure required by
references/create.md, into a checkable pass/fail run for a single generated
docs/*.md file - instead of trusting the model to self-audit. Pure standard
library, zero dependencies.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR  - file contains placeholder text (TODO, TBD, <fill in>, "...")
  ERROR  - a docs/*.md path is referenced as plain text instead of a
           Markdown link (e.g. "docs/architecture.md" not `[..](..)`)
  ERROR  - docs/architecture.md has no Mermaid diagram (```mermaid block)
  ERROR  - a docs/modules/<name>.md file is missing one of the 7 required
           sections (Purpose, Role in architecture, Interactions,
           Key concepts, Entry points, What this module is NOT) -
           matched heuristically by heading/keyword, not exact wording
  WARN   - no `#`/`##` heading found at all (file may not be Markdown)
  WARN   - a module file mentions implementation details (a fenced code
           block) - module files should stay high-level per create.md

Usage:
  python3 <skill-dir>/scripts/validate_doc_file.py <file.md> [--strict]

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bTBD\b|<fill in>|<[^>\n]+>|(?<!\w)\.\.\.(?!\w)")
PLAIN_DOC_REF_RE = re.compile(r"(?<![(\[`])\bdocs/[\w./-]+\.md\b(?!\))")
HEADING_RE = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
MERMAID_RE = re.compile(r"^```mermaid\s*$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)

MODULE_SECTIONS = {
    "purpose": r"purpose|responsibilit",
    "role in architecture": r"role.*architecture|architecture.*fit",
    "interactions": r"interaction",
    "key concepts": r"key concept|abstraction",
    "entry points": r"entry point",
    "what this module is not": r"not\b.*this module|this module is not|out of scope|scope boundar",
}


def is_module_file(path):
    parts = os.path.normpath(path).split(os.sep)
    return "modules" in parts


def is_architecture_file(path):
    return os.path.basename(path) == "architecture.md"


def check(path, text):
    errors, warnings = [], []

    if PLACEHOLDER_RE.search(text):
        errors.append("file contains placeholder text (TODO/TBD/<fill in>/...)")

    for m in PLAIN_DOC_REF_RE.finditer(text):
        errors.append(
            f"docs/ file referenced as plain text, not a Markdown link: {m.group(0)!r}"
        )

    if not HEADING_RE.search(text):
        warnings.append("no Markdown heading found - file may not be structured")

    if is_architecture_file(path) and not MERMAID_RE.search(text):
        errors.append("docs/architecture.md has no Mermaid diagram (```mermaid block)")

    if is_module_file(path):
        lower = text.lower()
        for label, pattern in MODULE_SECTIONS.items():
            if not re.search(pattern, lower):
                errors.append(f"module file missing required section: '{label}'")
        if CODE_FENCE_RE.search(text):
            warnings.append(
                "module file contains a fenced code block - keep module docs high-level, no code walkthroughs"
            )

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="validate_doc_file.py",
        description="Deterministic checks for one generate-docs output file.",
    )
    p.add_argument("target")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)

    if not os.path.isfile(args.target):
        print(f"validate_doc_file: file not found: {args.target}", file=sys.stderr)
        return 2

    with open(args.target, "r", encoding="utf-8") as f:
        text = f.read()

    errors, warnings = check(args.target, text)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    fail = errors or (warnings and args.strict)
    print(
        f"\nvalidate_doc_file: {len(errors)} error(s), {len(warnings)} warning(s) in {args.target}"
    )
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
