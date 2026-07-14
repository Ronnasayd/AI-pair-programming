# Examples

## Example 1: Execute Auto-Null-Cancellation Feature (Wave-Parallel)

**User says:** `tag="auto-null-cancellation"`

**Actions:**

1. Validate that design.md, spec.md, and metadata.json exist for the tag
2. Load files and extract context
3. Call taskmaster MCP with the tag → returns [T0, T1, T2, T3] (all pending)
4. Build wave groups from metadata.json:
   - Wave 0 (PARALLEL): T0, T1 (no mutual dependencies)
   - Wave 1 (SEQUENTIAL): T2, T3 (sequential dependencies)
5. Show plan: `"Ready to execute 4 tasks across 2 waves (~6 hours)? [yes/no]"`
6. User: yes
7. Execute Wave 0 (PARALLEL):
   - Main agent calls Agent tool twice in one message → spawns 2 subagents simultaneously
   - Subagent-1: runs tlc-spec-driven for T0 → completes successfully
   - Subagent-2: runs tlc-spec-driven for T1 → completes successfully
   - Main agent waits for both to finish, then updates taskmaster status for T0, T1 → both "done"
8. Execute Wave 1 (SEQUENTIAL):
   - Main agent calls Agent tool once for T2 (runs tlc-spec-driven) → fails (error: schema validation)
   - Report: `"T2 failed. [R]etry | [S]kip | [A]bort?"`
   - User: `[S]kip`
   - Mark T2 status = "cancelled", update taskmaster
   - Main agent calls Agent tool once for T3 (runs tlc-spec-driven) → completes successfully
   - Update taskmaster status for T3 → "done"
9. Summary: `"Wave 0: 2/2 done. Wave 1: 1/2 done, 1 skipped. Total: 3/4 tasks completed."`

**Result:** Summary in chat, taskmaster updated incrementally per-wave, user can retry/skip/abort at wave boundaries.
