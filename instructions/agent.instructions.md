---
description: Agent behavior rules — documentation retrieval and task execution standards.
applyTo: "**/*"
---

## Environments

- Prefer `yarn` over `npm` for JavaScript/TypeScript projects unless the project explicitly uses `npm`.
- For Python projects, prefer `pip` and `venv`.

## Documentation

Directories to search for context:

- `docs/**`, `docs/agents/**`, `docs/agents/specs/**`, `docs/agents/plans/**`, `docs/agents/reviews/**`
- `docs/adr/**`, `docs/techs/**`, `docs/misc/**`
- `docs/architecture.md`, `docs/setup.md`, `docs/usage.md`, `docs/modules.md`
- `docs/contribution.md`, `docs/faq.md`, `docs/SUMMARY.md`
- `.taskmaster/tasks/*.md`
- `README.md`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`

Load only the minimal required sections for the task domain.

## Rules to Avoid

- **Editing without verifying current content first**

  ```
  ❌ BAD: Immediately calling replace_string_in_file on "src/config.ts" based on memory
  ✅ GOOD: Call read_file on "src/config.ts" first, confirm the exact lines, then edit
  ```

- **Assuming file paths without verification**

  ```
  ❌ BAD: Writing to "src/utils/helpers.ts" because it sounds right
  ✅ GOOD: Call file_search "helpers.ts" or grep_search for a known symbol to locate the actual path
  ```

- **Assuming task status without querying current state first**
  ```
  ❌ BAD: "Task #5 is done, moving to #6" without checking .taskmaster/tasks/tasks.json
  ✅ GOOD: Read tasks.json or run `task-master list` to confirm current status before proceeding
  ```

## Rules to Follow

- **Never rewrite everything — edit only specific segments**

  ```
  ❌ BAD: Replacing all 200 lines of a component to fix one prop name
  ✅ GOOD: Use replace_string_in_file targeting only the 3 lines containing the prop
  ```

- **Verify file existence and line numbers before making edits**

  ```
  ❌ BAD: replace_string_in_file at "line 42" recalled from a previous read
  ✅ GOOD: Re-read or grep the file in the same turn to confirm line numbers haven't shifted
  ```

- **Organize task hierarchies by domain/theme, not sequential numbering**

  ```
  ❌ BAD: Tasks: 1-auth, 2-db, 3-auth-tests, 4-ui, 5-auth-fix  (interleaved)
  ✅ GOOD: auth/ → login, tests, fix; db/ → schema, migrations; ui/ → layout
  ```

- **Prefer expanding existing tasks over creating new ones**
  ```
  ❌ BAD: Creating task #42 "Fix login bug" when task #7 "Auth module" already exists
  ✅ GOOD: Add a subtask or note inside task #7 covering the login bug fix
  ```
