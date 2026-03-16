---
name: create-task-taskmaster
description: "A skill for creating structured task specifications based on detailed analysis of the provided task description. Use this skill to generate comprehensive technical specifications that will serve as input for task-master, ensuring that all necessary context, relevant files, code snippets, and a clear action plan are included to facilitate efficient task implementation."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the docs/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md."
---

./create-task.sh docs/specs/dd-MM-YYYY-<description>.md
