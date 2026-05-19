---
description: Rules for code generation and modification tasks.
applyTo: "**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx"
---

## Context

This file applies exclusively to code generation and modification tasks.
Code review, auditing, or diff inspection are handled separately — do not perform those unless explicitly requested.

## Rules

- Integrate new code compatibly with the existing codebase; follow established patterns and boundaries.
- Avoid breaking backward compatibility unless required; document migration steps if you do.
- Include automated tests, examples, or validation instructions whenever technically feasible.
- Include clear documentation when introducing significant new components, endpoints, or public interfaces.

## Anti-Patterns

- Do not use confusing, generic, or abbreviated identifiers (e.g., `x`, `temp1`, `doStuff`).
- Do not duplicate code; prefer reuse through functions, modules, or abstractions.
- Do not use magic values; use named constants or enums.
- Do not mix multiple responsibilities in a single function, class, or module.
- Do not ignore performance in critical paths (inefficient loops, heavy queries, blocking calls).
- Do not leave dead code, commented-out code, or unused functions.
- Do not catch overly broad exceptions without justification; prefer specific exception types.
- Avoid circular dependencies and excessive coupling; respect dependency inversion.
- Avoid hardcoded configs or absolute paths; do not create environment inconsistencies.
- Avoid outdated cryptographic algorithms or security practices.
