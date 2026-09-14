<!-- INIT AUTO-CONTEXT -->

## Environments

JS/TS: `yarn`, not `npm`, unless project says otherwise. Python: `pip` + `venv`.

## Always Use Interactive Question Tools

Every user question → interactive tool, never plain text. Claude:
`AskUserQuestion`. Multiple questions: `grilling` skill.

## Task Tracking

When task list exists (multi-step work), use `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` to give user feedback. Mark tasks complete as done, don't batch.

## Code style

Standard conventions apply (SRP, early returns, no duplication, explicit
types). Repo-specific deviations only:

- Names: specific and unique. Avoid `data`, `handler`, `Manager`.
  Prefer names that return <5 grep hits in the codebase.
- Exception messages must include the offending value and expected shape.
  Why: past debugging sessions wasted time on bare `ValueError` with no
  context — see git history on `src/mcps/`.

## Comments

Keep own comments on refactor — they carry intent/provenance. Beyond that,
standard WHY-not-WHAT applies.

## Tests

- Tests run with a single command: `<project-specific>`.
- Mock external I/O (API, DB, filesystem) with named fake classes,
  not inline stubs.
  Why: inline stubs drift silently from the real interface; a named
  fake class fails loudly when the real dependency's contract changes.

## Relevant Skills

| When                                                   | Use                                          |
| ------------------------------------------------------ | -------------------------------------------- |
| Creating/editing a skill under `skills/`               | `skill-creator` / `skill-architect`          |
| New skill's description doesn't trigger reliably       | `skill-description-generator`                |
| Writing a commit message                               | `semantic-commit-message` / `caveman-commit` |
| Opening a PR                                           | `generate-pr-description`                    |
| Unsure about git workflow (rebase, branch strategy)    | `git-guide` / `git-workflow`                 |
| Break big/complex problem into sub-problems            | `dynamic-programming-analysis`               |
| Generate/update project docs from code or diff         | `generate-docs`                              |
| Write PR description from diff/commits                 | `generate-pr-description`                    |
| Review a PR                                            | `pr-review`                                  |
| Resolve merge conflicts                                | `resolve-merge-conflicts`                    |
| Execute tasks for a spec-driven feature (taskmaster)   | `sd-execute`                                 |
| Generate a plan step-by-step                           | `sd-planning`                                |
| Build requirements review table from spec/design/tasks | `spec-to-requirements-table`                 |
| Pick between technical options (pros/cons)             | `technical-decision-helper`                  |

## Context-Specific Rules

The following rules apply to specific file types:

- [code.instructions](.claude/instructions/code.instructions.md) — applies to: `**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx`

<!-- END AUTO-CONTEXT -->

## Project Architecture

**AI Pair Programming Workspace** — toolkit for enhancing AI-assisted development. Centralizes agent personas, skills, and structured workflows.

### Core Components

- **MCP Servers** (`src/mcps/`): FastMCP-based tools — `skill_loader_mcp.py`, `search_engine.py` (semantic search). Registered proxies (DB, GitHub, Figma, etc.) are routed through `mcp-manager` and configured in `.mcp.json`.
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

- **Python 3.11+** with `uv` for dependency management (`uv.lock` at root; `src/` builds with setuptools)
- **FastMCP** (`fastmcp>=2.0`): Model Context Protocol server framework
- **pytest**: Test framework (`asyncio_mode = "auto"`)
- **Node.js/TypeScript**: Supported for various project types
- **Bash**: Installation and environment scripts

## Quick Start Commands

Install and setup:

```bash
uv sync                         # Install root Python deps (hook scripts)
cd src && uv sync               # Install MCP server deps
./install.sh [--all|--claude]   # Set up symlinks, git-hooks, and configurations
```

Run tests:

```bash
cd src && uv run pytest              # Run MCP server tests (testpaths = ["tests"])
```

Run MCP servers:

```bash
cd src && uv run skill-loader-mcp    # skill-loader MCP server
```

Other MCP servers are provided via `mcp-manager` (proxy); most are disabled by
default (`scripts/disable-mcps-default.py`). Request a disabled one from the user.

Development workflow:

1. Check `instructions/` for domain-specific rules (code style, testing patterns, framework conventions).
2. Track changes in `.taskmaster/` as tasks for significant work.
3. Use focused edits — prefer targeted replacements over full rewrites.
4. Validate via linting, type checking, or running the MCP server.
