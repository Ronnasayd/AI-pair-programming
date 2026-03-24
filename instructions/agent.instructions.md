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
- Do not manually analyze large code diffs (>1000 lines) in real-time without parallelizing work via specialist agents
- Do not assume task completion is the natural endpoint — reflect on whether the user would value retrospective or rule extraction
- Never assume task status without querying current state first — confirm done/pending before planning modifications
- Don't deploy bulk tool operations (MCP expand_task, etc.) without spot-checking 2–3 outputs — sample-verify before trusting bulk changes
- Don't mark parent task "done" while subtasks remain "pending" — establish task status semantics upfront (structure complete vs. work complete)
- Avoid one-task-per-component patterns for groups of related items — 50+ tasks are harder to navigate than 5-7 category tasks with subtasks
- Don't skip gap analysis before large task restructuring — identify missing coverage upfront to prevent rework

## Mandatory: Rules to Follow

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
- Always read the applicable SKILL.md file before starting specialized or complex work — skills contain tested workflows, format requirements, and tool guidance
- For analyses involving large code artifacts (>1000 lines), delegate to specialist agents via runSubagent rather than processing sequentially
- When delegating analysis or complex work to agents, provide explicit success criteria, category frameworks, and expected output structure
- After completing complex analysis tasks, proactively offer synthesis, retrospective, or rule extraction as a natural next step
- Include specific line references and code examples in all review findings — abstract concerns must be grounded in verifiable evidence
- Verify current task status (done/pending/in-progress) before modifying existing tasks — "done" tasks may be locked and prevent edits
- Use structured gap analysis matrices (category × component × task mapping) before bulk task operations — prevents missing coverage
- Organize complex task hierarchies by domain/theme rather than sequential numbering — matches developer mental models (Navigation, Chat, Forms)
- Generate before/after coverage metrics when modifying task structures — document components covered %, gaps resolved, remaining gaps
- Prefer expanding existing tasks to creating new ones for related components — keeps structure lean and reduces cognitive load
- Create PRDs or specifications BEFORE expanding unreviewed task structures — prevents wasted effort if scope changes
- When adding a new export to a module that has manual `jest.mock(...)` overrides in test files, audit every mock site and add the new export before running any test — partial mocks produce silent `undefined` runtime failures
- Before implementing a field that writes to both local DB and an external API payload, explicitly document which layer owns each representation — DB stores canonical value, external payload applies formatting
