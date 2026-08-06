# Create Mode — Generate Docs From Scratch

Full docs/ scaffold generation from source code. Selected when `docs/` does not yet exist (see mode-selection table in [SKILL.md](../SKILL.md)).

Shared writing standards, anti-patterns, the module symlink rule, and the quality checklist live in [shared.md](shared.md) — read that alongside this file, don't duplicate it here.

---

## Core Principles

- Your reasoning must be **thorough and detailed** — it is acceptable for it to be very long.
- You **MUST iterate** until the documentation is clear, complete, and appropriate for every target audience.
- Solve every documentation problem **completely and autonomously** before returning control to the user.
- Never end a session without having properly generated every planned artifact.
- If you say you will create a file, **actually create it** before finishing.
- Failing to review documentation or leaving it inconsistent is the **main cause of failure** in this type of task.

---

## Workflow

### Phase 1 — Codebase Investigation

1. Read the workspace tree (`ls -R`, `find`, or equivalent) to understand the full folder/file layout.
2. Open and study key files: entry points, configuration, existing docs, package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
3. Extract module names, responsibilities, dependencies, and data flows.
4. Update your mental model as you gather more information.
5. Note important commands, environment variables, and code snippets for later use in docs.

### Phase 2 — Incremental Analysis & Generation

Iterate over the workspace **one module / folder at a time**. For each unit:

1. **Announce** which file, module, or folder will be analyzed next.
2. **Analyze** its purpose, inputs/outputs, dependencies, and design decisions.
3. **Write** (or update) the relevant documentation file incrementally.
4. **Verify** consistency with already-generated docs before moving on.

Repeat until all relevant modules are covered.

### Phase 3 — Action Plan

Before writing, create a clear plan divided into specific, verifiable steps. **Module context files must be generated first** — they are the foundation for all other documents.

```
[ ] 1.  Investigate workspace root and entry points
[ ] 2.  Map module/folder structure and identify all top-level modules
[ ] 3.  For each module: generate docs/modules/<module-name>.md (high-level context)
[ ] 4.  For each module: create <module-name>/CONTEXT.md symlink → docs/modules/<module-name>.md
[ ] 5.  Generate docs/SUMMARY.md  (using module context files as foundation)
[ ] 6.  Generate docs/architecture.md
[ ] 7.  Generate docs/setup.md
[ ] 8.  Generate docs/usage.md
[ ] 9.  Generate docs/contribution.md
[ ] 10. Generate docs/adr/ (if applicable)
[ ] 11. Generate docs/techs/ (if applicable)
[ ] 12. Generate docs/endpoints.md (if API exists)
[ ] 13. Generate docs/models.md (if data models exist)
[ ] 14. Generate docs/faq.md (if applicable)
[ ] 15. Cross-link and consistency review
```

---

## Documentation Structure

```text
docs/
 ├── SUMMARY.md           # Executive summary — high-level view, fast onboarding
 ├── architecture.md      # Architecture, diagrams, design decisions
 ├── setup.md             # Installation and execution guide
 ├── usage.md             # Application usage examples
 ├── modules/             # One file per module — generated FIRST, used as foundation
 │    └── <module-name>.md
 ├── contribution.md      # Contributor guide
 ├── models.md            # Data models/entities (optional — only if models exist)
 ├── endpoints.md         # API endpoints (optional — only if API exists)
 ├── faq.md               # Frequently asked questions (optional)
 ├── adr/                 # Architectural Decision Records (optional)
 │    └── adr-001-*.md
 ├── techs/               # Technologies and frameworks (optional)
 │    └── *.md
 └── misc/                # Any other unspecified documentation (optional)
      └── *.md
```

See [shared.md](shared.md) for the module `CONTEXT.md` symlink rule — mandatory for every module file created here.

---

## Purpose and Scope Reference

| File / Folder              | Required?                     | Target Audience               | Main Objective                                                               | Essential Content                                                            |
| -------------------------- | ----------------------------- | ----------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `docs/SUMMARY.md`          | ✅ Always                     | Everyone                      | High-level overview and navigation                                           | System name, overview, modules, architecture summary, quick start, doc links |
| `docs/architecture.md`     | ✅ Always                     | Developers, architects        | Explain how the system works internally                                      | Mermaid diagrams, layers, components, decisions, trade-offs, ADR links       |
| `docs/setup.md`            | ✅ Always                     | Developers                    | Explain how to install and run                                               | Requirements, env vars, dependencies, commands, local run, build, deploy     |
| `docs/usage.md`            | ✅ Always                     | End users, integrators        | Demonstrate how to use the system                                            | Practical examples, flows, outputs, main use cases                           |
| `docs/modules/<module>.md` | ✅ Always (one per module)    | Developers                    | High-level module context: role, responsibilities, inter-module interactions | Overview, responsibilities, architecture fit, interactions, key concepts     |
| `docs/contribution.md`     | ✅ Always                     | Contributors                  | Guide consistent contributions                                               | Clone, branch, PRs, commit standards, code conventions                       |
| `docs/models.md`           | ⚙️ If data models exist       | Developers, analysts          | Describe data models / entities / schemas                                    | Structure, attributes, types, validations, relationships                     |
| `docs/endpoints.md`        | ⚙️ If API exists              | Integrators, frontend/backend | Describe exposed APIs                                                        | Endpoints, methods, params, responses, error codes, examples                 |
| `docs/faq.md`              | ⚙️ Recommended                | Everyone                      | Answer common questions quickly                                              | FAQs about usage, setup, known errors, best practices                        |
| `docs/adr/`                | ⚙️ Recommended for large apps | Architects, tech leads        | Record formal architectural decisions                                        | One decision per file: context, decision, alternatives, consequences         |
| `docs/techs/`              | ⚙️ Optional                   | New devs, maintainers         | Explain used technologies                                                    | Frameworks, versions, roles, references, justifications                      |
| `docs/misc/`               | ⚙️ Optional                   | General audience              | Store extra documentation                                                    | Logs, maintenance notes, style guides, performance reports                   |

---

## File Templates

| Output File                     | Word Range   | Template                                                         |
| ------------------------------- | ------------ | ---------------------------------------------------------------- |
| `docs/SUMMARY.md`               | 500–1500     | [templates/docs-SUMMARY.md](templates/docs-SUMMARY.md)           |
| `docs/architecture.md`          | 1500–3500    | [templates/docs-architecture.md](templates/docs-architecture.md) |
| `docs/setup.md`                 | 500–1500     | [templates/docs-setup.md](templates/docs-setup.md)               |
| `docs/usage.md`                 | 1000–2500    | [templates/docs-usage.md](templates/docs-usage.md)               |
| `docs/modules/<module-name>.md` | 400–900 each | [templates/docs-modules.md](templates/docs-modules.md)           |
| `docs/contribution.md`          | 500–1500     | [templates/docs-contribution.md](templates/docs-contribution.md) |
| `docs/models.md`                | 600–1500     | [templates/docs-models.md](templates/docs-models.md)             |
| `docs/endpoints.md`             | 800–2000     | [templates/docs-endpoints.md](templates/docs-endpoints.md)       |
| `docs/adr/adr-NNN-<title>.md`   | 300–800 each | [templates/docs-adr.md](templates/docs-adr.md)                   |
| `docs/techs/<technology>.md`    | 200–800 each | [templates/docs-techs.md](templates/docs-techs.md)               |
| `docs/faq.md`                   | 500–1000     | [templates/docs-faq.md](templates/docs-faq.md)                   |

> **Note for `docs/modules/<module-name>.md`:** each file covers **one module** and must focus on the **high-level view** — not implementation details. Content:
>
> 1. **Module name and location** — folder path in the repository.
> 2. **Purpose and responsibilities** — what it does and why it exists (2–4 sentences).
> 3. **Role in the overall architecture** — where it fits in the system layers/components.
> 4. **Interactions with other modules** — what it consumes, what it exposes, which modules it depends on and which depend on it.
> 5. **Key concepts and abstractions** — important domain terms, patterns, or mental models a developer needs to know.
> 6. **Entry points** — the main files, classes, or functions a new developer should read first.
> 7. **What this module is NOT** — explicit scope boundaries to prevent misuse.
>
> ⚠️ **Avoid:** low-level implementation details, exhaustive API lists, or code walkthroughs.
> The goal is a **5-minute orientation** that lets any developer understand the module's role and decide whether to dive deeper.

---

## Quality Gate

Before finishing, run the [shared.md](shared.md) Quality and Consistency Checklist and confirm none of the [shared.md](shared.md) anti-patterns are present.
