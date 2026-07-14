---
name: tlc-execute-tasks-adversarial
description: "Orchestrates feature task execution by tag. Main agent filters pending tasks from taskmaster, groups them into waves, and directly spawns/drives each task's own executor + evaluator agent pair (applying adversarial-dev's loop logic inline, not via a Skill call) within each wave, in parallel (capped concurrency), respecting wave dependencies. Each task's executor runs tlc-spec-driven with the task + spec context it's given; the evaluator grades against the task's own verification criteria. A task only counts as done at score 8+/10. Updates status via MCP after each wave completes. The user decides what to do on failures/exhaustion. Use: 'execute feature <tag>' or run tasks for <tag>. Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Execute Feature Tasks

Main agent acts as orchestrator AND directly manages the executor/evaluator agent pairs itself — it does not delegate coordination to the `adversarial-dev` skill via a `Skill` call. Instead, the orchestrator applies `adversarial-dev`'s own loop logic (`skills/adversarial-dev/SKILL.md` — read it once as reference before Step 4, not re-invoked per task) inline: for each task it spawns an executor agent (running `tlc-spec-driven` mode="execute") and an independent evaluator agent via the `Agent` tool directly, drives their iteration loop itself, and grades against the task's own verification criteria. A task is only marked done once the evaluator scores it 8+/10. Main agent respects wave dependencies (waits for wave N to finish before starting wave N+1), isolates parallel tasks in git worktrees, applies successful task diffs back sequentially at the end of each wave (uncommitted — the executor never commits, that's the user's call at the end), and updates taskmaster status after each wave completes. The user decides how failures/exhaustion should be handled.

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

### Step 4: Execute Tasks by Wave (Parallel within Wave, Direct Agent Spawn)

The main agent is the orchestrator AND the adversarial-loop driver. It does not delegate wave coordination, nor the executor/evaluator loop itself, to another skill call — for each task it spawns the executor and evaluator agents directly via the `Agent` tool, applying `adversarial-dev`'s loop mechanics (Steps 0-4 of `skills/adversarial-dev/SKILL.md`) inline, and directly waits on/aggregates results. Read `skills/adversarial-dev/SKILL.md` once before starting Step 4 to load the loop logic (spawn briefing, caveman-compressed agent communication, iteration/stagnation rules, scoring/verdict structure) — do not invoke it as a `Skill` call per task; that would spawn a redundant orchestrating layer on top of the agents this step already manages directly.

Process each wave in order. Within each wave, execute based on mode:

#### 4a. Per-Task Context Extraction

Before dispatching a task, build its self-contained context package:

- **Task object** (id, title, description, dependencies, verification criteria) from taskmaster.
- **Relevant excerpt** of spec.md/design.md scoped to that task (not the full files pasted verbatim unless small) — enough for the executor/evaluator to work without re-deriving context.
- **File references**: absolute paths to spec.md, design.md, and metadata.json, so the executor or evaluator can read the full files themselves if the excerpt isn't enough.
- **Scoped test/lint command**: derive a command narrower than metadata.json's module-wide `testCommands` (e.g. `testCommands.unit` filtered to the task's own target file(s)/pattern, not the whole module) whenever the task's target file(s) are known from the spec/design excerpt. Fall back to the module-wide command only when the task's own files can't be determined in advance. This is what executor and evaluator must run instead of the full suite — per adversarial-dev's caller-supplied-scope contract.
- **Expected file paths**: if spec.md/design.md names the file(s) the task should create/touch, list them explicitly so the executor doesn't need to `Glob`/explore to find them.
- **No-commit directive**: the executor must NOT run `git commit` — leave all changes staged/unstaged in its working tree/worktree. This overrides `tlc-spec-driven`'s own default of an atomic commit per task when it runs under this orchestrator. Committing is the user's call, done once at the end after reviewing the full feature.

#### 4a.5: Select Executor Model by Difficulty

Pick the executor's model before dispatch (evaluator is never affected — always its default, per adversarial-dev's own contract):

1. **Complexity source**: if the task carries a `metadata.complexity` (or equivalent effort/difficulty) field from taskmaster, use it. Otherwise infer from a cheap structural heuristic — no extra LLM call: count of requirements/subtasks, keywords suggesting broad scope ("refactor", "new architecture", "migrate"), estimated file count from the spec excerpt.
2. **Mapping (binary)**: trivial tasks (single small edit, narrow scope, no ambiguity) → `haiku`. Everything else (medium and hard) → `sonnet`. When in doubt, pick `sonnet` — a wrong haiku pick costs a full retry loop, which is more expensive than just using sonnet.
3. **Pass it along as free text** in the `adversarial-dev` call's `args` (e.g. "Executor model: haiku") — adversarial-dev only honors it if present; do not expect a structured parameter, and do not couple adversarial-dev's internals to this orchestrator.

This selection does not change the iteration cap (still fixed at 8, per adversarial-dev) and does not create new agent variants — only the `model` value passed to the executor changes.

#### 4b. Wave-Based Execution Dispatch

**For PARALLEL waves (2+ tasks), capped at 3 concurrent tasks:**

1. Split the wave's tasks into batches of at most 3.
2. For each task in the batch, the orchestrator itself spawns one executor + one evaluator via the `Agent` tool directly (per `adversarial-dev` Step 1), all agent spawns for the batch issued in the same message block so they run concurrently. The orchestrator — not a subordinate skill — then drives each task's iteration loop (per `adversarial-dev` Step 2-4: executor turn → evaluator turn → log → stagnation check → decide, up to 8 iterations) in parallel across the batch's tasks, using `SendMessage` to each agent's id for follow-up turns rather than re-spawning.

   Executor spawn (one per task):

   ```
   Agent({
     description: "Execute task {TASK_ID} ({TAG})",
     subagent_type: "general-purpose",
     model: {selected model from Step 4a.5, e.g. haiku or sonnet},
     isolation: "worktree",
     run_in_background: false,
     prompt: "Communicate in caveman-compressed style for your own prose (findings/reasoning) — code/diffs/commits stay normal syntax.
       Objective: run tlc-spec-driven mode=\"execute\" for task {TASK_ID} in feature tag \"{TAG}\".
       Task: {task object as JSON}
       Spec excerpt:\n{relevant spec.md section}
       Design excerpt:\n{relevant design.md section}
       Full file references: {spec.md path}, {design.md path}, {metadata.json path}
       Acceptance criteria: use the task's own verification criteria verbatim — do not invent new ones.
       Scoped test/lint command: {command from Step 4a} — use this exact command, never the full suite/module.
       Expected file paths: {file paths from Step 4a, if known} — use these instead of exploring to find them.
       No commits: never run git commit under any circumstance — leave changes staged/unstaged; the user commits at the end.
       Implement, do not self-review or self-grade — an independent evaluator will grade this."
   })
   ```

   Evaluator spawn (one per task, default model always — never honor the executor's model override):

   ```
   Agent({
     description: "Evaluate task {TASK_ID} ({TAG})",
     subagent_type: "general-purpose",
     run_in_background: false,
     prompt: "Communicate in caveman-compressed style for your own prose — findings/scores stay complete, only prose flavor is cut.
       You are adversarial QA for task {TASK_ID}. Never use Edit/Write/NotebookEdit. Find every reason this implementation is wrong or incomplete — do not soften findings, do not fix anything yourself.
       Acceptance criteria: {task's own verification criteria verbatim}
       Diff (primary source of truth): {git diff from the task's worktree}
       Scoped test/lint command: {same command given to the executor} — run against changed files only.
       Cap open-ended exploration to 2-3 extra reads, only when a criterion can't be checked from the diff alone.
       Return: qualitative findings per-criterion, objective lint/test pass-fail, a single score 0-10, verdict APPROVED(8-10)/CONDITIONAL(4-7)/REJECTED(0-3)."
   })
   ```

   Drive the loop per task exactly as `adversarial-dev` Step 2 describes: send the executor's diff/summary to the evaluator, log the iteration, check stagnation (score not improved + same core finding two rounds running → stop early), decide (score ≥8 → done; 4-7/0-3 and no stagnation → relay findings back to executor via `SendMessage`, next iteration; iteration 8 with score <8 → exhausted). Cap 8 iterations per task, same as `adversarial-dev`'s own contract.

3. Wait for every task's loop in the current batch to finish (each reaching APPROVED, exhausted, or stagnated) before starting the next batch. Wait for all batches in wave N before proceeding to wave N+1.

**For SEQUENTIAL waves (1 task or no wave metadata):**

Spawn the executor/evaluator pair and drive the loop the same way as above, but no worktree isolation is required (nothing else touches the working tree concurrently) — omit `isolation: "worktree"` on the executor spawn.

#### 4c. Post-Task Merge (PARALLEL waves only)

Once all tasks in a batch/wave have finished their executor/evaluator loop:

1. For each task that reached score 8+/10 (APPROVED), apply its worktree's changes back onto the working branch, one task at a time, in task order. Since the executor never commits (per the no-commit directive), there is no branch history to `git merge` — instead take the worktree's diff (`git -C <worktree> diff`, staged + unstaged) and apply it onto the working tree (e.g. `git apply`), leaving it staged/unstaged there too. Do not commit on the orchestrator's behalf either.
2. If applying a task's diff conflicts with changes already applied from an earlier task in the same wave, invoke the `resolve-merge-conflicts` skill to resolve it before applying the next task's diff.
3. Tasks that did not reach APPROVED are not applied — handle per 4d.

#### 4d. Handle Wave Failures / Exhaustion

The orchestrator itself does not auto-accept on exhaustion (8 iterations without score 8+) or on early stagnation (2 non-improving rounds on the same core issue) — since it drives the loop directly (no subordinate skill to report back to it), it hits Step 4 of the `adversarial-dev` logic itself and must pause there:

- Capture the task ID, last score, verdict, stop reason (`"cap reached"` vs `"stagnation"`), and outstanding findings.
- Ask user: **"[R]etry | [S]kip this task | [A]bort execution?"** via AskUserQuestion — if stop reason is `"stagnation"`, mention it: the criteria may need clarifying before a retry, not just another attempt.
- **Retry**: resume the same task's loop past the cap (or restart the entire batch for PARALLEL waves, per user preference) — explicitly authorized by the user, same as `adversarial-dev`'s own exhaustion contract.
- **Skip**: mark task as `"cancelled"` or `"deferred"` via set_task_status, continue to next task/wave. Its worktree (if any) is not merged.
- **Abort**: stop wave processing, return partial summary for Wave 0..N-1 only (only APPROVED, merged tasks count as done).

Log file for each task uses slug `{TAG}-{TASK_ID}` at `<scratchpad>/adversarial-dev/{TAG}-{TASK_ID}/log.md` (collision-proof across concurrent tasks, per `adversarial-dev`'s own Step 0 convention — reused here even though the orchestrator drives the loop itself).

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

- Task's adversarial-dev score reached 8+/10 (APPROVED) and its worktree diff applied cleanly → status = `"done"`
- Task skipped (user choice, after exhaustion) → status = `"cancelled"` or `"deferred"`
- Task exhausted 8 iterations (or stopped early on stagnation) without APPROVED and not retried → status = `"blocked"` or `"deferred"`

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
- The main agent IS both the orchestrator and the adversarial-loop driver: it spawns each task's executor + evaluator directly via `Agent`, applying `adversarial-dev`'s loop logic inline (read `skills/adversarial-dev/SKILL.md` once before Step 4 as reference) — it never issues a `Skill(adversarial-dev)` call per task
- Each task's executor agent runs `tlc-spec-driven mode="execute"` with the excerpted spec/design context plus file references for self-service lookups
- The evaluator agent grades against the task's own verification criteria — no separate criteria are invented
- A task is only `"done"` once the orchestrator's own loop scores it 8+/10 (APPROVED)
- PARALLEL waves cap concurrency at 3 tasks per batch; each parallel task runs its executor in an isolated git worktree (`isolation: "worktree"`) to keep `git diff` scoping correct for the evaluator
- Diffs of approved task worktrees are applied (not merged/committed) sequentially at the end of each batch/wave, never mid-execution; conflicts are handled by the `resolve-merge-conflicts` skill
- Executor never commits — this overrides `tlc-spec-driven`'s default atomic-commit-per-task behavior; all changes stay staged/unstaged through the whole run, and the user commits once at the end after reviewing the full feature
- On exhaustion (8 iterations, no APPROVED) or early stagnation (2 non-improving rounds on the same core issue), the orchestrator itself — since it drives the loop directly, no subordinate skill to report back — prompts the user with retry/skip/abort
- The user controls failure behavior (retry/skip/abort)
- Status updates use `set_task_status` MCP call with **`tag` parameter required** — without it, the call succeeds but makes no actual change
- Only the `status` field is updated in taskmaster, not logs or output
- Each task's log lives at `<scratchpad>/adversarial-dev/{TAG}-{TASK_ID}/log.md`
- Executor model is chosen per-task by difficulty (Step 4a.5): trivial → haiku, everything else → sonnet; evaluator always stays on its default model regardless of task difficulty
- The evaluator-scope directive (review from the diff, not open-ended exploration) is baked into the evaluator's own spawn prompt (Step 4b) — this is what actually bounds token cost per task, not wave concurrency (which already respects the 3-task cap correctly)
- Whatever the orchestrator already knows (target files, a scoped test/lint command narrower than the module-wide `testCommands`), it hands to executor/evaluator verbatim in Step 4a/4b — every fact re-derived by a subagent instead of handed to it is a wasted Read/Glob/Bash round
- Executor and evaluator run in caveman-compressed communication mode for their own prose (findings, reports, reasoning) — baked into `adversarial-dev`'s own Step 1 agent-spawn briefing, not something this orchestrator needs to pass per-call. Code/diffs/commit messages they write stay normal syntax; only their explanatory text is compressed. This shrinks the verdict/report text relayed between executor and evaluator each iteration, compounding over retries — it does not reduce Read/tool-result tokens, which the scoping rules above already handle.
- The summary shows what was completed; next actions remain user-directed
