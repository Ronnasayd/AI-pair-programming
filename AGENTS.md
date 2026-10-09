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
hooks/          Event-driven automation (Claude Code hooks)
lefthook/       Git hooks (managed by lefthook)
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
./install.sh [--all|--claude]   # Set up symlinks, lefthook, and configurations
```

Run tests:

```bash
cd src && uv run pytest              # Run MCP server tests (testpaths = ["tests"])
```

Run MCP servers:

```bash
cd src && uv run skill-loader-mcp    # skill-loader MCP server
```

<!-- INIT:AUTO-GENERATED-CONTEXT:DO-NOT-MODIFY -->


## Mandatory rules that must always be followed

- Every user question → interactive tool, never plain text. Claude:
  `AskUserQuestion`. Multiple questions: `grilling` skill.

- When task list exists (multi-step work), use `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` to give user feedback. Mark tasks complete as done, don't batch.

- Whenever you modify a component or screen → run tests using Playwright (or a similar E2E tool) before finalizing.

- Whenever lint, type, or test errors are reported, fix them, even if they were not caused by your changes.

- Never treat documentation (`markdown files`,`memories`) as absolute truth. Only the implemented code should be treated as the truth.

- Never assume the code is correct without tests to validate it.

## Commonly used skills

| When                                                   | Use                                          |
| ------------------------------------------------------ | -------------------------------------------- |
| New skill's description doesn't trigger reliably       | `skill-description-generator`                |
| Writing a commit message                               | `semantic-commit-message` / `caveman-commit` |
| Opening a PR                                           | `generate-pr-description`                    |
| Unsure about git workflow (rebase, branch strategy)    | `git-guide` / `git-workflow`                 |
| Break big/complex problem into sub-problems            | `dynamic-programming-analysis`               |
| Generate/update project docs from code or diff         | `generate-docs`                              |
| Write PR description from diff/commits                 | `generate-pr-description`                    |
| Review a PR                                            | `pr-review`                                  |
| Judge PR w/ evidence-first review + inline GH comments | `the-judge`                                  |
| Resolve merge conflicts                                | `resolve-merge-conflicts`                    |
| Execute tasks for a spec-driven feature (taskmaster)   | `sd-execute`                                 |
| Generate a plan step-by-step                           | `sd-planning`                                |
| Build requirements review table from spec/design/tasks | `spec-to-requirements-table`                 |
| Pick between technical options (pros/cons)             | `technical-decision-helper`                  |
| Map files/deps/tests a task touches before changing    | `context-map`                                |

## Context-Specific Rules

The following rules apply to specific file types:
- [code.instructions](.claude/instructions/code.instructions.md) — applies to: `**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx`
<!-- END:AUTO-GENERATED-CONTEXT:DO-NOT-MODIFY -->
