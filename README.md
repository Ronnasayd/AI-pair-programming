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

### Directory Structure

- `src/`: Core logic and tools.
- `agents/`: Markdown definitions for specialized AI roles.
- `skills/`: Reusable capabilities (e.g., style guides, TDD workflows).
- `instructions/`: Foundation rules for agents and project-specific conventions.

---
