---
name: create-task-taskmaster
description: "A skill for creating structured task specifications based on detailed analysis of the provided task description. Use this skill to generate comprehensive technical specifications that will serve as input for task-master, ensuring that all necessary context, relevant files, code snippets, and a clear action plan are included to facilitate efficient task implementation."
argument-hint: "[task_spec_path]: A string containing the path to a markdown file with the task specification. The file should be located in the .taskmaster/specs/ directory and follow the naming convention dd-MM-YYYY-<description>.md."
---

Execute the following commands sequentially in the terminal:

1. export TASK_PROMPT="<spec_description>\n$(cat .taskmaster/specs/dd-MM-YYYY-<description>.md)\n</spec_description>\n<workflow_for_task_execution>"

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

1. task-master add-task --research --prompt="$TASK_PROMPT"
2. task-master analyze-complexity
3. task-master expand --all --research --prompt="$TASK_PROMPT"

=
