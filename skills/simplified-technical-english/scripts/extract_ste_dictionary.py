#!/usr/bin/env python3
"""Extract the ASD-STE100 dictionary (Part 2) into structured JSON/CSV.

Usage:
    python3 extract_ste_dictionary.py <pdf_path> [--start PAGE] [--end PAGE] [--out OUT_PREFIX]

Page numbers are 1-indexed and inclusive, matching what you see in a PDF viewer.
Default range covers Part 2 - Dictionary (pages 103-382 in ASD-STE100 Issue 7).
"""

import argparse
import json
import re
import sys

import pdfplumber

# x0 column bands, calibrated against ASD-STE100 Issue 7 dictionary table layout
COLUMNS = [
    ("word", 40, 150),
    ("meaning_alt", 150, 306),
    ("approved_example", 308, 437),
    ("not_approved", 438, 610),
]
HEADER_TOP_CUTOFF = 85  # skip the repeated column-header row on each page
FOOTER_TOP_CUTOFF = 715  # skip the repeated "Issue 7 / date / page code" footer


def col_of(x0: float):
    for name, a, b in COLUMNS:
        if a <= x0 < b:
            return name
    return None


def extract_rows(page):
    """Group words on a page into text rows per column band."""
    words = page.extract_words()
    rows: dict[int, dict[str, list[str]]] = {}
    for w in words:
        if w["top"] < HEADER_TOP_CUTOFF or w["top"] > FOOTER_TOP_CUTOFF:
            continue
        top = round(w["top"])
        c = col_of(w["x0"])
        if c is None:
            continue
        rows.setdefault(top, {}).setdefault(c, []).append(w["text"])

    lines = []
    for top in sorted(rows):
        cells = rows[top]
        lines.append({name: " ".join(cells.get(name, [])) for name, _, _ in COLUMNS})
    return lines


WORD_RE = re.compile(r"^([A-Za-z][A-Za-z \-']*?)\s*\(([a-z]+)\)$")
ALT_HEADER_RE = re.compile(r"^[A-Z][A-Z \-']*\s*\([a-z]+\)$")


def is_new_alt_line(meaning_alt: str) -> bool:
    """True when a meaning_alt cell looks like a fresh alternative header,
    e.g. 'APPROXIMATELY (adv)' or 'AROUND (prep)', vs. a wrapped continuation
    line of the previous alternative's free-text meaning."""
    return bool(ALT_HEADER_RE.match(meaning_alt.strip()))


def is_new_entry_line(line):
    """A line starts a new dictionary entry if its 'word' cell is non-empty."""
    return bool(line["word"].strip())


def build_entries(lines):
    """Merge multi-line table rows into logical dictionary entries.

    Each entry may have several approved alternatives (several sub-rows sharing
    the same headword), so an entry is a word plus a list of alternative rows.
    """
    entries = []
    current = None
    current_alt = None

    def flush_alt():
        nonlocal current_alt
        if current is not None and current_alt is not None:
            if (
                current_alt["meaning_alt"]
                or current_alt["approved_example"]
                or current_alt["not_approved"]
            ):
                current["alternatives"].append(current_alt)
        current_alt = None

    for line in lines:
        if is_new_entry_line(line):
            # New headword -> close out previous entry entirely
            flush_alt()
            if current is not None:
                entries.append(current)

            word = line["word"].strip()
            current = {"word_raw": word, "alternatives": []}
            current_alt = {
                "meaning_alt": line["meaning_alt"].strip(),
                "approved_example": line["approved_example"].strip(),
                "not_approved": line["not_approved"].strip(),
            }
        else:
            if current is None:
                continue  # stray line before first entry (shouldn't happen past header)

            if is_new_alt_line(line["meaning_alt"]):
                flush_alt()
                current_alt = {
                    "meaning_alt": line["meaning_alt"].strip(),
                    "approved_example": line["approved_example"].strip(),
                    "not_approved": line["not_approved"].strip(),
                }
            else:
                if line["meaning_alt"].strip():
                    current_alt["meaning_alt"] = (
                        current_alt["meaning_alt"] + " " + line["meaning_alt"].strip()
                    ).strip()
                if line["approved_example"].strip():
                    current_alt["approved_example"] = (
                        current_alt["approved_example"]
                        + " "
                        + line["approved_example"].strip()
                    ).strip()
                if line["not_approved"].strip():
                    current_alt["not_approved"] = (
                        current_alt["not_approved"] + " " + line["not_approved"].strip()
                    ).strip()

    flush_alt()
    if current is not None:
        entries.append(current)
    return entries


def parse_word_raw(word_raw):
    """Split 'abaft (prep)' -> ('abaft', 'prep'); handle verb-form lists too."""
    m = WORD_RE.match(word_raw)
    if m:
        headword, pos = m.group(1).strip(), m.group(2)
    else:
        headword, pos = word_raw, ""
    approved = headword == headword.upper() and any(ch.isalpha() for ch in headword)
    return headword, pos, approved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf_path")
    ap.add_argument(
        "--start", type=int, default=103, help="1-indexed first page of dictionary"
    )
    ap.add_argument(
        "--end", type=int, default=382, help="1-indexed last page of dictionary"
    )
    ap.add_argument("--out", default="ste_dictionary", help="output file prefix")
    args = ap.parse_args()

    all_entries = []
    with pdfplumber.open(args.pdf_path) as pdf:
        total = len(pdf.pages)
        end = min(args.end, total)
        for i in range(args.start - 1, end):
            page = pdf.pages[i]
            lines = extract_rows(page)
            entries = build_entries(lines)
            for e in entries:
                headword, pos, approved = parse_word_raw(e["word_raw"])
                all_entries.append(
                    {
                        "word": headword,
                        "pos": pos,
                        "approved": approved,
                        "page": i + 1,
                        "alternatives": e["alternatives"],
                    }
                )
            print(f"page {i + 1}/{end}: {len(entries)} entries", file=sys.stderr)

    with open(f"{args.out}.json", "w") as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)

    print(
        f"Done. {len(all_entries)} entries -> {args.out}.json / {args.out}.csv",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
