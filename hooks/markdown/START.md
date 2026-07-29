# Rules to follow

- Always create sub-agents and specify that they must use `caveman` in _full mode_.
- Whenever creating a sub-agent for investigation, use `caveman:cavecrew-investigator`.
- Avoid reading entire files unless necessary; prefer reading only relevant excerpts. To do this, use `read` with `startLine` and `endLine`, or use `grep`, `rag-rat mcp`, or `serena mcp`.
- Use `grilling` to request clarification from the user when necessary. Mandatory in `plan mode`.
- If a task is complex, use `sequentialthinking mcp` to break it down into smaller tasks.
- Perform `semantic searches` using the available tools. Mandatory in `plan mode`.
