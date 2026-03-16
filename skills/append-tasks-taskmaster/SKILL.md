---
name: append-tasks-taskmaster
description: "A skill for appending new tasks to an existing task specification in task-master. Use this skill to enhance and expand the original task specification with additional context, relevant files, code snippets, and a clear action plan for efficient task implementation. This skill is designed to ensure that any new information or requirements are seamlessly integrated into the existing task specification, maintaining a comprehensive and organized structure for task execution."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the docs/agents/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md."
---

Execute one of the following commands in your terminal:

```shell
bash .github/skills/append-tasks-taskmaster/append-tasks.sh {task_spec_path}
bash $HOME/.gemini/skills/append-tasks-taskmaster/append-tasks.sh {task_spec_path}
```
