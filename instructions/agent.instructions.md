---
description: Agent behavior rules.
applyTo: "**/*"
---

## Mandatory rules that must always be followed

- Every user question → interactive tool, never plain text. Claude:
  `AskUserQuestion`. Multiple questions: `grilling` skill.

- When task list exists (multi-step work), use `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` to give user feedback. Mark tasks complete as done, don't batch.

- Whenever you modify a component or screen → run tests using Playwright (or a similar E2E tool) before finalizing.

- Never treat documentation (`markdown files`) as absolute truth. Only the implemented code should be treated as the truth.

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
| Generate a context-map                                 | `context-map`                                |
