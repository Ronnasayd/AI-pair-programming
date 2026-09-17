#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const IGNORED_DIRS = new Set([
  "node_modules",
  ".git",
  "coverage",
  "dist",
  "build"
]);
const SOURCE_FILE_PATTERN = /\.(js|jsx|ts|tsx)$/;

/**
 * Error thrown when a metric's required upstream file (lint/dup/coverage report) is missing.
 */
class MissingDependencyError extends Error {
  /**
   * Builds a MissingDependencyError naming the exact missing file.
   * @param missingPath - Absolute or relative path to the file that could not be found.
   */
  constructor(missingPath) {
    super(
      `quality-gate: required file not found: ${missingPath}. Run the tool that produces it before this script.`
    );
    this.name = "MissingDependencyError";
    this.missingPath = missingPath;
  }
}

/**
 * Reads a JSON file, raising MissingDependencyError when it does not exist.
 * @param filePath - Path to the JSON file to read.
 * @returns The parsed JSON content.
 */
function readJsonOrThrow(filePath) {
  if (!fs.existsSync(filePath)) throw new MissingDependencyError(filePath);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

/**
 * Counts total ESLint violations (errors + warnings) from an eslint --format json report.
 * @param root - Root directory containing eslint-report.json.
 * @returns Total count of lint violations across all files.
 */
function collectLintViolations(root) {
  const results = readJsonOrThrow(path.join(root, "eslint-report.json"));
  return results.reduce(
    (sum, file) => sum + file.errorCount + file.warningCount,
    0
  );
}

/**
 * Reads the overall duplication percentage from a jscpd JSON report.
 * @param root - Root directory containing jscpd-report.json.
 * @returns Duplication percentage as reported by jscpd.
 */
function collectDuplicationPercent(root) {
  const report = readJsonOrThrow(path.join(root, "jscpd-report.json"));
  return report.statistics.total.percentage;
}

/**
 * Reads the total line coverage percentage from an Istanbul/nyc coverage summary.
 * @param root - Root directory containing coverage/coverage-summary.json.
 * @returns Line coverage percentage.
 */
function collectCoveragePercent(root) {
  const summary = readJsonOrThrow(
    path.join(root, "coverage", "coverage-summary.json")
  );
  return summary.total.lines.pct;
}

/**
 * Counts the lines in a single file.
 * @param filePath - Path to the file to measure.
 * @returns Number of lines in the file.
 */
function countFileLines(filePath) {
  return fs.readFileSync(filePath, "utf8").split("\n").length;
}

/**
 * Recursively lists every source file under a directory, skipping ignored dirs.
 * @param dir - Directory to scan.
 * @returns Absolute paths of every matching source file found.
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
 * Finds source files whose line count exceeds the configured limit.
 * @param root - Root directory to scan.
 * @param maxLines - Maximum allowed line count per file.
 * @returns List of { path, lines } for files exceeding maxLines, relative to root.
 */
function collectLargeFiles(root, maxLines) {
  return listSourceFiles(root)
    .map((filePath) => ({
      path: path.relative(root, filePath),
      lines: countFileLines(filePath)
    }))
    .filter((file) => file.lines > maxLines);
}

/**
 * Collects all four quality-gate metrics for a project.
 * @param root - Project root directory.
 * @param options - Collection options.
 * @param options.maxLines - Maximum allowed line count per source file.
 * @returns Object with lintViolations, duplicationPercent, coveragePercent, and largeFiles.
 */
function collectMetrics(root, { maxLines }) {
  return {
    lintViolations: collectLintViolations(root),
    duplicationPercent: collectDuplicationPercent(root),
    coveragePercent: collectCoveragePercent(root),
    largeFiles: collectLargeFiles(root, maxLines)
  };
}

const BASELINE_REQUIRED_FIELDS = [
  "lintViolations",
  "duplicationPercent",
  "coveragePercent",
  "largeFilesCount"
];

/**
 * Error thrown when baseline.json exists but is invalid JSON or missing a required field.
 */
class MalformedBaselineError extends Error {
  /**
   * Builds a MalformedBaselineError naming the exact problematic field or parse failure.
   * @param baselinePath - Path to the malformed baseline file.
   * @param reason - Human-readable description of what is wrong (missing field or parse error).
   */
  constructor(baselinePath, reason) {
    super(
      `quality-gate: malformed baseline at ${baselinePath}: ${reason}. The file was not overwritten.`
    );
    this.name = "MalformedBaselineError";
    this.baselinePath = baselinePath;
  }
}

/**
 * Validates that a parsed baseline object contains every required field.
 * @param baseline - Parsed baseline JSON content.
 * @param baselinePath - Path to the baseline file, used for error reporting.
 */
function assertBaselineShape(baseline, baselinePath) {
  const missingField = BASELINE_REQUIRED_FIELDS.find(
    (field) => !(field in baseline)
  );
  if (missingField)
    throw new MalformedBaselineError(
      baselinePath,
      `missing field "${missingField}"`
    );
}

/**
 * Reads the baseline file for a project, distinguishing "does not exist" from "malformed".
 * @param baselinePath - Path to baseline.json.
 * @returns { exists: false } when the file is absent, or { exists: true, baseline } when present and valid.
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
 * Converts collected metrics into the flat shape stored in baseline.json.
 * @param metrics - Metrics object from collectMetrics.
 * @returns Flat baseline record with largeFilesCount instead of the full file list.
 */
function toBaselineRecord(metrics) {
  return {
    lintViolations: metrics.lintViolations,
    duplicationPercent: metrics.duplicationPercent,
    coveragePercent: metrics.coveragePercent,
    largeFilesCount: metrics.largeFiles.length
  };
}

/**
 * Writes the baseline file, always overwriting any existing content.
 * @param baselinePath - Path to baseline.json.
 * @param metrics - Metrics object from collectMetrics to persist as the new baseline.
 */
function writeBaseline(baselinePath, metrics) {
  fs.writeFileSync(
    baselinePath,
    JSON.stringify(toBaselineRecord(metrics), null, 2) + "\n"
  );
}

/**
 * Ensures a baseline exists, bootstrapping it from current metrics on first run.
 * @param baselinePath - Path to baseline.json.
 * @param metrics - Currently collected metrics, used to bootstrap when no baseline exists.
 * @returns { bootstrapped: true } when a new baseline was just created, or { bootstrapped: false, baseline } when one already existed.
 */
function ensureBaseline(baselinePath, metrics) {
  const read = readBaseline(baselinePath);
  if (read.exists) return { bootstrapped: false, baseline: read.baseline };
  writeBaseline(baselinePath, metrics);
  return { bootstrapped: true };
}

const HIGHER_IS_WORSE_FIELDS = new Set([
  "lintViolations",
  "duplicationPercent",
  "largeFilesCount"
]);

/**
 * Compares one metric field's current value against its baseline value.
 * @param field - Metric field name (determines whether higher or lower is worse).
 * @param baselineValue - Value recorded in baseline.json for this field.
 * @param currentValue - Value just collected for this field.
 * @returns { ok, delta } where ok is false when the current value regressed past the baseline.
 */
function compareField(field, baselineValue, currentValue) {
  const delta = currentValue - baselineValue;
  const regressed = HIGHER_IS_WORSE_FIELDS.has(field) ? delta > 0 : delta < 0;
  return { ok: !regressed, baselineValue, currentValue, delta };
}

/**
 * Compares current metrics against a baseline record for every ratchet field.
 * @param baseline - Baseline record read from baseline.json.
 * @param metrics - Currently collected metrics from collectMetrics.
 * @returns { passed, fields } where fields maps each metric field to its compareField result.
 */
function compareToBaseline(baseline, metrics) {
  const current = toBaselineRecord(metrics);
  const fields = {};
  for (const field of BASELINE_REQUIRED_FIELDS) {
    fields[field] = compareField(field, baseline[field], current[field]);
  }
  const passed = Object.values(fields).every((result) => result.ok);
  return { passed, fields };
}

module.exports = {
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
  toBaselineRecord,
  compareToBaseline,
  renderReport,
  parseArgs,
  run
};

const METRIC_LABELS = {
  lintViolations: "Lint violations",
  duplicationPercent: "Duplication %",
  coveragePercent: "Coverage %",
  largeFilesCount: "Large files"
};

/**
 * Renders the current-metrics and baseline summary tables as markdown.
 * @param baseline - Baseline record read from baseline.json.
 * @param current - Current metrics in baseline-record shape (see toBaselineRecord).
 * @returns Markdown string with two tables: current metrics and baseline values.
 */
function renderSummaryTables(baseline, current) {
  const rows = BASELINE_REQUIRED_FIELDS.map(
    (field) =>
      `| ${METRIC_LABELS[field]} | ${current[field]} | ${baseline[field]} |`
  );
  return [
    "| Metric | Current | Baseline |",
    "| --- | --- | --- |",
    ...rows
  ].join("\n");
}

/**
 * Renders the failures section listing baseline, current, and delta for each regressed metric.
 * @param fields - The `fields` map from compareToBaseline's result.
 * @returns Markdown string: a failures table when any field regressed, otherwise a "no failures" line.
 */
function renderFailuresSection(fields) {
  const failed = Object.entries(fields).filter(([, result]) => !result.ok);
  if (failed.length === 0) return "## Failures\n\nNone.";

  const rows = failed.map(
    ([field, result]) =>
      `| ${METRIC_LABELS[field]} | ${result.baselineValue} | ${result.currentValue} | ${result.delta} |`
  );
  return [
    "## Failures",
    "",
    "| Metric | Baseline | Current | Delta |",
    "| --- | --- | --- | --- |",
    ...rows
  ].join("\n");
}

/**
 * Renders the large-files section, explicitly stating "none" when the list is empty.
 * @param largeFiles - List of { path, lines } from collectMetrics.
 * @returns Markdown string listing each large file, or a "none" line when the list is empty.
 */
function renderLargeFilesSection(largeFiles) {
  if (largeFiles.length === 0) return "## Files over the line limit\n\nNone.";
  const rows = largeFiles.map((file) => `- ${file.path} (${file.lines} lines)`);
  return ["## Files over the line limit", "", ...rows].join("\n");
}

/**
 * Renders the full quality-gate report as markdown.
 * @param baseline - Baseline record read from baseline.json.
 * @param metrics - Currently collected metrics from collectMetrics.
 * @param comparison - Result of compareToBaseline(baseline, metrics).
 * @returns Full markdown report: summary tables, failures section, and large-files section.
 */
function renderReport(baseline, metrics, comparison) {
  const current = toBaselineRecord(metrics);
  return [
    "# Quality Gate Report",
    "",
    renderSummaryTables(baseline, current),
    "",
    renderFailuresSection(comparison.fields),
    "",
    renderLargeFilesSection(metrics.largeFiles),
    ""
  ].join("\n");
}

const DEFAULT_MAX_LINES = 500;
const DEFAULT_BASELINE_PATH = "baseline.json";
const DEFAULT_REPORT_PATH = "quality-gate-report.md";

/**
 * Parses CLI flags into structured options. Never reads stdin or prompts.
 * @param argv - Argument list, typically process.argv.slice(2).
 * @returns { root, maxLines, updateBaseline, baselinePath, reportPath } parsed options.
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
    baselinePath: getFlagValue("--baseline-path", DEFAULT_BASELINE_PATH),
    reportPath: getFlagValue("--report-path", DEFAULT_REPORT_PATH)
  };
}

/**
 * Handles the ratchet-comparison path once a valid baseline is confirmed present.
 * @param baseline - Baseline record read from baseline.json.
 * @param metrics - Currently collected metrics.
 * @param reportPath - Absolute path to write the markdown report to.
 * @param logger - Function used to print status messages.
 * @returns The process exit code (0 pass, 1 regression).
 */
function runComparison(baseline, metrics, reportPath, logger) {
  const comparison = compareToBaseline(baseline, metrics);
  fs.writeFileSync(reportPath, renderReport(baseline, metrics, comparison));
  logger(`quality-gate: report written to ${reportPath}`);
  return comparison.passed ? 0 : 1;
}

/**
 * Runs the full quality-gate flow: collect, bootstrap-or-compare, report, exit.
 * Never prompts for input, so it behaves identically local and in CI (FR-013, FR-014).
 * @param argv - Argument list, typically process.argv.slice(2).
 * @param logger - Function used to print status messages (defaults to console.log).
 * @returns The process exit code (0 success, 1 regression or error).
 */
function run(argv, logger = console.log) {
  const options = parseArgs(argv);
  const baselinePath = path.resolve(options.root, options.baselinePath);
  const reportPath = path.resolve(options.root, options.reportPath);

  let metrics;
  try {
    metrics = collectMetrics(options.root, { maxLines: options.maxLines });
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
}

if (require.main === module) {
  process.exit(run(process.argv.slice(2)));
}
