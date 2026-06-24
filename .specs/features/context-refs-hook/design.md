# Design: Context-Refs Hook

## Architecture

Single Python script invoked as a `PreToolUse` hook. Stateless per-call except for session cache written to `/tmp`.

```
PreToolUse (Edit|Write)
       │
       ▼
context_refs.py
       │
       ├─ read CLAUDE_TOOL_INPUT → file_path
       ├─ load .claude/context-refs.json
       ├─ glob match file_path against rules
       ├─ build union ref set
       ├─ load /tmp/context_refs_<SESSION_ID>.json
       ├─ apply dedup/refresh logic per ref
       ├─ print injected refs to stdout
       └─ save updated cache
```

## Session Cache

**File**: `/tmp/context_refs_<SESSION_ID>.json`

**Schema**: `{ "ref/path.ts": <skip_count: int> }`

**Per-ref logic**:
| State | Action | Cache update |
|---|---|---|
| Not in cache | Inject | `cache[ref] = 0` |
| `cache[ref] < refresh_after` | Skip | `cache[ref] += 1` |
| `cache[ref] >= refresh_after` | Inject | `cache[ref] = 0` |

## Glob Matching

- Normalize both `file_path` and glob to forward slashes
- Python 3.12+: `PurePosixPath.full_match(glob)` — correct `**` semantics
- Python <3.12: `fnmatch.fnmatch(str(path), glob)` — `**` treated as `*` (acceptable approximation)

## Stdout Protocol

Hook stdout is injected into Claude context by the harness. Script prints injected ref blocks only — no debug noise on stdout. Warnings (`# WARNING: ...`) acceptable as they surface missing config issues.

## Hook Registration

`claude/settings.json` — add to `PreToolUse` array before the catch-all `""` matcher:

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

## File Locations

| File                                    | Purpose                                   |
| --------------------------------------- | ----------------------------------------- |
| `.claude/hooks/scripts/context_refs.py` | Hook script                               |
| `.claude/context-refs.json`             | Project config (user-created per project) |
| `/tmp/context_refs_<SESSION_ID>.json`   | Session dedup cache (auto-created)        |
| `claude/settings.json`                  | Hook registration                         |
