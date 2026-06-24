# Context-Refs Hook: Pre-ToolUse Context Injection (v2)

## Context

When editing files, Claude lacks awareness of related reference files (types, interfaces, conventions, schemas) unless explicitly told. This hook auto-injects those references into context whenever a file path matches a configured glob.

**Problem addressed in v2**: Hook fires on every Edit/Write. If agent edits multiple files that match the same glob(s), same refs get injected repeatedly — wasteful token usage. Solution: session-level dedup cache with periodic refresh (to survive context compaction).

## Design Decisions

| Decision         | Choice                                                 |
| ---------------- | ------------------------------------------------------ |
| Config file      | `.claude/context-refs.json`                            |
| Glob base        | Repo root (cwd)                                        |
| Ref files        | Exact paths only                                       |
| Multi-match      | Union of all matched refs                              |
| Injection format | `=== path ===\n<contents>` per file                    |
| Missing ref      | Warning in stdout, continue                            |
| Tool scope       | `Edit` and `Write` only                                |
| Script language  | Python                                                 |
| Dedup mechanism  | Temp file per session: `{ref_path: skip_count}`        |
| Refresh strategy | Inject once; skip next N calls; re-inject on Nth skip  |
| N (threshold)    | Configurable via `refresh_after` in config (default 3) |

## Config Format

`.claude/context-refs.json`:

```json
{
  "refresh_after": 3,
  "rules": [
    {
      "glob": "src/components/**/*.tsx",
      "refs": ["src/types/components.ts", "src/theme/tokens.ts"]
    },
    {
      "glob": "src/api/**/*.ts",
      "refs": ["src/types/api.ts", "src/utils/http.ts"]
    }
  ]
}
```

`refresh_after` — optional, integer, default `3`. After a ref has been injected, it is skipped for the next `refresh_after` calls. On the `refresh_after`-th skip, it is injected again and the counter resets.

## Session Cache

**Location**: `/tmp/context_refs_<SESSION_ID>.json` where `SESSION_ID` is derived from `$CLAUDE_SESSION_ID` env var (fallback: hash of cwd + process start time).

**Schema**:

```json
{
  "ref/path.ts": 2
}
```

Value = number of times this ref has been _skipped_ since last injection.

**Per-call logic** (for each ref in the union set):

1. If ref not in cache → inject + set `cache[ref] = 0`
2. If `cache[ref] < refresh_after` → skip + `cache[ref] += 1`
3. If `cache[ref] >= refresh_after` → inject + `cache[ref] = 0`

## Files to Create/Modify

### New: `.claude/hooks/scripts/context_refs.py`

```
1. Read CLAUDE_TOOL_NAME — exit 0 if not Edit or Write
2. Read CLAUDE_TOOL_INPUT (JSON) — extract file_path
3. Load .claude/context-refs.json from cwd
4. Extract refresh_after (default 3)
5. For each rule: match file_path glob (pathlib.PurePosixPath.full_match or fnmatch)
6. Collect union of refs from all matching rules (ordered, deduplicated)
7. Load session cache from /tmp/context_refs_<SESSION_ID>.json (empty dict if missing)
8. For each ref:
   a. Determine inject/skip via cache logic above
   b. If inject and file exists: print === {ref} ===\n{contents}\n
   c. If inject and file missing: print # WARNING: ref not found: {ref}\n
9. Save updated cache to temp file
10. Exit 0
```

### Modify: `claude/settings.json`

Add to `PreToolUse` array (before catch-all `""`):

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "python3 .claude/hooks/scripts/context_refs.py"
    }
  ]
}
```

## Injection Output Format

```
=== src/types/components.ts ===
export interface ButtonProps { ... }

=== src/theme/tokens.ts ===
export const colors = { ... }
```

## Glob Matching

Use `pathlib.PurePosixPath` + `fnmatch`. Normalize both paths to forward slashes. For Python 3.12+: use `Path.full_match()` for proper `**` support. Fallback: `fnmatch.fnmatch(str(path), glob_pattern)`.

## Verification

1. Create `.claude/context-refs.json` with one rule matching a known file, `refresh_after: 2`
2. Edit matching file → verify refs injected (first call)
3. Edit another matching file → verify refs NOT injected (first skip)
4. Edit another matching file → verify refs NOT injected (second skip = refresh_after reached, but not yet)
5. Edit another matching file → verify refs injected again (counter hit threshold)
6. Test: non-matching path → no injection, cache unchanged
7. Test: missing ref → warning line, rest injected normally, cache updated
8. Test: two rules match same ref → ref appears once (union dedup), counter tracks single entry
9. Test: no `$CLAUDE_SESSION_ID` → fallback session ID derived deterministically, no crash
