---
name: tlc-execute-tasks
description: "Orchestrates feature task execution by tag. Main agent filters pending tasks from taskmaster, groups them into waves, and drives each task through the adversarial-dev skill (executor + evaluator loop) within each wave, in parallel (capped concurrency), respecting wave dependencies. Each task's executor runs tlc-spec-driven with the task + spec context it's given; the evaluator grades against the task's own verification criteria. A task only counts as done at score 8+/10. Updates status via MCP after each wave completes. The user decides what to do on failures/exhaustion. Use: 'execute feature <tag>' or run tasks for <tag>. Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Execute Feature Tasks

Main agent acts as orchestrator: filters pending tasks from taskmaster, groups them into execution waves, and drives each task in the wave through the `adversarial-dev` skill — an executor agent (running `tlc-spec-driven` mode="execute") paired with an independent evaluator agent that grades the result against the task's own verification criteria. A task is only marked done once the evaluator scores it 8+/10. Main agent respects wave dependencies (waits for wave N to finish before starting wave N+1), isolates parallel tasks in git worktrees, merges successful task branches back sequentially at the end of each wave, and updates taskmaster status after each wave completes. The user decides how failures/exhaustion should be handled.

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

```
mcp__mcp-manager__call_tool({
  "server": "taskmaster-ai",
  "tool_name": "get_tasks",
  "arguments": {
    "projectRoot": "{PROJECT_ROOT}",
    "tag": "{TAG}"
  }
})
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

### Step 4: Execute Tasks by Wave (Parallel within Wave, via adversarial-dev)

The main agent is the orchestrator. It does not delegate wave coordination to another skill — for each task it invokes the `adversarial-dev` skill directly (which itself spawns and manages the executor/evaluator agent pair), and directly waits on/aggregates results.

Process each wave in order. Within each wave, execute based on mode:

#### 4a. Per-Task Context Extraction

Before dispatching a task, build its self-contained context package:

- **Task object** (id, title, description, dependencies, verification criteria) from taskmaster.
- **Relevant excerpt** of spec.md/design.md scoped to that task (not the full files pasted verbatim unless small) — enough for the executor/evaluator to work without re-deriving context.
- **File references**: absolute paths to spec.md, design.md, and metadata.json, so the executor or evaluator can read the full files themselves if the excerpt isn't enough.

#### 4b. Wave-Based Execution Dispatch

**For PARALLEL waves (2+ tasks), capped at 3 concurrent tasks:**

1. Split the wave's tasks into batches of at most 3.
2. For each batch, invoke the `adversarial-dev` skill once per task, all in the same message block so they run concurrently:

   ```
   Skill({
     skill: "adversarial-dev",
     args: "Objective: run tlc-spec-driven mode=\"execute\" for task {TASK_ID} in feature tag \"{TAG}\".
       Task: {task object as JSON}
       Spec excerpt:\n{relevant spec.md section}
       Design excerpt:\n{relevant design.md section}
       Full file references: {spec.md path}, {design.md path}, {metadata.json path}
       Acceptance criteria: use the task's own verification criteria verbatim — do not invent new ones.
       Isolation: run the executor in an isolated git worktree (isolation: \"worktree\") since this task runs in a parallel wave; the evaluator must operate against the same worktree."
   })
   ```

3. Wait for every adversarial-dev invocation in the current batch to finish before starting the next batch. Wait for all batches in wave N before proceeding to wave N+1.

**For SEQUENTIAL waves (1 task or no wave metadata):**

Invoke `adversarial-dev` once for the task, same context package as above, but no worktree isolation is required (nothing else touches the working tree concurrently).

#### 4c. Post-Task Merge (PARALLEL waves only)

Once all tasks in a batch/wave have finished their adversarial-dev loop:

1. For each task that reached score 8+/10 (APPROVED), merge its worktree branch back into the working branch, one task at a time, in task order.
2. If a merge fails (conflict), invoke the `resolve-merge-conflicts` skill to resolve it before merging the next task's branch.
3. Tasks that did not reach APPROVED are not merged — handle per 4d.

#### 4d. Handle Wave Failures / Exhaustion

adversarial-dev does not prompt the user itself on exhaustion (10 iterations without score 8+) — it reports back to the orchestrator with the last score, verdict, and outstanding findings. The orchestrator intercepts that report and decides:

- Capture the task ID, last score, verdict, and outstanding findings.
- Ask user: **"[R]etry | [S]kip this task | [A]bort execution?"** via AskUserQuestion
- **Retry**: re-invoke `adversarial-dev` for the failed task (or the entire batch for PARALLEL waves, per user preference) — this starts a fresh 10-iteration loop, explicitly authorized by the user per adversarial-dev's own exhaustion contract.
- **Skip**: mark task as `"cancelled"` or `"deferred"` via set_task_status, continue to next task/wave. Its worktree (if any) is not merged.
- **Abort**: stop wave processing, return partial summary for Wave 0..N-1 only (only APPROVED, merged tasks count as done).

Log file for each task uses slug `{TAG}-{TASK_ID}` (per adversarial-dev's collision-proofing requirement for parallel invocations).

### Step 5: Update Taskmaster Status (Per-Wave)

After each wave N completes (all tasks in wave N have status), call set_task_status for each task:

```
mcp__mcp-manager__call_tool({
  "server": "taskmaster-ai",
  "tool_name": "set_task_status",
  "arguments": {
    "projectRoot": "{PROJECT_ROOT}",
    "id": "{TASK_ID}",
    "status": "{done|deferred|cancelled}",
    "tag": "{TAG}"
  }
})
```

**Critical**: Without `tag` parameter, call returns success but makes no actual change. With `tag`, updates both MCP backend AND `.taskmaster/tasks/tasks.json` file.

Status values: `"pending"`, `"in-progress"`, `"done"`, `"deferred"`, `"cancelled"`, `"blocked"`, `"review"`

**Status mapping:**

- Task's adversarial-dev score reached 8+/10 (APPROVED) and its worktree merged cleanly → status = `"done"`
- Task skipped (user choice, after exhaustion) → status = `"cancelled"` or `"deferred"`
- Task exhausted 10 iterations without APPROVED and not retried → status = `"blocked"` or `"deferred"`

A task never reaches `"done"` on tlc-spec-driven's own internal gate alone — the adversarial-dev score is the authoritative gate for status.

Do NOT wait until all waves complete to update status. Update after each wave finishes, so MCP state reflects progress incrementally.

**Handling failures within a wave:**

Failure recovery happens in Step 4d (before Step 5). By the time Step 5 runs, each task has a final status (done/cancelled/deferred/blocked). Step 5 simply syncs that status to taskmaster.

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
- The main agent is the orchestrator: it invokes `adversarial-dev` per task and never delegates wave coordination to another skill
- Each task's executor agent (inside adversarial-dev) runs `tlc-spec-driven mode="execute"` with the excerpted spec/design context plus file references for self-service lookups
- The evaluator agent grades against the task's own verification criteria — no separate criteria are invented
- A task is only `"done"` once adversarial-dev scores it 8+/10 (APPROVED)
- PARALLEL waves cap concurrency at 3 tasks per batch; each parallel task runs its executor in an isolated git worktree (`isolation: "worktree"`) to keep `git diff` scoping correct for the evaluator
- Merges of approved task worktrees happen sequentially at the end of each batch/wave, never mid-execution; conflicts are handled by the `resolve-merge-conflicts` skill
- On adversarial-dev exhaustion (10 iterations, no APPROVED), the orchestrator — not adversarial-dev — prompts the user with retry/skip/abort
- The user controls failure behavior (retry/skip/abort)
- Status updates use `set_task_status` MCP call with **`tag` parameter required** — without it, the call succeeds but makes no actual change
- Only the `status` field is updated in taskmaster, not logs or output
- Each task's adversarial-dev log lives at `<scratchpad>/adversarial-dev/{TAG}-{TASK_ID}/log.md`
- The summary shows what was completed; next actions remain user-directed
