# Task Master Commands and Tools

## MCP Tools
These tools are available directly within the AI assistant's context:

- **get_tasks**: Retrieves the list of all tasks.
  - Parameters: `projectRoot`, `status` (optional), `tag` (optional).
- **next_task**: Finds the next task based on dependencies.
- **get_task**: Gets detailed info for a specific task ID.
- **set_task_status**: Updates task status.
  - Statuses: `pending`, `in-progress`, `done`, `deferred`, `cancelled`, `blocked`, `review`.
- **expand_task**: Breaks a task into subtasks.
- **update_subtask**: Adds info/research to a subtask.
- **parse_prd**: Generates tasks from a PRD file.
- **analyze_project_complexity**: Estimates effort and identifies risks.
- **research**: Performs live technical research.

## CLI Commands
If running from a terminal:

- `task-master init`: Initialize `.taskmaster/`
- `task-master parse-prd <file>`: Parse PRD
- `task-master list`: List tasks
- `task-master show <id>`: Show task details
- `task-master next`: Show next task
- `task-master move --from=<id> --to-tag=<tag>`: Change task status
- `task-master research "<query>"`: Run research
