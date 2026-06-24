# Context-Refs Hook: Pre-ToolUse Context Injection

## Context

When editing files, Claude lacks awareness of related reference files (types, interfaces, conventions, schemas) unless explicitly told. This hook auto-injects those references into context whenever a file path matches a configured glob — removing manual `@file` mentions.

## Design Decisions (grilled)

| Decision         | Choice                              |
| ---------------- | ----------------------------------- |
| Config file      | `.claude/context-refs.json`         |
| Glob base        | Repo root (cwd)                     |
| Ref files        | Exact paths only                    |
| Multi-match      | Union of all matched refs           |
| Injection format | `=== path ===\n<contents>` per file |
| Missing ref      | Warning in stdout, continue         |
| Tool scope       | `Edit` and `Write` only             |
| Script language  | Python                              |

## Config Format

`.claude/context-refs.json`:

```json
{
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

## Files to Create/Modify

### New: `.claude/hooks/scripts/context_refs.py`

Logic:

1. Read `CLAUDE_TOOL_NAME` env var — exit 0 if not `Edit` or `Write`
2. Read `CLAUDE_TOOL_INPUT` (JSON) — extract `file_path`
3. Load `.claude/context-refs.json` from cwd
4. For each rule: test `fnmatch` (or `pathlib.Path.match`) against `file_path`
5. Collect union of all `refs` from matching rules (preserve order, deduplicate)
6. For each ref:
   - If exists: print `=== {ref} ===\n{contents}\n`
   - If missing: print `# WARNING: ref not found: {ref}\n`
7. Exit 0

### Modify: `claude/settings.json`

Add new entry to `PreToolUse` array (matcher `Edit|Write`, before the catch-all `""`):

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": ".claude/hooks/scripts/context_refs.py"
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

Use `pathlib.PurePosixPath` + `fnmatch` pattern. Normalize both the input path and glob pattern to forward slashes. Test with `fnmatch.fnmatch(str(path), glob_pattern)` — handles `**` via `fnmatch` approximation. For proper `**` support, use `pathlib.Path.full_match()` (Python 3.12+) or fall back to `fnmatch` with `*` semantics.

## Verification

1. Create `.claude/context-refs.json` with one rule matching a known file
2. Run `Edit` on a matching file — stdout from hook should appear in Claude context
3. Verify injected content visible: Claude should reference the ref file contents without being told
4. Test: non-matching path → no injection (empty stdout, exit 0)
5. Test: missing ref file → warning line in stdout, rest injected normally
6. Test: two rules match same file → both refs injected, no duplicates
