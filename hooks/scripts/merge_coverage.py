#!/usr/bin/python3
"""Merge a partial Istanbul coverage-final.json into a project's coverage dir.

Replaces nyc merge/report: reads coverage-final.json from the partial dir,
merges per-file counters into the existing coverage-final.json (sum s/f/b
counters, keep statementMap/fnMap/branchMap from whichever side has them),
and writes the result back. No report generation.
"""

import json
import sys
from pathlib import Path


def _merge_counter_map(base: dict, partial: dict) -> dict:
    merged = dict(base)
    for key, value in partial.items():
        merged[key] = merged.get(key, 0) + value
    return merged


def _merge_branch_counter_map(base: dict, partial: dict) -> dict:
    merged = dict(base)
    for key, counts in partial.items():
        if key not in merged:
            merged[key] = list(counts)
            continue
        merged[key] = [a + b for a, b in zip(merged[key], counts)]
    return merged


def _merge_file_coverage(base: dict, partial: dict) -> dict:
    merged = dict(partial)
    merged["s"] = _merge_counter_map(base.get("s", {}), partial.get("s", {}))
    merged["f"] = _merge_counter_map(base.get("f", {}), partial.get("f", {}))
    merged["b"] = _merge_branch_counter_map(base.get("b", {}), partial.get("b", {}))
    return merged


def merge_coverage(base: dict, partial: dict) -> dict:
    merged = dict(base)
    for file_path, file_coverage in partial.items():
        if file_path in merged:
            merged[file_path] = _merge_file_coverage(merged[file_path], file_coverage)
        else:
            merged[file_path] = file_coverage
    return merged


def main() -> None:
    partial_dir = Path(sys.argv[1])
    coverage_dir = Path(sys.argv[2])
    coverage_dir.mkdir(parents=True, exist_ok=True)

    partial_file = partial_dir / "coverage-final.json"
    if not partial_file.exists():
        return

    partial = json.loads(partial_file.read_text())

    coverage_file = coverage_dir / "coverage-final.json"
    base = json.loads(coverage_file.read_text()) if coverage_file.exists() else {}

    merged = merge_coverage(base, partial)
    coverage_file.write_text(json.dumps(merged))


if __name__ == "__main__":
    main()
