---
name: tlc-execute-tasks
description: "Orchestrates feature task execution by tag. Main agent filters pending tasks from taskmaster, groups them into waves, and directly spawns one subagent per task (via the Agent tool) within each wave, in parallel (capped at 3 concurrent), respecting wave dependencies. Each subagent runs tlc-spec-driven with the task + spec context it's given. Updates status via MCP after each wave completes. The user decides what to do on failures. Use: 'execute feature <tag>' or run tasks for <tag>. Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.1.0"
---

# Execute Feature Tasks

Main agent is the orchestrator: filters pending tasks, groups them into waves, and directly spawns one subagent per task within each wave via the Agent tool — never delegating coordination to another skill. Respects wave dependencies (wave N finishes before wave N+1 starts) and syncs taskmaster status after each wave. The user decides how failures are handled.

Use `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` to track wave/task progress alongside taskmaster MCP updates.

## Steps

| #   | Step                     | Action                                                                                                                                                                                                                                                                                    | Output / Gate                                                                                                                                                                |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Validate tag & load spec | Confirm `.specs/features/{TAG}/design.md`, `.specs/features/{TAG}/spec.md`, `.taskmaster/execution/metadata.json` all exist; read all 3 in parallel                                                                                                                                       | Missing file → report exact paths, stop. Otherwise extract: design (architecture/complexity/scope), spec (problem/goals/requirements), metadata (waves/critical path/effort) |
| 2   | Fetch pending tasks      | `mcp__mcp-manager__call_tool({server:"taskmaster-ai", tool_name:"get_tasks", arguments:{projectRoot, tag}})`; filter `status != "completed"`; sort by `metadata.wave` + dependency graph                                                                                                  | Ordered list of pending tasks                                                                                                                                                |
| 3   | Display plan             | Show tag, pending count, effort estimate, execution sequence T0→Tn                                                                                                                                                                                                                        | Ask user "Ready to execute {N} tasks? [yes/no]" via AskUserQuestion — no → abort                                                                                             |
| 3.5 | Build wave groups        | Group tasks by `metadata.wave` (no wave metadata → wave 0 / sequential). PARALLEL = 2+ tasks in wave; SEQUENTIAL = 1 task or no wave metadata or all sequential                                                                                                                           | Show wave breakdown, e.g. `Wave 0 (PARALLEL): T0, T1 — 2 tasks`                                                                                                              |
| 4   | Execute by wave          | PARALLEL (2+ tasks in wave): dispatch subagents in batches of ≤3 concurrent (see `references/orchestrator-model.md`, `references/agent-prompts.md`). SEQUENTIAL (1 task, no wave, or all sequential): main agent executes inline, no subagent. Wait for all of wave N before starting N+1 | Per-task status: Complete/Blocked/Partial + files changed + gate result                                                                                                      |
| 5   | Sync taskmaster status   | After each wave completes, call `set_task_status` per task with **`tag` required** (omitting it silently no-ops)                                                                                                                                                                          | done / cancelled / deferred / blocked synced incrementally, not batched at the end                                                                                           |
| 6   | Compile summary          | Report per-wave results + completed/skipped/failed counts                                                                                                                                                                                                                                 | See `references/examples.md` for full output format                                                                                                                          |

## Failure handling

On any task failure in wave N, ask the user **Retry / Skip / Abort** — see `references/orchestrator-model.md` for the full decision flow and status-mapping table.

## Reference files

- `references/agent-prompts.md` — verbatim Agent-call template used for every subagent dispatch
- `references/orchestrator-model.md` — wave dispatch rules, failure-handling flowchart, status sync details
- `references/examples.md` — full wave-parallel execution walkthrough with sample output
- `references/troubleshooting.md` — common failure symptoms and fixes
