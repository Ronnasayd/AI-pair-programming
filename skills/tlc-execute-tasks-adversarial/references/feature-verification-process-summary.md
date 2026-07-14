# Feature Verification Process (Reference)

See the complete process in `@docs/feature-verification-process.md`.

## Quick Reference

### Tag Pattern

```text
Received tag: auto-null-cancellation
Expected structure:
  @.specs/features/<tag>/design.md ✓ (required)
  @.specs/features/<tag>/spec.md ✓ (required)
  @.taskmaster/execution/metadata.json ✓ (required)
  @.specs/features/<tag>/tasks.md ○ (optional, fallback)
```

### Taskmaster MCP API (get_tasks)

```bash
server: "taskmaster-ai"
tool_name: "get_tasks"
arguments: {
  "projectRoot": "/home/ronnas/develop/lingopass/lingospace-backend",
  "tag": "<TAG>"
}
```

**Schema:**

- `projectRoot` (required, string): project root path
- `tag` (optional, string): filter tasks by tag
- `status` (optional, string): filter by status
- `withSubtasks` (optional, boolean): include subtasks

**Expected Result:**

- Array of tasks: id, title, description, status, dependencies, metadata.wave
- Statistics: total, completed, pending, blocked
- Tag confirmed in the response

### Taskmaster MCP API (update_task_status)

```bash
server: "taskmaster-ai"
tool_name: "update_task_status"
arguments: {
  "projectRoot": "/home/ronnas/develop/lingopass/lingospace-backend",
  "taskId": "<TASK_ID>",
  "status": "completed|skipped|failed",
  "timestamp": "ISO-8601"
}
```

### Metadata JSON Structure

Expected fields in `@.taskmaster/execution/metadata.json`:

- `execution_waves`: array of task waves (T0, T1, T2...)
- `critical_path`: sequence of critical tasks
- `estimated_effort_hours`: total estimated hours
- `dependencies`: task dependency graph
- `complexity_label`: complexity label (simple/medium/complex)
- `test_commands`: array of test commands

### If Tag Is Not Found

If taskmaster returns an empty tasks array:

1. Check whether `@.specs/features/<tag>/tasks.md` exists
2. Parse it manually: extract T0, T1, T2... along with dependencies and waves
3. If neither exists, ask the user to verify the tag

---

For more details, see `@docs/feature-verification-process.md`.
