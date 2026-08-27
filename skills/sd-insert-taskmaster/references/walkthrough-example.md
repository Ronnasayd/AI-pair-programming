# Full Walkthrough Example

**Input:** User says "transforme `.specs/features/auth-keycloak/tasks.md` em `.taskmaster/tasks/tasks.json`"

**Actions:**

1. Ask: "What tag should be used as the root key?" → user says `"master"` (or skips → default `"master"`)
2. Read `.specs/features/auth-keycloak/tasks.md` completely
3. Extract the ASCII execution diagram and all task tables
4. Build dependency graph edges (T01→[], T02→[1], T03→[1], ...)
5. Run BFS to assign waves: wave1=[1], wave2=[2,3,11,26], ...
6. Identify critical path by traversing graph bottom-up
7. Map each task to JSON fields (include `metadata: { wave, onCriticalPath }`)
8. Build **`.taskmaster/tasks/tasks.json`** — TaskMaster structure
9. Merge tasks.json using `scripts/merge-tasks.py` (preserves existing tags)
10. Validate the file using `scripts/validate-tasks.py`

**Result:**

- `.taskmaster/tasks/tasks.json` — TaskMaster-compatible with task-level metadata, all prior tags preserved
- **No data loss**: Multiple calls with different tags accumulate in tasks.json instead of overwriting
