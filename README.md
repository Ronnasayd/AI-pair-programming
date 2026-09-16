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
- `uninstall.sh`: Entry-point uninstaller.

### Instalation

```sh
git clone https://github.com/Ronnasayd/AI-pair-programming.git ~/AI-pair-programming
cd ~/AI-pair-programming
bash install.sh
```

### Uninstalation

```sh
bash uninstall.sh
```

### Environment Variables

| Variable                                                                                                                                            | Default         | Used in                                                           | Description                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `CLAUDE_INSTALL_SKIP_AUTO_CONTEXT`                                                                                                                  | unset           | `scripts/claude.install.sh`                                       | Set to `1` to skip regenerating the `<!-- INIT AUTO-CONTEXT -->` block in `AGENTS.md` on install.     |
| `CLAUDE_INSTALL_SKIP_CLAUDE_MD`                                                                                                                     | unset           | `scripts/claude.install.sh`                                       | Set to `1` to skip (re)writing `CLAUDE.md` on install.                                                |
| `CLAUDE_PROJECT_DIR`                                                                                                                                | project path    | `scripts/claude.install.sh`, `scripts/statusline-command.sh`      | Local project dir written to `settings.local.json`; used to locate `rag-rat.toml` for the statusline. |
| `AI_PROJECT_ROOT_DIR`                                                                                                                               | unset           | `scripts/ai-jail.sh`                                              | Root dir (hooks/statusline/skills live here via symlinks) read-only-bind-mounted into the sandbox.    |
| `AI_JAIL`                                                                                                                                           | unset           | `scripts/ai-jail.sh`, `scripts/statusline-command.sh`             | Set to `1` inside the sandbox by `ai-jail.sh`; read by the statusline to show a jail indicator.       |
| `GITHUB_PAT_TOKEN`                                                                                                                                  | none (required) | `scripts/update-external-tools.sh`                                | GitHub PAT used to authenticate API calls when syncing external tools.                                |
| `NERD_FONT`                                                                                                                                         | `1`             | `scripts/statusline-command.sh`, `scripts/subagent-statusline.sh` | Set to anything other than `1` to disable Nerd Font glyphs in the statusline.                         |
| `CLAUDE_CONFIG_DIR`                                                                                                                                 | `$HOME/.claude` | `scripts/statusline-command.sh`                                   | Claude config dir; used to locate the caveman-mode flag file and detect the `-L` (local) profile.     |
| `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, `ANTHROPIC_API_KEY`, `CLAUDE_PROJECT_DIR`, `ENABLE_TOOL_SEARCH`, `ASDF_NODEJS_VERSION`, `CONTEXT7_API_KEY` | unset           | `scripts/ai-jail.sh`                                              | Passed through into the sandbox when set (see `PASSTHROUGH_VARS`).                                    |

---
