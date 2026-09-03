---
name: sd-planning
description: step-by-step guide to generating a plan.
---

# Steps

Add the following steps as tasks using the `TaskCreate`, `TaskUpdate`, `TaskGet`, and `TaskList` tools. Update the status as you progress through each step to keep the user informed.

1. Repeat these steps until you have a complete understanding of the problem and how it fits into the current context. When you feel the loop should end because you have sufficient context, ask the user if they wish to finish or continue refining issues before creating the plan.

1.1. Use `sequentialthinking` in `mcp-manager` to break down the feature request into sub-issues (scope, constraints, edge cases, dependencies).
1.2. Next, use tools such as `rag-rat`, `serena`, `grep`, `Read`, or any other available tool to read files, perform a semantic search, and gather all necessary information from the codebase.
1.3. Conduct a `/grilling` session until you have obtained all necessary information and clarified any doubts with the user. Check for unlisted implicit requirements and potential undefined issues.

2. Execute the `/tlc-spec-driven` skill to generate a plan based on the described problem.
3. Execute the `/spec-to-requirements-table` skill to generate a `requirements.md` file.
4. Once planning is complete, ask the user if they wish to register the feature in _taskmaster_. If the answer is "yes," use the `/sd-insert-taskmaster` skill.
5. Check the definitions in [docs-adr](./references/docs-adr.md) and consider offering to create an ADR when the criteria are met.
6. At the end of the session, evaluate whether there is anything worth saving as permanent memory. Save as permanent memory only what the next session will need and cannot rediscover by reading the code, Git, or CLAUDE.md—such as the _reason_ behind a decision, a non-obvious invariant, or a user preference; if it is already in the repo or only matters for this specific conversation, do not save it. Use the `ai-memory-durable-pages` skill to persist it.
