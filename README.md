## Project Overview

This project is a comprehensive toolkit designed to enhance AI-assisted software development. It serves as a centralized "intelligence hub" for AI agents (Gemini, Copilot, etc.), providing them with specialized roles, reusable skills, and structured workflows.

### Directory Structure

- `AGENTS.md`: Canonical agent instruction file (single source of truth for all harnesses).
- `agents/`: Markdown definitions for specialized AI roles.
- `skills/`: Reusable capabilities (e.g., style guides, TDD workflows, TLC spec-driven flow).
- `commands/`: Slash-command templates.
- `instructions/`: Foundation rules for agents and project-specific conventions (per-language/framework).
- `hooks/`: Hook scripts and config wired into agent harnesses.
- `src/`: Core Python tooling (context generation, token counting, MCP clients).
- `scripts/`: Install/clean/setup scripts per harness (claude, gemini, codex, copilot, antigravity...).
- `taskmaster/`: Task tracking config and state.
- `docs/`: Reference docs and supporting documentation.
- `docker/`: Docker compose configs (e.g., litellm proxy).
- `legacy/`: Archived/deprecated configs kept for reference.
- `tlc-harness-toolkit/`: TLC harness tooling and config.
- Per-harness dirs (`claude/`, `gemini/`, `github-copilot/`, `antigravity/`, `.claude/`, `.tlc/`, `.serena/`): harness-specific configs, MCP setups, settings.
- `install.sh`: Entry-point installer.
- `uninstall.sh`: Entry-point uninstaller.

### Instalation

```sh
git clone https://github.com/Ronnasayd/aipp.git ~/aipp
cd ~/aipp
bash install.sh
```

### Uninstalation

```sh
bash uninstall.sh
```

### Environment Variables

Hook-specific env vars: [`hooks/ENVIRONMENTS.md`](hooks/ENVIRONMENTS.md).

| Variable                                                                                                                                            | Default         | Used in                                                           | Description                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `CLAUDE_INSTALL_SKIP_AUTO_CONTEXT`                                                                                                                  | unset           | `scripts/claude.install.sh`                                       | Set to `1` to skip regenerating the `<!-- INIT AUTO-CONTEXT -->` block in `AGENTS.md` on install.               |
| `CLAUDE_INSTALL_SKIP_CLAUDE_MD`                                                                                                                     | unset           | `scripts/claude.install.sh`                                       | Set to `1` to skip (re)writing `CLAUDE.md` on install.                                                          |
| `CLAUDE_PROJECT_DIR`                                                                                                                                | project path    | `scripts/claude.install.sh`, `scripts/statusline-command.sh`      | Local project dir written to `settings.local.json`; used to locate `rag-rat.toml`/index cbm for the statusline. |
| `AI_PROJECT_ROOT_DIR`                                                                                                                               | unset           | `scripts/ai-jail.sh`                                              | Root dir (hooks/statusline/skills live here via symlinks) read-only-bind-mounted into the sandbox.              |
| `AI_JAIL`                                                                                                                                           | unset           | `scripts/ai-jail.sh`, `scripts/statusline-command.sh`             | Set to `1` inside the sandbox by `ai-jail.sh`; read by the statusline to show a jail indicator.                 |
| `GITHUB_PAT_TOKEN`                                                                                                                                  | none (required) | `scripts/update-external-tools.sh`                                | GitHub PAT used to authenticate API calls when syncing external tools.                                          |
| `NERD_FONT`                                                                                                                                         | `1`             | `scripts/statusline-command.sh`, `scripts/subagent-statusline.sh` | Set to anything other than `1` to disable Nerd Font glyphs in the statusline.                                   |
| `CLAUDE_CONFIG_DIR`                                                                                                                                 | `$HOME/.claude` | `scripts/statusline-command.sh`                                   | Claude config dir; used to locate the caveman-mode flag file and detect the `-L` (local) profile.               |
| `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, `ANTHROPIC_API_KEY`, `CLAUDE_PROJECT_DIR`, `ENABLE_TOOL_SEARCH`, `ASDF_NODEJS_VERSION`, `CONTEXT7_API_KEY` | unset           | `scripts/ai-jail.sh`                                              | Passed through into the sandbox when set (see `PASSTHROUGH_VARS`).                                              |

### External Tools

Non-native (non-coreutils) tools required or installed by this project's bash/python scripts.

| Tool                                                 | Purpose                                                                                                         |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `uv`                                                 | Python package/dependency manager                                                                               |
| spaCy models (`pt_core_news_sm`, `en_core_web_sm`)   | NLP models used by Python tooling                                                                               |
| `claude` (Claude Code CLI)                           | Plugin marketplace management                                                                                   |
| `rag-rat` plugin (cq27-dev/rag-rat)                  | Claude Code plugin: repo intelligence                                                                           |
| `codebase-memory-mcp` (DeusData/codebase-memory-mcp) | MCP server: repo intelligence fallback for languages rag-rat doesn't index here (162 languages via tree-sitter) |
| `caveman` plugin (JuliusBrussee/caveman)             | Claude Code plugin: token-compressed communication mode                                                         |
| `ponytail` plugin (DietrichGebert/ponytail)          | Claude Code plugin: lazy/minimal-code enforcement mode                                                          |
| `serena`                                             | Code agent / LSP-backed coding tool                                                                             |
| `rtk`                                                | Token-usage-reducing CLI proxy                                                                                  |
| `bat`                                                | Syntax-highlighted `cat` replacement                                                                            |
| `jq`                                                 | JSON processor                                                                                                  |
| `fzf`                                                | Fuzzy finder                                                                                                    |
| `lefthook`                                           | Git hooks manager                                                                                               |
| `ai-memory`                                          | Persistent cross-session memory CLI                                                                             |
| `curl`                                               | HTTP client (GitHub Contents API)                                                                               |
| `python3`                                            | Config merging, inline JSON parsing                                                                             |
| `skillspector` (via `uv run`)                        | Security scan of downloaded skills, quarantines findings                                                        |
| `security` (macOS Keychain CLI)                      | Stores/reads Claude OAuth token in `scripts/claude.accounts.sh`                                                 |
| `bwrap` (bubblewrap)                                 | Sandboxing for `scripts/ai-jail.sh`                                                                             |
| `docker`                                             | Runs sandbox mounts (`ai-jail.sh`) and the litellm proxy container                                              |
| `litellm` (Docker image `ghcr.io/berriai/litellm`)   | LLM proxy service, `docker/litellm/docker-compose.yml`                                                          |
| `ai-memory` container (`akitaonrails/ai-memory`)     | Docker image run by `aims`/`aimsllm` aliases in `.aipp.alias.zshrc`                                             |
| `codeburn` (via `npx`)                               | CLI run by `codeburn` alias                                                                                     |
| `agent-flow-app` (via `npx`)                         | CLI run by `afa` alias                                                                                          |
| `omniroute` (via `npx`)                              | CLI run by `omniroute` alias                                                                                    |
| `detect-secrets`                                     | Secret scanning in `hooks/scripts/secret_scan.py` (regex fallback if absent)                                    |

---
