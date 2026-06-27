---
description: Define documentation search order and module context loading strategy. Use when reading, writing, or navigating project docs (.md files) — consult SUMMARY.md first, then architecture/setup/usage/contribution/models/endpoints/faq, then per-module CONTEXT.md. Do NOT use for code behavior, agent config, or non-doc tasks.
applyTo: "**/*.md"
---

## Documentation

Search context in this order:

- `@docs/SUMMARY.md` — executive summary, module table, quick start, full doc index
- `@docs/architecture.md` — Mermaid diagrams, components, data flow, patterns, ADR links
- `@docs/setup.md` — requirements, env vars, yarn commands, local setup guide
- `@docs/usage.md` — core flows with end-to-end HTTP examples (assign, deactivate, bulk, amendment)
- `@docs/contribution.md` — branch/commit conventions, layer rules, naming, test locations
- `@docs/models.md` — full data model for all entities with fields and invariants
- `@docs/endpoints.md` — all REST endpoints grouped by module with request/response examples
- `@docs/faq.md` — Q&A covering setup, auth, licensing, billing, and architecture
- `@docs/modules/<module>.md` — high-level context for each bounded context (generated first; linked via `CONTEXT.md` symlinks inside each module folder)
- `@docs/adr/` — Architectural Decision Records (ADR-001 to ADR-005)

When entering module, check for `CONTEXT.md` inside module directory. File holds module-only context.

Load only minimum sections needed for task domain.
