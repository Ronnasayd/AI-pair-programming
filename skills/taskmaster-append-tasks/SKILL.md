---
name: taskmaster-append-tasks
description: "A skill for appending new tasks to an existing task specification in task-master. Use this skill to enhance and expand the original task specification with additional context, relevant files, code snippets, and a clear action plan for efficient task implementation. This skill is designed to ensure that any new information or requirements are seamlessly integrated into the existing task specification, maintaining a comprehensive and organized structure for task execution."
argument-hint: "[task_spec_path]: Path to task specification file. [task_tag] (optional): Tag to categorize appended tasks (default: 'master'). [num_tasks] (optional): Number of tasks to create (default: 5). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute the mcp tool `taskmaster-ai/parse_prd` with the parameters:
input(string): The filepath specified at `task_spec_path`.
tag(string): The provided `task_tag` or 'master' if not specified.
research(boolean): true
force(boolean): false
append(boolean): true
numTasks(string): use the provided `num_tasks` or default to 5.
projectRoot(string): The root directory of the project, if applicable.
Add additional arguments (`additional_args`) if needed.

Execute the mcp tool `taskmaster-ai/analyze_project_complexity` with the parameters:
prompt(string): The integral content of the task specification file located at `task_spec_path`.
tag(string): The provided `task_tag` or 'master' if not specified.
ids(string): The IDs of the tasks created in the previous step.
research(boolean): true
threshold(integer): 5
projectRoot(string): The root directory of the project, if applicable.
Add additional arguments (`additional_args`) if needed.

