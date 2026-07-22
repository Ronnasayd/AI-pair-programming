#!/usr/bin/env python3
"""Flag words in a text that are not approved by ASD-STE100 and suggest replacements.

Usage:
    python3 check_ste.py <text_file_or_->
    echo "some text" | python3 check_ste.py -

Looks up each word (case-insensitive) against reference/ste_dictionary.json.
Words not found in the dictionary are technical names/verbs candidates (not
flagged, since STE explicitly allows those - see grammar-rules.md Section 1)
or genuine unknowns; only words explicitly marked "not approved" are flagged.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DICT_PATH = Path(__file__).parent.parent / "reference" / "ste_dictionary.json"
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
ALT_HEADER_RE = re.compile(r"^[A-Z][A-Z \-']*\s*\([a-z]+\)")


def load_dictionary():
    entries = json.loads(DICT_PATH.read_text())
    lookup: dict[str, list[dict]] = {}
    for e in entries:
        lookup.setdefault(e["word"].lower(), []).append(e)
    return lookup


def suggest_replacements(entries: list[dict]) -> list[str]:
    seen = []
    for e in entries:
        for alt in e["alternatives"]:
            raw = alt["meaning_alt"].strip()
            m = ALT_HEADER_RE.match(raw)
            word = m.group(0) if m else raw
            if word and word not in seen:
                seen.append(word)
    return seen


def check_text(text: str, lookup: dict[str, list[dict]]) -> list[dict]:
    findings = []
    flagged_positions = set()
    for m in WORD_RE.finditer(text):
        word = m.group(0)
        key = word.lower()
        if key in flagged_positions:
            continue
        entries = lookup.get(key)
        if not entries:
            continue
        not_approved = [e for e in entries if not e["approved"]]
        if not_approved:
            flagged_positions.add(key)
            findings.append(
                {
                    "word": word,
                    "suggestions": suggest_replacements(not_approved),
                }
            )
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="path to a text file, or '-' for stdin")
    args = ap.parse_args()

    text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text()
    lookup = load_dictionary()
    findings = check_text(text, lookup)

    if not findings:
        print("No unapproved STE words found.")
        return

    print(f"{len(findings)} unapproved word(s) found:\n")
    for f in findings:
        suggestions = (
            ", ".join(f["suggestions"])
            if f["suggestions"]
            else "(no direct alternative listed)"
        )
        print(f"  {f['word']!r} -> {suggestions}")


if __name__ == "__main__":
    main()
