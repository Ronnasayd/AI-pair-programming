# Agent Prompt Template

Used for every subagent dispatch (PARALLEL or SEQUENTIAL wave). Each subagent is self-contained — no access to the orchestrator's conversation, so pass everything.

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

- PARALLEL wave: send one Agent call per task, all in the same message block, so they run concurrently.
- SEQUENTIAL wave: call Agent once with the same prompt shape.
- `metadata.json` is orchestrator-only — never pass it to the subagent.
