# harness-toolkit: `codePaths` silently disables the lint gate

Draft for an upstream issue on `@tech-leads-club/harness-toolkit` (v0.16 schema).

## Summary

The `stop` hook skips the `grind` lint/test gates without any message when
`codePaths` holds an absolute path, a placeholder, or `.`. Files in the repo
root can never be covered, whatever value is configured.

## Observed

- Config: `grind.enabled: true`, `grind.lintCommand` set, `codePaths` set to the
  absolute repo path (`/home/<user>/.../aipp`).
- `lint_changed.py` run by hand exits 1 and prints the failures.
- `echo '{"hook_event_name":"Stop",...}' | node tlc-exec.mjs stop` exits 0 with
  empty output. The gate never ran, and nothing says why.

## Root cause

`src/entrypoints/stop.ts:596` runs the lint gate only when
`codeTargets.length > 0`. `codeTargets` comes from `filterCodeTargets`
(`src/platform/git.ts:257-268`), which calls `isUnderPrefixes`:

```ts
normalized === prefix || normalized.startsWith(`${prefix}/`);
```

`normalized` is a path relative to the git root, so only relative prefixes can
match. The same rule is duplicated in `isUnderCodePaths`
(`src/core/policy/policy.loader.ts:131`). `policy.loader.ts` merges `codePaths`
as-is (line 49), with no normalization or validation. The default is
`["src", "apps", "libs", "packages"]`.

Consequences:

| `codePaths` value                      | Matches                                                 |
| -------------------------------------- | ------------------------------------------------------- |
| `"/abs/path/to/repo"`                  | nothing                                                 |
| `"$CLAUDE_PROJECT_DIR$"` (placeholder) | nothing                                                 |
| `"."` or `""`                          | nothing (`"./"` and `"/"` never prefix a relative path) |
| `"src"`                                | `src` and `src/**`                                      |
| `"main.py"`                            | only that exact file                                    |

A repo-root file (for example `main.py`) is covered only by listing its exact
name.

## Impact

- Silent failure: the gate is skipped and the stop reply is empty, so the user
  believes lint passes. `docs/diagnose.md:158` says "both zero: check
  `grind.enabled` and `codePaths`", but nothing surfaces that hint at runtime.
- Templates that ship an absolute path or a placeholder produce a harness that
  never lints.

## Suggested fixes

1. Normalize `codePaths` on load: resolve absolute paths against the git root
   and turn them into relative prefixes; treat `.` as "whole repo".
2. Warn when `grind.enabled` is true and no changed file matched `codePaths`
   while files did change (include the offending value in the message).
3. Validate `codePaths` in `tlc harness doctor` and in the JSON schema
   (reject entries that start with `/` or contain `$`).

## Local workaround

Use relative prefixes in `.tlc/harness/config.json`
(`["src", "hooks", "scripts"]`) and move fixtures out of the repo root.
`tlc-harness-toolkit/config.json` now lists common directory names instead of
the `$CLAUDE_PROJECT_DIR$` placeholder.

## Not verified

After the config change, the `stop` hook has not been re-run against a changed
file under a covered directory. `lint_errors.py` sits in the repo root, so it
is still outside the gate.
