---
name: tlc-execute-tasks-adversarial
description: "Orchestrates feature task execution by tag. Main agent filters pending tasks from taskmaster, groups them into waves, and directly spawns/drives each task's own executor + evaluator agent pair (applying adversarial-dev's loop logic inline, not via a Skill call) within each wave, in parallel (capped concurrency), respecting wave dependencies. Each task's executor runs tlc-spec-driven with the task + spec context it's given; the evaluator grades against the task's own verification criteria. A task only counts as done at score 8+/10. Updates status via MCP after each wave completes. The user decides what to do on failures/exhaustion. Use: 'execute feature <tag>' or run tasks for <tag>. Do not use for direct task management (taskmaster skill) or spec creation (tlc-spec-driven)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.1.0"
---

# Execute Feature Tasks (Adversarial)

Main agent is orchestrator **and** adversarial-loop driver — spawns each task's executor + evaluator directly via `Agent`, applies `adversarial-dev`'s loop mechanics inline (read `skills/adversarial-dev/SKILL.md` once before Step 4, never a per-task `Skill` call). A task is `"done"` only at evaluator score 8+/10. Full dispatch model + diagram: `references/orchestrator-model.md`.

## Steps

| #   | Step                 | Input                                                                                                                      | Output / Gate                                                  |
| --- | -------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Validate & load      | `.specs/features/{TAG}/{spec,design}.md`, `.taskmaster/execution/metadata.json`                                            | abort if any missing; else summary of what loads               |
| 2   | Fetch pending tasks  | `mcp-manager call_tool(taskmaster-ai, get_tasks, {projectRoot, tag})`                                                      | filter `status != completed`, sort by wave + deps              |
| 3   | Show plan, confirm   | wave breakdown                                                                                                             | AskUserQuestion yes/no — no → abort                            |
| 3.5 | Build wave groups    | `metadata.wave` per task                                                                                                   | PARALLEL (2+ tasks/wave) vs SEQUENTIAL (1 task / no wave meta) |
| 4   | Execute waves        | see below; use `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` to track wave/task progress alongside taskmaster MCP updates | each task → done/cancelled/deferred/blocked                    |
| 5   | Sync status per wave | `set_task_status(..., tag)` — **tag required or no-op**                                                                    | taskmaster + tasks.json updated incrementally                  |
| 6   | Summary              | per-wave results                                                                                                           | user-directed next step                                        |

## Step 4: per-wave execution

- **PARALLEL** wave: batch ≤3 tasks concurrently. For each task, build context package (Step 4a) → pick executor model (Step 4a.5) → spawn executor (isolated worktree) + evaluator via `Agent` (templates: `references/agent-prompts.md`) → drive loop (exec→eval→log→stagnation-check→decide, cap 8 iter, per `adversarial-dev` Steps 2-4). Wait for whole batch before next batch; whole wave before next wave.
- **SEQUENTIAL** wave (1 task / no wave meta): same pair + loop, no worktree isolation needed.

**4a context package**: task object, scoped spec/design excerpt, file paths (spec/design/metadata), scoped test/lint cmd (narrower than module-wide), expected file paths if known, no-commit directive (executor never `git commit` — user commits once at the end).

**4a.5 model pick**: trivial task → `haiku`; everything else / unclear → `sonnet` (wrong haiku guess costs a full retry, so default sonnet). Evaluator always stays on default model.

**4c merge**: for each APPROVED task, apply its worktree diff (`git apply`, staged/unstaged, never committed) onto the working tree, sequentially in task order. Conflict → `resolve-merge-conflicts` skill.

**4d failure handling** — the orchestrator hits this itself (no subordinate skill to bounce back to it):

| Stop reason                                              | Action                                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------------------ |
| score ≥8                                                 | APPROVED, done                                                           |
| exhausted (8 iterations, no 8+)                          | ask user Retry / Skip / Abort                                            |
| stagnation (2 rounds, same core finding, no improvement) | ask user Retry / Skip / Abort — mention criteria may need clarifying     |
| Retry                                                    | resume same task's loop past cap (or restart batch for PARALLEL)         |
| Skip                                                     | `set_task_status` → cancelled/deferred, continue                         |
| Abort                                                    | stop wave processing, partial summary (only merged APPROVED tasks count) |

Log per task: `<scratchpad>/adversarial-dev/{TAG}-{TASK_ID}/log.md`.

## Reference files

- `references/orchestrator-model.md` — dispatch flowchart, context-package fields, model-selection table
- `references/agent-prompts.md` — executor/evaluator spawn templates
- `references/examples.md` — full wave-parallel walkthrough
- `references/troubleshooting.md` — error cases and recovery
