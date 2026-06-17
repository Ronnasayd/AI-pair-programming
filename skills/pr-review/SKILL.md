---
name: pr-review
description: Systematic PR review using GitHub MCP tools. Produces structured report with summary of changes, critical bugs, minor issues, code examples, and external references. Use when asked to "review PR", "analyze PR", "check PR", "give feedback on PR", or given a GitHub PR URL to evaluate. Works for any language or framework. Do NOT use for creating PRs or making code changes.
license: CC-BY-4.0
metadata:
  author: ronnas-machado
  version: 1.0.0
---

# PR Review

Systematic pull request review using GitHub MCP tools. Produces a structured report covering what the PR does, critical bugs, minor issues, code fixes, external references, and merge recommendation.

## Instructions

### Step 1: Collect Basic Metadata (parallel)

Call both simultaneously — they do not depend on each other:

```
pull_request_read method: get       → title, description, author, base branch, file count, +/- lines
pull_request_read method: get_files → file list with per-file patches
```

Extract from results:

- What the PR claims to do (description)
- Volume: files changed, additions, deletions
- Requested reviewers

### Step 2: Get Full Diff

```
pull_request_read method: get_diff
```

Use this for exact line numbers and adjacent context. `get_files` patches are truncated; `get_diff` is the source of truth for line-level findings.

### Step 3: Map Files to Architecture Layers

Before reading code, classify each file by its expected responsibility:

| Layer                                    | Expected Responsibility                |
| ---------------------------------------- | -------------------------------------- |
| Entry point (controller, handler, route) | Receive input, delegate, return output |
| Service / use case                       | Business logic                         |
| Worker / job / task / queue              | Isolated async processing              |
| Model / entity / schema                  | Data structure                         |
| Repository / DAO                         | Data access                            |
| Adapter / client                         | External communication                 |
| Config / infra / scheduler               | Configuration, scheduling              |

Flag immediately any file doing work outside its layer — this is always at least a 🟡 finding.

### Step 4: Review Each File

Apply this checklist to every changed file:

**Correctness**

- Variables used before initialization
- Null/empty/zero cases handled before use
- Return values checked before consuming
- Edge cases covered (empty list, zero value, null input)

**Architecture**

- File only does what its layer should do
- Dependencies injected, not instantiated internally
- No coupling between layers that should not know each other

**Security**

- External input validated/sanitized before use
- No hardcoded credentials or secrets
- No injection vectors (SQL, command, template)
- Destructive operations gated by permission check

**Consistency**

- Method/variable names correct and consistent across files
- Comments and docs match what the code actually does
- Style consistent with the surrounding codebase

### Step 5: Classify All Findings

| Symbol | Severity | Criterion                                                           |
| ------ | -------- | ------------------------------------------------------------------- |
| 🔴     | Critical | Can cause runtime failure, data loss, or security breach            |
| 🟡     | Minor    | No immediate breakage but creates future risk or maintenance burden |
| ⚪     | Debt     | Architectural violation or quality issue — handle in separate task  |

**Rule:** if a problem can produce wrong behavior in production with no visible error → 🔴 automatically.

### Step 6: Find External References

For each 🔴 and significant 🟡 finding, run a `WebSearch` to find supporting documentation.

Query patterns by category:

| Category              | Query pattern                              |
| --------------------- | ------------------------------------------ |
| Language behavior     | `[language] [behavior] spec`               |
| Framework antipattern | `[framework] [pattern] best practice`      |
| Security              | `[vulnerability name] OWASP`               |
| Performance           | `[operation] performance [db/runtime]`     |
| Future breakage       | `[language] RFC [behavior] future version` |

Use references to confirm the problem is real and to point to the canonical solution — not just opinion.

### Step 7: Write Fix Examples

For each 🔴 and 🟡 finding, produce:

```
File: path/to/file.ext — line N

// PROBLEM: one-line description
[problematic code]

// FIX
[corrected code — minimum necessary change]
```

Rules:

- Fix is surgical — only what is needed
- Larger refactors → flag as ⚪ debt, suggest separate task
- Never mix bug fix with style cleanup in the same example

### Step 8: Deliver Structured Report

```markdown
## What the PR does

| # | Feature | Detail |

## Problems Found

### 🔴 Critical

For each: **Cause** / **Impact** / **Fix** (code block) / **Reference** (link)

### 🟡 Minor

| File | Line | Problem |

### ⚪ Technical Debt

- bullet list of what to handle separately

## Fix Priority

| Priority | Fix | Effort |

## Recommendation

One line: safe to merge / do not merge / merge after fixing X
```

## Examples

### Example 1: PR with undefined variable

User says: "review this PR https://github.com/org/repo/pull/42"

Actions:

1. `get` + `get_files` in parallel
2. `get_diff` for line numbers
3. Find in diff: variable used in loop body but never initialized before loop
4. Classify: 🔴 — produces wrong output silently
5. WebSearch: `[language] undefined variable runtime behavior`
6. Write fix: add `variable = initial_value` before the loop
7. Deliver report with finding, fix, and reference link

Result: structured report, fix example with exact line, merge blocked until fixed.

---

### Example 2: Architecture violation — wrong layer

User says: "analyze PR #98 in LINGOPASS/lingo_digitalpass"

Actions:

1. Collect metadata + files in parallel
2. Full diff
3. Classify files: find Job file that instantiates a Controller internally
4. 🔴 — Controller has HTTP request dependencies; running it in a queue worker context fails
5. WebSearch: `[framework] job instantiate controller antipattern`
6. Fix: extract logic to Service class, inject Service into Job's handle method
7. Reference official queue docs + community article

Result: report blocks merge, shows before/after refactor, links docs.

---

### Example 3: Minor — doc/code mismatch

User says: "check PR #15"

Actions:
1-3. Standard collect + diff 4. Find: comment says "runs at 23:00", scheduler sets "22:00" 5. Classify: 🟡 — no runtime impact, operational risk during incidents 6. No WebSearch needed for this finding 7. Fix: align comment with actual scheduled time

Result: finding in minor table, one-line fix, no merge block.

## Troubleshooting

### No diff returned / empty patch

Cause: PR may be a draft or have conflicts blocking diff generation.
Solution: use `get_status` to check merge state; if `mergeable_state` is `dirty`, report conflicts first.

### File patches truncated in get_files

Cause: large files exceed per-file patch limit.
Solution: always run `get_diff` in Step 2 — it is the authoritative source.

### Cannot find exact line numbers

Cause: relying on `get_files` patches only.
Solution: cross-reference `get_diff` unified output where every `+` line has a line number in the new file.

### get_diff or get_files output too large (persisted to protected file)

Cause: output exceeds context limit and is saved to a path outside the project, which is blocked by file protection hooks.
Solution: paginate `get_files` with `perPage: 5` and iterate pages until all files are retrieved. Never use `get_file_contents` with `ref: refs/pull/{N}/head` as a substitute — it returns the file at branch HEAD regardless of whether it was changed in the PR, leading to false findings on pre-existing code.
