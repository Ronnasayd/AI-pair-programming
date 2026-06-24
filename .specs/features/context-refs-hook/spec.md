# Spec: Context-Refs Hook

## Problem

When Claude edits files, it lacks awareness of related reference files (types, interfaces, conventions, schemas) unless explicitly told via `@file`. This forces users to manually mention references every session.

## Goal

Auto-inject reference file contents into Claude context whenever a matched file is about to be edited — zero manual `@file` mentions required.

## Requirements

### REQ-001 — Trigger scope

Hook fires only on `Edit` and `Write` tool calls. All other tools ignored.

### REQ-002 — Config file

Project-level config at `.claude/context-refs.json`. No config → hook exits silently (exit 0).

### REQ-003 — Glob matching

Each rule maps a glob pattern to a list of ref file paths. Glob base is repo root (cwd). Multiple rules may match the same file path — union of all matching refs is injected.

### REQ-004 — Ref deduplication

Union set preserves insertion order and deduplicates across rules (same ref from two rules → injected once).

### REQ-005 — Injection format

Each injected ref outputs:

```
=== {ref_path} ===
{file_contents}

```

### REQ-006 — Missing ref handling

If a ref file does not exist: print warning line `# WARNING: ref not found: {path}` and continue. Do not abort.

### REQ-007 — Session-level dedup cache

Refs already injected in this session are suppressed to avoid redundant context injection across multiple Edit/Write calls.

### REQ-008 — Periodic refresh

After a ref is injected, it is skipped for the next `refresh_after` calls. On the `refresh_after`-th skip it is re-injected and the counter resets. Handles context compaction scenarios.

### REQ-009 — Configurable refresh threshold

`refresh_after` is an optional integer field in `.claude/context-refs.json`. Default: `3`.

### REQ-010 — Session ID

Cache is keyed by session. Source: `$CLAUDE_SESSION_ID` env var. Fallback: hash of `cwd + process start time`.

### REQ-011 — Hook registration

Script registered in `claude/settings.json` under `PreToolUse` with matcher `Edit|Write`.

## Config Schema

```json
{
  "refresh_after": 3,
  "rules": [
    {
      "glob": "src/components/**/*.tsx",
      "refs": ["src/types/components.ts", "src/theme/tokens.ts"]
    }
  ]
}
```

## Out of Scope

- Dynamic glob patterns based on file content
- Ref file watching / hot reload
- Non-exact ref paths (globs as refs)
