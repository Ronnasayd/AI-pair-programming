#!/usr/bin/env python3
"""
validate_summary.py - deterministic checks for docs/SUMMARY.md navigability.

Turns generate-docs' shared.md Quality Checklist ("Navigability - every doc
linked from SUMMARY.md; all cross-references use Markdown links") and its
matching anti-patterns ("Creating isolated files without linking from
SUMMARY.md", "Referencing files as plain text") into a checkable pass/fail
run, instead of trusting the model to self-audit. Pure standard library,
zero dependencies. Operates on docs/SUMMARY.md plus the docs/ tree it should
describe - never on source code - so it stays stack-agnostic.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR  - SUMMARY.md does not exist
  ERROR  - a markdown file under docs/ (excluding SUMMARY.md itself) is not
           linked from anywhere in SUMMARY.md
  ERROR  - SUMMARY.md contains placeholder text (TODO, TBD, <fill in>, ...)
  WARN   - a docs/ file is referenced in SUMMARY.md as plain text
           (e.g. "docs/architecture.md" not wrapped in a Markdown link)
  WARN   - a Markdown link in SUMMARY.md points to a docs/ path that
           doesn't exist (stale cross-reference)

Usage:
  python3 <skill-dir>/scripts/validate_summary.py [docs_dir] [--strict]

  Invoke from the skill directory that ships this script (not the project
  root). docs_dir defaults to "docs" in the current directory.
  --strict  Treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|\bTBD\b|<fill in>|<[^>\n]+>|\.\.\.\s*$", re.MULTILINE
)
PLAIN_DOC_REF_RE = re.compile(r"(?<![(\[`])\bdocs/[\w./-]+\.md\b(?!\))")


def find_doc_files(docs_dir, summary_path):
    found = []
    for root, _dirs, files in os.walk(docs_dir):
        for name in files:
            if not name.endswith(".md"):
                continue
            full = os.path.join(root, name)
            if os.path.abspath(full) == os.path.abspath(summary_path):
                continue
            found.append(os.path.relpath(full, docs_dir))
    return sorted(found)


def check(summary_path, docs_dir):
    errors, warnings = [], []

    with open(summary_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc_files = find_doc_files(docs_dir, summary_path)

    linked_targets = set()
    for m in MD_LINK_RE.finditer(text):
        target = m.group(1).split("#", 1)[0]
        linked_targets.add(target)
        linked_targets.add(os.path.normpath(target))

    for rel in doc_files:
        candidates = {
            rel,
            rel.replace(os.sep, "/"),
            f"docs/{rel.replace(os.sep, '/')}",
            f"./{rel.replace(os.sep, '/')}",
        }
        if not (candidates & linked_targets):
            errors.append(
                f"not linked from SUMMARY.md: docs/{rel.replace(os.sep, '/')}"
            )

    if PLACEHOLDER_RE.search(text):
        errors.append("SUMMARY.md contains placeholder text (TODO/TBD/<fill in>)")

    for m in PLAIN_DOC_REF_RE.finditer(text):
        warnings.append(
            f"docs/ file referenced as plain text, not a Markdown link: {m.group(0)!r}"
        )

    for m in MD_LINK_RE.finditer(text):
        target = m.group(1).split("#", 1)[0]
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = os.path.normpath(os.path.join(os.path.dirname(summary_path), target))
        if not os.path.isfile(resolved):
            warnings.append(f"link in SUMMARY.md points to a missing file: {target!r}")

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="validate_summary.py",
        description="Deterministic navigability checks for docs/SUMMARY.md.",
    )
    p.add_argument("docs_dir", nargs="?", default="docs")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)

    docs_dir = args.docs_dir
    summary_path = os.path.join(docs_dir, "SUMMARY.md")
    if not os.path.isfile(summary_path):
        print(f"validate_summary: file not found: {summary_path}", file=sys.stderr)
        return 2

    errors, warnings = check(summary_path, docs_dir)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    fail = errors or (warnings and args.strict)
    print(
        f"\nvalidate_summary: {len(errors)} error(s), {len(warnings)} warning(s) in {summary_path}"
    )
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
