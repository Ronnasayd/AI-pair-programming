---
name: taskmaster-create-task
description: "A skill for creating structured task specifications based on detailed analysis of the provided task description. Use this skill to generate comprehensive technical specifications that will serve as input for task-master, ensuring that all necessary context, relevant files, code snippets, and a clear action plan are included to facilitate efficient task implementation."
argument-hint: "[task_spec_path]: Path to task specification file. [task_tag] (optional): Tag to categorize tasks (default: 'master'). [additional_args]: Additional options to pass to task-master (e.g., --model='gpt-4')."
---

Execute the mcp tool `taskmaster-ai/add_task` with the parameters:
prompt(string): The integral content of the task specification file located at `task_spec_path`.
tag(string): The provided `task_tag` or 'master' if not specified.
research(boolean): true
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
