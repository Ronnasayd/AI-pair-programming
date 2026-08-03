# Agent Prompt Template

Used for every executor dispatch (PARALLEL or SEQUENTIAL wave). Each executor is self-contained — no access to the orchestrator's conversation, so pass everything, including its worktree path.

```
Agent({
  description: "Execute {TASK_ID} for {TAG}",
  prompt: "Run the tlc-spec-driven skill with mode=\"execute\" for task {TASK_ID} in feature tag \"{TAG}\".
    Working directory: isolated worktree at {WORKTREE_PATH}, branched off run branch {RUN_BRANCH}.
    Task: {task_0 object as JSON}
    Full spec.md:\n{spec.md content}
    Full design.md:\n{design.md content}
    Implement the task in this worktree only. Do not merge, push, or touch branches outside this worktree.
    Report back: status (Complete/Blocked/Partial), diff produced, gate result, and any errors."
})
```

- PARALLEL wave: send one Agent call per task, each pointed at its own worktree, all in the same message block, so they run concurrently.
- SEQUENTIAL wave: one Agent call per task, own worktree — never inline main-agent execution, run one task at a time.
- `metadata.json` is orchestrator-only — never pass it to the executor.
- The orchestrator (not the executor) applies the resulting diff onto the run branch via `git apply`, in task order, after approval.
