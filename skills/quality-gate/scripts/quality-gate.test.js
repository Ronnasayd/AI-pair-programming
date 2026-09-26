"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const {
  MissingDependencyError,
  MalformedBaselineError,
  resolveBin,
  collectEslintMetrics,
  collectDuplicationMetrics,
  collectCoverageMetrics,
  collectFileSizes,
  collectMetrics,
  readBaseline,
  writeBaseline,
  ensureBaseline,
  toBaselineRecord,
  compareToBaseline,
  renderReport,
  parseArgs,
  run
} = require("./quality-gate");

function makeTempProject() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "qg-test-"));
}

function writeEslintReport(dir, files) {
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "eslint-report.json"), JSON.stringify(files));
}

function writeJscpdReport(dir, { percentage, clones }) {
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(
    path.join(dir, "jscpd-report.json"),
    JSON.stringify({ statistics: { total: { percentage, clones } } })
  );
}

function writeCoverageSummary(dir, coverage) {
  fs.mkdirSync(path.join(dir, "coverage"), { recursive: true });
  fs.writeFileSync(
    path.join(dir, "coverage", "coverage-summary.json"),
    JSON.stringify({
      total: {
        lines: { pct: coverage.lines },
        statements: { pct: coverage.statements },
        functions: { pct: coverage.functions },
        branches: { pct: coverage.branches }
      }
    })
  );
}

function seedAllReports(dir) {
  writeEslintReport(dir, [
    {
      filePath: path.join(dir, "a.js"),
      errorCount: 0,
      warningCount: 0,
      messages: []
    }
  ]);
  writeJscpdReport(dir, { percentage: 0, clones: 0 });
  writeCoverageSummary(dir, {
    lines: 100,
    statements: 100,
    functions: 100,
    branches: 100
  });
}

test("resolveBin returns the quoted local node_modules/.bin path when it exists (FR-001b)", () => {
  const root = makeTempProject();
  fs.mkdirSync(path.join(root, "node_modules", ".bin"), { recursive: true });
  fs.writeFileSync(
    path.join(root, "node_modules", ".bin", "eslint"),
    "#!/bin/sh\n"
  );

  assert.equal(
    resolveBin("eslint", root),
    JSON.stringify(path.join(root, "node_modules", ".bin", "eslint"))
  );
});

test("resolveBin falls back to npx when no local bin exists (FR-001b)", () => {
  const root = makeTempProject();
  assert.equal(resolveBin("eslint", root), "npx eslint");
});

test("collectEslintMetrics aggregates total, byRule, byComplexityRule, and perFile (FR-001)", () => {
  const root = makeTempProject();
  writeEslintReport(root, [
    {
      filePath: path.join(root, "a.js"),
      errorCount: 2,
      warningCount: 1,
      messages: [
        { ruleId: "max-depth" },
        { ruleId: "max-depth" },
        { ruleId: "no-console" }
      ]
    },
    {
      filePath: path.join(root, "b.js"),
      errorCount: 0,
      warningCount: 1,
      messages: [{ ruleId: "no-console" }]
    }
  ]);

  const metrics = collectEslintMetrics(
    path.join(root, "eslint-report.json"),
    root
  );

  assert.equal(metrics.total, 4);
  assert.deepEqual(metrics.byRule, { "max-depth": 2, "no-console": 2 });
  assert.equal(metrics.byComplexityRule["max-depth"], 2);
  assert.equal(metrics.byComplexityRule.complexity, 0);
  assert.deepEqual(metrics.perFile["a.js"].byRule, {
    "max-depth": 2,
    "no-console": 1
  });
  assert.deepEqual(metrics.perFile["b.js"].byRule, { "no-console": 1 });
});

test("collectEslintMetrics throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () => collectEslintMetrics(path.join(root, "eslint-report.json"), root),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("eslint-report.json")
  );
});

test("collectDuplicationMetrics reads percentage and clones as fragments (FR-001)", () => {
  const root = makeTempProject();
  writeJscpdReport(root, { percentage: 4.2, clones: 3 });
  const metrics = collectDuplicationMetrics(
    path.join(root, "jscpd-report.json")
  );
  assert.deepEqual(metrics, { percentage: 4.2, fragments: 3 });
});

test("collectDuplicationMetrics throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () => collectDuplicationMetrics(path.join(root, "jscpd-report.json")),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("jscpd-report.json")
  );
});

test("collectCoverageMetrics reads all four coverage kinds (FR-001)", () => {
  const root = makeTempProject();
  writeCoverageSummary(root, {
    lines: 87.5,
    statements: 80,
    functions: 90,
    branches: 60
  });
  const metrics = collectCoverageMetrics(
    path.join(root, "coverage", "coverage-summary.json")
  );
  assert.deepEqual(metrics, {
    lines: 87.5,
    statements: 80,
    functions: 90,
    branches: 60
  });
});

test("collectCoverageMetrics throws MissingDependencyError naming the missing file (FR-002)", () => {
  const root = makeTempProject();
  assert.throws(
    () =>
      collectCoverageMetrics(
        path.join(root, "coverage", "coverage-summary.json")
      ),
    (err) =>
      err instanceof MissingDependencyError &&
      err.missingPath.endsWith("coverage-summary.json")
  );
});

test("collectFileSizes returns lines and bytes for every source file, not just oversized ones (edge case)", () => {
  const root = makeTempProject();
  fs.writeFileSync(path.join(root, "big.js"), Array(10).fill("x").join("\n"));
  fs.writeFileSync(path.join(root, "small.js"), "x");
  fs.mkdirSync(path.join(root, "node_modules"));
  fs.writeFileSync(
    path.join(root, "node_modules", "ignored.js"),
    Array(50).fill("x").join("\n")
  );

  const sizes = collectFileSizes(root);
  const byPath = Object.fromEntries(sizes.map((f) => [f.path, f]));
  assert.equal(byPath["big.js"].lines, 10);
  assert.ok(byPath["small.js"]);
  assert.equal(byPath["node_modules/ignored.js"], undefined);
});

test("collectMetrics reads pre-generated reports without auto-running when they already exist (FR-001)", () => {
  const root = makeTempProject();
  seedAllReports(root);

  const metrics = collectMetrics(root, {
    maxLines: 500,
    eslintReportPath: path.join(root, "eslint-report.json"),
    jscpdReportPath: path.join(root, "jscpd-report.json"),
    coverageSummaryPath: path.join(root, "coverage", "coverage-summary.json"),
    autoRun: true
  });

  assert.equal(metrics.eslint.total, 0);
  assert.equal(metrics.duplication.percentage, 0);
  assert.equal(metrics.coverage.lines, 100);
});

test("collectMetrics fails with MissingDependencyError when autoRun is false and reports are absent", () => {
  const root = makeTempProject();
  assert.throws(
    () =>
      collectMetrics(root, {
        maxLines: 500,
        eslintReportPath: path.join(root, "eslint-report.json"),
        jscpdReportPath: path.join(root, "jscpd-report.json"),
        coverageSummaryPath: path.join(
          root,
          "coverage",
          "coverage-summary.json"
        ),
        autoRun: false
      }),
    MissingDependencyError
  );
});

test("ensureBaseline bootstraps nested baseline.json from current metrics when file absent (FR-003)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  const metrics = {
    coverage: { lines: 90, statements: 85, functions: 88, branches: 70 },
    duplication: { percentage: 1.5, fragments: 2 },
    eslint: {
      total: 3,
      byRule: { "no-console": 3 },
      byComplexityRule: { complexity: 0 },
      perFile: {}
    },
    files: [{ path: "a.js", lines: 600, bytes: 100 }],
    maxLines: 500
  };

  const result = ensureBaseline(baselinePath, metrics);

  assert.equal(result.bootstrapped, true);
  const written = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
  assert.deepEqual(written.coverage, metrics.coverage);
  assert.deepEqual(written.duplication, metrics.duplication);
  assert.equal(written.eslint.total, 3);
  assert.deepEqual(written.files, { "a.js": { lines: 600, bytes: 100 } });
});

test("ensureBaseline does not bootstrap when baseline.json already exists (FR-005)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  const existing = toBaselineRecord({
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  fs.writeFileSync(baselinePath, JSON.stringify(existing));

  const result = ensureBaseline(baselinePath, {
    coverage: { lines: 1, statements: 1, functions: 1, branches: 1 },
    duplication: { percentage: 9, fragments: 9 },
    eslint: { total: 9, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });

  assert.equal(result.bootstrapped, false);
  assert.deepEqual(result.baseline, existing);
});

test("readBaseline throws MalformedBaselineError on invalid JSON without overwriting the file (FR-004)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(baselinePath, "{ not valid json");

  assert.throws(() => readBaseline(baselinePath), MalformedBaselineError);
  assert.equal(fs.readFileSync(baselinePath, "utf8"), "{ not valid json");
});

test("readBaseline throws MalformedBaselineError naming a missing nested field (FR-004)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(
    baselinePath,
    JSON.stringify({
      coverage: { lines: 0, statements: 0, functions: 0 },
      duplication: { percentage: 0, fragments: 0 },
      eslint: { total: 0, byComplexityRule: {} },
      files: {},
      perFileByComplexityRule: {}
    })
  );

  assert.throws(
    () => readBaseline(baselinePath),
    (err) =>
      err instanceof MalformedBaselineError &&
      err.message.includes("coverage.branches")
  );
});

test("readBaseline throws MalformedBaselineError for an old flat-shape baseline (backward-incompat note)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(
    baselinePath,
    JSON.stringify({
      lintViolations: 0,
      duplicationPercent: 0,
      coveragePercent: 100,
      largeFilesCount: 0
    })
  );

  assert.throws(() => readBaseline(baselinePath), MalformedBaselineError);
});

test("writeBaseline always overwrites regardless of prior content (--update-baseline path)", () => {
  const root = makeTempProject();
  const baselinePath = path.join(root, "baseline.json");
  fs.writeFileSync(baselinePath, JSON.stringify({ garbage: true }));

  writeBaseline(baselinePath, {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });

  const written = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
  assert.equal(written.coverage.lines, 100);
  assert.equal(written.eslint.total, 0);
});

test("compareToBaseline fails when a coverage field regresses by 0.1 (FR-007)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 90, statements: 90, functions: 90, branches: 90 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 89.9, statements: 90, functions: 90, branches: 90 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.equal(result.fields["coverage.lines"].ok, false);
  assert.ok(result.fields["coverage.lines"].delta < 0);
});

test("compareToBaseline fails when eslint total or a complexity rule regresses (FR-007)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: {
      total: 5,
      byRule: {},
      byComplexityRule: { "max-depth": 1 },
      perFile: {}
    },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: {
      total: 6,
      byRule: {},
      byComplexityRule: { "max-depth": 2 },
      perFile: {}
    },
    files: [],
    maxLines: 500
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.equal(result.fields["eslint.total"].ok, false);
  assert.equal(result.fields["eslint.byComplexityRule.max-depth"].ok, false);
});

test("compareToBaseline passes when all metrics equal or improve (FR-008)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 90, statements: 90, functions: 90, branches: 90 },
    duplication: { percentage: 5, fragments: 5 },
    eslint: { total: 5, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 95, statements: 92, functions: 91, branches: 90 },
    duplication: { percentage: 1, fragments: 1 },
    eslint: { total: 2, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  };

  assert.equal(compareToBaseline(baseline, metrics).passed, true);
});

test("compareToBaseline reports a lines/bytes regression for a file already over the limit (video 'Regressions' behavior)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [{ path: "big.js", lines: 1008, bytes: 36385 }],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [{ path: "big.js", lines: 1140, bytes: 42083 }],
    maxLines: 500
  };

  const result = compareToBaseline(baseline, metrics);

  assert.equal(result.passed, false);
  assert.ok(
    result.regressions.some((r) => r.includes("grew from 1008 to 1140 lines"))
  );
  assert.ok(
    result.regressions.some((r) => r.includes("grew from 36385 to 42083 bytes"))
  );
});

test("compareToBaseline reports a per-file complexity-rule regression (video 'max-depth violations increased' behavior)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: {
      total: 2,
      byRule: { "max-depth": 2 },
      byComplexityRule: { "max-depth": 2 },
      perFile: { "src/service.js": { byRule: { "max-depth": 2 } } }
    },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: {
      total: 9,
      byRule: { "max-depth": 9 },
      byComplexityRule: { "max-depth": 9 },
      perFile: { "src/service.js": { byRule: { "max-depth": 9 } } }
    },
    files: [],
    maxLines: 500
  };

  const result = compareToBaseline(baseline, metrics);

  assert.ok(
    result.regressions.some(
      (r) => r === "max-depth violations increased in src/service.js (2 -> 9)"
    )
  );
});

test("renderReport includes Coverage, Duplication, Violations, Regressions sections in order (FR-009)", () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 90, statements: 90, functions: 90, branches: 90 },
    duplication: { percentage: 1, fragments: 1 },
    eslint: { total: 2, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 90, statements: 90, functions: 90, branches: 90 },
    duplication: { percentage: 1, fragments: 1 },
    eslint: { total: 2, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  const coverageIdx = report.indexOf("## Coverage");
  const dupIdx = report.indexOf("## Duplication");
  const violIdx = report.indexOf("## Violations");
  const regrIdx = report.indexOf("## Regressions");
  assert.ok(coverageIdx > -1 && coverageIdx < dupIdx);
  assert.ok(dupIdx < violIdx);
  assert.ok(violIdx < regrIdx);
  assert.match(report, /Status: ✅ Passed/);
});

test('renderReport shows "None." for regressions when nothing regressed (FR-009)', () => {
  const baseline = toBaselineRecord({
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const metrics = {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  };
  const comparison = compareToBaseline(baseline, metrics);

  const report = renderReport(baseline, metrics, comparison);

  assert.match(report, /## Regressions\n\nNone\./);
});

test("parseArgs applies defaults and respects overrides, autoRun defaults true, --no-auto-run disables it (FR-011)", () => {
  const defaults = parseArgs([]);
  assert.equal(defaults.autoRun, true);
  assert.equal(defaults.maxLines, 500);
  assert.equal(defaults.persistDir, ".quality-gate");
  assert.equal(defaults.workDir, null);

  const options = parseArgs([
    "--root",
    "/proj",
    "--max-lines",
    "300",
    "--persist-dir",
    "qg-out",
    "--work-dir",
    "/tmp/qg-work",
    "--no-auto-run"
  ]);
  assert.equal(options.root, "/proj");
  assert.equal(options.maxLines, 300);
  assert.equal(options.persistDir, "qg-out");
  assert.equal(options.workDir, "/tmp/qg-work");
  assert.equal(options.autoRun, false);
});

test("run bootstraps nested baseline inside --persist-dir on first execution and exits 0 without prompting (FR-003, FR-014)", () => {
  const root = makeTempProject();
  const workDir = makeTempProject();
  seedAllReports(workDir);

  const messages = [];
  const exitCode = run(
    ["--root", root, "--no-auto-run", "--work-dir", workDir],
    (msg) => messages.push(msg)
  );

  assert.equal(exitCode, 0);
  const baseline = JSON.parse(
    fs.readFileSync(path.join(root, ".quality-gate", "baseline.json"), "utf8")
  );
  assert.equal(baseline.coverage.lines, 100);
  assert.ok(messages.some((m) => m.includes("created")));
});

test("run does not delete a user-supplied --work-dir, only the default auto-created one (FR-001c / cleanup)", () => {
  const root = makeTempProject();
  const workDir = makeTempProject();
  seedAllReports(workDir);

  run(["--root", root, "--no-auto-run", "--work-dir", workDir], () => {});

  assert.ok(fs.existsSync(path.join(workDir, "eslint-report.json")));
});

test("run exits 1 and writes the report inside --persist-dir when a metric regresses (FR-007, FR-011)", () => {
  const root = makeTempProject();
  const persistDir = path.join(root, ".quality-gate");
  fs.mkdirSync(persistDir, { recursive: true });
  writeBaseline(path.join(persistDir, "baseline.json"), {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const workDir = makeTempProject();
  writeEslintReport(workDir, [
    {
      filePath: path.join(root, "a.js"),
      errorCount: 1,
      warningCount: 0,
      messages: []
    }
  ]);
  writeJscpdReport(workDir, { percentage: 0, clones: 0 });
  writeCoverageSummary(workDir, {
    lines: 100,
    statements: 100,
    functions: 100,
    branches: 100
  });

  const exitCode = run(
    ["--root", root, "--no-auto-run", "--work-dir", workDir],
    () => {}
  );

  assert.equal(exitCode, 1);
  assert.ok(fs.existsSync(path.join(persistDir, "quality-gate-report.md")));
});

test("run exits 0 when metrics match the baseline exactly (FR-008)", () => {
  const root = makeTempProject();
  const persistDir = path.join(root, ".quality-gate");
  fs.mkdirSync(persistDir, { recursive: true });
  writeBaseline(path.join(persistDir, "baseline.json"), {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const workDir = makeTempProject();
  seedAllReports(workDir);

  assert.equal(
    run(["--root", root, "--no-auto-run", "--work-dir", workDir], () => {}),
    0
  );
});

test("run with --update-baseline overwrites baseline.json inside --persist-dir and exits 0 regardless of regression (FR-006)", () => {
  const root = makeTempProject();
  const persistDir = path.join(root, ".quality-gate");
  fs.mkdirSync(persistDir, { recursive: true });
  writeBaseline(path.join(persistDir, "baseline.json"), {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const workDir = makeTempProject();
  writeEslintReport(workDir, [
    {
      filePath: path.join(root, "a.js"),
      errorCount: 5,
      warningCount: 0,
      messages: []
    }
  ]);
  writeJscpdReport(workDir, { percentage: 0, clones: 0 });
  writeCoverageSummary(workDir, {
    lines: 100,
    statements: 100,
    functions: 100,
    branches: 100
  });

  const exitCode = run(
    [
      "--root",
      root,
      "--no-auto-run",
      "--work-dir",
      workDir,
      "--update-baseline"
    ],
    () => {}
  );

  assert.equal(exitCode, 0);
  const written = JSON.parse(
    fs.readFileSync(path.join(persistDir, "baseline.json"), "utf8")
  );
  assert.equal(written.eslint.total, 5);
});

test("run exits 1 with a clear message when a required dependency is missing and auto-run is disabled, no crash (FR-002)", () => {
  const root = makeTempProject();
  const workDir = makeTempProject();
  const messages = [];

  const exitCode = run(
    ["--root", root, "--no-auto-run", "--work-dir", workDir],
    (msg) => messages.push(msg)
  );

  assert.equal(exitCode, 1);
  assert.ok(messages[0].includes("eslint-report.json"));
});

test("run deletes the default auto-created work-dir at the end, leaving only baseline+report in --persist-dir (FR-001c cleanup)", () => {
  const root = makeTempProject();
  const persistDir = path.join(root, ".quality-gate");
  fs.mkdirSync(persistDir, { recursive: true });
  writeBaseline(path.join(persistDir, "baseline.json"), {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });

  const tmpDirsBefore = fs
    .readdirSync(os.tmpdir())
    .filter((n) => n.startsWith("quality-gate-"));
  const exitCode = run(["--root", root, "--no-auto-run"], () => {});
  const tmpDirsAfter = fs
    .readdirSync(os.tmpdir())
    .filter((n) => n.startsWith("quality-gate-"));

  assert.equal(exitCode, 1);
  assert.deepEqual(tmpDirsAfter, tmpDirsBefore);
});

test("run leaves only baseline+report behind in --persist-dir on a successful comparison, tmp work-dir cleaned up (FR-001c cleanup)", () => {
  const root = makeTempProject();
  const persistDir = path.join(root, ".quality-gate");
  fs.mkdirSync(persistDir, { recursive: true });
  writeBaseline(path.join(persistDir, "baseline.json"), {
    coverage: { lines: 100, statements: 100, functions: 100, branches: 100 },
    duplication: { percentage: 0, fragments: 0 },
    eslint: { total: 0, byRule: {}, byComplexityRule: {}, perFile: {} },
    files: [],
    maxLines: 500
  });
  const workDir = makeTempProject();
  seedAllReports(workDir);

  const exitCode = run(
    ["--root", root, "--no-auto-run", "--work-dir", workDir],
    () => {}
  );

  assert.equal(exitCode, 0);
  assert.deepEqual(fs.readdirSync(persistDir).sort(), [
    "baseline.json",
    "quality-gate-report.md"
  ]);
  assert.ok(fs.existsSync(workDir));
});
