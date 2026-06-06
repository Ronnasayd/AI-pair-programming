---
description: Agent behavior rules.
applyTo: "**/*"
---

## Environments

- JS/TS: use `yarn`, not `npm`, unless project says `npm`.
- Python: use `pip` + `venv`.
- Multi-language versions: use `asdf` when fit.

## Documentation

Search context in this order:

- `docs/SUMMARY.md`, `README.md`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`
- `docs/architecture.md`, `docs/setup.md`, `docs/usage.md`, `docs/modules/**`, `docs/contribution.md`, `docs/faq.md`
- `docs/adr/**`, `docs/techs/**`, `docs/misc/**`

When entering module, check for `CONTEXT.md` inside module dir. File holds module-only context.

Load only minimum sections needed for task domain.

## Always Use Interactive Question Tools

For every user question, use interactive question tool. No exceptions for context, type, or intent.

Use this for clarifications, options, confirmations, preference checks, all user interactions.

- **VS Code (GitHub Copilot)**: Use `vscode_askQuestions`
- **Other environments**: Use equivalent interactive question tools available in your context
- **Fallback**: if no interactive tools exist, use labeled options (A, B, C... Z)

If interactive tool exists, never ask plain-text question.
