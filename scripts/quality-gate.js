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
  compareToBaseline
};
