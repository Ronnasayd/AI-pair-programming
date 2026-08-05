# Agent Prompt Template

Used for every executor dispatch (PARALLEL or SEQUENTIAL wave). Each executor is self-contained — no access to the orchestrator's conversation, so pass everything, including its worktree path. The orchestrator has already read `tlc-spec-driven/SKILL.md` and built this task's context-map; the executor receives only the curated excerpts below, never the full spec files, and never calls `Skill(tlc-spec-driven)` itself.

```
Agent({
  description: "Execute {TASK_ID} for {TAG}",
  prompt: "Implement task {TASK_ID} for feature tag \"{TAG}\" following the execution conventions below (atomic commits, verification-criteria-driven, no scope beyond the task).
    Working directory: isolated worktree at {WORKTREE_PATH}, branched off run branch {RUN_BRANCH}.
    Task: {task object as JSON, from tasks.md section for this task}
    Spec excerpt (scoped to this task):\n{relevant spec.md section}
    Design excerpt (scoped to this task):\n{relevant design.md section}
    Relevant source excerpts:\n{excerpts of files this task touches, located via grep/glob}
    Verification criteria: use the task's own criteria verbatim — do not invent new ones.
    Implement the task in this worktree only. Do not merge, push, or touch branches outside this worktree.
    Report back: status (Complete/Blocked/Partial), diff produced, gate result, and any errors."
})
```

- PARALLEL wave: send one Agent call per task, each pointed at its own worktree, all in the same message block, so they run concurrently.
- SEQUENTIAL wave: one Agent call per task, own worktree — never inline main-agent execution, run one task at a time.
- `metadata.json` is orchestrator-only — never pass it to the executor.
- The orchestrator (not the executor) merges the task branch onto the run branch via `git merge --no-ff`, in task order, after approval.
