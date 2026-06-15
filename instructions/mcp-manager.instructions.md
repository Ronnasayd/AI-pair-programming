---
description: How to use the mcp-manager tool
applyTo: "**/*"
---

## Description

The **mcp-manager** is a Model Context Protocol (MCP) manager that allows access to tools from different servers. Here is the practical guide:

## **Discover Available Tools**

```bash
# List all MCP servers
mcp_mcp-manager_list_servers

# Search for tools by keyword
mcp_mcp-manager_search_tools
  query: "your search term"
  max_results: 10

# Get tools from a specific server
mcp_mcp-manager_get_tools_by_server
  server: "taskmaster-ai"  # or: exa, csv-editor, burp, etc.
```

## **Understand a Tool's Structure**

```bash
# View the complete schema (parameters, types, etc.)
mcp_mcp-manager_get_tool_schema
  server: "taskmaster-ai"
  tool_name: "get_tasks"
```

## **Execute a Tool**

```bash
# General syntax
mcp_mcp-manager_call_tool
  server: "server-name"
  tool_name: "tool-name"
  arguments: { /* tool parameters */ }
```

## Available servers

- sequentialthinking
- taskmaster-ai
- my-mcp-server
- context7
- chrome-devtools
- exa
- next-devtools
- a11y
- playwright
- csv-editor
- html-to-markdown
- json-mcp-filter
- large-file
- burp
- gcloud

## 💡 **Typical Workflow**

1. **Discover** → `list_servers` → `get_tools_by_server`
2. **Understand** → `get_tool_schema`
3. **Execute** → `call_tool` with the correct arguments
4. **Interpret results** → use the tool output

---
