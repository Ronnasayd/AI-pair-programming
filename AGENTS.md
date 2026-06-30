<!-- INIT AUTO-CONTEXT -->


## Environments

- JS/TS: use `yarn`, not `npm`, unless project says `npm`.
- Python: use `pip` + `venv`.
- Multi-language versions: use `asdf` when fit.

## Always Use Interactive Question Tools

For every user question, use interactive question tool. No exceptions for context, type, or intent.

Use this for clarifications, options, confirmations, preference checks, all user interactions.

- **Claude**: Use `AskUserQuestion`
- **Other environments**: Use equivalent interactive question tools available in your context
- **Fallback**: if no interactive tools exist, use labeled options (A, B, C... Z)

If interactive tool exists, never ask plain-text question.

## Code style

- Functions: 4-20 lines. Split if longer.
- Files: under 500 lines. Split by responsibility.
- One thing per function, one responsibility per module (SRP).
- Names: specific and unique. Avoid `data`, `handler`, `Manager`.
  Prefer names that return <5 grep hits in the codebase.
- Types: explicit. No `any`, no `Dict`, no untyped functions.
- No code duplication. Extract shared logic into a function/module.
- Early returns over nested ifs. Max 2 levels of indentation.
- Exception messages must include the offending value and expected shape.

## Comments

- Keep your own comments. Don't strip them on refactor — they carry
  intent and provenance.
- Write WHY, not WHAT. Skip `// increment counter` above `i++`.
- Docstrings on public functions: intent + one usage example.
- Reference issue numbers / commit SHAs when a line exists because
  of a specific bug or upstream constraint.

## Tests

- Tests run with a single command: `<project-specific>`.
- Every new function gets a test. Bug fixes get a regression test.
- Mock external I/O (API, DB, filesystem) with named fake classes,
  not inline stubs.
- Tests must be F.I.R.S.T: fast, independent, repeatable,
  self-validating, timely.

## Dependencies

- Inject dependencies through constructor/parameter, not global/import.
- Wrap third-party libs behind a thin interface owned by this project.

## Structure

- Follow the framework's convention (Rails, Django, Next.js, etc.).
- Prefer small focused modules over god files.
- Predictable paths: controller/model/view, src/lib/test, etc.

## Formatting

- Use the language default formatter (`cargo fmt`, `gofmt`, `prettier`,
  `black`, `rubocop -A`). Don't discuss style beyond that.

## Logging

- Structured JSON when logging for debugging / observability.
- Plain text only for user-facing CLI output.

## Context-Specific Rules

The following rules apply to specific file types:
- [code.instructions](.claude/instructions/code.instructions.md) — applies to: `**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx`
<!-- END AUTO-CONTEXT -->

## Project Architecture

**AI Pair Programming Workspace** — toolkit for enhancing AI-assisted development. Centralizes agent personas, skills, and structured workflows.

### Core Components

- **MCP Servers** (`src/mcps/`, `src/my_mcp_server.py`): FastMCP-based tools for codebase context, code review, documentation sync, semantic search. Supports MongoDB, MySQL, PostgreSQL, SQLite.
- **Agents** (`agents/`): Persona definitions (developer-specialist, cybersecurity-specialist, etc.) with behavioral instructions.
- **Skills** (`skills/`): Reusable capabilities (workflows, guides, analysis patterns).
- **Instructions** (`instructions/`): Domain-specific rules (code style, testing, React patterns, etc.).

### Directory Reference

```
src/            MCP servers, utilities, copilot proxy
agents/         Agent persona YAML/markdown definitions
skills/         Skill files (workflows, style guides)
instructions/   Domain-specific rules and conventions
scripts/        Installation and environment setup
commands/       CLI command definitions
hooks/          Git and event-driven automation
docs/           Project documentation
```

## Key Technologies

- **Python 3.11+** with Poetry for dependency management
- **FastMCP**: Model Context Protocol server framework
- **pytest**: Test framework (async mode enabled)
- **Node.js/TypeScript**: Supported for various project types
- **Bash**: Installation and environment scripts

## Quick Start Commands

Install and setup:

```bash
poetry install                  # Install Python dependencies
./install.sh [--all|--claude]   # Set up symlinks and configurations
```

Run tests:

```bash
cd src && pytest                     # Run all tests
pytest src/copilot/test_*.py         # Run Copilot tests
```

Run MCP servers:

```bash
poetry run mongodb-mcp              # MongoDB server
poetry run mysql-mcp                # MySQL server
poetry run postgresql-mcp           # PostgreSQL server
poetry run sqlite-mcp               # SQLite server
python src/my_mcp_server.py         # Main MCP server
```

Development workflow:

1. Check `instructions/` for domain-specific rules (code style, testing patterns, framework conventions).
2. Track changes in `.taskmaster/` as tasks for significant work.
3. Use focused edits — prefer targeted replacements over full rewrites.
4. Validate via linting, type checking, or running the MCP server.
