---
name: create-task-taskmaster
description: "A skill for creating structured task specifications based on detailed analysis of the provided task description. Use this skill to generate comprehensive technical specifications that will serve as input for task-master, ensuring that all necessary context, relevant files, code snippets, and a clear action plan are included to facilitate efficient task implementation."
argument-hint: "[task_spec_path]: Path to task specification file. [task_tag] (optional): Tag to categorize tasks (default: 'master'). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute one of the following commands in your terminal:

```shell
# Basic usage (uses 'master' as default task_tag)
bash .github/skills/create-task-taskmaster/create-task.sh {task_spec_path}
bash $HOME/.gemini/skills/create-task-taskmaster/create-task.sh {task_spec_path}

# With custom task_tag
bash .github/skills/create-task-taskmaster/create-task.sh {task_spec_path} custom-tag
bash .github/skills/create-task-taskmaster/create-task.sh {task_spec_path} custom-tag --model="gpt-4"

# With additional options only (uses default 'master' tag)
bash .github/skills/create-task-taskmaster/create-task.sh {task_spec_path} master --model="gpt-4"
```

All additional arguments (like `--model`, `--project-id`, etc.) are passed through to the task-master commands.
