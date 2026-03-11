---
name: append-tasks
description: "A skill for appending tasks to existing structured task specifications based on detailed analysis of the provided task description. Use this skill to generate comprehensive technical specifications that will serve as input for task-master, ensuring that all necessary context, relevant files, code snippets, and a clear action plan are included to facilitate efficient task implementation."
argument-hint: "[task_description]: A string containing the detailed description of the task to be analyzed and transformed into a structured technical specification document. Or a file path to a markdown file containing the task description."
---

MANDATORY: Use task-reviewer-specialist agent
MANDATORY: execute the **$0** argument as a task description and analyze it according to the system instructions.

Your objective is to analyze the task and produce a structured technical specification document that will later be used as input for task-master.

====================
PHASE 1 — CONTEXT DISCOVERY
====================

1. Search the @workspace to identify files, modules, documentation, and code relevant to the task.
2. Prioritize local documentation (\*.md files), starting from:
   - SUMMARY.md
   - docs/
3. Only search the web if:
   - The workspace does not contain sufficient information, OR
   - External documentation is clearly required (e.g., framework or library behavior).
4. When searching the web, prioritize official documentation and stable sources.

⚠️ Do NOT implement any code.
⚠️ Do NOT execute any terminal commands in this phase.

====================
PHASE 2 — SPECIFICATION GENERATION
====================

Based on your analysis, generate a task specification and save it as:

.taskmaster/specs/dd-MM-YYYY-<short-task-description>.md

You MUST strictly follow the format below. Do not add, remove, reorder, or rename sections.

  <format>
  <description>

## Problem Summary

## Relevant Files for Solving the Problem

## Relevant Code Snippets for Solving the Problem

## Proposed Action Plan for Task Implementation

## Testing Strategy for Validating the Implementation

## Context Map

```markdown
### Files to Modify

| File         | Purpose     | Changes Needed |
| ------------ | ----------- | -------------- |
| path/to/file | description | what changes   |

### Dependencies (may need updates)

| File        | Relationship                 |
| ----------- | ---------------------------- |
| path/to/dep | imports X from modified file |

### Test Files

| Test         | Coverage                     |
| ------------ | ---------------------------- |
| path/to/test | tests affected functionality |

### Reference Patterns

| File            | Pattern           |
| --------------- | ----------------- |
| path/to/similar | example to follow |

### Risk Assessment

- [ ] Breaking changes to public API
- [ ] Database migrations needed
- [ ] Configuration changes required
```

## Relevant Links (Optional)

  </description>

  <!--- THE FOLLOWING TEXT IS UNCHANGEABLE. --->
  <!--- DO NOT REWRITE, DO NOT CORRECT, DO NOT ADAPT. --->
  <!--- USE IT EXACTLY AS IT IS, CHARACTER BY CHARACTER. --->
  <!--- UNCHANGING_TEXT_START --->
  <workflow>
  - If documentation files or any other type of file are provided, extract relevant links and related files that may assist in implementing the task.
  - When creating a task or subtask, add references to relevant files or links that may assist in implementing the task.
  - Before each implementation step (tasks or subtasks), check relevant references and links. Perform a thorough review of relevant files and documents until you have a complete understanding of what needs to be done.
  - Add relevant code snippets that may assist in implementing the task in markdown format.
  - Check all *.md files starting from SUMMARY.md and docs/ to find relevant documentation.
  - Create and present a detailed action plan for executing the task implementation.
  - Ensure that changes are fully backward compatible and do not affect other system flows.
  - At the end of the implementation, show a summary of what was done and save it as a .md file in docs/features/dd-MM-YYYY-<description>/README.md
  </workflow>
  <!--- UNCHANGING_TEXT_END --->
  </format>

====================
PHASE 3 — USER REVIEW
====================

Ask the user to review the generated document.

- If the user suggests modifications or extensions, apply them to the same document.
- Repeat this step until the user explicitly confirms with a phrase equivalent to:
  "You can proceed."

Do NOT proceed without explicit confirmation.

====================
PHASE 4 — TASK-MASTER EXECUTION
====================

Ask the user to confirm if he wants to create one task or append multiple tasks.

Execute the following commands sequentially in the terminal:

1. task-master parse-prd --research --prompt="$(cat .taskmaster/specs/dd-MM-YYYY-<description>.md)" --append
2. task-master analyze-complexity
3. task-master expand --all --research --prompt="$(cat .taskmaster/specs/dd-MM-YYYY-<description>.md)"
