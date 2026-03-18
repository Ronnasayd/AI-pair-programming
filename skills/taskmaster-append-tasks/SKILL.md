---
name: taskmaster-append-tasks
description: "A skill for appending new tasks to an existing task specification in task-master. Use this skill to enhance and expand the original task specification with additional context, relevant files, code snippets, and a clear action plan for efficient task implementation. This skill is designed to ensure that any new information or requirements are seamlessly integrated into the existing task specification, maintaining a comprehensive and organized structure for task execution."
argument-hint: "[task_spec_path]: Path to task specification file. [task_tag] (optional): Tag to categorize appended tasks (default: 'master'). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute one of the following commands in your terminal:

```shell
# Basic usage (appends with 'master' tag)
bash .github/skills/taskmaster-append-tasks/append-tasks.sh {task_spec_path}
bash $HOME/.gemini/skills/taskmaster-append-tasks/append-tasks.sh {task_spec_path}

# With custom task_tag
bash .github/skills/taskmaster-append-tasks/append-tasks.sh {task_spec_path} custom-tag
bash .github/skills/taskmaster-append-tasks/append-tasks.sh {task_spec_path} custom-tag --model="gpt-4"

# With additional options only (uses default 'master' tag)
bash .github/skills/taskmaster-append-tasks/append-tasks.sh {task_spec_path} master --model="gpt-4"
```

All additional arguments (like `--model`, `--project-id`, etc.) are passed through to the task-master commands.
