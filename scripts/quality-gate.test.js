"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const {
  MissingDependencyError,
  MalformedBaselineError,
  collectLintViolations,
  collectDuplicationPercent,
  collectCoveragePercent,
  collectLargeFiles,
  collectMetrics,
  readBaseline,
  writeBaseline,
  ensureBaseline,
  compareToBaseline,
  renderReport,
  parseArgs,
  run
} = require("./quality-gate");

function makeTempProject() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "qg-test-"));
}

test("collectLintViolations sums errorCount and warningCount across files (FR-001)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([
      { errorCount: 2, warningCount: 1 },
      { errorCount: 0, warningCount: 3 }
    ])
  );
  assert.equal(collectLintViolations(root), 6);
});

test("collectLintViolations throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () => collectLintViolations(root),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("eslint-report.json")
  );
});

test("collectDuplicationPercent reads statistics.total.percentage (FR-001)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 4.2 } } })
  );
  assert.equal(collectDuplicationPercent(root), 4.2);
});

test("collectDuplicationPercent throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () => collectDuplicationPercent(root),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("jscpd-report.json")
  );
});

test("collectCoveragePercent reads total.lines.pct (FR-001)", () => {
  const root = makeTempProject();
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 87.5 } } })
  );
  assert.equal(collectCoveragePercent(root), 87.5);
});

test("collectCoveragePercent throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () => collectCoveragePercent(root),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("coverage-summary.json")
  );
});

test("collectLargeFiles lists files exceeding maxLines with relative path and line count (FR-001)", () => {
  const root = makeTempProject();
  fs.writeFileSync(path.join(root, "big.js"), Array(10).fill("x").join("\n"));
  fs.writeFileSync(path.join(root, "small.js"), "x");
  fs.mkdirSync(path.join(root, "node_modules"));
  fs.writeFileSync(
    path.join(root, "node_modules", "ignored.js"),
    Array(50).fill("x").join("\n")
  );

  const large = collectLargeFiles(root, 5);
  assert.deepEqual(large, [{ path: "big.js", lines: 10 }]);
});

test("collectLargeFiles returns empty list when nothing exceeds the limit (edge case)", () => {
  const root = makeTempProject();
  fs.writeFileSync(path.join(root, "small.js"), "x");
  assert.deepEqual(collectLargeFiles(root, 500), []);
});

test("collectMetrics aggregates all four metrics in one object (FR-001)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([{ errorCount: 1, warningCount: 0 }])
  );
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 2 } } })
  );
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 90 } } })
  );

  const metrics = collectMetrics(root, { maxLines: 500 });
  assert.deepEqual(metrics, {
    lintViolations: 1,
    duplicationPercent: 2,
    coveragePercent: 90,
    largeFiles: []
  });
});

test("ensureBaseline bootstraps baseline.json from current metrics when file absent (FR-003)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  const metrics = {
    lintViolations: 3,
    duplicationPercent: 1.5,
    coveragePercent: 92,
    largeFiles: [{ path: "a.js", lines: 10 }]
  };

  const result = ensureBaseline(baselinePath, metrics);

  assert.equal(result.bootstrapped, true);
  const written = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
  assert.deepEqual(written, {
    lintViolations: 3,
    duplicationPercent: 1.5,
    coveragePercent: 92,
    largeFilesCount: 1
  });
});

test("ensureBaseline does not bootstrap when baseline.json already exists (FR-005)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  const existing = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFilesCount: 0
  };
  fs.writeFileSync(baselinePath, JSON.stringify(existing));

  const result = ensureBaseline(baselinePath, {
    lintViolations: 9,
    duplicationPercent: 9,
    coveragePercent: 1,
    largeFiles: []
  });

  assert.equal(result.bootstrapped, false);
  assert.deepEqual(result.baseline, existing);
  assert.deepEqual(JSON.parse(fs.readFileSync(baselinePath, "utf8")), existing);
});

test("readBaseline throws MalformedBaselineError on invalid JSON without overwriting the file (FR-004)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(baselinePath, "{ not valid json");

  assert.throws(() => readBaseline(baselinePath), MalformedBaselineError);
  assert.equal(fs.readFileSync(baselinePath, "utf8"), "{ not valid json");
});

test("readBaseline throws MalformedBaselineError naming the missing field (FR-004)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(
    baselinePath,
    JSON.stringify({
      lintViolations: 0,
      duplicationPercent: 0,
      coveragePercent: 100
    })
  );

  assert.throws(
    () => readBaseline(baselinePath),
    (err) =>
      err instanceof MalformedBaselineError &&
      err.message.includes("largeFilesCount")
  );
});

test("writeBaseline always overwrites regardless of prior content (--update-baseline path)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(
    baselinePath,
    JSON.stringify({
      lintViolations: 99,
      duplicationPercent: 99,
      coveragePercent: 0,
      largeFilesCount: 99
    })
  );

  writeBaseline(baselinePath, {
    lintViolations: 1,
    duplicationPercent: 1,
    coveragePercent: 100,
    largeFiles: []
  });

  assert.deepEqual(JSON.parse(fs.readFileSync(baselinePath, "utf8")), {
    lintViolations: 1,
    duplicationPercent: 1,
    coveragePercent: 100,
    largeFilesCount: 0
  });
});

test("compareToBaseline fails when lintViolations regresses by even 1 unit (FR-007)", () => {
  const baseline = {
    lintViolations: 5,
    duplicationPercent: 2,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 6,
    duplicationPercent: 2,
    coveragePercent: 90,
    largeFiles: []
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.deepEqual(result.fields.lintViolations, {
    ok: false,
    baselineValue: 5,
    currentValue: 6,
    delta: 1
  });
});

test("compareToBaseline fails when coveragePercent regresses by 0.1 (FR-007)", () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 89.9,
    largeFiles: []
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.equal(result.fields.coveragePercent.ok, false);
  assert.equal(result.fields.coveragePercent.baselineValue, 90);
  assert.equal(result.fields.coveragePercent.currentValue, 89.9);
  assert.ok(result.fields.coveragePercent.delta < 0);
});

test("compareToBaseline passes when all metrics equal the baseline (FR-008)", () => {
  const baseline = {
    lintViolations: 3,
    duplicationPercent: 1,
    coveragePercent: 95,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 3,
    duplicationPercent: 1,
    coveragePercent: 95,
    largeFiles: []
  };

  assert.equal(compareToBaseline(baseline, metrics).passed, true);
});

test("compareToBaseline passes when all metrics improve on the baseline (FR-008)", () => {
  const baseline = {
    lintViolations: 5,
    duplicationPercent: 5,
    coveragePercent: 80,
    largeFilesCount: 2
  };
  const metrics = {
    lintViolations: 2,
    duplicationPercent: 1,
    coveragePercent: 95,
    largeFiles: []
  };

  assert.equal(compareToBaseline(baseline, metrics).passed, true);
});

test("compareToBaseline treats fewer large files as an improvement, more as a regression (FR-007/FR-008)", () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFilesCount: 1
  };
  const worse = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFiles: [
      { path: "a.js", lines: 1 },
      { path: "b.js", lines: 1 }
    ]
  };

  assert.equal(compareToBaseline(baseline, worse).passed, false);
});

test("renderReport includes current-metrics table and baseline table (FR-009)", () => {
  const baseline = {
    lintViolations: 2,
    duplicationPercent: 1,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 2,
    duplicationPercent: 1,
    coveragePercent: 90,
    largeFiles: []
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /\| Metric \| Current \| Baseline \|/);
  assert.match(report, /\| Lint violations \| 2 \| 2 \|/);
});

test("renderReport lists each failing metric with baseline, current, and delta (FR-010)", () => {
  const baseline = {
    lintViolations: 2,
    duplicationPercent: 1,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 5,
    duplicationPercent: 1,
    coveragePercent: 90,
    largeFiles: []
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /\| Lint violations \| 2 \| 5 \| 3 \|/);
});

test('renderReport shows "None." for failures when nothing regressed (FR-009)', () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFiles: []
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /## Failures\n\nNone\./);
});

test('renderReport shows large files section explicitly as "None." when empty (FR-012)', () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFiles: []
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /## Files over the line limit\n\nNone\./);
});

test("renderReport lists each large file with its line count when present (FR-001)", () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 0,
    coveragePercent: 100,
    largeFiles: [{ path: "big.js", lines: 900 }]
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /- big\.js \(900 lines\)/);
});

test("parseArgs applies defaults and respects --max-lines, --baseline-path, --report-path, --root (FR-011)", () => {
  const options = parseArgs([
    "--root",
    "/proj",
    "--max-lines",
    "300",
    "--baseline-path",
    "b.json",
    "--report-path",
    "r.md"
  ]);
  assert.deepEqual(options, {
    root: "/proj",
    maxLines: 300,
    updateBaseline: false,
    baselinePath: "b.json",
    reportPath: "r.md"
  });
});

test("parseArgs sets updateBaseline true when --update-baseline is present (FR-006)", () => {
  assert.equal(parseArgs(["--update-baseline"]).updateBaseline, true);
});

test("run bootstraps baseline on first execution and exits 0 without prompting (FR-003, FR-014)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([{ errorCount: 0, warningCount: 0 }])
  );
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 0 } } })
  );
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 100 } } })
  );

  const messages = [];
  const exitCode = run(["--root", root], (msg) => messages.push(msg));

  assert.equal(exitCode, 0);
  assert.ok(fs.existsSync(path.join(root, "baseline.json")));
  assert.ok(messages.some((m) => m.includes("created")));
});

test("run exits 1 and writes the report when a metric regresses (FR-007, FR-011)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "baseline.json"),
    JSON.stringify({
      lintViolations: 0,
      duplicationPercent: 0,
      coveragePercent: 100,
      largeFilesCount: 0
    })
  );
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([{ errorCount: 1, warningCount: 0 }])
  );
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 0 } } })
  );
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 100 } } })
  );

  const exitCode = run(["--root", root, "--report-path", "out.md"], () => {});

  assert.equal(exitCode, 1);
  assert.ok(fs.existsSync(path.join(root, "out.md")));
});

test("run exits 0 when metrics match the baseline exactly (FR-008)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "baseline.json"),
    JSON.stringify({
      lintViolations: 0,
      duplicationPercent: 0,
      coveragePercent: 100,
      largeFilesCount: 0
    })
  );
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([{ errorCount: 0, warningCount: 0 }])
  );
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 0 } } })
  );
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 100 } } })
  );

  assert.equal(
    run(["--root", root], () => {}),
    0
  );
});

test("run with --update-baseline overwrites baseline.json and exits 0 regardless of regression (FR-006)", () => {
  const root = makeTempProject();
  fs.writeFileSync(
    path.join(root, "baseline.json"),
    JSON.stringify({
      lintViolations: 0,
      duplicationPercent: 0,
      coveragePercent: 100,
      largeFilesCount: 0
    })
  );
  fs.writeFileSync(
    path.join(root, "eslint-report.json"),
    JSON.stringify([{ errorCount: 5, warningCount: 0 }])
  );
  fs.writeFileSync(
    path.join(root, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage: 0 } } })
  );
  fs.mkdirSync(path.join(root, "coverage"));
  fs.writeFileSync(
    path.join(root, "coverage", "coverage-summary.json"),
    JSON.stringify({ total: { lines: { pct: 100 } } })
  );

  const exitCode = run(["--root", root, "--update-baseline"], () => {});

  assert.equal(exitCode, 0);
  assert.equal(
    JSON.parse(fs.readFileSync(path.join(root, "baseline.json"), "utf8"))
      .lintViolations,
    5
  );
});

test("run exits 1 with a clear message when a required dependency is missing, no crash (FR-002)", () => {
  const root = makeTempProject();
  const messages = [];

  const exitCode = run(["--root", root], (msg) => messages.push(msg));

  assert.equal(exitCode, 1);
  assert.ok(messages[0].includes("eslint-report.json"));
});

test("compareToBaseline fails when duplicationPercent regresses (higher is worse) (FR-007)", () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 2,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 3,
    coveragePercent: 90,
    largeFiles: []
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.deepEqual(result.fields.duplicationPercent, {
    ok: false,
    baselineValue: 2,
    currentValue: 3,
    delta: 1
  });
});

test("compareToBaseline passes when duplicationPercent improves (lower is better) (FR-008)", () => {
  const baseline = {
    lintViolations: 0,
    duplicationPercent: 5,
    coveragePercent: 90,
    largeFilesCount: 0
  };
  const metrics = {
    lintViolations: 0,
    duplicationPercent: 2,
    coveragePercent: 90,
    largeFiles: []
  };

  assert.equal(compareToBaseline(baseline, metrics).passed, true);
});
