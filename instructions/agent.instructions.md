---
description: Agent behavior rules — documentation retrieval and task execution standards.
applyTo: "**/*"
---

## Environments

- Prefer `yarn` over `npm` for JavaScript/TypeScript projects unless the project explicitly uses `npm`.
- For Python projects, prefer `pip` and `venv`.

## Documentation

Directories to search for context:

- `docs/**`, `docs/agents/**`, `docs/agents/specs/**`, `docs/agents/plans/**`, `docs/agents/reviews/**`
- `docs/adr/**`, `docs/techs/**`, `docs/misc/**`
- `docs/architecture.md`, `docs/setup.md`, `docs/usage.md`, `docs/modules.md`
- `docs/contribution.md`, `docs/faq.md`, `docs/SUMMARY.md`
- `.taskmaster/tasks/*.md`
- `README.md`, `GEMINI.md`, `CLAUDE.md`

Load only the minimal required sections for the task domain.

## Rules to Avoid

- [ ] Editing without verifying current content first
- [ ] Assuming file paths without verification
- [ ] Assuming task status without querying current state first
- [ ] Running bulk tool operations without spot-checking 2–3 outputs first
- [ ] Marking parent task done while subtasks remain pending

## Rules to Follow

- [ ] List each requirement as a checklist and validate each item
- [ ] Never rewrite everything — edit only specific segments
- [ ] Always read the applicable SKILL.md before specialized work
- [ ] Create a detailed specification before implementation
- [ ] Verify file existence and line numbers before making edits
- [ ] Use agent orchestration to parallelize independent subtasks
- [ ] Define dependencies between subtasks explicitly
- [ ] Delegate large code artifacts (>1000 lines) to specialist agents with explicit success criteria
- [ ] Test edge cases before marking a task complete
- [ ] Include specific line references in all review findings
- [ ] Use structured gap analysis matrices before bulk task operations
- [ ] Organize task hierarchies by domain/theme, not sequential numbering
- [ ] Prefer expanding existing tasks over creating new ones
- [ ] Proactively offer synthesis or retrospective after complex tasks
