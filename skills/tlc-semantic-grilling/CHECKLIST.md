1. Use `sequentialthinking` to break down the feature request into sub-questions (scope, constraints, edge cases, dependencies).
2. Next, use tools such as `rag-rat`, `serena`, `grep`, `Read`, or any other available tool to read files, perform a semantic search, and gather all necessary information from the codebase.
3. Conduct a `/grilling` session until you have obtained all the required information and clarified any questions with the user. Check for implicit requirements that were not listed and potential undefined issues.
4. Repeat steps 1 through 3 until you have a complete understanding of the problem and how it fits into the current context.
5. Execute the `/tlc-spec-driven` command for generate a plan.
6. Once `/tlc-spec-driven` finishes execution and the files have been generated, ask the user if they wish to register the feature in _taskmaster_. If the answer is "yes," use the `/tlc-tasks-to-taskmaster` skill—this derives tasks from the `tasks.md` file (if present) or, if the task generation step was skipped, creates a task for each requirement/acceptance criterion (AC) defined in `spec.md`.
7. Check the definitions in [docs-adr](.claude/skills/generate-docs/references/templates/docs-adr.md) and consider offering to create an ADR when the criteria are met.
