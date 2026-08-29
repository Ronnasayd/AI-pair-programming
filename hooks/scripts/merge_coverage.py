#!/usr/bin/python3
"""Merge a partial Istanbul coverage run into a project's coverage dir.

Replaces nyc merge/report: merges coverage-final.json (sum s/f/b counters,
keep statementMap/fnMap/branchMap from whichever side has them) and swaps in
the updated per-file HTML page(s) from the partial run's lcov-report.

coverage-summary.json is NOT written here — jest_coverage_report.py builds it
on demand from coverage-final.json. Writing it from this background process
raced against that read (report could see a half-written file).
"""

import fcntl
import json
import os
import sys
from pathlib import Path


def _write_json_atomic(path: Path, data: object, **dump_kwargs) -> None:
    """Write via temp file + os.replace so concurrent readers never see a partial write."""
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(data, **dump_kwargs))
    os.replace(tmp, path)


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

    # Serialize the read-modify-write of coverage-final.json across all
    # concurrent per-file merges (each holds only its own per-file lock, so
    # without this two edits race and one merge is lost).
    merge_lock = coverage_dir / ".merge.lock"
    with open(merge_lock, "w") as lock_fh:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)
        base = json.loads(coverage_file.read_text()) if coverage_file.exists() else {}
        merged = merge_coverage(base, partial)
        _write_json_atomic(coverage_file, merged)


if __name__ == "__main__":
    main()
