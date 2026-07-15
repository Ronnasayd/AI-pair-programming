---
model: sonnet
---

Read the skill **tlc-spec-driven**. Using the plan above as input (research + scope), run:

1. Specify — write `.specs/features/[feature]/spec.md` (requirement IDs, acceptance criteria). Trigger Discuss if gray areas exist.
2. Design — only if scope is Large/Complex (skip inline otherwise).
3. Tasks — only if scope is Large/Complex (skip inline otherwise).

Let the skill's auto-sizing decide which files actually get created — do not force all three.

After the files exist, ask the user if he wants to add the tasks to taskmaster. If he answers `yes`, use the skill **tlc-tasks-to-taskmaster**.
