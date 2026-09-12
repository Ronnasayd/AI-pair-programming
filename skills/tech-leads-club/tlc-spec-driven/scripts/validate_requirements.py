#!/usr/bin/env python3
"""
validate_requirements.py - deterministic checks for a spec-to-requirements-table output.

Turns the spec-to-requirements-table skill's step-7 verification and
anti-pattern list into a checkable pass/fail run BEFORE the table is handed
to a reviewer, instead of trusting the model to self-audit. Pure standard
library, zero dependencies. Operates only on the generated requirements.md
markdown artifact - never on spec.md/design.md/tasks.md - so it stays
stack-agnostic and reusable on any project's table.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR  - no data rows found in any requirement table
  ERROR  - a row's Path/id column is not tagged SP or EP
  ERROR  - a row's rationale cell cites a spec code (REQ-03, AC-1.3, FR-07 ...)
           instead of explaining in plain words
  ERROR  - an "Accepted consequences" section is missing
  ERROR  - a consequences row has no "Driven by" row-id back-link
  WARN   - a row's Expression cell contains a bare concrete id/sample value
           (e.g. a standalone number, or a quoted literal) - possible lookup
  WARN   - no Glossary section, or an abbreviation used in the body
           (FR/NR/SP/EP) is not defined in it
  WARN   - a source line (Spec/Design/Tasks path) is missing

Usage:
  python3 <skill-dir>/scripts/validate_requirements.py [target] [--strict]

  Invoke from the skill directory that ships this script (not the project
  root). target defaults to requirements.md in the current directory.
  --strict  Treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

SPEC_CODE_RE = re.compile(r"\b(REQ|AC|FR|NR)-\d+(\.\d+)?\b")
PATH_TAG_RE = re.compile(r"\b(SP|EP)\b")
BARE_NUMBER_RE = re.compile(r"(?<![\w.#-])\d{2,}(?![\w.-])")
QUOTED_LITERAL_RE = re.compile(r'"[^"]{2,}"|\'[^\']{2,}\'')
SOURCE_LINE_RE = re.compile(
    r"^\*\*(Spec|Design|Tasks|BDD):\*\*\s*`([^`]+)`", re.MULTILINE
)


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def is_separator(line):
    return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)) and "-" in line


def find_tables(lines):
    """Yield (header_cells, [data_rows]) for every markdown table in the doc."""
    i = 0
    while i < len(lines):
        if (
            lines[i].strip().startswith("|")
            and i + 1 < len(lines)
            and is_separator(lines[i + 1])
        ):
            header = split_row(lines[i])
            j = i + 2
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            yield header, rows
            i = j
        else:
            i += 1


def check(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    errors, warnings = [], []

    tables = list(find_tables(lines))
    req_tables = [
        (h, r) for h, r in tables if not any("driven by" in c.lower() for c in h)
    ]
    cons_tables = [
        (h, r) for h, r in tables if any("driven by" in c.lower() for c in h)
    ]

    # 1. Requirement rows exist, tagged SP/EP, rationale doesn't cite spec codes.
    total_rows = 0
    for header, rows in req_tables:
        path_col = next(
            (
                idx
                for idx, c in enumerate(header)
                if c.strip().lower() in ("path", "sp/ep")
            ),
            None,
        )
        expr_col = next(
            (idx for idx, c in enumerate(header) if "expression" in c.lower()), None
        )
        comp_col = next(
            (idx for idx, c in enumerate(header) if "complement" in c.lower()), None
        )
        for row in rows:
            total_rows += 1
            if path_col is not None and path_col < len(row):
                if not PATH_TAG_RE.search(row[path_col]):
                    errors.append(f"row not tagged SP/EP: {row[0][:50]!r}")
            if comp_col is not None and comp_col < len(row):
                m = SPEC_CODE_RE.search(row[comp_col])
                if m:
                    errors.append(
                        f"rationale cites spec code {m.group(0)} instead of explaining: {row[0][:40]!r}"
                    )
            if expr_col is not None and expr_col < len(row):
                cell = row[expr_col]
                if BARE_NUMBER_RE.search(cell) or QUOTED_LITERAL_RE.search(cell):
                    warnings.append(
                        f"Expression may embed a concrete id/sample value (forces lookup): {row[0][:40]!r}"
                    )

    if total_rows == 0:
        errors.append("no data rows found in any requirement table")

    # 2. Accepted consequences section + Driven by back-links.
    if not re.search(r"^#{1,3}\s.*consequence", text, re.IGNORECASE | re.MULTILINE):
        errors.append("missing 'Accepted consequences' section")
    elif not cons_tables:
        errors.append("consequences section has no table with a 'Driven by' column")
    else:
        for header, rows in cons_tables:
            driven_col = next(
                idx for idx, c in enumerate(header) if "driven by" in c.lower()
            )
            for row in rows:
                if driven_col >= len(row) or not row[driven_col].strip():
                    errors.append(
                        f"consequence row has empty 'Driven by' back-link: {row[0][:40]!r}"
                    )

    # 3. Glossary covers abbreviations actually used.
    body_upper = text.upper()
    used_abbrevs = {
        a for a in ("FR", "NR", "SP", "EP") if re.search(rf"\b{a}\b", body_upper)
    }
    gloss_match = re.search(
        r"^#{1,3}\s*Glossary\s*$", text, re.IGNORECASE | re.MULTILINE
    )
    if not gloss_match and used_abbrevs:
        warnings.append(
            f"no Glossary section, but abbreviations used: {sorted(used_abbrevs)}"
        )
    elif gloss_match:
        gloss_body = text[gloss_match.end() :]
        undefined = [
            a for a in used_abbrevs if not re.search(rf"\*\*{a}\*\*", gloss_body)
        ]
        if undefined:
            warnings.append(
                f"abbreviations used but not defined in Glossary: {sorted(undefined)}"
            )

    # 4. Source lines present.
    sources = dict(SOURCE_LINE_RE.findall(text))
    for label in ("Spec", "Design"):
        if label not in sources:
            warnings.append(f"no **{label}**: source line at top of file")

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="validate_requirements.py",
        description="Deterministic checks for a spec-to-requirements-table output.",
    )
    p.add_argument("target", nargs="?", default="requirements.md")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)

    path = args.target
    if os.path.isdir(path):
        path = os.path.join(path, "requirements.md")
    if not os.path.isfile(path):
        print(f"validate_requirements: file not found: {path}", file=sys.stderr)
        return 2

    errors, warnings = check(path)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    fail = errors or (warnings and args.strict)
    print(
        f"\nvalidate_requirements: {len(errors)} error(s), {len(warnings)} warning(s) in {path}"
    )
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
