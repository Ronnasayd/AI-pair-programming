#!/usr/bin/env python3
"""Deterministic checks for an srs-generator output.

Turns the srs-generator SKILL.md's Generation Rules and Quality Checklist
into a checkable pass/fail run BEFORE the document is handed to a reviewer,
instead of trusting the model to self-audit. Pure standard library, zero
dependencies. Operates only on the generated SRS markdown file - never on
the template itself - so it stays reusable on any generated SRS.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR  - missing top-level "# SRS — {title}" header
  ERROR  - a required numbered section (1..4 and their subsections per
           references/srs-template.md) is absent
  ERROR  - no functional requirement (FR-XXX) found
  ERROR  - fewer than 3 FR, 1 UR (usability), or 1 PR (performance) found
  ERROR  - a requirement id repeats (duplicate FR-001, NFR-002, ...)
  ERROR  - a FR/NFR block is missing "Priority" or "Verification Method"
  ERROR  - Priority value is not High/Medium/Low
  ERROR  - Verification Method value is not one of Inspection/Analysis/
           Demonstration/Test
  ERROR  - no mention of "ISO/IEC/IEEE 29148" anywhere in the document
  WARN   - a requirement description contains " and " (possible non-Singular
           requirement, should be split)
  WARN   - a requirement description contains a vague/ambiguous term
           (e.g. "etc", "as needed", "user-friendly", "fast", "TBD")
  WARN   - "To be defined" gap markers present (informational: review before
           finalizing, not a defect in the script's output)

Usage:
  python3 <skill-dir>/scripts/validate_srs.py [target] [--strict]

  target defaults to the newest file under docs/srs/*.md in the current
  directory tree; pass an explicit path otherwise.
  --strict  Treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import glob
import os
import re
import sys

REQUIRED_SECTIONS = [
    r"^##\s*1\.\s*Introduction",
    r"^###\s*1\.1\s*Purpose",
    r"^###\s*1\.2\s*Scope",
    r"^###\s*1\.3\s*Definitions",
    r"^###\s*1\.4\s*References",
    r"^##\s*2\.\s*Overall Description",
    r"^###\s*2\.1\s*Product Perspective",
    r"^###\s*2\.2\s*Product Functions",
    r"^###\s*2\.3\s*User Characteristics",
    r"^##\s*3\.\s*Specific Requirements",
    r"^###\s*3\.2\s*Functional Requirements",
    r"^###\s*3\.3\s*Usability Requirements",
    r"^###\s*3\.4\s*Performance Requirements",
    r"^###\s*3\.8\s*System Attributes",
    r"^##\s*4\.\s*Appendices",
    r"^###\s*4\.2\s*Glossary",
]

REQ_ID_RE = re.compile(r"^####\s*(FR|NFR|UR|PR|DBR|INT)-(\d+)\b.*$", re.MULTILINE)
FIELD_LINE_RE = re.compile(
    r"^-\s*\*\*(Priority|Verification Method):?\*\*:?\s*(.+)$", re.MULTILINE
)
VALID_PRIORITY = {"high", "medium", "low"}
VALID_VERIFICATION = {"inspection", "analysis", "demonstration", "test"}
VAGUE_TERMS = [
    "etc",
    "as needed",
    "user-friendly",
    "user friendly",
    "fast",
    "TBD",
    "should probably",
]

RequirementBlock = tuple[str, str, str]
CheckResult = tuple[list[str], list[str]]


def find_requirement_blocks(text: str) -> list[RequirementBlock]:
    """Split the document into one entry per requirement heading.

    Args:
        text: Full SRS document source.

    Returns:
        List of (requirement_id, kind, block_text) tuples, one per
        '#### ID — ...' heading, where block_text is everything up to the
        next heading (or end of document).
    """
    matches = list(REQ_ID_RE.finditer(text))
    blocks = []
    for i, m in enumerate(matches):
        kind, num = m.group(1), m.group(2)
        rid = f"{kind}-{num}"
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append((rid, kind, text[start:end]))
    return blocks


def check_structure(text: str) -> list[str]:
    """Check the document header, required sections, and standard reference.

    Args:
        text: Full SRS document source.

    Returns:
        Error messages for any missing header, required section, or
        ISO/IEC/IEEE 29148 reference.
    """
    errors = []
    if not re.search(r"^#\s*SRS\s*—", text, re.MULTILINE):
        errors.append("missing top-level '# SRS — {title}' header")
    errors.extend(
        f"missing required section matching /{pattern}/"
        for pattern in REQUIRED_SECTIONS
        if not re.search(pattern, text, re.MULTILINE)
    )
    if "ISO/IEC/IEEE 29148" not in text:
        errors.append("no reference to 'ISO/IEC/IEEE 29148' found in the document")
    return errors


def check_requirement_fields(rid: str, kind: str, body: str) -> CheckResult:
    """Check one requirement block's fields and description quality.

    Args:
        rid: Requirement id, e.g. "FR-001".
        kind: Requirement kind parsed from the id (FR, NFR, UR, PR, DBR, INT).
        body: Block text between this requirement's heading and the next.

    Returns:
        Tuple of (errors, warnings) found in this block. FR/NFR blocks are
        checked for Priority/Verification Method fields; every block's first
        description line is checked for non-Singular ("and") phrasing and
        vague terms.
    """
    errors: list[str] = []
    warnings: list[str] = []

    fields = {m.group(1): m.group(2).strip() for m in FIELD_LINE_RE.finditer(body)}
    # why: template only lists Priority/Verification Method fields under
    # §3.2 Functional Requirements; UR/PR/DBR/INT sections (§3.3-3.5) are
    # prose-only, so enforcing those fields there would false-positive.
    if kind in ("FR", "NFR"):
        if "Priority" not in fields:
            errors.append(f"{rid}: missing '**Priority:**' field")
        elif fields["Priority"].lower() not in VALID_PRIORITY:
            errors.append(
                f"{rid}: invalid Priority value {fields['Priority']!r} "
                "(want High/Medium/Low)"
            )
        if "Verification Method" not in fields:
            errors.append(f"{rid}: missing '**Verification Method:**' field")
        elif fields["Verification Method"].lower() not in VALID_VERIFICATION:
            errors.append(
                f"{rid}: invalid Verification Method "
                f"{fields['Verification Method']!r} "
                "(want Inspection/Analysis/Demonstration/Test)"
            )

    first_line = body.strip().splitlines()[0] if body.strip() else ""
    if re.search(r"\band\b", first_line, re.IGNORECASE):
        warnings.append(
            f"{rid}: description contains ' and ' (possible non-Singular requirement)"
        )
    warnings.extend(
        f"{rid}: possibly ambiguous term {term!r} in description"
        for term in VAGUE_TERMS
        if re.search(rf"\b{re.escape(term)}\b", first_line, re.IGNORECASE)
    )

    return errors, warnings


def check_requirements(text: str) -> CheckResult:
    """Check requirement id uniqueness, per-block fields, and minimum counts.

    Args:
        text: Full SRS document source.

    Returns:
        Tuple of (errors, warnings) aggregated across every requirement
        block plus the document-wide minimum-count rules (>=3 FR, >=1 UR,
        >=1 PR).
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()
    counts = {"FR": 0, "NFR": 0, "UR": 0, "PR": 0, "DBR": 0, "INT": 0}

    for rid, kind, body in find_requirement_blocks(text):
        counts[kind] = counts.get(kind, 0) + 1
        if rid in seen_ids:
            errors.append(f"duplicate requirement id: {rid}")
        seen_ids.add(rid)

        block_errors, block_warnings = check_requirement_fields(rid, kind, body)
        errors.extend(block_errors)
        warnings.extend(block_warnings)

    if counts["FR"] == 0:
        errors.append("no functional requirement (FR-XXX) found")
    if counts["FR"] < 3:
        errors.append(f"fewer than 3 functional requirements found ({counts['FR']})")
    if counts["UR"] < 1:
        errors.append("no usability requirement (UR-XXX) found")
    if counts["PR"] < 1:
        errors.append("no performance requirement (PR-XXX) found")

    return errors, warnings


def check_gaps(text: str) -> list[str]:
    """Warn about outstanding 'To be defined' gap markers.

    Args:
        text: Full SRS document source.

    Returns:
        A single warning naming the gap-marker count, or an empty list if
        none are present.
    """
    gap_count = len(re.findall(r"To be defined", text))
    if not gap_count:
        return []
    return [f"{gap_count} 'To be defined' gap marker(s) present - review before saving"]


def check(path: str) -> CheckResult:
    """Run every check against the SRS document at `path`.

    Args:
        path: Filesystem path to the generated SRS markdown file.

    Returns:
        Tuple of (errors, warnings) collected from the structure, header,
        requirement, and gap-marker checks.

    Raises:
        OSError: If `path` cannot be opened for reading.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()

    errors = check_structure(text)
    warnings: list[str] = []

    req_errors, req_warnings = check_requirements(text)
    errors.extend(req_errors)
    warnings.extend(req_warnings)
    warnings.extend(check_gaps(text))

    return errors, warnings


def default_target() -> str | None:
    """Find the most recently named SRS file under docs/srs/.

    Returns:
        Path to the lexicographically-last docs/srs/*.md file (filenames
        are timestamp-prefixed, so this is the newest), or None if the
        directory has no matching file.
    """
    candidates = sorted(glob.glob("docs/srs/*.md"), reverse=True)
    return candidates[0] if candidates else None


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the checks, print results, and return an exit code.

    Args:
        argv: Command-line arguments to parse, excluding the program name.
            Defaults to `sys.argv[1:]` when None.

    Returns:
        0 if the target passed (no errors, and no warnings under --strict),
        1 if errors were found (or warnings under --strict), 2 on usage
        error (no resolvable target, or target file not found).
    """
    parser = argparse.ArgumentParser(
        prog="validate_srs.py",
        description="Deterministic checks for an srs-generator output.",
    )
    parser.add_argument("target", nargs="?", default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    path = args.target or default_target()
    if path is None:
        print(  # noqa: T201 -- CLI diagnostic output, not debug leftover
            "validate_srs: no target given and no file under docs/srs/*.md found",
            file=sys.stderr,
        )
        return 2
    if os.path.isdir(path):
        found = sorted(glob.glob(os.path.join(path, "*.md")), reverse=True)
        path = found[0] if found else path
    if not os.path.isfile(path):
        print(f"validate_srs: file not found: {path}", file=sys.stderr)  # noqa: T201
        return 2

    errors, warnings = check(path)
    for warning in warnings:
        print(f"  WARN  {warning}")  # noqa: T201
    for error in errors:
        print(f"  ERROR {error}")  # noqa: T201
    fail = bool(errors) or (bool(warnings) and args.strict)
    print(  # noqa: T201
        f"\nvalidate_srs: {len(errors)} error(s), {len(warnings)} warning(s) in {path}"
    )
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
