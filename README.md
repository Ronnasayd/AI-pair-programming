# AI Pair Programming Workspace

This workspace is a comprehensive collection of tools, agents, skills, and instructions designed to enhance AI-powered pair programming and software development workflows. It integrates with Gemini CLI and GitHub Copilot, providing a structured environment for task management, code generation, and documentation.

## Project Overview

The project acts as a centralized repository for AI development "intelligence." It includes:

- **Custom MCP Server:** A FastMCP-based server (`src/my_mcp_server.py`) that provides tools for code review, context generation, task conversion, and more.
- **Specialized Agents:** A library of Markdown-defined expert agents (in `agents/`) covering roles like product owner, developer, cybersecurity specialist, and database expert.
- **Development Skills:** Built-in skills for style guides (TypeScript, Python, Go) and specialized workflows like `taskmaster`.
- **Instructional Context:** Comprehensive guidelines for code generation, PRD/SRS creation, and testing.
- **Task Management:** A local task tracking system (`.taskmaster/`) that supports JSON-to-Markdown conversion for better human-AI collaboration.

## Key Directories

- `src/`: Core logic, including the MCP server and utility scripts for token counting, context generation, and search.
- `agents/`: Definitions for various AI personas and their specific instructions.
- `skills/`: Reusable skill sets for different programming languages and methodologies.
- `instructions/`: Deep-dive guidelines for specific tasks (e.g., `copilot.instructions.md`).
- `templates/`: Standardized JSON/Markdown templates for PRDs, SRS, and Plans.
- `docs/`: Project-specific documentation and workflow diagrams.
- `mcps/`: Configuration files for Model Context Protocol (MCP) clients like VS Code.

## Core Tools & Commands

### MCP Server (FastMCP)

The server in `src/my_mcp_server.py` exposes several tools:

- `my_mcp_get_context`: Generates a structured context of the codebase.
- `my_mcp_code_review`: Analyzes git diffs based on specialist instructions.
- `my_mcp_convert_tasks_to_markdown` / `my_mcp_convert_markdown_to_tasks`: Syncs the internal task state with a human-readable `tasks.md`.

### Setup and Installation

- `install.sh`: A bash script that symlinks commands, skills, and agents to the user's `~/.gemini/` and `.github/` directories, setting up the local environment.

## Development Conventions

- **Instruction-Driven:** Always refer to the relevant `.agent.md` or `.instructions.md` file before performing significant tasks.
- **Task-Master Workflow:** Use the `taskmaster` skill to track progress. Maintain the `tasks.json` and sync it to `tasks.md` for visibility.
- **Surgical Changes:** Follow the "Research -> Strategy -> Execution" lifecycle. Use `replace` for targeted edits and ensure all changes are validated with tests.
- **Security:** Adhere to the `cybersecurity-specialist` guidelines. Never commit secrets or hardcoded credentials.

## Usage

To use this workspace effectively:

1. Run `install.sh` to initialize your local environment and symlink the necessary components.
2. Activate the `taskmaster` skill when starting a new feature or bug fix.
3. Use the MCP tools (e.g., via a compatible IDE or the CLI) to generate context, perform reviews, and manage tasks.
4. Follow the templates in `templates/` when generating requirements or plans.
