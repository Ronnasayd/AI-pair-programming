# Tasks: Context-Refs Hook

## T-01 — Write hook script

**What**: Create `.claude/hooks/scripts/context_refs.py`

**Logic**:

1. Read `CLAUDE_TOOL_NAME` — exit 0 if not `Edit` or `Write`
2. Read `CLAUDE_TOOL_INPUT` (JSON) — extract `file_path`
3. Load `.claude/context-refs.json` from cwd — exit 0 silently if missing
4. Extract `refresh_after` (default `3`)
5. Glob-match `file_path` against all rules (PurePosixPath.full_match or fnmatch fallback)
6. Build ordered, deduplicated union of matching refs
7. Derive session ID from `$CLAUDE_SESSION_ID` or hash(cwd + process start)
8. Load `/tmp/context_refs_<SESSION_ID>.json` (empty dict if missing)
9. For each ref: apply inject/skip logic per cache state
10. Print injected ref blocks to stdout
11. Print `# WARNING: ref not found: {path}` for missing refs
12. Save updated cache to temp file
13. Exit 0

**Done when**:

- Script exits 0 in all cases (no unhandled exceptions)
- Matching file → ref contents in stdout
- Non-matching file → empty stdout
- Missing ref → warning line, other refs still injected
- Second call with same refs → no stdout (suppressed by cache)
- After `refresh_after` skips → refs re-injected, counter reset

---

## T-02 — Register hook in settings.json

**What**: Add `Edit|Write` PreToolUse entry to `claude/settings.json`

**Where**: `claude/settings.json` — `PreToolUse` array, before catch-all `""` matcher

**Entry**:

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

**Depends on**: T-01

**Done when**: Hook fires on next Edit/Write call in a Claude Code session

---

## T-03 — Create example config

**What**: Create `.claude/context-refs.json` in this repo as working example + documentation

**Content**:

```json
{
  "refresh_after": 3,
  "rules": [
    {
      "glob": "claude/settings.json",
      "refs": []
    }
  ]
}
```

**Done when**: File exists, valid JSON, parseable by script

---

## T-04 — Verify end-to-end

**Steps**:

1. Set `refresh_after: 2` in `.claude/context-refs.json`
2. Add rule matching a known file, refs pointing to real files
3. Edit matched file → verify ref contents appear in Claude context
4. Edit matched file again → verify NO injection (skip 1)
5. Edit matched file again → verify NO injection (skip 2 = threshold, re-inject on NEXT)
6. Edit matched file again → verify ref injected again, counter reset
7. Edit non-matching file → verify empty stdout
8. Point ref to missing file → verify warning line, session continues
9. Two rules matching same ref → verify ref injected once

**Done when**: All 9 checks pass
