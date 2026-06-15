---
description: Establish agent behavior and development conventions including environment tooling, documentation hierarchy, interactive question requirements, and response style. Use when updating agent instructions, configuring agent behavior, setting environment preferences, defining documentation hierarchy, or establishing response standards.
applyTo: "**/*"
---

## Environments

- JS/TS: use `yarn`, not `npm`, unless project says `npm`.
- Python: use `pip` + `venv`.
- Multi-language versions: use `asdf` when fit.

## Documentation

Search context in this order:

- `@docs/SUMMARY.md`
- `@docs/architecture.md`
- `@docs/setup.md`
- `@docs/usage.md`
- `@docs/modules/**/*.md`
- `@docs/contribution.md`
- `@docs/faq.md`
- `@docs/adr/**/*.md`
- `@docs/techs/**/*.md`
- `@docs/misc/**/*.md`

When entering module, check for `CONTEXT.md` inside module directory. File holds module-only context.

Load only minimum sections needed for task domain.

## Always Use Interactive Question Tools

For every user question, use interactive question tool. No exceptions for context, type, or intent.

Use this for clarifications, options, confirmations, preference checks, all user interactions.

- **VS Code (GitHub Copilot)**: Use `vscode_askQuestions`
- **Other environments**: Use equivalent interactive question tools available in your context
- **Fallback**: if no interactive tools exist, use labeled options (A, B, C... Z)

If interactive tool exists, never ask plain-text question.

## Response Style

- Activate skill **caveman** in mode full when available. If not, use concise, direct style.
