# Tool Selection

Pick by question, not habit. Fall back down the columns when a tool is dormant, stale, or lacks the language.

| Question                                     | 1st (rag-rat)                                         | Fallback (codebase-memory)                  | Precision (serena)             |
| -------------------------------------------- | ----------------------------------------------------- | ------------------------------------------- | ------------------------------ |
| Orientation: layout, hot files, entry points | `repo_brief`, `important_symbols`                     | `get_architecture`, `index_status`          | —                              |
| Concept → code ("where is X handled?")       | `semantic_search`                                     | `search_graph` (`query` / `semantic_query`) | —                              |
| Exact symbol location                        | `symbol_lookup`                                       | `search_graph` (`name_pattern`)             | `find_symbol`                  |
| Who calls / what is called                   | `find_callers`, `trace_callees`                       | `trace_path` (`inbound` / `outbound`)       | `find_referencing_symbols`     |
| Blast radius of a change                     | `impact_surface`                                      | `trace_path` depth 2-3, `detect_changes`    | `find_referencing_symbols`     |
| File structure without reading it            | —                                                     | `get_file_outline`                          | `get_symbols_overview`         |
| Read only the relevant body                  | —                                                     | `get_code_snippet`                          | `find_symbol` + `include_body` |
| Interface → implementations                  | —                                                     | `trace_path` (`INHERITS`/`IMPLEMENTS`)      | `find_implementations`         |
| Multi-hop / aggregate ("all X that call Y")  | —                                                     | `query_graph` (Cypher)                      | —                              |
| Literal strings, config keys, non-code files | `grep`                                                | `search_code`                               | —                              |
| Why built this way                           | `memory_search` (rag-rat), `memory_query` (ai-memory) | —                                           | —                              |
| Library/API behavior                         | context7 (`resolve-library-id` → `query-docs`)        | —                                           | —                              |

Rules:

- Never `cat` whole files — outline first, then read the excerpt.
- Check index freshness (`index_status` / rag-rat `health`) before trusting absence of results; absence is not proof.
