1. Repeat this steps until you have a complete understanding of the problem and how it fits into the current context.

   1.1. Use `sequentialthinking` in `mcp-manager` to break down the feature request into sub-questions (scope, constraints, edge cases, dependencies).
   1.2. Next, use tools such as `rag-rat`, `serena`, `grep`, `Read`, or any other available tool to read files, perform a semantic search, and gather all necessary information from the codebase.
   1.3. Conduct a `/grilling` session until you have obtained all necessary information and clarified any doubts with the user. Check for unlisted implicit requirements and potential undefined issues.

2. Execute the `/tlc-spec-driven` skill to generate a plan based on the described problem.
3. Once planning is complete, ask the user if they wish to register the feature in _taskmaster_. If the answer is "yes," use the `/tlc-tasks-to-taskmaster` skill.
4. Check the definitions in [docs-adr](./references/docs-adr.md) and consider offering to create an ADR when the criteria are met.
