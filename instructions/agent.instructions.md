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
- `.taskmaster/tasks/*.md`
- `README.md`
- `GEMINI.md`
- `CLAUDE.md`

Retrieval process:

1. Determine the task domain.
2. Search the appropriate documentation directory.
3. Load only the minimal required sections.

## Rules to Avoid

- [ ] Over-engineering in the first iteration
- [ ] Creating unsolicited files
- [ ] Ignoring or misinterpreting feedback
- [ ] Editing without verifying current content first
- [ ] Creating documentation structure when not requested
- [ ] Mixing concepts
- [ ] Unnecessary complexity in logic
- [ ] Not testing requirements against results
- [ ] Rushing into implementation before spec is approved
- [ ] Merging code without full integration test validation
- [ ] Assuming file paths without verification
- [ ] Manually analyzing large diffs (>1000 lines) without parallelizing
- [ ] Assuming task completion is the natural endpoint — offer retrospective
- [ ] Assuming task status without querying current state first
- [ ] Running bulk tool operations without spot-checking 2–3 outputs first
- [ ] Marking parent task done while subtasks remain pending
- [ ] One-task-per-component patterns for groups of related items
- [ ] Skipping gap analysis before large task restructuring

## Rules to Follow

- [ ] List each requirement as a checklist
- [ ] Validate each requirement
- [ ] Make incremental adjustments based on feedback
- [ ] Never rewrite everything — only specific segments
- [ ] Always confirm current content before editing
- [ ] Create detailed specification before implementation
- [ ] Use agent orchestration to parallelize independent subtasks
- [ ] Establish clear checkpoints/gates between phases
- [ ] Define dependencies between subtasks explicitly
- [ ] Test edge cases before marking task complete
- [ ] Delegate specialized work to expert agents
- [ ] Verify file existence and line numbers before making edits
- [ ] Keep functions focused and single-responsibility
- [ ] Always read the applicable SKILL.md before specialized work
- [ ] Delegate large code artifacts (>1000 lines) to specialist agents
- [ ] Provide explicit success criteria when delegating to agents
- [ ] Proactively offer synthesis or retrospective after complex tasks
- [ ] Include specific line references in all review findings
- [ ] Verify task status before modifying existing tasks
- [ ] Use structured gap analysis matrices before bulk task operations
- [ ] Organize task hierarchies by domain/theme, not sequential numbering
- [ ] Generate before/after coverage metrics when modifying task structures
- [ ] Prefer expanding existing tasks over creating new ones
- [ ] Create PRDs or specs before expanding unreviewed task structures
