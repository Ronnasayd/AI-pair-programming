## Project Overview

This project is a comprehensive toolkit designed to enhance AI-assisted software development. It serves as a centralized "intelligence hub" for AI agents (Gemini, Copilot, etc.), providing them with specialized roles, reusable skills, and structured workflows.

### Directory Structure

- `AGENTS.md`: Canonical agent instruction file (single source of truth for all harnesses).
- `agents/`: Markdown definitions for specialized AI roles.
- `skills/`: Reusable capabilities (e.g., style guides, TDD workflows, TLC spec-driven flow).
- `commands/` / `prompts/`: Slash-command and prompt templates.
- `instructions/`: Foundation rules for agents and project-specific conventions (per-language/framework).
- `hooks/`: Hook scripts and config wired into agent harnesses.
- `src/`: Core Python tooling (context generation, token counting, MCP clients).
- `scripts/`: Install/clean/setup scripts per harness (claude, gemini, codex, copilot, antigravity...).
- `templates/`: Templates for PRD, SRS, tasks, plans.
- `taskmaster/` / `.taskmaster/`: Task tracking config and state.
- `documentation/`: Reference docs, SRS/PRD generation guides, standards.
- `reference/`, `benchmark/`, `docs/`: Supporting references and benchmarks.
- Per-harness dirs (`claude/`, `gemini/`, `github-copilot/`, `antigravity/`, `.claude/`, `.gemini/`): harness-specific configs, MCP setups, settings.
- `install.sh`: Entry-point installer.

### Instalation

```sh
git clone https://github.com/Ronnasayd/AI-pair-programming.git ~/AI-pair-programming
cd ~/AI-pair-programming
bash install.sh
```

---
