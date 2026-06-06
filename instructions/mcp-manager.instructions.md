---
description: How to use the mcp-manager tool
applyTo: "**/*"
---

The **mcp-manager** is a Model Context Protocol (MCP) manager that allows access to tools from different servers. Here is the practical guide:

## 1️⃣ **Discover Available Tools**

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

## 2️⃣ **Understand a Tool's Structure**

```bash
# View the complete schema (parameters, types, etc.)
mcp_mcp-manager_get_tool_schema
  server: "taskmaster-ai"
  tool_name: "get_tasks"
```

## 3️⃣ **Execute a Tool**

```bash
# General syntax
mcp_mcp-manager_call_tool
  server: "server-name"
  tool_name: "tool-name"
  arguments: { /* tool parameters */ }
```

### Practical Examples:

**Example 1: Get tasks from TaskMaster**

```bash
mcp_mcp-manager_call_tool
  server: "taskmaster-ai"
  tool_name: "get_tasks"
  arguments: { "status": "not-started" }
```

**Example 2: Search the web (Exa)**

```bash
mcp_mcp-manager_call_tool
  server: "exa"
  tool_name: "web_search_exa"
  arguments: { "query": "TypeScript best practices" }
```

**Example 3: Update task status**

```bash
mcp_mcp-manager_call_tool
  server: "taskmaster-ai"
  tool_name: "set_task_status"
  arguments: {
    "task_id": "task-123",
    "status": "completed"
  }
```

## 💡 **Typical Workflow**

1. **Discover** → `list_servers` → `get_tools_by_server`
2. **Understand** → `get_tool_schema`
3. **Execute** → `call_tool` with the correct arguments
4. **Interpret results** → use the tool output

---

**Want to execute something specific?** Tell me which server/tool you want to use, and I'll call it for you! 🚀
