## Rules to follow

- Whenever you create sub-agents, specify that they must use `caveman` in *full mode*.
- Whenever creating a sub-agent for investigation, use `caveman:cavecrew-investigator`.
- Avoid reading entire files unless necessary; prefer reading only relevant excerpts. To do this, use `read` with `startLine` and `endLine`, or use `grep`, `rag-rat`, or `serena`.
- Use `grilling` to request clarification from the user when necessary. Mandatory in `plan mode`.
- If a task is complex, use `sequentialthinking` under `mcp-manager` to break it down into smaller tasks.
