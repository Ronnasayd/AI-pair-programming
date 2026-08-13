## Rules to follow

- Whenever you create sub-agents, specify that they must use `caveman` in *full mode*.
- Whenever creating a sub-agent for investigation, use `caveman:cavecrew-investigator`.
- Avoid reading entire files unless necessary; prefer reading only relevant excerpts. To do this, use `read` with `startLine` and `endLine`, or use `grep`, `rag-rat`, or `serena`.
- Use `grilling` to request clarification from the user when necessary. Mandatory in `plan mode`.
- If a task is complex, use `sequentialthinking` under `mcp-manager` to break it down into smaller tasks.

## Mcp-manager

List of available tools grouped via mcp-manager

| Server             | Tools | Description                                                     |
| ------------------ | ----- | --------------------------------------------------------------- |
| sequentialthinking | 1     | Reflective step-by-step reasoning for complex problems          |
| taskmaster-ai      | 14    | Task management (next_task, set_task_status, expand_all, etc.)  |
| chrome-devtools    | 29    | Chrome control/inspection (DOM, network, console, emulate)      |
| exa                | 2     | Web search / semantic search                                    |
| next-devtools      | 4     | Next.js dev server introspection (routes, components, errors)   |
| a11y               | 2     | Accessibility checking                                          |
| playwright         | 23    | Browser automation (e2e, scraping)                              |
| csv-editor         | 39    | Edit/analyze CSV (sort, group_by, undo, history, etc.)          |
| html-to-markdown   | 2     | Convert HTML → Markdown                                         |
| json-mcp-filter    | 3     | Filter/query large JSON                                         |
| large-file         | 6     | Handle large files (exceeding normal read limits)               |
| burp               | 0     | Burp Suite (pentest/HTTP proxy) — no tools listed               |
| gcloud             | 1     | Google Cloud CLI via MCP                                        |
