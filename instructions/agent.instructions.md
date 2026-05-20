---
description: Agent behavior rules.
applyTo: "**/*"
---

## Environments

- Prefer `yarn` over `npm` for JavaScript/TypeScript projects unless the project explicitly uses `npm`.
- For Python projects, prefer `pip` and `venv`.
- Use `asdf` for managing multiple language versions when applicable.

## Documentation

Directories to search for context, in this sequential order:

- `docs/SUMMARY.md`, `README.md`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`
- `docs/architecture.md`, `docs/setup.md`, `docs/usage.md`, `docs/modules/**`, `docs/contribution.md`, `docs/faq.md`,
- `docs/adr/**`, `docs/techs/**`, `docs/misc/**`

When accessing a module, check for the existence of CONTEXT.md files inside the module directory. These files contain relevant information about only the module.

Load only the minimal required sections for the task domain.

## Always Use Interactive Question Tools

**For every question asked to the user** — regardless of context — always use the interactive question tools available in the environment. This rule applies universally: clarifications, option selections, confirmations, preference checks, and any other user interaction.

- **VS Code (GitHub Copilot)**: Use `vscode_askQuestions`
- **Other environments**: Use equivalent interactive question tools available in your context
- **Fallback**: Only if no interactive tools are available, use the labeled option format (A, B, C… Z) described below

Never ask questions as plain text when an interactive tool is available.
