---
model: sonnet
---

Read the skill **tlc-spec-driven**. Using the plan above as input (research + scope), run:

1. Specify -- write `.specs/features/[feature]/spec.md` (requirement IDs, acceptance criteria). Trigger Discuss if gray areas exist.
2. Design -- write `.specs/features/[feature]/design.md`, only if the auto-sizing table (SKILL.md) says this scope needs it. Skip otherwise.
3. Tasks -- write `.specs/features/[feature]/tasks.md`, only if the auto-sizing table says this scope needs it. Skip otherwise.

After the files exist, ask the user if they want to register the feature in taskmaster. If they answer `yes`, use the skill **tlc-tasks-to-taskmaster** -- it derives tasks from `tasks.md` when present, or falls back to one task per requirement/AC from `spec.md` when Tasks was skipped.
