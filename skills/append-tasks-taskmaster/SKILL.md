---
name: append-tasks-taskmaster
description: "A skill for appending new tasks to an existing task specification in task-master. Use this skill to enhance and expand the original task specification with additional context, relevant files, code snippets, and a clear action plan for efficient task implementation. This skill is designed to ensure that any new information or requirements are seamlessly integrated into the existing task specification, maintaining a comprehensive and organized structure for task execution."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the docs/agents/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md."
---

Generate a {task_tag} for the new tasks being appended to the existing task specification. The {task_tag} should be a concise and descriptive identifier that categorizes the new tasks, making it easier to manage and track them within task-master. The {task_tag} will be used to label the appended tasks, allowing for efficient organization and retrieval of information related to those specific tasks in the future.
Execute one of the following commands in your terminal:

```shell
bash .github/skills/append-tasks-taskmaster/append-tasks.sh {task_spec_path} {task_tag}
bash $HOME/.gemini/skills/append-tasks-taskmaster/append-tasks.sh {task_spec_path} {task_tag}
```
