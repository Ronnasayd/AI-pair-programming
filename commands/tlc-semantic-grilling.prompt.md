Run a `/grilling` session with `/tlc-spec-driven` in specify mode, but first, use `sequentialthinking` to break the feature request into sub-questions (scope, constraints, edge cases, dependencies), then use tools like `rag-rat`,`serena`, `grep`, `Read` o any available tool to perform a semantic search to gather all the necessary information.

After `/tlc-spec-driven` in the specify mode finish and the files are generated, ask the user if they want to register the feature in taskmaster. If they answer `yes`, use the skill `/tlc-tasks-to-taskmaster` -- it derives tasks from `tasks.md` when present, or falls back to one task per requirement/AC from `spec.md` when Tasks was skipped.

Check the definitions in [docs-adr](.claude/skills/generate-docs/references/templates/docs-adr.md) and consider offering to create an ADR when the criteria are met.
