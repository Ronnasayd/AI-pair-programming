---
name: tlc-execute-tasks
description: 'Executes feature tasks by tag, integrating spec files with tlc-spec-driven. Filters pending tasks from taskmaster, groups them into waves, and executes tasks within each wave in parallel (via orchestrate skill) while respecting wave dependencies. Updates status via MCP after each wave completes. The user decides what to do on failures. Use: "execute feature <tag>" or "run tasks for <tag>". Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven).'
---

# Execute Feature Tasks

Executes the tasks of a feature by tag, integrating spec files with tlc-spec-driven. Filters pending tasks from taskmaster, groups them into execution waves, and executes independent tasks within each wave in parallel via the orchestrate skill. Respects wave dependencies to ensure correct execution order. Updates taskmaster status after each wave completes. The user decides how failures should be handled.

## Instructions

### Step 1: Validate Tag & Load Spec Files

The user provides a tag (e.g. `tag="auto-null-cancellation"`). Validate that:

- `@.specs/features/{TAG}/design.md` exists
- `@.specs/features/{TAG}/spec.md` exists
- `@.taskmaster/execution/metadata.json` exists

If any file is missing, report an error listing the missing paths. Do not proceed.

If validation succeeds, read all 3 files in parallel. Extract:

- **design.md**: architecture, complexity label, scope
- **spec.md**: problem statement, goals, requirements
- **metadata.json**: execution waves, critical path, dependencies, effort estimate

Expected output: confirmation that files were loaded plus a summary of what will be executed.

### Step 2: Fetch Pending Tasks from Taskmaster MCP

Call taskmaster MCP:

```json
{
  "server": "taskmaster-ai",
  "tool_name": "get_tasks",
  "arguments": {
    "projectRoot": "{PROJECT_ROOT}",
    "tag": "{TAG}"
  }
}
```

Result: array of tasks with id, title, description, status, dependencies, metadata.

Filter: keep only tasks where `status != "completed"`.

Sort: respect `metadata.wave` order plus the dependency graph from metadata.json.

Expected output: list of pending tasks in execution order.

### Step 3: Display Execution Plan to User

Show:

- Feature tag
- Total pending tasks + effort estimate
- Execution sequence (T0 → T1 → ... → Tn)

Ask the user: **"Ready to execute {N} tasks? [yes/no]"** via the AskUserQuestion tool.

If no: abort. If yes: proceed to Step 3.5.

### Step 3.5: Build Wave Groups

Group all pending tasks by their `metadata.wave` value from metadata.json:

- **Wave N**: all tasks where `metadata.wave === N`
- **No wave metadata**: tasks without explicit wave assignment default to Wave 0 or treated as sequential

Classify each wave:

- **PARALLEL**: wave with 2+ independent tasks → delegate to subagents
- **SEQUENTIAL**: wave with 1 task OR tasks with no wave metadata → execute directly

Update execution plan shown to user to include wave breakdown:

```
Wave 0 (PARALLEL):  T0, T1     — 2 tasks
Wave 1 (SEQUENTIAL): T2        — 1 task
```

Expected output: wave groupings, mode (PARALLEL/SEQUENTIAL) per wave, total task count by mode.

If yes from Step 3: proceed to Step 4.

### Step 4: Execute Tasks by Wave (Parallel within Wave)

Process each wave in order. Within each wave, execute based on mode:

#### 4a. Wave-Based Execution Dispatch

**For PARALLEL waves (2+ tasks):**

1. Invoke orchestrate skill to manage subagent coordination:

   ```json
   {
     "skill": "orchestrate",
     "context": {
       "tag": "{TAG}",
       "wave_number": N,
       "tasks": [task_0, task_1, ...],
       "spec_md": "{full spec.md content}",
       "design_md": "{full design.md content}",
       "metadata_json": "{metadata.json object}"
     }
   }
   ```

2. Orchestrate spawns one subagent per task simultaneously. Each subagent:
   - Receives complete self-contained context (task object + spec + design + metadata)
   - Invokes `tlc-spec-driven` with `mode="execute"` for its single task
   - Reports: status (Complete/Blocked/Partial), files changed, gate result, errors
   - Subagents execute in true parallel (all at once, not sequentially)

3. Wait for all subagents in wave N to complete before proceeding to wave N+1.

**For SEQUENTIAL waves (1 task or no wave metadata):**

Execute directly without subagent overhead:

- Load task object (id, title, description, dependencies)
- Load spec.md, design.md, metadata.json
- Invoke tlc-spec-driven with `tag={TAG}, task_id={TASK_ID}, mode="execute"`
- Capture output (logs, commits, test results)

#### 4b. Handle Wave Failures

If any task in wave N fails:

- Capture error message and task ID
- Ask user: **"[R]etry | [S]kip this task | [A]bort execution?"** via AskUserQuestion
- **Retry**: re-execute the failed task (or the entire wave for PARALLEL waves, per user preference)
- **Skip**: mark task as `"cancelled"` or `"deferred"` via set_task_status, continue to next task/wave
- **Abort**: stop wave processing, return partial summary for Wave 0..N-1 only

### Step 5: Update Taskmaster Status (Per-Wave)

After each wave N completes (all tasks in wave N have status), call set_task_status for each task:

```json
{
  "server": "taskmaster-ai",
  "tool_name": "set_task_status",
  "arguments": {
    "projectRoot": "{PROJECT_ROOT}",
    "id": "{TASK_ID}",
    "status": "{done|deferred|cancelled}",
    "tag": "{TAG}"
  }
}
```

**Critical**: Without `tag` parameter, call returns success but makes no actual change. With `tag`, updates both MCP backend AND `.taskmaster/tasks/tasks.json` file.

Status values: `"pending"`, `"in-progress"`, `"done"`, `"deferred"`, `"cancelled"`, `"blocked"`, `"review"`

**Status mapping:**

- Task succeeded → status = `"done"`
- Task skipped (user choice) → status = `"cancelled"` or `"deferred"`
- Task failed and not retried → status = `"blocked"` or `"deferred"`

Do NOT wait until all waves complete to update status. Update after each wave finishes, so MCP state reflects progress incrementally.

**Handling failures within a wave:**

Failure recovery happens in Step 4b (before Step 5). By the time Step 5 runs, each task has a final status (done/cancelled/deferred/blocked). Step 5 simply syncs that status to taskmaster.

### Step 6: Compile & Return Summary

After all waves complete (or execution aborts), show:

```text
Execution Summary for {TAG}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave Execution:
  Wave 0 (PARALLEL):   2 tasks — ✓ T0, ✓ T1
  Wave 1 (SEQUENTIAL): 1 task  — ✓ T2
  Wave 2 (PARALLEL):   2 tasks — ✓ T3, ✗ T4 (failed: schema error)

Summary:
  Completed:  {N} tasks
  Skipped:    {N} tasks
  Failed:     {N} tasks
  Total time: {estimate}

Details:
  ✓ T0: [title] — completed
  ✓ T1: [title] — completed
  ✓ T2: [title] — completed
  ✓ T3: [title] — completed
  ✗ T4: [title] — failed (reason: schema validation error)

Next step: [user-directed action based on result]
```

If all tasks were completed:

```text
Feature execution complete. All {N} tasks done.
```

If only partially completed:

```text
Feature partially executed. {N} tasks completed, {M} tasks pending/failed. Run again to continue or review failures.
```

---

## Examples

### Example 1: Execute Auto-Null-Cancellation Feature (Wave-Parallel)

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
   - Invoke orchestrate skill → spawns 2 subagents simultaneously
   - Subagent-1: Execute T0 via tlc-spec-driven → completes successfully
   - Subagent-2: Execute T1 via tlc-spec-driven → completes successfully
   - Wait for both to finish, then update taskmaster status for T0, T1 → both "done"
8. Execute Wave 1 (SEQUENTIAL):
   - Execute T2 via tlc-spec-driven directly → fails (error: schema validation)
   - Report: `"T2 failed. [R]etry | [S]kip | [A]bort?"`
   - User: `[S]kip`
   - Mark T2 status = "cancelled", update taskmaster
   - Execute T3 via tlc-spec-driven → completes successfully
   - Update taskmaster status for T3 → "done"
9. Summary: `"Wave 0: 2/2 done. Wave 1: 1/2 done, 1 skipped. Total: 3/4 tasks completed."`

**Result:** Summary in chat, taskmaster updated incrementally per-wave, user can retry/skip/abort at wave boundaries.

---

## Troubleshooting

### Error: "Tag directory not found"

**Cause:** `@.specs/features/{TAG}/` does not exist or the naming does not match.

**Solution:** Verify the tag format (kebab-case) and ensure the spec files exist in the project. Check `@docs/feature-verification-process.md` for the expected structure.

---

### Error: "Taskmaster MCP returned empty tasks array"

**Cause:** The tag exists but has no tasks in taskmaster, or the tag is not recognized by MCP.

**Solution:** Fall back to `@.specs/features/{TAG}/tasks.md` if it exists. Parse it manually (T0, T1, T2, ...). If no tasks.md exists either, ask the user whether the tag is correct.

---

### Error: "tlc-spec-driven failed to execute task"

**Cause:** A task execution error occurred in tlc-spec-driven (code error, test failure, etc.).

**Solution:** Show the error to the user and let them choose `[R]etry`, `[S]kip`, or `[A]bort`. Retry executes the same task again. Skip marks it as `"skipped"` and continues. Abort stops execution.

---

### Error: "Taskmaster MCP set_task_status failed"

**Cause:** MCP connection issue, invalid task ID, or missing `tag` parameter.

**Solution:** Log the error and continue execution (do not block on status updates). Ensure `tag` parameter is always passed to set_task_status. Report it in the summary:

```text
Note: some status updates may not have synchronized with taskmaster. Please verify manually.
Verify via: taskmaster list --tag={TAG}
```

---

## Orchestrate Skill Integration

When executing PARALLEL waves (2+ independent tasks):

1. **Wave Grouping**: Pending tasks are grouped by `metadata.wave` from metadata.json
2. **Orchestrate Invocation**: For each wave with 2+ tasks, the orchestrate skill is invoked to coordinate subagent dispatch
3. **Subagent Spawning**: Orchestrate spawns one subagent per task (all simultaneously, not sequentially)
4. **Execution Context**: Each subagent receives:
   - Task object (id, title, description, dependencies)
   - Full spec.md content (problem statement, goals, requirements)
   - Full design.md content (architecture, complexity, scope)
   - Full metadata.json (waves, critical path, dependencies, estimates)
   - TAG value and any coding conventions
5. **Self-Contained Execution**: Subagents execute `tlc-spec-driven` with `mode="execute"` independently; they do NOT need to consult the main thread
6. **Wave Synchronization**: All subagents in a wave must complete before the next wave begins (orchestrate enforces this)
7. **Status Reporting**: After each wave completes, status updates are sent to taskmaster via `set_task_status` with the `tag` parameter
8. **Single-Task Waves**: Waves with only 1 task (or no wave metadata) bypass orchestrate and execute directly via `tlc-spec-driven` to avoid subagent overhead

**Performance benefit**: Multi-task waves execute in true parallel (wall-clock time = longest task, not sum of all tasks).

## Notes

- Task execution order respects `metadata.wave` from metadata.json plus the dependency graph
- tlc-spec-driven is invoked with the full context (spec files + task object)
- The user controls failure behavior (retry/skip/abort)
- Status updates use `set_task_status` MCP call with **`tag` parameter required** — without it, the call succeeds but makes no actual change
- Only the `status` field is updated in taskmaster, not logs or output
- The summary shows what was completed; next actions remain user-directed
- Parallel execution within a wave requires the orchestrate skill; single-task waves execute directly to minimize overhead
