#!/usr/bin/env python3
"""validate_context_map.py - deterministic structure check for a context-map output.

Turns the context-map skill's "Output Format" and Phase 7 verification into a
checkable pass/fail run BEFORE the map is handed to a reviewer, instead of
trusting the model to self-audit. Pure standard library, zero dependencies.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR - a required section heading (###) is missing
  ERROR - a required section is empty
  ERROR - a required table has the wrong header columns
  ERROR - "Files to Modify" has no data rows
  ERROR - a table still contains template placeholder rows (path/to/...)
  ERROR - "Task Interpretation" lacks a valid "Task type:" or an "Anchors:" line
  ERROR - "Risk Assessment" has no checkbox items
  WARN  - a table has more than 10 data rows (rank by impact, trim)
  WARN  - a path in a table's first column does not exist under --root
          (skipped for values that are not path-like)
  WARN  - "Assumptions:" line missing from "Task Interpretation"

Usage:
  python3 <skill-dir>/scripts/validate_context_map.py [target] [--root DIR] [--strict]

  target   context map markdown file; defaults to stdin when piped, else
           context-map.md in cwd.
  --root   repo root used to verify cited paths (default: cwd).
  --strict treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
from pathlib import Path
import re
import sys
from typing import TextIO

TASK_TYPES = {"feature", "fix", "refactor", "config", "docs"}

TABLES = {
    "Files to Modify": ["file", "purpose", "changes needed"],
    "Dependencies (may need updates)": ["file", "relationship"],
    "Test Files": ["test", "coverage"],
    "Reference Patterns": ["file", "pattern"],
}
REQUIRED = [
    "Task Interpretation",
    *TABLES,
    "Risk Assessment",
    "Not Checked",
]
MAX_ROWS = 10
DEFAULT_TARGET = "context-map.md"

HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(
    r"path/to/|\bTODO\b|\bTBD\b|what changes|^description$", re.IGNORECASE
)
PATH_RE = re.compile(r"^[\w./@+-]+\.\w+$|^[\w./@+-]+/[\w./@+-]*$")
CHECKBOX_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+\S", re.MULTILINE)
TASK_TYPE_RE = re.compile(r"task type:\s*`?([a-z]+)", re.IGNORECASE)
ANCHORS_RE = re.compile(r"anchors?:", re.IGNORECASE)
ASSUMPTIONS_RE = re.compile(r"assumptions?:", re.IGNORECASE)


def read_text(target: str | None) -> str:
    """Read the map from a file, stdin, or the default file.

    Args:
        target: path to the map, or None to use stdin / the default file.

    Returns:
        The map text, empty when nothing was provided.
    """
    if target:
        return Path(target).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    default = Path(DEFAULT_TARGET)
    return default.read_text(encoding="utf-8") if default.exists() else ""


def sections(text: str) -> dict[str, str]:
    """Map lowercase ### heading -> body up to the next heading.

    Args:
        text: the whole map.

    Returns:
        Dict of heading to stripped body.
    """
    matches = list(HEADING_RE.finditer(text))
    out = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[m.group(1).strip().lower()] = text[m.end() : end].strip()
    return out


def split_row(line: str) -> list[str]:
    """Split one markdown table row into stripped cells.

    Args:
        line: a `| a | b |` row.

    Returns:
        The cell texts.
    """
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_table(body: str) -> tuple[list[str] | None, list[list[str]]]:
    """Parse the first markdown table in a section body.

    Args:
        body: section text.

    Returns:
        (lowercase header cells or None when no table, data rows).
    """
    lines = [ln for ln in body.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return None, []
    header = [c.lower() for c in split_row(lines[0])]
    return header, [split_row(ln) for ln in lines[2:]]


def clean_cell(cell: str) -> str:
    """Strip backticks/emphasis/spaces around a cell value.

    Args:
        cell: raw cell text.

    Returns:
        The cleaned value.
    """
    return cell.strip("`* ")


def check_table(name: str, body: str, root: Path) -> tuple[list[str], list[str]]:
    """Check one required table's columns, rows, placeholders and paths.

    Args:
        name: table section name.
        body: section body.
        root: repo root for path existence checks.

    Returns:
        (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []
    header, rows = parse_table(body)
    if header is None:
        # why: prose such as "None found." is valid for every table but Files to Modify
        if name == "Files to Modify":
            errors.append("'Files to Modify' has no table")
        return errors, warnings
    if header != TABLES[name]:
        errors.append(f"'{name}' header {header} != expected {TABLES[name]}")
    if not rows and name == "Files to Modify":
        errors.append("'Files to Modify' has no data rows")
    if len(rows) > MAX_ROWS:
        warnings.append(f"'{name}' has {len(rows)} rows (> {MAX_ROWS}); trim")
    for row in rows:
        if any(PLACEHOLDER_RE.search(clean_cell(c)) for c in row):
            errors.append(f"'{name}' contains placeholder row: {row}")
            continue
        path = clean_cell(row[0]) if row else ""
        if PATH_RE.match(path) and not (root / path).exists():
            warnings.append(f"'{name}': path not found under root: {path}")
    return errors, warnings


def check_interpretation(body: str) -> tuple[list[str], list[str]]:
    """Check the Task Interpretation section's required lines.

    Args:
        body: section body.

    Returns:
        (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []
    m = TASK_TYPE_RE.search(body)
    if not m or m.group(1).lower() not in TASK_TYPES:
        errors.append(
            f"'Task Interpretation' needs 'Task type:' one of {sorted(TASK_TYPES)}"
        )
    if not ANCHORS_RE.search(body):
        errors.append("'Task Interpretation' needs an 'Anchors:' line")
    if not ASSUMPTIONS_RE.search(body):
        warnings.append("'Task Interpretation' has no 'Assumptions:' line")
    return errors, warnings


def check(text: str, root: Path) -> tuple[list[str], list[str]]:
    """Run every check against a context map.

    Args:
        text: the whole map.
        root: repo root for path existence checks.

    Returns:
        (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []
    secs = sections(text)

    for name in REQUIRED:
        body = secs.get(name.lower())
        if body is None:
            errors.append(f"missing required section: '{name}'")
        elif not body:
            errors.append(f"section '{name}' is empty")

    checks = [
        check_table(name, secs[name.lower()], root)
        for name in TABLES
        if secs.get(name.lower())
    ]
    if secs.get("task interpretation"):
        checks.append(check_interpretation(secs["task interpretation"]))
    for errs, warns in checks:
        errors += errs
        warnings += warns

    risk = secs.get("risk assessment")
    if risk and not CHECKBOX_RE.search(risk):
        errors.append("'Risk Assessment' has no checkbox items (- [ ] ...)")
    return errors, warnings


def emit(message: str, stream: TextIO | None = None) -> None:
    """Write one line to stdout, or to the given stream.

    Args:
        message: text to write.
        stream: file-like target, stdout when None.
    """
    (stream or sys.stdout).write(message + "\n")


def main(argv: list[str] | None = None) -> int:
    """Validate a context map from the command line.

    Args:
        argv: argument list, sys.argv[1:] when None.

    Returns:
        Exit code: 0 pass, 1 violations, 2 usage error.
    """
    p = argparse.ArgumentParser(
        prog="validate_context_map.py",
        description="Validate a generated context-map's structure.",
    )
    p.add_argument("target", nargs="?", default=None, help="context map file")
    p.add_argument("--root", default=str(Path.cwd()), help="repo root for paths")
    p.add_argument("--strict", action="store_true", help="warnings are errors")
    args = p.parse_args(argv)

    try:
        text = read_text(args.target)
    except OSError as exc:
        emit(f"validate_context_map: {exc}", sys.stderr)
        return 2
    if not text.strip():
        emit(
            "validate_context_map: no content (pass a file, pipe stdin, "
            f"or create {DEFAULT_TARGET}).",
            sys.stderr,
        )
        return 2

    errors, warnings = check(text, Path(args.root))
    for w in warnings:
        emit(f"  WARN  {w}")
    for err in errors:
        emit(f"  ERROR {err}")
    if errors or (args.strict and warnings):
        emit(
            f"\nvalidate_context_map: FAIL "
            f"({len(errors)} error(s), {len(warnings)} warning(s))"
        )
        return 1
    emit(f"validate_context_map: OK ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
