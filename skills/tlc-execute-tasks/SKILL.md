---
name: tlc-execute-tasks
description: Executes feature tasks by tag, integrating spec files with tlc-spec-driven. Filters pending tasks from taskmaster, executes them in order, and updates status via MCP when each task finishes. The user decides what to do on failures. Use: "execute feature <tag>" or "run tasks for <tag>". Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven).
---

# Execute Feature Tasks

Executes the tasks of a feature by tag, integrating spec files with tlc-spec-driven. Filters pending tasks from taskmaster, executes them according to dependency order, and updates status via MCP when each task is completed. The user decides how failures should be handled.

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
    "projectRoot": "/home/ronnas/develop/lingopass/lingospace-backend",
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

If no: abort. If yes: proceed to Step 4.

### Step 4: Execute Each Task via tlc-spec-driven

For each pending task (in order):

#### 4a. Prepare Context

- Load task object (id, title, description, dependencies)
- Load spec files (design.md, spec.md)
- Load metadata.json

#### 4b. Call tlc-spec-driven in Execute Mode

```text
Invoke skill: tlc-spec-driven
Arguments: tag={TAG}, task_id={TASK_ID}, mode="execute"
```

Expected: tlc-spec-driven performs the implementation for this task.

#### 4c. Monitor Execution

- Capture output (logs, commits, test results)
- Watch for errors or failures

### Step 5: Update Taskmaster Status

If the task succeeds:

```json
{
  "server": "taskmaster-ai",
  "tool_name": "update_task_status",
  "arguments": {
    "projectRoot": "/home/ronnas/develop/lingopass/lingospace-backend",
    "taskId": "{TASK_ID}",
    "status": "completed",
    "timestamp": "{ISO-8601}"
  }
}
```

If the task fails:

- Report the error to the user: **"Task {TASK_ID} failed: {error message}"**
- Ask: **"[R]etry | [S]kip this task | [A]bort execution?"** via the AskUserQuestion tool

Actions:

- Retry: loop back to Step 4b
- Skip: mark as `"skipped"` and continue to the next task
- Abort: stop execution and return a partial summary

### Step 6: Compile & Return Summary

After all tasks (success/skip/abort), show:

```text
Execution Summary for {TAG}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completed:  {N} tasks
Skipped:    {N} tasks
Failed:     {N} tasks
Total time: {estimate}

Tasks executed:
  ✓ T0: [title] — {status}
  ○ T1: [title] — skipped
  ✗ T2: [title] — failed (reason)

Next step: [user-directed action based on result]
```

If all tasks were completed:

```text
Feature execution complete. All tasks done.
```

If only partially completed:

```text
Feature partially executed. {N} tasks pending. Run again to continue.
```

---

## Examples

### Example 1: Execute Auto-Null-Cancellation Feature

**User says:** `tag="auto-null-cancellation"`

**Actions:**

1. Validate that design.md, spec.md, and metadata.json exist for the tag
2. Load files and extract context
3. Call taskmaster MCP with the tag → returns [T0, T1, T2, T3] (all pending)
4. Show plan: `"Ready to execute 4 tasks (~6 hours)? [yes/no]"`
5. User: yes
6. Execute T0 via tlc-spec-driven → update status to completed
7. Execute T1 via tlc-spec-driven → update status to completed
8. Execute T2 via tlc-spec-driven → fails (error: schema validation)
9. Report: `"T2 failed. [R]etry | [S]kip | [A]bort?"`
10. User: `[S]kip`
11. Execute T3 via tlc-spec-driven → update status to completed
12. Summary: `"3/4 tasks completed, 1 skipped. Next: review T2 manually."`

**Result:** Summary in chat plus taskmaster updated with completed/skipped status.

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

### Error: "Taskmaster MCP update_task_status failed"

**Cause:** MCP connection issue or invalid task ID.

**Solution:** Log the error and continue execution (do not block on status updates). Report it in the summary:

```text
Note: some status updates may not have synchronized with taskmaster. Please verify manually.
```

---

## Notes

- Task execution order respects `metadata.wave` from metadata.json plus the dependency graph
- tlc-spec-driven is invoked with the full context (spec files + task object)
- The user controls failure behavior (retry/skip/abort)
- Only the `status` field is updated in taskmaster, not logs or output
- The summary shows what was completed; next actions remain user-directed
