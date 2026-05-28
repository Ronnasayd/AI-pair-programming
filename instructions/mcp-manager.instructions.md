---
description: How to use mcp-manager tool
applyTo: "**/*"
---

O **mcp-manager** é um gerenciador de Model Context Protocol (MCP) que permite acessar ferramentas de diferentes servidores. Aqui está o guia prático:

## 1️⃣ **Descobrir Ferramentas Disponíveis**

```bash
# Listar todos os servidores MCP
mcp_mcp-manager_list_servers

# Buscar ferramentas por palavra-chave
mcp_mcp-manager_search_tools
  query: "seu termo de busca"
  max_results: 10

# Obter ferramentas de um servidor específico
mcp_mcp-manager_get_tools_by_server
  server: "taskmaster-ai"  # ou: exa, csv-editor, burp, etc.
```

## 2️⃣ **Entender Estrutura de Uma Tool**

```bash
# Ver o schema completo (parâmetros, tipos, etc)
mcp_mcp-manager_get_tool_schema
  server: "taskmaster-ai"
  tool_name: "get_tasks"
```

## 3️⃣ **Executar uma Ferramenta**

```bash
# Sintaxe geral
mcp_mcp-manager_call_tool
  server: "nome-do-servidor"
  tool_name: "nome-da-ferramenta"
  arguments: { /* parâmetros da tool */ }
```

### Exemplos Práticos:

**Exemplo 1: Obter tarefas do TaskMaster**

```bash
mcp_mcp-manager_call_tool
  server: "taskmaster-ai"
  tool_name: "get_tasks"
  arguments: { "status": "not-started" }
```

**Exemplo 2: Buscar na web (Exa)**

```bash
mcp_mcp-manager_call_tool
  server: "exa"
  tool_name: "web_search_exa"
  arguments: { "query": "TypeScript best practices" }
```

**Exemplo 3: Definir status de tarefa**

```bash
mcp_mcp-manager_call_tool
  server: "taskmaster-ai"
  tool_name: "set_task_status"
  arguments: {
    "task_id": "task-123",
    "status": "completed"
  }
```

## 💡 **Fluxo Típico**

1. **Descobrir** → `list_servers` → `get_tools_by_server`
2. **Entender** → `get_tool_schema`
3. **Executar** → `call_tool` com argumentos corretos
4. **Interpretar resultado** → usar output da ferramenta

---

**Quer executar algo específico?** Diga qual servidor/ferramenta e eu chamo para você! 🚀
