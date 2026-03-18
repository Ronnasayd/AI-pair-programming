---
name: taskmaster-expand-task
description: "A skill for expanding existing task specifications with additional details and context. This skill takes a task specification in markdown format and generates an expanded version that includes more comprehensive information, examples, and clarifications to help users better understand the task requirements and expectations."
argument-hint: "[task_spec_path]: Path to task specification file. [task_id]: ID of task to expand. [task_tag] (optional): Tag context (default: 'master'). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute one of the following commands in your terminal:

```shell
# Basic usage (uses 'master' as default task_tag)
bash .github/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id}
bash $HOME/.gemini/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id}

# With custom task_tag
bash .github/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id} custom-tag
bash .github/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id} custom-tag --model="gpt-4"

# With additional options only (uses default 'master' tag)
bash .github/skills/expand-task-taskmaster/expand-task.sh {task_spec_path} {task_id} master --model="gpt-4"
```

All additional arguments (like `--model`, `--project-id`, etc.) are passed through to the task-master commands.
