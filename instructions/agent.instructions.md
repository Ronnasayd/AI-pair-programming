---
description: Repo-specific dev conventions for all files — package managers (yarn/pip), mandatory AskUserQuestion for every interaction, task tracking tools, naming (<5-grep-hit names), exception-message content, named-fake mocking. Apply to every code task, always. Do NOT use for doc navigation (see docs.instructions.md) or per-language/framework detail (see code/node-ts/python/react/vue.instructions.md).
applyTo: "**/*"
---

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
