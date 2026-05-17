---
name: taskmaster-expand-task
description: "A skill for expanding existing task specifications with additional details and context. This skill takes a task specification in markdown format and generates an expanded version that includes more comprehensive information, examples, and clarifications to help users better understand the task requirements and expectations."
argument-hint: "[task_spec_path]: Path to task specification file. [task_id]: ID of task to expand. [task_tag] (optional): Tag context (default: 'master'). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute the mcp tool `taskmaster-ai/expand_task` with the parameters:
prompt(string): The integral content of the task specification file located at `task_spec_path`.
id(string): The provided `task_id` to identify the task to expand.
tag(string): The provided `task_tag` or 'master' if not specified.
research(boolean): true
force(boolean): false
projectRoot(string): The root directory of the project, if applicable.
Add additional arguments (`additional_args`) if needed.

`