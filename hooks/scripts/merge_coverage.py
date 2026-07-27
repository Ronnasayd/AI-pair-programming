#!/usr/bin/python3
"""Merge a partial Istanbul coverage run into a project's coverage dir.

Replaces nyc merge/report: merges coverage-final.json (sum s/f/b counters,
keep statementMap/fnMap/branchMap from whichever side has them), recomputes
coverage-summary.json from the merged final json, and swaps in the updated
per-file HTML page(s) from the partial run's lcov-report.
"""

import json
import shutil
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


def _pct(covered: int, total: int) -> float:
    if total == 0:
        return 100
    return round((covered / total) * 10000) / 100


def _line_hits(file_coverage: dict) -> dict:
    """Collapse statement hits onto their starting line (istanbul's 'lines' metric)."""
    statement_map = file_coverage.get("statementMap", {})
    statement_hits = file_coverage.get("s", {})
    line_hits: dict[int, int] = {}
    for stmt_id, loc in statement_map.items():
        line = loc["start"]["line"]
        hits = statement_hits.get(stmt_id, 0)
        line_hits[line] = max(line_hits.get(line, 0), hits)
    return line_hits


def _file_summary(file_coverage: dict) -> dict:
    line_hits = _line_hits(file_coverage)
    lines_total = len(line_hits)
    lines_covered = sum(1 for hits in line_hits.values() if hits > 0)

    statement_hits = file_coverage.get("s", {})
    statements_total = len(statement_hits)
    statements_covered = sum(1 for hits in statement_hits.values() if hits > 0)

    fn_hits = file_coverage.get("f", {})
    functions_total = len(fn_hits)
    functions_covered = sum(1 for hits in fn_hits.values() if hits > 0)

    branch_hits = file_coverage.get("b", {})
    branches_total = sum(len(counts) for counts in branch_hits.values())
    branches_covered = sum(
        sum(1 for hit in counts if hit > 0) for counts in branch_hits.values()
    )

    return {
        "lines": {
            "total": lines_total,
            "covered": lines_covered,
            "skipped": 0,
            "pct": _pct(lines_covered, lines_total),
        },
        "statements": {
            "total": statements_total,
            "covered": statements_covered,
            "skipped": 0,
            "pct": _pct(statements_covered, statements_total),
        },
        "functions": {
            "total": functions_total,
            "covered": functions_covered,
            "skipped": 0,
            "pct": _pct(functions_covered, functions_total),
        },
        "branches": {
            "total": branches_total,
            "covered": branches_covered,
            "skipped": 0,
            "pct": _pct(branches_covered, branches_total),
        },
    }


def build_summary(merged_final: dict) -> dict:
    summary = {}
    totals = {
        "lines": [0, 0],
        "statements": [0, 0],
        "functions": [0, 0],
        "branches": [0, 0],
    }
    for file_path, file_coverage in merged_final.items():
        file_summary = _file_summary(file_coverage)
        summary[file_path] = file_summary
        for metric, [total, covered] in totals.items():
            totals[metric] = [
                total + file_summary[metric]["total"],
                covered + file_summary[metric]["covered"],
            ]

    summary["total"] = {
        metric: {
            "total": total,
            "covered": covered,
            "skipped": 0,
            "pct": _pct(covered, total),
        }
        for metric, (total, covered) in totals.items()
    }
    return summary


def _copy_html_report(partial_dir: Path, coverage_dir: Path, rel_path: str) -> None:
    """Swap in the updated file's HTML page from the partial run's lcov-report.

    The partial run's report only covers one file, so istanbul flattens its
    lcov-report (no per-directory nesting) and names the page after the
    basename only, e.g. lcov-report/AuthorizeActionMiddleware.ts.html. The
    project's full coverage dir mirrors the source tree instead, e.g.
    lcov-report/src/.../AuthorizeActionMiddleware.ts.html.
    """
    basename = Path(rel_path).name
    src = partial_dir / "lcov-report" / f"{basename}.html"
    if not src.exists():
        return
    dst = coverage_dir / "lcov-report" / f"{rel_path}.html"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main() -> None:
    partial_dir = Path(sys.argv[1])
    coverage_dir = Path(sys.argv[2])
    rel_path = sys.argv[3] if len(sys.argv) > 3 else None
    coverage_dir.mkdir(parents=True, exist_ok=True)

    partial_file = partial_dir / "coverage-final.json"
    if not partial_file.exists():
        return

    partial = json.loads(partial_file.read_text())

    coverage_file = coverage_dir / "coverage-final.json"
    base = json.loads(coverage_file.read_text()) if coverage_file.exists() else {}

    merged = merge_coverage(base, partial)
    coverage_file.write_text(json.dumps(merged))

    summary_file = coverage_dir / "coverage-summary.json"
    summary_file.write_text(json.dumps(build_summary(merged), indent=2))

    if rel_path:
        _copy_html_report(partial_dir, coverage_dir, rel_path)


if __name__ == "__main__":
    main()
