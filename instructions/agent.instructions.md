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
- `README.md`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`

Load only the minimal required sections for the task domain.

## Rules to Avoid

- Editing without verifying current content first
- Assuming file paths without verification
- Assuming task status without querying current state first

## Rules to Follow

- Never rewrite everything — edit only specific segments
- Always read the applicable skills before specialized work
- Verify file existence and line numbers before making edits
- Organize task hierarchies by domain/theme, not sequential numbering
- Prefer expanding existing tasks over creating new ones
