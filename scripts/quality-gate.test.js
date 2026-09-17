"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const {
  MissingDependencyError,
  collectLintViolations,
  collectDuplicationPercent,
  collectCoveragePercent,
  collectLargeFiles,
  collectMetrics
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
