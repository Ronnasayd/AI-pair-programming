# Main-Agent-as-Orchestrator Model

Main agent is both orchestrator AND adversarial-loop driver — no `Skill(adversarial-dev)` call per task. It applies `adversarial-dev`'s Step 0-4 loop mechanics inline via direct `Agent`/`SendMessage` calls.

```mermaid
flowchart TD
    A[Fetch pending tasks] --> B[Group by metadata.wave]
    B --> C{Wave mode?}
    C -->|2+ tasks| D[PARALLEL: batch ≤3, spawn executor+evaluator per task]
    C -->|1 task / no wave| E[SEQUENTIAL: spawn pair, no worktree]
    D --> F[Drive each task's loop: exec→eval→log→stagnation check]
    E --> F
    F --> G{score ≥8?}
    G -->|yes| H[APPROVED]
    G -->|no, cap/stagnation| I[Ask user: Retry/Skip/Abort]
    H --> J[Apply worktree diff to working tree, sequential]
    I -->|retry| F
    I -->|skip| K[status=cancelled/deferred]
    I -->|abort| L[stop, partial summary]
    J --> M[set_task_status per wave, tag required]
    K --> M
    M --> N{more waves?}
    N -->|yes| B
    N -->|no| O[Final summary]
```

## Per-task context package (built before dispatch)

| Field                | Source                                                                  |
| -------------------- | ----------------------------------------------------------------------- |
| Task object          | taskmaster (id, title, description, deps, verification criteria)        |
| Spec/design excerpt  | scoped to the task, not full files                                      |
| File references      | absolute paths to spec.md/design.md/metadata.json                       |
| Scoped test/lint cmd | narrower than module-wide `testCommands`, derived from task's own files |
| Expected file paths  | from spec/design if named                                               |
| No-commit directive  | executor never commits — overrides tlc-spec-driven default              |

## Executor model selection (Step 4a.5)

| Complexity                                | Model                                                                |
| ----------------------------------------- | -------------------------------------------------------------------- |
| trivial (single small edit, no ambiguity) | haiku                                                                |
| medium/hard/unclear                       | sonnet (default when in doubt — wrong haiku pick costs a full retry) |

Evaluator always uses default model, never the executor's override.

## Notes

- PARALLEL batches capped at 3 concurrent tasks; each parallel task's executor runs in an isolated git worktree.
- Diffs of APPROVED tasks are applied (`git apply`, staged/unstaged, never committed) sequentially at end of wave/batch; conflicts → `resolve-merge-conflicts` skill.
- `set_task_status` requires `tag` param — without it, call succeeds but changes nothing.
- Status update happens per-wave, not batched to the end.
