---
name: tcl-execute-tasks-by-orchestrate-taskmaster
description: Orchestrate the execution of tasks related to a specific tag using the taskmaster system.
argument-hint: "[tag] tag in taskmaster to get tasks related to that tag"
---

Use skills `tcl-spec-driven` and `orchestrate` to execute the tasks of [tag]
verify the files .specs/[tag]/spec.md,.specs/[tag]/design.md and .specs/[tag]/tasks.md if they exist.

get the tasks by calling mcp-manager:call_tool. You must pass as argument the tag and the projectRoot.

```js
  input: {
  "server": "taskmaster-ai",
  "tool_name": "get_tasks",
  "arguments": {
  "tag": "[tag]",
  "projectRoot": "[projectRoot]"
  }
}
```
parallelize the tasks delegation to subagents using the `orchestrate` skill. Each subagent will be responsible for executing one task. You must provide the subagent with the necessary information to execute the task, such as the task description, any relevant files, and the expected output.
when a subagent finish a task you must update the task status to "done".
