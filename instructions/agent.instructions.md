---
description: This file outlines the instructions for the agent's behavior, including documentation retrieval and mandatory rules to follow and avoid during task execution.
applyTo: "**/*"
---

## Enviroments

- Prefer `yarn`instead of `npm` for JavaScript/TypeScript projects, unless the project explicitly uses `npm`.
- For Python projects, prefer `pip` and `venv` for dependency management and virtual

## Documentation

Directories and files to search for context:

- `docs/**`
- `docs/agents/**`
- `docs/agents/specs/**`
- `docs/agents/plans/**`
- `docs/agents/reviews/**`
- `docs/adr/**`
- `docs/techs/**`
- `docs/misc/**`
- `docs/architecture.md`
- `docs/setup.md`
- `docs/usage.md`
- `docs/modules.md`
- `docs/contribution.md`
- `docs/faq.md`
- `docs/SUMMARY.md`
- `README.md`
- `GEMINI.md`
- `CLAUDE.md`

Retrieval process:

1. Determine the task domain.
2. Search the appropriate documentation directory.
3. Load only the minimal required sections.

## Mandatory: Rules to Avoid

- Over-Engineering in the First Iteration
- Creating Unsolicited Files
- Ignoring or Misinterpreting Feedback
- Not Verifying Current Content Before Editing
- Creating Documentation Structure When Not Requested
- Mixing Concepts
- Unnecessary Complexity in Logic
- Not Testing Requirements Against Results
- Rushing into implementation before specification is approved
- Merging code without full integration test validation
- Assuming file paths and locations without verification

## Mandatory: Rules toFollow

- List each requirement as a checklist
- Validate each requirement
- Make incremental adjustments based on feedback
- Never rewrite everything, only specific segments
- Always confirm current content before editing
- Create detailed specification BEFORE implementation
- Use agent orchestration to parallelize independent subtasks
- Establish clear checkpoints/gates between phases
- Define dependencies between subtasks explicitly
- Test edge cases before marking task complete
- Delegate specialized work to expert agents
- Verify file existence and line numbers in code references before making edits
- Keep functions focused and single-responsibility
