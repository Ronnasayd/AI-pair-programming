## Rules to follow

- Whenever you create sub-agents, specify that they must use `caveman` in _full mode_.
- For sub-agents with simple tasks, use the `Haiku` model, and for medium tasks, use `Sonnet`.
- Avoid reading entire files unless necessary; prefer reading only relevant excerpts. To do this, use `read` with `startLine` and `endLine`, or use `grep`, `rag-rat`, or `serena`.
- Use `grilling` to request clarification from the user when necessary.
- If a task is complex, use `sequentialthinking` to break it down into smaller tasks.
- Read `CLAUDE.md` and `AGENTS.md` for additional rules and guidelines.
- In any time evaluate whether there is anything worth saving as permanent memory. Save as permanent memory only what the next session will need and cannot rediscover by reading the code, Git, or CLAUDE.md—such as the _reason_ behind a decision, a non-obvious invariant, or a user preference; if it is already in the repo or only matters for this specific conversation, do not save it. Use the `ai-memory-durable-pages` skill to persist it.
