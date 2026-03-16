---
name: append-tasks-taskmaster
description: "A skill for appending new tasks to an existing task specification in task-master. Use this skill to enhance and expand the original task specification with additional context, relevant files, code snippets, and a clear action plan for efficient task implementation. This skill is designed to ensure that any new information or requirements are seamlessly integrated into the existing task specification, maintaining a comprehensive and organized structure for task execution."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the docs/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md."
---

Execute the following commands sequentially in the terminal:

1. export TASK_PROMPT="<spec_description>\n$(cat docs/specs/dd-MM-YYYY-<description>.md)\n</spec_description>\n<workflow_for_task_execution>"

- If documentation files or any other type of file are provided, extract relevant links and related files that may assist in implementing the task.
- When creating a task or subtask, add references to relevant files or links that may assist in implementing the task.
- Before each implementation step (tasks or subtasks), check relevant references and links. Perform a thorough review of relevant files and documents until you have a complete understanding of what needs to be done.
- Use code references (file#L123-L456) in the \"Key Code References\" section instead of full code snippets
- Include code snippets ONLY when demonstrating new patterns not present in the codebase
- Describe tests using comparison tables (test cases, inputs, expected outputs) instead of code blocks
- Use matrices and tables for scenarios instead of narrative descriptions
- Check all \*.md files starting from SUMMARY.md and docs/ to find relevant documentation.
- Create and present a detailed action plan for executing the task implementation.
- Ensure that changes are fully backward compatible and do not affect other system flows.
  </workflow_for_task_execution>""

1. task-master parse-prd --research --prompt="$TASK_PROMPT" --append
2. task-master analyze-complexity
3. task-master expand --all --research --prompt="$TASK_PROMPT"
