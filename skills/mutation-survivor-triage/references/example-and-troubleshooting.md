# Example

User: "triage the mutation survivors in reports/mutation/mutation.json"

1. `jq` scale query → 47 survivors, `src/logger.ts` (18), `src/auth/session.service.ts` (12), rest scattered.
2. `src/logger.ts`: all 18 are `StringLiteral`/`ObjectLiteral` on log message templates → false negative cluster, but note file IS the logging implementation, so check for any conditional-format-selection mutants separately (found none survived there — clean).
3. `src/auth/session.service.ts`: 8 are `ConditionalExpression` on a repeated `ensureAuthenticated()` guard across 4 methods → real gap, repeated pattern. 4 are `EqualityOperator` on an env check (`NODE_ENV === 'production'`) gating token redaction → real gap, security-flagged.
4. Output: consolidated table with 12 real-gap rows (each with a named test), false-negative summary for logger.ts with suggested `// Stryker disable next-line all` per log call or a `mutate` glob exclusion if the team prefers file-level.

# Troubleshooting

| Error                                       | Cause                                                                                          | Solution                                                                                                                          |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `jq: error: Cannot index array with string` | Report path wrong or `.files` structure differs across Stryker versions                        | `jq '.schemaVersion, (.files \| keys[0])' mutation.json` to inspect actual shape first                                            |
| No `reports/mutation/mutation.json`         | JSON reporter not enabled, or written elsewhere (`mutation-report.json`, `html/mutation.json`) | Check `stryker.config.mjs` `reporters`/`jsonReporter.fileName`, or `find . -name '*mutation*.json' -not -path '*/node_modules/*'` |
