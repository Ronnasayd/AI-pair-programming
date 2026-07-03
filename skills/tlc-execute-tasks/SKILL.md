---
name: tlc-execute-tasks
description: "Orchestrates feature task execution by tag. Main agent filters pending tasks from taskmaster, groups them into waves, and directly spawns one subagent per task (via the Agent tool) within each wave, in parallel, respecting wave dependencies. Each subagent runs tlc-spec-driven with the task + spec context it's given. Updates status via MCP after each wave completes. The user decides what to do on failures. Use: 'execute feature <tag>' or run tasks for <tag>. Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Execute Feature Tasks

Main agent acts as orchestrator: filters pending tasks from taskmaster, groups them into execution waves, and directly spawns one subagent (via the Agent tool) per task within each wave, in parallel. Each subagent runs the `tlc-spec-driven` skill with the task object + spec/design/metadata context the main agent passes to it. Main agent respects wave dependencies (waits for wave N to finish before starting wave N+1) and updates taskmaster status after each wave completes. The user decides how failures should be handled.

## Instructions

Use `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` to track wave/task progress and give user feedback throughout execution (in addition to taskmaster MCP status updates).

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

The main agent is the orchestrator. It does not delegate coordination to another skill — it directly spawns subagents itself via the Agent tool, and directly waits on/aggregates their results.

Process each wave in order. Within each wave, execute based on mode:

#### 4a. Wave-Based Execution Dispatch

**For PARALLEL waves (2+ tasks):**

1. For each task in the wave, call the Agent tool directly (all calls in one message, so they run concurrently). Give each subagent complete, self-contained context — it has no access to this conversation:

   ```
   Agent({
     description: "Execute {TASK_ID} for {TAG}",
     prompt: "Run the tlc-spec-driven skill with mode=\"execute\" for task {TASK_ID} in feature tag \"{TAG}\".
       Task: {task_0 object as JSON}
       Full spec.md:\n{spec.md content}
       Full design.md:\n{design.md content}
       Report back: status (Complete/Blocked/Partial), files changed, gate result, and any errors."
   })
   ```

2. Send one Agent call per task in the wave, all in the same message block, so they execute in true parallel (all at once, not sequentially).

3. Wait for all subagent results in wave N before proceeding to wave N+1 (do not fire wave N+1's Agent calls until every wave-N subagent has returned).

**For SEQUENTIAL waves (1 task or no wave metadata):**

Still dispatch to a single subagent (no orchestration overhead needed since there's nothing to parallelize):

- Load task object (id, title, description, dependencies)
- Load spec.md, design.md (metadata.json is orchestrator-only, not passed to the subagent)
- Call Agent once with the same self-contained prompt shape as above (task + spec + design), instructing it to run tlc-spec-driven with `mode="execute"` for that task
- Capture the subagent's reported output (status, files changed, gate result, errors)

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

## Reference Files

- `references/examples.md` — full walkthrough example (wave-parallel execution)
- `references/troubleshooting.md` — error cases and recovery steps
- `references/orchestrator-model.md` — detailed main-agent-as-orchestrator dispatch model

## Notes

- Task execution order respects `metadata.wave` from metadata.json plus the dependency graph
- The main agent is the orchestrator: it spawns subagents directly via the Agent tool and never delegates coordination to another skill
- Each subagent is invoked with the full context (spec files + task object) and runs tlc-spec-driven itself
- The user controls failure behavior (retry/skip/abort)
- Status updates use `set_task_status` MCP call with **`tag` parameter required** — without it, the call succeeds but makes no actual change
- Only the `status` field is updated in taskmaster, not logs or output
- The summary shows what was completed; next actions remain user-directed
