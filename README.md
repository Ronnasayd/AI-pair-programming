# GEMINI.md - AI Pair Programming Workspace

This document provides essential context and instructions for AI agents operating within this workspace. It summarizes the project's architecture, tools, and development conventions.

## Project Overview

This project is a comprehensive toolkit designed to enhance AI-assisted software development. It serves as a centralized "intelligence hub" for AI agents (Gemini, Copilot, etc.), providing them with specialized roles, reusable skills, and structured workflows.

### Main Technologies

- **Python:** Core logic for MCP servers and utility scripts.
- **FastMCP:** Used to implement Model Context Protocol servers for tool integration.
- **Node.js/TypeScript:** Supported environment for various project types within the workspace.
- **Bash:** Used for installation and environment setup scripts.
- **Markdown:** Used for defining agents, instructions, and task tracking.

### Key Components

- **MCP Server (`src/my_mcp_server.py`):** Provides tools for codebase context generation, code review, documentation syncing, and semantic search.
- **Specialized Agents (`agents/`):** A library of personas (e.g., `developer-specialist`, `cybersecurity-specialist`) with specific behavioral instructions.
- **Taskmaster (`.taskmaster/`):** A local task tracking and management system.
- **Copilot Ollama Proxy (`src/copilot/`):** Maps Ollama-compatible requests to the GitHub Copilot API.

## Building and Running

### Environment Setup

1.  **Dependencies:** Install Python requirements:
    ```bash
    pip install -r src/requirements.txt
    ```
2.  **Installation:** Symlink components to your local environment:
    ```bash
    ./install.sh
    ```

### Running the MCP Server

- Start the server using `stdio`:
  ```bash
  python src/my_mcp_server.py
  ```

### Task Management

- Sync tasks between JSON and Markdown:
  - JSON to MD: Use `my_mcp_convert_tasks_to_markdown` tool.
  - MD to JSON: Use `my_mcp_convert_markdown_to_tasks` tool.

## Development Conventions

### General Rules

- **Instruction-Driven:** Always check `@.github/instructions/` for domain-specific guidelines (Code, Orchestration, Agent Behavior).
- **Task-Master Workflow:** Every significant change should be tracked as a task in `.taskmaster/`.
- **Surgical Changes:** Prioritize targeted `replace` operations over complete file overwrites.
- **Validation:** Every change must be verified (e.g., via linting, type checking, or running the MCP server).

### Directory Structure

- `src/`: Core logic and tools.
- `agents/`: Markdown definitions for specialized AI roles.
- `skills/`: Reusable capabilities (e.g., style guides, TDD workflows).
- `instructions/`: Foundation rules for agents and project-specific conventions.
- `templates/`: Standardized formats for PRDs, SRS, and Plans.
- `.taskmaster/`: Internal state and Markdown reports for tasks.

---
