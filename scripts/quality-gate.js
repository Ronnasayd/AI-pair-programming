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

module.exports = {
  MissingDependencyError,
  collectLintViolations,
  collectDuplicationPercent,
  collectCoveragePercent,
  collectLargeFiles,
  collectMetrics
};
