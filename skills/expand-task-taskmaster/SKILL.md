---
name: expand-task-taskmaster
description: "A skill for expanding existing task specifications with additional details and context. This skill takes a task specification in markdown format and generates an expanded version that includes more comprehensive information, examples, and clarifications to help users better understand the task requirements and expectations."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the docs/agents/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md,[task_id]: A string containing the ID of the task to be expanded. This ID should correspond to an existing task in the Task Master system that you want to expand with additional details and context."
---

Execute one of the following commands in your terminal:

```shell
bash .github/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id}
bash $HOME/.gemini/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id}
```
