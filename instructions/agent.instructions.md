---
description: Core dev conventions for all files — package managers (yarn/pip/asdf), mandatory AskUserQuestion for every interaction, code style (SRP/early-returns/no-any/4-20 line functions), comment policy (WHY not WHAT), test rules (FIRST/named fakes), DI, formatting, and logging. Apply to every code task. Do NOT use for doc navigation or project-specific architecture.
applyTo: "**/*"
---

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

## Task Tracking

When task list exists (multi-step work), use `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` to give user feedback. Mark tasks complete as done, don't batch.

## MCP-Manager

### `mcp__mcp-manager__call_tool`

Executa uma ferramenta em um servidor MCP.

**Argumentos**

- `server`: ID exato do servidor (ex.: `taskmaster-ai`)
- `tool_name`: nome da ferramenta (ex.: `get_tasks`)
- `arguments`: objeto JSON compatível com o `inputSchema`

**Antes de chamar**

```text
# Listar ferramentas de um servidor
mcp__mcp-manager__get_tools_by_server({ server: "<server_id>" })

# Listar servidores disponíveis
mcp__mcp-manager__list_servers()
```

> **Importante:** `server`, `tool_name` e `arguments` são obrigatórios. Os `arguments` devem seguir exatamente o `inputSchema`, caso contrário a chamada falhará na validação.

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
