#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execSync } = require("child_process");

const IGNORED_DIRS = new Set([
  "node_modules",
  ".git",
  "coverage",
  "dist",
  "build",
  ".quality-gate",
  ".stryker"
]);
const SOURCE_FILE_PATTERN = /\.(js|jsx|ts|tsx)$/;
const COMPLEXITY_RULES = [
  "complexity",
  "max-depth",
  "max-lines",
  "max-lines-per-function",
  "max-params",
  "max-statements"
];

/**
 * Error thrown when a metric's required upstream file (lint/dup/coverage report) is missing
 * and auto-run either produced nothing or was disabled.
 */
class MissingDependencyError extends Error {
  constructor(missingPath) {
    super(
      `quality-gate: required file not found: ${missingPath}. Run the tool that produces it before this script (or enable auto-run).`
    );
    this.name = "MissingDependencyError";
    this.missingPath = missingPath;
  }
}

/**
 * Error thrown when a collector command itself fails to spawn (not a lint/test failure).
 */
class CollectorExecutionError extends Error {
  constructor(command, cause) {
    super(`quality-gate: failed to run collector "${command}": ${cause}`);
    this.name = "CollectorExecutionError";
    this.command = command;
  }
}

/**
 * Resolves the CLI to invoke for a tool: the project's local `node_modules/.bin/<name>`
 * when present (no npx registry check, no version drift), falling back to `npx <name>`.
 * @param name - Bin name (e.g. "eslint", "jscpd", "jest").
 * @param root - Project root to look for node_modules/.bin in.
 * @returns The command prefix to use in place of `npx <name>`.
 */
function resolveBin(name, root) {
  const localBin = path.join(root, "node_modules", ".bin", name);
  return fs.existsSync(localBin) ? JSON.stringify(localBin) : `npx ${name}`;
}

/**
 * Runs a collector shell command, tolerating the non-zero exit codes lint/dup/test
 * tools use to signal "violations found" — that is expected output, not a script failure.
 * @param command - Shell command to execute.
 * @param cwd - Working directory for the command.
 */
function runCollector(command, cwd) {
  try {
    execSync(command, { cwd, stdio: ["ignore", "pipe", "pipe"] });
  } catch (error) {
    if (typeof error.status === "number") return;
    throw new CollectorExecutionError(command, error.message);
  }
}

/**
 * Reads a JSON file, raising MissingDependencyError when it does not exist.
 */
function readJsonOrThrow(filePath) {
  if (!fs.existsSync(filePath)) throw new MissingDependencyError(filePath);
  const content = fs.readFileSync(filePath, "utf8");
  if (content.trim() === "") throw new MissingDependencyError(filePath);
  return JSON.parse(content);
}

/**
 * Ensures a report file exists, running its collector command first when missing and
 * auto-run is enabled.
 * @param filePath - Expected report path.
 * @param autoRun - Whether to run the collector when the file is missing.
 * @param root - Project root to run the collector in.
 * @param command - Shell command that produces filePath (may write to a directory instead).
 */
function ensureReportFile(filePath, autoRun, root, command) {
  if (fs.existsSync(filePath)) return;
  if (!autoRun) return;
  runCollector(command, root);
}

/**
 * Counts total ESLint violations and aggregates rule-id counts (overall and per file).
 * @returns { total, byRule, perFile } where perFile maps relative path -> { byRule }.
 */
function collectEslintMetrics(eslintReportPath, root) {
  const results = readJsonOrThrow(eslintReportPath);
  const byRule = {};
  const perFile = {};
  let total = 0;

  for (const file of results) {
    total += file.errorCount + file.warningCount;
    const relPath = path.relative(root, file.filePath);
    const fileByRule = {};
    for (const message of file.messages || []) {
      if (!message.ruleId) continue;
      byRule[message.ruleId] = (byRule[message.ruleId] || 0) + 1;
      fileByRule[message.ruleId] = (fileByRule[message.ruleId] || 0) + 1;
    }
    perFile[relPath] = { byRule: fileByRule };
  }

  const byComplexityRule = {};
  for (const rule of COMPLEXITY_RULES)
    byComplexityRule[rule] = byRule[rule] || 0;

  return { total, byRule, byComplexityRule, perFile };
}

/**
 * Reads duplication percentage and clone count from a jscpd JSON report.
 */
function collectDuplicationMetrics(jscpdReportPath) {
  const report = readJsonOrThrow(jscpdReportPath);
  return {
    percentage: report.statistics.total.percentage,
    fragments: report.statistics.total.clones
  };
}

/**
 * Reads per-kind coverage percentages from an Istanbul/nyc coverage summary.
 */
function collectCoverageMetrics(coverageSummaryPath) {
  const summary = readJsonOrThrow(coverageSummaryPath);
  return {
    lines: summary.total.lines.pct,
    statements: summary.total.statements.pct,
    functions: summary.total.functions.pct,
    branches: summary.total.branches.pct
  };
}

/**
 * Recursively lists every source file under a directory, skipping ignored dirs.
 */
function listSourceFiles(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const entryPath = path.join(dir, entry.name);
    if (entry.isDirectory() && !IGNORED_DIRS.has(entry.name)) {
      files.push(...listSourceFiles(entryPath));
      continue;
    }
    if (entry.isFile() && SOURCE_FILE_PATTERN.test(entry.name))
      files.push(entryPath);
  }
  return files;
}

/**
 * Measures every tracked source file's line and byte size.
 * @returns List of { path, lines, bytes } (relative to root), for every source file — not
 * filtered by the line limit, so oversized-file regressions can be detected against baseline.
 */
function collectFileSizes(root) {
  return listSourceFiles(root).map((filePath) => {
    const content = fs.readFileSync(filePath, "utf8");
    return {
      path: path.relative(root, filePath),
      lines: content.split("\n").length,
      bytes: Buffer.byteLength(content, "utf8")
    };
  });
}

/**
 * Collects all quality-gate metrics for a project, auto-running eslint/jscpd/jest first
 * when their reports are missing and autoRun is enabled.
 */
function collectMetrics(
  root,
  {
    maxLines,
    eslintReportPath,
    jscpdReportPath,
    coverageSummaryPath,
    autoRun = true
  }
) {
  ensureReportFile(
    eslintReportPath,
    autoRun,
    root,
    `${resolveBin("eslint", root)} . --format json > ${JSON.stringify(eslintReportPath)}`
  );
  ensureReportFile(
    jscpdReportPath,
    autoRun,
    root,
    `${resolveBin("jscpd", root)} . --reporters json -o ${JSON.stringify(path.dirname(jscpdReportPath))}`
  );
  ensureReportFile(
    coverageSummaryPath,
    autoRun,
    root,
    `${resolveBin("jest", root)} --coverage --coverageReporters=json-summary --coverageDirectory=${JSON.stringify(path.dirname(coverageSummaryPath))}`
  );

  return {
    eslint: collectEslintMetrics(eslintReportPath, root),
    duplication: collectDuplicationMetrics(jscpdReportPath),
    coverage: collectCoverageMetrics(coverageSummaryPath),
    files: collectFileSizes(root),
    maxLines
  };
}

/**
 * Error thrown when baseline.json exists but is invalid JSON or missing a required field.
 */
class MalformedBaselineError extends Error {
  constructor(baselinePath, reason) {
    super(
      `quality-gate: malformed baseline at ${baselinePath}: ${reason}. The file was not overwritten.`
    );
    this.name = "MalformedBaselineError";
    this.baselinePath = baselinePath;
  }
}

const BASELINE_TOP_FIELDS = ["coverage", "duplication", "eslint", "files"];
const COVERAGE_FIELDS = ["lines", "statements", "functions", "branches"];
const DUPLICATION_FIELDS = ["percentage", "fragments"];

/**
 * Validates that a parsed baseline object contains every required nested field.
 */
function assertBaselineShape(baseline, baselinePath) {
  const missingTop = BASELINE_TOP_FIELDS.find((field) => !(field in baseline));
  if (missingTop)
    throw new MalformedBaselineError(
      baselinePath,
      `missing field "${missingTop}"`
    );

  for (const field of COVERAGE_FIELDS) {
    if (!(field in baseline.coverage))
      throw new MalformedBaselineError(
        baselinePath,
        `missing field "coverage.${field}"`
      );
  }
  for (const field of DUPLICATION_FIELDS) {
    if (!(field in baseline.duplication))
      throw new MalformedBaselineError(
        baselinePath,
        `missing field "duplication.${field}"`
      );
  }
  if (!("total" in baseline.eslint))
    throw new MalformedBaselineError(
      baselinePath,
      `missing field "eslint.total"`
    );
  if (!("byComplexityRule" in baseline.eslint))
    throw new MalformedBaselineError(
      baselinePath,
      `missing field "eslint.byComplexityRule"`
    );
  if (!("perFileByComplexityRule" in baseline))
    throw new MalformedBaselineError(
      baselinePath,
      `missing field "perFileByComplexityRule"`
    );
}

/**
 * Reads the baseline file for a project, distinguishing "does not exist" from "malformed".
 */
function readBaseline(baselinePath) {
  if (!fs.existsSync(baselinePath)) return { exists: false };

  let baseline;
  try {
    baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
  } catch (error) {
    throw new MalformedBaselineError(
      baselinePath,
      `invalid JSON (${error.message})`
    );
  }
  assertBaselineShape(baseline, baselinePath);
  return { exists: true, baseline };
}

/**
 * Converts collected metrics into the nested shape stored in baseline.json.
 * Only files currently over maxLines are persisted (same population rule as before),
 * now keyed by path with both lines and bytes so growth can be tracked per file.
 */
function toBaselineRecord(metrics) {
  const oversizedFiles = {};
  for (const file of metrics.files) {
    if (file.lines > metrics.maxLines)
      oversizedFiles[file.path] = { lines: file.lines, bytes: file.bytes };
  }

  const perFileByComplexityRule = {};
  for (const [filePath, entry] of Object.entries(metrics.eslint.perFile)) {
    const byRule = {};
    for (const ruleId of COMPLEXITY_RULES)
      byRule[ruleId] = entry.byRule[ruleId] || 0;
    perFileByComplexityRule[filePath] = byRule;
  }

  return {
    coverage: { ...metrics.coverage },
    duplication: { ...metrics.duplication },
    eslint: {
      total: metrics.eslint.total,
      byRule: { ...metrics.eslint.byRule },
      byComplexityRule: { ...metrics.eslint.byComplexityRule }
    },
    files: oversizedFiles,
    perFileByComplexityRule
  };
}

/**
 * Writes the baseline file, always overwriting any existing content.
 */
function writeBaseline(baselinePath, metrics) {
  fs.writeFileSync(
    baselinePath,
    JSON.stringify(toBaselineRecord(metrics), null, 2) + "\n"
  );
}

/**
 * Ensures a baseline exists, bootstrapping it from current metrics on first run.
 */
function ensureBaseline(baselinePath, metrics) {
  const read = readBaseline(baselinePath);
  if (read.exists) return { bootstrapped: false, baseline: read.baseline };
  writeBaseline(baselinePath, metrics);
  return { bootstrapped: true };
}

/**
 * Compares one leaf value; higherIsWorse decides which direction counts as a regression.
 */
function compareLeaf(baselineValue, currentValue, higherIsWorse) {
  const delta = currentValue - baselineValue;
  const regressed = higherIsWorse ? delta > 0 : delta < 0;
  return { ok: !regressed, baselineValue, currentValue, delta };
}

/**
 * Compares current metrics against a baseline record across every nested leaf field,
 * plus per-file oversized-file regressions (lines/bytes growth while already over limit).
 * @returns { passed, fields, regressions } — fields is a flat map keyed "group.leaf" (or
 * "eslint.byRule.<ruleId>" for dynamic rule ids); regressions is a list of human-readable strings.
 */
function compareToBaseline(baseline, metrics) {
  const current = toBaselineRecord(metrics);
  const fields = {};
  const regressions = [];

  for (const field of COVERAGE_FIELDS) {
    fields[`coverage.${field}`] = compareLeaf(
      baseline.coverage[field],
      current.coverage[field],
      false
    );
  }

  for (const field of DUPLICATION_FIELDS) {
    fields[`duplication.${field}`] = compareLeaf(
      baseline.duplication[field],
      current.duplication[field],
      true
    );
  }

  fields["eslint.total"] = compareLeaf(
    baseline.eslint.total,
    current.eslint.total,
    true
  );

  const ruleIds = new Set([
    ...Object.keys(baseline.eslint.byComplexityRule || {}),
    ...Object.keys(current.eslint.byComplexityRule)
  ]);
  for (const ruleId of ruleIds) {
    const baselineCount = baseline.eslint.byComplexityRule[ruleId] || 0;
    const currentCount = current.eslint.byComplexityRule[ruleId] || 0;
    fields[`eslint.byComplexityRule.${ruleId}`] = compareLeaf(
      baselineCount,
      currentCount,
      true
    );
  }

  const oversizedPaths = new Set([
    ...Object.keys(baseline.files || {}),
    ...Object.keys(current.files)
  ]);
  for (const filePath of oversizedPaths) {
    const before = baseline.files[filePath];
    const after = current.files[filePath];
    fields[`files.${filePath}.lines`] = compareLeaf(
      before ? before.lines : 0,
      after ? after.lines : 0,
      true
    );
    fields[`files.${filePath}.bytes`] = compareLeaf(
      before ? before.bytes : 0,
      after ? after.bytes : 0,
      true
    );

    if (before && after && after.lines > before.lines) {
      regressions.push(
        `${filePath} grew from ${before.lines} to ${after.lines} lines while already over the limit`
      );
    }
    if (before && after && after.bytes > before.bytes) {
      regressions.push(
        `${filePath} grew from ${before.bytes} to ${after.bytes} bytes while already over the limit`
      );
    }
  }

  for (const ruleId of COMPLEXITY_RULES) {
    const perFilePaths = new Set([
      ...Object.keys(baseline.perFileByComplexityRule || {}),
      ...Object.keys(current.perFileByComplexityRule)
    ]);
    for (const filePath of perFilePaths) {
      const beforeCount =
        ((baseline.perFileByComplexityRule || {})[filePath] || {})[ruleId] || 0;
      const afterCount =
        (current.perFileByComplexityRule[filePath] || {})[ruleId] || 0;
      if (afterCount > beforeCount) {
        regressions.push(
          `${ruleId} violations increased in ${filePath} (${beforeCount} -> ${afterCount})`
        );
      }
    }
  }

  const passed = Object.values(fields).every((result) => result.ok);
  return { passed, fields, regressions };
}

module.exports = {
  MissingDependencyError,
  MalformedBaselineError,
  CollectorExecutionError,
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
};

/**
 * Renders the Coverage section: a 4-row table (lines/statements/functions/branches).
 */
function renderCoverageSection(baseline, current) {
  const rows = COVERAGE_FIELDS.map((field) => {
    const label = field.charAt(0).toUpperCase() + field.slice(1);
    const delta = (current.coverage[field] - baseline.coverage[field]).toFixed(
      2
    );
    return `| ${label} | ${baseline.coverage[field]}% | ${current.coverage[field]}% | ${delta >= 0 ? "+" : ""}${delta}% |`;
  });
  return [
    "## Coverage",
    "",
    "| Metric | Baseline | Current | Δ |",
    "| --- | --- | --- | --- |",
    ...rows
  ].join("\n");
}

/**
 * Renders the Duplication section: percentage + fragment count rows.
 */
function renderDuplicationSection(baseline, current) {
  const rows = [
    `| Percentage | ${baseline.duplication.percentage}% | ${current.duplication.percentage}% |`,
    `| Fragments | ${baseline.duplication.fragments} | ${current.duplication.fragments} |`
  ];
  return [
    "## Duplication",
    "",
    "| Metric | Baseline | Current |",
    "| --- | --- | --- |",
    ...rows
  ].join("\n");
}

/**
 * Renders the Violations section: eslint total + oversized-files count.
 */
function renderViolationsSection(baseline, current) {
  const rows = [
    `| Quality rule violations | ${baseline.eslint.total} | ${current.eslint.total} | ${current.eslint.total - baseline.eslint.total} |`,
    `| Oversized files | ${Object.keys(baseline.files).length} | ${Object.keys(current.files).length} | ${Object.keys(current.files).length - Object.keys(baseline.files).length} |`
  ];
  return [
    "## Violations",
    "",
    "| Metric | Baseline | Current | Δ |",
    "| --- | --- | --- | --- |",
    ...rows
  ].join("\n");
}

/**
 * Renders the Regressions section as a bullet list, "None." when empty.
 */
function renderRegressionsSection(regressions) {
  if (regressions.length === 0) return "## Regressions\n\nNone.";
  return ["## Regressions", "", ...regressions.map((line) => `- ${line}`)].join(
    "\n"
  );
}

/**
 * Renders the full quality-gate report as markdown, matching the video's section order:
 * Coverage, Duplication, Violations, Regressions, footer timestamp.
 */
function renderReport(baseline, metrics, comparison) {
  const current = toBaselineRecord(metrics);
  return [
    "# Quality Gate",
    "",
    `Status: ${comparison.passed ? "✅ Passed" : "❌ Failed"}`,
    "",
    renderCoverageSection(baseline, current),
    "",
    renderDuplicationSection(baseline, current),
    "",
    renderViolationsSection(baseline, current),
    "",
    renderRegressionsSection(comparison.regressions),
    "",
    `Generated by scripts/quality-gate.js on ${new Date().toISOString()}`,
    ""
  ].join("\n");
}

const DEFAULT_MAX_LINES = 500;
const DEFAULT_PERSIST_DIR = ".quality-gate";
const BASELINE_FILENAME = "baseline.json";
const REPORT_FILENAME = "quality-gate-report.md";
const ESLINT_REPORT_FILENAME = "eslint-report.json";
const JSCPD_REPORT_FILENAME = "jscpd-report.json";
const COVERAGE_SUMMARY_RELATIVE_PATH = "coverage/coverage-summary.json";

/**
 * Builds a fresh, collision-free work-dir path under the OS tmp dir for one run's
 * intermediate collector reports (eslint/jscpd/coverage) — deleted at the end of run().
 */
function defaultWorkDir() {
  return path.join(
    os.tmpdir(),
    `quality-gate-${process.pid}-${Math.random().toString(36).slice(2, 8)}`
  );
}

/**
 * Parses CLI flags into structured options. Never reads stdin or prompts.
 * Only two directories are configurable: --persist-dir (baseline.json + the markdown
 * report, survives the run) and --work-dir (intermediate collector reports, deleted at
 * the end of the run). Individual report/baseline file paths are no longer exposed —
 * their names are fixed inside those two directories.
 */
function parseArgs(argv) {
  const getFlagValue = (name, fallback) => {
    const index = argv.indexOf(name);
    return index === -1 ? fallback : argv[index + 1];
  };

  return {
    root: getFlagValue("--root", process.cwd()),
    maxLines: Number(getFlagValue("--max-lines", DEFAULT_MAX_LINES)),
    updateBaseline: argv.includes("--update-baseline"),
    autoRun: !argv.includes("--no-auto-run"),
    persistDir: getFlagValue("--persist-dir", DEFAULT_PERSIST_DIR),
    workDir: getFlagValue("--work-dir", null)
  };
}

/**
 * Handles the ratchet-comparison path once a valid baseline is confirmed present.
 */
function runComparison(baseline, metrics, reportPath, logger) {
  const comparison = compareToBaseline(baseline, metrics);
  fs.writeFileSync(reportPath, renderReport(baseline, metrics, comparison));
  logger(`quality-gate: report written to ${reportPath}`);
  return comparison.passed ? 0 : 1;
}

/**
 * Deletes a directory tree, silently ignoring a missing path (nothing to clean up).
 */
function removeDirQuietly(dirPath) {
  fs.rmSync(dirPath, { recursive: true, force: true });
}

/**
 * Runs the full quality-gate flow: collect (auto-running eslint/jscpd/jest when needed),
 * bootstrap-or-compare, report, exit. Never prompts for input, so it behaves identically
 * local and in CI. Intermediate collector reports live in a work dir (default: a fresh,
 * collision-free directory under the OS tmp dir) that is always deleted before returning
 * — only baseline.json and the markdown report survive, inside --persist-dir.
 */
function run(argv, logger = console.log) {
  const options = parseArgs(argv);
  const persistDir = path.resolve(options.root, options.persistDir);
  const workDir = options.workDir
    ? path.resolve(options.root, options.workDir)
    : defaultWorkDir();
  const ownsWorkDir = !options.workDir;

  fs.mkdirSync(persistDir, { recursive: true });
  fs.mkdirSync(workDir, { recursive: true });

  const baselinePath = path.join(persistDir, BASELINE_FILENAME);
  const reportPath = path.join(persistDir, REPORT_FILENAME);
  const eslintReportPath = path.join(workDir, ESLINT_REPORT_FILENAME);
  const jscpdReportPath = path.join(workDir, JSCPD_REPORT_FILENAME);
  const coverageSummaryPath = path.join(
    workDir,
    COVERAGE_SUMMARY_RELATIVE_PATH
  );

  try {
    let metrics;
    try {
      metrics = collectMetrics(options.root, {
        maxLines: options.maxLines,
        eslintReportPath,
        jscpdReportPath,
        coverageSummaryPath,
        autoRun: options.autoRun
      });
    } catch (error) {
      logger(error.message);
      return 1;
    }

    if (options.updateBaseline) {
      writeBaseline(baselinePath, metrics);
      logger(`quality-gate: baseline updated at ${baselinePath}`);
      return 0;
    }

    let read;
    try {
      read = readBaseline(baselinePath);
    } catch (error) {
      logger(error.message);
      return 1;
    }

    if (!read.exists) {
      writeBaseline(baselinePath, metrics);
      logger(
        `quality-gate: no baseline found, created ${baselinePath} from current metrics`
      );
      return 0;
    }

    return runComparison(read.baseline, metrics, reportPath, logger);
  } finally {
    if (ownsWorkDir) removeDirQuietly(workDir);
  }
}

if (require.main === module) {
  process.exit(run(process.argv.slice(2)));
}
